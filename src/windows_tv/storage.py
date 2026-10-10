"""Small local settings store for favorite stream URLs."""
from __future__ import annotations

import json
from pathlib import Path
from PySide6.QtCore import QStandardPaths


def _settings_path() -> Path:
    base = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
    base.mkdir(parents=True, exist_ok=True)
    return base / "settings.json"


def load_favorites() -> set[str]:
    try:
        data = json.loads(_settings_path().read_text(encoding="utf-8"))
        values = data.get("favorites", [])
        return {str(value) for value in values if isinstance(value, str)}
    except (OSError, ValueError, TypeError):
        return set()


def save_favorites(favorites: set[str]) -> None:
    path = _settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"favorites": sorted(favorites)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
