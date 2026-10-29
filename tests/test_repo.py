import subprocess

from conftest import REPO


def _ignored(path: str) -> bool:
    return subprocess.run(["git", "check-ignore", "-q", path], cwd=REPO).returncode == 0


def test_local_fonts_are_never_tracked():
    """Die umbenannten Schriftdateien bleiben lokal (Reserved Font Name), die Web-Schriften der Seite nicht."""
    assert _ignored("fonts/Archivo-SemiBold.ttf") and _ignored("fonts/IBMPlexSans-Medium.ttf")
    assert not _ignored("site/assets/fonts/archivo-600.woff2")


def test_build_output_is_not_tracked():
    assert _ignored("out/ecowerth-praesentation.pptx") and _ignored("node_modules/@vercel/functions/index.js")
    assert _ignored(".vercel/project.json")
