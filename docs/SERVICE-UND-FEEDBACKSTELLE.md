# Zentrale Service- und Rückmeldestelle

## Ziel

Windows TV benötigt eine zentrale, übergeordnete Service-Stelle für **beide** Installationsvarianten. Die Basisinstallation bleibt ohne integrierte öffentliche GitHub-Oberfläche, muss aber dieselben allgemeinen Service-Möglichkeiten wie die Standardinstallation erreichen können.

Die bestehende öffentliche Datei `status/service-status.json` ist nur ein Prototyp für eine Statusquelle. Sie ist noch keine vollständige Verwaltungsoberfläche, kein Meldungseingang und kein Backend.

## Nutzer-Schnittstellen

Die Anwendung soll einen gut auffindbaren Bereich **Hilfe & Rückmeldung** anbieten, sowohl in der Basis- als auch in der Standardinstallation:

1. **Kritik und Feedback**
   - Lob, Kritik, Verbesserungsideen und Wünsche
   - Kategorie und kurze Betreffzeile
   - Freitext mit sinnvoller Zeichenbegrenzung
   - optionaler Rückkontakt; standardmäßig keine Kontaktdaten verlangen
2. **Störung melden**
   - Auswahl von Problemtyp: Startfehler, Oberfläche hängt, Quellenimport, Wiedergabe, Favoriten/Einstellungen, Update/Installation, Sonstiges
   - Schweregrad: Funktion eingeschränkt, zentrale Funktion ausgefallen, Programm startet nicht
   - Beschreibung und optionaler Zeitpunkt
   - optionaler technischer Diagnosebericht, der vor dem Versand angezeigt und vom Nutzer bestätigt wird
   - niemals Playlist-URLs, Zugangsdaten, persönliche Dateien oder andere sensible Inhalte ohne ausdrückliche, separate Zustimmung mitsenden
3. **Meldungsbestätigung**
   - nach erfolgreicher Übermittlung eine Referenznummer anzeigen
   - deutlich anzeigen, wenn keine Verbindung besteht und die Meldung nicht übermittelt wurde
   - später optionalen Status der Meldung über Referenznummer anbieten; dafür ist ein passender Backend-Endpunkt erforderlich

Eine Störungsmeldung ist kein Notruf und garantiert keine sofortige Reaktion. Dies muss vor dem Absenden verständlich stehen.

## Zentrale Verwaltungsoberfläche

Ein geschützter Betreiberbereich soll folgende Funktionen bieten:

- Service-Status und Wartungsankündigungen bearbeiten
- Störungen und Rückmeldungen in einer gemeinsamen Inbox ansehen
- Meldungen kategorisieren, priorisieren, zusammenführen und als neu/in Bearbeitung/gelöst markieren
- interne Notizen getrennt von nutzerseitigen Antworten führen
- Meldungen bei Bedarf beantworten, sofern Rückkontakt vorliegt
- öffentliche Statusmeldung aus einer bestätigten Störung ableiten, ohne persönliche Meldungsinhalte zu veröffentlichen
- Änderungsverlauf für Statusänderungen und administrative Aktionen führen

Nur berechtigte Betreiber dürfen den Status ändern oder Meldungen verwalten. Die öffentliche Statusquelle darf keine geheimen Daten enthalten.

## Technische Architektur

- Ein zentraler HTTPS-Service stellt den aktuellen Dienststatus bereit und nimmt Feedback- und Störungsmeldungen über getrennte API-Endpunkte entgegen.
- Beide Installationsvarianten nutzen dieselbe öffentliche Status-URL und dieselben Melde-Endpunkte. Das Vorhandensein einer GitHub-Oberfläche darf darüber nicht entscheiden.
- Die Standardinstallation darf zusätzlich die öffentliche GitHub-Schnittstelle für Projektinformationen und Update-Prüfungen verwenden.
- Die Basisinstallation bleibt ohne integrierte öffentliche GitHub-Schnittstelle. Sie darf jedoch den zentralen Service aufrufen, wenn der Nutzer Status oder Meldungen öffnet bzw. die Statusabfrage aktiviert ist.
- GitHub Pages bzw. eine statische JSON-Datei allein kann keine sicheren, vertraulichen Meldungen entgegennehmen oder eine geschützte Inbox bereitstellen. Dafür ist ein Backend mit Datenspeicherung, Zugriffsschutz und Missbrauchsschutz nötig.
- Keine Geheimnisse, Tokens oder Zugangsdaten in den Client einbetten. Anonyme Einsendungen müssen durch Rate-Limits, Eingabevalidierung und Spam-Schutz abgesichert werden.
- Bei nicht erreichbarem Service bleibt die App grundsätzlich nutzbar; die Oberfläche zeigt den Verbindungsfehler an. Eine nicht bestätigte Meldung darf niemals als erfolgreich versendet angezeigt werden.
- Für Sperren gilt: Ein lokaler Client kann eine zentrale Sperre nur empfangen, solange er den Dienst erreichen kann. Der Dienststatus darf nicht als DRM oder als Ersatz für lokale Fehlerbehandlung verwendet werden.

## Datenschutz und Sicherheit

- Datensparsamkeit: Kontaktangaben sind optional und standardmäßig nicht erforderlich.
- Vor dem Senden eines Diagnoseberichts dessen Inhalt sichtbar machen und eine ausdrückliche Bestätigung verlangen.
- Keine Passwörter, Tokens, Stream-Zugangsdaten oder vollständigen privaten Playlists erfassen.
- Lösch- und Aufbewahrungsfristen, Datenschutzhinweise und verantwortliche Kontaktadresse müssen vor dem öffentlichen Betrieb festgelegt werden.
- Backend-Endpunkte müssen serverseitig validieren, Eingabegrößen begrenzen, Missbrauch begrenzen und vertrauliche Meldungen vor öffentlichem Zugriff schützen.
- Öffentliche Wartungsankündigungen nur aus freigegebenen, bereinigten Informationen erzeugen.

## Umsetzungsreihenfolge

1. API-Vertrag und Datenschutzanforderungen festlegen.
2. Zentralen Status-Endpunkt für beide Varianten einführen und die bisherige direkte GitHub-Statusabfrage ablösen.
3. Gemeinsame Hilfe-/Feedback-/Störungsmaske in beiden Varianten bereitstellen.
4. Backend für Meldungseingang, Referenznummern und geschützte Speicherung einrichten.
5. Geschützte Betreiber-Inbox und Statusverwaltung entwickeln.
6. Tests für Offline-Verhalten, Validierung, Datenschutz, Spam-Schutz und beide Installationsvarianten ergänzen.

## Aktueller Umsetzungsstand

Dieses Dokument legt die Anforderungen fest. Die vollständige zentrale Backend- und Betreiberoberfläche sowie die Übermittlung von Feedback und Störungsmeldungen sind **noch nicht implementiert**. Die bestehende Statusdatei bleibt vorerst ein einfacher Prototyp und darf nicht als vollständige Wartungsstelle bezeichnet werden.
