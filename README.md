# Windows TV

**Vorläufiger technischer Repository-Name:** Windows TV  
**Interner bzw. späterer Produktname:** noch offen. „Viewora TV“ ist lediglich ein Namensvorschlag und wird vor einer Veröffentlichung rechtlich geprüft.

Windows TV ist ein lokaler Windows-Client zum Verwalten und Wiedergeben unterstützter Netzwerk-TV- und Streamquellen. Das Projekt befindet sich im frühen Prototyp-Stadium. Es wird zunächst nur Quellcode veröffentlicht; eine fertige `.exe` wird nicht vorgetäuscht.

## Installationsvarianten

Beide Varianten verwenden denselben Anwendungskern, dieselben Funktionen und dieselben Design- und Funktionsupdates.

- **Basisinstallation:** reguläre Anwendung ohne integrierte öffentliche GitHub-Schnittstelle. Sie erhält dieselben Kern-, Design- und Funktionsupdates wie die Standardinstallation; Updates werden manuell über veröffentlichte Pakete bezogen und installiert.
- **Standardinstallation:** dieselbe Anwendung mit zusätzlicher öffentlicher GitHub-Schnittstelle für Projektinformationen und die Prüfung verfügbarer Updates. Die Schnittstelle zeigt Veröffentlichungen an; automatische Installation ist noch nicht implementiert.

Die Varianten dürfen **keine getrennten Designstände** entwickeln. Ein Design- oder Funktionsupdate wird zuerst gemeinsam entwickelt und getestet und danach für beide Varianten bereitgestellt.

## Prototyp 0.1

- Windows-GUI
- M3U- und M3U8-Playlists von einer URL oder aus einer lokalen Playlist-Datei importieren
- Playlist technisch abrufen und Einträge parsen
- Sender suchen und nach Gruppe filtern
- Favoriten lokal speichern
- unterstützte Netzwerkstreams abspielen
- verständliche Meldungen bei nicht unterstützten oder nicht erreichbaren Streams
- in der Standardvariante: automatische Update-Prüfung beim Start und danach alle 24 Stunden sowie manuelle Prüfung
- aktueller Prototyp: Statusabfrage über eine öffentliche Statusdatei ist vorhanden; die vollständige zentrale Wartungs- und Meldestelle ist noch nicht implementiert

**Keine lokalen Videodateien:** MP4, MKV, AVI und vergleichbare Dateien sind keine Wiedergabequellen dieser Anwendung. Eine lokale M3U/M3U8-Datei ist nur eine Sender-/Quellenliste, keine Videodatei.

Externe Streamingdienste, DRM-Umgehung, Bezahlzugangs-Umgehung, vollständiges EPG und Kinderbereich gehören nicht zum ersten Prototyp. Die Update-Prüfung informiert über veröffentlichte Releases, installiert Updates aber nicht automatisch.

## Zentrale Service- und Rückmeldestelle

Geplant ist eine zentrale Stelle für **beide** Installationsvarianten. Sie soll Wartungs- und Störungsstatus veröffentlichen und eine Schnittstelle für Kritik, Feedback und spontane Störungsmeldungen bereitstellen. Dazu gehört auch ein geschützter Betreiberbereich zur Bearbeitung der Meldungen.

Die Basisinstallation soll diese Service-Schnittstelle erreichen können, ohne eine integrierte öffentliche GitHub-Oberfläche zu erhalten. Die Standardinstallation darf zusätzlich die GitHub-Schnittstelle für Projektinformationen und Update-Prüfungen nutzen.

**Wichtig:** Die vollständige Backend-API, die Feedback-/Störungsübermittlung und die geschützte Verwaltungsoberfläche sind noch nicht implementiert. Eine statische GitHub-Statusdatei allein kann diese Aufgaben nicht übernehmen. Die Anforderungen und die geplante Architektur stehen in [docs/SERVICE-UND-FEEDBACKSTELLE.md](docs/SERVICE-UND-FEEDBACKSTELLE.md).

## Entwicklung

Voraussetzung: Python 3.11 oder neuer.

```powershell
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -e .
python -m windows_tv
```

Für die Basisvariante:
```powershell
$env:WINDOWS_TV_VARIANT = "basis"
python -m windows_tv
```

Für die Standardvariante:
```powershell
$env:WINDOWS_TV_VARIANT = "standard"
python -m windows_tv
```

## Aktueller Dienststatus-Prototyp

Die Standardinstallation liest derzeit `status/service-status.json` aus diesem öffentlichen Repository und fragt beim Start und danach alle fünf Minuten nach Änderungen. Unterstützte Modi sind `normal`, `limited_service`, `scheduled_maintenance`, `maintenance`, `outage` und `acute_outage`. Zulässige Sperren sind `source_import`, `playback`, `favorites` und `all`. Wenn die Statusdatei nicht erreichbar oder ungültig ist, wird keine neue Funktionssperre aktiviert.

Das ist nur der aktuelle Prototyp. Zielarchitektur ist ein zentraler HTTPS-Service, den beide Varianten für Status und Meldungen verwenden; die Standardinstallation behält zusätzlich die GitHub-Schnittstelle. Details zur bisherigen Statusverwaltung stehen in [docs/STATUSBETRIEB.md](docs/STATUSBETRIEB.md).

## Feedback und Störungsmeldungen

Für das geplante zentrale Meldewesen sind drei Wege vorgesehen: technische Störung, Kritik/Feedback und Funktionswunsch. Zielablauf, Datenschutzregeln und offene technische Anforderungen sind in [Feedback und Störungsmeldungen](docs/FEEDBACK-UND-STOERUNGSMELDUNGEN.md) beschrieben. **Die zentrale Live-Meldemaske ist noch nicht implementiert**; dafür wird ein gesicherter HTTPS-Dienst mit Verwaltungsoberfläche benötigt. Die Funktion soll später in Basis- und Standardinstallation gleichermaßen verfügbar sein.

## Quellen und Nutzungsrechte

Die technische Erreichbarkeit einer Playlist bedeutet nicht automatisch, dass alle darin verlinkten Inhalte zur Wiedergabe oder Weiterverbreitung freigegeben sind. Nutzer müssen erforderliche Rechte, Lizenzen und gültige Anbieterzugänge besitzen. Windows TV ist nicht dafür vorgesehen, Schutzmaßnahmen oder Bezahlschranken zu umgehen.

## Projektstatus

Früher Entwicklungsstand. Noch kein fertiges Installationspaket und keine verbindliche Freigabe für den späteren Produktnamen. Lizenzbedingungen für das Projekt müssen vor einer öffentlichen Codefreigabe bewusst festgelegt werden.
