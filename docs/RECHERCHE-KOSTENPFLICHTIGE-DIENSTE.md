# FlemmauTV – vorläufige Recherche zu kostenpflichtigen Streamingdiensten

**Stand:** 10.10.2026  
**Zweck:** interne technische Recherche. Dieses Dokument ist ausdrücklich kein Anbieter-Katalog und fügt keine Anbieter zur App-Konfiguration hinzu.

## Vorläufige Erkenntnisse

- **Disney+:** Die öffentlich auffindbaren Nutzungsbedingungen untersagen unter anderem die Umgehung von DRM/Zugangsschutz und das Weiterverbreiten von Inhalten. Eine direkte Player-Integration darf deshalb nicht durch Reverse Engineering oder Schutzumgehung gebaut werden. Zuerst sind offizielle Partner-/Integrationswege zu klären. Falls kein genehmigter Weg verfügbar ist, kommt höchstens das Öffnen der offiziellen App/Webseite infrage.
- **Netflix:** Öffentlich dokumentierte Netflix-Partnerprogramme wie Open Connect betreffen primär die Bereitstellung/Netzwerkinfrastruktur für Internetanbieter, nicht eine frei nutzbare Consumer-Playback-API für beliebige Desktop-Player. Eine direkte Wiedergabeintegration ist daher nicht als verfügbar anzunehmen; Partnerfreigabe und offizielle Optionen müssen separat angefragt/geprüft werden.
- **Sky:** Öffentliche Hilfeseiten zeigen, dass Sky eigene Apps und Partner-Apps auf seinen Plattformen anbietet. Das ist kein Nachweis für eine frei nutzbare externe Wiedergabe-API für FlemmauTV. Vor einer direkten Integration ist eine schriftliche technische/vertragliche Klärung erforderlich.
- **MagentaTV:** Vorläufig offen. Es ist eine aktuelle offizielle Entwickler-/Partnerdokumentation und die Zulässigkeit eines Drittanbieter-Windows-Clients zu recherchieren. Ohne bestätigte Schnittstelle nicht als integrierbar behandeln.
- **Joyn:** Öffentlich auffindbare API-Dokumentation betrifft Joyn-Loyalty-/Partnerfunktionen (z. B. Treuepunkte), nicht erkennbar die Wiedergabe von TV-Inhalten. Nicht mit einer Streaming-Playback-API verwechseln.
- **Apple TV:** Apple dokumentiert Partnerintegrationen für die Apple-TV-App, darunter Katalog-/Verfügbarkeitsfeeds und App-APIs. Die Dokumentation ist an Partner-Apps und Apple-Plattformen gebunden und ist kein Beleg für eine universell nutzbare Windows-Wiedergabe-API für Fremddienste. Direkte Integration bleibt ungeklärt.

## Vorläufige Schlussfolgerung

1. Keine der genannten kostenpflichtigen Dienste wird aufgrund dieser ersten Recherche als direkt integriert markiert.
2. Die App soll später, soweit rechtlich und technisch möglich, offizielle Apps/Webseiten oder zulässige Deep Links öffnen können.
3. Für direkte Wiedergabe braucht jeder Anbieter eine eigene Prüfung: offizieller Partnerweg, Plattform-/OS-Unterstützung, Anmeldung und Abo, DRM/Content Protection, Nutzungsbedingungen, Metadaten-/Suchzugriff und Freigabe zur Weiterleitung aus einer Drittanbieter-App.
4. Keine Speicherung von Anbieterpasswörtern im FlemmauTV-Katalog oder Quellcode. Keine DRM-Umgehung, kein Scraping geschützter Kataloge und kein Abspielen über nicht genehmigte private Endpunkte.

## Erste Quellen (offizielle oder anbieternahe Dokumentation)

- Disney+ Subscriber Agreement: https://www.disneyplus.com/welcome/subscriber-agreement
- Netflix Open Connect (Partnerprogramm für Netzwerkinfrastruktur): https://openconnect.netflix.com/de_de/
- Sky – Apps auf Sky Stream und Sky Q: https://www.sky.de/pakete-produkte/apps
- Joyn API-Dokumentation: https://developer.joyn.eu/v1/
- Apple TV App – Integration für Partner: https://tvpartners.apple.com/support/3705-integrating-your-app-with-apple-tv-app
- Apple HTTP Live Streaming (allgemeines Streamingprotokoll, keine Berechtigung für geschützte Anbieterinhalte): https://developer.apple.com/streaming/

**Wichtig:** Die Quellen sind ein erster Prüfstand, keine Rechtsberatung und keine vollständige aktuelle Vertragsprüfung. Anbieterbedingungen und Partnerprogramme können sich ändern. Vor einer Umsetzung müssen die jeweils aktuellen offiziellen Bedingungen und eine mögliche schriftliche Freigabe geprüft werden.
