"""Build/runtime selection for the two agreed Windows TV variants."""
from __future__ import annotations

import os


def current_variant() -> str:
    value = os.environ.get("WINDOWS_TV_VARIANT", "basis").strip().lower()
    return value if value in {"basis", "standard"} else "basis"


def is_standard_variant() -> bool:
    return current_variant() == "standard"
