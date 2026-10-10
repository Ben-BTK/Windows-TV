# FlemmauTV – interne Anbieterübersicht und Schnittstelle

## Zweck und Abgrenzung

Diese Datei beschreibt die erste technische Anbieterschnittstelle für FlemmauTV. Sie ist für die App und interne Planung gedacht. Sie ist **keine Homepage** und keine öffentliche Werbe- oder Anbieterseite.

Der Katalog führt bereits integrierte, geplante und noch zu prüfende Anbieter gemeinsam auf. Ein Eintrag im Katalog bedeutet ausdrücklich nicht, dass der Dienst bereits erreichbar, lizenziert, abspielbar oder technisch integriert ist.

## API

### `GET /api/providers`

Gibt den vollständigen Katalog als JSON zurück.

Optionale Filter:
- `?category=streaming`
- `?status=planned`

Mögliche Kategorien sind aktuell `playlist`, `live_tv`, `program_data`, `streaming`, `tv_service` und `broadcaster`.

Mögliche Statuswerte:
- `integrated` – derzeit im Projekt technisch vorhanden (nur der bestehende M3U/M3U8-Import ist so markiert)
- `planned` – geplant, noch nicht integriert
- `in_review` – technische/rechtliche Prüfung läuft
- `unavailable` – derzeit nicht verfügbar

### `GET /api/providers/{provider_id}`

Gibt die Angaben für einen einzelnen Anbieter zurück. Unbekannte IDs liefern HTTP 404.

Diese Endpunkte sind **Katalog-/Metadaten-Endpunkte**, keine Stream-Proxy- oder Wiedergabe-Endpunkte. Sie geben keine Anbieterpasswörter, Cookies, Tokens oder Zugangsdaten zurück.

## Erste Katalogeinträge

- Bestehender M3U/M3U8-Import
- Kostenlose, rechtmäßig nutzbare TV-Quellen
- EPG-/Programmdaten
- Disney+
- Netflix
- Sky
- MagentaTV
- Joyn
- Apple TV
- ARD / Das Erste
- ZDF
- ARTE
- 3sat
- Regionale und lokale Sender

Die Liste ist erweiterbar. Weitere Anbieter sollen durch neue Datensätze hinzukommen können, ohne den API-Vertrag zu ändern.

## Kostenpflichtige Dienste

Disney+, Netflix, Sky, MagentaTV, Joyn und Apple TV sind als **geplant** erfasst. Sie sind aktuell noch nicht als direkte Wiedergabeintegration umgesetzt. Spätere Unterstützung hängt von offiziellen bzw. ausdrücklich erlaubten technischen Zugriffsmöglichkeiten ab. Ein gültiges Abo oder eine Anmeldung kann erforderlich sein. FlemmauTV darf keine DRM-, Anmelde- oder Bezahlschranken umgehen. Falls direkte Wiedergabe nicht unterstützt wird, ist ein Öffnen der offiziellen App/Webseite die vorgesehene Ausweichmöglichkeit.

## Regeln für spätere Erweiterungen

- Den Katalogstatus immer ehrlich aktualisieren; keine geplante Integration als verfügbar darstellen.
- Anbieterintegration über austauschbare Adapter entwickeln, statt Anbieterlogik fest in die allgemeine Suche einzubauen.
- Verfügbarkeit und rechtliche Nutzungsbedingungen vor der Integration prüfen.
- Keine persönlichen Kontodaten oder Zugangsdaten im Katalog, im Client-Quellcode oder in öffentlichen GitHub-Dateien speichern.
- Fehler eines Anbieters dürfen nicht den übrigen lokalen Player oder andere Anbieter blockieren.
- Kostenlose Quellen standardmäßig bevorzugen; kostenpflichtige Anbieter separat filterbar machen.

## Aktueller Stand

Die erste Katalog-API ist im Backend unter `service/app.py` implementiert. Sie ist noch nicht auf einem öffentlichen Host bereitgestellt. Die bestehenden Registrierungs-/Beta-Freigabeprozesse für Benutzer und Geräte sind davon getrennt und noch nicht vollständig produktiv implementiert.
