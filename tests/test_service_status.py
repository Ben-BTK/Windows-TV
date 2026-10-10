import io
import json

import pytest

from windows_tv import service_status


class FakeResponse:
    status = 200

    def __init__(self, payload: dict):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit: int):
        return self.payload


def test_accepts_valid_maintenance_status(monkeypatch):
    payload = {
        "mode": "maintenance",
        "title": "Wartung",
        "message": "Quellenimport kurzzeitig gesperrt",
        "locked_features": ["source_import"],
        "starts_at": "22:00 UTC",
        "ends_at": "22:30 UTC",
        "updated_at": "2026-10-10T21:50:00Z",
        "announcement": "",
    }
    monkeypatch.setattr(service_status, "urlopen", lambda *_args, **_kwargs: FakeResponse(payload))
    result = service_status.fetch_service_status()
    assert result["mode"] == "maintenance"
    assert result["locked_features"] == ["source_import"]
    assert result["title"] == "Wartung"


def test_rejects_unknown_lock(monkeypatch):
    payload = {"mode": "maintenance", "locked_features": ["run_arbitrary_command"]}
    monkeypatch.setattr(service_status, "urlopen", lambda *_args, **_kwargs: FakeResponse(payload))
    with pytest.raises(ValueError):
        service_status.fetch_service_status()


def test_rejects_unknown_mode(monkeypatch):
    payload = {"mode": "remote_control", "locked_features": []}
    monkeypatch.setattr(service_status, "urlopen", lambda *_args, **_kwargs: FakeResponse(payload))
    with pytest.raises(ValueError):
        service_status.fetch_service_status()
