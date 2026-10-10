"""FlemmauTV registration and beta-activation API.

This router is an initial server-side workflow. It does not grant access merely
because a registration request was submitted. Public deployment requires HTTPS,
shared/proxy rate limits, privacy information and security testing.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

router = APIRouter()
DB_PATH = Path(os.environ.get("WINDOWS_TV_SERVICE_DB", "/data/windows_tv_service.sqlite3"))
ADMIN_USER = os.environ.get("WINDOWS_TV_ADMIN_USER", "")
ADMIN_PASSWORD = os.environ.get("WINDOWS_TV_ADMIN_PASSWORD", "")
security = HTTPBasic(auto_error=False)
_attempts: dict[str, list[float]] = {}


def now() -> datetime:
    return datetime.now(timezone.utc)


def stamp(value: datetime | None = None) -> str:
    return (value or now()).isoformat(timespec="seconds")


def db_connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables() -> None:
    with db_connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS registration_requests (
                id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                contact TEXT NOT NULL DEFAULT '',
                reason TEXT NOT NULL DEFAULT '',
                device_id TEXT NOT NULL,
                app_version TEXT NOT NULL DEFAULT '',
                app_variant TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS activation_codes (
                code_hash TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                redeemed_at TEXT NOT NULL DEFAULT '',
                revoked_at TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS device_grants (
                id TEXT PRIMARY KEY,
                request_id TEXT NOT NULL,
                device_id TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked_at TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)


@router.on_event("startup")
def registration_startup() -> None:
    ensure_tables()


class RegistrationRequestIn(BaseModel):
    display_name: str = Field(min_length=1, max_length=80)
    contact: str = Field(default="", max_length=254)
    reason: str = Field(default="", max_length=1000)
    # Generate a random persistent UUID locally. Never send hardware serial numbers.
    device_id: str = Field(min_length=16, max_length=80)
    app_version: str = Field(default="", max_length=40)
    app_variant: str = Field(default="", max_length=20)


class RedeemCodeIn(BaseModel):
    code: str = Field(min_length=12, max_length=100)
    device_id: str = Field(min_length=16, max_length=80)


def require_registration_admin(credentials: HTTPBasicCredentials | None = Depends(security)) -> str:
    if not ADMIN_USER or not ADMIN_PASSWORD:
        raise HTTPException(status_code=503, detail="Betreiberzugang ist nicht konfiguriert.")
    if credentials is None:
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Basic"}, detail="Anmeldung erforderlich.")
    user_ok = hmac.compare_digest(credentials.username.encode(), ADMIN_USER.encode())
    pass_ok = hmac.compare_digest(credentials.password.encode(), ADMIN_PASSWORD.encode())
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Basic"}, detail="Anmeldung fehlgeschlagen.")
    return credentials.username


def rate_limit(request: Request, key: str, max_count: int, seconds: int) -> None:
    now_mono = time.monotonic()
    entries = [t for t in _attempts.get(key, []) if now_mono - t < seconds]
    if len(entries) >= max_count:
        raise HTTPException(status_code=429, detail="Zu viele Versuche. Bitte später erneut versuchen.")
    entries.append(now_mono)
    _attempts[key] = entries


@router.post("/api/registration-requests", status_code=201)
def create_registration(payload: RegistrationRequestIn, request: Request) -> dict:
    ensure_tables()
    ip = request.client.host if request.client else "unknown"
    rate_limit(request, "register:" + ip, 5, 3600)
    if payload.app_variant not in {"", "basis", "standard"}:
        raise HTTPException(status_code=422, detail="Unbekannte Installationsvariante.")
    request_id = "FTR-" + uuid4().hex[:12].upper()
    created = stamp()
    with db_connect() as db:
        db.execute(
            """INSERT INTO registration_requests
            (id, display_name, contact, reason, device_id, app_version, app_variant, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
            (request_id, payload.display_name.strip(), payload.contact.strip(), payload.reason.strip(),
             payload.device_id.strip(), payload.app_version.strip(), payload.app_variant, created, created),
        )
    return {
        "accepted": True,
        "request_id": request_id,
        "status": "pending",
        "message": "Anfrage gespeichert; eine Freigabe ist damit noch nicht erteilt.",
        "created_at": created,
    }


@router.get("/api/registration-requests/{request_id}")
def registration_status(request_id: str, request: Request) -> dict:
    # The public status response deliberately exposes no contact or device data.
    ensure_tables()
    with db_connect() as db:
        row = db.execute(
            "SELECT id, status, created_at, updated_at FROM registration_requests WHERE id=?",
            (request_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Registrierungsanfrage nicht gefunden.")
    return dict(row)


@router.get("/admin/api/registration-requests", dependencies=[Depends(require_registration_admin)])
def list_registration_requests(status: str = "pending") -> dict:
    ensure_tables()
    if status not in {"pending", "approved", "rejected", "all"}:
        raise HTTPException(status_code=400, detail="Ungültiger Filter.")
    with db_connect() as db:
        if status == "all":
            rows = db.execute("SELECT * FROM registration_requests ORDER BY created_at DESC LIMIT 200").fetchall()
        else:
            rows = db.execute("SELECT * FROM registration_requests WHERE status=? ORDER BY created_at DESC LIMIT 200", (status,)).fetchall()
    return {"items": [dict(row) for row in rows], "count": len(rows)}


@router.post("/admin/api/registration-requests/{request_id}/approve", dependencies=[Depends(require_registration_admin)])
def approve_registration(request_id: str, lifetime_days: int = 7) -> dict:
    ensure_tables()
    if lifetime_days < 1 or lifetime_days > 30:
        raise HTTPException(status_code=400, detail="Die Codegültigkeit muss zwischen 1 und 30 Tagen liegen.")
    raw_code = secrets.token_urlsafe(24)
    code_hash = hashlib.sha256(raw_code.encode()).hexdigest()
    created = now()
    expires = created + timedelta(days=lifetime_days)
    with db_connect() as db:
        row = db.execute("SELECT id, status FROM registration_requests WHERE id=?", (request_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Registrierungsanfrage nicht gefunden.")
        if row["status"] != "pending":
            raise HTTPException(status_code=409, detail="Nur offene Anfragen können freigegeben werden.")
        db.execute(
            "INSERT INTO activation_codes (code_hash, request_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
            (code_hash, request_id, stamp(expires), stamp(created)),
        )
        db.execute("UPDATE registration_requests SET status='approved', updated_at=? WHERE id=?", (stamp(created), request_id))
    # Show this once to the authenticated operator; do not log or store the plaintext.
    return {"approved": True, "request_id": request_id, "activation_code": raw_code, "expires_at": stamp(expires), "note": "Code jetzt sicher an den Tester übermitteln; er wird nicht erneut im Klartext angezeigt."}


@router.post("/admin/api/registration-requests/{request_id}/reject", dependencies=[Depends(require_registration_admin)])
def reject_registration(request_id: str) -> dict:
    ensure_tables()
    with db_connect() as db:
        row = db.execute("SELECT status FROM registration_requests WHERE id=?", (request_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Registrierungsanfrage nicht gefunden.")
        if row["status"] != "pending":
            raise HTTPException(status_code=409, detail="Nur offene Anfragen können abgelehnt werden.")
        db.execute("UPDATE registration_requests SET status='rejected', updated_at=? WHERE id=?", (stamp(), request_id))
    return {"rejected": True, "request_id": request_id}


@router.post("/api/activation/redeem")
def redeem_activation_code(payload: RedeemCodeIn, request: Request) -> dict:
    ensure_tables()
    ip = request.client.host if request.client else "unknown"
    rate_limit(request, "redeem:" + ip, 10, 900)
    code_hash = hashlib.sha256(payload.code.strip().encode()).hexdigest()
    now_value = now()
    with db_connect() as db:
        code = db.execute("SELECT * FROM activation_codes WHERE code_hash=?", (code_hash,)).fetchone()
        if not code or code["redeemed_at"] or code["revoked_at"]:
            raise HTTPException(status_code=400, detail="Code ungültig, bereits verwendet oder widerrufen.")
        try:
            expires = datetime.fromisoformat(code["expires_at"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Code ungültig.")
        if expires <= now_value:
            raise HTTPException(status_code=400, detail="Code abgelaufen.")
        req = db.execute("SELECT * FROM registration_requests WHERE id=?", (code["request_id"],)).fetchone()
        if not req or req["status"] != "approved" or req["device_id"] != payload.device_id.strip():
            raise HTTPException(status_code=400, detail="Code ist nicht für dieses freigegebene Gerät bestimmt.")
        grant_id = "FTG-" + uuid4().hex
        grant_expiry = now_value + timedelta(days=30)
        db.execute("UPDATE activation_codes SET redeemed_at=? WHERE code_hash=?", (stamp(now_value), code_hash))
        db.execute(
            "INSERT INTO device_grants (id, request_id, device_id, expires_at, created_at) VALUES (?, ?, ?, ?, ?)",
            (grant_id, req["id"], req["device_id"], stamp(grant_expiry), stamp(now_value)),
        )
    return {"activated": True, "grant_id": grant_id, "expires_at": stamp(grant_expiry), "message": "Testgerät freigeschaltet."}


@router.get("/api/activation/{grant_id}")
def check_activation(grant_id: str, request: Request) -> dict:
    ensure_tables()
    with db_connect() as db:
        row = db.execute("SELECT expires_at, revoked_at FROM device_grants WHERE id=?", (grant_id,)).fetchone()
    if not row:
        return {"active": False, "reason": "unknown_grant"}
    if row["revoked_at"]:
        return {"active": False, "reason": "revoked"}
    try:
        expires = datetime.fromisoformat(row["expires_at"])
    except ValueError:
        return {"active": False, "reason": "invalid_expiry"}
    if expires <= now():
        return {"active": False, "reason": "expired"}
    return {"active": True, "expires_at": row["expires_at"]}
