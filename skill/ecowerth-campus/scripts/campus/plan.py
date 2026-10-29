"""Folienplan (JSON) laden und prüfen.

Fehlertexte: "presentation: …" bzw. "slide {n} ({type}): …"; alle Fehler werden gesammelt.
Geprüft werden Pflichtfelder, Anzahlen und Typen, damit der Bau nie mit einem Traceback abbricht.
"""
import json
from pathlib import Path

from .tokens import BRANDS

# Optionale Textfelder auf Folienebene; Pflichtfelder prüfen die Typ-Prüfungen unten zusätzlich.
OPTIONAL_TEXT = ("kicker", "title", "source", "notes", "caption", "line", "big", "statement", "text",
                 "explanation", "style", "lead")
BOX_TEXT = ("label", "title", "text")


class PlanError(Exception):
    def __init__(self, errors: list[str]):
        super().__init__("\n".join(errors))
        self.errors = errors


def _is_text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _text(obj: dict, key: str) -> list[str]:
    value = obj.get(key)
    if value is not None and not isinstance(value, str):
        return [f"'{key}' muss Text sein"]
    return [] if _is_text(value) else [f"'{key}' fehlt"]


def _optional_text(obj: dict, keys: tuple[str, ...], prefix: str = "") -> list[str]:
    return [f"{prefix}'{k}' muss Text sein" for k in keys if k in obj and not isinstance(obj[k], str)]


def _photo(value, name: str = "photo") -> list[str]:
    if not isinstance(value, dict):
        return [f"{name} braucht 'file' oder 'brief'"]
    problems = _optional_text(value, ("file", "brief"), f"{name} ")
    if "fit" in value and not isinstance(value["fit"], bool):
        problems.append(f"{name} 'fit' muss true oder false sein")
    if problems:
        return problems
    return [] if (_is_text(value.get("file")) or _is_text(value.get("brief"))) else [f"{name} braucht 'file' oder 'brief'"]


def _items(value, name: str, lo: int, hi: int, keys: tuple[str, ...] = (), optional: tuple[str, ...] = ()) -> list[str]:
    if not isinstance(value, list) or not lo <= len(value) <= hi:
        return [f"{name}: genau {lo} Einträge" if lo == hi else f"{name}: {lo}–{hi} Einträge"]
    problems = []
    for i, item in enumerate(value, 1):
        if not keys and not optional:
            if not _is_text(item):
                problems.append(f"{name}[{i}] muss Text sein")
            continue
        if not isinstance(item, dict):
            problems.append(f"{name}[{i}] muss ein Objekt sein")
            continue
        wrong = [k for k in keys + optional if k in item and item[k] is not None and not isinstance(item[k], str)]
        problems += [f"{name}[{i}] '{k}' muss Text sein" for k in wrong]
        missing = [k for k in keys if k not in wrong and not _is_text(item.get(k))]
        if missing:
            problems.append(f"{name}[{i}] fehlt {', '.join(missing)}")
    return problems


def _box(value, name: str, keys: tuple[str, ...]) -> list[str]:
    if not isinstance(value, dict):
        return [f"'{name}' fehlt"]
    wrong = [k for k in BOX_TEXT if k in value and not isinstance(value[k], str)]
    problems = [f"{name} '{k}' muss Text sein" for k in wrong]
    return problems + [f"{name} fehlt '{k}'" for k in keys if k not in wrong and not _is_text(value.get(k))]


def _focus(slide: dict) -> list[str]:
    return _box(slide["focus"], "focus", ("title",)) if "focus" in slide else []


def _legal(slide: dict) -> list[str]:
    if "legal" not in slide:
        return []
    return _items(slide["legal"], "legal", 1, 6)


def _check_points(s):
    return _text(s, "title") + _items(s.get("points"), "points", 2, 4, ("lead", "text")) + _focus(s)


def _check_points_photo(s):
    return _text(s, "title") + _items(s.get("points"), "points", 2, 4, ("lead", "text")) + _photo(s.get("photo"))


def _check_points_chart(s):
    problems = _text(s, "title") + _items(s.get("points"), "points", 2, 4, ("lead", "text"))
    chart = s.get("chart")
    if not isinstance(chart, dict):
        return problems + ["'chart' fehlt"]
    problems += _optional_text(chart, ("title", "note"), "chart ")
    problems += _items(chart.get("bars"), "chart.bars", 2, 4, ("label",))
    for i, bar in enumerate(chart.get("bars") or [], 1):
        if not isinstance(bar, dict):
            continue
        value = bar.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 100:
            problems.append(f"chart.bars[{i}] value muss 0–100 sein")
        problems += _optional_text(bar, ("display",), f"chart.bars[{i}] ")
    return problems


def _check_steps(s):
    """Text-Schritte (3–5, Titel + Text) oder Foto-Schritte (2–4, Titel + Foto, optional Bildunterschrift)."""
    problems = _text(s, "title")
    steps = s.get("steps")
    with_photo = [isinstance(st, dict) and "photo" in st for st in steps] if isinstance(steps, list) else []
    if any(with_photo):
        if not all(with_photo):
            return problems + ["entweder jeder Schritt mit Foto oder keiner"]
        problems += _items(steps, "steps", 2, 4, ("title",))
        for i, st in enumerate(steps, 1):
            problems += _photo(st.get("photo"), f"steps[{i}].photo")
            if "text" in st:
                problems.append(f"steps[{i}] 'text' erscheint bei Fotos nicht – Bildunterschrift oder Notizen nutzen")
    else:
        problems += _items(steps, "steps", 3, 5, ("title", "text"))
        if "caption" in s:
            problems.append("'caption' gibt es nur bei Schrittfotos")
    start = s.get("start", 1)
    if not isinstance(start, int) or isinstance(start, bool) or start < 1:
        problems.append("'start' muss eine ganze Zahl ab 1 sein")
    return problems


def _check_statement(s):
    if not (_is_text(s.get("big")) or _is_text(s.get("statement"))):
        return ["braucht 'big' oder 'statement'"]
    return []


def _check_facts(s):
    return _text(s, "title") + _items(s.get("facts"), "facts", 2, 4, ("value", "label"))


def _check_brands(s):
    problems = _text(s, "title")
    columns = s.get("columns")
    if not isinstance(columns, list) or not 2 <= len(columns) <= 3:
        return problems + ["columns: 2–3 Einträge"]
    for i, c in enumerate(columns, 1):
        if not isinstance(c, dict):
            problems.append(f"columns[{i}] muss ein Objekt sein")
            continue
        if "brand" in c and c["brand"] not in BRANDS:
            problems.append(f"columns[{i}] brand muss {', '.join(BRANDS)} sein")
        elif "brand" not in c and not _is_text(c.get("title")):
            problems.append(f"columns[{i}] braucht 'brand' oder 'title'")
        problems += _optional_text(c, ("title", "label", "from", "text"), f"columns[{i}] ")
        if "items" in c:
            problems += _items(c["items"], f"columns[{i}].items", 1, 5)
    return problems


def _check_agenda(s, chapters: list) -> list[str]:
    if "items" in s:
        return _items(s["items"], "items", 2, 6, ("title",), ("text",))
    return [] if len(chapters) >= 2 else ["braucht 'items' oder Kapitel in 'presentation.chapters'"]


def _check_matrix(s):
    problems = _text(s, "title")
    columns = s.get("columns")
    problems += _items(columns, "columns", 2, 7)
    rows = s.get("rows")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 10:
        return problems + ["rows: 1–10 Einträge"]
    n = len(columns) if isinstance(columns, list) else None
    for i, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            problems.append(f"rows[{i}] muss ein Objekt sein")
            continue
        problems += [f"rows[{i}] {p}" for p in _text(row, "label")]
        cells = row.get("cells")
        if not isinstance(cells, list) or (n is not None and len(cells) != n):
            problems.append(f"rows[{i}] cells: so viele Einträge wie columns")
            continue
        for j, cell in enumerate(cells, 1):
            if not (isinstance(cell, bool) or isinstance(cell, str)):
                problems.append(f"rows[{i}].cells[{j}] muss true, false oder Text sein")
    if "note" in s and not isinstance(s["note"], str):
        problems.append("'note' muss Text sein")
    if "note" in s and ("source" in s or "legal" in s):
        problems.append("'note' und 'source'/'legal' liegen an derselben Stelle – nur eins davon")
    return problems


def _check_scale(s):
    problems = _text(s, "title")
    if "scale" in s:
        scale = s["scale"]
        if not isinstance(scale, dict):
            return problems + ["'scale' muss ein Objekt sein"]
        problems += _items(scale.get("items"), "scale.items", 2, 16)
        highlight = scale.get("highlight", [])
        if not isinstance(highlight, list) or not all(isinstance(h, str) for h in highlight):
            problems.append("scale.highlight muss eine Liste von Texten sein")
    elif "timeline" in s:
        timeline = s["timeline"]
        if not isinstance(timeline, dict):
            return problems + ["'timeline' muss ein Objekt sein"]
        problems += _items(timeline.get("points"), "timeline.points", 2, 6, ("at", "label"))
    elif "tags" in s:
        tags = s["tags"]
        if not isinstance(tags, dict):
            return problems + ["'tags' muss ein Objekt sein"]
        problems += _items(tags.get("items"), "tags.items", 2, 16)
        highlight = tags.get("highlight", [])
        if not isinstance(highlight, list) or not all(isinstance(h, str) for h in highlight):
            problems.append("tags.highlight muss eine Liste von Texten sein")
    else:
        problems.append("braucht 'scale', 'timeline' oder 'tags'")
    if "points" in s:
        problems += _items(s["points"], "points", 1, 2, ("lead", "text"))
    return problems


def _check_compare(s):
    problems = _text(s, "title")
    for side in ("left", "right"):
        box = s.get(side)
        problems += _box(box, side, ("label",))
        if isinstance(box, dict):
            problems += _items(box.get("items"), f"{side}.items", 1, 4)
    if s.get("style", "do_dont") not in ("do_dont", "myth_fact", "neutral"):
        problems.append("style muss 'do_dont', 'myth_fact' oder 'neutral' sein")
    return problems


def _check_photo_pair(s):
    problems = _text(s, "title")
    for side in ("left", "right"):
        box = s.get(side)
        problems += _box(box, side, ("label",))
        if isinstance(box, dict):
            problems += _photo(box.get("photo"), f"{side}.photo")
    return problems


def _check_photo(s):
    problems = _text(s, "title") + _photo(s.get("photo"))
    for key in ("source", "legal"):
        if key in s:  # Quelle und Chips lägen über dem Textband
            problems.append(f"'{key}' erscheint auf Fotofolien nicht – in die Bildunterschrift schreiben")
    return problems


def _check_photo_annotated(s):
    problems = _text(s, "title") + _photo(s.get("photo")) + _items(s.get("markers"), "markers", 1, 5, ("label",))
    for i, mk in enumerate(s.get("markers") or [], 1):
        if not isinstance(mk, dict) or not all(isinstance(mk.get(k), (int, float)) and not isinstance(mk.get(k), bool)
                                                and 0 <= mk[k] <= 1 for k in ("x", "y")):
            problems.append(f"markers[{i}] x und y müssen 0–1 sein")
    return problems


def _check_case(s):
    problems = _text(s, "title") + _text(s, "story")
    problems += _items(s.get("findings"), "findings", 1, 5, ("finding", "cause"))
    if "columns" in s:
        problems += _items(s["columns"], "columns", 2, 2)
    return problems


def _check_quote(s):
    problems = _text(s, "quote") + _text(s, "name") + _optional_text(s, ("role",))
    if "photo" in s:
        problems += _photo(s["photo"])
    return problems


def _check_quiz(s):
    problems = _text(s, "question") + _items(s.get("options"), "options", 3, 3)
    if s.get("answer") not in (0, 1, 2) or isinstance(s.get("answer"), bool):
        problems.append("answer muss 0–2 sein")
    return problems


CHECKS = {
    "cover": lambda s: [],
    "agenda": None,   # braucht die Kapitel, siehe validate_plan
    "chapter": lambda s: [] if "chapter" in s else ["'chapter' fehlt"],
    "hook": lambda s: _text(s, "quote") + _box(s.get("truth"), "truth", ("text",))
    + _box(s.get("answer"), "answer", ("text",)),
    "points": _check_points,
    "points_photo": _check_points_photo,
    "points_chart": _check_points_chart,
    "statement": _check_statement,
    "facts": _check_facts,
    "brands": _check_brands,
    "checklist": lambda s: _text(s, "title") + _items(s.get("items"), "items", 1, 8) + _focus(s),
    "steps": _check_steps,
    "compare": _check_compare,
    "matrix": _check_matrix,
    "scale": _check_scale,
    "photo": _check_photo,
    "photo_pair": _check_photo_pair,
    "photo_annotated": _check_photo_annotated,
    "case": _check_case,
    "quote": _check_quote,
    "quiz": _check_quiz,
    "summary": lambda s: _text(s, "title") + _items(s.get("items"), "items", 1, 5, ("title", "text")),
    "closing": lambda s: _text(s, "title") + _items(s.get("steps"), "steps", 1, 3, ("title", "text"))
    + _box(s.get("next"), "next", ("title",)),
}
SLIDE_TYPES = tuple(CHECKS)


def _check_presentation(pres) -> list[str]:
    if not isinstance(pres, dict):
        return ["presentation: fehlt"]
    problems = _text(pres, "title") + _optional_text(pres, ("subtitle", "kicker", "date"))
    if "chapters" in pres:
        problems += _items(pres["chapters"], "chapters", 2, 6)
    if "presenter" in pres:
        presenter = pres["presenter"]
        if not isinstance(presenter, dict):
            problems.append("'presenter' muss ein Objekt sein")
        else:
            problems += _optional_text(presenter, ("name", "role"), "presenter ")
    return [f"presentation: {p}" for p in problems]


def chapters_of(plan: dict) -> list[str]:
    pres = plan.get("presentation") if isinstance(plan, dict) else None
    chapters = pres.get("chapters") if isinstance(pres, dict) else None
    return chapters if isinstance(chapters, list) else []


def validate_plan(plan: dict) -> list[str]:
    pres = plan.get("presentation") if isinstance(plan, dict) else None
    errors = _check_presentation(pres)
    chapters = chapters_of(plan)
    slides = plan.get("slides") if isinstance(plan, dict) else None
    if not isinstance(slides, list) or not slides:
        return errors + ["slides: mindestens eine Folie"]
    for n, slide in enumerate(slides, 1):
        kind = slide.get("type") if isinstance(slide, dict) else None
        prefix = f"slide {n} ({kind}): "
        if kind not in CHECKS:
            errors.append(prefix + f"unbekannter Typ '{kind}'")
            continue
        check = CHECKS[kind] or (lambda s: _check_agenda(s, chapters))
        problems = _optional_text(slide, OPTIONAL_TEXT) + _legal(slide) + list(check(slide))
        if "chapter" in slide:
            ch = slide["chapter"]
            if not isinstance(ch, int) or isinstance(ch, bool) or not 1 <= ch <= len(chapters):
                problems.append(f"chapter {ch} außerhalb 1–{len(chapters)}" if chapters
                                else "'chapter' braucht Kapitel in 'presentation.chapters'")
        errors += [prefix + p for p in dict.fromkeys(problems)]
    return errors


def load_plan(path: Path) -> dict:
    plan = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_plan(plan)
    if errors:
        raise PlanError(errors)
    return plan


def default_kicker(plan: dict, slide: dict) -> str | None:
    n = slide.get("chapter")
    if not n:
        return None
    return f"{n:02d} · {chapters_of(plan)[n - 1]}"
