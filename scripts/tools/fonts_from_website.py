#!/usr/bin/env python3
"""Holt die Schriften für Prüfung und Rendern aus dem Website-Prototyp (nur lokal).

Der Prototyp bettet Archivo, IBM Plex Sans und IBM Plex Mono als WOFF2 ein (statische
Schnitte, Teilmenge latin + latin-ext). Dieses Script entpackt sie zu TTF, setzt die
Namen so, wie sie PowerPoint und LibreOffice erwarten („Archivo SemiBold“, „IBM Plex
Mono Medium“ …), und legt sie in einem Ordner ab.

Die Dateien sind veränderte Fassungen (Teilmenge, umbenannt) und nur für die Prüfung
und das Rendern auf diesem Rechner gedacht. Nicht weitergeben und nicht einchecken:
Zum Bearbeiten der Folien die Originalschriften von Google Fonts installieren.

Aufruf:
    PYTHONPATH=scripts/tools python3 scripts/tools/fonts_from_website.py PROTOTYP.html fonts/
Danach für LibreOffice: Ordner nach ~/.fonts kopieren und `fc-cache -f` ausführen.

Mit --webfonts landen die WOFF2-Dateien unverändert in einem Ordner (für die Präsentationsseite):
    python3 scripts/tools/fonts_from_website.py --webfonts PROTOTYP.html site/assets/fonts/
"""
import base64
import io
import re
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

# (CSS-Familie, Stil, Gewicht) → (Dateiname, Familie ID1, Stil ID2, Typogr. Familie ID16, Typogr. Stil ID17)
FACES = {
    ("Archivo", "normal", 400): ("Archivo-Regular", "Archivo", "Regular", None, None),
    ("Archivo", "normal", 500): ("Archivo-Medium", "Archivo Medium", "Regular", "Archivo", "Medium"),
    ("Archivo", "normal", 600): ("Archivo-SemiBold", "Archivo SemiBold", "Regular", "Archivo", "SemiBold"),
    ("Archivo", "normal", 700): ("Archivo-Bold", "Archivo", "Bold", None, None),
    ("IBM Plex Sans", "normal", 400): ("IBMPlexSans-Regular", "IBM Plex Sans", "Regular", None, None),
    ("IBM Plex Sans", "normal", 500): ("IBMPlexSans-Medium", "IBM Plex Sans Medium", "Regular", "IBM Plex Sans",
                                       "Medium"),
    ("IBM Plex Sans", "normal", 600): ("IBMPlexSans-SemiBold", "IBM Plex Sans SemiBold", "Regular",
                                       "IBM Plex Sans", "SemiBold"),
    ("IBM Plex Sans", "italic", 400): ("IBMPlexSans-Italic", "IBM Plex Sans", "Italic", None, None),
    ("IBM Plex Mono", "normal", 400): ("IBMPlexMono-Regular", "IBM Plex Mono", "Regular", None, None),
    ("IBM Plex Mono", "normal", 500): ("IBMPlexMono-Medium", "IBM Plex Mono Medium", "Regular", "IBM Plex Mono",
                                       "Medium"),
}

FACE_RE = re.compile(r'@font-face\{font-family:"([^"]+)";font-style:(\w+);font-weight:(\d+);[^}]*?'
                     r'src:url\(data:font/woff2;base64,([A-Za-z0-9+/=]+)\)')


def _set_names(font: TTFont, file: str, fam: str, sub: str, tfam: str | None, tsub: str | None) -> None:
    name = font["name"]
    full = fam if sub == "Regular" else f"{fam} {sub}"
    values = {1: fam, 2: sub, 3: f"{file};local", 4: full, 6: file}
    if tfam:
        values.update({16: tfam, 17: tsub})
    for rec in list(name.names):
        if rec.nameID in (1, 2, 3, 4, 6, 16, 17):
            name.removeNames(nameID=rec.nameID)
    for nid, text in values.items():
        name.setName(text, nid, 3, 1, 0x409)
        name.setName(text, nid, 1, 0, 0)
    bold, italic = sub == "Bold", sub == "Italic"
    os2 = font["OS/2"]
    sel = os2.fsSelection & ~0b1100001          # Bits ITALIC, BOLD, REGULAR zurücksetzen
    sel |= (1 << 5) if bold else 0
    sel |= 1 if italic else 0
    sel |= (1 << 6) if not (bold or italic) else 0
    os2.fsSelection = sel
    font["head"].macStyle = (1 if bold else 0) | (2 if italic else 0)


def extract(html: Path, out_dir: Path) -> list[Path]:
    text = Path(html).read_text(encoding="utf-8")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for family, style, weight, data in FACE_RE.findall(text):
        spec = FACES.get((family, style, int(weight)))
        if spec is None:
            continue
        file, fam, sub, tfam, tsub = spec
        font = TTFont(io.BytesIO(base64.b64decode(data)))
        font.flavor = None
        _set_names(font, file, fam, sub, tfam, tsub)
        path = out_dir / f"{file}.ttf"
        font.save(str(path))
        written.append(path)
    missing = {spec[0] for spec in FACES.values()} - {p.stem for p in written}
    if missing:
        raise SystemExit(f"Schnitte fehlen im Prototyp: {', '.join(sorted(missing))}")
    return written


WEB_NAMES = {"Archivo": "archivo", "IBM Plex Sans": "ibm-plex-sans", "IBM Plex Mono": "ibm-plex-mono"}


def extract_webfonts(html: Path, out_dir: Path) -> list[Path]:
    """Die WOFF2-Dateien unverändert für die Präsentationsseite ablegen (archivo-600.woff2 …)."""
    text = Path(html).read_text(encoding="utf-8")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for family, style, weight, data in FACE_RE.findall(text):
        if style != "normal":
            continue
        path = out_dir / f"{WEB_NAMES[family]}-{weight}.woff2"
        path.write_bytes(base64.b64decode(data))
        written.append(path)
    return written


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--webfonts"]
    if len(args) != 2:
        raise SystemExit(__doc__)
    run = extract_webfonts if "--webfonts" in sys.argv else extract
    for p in run(Path(args[0]), Path(args[1])):
        print(p)
