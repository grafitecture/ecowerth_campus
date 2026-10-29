// ECOWERTH Campus – Login: Passwort prüfen lassen, bei Erfolg schließt sich der Kreislauf, dann lädt die Seite.
// Ohne JavaScript schickt das Formular normal ab; die Middleware leitet dann selbst weiter.
(() => {
  const gate = document.getElementById("gate");
  const form = document.getElementById("g-form");
  const pass = document.getElementById("g-pass");
  const msg = document.getElementById("g-msg");
  const submit = document.getElementById("g-submit");
  const label = document.getElementById("g-submit-t");
  const group = pass.closest(".g-group");
  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const INTRO = "Diese Seite ist nicht öffentlich. Bitte geben Sie das Passwort ein.";

  const say = (text, error) => { msg.textContent = text; msg.classList.toggle("is-error", Boolean(error)); };
  const nudge = () => {
    if (calm) return;
    group.classList.remove("is-nudge");
    void group.offsetWidth;
    group.classList.add("is-nudge");
  };
  const busy = (on) => {
    submit.disabled = on;
    pass.readOnly = on;
    label.textContent = on ? "Wird geprüft …" : "Präsentation öffnen";
  };

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!pass.value.trim()) {
      say("Bitte geben Sie das Passwort ein.", true);
      pass.setAttribute("aria-invalid", "true");
      nudge();
      pass.focus();
      return;
    }
    busy(true);
    try {
      const res = await fetch(location.href, {
        method: "POST",
        credentials: "same-origin",
        headers: { "content-type": "application/x-www-form-urlencoded", "x-campus-login": "1" },
        body: new URLSearchParams(new FormData(form)),
      });
      if (res.status === 204) {
        label.textContent = "Willkommen";
        gate.classList.add("is-open");
        setTimeout(() => location.reload(), calm ? 0 : 750);
        return;
      }
      busy(false);
      say("Das Passwort stimmt nicht. Bitte prüfen Sie die Schreibweise.", true);
      pass.setAttribute("aria-invalid", "true");
      nudge();
      pass.select();
    } catch (err) {
      busy(false);
      say("Die Anmeldung hat nicht geklappt. Bitte laden Sie die Seite neu.", true);
    }
  });

  pass.addEventListener("input", () => {
    if (pass.getAttribute("aria-invalid") === "true") {
      pass.removeAttribute("aria-invalid");
      say(INTRO, false);
    }
  });

  if (matchMedia("(pointer: fine)").matches) pass.focus({ preventScroll: true });
})();
