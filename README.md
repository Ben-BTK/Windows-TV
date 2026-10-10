# Windows TV

**Vorläufiger technischer Repository-Name:** Windows TV  
**Interner bzw. späterer Produktname:** noch offen. „Viewora TV“ ist lediglich ein Namensvorschlag und wird vor einer Veröffentlichung rechtlich geprüft.

Windows TV ist ein lokaler Windows-Client zum Verwalten und Wiedergeben unterstützter Netzwerk-TV- und Streamquellen. Das Projekt befindet sich im frühen Prototyp-Stadium. Es wird zunächst nur Quellcode veröffentlicht; eine fertige `.exe` wird nicht vorgetäuscht.

## Installationsvarianten

Beide Varianten verwenden denselben Anwendungskern, dieselben Funktionen und dieselben Design- und Funktionsupdates.

- **Basisinstallation:** reguläre Anwendung ohne integrierte öffentliche GitHub-Schnittstelle. Sie erhält dieselben Kern-, Design- und Funktionsupdates wie die Standardinstallation; Updates werden manuell über veröffentlichte Pakete bezogen und installiert.
- **Standardinstallation:** dieselbe Anwendung mit zusätzlicher öffentlicher GitHub-Schnittstelle für Projektinformationen und die Prüfung verfügbarer Updates. Die Schnittstelle zeigt Veröffentlichungen an; automatische Installation ist noch nicht implementiert.

Die Varianten dürfen **keine getrennten Designstände** entwickeln. Ein Design- oder Funktionsupdate wird zuerst gemeinsam entwickelt und getestet und danach für beide Varianten bereitgestellt. Die Standardvariante darf zusätzliche Online-Komfortfunktionen besitzen; die Basisvariante darf dadurch nicht auf ältere Designs oder Kernfunktionen festgelegt werden.

## Prototyp 0.1

- Windows-GUI
- M3U- und M3U8-Playlists von einer URL oder aus einer lokalen Playlist-Datei importieren
- Playlist technisch abrufen und Einträge parsen
- Sender suchen und nach Gruppe filtern
- Favoriten lokal speichern
- unterstützte Netzwerkstreams abspielen
- verständliche Meldungen bei nicht unterstützten oder nicht erreichbaren Streams
- in der Standardvariante: automatische Update-Prüfung beim Start und danach alle 24 Stunden sowie manuelle Prüfung
- in der Standardvariante: Abruf einer öffentlichen Statusdatei beim Start und danach alle 5 Minuten
- sichtbare Wartungs-/Störungsanzeige mit konfigurierbaren Sperren für Wiedergabe, Quellenimport, Favoriten oder alle Kernfunktionen

**Keine lokalen Videodateien:** MP4, MKV, AVI und vergleichbare Dateien sind keine Wiedergabequellen dieser Anwendung. Eine lokale M3U/M3U8-Datei ist nur eine Sender-/Quellenliste, keine Videodatei.

Externe Streamingdienste, DRM-Umgehung, Bezahlzugangs-Umgehung, vollständiges EPG und Kinderbereich gehören nicht zum ersten Prototyp. Die Update-Prüfung informiert über veröffentlichte Releases, installiert Updates aber nicht automatisch. Die Basisinstallation hat keine integrierte öffentliche GitHub-Schnittstelle; sie erhält gemeinsame Design- und Kernupdates über manuell bereitgestellte Pakete.

## Entwicklung

Voraussetzung: Python 3.11 oder neuer.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
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

## Dienststatus und Funktionssperren

Die Standardinstallation liest `status/service-status.json` aus diesem öffentlichen Repository. Sie fragt beim Start und danach alle fünf Minuten nach Änderungen. Die Anzeige kann geplante Wartung, laufende Wartung, eingeschränkten Dienst, Ausfall oder akute Störung melden. Über `locked_features` lassen sich Quellenimport, Wiedergabe, Favoriten oder alle Kernfunktionen vorübergehend sperren. Die Schaltfläche zum Stoppen der Wiedergabe bleibt verfügbar.

Beispiele für `mode`: `normal`, `limited_service`, `scheduled_maintenance`, `maintenance`, `outage`, `acute_outage`. Zulässige Sperren: `source_import`, `playback`, `favorites`, `all`. Bei einem Wartungsmodus ohne ausdrücklich angegebene Sperren werden sichere Standardwerte angewendet. Wenn die Statusdatei nicht erreichbar ist, wird keine neue Sperre aktiviert.

Die Basisinstallation fragt keine öffentliche GitHub-Schnittstelle ab. Sie verwendet aber denselben gemeinsamen Programm- und Designstand; gemeinsame Updates werden für beide Varianten bereitgestellt.

## Quellen und Nutzungsrechte

Die technische Erreichbarkeit einer Playlist bedeutet nicht automatisch, dass alle darin verlinkten Inhalte zur Wiedergabe oder Weiterverbreitung freigegeben sind. Nutzer müssen erforderliche Rechte, Lizenzen und gültige Anbieterzugänge besitzen. Windows TV ist nicht dafür vorgesehen, Schutzmaßnahmen oder Bezahlschranken zu umgehen.

## Projektstatus

Früher Entwicklungsstand. Noch kein fertiges Installationspaket und keine verbindliche Freigabe für den späteren Produktnamen. Lizenzbedingungen für das Projekt müssen vor einer öffentlichen Codefreigabe bewusst festgelegt werden.
