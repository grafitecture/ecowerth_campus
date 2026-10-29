"""Deklarative Definition der 23 Layouts (Maße in px auf dem 1920 × 1080-Raster)."""
from dataclasses import dataclass, field
from typing import Literal

from .tokens import (COLOR, COVER_LOGO_BOX, FOOT_LINE_Y, HEAD_H, KICKER_SPC, LABEL_SPC, LINE_PX, LOGO_BOX,
                     MARGIN_X, CONTENT_W, SIZE_PT)

Box = tuple[float, float, float, float]


@dataclass
class PhDef:
    name: str
    ph_type: Literal["title", "body", "pic"]
    box: Box
    levels: list[dict]
    prompt: list[str]
    anchor: str = "t"
    geom: str = "rect"
    fill: str | None = None
    fill_alpha: int | None = None
    line: tuple | None = None          # (Farbe, Breite px)
    insets: tuple[float, float, float, float] = (0, 0, 0, 0)


@dataclass
class DecorDef:
    kind: Literal["rect", "text", "image", "hline", "ellipse", "kreislauf"]
    name: str
    box: Box
    style: dict = field(default_factory=dict)


@dataclass
class LayoutDef:
    name: str
    key: str
    frame: Literal["cover", "dark", "light", "full"]
    placeholders: list[PhDef]
    decor: list[DecorDef]


def lvl(size: str | float, color: str, font: str = "body", **extra) -> dict:
    """Ebenen-Stil: Größe als SIZE_PT-Schlüssel oder pt-Zahl, Farbe als COLOR-Schlüssel, Schriftrolle."""
    size_pt = SIZE_PT[size] if isinstance(size, str) else size
    return {"size_pt": size_pt, "color": COLOR[color], "font": font, **extra}


def kicker_lvl(dark: bool) -> dict:
    return lvl("kicker", "green_light" if dark else "green_ink", "mono_medium", caps=True, spc=KICKER_SPC)


def label_lvl(color: str) -> dict:
    return lvl("label", color, "mono_medium", caps=True, spc=LABEL_SPC)


POINT_LEVELS = [
    lvl("lead", "navy", "display", spc_before_pt=22, mar_l_px=72, indent_px=-72, tab_px=72),
    lvl("body", "muted", spc_before_pt=6, mar_l_px=72),
]
PIC_LEVELS = [lvl("small", "muted", align="center")]


def kicker_ph(dark: bool) -> PhDef:
    return PhDef("Kicker", "body", (MARGIN_X, 158, CONTENT_W, 36), [kicker_lvl(dark)], ["Kapitel · Thema"])


def title_ph(dark: bool) -> PhDef:
    return PhDef("Title", "title", (MARGIN_X - 3, 196, CONTENT_W, 110),
                 [lvl("title", "white" if dark else "navy", "display")], ["Folientitel"])


def points_ph(box: Box) -> PhDef:
    return PhDef("Points", "body", box, POINT_LEVELS, ["01\tPunkt", "Kurze Erklärung"])


def pic_ph(name: str, box: Box, **extra) -> PhDef:
    return PhDef(name, "pic", box, PIC_LEVELS, ["Foto einfügen"], anchor="ctr", **extra)


def text_ph(name: str, box: Box, size: str | float, color: str, prompt: str, font: str = "body", **extra) -> PhDef:
    level_extra = {k: extra.pop(k) for k in ("ln_spc_pct", "align", "caps", "spc") if k in extra}
    return PhDef(name, "body", box, [lvl(size, color, font, **level_extra)], [prompt], **extra)


def frame_decor(frame: str) -> list[DecorDef]:
    """Rahmen je Typ: Kopfzeile mit Logo und Haarlinie, Fußlinie; Titelfolie mit Kreislauf."""
    if frame == "full":
        return []
    if frame == "cover":
        return [
            DecorDef("image", "cover-logo", COVER_LOGO_BOX, {"file": "brand/logo-white.png"}),
            DecorDef("kreislauf", "cover-loop", (1440, 560, 372, 372),
                     {"core_fill": "white", "dot_color": "white", "hair_color": "line_dark"}),
        ]
    dark = frame == "dark"
    line = COLOR["line_dark"] if dark else COLOR["grey"]
    return [
        DecorDef("image", "head-logo", LOGO_BOX, {"file": f"brand/logo-{'white' if dark else 'navy'}.png"}),
        DecorDef("hline", "head-line", (0, HEAD_H, 1920, LINE_PX), {"color": line}),
        DecorDef("hline", "foot-line", (MARGIN_X, FOOT_LINE_Y, CONTENT_W, LINE_PX), {"color": line}),
    ]


def _card(name: str, box: Box, accent: bool) -> list[DecorDef]:
    """Karte auf Dunkelblau; die hervorgehobene trägt links eine grüne Kante (wie .legal-box der Website)."""
    cards = [DecorDef("rect", name, box, {"fill": COLOR["navy_deep"]})]
    if accent:
        x, y, _, h = box
        cards.append(DecorDef("rect", f"{name}-accent", (x, y, 6, h), {"fill": COLOR["green"]}))
    return cards


def _layout(name: str, key: str, frame: str, placeholders=(), decor=()) -> LayoutDef:
    return LayoutDef(name, key, frame, list(placeholders), list(decor))


def _light(name: str, key: str, *extra: PhDef, title: bool = True, decor=()) -> LayoutDef:
    head = [kicker_ph(False), title_ph(False)] if title else [kicker_ph(False)]
    return _layout(name, key, "light", [*head, *extra], decor)


def _dark(name: str, key: str, *extra: PhDef, title: bool = True, decor=()) -> LayoutDef:
    head = [kicker_ph(True), title_ph(True)] if title else [kicker_ph(True)]
    return _layout(name, key, "dark", [*head, *extra], decor)


_PHOTO_CARD = {"fill": COLOR["navy"]}   # deckend und 2 px überlappend: eine Karte ohne Fugen

# Kapitel: Ring links (Mitte 480/600), Text rechts
CHAPTER_RING = (440, 600, 250, 30)       # Mitte x, Mitte y, Radius, Strichbreite
CHAPTER_HAIR_R = 300

LAYOUTS: list[LayoutDef] = [
    _layout("01 Titel", "cover", "cover", [
        PhDef("Kicker", "body", (MARGIN_X, 328, 880, 36), [kicker_lvl(True)], ["ECOWERTH · Präsentation"]),
        PhDef("Title", "title", (MARGIN_X - 4, 372, 900, 300), [lvl("display", "white", "display", ln_spc_pct=92)],
              ["Titel der Präsentation"]),
        text_ph("Subtitle", (MARGIN_X, 690, 840, 124), "subtitle", "on_dark", "Untertitel"),
        text_ph("Presenter", (MARGIN_X, 858, 880, 52), 19, "white", "Name", "body_medium"),
        text_ph("Credentials", (MARGIN_X, 910, 880, 70), "chip", "muted_dark", "Funktion\nDatum · Ort", "mono"),
    ]),
    _light("02 Agenda", "agenda"),
    _layout("03 Kapitel", "chapter", "dark", [
        PhDef("Number", "body", (CHAPTER_RING[0] - 200, CHAPTER_RING[1] - 130, 400, 260),
              [lvl("chapter_number", "white", "display", align="center")], ["01"], anchor="ctr"),
        PhDef("Kicker", "body", (840, 392, 960, 36), [kicker_lvl(True)], ["Kapitel 1 von 5"]),
        PhDef("Title", "title", (836, 436, 964, 132), [lvl("chapter_title", "white", "display", ln_spc_pct=92)],
              ["Kapitel"]),
        text_ph("Line", (840, 592, 880, 150), "line", "on_dark", "Ein Satz zu diesem Kapitel."),
    ], decor=[
        DecorDef("ellipse", "chapter-hair", (CHAPTER_RING[0] - CHAPTER_HAIR_R, CHAPTER_RING[1] - CHAPTER_HAIR_R,
                                             2 * CHAPTER_HAIR_R, 2 * CHAPTER_HAIR_R),
                 {"line": (COLOR["line_dark"], LINE_PX)}),
    ]),
    _layout("04 Einstieg", "hook", "dark", [
        kicker_ph(True),
        text_ph("Quote", (MARGIN_X, 200, 1560, 290), "quote", "white", "Die Frage Ihres Gegenübers",
                "display_regular", ln_spc_pct=112),
        PhDef("TruthLabel", "body", (170, 580, 700, 30), [label_lvl("muted_dark")], ["Ausgangslage"]),
        text_ph("TruthText", (170, 628, 700, 230), 19, "on_dark", "Was heute passiert."),
        PhDef("AnswerLabel", "body", (1010, 580, 740, 30), [label_lvl("green_light")], ["Unsere Antwort"]),
        text_ph("AnswerText", (1010, 628, 740, 230), 19, "white", "Wie ECOWERTH es löst."),
    ], decor=[
        *_card("truth-card", (MARGIN_X, 540, 800, 340), accent=False),
        *_card("answer-card", (960, 540, 840, 340), accent=True),
    ]),
    _light("05 Punkte", "points", points_ph((MARGIN_X, 340, 1560, 560))),
    _light("06 Punkte + Foto", "points_photo", points_ph((MARGIN_X, 340, 760, 560)),
           pic_ph("Photo", (960, 330, 840, 473)),
           text_ph("Caption", (960, 820, 840, 40), "small", "muted", "Bildunterschrift")),
    _light("07 Punkte + Grafik", "points_chart", points_ph((MARGIN_X, 340, 760, 560))),
    _light("08 Aussage", "statement",
           PhDef("Big", "body", (MARGIN_X - 6, 228, 1560, 320),
                 [lvl("statement_big", "green_ink", "display", ln_spc_pct=85)], ["4"]),
           text_ph("Statement", (MARGIN_X, 570, 1560, 150), "statement", "navy", "Aussage in ein bis zwei Zeilen",
                   "display"),
           text_ph("Text", (MARGIN_X, 740, 1560, 130), "body", "muted", "Ergänzender Satz."), title=False),
    _light("09 Kennzahlen", "facts",
           text_ph("Lead", (MARGIN_X, 330, 1400, 140), 20, "muted", "Einleitender Satz zu den Kennzahlen."),
           decor=[DecorDef("rect", "facts-band", (0, 540, 1920, 350), {"fill": COLOR["green"]})]),
    _light("10 Marken", "brands"),
    _light("11 Checkliste", "checklist"),
    _light("12 Schritte", "steps"),
    _light("13 Vergleich", "compare"),
    _light("14 Tabelle", "matrix"),
    _light("15 Skala", "scale", points_ph((MARGIN_X, 600, 1560, 300))),
    _layout("16 Foto", "photo", "full", [
        pic_ph("Photo", (0, 0, 1920, 1080)),
        PhDef("Kicker", "body", (MARGIN_X, 760, 1400, 62), [kicker_lvl(True)], ["Kapitel · Thema"],
              insets=(44, 24, 44, 0), **_PHOTO_CARD),
        PhDef("Title", "title", (MARGIN_X, 820, 1400, 102), [lvl("title", "white", "display")], ["Fototitel"],
              insets=(44, 8, 44, 0), **_PHOTO_CARD),
        text_ph("Caption", (MARGIN_X, 920, 1400, 88), "body", "on_dark", "Bildunterschrift",
                insets=(44, 0, 44, 22), **_PHOTO_CARD),
    ]),
    _light("17 Zwei Fotos", "photo_pair",
           pic_ph("PhotoLeft", (MARGIN_X, 340, 820, 461)), pic_ph("PhotoRight", (980, 340, 820, 461)),
           text_ph("LabelLeft", (MARGIN_X, 824, 820, 44), 21, "navy", "Links", "display"),
           text_ph("LabelRight", (980, 824, 820, 44), 21, "navy", "Rechts", "display")),
    _light("18 Foto mit Markierungen", "photo_annotated", pic_ph("Photo", (MARGIN_X, 330, 1000, 563))),
    _light("19 Praxisfall", "case",
           text_ph("Story", (MARGIN_X, 336, 1560, 150), 24, "navy", "Der Fall in zwei, drei Sätzen.",
                   "display_regular", ln_spc_pct=110)),
    _layout("20 Zitat", "quote", "dark", [
        kicker_ph(True),
        pic_ph("Photo", (MARGIN_X, 250, 480, 600)),
        text_ph("Quote", (720, 250, 1080, 450), "quote", "white", "„Zitat in zwei bis vier Zeilen.“",
                "display_regular", ln_spc_pct=115),
        text_ph("Name", (720, 740, 1080, 56), 24, "white", "Name", "display"),
        PhDef("Role", "body", (720, 800, 1080, 36), [label_lvl("muted_dark")], ["Funktion"]),
    ]),
    _dark("21 Wissenscheck", "quiz",
          text_ph("Question", (MARGIN_X, 200, 1560, 230), "quote", "white", "Frage?", "display", ln_spc_pct=105),
          title=False),
    _light("22 Zusammenfassung", "summary"),
    _dark("23 Abschluss", "closing",
          PhDef("NextLabel", "body", (1210, 384, 540, 30), [label_lvl("green_light")], ["Kontakt"]),
          text_ph("NextTitle", (1210, 428, 540, 100), 26, "white", "Name", "display"),
          text_ph("NextText", (1210, 536, 540, 190), "body", "on_dark", "Funktion, Telefon, E-Mail"),
          decor=_card("next-card", (1160, 340, 640, 420), accent=True)),
]
