"""Leaving instead of finishing.

The horizon is the end of the test. Going sideways off the measured line is the end of the
test's authority, which is a different thing. Every zone has one way out that is not forward;
you have to find it first, and once you commit, the recall starts hunting.

The chip is the complication. It is most of this creature's intelligence and all of your
control. Cutting it out is the only clean break, and it is a break for both of you.
"""
from . import body as B
from . import items as I
from . import timers as T
from . import world as W

ROUTES = {
    "holding": "a service shaft behind the tank room that does not appear on any door list",
    "fence": "a breach where something large went through the wire and nobody came to fix it",
    "flats": "a storm culvert running away under the ash at right angles to your heading",
    "woods": "a game trail the long ones use, going sideways and steeply down",
    "sink": "a spillway at the basin's edge with a current going somewhere unmeasured",
    "steppe": "a fault in the glass, wide enough to walk in, roofed over by its own edges",
    "ridge": "a maintenance tunnel under the tower line, still lit, still ventilated",
    "shelf": "a dead patch in the projection where the grid does not resolve, and you can walk in",
}

NEEDED = 6.0


def known_here(s):
    return W.zone(s)["key"] in (s.escape.get("known") or [])


def find_route(s, quiet=False):
    """Discovery. Returns a line, or None if there was nothing to find."""
    k = W.zone(s)["key"]
    known = s.escape.setdefault("known", [])
    if k in known:
        return None
    known.append(k)
    s.escape["route"] = k
    desc = ROUTES.get(k, "a way out that is not forward")
    s.note("ESCAPE ROUTE FOUND in %s: %s" % (W.zone(s)["name"], desc))
    if quiet:
        return None
    return ("You have found a way out of the test rather than through it: %s.\n"
            "  Use it with 'escape'. It is a one-way decision and the recall will come." % desc)


def begin(s):
    from . import regions as REG
    if not REG.flag(s, "escape"):
        return ("There is no off the route down here. The route IS the hole. Whatever you are "
                "going to do about %s, you do it at the bottom of it."
                % ("the battery" if REG.info(s)["goal_kind"] == "battery" else "the line"))
    if s.escape.get("active"):
        return "You are already off the line. Keep going: 'go' puts distance between you and it."
    if not known_here(s):
        return ("You do not know a way out of %s. Ways out get found by looking - 'gather' - "
                "and by what happens to you on the road." % W.zone(s)["name"])
    if B.legs_usable(s) == 0 and B.arms_usable(s) == 0:
        return "You cannot go anywhere at all, let alone sideways."
    s.escape["active"] = True
    s.escape["progress"] = 0.0
    s.escape["needed"] = NEEDED
    s.stats["escape_tries"] = s.stats.get("escape_tries", 0) + 1
    s.flag("went_off_route")
    T.add(s, "recall", "recall sweep hunting you", 8,
          "get clear ('go'), or 'hide'")
    s.mood = B.clamp(s.mood + 12)
    s.will = B.clamp(s.will + 8)
    B.tick(s, 30, exertion=1.4)
    return ("You turn off the line.\n"
            "  %s\n"
            "  Nothing stops you, which is the frightening part - the enclosure was never the "
            "problem. Something above you notices the heading change inside a minute.\n"
            "  KEEP GOING: 'go' now buys distance from the test, not toward the horizon. "
            "'hide' breaks their line of sight. You need about %d good pushes."
            % (ROUTES.get(W.zone(s)["key"], "You go sideways."), int(NEEDED)))


def push(s):
    """A 'go' while off the route. Returns a text line."""
    step, mins = B.move_cost(s)
    gain = step * 0.9
    s.escape["progress"] = s.escape.get("progress", 0.0) + gain
    B.tick(s, mins, exertion=1.5, cold=W.cold(s))
    p, need = s.escape["progress"], s.escape.get("needed", NEEDED)
    line = "You put more ground between yourself and the line. %.1f of %.0f clear." % (p, need)
    if s.rng.random() < 0.3:
        limb = s.rng.choice(["left leg", "right leg", "left arm", "tail"])
        B.hurt(s, limb, s.rng.uniform(8, 18), "cut")
        line += " The country off the route is not maintained, and it takes a piece of your %s." % limb
    return line


def hide(s):
    if I.has(s, "charcoal"):
        I.take(s, "charcoal")
        s.add_eff("hidden", 180)
        B.tick(s, 30, exertion=0.8)
        return ("You black out the shine of your eyes with charcoal and get under cover. "
                "Nothing about you reads as warm, lit, or worth a second pass.")
    s.add_eff("hidden", 80)
    B.tick(s, 35, exertion=0.9)
    return ("You get into cover and hold still. Your eyes are the problem - they do not have an "
            "off switch - so you keep them shut and breathe slowly.")


def complete(s):
    return s.escape.get("active") and s.escape.get("progress", 0) >= s.escape.get("needed", NEEDED)


def cut_chip(s):
    """The only clean break. Returns (ending_key or None, text)."""
    if s.escape.get("chip_cut"):
        return None, "It is already out."
    if B.arms_usable(s) == 0:
        return None, "You need a working arm to do this, and it does not have one."
    if not I.has(s, "shard"):
        return None, "That needs a cutting edge. Find or make a 'shard'."
    I.take(s, "shard")
    s.escape["chip_cut"] = True
    B.hurt(s, "left ear", 18, "cut")
    prog = s.escape.get("progress", 0.0)
    if s.escape.get("active") and prog >= s.escape.get("needed", NEEDED) * 0.6:
        return "CUT LOOSE", None
    return "SIGNAL LOST", None


def status_line(s):
    if not s.escape.get("active"):
        if s.escape.get("known"):
            return "ESCAPE  routes known: %s  (use 'escape' in one of them)" % ", ".join(
                s.escape["known"])
        return None
    return ("ESCAPE  OFF THE ROUTE - %.1f of %.0f clear%s"
            % (s.escape.get("progress", 0), s.escape.get("needed", NEEDED),
               "  [chip cut]" if s.escape.get("chip_cut") else ""))
