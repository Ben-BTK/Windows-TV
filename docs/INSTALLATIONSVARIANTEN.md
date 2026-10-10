# Installationsvarianten

## Verbindliche Grundregel

Es gibt genau zwei vereinbarte Varianten. Sie sind keine unterschiedlichen Funktions- oder Designeditionen.

### 1. Basisinstallation

- Enthält den normalen Windows-TV-Anwendungskern.
- Enthält dieselben Oberflächen, Designs, Kernfunktionen und Fehlerbehebungen wie die Standardinstallation.
- Enthält keine integrierte öffentliche GitHub-Schnittstelle.
- Updates werden über veröffentlichte Pakete bzw. manuell bereitgestellte Installationsdateien übernommen.
- Jedes neue gemeinsame Design und jede gemeinsame Funktionsverbesserung muss auch für die Basisinstallation bereitgestellt werden.

### 2. Standardinstallation

- Enthält denselben Anwendungskern und dieselben Designs wie die Basisinstallation.
- Enthält zusätzlich eine öffentliche GitHub-Schnittstelle für freigegebene Projektinformationen und Update-Prüfungen.
- Im aktuellen Prototyp kann die Schnittstelle nach öffentlichen GitHub-Releases suchen und die Versionsinformation anzeigen.
- Automatischer Download und Installation von Updates sind noch nicht implementiert.

## Gemeinsame Release-Pipeline

1. Änderung entwickeln.
2. Gemeinsame Tests für Anwendung und Design durchführen.
3. Eine gemeinsame Versionsnummer und Änderungsübersicht festlegen.
4. Das gemeinsame Programm-/Designupdate für beide Varianten veröffentlichen.
5. Für die Basisinstallation ein manuell installierbares Paket bereitstellen.
6. Für die Standardinstallation zusätzlich Update-Metadaten über die öffentliche GitHub-Schnittstelle bereitstellen.

Die Varianten dürfen nicht auseinanderlaufen. Ein Update darf nicht ausschließlich für die Standardinstallation erscheinen, wenn es das gemeinsame Design oder den gemeinsamen Anwendungskern betrifft.

## Aktueller Stand

Die Laufzeit-Auswahl ist für den Quellcode über `WINDOWS_TV_VARIANT=basis` oder `WINDOWS_TV_VARIANT=standard` vorgesehen. Der fertige Windows-Installer mit Auswahl der beiden Varianten ist noch nicht erstellt.
