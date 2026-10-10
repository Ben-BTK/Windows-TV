# Feedback und spontane Störungsmeldungen

## Ziel

Windows TV benötigt eine zentrale Anlaufstelle für Rückmeldungen, Verbesserungsvorschläge und technische Störungen. Die Meldefunktion soll langfristig sowohl aus der Basisinstallation als auch aus der Standardinstallation erreichbar sein. Die Installationsvarianten bleiben dabei auf genau zwei beschränkt.

## Drei Meldearten

1. **Technische Störung** – Wiedergabefehler, Absturz, Importfehler, Fehler nach einem Update oder andere unerwartete Probleme.
2. **Kritik und Feedback** – Bedienbarkeit, Design, Verständlichkeit, Barrierefreiheit und allgemeine Nutzung.
3. **Verbesserungs- oder Funktionswunsch** – gewünschte Funktionen und konkrete Änderungsvorschläge.

## Felder der Meldemaske

Pflichtfelder:
- Meldeart
- Kurzer Betreff
- Beschreibung

Optionale Felder:
- Dringlichkeit: normal, hoch oder kritisch
- Betroffene Funktion
- Zeitpunkt des Auftretens
- Programmversion und Installationsvariante
- Fehlermeldung oder Diagnosebericht
- Kontaktmöglichkeit für Rückfragen
- Screenshot oder Logdatei, nach ausdrücklicher Auswahl durch den Nutzer

Die Oberfläche muss vor dem Absenden deutlich anzeigen, welche Daten übermittelt werden. Diagnoseinformationen dürfen keine Playlist-Inhalte, Zugangsdaten, Tokens oder andere Geheimnisse enthalten. Keine Dateien und keine personenbezogenen Angaben automatisch anhängen. Kontaktangaben sollen optional sein; anonyme Meldungen müssen möglich sein, sofern der gewählte Übermittlungsweg dies technisch unterstützt.

## Empfohlener Ablauf

1. Die Anwendung zeigt einen kurzen, verständlichen Meldeassistenten.
2. Bei Störungen kann sie nach Zustimmung technische Basisinformationen wie Version, Variante, Betriebssystem und eine bereinigte Fehlermeldung vorschlagen.
3. Nutzer prüft und bestätigt die Angaben vor dem Versand.
4. Die Meldung wird über einen zentralen HTTPS-Endpunkt an die Wartungsstelle übertragen.
5. Die Wartungsstelle vergibt eine Vorgangsnummer und ordnet die Meldung einer internen Kategorie zu.
6. Die zuständige Person prüft die Meldung und kann ihren Status auf „eingegangen“, „in Prüfung“, „Rückfrage“, „geplant“, „behoben“ oder „geschlossen“ setzen.
7. Falls eine Kontaktmöglichkeit hinterlegt wurde, kann eine Rückmeldung erfolgen. Ohne Kontaktmöglichkeit gibt es keine persönliche Statusbenachrichtigung.

## Trennung von Status und Meldesystem

Die öffentliche Statusdatei dient nur zur Anzeige von Wartung, Einschränkungen und Störungen. Sie darf keine eingereichten Meldungen enthalten. Eingehende Meldungen gehören in einen getrennten, zugriffsgeschützten Dienst mit Spam-Schutz, Größenlimits, Protokollierung und begrenzten Aufbewahrungsfristen.

Ein öffentlicher GitHub-Issue-Link kann für Nutzer geeignet sein, die selbst öffentlich diskutieren möchten. Er ist aber **kein** Ersatz für die zentrale Meldemaske: GitHub-Issues sind öffentlich sichtbar, benötigen ein passendes Konto und sind ungeeignet für private Diagnoseinformationen oder Kontaktdaten.

## Datenschutz und Sicherheit

- Vor dem Absenden transparent erklären, welche Daten übertragen werden und wofür sie gebraucht werden.
- Datenminimierung und kurze, festgelegte Aufbewahrungsfristen umsetzen.
- Keine Passwörter, Stream-Zugangsdaten, Tokens oder vollständigen Playlists übertragen.
- Uploads standardmäßig deaktiviert lassen und nur nach bewusster Auswahl ermöglichen.
- Eingaben serverseitig validieren, Spam und Missbrauch begrenzen und Übertragungen per HTTPS absichern.
- Eine Störungsmeldung darf niemals automatisch eine globale Funktionssperre auslösen. Sperren und Statusmeldungen werden getrennt und ausdrücklich durch die Wartungsverwaltung gesetzt.

## Noch notwendige technische Umsetzung

Dieses Dokument beschreibt den Zielablauf, nicht bereits vorhandene Live-Funktionalität. Für den tatsächlichen Versand wird ein zentraler HTTPS-Backend-Endpunkt mit Datenhaltung, geschützter Verwaltungsoberfläche und Missbrauchsschutz benötigt. Ein rein statisches GitHub-Repository kann Meldungen nicht sicher und zuverlässig entgegennehmen oder verwalten.

Die Basisinstallation soll den zentralen Meldedienst direkt erreichen können, ohne eine integrierte GitHub-Oberfläche zu erhalten. Die Standardinstallation darf zusätzlich Verweise auf öffentliche Projektinformationen anbieten. Beide Varianten nutzen dieselbe Meldelogik und dieselben Datenschutzregeln.
