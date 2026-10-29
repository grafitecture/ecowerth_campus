"""Passwortschutz (middleware.js) mit Node prüfen; @vercel/functions wird durch einen kleinen Stub ersetzt."""
import shutil
import subprocess

import pytest

from conftest import REPO

HARNESS = r"""
import mw, { config } from './middleware.mjs';
const base = 'https://campus.example';
const fails = [];
const ok = (c, m) => { if (!c) fails.push(m); };
const form = (pw, keep) => new URLSearchParams({ passwort: pw, ...(keep ? { bleiben: '1' } : {}) });
const post = (body, script) => new Request(base + '/', { method: 'POST', body,
  headers: { 'content-type': 'application/x-www-form-urlencoded', ...(script ? { 'x-campus-login': '1' } : {}) } });

let r = await mw(new Request(base + '/'));
const page = await r.text();
ok(r.status === 401, 'GET / ohne Cookie → 401');
ok(page.includes('Präsentationsvorlage') && page.includes('href="/impressum"'), 'Login-Seite');
ok(!page.includes('<style') && !page.includes(' style='), 'keine Inline-Stile (CSP)');
ok(r.headers.get('content-security-policy').includes("frame-ancestors 'none'"), 'CSP');
ok(r.headers.get('cache-control') === 'no-store', 'kein Cache für die Login-Seite');
r = await mw(post(form('falsch'), true));
ok(r.status === 401, 'falsches Passwort → 401');
r = await mw(post(form(''), false));
ok(r.status === 401 && (await r.text()).includes('stimmt nicht'), 'leeres Passwort ohne Skript → Fehlermeldung');
r = await mw(post(form('  ECOWERTH ', true), true));
ok(r.status === 204, 'richtiges Passwort, Schreibweise egal → 204');
const set = r.headers.get('set-cookie') || '';
ok(/^ew_campus=[0-9a-f]{64}; Path=\/; HttpOnly; Secure; SameSite=Lax; Max-Age=2592000$/.test(set), '30 Tage');
const cookie = set.split(';')[0];
r = await mw(post(form('ecowerth'), false));
ok(r.status === 303 && !/Max-Age/.test(r.headers.get('set-cookie')), 'ohne Skript → 303 mit Sitzungs-Cookie');
r = await mw(new Request(base + '/downloads/ecowerth-campus-vorlage.pptx', { headers: { cookie } }));
ok(r.headers.get('x-middleware-next') === '1', 'mit Cookie → weiter');
r = await mw(new Request(base + '/downloads/ecowerth-campus-vorlage.pptx'));
ok(r.status === 401, 'Download ohne Cookie → 401');
r = await mw(new Request(base + '/', { headers: { cookie: cookie.slice(0, -1) + (cookie.endsWith('0') ? '1' : '0') } }));
ok(r.status === 401, 'verfälschtes Cookie → 401');
r = await mw(new Request(base + '/abmelden', { headers: { cookie } }));
ok(r.status === 303 && /Max-Age=0/.test(r.headers.get('set-cookie')), 'Abmelden löscht das Cookie');
const re = new RegExp('^' + config.matcher[0].replace('/((?!', '/(?!').replace(').*)', ').*') + '$');
for (const p of ['/impressum', '/datenschutz', '/assets/fonts/archivo-600.woff2', '/assets/public/login.css',
                 '/favicon.svg', '/robots.txt']) ok(!re.test(p), 'frei: ' + p);
for (const p of ['/', '/index.html', '/slides/praesentation/01.jpg', '/downloads/x.pdf', '/assets/site.css',
                 '/assets/site.js']) ok(re.test(p), 'geschützt: ' + p);
console.log(JSON.stringify(fails));
"""


@pytest.fixture
def harness(tmp_path):
    if shutil.which("node") is None:
        pytest.skip("Node.js fehlt")
    shutil.copyfile(REPO / "middleware.js", tmp_path / "middleware.mjs")
    stub = tmp_path / "node_modules" / "@vercel" / "functions"
    stub.mkdir(parents=True)
    (stub / "package.json").write_text('{"name":"@vercel/functions","type":"module","exports":"./index.js"}')
    (stub / "index.js").write_text(
        "export function next() { return new Response(null, { headers: { 'x-middleware-next': '1' } }); }\n")
    (tmp_path / "run.mjs").write_text(HARNESS, encoding="utf-8")
    return tmp_path


def _node(harness, script, password):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin"}
    if password is not None:
        env["SITE_PASSWORD"] = password
    return subprocess.run(["node", script], cwd=harness, capture_output=True, text=True, env=env)


def test_middleware(harness):
    res = _node(harness, "run.mjs", "ecowerth")
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip().splitlines()[-1] == "[]"


def test_password_from_env(harness):
    script = harness / "env.mjs"
    script.write_text("""
import mw from './middleware.mjs';
const body = new URLSearchParams({ passwort: 'anderes' });
const r = await mw(new Request('https://campus.example/', { method: 'POST', body,
  headers: { 'content-type': 'application/x-www-form-urlencoded', 'x-campus-login': '1' } }));
console.log(r.status);
""", encoding="utf-8")
    assert _node(harness, "env.mjs", "Anderes").stdout.strip() == "204"
    assert _node(harness, "env.mjs", "Drittes").stdout.strip() == "401"


def test_password_is_not_in_the_code():
    assert "ecowerth'" not in (REPO / "middleware.js").read_text(encoding="utf-8")


@pytest.mark.parametrize("password", [None, "", "   "])
def test_locked_without_password(harness, password):
    """Ohne SITE_PASSWORD kommt niemand hinein – auch nicht mit leerem Passwort oder einem nachgerechneten Cookie."""
    script = harness / "locked.mjs"
    script.write_text("""
import mw from './middleware.mjs';
const hex = async (t) => Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(t))))
  .map((b) => b.toString(16).padStart(2, '0')).join('');
const out = [];
for (const pw of ['', ' ', 'ecowerth']) {
  const r = await mw(new Request('https://campus.example/', { method: 'POST', body: new URLSearchParams({ passwort: pw }),
    headers: { 'content-type': 'application/x-www-form-urlencoded', 'x-campus-login': '1' } }));
  out.push(r.status);
}
const forged = 'ew_campus=' + await hex('ecowerth-campus:v1:');
out.push((await mw(new Request('https://campus.example/', { headers: { cookie: forged } }))).status);
console.log(JSON.stringify(out));
""", encoding="utf-8")
    assert _node(harness, "locked.mjs", password).stdout.strip() == "[401,401,401,401]"
