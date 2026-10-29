---
name: ecowerth-campus
description: Präsentationen im ECOWERTH-Erscheinungsbild als PowerPoint bauen – aus einem Folienplan (JSON) mit 23 Layouts, Textprüfung mit echten Schriftmaßen und Sichtprüfung. Verwenden, wenn für ECOWERTH, ECOLOGICON, ECORELOOP oder ECOINVEST Folien, ein Vortrag oder eine Präsentation entstehen sollen.
---

# ECOWERTH Campus

Ein Folienplan (JSON) wird zur fertigen PowerPoint auf der Vorlage `assets/template/ecowerth-campus-template.pptx`
(23 Layouts im Erscheinungsbild der ECOWERTH-Website). Pfade in dieser Datei gelten relativ zum Skill-Ordner.

## Ablauf

1. **Inhalte sammeln.** Quellen: Website, Portfolio-Übersicht, Zielgruppen-/Pflichtenmatrix. Nichts erfinden –
   fehlende Fotos als `brief` beschreiben, offene Angaben im Sprechertext (`notes`) markieren.
2. **Plan schreiben.** Muster: `examples/ecowerth-praesentation.json` (30 Folien, Kapitel),
   alle Folientypen: `examples/layout-gallery.json`. Fotos liegen relativ zur Plandatei.
3. **Bauen:** `python3 scripts/build_deck.py PLAN.json --out out/deck.pptx`
   Ausgabe: JSON mit `briefs` (Folien mit Foto-Platzhalter) und `warnings`. Exit-Code 2 = Fehler im Plan
   (deutsche Meldung je Feld).
4. **Prüfen:** `python3 scripts/check_deck.py out/deck.pptx --render out/render`
   Jede Zeile ist ein Befund (`overflow`, `word`, `glyph`, `font`, `bounds`, `empty`). Text kürzen,
   nicht die Schrift verkleinern. Exit-Code 0 = sauber.
5. **Ansehen:** die PNGs in `out/render/` Folie für Folie prüfen, dann erst ausliefern.

Die Prüfung misst mit Archivo, IBM Plex Sans und IBM Plex Mono aus `fonts/` im Repo (oder `CAMPUS_FONTS`).
Fehlen sie, misst sie nur ungefähr und meldet das.

## Folienplan

```json
{"presentation": {"title": "Zukunft im Kreislauf", "subtitle": "…", "kicker": "ECOWERTH · …",
                  "date": "Oktober 2026", "presenter": {"name": "…", "role": "…"},
                  "chapters": ["Die Gruppe", "Unsere Marken", "Leistungen"]},
 "slides": [{"type": "cover"}, {"type": "agenda"}, {"type": "chapter", "chapter": 1}, …]}
```

`presentation.title` ist Pflicht, `chapters` 2–6. Jede Folie kann zusätzlich `kicker`, `source`, `notes`
(Sprechertext), `legal` (1–6 Paragrafen-Chips wie `"§ 59 KrWG"`) und `chapter` (1-basiert) tragen.
`chapter` markiert das Kapitel in der Kopfzeile und setzt den Kicker „02 · Unsere Marken“.

| type | Layout | Pflicht | optional |
|---|---|---|---|
| `cover` | 01 Titel | – | Titel, Untertitel, Referent aus `presentation` |
| `agenda` | 02 Agenda | `items` 2–6 {title, text} oder Kapitel | – |
| `chapter` | 03 Kapitel | `chapter` | `line` |
| `hook` | 04 Einstieg | `quote`, `truth` {text}, `answer` {text} | `label` je Box |
| `points` | 05 Punkte | `title`, `points` 2–4 {lead, text} | `focus` {label, title, text} |
| `points_photo` | 06 Punkte + Foto | `title`, `points`, `photo` | `caption` |
| `points_chart` | 07 Punkte + Grafik | `title`, `points`, `chart` {bars 2–4 {label, value 0–100, display}} | `highlight` je Balken |
| `statement` | 08 Aussage | `big` oder `statement` | – |
| `facts` | 09 Kennzahlen | `title`, `facts` 2–4 {value, label} | `lead` |
| `brands` | 10 Marken | `title`, `columns` 2–3 {brand: ecologicon/ecoreloop/ecoinvest} | `label`, `from`, `text`, `items` 1–5 |
| `checklist` | 11 Checkliste | `title`, `items` 1–8 | `focus` |
| `steps` | 12 Schritte | `title`, `steps` 3–5 {title, text} oder 2–4 {title, photo} | `start`, `caption` |
| `compare` | 13 Vergleich | `title`, `left`/`right` {label, items 1–4} | `style`: do_dont, myth_fact, neutral |
| `matrix` | 14 Tabelle | `title`, `columns` 2–7, `rows` 1–10 {label, cells: true/false/Text} | `corner`, `note` |
| `scale` | 15 Skala | `title` + `scale`, `timeline` oder `tags` | `points` 1–2 |
| `photo` | 16 Foto | `title`, `photo` | `caption` (kein `source`/`legal`) |
| `photo_pair` | 17 Zwei Fotos | `title`, `left`/`right` {label, photo} | – |
| `photo_annotated` | 18 Foto mit Markierungen | `title`, `photo`, `markers` 1–5 {x, y 0–1, label} | – |
| `case` | 19 Praxisfall | `title`, `story`, `findings` 1–5 {finding, cause} | `columns` (2 Spaltennamen) |
| `quote` | 20 Zitat | `quote`, `name` | `role`, `photo` |
| `quiz` | 21 Wissenscheck | `question`, `options` (3), `answer` 0–2 | `explanation`; ergibt zwei Folien: Frage, Auflösung |
| `summary` | 22 Zusammenfassung | `title`, `items` 1–5 {title, text} | – |
| `closing` | 23 Abschluss | `title`, `steps` 1–3 {title, text}, `next` {title} | `next.label`, `next.text` |

`photo` ist `{"file": "photos/x.jpg"}` oder `{"brief": "Foto: …"}` (Platzhalter mit Beschreibung).

## Gestaltung

- Farben nur aus `scripts/campus/tokens.py`: Dunkelblau #043751, Grün #6EA52E, Blau #117EC2, Rot #AC1920.
  Marken: ECOLOGICON Blau, ECORELOOP Grün, ECOINVEST Rot – immer in dieser Reihenfolge.
- Schriften: Archivo (Titel, Zahlen), IBM Plex Sans (Text), IBM Plex Mono (Kicker, Labels, Paragrafen).
- Titel passen auf eine Zeile; lieber eine Folie mehr als volle Folien.
- Deutsche Anführungszeichen „…“, Gedankenstrich –, keine Pfeile oder Sonderzeichen außerhalb der Schriften.
- Rechtsgrundlagen als Chips (`legal`), Quellen in `source`; Paragrafen exakt wie im Gesetz.
- Der Kreislauf (drei Bögen) erscheint nur auf Titel- und Kapitelfolien; kein Schatten, kein Leuchten.
