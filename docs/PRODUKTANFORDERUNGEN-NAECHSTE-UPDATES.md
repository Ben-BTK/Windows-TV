# FlemmauTV – festgehaltene Produktanforderungen für die nächsten Ausbauschritte

**Status:** verbindliche Konzept- und Umsetzungsanforderungen; nicht als bereits implementierte Funktionen verstehen.  
**Versionsregel:** Dieses Dokument ändert weder die Versionsnummer in `pyproject.toml` noch die angezeigte App-Version oder einen bestehenden Release-Tag.  
**Produkt:** FlemmauTV  
**Repository:** `Ben-BTK/Windows-TV`

Dieses Dokument fasst die zuletzt gemeinsam besprochenen Anforderungen zusammen. Bei der Umsetzung sind vorhandene Funktionen und Tests zu prüfen, Änderungen klein und nachvollziehbar zu halten und die Anwendung nach jeder Änderung zu testen.

## 1. Installations- und Update-Architektur

### 1.1 EXE als technische Basis

- Die Windows-Setup-Datei (vorgesehener Name: `FlemmauTV-Setup.exe`) stellt zunächst die technische Basis bereit: Installer, Startfähigkeit, sichere Update-Prüfung und die Möglichkeit, benötigte Komponenten kontrolliert nachzuladen.
- Die EXE bzw. das installierte Grundmodul ist nicht automatisch mit dem vollständigen, dauerhaft aktuellen Funktionsumfang gleichzusetzen.
- Nach der Installation soll die Anwendung – sofern eine Internetverbindung besteht – die vorgesehenen eigentlichen Programmkomponenten bzw. das Standardmodul aus einer offiziellen Quelle laden können.
- Die Basisinstallation und die Standardvariante sollen einen gemeinsamen Kern und einen gemeinsamen Designstand nutzen. Unterschiede zwischen Varianten müssen ausdrücklich dokumentiert und auf notwendige Funktionen beschränkt sein.
- Ein Nachladen ausführbaren Codes darf erst umgesetzt werden, wenn ein sicherer Update-Mechanismus vorhanden ist: HTTPS, authentische Herausgeber-/Signaturprüfung, Integritätsprüfung (z. B. SHA-256), sichere Ablage, Versions-/Kompatibilitätsprüfung, atomarer Austausch, Rollback bei Fehlern und verständliche Fehlermeldungen. Niemals ungeprüften Code aus einer beliebigen URL ausführen.
- Wenn Download, Prüfung oder Verbindung scheitert, darf die Anwendung nicht in eine Endlosschleife geraten. Sie soll die letzte gültige Version weiterverwenden, soweit das sicher möglich ist, und einen verständlichen Status anzeigen.
- Offline-Verhalten, Wiederholungsversuche, Speicherplatzprüfung, Abbruchmöglichkeit und Wiederherstellung nach einem fehlgeschlagenen Update müssen getestet werden.

### 1.2 Update-Suche beim Programmstart

- In der Standardvariante wird beim Start der Anwendung nach Möglichkeit sofort auf verfügbare Updates geprüft, sobald Internetzugang besteht.
- Ist der Rechner beim Start offline, wird die Prüfung später erneut versucht, sobald Verbindung verfügbar ist; eine Offline-Situation darf die lokale Bedienung nicht unnötig blockieren.
- Zusätzlich bleibt eine manuelle Update-Prüfung verfügbar.
- Nach dem Start kann eine regelmäßige erneute Prüfung erfolgen; die genaue Frequenz soll konfigurierbar bzw. dokumentiert sein.
- Ein gefundenes Update wird außerhalb des automatischen Wartungsfensters nicht stillschweigend installiert. Der Dialog bietet **„Ja“** (jetzt installieren) und **„Nein“** (später).
- Geplante automatische Installation: ausschließlich zwischen **01:00 und 04:00 Uhr Ortszeit**, nur bei bestehender Internetverbindung und nach erfolgreicher Signatur-/Integritätsprüfung. Wenn der Rechner offline ist oder die Prüfung fehlschlägt, wird die Installation verschoben. Kein ungefragter Neustart des Computers.
- Automatische Installation muss sich sicher deaktivieren lassen. Ein Update darf die Zustimmung zu neuen Bedingungen nicht umgehen.

### 1.3 Designupdates ohne Änderung der Produktversionsnummer

- Die Oberfläche darf auch zwischen größeren Funktionsversionen ein Designupdate erhalten.
- Ein reines Designupdate soll nicht zwingend die sichtbare Produktversionsnummer erhöhen müssen. Trotzdem muss intern ein Build-/Paketstand oder eine Designrevision eindeutig nachvollziehbar bleiben, damit Fehler eingegrenzt und problematische Updates zurückgerollt werden können.
- Die sichtbare Version darf bei dieser Dokumentationsänderung nicht geändert werden. Für spätere Code-/Paketupdates ist die Projekt-Versionierungsregel separat anzuwenden; nicht einfach unterschiedliche Binärdateien unter derselben ununterscheidbaren Paketkennung verteilen.
- Dunkles Design ist Standard; ein helles Design bleibt optional. Spätere saisonale Themen (z. B. Winter/Weihnachten, Ostern, Herbst, Tag der Deutschen Einheit, Silvester/Neujahr) sind optionale Erweiterungen und sollen manuell deaktivierbar sein.

## 2. TV-Wiedergabe, Testvideo und Größe

- Die Videofläche passt sich standardmäßig automatisch an den verfügbaren Wiedergabebereich an und bewahrt das Seitenverhältnis ohne Verzerrung.
- Manuelle Größenanpassung soll zusätzlich möglich sein; die automatische Anpassung bleibt der Standard.
- Vollbild und ein separates Wiedergabefenster sollen möglich sein, ohne versehentlich einen zweiten unabhängigen Stream zu starten oder den Wiedergabezustand unnötig zu verlieren.
- Das derzeit besprochene YouTube-Video (`JNl1_hRwpXE`) ist ausschließlich ein vorübergehendes Testvideo für Einbettung, Größenanpassung, Vollbild und Tastaturbedienung. Es ist kein dauerhaft vorgesehener Sender und muss vor dem regulären Produktbetrieb aus dem Testpfad entfernt oder ausdrücklich als Testfunktion gekennzeichnet bleiben.
- Der bereitgestellte iframe-Link lautet `https://www.youtube.com/embed/JNl1_hRwpXE?si=80ezd6IQFwfz5kbH`. Die Einbettung muss praktisch getestet werden; die Angabe des iframe-Codes allein beweist nicht, dass jede Wiedergabeumgebung das Video abspielen kann.
- Die derzeitige native Qt-Medienwiedergabe kann eine YouTube-Webseite nicht automatisch wie eine direkte Stream-URL wiedergeben. Falls Qt WebEngine oder eine andere Web-Komponente verwendet wird, müssen Abhängigkeiten und Laufzeitdateien in den Windows-Installer aufgenommen und in einer sauberen Windows-Umgebung getestet werden.
- Nur rechtmäßig erreichbare Quellen verwenden; keine DRM-, Abo- oder Bezahlschranken umgehen. Video-Lizenz und Einbettungsfreigabe sind vor Veröffentlichung zu prüfen.

## 3. Tastatur- und Mausbedienung

Die Tastenbelegung ist ein Zielkonzept und muss beim Implementieren mit der jeweiligen Qt-/Webplayer-Fokussteuerung abgeglichen werden.

| Taste | Vorgesehene Funktion |
|---|---|
| Pfeil hoch / runter | Vorheriger / nächster Sender |
| Pfeil links / rechts | Lautstärke leiser / lauter |
| Ziffern 0–9 und Numpad 0–9 | Direkte Senderwahl; mehrstellige Nummern kurz sammeln |
| Enter | Sendernummer sofort bestätigen |
| Backspace | Letzte Ziffer der noch nicht bestätigten Sendernummer löschen |
| Tab | Zwischen TV- und Kameramodus wechseln, nur wenn Kameramodus freigeschaltet und kein Eingabefeld aktiv ist |
| Escape | Zur Startseite zurückkehren; nicht ohne Rückfrage die Anwendung beenden |
| F5 | Aktuellen Sender/Inhalt erneut laden bzw. Verbindung neu aufbauen, ohne die ganze App neu zu starten |
| F7 | Hilfefenster mit Tastenkürzeln und Bedienerklärung öffnen |
| F12 | Eigenständiges Wiedergabefenster öffnen; nach Möglichkeit Wiedergabezustand übernehmen |
| Entf | Zwischen aktueller und zuletzt geöffneter Seite/Ansicht wechseln, sofern ein Seitenverlauf existiert |
| Druck / Print Screen | Innerhalb des geschützten Wiedergabemodus möglichst abfangen; zusätzlich den vorgesehenen Windows-Aufnahmeschutz nutzen |
| Mausklick auf Schloss-Symbol | Tastensperre ein-/ausschalten |

Weitere Regeln:
- Normale Ziffern und Numpad sollen gleichwertig funktionieren.
- Eine ungültige Sendernummer lässt den aktuellen Sender unverändert und zeigt eine kurze Rückmeldung.
- Sendernummern dürfen im Kameramodus nicht versehentlich den TV-Sender wechseln.
- Das Schloss-Symbol zeigt den Sperrzustand eindeutig (geschlossen/offen). Die Mausbedienung zum Entsperren bleibt möglich.
- Bei aktiver Tastensperre werden normale Bedienbefehle ignoriert. Eine definierte Entsperraktion bleibt verfügbar. Eingabefelder dürfen ihre notwendige Bedienbarkeit behalten.
- F5 muss abhängig von der Quelle korrekt reagieren; eine YouTube-Webansicht kann eigene Tastaturbefehle beanspruchen. Die globale FlemmauTV-Steuerung soll dabei nicht unvorhersehbar ausfallen.

## 4. Bildschirmaufnahme-Schutz und Kameraausnahme

### 4.1 Geschützter Wiedergabebereich

- Für normale TV-Wiedergabe, Videos, Bilder, pausierte Standbilder, Vollbild und ein separates Wiedergabefenster soll der Schutz für den eigentlichen Bild-/Wiedergabebereich gelten.
- Bei unterstützten Bildschirmaufnahmewegen soll der geschützte Bereich in der Aufnahme möglichst schwarz oder ausgeblendet sein. Die übrige Benutzeroberfläche kann weiterhin aufnehmbar bleiben, soweit das mit dem Schutzkonzept vereinbar ist.
- Unter Windows kann – nach Prüfung der konkreten Fensterarchitektur – `SetWindowDisplayAffinity` mit `WDA_EXCLUDEFROMCAPTURE` für ein geeignetes Fenster verwendet werden. Das muss auf unterstützten Windows-Versionen getestet werden.
- Die Drucktaste abzufangen reicht nicht aus. Der Fensterschutz und alle Modi (Vollbild, separates Fenster, Standbild, Video) müssen gesondert geprüft werden.
- Es darf nicht behauptet werden, dass sämtliche Aufnahmen unmöglich sind: Betriebssysteme, Aufnahmeprogramme, Remote-Desktop, externe Capture-Hardware und Kameras können Einschränkungen umgehen oder anders arbeiten. Der Schutz ist eine technische Hürde, keine universelle Kopiersperre.
- Bei eingebettetem YouTube können Player- und Browserkomponenten eigene Beschränkungen haben; FlemmauTV kann nicht garantieren, jeden Aufnahmeweg dieses Drittanbieters zu kontrollieren.

### 4.2 Ausnahme für Webcam-/Überwachungsmodus

- Der Webcam-/Überwachungsmodus ist ausdrücklich vom Wiedergabe-Aufnahmeschutz ausgenommen, damit eine berechtigte Überwachungsaufnahme bzw. Speicherung funktionieren kann.
- Die Ausnahme gilt nur für den eindeutig aktiven und freigeschalteten Kamera-/Überwachungsmodus, nicht pauschal für normale TV-Wiedergabe.
- Berechtigungen, Zugriff auf Kamera/Mikrofon, Speicherziel, Aufzeichnungsstatus und Datenschutzinformationen müssen verständlich sein. Aufnahmen sollen nicht heimlich aktiviert werden.
- Beim Wechsel zwischen TV- und Kameramodus muss der Schutzstatus korrekt und sichtbar wechseln. Fehlerhafte oder nicht bestätigte Moduswechsel dürfen den geschützten TV-Bereich nicht versehentlich freigeben.

## 5. Nutzungs-, Datenschutz- und Änderungshinweise

### 5.1 Ersteinrichtung/Installation

- Bei Installation und Ersteinrichtung müssen die für die Nutzung erforderlichen Nutzungsbedingungen, Datenschutzinformationen, Sicherheits- und Funktionshinweise angezeigt werden.
- Zwischen **Kenntnisnahme**, **vertraglicher Zustimmung** und **datenschutzrechtlicher Einwilligung** muss unterschieden werden. Nicht jede Information erfordert eine Einwilligung; notwendige Einwilligungen dürfen nicht in einer pauschalen Zustimmung versteckt werden.
- Die erste Einrichtung soll zunächst einfach bleiben: Gerätenamen vergeben. Unnötige Extras, insbesondere eine nicht benötigte Kinderprogramm-Auswahl, gehören nicht in den ersten einfachen Einrichtungsschritt. Rechtlich erforderliche Hinweise müssen in denselben klaren Ablauf integriert oder davor/danach gezielt angezeigt werden.
- Die Bedingungen müssen lesbar und vor Bestätigung erreichbar sein. Ablehnen muss eine verständliche Folge haben; es darf nicht so getan werden, als hätte der Nutzer zugestimmt.

### 5.2 Änderungsklassen

Jede Änderung an Bedingungen/Hinweisen bekommt eine dokumentierte Klasse:

1. **Normale Änderung:** rein redaktionell oder ohne wesentliche Auswirkungen. Änderungsnotiz/Versionshistorie genügt in der Regel; kein unnötiges Unterbrechen der Nutzung.
2. **Wesentliche Änderung:** betrifft Rechte, Pflichten, Datenschutz, Berechtigungen, Aufzeichnung, Sicherheitsverhalten oder wesentliche Funktionen. Gezielte Anzeige und erneute Bestätigung, bevor die davon betroffenen Funktionen weiter genutzt werden, soweit rechtlich erforderlich.
3. **Besonders wichtige Ankündigung / kritische Änderung:** klarer, auffälliger Dialog mit Zusammenfassung und ausdrücklicher Bestätigung, wenn die Änderung die Zustimmung des Nutzers erfordert oder die sichere Nutzung sonst nicht gewährleistet werden kann.

### 5.3 Sonderregel für Webcam-/Überwachungsmodus

- Normale Änderungen, die den Überwachungsmodus nicht betreffen, sollen diesen Modus nicht allein durch eine allgemeine Aktualisierung unnötig unterbrechen.
- Änderungen, die Kamera, Überwachung, Aufzeichnung, Berechtigungen, Datenschutz oder Sicherheit dieses Modus betreffen, müssen gezielt angekündigt werden.
- Bei besonders wichtigen oder sicherheitskritischen Ankündigungen kann eine ausdrückliche Bestätigung auch für Nutzer des Überwachungsmodus erforderlich sein. Wenn eine zwingende Bestätigung aussteht, darf nur der betroffene Funktionsumfang weiterlaufen, soweit das rechtlich und technisch vertretbar ist.
- Die Ausnahmeregel ist kein Weg, notwendige Datenschutzinformationen, Einwilligungen oder sicherheitsrelevante Änderungen zu umgehen.

### 5.4 Protokoll und Ablehnung

- Die Anwendung hält nachvollziehbar fest, welche Fassung und welche Änderungsklasse angezeigt und bestätigt wurde sowie den Bestätigungszeitpunkt, soweit dafür eine zulässige Grundlage besteht.
- Keine stillschweigende Zustimmung allein durch Installation eines Updates oder bloße Weiternutzung, wenn ausdrückliche Zustimmung erforderlich ist.
- Dialoge enthalten verständliche Schaltflächen, beispielsweise **„Bestätigen“** und **„Ablehnen“**. Ein Ablehnen wird respektiert und führt zu einer klar erklärten Begrenzung oder Nichtverfügbarkeit der betroffenen Funktion – nicht zu einer irreführenden Zustimmung.
- Speicherung so datensparsam wie möglich; keine unnötigen Geräte- oder Nutzungsdaten protokollieren.

### 5.5 Hinweis zu unzulässigen Aufnahmen

Vorgeschlagener Hinweistext:

> **Hinweis zu Bildschirmaufnahmen**  
> Die Wiedergabe kann Inhalte enthalten, die urheberrechtlich oder datenschutzrechtlich geschützt sind. Unbefugte Aufzeichnungen, Vervielfältigungen oder Weitergaben können rechtswidrig sein. Bitte beachten Sie die geltenden Gesetze sowie die Rechte betroffener Personen und Rechteinhaber. Versuche, technische Schutzmaßnahmen zu umgehen, können rechtliche Folgen haben. Die Verantwortung für eigene Aufnahmen und deren Verwendung liegt bei der handelnden Person, soweit gesetzlich zulässig.

Der Hinweis ersetzt keine technische Schutzfunktion und keine rechtliche Prüfung. Nicht jede Aufnahme ist automatisch rechtswidrig; zulässige Verwendungszwecke und die ausdrücklich vorgesehene Kamera-/Überwachungsfunktion müssen berücksichtigt werden.

## 6. Gestaltung und erste Einrichtung

- Dunkelmodus ist der Standard. Ein optionaler heller Modus bleibt vorhanden.
- Die erste Einrichtung wird auf einen klaren Schritt zur Vergabe eines **Gerätenamens** reduziert. Das ist kein Personenname und kein Kontoname.
- Bei der nächsten vorgesehenen Einrichtungsversion soll der Einrichtungsdialog erneut erscheinen, wenn dafür eine echte Änderung des Setup-/Bedingungsstands erforderlich ist; nicht bei jedem Start.
- Die Oberfläche soll weniger Menüeinträge und eine klare Trennung zwischen TV-Wiedergabe, Kamera-/Überwachungsmodus, Einstellungen und Hilfe haben.
- F7 öffnet die Hilfe; die Tastenkürzel sind zusätzlich über die Oberfläche auffindbar.
- Designänderungen sollen möglichst mit denselben Komponenten für Basis- und Standardvariante umgesetzt werden.

## 7. Umsetzung und Testabnahme

Vor einer Freigabe müssen mindestens folgende Punkte getestet werden:

- Setup-EXE installiert die Basis zuverlässig auf einer sauberen Windows-Umgebung.
- Version/Anzeige bleibt bei rein dokumentarischen Änderungen unverändert.
- Update-Prüfung beim Online-Start, erneuter Versuch nach Offline-Start, Ja/Nein-Dialog, Zeitfenster 01:00–04:00, Integritätsprüfung und Fehler-/Rollback-Verhalten.
- Keine Ausführung ungeprüfter heruntergeladener Komponenten.
- Automatische und manuelle Playergrößen, Seitenverhältnis, Vollbild und separates Fenster.
- Testvideo wird nur im Testbetrieb angezeigt und kann eingebettet wiedergegeben werden.
- Jede Tastenkombination funktioniert im richtigen Modus; Eingabefelder, Tab-Navigation und Tastensperre bleiben bedienbar.
- Aufnahmeschutz wird für Video, Bild, Pause, Vollbild und separates Fenster unter den unterstützten Windows-Aufnahmewegen geprüft.
- Webcam-/Überwachungsmodus kann wie vorgesehen aufzeichnen und die Ausnahme greift ausschließlich dort.
- Installation, normale Änderungen, wesentliche Änderungen, kritische Ankündigungen und Ablehnung werden getestet; der Überwachungsmodus wird bei irrelevanten Änderungen nicht unnötig unterbrochen.
- Nach jedem Code-Commit werden passende Tests und der Windows-Installer-Build ausgeführt. Ein erfolgreicher Build gilt nicht allein als Nachweis, dass die Wiedergabe auf einem echten Gerät funktioniert.

## 8. Versionshinweis

Diese Datei dokumentiert Anforderungen und ändert keine Versionsnummer. Die Versionsnummer darf nicht heimlich erhöht oder umgeschrieben werden. Vorhandene Versionierung und Release-Tags bleiben unberührt. Interne Build-/Designrevisionen können ergänzend geführt werden, damit Designpakete und Fehler nachvollziehbar bleiben.

**Wichtig:** Alle hier genannten noch nicht implementierten Punkte müssen in Oberfläche, README, Release-Notizen und Tests klar als geplant/in Arbeit gekennzeichnet bleiben, bis sie tatsächlich umgesetzt und überprüft wurden.
