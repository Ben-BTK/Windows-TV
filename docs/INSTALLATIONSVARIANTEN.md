# Installationsvarianten

## Verbindliche Grundregel

Es gibt genau zwei vereinbarte Varianten. Sie sind keine unterschiedlichen Funktions- oder Designeditionen.

### 1. Basisinstallation

- Enthält den normalen Windows-TV-Anwendungskern.
- Enthält dieselben Oberflächen, Designs, Kernfunktionen und Fehlerbehebungen wie die Standardinstallation.
- Enthält keine integrierte öffentliche GitHub-Schnittstelle.
- Gemeinsame Updates werden über veröffentlichte Pakete bzw. manuell bereitgestellte Installationsdateien übernommen.
- Jedes neue gemeinsame Design und jede gemeinsame Funktionsverbesserung muss auch für die Basisinstallation bereitgestellt werden.

### 2. Standardinstallation

- Enthält denselben Anwendungskern und dieselben Designs wie die Basisinstallation.
- Enthält zusätzlich eine öffentliche GitHub-Schnittstelle für Update-Prüfung und Dienststatus.
- Prüft beim Start und danach alle 24 Stunden auf veröffentlichte Updates; manuelle Prüfung bleibt verfügbar.
- Fragt den öffentlichen Dienststatus beim Start und danach alle fünf Minuten ab.
- Die Update-Prüfung zeigt eine neue Veröffentlichung an, installiert sie aber nicht automatisch.

## Gemeinsame Releases

1. Änderung entwickeln und gemeinsame Tests ausführen.
2. Eine gemeinsame Versionsnummer und Änderungsübersicht festlegen.
3. Gemeinsames Programm-/Designupdate veröffentlichen.
4. Installationspaket für die Basisinstallation bereitstellen.
5. Dieselbe Programmversion für die Standardinstallation bereitstellen und Release-Metadaten veröffentlichen.

Die Varianten dürfen nicht auseinanderlaufen. Ein Update darf nicht ausschließlich für die Standardinstallation erscheinen, wenn es das gemeinsame Design oder den gemeinsamen Anwendungskern betrifft.

## Dienststatus und Funktionssperren

Die Standardinstallation liest `status/service-status.json`. Die Datei unterstützt diese Modi:

- `normal`
- `limited_service`
- `scheduled_maintenance`
- `maintenance`
- `outage`
- `acute_outage`

Zulässige Einträge in `locked_features` sind `source_import`, `playback`, `favorites` und `all`. Wenn bei `maintenance` oder `acute_outage` keine Sperre angegeben ist, werden standardmäßig alle Kernfunktionen gesperrt. Bei `scheduled_maintenance` wird standardmäßig der Quellenimport gesperrt; bei `outage` die Wiedergabe. Explizite Sperren in der Statusdatei überschreiben diese Standardwerte. Stoppen bleibt immer möglich.

Beispiel für eine Wartungsmeldung:

```json
{
  "mode": "maintenance",
  "title": "Geplante Wartung",
  "message": "Die Quellenverwaltung wird gewartet.",
  "locked_features": ["source_import"],
  "starts_at": "2026-10-10 22:00 UTC",
  "ends_at": "2026-10-10 22:30 UTC",
  "updated_at": "2026-10-10T21:50:00Z",
  "announcement": ""
}
```

Wenn die Statusdatei nicht erreichbar oder ungültig ist, wird keine neue Funktionssperre aktiviert. Diese Statusabfrage ist Teil der Standardinstallation; die Basisinstallation enthält keine öffentliche GitHub-Schnittstelle, behält aber denselben gemeinsamen Design- und Funktionsstand.

## Installer und aktueller Stand

Der Inno-Setup-Installer enthält genau zwei Auswahlmöglichkeiten: **Basisinstallation** und **Standardinstallation**. Er installiert die Anwendung systemweit in den Programmordner und schreibt die gewählte Variante in eine lokale `variant.txt`. Die automatische Update-Prüfung lädt keine Programmdateien herunter und installiert keine Updates selbstständig. Der Installer wird über GitHub Actions gebaut; ein veröffentlichter Release muss zusätzlich angelegt werden.
