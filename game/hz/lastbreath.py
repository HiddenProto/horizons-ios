"""The moment it should have stopped, and did not.

Two things live here.

FINAL MESSAGES. Every death prints what this particular body did at the end. It is not a
game-over screen and it is not the same text twice - what each one does when it stops is the
only place the game ever says outright what was done to it. See subjects.FINAL.

THE REPRIEVE. Sometimes it does not go down the first time it should. It gets up, it is
briefly and completely lucid, and for a short window nothing can kill it. That window is not a
rescue and the game is careful never to present it as one: the thing that was killing it is
still killing it, none of it has been treated, and when the window closes the body is measured
against the actual numbers. Fix what is wrong and it walks away. Spend the window walking and
it dies at the end of it, having felt fine the whole way.

How likely it is at all is the subject's "grit", and the spread across the roster is wide on
purpose - 1278 has essentially none, because a thing with no pause in it has nothing to spend
on getting up, and 682 has nearly all of it.
"""
from . import body as B
from . import subjects as SUB

FRESH = {"active": False, "left": 0, "cause": "", "used": 0, "turns": 0}

# how long the clarity lasts, in turns
WINDOW = 6
WINDOW_682 = 8

# the only deaths a body can be pulled back from. Everything else is somebody arriving, or a
# decision, or the end of the act - none of which is a thing to get up from.
CATCHABLE = ("BLED OUT", "DRY", "HOLLOW", "SEPSIS", "COLD", "BOILED", "UNMADE",
             "COLLAPSED", "HEART FAILED", "DROWNED", "SUFFOCATED", "STOPPED",
             "CHOKED", "SHOCK",
             # and the three that arrive through the middle of it. A thing that does not go
             # down the first time it should does not go down for a harpoon either.
             "SHOT", "PINNED", "TOOK THE GROUND WITH IT")

# what the body has to look like when the window closes, per killing cause. These are the
# numbers the run has to actually move, and they are deliberately not generous: being one
# point off the wall is not surviving, it is dying more slowly.
SAFE = [
    ("blood", "low", 18.0, "there is not enough left in it"),
    ("thirst", "high", 88.0, "it never got any water"),
    ("hunger", "high", 92.0, "it was empty when it got up and it is empty now"),
    ("infection", "high", 88.0, "the wound was never dealt with"),
    ("warmth", "low", 12.0, "it never got warm"),
    ("heat", "high", 88.0, "it never got off the heat"),
    ("weird", "high", 90.0, "it never came back to itself"),
    ("fatigue", "high", 94.0, "it had nothing left to stand on"),
]


def get(s):
    d = getattr(s, "laststand", None)
    if not isinstance(d, dict):
        d = dict(FRESH)
        s.laststand = d
    for k, v in FRESH.items():
        d.setdefault(k, v)
    return d


def active(s):
    return bool(get(s)["active"])


def _window(s):
    return WINDOW_682 if getattr(s, "subject", "") == "682" else WINDOW


def _allowance(s):
    """How many times this body gets to not die. 682 gets two; most get one; some get none."""
    g = SUB.trait(s, "grit")
    if g <= 0.08:
        return 0
    return 2 if g >= 0.90 else 1


def chance(s, key):
    """The luck. Worse the second time, worse when there is nothing left to get up with."""
    d = get(s)
    if key not in CATCHABLE:
        return 0.0
    if d["used"] >= _allowance(s):
        return 0.0
    p = float(SUB.trait(s, "grit"))
    if d["used"]:
        p *= 0.45
    # a body that has already been taken apart has less to spend on this
    p *= max(0.30, 1.0 - 0.14 * B.limbs_lost(s) - 0.004 * len(s.issues) * 10.0)
    if s.mood < 20:
        p *= 0.60          # it has to want to
    if s.eff("rested"):
        p *= 1.15
    return max(0.0, min(0.92, p))


def try_catch(s, key, text):
    """Rolled at the moment of death. Returns the getting-up text, or None."""
    if s.rng.random() >= chance(s, key):
        return None
    d = get(s)
    d["active"] = True
    d["left"] = _window(s)
    d["turns"] = _window(s)
    d["cause"] = key
    d["used"] += 1
    s.stats["reprieves"] = s.stats.get("reprieves", 0) + 1
    hold(s)
    # the clarity. It is not painkiller and it is not healing - nothing on the body changes.
    # What changes is that for a few turns it is entirely present, and entirely willing.
    s.add_eff("clarity", 210)
    s.will = B.clamp(max(s.will, 88.0))
    s.mood = B.clamp(max(s.mood, 60.0))
    s.snap = B.clamp(float(getattr(s, "snap", 0.0) or 0.0) - 25.0)
    s.note("IT GOT UP. %s" % key)
    s.pending_voice.append("rise")
    rise = SUB.rising(getattr(s, "subject", "")) or (
        "It gets up. There is no good reason for it to be able to and it does it anyway.")
    return ("maybe lets not give up yet..\n\n"
            "  %s\n\n"
            "*** IT IS NOT OVER. %d TURNS. ***\n"
            "  What was killing it - %s - has not stopped and has not been treated. Nothing "
            "has healed. It simply cannot go down while this lasts.\n"
            "  When it runs out the body gets measured against the real numbers. Fix the thing "
            "or this happens again and it is the last time."
            % (rise, d["left"], key))


def hold(s):
    """Keep every lethal stat one step off the wall while the window is open."""
    s.blood = max(s.blood, 1.0)
    s.thirst = min(s.thirst, 99.0)
    s.hunger = min(s.hunger, 99.0)
    s.infection = min(s.infection, 99.0)
    s.warmth = max(s.warmth, 1.0)
    s.heat = min(float(getattr(s, "heat", 0.0) or 0.0), 99.0)
    s.weird = min(s.weird, 99.0)
    s.fatigue = min(s.fatigue, 99.0)


def _failing(s):
    """Everything still over the line when the window closes, worst first."""
    out = []
    for stat, side, limit, why in SAFE:
        v = float(getattr(s, stat, 0.0) or 0.0)
        bad = v < limit if side == "low" else v > limit
        if bad:
            out.append((stat, why))
    if B.bleed_rate(s) > 0.05:
        out.insert(0, ("blood", "it is still leaking"))
    hell = [i for i in s.issues
            if _is_hell(i["kind"])]
    if len(hell) >= 2:
        out.append(("issues", "it is carrying %d things that are still taking it apart"
                    % len(hell)))
    return out


def _is_hell(kind):
    from . import issues as ISS
    return bool((ISS.TYPES.get(kind) or {}).get("hell"))


def tick(s):
    """One turn of the window. Returns (lines, ending or None)."""
    d = get(s)
    if not d["active"]:
        return [], None
    hold(s)
    d["left"] -= 1
    if d["left"] > 0:
        left = d["left"]
        bad = _failing(s)
        note = ("Still wrong: %s." % ", ".join(w for _, w in bad[:2])) if bad else \
            "It is out of the wall. Hold it there."
        return (["*** %d %s OF THIS LEFT ***  %s"
                 % (left, "TURN" if left == 1 else "TURNS", note)], None)
    d["active"] = False
    d["left"] = 0
    if "clarity" in s.effects:
        del s.effects["clarity"]
    bad = _failing(s)
    if not bad:
        s.note("It held.")
        s.mood = B.clamp(s.mood - 6.0)
        s.will = B.clamp(s.will - 10.0)
        s.fatigue = B.clamp(s.fatigue + 12.0)
        s.pain = B.clamp(s.pain + 14.0)
        s.weird = B.clamp(s.weird + 6.0)
        return (["*** IT HELD. ***  The clarity goes out of it all at once and what is left "
                 "underneath is a body that nearly stopped and knows it. It is still here. "
                 "None of that was free and the next one will not go this way."], None)
    stat, why = bad[0]
    key = d["cause"]
    text = ("The window closes. It has been upright and lucid and entirely present for a "
            "little while, and underneath all of that nothing was ever dealt with - %s.\n"
            "  It goes down the second time the way it should have gone down the first." % why)
    return [], (key, text)


def banner(s):
    d = get(s)
    if not d["active"]:
        return []
    bad = _failing(s)
    L = ["*** STILL UP - %d %s ***  nothing can kill it until this runs out"
         % (d["left"], "TURN" if d["left"] == 1 else "TURNS")]
    if bad:
        L.append("  FIX THIS OR IT ENDS: " + "; ".join(w for _, w in bad[:3]))
    else:
        L.append("  Nothing is over the line right now. Keep it that way until the window "
                 "closes.")
    # What the window is actually like from the inside, which is the part that makes it a
    # trap: it is not hurting, it is not arguing, and it moves like nothing is wrong with it.
    L.append("  It is not feeling any of it. It is moving at a pace the body has not managed "
             "in hours and it is not refusing anything, and none of that is recovery.")
    return L


def status_word(s):
    d = get(s)
    return "LAST BREATH (%d)" % d["left"] if d["active"] else ""
