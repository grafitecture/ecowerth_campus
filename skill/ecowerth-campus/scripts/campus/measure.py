"""Textmessung mit den echten Schriftmaßen (1 pt = 2 px auf dem 1920er Raster).

Archivo, IBM Plex Sans und IBM Plex Mono stehen unter der SIL Open Font License. Gemessen wird
mit den Dateien aus `fonts/` im Repo (git-ignoriert, siehe README) oder aus `CAMPUS_FONTS`.
Fehlt eine Datei, misst die Prüfung mit einer Ersatzschrift und sagt das dazu.
"""
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import ImageFont

from .tokens import FONT_FILES, FONTS

_SCRIPTS = Path(__file__).resolve().parents[1]
DEFAULT_FONT = FONTS["body"]


@dataclass
class Para:
    text: str
    size_pt: float
    ln_spc_pct: float = 100
    spc_before_pt: float = 0
    spc_after_pt: float = 0
    spc_pt: float = 0
    indent_px: float = 0
    font: tuple[str, bool] = DEFAULT_FONT


def font_dirs() -> list[Path]:
    dirs = []
    if os.environ.get("CAMPUS_FONTS"):
        dirs.append(Path(os.environ["CAMPUS_FONTS"]))
    dirs.append(_SCRIPTS.parent / "assets" / "fonts")      # Skill-Paket
    dirs.append(_SCRIPTS.parents[2] / "fonts")              # Repo
    return dirs


def find_fonts() -> dict[tuple[str, bool], Path]:
    """Gefundene Schriftdateien je (Schriftname, fett)."""
    found = {}
    for key, file in FONT_FILES.items():
        for d in font_dirs():
            if (d / file).exists():
                found[key] = d / file
                break
    return found


def _fallback_font() -> Path:
    out = subprocess.run(["fc-match", "-f", "%{file}", "sans"], capture_output=True, text=True).stdout.strip()
    return Path(out)


class _Face:
    def __init__(self, path: Path):
        tt = TTFont(str(path))
        hhea, upm = tt["hhea"], tt["head"].unitsPerEm
        self.path = path
        self.line_ratio = (hhea.ascent - hhea.descent + hhea.lineGap) / upm
        self.cmap = set(tt.getBestCmap())
        self._sizes: dict[float, ImageFont.FreeTypeFont] = {}

    def font(self, size_pt: float) -> ImageFont.FreeTypeFont:
        if size_pt not in self._sizes:
            self._sizes[size_pt] = ImageFont.truetype(str(self.path), size_pt * 2)
        return self._sizes[size_pt]


class Measurer:
    def __init__(self, fonts: dict[tuple[str, bool], Path] | None = None):
        fonts = find_fonts() if fonts is None else fonts
        self.missing = sorted({name for name in FONT_FILES if name not in fonts})
        self.approximate = bool(self.missing)
        fallback = _Face(_fallback_font()) if self.missing else None
        self._faces = {key: _Face(path) for key, path in fonts.items()}
        self._fallback = fallback

    def face(self, font: tuple[str, bool] = DEFAULT_FONT) -> _Face:
        return self._faces.get(tuple(font)) or self._faces.get(DEFAULT_FONT) or self._fallback

    def cmap(self, font: tuple[str, bool]) -> set[int] | None:
        """Zeichenvorrat einer Schrift; None, wenn nur mit Ersatzschrift gemessen wird."""
        face = self._faces.get(tuple(font))
        return face.cmap if face else None

    def width_px(self, text: str, size_pt: float, spc_pt: float = 0, font=DEFAULT_FONT) -> float:
        return self.face(font).font(size_pt).getlength(text) + spc_pt * 2 * len(text)

    def line_height_px(self, size_pt: float, ln_spc_pct: float = 100, font=DEFAULT_FONT) -> float:
        return self.face(font).line_ratio * size_pt * 2 * ln_spc_pct / 100

    def wrap(self, text: str, size_pt: float, width_px: float, spc_pt: float = 0, font=DEFAULT_FONT) -> list[str]:
        lines: list[str] = []
        for block in text.split("\n"):
            lines.extend(self._wrap_block(block, size_pt, width_px, spc_pt, font))
        return lines

    def _wrap_block(self, text: str, size_pt: float, width_px: float, spc_pt: float, font) -> list[str]:
        fits = lambda s: self.width_px(s, size_pt, spc_pt, font) <= width_px  # noqa: E731
        lines: list[str] = []
        line = ""
        for word in text.split():
            candidate = f"{line} {word}" if line else word
            if fits(candidate):
                line = candidate
                continue
            if line:
                lines.append(line)
            if fits(word):
                line = word
                continue
            chunk = ""
            for ch in word:
                if chunk and not fits(chunk + ch):
                    lines.append(chunk)
                    chunk = ch
                else:
                    chunk += ch
            line = chunk
        lines.append(line)
        return lines

    def block_height_px(self, paras: list[Para], width_px: float) -> float:
        total = 0.0
        for p in paras:
            text = p.text.rsplit("\t", 1)[-1]
            lines = self.wrap(text, p.size_pt, width_px - p.indent_px, p.spc_pt, p.font)
            total += p.spc_before_pt * 2 + p.spc_after_pt * 2
            total += len(lines) * self.line_height_px(p.size_pt, p.ln_spc_pct, p.font)
        return total

    def text_height_px(self, text: str, style: dict, width_px: float) -> float:
        """Höhe eines Textes in einem Stil aus `draw.style` (für Widgets, die ihre Höhe selbst bestimmen)."""
        font = FONTS[style.get("font", "body")]
        para = Para(text, style["size_pt"], style.get("ln_spc_pct", 100), spc_pt=style.get("spc", 0) / 100,
                    font=font)
        return self.block_height_px([para], width_px)

    def long_words(self, text: str, size_pt: float, width_px: float, spc_pt: float = 0, font=DEFAULT_FONT) -> list[str]:
        return [w for w in text.split() if self.width_px(w, size_pt, spc_pt, font) > width_px]
