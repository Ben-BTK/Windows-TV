# Datenschutz, öffentliche Repositorys und Kamerafunktion

## Grundregel für ein öffentliches GitHub-Repository

Alles, was committed oder als Datei/Artefakt öffentlich hochgeladen wird, kann von anderen gelesen und kopiert werden. Ein öffentliches Repository ist kein privater Datenspeicher. Deshalb gehören niemals folgende Inhalte hinein:

- Kamera- oder NVR-Adressen, Benutzername/Passwort, RTSP-URLs mit Zugangsdaten, API-Schlüssel oder Token;
- private M3U/M3U8-Listen, private Sender-/Kamera-URLs oder persönliche Favoriten-/Einstellungsdateien;
- Meldungen von Nutzern, E-Mail-Adressen, Diagnoselogs, Datenbankdateien, Sicherungen oder personenbezogene Informationen;
- produktive .env-Dateien und Betreiberpasswörter.

Die .gitignore-Datei schützt neue, noch nicht versionierte Dateien vor versehentlichem Hinzufügen. Sie macht bereits committete Dateien nicht rückwirkend privat und verhindert keine bewusste Veröffentlichung. Vor jedem Commit und vor öffentlichen Releases muss geprüft werden, welche Dateien tatsächlich enthalten sind. Falls ein Geheimnis versehentlich veröffentlicht wird, reicht Löschen allein nicht: Das Geheimnis muss sofort widerrufen/rotiert werden und gegebenenfalls muss der Git-Verlauf bereinigt werden.

GitHub-Commit-Metadaten können außerdem den Namen und die E-Mail-Adresse enthalten, die beim Commit verwendet wurden. Für öffentliche Projekte sollte eine GitHub-noreply-Adresse als Commit-E-Mail eingerichtet werden.

## Daten lokal und zentral trennen

- Die Wiedergabe und die lokalen Benutzer-Einstellungen sollen ohne den zentralen Service funktionieren.
- Persönliche Quellen, Kameraadressen und Zugangsdaten bleiben lokal und dürfen nie in die öffentliche Statusdatei oder in Statusabfragen gelangen.
- An die zentrale Meldestelle werden nur die vom Benutzer bewusst eingegebenen Meldeinhalte und die ausdrücklich ausgewählten optionalen Diagnoseinformationen übertragen.
- Keine automatische Übertragung von Playlist-Inhalten, Kamera-Streams, Kamera-Screenshots, Zugangsdaten oder lokalen Dateien.
- Die Meldedatenbank und Backups gehören ausschließlich auf den geschützten Hostingdienst, niemals in das Repository oder öffentliche Build-Artefakte.

## Zukünftige Kamera-/Videoübertragung

Die Kameraübertragung ist noch nicht implementiert. Bei ihrer späteren Entwicklung gelten folgende Regeln:

1. Wartungs- und Störungsstatus für TV-Playlists dürfen die Kamera-Funktion nicht sperren oder eine laufende Kamera-Session stoppen.
2. Die Kamera wird als eigenständiger Medienpfad mit eigenen Zuständen und Fehlern entwickelt.
3. Kameraübertragung wird nur durch eine ausdrückliche lokale Konfiguration aktiviert. Es gibt keine automatische Gerätesuche oder Veröffentlichung einer Kamera im Internet.
4. Zugangsdaten bleiben in einem geeigneten lokalen Geheimnisspeicher bzw. geschützten lokalen Konfigurationsspeicher; sie dürfen nicht im Klartext in Logs oder Fehlermeldungen landen.
5. Es darf keine Portfreigabe, kein öffentlicher Stream und keine Weiterleitung an den zentralen Service automatisch eingerichtet werden.
6. Für Fernzugriff sind Authentifizierung, verschlüsselte Übertragung und ein bewusst konfigurierter sicherer Zugriffsweg erforderlich. Das Programm darf eine Kamera nicht ohne Berechtigung erreichbar machen.
7. Der Nutzer muss erkennen können, wann eine Kamera verbunden ist bzw. sendet, und die Verbindung jederzeit selbst beenden können.

## Installationsvarianten und Designs

Basis- und Standardinstallation bleiben zwei Installationsvarianten mit demselben Anwendungskern. Die Wahl zwischen aktuellem und klassischem Oberflächendesign ist eine persönliche Benutzereinstellung, keine dritte Installationsvariante. Diese Wahl wird lokal gespeichert und darf weder in GitHub noch an den Service übertragen werden.
