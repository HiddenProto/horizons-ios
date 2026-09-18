"""The headphones, which are two separate things wearing one shape.

The SHELL is armour. It is plate bonded over the cups and it protects exactly what it sits on -
the sides of the head and the ears under them - and nothing else at all. A hit anywhere below
the neck does not care that they are there. This is the only directional protection in the
game: it has a place, and outside that place it is worth nothing.

The MUSIC is not armour. It does not stop anything hitting anything. What it does is hold a
mind together that does not hold itself together, and the only evidence that it matters is
what happens when it stops.

They break together, because they are one object. That is the trap: the hit that takes the
armour off also takes the sound away, at the exact moment something has just hit it hard
enough to break plate.
"""
from . import body as B
from . import subjects as SUB

# what the shell covers. Nothing else.
COVERED = ("left ear", "right ear")

# how much of a covered hit the shell eats while it is whole
SOAK = 0.80


def get(s):
    p = getattr(s, "phones", None)
    if not isinstance(p, dict):
        return None
    return p


def worn(s):
    p = get(s)
    return bool(p and p.get("on"))


def playing(s):
    p = get(s)
    return bool(p and p.get("on") and p.get("music"))


def condition(s):
    p = get(s)
    return float(p.get("hp", 0.0)) if p else 0.0


def soak(s, limb, amount):
    """Take a hit on the shell instead of the head. Returns (amount_through, lines)."""
    p = get(s)
    if not p or not p.get("on") or limb not in COVERED:
        return amount, []
    eaten = amount * SOAK
    p["hp"] = max(0.0, float(p.get("hp", 0.0)) - eaten * 1.15)
    out = []
    if p["hp"] <= 0.0:
        out.extend(break_them(s, "it took a hit the shell could not take"))
    elif p["hp"] < 35.0 and not p.get("warned"):
        p["warned"] = True
        out.append("THE SHELL IS GOING. The casing over the ears is split and hanging. It is "
                   "still playing. It will not take many more like that.")
    return amount - eaten, out


def break_them(s, why):
    """Both halves go at once, because they were always one object."""
    p = get(s)
    if not p or not p.get("on"):
        return []
    p["on"] = False
    p["music"] = False
    p["hp"] = 0.0
    p["broke_at"] = getattr(s, "turn", 0)
    s.stats["phones_lost"] = s.stats.get("phones_lost", 0) + 1
    s.note("THE HEADPHONES ARE GONE: " + why)
    from . import link as LK
    out = ["*** THE HEADPHONES COME APART ***  %s.\n"
           "  Two things happen and only one of them is about armour. The side of its head is "
           "bare now, and everything that reaches it there reaches it properly.\n"
           "  And the sound stops. It has never once stopped." % why]
    went = LK.snap(s, 34.0, "the sound stopping")
    s.weird = B.clamp(s.weird + 12.0)
    s.mood = B.clamp(s.mood - 14.0)
    if went:
        out.append(went)
    return out


def tick(s, minutes):
    """What the sound is worth, per minute, measured only by its absence."""
    p = get(s)
    if not p:
        return []
    from . import link as LK
    per = minutes / 60.0
    if p.get("on") and p.get("music"):
        # it is not calm. It is held. There is a difference and the difference is that this
        # stops the moment the object does.
        LK.calmed(s, 3.4 * per)
        s.weird = B.clamp(s.weird - 0.9 * per)
        return []
    # no sound. The thing it was holding down comes back up on its own.
    s.snap = B.clamp(float(getattr(s, "snap", 0.0) or 0.0) + 2.6 * per)
    s.weird = B.clamp(s.weird + 0.7 * per)
    out = []
    if not p.get("mourned") and getattr(s, "turn", 0) - int(p.get("broke_at", 0)) >= 3:
        p["mourned"] = True
        out.append("IT KEEPS PUTTING A HAND UP TO THE SIDE OF ITS HEAD. Nothing is there. It "
                   "does it again a few steps later.")
    return out


def line(s):
    """The frame readout. Says both halves separately, because they are separate."""
    p = get(s)
    if not p:
        return None
    if not p.get("on"):
        return "EARS  headphones destroyed - no plate on the head, and no sound in it"
    hp = p.get("hp", 100.0)
    word = ("intact" if hp > 80 else "scuffed" if hp > 55 else
            "cracked" if hp > 35 else "splitting")
    return ("EARS  headphones %s (%.0f%%) - plate over the ears only%s"
            % (word, hp, ", and still playing" if p.get("music") else ""))


def wants_repair(s):
    p = get(s)
    return bool(p and p.get("on") and p.get("hp", 100.0) < 70.0)


def mend(s):
    """Patch the shell. The sound is not something you can put back."""
    p = get(s)
    if not p:
        return "There is nothing over its ears to mend."
    if not p.get("on"):
        return ("The set is in pieces and the pieces are somewhere behind you. There is no "
                "mending this, and there is nothing in here that makes a new one.")
    if p.get("hp", 100.0) >= 99.0:
        return "The shell is whole. Leave it alone."
    from . import items as I
    if not (I.has(s, "scrap") and I.has(s, "cord")):
        return "Patching the shell takes scrap and cord, and you have not got both."
    I.take(s, "scrap")
    I.take(s, "cord")
    p["hp"] = min(100.0, p.get("hp", 0.0) + 38.0)
    p["warned"] = False
    B.tick(s, 25)
    return ("You talk it through holding still - which is most of the work - and lash scrap "
            "over the split in the casing. The plate is ugly and it is plate. Underneath it "
            "the sound has not stopped once.")
