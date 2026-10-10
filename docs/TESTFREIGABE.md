# Geschützte Testfreigabe für Windows-TV

## Ziel

Windows-TV darf für externe Windows-Tests installiert werden, obwohl die TV-Stream-Funktion noch nicht allgemein freigegeben ist. Die Anwendung muss den Status klar anzeigen und die gesperrte Funktion mit einem Schloss kennzeichnen.

## Vorgesehener Ablauf

1. Der Tester lädt ein ausdrücklich als **Testversion** gekennzeichnetes Installationspaket herunter und installiert es.
2. Beim Start erscheint ein Hinweis, dass die TV-Stream-Funktion noch nicht freigegeben ist und Wartungs-/Entwicklungsarbeiten stattfinden.
3. Die gesperrte Funktion zeigt ein Schloss und die Aktion **Freischaltung anfordern**.
4. Die Anfrage erzeugt eine Anfrage-ID. Die Anfrage darf keine privaten Playlist-URLs, Kameraadressen, Passwörter oder lokalen Dateien mitsenden. Kontaktangaben bleiben freiwillig.
5. Der Betreiber prüft und genehmigt die Anfrage. Der Tester erhält einen persönlichen, einmalig einlösbaren und zeitlich begrenzten Freischaltcode.
6. Windows-TV sendet den Code über HTTPS an den Freigabedienst. Nur der Server entscheidet, ob der Code gültig, unbenutzt, für diesen Test bestimmt und noch nicht abgelaufen ist.
7. Bei Erfolg erhält die Installation eine befristete Freigabe. Der Code selbst wird nicht als Klartext dauerhaft lokal gespeichert. Der Betreiber kann die Freigabe widerrufen oder auslaufen lassen.

## Sicherheitsanforderungen

- Keine fest eingebauten Betreiberpasswörter, Codes, privaten Schlüssel oder API-Schlüssel im Quellcode oder Installer.
- Codes müssen kryptografisch zufällig, begrenzt gültig und einmalig einlösbar sein; serverseitig nur als sicherer Hash speichern.
- Serverseitige Begrenzung von Anfragen und Codeversuchen; keine unbegrenzten Rate-Limits nur im Client.
- HTTPS für Anfragen und Freigabeprüfung.
- Der Client darf bei Nichterreichbarkeit des Freigabedienstes nicht behaupten, die Freigabe sei erteilt worden.
- Eine Service-/Wartungsstörung darf lokale Programmteile und bereits laufende lokale Wiedergabe nicht unnötig blockieren. Die gesperrte TV-Funktion bleibt jedoch gesperrt, solange keine gültige Freigabe vorliegt.
- Die spätere Kamera-/Kamerastream-Funktion ist ein eigener Funktionsbereich und darf nicht durch den TV-Stream-Wartungsstatus abgeschaltet werden.
- Keine Kamera- oder TV-Stream-URLs, Zugangsdaten, private Playlists, lokale Logs oder persönliche Einstellungen an GitHub senden.
- Testpakete klar als Vorabversion kennzeichnen. Tester sollen Fehler und Windows-Version melden können, aber keine privaten Stream-Zugangsdaten übermitteln.

## Status

Dies ist die verbindliche Anforderung für die nächste Implementierungsstufe, **keine Behauptung, dass die Freigabe bereits aktiv ist**. Die aktuelle App besitzt einen allgemeinen Status-/Wartungsbanner und eine vorbereitete Rückmeldemaske. Der Freischaltantrags-Workflow, die Codeverwaltung, die befristete Lizenz-/Testfreigabe und der öffentliche Freigabeserver müssen noch implementiert und getestet werden.

## Hosting für einen kostenlosen Prototyp

Empfohlener Start: Cloudflare Workers für die HTTPS-API und Cloudflare D1 für Anfragen, Status und Freigabecodes. Vor dem Livebetrieb sind Zugriffsschutz für den Betreiberbereich, Rate-Limits, Datenschutzinformationen, Löschfristen, Backups/Export und Tests erforderlich. Kostenlose Tarifgrenzen können sich ändern; bei ausgeschöpften Limits kann der Dienst vorübergehend keine Anfragen verarbeiten.

Offizielle Anleitung: https://developers.cloudflare.com/d1/get-started/

Die Einrichtung eines Cloudflare-Kontos allein veröffentlicht noch keinen Dienst. Erst nach Anlegen und Konfigurieren des Workers und der Datenbank, Einrichten der Secrets und Deployment existiert eine nutzbare HTTPS-Adresse. Diese Adresse muss anschließend bewusst in Windows-TV konfiguriert werden.
