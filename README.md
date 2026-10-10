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
- in der Standardvariante: manuelle Prüfung öffentlicher GitHub-Releases

**Keine lokalen Videodateien:** MP4, MKV, AVI und vergleichbare Dateien sind keine Wiedergabequellen dieser Anwendung. Eine lokale M3U/M3U8-Datei ist nur eine Sender-/Quellenliste, keine Videodatei.

Externe Streamingdienste, DRM-Umgehung, Bezahlzugangs-Umgehung, vollständiges EPG, Kinderbereich und ein fertiger Installer gehören nicht zum ersten Prototyp.

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

## Quellen und Nutzungsrechte

Die technische Erreichbarkeit einer Playlist bedeutet nicht automatisch, dass alle darin verlinkten Inhalte zur Wiedergabe oder Weiterverbreitung freigegeben sind. Nutzer müssen erforderliche Rechte, Lizenzen und gültige Anbieterzugänge besitzen. Windows TV ist nicht dafür vorgesehen, Schutzmaßnahmen oder Bezahlschranken zu umgehen.

## Projektstatus

Früher Entwicklungsstand. Noch kein fertiges Installationspaket und keine verbindliche Freigabe für den späteren Produktnamen. Lizenzbedingungen für das Projekt müssen vor einer öffentlichen Codefreigabe bewusst festgelegt werden.
