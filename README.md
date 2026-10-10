# FlemmauTV

**Produktname:** FlemmauTV  
**Repository:** `Ben-BTK/Windows-TV` (der GitHub-Repository-Pfad bleibt vorerst unverändert; der sichtbare Produktname ist FlemmauTV).

FlemmauTV ist ein lokaler Windows-Client zum Verwalten und Wiedergeben unterstützter Netzwerk-TV- und Streamquellen. Das Projekt befindet sich im frühen Prototyp-Stadium. Es wird zunächst nur Quellcode veröffentlicht; eine fertige `.exe` wird nicht vorgetäuscht.

## Installationsvarianten

Beide Varianten verwenden denselben Anwendungskern, dieselben Funktionen und dieselben Design- und Funktionsupdates.

- **Basisinstallation:** reguläre Anwendung ohne integrierte öffentliche GitHub-Schnittstelle. Sie erhält dieselben Kern-, Design- und Funktionsupdates wie die Standardinstallation; Updates werden manuell über veröffentlichte Pakete bezogen und installiert.
- **Standardinstallation:** dieselbe Anwendung mit zusätzlicher öffentlicher GitHub-Schnittstelle für Projektinformationen und die Prüfung verfügbarer Updates. Die Schnittstelle zeigt Veröffentlichungen an; automatische Installation ist noch nicht implementiert.

Die Varianten dürfen **keine getrennten Designstände** entwickeln. Ein Design- oder Funktionsupdate wird zuerst gemeinsam entwickelt und getestet und danach für beide Varianten bereitgestellt. Unabhängig davon kann jeder Nutzer in der Anwendung lokal zwischen dem aktuellen dunklen und einem klassischen hellen Oberflächendesign wählen; diese Auswahl ist keine dritte Installationsvariante.

## Prototyp 0.1 – aktueller Funktionsumfang

- Windows-GUI
- M3U- und M3U8-Playlists von einer URL oder aus einer lokalen Playlist-Datei importieren
- Playlist technisch abrufen und Einträge parsen
- Sender suchen und nach Gruppe filtern
- Favoriten lokal speichern
- unterstützte Netzwerkstreams abspielen
- verständliche Meldungen bei nicht unterstützten oder nicht erreichbaren Streams
- in der Standardvariante: automatische Update-Prüfung beim Start und danach alle 24 Stunden sowie manuelle Prüfung
- aktueller Prototyp: Statusabfrage über eine öffentliche Statusdatei ist vorhanden; die vollständige zentrale Wartungs- und Meldestelle ist noch nicht produktiv bereitgestellt

**Keine lokalen Videodateien:** MP4, MKV, AVI und vergleichbare Dateien sind keine Wiedergabequellen dieser Anwendung. Eine lokale M3U/M3U8-Datei ist nur eine Sender-/Quellenliste, keine Videodatei.

Externe Streamingdienste, DRM-Umgehung, Bezahlzugangs-Umgehung, vollständiges EPG und Kinderbereich gehören nicht zum ersten Prototyp. Die Update-Prüfung informiert über veröffentlichte Releases, installiert Updates aber nicht automatisch.

## Geplante Erweiterungen – noch nicht als umgesetzt ansehen

Die folgenden Punkte sind festgehaltene Projektanforderungen, aber noch nicht vollständig implementiert:

- Allgemeine Serien- und Programmsuche über kompatible, erlaubte Senderlisten und Programmdaten; kostenlose Quellen sollen standardmäßig bevorzugt werden.
- Optionale Berücksichtigung kommerzieller Dienste wie Disney+, Netflix, Sky, MagentaTV, Joyn und Apple TV, soweit offizielle/erlaubte technische Anbindungen bestehen. Keine Umgehung von DRM, Abos oder Bezahlschranken.
- EPG-gestützte Serienfavoriten und Erinnerungen über Windows-Benachrichtigungen.
- Optionaler Hintergrunddienst nur nach ausdrücklicher Zustimmung während der persönlichen Einrichtung. Bei Zustimmung kann eine Hintergrundkomponente ohne sichtbares Hauptfenster mit Windows starten. Ablehnung darf die normale Wiedergabe nicht blockieren; Widerruf muss den Autostart wieder entfernen.
- Kinderprofil: grundsätzlich nur freigegebene Kinderkanäle; Das Erste und ZDF können am Wochenende für einen noch festzulegenden Zeitraum zusätzlich freigegeben werden. Zeitfenster und Senderliste sollen konfigurierbar sein.
- Saisonale Oberflächenthemen, etwa Weihnachten, Silvester und Ostern, mit manueller Abschaltmöglichkeit.
- Lokale Sicherung/Wiederherstellung persönlicher Einstellungen und Favoriten, soweit vom Nutzer gewünscht; Zugangsdaten müssen separat geschützt werden.
- Serverseitige Registrierung und kontrollierte Beta-Gerätefreigabe mit kurzlebigem Bestätigungscode. Die Gerätekennung soll zufällig sein und keine Hardware-Seriennummer ableiten. Datenschutz, Rechtsgrundlage, Löschfristen und Sicherheitsmaßnahmen sind vor Live-Betrieb festzulegen.
- Gemeinsame Status-, Wartungs- und Feedbackschnittstelle für beide Installationsvarianten; sie darf die lokale Wiedergabe nicht unnötig blockieren.

## Zentrale Service- und Rückmeldestelle

Die zentrale Service-Komponente für **beide** Installationsvarianten ist als Backend-Grundlage im Ordner `service/` angelegt: HTTPS-API für Dienststatus und Meldungen, SQLite-Speicherung, Referenznummern und ein geschützter Betreiberbereich. Die Anwendung enthält außerdem eine gemeinsame Hilfe-/Rückmeldemaske. Sie bleibt bis zur Konfiguration einer echten öffentlichen HTTPS-Serveradresse bewusst deaktiviert, damit keine Meldung fälschlich als versendet gilt.

Die Basisinstallation soll diese Service-Schnittstelle erreichen können, ohne eine integrierte öffentliche GitHub-Oberfläche zu erhalten. Die Standardinstallation darf zusätzlich die GitHub-Schnittstelle für Projektinformationen und Update-Prüfungen nutzen.

**Wichtig:** Der Backend-Code ist vorhanden, aber noch nicht auf einem öffentlichen Host bereitgestellt und noch nicht produktiv verbunden. Vor einem Live-Betrieb fehlen Hosting/HTTPS-Domain, produktive Sicherheitsprüfung und Datenschutz-/Löschangaben. Die Anleitung steht in [service/README.md](service/README.md); Architektur und Variantenregeln stehen in [docs/SERVICE-UND-FEEDBACKSTELLE.md](docs/SERVICE-UND-FEEDBACKSTELLE.md). Die geplante geschlossene Testfreigabe mit Freischaltungsanfrage und einmaligem Code ist in [docs/TESTZUGANG-UND-FREISCHALTUNG.md](docs/TESTZUGANG-UND-FREISCHALTUNG.md) beschrieben; der vollständige Ablauf ist noch nicht live.

## Entwicklung

Voraussetzung: Python 3.11 oder neuer.

```powershell
py -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
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

## Aktueller Dienststatus-Prototyp

Die Standardinstallation liest derzeit `status/service-status.json` aus diesem öffentlichen Repository und fragt beim Start und danach alle fünf Minuten nach Änderungen. Unterstützte Modi sind `normal`, `limited_service`, `scheduled_maintenance`, `maintenance`, `outage` und `acute_outage`. Zulässige Sperren sind `source_import`, `playback`, `favorites` und `all`. Wenn die Statusdatei nicht erreichbar oder ungültig ist, wird keine neue Funktionssperre aktiviert.

Das ist nur der aktuelle Prototyp. Zielarchitektur ist ein zentraler HTTPS-Service, den beide Varianten für Status und Meldungen verwenden; die Standardinstallation behält zusätzlich die GitHub-Schnittstelle. Details zur bisherigen Statusverwaltung stehen in [docs/STATUSBETRIEB.md](docs/STATUSBETRIEB.md).

## Feedback und Störungsmeldungen

Die gemeinsame Maske für technische Störung, Kritik/Feedback und Funktionswunsch ist in der App angelegt. Sobald `WINDOWS_TV_SERVICE_URL` auf die bereitgestellte HTTPS-Serveradresse zeigt, können beide Installationsvarianten Status und Meldeservice nutzen. Ohne diese Konfiguration bleibt das Senden deaktiviert. Ablauf und Datenschutzregeln stehen in [docs/FEEDBACK-UND-STOERUNGSMELDUNGEN.md](docs/FEEDBACK-UND-STOERUNGSMELDUNGEN.md).

## Quellen und Nutzungsrechte

Die technische Erreichbarkeit einer Playlist bedeutet nicht automatisch, dass alle darin verlinkten Inhalte zur Wiedergabe oder Weiterverbreitung freigegeben sind. Nutzer müssen erforderliche Rechte, Lizenzen und gültige Anbieterzugänge besitzen. FlemmauTV ist nicht dafür vorgesehen, Schutzmaßnahmen oder Bezahlschranken zu umgehen. Die Kompatibilität mit einer externen GitHub-Senderliste muss vor einer Integration technisch und anhand der Lizenzbedingungen geprüft werden.

## Projektstatus

Früher Entwicklungsstand. Der Produktname **FlemmauTV** ist festgelegt. Der GitHub-Repository-Pfad lautet aktuell weiterhin `Windows-TV`; ein tatsächliches Umbenennen des Repositorys ist ein separater GitHub-Schritt. Noch kein fertiges Installationspaket und keine produktive öffentliche Service-Homepage. Lizenzbedingungen für das Projekt müssen vor einer öffentlichen Codefreigabe bewusst festgelegt werden.

### Wartung und spätere Kamerastreams

Wartungsanzeigen dürfen die Video-/Kamerastream-Schnittstelle nicht blockieren. Eine spätere Kameraübertragung wird separat vom TV-Playlist-Wiedergabepfad umgesetzt; der zentrale Wartungsstatus darf eine aktive Medienwiedergabe nicht pauschal stoppen. Die dedizierte Kamerafunktion ist noch nicht implementiert. Anforderungen an öffentliche Repositorys, private Daten und Kamerasicherheit stehen in [docs/PRIVATSPHAERE-UND-KAMERA.md](docs/PRIVATSPHAERE-UND-KAMERA.md).

### Geschützte externe Testfreigabe

Die Anforderungen für eine spätere, passwort-/codegeschützte Testfreigabe der TV-Stream-Funktion sind in [docs/TESTFREIGABE.md](docs/TESTFREIGABE.md) dokumentiert. Der Freigabecode-Workflow und der öffentliche Freigabedienst sind noch nicht implementiert; ein Testpaket darf diesen Stand nicht als bereits aktiv darstellen.
