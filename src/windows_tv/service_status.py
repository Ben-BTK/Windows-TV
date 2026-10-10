"""Read a small, validated public service-status document from this repository."""
from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen


STATUS_URL = (
    "https://raw.githubusercontent.com/Ben-BTK/Windows-TV/main/"
    "status/service-status.json"
)
ALLOWED_MODES = {
    "normal",
    "limited_service",
    "scheduled_maintenance",
    "maintenance",
    "outage",
    "acute_outage",
}
ALLOWED_LOCKS = {"all", "playback", "source_import", "favorites"}


def central_service_base_url() -> str:
    return os.environ.get("WINDOWS_TV_SERVICE_URL", "").strip().rstrip("/")


def fetch_service_status(timeout: float = 4.0) -> dict:
    base_url = central_service_base_url()
    status_url = base_url + "/api/status" if base_url else STATUS_URL
    request = Request(
        status_url,
        headers={"User-Agent": "Windows-TV-service-status/0.1", "Cache-Control": "no-cache"},
    )
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError(f"Statusserver antwortete mit HTTP {response.status}.")
        raw = response.read(64 * 1024 + 1)
    if len(raw) > 64 * 1024:
        raise ValueError("Statusmeldung überschreitet die erlaubte Größe.")
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Statusmeldung hat ein ungültiges Format.")

    mode = data.get("mode", "normal")
    if mode not in ALLOWED_MODES:
        raise ValueError("Unbekannter Statusmodus.")
    locks = data.get("locked_features", [])
    if not isinstance(locks, list) or any(lock not in ALLOWED_LOCKS for lock in locks):
        raise ValueError("Die Liste gesperrter Funktionen ist ungültig.")

    return {
        "mode": mode,
        "title": str(data.get("title", ""))[:160],
        "message": str(data.get("message", ""))[:2000],
        "locked_features": list(dict.fromkeys(locks)),
        "locks_explicit": "locked_features" in data,
        "starts_at": str(data.get("starts_at", ""))[:80],
        "ends_at": str(data.get("ends_at", ""))[:80],
        "updated_at": str(data.get("updated_at", ""))[:80],
        "announcement": str(data.get("announcement", ""))[:2000],
    }
