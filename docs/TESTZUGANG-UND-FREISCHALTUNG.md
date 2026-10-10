# Geschlossener Testbetrieb und Freischaltung

## Ziel

Öffentliche Downloads dürfen vor der offiziellen Freigabe nicht versehentlich wie eine fertige, offene TV-Anwendung wirken. Die App soll zunächst sichtbar als geschlossener Testbetrieb starten: Schloss-Symbol, Hinweis auf Wartung bzw. noch nicht freigegebenen Testzugang und eine Möglichkeit, eine Freischaltung anzufragen.

Das ist ein kontrollierter Beta-Zugang, keine DRM- oder Kopierschutzgarantie. Da der Client-Quellcode öffentlich ist, könnte eine technisch versierte Person einen veränderten Build erstellen. Die Freischaltung steuert deshalb die offiziellen Builds und den offiziellen Service, nicht beliebige fremde Änderungen am Quellcode.

## Vorgeschlagener Ablauf

1. **Installation:** Die App lässt sich installieren und starten. Vor einer Freigabe erscheint eine klare Sperrseite mit Schloss-Symbol: „Windows TV ist noch nicht öffentlich freigegeben. Wartungsarbeiten / geschlossener Testbetrieb.“
2. **Anfrage:** Der Tester gibt freiwillig einen Anzeigenamen und optional eine Kontaktadresse sowie eine kurze Begründung an. Die Anfrage wird nur mit Zustimmung übertragen. Keine Playlist-URLs, Stream-Inhalte, Kameraadressen, Passwörter oder privaten Dateien werden übermittelt.
3. **Prüfung durch den Betreiber:** Die Anfrage landet im geschützten Betreiberbereich und bleibt zunächst „Ausstehend“. Der Betreiber kann sie genehmigen oder ablehnen.
4. **Einmaliger Freischaltcode:** Bei Genehmigung wird ein kryptografisch zufälliger, einmalig verwendbarer Code mit kurzer Ablaufzeit erzeugt. Er wird dem Tester über einen bewusst gewählten Kontaktweg mitgeteilt. Codes werden serverseitig nicht im Klartext gespeichert und können widerrufen werden.
5. **Aktivierung:** Der Tester gibt den Code in der App ein. Der Server prüft Code, Ablaufzeit und Verwendungsstatus und tauscht ihn gegen eine gerätebezogene, widerrufbare Freigabe aus. Die App speichert die Freigabe lokal geschützt.
6. **Widerruf und Ablauf:** Der Betreiber kann eine Freigabe sperren. Bei erreichbarem Service wird die Freigabe regelmäßig geprüft. Bei nicht erreichbarem Service bleibt die App im geschlossenen Testmodus, solange noch keine gültige lokale Freigabe vorliegt; bereits freigegebene lokale Funktionen sollen bei einem vorübergehenden Ausfall nicht abrupt abbrechen.
7. **Freigabe später:** Der Betreiber kann den allgemeinen Testzugang oder einzelne Funktionen zentral öffnen/schließen, ohne für jede Statusmeldung eine neue App-Version veröffentlichen zu müssen.

## Sicherheitsregeln

- Keine gemeinsame feste Passphrase in den Client oder ins öffentliche Repository einbauen. Ein festes Passwort wäre in einem öffentlichen Client auslesbar und ließe sich nach Verbreitung kaum kontrollieren.
- Betreiber-Anmeldung, Code-Erzeugung und Freigabeentscheidungen erfolgen ausschließlich serverseitig. Betreiberpasswörter und API-Geheimnisse dürfen niemals in der App oder in GitHub eingecheckt werden.
- Freischaltcodes müssen zufällig, zeitlich begrenzt, einmalig verwendbar, rate-limitiert und serverseitig widerrufbar sein. Codes nicht in normalen Logs speichern.
- Der öffentliche Client darf keinen Administratorzugang enthalten. Das Admin-Panel muss HTTPS, starke Authentifizierung, CSRF-Schutz und Missbrauchsschutz nutzen.
- Testanfragen und Kontaktdaten sind vertrauliche Daten. Sie gehören ausschließlich in die geschützte Datenbank, nicht in GitHub-Issues, öffentliche Statusdateien, Commit-Inhalte oder Build-Artefakte. Vor Livebetrieb sind Datenschutzhinweise, Löschfrist und Kontaktweg festzulegen.
- Die zentrale Sperre betrifft nur die offiziellen Windows-TV-Testfunktionen. Ein Ausfall des Service darf keine persönlichen Daten übertragen oder lokale Einstellungen löschen. Künftige Kamera-/Video-Sessions müssen einen getrennten Funktionspfad behalten und dürfen nicht durch den allgemeinen TV-Wartungsstatus beendet werden.
- Die App muss bei fehlendem Server verständlich erklären, dass der Zugang nicht bestätigt werden kann. Sie darf niemals behaupten, eine Anfrage oder Aktivierung sei erfolgreich, wenn der Server dies nicht bestätigt hat.

## Externe TV-Signalquelle und Linux-Basissystem

Die Signalquellen-Anbindung ist eine optionale Integration. Windows TV soll beim Fehlen, bei einer Umbenennung, Sperrung oder Löschung eines externen GitHub-Projekts weiterhin starten. Dann zeigt die App „Signalquelle derzeit nicht verfügbar“ und erlaubt lokale Einstellungen bzw. das manuelle Importieren einer eigenen M3U/M3U8-Liste, soweit der Testzugang diese Funktionen freigibt.

Vor der Integration ist zu klären, welches Linux-Basissystem bereits existiert, welche Schnittstelle es anbietet und welche Lizenz-/Nutzungsbedingungen für externe Quellen gelten. Die Signalquelle darf nicht als zwingende Laufzeitabhängigkeit eingebaut werden. Falls sie später verschwindet, soll ein austauschbarer Adapter entfernt oder ersetzt werden können, ohne den Kern der App neu zu schreiben.

## Hosting und nächster Schritt

Für den kleinen zentralen Testzugang kann Cloudflare Workers mit D1 als mögliche kostenlose Einstiegsvariante geprüft werden. Dafür ist ein Cloudflare-Konto erforderlich; der Worker und die Datenbank müssen eingerichtet und bereitgestellt werden. Eine eigene Domain ist zum Start nicht zwingend, weil Workers eine workers.dev-Adresse bereitstellen kann. Ein kostenloser Tarif hat Grenzen und ist keine Verfügbarkeitsgarantie.

Offizielle Anleitung: https://developers.cloudflare.com/d1/get-started/
Konto: https://dash.cloudflare.com/sign-up
Limits: https://developers.cloudflare.com/workers/platform/limits/

Die derzeitige FastAPI-/SQLite-Service-Grundlage im Ordner service/ ist noch nicht öffentlich bereitgestellt und läuft nicht automatisch durch das Hinzufügen dieser Dokumentation. Für Cloudflare muss entweder ein kompatibler Worker-/D1-Service implementiert oder ein anderer dauerhafter Host eingerichtet werden. Vor der Freischaltungsfunktion ist dieser Hostingweg auszuwählen und zu testen.

## Status

Diese Datei legt die Anforderungen und den vorgeschlagenen Ablauf fest. Der vollständige Anfrage-/Genehmigungs-/Code-Aktivierungsprozess ist noch nicht als produktive Funktion verfügbar und darf nicht als bereits live dargestellt werden.