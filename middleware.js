/*
 * ECOWERTH Campus: Passwortschutz für die Präsentationsseite (Vercel Routing Middleware, ohne Framework).
 *
 * Jede Anfrage ohne gültiges Zugangs-Cookie bekommt die Login-Seite mit Status 401; Folien, Bilder und
 * Downloads verlassen den Server erst nach der Anmeldung. Frei bleiben nur Schriften, die Dateien der
 * Login-Seite (assets/public), Favicon, robots.txt sowie Impressum und Datenschutz.
 *
 * Passwort: Umgebungsvariable SITE_PASSWORD im Vercel-Projekt; es steht bewusst nicht im Code. Fehlt sie,
 * bleibt die Seite gesperrt. Groß-/Kleinschreibung und Leerzeichen am Rand spielen keine Rolle.
 * Ein geteiltes Passwort ist Sichtschutz, keine Zugriffskontrolle.
 */
import { next } from '@vercel/functions';

export const config = {
  runtime: 'nodejs', // wie beim Website-Prototyp
  matcher: ['/((?!_vercel|assets/fonts/|assets/public/|favicon\\.svg|robots\\.txt|impressum|datenschutz).*)'],
};

const COOKIE = 'ew_campus';
const BLEIBEN_SEKUNDEN = 60 * 60 * 24 * 30; // „Angemeldet bleiben“: 30 Tage

const SICHERHEIT = {
  'x-robots-tag': 'noindex, nofollow',
  'x-content-type-options': 'nosniff',
  'x-frame-options': 'DENY',
  'referrer-policy': 'strict-origin-when-cross-origin',
  'content-security-policy':
    "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; font-src 'self'; " +
    "form-action 'self'; frame-ancestors 'none'; base-uri 'self'",
};

function normalisiert(passwort) {
  return String(passwort || '').normalize('NFC').trim().toLowerCase();
}

/** Cookie-Wert: aus dem Passwort abgeleitet, damit es nicht im Klartext im Browser liegt. */
async function pruefwert(passwort) {
  const bytes = new TextEncoder().encode('ecowerth-campus:v1:' + normalisiert(passwort));
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest)).map((b) => b.toString(16).padStart(2, '0')).join('');
}

/** Vergleich ohne frühen Abbruch. */
function gleich(a, b) {
  if (typeof a !== 'string' || typeof b !== 'string' || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function cookieLesen(header, name) {
  if (!header) return null;
  for (const teil of header.split(';')) {
    const idx = teil.indexOf('=');
    if (idx > 0 && teil.slice(0, idx).trim() === name) return teil.slice(idx + 1).trim();
  }
  return null;
}

function cookieSetzen(wert, bleiben) {
  return `${COOKIE}=${wert}; Path=/; HttpOnly; Secure; SameSite=Lax` + (bleiben ? `; Max-Age=${BLEIBEN_SEKUNDEN}` : '');
}

function antwort(body, status, extra = {}) {
  return new Response(body, {
    status,
    headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store', ...SICHERHEIT, ...extra },
  });
}

const LOOP = `<svg class="g-loop" viewBox="0 0 220 220" aria-hidden="true" focusable="false">
  <circle class="g-hair" cx="110" cy="110" r="86"></circle>
  <g class="g-spin">
    <circle class="g-arc g-arc--c" cx="110" cy="110" r="72"></circle>
    <circle class="g-arc g-arc--r" cx="110" cy="110" r="72"></circle>
    <circle class="g-arc g-arc--i" cx="110" cy="110" r="72"></circle>
  </g>
  <g class="g-orbit"><circle class="g-dot" cx="110" cy="38" r="10"></circle></g>
</svg>`;

function loginSeite(fehler) {
  const meldung = fehler
    ? '<p class="g-msg is-error" id="g-msg" role="status" aria-live="polite">Das Passwort stimmt nicht. Bitte prüfen Sie die Schreibweise.</p>'
    : '<p class="g-msg" id="g-msg" role="status" aria-live="polite">Diese Seite ist nicht öffentlich. Bitte geben Sie das Passwort ein.</p>';
  return `<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>ECOWERTH Campus · Anmeldung</title>
<link rel="preload" href="/assets/fonts/archivo-600.woff2?v=1" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/public/login.css?v=1">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
</head>
<body>
<div id="gate">
  <header class="g-head"><div class="g-bar">
    <img class="g-logo" src="/assets/public/logo.svg?v=1" alt="ECOWERTH" width="204" height="34">
    <span class="g-campus">Campus</span>
  </div></header>
  <main class="g-stage">
    ${LOOP}
    <div class="g-core">
      <form class="g-form" id="g-form" method="post" action="" novalidate>
        <h1 class="g-title">Präsentationsvorlage</h1>
        ${meldung}
        <div class="g-group">
          <label class="g-label" for="g-pass">Passwort</label>
          <input id="g-pass" name="passwort" type="password" autocomplete="current-password" autocapitalize="none"
                 autocorrect="off" spellcheck="false" aria-describedby="g-msg"${fehler ? ' aria-invalid="true"' : ''}>
        </div>
        <label class="g-remember" for="g-remember"><input type="checkbox" id="g-remember" name="bleiben" value="1"><span>Angemeldet bleiben</span></label>
        <button type="submit" class="g-submit" id="g-submit"><span id="g-submit-t">Präsentation öffnen</span></button>
      </form>
    </div>
  </main>
  <footer class="g-foot"><div class="g-bar">
    <span>ECOWERTH Campus · Grafitecture für die ecowerth GmbH</span>
    <nav class="g-legal" aria-label="Rechtliches"><a href="/impressum">Impressum</a><a href="/datenschutz">Datenschutz</a></nav>
  </div></footer>
</div>
<script src="/assets/public/login.js?v=1" defer></script>
</body>
</html>`;
}

export default async function middleware(request) {
  const url = new URL(request.url);
  const passwort = normalisiert(process.env.SITE_PASSWORD);
  const erwartet = passwort ? await pruefwert(passwort) : null; // ohne Passwort: niemand kommt hinein
  const angemeldet = erwartet !== null && gleich(cookieLesen(request.headers.get('cookie'), COOKIE), erwartet);

  if (url.pathname === '/abmelden') {
    return new Response(null, {
      status: 303,
      headers: { location: '/', 'set-cookie': `${COOKIE}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`,
                 'cache-control': 'no-store' },
    });
  }

  if (request.method === 'POST') {
    const perSkript = request.headers.get('x-campus-login') === '1';
    if (angemeldet) {
      return perSkript ? new Response(null, { status: 204 })
        : new Response(null, { status: 303, headers: { location: url.pathname + url.search } });
    }
    let eingabe = '';
    let bleiben = false;
    try {
      const formular = await request.formData();
      eingabe = String(formular.get('passwort') || '');
      bleiben = formular.get('bleiben') === '1';
    } catch {
      eingabe = '';
    }
    if (erwartet !== null && normalisiert(eingabe) && gleich(await pruefwert(eingabe), erwartet)) {
      const cookie = cookieSetzen(erwartet, bleiben);
      return perSkript
        ? new Response(null, { status: 204, headers: { 'set-cookie': cookie, 'cache-control': 'no-store' } })
        : new Response(null, { status: 303, headers: { location: url.pathname + url.search, 'set-cookie': cookie,
                                                       'cache-control': 'no-store' } });
    }
    return perSkript
      ? new Response('{"ok":false}', { status: 401, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } })
      : antwort(loginSeite(true), 401);
  }

  if (angemeldet) return next();
  return antwort(loginSeite(false), 401);
}
