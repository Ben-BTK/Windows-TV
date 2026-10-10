from __future__ import annotations

import hmac
import os
import secrets
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import parse_qs
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

APP_TITLE = "Windows TV – zentrale Servicestelle"
DB_PATH = Path(os.environ.get("WINDOWS_TV_SERVICE_DB", "/data/windows_tv_service.sqlite3"))
ADMIN_USER = os.environ.get("WINDOWS_TV_ADMIN_USER", "")
ADMIN_PASSWORD = os.environ.get("WINDOWS_TV_ADMIN_PASSWORD", "")
ALLOWED_TYPES = {"incident", "feedback", "feature_request"}
ALLOWED_SEVERITIES = {"normal", "high", "critical"}
ALLOWED_STATUSES = {"new", "in_progress", "resolved"}
ALLOWED_MODES = {"normal", "limited_service", "scheduled_maintenance", "maintenance", "outage", "acute_outage"}
ALLOWED_LOCKS = {"all", "playback", "source_import", "favorites"}
security = HTTPBasic(auto_error=False)
app = FastAPI(title=APP_TITLE, docs_url=None, redoc_url=None)
_rate_buckets: dict[str, list[float]] = {}


class ReportIn(BaseModel):
    report_type: str
    subject: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=10, max_length=5000)
    severity: str = "normal"
    affected_feature: str = Field(default="", max_length=120)
    app_version: str = Field(default="", max_length=40)
    app_variant: str = Field(default="", max_length=20)
    contact: str = Field(default="", max_length=254)
    diagnostic_text: str = Field(default="", max_length=12000)
    website: str = Field(default="", max_length=200)  # honeypot; keep empty


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


@contextmanager
def db_session():
    conn = connect_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with db_session() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY, report_type TEXT NOT NULL, subject TEXT NOT NULL,
                description TEXT NOT NULL, severity TEXT NOT NULL, affected_feature TEXT NOT NULL,
                app_version TEXT NOT NULL, app_variant TEXT NOT NULL, contact TEXT NOT NULL,
                diagnostic_text TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'new',
                internal_note TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS service_status (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                mode TEXT NOT NULL, title TEXT NOT NULL, message TEXT NOT NULL,
                locked_features TEXT NOT NULL, updated_at TEXT NOT NULL
            )
        """)
        db.execute(
            "INSERT OR IGNORE INTO service_status VALUES (1, 'normal', 'Dienst verfügbar', '', '[]', ?)",
            (now_iso(),),
        )


@app.on_event("startup")
def startup() -> None:
    init_db()


def require_admin(credentials: HTTPBasicCredentials | None = Depends(security)) -> str:
    # Fail closed if deployment secrets were not configured.
    if not ADMIN_USER or not ADMIN_PASSWORD:
        raise HTTPException(status_code=503, detail="Betreiberzugang ist nicht konfiguriert.")
    if credentials is None:
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Basic"}, detail="Anmeldung erforderlich.")
    valid_user = hmac.compare_digest(credentials.username.encode(), ADMIN_USER.encode())
    valid_password = hmac.compare_digest(credentials.password.encode(), ADMIN_PASSWORD.encode())
    if not (valid_user and valid_password):
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Basic"}, detail="Anmeldung fehlgeschlagen.")
    return credentials.username


def limit_reports(request: Request) -> None:
    # Lightweight single-process guard. A public deployment must also enforce
    # rate limiting at its reverse proxy/WAF and use shared storage if multi-worker.
    host = request.client.host if request.client else "unknown"
    now = time.monotonic()
    bucket = [t for t in _rate_buckets.get(host, []) if now - t < 900]
    if len(bucket) >= 5:
        raise HTTPException(status_code=429, detail="Zu viele Meldungen. Bitte später erneut versuchen.")
    bucket.append(now)
    _rate_buckets[host] = bucket


def verify_csrf(request: Request, form_token: str) -> None:
    cookie_token = request.cookies.get("wt_csrf", "")
    if not cookie_token or not form_token or not hmac.compare_digest(cookie_token, form_token):
        raise HTTPException(status_code=403, detail="Ungültiges Formular-Token. Bitte die Seite neu laden.")


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "windows-tv-service", "time": now_iso()}


@app.get("/api/status")
def public_status() -> dict:
    with db_session() as db:
        row = db.execute("SELECT * FROM service_status WHERE singleton = 1").fetchone()
    import json
    return {
        "mode": row["mode"], "title": row["title"], "message": row["message"],
        "locked_features": json.loads(row["locked_features"]),
        "locks_explicit": True, "updated_at": row["updated_at"],
    }


@app.post("/api/reports", status_code=201)
def submit_report(payload: ReportIn, request: Request) -> dict:
    limit_reports(request)
    if payload.website.strip():
        # Return a generic response so the honeypot does not expose the check.
        raise HTTPException(status_code=400, detail="Meldung konnte nicht angenommen werden.")
    if payload.report_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=422, detail="Ungültige Meldekategorie.")
    if payload.severity not in ALLOWED_SEVERITIES:
        raise HTTPException(status_code=422, detail="Ungültiger Schweregrad.")
    if payload.app_variant not in {"", "basis", "standard"}:
        raise HTTPException(status_code=422, detail="Ungültige Installationsvariante.")
    report_id = "WT-" + uuid4().hex[:10].upper()
    created = now_iso()
    with db_session() as db:
        db.execute("""
            INSERT INTO reports
            (id, report_type, subject, description, severity, affected_feature,
             app_version, app_variant, contact, diagnostic_text, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id, payload.report_type, payload.subject.strip(), payload.description.strip(),
            payload.severity, payload.affected_feature.strip(), payload.app_version.strip(),
            payload.app_variant, payload.contact.strip(), payload.diagnostic_text.strip(), created, created,
        ))
    return {"accepted": True, "reference": report_id, "created_at": created}


def admin_page(title: str, body: str) -> HTMLResponse:
    token = secrets.token_urlsafe(24)
    html = f"""<!doctype html><html lang="de"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title><style>
body{{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:0 1rem;background:#15191f;color:#eef2f6}}
a{{color:#8bc7ff}}input,textarea,select,button{{font:inherit;padding:.55rem;margin:.2rem;background:#202731;color:#eef2f6;border:1px solid #526173;border-radius:5px}}
article{{border:1px solid #3a4553;border-radius:8px;padding:1rem;margin:1rem 0;overflow-wrap:anywhere}}
small{{color:#bdc7d3}}.row{{display:flex;gap:.5rem;flex-wrap:wrap}}label{{display:block;margin-top:.5rem}}
</style><h1>{escape(title)}</h1>{body}"""
    html = html.replace("__CSRF__", escape(token))
    response = HTMLResponse(html, headers={"Cache-Control": "no-store"})
    response.set_cookie("wt_csrf", token, httponly=True, secure=True, samesite="strict", max_age=1800)
    return response


@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request, _user: str = Depends(require_admin)) -> HTMLResponse:
    with db_session() as db:
        reports = db.execute("SELECT * FROM reports ORDER BY CASE status WHEN 'new' THEN 0 WHEN 'in_progress' THEN 1 ELSE 2 END, created_at DESC LIMIT 100").fetchall()
        status = db.execute("SELECT * FROM service_status WHERE singleton = 1").fetchone()
    import json
    status_options = "".join(f'<option value="{m}" {"selected" if status["mode"] == m else ""}>{m}</option>' for m in sorted(ALLOWED_MODES))
    lock_options = "".join(f'<label><input type="checkbox" name="locks" value="{lock}" {"checked" if lock in json.loads(status["locked_features"]) else ""}>{lock}</label>' for lock in sorted(ALLOWED_LOCKS))
    body = f"""<p>Letzte 100 Meldungen. Personenbezogene Angaben nicht öffentlich weitergeben.</p>
<article><h2>Öffentlicher Dienststatus</h2>
<form method="post" action="/admin/status">
<input type="hidden" name="csrf" value="__CSRF__">
<label>Modus <select name="mode">{status_options}</select></label>
<label>Titel <input name="title" maxlength="160" value="{escape(status["title"], quote=True)}" required></label>
<label>Meldung <textarea name="message" maxlength="2000" rows="3">{escape(status["message"])}</textarea></label>
<p>Funktionssperren:</p>{lock_options}<p><button>Öffentlichen Status speichern</button></p></form>
<small>Zuletzt geändert: {escape(status["updated_at"])}</small></article>"""
    for r in reports:
        body += f"""<article><h2>{escape(r["id"])} · {escape(r["subject"])}</h2>
<p><small>{escape(r["created_at"])} · Typ: {escape(r["report_type"])} · Schweregrad: {escape(r["severity"])} · Status: {escape(r["status"])}</small></p>
<p>{escape(r["description"]).replace(chr(10), "<br>")}</p>
<p><small>Bereich: {escape(r["affected_feature"])} · Version: {escape(r["app_version"])} · Variante: {escape(r["app_variant"])}</small></p>
{"<details><summary>Diagnosetext (vom Nutzer bewusst mitgesendet)</summary><pre>"+escape(r["diagnostic_text"])+"</pre></details>" if r["diagnostic_text"] else ""}
{"<p>Kontakt: "+escape(r["contact"])+"</p>" if r["contact"] else ""}
<form method="post" action="/admin/reports/{escape(r["id"], quote=True)}">
<input type="hidden" name="csrf" value="__CSRF__">
<label>Status <select name="status">{"".join(f'<option value="{s}" {"selected" if r["status"] == s else ""}>{s}</option>' for s in sorted(ALLOWED_STATUSES))}</select></label>
<label>Interne Notiz <textarea name="internal_note" maxlength="4000" rows="2">{escape(r["internal_note"])}</textarea></label>
<button>Meldung aktualisieren</button></form></article>"""
    return admin_page("Windows TV – Betreiberbereich", body)


@app.post("/admin/reports/{report_id}")
async def update_report(report_id: str, request: Request, _user: str = Depends(require_admin)) -> Response:
    form = parse_qs((await request.body()).decode("utf-8", errors="replace"))
    verify_csrf(request, form.get("csrf", [""])[0])
    status = form.get("status", ["new"])[0]
    note = form.get("internal_note", [""])[0][:4000]
    if status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=422, detail="Ungültiger Meldestatus.")
    with db_session() as db:
        cur = db.execute("UPDATE reports SET status=?, internal_note=?, updated_at=? WHERE id=?", (status, note, now_iso(), report_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Meldung nicht gefunden.")
    return RedirectResponse("/admin", status_code=303)


@app.post("/admin/status")
async def update_status(request: Request, _user: str = Depends(require_admin)) -> Response:
    form = parse_qs((await request.body()).decode("utf-8", errors="replace"))
    verify_csrf(request, form.get("csrf", [""])[0])
    mode = form.get("mode", ["normal"])[0]
    title = form.get("title", ["Dienststatus"])[0][:160].strip()
    message = form.get("message", [""])[0][:2000].strip()
    locks = list(dict.fromkeys(form.get("locks", [])))
    if mode not in ALLOWED_MODES or any(lock not in ALLOWED_LOCKS for lock in locks) or not title:
        raise HTTPException(status_code=422, detail="Ungültige Statusdaten.")
    import json
    with db_session() as db:
        db.execute(
            "UPDATE service_status SET mode=?, title=?, message=?, locked_features=?, updated_at=? WHERE singleton=1",
            (mode, title, message, json.dumps(locks), now_iso()),
        )
    return RedirectResponse("/admin", status_code=303)


# FlemmauTV provider catalogue.
# This is an API/data contract for the app and internal planning, not a public website
# and not a claim that these services are already technically integrated.
PROVIDER_CATALOG = [
    {"id": "m3u-m3u8", "name": "M3U/M3U8-Quellen", "category": "playlist", "access": "user_supplied", "status": "integrated", "integration": "playlist_import", "notes": "Unterstützte Senderlisten per URL oder lokaler Playlist-Datei."},
    {"id": "free-tv-sources", "name": "Kostenlose legale TV-Quellen", "category": "live_tv", "access": "free", "status": "planned", "integration": "source_adapter", "notes": "Nur kompatible Quellen mit geklärten Nutzungsrechten."},
    {"id": "epg", "name": "EPG- und Programmdaten", "category": "program_data", "access": "mixed", "status": "planned", "integration": "epg_adapter", "notes": "Abhängig von Verfügbarkeit, Format und Nutzungsrechten."},
    {"id": "disney-plus", "name": "Disney+", "category": "streaming", "access": "paid", "status": "planned", "integration": "official_app_or_api", "notes": "Noch nicht integriert; nur offizielle/erlaubte Zugriffswege, Abo erforderlich."},
    {"id": "netflix", "name": "Netflix", "category": "streaming", "access": "paid", "status": "planned", "integration": "official_app_or_api", "notes": "Noch nicht integriert; nur offizielle/erlaubte Zugriffswege, Abo erforderlich."},
    {"id": "sky", "name": "Sky", "category": "streaming", "access": "paid", "status": "planned", "integration": "official_app_or_api", "notes": "Noch nicht integriert; Angebot und Zugang je nach Region/Abo."},
    {"id": "magenta-tv", "name": "MagentaTV", "category": "tv_service", "access": "paid_or_bundle", "status": "planned", "integration": "official_app_or_api", "notes": "Noch nicht integriert; nur offizielle/erlaubte Zugriffswege."},
    {"id": "joyn", "name": "Joyn", "category": "streaming", "access": "mixed", "status": "planned", "integration": "official_app_or_api", "notes": "Noch nicht integriert; kostenloses und kostenpflichtiges Angebot unterscheiden."},
    {"id": "apple-tv", "name": "Apple TV", "category": "streaming", "access": "paid_or_rental", "status": "planned", "integration": "official_app_or_api", "notes": "Noch nicht integriert; Abo/Kauf/Leihe je nach Inhalt."},
    {"id": "ard", "name": "ARD / Das Erste", "category": "broadcaster", "access": "free", "status": "planned", "integration": "official_app_or_stream", "notes": "Anbindung erst nach technischer und rechtlicher Prüfung."},
    {"id": "zdf", "name": "ZDF", "category": "broadcaster", "access": "free", "status": "planned", "integration": "official_app_or_stream", "notes": "Anbindung erst nach technischer und rechtlicher Prüfung."},
    {"id": "arte", "name": "ARTE", "category": "broadcaster", "access": "free", "status": "planned", "integration": "official_app_or_stream", "notes": "Anbindung erst nach technischer und rechtlicher Prüfung."},
    {"id": "3sat", "name": "3sat", "category": "broadcaster", "access": "free", "status": "planned", "integration": "official_app_or_stream", "notes": "Anbindung erst nach technischer und rechtlicher Prüfung."},
    {"id": "regional-local", "name": "Regionale und lokale Sender", "category": "broadcaster", "access": "mixed", "status": "planned", "integration": "source_adapter", "notes": "Nur verfügbare, kompatible und rechtmäßig nutzbare Quellen."},
]
PROVIDER_STATUSES = {"planned", "in_review", "integrated", "unavailable"}


@app.get("/api/providers", dependencies=[Depends(require_admin)])
def list_providers(category: str | None = None, status: str | None = None) -> dict:
    """Machine-readable provider catalogue; this endpoint does not provide playback."""
    if category and category not in {p["category"] for p in PROVIDER_CATALOG}:
        raise HTTPException(status_code=400, detail="Unbekannte Anbieter-Kategorie.")
    if status and status not in PROVIDER_STATUSES:
        raise HTTPException(status_code=400, detail="Ungültiger Anbieterstatus.")
    items = [
        p for p in PROVIDER_CATALOG
        if (not category or p["category"] == category) and (not status or p["status"] == status)
    ]
    return {
        "product": "FlemmauTV",
        "catalog_version": 1,
        "is_playback_endpoint": False,
        "items": items,
        "count": len(items),
        "notice": "Ein Katalogeintrag bedeutet nicht, dass der Anbieter bereits integriert oder abspielbar ist.",
    }


@app.get("/api/providers/{provider_id}", dependencies=[Depends(require_admin)])
def get_provider(provider_id: str) -> dict:
    """Return one provider's current planning/integration metadata."""
    provider = next((p for p in PROVIDER_CATALOG if p["id"] == provider_id), None)
    if provider is None:
        raise HTTPException(status_code=404, detail="Anbieter nicht gefunden.")
    return {"product": "FlemmauTV", "is_playback_endpoint": False, "provider": provider}
