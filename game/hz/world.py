"""Zones laid out along one axis. Which set of them you get depends on the region: the surface
test, the crust under it, or the core under that."""
from . import body as B
from . import subjects as SUB
from . import items as I
from . import regions as REG
from . import rock as RK
from . import warrens as WR
from . import thebuilding as TB

# key, name, start distance, danger 0..1, cold drift, gather table, blurb
ZONES = [
    {
        "key": "holding", "name": "The Holding", "at": 0.0, "danger": 0.10, "cold": 0.00,
        "gather": {"cloth": 4, "scrap": 4, "ration": 3, "water": 3, "shard": 2, "cord": 1},
        "blurb": "Corridors with the lights still on and nobody left to turn them off. "
                 "Every surface is the colour of a held breath.",
    },
    {
        "key": "fence", "name": "The Fence Line", "at": 8.0, "danger": 0.22, "cold": 0.02,
        "gather": {"cloth": 3, "scrap": 4, "cord": 3, "water": 3, "shard": 2,
                   "charcoal": 1, "resin": 2, "hide": 1, "branch": 2},
        "blurb": "Dead grass, pylons humming to each other, and wire strung to keep something "
                 "either out or in.",
    },
    {
        "key": "flats", "name": "The Ash Flats", "at": 20.0, "danger": 0.30, "cold": -0.04,
        "gather": {"charcoal": 4, "scrap": 3, "shard": 3, "hide": 1, "water": 4,
                   "ration": 1, "cloth": 2},
        "blurb": "Grey powder to the knees and heat that stands up off it in sheets. "
                 "Nothing here drinks.",
    },
    {
        "key": "woods", "name": "The Rust Woods", "at": 35.0, "danger": 0.44, "cold": 0.03,
        "gather": {"branch": 5, "resin": 4, "cord": 3, "meat": 2, "hide": 2, "glowmoss": 2,
                   "water": 2, "cloth": 2},
        "blurb": "Trees of fused scrap, bark flaking orange, and the long ones moving between "
                 "them at the edge of where you can see.",
    },
    {
        "key": "sink", "name": "The Sink", "at": 50.0, "danger": 0.40, "cold": 0.11,
        "gather": {"water": 5, "glowmoss": 4, "hide": 2, "cloth": 2, "scrap": 3, "meat": 2},
        "blurb": "A flooded basin. Cold to the chest, and the cold gets in and stays.",
    },
    {
        "key": "steppe", "name": "The Glass Steppe", "at": 62.0, "danger": 0.38, "cold": -0.03,
        "gather": {"shard": 6, "scrap": 3, "charcoal": 2, "water": 1, "cloth": 2},
        "blurb": "Sand fused to a mirror by something that happened here once. You can see "
                 "yourself walking, a long way off, doing almost the same thing.",
    },
    {
        "key": "ridge", "name": "Signal Ridge", "at": 75.0, "danger": 0.50, "cold": 0.07,
        "gather": {"scrap": 5, "cord": 4, "stim": 1, "ration": 2, "water": 2, "cloth": 2},
        "blurb": "Towers in a row, all leaning the same way, all still transmitting. "
                 "The static gets into your memory and rearranges the furniture.",
    },
    {
        "key": "shelf", "name": "The Horizon Shelf", "at": 88.0, "danger": 0.34, "cold": 0.05,
        "gather": {"scrap": 3, "water": 2, "cloth": 2, "shard": 2},
        "blurb": "The ground runs flat and then stops running. Past the stopping place the sky "
                 "keeps going, but it keeps going wrong.",
    },
]

GOAL = 100.0          # kept for anything that still asks; goal(s) is the real answer

ZONE_SETS = {"outside": ZONES, "crust": REG.CRUST_ZONES, "core": REG.CORE_ZONES,
             # the three Destiny acts are their own ground, not the same ground harder
             "rock": RK.ROCK_ZONES, "warrens": WR.WARREN_ZONES, "deep": WR.DEEP_ZONES,
             # and the last tier is not on the planet at all - it is the building
             "building": TB.BUILDING_ZONES}


def zones(s):
    zs = ZONE_SETS.get(REG.zone_set_key(s), ZONES)
    if REG.on_destiny(s):
        return REG.stretched_zones(REG.stretch_key(s), zs, REG.base_goal(s))[0]
    return zs


def goal(s):
    if REG.on_destiny(s):
        zs = ZONE_SETS.get(REG.zone_set_key(s), ZONES)
        return REG.stretched_zones(REG.stretch_key(s), zs, REG.base_goal(s))[1]
    return float(REG.info(s)["goal"])


def zone(s):
    zs = zones(s)
    z = zs[0]
    for cand in zs:
        if s.distance >= cand["at"]:
            z = cand
    return z


def zone_at(s, d):
    """The ground a given distance falls in - used to look one step ahead at a shut door."""
    z = zones(s)[0]
    for cand in zones(s):
        if d >= cand["at"]:
            z = cand
    return z


def zone_index(s):
    return zones(s).index(zone(s))


def danger(s):
    d = zone(s)["danger"] * REG.dial(s, "danger_mult")
    if s.night:
        d += 0.12
    if s.eff("fire"):
        d -= 0.06
    if s.eff("hidden"):
        d -= 0.14
    if B.legs_usable(s) < 2:
        d += 0.08
    return max(0.02, min(0.95, d))


def cold(s):
    c = zone(s)["cold"]
    if s.eff("wet"):
        c += 0.09
    # deeper regions push whichever direction the layer already leans, heat included
    d = REG.dial(s, "drain_mult")
    return c * (1.0 + (d - 1.0) * 0.5)


def advance(s):
    """One push forward. Returns a text line."""
    if not B.can_walk(s) and B.arms_usable(s) == 0:
        return "You have nothing left to move with. You lie where you are."
    step, mins = B.move_cost(s)
    # In the Final the ground is not what stops you. Look one step ahead: if that step would
    # cross into new ground and the way into it is shut, the step does not happen, and the
    # frame says what shape the problem is without ever saying what the answer is made of.
    if REG.on_final(s):
        nxt = zone_at(s, min(goal(s), s.distance + step))
        if nxt["key"] != zone(s)["key"]:
            shut, why = TB.gate_for(s, nxt["key"])
            if shut:
                B.tick(s, 14, exertion=0.6)
                return why
    before = zone(s)["name"]
    s.distance = min(goal(s), s.distance + step)
    s.stats["steps"] = s.stats.get("steps", 0) + 1
    B.tick(s, mins, exertion=1.35, cold=cold(s))
    after = zone(s)["name"]
    # the ones that keep going through pain do real damage doing it. This is the cost
    # side of the `pushes` trait and it is charged here rather than in move_cost,
    # because move_cost is also called to look ahead and must not have side effects.
    _push = SUB.trait(s, "pushes")
    if _push > 0 and s.pain > 62:
        hurtleg = None
        for n in ("left leg", "right leg"):
            if s.limbs[n]["state"] != "lost":
                if hurtleg is None or s.limbs[n]["hp"] < s.limbs[hurtleg]["hp"]:
                    hurtleg = n
        if hurtleg:
            B.hurt(s, hurtleg, _push * (1.6 + 0.06 * (s.pain - 62.0)), "blunt")
            s.strain = B.clamp(s.strain + 2.5 * _push)
            s.feedback.append("IT WENT ON THE ORDER AND IT SHOULD NOT HAVE. Nothing in "
                              "it argued and nothing in it slowed down, and the %s took "
                              "the whole of that step." % hurtleg)
    how = "walk" if B.legs_usable(s) == 2 else ("limp" if B.legs_usable(s) == 1 else "drag yourself")
    line = "You %s forward. %.1f of %.0f." % (how, s.distance, goal(s))
    if after != before:
        line += "  --- %s ---  %s" % (after.upper(), zone(s)["blurb"])
        s.flag("entered_" + zone(s)["key"])
        from . import intel as IN
        gl = IN.gain(s, "zone")
        if gl:
            s.feedback.append(gl)
        # new ground in the Final is a checkpoint, and the checkpoint is on disk
        if REG.on_final(s):
            REG.save_final(s, zone(s)["name"])
            line += "\n  (This ground is written down. Leaving here with 'leave' keeps it.)"
    return line


def gather(s):
    z = zone(s)
    table = z["gather"]
    if not table:
        return "There is nothing here to take."
    names = list(table)
    weights = [table[n] for n in names]
    picks = 2 + (1 if s.rng.random() < 0.35 else 0)
    if B.arms_usable(s) == 0:
        return "You cannot pick anything up."
    if B.arms_usable(s) == 1 and s.rng.random() < 0.5:
        picks -= 1
    got = []
    for _ in range(picks):
        n = s.rng.choices(names, weights=weights, k=1)[0]
        I.give(s, n, 1)
        got.append(n)
    s.stats["gathers"] = s.stats.get("gathers", 0) + 1
    s.pending_voice.append("find")
    B.tick(s, 34, exertion=1.15, cold=cold(s))
    extra = ""
    if s.rng.random() < danger(s) * 0.35:
        limb = s.rng.choice(["left arm", "right arm"])
        B.hurt(s, limb, s.rng.uniform(8, 18), "cut")
        extra = " Something in the pile opens your %s on the way out." % limb
    return "You search %s and come up with: %s.%s" % (z["name"], ", ".join(got), extra)


def camp(s, hours=6.0):
    """Sleep with whatever protection you have arranged."""
    safety = 1.0
    notes = []
    if s.eff("sheltered"):
        safety += 1.2
        notes.append("Your shelter holds.")
    if s.eff("fire"):
        safety += 0.6
        notes.append("The fire keeps its circle.")
    edge = I.weapon_edge(s)
    if edge > 0:
        safety += 0.45 * edge
        notes.append("Something stays in its hands the whole night.")
    if s.eff("charge_set"):
        safety += 1.4
        notes.append("The thing it buried on the back trail is still there.")
    safety /= max(0.3, danger(s) * 2.2)
    s.pending_voice.append("sleep")
    txt, interrupted = B.sleep(s, hours, safety=max(0.25, safety), cold=cold(s))
    out = [txt] + notes
    # a set snare works while you do not. This is the only food in the game you get for
    # having planned ahead rather than for having gone looking.
    if s.eff("snared"):
        s.effects.pop("snared", None)
        I.take(s, "snare")
        if s.rng.random() < 0.62:
            n = 1 + (1 if s.rng.random() < 0.3 else 0)
            I.give(s, "meat", n)
            I.give(s, "hide")
            out.append("The snare has something in it. It is not pretty and it is %d of meat "
                       "and a hide you did not have to chase." % n)
        else:
            out.append("The snare is sprung and empty. Something got out of it, and took the "
                       "scrap with it.")
    if interrupted and s.rng.random() < 0.55:
        limb = s.rng.choice(["left leg", "right leg", "tail", "left arm"])
        B.hurt(s, limb, s.rng.uniform(10, 26), "bite")
        out.append("Something had your %s in its mouth before you were properly awake." % limb)
    return " ".join(out)


def build_shelter(s):
    if B.arms_usable(s) < 1:
        return "You cannot build with no arms."
    have_b = I.has(s, "branch", 2)
    have_h = I.has(s, "hide")
    if not (have_b or have_h):
        return "You need branches or a hide to make anything that keeps weather off."
    if have_b:
        I.take(s, "branch", 2)
    if have_h:
        I.take(s, "hide", 1)
    s.add_eff("sheltered", 600)
    B.tick(s, 50, exertion=1.2, cold=cold(s))
    return "You wedge a lean-to together. It is low and mean and it is yours."


def progress_bar(s, width=24):
    filled = int(round(width * s.distance / goal(s)))
    return "[" + "#" * filled + "-" * (width - filled) + "]"
