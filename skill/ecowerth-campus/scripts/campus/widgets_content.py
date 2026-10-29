"""Inhalts-Widgets: Punkte, Agenda, Checkliste, Schritte, Balken, Kennzahlen, Marken, Tabelle, Vergleich,
Skala, Zeitstrahl, Schlagworte, Zusammenfassung, Marker, Befunde, Quiz, Abschluss-Schritte.

Gestaltung wie ecowerth.de: Haarlinien statt Schattenkarten, Nummern in IBM Plex Mono, kurze Striche als
Aufzählungszeichen in der Markenfarbe. Symbole (Haken, Kreuz, Pfeil) sind Formen, keine Schriftzeichen.
"""
import math
from pathlib import Path
from typing import Literal

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE

from . import oxml
from .draw import circle, hline, picture, rect, shape, style, textbox, vline
from .measure import Measurer
from .tokens import BRANDS, COLOR, CONTENT_BOTTOM, CONTENT_TOP, CONTENT_W, FONTS, KICKER_SPC, LABEL_SPC, MARGIN_X, px
from .widgets_frame import add_photo

ASSETS = Path(__file__).resolve().parents[2] / "assets"
X0, X1 = MARGIN_X, MARGIN_X + CONTENT_W


def label_st(color: str, size: str | float = "label") -> dict:
    return style(size, color, "mono_medium", caps=True, spc=LABEL_SPC)


def num_st(color: str = "green_ink", size: float = 15, **extra) -> dict:
    return style(size, color, "mono_medium", **extra)


# ---------------------------------------------------------------- Symbole

def _lines_group(slide, name: str, segments, color: str, width_px: float):
    """Symbol aus geraden Linien (in px); als Gruppe benannt."""
    group = slide.shapes.add_group_shape()
    group.name = name
    for (x1, y1), (x2, y2) in segments:
        line = group.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, px(x1), px(y1), px(x2), px(y2))
        line.line.color.rgb = RGBColor.from_string(COLOR.get(color, color))
        line.line.width = px(width_px)
    return group


def check_icon(slide, name: str, x: float, y: float, size: float, color: str = "green_ink"):
    s = size
    return _lines_group(slide, name, [((x + .15 * s, y + .52 * s), (x + .40 * s, y + .78 * s)),
                                      ((x + .40 * s, y + .78 * s), (x + .86 * s, y + .22 * s))], color, s * .12)


def cross_icon(slide, name: str, x: float, y: float, size: float, color: str = "muted"):
    s = size
    return _lines_group(slide, name, [((x + .2 * s, y + .2 * s), (x + .8 * s, y + .8 * s)),
                                      ((x + .8 * s, y + .2 * s), (x + .2 * s, y + .8 * s))], color, s * .12)


def dash(slide, name: str, x: float, y: float, color: str = "green", w: float = 14):
    """Aufzählungszeichen der Website: ein kurzer Strich in der Markenfarbe."""
    return rect(slide.shapes, name, (x, y - 1, w, 2), color)


def number_badge(slide, name: str, box, n: int | str, fill: str, color: str, size: float = 15, line=None):
    """Kreis mit Zahl in Mono (Marker, Legende, Quiz-Buchstaben)."""
    sp = shape(slide.shapes, MSO_SHAPE.OVAL, name, box, fill=fill, line=line)
    oxml.fill_text_frame(sp.text_frame, [(str(n), num_st(color, size, align="center"))], anchor="ctr")
    return sp


# ---------------------------------------------------------------- Punkte

def points_text(ph, points: list[dict]) -> None:
    tf = ph.text_frame
    for extra in list(tf.paragraphs)[1:]:
        extra._p.getparent().remove(extra._p)
    first = tf.paragraphs[0]
    for run in list(first.runs):
        run._r.getparent().remove(run._r)
    for i, point in enumerate(points):
        lead = first if i == 0 else tf.add_paragraph()
        lead.level = 0
        num = lead.add_run()
        num.text = f"{i + 1:02d}"
        oxml.style_run(num, num_st("green_ink", 16))
        lead.add_run().text = "\t" + point["lead"]
        if point.get("text"):
            body = tf.add_paragraph()
            body.level = 1
            body.add_run().text = point["text"]
    from pptx.util import Pt
    first.space_before = Pt(0)


# ---------------------------------------------------------------- Agenda

def agenda_rows(slide, items: list[dict], m: Measurer, current: int | None = None) -> None:
    """Kapitel als Liste wie das Portfolio der Website: Nummer, Titel, Satz; Haarlinien dazwischen."""
    n = len(items)
    row_h = min(120, (CONTENT_BOTTOM - CONTENT_TOP) / n)
    hline(slide.shapes, "agenda-rule", X0, CONTENT_TOP, CONTENT_W, "navy")
    title_st = style("agenda", "navy", "display")
    text_st = style("body", "muted")
    for i, item in enumerate(items, 1):
        y = CONTENT_TOP + (i - 1) * row_h
        textbox(slide.shapes, f"agenda-num-{i}", (X0, y, 90, row_h), [(f"{i:02d}", num_st("green_ink", 18))],
                anchor="ctr")
        textbox(slide.shapes, f"agenda-title-{i}", (X0 + 100, y, 700, row_h), [(item["title"], title_st)],
                anchor="ctr")
        if item.get("text"):
            textbox(slide.shapes, f"agenda-text-{i}", (X0 + 860, y, CONTENT_W - 860, row_h),
                    [(item["text"], text_st)], anchor="ctr")
        hline(slide.shapes, f"agenda-line-{i}", X0, y + row_h, CONTENT_W, "grey")


# ---------------------------------------------------------------- Checkliste, Schritte, Zusammenfassung

def checklist(slide, items: list[str], m: Measurer, x: float = X0, y: float = CONTENT_TOP, w: float = CONTENT_W,
              columns: int = 1) -> float:
    """Nummerierte Zeilen mit Haarlinien; bei mehr als fünf Einträgen in zwei Spalten. Gibt das untere Ende zurück."""
    gap = 80
    col_w = (w - gap * (columns - 1)) / columns
    per_col = math.ceil(len(items) / columns)
    text_st = style(18, "navy")
    bottom = y
    for i, item in enumerate(items, 1):
        c, r = divmod(i - 1, per_col)
        cx = x + c * (col_w + gap)
        if r == 0:
            top = y
            hline(slide.shapes, f"check-rule-{c + 1}", cx, top, col_w, "navy")
        text_w = col_w - 76
        h = max(72, m.text_height_px(item, text_st, text_w) + 32)
        textbox(slide.shapes, f"check-num-{i}", (cx, top, 64, h), [(f"{i:02d}", num_st("green_ink", 16))],
                anchor="ctr")
        textbox(slide.shapes, f"check-text-{i}", (cx + 76, top, text_w, h), [(item, text_st)], anchor="ctr")
        top += h
        hline(slide.shapes, f"check-line-{i}", cx, top, col_w, "grey")
        bottom = max(bottom, top)
    return bottom


STEP_ROWS = {3: [3], 4: [4], 5: [3, 2]}


def steps_grid(slide, steps: list[dict], m: Measurer, area=(X0, CONTENT_TOP, CONTENT_W, 560), start: int = 1) -> None:
    """Schritte als Spalten mit Linie oben (wie die Markenspalten der Website), Nummer in Mono."""
    ax, ay, aw, ah = area
    rows = STEP_ROWS.get(len(steps), [len(steps)])
    cols = max(rows)
    gap = 48
    cw = (aw - gap * (cols - 1)) / cols
    rh = ah / len(rows)
    title_st = style("lead", "navy", "display")
    text_st = style("body", "muted")
    i = 0
    for r, count in enumerate(rows):
        for c in range(count):
            step = steps[i]
            i += 1
            x, y = ax + c * (cw + gap), ay + r * rh
            hline(slide.shapes, f"step-rule-{i}", x, y, cw, "navy")
            textbox(slide.shapes, f"step-num-{i}", (x, y + 20, cw, 44), [(f"{start + i - 1:02d}", num_st("green_ink", 16))])
            title_h = m.text_height_px(step["title"], title_st, cw)
            textbox(slide.shapes, f"step-title-{i}", (x, y + 66, cw, title_h + 4), [(step["title"], title_st)])
            textbox(slide.shapes, f"step-text-{i}", (x, y + 66 + title_h + 14, cw, rh - 66 - title_h - 30),
                    [(step["text"], text_st)])


PHOTO_STEPS_TOP, PHOTO_STEPS_GAP, PHOTO_STEPS_WIDTH, PHOTO_STEPS_MAX_CELL = 330, 32, CONTENT_W, 540


def photo_steps(slide, steps: list[dict], base_dir, warnings: list[str], start: int = 1,
                caption: str | None = None) -> list[str]:
    """Schrittfotos in einer Reihe (16:9), Nummer als Fahne auf dem Foto, Titel darunter.
    Gibt die Briefings fehlender Fotos zurück."""
    n = len(steps)
    cell = min(PHOTO_STEPS_MAX_CELL, (PHOTO_STEPS_WIDTH - PHOTO_STEPS_GAP * (n - 1)) / n)
    h = cell * 9 / 16
    briefs = []
    for i, step in enumerate(steps, 1):
        x = X0 + (i - 1) * (cell + PHOTO_STEPS_GAP)
        brief = add_photo(slide, f"step-photo-{i}", (x, PHOTO_STEPS_TOP, cell, h), step["photo"], base_dir, warnings)
        if brief:
            briefs.append(brief)
        tag = rect(slide.shapes, f"step-tag-{i}", (x, PHOTO_STEPS_TOP + 20, 64, 40), "navy")
        oxml.fill_text_frame(tag.text_frame, [(f"{start + i - 1:02d}", num_st("white", 15, align="center"))],
                             anchor="ctr")
        textbox(slide.shapes, f"step-title-{i}", (x, PHOTO_STEPS_TOP + h + 20, cell, 100),
                [(step["title"], style("lead", "navy", "display"))])
    if caption:
        textbox(slide.shapes, "steps-caption", (X0, PHOTO_STEPS_TOP + h + 150, 1400, 80),
                [(caption, style("body", "muted"))])
    return briefs


def summary_items(slide, items: list[dict], m: Measurer) -> None:
    title_st = style("lead", "navy", "display")
    text_st = style("body", "muted")
    for i, item in enumerate(items, 1):
        col, row = (0, i - 1) if i <= 3 else (1, i - 4)
        x, y = X0 + col * 860, CONTENT_TOP + row * 190
        circle(slide.shapes, f"sum-check-{i}", x + 22, y + 22, 22, fill="green")
        check_icon(slide, f"sum-check-icon-{i}", x + 8, y + 8, 28, "white")
        title_h = m.text_height_px(item["title"], title_st, 720)
        textbox(slide.shapes, f"sum-title-{i}", (x + 72, y, 720, title_h + 4), [(item["title"], title_st)])
        textbox(slide.shapes, f"sum-text-{i}", (x + 72, y + title_h + 10, 720, 150 - title_h), [(item["text"], text_st)])


def closing_steps(slide, steps: list[dict], m: Measurer) -> None:
    """Nächste Schritte auf Dunkelblau: Nummer, Titel, Satz; Haarlinien dazwischen."""
    title_st = style("lead", "white", "display")
    text_st = style("body", "on_dark")
    w = 920
    y = CONTENT_TOP
    hline(slide.shapes, "next-step-rule", X0, y, w, "line_dark")
    for i, step in enumerate(steps, 1):
        title_h = m.text_height_px(step["title"], title_st, w - 90)
        text_h = m.text_height_px(step["text"], text_st, w - 90)
        h = max(130, 28 + title_h + 8 + text_h + 28)
        textbox(slide.shapes, f"next-step-num-{i}", (X0, y + 26, 70, 44), [(f"{i:02d}", num_st("green_light", 16))])
        textbox(slide.shapes, f"next-step-title-{i}", (X0 + 90, y + 26, w - 90, title_h + 4), [(step["title"], title_st)])
        textbox(slide.shapes, f"next-step-text-{i}", (X0 + 90, y + 26 + title_h + 8, w - 90, text_h + 4),
                [(step["text"], text_st)])
        y += h
        hline(slide.shapes, f"next-step-line-{i}", X0, y, w, "line_dark")


# ---------------------------------------------------------------- Balken und Kennzahlen

def bars_card(slide, chart: dict, box=(960, 330, 840, 0)) -> None:
    x, y, w, _ = box
    bars = chart["bars"]
    pitch, note_h = 100, (44 if chart.get("note") else 0)
    h = 40 + 34 + 20 + len(bars) * pitch + note_h + 24
    rect(slide.shapes, "chart-card", (x, y, w, h), "bg")
    inner = w - 96
    textbox(slide.shapes, "chart-title", (x + 48, y + 40, inner, 30), [(chart.get("title", ""), label_st("muted"))])
    track_w = inner - 210
    tops = [y + 94 + (i - 1) * pitch for i in range(1, len(bars) + 1)]
    for i, (bar, by) in enumerate(zip(bars, tops), 1):
        track_y = by + 44                  # Beschriftung (40 px, eine Zeile 17 pt) steht über dem Balken
        rect(slide.shapes, f"bar-track-{i}", (x + 48, track_y, track_w, 24), "white")
        hi = bar.get("highlight")
        fill_w = max(track_w * bar["value"] / 100, 2)
        rect(slide.shapes, f"bar-fill-{i}", (x + 48, track_y, fill_w, 24), "green" if hi else "steel")
        value = bar.get("display", f"{bar['value']:g} %")
        textbox(slide.shapes, f"bar-value-{i}", (x + w - 48 - 190, track_y - 10, 190, 44),
                [(value, num_st("navy", 17, align="right"))], anchor="ctr")
        textbox(slide.shapes, f"bar-label-{i}", (x + 48, by - 4, inner, 46), [(bar["label"], style("body", "navy"))])
    if chart.get("note"):
        textbox(slide.shapes, "chart-note", (x + 48, y + h - 24 - 40, inner, 40), [(chart["note"], style("small", "muted"))])


FACTS_BAND = (540, 350)   # y, Höhe des grünen Bands (liegt in der Vorlage)
FACT_MIN_W = 360


def fact_widths(facts: list[dict], m: Measurer) -> list[float]:
    """Spaltenbreiten nach Inhalt: lange Werte („8.000 m²“) bekommen mehr Platz, kurze („4“) mindestens 360 px."""
    st = style("fact", "white", "display_bold")
    need = [max(FACT_MIN_W, m.width_px(f["value"], st["size_pt"], font=FONTS["display_bold"]) + 72) for f in facts]
    spare = CONTENT_W - sum(need)
    if spare <= 0:
        return [w * CONTENT_W / sum(need) for w in need]
    return [w + spare / len(need) for w in need]


def facts_band(slide, facts: list[dict], m: Measurer) -> None:
    """Kennzahlen auf dem grünen Band wie auf der Website: große Zahl, kurze Erklärung, feine Trennlinien."""
    band_y, band_h = FACTS_BAND
    x = X0
    for i, (fact, cw) in enumerate(zip(facts, fact_widths(facts, m)), 1):
        if i > 1:
            sep = rect(slide.shapes, f"fact-sep-{i}", (x - 1, band_y + 48, 2, band_h - 96), "white")
            oxml.set_fill_alpha(sep, 40)
        pad = 0 if i == 1 else 40
        textbox(slide.shapes, f"fact-value-{i}", (x + pad, band_y + 34, cw - pad - 24, 136),
                [(fact["value"], style("fact", "white", "display_bold"))])
        textbox(slide.shapes, f"fact-label-{i}", (x + pad, band_y + 172, cw - pad - 32, 180),
                [(fact["label"], style("fact_label", "white"))])
        x += cw


# ---------------------------------------------------------------- Marken

def brand_columns(slide, columns: list[dict], m: Measurer) -> None:
    """Spalten der Untermarken wie „Unsere Marken“ auf der Website: Wortmarke, Herkunft, Text, Stichpunkte."""
    n = len(columns)
    pitch = CONTENT_W / n
    gutter = 48
    top = CONTENT_TOP
    hline(slide.shapes, "brands-rule", X0, top, CONTENT_W, "navy")
    for i, c in enumerate(columns, 1):
        brand = BRANDS.get(c.get("brand", ""), {})
        color = c.get("color") or brand.get("color", "green")
        ink = brand.get("ink", "green_ink" if color == "green" else f"{color}_ink")
        x = X0 + (i - 1) * pitch + (gutter / 2 if i > 1 else 0)
        w = pitch - gutter / 2 - (gutter / 2 if i > 1 else 0)
        if i < n:
            vline(slide.shapes, f"brand-sep-{i}", X0 + i * pitch, top + 24, CONTENT_BOTTOM - top - 24, "grey")
        y = top + 32
        if c.get("label"):
            textbox(slide.shapes, f"brand-label-{i}", (x, y, w, 32), [(c["label"], label_st("muted"))])
            y += 44
        if brand.get("logo") and not c.get("title"):
            logo_h = 32
            path = ASSETS / brand["logo"]
            from PIL import Image
            with Image.open(path) as im:
                logo_w = logo_h * im.width / im.height
            picture(slide.shapes, f"brand-logo-{i}", path, (x, y, min(logo_w, w), logo_h))
            y += logo_h + 18
        else:
            title_st = style(28, ink, "display")
            title = c.get("title") or brand.get("name", "")
            textbox(slide.shapes, f"brand-title-{i}", (x, y, w, 44), [(title, title_st)])
            y += 52
        if c.get("from"):
            from_st = style("chip", "muted", "mono")
            h = m.text_height_px(c["from"], from_st, w)
            textbox(slide.shapes, f"brand-from-{i}", (x, y, w, h + 4), [(c["from"], from_st)])
            y += h + 20
        if c.get("text"):
            text_st = style(16, "muted")
            h = m.text_height_px(c["text"], text_st, w)
            textbox(slide.shapes, f"brand-text-{i}", (x, y, w, h + 4), [(c["text"], text_st)])
            y += h + 16
        item_st = style(16, "navy")
        for j, item in enumerate(c.get("items") or [], 1):
            h = m.text_height_px(item, item_st, w - 26)
            dash(slide, f"brand-dash-{i}-{j}", x, y + 16, color)
            textbox(slide.shapes, f"brand-item-{i}-{j}", (x + 26, y, w - 26, h + 4), [(item, item_st)])
            y += h + 6


# ---------------------------------------------------------------- Tabelle

def matrix_table(slide, columns: list[str], rows: list[dict], m: Measurer, corner: str = "",
                 area=(X0, CONTENT_TOP, CONTENT_W, 0)) -> float:
    """Tabelle wie die Pflichtenmatrix der Website: Kopf in Mono, Zeilen mit Haarlinien, Haken als Form.
    Gibt das untere Ende zurück."""
    x, y, w, _ = area
    head_h = 52
    row_h = min(56, (896 - y - head_h) / len(rows))
    label_style = style(16, "navy", "body_medium")
    first_w = min(max(m.width_px(r["label"], 16, font=FONTS["body_medium"]) for r in rows) + 64, w * 0.42)
    cw = (w - first_w) / len(columns)
    h = head_h + row_h * len(rows)
    rect(slide.shapes, "matrix-head", (x, y, w, head_h), "surface2")
    shape(slide.shapes, MSO_SHAPE.RECTANGLE, "matrix-frame", (x, y, w, h), line=("grey", 2))
    head_st = label_st("muted")
    if corner:
        textbox(slide.shapes, "matrix-corner", (x + 24, y, first_w - 24, head_h), [(corner, head_st)], anchor="ctr")
    for j, colname in enumerate(columns, 1):
        cx = x + first_w + (j - 1) * cw
        textbox(slide.shapes, f"matrix-col-{j}", (cx, y, cw, head_h), [(colname, {**head_st, "align": "center"})],
                anchor="ctr")
    for i, row in enumerate(rows, 1):
        ry = y + head_h + (i - 1) * row_h
        if i > 1:
            hline(slide.shapes, f"matrix-line-{i}", x, ry, w, "grey")
        textbox(slide.shapes, f"matrix-row-{i}", (x + 24, ry, first_w - 32, row_h), [(row["label"], label_style)],
                anchor="ctr")
        for j, cell in enumerate(row["cells"], 1):
            cx = x + first_w + (j - 1) * cw
            if cell is True:
                size = 26
                check_icon(slide, f"matrix-yes-{i}-{j}", cx + cw / 2 - size / 2, ry + row_h / 2 - size / 2, size,
                           "green_ink")
            elif cell is False or str(cell).strip() in ("", "-", "–"):
                textbox(slide.shapes, f"matrix-no-{i}-{j}", (cx, ry, cw, row_h),
                        [("–", style(16, "steel", align="center"))], anchor="ctr")
            else:
                textbox(slide.shapes, f"matrix-cell-{i}-{j}", (cx + 8, ry, cw - 16, row_h),
                        [(str(cell), style("chip", "navy", "mono", align="center"))], anchor="ctr")
    return y + h


# ---------------------------------------------------------------- Vergleich

def compare_columns(slide, left: dict, right: dict, style_: Literal["do_dont", "myth_fact", "neutral"] = "do_dont") -> None:
    positive = {"do_dont": "l", "myth_fact": "r", "neutral": None}[style_]
    for side, data, x in (("l", left, X0), ("r", right, 980)):
        good = positive is None or side == positive
        head_fill = "navy" if positive is None else ("green" if good else "surface2")
        head_color = "white" if positive is None or good else "muted"
        head = rect(slide.shapes, f"compare-head-{side}", (x, CONTENT_TOP, 820, 60), head_fill)
        oxml.fill_text_frame(head.text_frame, [(data["label"], style("kicker", head_color, "mono_medium", caps=True,
                                                                      spc=KICKER_SPC))], anchor="ctr")
        head.text_frame.margin_left = px(28)
        for i, item in enumerate(data["items"], 1):
            y = CONTENT_TOP + 92 + (i - 1) * 118
            if positive is None:
                dash(slide, f"icon-dash-{side}-{i}", x + 4, y + 22, "green", 22)
            elif good:
                check_icon(slide, f"icon-check-{side}-{i}", x, y + 2, 36, "green_ink")
            else:
                cross_icon(slide, f"icon-cross-{side}-{i}", x, y + 2, 36, "muted")
            textbox(slide.shapes, f"compare-item-{side}-{i}", (x + 60, y, 760, 104), [(item, style(19, "navy"))])
            hline(slide.shapes, f"compare-line-{side}-{i}", x, y + 106, 820, "grey")


# ---------------------------------------------------------------- Skala, Zeitstrahl, Schlagworte

def scale_chips(slide, items: list[str], highlight: list[str], box=(X0, CONTENT_TOP, CONTENT_W, 100)) -> None:
    x, y, w, h = box
    gap = 8
    cw = (w - gap * (len(items) - 1)) / len(items)
    for i, item in enumerate(items, 1):
        hi = item in (highlight or [])
        chip = shape(slide.shapes, MSO_SHAPE.ROUNDED_RECTANGLE, f"scale-chip-{i}", (x + (i - 1) * (cw + gap), y, cw, h),
                     fill="green" if hi else "surface2", radius_px=4)
        oxml.fill_text_frame(chip.text_frame, [(item, style(17, "white" if hi else "navy", "body_medium",
                                                            align="center"))], anchor="ctr")
        chip.text_frame.margin_left = chip.text_frame.margin_right = px(10)


def scale_caption(slide, text: str, y: float = 470) -> None:
    textbox(slide.shapes, "scale-caption", (X0, y, 1400, 40), [(text, style("small", "muted"))])


TAG_H, TAG_GAP, TAG_PAD = 54, 14, 24


def tag_cloud(slide, items: list[str], highlight: list[str], m: Measurer, x: float = X0, y: float = CONTENT_TOP,
              w: float = CONTENT_W) -> float:
    """Schlagworte als Pillen wie die Zielgruppen-Tags der Website; bricht in Zeilen um. Gibt das untere Ende zurück."""
    st = style(17, "navy")
    cx, cy = x, y
    for i, item in enumerate(items, 1):
        tw = m.width_px(item, st["size_pt"], font=FONTS["body"]) + 2 * TAG_PAD + 4
        if cx > x and cx + tw > x + w:
            cx, cy = x, cy + TAG_H + TAG_GAP
        hi = item in (highlight or [])
        pill = shape(slide.shapes, MSO_SHAPE.ROUNDED_RECTANGLE, f"tag-{i}", (cx, cy, tw, TAG_H),
                     fill="green_tint" if hi else "white", line=("green" if hi else "grey", 2), radius_px=TAG_H / 2)
        oxml.fill_text_frame(pill.text_frame, [(item, {**st, "color": COLOR["green_ink" if hi else "navy"],
                                                       "align": "center"})], anchor="ctr")
        pill.text_frame.margin_left = pill.text_frame.margin_right = 0
        cx += tw + TAG_GAP
    return cy + TAG_H


def timeline(slide, points: list[dict], box=(X0, CONTENT_TOP, CONTENT_W, 200), dark: bool = False) -> None:
    x, y, w, _ = box
    inner_x, inner_w = x + 150, w - 300
    n = len(points)
    xs = [inner_x + (inner_w * i / (n - 1) if n > 1 else inner_w / 2) for i in range(n)]
    line_y = y + 66
    label_w = min(320, inner_w / (n - 1) - 24) if n > 1 else 320  # Nachbarn überlappen nicht (bis 6 Punkte)
    rect(slide.shapes, "tl-line", (xs[0], line_y - 2, xs[-1] - xs[0], 4), "grey")
    for i, (cx, point) in enumerate(zip(xs, points), 1):
        circle(slide.shapes, f"tl-dot-{i}", cx, line_y, 13, fill="green", line=("white", 4))
        textbox(slide.shapes, f"tl-at-{i}", (cx - label_w / 2, y - 10, label_w, 54),
                [(point["at"], style("lead", "white" if dark else "navy", "display", align="center"))], anchor="b")
        textbox(slide.shapes, f"tl-label-{i}", (cx - label_w / 2, line_y + 30, label_w, 84),
                [(point["label"], style("body", "on_dark" if dark else "muted", align="center"))])


# ---------------------------------------------------------------- Fotomarker, Befunde, Quiz

def markers(slide, photo_box, items: list[dict], m: Measurer) -> None:
    px0, py0, pw, ph = photo_box
    for i, mk in enumerate(items, 1):
        cx, cy = px0 + mk["x"] * pw, py0 + mk["y"] * ph
        number_badge(slide, f"marker-{i}", (cx - 26, cy - 26, 52, 52), i, "navy", "white", 17, line=("white", 4))
    x, w = 1180, 620
    y = CONTENT_TOP
    hline(slide.shapes, "legend-rule", x, y, w, "navy")
    text_st = style(18, "navy")
    for i, mk in enumerate(items, 1):
        h = max(76, m.text_height_px(mk["label"], text_st, w - 70) + 30)
        number_badge(slide, f"legend-num-{i}", (x, y + h / 2 - 20, 40, 40), i, "navy", "white", 14)
        textbox(slide.shapes, f"legend-{i}", (x + 64, y, w - 64, h), [(mk["label"], text_st)], anchor="ctr")
        y += h
        hline(slide.shapes, f"legend-line-{i}", x, y, w, "grey")


def case_findings(slide, findings: list[dict], labels: tuple[str, str] = ("Befund", "Ursache"), y: float = 570) -> None:
    textbox(slide.shapes, "finding-head", (X0, y - 46, 640, 30), [(labels[0], label_st("green_ink"))])
    textbox(slide.shapes, "cause-head", (860, y - 46, 640, 30), [(labels[1], label_st("green_ink"))])
    hline(slide.shapes, "finding-rule", X0, y - 6, CONTENT_W, "navy")
    for i, item in enumerate(findings, 1):
        top = y + (i - 1) * 72
        textbox(slide.shapes, f"finding-{i}", (X0, top, 640, 64), [(item["finding"], style(18, "navy", "body_medium"))],
                anchor="ctr")
        shape(slide.shapes, MSO_SHAPE.RIGHT_ARROW, f"arrow-{i}", (784, top + 22, 40, 20), fill="green")
        textbox(slide.shapes, f"cause-{i}", (860, top, 940, 64), [(item["cause"], style(18, "muted"))], anchor="ctr")
        hline(slide.shapes, f"finding-line-{i}", X0, top + 68, CONTENT_W, "grey")


def quiz_options(slide, options: list[str], answer: int | None, explanation: str | None) -> None:
    for i, option in enumerate(options, 1):
        y = 480 + (i - 1) * 118
        correct = answer is not None and i - 1 == answer
        rect(slide.shapes, f"quiz-opt-{i}", (X0, y, 1500, 96), "green_light" if correct else "navy_deep")
        number_badge(slide, f"quiz-letter-{i}", (X0 + 28, y + 22, 52, 52), "ABC"[i - 1],
                     "navy" if correct else "navy_deep", "white" if correct else "green_light", 17,
                     line=None if correct else ("green_light", 2))
        textbox(slide.shapes, f"quiz-text-{i}", (X0 + 112, y, 1360, 96),
                [(option, style(21, "navy" if correct else "white", "body_medium" if correct else "body"))],
                anchor="ctr")
    if answer is not None and explanation:
        textbox(slide.shapes, "quiz-expl", (X0, 846, 1500, 104), [(explanation, style("body", "on_dark"))])
