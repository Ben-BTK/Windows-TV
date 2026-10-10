# Installationsvarianten

## Verbindliche Grundregel

Es gibt genau zwei vereinbarte Varianten. Sie sind keine unterschiedlichen Funktions- oder Designeditionen.

### 1. Basisinstallation

- Enthält den normalen Windows-TV-Anwendungskern.
- Enthält dieselben Oberflächen, Designs, Kernfunktionen und Fehlerbehebungen wie die Standardinstallation.
- Enthält keine integrierte öffentliche GitHub-Schnittstelle.
- Updates werden über veröffentlichte Pakete bzw. manuell bereitgestellte Installationsdateien übernommen.
- Wird ein neues Design veröffentlicht, muss es auch für die Basisinstallation verfügbar sein.

### 2. Standardinstallation

- Enthält denselben Anwendungskern und dieselben Designs wie die Basisinstallation.
- Enthält zusätzlich eine öffentliche GitHub-Schnittstelle für freigegebene Projektinformationen und Update-Prüfungen.
- Darf Updates nach Bestätigung durch den Nutzer über die offizielle Veröffentlichungsquelle beziehen.
- Die Schnittstelle darf keine privaten Zugangsdaten oder persönlichen Dateien übertragen.

## Gemeinsame Release-Pipeline

1. Änderung entwickeln.
2. Gemeinsame Tests für Anwendung und Design durchführen.
3. Eine gemeinsame Versionsnummer und Änderungsübersicht festlegen.
4. Das gemeinsame Programm-/Designupdate für beide Varianten veröffentlichen.
5. Für die Basisinstallation ein manuell installierbares Paket bereitstellen.
6. Für die Standardinstallation zusätzlich Update-Metadaten über die öffentliche GitHub-Schnittstelle bereitstellen.

Die Varianten dürfen nicht auseinanderlaufen. Ein Update darf nicht ausschließlich für die Standardinstallation erscheinen, wenn es das gemeinsame Design oder den gemeinsamen Anwendungskern betrifft.

## Noch nicht umgesetzt

Diese Datei dokumentiert das vereinbarte Verhalten. Der automatische Updater und die beiden fertigen Windows-Installer sind noch nicht fertiggestellt. Das Repository enthält zunächst Quellcode.
