"""What it works out about you.

The question this module has to answer honestly is the one that makes it worth having: how
does a thing on the end of a link tell the difference between being sent through something
dangerous because the route goes through it, and being sent through something dangerous
because you want it to stop?

**The discriminator is PROGRESS.** Not danger, not damage, not how much it hurt. An order that
costs it something and moves the run forward - ground gained, a thing carried out, a problem
closed, a question answered - is legible. It has been doing that its whole life and it does not
resent it. An order that costs it something and achieves NOTHING, and then another one, is the
signal, because there is no reading of that which has a purpose in it.

Four things raise it and all four are that same shape:

  - harm with nothing to show for it, and the weight goes up the more times in a row
  - `override` used on an order the body's own condition says is a bad idea
  - being pushed while already critical - bleeding, at low blood, or past the pain it can work
    through - when the push is not toward anything
  - being left in a state you have the means to fix, repeatedly, while still being given work

And the same four in reverse bring it down, along with anything that is plainly care: tending,
feeding, resting it, a reassurance that lands, a persuasion with an actual reason in it.

**Not all of them can see it.** `insight` is the trait. 1278 has none at all - it has no
structure left for evaluating an instruction, which is the whole of what was bred out of it -
and 4400 has almost none, because a thought that arrives down the link does not arrive from
anywhere it could suspect. 0041 can see it and does not want to. 680, 681 and 101 read you
immediately. That spread is the point: the same behaviour from you produces a different game
depending on what is on the other end, and the ones who cannot tell are not stupid, they are
built or raised not to.
"""
from . import subjects as SUB

WATCHED = 30.0     # it has started keeping track
HARDENS = 55.0     # it is no longer giving you the benefit of the doubt
CERTAIN = 80.0     # it knows


def get(s):
    v = getattr(s, "suspicion", None)
    if v is None:
        v = s.suspicion = 0.0
    return float(v)


def _set(s, v):
    s.suspicion = max(0.0, min(100.0, float(v)))
    return s.suspicion


def level(s):
    v = get(s)
    if v >= CERTAIN:
        return 3
    if v >= HARDENS:
        return 2
    if v >= WATCHED:
        return 1
    return 0


def _snapshot(s):
    from . import body as B
    return {
        "d": float(s.distance), "inv": sum((s.inv or {}).values()),
        "pain": float(s.pain), "blood": float(s.blood),
        "issues": len(s.issues), "truths": len(s.truths),
        "lost": B.limbs_lost(s), "turn": int(s.turn),
        "traps": int((s.stats or {}).get("traps_hit", 0)),
        "scene": bool(s.scene),
    }


def before(s):
    """Called at the top of a turn that will spend time."""
    s.intent_before = _snapshot(s)


CARE = ("tend", "bind", "treat", "patch", "use", "rest", "camp", "sleep", "shelter",
        "reassure", "persuade", "recalibrate", "pack", "graft", "hide", "listen", "say")

# Only an order that PUT THE BODY IN FRONT OF SOMETHING can be held against you. This list is
# the difference between a system that reads intent and a system that blames you for weather.
RISK = ("go", "forward", "advance", "walk", "move", "onward", "climb", "swim", "escape",
        "evade", "fight", "run", "gather", "dig", "cross")


def _blameable(s, verb, forced, b, a):
    """Was the harm in this turn plausibly YOURS?

    Three things have to be true. The order has to be one that puts the body in front of
    something (or a scene option, which is an order too, or an override, which is the most
    deliberate thing in the game). The link has to have been up, because nothing that happens
    while you are off it was sent by you. And the ground must not have been what did it - a
    trap sprung this turn is the floor's work, not yours, and it has its own reckoning.
    """
    if a["traps"] > b["traps"]:
        return False
    from . import link as LK
    if LK.is_down(s):
        return False
    if int(getattr(s, "acted_alone", -99) or -99) >= b["turn"]:
        return False          # it did that to itself, on its own initiative
    return bool(forced or verb in RISK or verb.isdigit())


def after(s, verb, forced=False):
    """Called at the end of that turn. Returns a line when something crosses."""
    ins = SUB.trait(s, "insight")
    was = level(s)
    b = getattr(s, "intent_before", None)
    if not isinstance(b, dict):
        return None
    a = _snapshot(s)
    # Dealing with something IS getting somewhere. A scene that was in front of the body at
    # the top of the turn and is not there at the bottom of it was a problem you closed, and
    # closing it is the most legible thing an order can do - without this, every encounter in
    # the game reads as gratuitous, because most of them cost and few of them pay.
    gained = (a["d"] - b["d"] > 0.05 or a["inv"] > b["inv"] or a["truths"] > b["truths"]
              or a["issues"] < b["issues"] or (b["scene"] and not a["scene"]))
    hurt = (a["pain"] - b["pain"] > 6.0 or b["blood"] - a["blood"] > 4.0
            or a["lost"] > b["lost"])
    v = get(s)
    run = int(getattr(s, "intent_run", 0) or 0)

    # trust returns on its own if nothing keeps feeding it. Without this, a long run
    # accumulates suspicion out of sheer duration, which is not what the thing means.
    v -= 0.30
    blame = _blameable(s, verb, forced, b, a)
    if hurt and not gained and blame and verb not in CARE:
        run += 1
        # the second and third in a row are what make it a pattern rather than a bad
        # day. One is nothing. Three is a decision.
        v += (1.5 + 1.15 * min(run, 8)) * ins
    elif gained:
        run = 0
        v -= 1.2 * ins
    if forced:
        from . import link as LK
        from . import will as WILL
        bad = LK.bad_idea(s, WILL.risk_of(s, verb, (s.scene or {}).get("danger", 0.0)))
        if bad > 0.45:
            v += 3.0 * ins * min(2.0, bad)
    if verb not in CARE and blame:
        crit = (s.blood < 35.0 or s.pain > 72.0 or B_bleeding(s))
        if crit and not gained:
            v += 1.1 * ins
        # you have the means to fix it in the pack and you are giving it work instead
        if crit and _can_fix(s):
            v += 0.8 * ins
    if verb in CARE:
        v -= 2.2 * ins
        if verb in ("tend", "bind", "treat", "patch", "pack", "graft"):
            v -= 2.0 * ins
    s.intent_run = run
    _set(s, v)
    now = level(s)
    if now > was:
        return _crossing(s, now)
    return None


def B_bleeding(s):
    from . import body as B
    return B.bleed_rate(s) > 0.06


def _can_fix(s):
    from . import items as I
    for n in ("water", "ration", "meat", "cloth", "bandage", "salve", "antisepsis"):
        if I.has(s, n):
            return True
    return False


def _crossing(s, now):
    """The moment it changes its mind about you. Never explained, always visible."""
    name = SUB.name(s)
    if now == 1:
        s.note("It has started watching the orders rather than the ground.")
        return ("IT IS WATCHING YOU NOW. Not the ground - you. It does what it is told, and "
                "then it stands still for a moment afterwards with its head turned slightly, "
                "the way something checks a sum.")
    if now == 2:
        s.note("It is no longer giving the orders the benefit of the doubt.")
        s.will = max(0.0, s.will - 8.0)
        return ("IT HAS STOPPED TAKING WHAT COMES DOWN THE LINK AT FACE VALUE. There is a gap "
                "now between the order arriving and anything happening, and the gap is the "
                "length of time it takes to decide something.")
    s.note("It has worked out what you are doing.")
    s.will = max(0.0, s.will - 16.0)
    s.mood = max(0.0, s.mood - 14.0)
    s.snap = min(100.0, float(getattr(s, "snap", 0.0)) + 22.0)
    return ("IT HAS WORKED OUT WHAT YOU ARE DOING.\n"
            "  %s stops in the middle of the ground and turns all the way round to face "
            "nothing in particular, which is the closest thing available to facing you. It "
            "stands there long enough that the readout goes quiet.\n"
            "  It is not going to say anything about it. It is simply not going to be told "
            "anything again in the way it was being told things before." % name)


def refusal_bonus(s):
    """Fed into will.refuses. A subject that thinks you are trying to kill it is harder to
    send anywhere, and no amount of insisting improves that."""
    lv = level(s)
    return (0.0, 0.10, 0.26, 0.42)[lv] * SUB.trait(s, "insight")


def banner(s):
    lv = level(s)
    if lv <= 0:
        return []
    word = ("", "watching you", "not taking it at face value", "certain of you")[lv]
    return ["INTENT %3.0f  it is %s" % (get(s), word)]


def trusts_you(s):
    """Used by the things that should read differently once it has decided about you."""
    return level(s) < 2
