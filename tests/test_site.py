import json
import re
import subprocess
import sys

from conftest import REPO, SKILL

sys.path.insert(0, str(REPO / "scripts" / "tools"))

from campus.build import build_deck  # noqa: E402
from build_site import (download_sources, favicon_svg, logo_file_svg, logo_svg, slide_records, versioned,  # noqa: E402
                        write_index, write_legal)

PLAN = {"presentation": {"title": "Zukunft im Kreislauf", "chapters": ["Die Gruppe", "Leistungen"]}, "slides": [
    {"type": "cover"},
    {"type": "chapter", "chapter": 2},
    {"type": "points", "chapter": 2, "kicker": "02 · Leistungen", "title": "Beratung",
     "points": [{"lead": "Analyse", "text": "Pflichten klären."}, {"lead": "Umsetzung", "text": "Systeme betreiben."}],
     "notes": "Hier kurz die Rolle erfragen."},
    {"type": "quote", "quote": "Haltung gegenüber Ressourcen.", "name": "Florian Werthmann"},
]}
SLIDES = [{"n": i, "title": f"Folie {i}", "kicker": "", "chapter": None, "notes": "",
           "src": f"slides/praesentation/{i:02d}.jpg", "thumb": f"slides/praesentation/thumb/{i:02d}.jpg"} for i in (1, 2)]
DECK = {"title": "Zukunft im Kreislauf", "chapters": ["Die Gruppe", "Leistungen"]}


def test_slide_records(template_path, tmp_path):
    deck = tmp_path / "deck.pptx"
    build_deck(PLAN, template_path, deck, SKILL / "examples")
    records = slide_records(deck)
    assert [r["n"] for r in records] == [1, 2, 3, 4]
    assert records[0]["title"] == "Zukunft im Kreislauf" and records[0]["chapter"] is None
    assert records[1]["chapter"] == 2                       # Kapitelring
    assert records[2]["chapter"] == 2 and records[2]["kicker"] == "02 · Leistungen"
    assert records[2]["notes"] == "Hier kurz die Rolle erfragen."
    assert records[3]["title"].startswith("„Haltung")       # Zitat ohne Titel
    assert records[2]["layout"] == "05 Punkte"


def test_write_index(tmp_path):
    layouts = [{"name": "01 Titel", "key": "cover", "src": "slides/layouts/01.jpg", "thumb": "slides/layouts/thumb/01.jpg"}]
    downloads = [{"label": "Beispiel-Präsentation als PDF", "href": "downloads/x.pdf", "size": "1,8 MB", "kind": "PDF"}]
    page = write_index(tmp_path, DECK, SLIDES, layouts, downloads).read_text(encoding="utf-8")
    assert '<meta name="robots" content="noindex, nofollow">' in page
    assert 'src="/slides/praesentation/01.jpg"' in page and 'src="/slides/praesentation/thumb/02.jpg"' in page
    assert 'href="/downloads/x.pdf"' in page and 'data-src="/slides/layouts/01.jpg"' in page
    assert "<title>ECOWERTH Campus · Zukunft im Kreislauf</title>" in page
    assert 'href="/abmelden"' in page and 'href="/impressum"' in page and 'href="/datenschutz"' in page
    assert page.count('class="logo"') == 2                 # Kopf und Fuß
    assert "<style" not in page and " style=" not in page    # CSP: keine Inline-Stile
    assert re.search(r"<script>(?!\s*$)", page) is None      # nur Daten-JSON und externes Skript
    data = json.loads(re.search(r'<script type="application/json" id="deck-data">(.*?)</script>', page, re.S).group(1))
    assert data["chapters"] == DECK["chapters"] and len(data["slides"]) == 2


def test_index_escapes_script_end(tmp_path):
    slides = [dict(SLIDES[0], notes="Achtung </script><script>alert(1)</script>")]
    page = write_index(tmp_path, DECK, slides, [], []).read_text(encoding="utf-8")
    assert "</script><script>alert" not in page


def test_legal_pages(tmp_path):
    imp, ds = write_legal(tmp_path)
    imp, ds = imp.read_text(encoding="utf-8"), ds.read_text(encoding="utf-8")
    assert "Angaben gemäß § 5 DDG" in imp and "Goldleite 9" in imp and "§ 18 Abs. 2 MStV" in imp
    assert "ew_campus" in ds and "§ 25 Abs. 2 Nr. 2 TDDDG" in ds and "Vercel" in ds
    for page in (imp, ds):
        assert "<style" not in page and " style=" not in page and "<script" not in page


def test_versioned(tmp_path):
    (tmp_path / "slides").mkdir()
    image = tmp_path / "slides" / "01.jpg"
    image.write_bytes(b"alt")
    old = versioned(tmp_path, "slides/01.jpg")
    image.write_bytes(b"neu")
    new = versioned(tmp_path, "slides/01.jpg")
    assert old.startswith("slides/01.jpg?v=") and old != new


def test_logo_variants():
    inline = logo_svg()
    assert inline.startswith('<svg class="logo" role="img" aria-label="ECOWERTH"') and 'class="sep"' in inline
    standalone = logo_file_svg()
    assert "currentColor" not in standalone and "#043751" in standalone and "#F4F6F8" in standalone
    icon = favicon_svg()
    assert icon.startswith("<svg") and "currentColor" not in icon and icon.count("<path") >= 3


def test_downloads():
    sources = download_sources()
    assert [name for _, _, name, _ in sources] == [
        "ecowerth-campus-zukunft-im-kreislauf.pdf", "ecowerth-campus-zukunft-im-kreislauf.pptx",
        "ecowerth-campus-vorlage.pptx", "ecowerth-campus-layouts.pdf"]


def test_vercel_config():
    cfg = json.loads((REPO / "vercel.json").read_text(encoding="utf-8"))
    assert cfg["outputDirectory"] == "site" and cfg["cleanUrls"] is True
    headers = {h["key"].lower(): h["value"] for rule in cfg["headers"] for h in rule["headers"]}
    assert headers["x-robots-tag"] == "noindex, nofollow"
    assert "frame-ancestors 'none'" in headers["content-security-policy"]
    assert not any("max-age" in v for v in headers.values())


def test_site_files_are_in_git():
    """Alles, was die Seite lädt, liegt im Repo – Vercel veröffentlicht nur, was eingecheckt ist."""
    res = subprocess.run(["git", "ls-files", "site"], cwd=REPO, capture_output=True, text=True, check=True)
    tracked = set(res.stdout.split())
    if not tracked:
        import pytest
        pytest.skip("noch nichts eingecheckt")
    css = (REPO / "site" / "assets" / "site.css").read_text(encoding="utf-8")
    page = (REPO / "site" / "index.html").read_text(encoding="utf-8")
    refs = {"site/assets/" + url.lstrip("./") for url in re.findall(r'url\("([^"?]+)', css) if not url.startswith("/")}
    refs |= {"site" + url for url in re.findall(r'url\("(/[^"?]+)', css)}
    refs |= {"site/" + url for url in re.findall(r'(?:src|href)="/((?:assets|slides|downloads)/[^"?]+)', page)}
    refs |= {"site/assets/fonts/OFL.txt", "site/assets/public/login.css", "site/assets/public/login.js",
             "site/assets/public/logo.svg", "site/impressum.html", "site/datenschutz.html", "site/favicon.svg"}
    assert sorted(ref for ref in refs if ref not in tracked) == []
