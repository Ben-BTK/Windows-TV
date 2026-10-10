from __future__ import annotations

import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PySide6.QtCore import Qt, QUrl, QTimer, QSettings
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QFileDialog, QFormLayout,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QMessageBox, QPushButton, QSplitter, QTextEdit, QVBoxLayout, QWidget
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

from windows_tv.playlist import Channel, load_playlist_file, parse_m3u
from windows_tv.storage import load_favorites, save_favorites
from windows_tv.update_checker import check_latest_release
from windows_tv.service_status import central_service_base_url, fetch_service_status
from windows_tv.variant import is_standard_variant


APP_TITLE = "Windows TV"
APP_VERSION = "0.1.0.dev0"
UPDATE_CHECK_INTERVAL_MS = 24 * 60 * 60 * 1000
STATUS_CHECK_INTERVAL_MS = 5 * 60 * 1000


def fetch_playlist(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Windows-TV/0.1 (playlist importer)"})
    with urlopen(request, timeout=12) as response:
        status = response.status
        raw = response.read(8 * 1024 * 1024 + 1)
    if status < 200 or status >= 300:
        raise ValueError(f"Der Server antwortete mit HTTP {status}.")
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
        self.standard_variant = is_standard_variant()
        self.settings = QSettings("Ben-BTK", APP_TITLE)
        self.service_mode = "unknown"
        self.locked_features: set[str] = set()
        self.last_notified_release = self.settings.value("last_notified_release", "", type=str)

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
        self.service_banner = QLabel()
        self.service_banner.setWordWrap(True)
        self.service_banner.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.service_banner.setStyleSheet(
            "QLabel { background: #493b20; color: #fff1c2; border: 1px solid #8b6b2d; "
            "border-radius: 7px; padding: 10px; font-weight: 600; }"
        )
        self.service_banner.hide()

        self.import_url_button.clicked.connect(self.import_url)
        self.import_file_button.clicked.connect(self.import_file)
        self.search_input.textChanged.connect(self.refresh_channels)
        self.group_filter.currentTextChanged.connect(self.refresh_channels)
        self.channel_list.itemDoubleClicked.connect(self.play_selected)

        self.play_button = QPushButton("Abspielen")
        self.stop_button = QPushButton("Stop")
        self.favorite_button = QPushButton("☆ Favorit")
        self.feedback_button = QPushButton("Hilfe & Rückmeldung")
        self.play_button.clicked.connect(self.play_selected)
        self.stop_button.clicked.connect(self.player.stop)
        self.favorite_button.clicked.connect(self.toggle_favorite)
        self.feedback_button.clicked.connect(self.open_feedback_dialog)

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
        left_layout.addWidget(self.feedback_button)

        if self.standard_variant:
            self.update_button = QPushButton("Jetzt nach Updates suchen")
            self.update_button.clicked.connect(self.check_updates)
            left_layout.addWidget(self.update_button)

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
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(8, 8, 8, 8)
        central_layout.addWidget(self.service_banner)
        central_layout.addWidget(splitter, 1)
        self.setCentralWidget(central)

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

        # GitHub update checks remain exclusive to the Standard installation.
        if self.standard_variant:
            QTimer.singleShot(2500, self.check_updates_automatically)
            self.update_timer = QTimer(self)
            self.update_timer.setInterval(UPDATE_CHECK_INTERVAL_MS)
            self.update_timer.timeout.connect(self.check_updates_automatically)
            self.update_timer.start()

        # Both variants can use the central service once its HTTPS URL is configured.
        # Until then, Standard retains the existing public status-file fallback.
        if self.standard_variant or central_service_base_url():
            QTimer.singleShot(1200, self.check_service_status)
            self.service_timer = QTimer(self)
            self.service_timer.setInterval(STATUS_CHECK_INTERVAL_MS)
            self.service_timer.timeout.connect(self.check_service_status)
            self.service_timer.start()

    def import_url(self) -> None:
        if self._is_locked("source_import"):
            self._show_locked_message("Quellenimport")
            return
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
        if self._is_locked("source_import"):
            self._show_locked_message("Quellenimport")
            return
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
        if self._is_locked("playback"):
            self._show_locked_message("Wiedergabe")
            return
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
        if self._is_locked("favorites"):
            self._show_locked_message("Favoriten")
            return
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

    def check_updates(self) -> None:
        self._check_updates(automatic=False)

    def check_updates_automatically(self) -> None:
        self._check_updates(automatic=True)

    def _check_updates(self, automatic: bool) -> None:
        if not self.standard_variant:
            return
        if not automatic:
            self.status.setText("Prüfe öffentliche GitHub-Veröffentlichungen …")
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            release = check_latest_release()
            if release is None:
                if not automatic:
                    QMessageBox.information(
                        self, "Updates",
                        "Es wurde noch keine öffentliche GitHub-Veröffentlichung gefunden."
                    )
                    self.status.setText("Keine veröffentlichte Version gefunden.")
                return

            tag = release["tag_name"].strip()
            normalized_tag = tag.removeprefix("v").removeprefix("V")
            normalized_current = APP_VERSION.removeprefix("v").removeprefix("V")
            if normalized_tag == normalized_current:
                if not automatic:
                    QMessageBox.information(
                        self, "Updates",
                        f"Du verwendest die aktuell veröffentlichte Version ({tag})."
                    )
                    self.status.setText(f"Version aktuell: {tag}")
                return

            self.status.setText(f"Eine GitHub-Veröffentlichung ist verfügbar: {tag}")
            if automatic and tag == self.last_notified_release:
                return
            self.last_notified_release = tag
            self.settings.setValue("last_notified_release", tag)
            box = QMessageBox(self)
            box.setWindowTitle("Update verfügbar")
            box.setIcon(QMessageBox.Icon.Information)
            box.setText(f"Eine veröffentlichte Windows-TV-Version wurde gefunden: {tag}")
            box.setInformativeText(
                f"{release.get('name', '')}\n\n"
                f"{release.get('html_url', '')}\n\n"
                "Die Aktualisierung wird nicht automatisch installiert. "
                "Bitte öffne die Veröffentlichung und prüfe die Hinweise."
            )
            box.setStandardButtons(QMessageBox.StandardButton.Ok)
            box.exec()
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError) as exc:
            # Scheduled checks should not interrupt the user with repeated pop-ups.
            if not automatic:
                QMessageBox.warning(self, "Update-Prüfung fehlgeschlagen", str(exc))
            self.status.setText("GitHub-Update-Informationen sind derzeit nicht erreichbar.")
        finally:
            if not automatic:
                QApplication.restoreOverrideCursor()


    def open_feedback_dialog(self) -> None:
        base_url = central_service_base_url()
        dialog = QDialog(self)
        dialog.setWindowTitle("Hilfe & Rückmeldung")
        dialog.resize(560, 520)
        layout = QVBoxLayout(dialog)
        if base_url:
            info = QLabel(
                "Du kannst eine Störung melden, Feedback geben oder einen Funktionswunsch senden. "
                "Kontaktangaben sind freiwillig. Es werden keine Playlist-URLs oder Zugangsdaten übertragen."
            )
        else:
            info = QLabel(
                "Die zentrale Meldestelle ist noch nicht mit einem öffentlichen HTTPS-Server verbunden. "
                "Es wird nichts übertragen. Die Maske ist vorbereitet und wird nach Einrichtung der Serveradresse aktiviert."
            )
        info.setWordWrap(True)
        layout.addWidget(info)

        form = QFormLayout()
        category = QComboBox()
        category.addItem("Störung melden", "incident")
        category.addItem("Kritik / Feedback", "feedback")
        category.addItem("Funktionswunsch", "feature_request")
        subject = QLineEdit()
        subject.setMaxLength(160)
        subject.setPlaceholderText("Kurzer Titel")
        description = QTextEdit()
        description.setPlaceholderText("Was ist passiert oder was möchtest du vorschlagen?")
        description.setMinimumHeight(130)
        severity = QComboBox()
        severity.addItem("Normal", "normal")
        severity.addItem("Hoch – Funktion stark eingeschränkt", "high")
        severity.addItem("Kritisch – Programm startet nicht / Hauptfunktion ausgefallen", "critical")
        feature = QComboBox()
        feature.addItem("Allgemein", "")
        feature.addItem("Start / Programmfenster", "startup")
        feature.addItem("Quellenimport", "source_import")
        feature.addItem("Wiedergabe", "playback")
        feature.addItem("Favoriten / Einstellungen", "favorites")
        feature.addItem("Installation / Update", "installation")
        contact = QLineEdit()
        contact.setMaxLength(254)
        contact.setPlaceholderText("Optional – z. B. E-Mail-Adresse")
        form.addRow("Art der Meldung", category)
        form.addRow("Betreff", subject)
        form.addRow("Beschreibung", description)
        form.addRow("Schweregrad", severity)
        form.addRow("Betroffener Bereich", feature)
        form.addRow("Rückkontakt (optional)", contact)
        layout.addLayout(form)

        privacy = QLabel(
            "Bitte keine Passwörter, Stream-Zugangsdaten oder privaten Playlist-Inhalte eingeben. "
            "Die Meldung ist kein Notruf und garantiert keine sofortige Reaktion."
        )
        privacy.setWordWrap(True)
        layout.addWidget(privacy)
        buttons = QHBoxLayout()
        send_button = QPushButton("Meldung senden")
        cancel_button = QPushButton("Schließen")
        send_button.setEnabled(bool(base_url))
        buttons.addWidget(send_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)
        cancel_button.clicked.connect(dialog.reject)

        def send_report() -> None:
            title = subject.text().strip()
            details = description.toPlainText().strip()
            if len(title) < 3 or len(details) < 10:
                QMessageBox.warning(dialog, "Angaben fehlen", "Bitte Betreff (mindestens 3 Zeichen) und Beschreibung (mindestens 10 Zeichen) ausfüllen.")
                return
            payload = {
                "report_type": category.currentData(),
                "subject": title,
                "description": details,
                "severity": severity.currentData(),
                "affected_feature": feature.currentData(),
                "app_version": APP_VERSION,
                "app_variant": "standard" if self.standard_variant else "basis",
                "contact": contact.text().strip(),
                "diagnostic_text": "",
                "website": "",
            }
            request = Request(
                base_url + "/api/reports",
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": f"Windows-TV/{APP_VERSION}"},
                method="POST",
            )
            send_button.setEnabled(False)
            try:
                with urlopen(request, timeout=8) as response:
                    result = json.loads(response.read(64 * 1024 + 1).decode("utf-8"))
                reference = result.get("reference", "")
                if not result.get("accepted") or not reference:
                    raise ValueError("Der Server hat keine gültige Eingangsbestätigung zurückgegeben.")
                QMessageBox.information(
                    dialog, "Meldung angenommen",
                    f"Deine Meldung wurde gespeichert. Referenznummer: {reference}\n\n"
                    "Bitte bewahre diese Nummer auf. Eine sofortige Antwort ist nicht garantiert."
                )
                dialog.accept()
            except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
                QMessageBox.warning(
                    dialog, "Übermittlung fehlgeschlagen",
                    "Die Meldung konnte nicht bestätigt werden. Sie wurde nicht als erfolgreich versendet markiert. "
                    f"Bitte versuche es später erneut.\n\nDetails: {exc}"
                )
            finally:
                if dialog.isVisible():
                    send_button.setEnabled(True)

        send_button.clicked.connect(send_report)
        dialog.exec()

    def check_service_status(self) -> None:
        if not self.standard_variant and not central_service_base_url():
            return
        try:
            data = fetch_service_status()
            self._apply_service_status(data)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError):
            # A temporary status endpoint failure must not falsely lock the app.
            if self.service_mode == "unknown":
                self.status.setText(
                    "Der öffentliche Dienststatus ist derzeit nicht erreichbar; "
                    "es wurde keine automatische Funktionssperre aktiviert."
                )

    def _apply_service_status(self, data: dict) -> None:
        mode = data["mode"]
        locks = set(data["locked_features"])
        if not data.get("locks_explicit", False):
            if mode in {"maintenance", "acute_outage"}:
                locks = {"all"}
            elif mode == "scheduled_maintenance":
                locks = {"source_import"}
            elif mode == "outage":
                locks = {"playback"}

        self.service_mode = mode
        self.locked_features = locks
        title = data.get("title", "").strip()
        message = data.get("message", "").strip()
        announcement = data.get("announcement", "").strip()
        lines = []
        if title:
            lines.append(title)
        elif mode != "normal":
            lines.append({
                "limited_service": "Eingeschränkter Dienst",
                "scheduled_maintenance": "Geplante Wartungsarbeiten",
                "maintenance": "Wartungsarbeiten",
                "outage": "Dienststörung",
                "acute_outage": "Akute Störung",
            }.get(mode, "Dienststatus"))
        if message:
            lines.append(message)
        if announcement:
            lines.append(announcement)
        if data.get("starts_at"):
            lines.append("Beginn: " + data["starts_at"])
        if data.get("ends_at"):
            lines.append("Voraussichtliches Ende: " + data["ends_at"])

        if mode == "normal" and not lines:
            self.service_banner.hide()
        else:
            self.service_banner.setText("\n".join(lines) or "Dienstinformationen verfügbar.")
            self.service_banner.show()

        self._sync_locked_controls()
        if mode != "normal":
            self.status.setText("Dienststatus: " + mode.replace("_", " "))
        elif announcement:
            self.status.setText(announcement)

        if "playback" in locks or "all" in locks:
            self.player.stop()
            self.current_channel = None
            self.now_playing.setText("Wiedergabe derzeit gesperrt")

    def _is_locked(self, feature: str) -> bool:
        return "all" in self.locked_features or feature in self.locked_features

    def _show_locked_message(self, feature_name: str) -> None:
        QMessageBox.information(
            self, "Funktion vorübergehend gesperrt",
            f"{feature_name} ist aufgrund von Wartungsarbeiten oder einer Dienststörung "
            "vorübergehend gesperrt. Bitte beachte die Statusanzeige im oberen Bereich."
        )

    def _sync_locked_controls(self) -> None:
        self.import_url_button.setEnabled(not self._is_locked("source_import"))
        self.import_file_button.setEnabled(not self._is_locked("source_import"))
        self.play_button.setEnabled(not self._is_locked("playback"))
        self.favorite_button.setEnabled(not self._is_locked("favorites"))
        self.channel_list.setEnabled(not self._is_locked("all"))
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
