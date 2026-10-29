"""Design-Tokens für ECOWERTH Campus (Corporate Identity wie ecowerth.de).

Raster 1920 × 1080 px auf 13,333 × 7,5 Zoll: 1 px = 6350 EMU, 1 pt = 2 px.
"""

SLIDE_PX = (1920, 1080)
EMU_PER_PX = 6350
SLIDE_EMU = (12192000, 6858000)

# Schriften wie auf der Website: Archivo für Überschriften, IBM Plex Sans für Text,
# IBM Plex Mono für Kicker, Nummern, Labels und Paragrafen-Chips.
# Rolle → (Schriftname, wie PowerPoint ihn kennt, fett)
FONTS = {
    "display": ("Archivo SemiBold", False),
    "display_regular": ("Archivo", False),
    "display_bold": ("Archivo", True),
    "body": ("IBM Plex Sans", False),
    "body_medium": ("IBM Plex Sans Medium", False),
    "mono": ("IBM Plex Mono", False),
    "mono_medium": ("IBM Plex Mono Medium", False),
}
# (Schriftname, fett) → Datei für die Textmessung
FONT_FILES = {
    ("Archivo SemiBold", False): "Archivo-SemiBold.ttf",
    ("Archivo", False): "Archivo-Regular.ttf",
    ("Archivo", True): "Archivo-Bold.ttf",
    ("IBM Plex Sans", False): "IBMPlexSans-Regular.ttf",
    ("IBM Plex Sans Medium", False): "IBMPlexSans-Medium.ttf",
    ("IBM Plex Mono", False): "IBMPlexMono-Regular.ttf",
    ("IBM Plex Mono Medium", False): "IBMPlexMono-Medium.ttf",
}
THEME_MAJOR = "Archivo SemiBold"
THEME_MINOR = "IBM Plex Sans"

COLOR = {
    # Markenfarben
    "navy": "043751",
    "green": "6EA52E",
    "blue": "117EC2",
    "red": "AC1920",
    "grey": "D9D9D9",
    # Textsichere Varianten und Tönungen (wie auf der Website)
    "green_ink": "4F7A1E",
    "blue_ink": "0F6AA6",
    "red_ink": "AC1920",
    "green_tint": "EDF4E3",
    "blue_tint": "E3F0F8",
    "red_tint": "F8E7E8",
    # Flächen und Text
    "white": "FFFFFF",
    "bg": "F4F6F8",
    "surface2": "E7ECF1",
    "muted": "4A6079",
    "steel": "A3B6C9",
    # Auf Dunkelblau
    "navy_deep": "032C41",
    "line_dark": "325C72",
    "on_dark": "E8EEF4",
    "muted_dark": "A3B6C9",
    "green_light": "8FC65A",
}

# Markenfarbe je Untermarke: Fläche/Balken und textsichere Variante
BRANDS = {
    "ecologicon": {"name": "ECOLOGICON", "color": "blue", "ink": "blue_ink", "logo": "brand/ecologicon.png"},
    "ecoreloop": {"name": "ECORELOOP", "color": "green", "ink": "green_ink", "logo": "brand/ecoreloop.png"},
    "ecoinvest": {"name": "ECOINVEST", "color": "red", "ink": "red_ink", "logo": "brand/ecoinvest.png"},
}

SIZE_PT = {
    "display": 58,
    "chapter_number": 120,
    "chapter_title": 60,
    "agenda": 28,
    "title": 40,
    "quote": 34,
    "statement_big": 150,
    "statement": 32,
    "fact": 60,
    "line": 24,
    "focus_title": 22,
    "lead": 22,
    "subtitle": 22,
    "fact_label": 17,
    "body": 17,
    "number": 15,
    "kicker": 13,
    "small": 13,
    "chip": 12,
    "nav": 12,
    "label": 11,
    "footer": 10,
}

# Laufweite in 1/100 pt (Website: Eyebrows .14em, Labels .08–.1em, Navigation .06em)
KICKER_SPC = 182
LABEL_SPC = 110
NAV_SPC = 72

# Raster
MARGIN_X = 120
CONTENT_W = 1680
HEAD_H = 112                         # Kopfzeile mit Logo und Kapitel-Navigation, Haarlinie darunter
LOGO_RATIO = 427.710156 / 71.207031  # Breite : Höhe der Wortmarke
LOGO_BOX = (120, 40, 192, 32)        # Logo in der Kopfzeile
COVER_LOGO_BOX = (120, 92, 336, 56)
CONTENT_TOP = 340
CONTENT_BOTTOM = 900
SOURCE_Y = 920                       # Quelle oder Paragrafen-Chips über der Fußzeile
FOOT_LINE_Y = 984
FOOT_TEXT_Y = 1000
LINE_PX = 2                          # Haarlinien: 1 pt, damit sie auch verkleinert stehen bleiben

PH_IDX = {
    "Title": 0,
    "Kicker": 11,
    "Subtitle": 12,
    "Presenter": 13,
    "Credentials": 14,
    "Photo": 15,
    "Number": 16,
    "Line": 17,
    "Quote": 18,
    "TruthLabel": 19,
    "TruthText": 20,
    "AnswerLabel": 21,
    "AnswerText": 22,
    "NextLabel": 23,
    "NextTitle": 24,
    "NextText": 25,
    "Points": 26,
    "Caption": 27,
    "Big": 28,
    "Statement": 29,
    "Text": 30,
    "PhotoLeft": 31,
    "PhotoRight": 32,
    "LabelLeft": 33,
    "LabelRight": 34,
    "Story": 35,
    "Question": 36,
    "Lead": 37,
    "Name": 38,
    "Role": 39,
}


def px(v: float) -> int:
    """Rasterpixel → EMU."""
    return int(round(v * EMU_PER_PX))


def font_of(role: str) -> tuple[str, bool]:
    """Schriftname und Fett-Schalter für eine Schriftrolle."""
    return FONTS[role]
