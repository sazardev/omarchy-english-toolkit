/* English Verbs — offline reference
 *
 * No build step, no framework, no network after the first load. The data
 * is a static JSON and the voice is the browser's own speech synthesis,
 * so there are no audio files to host: 415 verbs x 4 forms would be
 * hundreds of megabytes, and generated audio sounds worse than the
 * system's.
 */
"use strict";

const $ = (s) => document.querySelector(s);
const out = $("#out"), q = $("#q"), count = $("#count"), clearBtn = $("#clear");
const bar = $("#speakbar"), barText = $("#speaktext");

let DATA = null;
let view = "verbs";
let filter = "";

/* ------------------------------------------------------------------ voice */
const speech = {
  voices: [],
  pick() {
    if (!this.voices.length && "speechSynthesis" in window) {
      this.voices = speechSynthesis.getVoices() || [];
    }
    // a natural en-GB voice if the system has one
    const pref = ["Daniel", "Serena", "Kate", "Arthur", "Google UK English"];
    for (const want of pref) {
      const hit = this.voices.find((v) => v.name.startsWith(want));
      if (hit) return hit;
    }
    return this.voices.find((v) => /^en-GB/i.test(v.lang))
        || this.voices.find((v) => /^en/i.test(v.lang))
        || null;
  },
  say(text, label) {
    if (!("speechSynthesis" in window)) {
      barText.textContent = "This browser has no speech synthesis";
      bar.classList.add("on");
      setTimeout(() => bar.classList.remove("on"), 2600);
      return;
    }
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.88;
    u.pitch = 1;
    const v = this.pick();
    if (v) u.voice = v;
    u.onend = () => {
      bar.classList.remove("on");
      document.querySelectorAll("button.say.speaking")
        .forEach((b) => b.classList.remove("speaking"));
    };
    barText.textContent = label || text;
    bar.classList.add("on");
    speechSynthesis.speak(u);
  }
};

if ("speechSynthesis" in window) {
  speechSynthesis.getVoices();
  speechSynthesis.onvoiceschanged = () => (speech.voices = speechSynthesis.getVoices());
}

const ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
  + 'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
  + '<path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/>'
  + '<path d="M18.5 5.5a9 9 0 0 1 0 13"/></svg>';

const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function sayBtn(text, label) {
  return `<button class="say" data-say="${esc(text)}" data-label="${esc(label || text)}"
    aria-label="Hear ${esc(label || text)}">${ICON}</button>`;
}

/* ------------------------------------------------------------------- data */
function load() {
  return fetch("data/verbs.json")
    .then((r) => {
      if (!r.ok) throw new Error("data/verbs.json " + r.status);
      return r.json();
    })
    .then((d) => {
      DATA = d;
      render();
    })
    .catch((e) => {
      out.innerHTML = `<div class="empty">
        <p>Could not load <code>data/verbs.json</code>.</p>
        <p style="font-size:13px">${esc(e.message)}</p></div>`;
      count.textContent = "";
    });
}

/* ---------------------------------------------------------------- render */
function matchVerb(v) {
  if (!filter) return true;
  const f = filter.toLowerCase();
  return v.base.includes(f) || v.past.includes(f) || v.participle.includes(f)
    || v.ing.includes(f) || v.third.includes(f)
    || (v.meaning || "").toLowerCase().includes(f)
    || (v.alt || "").toLowerCase().includes(f)
    || (v.note || "").toLowerCase().includes(f);
}

function matchText(s) {
  if (!filter) return true;
  return String(s || "").toLowerCase().includes(filter.toLowerCase());
}

function verbCard(v) {
  return `<article class="card">
    <div class="chead">
      <span class="v">${esc(v.base)}</span>
      <span class="tag irreg">irregular</span>
    </div>
    ${v.meaning ? `<p class="meaning">${esc(v.meaning)}</p>` : ""}
    <dl class="forms">
      <dt>3rd</dt><dd>${esc(v.third)} ${sayBtn(v.third, v.third)}</dd>
      <dt>past</dt><dd>${esc(v.past)} ${sayBtn(v.past, v.past)}</dd>
      <dt>part.</dt><dd class="pp">${esc(v.participle)} ${sayBtn(v.participle, v.participle)}</dd>
      <dt>-ing</dt><dd>${esc(v.ing)} ${sayBtn(v.ing, v.ing)}</dd>
    </dl>
  </article>`;
}

function ruleCard(r) {
  const ex = r.examples.map((e) => `<dt>${esc(e.base)}</dt>
    <dd>${esc(e.past)} · <span style="color:var(--accent)">${esc(e.participle)}</span> · ${esc(e.ing)}</dd>`).join("");
  return `<section class="rulecard">
    <span class="rid">${esc(r.id)}</span>
    <h4>${esc(r.name)}</h4>
    <p class="test"><b>When:</b> ${esc(r.test)}</p>
    <p class="how">${esc(r.how)}</p>
    <dl class="mini">${ex}</dl>
    <p class="note">${esc(r.note)}</p>
  </section>`;
}

function scenarioPanel(s) {
  return `<section class="panel">
    <h3>${esc(s.title)}</h3>
    <p class="why">${esc(s.why)}</p>
    <p class="frame">${esc(s.frame).replace("{v}", "<b>verb</b>")} &nbsp;
      <span style="color:var(--ink-3)">${esc(s.form)}</span></p>
    <div>${s.verbs.map((v) => `<span class="chip" data-say="${esc(v)}" data-label="${esc(v)}">${esc(v)}</span>`).join("")}</div>
    <ul class="eg" style="margin-top:10px">${s.examples.map((e) => `<li>${esc(e)} ${sayBtn(e, e)}</li>`).join("")}</ul>
  </section>`;
}

function tableAll() {
  const rows = DATA.verbs.filter(matchVerb).map((v) => `<tr>
    <td class="b">${esc(v.base)}</td>
    <td>${esc(v.third)} ${sayBtn(v.third, v.third)}</td>
    <td>${esc(v.past)} ${sayBtn(v.past, v.past)}</td>
    <td class="pp">${esc(v.participle)} ${sayBtn(v.participle, v.participle)}</td>
    <td>${esc(v.ing)} ${sayBtn(v.ing, v.ing)}</td>
    <td style="white-space:normal;color:var(--ink-2)">${esc(v.meaning || "")}</td>
  </tr>`).join("");
  return `<div class="tw"><table>
    <thead><tr><th>base</th><th>3rd person</th><th>past</th>
      <th>past participle</th><th>-ing</th><th>meaning</th></tr></thead>
    <tbody>${rows}</tbody></table></div>`;
}

function tableDecisions() {
  const rows = DATA.decisions.filter((d) => matchVerb({ base: d.base })
    || matchText(d.why) || matchText(d.rule)).map((d) => `<tr>
    <td class="b">${esc(d.base)}</td>
    <td><span class="rid" style="font-family:ui-monospace,monospace;font-weight:700;color:var(--accent)">${esc(d.rule)}</span></td>
    <td style="white-space:normal;color:var(--ink-2)">${esc(d.why)}</td>
  </tr>`).join("");
  return `<div class="tw" style="margin-top:12px"><table>
    <thead><tr><th>verb</th><th>rule</th><th>why</th></tr></thead>
    <tbody>${rows}</tbody></table></div>`;
}

function render() {
  if (!DATA) return;
  let html = "";
  let label = "";

  if (view === "verbs") {
    const vs = DATA.verbs.filter(matchVerb);
    label = `${vs.length} verb${vs.length === 1 ? "" : "s"}`;
    html = vs.length
      ? `<div class="grid">${vs.map(verbCard).join("")}</div>`
      : empty();
  } else if (view === "rules") {
    const rs = DATA.rules.filter((r) => matchText(r.name) || matchText(r.test)
      || matchText(r.how) || matchText(r.note) || r.examples.some(matchText));
    label = `${rs.length} rule${rs.length === 1 ? "" : "s"}`;
    html = rs.length
      ? `<div class="rulegrid">${rs.map(ruleCard).join("")}</div>${tableDecisions()}`
      : empty();
  } else if (view === "scenarios") {
    const ss = DATA.scenarios.filter((s) => matchText(s.title) || matchText(s.why)
      || matchText(s.form) || matchText(s.frame)
      || s.verbs.some(matchText) || s.examples.some(matchText));
    label = `${ss.length} situation${ss.length === 1 ? "" : "s"}`;
    html = ss.length ? ss.map(scenarioPanel).join("") : empty();
  } else if (view === "traps") {
    const ts = DATA.traps.filter((t) => matchText(t.wrong) || matchText(t.right)
      || matchText(t.rule));
    label = `${ts.length} common mistake${ts.length === 1 ? "" : "s"}`;
    html = ts.length ? `<section class="panel">${ts.map((t) => `<div class="trap">
        <span class="w">${esc(t.wrong)} ${sayBtn(t.wrong, t.wrong)}</span>
        <span class="arrow">→</span>
        <span class="r">${esc(t.right)} ${sayBtn(t.right, t.right)}</span>
        <span class="rule">${esc(t.rule)}</span>
      </div>`).join("")}</section>` : empty();
  } else {
    const n = DATA.verbs.filter(matchVerb).length;
    label = `${n} verb${n === 1 ? "" : "s"} in the full table`;
    html = n ? tableAll() : empty();
  }

  out.innerHTML = html;
  count.textContent = filter ? `${label} · matching “${q.value.trim()}”` : label;
}

function empty() {
  return `<div class="empty">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"
         stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
    <p>Nothing found for “${esc(q.value.trim())}”.</p>
    <p style="font-size:13px">Try a verb, a past form, a meaning or a situation.</p>
  </div>`;
}

/* ------------------------------------------------------------------ wiring */
document.querySelectorAll("nav.tabs button").forEach((b) => {
  b.addEventListener("click", () => {
    document.querySelectorAll("nav.tabs button")
      .forEach((x) => x.setAttribute("aria-selected", String(x === b)));
    view = b.dataset.view;
    render();
  });
});

q.addEventListener("input", () => {
  filter = q.value.trim().toLowerCase();
  clearBtn.classList.toggle("on", q.value.length > 0);
  render();
});

clearBtn.addEventListener("click", () => {
  q.value = "";
  filter = "";
  clearBtn.classList.remove("on");
  render();
  q.focus();
});

document.addEventListener("click", (e) => {
  const b = e.target.closest("[data-say]");
  if (!b) return;
  document.querySelectorAll("button.say.speaking")
    .forEach((x) => x.classList.remove("speaking"));
  if (b.classList.contains("speaking")) { speechSynthesis.cancel(); return; }
  b.classList.add("speaking");
  speech.say(b.dataset.say, b.dataset.label);
});

document.addEventListener("keydown", (e) => {
  if (e.key === "/" && document.activeElement !== q) {
    e.preventDefault();
    q.focus();
  }
  if (e.key === "Escape" && document.activeElement === q) {
    q.value = "";
    filter = "";
    clearBtn.classList.remove("on");
    render();
  }
});

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => navigator.serviceWorker.register("sw.js")
    .catch(() => {}));
}

load();
