/* HORIZONS - the chip, seated in a touchscreen.
 *
 * The desktop game is driven by an AI typing one command per turn. Here the person is the chip:
 * everything that can be ordered right now is a button, built from the live state the Python
 * bridge hands back after every turn. The game itself runs unchanged inside Pyodide.
 */
"use strict";

const GAME = "/game";
const MAX_CARDS = 30;
let py = null, B = null;
let C = null;            // latest choices
let HEAD = null;
let MENU = null;
let tab = "move";
let force = false;       // next order goes through as 'override <order>'
let recent = [];

const $ = (id) => document.getElementById(id);
const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
function el(tag, cls, html) { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }

// ---------------------------------------------------------------- saves
// In the iOS shell, native code owns the files: it injects what is on disk as window.__HZ_SAVED
// before the page runs, and takes each changed file back through a message handler. In a plain
// browser (testing) localStorage stands in for it.
const Store = {
  native: !!(window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.hzsave),
  load() {
    if (window.__HZ_SAVED && typeof window.__HZ_SAVED === "object") return window.__HZ_SAVED;
    const o = {};
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.startsWith("hz:stuff:")) o[k.slice(9)] = localStorage.getItem(k);
      }
    } catch (e) { /* private mode */ }
    return o;
  },
  save(name, content) {
    if (this.native) { window.webkit.messageHandlers.hzsave.postMessage({ name, content }); return; }
    try { localStorage.setItem("hz:stuff:" + name, content); } catch (e) { /* full or blocked */ }
  },
  remove(name) {
    if (this.native) { window.webkit.messageHandlers.hzsave.postMessage({ name, remove: true }); return; }
    try { localStorage.removeItem("hz:stuff:" + name); } catch (e) { /* blocked */ }
  },
};
const disk = {};

// Every file the game writes under stuff/ goes to the device after every turn, and a file the
// game deleted is deleted there too - so closing the app at any point loses nothing.
function syncOut() {
  let names = [];
  try { names = py.FS.readdir(GAME + "/stuff"); } catch (e) { return; }
  const seen = new Set();
  for (const n of names) {
    if (n === "." || n === ".." || n.endsWith(".tmp")) continue;
    seen.add(n);
    let t;
    try { t = py.FS.readFile(GAME + "/stuff/" + n, { encoding: "utf8" }); } catch (e) { continue; }
    if (disk[n] !== t) { disk[n] = t; Store.save(n, t); }
  }
  for (const n of Object.keys(disk)) {
    if (!seen.has(n)) { delete disk[n]; Store.remove(n); }
  }
}

// The log on screen, kept alongside the save so reopening the app shows where you were.
let FEED = [];
function saveFeed() {
  if (!HEAD) return;
  Store.save("feed.json", JSON.stringify({ seed: HEAD.seed, sid: HEAD.sid, turn: HEAD.turn, cards: FEED.slice(-MAX_CARDS) }));
}
function clearFeed() { FEED = []; $("feed").innerHTML = ""; Store.remove("feed.json"); }

function call(fn, ...args) {
  const r = JSON.parse(B[fn](...args));
  syncOut();
  return r;
}

// ---------------------------------------------------------------- boot
function bootMsg(t) { $("boot-msg").textContent = t; }
function fadeOut(node) {
  node.classList.add("fading");
  setTimeout(() => { node.classList.add("hidden"); node.classList.remove("fading"); }, 420);
}
function fadeIn(node) {
  node.classList.remove("hidden");
  node.classList.add("fading");
  requestAnimationFrame(() => requestAnimationFrame(() => node.classList.remove("fading")));
}

async function boot() {
  try {
    bootMsg("loading python…");
    py = await loadPyodide({ indexURL: "pyodide/" });
    bootMsg("unpacking the world…");
    const buf = await (await fetch("game.zip")).arrayBuffer();
    py.unpackArchive(buf, "zip", { extractDir: GAME });
    py.FS.mkdirTree(GAME + "/stuff");
    const saved = Store.load();
    loadUI();
    applyUI();
    for (const [n, t] of Object.entries(saved)) {
      if (typeof t !== "string" || n === "ui.json" || n === "feed.json") continue;   // the page's, not the game's
      py.FS.writeFile(GAME + "/stuff/" + n, t);
      disk[n] = t;
    }
    bootMsg("seating the chip…");
    py.runPython(`import sys\nsys.path.insert(0, "${GAME}")\nimport os\nos.chdir("${GAME}")\nimport bridge`);
    B = py.pyimport("bridge");
    const b = call("boot");
    MENU = b.menu;
    fadeOut($("boot"));
    if (b.has_save && !b.over) {
      resume();
    } else {
      showStart(b);
    }
  } catch (e) {
    bootMsg("the chip did not seat.\n\n" + (e && e.message ? e.message : e));
    console.error(e);
  }
}

function resume() {
  const r = call("current");
  $("feed").innerHTML = "";
  FEED = [];
  let kept = null;
  try { kept = JSON.parse(Store.load()["feed.json"] || "null"); } catch (e) { kept = null; }
  const h = r.head || {};
  if (kept && kept.seed === h.seed && kept.sid === h.sid && kept.turn === h.turn && (kept.cards || []).length) {
    // same body, same turn: put the log back exactly as it was left
    for (const c of kept.cards) { FEED.push(c); addCard(c.cmd, c.text, true); }
    C = r.choices || {}; HEAD = h;
    atmosphere(HEAD); drawHead(); drawContext(); drawTabs(); drawPanel();
    return;
  }
  apply(r, null);
}

// ---------------------------------------------------------------- start screen
const pick = { region: null, subject: null, mode: "normal" };

function showStart(b) {
  b = b || call("boot");
  MENU = b.menu;
  HEAD = null;
  atmosphere(null);
  fadeIn($("start"));
  $("btn-continue").classList.toggle("hidden", !(b.has_save && !b.over));
  pick.region = pick.region || MENU.default_region;
  pick.subject = pick.subject || MENU.default_subject;
  drawStart();
}

function drawStart() {
  const R = $("pick-region"); R.innerHTML = "";
  for (const r of MENU.regions) {
    const c = el("button", "chip" + (pick.region === r.key ? " on" : ""), esc(r.name));
    if (!r.open) { c.disabled = true; c.title = "not open yet"; }
    c.onclick = () => { pick.region = r.key; drawStart(); };
    R.appendChild(c);
  }
  const S = $("pick-subject"); S.innerHTML = "";
  MENU.subjects.forEach((s, i) => {
    const tags = [];
    if (s.lore) tags.push("history");
    if (s.destiny) tags.push(MENU.destiny_name.toLowerCase());
    if (s.final) tags.push(MENU.final_name.toLowerCase());
    const c = el("button", "subj" + (pick.subject === s.id ? " on" : ""),
      `<span class="no">${i + 1}.</span><b>${esc(s.id)}</b><small>${esc(s.name)}</small>` +
      (tags.length ? `<span class="tags">${esc(tags.join(" · "))}</span>` : ""));
    c.onclick = () => {
      pick.subject = s.id;
      if ((pick.mode === "destiny" && !s.destiny) || (pick.mode === "final" && !s.final)) pick.mode = "normal";
      drawStart();
    };
    S.appendChild(c);
  });
  const sub = MENU.subjects.find((x) => x.id === pick.subject) || {};
  const M = $("pick-mode"); M.innerHTML = "";
  const modes = [["normal", "normal"]];
  if (sub.destiny) modes.push(["destiny", MENU.destiny_name]);
  if (sub.final) modes.push(["final", MENU.final_name]);
  if (modes.length > 1) {
    for (const [k, name] of modes) {
      const c = el("button", "chip" + (pick.mode === k ? " on" : ""), esc(name));
      c.onclick = () => { pick.mode = k; drawStart(); };
      M.appendChild(c);
    }
  }
  const lore = MENU.subjects.filter((s) => s.lore);
  $("lore-row").classList.toggle("hidden", !lore.length);
  const L = $("pick-lore"); L.innerHTML = "";
  for (const s of lore) {
    const c = el("button", "chip", esc(s.id));
    c.onclick = () => {
      const r = call("lore", s.id);
      sheet(r.title || "HISTORY", (body) => { body.appendChild(el("pre", "frame", esc(r.text || r.error))); });
    };
    L.appendChild(c);
  }
}

$("btn-continue").onclick = () => { fadeOut($("start")); resume(); };
$("btn-new").onclick = () => {
  const go = () => {
    const r = call("new_run", pick.region, pick.subject, pick.mode === "destiny", pick.mode === "final", null);
    if (r.error) { sheet("NOT OPEN", (b) => b.appendChild(el("p", "", esc(r.error)))); return; }
    fadeOut($("start"));
    clearFeed();
    force = false;
    apply(r, null);
  };
  const b = call("boot");
  if (b.has_save && !b.over) {
    confirmSheet("There is a run in progress. Seating the chip somewhere new ends it.", "End it and start over", go);
  } else go();
};

// ---------------------------------------------------------------- the feed
function lineClass(ln) {
  const t = ln.trimStart();
  if (/^[=\-]{20,}\s*$/.test(ln)) return "rule";
  if (t.startsWith("!!") || t.startsWith("EDGE") || /^LINK (DOWN|LOST)|SIGNAL LOST|IT IS DOWN/.test(t)) return "l-danger";
  if (/^(ISSUES|TIMED|OPTIONS|ASKED OF IT)\b/.test(t)) return "l-head";
  if (t.startsWith("FIX")) return "l-fix";
  if (t.startsWith("CHIP ") || t.startsWith("MIND ")) return "l-chip";
  if (t.startsWith("CALIBRATION")) return "l-cal";
  if (t.startsWith("IT STOPS AND ASKS") || t.startsWith("WARNING") || /REFUSES|won't|will not/.test(t.slice(0, 40))) return "l-warn";
  if (/^\d+\)\s/.test(t)) return "l-opt";
  if (/^['"‘“]/.test(t) || t.startsWith("SAYS")) return "l-voice";
  if (/^\(.*\)$/.test(t)) return "l-dim";
  return "";
}

// Each line is its own block so a new frame can come in line by line, like a terminal printing
// it, instead of appearing all at once. The whole reveal is capped under a second.
function renderFrame(text, animate) {
  const box = el("div", "frame" + (animate ? " typing" : ""));
  const lines = String(text).split("\n");
  const step = animate ? Math.min(24, 850 / Math.max(1, lines.length)) : 0;
  const out = [];
  lines.forEach((ln, i) => {
    const c = lineClass(ln);
    const d = animate ? ` style="animation-delay:${Math.round(i * step)}ms"` : "";
    if (c === "rule") { out.push(`<span class="ln rule"${d}></span>`); return; }
    const body = esc(ln).replace(/\[([A-Z][A-Z0-9 ]*(?: [a-z][a-z0-9 ]*)?)\]/g, '<span class="kbd">$1</span>');
    out.push(`<span class="ln ${c}"${d}>${body || "&nbsp;"}</span>`);
  });
  box.innerHTML = out.join("");
  return box;
}
// a tap on the log finishes the printing at once
$("feed").addEventListener("click", () => document.querySelectorAll(".frame.typing").forEach((f) => f.classList.remove("typing")));

function addCard(cmd, text, restoring) {
  if (!restoring) FEED.push({ cmd: cmd || null, text: String(text) });
  if (FEED.length > MAX_CARDS) FEED = FEED.slice(-MAX_CARDS);
  const feed = $("feed");
  for (const old of feed.querySelectorAll(".turn")) old.classList.add("old");
  const card = el("div", "turn");
  if (cmd) {
    const forced = cmd.startsWith("override ");
    card.appendChild(el("div", "sent", forced
      ? `ORDER — ${esc(cmd.slice(9))} <span class="forced">FORCED</span>`
      : `ORDER — ${esc(cmd)}`));
  }
  if (!restoring) card.classList.add("enter");
  card.appendChild(renderFrame(text, !restoring));
  feed.appendChild(card);
  while (feed.children.length > MAX_CARDS) feed.removeChild(feed.firstChild);
  requestAnimationFrame(() => card.scrollIntoView({ block: "start", behavior: "smooth" }));
}

// ---------------------------------------------------------------- look & feel
const UI = { theme: "terminal", follow: true, size: "m" };
function loadUI() {
  try { Object.assign(UI, JSON.parse(Store.load()["ui.json"] || "{}")); } catch (e) { /* default */ }
}
function saveUI() { Store.save("ui.json", JSON.stringify(UI)); applyUI(); }
function applyUI() {
  const b = document.body;
  b.classList.toggle("t-terminal", UI.theme !== "dossier");
  b.classList.toggle("t-dossier", UI.theme === "dossier");
  b.classList.toggle("fx", UI.theme !== "dossier" && UI.follow);
  for (const s of ["s", "l", "xl"]) b.classList.toggle("size-" + s, UI.size === s);
  atmosphere(HEAD);
}

const HOT_ZONES = new Set(["thermals", "furnace"]);

// Neutral is a plain black terminal. Colour comes in only as it stops feeling neutral: towards
// the subject's own colour when it is good, towards its own kind of bad when it is not (cold
// and drained for most, red for the two that go hot). It covers the whole screen, not the log.
const NEUTRAL = { text: "#c9c9c4", accent: "#ecece6" };
const HUES = {
  "2008": { hi: "#ffb454", lo: "#7a8aa0" },
  "1278": { hi: "#d8f5cf", lo: "#7f8c86" },
  "101":  { hi: "#ff8a5c", lo: "#d0463a" },
  "0041": { hi: "#ffc2a6", lo: "#56607a" },
  "7":    { hi: "#7dff8a", lo: "#5f8a6a" },
  "3350": { hi: "#6ff0ff", lo: "#6a7f9c" },
  "682":  { hi: "#ff84e4", lo: "#ff3b3b" },
  "680":  { hi: "#e9eef3", lo: "#6d7378" },
  "681":  { hi: "#ffb454", lo: "#7a8aa0" },
  "4400": { hi: "#a9cbff", lo: "#6e7890" },
};
const PALETTE_VARS = ["--text", "--accent", "--dim", "--faint", "--line", "--bg", "--panel", "--panel2", "--glow", "--voice"];
const rgb = (hx) => [1, 3, 5].map((i) => parseInt(hx.slice(i, i + 2), 16));
const hex = (c) => "#" + c.map((v) => Math.round(clamp(v, 0, 255)).toString(16).padStart(2, "0")).join("");
const mix = (a, b, t) => { const A = rgb(a), B = rgb(b); return hex(A.map((v, i) => v + (B[i] - v) * t)); };

function moodPalette(h, mood) {
  const st = document.body.style;
  const hue = HUES[h.sid] || HUES["2008"];
  const up = clamp((mood - 58) / 32, 0, 1), down = clamp((44 - mood) / 34, 0, 1);   // 44-58 is neutral
  const target = up ? hue.hi : hue.lo, k = up || down;
  let text = mix(NEUTRAL.text, target, 0.95 * k);
  let bg = mix("#000000", target, (up ? 0.07 : 0.05) * k);
  if (down) text = mix(text, bg, 0.25 * down);                 // low is dimmer, not just colder
  let accent = mix(NEUTRAL.accent, mix(target, "#ffffff", up ? 0.3 : 0.1), k);
  // asleep: the screen goes where it goes - pale, lavender, soft, whatever the mood was
  if (h.asleep && !h.crisis) {
    text = mix(text, "#dcd4ff", 0.6); bg = mix(bg, "#0b0818", 0.85); accent = mix(accent, "#f4e9ff", 0.7);
  } else if (h.resting && !h.crisis) {
    text = mix(text, bg, 0.14);
  }
  if (h.crisis) accent = "#ff5a44";
  const env = h.destiny || h.final;                             // the place owns the background there
  const set = (k2, v) => st.setProperty(k2, v);
  set("--text", text);
  set("--accent", h.down ? mix(bg, text, 0.58) : accent);
  set("--dim", mix(bg, text, 0.58));
  set("--faint", mix(bg, text, 0.38));
  set("--voice", mix(text, "#ffffff", 0.25));
  const [r, g, b] = rgb(text);
  set("--glow", `rgba(${r},${g},${b},${(h.asleep ? 0.6 : 0.5 * up + 0.15 * down).toFixed(2)})`);
  for (const v of ["--bg", "--panel", "--panel2", "--line"]) st.removeProperty(v);
  if (!env) {
    set("--bg", bg);
    set("--panel", mix(bg, text, 0.045));
    set("--panel2", mix(bg, text, 0.07));
    set("--line", mix(bg, text, 0.22));
  }
  if (h.over) PALETTE_VARS.forEach((v) => st.removeProperty(v));
}
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));

// The terminal takes on who is on the other end of the link and how that body is right now.
// Everything here is mood, never information: all of it is already on the frame in numbers.
function atmosphere(h) {
  const b = document.body;
  [...b.classList].filter((c) => /^(sub-|s-|r-)/.test(c)).forEach((c) => b.classList.remove(c));
  const st = b.style;
  if (!h || !h.sid || UI.theme === "dossier" || !UI.follow) {
    ["--feel-filter", "--pain-a", "--static-a", "--tshadow", "--beat", ...PALETTE_VARS].forEach((v) => st.removeProperty(v));
    return;
  }
  b.classList.add("sub-" + h.sid, "r-" + (h.rkey || "outside"));
  const on = (cls, cond) => { if (cond) b.classList.add(cls); };
  on("s-destiny", h.destiny); on("s-final", h.final); on("s-night", h.night);
  on("s-down", h.down); on("s-crisis", h.crisis); on("s-clarity", h.clarity);
  on("s-over", h.over); on("s-edge", h.edge); on("s-weird-hi", h.weird > 70);
  on("s-hot", HOT_ZONES.has(h.zone) || h.rkey === "core");
  on("s-dream", h.asleep && !h.crisis); on("s-rest", h.resting && !h.crisis);
  const f = h.feel || {};
  const tired = clamp((f.fatigue ?? 0) / 100, 0, 1);
  const blood = f.blood ?? 100, link = f.link ?? 100, pain = f.pain ?? 0, weird = h.weird ?? 0;
  moodPalette(h, f.mood ?? 50);
  let bright = 1 - 0.12 * tired - (blood < 60 ? (60 - blood) / 220 : 0);
  if (h.night) bright -= 0.06;
  let filter = `brightness(${clamp(bright, 0.55, 1.05).toFixed(2)})`;
  // 4400 has no second opinion to check the link against: a bad link is it going out of focus
  if (h.sid === "4400" && link < 85) filter += ` blur(${((85 - link) / 85 * 1.4).toFixed(2)}px)`;
  if (h.night) filter += " hue-rotate(-8deg)";
  st.setProperty("--feel-filter", filter);
  st.setProperty("--pain-a", (clamp((pain - 25) / 75, 0, 1) * 0.8).toFixed(2));
  st.setProperty("--static-a", (link < 80 ? (80 - link) / 80 * 0.35 : 0).toFixed(2));
  const ab = weird > 30 ? (weird - 30) / 70 * 2.2 : 0;
  st.setProperty("--tshadow", ab > 0.1
    ? `${(-ab).toFixed(1)}px 0 rgba(255,40,80,.45), ${ab.toFixed(1)}px 0 rgba(40,220,255,.45), 0 0 5px var(--glow)`
    : "0 0 5px var(--glow)");
  st.setProperty("--beat", (1.3 - clamp((f.strain ?? 0) / 100, 0, 1) * 0.7).toFixed(2) + "s");
}

function lookSheet() {
  sheet("LOOK & FEEL", (b) => {
    const group = (label, key, opts) => {
      b.appendChild(el("div", "label", esc(label)));
      const row = el("div", "chips");
      for (const [v, name] of opts) {
        const c = el("button", "chip" + (UI[key] === v ? " on" : ""), esc(name));
        c.onclick = () => { UI[key] = v; saveUI(); [...row.children].forEach((x) => x.classList.toggle("on", x === c)); };
        row.appendChild(c);
      }
      b.appendChild(row);
    };
    group("THEME", "theme", [["terminal", "terminal"], ["dossier", "paper dossier"]]);
    group("THE SCREEN FOLLOWS IT", "follow", [[true, "yes - subject, feeling, place"], [false, "no - plain black"]]);
    b.appendChild(el("p", "", "When it follows, the terminal is plain black while the subject feels nothing in particular, and the whole screen takes on colour as that changes - its own colour when it is good, its own kind of bad when it is not - and picks up where it is. Terminal theme only."));
    group("TEXT SIZE", "size", [["s", "small"], ["m", "medium"], ["l", "large"], ["xl", "extra large"]]);
  });
}

function apply(r, cmd) {
  if (r.error) { addCard(cmd, r.error); return; }
  C = r.choices || {};
  HEAD = r.head || HEAD;
  addCard(cmd, r.text || "");
  saveFeed();
  atmosphere(HEAD);
  drawHead();
  drawContext();
  drawTabs();
  drawPanel();
}

function drawHead() {
  if (!HEAD) { $("head").innerHTML = ""; return; }
  $("head").innerHTML = `<b>${esc(HEAD.sid)}</b> · ${esc(HEAD.region)}${HEAD.destiny ? " · " + esc(MENU.destiny_name) : ""} · T${HEAD.turn} · ${esc(HEAD.clock)}`;
}

// ---------------------------------------------------------------- sending orders
function send(cmd, opts) {
  opts = opts || {};
  if (!cmd || document.body.classList.contains("busy")) return;
  let full = cmd.trim();
  if (force && !opts.raw && !full.startsWith("override ")) full = "override " + full;
  if (!opts.keepForce) force = false;
  closeSheet();
  document.body.classList.add("busy");
  // let the press paint before python takes the thread
  setTimeout(() => {
    try {
      const r = call("do", full);
      recent = [full, ...recent.filter((x) => x !== full)].slice(0, 8);
      apply(r, full);
    } catch (e) {
      addCard(full, "[the bridge failed: " + (e && e.message ? e.message : e) + "]");
    } finally {
      document.body.classList.remove("busy");
    }
  }, 30);
}

// ---------------------------------------------------------------- what is in front of it
function optBtn(cls, n, label, sub, onclick) {
  const b = el("button", "opt " + cls,
    (n != null ? `<span class="n">${esc(n)}</span>` : "") + esc(label) + (sub ? `<span class="sub">${esc(sub)}</span>` : ""));
  b.onclick = onclick;
  return b;
}

let lastCrisisPct = null;

function section(label, items) {
  const box = $("context");
  box.appendChild(el("div", "ctx-label", esc(label)));
  const row = el("div", "ctx-row");
  items.forEach((i, n) => { i.style.animationDelay = n * 45 + "ms"; row.appendChild(i); });
  box.appendChild(row);
}

// what is wrong with it and what fixes each one, one tap per step
function fixStep(step, limb) {
  const verb = step.split(" ")[0];
  if (verb === "persuade" && step === "persuade") { persuadeSheet(); return; }
  if ((verb === "tend" || verb === "graft") && step === verb) { limbSheet(verb); return; }
  send(step, { raw: true });
}

function issuesSheet() {
  sheet("WHAT IS WRONG", (b) => {
    const iss = (C && C.issues) || [], tim = (C && C.timers) || [];
    if (!iss.length && !tim.length) b.appendChild(el("p", "", "Nothing, right now."));
    for (const it of iss) {
      const card = el("div", "issue");
      card.appendChild(el("div", "i-title", esc(it.label) + (it.limb ? ` <span>[${esc(it.limb)}]</span>` : "")));
      if (it.desc) card.appendChild(el("div", "i-desc", esc(it.desc)));
      card.appendChild(el("div", "i-fix", "fix: " + esc(it.fix)));
      if ((it.steps || []).length) {
        const row = el("div", "chips");
        it.steps.forEach((st, n) => {
          const c = el("button", "chip", (it.steps.length > 1 ? n + 1 + ". " : "") + esc(st));
          c.onclick = () => fixStep(st, it.limb);
          row.appendChild(c);
        });
        card.appendChild(row);
      }
      b.appendChild(card);
    }
    if (tim.length) {
      b.appendChild(el("div", "label", "ON A COUNTDOWN"));
      for (const t of tim) {
        b.appendChild(el("div", "issue" + (t.left <= 2 ? " urgent" : ""),
          `<div class="i-title">${esc(t.label)} <span>${t.left} turn${t.left === 1 ? "" : "s"}</span></div>` +
          `<div class="i-fix">${esc(t.hint)}</div>`));
      }
    }
  });
}

function drawContext() {
  const box = $("context");
  box.innerHTML = "";
  if (!C) return;
  if (C.over) {
    section("THE RUN IS OVER", [
      optBtn("hint", null, "Seat the chip again", "pick a subject and a place", () => showStart()),
    ]);
    return;
  }
  if (force) section("FORCING THE NEXT ORDER", [optBtn("crisis", null, "stop forcing", "send orders normally", () => { force = false; drawContext(); drawTabs(); drawPanel(); })]);
  document.body.classList.toggle("in-crisis", !!C.crisis);
  if (C.crisis) {
    // the forty seconds: what is wrong, how much residual power is left, what has landed
    const ci = C.crisis_info || {};
    const pct = clamp((ci.left || 0) / (ci.total || 40) * 100, 0, 100);
    const panel = el("div", "crisis-box",
      `<div class="c-title">${esc((ci.label || "DOWN").toUpperCase())}</div>` +
      (ci.why ? `<div class="c-why">${esc(ci.why)}</div>` : "") +
      `<div class="c-bar"><i style="width:${lastCrisisPct ?? pct}%"></i></div>` +
      `<div class="c-meta"><b>${Math.max(0, Math.round(ci.left || 0))}s</b> of residual power` +
      ` · pumps landed ${ci.pumps || 0} · breaths ${ci.air || 0}${C.down ? " · <b>NO LINK</b>" : ""}</div>`);
    box.appendChild(panel);
    requestAnimationFrame(() => { const i = panel.querySelector(".c-bar i"); if (i) i.style.width = pct + "%"; });
    lastCrisisPct = pct;
    section("WHAT THE CHIP CAN DO", C.crisis.map((a) => optBtn("crisis" + (a.cost > (ci.left || 0) ? " short" : ""),
      null, a.label, a.sub, () => send(a.cmd, { raw: true }))));
    return;
  }
  lastCrisisPct = null;
  const iss = C.issues || [], tim = C.timers || [];
  if (iss.length || tim.length) {
    const strip = el("div", "strip");
    if (iss.length) {
      const b = el("button", "stat bad", `⚠ ${iss.length} issue${iss.length > 1 ? "s" : ""}`);
      b.onclick = issuesSheet; strip.appendChild(b);
    }
    for (const t of tim.slice(0, 3)) {
      const b = el("button", "stat" + (t.left <= 2 ? " bad" : ""), `⏱ ${esc(t.label)} · ${t.left}`);
      b.onclick = issuesSheet; strip.appendChild(b);
    }
    box.appendChild(strip);
  }
  if (C.down) section("THE LINK IS DOWN", [optBtn("crisis", null, "reconnect", "re-seat the link - costs time, can fail", () => send("reconnect", { raw: true }))]);
  if (C.question) section("IT ASKED YOU", C.question.map((o, i) => optBtn("q", i + 1, o.label, null, () => send(o.cmd, { raw: true }))));
  if (C.scene) section("IN FRONT OF IT", C.scene.map((o, i) => optBtn("", i + 1, o.label, null, () => send(o.cmd))));
  if (C.hint && !C.scene) section("CALIBRATION", [optBtn("hint", null, C.hint, null, () => send(C.hint))]);
}

// ---------------------------------------------------------------- tabs
const TABS = [
  ["move", "MOVE"], ["body", "BODY"], ["things", "THINGS"], ["chip", "CHIP"], ["mind", "MIND"], ["type", "⌨"],
];

function drawTabs() {
  const T = $("tabs");
  T.innerHTML = "";
  for (const [k, name] of TABS) {
    const n = k === "body" && C && C.issues ? C.issues.length : 0;
    const b = el("button", "tab" + (tab === k ? " on" : "") + (k === "chip" && force ? " force" : ""),
      name + (n ? ` <span class="badge">${n}</span>` : ""));
    b.onclick = () => { if (k === "type") { typeSheet(); return; } tab = k; drawTabs(); drawPanel(true); };
    T.appendChild(b);
  }
}

function btn(label, sub, onclick, cls) {
  const b = el("button", "btn" + (cls ? " " + cls : ""), esc(label) + (sub ? `<small>${esc(sub)}</small>` : ""));
  b.onclick = onclick;
  return b;
}

function worstLimb() {
  const order = ["lost", "mangled", "broken", "gashed", "bruised", "intact"];
  const L = (C.limbs || []).filter((l) => l.state !== "intact" && l.state !== "lost");
  L.sort((a, b) => (b.bleed - a.bleed) || (order.indexOf(a.state) - order.indexOf(b.state)));
  return L[0];
}

function drawPanel(swap) {
  const P = $("panel");
  P.innerHTML = "";
  P.classList.remove("swap");
  if (swap) { void P.offsetWidth; P.classList.add("swap"); }
  if (!C || C.over) return;
  let n = 0;
  const add = (...a) => { const b = btn(...a); b.style.animationDelay = (n++) * 22 + "ms"; P.appendChild(b); };
  if (tab === "move") {
    add("go", "toward the horizon", () => send("go"), C.hint === "go" ? "lit" : "");
    add("look", "the situation", () => send("look"), C.hint === "look" ? "lit" : "");
    add("map", "the route", () => send("map"), C.hint === "map" ? "lit" : "");
    add("gather", "search here", () => send("gather"), C.hint === "gather" ? "lit" : "");
    add("rest…", "short rest", () => hoursSheet("rest", 1, 1, 8));
    add("camp…", "sleep properly", () => hoursSheet("camp", 6, 1, 12));
    add("shelter", "build a lean-to", () => send("shelter"));
    add("hide", "break line of sight", () => send("hide"));
    if (C.surface) add("escape", "off-route way out", () => send("escape"));
    if (C.final) add("leave", "", () => send("leave"));
  } else if (tab === "body") {
    const w = worstLimb();
    add("status", "limb by limb", () => send("status"), C.hint === "status" ? "lit" : "");
    add("tend…", w ? "worst: " + w.key : "bind, splint, salve", () => limbSheet("tend"), (C.hint || "").startsWith("tend") ? "lit" : "");
    add("graft…", "fit a strut", () => limbSheet("graft"));
    add("issues", "complications", () => send("issues"));
    add("timers", "countdowns", () => send("timers"));
    if (C.holed) add("pack", "the hole in it", () => send("pack"), "warn");
  } else if (tab === "things") {
    add("inv", (C.items || []).length + " kinds", () => send("inv"), C.hint === "inv" ? "lit" : "");
    add("use…", "eat, drink, apply", () => itemSheet("use"));
    add("craft…", (C.craft || []).length + " ready", () => craftSheet(), (C.hint || "").startsWith("craft") ? "lit" : "");
    add("recipes", "what can be made", () => send("recipes"));
    add("drop…", "put something down", () => itemSheet("drop"));
  } else if (tab === "chip") {
    add("reassure", "hold the link", () => send("reassure"), C.hint === "reassure" ? "lit" : "");
    add("persuade…", "reason with it", () => persuadeSheet());
    add(force ? "forcing ON" : "force…", "override the next order", () => { force = !force; drawContext(); drawTabs(); drawPanel(); }, force ? "on" : "warn");
    add("recalibrate", "clear faults", () => send("recalibrate"));
    add("reconnect", "re-seat the link", () => send("reconnect", { raw: true }), C.down ? "lit" : "");
    add("disconnect…", "let it run itself", () => hoursSheet("disconnect", 3, 1, 8, "turns"));
    if (C.phones) add("mend", "patch the shell", () => send("mend"));
    add("listen", "what it said", () => send("listen"));
    add("cut chip", "", () => confirmSheet("Take the chip out. Read that twice before you do it.", "cut chip", () => send("cut chip", { raw: true })), "warn");
  } else if (tab === "mind") {
    add("think", "inner monologue", () => send("think"), C.hint === "think" ? "lit" : "");
    add("truths", "what it knows", () => send("truths"));
    add("region", "which act this is", () => send("region"));
    add("wins", "finished regions", () => send("wins"));
    add("help", "every command", () => send("help"));
    add("new run…", "", () => showStart());
  }
}

// ---------------------------------------------------------------- sheets
function sheet(title, build) {
  $("sheet-title").textContent = title;
  const body = $("sheet-body");
  body.innerHTML = "";
  build(body);
  const sh = $("sheet");
  clearTimeout(sheetTimer);
  sh.classList.remove("hidden");
  requestAnimationFrame(() => requestAnimationFrame(() => sh.classList.add("open")));
}
let sheetTimer = 0;
function closeSheet() {
  const sh = $("sheet");
  if (sh.classList.contains("hidden")) return;
  sh.classList.remove("open");
  sheetTimer = setTimeout(() => sh.classList.add("hidden"), 230);
}
$("sheet-close").onclick = closeSheet;
$("sheet").addEventListener("click", (e) => { if (e.target === $("sheet")) closeSheet(); });

function confirmSheet(text, label, onyes) {
  sheet("ARE YOU SURE", (b) => {
    b.appendChild(el("p", "", esc(text)));
    const row = el("div", "row");
    row.appendChild(btn("no", "", closeSheet));
    row.appendChild(btn(label, "", () => { closeSheet(); onyes(); }, "warn"));
    b.appendChild(row);
  });
}

function limbSheet(verb) {
  sheet(verb.toUpperCase() + " WHICH LIMB", (b) => {
    const g = el("div", "grid");
    for (const l of C.limbs || []) {
      const note = [l.state, l.bleed ? "BLEEDING" : "", l.bound ? "bound" : "", l.strut ? "strut" : ""].filter(Boolean).join(" · ");
      const cls = l.bleed ? "warn" : (l.state !== "intact" ? "lit" : "");
      g.appendChild(btn(l.key, note + " · " + l.hp + "hp", () => send(verb + " " + l.key), cls));
    }
    b.appendChild(g);
  });
}

function itemSheet(verb) {
  sheet(verb.toUpperCase() + " WHAT", (b) => {
    if (!(C.items || []).length) { b.appendChild(el("p", "", "It is carrying nothing.")); return; }
    const g = el("div", "grid");
    for (const it of C.items) g.appendChild(btn(it.label, "x" + it.n, () => send(verb + " " + it.key)));
    b.appendChild(g);
  });
}

function craftSheet() {
  sheet("CRAFT", (b) => {
    const list = C.craft || [];
    if (list.length) {
      b.appendChild(el("p", "", "It could make these with what it has right now:"));
      const g = el("div", "grid");
      for (const r of list) g.appendChild(btn(r, "", () => send("craft " + r), (C.hint || "") === "craft " + r ? "lit" : ""));
      b.appendChild(g);
    } else {
      b.appendChild(el("p", "", "Nothing it knows how to make is in reach with what it has."));
    }
    b.appendChild(el("p", "", "Or name the thing:"));
    const inp = el("input"); inp.type = "text"; inp.placeholder = "e.g. bandage"; inp.autocapitalize = "off";
    b.appendChild(inp);
    const row = el("div", "row");
    row.appendChild(btn("recipes", "list them", () => send("recipes")));
    row.appendChild(btn("craft it", "", () => inp.value.trim() && send("craft " + inp.value.trim().toLowerCase()), "lit"));
    b.appendChild(row);
  });
}

function hoursSheet(verb, def, min, max, unit) {
  unit = unit || "hours";
  let n = def;
  sheet(verb.toUpperCase(), (b) => {
    const st = el("div", "stepper");
    const minus = el("button", "chip", "−"), plus = el("button", "chip", "+"), val = el("b", "", String(n));
    minus.onclick = () => { n = Math.max(min, n - 1); val.textContent = n; };
    plus.onclick = () => { n = Math.min(max, n + 1); val.textContent = n; };
    st.append(minus, val, plus);
    b.appendChild(st);
    b.appendChild(el("p", "", unit));
    b.appendChild(btn(verb + " " + "for " + "that long", "", () => send(verb + " " + n, { raw: verb === "disconnect" }), "lit"));
  });
}

function persuadeSheet() {
  const topics = C.topics || [];
  let topic = null, pol = "stop";
  sheet("PERSUADE", (b) => {
    b.appendChild(el("p", "how",
      "It listens for three things: <b>what</b> it is about, whether you want it to <b>stop</b> or " +
      "<b>keep on</b>, and <b>why</b>. The why is most of what convinces it - start it with " +
      "<i>because</i>, <i>we need</i>, <i>otherwise</i>, <i>there is no</i>. If it agrees it keeps to it " +
      "on its own for a while (ASKED OF IT) until its mood drops too low to hold it. Ask about something " +
      "that is not happening and it will not know what you mean. Some of them hear you out and carry on anyway."));
    const preview = el("div", "preview");
    const reason = el("input"); reason.type = "text"; reason.placeholder = "because…"; reason.autocapitalize = "off";
    const free = el("textarea"); free.placeholder = "or say it in your own words"; free.autocapitalize = "off";
    const sentence = () => {
      if (free.value.trim()) return free.value.trim();
      if (!topic) return "";
      let why = reason.value.trim();
      if (why && !/^(because|cause|since|so |otherwise|or we|we need|there('s| is) no|no more)/i.test(why)) why = "because " + why;
      return (pol === "stop" ? "please don't " : "please ") + topic.word + (why ? " " + why : "");
    };
    const upd = () => { preview.textContent = sentence() ? "persuade " + sentence() : ""; };
    if (topics.length) {
      b.appendChild(el("div", "label", "ABOUT"));
      const tc = el("div", "chips");
      for (const t of topics) {
        const c = el("button", "chip", esc(t.key));
        c.onclick = () => { topic = t; [...tc.children].forEach((x) => x.classList.toggle("on", x === c)); drawPol(); upd(); };
        tc.appendChild(c);
      }
      b.appendChild(tc);
      b.appendChild(el("div", "label", "SO THAT IT WILL"));
      const pc = el("div", "chips");
      const drawPol = () => {
        pc.innerHTML = "";
        for (const [k, txt] of [["stop", topic ? topic.stop : "stop"], ["do", topic ? topic.do : "keep doing it"]]) {
          const c = el("button", "chip" + (pol === k ? " on" : ""), esc(txt));
          c.onclick = () => { pol = k; drawPol(); upd(); };
          pc.appendChild(c);
        }
      };
      drawPol();
      b.appendChild(pc);
      b.appendChild(reason);
    } else {
      b.appendChild(el("p", "", "Nothing it is doing right now is something it would understand being asked about."));
    }
    b.appendChild(el("div", "label", "OWN WORDS"));
    b.appendChild(free);
    b.appendChild(preview);
    reason.oninput = upd; free.oninput = upd;
    b.appendChild(btn("persuade", "free - it is not an order", () => { const s = sentence(); if (s) send("persuade " + s, { raw: true }); }, "lit"));
  });
}

function typeSheet() {
  sheet("TYPE AN ORDER", (b) => {
    b.appendChild(el("p", "", "Anything the chip understands. 'help' lists it all."));
    const inp = el("input"); inp.type = "text"; inp.placeholder = "e.g. tend leg"; inp.autocapitalize = "off"; inp.autocomplete = "off";
    inp.onkeydown = (e) => { if (e.key === "Enter" && inp.value.trim()) send(inp.value.trim()); };
    b.appendChild(inp);
    if (recent.length) {
      b.appendChild(el("div", "label", "RECENT"));
      const rc = el("div", "chips");
      for (const r of recent) { const c = el("button", "chip", esc(r)); c.onclick = () => send(r, { raw: true }); rc.appendChild(c); }
      b.appendChild(rc);
    }
    b.appendChild(btn("send", force ? "forced" : "", () => inp.value.trim() && send(inp.value.trim()), "lit"));
    setTimeout(() => inp.focus(), 50);
  });
}

$("btn-menu").onclick = () => {
  sheet("MENU", (b) => {
    const g = el("div", "grid");
    g.appendChild(btn("new run", "pick subject & place", () => { closeSheet(); showStart(); }));
    g.appendChild(btn("look & feel", "theme, text size", () => lookSheet()));
    g.appendChild(btn("status", "full readout", () => send("status", { raw: true })));
    g.appendChild(btn("help", "every command", () => send("help", { raw: true })));
    g.appendChild(btn("clear log", "keeps the run", () => { clearFeed(); closeSheet(); resume(); }));
    b.appendChild(g);
    b.appendChild(el("p", "", "The run saves after every order. Close the app whenever you like - it will be exactly where you left it."));
    const g2 = el("div", "grid");
    g2.appendChild(btn("end this run", "unlocks are kept", () => confirmSheet(
      "Leave this body where it is. The run is gone; everything you have unlocked stays.",
      "end the run", () => { const r = call("end_run"); clearFeed(); showStart(r); }), "warn"));
    g2.appendChild(btn("erase everything", "run, unlocks, wins", () => confirmSheet(
      "Wipe the run AND every region, history, Destiny and Final you have opened. This cannot be undone.",
      "erase it all", () => { const r = call("erase_all"); clearFeed(); showStart(r); }), "warn"));
    b.appendChild(g2);
  });
};

// iPad with a keyboard: 1-9 pick what is in front of it, Enter types an order, Esc closes
document.addEventListener("keydown", (e) => {
  const typing = /^(INPUT|TEXTAREA)$/.test((e.target && e.target.tagName) || "");
  if (e.key === "Escape") { closeSheet(); return; }
  if (typing || e.metaKey || e.ctrlKey || e.altKey || !C || !$("start").classList.contains("hidden")) return;
  if (!$("sheet").classList.contains("hidden")) return;
  if (/^[1-9]$/.test(e.key)) {
    const cards = [...document.querySelectorAll("#context .opt")];
    const pickable = cards.filter((c) => c.querySelector(".n"));
    const t = (pickable.length ? pickable : cards)[+e.key - 1];
    if (t) { e.preventDefault(); t.click(); }
  } else if (e.key === "Enter") { e.preventDefault(); typeSheet(); }
});

drawTabs();
boot();
