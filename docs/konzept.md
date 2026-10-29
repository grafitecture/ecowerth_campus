# ECOWERTH Campus – Konzept

Stand: 29. Oktober 2026 · Grafitecture für die ecowerth GmbH

## Ziel

Eine PowerPoint-Vorlage, mit der ECOWERTH Präsentationen im Erscheinungsbild der neuen Website erstellt: von Hand in PowerPoint (23 Layouts mit benannten Platzhaltern) oder automatisch aus einem Folienplan (JSON). Dazu eine passwortgeschützte Seite, auf der Kunde und Team Beispiel-Präsentation und Layouts ansehen und die Dateien herunterladen.

## Übernommen aus fläsh Campus

Bau-Pipeline (Plan → Vorlage → Prüfung → Rendern), Präsentationsseite, Tests. Entfallen sind die Videoeinblendung des Referenten, die Kapitelleiste mit Leuchtpunkten und die Folientypen der Trainingsreihe (Belege, Zustandsskala). Neu sind Marken, Kennzahlen-Band, Tabelle, Praxisfall und Paragrafen-Chips.

## Erscheinungsbild

Alles stammt aus dem Website-Prototyp; Werte stehen in `skill/ecowerth-campus/scripts/campus/tokens.py`.

| Element | Umsetzung |
|---|---|
| Farben | Dunkelblau #043751 (Text, dunkle Folien), Grün #6EA52E (Akzent, Kennzahlen-Band), Blau #117EC2, Rot #AC1920, Grau #D9D9D9 (Haarlinien). Für kleine Schrift auf Weiß die dunkleren Töne #4F7A1E (Grün) und #0F6AA6 (Blau). |
| Marken | ECOLOGICON Blau, ECORELOOP Grün, ECOINVEST Rot – Reihenfolge wie im Signet |
| Schriften | Archivo SemiBold/Bold (Titel, Zahlen), IBM Plex Sans (Text), IBM Plex Mono (Kicker, Labels, Seitenzahlen, Paragrafen) |
| Kreislauf | drei Bögen in den Markenfarben mit Punkt, aus dem Hero der Website; groß auf der Titelfolie, als Fortschrittsring (ein Segment je Kapitel) auf Kapitelfolien |
| Kopfzeile | Logo links, Kapitelnavigation rechts wie das Menü der Website, aktives Kapitel grün unterstrichen, Haarlinie |
| Fußzeile | Titel der Präsentation und Seitenzahl in Mono-Versalien über einer Haarlinie |
| Paragrafen | Chips in Mono auf hellblauem Grund (`§ 59 KrWG`), wie die Leistungsseiten der Website |
| Raster | 16:9, 1920 × 1080 px, Ränder 120 px, Titelzone ab 158 px, Inhalt 340–900 px |

Keine Schatten, kein Leuchten, keine Verläufe außer im Bildbriefing-Platzhalter.

## Layouts

| Gruppe | Layouts |
|---|---|
| Rahmen | 01 Titel · 02 Agenda · 03 Kapitel · 23 Abschluss |
| Inhalt | 05 Punkte · 06 Punkte + Foto · 07 Punkte + Grafik · 08 Aussage · 09 Kennzahlen · 10 Marken · 11 Checkliste · 12 Schritte · 13 Vergleich · 14 Tabelle · 15 Skala |
| Bild | 16 Foto · 17 Zwei Fotos · 18 Foto mit Markierungen |
| Dialog | 04 Einstieg · 19 Praxisfall · 20 Zitat · 21 Wissenscheck · 22 Zusammenfassung |

Dunkle Folien (Titel, Kapitel, Einstieg, Zitat, Wissenscheck, Abschluss) setzen Abschnitte; alle übrigen sind weiß.

## Beispiel-Präsentation

„Zukunft im Kreislauf“, 30 Folien in fünf Kapiteln: Die Gruppe, Unsere Marken, Leistungen, Rechtsrahmen, Zusammenarbeit. Inhalte nur aus Website, Portfolio-Übersicht 2026 und Zielgruppen-/Pflichtenmatrix; Referent ist Florian Werthmann.

## Offene Punkte

1. **Batterierecht:** Tabelle, Praxisfall und Wissenscheck nennen „BattG“ wie die Pflichtenmatrix (Stand 2025). Seit dem 18. August 2025 gilt stattdessen das Batterierecht-Durchführungsgesetz (BattDG). Mit ECOWERTH klären und dann in Website und Vorlage gemeinsam ändern.
2. **Fotos:** Die Bilder der Website sind generiert, keine Aufnahmen von ecowerth-Standorten. Für den ECO Park Röthlein zeigt die Präsentation deshalb Platzhalter mit Bildbeschreibung (Luftbild, Lagerfläche, Lkw-Waage). Vor dem Einsatz bei Kunden durch echte Fotos ersetzen.
3. **Impressum und Datenschutz** der Seite: Handelsregister, USt-IdNr., Datenschutzbeauftragter und Auftragsverarbeitung sind als `PLATZHALTER` markiert.
4. **Vercel:** Das Projekt liegt im Hobby-Team von Grafitecture. Einen Auftragsverarbeitungsvertrag bietet Vercel erst ab dem Pro-Tarif.
5. **Schriften:** Wer die Vorlage in PowerPoint bearbeitet, braucht Archivo, IBM Plex Sans und IBM Plex Mono (Google Fonts).
