from PIL import Image

from campus.tokens import BRANDS, LOGO_RATIO
from conftest import SKILL

BRAND = SKILL / "assets" / "brand"


def test_logo_pngs():
    for name in ("logo-navy.png", "logo-white.png"):
        im = Image.open(BRAND / name)
        assert im.mode == "RGBA"
        assert im.width >= 1600
        assert abs(im.width / im.height - LOGO_RATIO) / LOGO_RATIO < 0.01
        assert im.getpixel((im.width - 1, 0))[3] == 0   # freigestellt


def test_logo_svg_is_recolorable():
    """ECOWERTH-Logo (FINAL1): Wortmarke und Unterzeile in currentColor, Signet in den Markenfarben."""
    svg = (BRAND / "logo.svg").read_text(encoding="utf-8")
    assert svg.count('fill="currentColor"') == 1
    assert "#043751" not in svg
    for color in ("#117EC2", "#6EA52E", "#AC1920", "#D9D9D9"):
        assert color in svg


def test_campus_lockups():
    """ECOWERTH | CAMPUS: positiv mit graublauer Linie und Schrift, auf Blau Linie und CAMPUS weiß."""
    pos = (BRAND / "logo-campus.svg").read_text(encoding="utf-8")
    neg = (BRAND / "logo-campus-weiss.svg").read_text(encoding="utf-8")
    assert "#043751" in pos and "#627078" in pos
    assert "#043751" not in neg and "#627078" not in neg and "#FFFFFF" in neg
    for color in ("#117EC2", "#6EA52E", "#AC1920"):
        assert color in pos and color in neg


def test_brand_wordmarks():
    for brand in BRANDS.values():
        im = Image.open(SKILL / "assets" / brand["logo"])
        assert im.mode == "RGBA" and im.width > 800


def test_example_photos():
    photos = SKILL / "examples" / "photos"
    for name in ("sortierhalle.jpg", "florian-werthmann.jpg", "electro-box.jpg", "green-box.jpg"):
        im = Image.open(photos / name)
        assert im.format == "JPEG" and im.width >= 800
