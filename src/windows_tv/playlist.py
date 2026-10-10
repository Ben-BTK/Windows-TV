"""Minimal M3U/M3U8 parser for network stream playlists.

Local playlist files are supported; local video files are deliberately not
treated as playback sources.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import re


@dataclass(frozen=True)
class Channel:
    name: str
    url: str
    logo: str = ""
    group: str = ""
    tvg_id: str = ""
    country: str = ""
    language: str = ""


_ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')


def _attrs(line: str) -> dict[str, str]:
    return {key.lower(): value for key, value in _ATTR_RE.findall(line)}


def _display_name(info_line: str, attrs: dict[str, str]) -> str:
    if attrs.get("tvg-name"):
        return attrs["tvg-name"].strip()
    if "," in info_line:
        return info_line.split(",", 1)[1].strip()
    return attrs.get("tvg-id", "").strip() or "Unbenannter Sender"


def parse_m3u(text: str) -> list[Channel]:
    channels: list[Channel] = []
    pending: tuple[str, dict[str, str]] | None = None

    for raw_line in text.lstrip("\ufeff").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.upper().startswith("#EXTINF:"):
            pending = (line, _attrs(line))
            continue
        if line.startswith("#"):
            continue
        if pending is None:
            # Permit a bare stream URL, but do not guess a title from a file.
            name, attrs = "Unbenannter Sender", {}
        else:
            info_line, attrs = pending
            name = _display_name(info_line, attrs)
        parsed = urlparse(line)
        if parsed.scheme.lower() not in {"http", "https", "rtsp", "rtmp", "udp"}:
            pending = None
            continue
        channels.append(Channel(
            name=name or "Unbenannter Sender",
            url=line,
            logo=attrs.get("tvg-logo", ""),
            group=attrs.get("group-title", ""),
            tvg_id=attrs.get("tvg-id", ""),
            country=attrs.get("tvg-country", ""),
            language=attrs.get("tvg-language", attrs.get("audio-track", "")),
        ))
        pending = None
    return channels


def load_playlist_file(path: str | Path) -> list[Channel]:
    file_path = Path(path)
    if file_path.suffix.lower() not in {".m3u", ".m3u8"}:
        raise ValueError("Bitte eine M3U- oder M3U8-Playlist auswählen.")
    data = file_path.read_text(encoding="utf-8-sig", errors="replace")
    return parse_m3u(data)
