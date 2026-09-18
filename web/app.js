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
};
const disk = {};

function syncOut() {
  let names = [];
  try { names = py.FS.readdir(GAME + "/stuff"); } catch (e) { return; }
  for (const n of names) {
    if (n === "." || n === ".." || n.endsWith(".tmp")) continue;
    let t;
    try { t = py.FS.readFile(GAME + "/stuff/" + n, { encoding: "utf8" }); } catch (e) { continue; }
    if (disk[n] !== t) { disk[n] = t; Store.save(n, t); }
  }
}

function call(fn, ...args) {
  const r = JSON.parse(B[fn](...args));
  syncOut();
  return r;
}

// ---------------------------------------------------------------- boot
function bootMsg(t) { $("boot-msg").textContent = t; }

async function boot() {
  try {
    bootMsg("loading python…");
    py = await loadPyodide({ indexURL: "pyodide/" });
    bootMsg("unpacking the world…");
    const buf = await (await fetch("game.zip")).arrayBuffer();
    py.unpackArchive(buf, "zip", { extractDir: GAME });
    py.FS.mkdirTree(GAME + "/stuff");
    const saved = Store.load();
    for (const [n, t] of Object.entries(saved)) {
      if (typeof t !== "string") continue;
      py.FS.writeFile(GAME + "/stuff/" + n, t);
      disk[n] = t;
    }
    bootMsg("seating the chip…");
    py.runPython(`import sys\nsys.path.insert(0, "${GAME}")\nimport os\nos.chdir("${GAME}")\nimport bridge`);
    B = py.pyimport("bridge");
    const b = call("boot");
    MENU = b.menu;
    $("boot").classList.add("hidden");
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
  apply(r, null);
}

// ---------------------------------------------------------------- start screen
const pick = { region: null, subject: null, mode: "normal" };

function showStart(b) {
  b = b || call("boot");
  MENU = b.menu;
  $("start").classList.remove("hidden");
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

$("btn-continue").onclick = () => { $("start").classList.add("hidden"); resume(); };
$("btn-new").onclick = () => {
  const go = () => {
    const r = call("new_run", pick.region, pick.subject, pick.mode === "destiny", pick.mode === "final", null);
    if (r.error) { sheet("NOT OPEN", (b) => b.appendChild(el("p", "", esc(r.error)))); return; }
    $("start").classList.add("hidden");
    $("feed").innerHTML = "";
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

function renderFrame(text) {
  const pre = el("pre", "frame");
  const out = [];
  for (const ln of String(text).split("\n")) {
    const c = lineClass(ln);
    if (c === "rule") { out.push('<span class="rule"></span>'); continue; }
    const body = esc(ln).replace(/\[([A-Z][A-Z0-9 ]*(?: [a-z][a-z0-9 ]*)?)\]/g, '<span class="kbd">$1</span>');
    out.push(c ? `<span class="${c}">${body}</span>` : body);
  }
  pre.innerHTML = out.join("\n").replace(/<\/span>\n<span class="rule"><\/span>\n?/g, '</span><span class="rule"></span>')
    .replace(/\n?<span class="rule"><\/span>\n?/g, '<span class="rule"></span>');
  return pre;
}

function addCard(cmd, text) {
  const feed = $("feed");
  for (const old of feed.querySelectorAll(".turn")) old.classList.add("old");
  const card = el("div", "turn");
  if (cmd) {
    const forced = cmd.startsWith("override ");
    card.appendChild(el("div", "sent", forced
      ? `ORDER — ${esc(cmd.slice(9))} <span class="forced">FORCED</span>`
      : `ORDER — ${esc(cmd)}`));
  }
  card.appendChild(renderFrame(text));
  feed.appendChild(card);
  while (feed.children.length > MAX_CARDS) feed.removeChild(feed.firstChild);
  requestAnimationFrame(() => card.scrollIntoView({ block: "start", behavior: "smooth" }));
}

function apply(r, cmd) {
  if (r.error) { addCard(cmd, r.error); return; }
  C = r.choices || {};
  HEAD = r.head || HEAD;
  addCard(cmd, r.text || "");
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

function section(label, items) {
  const box = $("context");
  box.appendChild(el("div", "ctx-label", esc(label)));
  const row = el("div", "ctx-row");
  items.forEach((i) => row.appendChild(i));
  box.appendChild(row);
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
  if (C.crisis) {
    section("IT IS DOWN - EVERY SECOND COUNTS", C.crisis.map((a) => optBtn("crisis", null, a.label, a.sub, () => send(a.cmd, { raw: true }))));
    return;
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
    const b = el("button", "tab" + (tab === k ? " on" : "") + (k === "chip" && force ? " force" : ""), name);
    b.onclick = () => { if (k === "type") { typeSheet(); return; } tab = k; drawTabs(); drawPanel(); };
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

function drawPanel() {
  const P = $("panel");
  P.innerHTML = "";
  if (!C || C.over) return;
  const add = (...a) => P.appendChild(btn(...a));
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
  $("sheet").classList.remove("hidden");
}
function closeSheet() { $("sheet").classList.add("hidden"); }
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
    g.appendChild(btn("status", "full readout", () => send("status", { raw: true })));
    g.appendChild(btn("help", "every command", () => send("help", { raw: true })));
    g.appendChild(btn("clear feed", "", () => { $("feed").innerHTML = ""; closeSheet(); resume(); }));
    b.appendChild(g);
  });
};

drawTabs();
boot();
