# ECOWERTH Campus

PowerPoint-Vorlage und Bau-Pipeline für Präsentationen der ecowerth GmbH mit ihren Marken ECOLOGICON, ECORELOOP und ECOINVEST und den Themengruppen ECOACADEMY und ECOVENTURES. Gestaltung und Umsetzung: Grafitecture. Technische Grundlage ist fläsh Campus (`grafitecture/flaeshcampus`).

Ein Folienplan im JSON-Format wird zu einer fertigen PowerPoint im Erscheinungsbild der ECOWERTH-Website. Die Vorlage hat 23 Layouts. Eine Prüfung misst jeden Text mit den echten Schriftmaßen von Archivo und IBM Plex und meldet Überlauf, Wortbrüche, fremde Schriften und fehlende Zeichen.

## Inhalt

| Pfad | Was |
|---|---|
| `skill/ecowerth-campus/SKILL.md` | Anleitung und Format des Folienplans (alle 23 Folientypen) |
| `skill/ecowerth-campus/assets/template/` | Vorlage `ecowerth-campus-template.pptx` mit 23 Layouts und Beispielgalerie, `layout-spec.json` |
| `skill/ecowerth-campus/assets/brand/` | Logos Stand FINAL1: ECOWERTH (SVG, PNG navy/weiß), ECOLOGICON, ECORELOOP, ECOINVEST, ECOACADEMY, ECOVENTURES; Lockup ECOWERTH \| CAMPUS (`logo-campus.svg`, auf Blau `logo-campus-weiss.svg`) |
| `skill/ecowerth-campus/scripts/` | `make_template.py`, `build_deck.py`, `check_deck.py` und das Paket `campus/` |
| `skill/ecowerth-campus/examples/` | Beispiel-Präsentation „Zukunft im Kreislauf“, Layout-Galerie, Fotos der Website und die Higgsfield-Bilder vom 14.11.2026 (Titel, Kapitel, ECOACADEMY, ECOVENTURES) |
| `site/` | Präsentationsseite für Vercel, erzeugt mit `scripts/tools/build_site.py` |
| `middleware.js` | Passwortschutz der Seite (Vercel Routing Middleware) |
| `docs/konzept.md` | Gestaltungskonzept und offene Punkte |

## Bauen

```bash
S=skill/ecowerth-campus
python3 $S/scripts/make_template.py --gallery $S/examples/layout-gallery.json \
        --out $S/assets/template/ecowerth-campus-template.pptx
python3 $S/scripts/build_deck.py $S/examples/ecowerth-praesentation.json --out out/ecowerth-praesentation.pptx
python3 $S/scripts/check_deck.py out/ecowerth-praesentation.pptx --render out/render
python3 scripts/tools/build_site.py   # site/ neu erzeugen (Folienbilder, Downloads, Impressum, Datenschutz)
```

Voraussetzungen: Python 3.12+, `python-pptx` 1.0.2, `lxml`, `Pillow`, `fonttools`, für das Rendern LibreOffice mit `pdftoppm`.

Tests: `python3 -m pytest tests -q` (der Test der Middleware braucht Node.js 18+).

## Schriften

Die Website setzt **Archivo** (Titel), **IBM Plex Sans** (Text) und **IBM Plex Mono** (Labels, Paragrafen), alle unter der SIL Open Font License.

- **Prüfen und Rendern:** Die Schnitte liegen lokal als TTF in `fonts/` und müssen für LibreOffice installiert sein (`~/.fonts`, dann `fc-cache -f`). Erzeugt werden sie aus den Schriften der Website:
  `PYTHONPATH=scripts/tools python3 scripts/tools/fonts_from_website.py <index.html der Website> fonts/`
  Das Skript benennt die Schnitte so, wie PowerPoint sie anspricht („Archivo SemiBold“, „IBM Plex Sans Medium“). `fonts/` ist von Git ausgeschlossen und wird nie eingecheckt.
- **Bearbeiten in PowerPoint:** die drei Familien von Google Fonts installieren. Ohne sie ersetzt PowerPoint die Schrift und Zeilen brechen anders.
- **Seite:** Die WOFF2-Dateien der Website liegen unverändert in `site/assets/fonts/`, daneben `OFL.txt`.

## Webseite

Vercel-Projekt `ecowerth_campus` im Team Grafitecture, verbunden mit diesem Repo. Jeder Push auf `main` veröffentlicht die Seite neu. Vercel liefert `site/` aus (`vercel.json`); einen Build-Schritt gibt es nicht. Die Seite ist von Suchmaschinen ausgeschlossen und lädt nichts von fremden Servern.

**Zugang:** `middleware.js` zeigt ohne gültiges Cookie die Login-Seite (Status 401) – auch für Folienbilder und Downloads. Frei bleiben nur Login-Dateien, Schriften, Favicon, `robots.txt`, Impressum und Datenschutz. Das Passwort steht nur in der Umgebungsvariable `SITE_PASSWORD` im Vercel-Projekt, nicht im Code; fehlt sie, bleibt die Seite gesperrt. Groß- und Kleinschreibung spielen keine Rolle. „Angemeldet bleiben“ hält die Anmeldung 30 Tage, `/abmelden` meldet ab. Ein geteiltes Passwort ist Sichtschutz, keine Benutzerverwaltung.

Impressum und Datenschutz enthalten markierte `PLATZHALTER` (Handelsregister, USt-IdNr., Datenschutzbeauftragter, Auftragsverarbeitung), die vor einer Weitergabe an Dritte gefüllt werden müssen.

## Stand 14.11.2026

- **Logo:** Seite, Impressum, Datenschutz und Login zeigen das Lockup ECOWERTH | CAMPUS (Vorlage `LOGO_ECOWERTH_LOGO_CAMPUS.pdf`). Auf Blau (Login, Fußzeile) sind Wortmarke, Linie und CAMPUS weiß.
- **Präsentation:** Logos auf Stand FINAL1; das Kreislauf-Motiv der Titelfolie und der Kapitelring sind entfernt, dafür tragen Titel und Kapitel ein Foto. Kapitel 2 hat drei neue Folien: „Zwei Themengruppen unter dem Dach“ (ECOACADEMY, ECOVENTURES), ECOACADEMY und ECOVENTURES je mit Foto – Inhalte von der Website. Beispiel-Präsentation jetzt 33 Folien.
- **Seite:** Stylesheet mit Inhalts-Kennung (`site.css?v=<hash>`), Favicon aus dem neuen Signet, „Datenschutzerklärung“ bricht bei 320 px um.

