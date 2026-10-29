"""Das Kreislauf-Motiv der Website als PowerPoint-Formen.

Geometrie wie die Hero-Animation auf ecowerth.de (SVG 220 × 220): Haarlinie r 86,
drei Bögen r 72 mit 10 Breite in Blau, Grün, Rot (je 118 von 452 Einheiten, Abstand 151),
ein Punkt r 10 auf der Bahn, weißer Kern r 55 mit den drei Markennamen.
Die Animation dreht sich auf der Website; auf der Folie steht sie in einer festen Stellung.
"""
import math

from . import draw
from .tokens import BRANDS, KICKER_SPC, LINE_PX

_CIRCUMFERENCE = 2 * math.pi * 72
ARC_DEG = 118 / _CIRCUMFERENCE * 360          # Länge eines Bogens
STEP_DEG = 151 / _CIRCUMFERENCE * 360         # Abstand der Bogenanfänge
LOOP_COLORS = ("blue", "green", "red")       # Reihenfolge wie im Signet: ECOLOGICON, ECORELOOP, ECOINVEST
LOOP_INKS = ("blue_ink", "green_ink", "red_ink")


def kreislauf(shapes, cx: float, cy: float, outer_r: float, *, prefix: str = "loop", core_fill: str = "white",
              dot_color: str = "white", hair_color: str = "grey", names: bool = True,
              rotation_deg: float | None = None, dot_deg: float = -35) -> float:
    """Zeichnet den Kreislauf; `outer_r` ist der Radius der Haarlinie. Gibt den Kernradius zurück."""
    k = outer_r / 86
    draw.circle(shapes, f"{prefix}-hair", cx, cy, 86 * k, line=(hair_color, LINE_PX))
    start = -90 - ARC_DEG / 2 if rotation_deg is None else rotation_deg   # Blau mittig oben
    for i, color in enumerate(LOOP_COLORS):
        a0 = start + i * STEP_DEG
        draw.arc(shapes, f"{prefix}-arc-{i + 1}", cx, cy, 72 * k, a0, a0 + ARC_DEG, color, 10 * k)
    rad = math.radians(dot_deg)
    draw.circle(shapes, f"{prefix}-dot", cx + 72 * k * math.cos(rad), cy + 72 * k * math.sin(rad), 10 * k,
                fill=dot_color)
    core_r = 55 * k
    draw.circle(shapes, f"{prefix}-core", cx, cy, core_r, fill=core_fill, line=("grey", LINE_PX))
    if names:
        size_pt = 9.2 * k / 2
        for i, (key, ink) in enumerate(zip(BRANDS, LOOP_INKS)):
            mid = cy + (-15.3 + 16 * i) * k
            draw.textbox(shapes, f"{prefix}-name-{i + 1}", (cx - core_r, mid - size_pt * 1.4, 2 * core_r, size_pt * 2.8),
                         [(BRANDS[key]["name"], draw.style(size_pt, ink, "mono_medium", align="center",
                                                           spc=round(0.7 * k / 2 * 100)))], anchor="ctr")
    return core_r


def progress_segments(n: int, gap_deg: float) -> list[tuple[float, float]]:
    """Start- und Endwinkel von n Ringsegmenten, das erste beginnt oben (12 Uhr)."""
    pitch = 360 / n
    return [(-90 + i * pitch + gap_deg / 2, -90 + (i + 1) * pitch - gap_deg / 2) for i in range(n)]


def progress_ring(shapes, cx: float, cy: float, r: float, width: float, n: int, current: int, *,
                  prefix: str = "ring", visible_gap: float = 30, done: str = "muted_dark",
                  todo: str = "line_dark", active: str = "green") -> None:
    """Kapitel als Kreislauf: ein Segment je Kapitel, das aktuelle in Grün, erledigte hell, offene dunkel."""
    gap = math.degrees((visible_gap + width) / r)      # runde Enden ragen je width/2 in die Lücke
    for i, (a0, a1) in enumerate(progress_segments(n, gap), 1):
        color = active if i == current else (done if i < current else todo)
        state = "active" if i == current else ("done" if i < current else "todo")
        draw.arc(shapes, f"{prefix}-seg-{i}-{state}", cx, cy, r, a0, a1, color, width)


def label_style(color: str, size: str = "label") -> dict:
    """Mono-Versalien mit Laufweite, wie die Eyebrows der Website."""
    return draw.style(size, color, "mono_medium", caps=True, spc=KICKER_SPC if size == "kicker" else 110)
