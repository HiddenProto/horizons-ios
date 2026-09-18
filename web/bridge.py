"""The mobile seat for the chip.

On the desktop an AI drives HORIZONS one `run.bat cmd` at a time. Here a person does it with
their thumbs, so this module is the whole of the difference: it calls the same engine the CLI
does (`commands.step`, `horizons.new_game`) and additionally reads the live state back out as
a list of things that can be pressed right now. It never changes a rule of the game.

Every public function returns a JSON string so the JS side has one shape to deal with.
"""
import json
import os
import re
import sys
import types

GAME = os.path.dirname(os.path.abspath(__file__))
if GAME not in sys.path:
    sys.path.insert(0, GAME)

# horizons.py imports the Tk watch window at the top; there is no Tk here and no window to
# watch from, so it gets an empty module in its place.
sys.modules.setdefault("hz.watcher", types.ModuleType("hz.watcher"))

import horizons as H                      # noqa: E402
from hz import commands as C              # noqa: E402
from hz import render as R                # noqa: E402
from hz import regions as REG             # noqa: E402
from hz import subjects as SUB            # noqa: E402
from hz import items as I                 # noqa: E402
from hz import intel as IN                # noqa: E402
from hz import persuade as P              # noqa: E402
from hz import tutorial as TUT            # noqa: E402
from hz import link as LK                 # noqa: E402
from hz import crisis as CR               # noqa: E402
from hz import endings as E               # noqa: E402
from hz.state import State, save_exists   # noqa: E402

LIMB_NAMES = ["left arm", "right arm", "left leg", "right leg", "tail", "left ear", "right ear"]


def _out(**kw):
    return json.dumps(kw)


# ------------------------------------------------------------------ desktop words -> touch words
# The game text tells a typist what to type. On here nothing is typed, so every instruction is
# re-pointed at the button that does it. Rewrites only - the game's own wording is untouched.
LABEL = {"override": "FORCE", "cut": "CUT CHIP", "inv": "INV", "say": "ANSWER"}
VERBS = ("go look map gather rest camp shelter hide escape leave status tend graft issues timers "
         "pack plug inv use craft recipes drop reassure persuade override recalibrate reconnect "
         "disconnect mend listen think truths region wins help cut say pulse breathe drain warm "
         "calm speak check").split()
_QUOTED = re.compile(r"'(%s)((?: [^',;!?]{0,30})?)'" % "|".join(VERBS))
_REWRITES = [
    (re.compile(r"reply with 'say 1', 'say 2' and so on\."), "the answers appear below."),
    (re.compile(r"\('say 1', 'say 2', \.\.\.\)"), "(answer it below)"),
    (re.compile(r"Answer its question with 'say \d+', not '\d+'\."),
     "Answer it with the buttons under IT ASKED YOU."),
    (re.compile(r"Type 'look' to begin\. Type 'help' for everything else\."),
     "Press LOOK to begin. HELP is under MIND."),
    (re.compile(r"Type 'help'\."), "HELP is under MIND."),
    (re.compile(r"(?:with:?\s+)?\.\\run\.bat new [^\n]*final"), "from NEW RUN, as " + "THE FINAL"),
    (re.compile(r"\.\\run\.bat new [^\n]*destiny"), "NEW RUN, as DESTINY"),
    (re.compile(r"\.\\run\.bat new [^\n]*"), "NEW RUN, in the menu"),
    (re.compile(r"\.\\run\.bat lore [^\n]*"), "HISTORY, on the NEW RUN page"),
    (re.compile(r"Command: (.+)$", re.M), lambda m: "Press: " + m.group(1).upper()),
]


def _button(m):
    verb, rest = m.group(1), (m.group(2) or "").strip()
    if ".." in rest and rest not in ("...",):
        return m.group(0)          # that is it talking, not an instruction
    name = LABEL.get(verb, verb.upper())
    if verb == "cut":
        return "[CUT CHIP]"
    if not rest or rest.startswith("<") or rest in ("...", "…"):
        return "[%s]" % name
    return "[%s %s]" % (name, rest)


def _mobile(text):
    for pat, rep in _REWRITES:
        text = pat.sub(rep, text)
    return _QUOTED.sub(_button, text)


def _steps(fix):
    """'use marrow, then rest' -> ['use marrow', 'rest']: each one a button. Anything that is
    not an order ('there is no fix', 'answer what it asks') is left as words."""
    out = []
    for part in re.split(r",\s*then\s+|\s+then\s+|,\s*or\s+", fix or ""):
        part = re.sub(r"\(.*?\)", "", part).strip(" .,")
        if part and part.split(" ")[0] in VERBS and "<" not in part:
            out.append(part)
    return out


def _clean(text):
    """The CMDS footer is for someone typing. Here the buttons are the command list."""
    text = text.replace(R.QUICK + " | leave", "").replace(R.QUICK, "")
    return _mobile(text).rstrip()


MOBILE_HELP = """HOW TO DRIVE IT

You are the chip seated behind its ear. You give the orders; it decides whether to carry
them out. Every button is one order, and every order is one turn.

WHAT IS IN FRONT OF IT
  When something happens, the choices appear as cards above the buttons. Pick one.
  When it stops and asks you something, the answers appear there too. Honest ones help.
  When it goes down, the only cards are what the chip can do in the seconds it has.

MOVE     GO pushes toward the horizon. LOOK, MAP, GATHER searches the area.
         REST is a short rest; CAMP is proper sleep - build a SHELTER first.
         HIDE breaks line of sight. ESCAPE is a way off the route, on the surface only.
BODY     STATUS is the full readout. TEND binds bleeding, splints breaks, salves heat -
         it asks which limb. GRAFT fits a strut where a limb is gone.
         ISSUES are complications and how to clear each one. TIMERS are countdowns.
THINGS   INV, USE (eat, drink, apply, read), CRAFT, RECIPES, DROP.
         Things it does not understand have no name yet, only what they look like.
         Using one anyway goes wrong about a third of the time.
CHIP     REASSURE says nothing and just holds the link - mood and willingness go up.
         PERSUADE reasons with it: pick what it is about, whether to stop or keep doing
         it, and say why. The why is most of what makes it land. If it agrees, it keeps to
         it on its own for a while, listed as ASKED OF IT.
         FORCE makes the next order an override: it goes through a refusal, and it costs
         mood, will and link. Some refusals are judgement, and FORCE does not reach those.
         RECALIBRATE repairs the link. RECONNECT re-seats it if it drops. DISCONNECT lets it
         run itself for a few turns. CUT CHIP ends it. Read that twice.
MIND     THINK, TRUTHS, which REGION this is, WINS. LISTEN (under CHIP) replays what
         it said out loud.
⌨        Type any order yourself, if you know the words.

Words in [BRACKETS] in the text are buttons."""


def _load():
    return State.load() if save_exists() else None


# ------------------------------------------------------------------ what can be pressed
def choices(s):
    c = {"over": bool(s.over)}
    if s.over:
        return c
    c["down"] = bool(LK.is_down(s))
    if s.crisis:
        cr = s.crisis
        c["crisis"] = [{"cmd": cmd, "label": cmd, "sub": "%ds - %s" % (cost, what), "cost": cost}
                       for cmd, cost, what in CR.ACTION_HELP]
        kind = CR.KINDS.get(cr.get("kind"), {})
        c["crisis_info"] = {"kind": cr.get("kind"), "label": kind.get("label", ""),
                            "why": kind.get("why", ""), "left": float(cr.get("left", 0)),
                            "total": float(cr.get("total", 40) or 40), "pumps": int(cr.get("pumps", 0)),
                            "air": int(cr.get("air", 0)), "cause": cr.get("cause", "")}
        return c
    from hz import issues as ISS
    c["issues"] = [{"label": it.get("label", ""), "limb": it.get("limb"),
                    "desc": ISS.TYPES.get(it.get("kind"), {}).get("desc", ""),
                    "fix": it.get("fix", ""), "steps": _steps(it.get("fix", ""))}
                   for it in s.issues]
    c["timers"] = [{"label": t.get("label", ""), "left": int(t.get("left", 0)),
                    "hint": _mobile(t.get("hint", ""))}
                   for t in sorted(s.timers, key=lambda x: x["left"])]
    if s.scene:
        c["scene"] = [{"cmd": str(i), "label": str(o)}
                      for i, o in enumerate(s.scene.get("opts") or [], 1)]
    if s.question:
        c["question"] = [{"cmd": "say %d" % i, "label": str(o)}
                         for i, o in enumerate(s.question.get("opts") or [], 1)]
    st = TUT.current(s) if not TUT.done(s) else None
    if st:
        c["hint"] = st.get("cmd")
    c["limbs"] = [{"key": n, "state": s.limbs[n]["state"],
                   "hp": round(float(s.limbs[n].get("hp", 0))),
                   "bleed": float(s.limbs[n].get("bleed", 0)) > 0,
                   "bound": bool(s.limbs[n].get("bound")),
                   "strut": bool(s.limbs[n].get("strut"))}
                  for n in LIMB_NAMES if n in s.limbs]
    # the label, never the key: below the intelligence line an object has no name, and the
    # button must not give away what the frame is careful not to
    c["items"] = [{"key": k, "label": IN.label(s, k), "n": v}
                  for k, v in sorted(s.inv.items())]
    c["craft"] = I.craftable(s)
    topics = []
    for key, t in P.TOPICS.items():
        try:
            live = bool(t["rel"](s))
        except Exception:
            live = False
        if live:
            topics.append({"key": key, "word": t["keys"][0],
                           "stop": t.get("stop", ""), "do": t.get("do", "")})
    c["topics"] = topics
    c["final"] = bool(REG.on_final(s))
    from hz import mortal as MO
    c["holed"] = bool(MO.holed(s))
    from hz import phones as PH
    c["phones"] = bool(SUB.trait(s, "phones"))
    c["surface"] = getattr(s, "region", "outside") == "outside"
    return c


def _head(s):
    if not s:
        return {}
    sub = SUB.BY_ID.get(getattr(s, "subject", ""), {})
    reg = REG.BY_KEY.get(getattr(s, "region", ""), {})
    try:
        from hz import world as W
        zone = W.zone(s).get("key", "")
    except Exception:
        zone = ""
    # what the screen itself reacts to - atmosphere only, never information the frame hides
    return {"subject": sub.get("name", ""), "sid": getattr(s, "subject", ""),
            "region": reg.get("name", ""), "rkey": getattr(s, "region", ""), "zone": zone,
            "destiny": bool(getattr(s, "destiny", False)), "final": bool(REG.on_final(s)),
            "turn": s.turn, "clock": s.clock, "night": bool(s.night), "seed": s.seed,
            "weird": round(float(s.weird)), "crisis": bool(s.crisis), "down": bool(LK.is_down(s)),
            "clarity": bool(s.eff("clarity")), "over": bool(s.over),
            "asleep": s.activity == "sleeping", "resting": s.activity == "resting",
            "edge": float(getattr(s, "snap", 0.0) or 0.0) > 45.0,
            "feel": {"mood": round(s.mood), "pain": round(s.pain), "fatigue": round(s.fatigue),
                     "blood": round(s.blood), "strain": round(s.strain), "link": round(s.chip),
                     "snap": round(float(getattr(s, "snap", 0.0) or 0.0))}}


# ------------------------------------------------------------------ calls from the page
def boot():
    s = None
    try:
        s = _load()
    except Exception:
        s = None
    return _out(has_save=bool(s), over=bool(s and s.over), head=_head(s), menu=_menu())


def _menu():
    regs = [{"key": r["key"], "name": r["name"], "label": r.get("label", ""),
             "open": bool(REG.is_unlocked(r["key"]))} for r in REG.REGIONS]
    subs = []
    for sub in SUB.SUBJECTS:
        sid = sub["id"]
        subs.append({"id": sid, "name": sub["name"],
                     "lore": bool(REG.lore_open(sid)),
                     "destiny": bool(REG.destiny_open(sid)),
                     "final": bool(REG.final_open(sid))})
    return {"regions": regs, "subjects": subs, "default_region": REG.DEFAULT,
            "default_subject": SUB.DEFAULT,
            "destiny_name": REG.DESTINY_NAME, "final_name": REG.FINAL_NAME}


def new_run(region, subject, destiny=False, final=False, seed=None):
    reg = REG.resolve(region) or REG.BY_KEY[REG.DEFAULT]
    sub = SUB.resolve(subject) or SUB.BY_ID[SUB.DEFAULT]
    if not REG.is_unlocked(reg["key"]):
        return _out(error="%s is not open yet. Finish the region above it first." % reg["name"])
    if final and not REG.final_open(sub["id"]):
        return _out(error="%s is not open to %s." % (REG.FINAL_NAME, sub["name"]))
    if destiny and not REG.destiny_open(sub["id"]):
        return _out(error="%s is not open to %s." % (REG.DESTINY_NAME, sub["name"]))
    try:
        seed = int(seed) if seed not in (None, "") else None
    except Exception:
        seed = None
    resumed = bool(final and REG.final_slot(sub["id"]))
    s = H.new_game(seed, sub["id"], reg["key"], bool(destiny), bool(final))
    parts = [_mobile(R.intro(reg, destiny=bool(destiny), carried=bool(getattr(s, "carried_in", False)),
                             final=bool(final), resumed=resumed)),
             _mobile(SUB.implantation(sub)),
             _clean(C.step(s, "look"))]
    s.save()
    return _out(text="\n\n".join(parts), choices=choices(s), head=_head(s))


def current():
    s = _load()
    if not s:
        return _out(error="no run")
    if s.over:
        text = _mobile(R.frame(s, s.ending_text + "\n\n" + E.scorecard(s), show_cmds=False))
    else:
        text = _clean(R.frame(s, "(no action taken)"))
    return _out(text=text, choices=choices(s), head=_head(s))


def do(cmd):
    s = _load()
    if not s:
        return _out(error="no run")
    if s.over:
        return _out(text=_mobile("This run is over: %s\n\n%s\n\n%s"
                                 % (s.ending, s.ending_text, E.scorecard(s))),
                    choices=choices(s), head=_head(s))
    if cmd.strip().lower() in ("help", "?", "h"):
        return _out(text=MOBILE_HELP, choices=choices(s), head=_head(s))
    try:
        text = _clean(C.step(s, cmd))
    except Exception as e:
        s.note("[the world stuttered: %s]" % e)
        text = ("[that turn did not resolve: %s: %s]\n[state preserved - try something else]"
                % (type(e).__name__, e))
    s.save()
    return _out(text=text, choices=choices(s), head=_head(s))


def end_run():
    """Walk away from this body. What has been unlocked stays unlocked."""
    from hz.state import SAVE_PATH
    for p in (SAVE_PATH, SAVE_PATH + ".tmp"):
        try:
            os.remove(p)
        except OSError:
            pass
    return boot()


def erase_all():
    """Everything: the run, the unlocks, the wins, the Final's slot, the histories read."""
    from hz.state import SAVE_DIR
    try:
        for f in os.listdir(SAVE_DIR):
            try:
                os.remove(os.path.join(SAVE_DIR, f))
            except OSError:
                pass
    except OSError:
        pass
    return boot()


def lore(sid):
    sub = SUB.resolve(sid)
    if not sub or not REG.lore_open(sub["id"]):
        return _out(error="Nothing of its history is open.")
    return _out(title="%s - WHAT IT WAS BEFORE THE CHIP" % sub["name"].upper(),
                text=_mobile(SUB.lore(sub["id"]) or "There is nothing written down about it."))


def roster():
    return _out(text=REG.roster() + "\n\n" + SUB.roster())
