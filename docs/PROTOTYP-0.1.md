# Prototyp 0.1 – Umfang

## In scope

- Windows-Desktopoberfläche
- M3U/M3U8 von HTTP(S)-URL und aus lokaler Playlist-Datei importieren
- Grundlegende technische Prüfung und Parser
- Senderliste, Suche und Gruppenfilter
- lokal gespeicherte Favoriten
- Wiedergabeversuch über Qt Multimedia für unterstützte Netzwerkstreams
- verständliche Fehlermeldungen, wenn eine Quelle nicht erreichbar oder nicht unterstützt ist

## Nicht in scope

- Wiedergabe lokaler MP4-, MKV-, AVI- oder anderer Videodateien
- Netflix, Disney+, Prime Video, WOW, Apple TV+ oder andere externe Premiumanbieter
- Umgehung von DRM, Zugangsbeschränkungen oder Bezahlschranken
- vollständiges EPG, Kinderbereich oder KI-Klassifizierung
- automatische Installation von Updates
- fertige EXE/MSI-Installer
- Zusage, dass jede M3U/M3U8-Quelle technisch abspielbar ist

## Technische Grenzen

Eine Playlist kann URLs zu unterschiedlichen Protokollen und Drittplattformen enthalten. Qt Multimedia unterstützt abhängig vom Betriebssystem, installierten Multimedia-Backends und Quellformat nur bestimmte Varianten. Der Import einer Playlist ist daher nicht gleichbedeutend mit erfolgreicher Wiedergabe.

Die aktuelle URL-Prüfung ist ein erster technischer Abruf, keine Prüfung der Legalität, Sicherheit oder Rechte an den verlinkten Inhalten. Vor einem breiteren Test müssen Fehlerbehandlung, Redirect-Verhalten, Netzwerksicherheit und Medienformat-Unterstützung weiter geprüft werden.
