"""Build/runtime selection for the two agreed Windows TV variants."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def current_variant() -> str:
    override = os.environ.get("WINDOWS_TV_VARIANT", "").strip().lower()
    if override in {"basis", "standard"}:
        return override

    # Installed PyInstaller builds receive variant.txt from the installer.
    candidates = [
        Path(sys.argv[0]).resolve().parent / "variant.txt",
        Path(sys.executable).resolve().parent / "variant.txt",
    ]
    for candidate in candidates:
        try:
            value = candidate.read_text(encoding="utf-8").strip().lower()
        except OSError:
            continue
        if value in {"basis", "standard"}:
            return value
    return "basis"


def is_standard_variant() -> bool:
    return current_variant() == "standard"
