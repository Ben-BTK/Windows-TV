from __future__ import annotations

import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QPushButton,
    QSplitter, QVBoxLayout, QWidget
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

from windows_tv.playlist import Channel, load_playlist_file, parse_m3u
from windows_tv.storage import load_favorites, save_favorites


APP_TITLE = "Windows TV"


def fetch_playlist(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Windows-TV/0.1 (playlist importer)"})
    with urlopen(request, timeout=12) as response:
        content_type = response.headers.get_content_type()
        if response.status < 200 or response.status >= 300:
            raise ValueError(f"Der Server antwortete mit HTTP {response.status}.")
        if len(response.read(1)) == 0:
            raise ValueError("Die Playlist ist leer.")
        response.close()
    # Read the playlist separately with a bounded response to avoid unbounded downloads.
    with urlopen(request, timeout=12) as response:
        raw = response.read(8 * 1024 * 1024 + 1)
    if len(raw) > 8 * 1024 * 1024:
        raise ValueError("Die Playlist ist größer als 8 MiB und wird nicht importiert.")
    if not raw.strip():
        raise ValueError("Die Playlist ist leer.")
    return raw.decode("utf-8-sig", errors="replace")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1180, 740)
        self.channels: list[Channel] = []
        self.favorites = load_favorites()
        self.current_channel: Channel | None = None

        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.video = QVideoWidget()
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video)
        self.player.errorOccurred.connect(self._player_error)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("M3U/M3U8-Playlist-URL einfügen")
        self.import_url_button = QPushButton("URL prüfen & importieren")
        self.import_file_button = QPushButton("Playlist-Datei öffnen")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Sender suchen …")
        self.group_filter = QComboBox()
        self.group_filter.addItem("Alle Gruppen")
        self.channel_list = QListWidget()
        self.status = QLabel("Bereit. Bitte eine M3U/M3U8-Quelle hinzufügen.")
        self.status.setWordWrap(True)

        self.import_url_button.clicked.connect(self.import_url)
        self.import_file_button.clicked.connect(self.import_file)
        self.search_input.textChanged.connect(self.refresh_channels)
        self.group_filter.currentTextChanged.connect(self.refresh_channels)
        self.channel_list.itemDoubleClicked.connect(self.play_selected)

        self.play_button = QPushButton("Abspielen")
        self.stop_button = QPushButton("Stop")
        self.favorite_button = QPushButton("☆ Favorit")
        self.play_button.clicked.connect(self.play_selected)
        self.stop_button.clicked.connect(self.player.stop)
        self.favorite_button.clicked.connect(self.toggle_favorite)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Quelle"))
        url_row = QHBoxLayout()
        url_row.addWidget(self.url_input, 1)
        url_row.addWidget(self.import_url_button)
        left_layout.addLayout(url_row)
        left_layout.addWidget(self.import_file_button)
        left_layout.addWidget(self.search_input)
        left_layout.addWidget(self.group_filter)
        left_layout.addWidget(self.channel_list, 1)
        controls = QHBoxLayout()
        controls.addWidget(self.play_button)
        controls.addWidget(self.stop_button)
        controls.addWidget(self.favorite_button)
        left_layout.addLayout(controls)
        left_layout.addWidget(self.status)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        self.now_playing = QLabel("Kein Sender ausgewählt")
        self.now_playing.setWordWrap(True)
        right_layout.addWidget(self.now_playing)
        right_layout.addWidget(self.video, 1)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([380, 800])
        self.setCentralWidget(splitter)

        self.setStyleSheet("""
            QMainWindow { background: #15191f; color: #eef2f6; }
            QWidget { color: #eef2f6; font-size: 10pt; }
            QLineEdit, QListWidget, QComboBox {
                background: #202731; border: 1px solid #3a4553;
                border-radius: 6px; padding: 7px;
            }
            QPushButton {
                background: #2b3746; border: 1px solid #455466;
                border-radius: 6px; padding: 8px 11px;
            }
            QPushButton:hover { background: #394a5e; }
            QListWidget::item { padding: 7px; }
            QListWidget::item:selected { background: #315b80; }
        """)

    def import_url(self) -> None:
        url = self.url_input.text().strip()
        if not url.lower().startswith(("https://", "http://")):
            QMessageBox.warning(self, "Quelle prüfen", "Bitte eine HTTP- oder HTTPS-Playlist-URL eingeben.")
            return
        self.status.setText("Prüfe Verbindung und lese Playlist …")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            text = fetch_playlist(url)
            parsed = parse_m3u(text)
            if not parsed:
                raise ValueError("Es wurden keine unterstützten Stream-Einträge gefunden.")
            self._set_channels(parsed, f"Playlist erreichbar; {len(parsed)} Einträge importiert.")
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            QMessageBox.warning(self, "Import fehlgeschlagen", f"Die Quelle konnte nicht importiert werden.\n\n{exc}")
            self.status.setText("Import fehlgeschlagen. Prüfe URL, Internetverbindung und Playlistformat.")
        finally:
            QApplication.restoreOverrideCursor()

    def import_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "M3U/M3U8-Playlist öffnen", "", "Playlist-Dateien (*.m3u *.m3u8)"
        )
        if not path:
            return
        try:
            parsed = load_playlist_file(path)
            if not parsed:
                raise ValueError("Es wurden keine unterstützten Stream-Einträge gefunden.")
            self._set_channels(parsed, f"{len(parsed)} Einträge aus lokaler Playlist importiert.")
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Playlist nicht lesbar", str(exc))

    def _set_channels(self, channels: list[Channel], message: str) -> None:
        self.channels = channels
        groups = sorted({channel.group for channel in channels if channel.group})
        self.group_filter.blockSignals(True)
        self.group_filter.clear()
        self.group_filter.addItem("Alle Gruppen")
        self.group_filter.addItems(groups)
        self.group_filter.blockSignals(False)
        self.refresh_channels()
        self.status.setText(message + " Die Nutzungsrechte der Inhalte müssen separat geprüft werden.")

    def refresh_channels(self, *_args) -> None:
        query = self.search_input.text().casefold().strip()
        selected_group = self.group_filter.currentText()
        self.channel_list.clear()
        for channel in self.channels:
            if query and query not in channel.name.casefold() and query not in channel.group.casefold():
                continue
            if selected_group != "Alle Gruppen" and channel.group != selected_group:
                continue
            prefix = "★ " if channel.url in self.favorites else ""
            item = QListWidgetItem(prefix + channel.name)
            item.setData(Qt.ItemDataRole.UserRole, channel.url)
            item.setToolTip(channel.url)
            self.channel_list.addItem(item)

    def _selected_channel(self) -> Channel | None:
        item = self.channel_list.currentItem()
        if item is None:
            return None
        url = item.data(Qt.ItemDataRole.UserRole)
        return next((channel for channel in self.channels if channel.url == url), None)

    def play_selected(self, *_args) -> None:
        channel = self._selected_channel()
        if channel is None:
            QMessageBox.information(self, "Sender auswählen", "Bitte zuerst einen Sender aus der Liste auswählen.")
            return
        self.current_channel = channel
        self.now_playing.setText(f"Jetzt ausgewählt: {channel.name}\n{channel.group}")
        self.status.setText("Verbindung zum Stream wird aufgebaut …")
        self.player.setSource(QUrl(channel.url))
        self.player.play()

    def toggle_favorite(self) -> None:
        channel = self._selected_channel()
        if channel is None:
            QMessageBox.information(self, "Favorit", "Bitte zuerst einen Sender auswählen.")
            return
        if channel.url in self.favorites:
            self.favorites.remove(channel.url)
            self.status.setText(f"Favorit entfernt: {channel.name}")
        else:
            self.favorites.add(channel.url)
            self.status.setText(f"Favorit gespeichert: {channel.name}")
        save_favorites(self.favorites)
        self.refresh_channels()

    def _player_error(self, *_args) -> None:
        message = self.player.errorString() or "Der Stream kann mit dem aktuell verfügbaren Wiedergabemodul nicht abgespielt werden."
        self.status.setText("Stream nicht verfügbar oder nicht unterstützt.")
        QMessageBox.warning(
            self, "Wiedergabe fehlgeschlagen",
            f"{message}\n\nNicht jede M3U/M3U8-Quelle verwendet dasselbe Streamingformat. "
            "Ein erfolgreicher Playlist-Import garantiert keine Wiedergabe."
        )


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Windows TV")
    app.setOrganizationName("Ben-BTK")
    window = MainWindow()
    window.show()
    return app.exec()
