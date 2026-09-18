"""Reasoning with it, as opposed to ordering it.

The chip has two levers on the body: 'reassure' (say nothing, just hold the link open) and
'override' (force the order down and pay for it). This is the third one, and it is the only
one that is an argument. You say a sentence in plain words - what you want it to stop or keep
doing, and why - and it either takes your point, or does not understand what you are talking
about, or understands perfectly well and carries on.

What comes out of a successful one is a STANDING REQUEST: a thing it is now trying to honour
on its own, without being told again, until it stops being able to. That is the value here.
An order lasts one turn. A request it has agreed with lasts until the mood that agreed with
it is gone.

Always available, costs no time, and safe to attempt at any moment - including while it is
on the ground and the chip is running on residual power, where it is one of the few things
that reaches it at all.
"""
import re

from . import body as B
from . import subjects as SUB

# how long a request survives before it stops being live, in turns
LIFESPAN = 45
# below this mood it stops keeping its agreements - not out of spite, it just cannot hold them
LAPSE_MOOD = 22.0

NEGATIONS = (
    "do not", "dont", "don't", "do n't", "never", "stop", "quit", "cease", "less",
    "no more", "not", "avoid", "leave off", "enough", "shouldn't", "shouldnt",
    "cannot", "can't", "cant", "won't", "wont", "must not", "mustn't", "mustnt",
    "no need", "rather not",
)
# a negation aimed at a negative means carry on: "don't stop", "never give up"
DOUBLE_NEG = re.compile(
    r"(?<!\w)(do not|dont|don't|never|no)\s+(stop|stopping|quit|give up|giving up|rest|sit)(?!\w)")
REASON_MARKS = ("because", "cause", "cos", "since", "as we", "so we", "so that",
                "there is no", "there's no", "we have no", "we need", "no more",
                "or we", "otherwise", "for once")


def _has(text, words):
    """Whole words only. 'nothing is chasing us' is not a negation, and reading it as one
    turns 'keep going, nothing is out there' into an agreement to stop walking."""
    for w in words:
        if re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", text):
            return True
    return False


# ---------------------------------------------------------------- what it can be asked
# rel(s) answers: is this even a live subject right now? Asking it not to climb while it is
# lying in a dry wash with nothing to climb is how you confuse it.
TOPICS = {
    "eat": {
        "keys": ("eat", "eating", "food", "meat", "ration", "chew", "swallow", "hungry", "hunger"),
        "stop": "ration what it eats",
        "do": "eat when it can",
        "rel": lambda s: (s.inv.get("meat", 0) + s.inv.get("ration", 0) + s.inv.get("root", 0)) > 0
                         or s.hunger > 35,
    },
    "drink": {
        "keys": ("drink", "drinking", "water", "waterskin", "thirst", "thirsty", "sip"),
        "stop": "ration the water",
        "do": "drink when it can",
        "rel": lambda s: s.inv.get("water", 0) > 0 or s.thirst > 35,
    },
    "rest": {
        "keys": ("rest", "sleep", "sit", "stop walking", "slow down", "take a break", "lie down"),
        "stop": "stay on its feet",
        "do": "rest when it needs to",
        "rel": lambda s: s.fatigue > 30 or s.strain > 30,
    },
    "wander": {
        "keys": ("wander", "walk off", "walk away", "go off", "leave", "stray", "own way",
                 "without me", "on your own", "ahead"),
        "stop": "stay where you put it",
        "do": "use its own judgement about moving",
        "rel": lambda s: SUB.trait(s, "autonomy") > 0 or s.will < 55,
    },
    "bolt": {
        "keys": ("bolt", "run", "running", "rush", "sprint", "flee", "panic run", "hurry"),
        "stop": "not bolt",
        "do": "run when it has to",
        "rel": lambda s: bool(s.timers) or s.strain > 45 or (s.scene or {}).get("danger", 0) > 0,
    },
    "fight": {
        "keys": ("fight", "fighting", "attack", "bite", "claw", "kill", "charge", "swipe"),
        "stop": "not fight anything",
        "do": "defend itself",
        "rel": lambda s: (s.scene or {}).get("danger", 0) > 0.05 or s.inv.get("spear", 0) > 0,
    },
    "climb": {
        "keys": ("climb", "high", "height", "up there", "ledge", "cliff", "edge", "jump",
                 "this high", "so high"),
        "stop": "keep its feet on the ground",
        "do": "climb when it is the way through",
        "rel": lambda s: (s.scene or {}).get("danger", 0) > 0.05 or s.distance > 20,
    },
    "quiet": {
        "keys": ("quiet", "shh", "hush", "silent", "shut up", "loud", "noise", "shout",
                 "talking", "talk so much", "be quiet"),
        "stop": "keep quiet",
        "do": "say what it is thinking",
        "rel": lambda s: True,
    },
    "calm": {
        "keys": ("calm", "panic", "scared", "afraid", "frightened", "settle", "breathe",
                 "worry", "worrying", "spiral"),
        "stop": "not spiral",
        "do": "hold itself together",
        "rel": lambda s: True,
    },
    "go": {
        "keys": ("go", "going", "keep going", "walk", "forward", "push on", "the line",
                 "the horizon", "onward", "further", "give up", "giving up", "carry on"),
        "stop": "stop walking the line",
        "do": "keep going",
        "rel": lambda s: True,
    },
}

# which ordered verbs each topic bears on, for the refusal hook
VERB_TOPIC = {
    "go": "go", "forward": "go", "walk": "go", "push": "go",
    "camp": "rest", "sleep": "rest", "rest": "rest",
    "fight": "fight", "attack": "fight",
    "climb": "climb",
    "gather": "wander", "escape": "go", "hide": "bolt",
    "use": "eat", "eat": "eat", "drink": "drink",
}


def parse(text):
    """Pull a topic, a direction and a reason out of a plain sentence."""
    t = (text or "").strip().lower()
    t = t.lstrip("_").strip()
    for lead in ("please ", "hey ", "listen ", "look "):
        while t.startswith(lead):
            t = t[len(lead):]
    reason = ""
    for m in REASON_MARKS:
        i = t.find(m)
        if i >= 0:
            reason = t[i:].strip(" .,")
            break
    # a negation is the only thing that makes this a "stop doing that". Defaulting the other way
    # would read a politely phrased order - "please go" - as an agreement to stop walking.
    if DOUBLE_NEG.search(t):
        pol = "do"
    else:
        pol = "stop" if _has(t, NEGATIONS) else "do"
    # topic: longest keyword match wins, so "walk off" beats "walk"
    best, best_len = None, 0
    for tid, spec in TOPICS.items():
        for k in spec["keys"]:
            if k in t and len(k) > best_len:
                best, best_len = tid, len(k)
    return {"topic": best, "pol": pol, "reason": reason, "raw": t}


def in_scene(s, keys):
    """Is the thing you are talking about literally on the menu in front of it? If a scene
    offers 'Climb it', then climbing is live, whatever the danger rating of the scene says."""
    sc = s.scene
    if not sc:
        return False
    blob = (sc.get("text", "") + " " + " ".join(str(o) for o in sc.get("opts", []))).lower()
    return any(k in blob for k in keys)


def honours(s, topic, pol="stop"):
    """Is there a live agreement about this, in this direction?"""
    r = (s.requests or {}).get(topic)
    if not r:
        return False
    return r.get("pol") == pol


def get(s, topic):
    return (s.requests or {}).get(topic)


# ---------------------------------------------------------------- the attempt
def _score(s, topic, reason, rel):
    # deliberately kept off the ceiling: a stated reason and good timing have to be worth
    # something measurable, which they cannot be if a bare sentence already lands 95% of the time
    sc = 0.05 + 0.0030 * s.mood + 0.0020 * s.will
    if reason:
        sc += 0.22
    sc += 0.10 if rel else -0.38
    if s.weird > 70:
        sc -= 0.10
    if s.pain > 70:
        sc -= 0.08
    if s.question:
        sc -= 0.12          # it is still waiting on the last thing it asked you
    from . import voice as V
    sc *= V.trust_factor(s)
    sc *= SUB.trait(s, "persuadable")
    # some of them weigh the argument rather than the fact that you made one. Asking without
    # saying why is not an argument, and it is treated as one being absent.
    nr = SUB.trait(s, "needs_reason")
    if nr > 0 and not reason:
        sc *= max(0.05, 1.0 - 0.80 * nr)
    return max(0.03, min(0.90, sc))


def attempt(s, text):
    """Returns (feedback, voice_context). Mutates standing requests."""
    from . import voice as V
    p = parse(text)
    s.stats["persuaded"] = s.stats.get("persuaded", 0) + 1
    topic, pol, reason = p["topic"], p["pol"], p["reason"]

    if not p["raw"]:
        return ("You open the link to reason with it and put nothing down it. It waits, and "
                "then stops waiting.", None)

    # nothing it can hook the words onto
    if topic is None:
        s.weird = B.clamp(s.weird + 1.5)
        return ("IT DOES NOT FOLLOW. You said something at it and none of it landed on anything "
                "it can do or not do. It turns that over and gets nothing out of it, and is a "
                "little more unsettled than it was.", "confused")

    spec = TOPICS[topic]
    want = spec[pol]
    rel = bool(spec["rel"](s)) or in_scene(s, spec["keys"])
    sc = _score(s, topic, reason, rel)
    took = s.rng.random() < sc

    if took:
        s.requests[topic] = {"pol": pol, "reason": reason, "turn": s.turn,
                             "label": want, "heeded": 0}
        s.mood = B.clamp(s.mood + (3.0 if reason else 1.5))
        s.will = B.clamp(s.will + (3.5 if reason else 1.5))
        from . import link as LK
        LK.calmed(s, 8.0)          # being reasoned with is the thing that talks it down
        fb = "IT TAKES YOUR POINT. It is going to try to %s from here on." % want
        if reason:
            fb += " You gave it a reason and the reason is what did it."
        else:
            fb += " You did not say why, and it agreed anyway, which is worth noticing."
        return (fb, "persuaded")

    # it understood and did not agree - or could not find the thing you meant
    if not rel:
        s.weird = B.clamp(s.weird + 1.0)
        return ("IT IS CONFUSED AT YOU. It looks around for the thing you are talking about, "
                "does not find it, and looks at nothing in particular for a moment. Whatever "
                "you were heading off is not in front of it.", "confused")

    # telling it to stop doing the thing it is in the middle of doing is criticism, whatever
    # you meant by it, and there is one of them that takes criticism very badly indeed.
    from . import link as LK
    if pol == "stop" and rel:
        went = LK.snap(s, 11.0 if not reason else 5.0,
                       "being told to stop in the middle of doing it")
        if went:
            return (went, "snapped")

    indifferent = SUB.trait(s, "persuadable") < 0.6 and s.rng.random() < 0.45
    if indifferent:
        return ("IT DOES NOT CARE. Your words arrive, are understood, and are set down "
                "somewhere it does not keep things. There is no argument in it to win.",
                "indifferent")

    s.will = B.clamp(s.will - 1.0)
    return ("IT HEARS YOU AND CARRIES ON. It knows exactly what you asked. It has decided "
            "your opinion is one of the things in the situation, and not the deciding one.",
            "disregarded")


# ---------------------------------------------------------------- upkeep
def tick(s):
    """Expire old agreements, and drop the lot if it has fallen too far to keep them."""
    if not s.requests:
        return []
    out = []
    if s.mood < LAPSE_MOOD:
        labels = [r["label"] for r in s.requests.values()]
        s.requests = {}
        out.append("IT HAS STOPPED HONOURING WHAT YOU ASKED (%s). It is not far enough above "
                   "the floor to keep an agreement with anybody." % ", ".join(labels))
        return out
    for tid in list(s.requests):
        r = s.requests[tid]
        if s.turn - r.get("turn", 0) > LIFESPAN:
            del s.requests[tid]
            out.append("IT HAS FORGOTTEN THAT IT AGREED TO %s. That was a long time ago and "
                       "nothing has reminded it since." % r["label"].upper())
    return out


def heed(s, topic):
    """Mark that an agreement actually changed a behaviour this turn."""
    r = (s.requests or {}).get(topic)
    if r:
        r["heeded"] = r.get("heeded", 0) + 1


def lines(s):
    """The frame block."""
    if not s.requests:
        return []
    out = ["ASKED OF IT"]
    for tid, r in s.requests.items():
        age = s.turn - r.get("turn", 0)
        held = r.get("heeded", 0)
        out.append("  - trying to %s%s   (%d turns ago%s)"
                   % (r["label"],
                      ("  <- " + r["reason"]) if r.get("reason") else "",
                      age, ", held %d times" % held if held else ""))
    return out
