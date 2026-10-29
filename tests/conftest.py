import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "skill" / "ecowerth-campus"
sys.path.insert(0, str(SKILL / "scripts"))


@pytest.fixture(scope="session")
def m():
    """Messung mit den echten Schriften; ohne sie (fonts/ fehlt) werden die Tests übersprungen."""
    from campus.measure import Measurer

    meas = Measurer()
    if meas.approximate:
        pytest.skip("Schriftdateien fehlen in fonts/ – siehe README, Abschnitt Schriften")
    return meas


@pytest.fixture(scope="session")
def template_path(tmp_path_factory) -> pathlib.Path:
    from campus.template import build_template

    out = tmp_path_factory.mktemp("template") / "ecowerth-campus-template.pptx"
    return build_template(out, SKILL / "assets")
