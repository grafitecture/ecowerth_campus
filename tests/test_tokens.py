import re

from campus.tokens import BRANDS, COLOR, FONT_FILES, FONTS, PH_IDX, px


def test_px():
    assert px(1920) == 12192000
    assert px(1080) == 6858000
    assert px(1) == 6350


def test_colors_are_ci():
    for name, value in COLOR.items():
        assert re.fullmatch(r"[0-9A-F]{6}", value), name
    # Markenfarben exakt wie auf ecowerth.de
    assert (COLOR["navy"], COLOR["green"], COLOR["blue"], COLOR["red"], COLOR["grey"]) == \
        ("043751", "6EA52E", "117EC2", "AC1920", "D9D9D9")


def test_every_font_role_can_be_measured():
    assert set(FONTS.values()) <= set(FONT_FILES)


def test_brands():
    assert list(BRANDS) == ["ecologicon", "ecoreloop", "ecoinvest"]
    assert [b["color"] for b in BRANDS.values()] == ["blue", "green", "red"]


def test_ph_idx_unique():
    values = list(PH_IDX.values())
    assert len(values) == len(set(values))
    assert PH_IDX["Title"] == 0
