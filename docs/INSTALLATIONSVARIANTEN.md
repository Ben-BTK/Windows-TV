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

1. Änderung entwickeln und gemeinsame Tests ausführen.
2. Eine gemeinsame Versionsnummer und Änderungsübersicht festlegen.
3. Das gemeinsame Programm-/Designupdate für beide Varianten veröffentlichen.
4. Für die Basisinstallation ein manuell installierbares Paket bereitstellen.
5. Für die Standardinstallation zusätzlich Update-Metadaten über die öffentliche GitHub-Schnittstelle bereitstellen.

Die Varianten dürfen nicht auseinanderlaufen. Ein Update darf nicht ausschließlich für die Standardinstallation erscheinen, wenn es das gemeinsame Design oder den gemeinsamen Anwendungskern betrifft.

## Installer

Der Inno Setup-Installer enthält genau zwei Auswahlmöglichkeiten: **Basisinstallation** und **Standardinstallation**. Er installiert die Anwendung systemweit in den Programmordner und schreibt die gewählte Variante in eine lokale `variant.txt`. Die Standardvariante blendet die manuelle GitHub-Updateprüfung ein; die Basisvariante nicht.

## Aktueller Stand

Die Installerdefinition und ein GitHub Actions Build sind vorbereitet. Ein fertiger Installer liegt erst vor, wenn der Windows-Build erfolgreich durchgelaufen ist und das Build-Artefakt veröffentlicht wurde. Die Updateprüfung zeigt nur öffentliche Release-Informationen an; sie installiert noch keine Updates automatisch.
