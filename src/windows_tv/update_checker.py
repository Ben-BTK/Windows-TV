"""Read public GitHub release metadata; never downloads or installs binaries."""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


OWNER = "Ben-BTK"
REPOSITORY = "Windows-TV"
RELEASES_API = f"https://api.github.com/repos/{OWNER}/{REPOSITORY}/releases/latest"


def check_latest_release(timeout: float = 8.0) -> dict[str, str] | None:
    request = Request(
        RELEASES_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Windows-TV-release-checker",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise ValueError(f"GitHub antwortete mit HTTP {response.status}.")
            raw = response.read(1024 * 1024 + 1)
    except HTTPError as exc:
        if exc.code == 404:
            # GitHub returns 404 when the repository has no published releases yet.
            return None
        raise
    if len(raw) > 1024 * 1024:
        raise ValueError("Die GitHub-Antwort überschreitet die erlaubte Größe.")
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("tag_name"), str):
        raise ValueError("GitHub hat keine gültigen Release-Metadaten zurückgegeben.")
    return {
        "tag_name": data["tag_name"],
        "html_url": str(data.get("html_url", "")),
        "name": str(data.get("name", "")),
    }
