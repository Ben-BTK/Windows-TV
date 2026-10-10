# Zentrale Service-API – technischer Stand

## Endpunkte

- `GET /health` – technischer Erreichbarkeitstest.
- `GET /api/status` – öffentlicher, maschinenlesbarer Dienststatus.
- `POST /api/reports` – neue Kritik, ein Feedback, Funktionswunsch oder eine Störung einreichen.
- `GET /admin` – geschützter Betreiberbereich: Meldungen sichten, Status und interne Notizen pflegen, öffentlichen Dienststatus verwalten.

Beispiel für `POST /api/reports` (JSON):

```json
{
  "report_type": "incident",
  "subject": "Wiedergabe startet nicht",
  "description": "Beim Start eines unterstützten Streams erscheint eine Fehlermeldung.",
  "severity": "normal",
  "affected_feature": "playback",
  "app_version": "0.1.0.dev0",
  "app_variant": "basis",
  "contact": "",
  "diagnostic_text": "",
  "website": ""
}
```

Erfolgreiche Übermittlung liefert HTTP 201 und eine Referenz, z. B. `WT-ABC1234567`. Eine Referenz wird nur nach dem Speichern zurückgegeben. Das ist noch keine Zusage zu Antwort- oder Bearbeitungszeiten.

## Lokaler Start zum Entwickeln

Im Ordner `service`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:WINDOWS_TV_SERVICE_DB = "$PWD\windows_tv_service.sqlite3"
$env:WINDOWS_TV_ADMIN_USER = "operator"
$env:WINDOWS_TV_ADMIN_PASSWORD = "replace-with-a-long-random-password"
uvicorn app:app --host 127.0.0.1 --port 8000
```

Danach `http://127.0.0.1:8000/health` und `http://127.0.0.1:8000/api/status` aufrufen. Der Adminbereich ist unter `/admin` verfügbar. Für lokales HTTP funktioniert das Secure-CSRF-Cookie nicht in allen Browsern; produktiv muss die Oberfläche ausschließlich über HTTPS laufen.

## Bereitstellung – Pflichtpunkte

1. Einen verwalteten Host/VPS mit dauerhaftem Speicher auswählen und eine eigene HTTPS-Domain konfigurieren.
2. Reverse Proxy mit TLS, Request-Größenlimit und Rate-Limit für `POST /api/reports` vorschalten. Port 8000 nicht direkt öffentlich freigeben.
3. `WINDOWS_TV_ADMIN_USER` und ein langes, zufälliges `WINDOWS_TV_ADMIN_PASSWORD` nur auf dem Host als Geheimnisse setzen. Niemals echte Zugangsdaten in Git committen.
4. Persistentes Volume für `/data` verwenden und verschlüsselte, zugriffsgeschützte Backups sowie Wiederherstellung testen.
5. Datenschutzhinweise, Verantwortlichen-/Kontaktangaben, Löschfristen und Betriebsüberwachung vor dem öffentlichen Start festlegen.
6. Vor Veröffentlichung mit Tests prüfen, dass HTTPS, Admin-Authentifizierung, CSRF-Schutz, Rate-Limits, Backups und Löschprozess funktionieren.

## Sicherheit und Grenzen

- Keine Client-Geheimnisse: der Client benötigt kein Betreiberpasswort.
- Der Backend-Code enthält Eingabegrenzen, eine Honeypot-Spalte, einfache In-Process-Begrenzung (maximal fünf Meldungen je Client-IP in 15 Minuten) und HTTP-Basic-Authentifizierung für den Betreiberbereich.
- Die In-Process-Begrenzung ist nur ein zusätzlicher Basisschutz. Sie ersetzt kein Reverse-Proxy-/WAF-Rate-Limit; mehrere Worker/Instanzen benötigen einen gemeinsamen Limiter.
- Die Meldungen werden zunächst in SQLite gespeichert. Der Datenträger und Backups enthalten vertrauliche Angaben, falls Nutzer Kontakt- oder Diagnosedaten eintragen.
- Diagnosedaten werden nicht automatisch aus dem Client ermittelt; sie werden nur gespeichert, wenn der Client sie ausdrücklich mitsendet.
- Der Adminbereich verwendet CSRF-Token und ein Secure-Cookie; er ist für HTTPS-Betrieb vorgesehen.
- Der Service versendet derzeit keine E-Mail-Benachrichtigungen und bietet noch keine öffentliche Statusabfrage einzelner Tickets.
- Diese Backend-Komponente ist noch nicht auf einem öffentlichen Host bereitgestellt und noch nicht in den Windows-TV-Client integriert. Daher gibt es aktuell noch keine produktive Live-Meldestelle.
