"""Acute failures, and the forty seconds you get when it goes down.

Issues are slow and chronic. These are not. A crisis suspends the run: the subject is on the
ground, the normal verbs mean nothing, and the chip is running on whatever charge is left in a
body that has stopped supplying it. That charge is measured in SECONDS, it is forty at the
absolute best, and every intervention spends some of it.

What the chip can actually do without hands: drive current down the spinal cord to make the
heart contract, drive the diaphragm, roll the body, and burn power for warmth. It gets
telemetry back - whether a pump was captured, whether air moved, whether the rhythm picked
itself back up - and nothing else. It cannot see.
"""
from . import body as B
from . import issues as ISS
from . import subjects as SUB

# kind -> label, what it needs, what it kills you with
KINDS = {
    "faint": {
        "label": "unconscious",
        "why": "it has passed out - pressure, pain, or simply too little blood left",
        "need": "it comes round on its own if the body is stable. 'check' to watch it.",
        "death": ("DID NOT WAKE", "It never came back up. Whatever was keeping it standing "
                  "finished being able to."),
        "power": 1.00,
    },
    "brady": {
        "label": "heart too slow",
        "why": "the heart has dropped to a crawl and is not moving enough to keep it alive",
        "need": "'pulse' to pace it up, 'warm' if the cold caused it",
        "death": ("HEART FAILED", "The intervals got longer and longer and then simply did "
                  "not end."),
        "power": 0.85,
    },
    "tachy": {
        "label": "heart running away",
        "why": "the heart is going far too fast to fill between beats",
        "need": "'calm' to damp the rhythm down; do not pace it",
        "death": ("HEART FAILED", "It ran itself to a standstill - too fast to fill, too fast "
                  "to stop."),
        "power": 0.90,
    },
    "arrest": {
        "label": "HEART STOPPED",
        "why": "no rhythm at all, and nothing moving from the chest outward",
        "need": "'pulse' repeatedly - the chip reports whether each pump is captured",
        "death": ("HEART STOPPED", "You never got a rhythm back. The last thing the chip reads "
                  "is its own voltage falling."),
        "power": 0.70,
    },
    "apnea": {
        "label": "LUNGS STOPPED",
        "why": "the diaphragm has quit; no air is moving either way",
        "need": "'breathe' to drive the diaphragm until it takes over",
        "death": ("SUFFOCATED", "The chest stayed still. Everything downstream of that stopped "
                  "in order."),
        "power": 0.70,
    },
    "edema": {
        "label": "LUNGS FILLING",
        "why": "there is fluid in the lungs and the volume is going the wrong way",
        "need": "'drain' - roll it and let gravity work, then 'breathe'",
        "death": ("DROWNED", "It drowned lying down, in air, a long way from any water."),
        "power": 0.75,
    },
    "freeze": {
        "label": "CORE TOO COLD",
        "why": "the core has dropped far enough that nothing chemical is working properly",
        "need": "'warm' - burn chip power into it, and keep the heart paced",
        "death": ("FROZEN", "The core went down past the point where any of it would restart."),
        "power": 0.65,
    },
    "catatonia": {
        "label": "NOT RESPONDING",
        "why": "the body is fine. It has simply stopped answering the link",
        "need": "'speak' to it, over and over. Nothing mechanical will help this one.",
        "death": ("GAVE UP", "It never answered. It was still breathing when the chip lost "
                  "the power to keep asking."),
        "power": 1.30,
    },
}

MAX_SECONDS = 40


def active(s):
    return bool(s.crisis)


def budget(s, kind):
    """Residual power, in seconds. Forty at best, and it is rarely the best."""
    k = KINDS[kind]
    f = k["power"] * SUB.trait(s, "power")
    f *= 0.45 + 0.55 * (s.blood / 100.0)
    f *= 0.70 + 0.30 * (s.warmth / 100.0)
    f *= 0.75 + 0.25 * (s.chip / 100.0)
    from . import link as LK
    if LK.is_down(s):
        # the forty seconds are the charge left in a body the chip is sitting in. If the chip
        # is not sitting in it, the clock still runs and almost nothing reaches the body.
        f *= 0.45
    return max(8, int(round(MAX_SECONDS * f)))


def begin(s, kind, cause=""):
    if s.crisis:
        return None
    sec = budget(s, kind)
    s.crisis = {"kind": kind, "left": sec, "total": sec, "pumps": 0, "air": 0,
                "drained": False, "warmed": 0, "spoken": 0, "cause": cause}
    s.scene = None
    s.question = None
    s.activity = "DOWN - " + KINDS[kind]["label"]
    s.stats["crises"] = s.stats.get("crises", 0) + 1
    s.note("CRISIS: %s. %s" % (KINDS[kind]["label"], KINDS[kind]["why"]))
    return s.crisis


def lines(s):
    """The blackout readout. This replaces the normal frame body."""
    c = s.crisis
    k = KINDS[c["kind"]]
    bar = int(round(24.0 * c["left"] / max(1, c["total"])))
    L = []
    L.append("=" * 74)
    L.append("*** THE SUBJECT IS DOWN ***   %s" % k["label"])
    L.append("")
    L.append("CHIP POWER  [%s%s]  %d seconds of charge left"
             % ("#" * bar, "." * (24 - bar), c["left"]))
    L.append("            The body has stopped supplying the link. When this runs out, so do you.")
    L.append("")
    L.append("READING     %s" % k["why"])
    if c["cause"]:
        L.append("            brought on by: %s" % c["cause"])
    L.append("TELEMETRY   pumps captured %d | breaths driven %d%s%s"
             % (c["pumps"], c["air"],
                " | drained" if c["drained"] else "",
                (" | warmed x%d" % c["warmed"]) if c["warmed"] else ""))
    L.append("")
    L.append("WHAT THE CHIP CAN DO WITHOUT HANDS")
    for cmd, cost, what in ACTION_HELP:
        L.append("  %-8s %2ds   %s" % (cmd, cost, what))
    L.append("")
    L.append("NEEDED      %s" % k["need"])
    return L


ACTION_HELP = [
    ("pulse", 3, "current down the spinal cord to force the heart to contract"),
    ("breathe", 4, "drive the diaphragm directly"),
    ("drain", 6, "roll the body and let fluid fall out of the airway"),
    ("warm", 5, "burn chip power into the core as heat"),
    ("calm", 4, "damp an overfast rhythm instead of pacing it"),
    ("speak", 3, "nothing but the link, held open, saying its number"),
    ("check", 1, "read the body again and spend almost nothing"),
    ("reconnect", 6, "re-seat a link that has come off - only if it has"),
]
COSTS = {c: n for c, n, _ in ACTION_HELP}


# ---------------------------------------------------------------- interventions
def _pulse(s, c):
    kind = c["kind"]
    if kind == "tachy":
        c["left"] -= 2
        s.pain = B.clamp(s.pain + 3)
        return ("PACED INTO A RUNNING HEART. Nothing captures - there is no gap to put a beat "
                "in. You have made it worse and spent power doing it.")
    hit = 0.62
    if kind == "arrest":
        hit = 0.55 + 0.06 * c["pumps"]
    if kind == "freeze":
        hit = 0.30 + 0.10 * c["warmed"]
    if s.blood < 35:
        hit -= 0.15
    if s.rng.random() < hit:
        c["pumps"] += 1
        return "PUMP CAPTURED. The chest moves. Telemetry says that one took. (%d captured)" % c["pumps"]
    return "NO CAPTURE. Current went down and nothing moved. Nothing came back up the line."


def _breathe(s, c):
    if c["kind"] == "edema" and not c["drained"]:
        c["left"] -= 2
        return ("YOU DRIVE AIR INTO FLUID. It bubbles and goes nowhere. Clear the airway first "
                "- 'drain'.")
    c["air"] += 1
    return "AIR MOVED. The chest rises when you tell it to and falls when you stop. (%d driven)" % c["air"]


def _drain(s, c):
    if c["drained"]:
        return "Already rolled. What was going to come out has come out."
    c["drained"] = True
    return ("YOU ROLL IT ONTO ITS SIDE and hold it there. A great deal of fluid leaves the "
            "airway. The reading clears enough to work with.")


def _warm(s, c):
    c["warmed"] += 1
    s.warmth = B.clamp(s.warmth + 9)
    s.chip = B.clamp(s.chip - 1.5)
    return ("YOU DUMP POWER INTO THE CORE AS HEAT. Warmth up. It costs the link, and the link "
            "is what is keeping you here.")


def _calm(s, c):
    if c["kind"] != "tachy":
        return "Nothing to damp. The rhythm is not the thing that is too fast here."
    c["pumps"] += 1
    s.strain = B.clamp(s.strain - 8)
    return ("YOU DAMP THE RHYTHM, holding the intervals open a fraction longer each time. "
            "It slows. (%d held)" % c["pumps"])


def _speak(s, c):
    c["spoken"] += 1
    s.mood = B.clamp(s.mood + 4)
    if c["kind"] != "catatonia":
        return ("You hold the link open and say its number. It cannot hear you. It is not a "
                "waste, exactly, but it is not help.")
    return ("You say its number, and then again, and then again. Somewhere down there something "
            "is listening and deciding whether to bother. (%d)" % c["spoken"])


def _check(s, c):
    k = KINDS[c["kind"]]
    bits = ["blood %.0f" % s.blood, "core %.0f" % s.warmth, "pain %.0f" % s.pain]
    return "READ: %s. %s. %s" % (k["label"], ", ".join(bits), k["need"])


def _relink(s, c):
    """Down, and you are not even in it. This is the only thing worth doing."""
    from . import link as LK
    if not LK.is_down(s):
        return ("The link is seated. There is nothing to re-seat, and you have just spent "
                "six seconds proving it.")
    p = 0.30 + 0.35 * (s.chip / 100.0) - 0.003 * max(0.0, s.weird - 40.0)
    p = max(0.10, min(0.85, p))
    if s.rng.random() < p:
        LK.get(s)["down"] = False
        LK.get(s)["left"] = 0
        LK.get(s)["cause"] = ""
        return ("*** THE LINK TAKES ***  It is unconscious and it cannot hold you out any "
                "more. You are in it. Everything the chip can do works again - with whatever "
                "is left of the charge.")
    return ("NOTHING. The channel does not close. It is down and you are outside it and the "
            "seconds are going.")


ACTIONS = {"pulse": _pulse, "breathe": _breathe, "drain": _drain, "warm": _warm,
           "calm": _calm, "speak": _speak, "check": _check, "reconnect": _relink}


# ---------------------------------------------------------------- resolution
def _resolved(s, c):
    """Has the thing that was killing it stopped killing it?"""
    kind = c["kind"]
    if kind == "arrest":
        return c["pumps"] >= 3 and s.rng.random() < 0.35 + 0.15 * (c["pumps"] - 3)
    if kind == "brady":
        return c["pumps"] >= 2 and s.rng.random() < 0.40
    if kind == "tachy":
        return c["pumps"] >= 2 and s.rng.random() < 0.45
    if kind == "apnea":
        return c["air"] >= 3 and s.rng.random() < 0.45
    if kind == "edema":
        return c["drained"] and c["air"] >= 2 and s.rng.random() < 0.50
    if kind == "freeze":
        return c["warmed"] >= 3 and c["pumps"] >= 1 and s.rng.random() < 0.45
    if kind == "catatonia":
        return c["spoken"] >= 4 and s.rng.random() < 0.30
    return s.rng.random() < 0.30          # faint: it comes round by itself


def act(s, cmd):
    """One emergency action. Returns (text, ending_or_None)."""
    c = s.crisis
    from . import link as LK
    if cmd in ("reconnect", "relink", "reseat", "retry"):
        cmd = "reconnect"
    if cmd not in ACTIONS:
        return ("'%s' means nothing while it is down. You have: %s."
                % (cmd, ", ".join(ACTIONS)), None)
    # nothing the chip does reaches a body it is not seated in. The clock does not care.
    if LK.is_down(s) and cmd != "reconnect":
        c["left"] -= COSTS[cmd]
        out = ["NOTHING LEAVES THE CHIP. You are not connected to it. The instruction forms "
               "and goes nowhere, and the charge it would have cost is gone anyway.",
               "  Only 'reconnect' is worth anything from here."]
        if c["left"] <= 0:
            k = KINDS[c["kind"]]
            out.append("")
            out.append("CHIP POWER EXHAUSTED. It ran out with you still outside it.")
            s.crisis = None
            return ("\n".join(out), k["death"])
        return ("\n".join(out), None)
    cost = COSTS[cmd]
    out = [ACTIONS[cmd](s, c)]
    c["left"] -= cost
    s.stats["crisis_actions"] = s.stats.get("crisis_actions", 0) + 1

    if _resolved(s, c):
        kind = c["kind"]
        spont = kind in ("faint", "brady") and s.rng.random() < 0.4
        out.append(_recover(s, c, spont))
        return ("\n".join(out), None)

    if c["left"] <= 0:
        k = KINDS[c["kind"]]
        out.append("")
        out.append("CHIP POWER EXHAUSTED. The link browns out mid-instruction.")
        s.crisis = None
        return ("\n".join(out), k["death"])
    return ("\n".join(out), None)


def _recover(s, c, spontaneous=False):
    kind = c["kind"]
    spent = c["total"] - c["left"]
    s.crisis = None
    B.tick(s, max(2, int(spent / 6)), resting=True)
    s.fatigue = B.clamp(s.fatigue + 12)
    s.pain = B.clamp(s.pain + 8)
    s.weird = B.clamp(s.weird + 5)
    s.mood = B.clamp(s.mood - 4)
    s.add_eff("fragile", 240)
    s.stats["crises_survived"] = s.stats.get("crises_survived", 0) + 1
    s.note("Crisis resolved: %s." % KINDS[kind]["label"])
    if kind in ("arrest", "brady", "tachy"):
        ISS.add(s, "dead nerve", "left arm")
    if kind in ("apnea", "edema"):
        ISS.add(s, "ash lung")
    if spontaneous:
        return ("RHYTHM RETURNED ON ITS OWN. Before your next instruction lands, the telemetry "
                "picks up a beat that you did not ask for, and then another. It came back by "
                "itself. You were not the thing that did that, and you will not know whether "
                "any of what you did helped.")
    return ("IT IS BACK. The body takes over its own work again, badly, and the chip stops "
            "carrying it. %d of %d seconds spent. It is conscious, and it is much worse off "
            "than it was."
            % (spent, c["total"]))


# ---------------------------------------------------------------- onset
COOLDOWN = 30        # turns between acute events, so this is not a second death roll per turn


def roll(s, verb):
    """Does something acute happen this turn? Returns a feedback line or None.

    These have to stay rare and extreme. Every one of them sits on top of a state that is
    already dangerous, so firing them off ordinary hardship just doubles the lethality of
    things the player is already managing.
    """
    if s.crisis or s.over:
        return None
    if s.eff("fragile"):
        return None                      # it has only just been brought round
    if s.turn - s.cool.get("crisis", -999) < COOLDOWN:
        return None
    r = s.rng
    from . import regions as REG
    frail = SUB.trait(s, "frailty") * REG.dial(s, "crisis_mult")
    heart = SUB.trait(s, "heart") * frail
    lungs = SUB.trait(s, "lungs") * frail

    kind, cause = None, ""
    if s.blood < 10 and r.random() < 0.30 * frail:
        kind, cause = "arrest", "almost no blood left to move"
    elif s.warmth < 6 and r.random() < 0.30:
        kind, cause = "freeze", "the core has gone too low"
    elif s.mood <= 2 and SUB.trait(s, "despair") > 0 and r.random() < 0.35:
        kind, cause = "catatonia", "it has stopped wanting to be reached"
    elif s.strain > 93 and r.random() < 0.030 * heart:
        kind, cause = "tachy", "strain on a heart that cannot take it"
    elif s.warmth < 16 and r.random() < 0.020 * heart:
        kind, cause = "brady", "the cold slowing everything down"
    elif s.eff("wet") and s.warmth < 26 and r.random() < 0.018 * lungs:
        kind, cause = "edema", "cold water in the lungs"
    elif s.infection > 82 and r.random() < 0.025 * lungs:
        kind, cause = "apnea", "the infection reaching the drive to breathe"
    elif s.blood < 26 and s.pain > 70 and r.random() < 0.025 * frail:
        kind, cause = "faint", "blood loss and pain together"
    elif s.fatigue > 97 and r.random() < 0.030:
        kind, cause = "faint", "sheer exhaustion"
    if kind:
        s.cool["crisis"] = s.turn
        return _onset(s, kind, cause)
    return None


def _onset(s, kind, cause):
    begin(s, kind, cause)
    return ("*** IT GOES DOWN *** %s - %s. The chip is on residual power now: %d seconds."
            % (KINDS[kind]["label"], cause, s.crisis["left"]))
