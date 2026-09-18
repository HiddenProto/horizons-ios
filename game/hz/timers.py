"""Timed events. Something is coming, you have this many turns, here is what closes it.

A timer is JSON-safe: an id naming its behaviour, a countdown in turns, a hint, and a little
data bag. Behaviour lives in the dispatch tables below, keyed by that id.
"""
from . import body as B
from . import issues as ISS
from . import items as I


def add(s, tid, label, turns, hint, data=None):
    for t in s.timers:
        if t["id"] == tid:
            return None
    t = {"id": tid, "label": label, "left": int(turns), "hint": hint, "data": data or {}}
    s.timers.append(t)
    s.note("TIMED: %s - %d turns. %s" % (label, turns, hint))
    return t


def get(s, tid):
    for t in s.timers:
        if t["id"] == tid:
            return t
    return None


def drop(s, tid):
    t = get(s, tid)
    if t:
        s.timers.remove(t)
    return t


def lines(s):
    out = []
    for t in sorted(s.timers, key=lambda x: x["left"]):
        urgent = "!" if t["left"] <= 2 else " "
        out.append("  %s %-26s %d turn%s left  ->  %s"
                   % (urgent, t["label"], t["left"], "" if t["left"] == 1 else "s", t["hint"]))
    return out


# ---------------------------------------------------------------- satisfaction
def _sat_recall(s, t):
    return s.eff("hidden") or s.escape.get("progress", 0) >= s.escape.get("needed", 6)


def _sat_flood(s, t):
    return s.distance >= t["data"].get("from", 0) + 3.0


def _sat_storm(s, t):
    return s.eff("sheltered")


def _sat_stalker(s, t):
    return s.eff("fire") or I.armed(s) or s.eff("sheltered")


def _sat_chip(s, t):
    return s.chip >= t["data"].get("was", 0) + 5 or not any(
        i["kind"] == "chip fault" for i in s.issues)


def _sat_bleed(s, t):
    return B.bleed_rate(s) <= 0.02


SATISFY = {
    "recall": _sat_recall, "flood": _sat_flood, "storm": _sat_storm,
    "stalker": _sat_stalker, "chipwindow": _sat_chip, "bleedout": _sat_bleed,
}

CLEARED = {
    "recall": "The sweep passes over and finds nothing worth reporting.",
    "flood": "You are up out of the basin before the water gets where it was going.",
    "storm": "The shelter is up before the wall of ash arrives.",
    "stalker": "Whatever was pacing you decides the odds have changed, and leaves.",
    "chipwindow": "The link steadies inside the window. Nothing is lost.",
    "bleedout": "The bleeding is stopped with time to spare.",
}


# ---------------------------------------------------------------- expiry
def _x_recall(s, t):
    if s.escape.get("active"):
        return ("CAUGHT", "The sweep finds you off the route with nothing between you and the sky.")
    limb = s.rng.choice(["left arm", "right arm", "right leg", "left leg"])
    B.hurt(s, limb, s.rng.uniform(18, 32), "burn")
    s.weird = B.clamp(s.weird + 8)
    return (None, "MISSED: the sweep finds you in the open and burns a line across your %s "
                  "before you are under anything." % limb)


def _x_flood(s, t):
    s.add_eff("wet", 300)
    s.warmth = B.clamp(s.warmth - 26)
    B.hurt(s, s.rng.choice(["left leg", "right leg"]), s.rng.uniform(12, 22), "blunt")
    ISS.add(s, "cold shock")
    return (None, "MISSED: the basin fills faster than you crossed it. You come out the far "
                  "side soaked, battered and shaking.")


def _x_storm(s, t):
    B.hurt(s, "left ear", s.rng.uniform(10, 18), "cut")
    s.thirst = B.clamp(s.thirst + 16)
    s.strain = B.clamp(s.strain + 16)
    ISS.add(s, "ash lung")
    return (None, "MISSED: the storm arrives with nothing built. It sands you down for an hour "
                  "and leaves grey in your chest.")


def _x_stalker(s, t):
    limb = s.rng.choice(["right leg", "left arm", "tail"])
    if s.rng.random() < 0.22:
        B.sever(s, limb)
        return (None, "MISSED: it had been waiting for exactly this. Your %s goes with it." % limb)
    B.hurt(s, limb, s.rng.uniform(20, 34), "bite")
    return (None, "MISSED: it comes out of the dark at the hour you were least ready and opens "
                  "your %s." % limb)


def _x_chip(s, t):
    s.chip = B.clamp(s.chip - 12)
    s.weird = B.clamp(s.weird + 14)
    s.will = B.clamp(s.will - 10)
    ISS.add(s, "chip fault")
    return (None, "MISSED: the fault sets. Orders are arriving in the wrong order now, and it "
                  "can feel that they are.")


def _x_bleed(s, t):
    s.blood = B.clamp(s.blood - 18)
    if s.blood <= 0:
        return ("BLED OUT", "You did not stop it in time.")
    return (None, "MISSED: you did not close it in time. There is a great deal less of you now.")


EXPIRE = {
    "recall": _x_recall, "flood": _x_flood, "storm": _x_storm,
    "stalker": _x_stalker, "chipwindow": _x_chip, "bleedout": _x_bleed,
}


def tick(s, turns=1):
    """Advance every countdown. Returns (feedback lines, ending or None)."""
    out = []
    ending = None
    for t in list(s.timers):
        sat = SATISFY.get(t["id"])
        if sat and sat(s, t):
            s.timers.remove(t)
            out.append("RESOLVED: " + CLEARED.get(t["id"], t["label"] + " dealt with."))
            continue
        t["left"] -= turns
        if t["left"] > 0:
            if t["left"] <= 2:
                out.append("URGENT: %s in %d turn%s. %s"
                           % (t["label"], t["left"], "" if t["left"] == 1 else "s", t["hint"]))
            continue
        s.timers.remove(t)
        s.stats["timers_missed"] = s.stats.get("timers_missed", 0) + 1
        fn = EXPIRE.get(t["id"])
        if fn:
            key, text = fn(s, t)
            out.append(text)
            if key:
                ending = (key, text)
    return out, ending


# ---------------------------------------------------------------- spawning
def maybe_spawn(s, zone_key, verb):
    """The world starting a clock on you. Returns a feedback line or None."""
    r = s.rng
    if B.bleed_rate(s) > 0.15 and s.blood < 34 and not get(s, "bleedout"):
        add(s, "bleedout", "bleeding out", 5, "stop it: 'tend <limb>'")
        return "TIMED: you have about five turns of blood left at this rate."
    if any(i["kind"] == "chip fault" for i in s.issues) and not get(s, "chipwindow"):
        add(s, "chipwindow", "chip fault setting", 4, "'recalibrate' before it sets",
            {"was": s.chip})
        return "TIMED: the fault will set if it is not walked back inside four turns."
    if verb not in ("go", "forward", "advance", "walk", "move", "onward", "gather", "search"):
        return None
    if zone_key == "sink" and not get(s, "flood") and r.random() < 0.11:
        add(s, "flood", "the basin filling", 5, "get 3 units further on: 'go'",
            {"from": s.distance})
        return "TIMED: somewhere behind you a sluice has let go. The water is coming up."
    if zone_key == "flats" and not get(s, "storm") and r.random() < 0.10:
        add(s, "storm", "ash storm arriving", 4, "'shelter' before it lands")
        return "TIMED: the horizon behind you has gone the colour of a bruise."
    if zone_key == "woods" and not get(s, "stalker") and r.random() < 0.11:
        add(s, "stalker", "something pacing you", 5,
            "'use torch', make something to hold ('spear', 'blade', 'club'), or "
            "'shelter'")
        return "TIMED: something has picked up your trail and is keeping station on it."
    if zone_key in ("fence", "ridge", "shelf") and not get(s, "recall") and r.random() < 0.09:
        add(s, "recall", "recall sweep inbound", 6, "'hide' (charcoal helps) or get clear")
        return "TIMED: " + {
            "fence": "there is a drone line forming up out past the pylons, and it is a sweep.",
            "ridge": "the towers have stopped transmitting one after another, in a line, "
                     "coming this way.",
            "shelf": "something is coming out across the flat behind you in a line too even "
                     "to be weather.",
        }.get(zone_key, "a line is forming up behind you, and it is a sweep.")
    return None
