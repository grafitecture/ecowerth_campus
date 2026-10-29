import copy
import json

import pytest

from campus.plan import PlanError, default_kicker, load_plan, validate_plan

PLAN = {
    "presentation": {"title": "Zukunft im Kreislauf", "chapters": ["Die Gruppe", "Unsere Marken", "Leistungen"]},
    "slides": [
        {"type": "cover"},
        {"type": "points", "chapter": 2, "title": "Drei Marken",
         "points": [{"lead": "Beratung", "text": "ECOLOGICON"}, {"lead": "Systembetrieb", "text": "ECORELOOP"}]},
    ],
}


@pytest.fixture
def plan():
    return copy.deepcopy(PLAN)


def test_minimal_ok(plan):
    assert validate_plan(plan) == []


def test_unknown_type(plan):
    plan["slides"].append({"type": "video"})
    assert validate_plan(plan) == ["slide 3 (video): unbekannter Typ 'video'"]


def test_points_bounds(plan):
    plan["slides"][1]["points"] *= 3
    assert "points: 2–4 Einträge" in validate_plan(plan)[0]


def test_chapter_range(plan):
    plan["slides"][1]["chapter"] = 4
    assert "chapter 4 außerhalb 1–3" in validate_plan(plan)[0]


def test_chapter_needs_chapters(plan):
    del plan["presentation"]["chapters"]
    assert "Kapitel" in validate_plan(plan)[0]


def test_agenda_uses_chapters_or_items(plan):
    plan["slides"].append({"type": "agenda"})
    assert validate_plan(plan) == []
    del plan["presentation"]["chapters"]
    plan["slides"][1].pop("chapter")
    assert "braucht 'items'" in validate_plan(plan)[0]


@pytest.mark.parametrize("slide, expected", [
    ({"type": "brands", "title": "Marken", "columns": [{"brand": "ecologicon"}, {"brand": "ecopark"}]}, "brand muss"),
    ({"type": "brands", "title": "Marken", "columns": [{"brand": "ecologicon"}]}, "columns: 2–3"),
    ({"type": "facts", "title": "Zahlen", "facts": [{"value": "4", "label": "Firmen"}]}, "facts: 2–4"),
    ({"type": "matrix", "title": "T", "columns": ["A", "B"], "rows": [{"label": "X", "cells": [True]}]},
     "so viele Einträge wie columns"),
    ({"type": "matrix", "title": "T", "columns": ["A", "B"], "rows": [{"label": "X", "cells": [True, 3]}]},
     "true, false oder Text"),
    ({"type": "matrix", "title": "T", "columns": ["A", "B"], "rows": [{"label": "X", "cells": [True, False]}],
      "note": "Quelle", "source": "doppelt"}, "nur eins davon"),
    ({"type": "scale", "title": "S"}, "braucht 'scale', 'timeline' oder 'tags'"),
    ({"type": "compare", "title": "V", "style": "pro_contra", "left": {"label": "A", "items": ["x"]},
      "right": {"label": "B", "items": ["y"]}}, "style muss"),
    ({"type": "quote", "quote": "Haltung"}, "'name' fehlt"),
    ({"type": "quiz", "question": "?", "options": ["a", "b", "c"], "answer": 3}, "answer muss 0–2"),
    ({"type": "closing", "title": "Danke", "steps": [{"title": "a", "text": "b"}]}, "'next' fehlt"),
    ({"type": "photo", "title": "Foto", "photo": {"brief": "Foto: Halle"}, "legal": ["§ 59 KrWG"]},
     "erscheint auf Fotofolien nicht"),
    ({"type": "points", "title": "P", "points": [{"lead": "a", "text": "b"}] * 2, "legal": []}, "legal: 1–6"),
    ({"type": "steps", "title": "S", "steps": [{"title": "a", "photo": {"brief": "x"}}, {"title": "b", "text": "c"}]},
     "entweder jeder Schritt mit Foto oder keiner"),
])
def test_type_checks(plan, slide, expected):
    plan["slides"].append(slide)
    errors = validate_plan(plan)
    assert any(expected in e for e in errors), errors


def test_collects_all(plan):
    plan["slides"].append({"type": "points"})
    plan["slides"].append({"type": "statement"})
    errors = validate_plan(plan)
    assert any(e.startswith("slide 3 (points)") for e in errors)
    assert any(e.startswith("slide 4 (statement)") for e in errors)


def test_load_plan_raises(tmp_path, plan):
    plan["slides"][1]["title"] = 5
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(PlanError) as err:
        load_plan(path)
    assert "'title' muss Text sein" in str(err.value)


def test_default_kicker(plan):
    assert default_kicker(plan, plan["slides"][1]) == "02 · Unsere Marken"
    assert default_kicker(plan, plan["slides"][0]) is None


def test_examples_are_valid():
    from conftest import SKILL

    for name in ("layout-gallery.json", "ecowerth-praesentation.json"):
        assert load_plan(SKILL / "examples" / name)
