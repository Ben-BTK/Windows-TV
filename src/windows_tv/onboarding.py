"""First-run setup and variant-specific terms for FlemmauTV.

This is a local prototype only. It does not authenticate users or grant server-side
permissions; those require a trusted backend and must never rely on this UI.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFormLayout,
    QLabel, QLineEdit, QMessageBox, QVBoxLayout,
)

BASIS_TERMS_VERSION = "basis-0.1"
STANDARD_TERMS_VERSION = "standard-0.1"
DISPLAY_NAME_PATTERN = re.compile(r"^[\wÀ-ÖØ-öø-ÿ]+(?:[- ][\wÀ-ÖØ-öø-ÿ]+)?$", re.UNICODE)
# Common full names of public figures and prohibited slogans cannot be reliably
# identified with a small offline list. Ambiguous cases require human review.
BLOCKED_EXACT_NAMES = {
    "adolf hitler",
    "osama bin laden",
}
BLOCKED_TERMS = {
    "heil hitler",
    "sieg heil",
}


def validate_display_name(value: str) -> tuple[bool, str]:
    """Validate the shape of an address name; not a complete abuse/name moderation system."""
    name = " ".join(value.strip().split())
    if not name:
        return False, "Bitte einen Vornamen oder geläufigen Spitznamen eingeben."
    if len(name) > 40:
        return False, "Der Ansprechname darf höchstens 40 Zeichen lang sein."
    if not DISPLAY_NAME_PATTERN.fullmatch(name):
        return False, (
            "Erlaubt ist ein Vorname oder Spitzname. Ausnahme: genau zwei Namen "
            "mit einem Bindestrich oder Leerzeichen. Keine vollständigen Vor- und Nachnamen."
        )
    if len(re.split(r"[- ]", name)) > 2:
        return False, "Es sind höchstens zwei Namen erlaubt."
    normalized = name.casefold()
    if normalized in BLOCKED_EXACT_NAMES or normalized in BLOCKED_TERMS:
        return False, "Dieser Ansprechname kann nicht verwendet werden."
    return True, ""


class FirstRunSetup(QDialog):
    """Collect the local first-run consent and optional Standard preferences."""

    def __init__(self, settings: QSettings, variant: str, parent=None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.variant = variant if variant in {"basis", "standard"} else "basis"
        self.setWindowTitle("FlemmauTV – Ersteinrichtung")
        self.setMinimumWidth(520)
        layout = QVBoxLayout(self)

        intro = QLabel(
            "Willkommen bei FlemmauTV. Diese Einrichtung speichert deine Auswahl "
            "lokal auf diesem Gerät. Sie erstellt noch kein Online-Konto und vergibt "
            "keine serverseitigen Mitarbeiter- oder Verwaltungsrechte."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        form = QFormLayout()
        self.country = QComboBox()
        self.country.addItem("Deutschland", "DE")
        self.country.addItem("Österreich", "AT")
        self.country.addItem("Schweiz", "CH")
        saved_country = settings.value("profile/country", "DE", type=str)
        index = self.country.findData(saved_country)
        if index >= 0:
            self.country.setCurrentIndex(index)
        self.display_name = QLineEdit(settings.value("profile/display_name", "", type=str))
        self.display_name.setMaxLength(40)
        self.display_name.setPlaceholderText("Vorname oder geläufiger Spitzname")
        form.addRow("Bevorzugtes Land", self.country)
        if self.variant == "standard":
            form.addRow("Ansprechname", self.display_name)
        layout.addLayout(form)

        self.kids = QCheckBox("Kinderprogramm später einrichten (optional)")
        self.kids.setChecked(settings.value("features/kids_setup_requested", False, type=bool))
        if self.variant == "standard":
            layout.addWidget(self.kids)

        self.terms_label = QLabel(
            "Bitte lies die für deine Variante geltenden Bedingungen. Deine Bestätigung "
            "wird mit Versionsstand und UTC-Zeitpunkt lokal dokumentiert. Die rechtliche "
            "Ausgestaltung muss vor einem öffentlichen Produktivbetrieb geprüft werden."
        )
        self.terms_label.setWordWrap(True)
        layout.addWidget(self.terms_label)
        self.terms = QCheckBox(
            f"Ich habe die Nutzungsbedingungen für die Variante {self.variant.capitalize()} gelesen "
            "und bestätige sie."
        )
        layout.addWidget(self.terms)

        self.camera_note = QLabel(
            "Kamerafunktionen sind unabhängig von Basis/Standard. Diese Einrichtung "
            "erteilt keine Kameraberechtigung; diese muss separat und ausdrücklich "
            "eingerichtet werden."
        )
        self.camera_note.setWordWrap(True)
        layout.addWidget(self.camera_note)

        self.error = QLabel("")
        self.error.setWordWrap(True)
        layout.addWidget(self.error)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self) -> None:
        if not self.terms.isChecked():
            self.error.setText("Du musst die geltenden Bedingungen bestätigen, bevor du fortfährst.")
            return
        display_name = self.display_name.text().strip()
        if self.variant == "standard":
            valid, reason = validate_display_name(display_name)
            if not valid:
                self.error.setText(reason)
                return
        terms_version = BASIS_TERMS_VERSION if self.variant == "basis" else STANDARD_TERMS_VERSION
        prefix = f"consent/{self.variant}"
        self.settings.setValue(f"{prefix}/version", terms_version)
        self.settings.setValue(
            f"{prefix}/accepted_at_utc",
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        self.settings.setValue("profile/country", self.country.currentData())
        if self.variant == "standard":
            self.settings.setValue("profile/display_name", display_name)
            self.settings.setValue("features/kids_setup_requested", self.kids.isChecked())
            self.settings.setValue("setup/standard_completed", True)
        else:
            self.settings.setValue("setup/basis_completed", True)
        self.settings.sync()
        self.accept()


def ensure_initial_setup(settings: QSettings, variant: str, parent=None) -> bool:
    """Run setup when current variant has not accepted its current terms version."""
    variant = variant if variant in {"basis", "standard"} else "basis"
    expected = BASIS_TERMS_VERSION if variant == "basis" else STANDARD_TERMS_VERSION
    if settings.value(f"consent/{variant}/version", "", type=str) == expected:
        return True
    dialog = FirstRunSetup(settings, variant, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted
