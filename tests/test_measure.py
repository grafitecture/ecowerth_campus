from campus.measure import Para
from campus.tokens import FONTS


def test_width_monotonic(m):
    assert m.width_px("Kreislauf", 20) < m.width_px("Kreislaufwirtschaft", 20)
    assert m.width_px("Kreislauf", 20) < m.width_px("Kreislauf", 30)


def test_fonts_differ(m):
    mono = m.width_px("iiii", 20, font=FONTS["mono"])
    sans = m.width_px("iiii", 20, font=FONTS["body"])
    assert mono > sans                                  # Mono: jedes Zeichen gleich breit


def test_wrap(m):
    assert m.wrap("Zukunft im Kreislauf", 20, 2000) == ["Zukunft im Kreislauf"]
    lines = m.wrap("Werte bewahren. Kreisläufe schließen. " * 4, 20, 400)
    assert len(lines) > 2 and all(m.width_px(line, 20) <= 400 for line in lines)


def test_unbreakable_word_ends(m):
    word = "Kreislaufwirtschaftsgesetzesänderungsverordnung"
    lines = m.wrap(word, 40, 300, font=FONTS["display"])
    assert len(lines) > 1 and "".join(lines) == word
    assert m.long_words(word, 40, 300, font=FONTS["display"]) == [word]


def test_line_height_by_font(m):
    assert m.line_height_px(20, font=FONTS["body"]) > m.line_height_px(20, font=FONTS["display"])


def test_block_height_adds_paragraphs(m):
    one = m.block_height_px([Para("Eins", 17)], 1000)
    two = m.block_height_px([Para("Eins", 17), Para("Zwei", 17, spc_before_pt=6)], 1000)
    assert two > 2 * one
