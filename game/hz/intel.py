"""How much the chip actually understands of what it is looking at.

The chip is most of this creature's intelligence, but it woke up as ignorant as the body did.
Intelligence is the one stat that only goes up, and it buys two things: the ability to read a
manufactured object for what it is, and the ability to build with it.

Below the threshold you do not get a name. You get what it looks like - "a flat sealed packet,
cold to the touch" - and you can still put it in the wound and hope. Hoping is how a lot of
this gets learned.
"""
from . import body as B

# what raising it is worth, and where it comes from
GAINS = {
    "truth": (6.0, "something it worked out about itself"),
    "answer": (2.0, "a straight answer given to it"),
    "craft": (3.0, "the first time a thing was built"),
    "read": (2.5, "something with writing on it"),
    "issue": (1.0, "a complication worked through"),
    "zone": (1.5, "ground nobody described to it"),
    "identify": (1.0, "a thing correctly recognised"),
}

BANDS = [
    (0.0, "blank", "it can name what it can eat and nothing else"),
    (20.0, "slow", "simple made things read as shapes with uses"),
    (38.0, "reading", "most labels resolve, given a moment"),
    (56.0, "capable", "it can work out what a thing is for from how it is built"),
    (74.0, "sharp", "very little arrives unrecognised"),
    (90.0, "lit", "it reads the intent behind the object"),
]


def level(s):
    return float(getattr(s, "intel", 14.0) or 0.0)


def reading_level(s):
    """What it can actually resolve, as opposed to what it understands.

    Understanding and eyesight are not the same faculty. One of them cannot hold a thing
    still long enough to read the small print on it, and no amount of getting cleverer fixes
    an eye. This is what gates naming an object; level() still gates everything else.
    """
    from . import subjects as SUB
    j = SUB.trait(s, "jitter")
    if j <= 0:
        return level(s)
    return level(s) * (1.0 - 0.38 * j)


def band(s):
    v = level(s)
    out = BANDS[0]
    for b in BANDS:
        if v >= b[0]:
            out = b
    return out


def word(s):
    return band(s)[1]


def gain(s, kind, mult=1.0):
    """Returns a feedback line, or None."""
    spec = GAINS.get(kind)
    if not spec:
        return None
    amt = spec[0] * mult
    before = level(s)
    s.intel = min(100.0, before + amt)
    if int(s.intel / 1) == int(before / 1) and amt < 0.5:
        return None
    crossed = band_crossed(before, s.intel)
    if crossed:
        return ("INTELLIGENCE %s -> %.0f. %s. The link is carrying more than it was."
                % (crossed[1].upper(), s.intel, crossed[2].capitalize()))
    return None


def band_crossed(before, after):
    for b in BANDS:
        if before < b[0] <= after:
            return b
    return None


# ---------------------------------------------------------------- reading a thing
def identified(s, name):
    from . import items as I
    spec = I.MANUFACTURED.get(name)
    if not spec:
        return True                       # ordinary material, obvious on sight
    if name in (getattr(s, "known_items", None) or []):
        return True
    return reading_level(s) >= spec["intel"]


def label(s, name):
    """What to call it on screen."""
    from . import items as I
    if identified(s, name):
        return name
    return I.MANUFACTURED[name]["looks"]


def describe(s, name):
    from . import items as I
    spec = I.MANUFACTURED.get(name)
    if not spec:
        return I.CATALOG.get(name, "")
    if identified(s, name):
        return I.CATALOG.get(name, "")
    return ("%s You do not know what it is for. You could put it in a wound and find out."
            % spec["looks"].capitalize())


def tick(s):
    """Anything in the pack that has just become readable says so, once."""
    from . import items as I
    out = []
    known = getattr(s, "known_items", None)
    if known is None:
        known = s.known_items = []
    for name in list(s.inv):
        spec = I.MANUFACTURED.get(name)
        if not spec or name in known:
            continue
        if reading_level(s) >= spec["intel"]:
            known.append(name)
            out.append("YOU CAN READ IT NOW: %s - it is a %s. %s"
                       % (spec["looks"].capitalize(), name, I.CATALOG.get(name, "")))
    return out


def learn_item(s, name):
    known = getattr(s, "known_items", None)
    if known is None:
        known = s.known_items = []
    if name not in known:
        known.append(name)
        return True
    return False


def line(s):
    b = band(s)
    out = "MIND  intel %3.0f  (%s - %s)" % (level(s), b[1], b[2])
    from . import subjects as SUB
    if SUB.trait(s, "jitter") > 0:
        out += "\n      eyes will not hold still - it reads as if it were %.0f" % reading_level(s)
    return out
