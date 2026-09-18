"""Three acts, going down.

OUTSIDE is the original test: walk the surface to the line they drew. It is the only one you
can pick cold, and it is the tutorial for the other two whether it admits that or not.

INTO THE CRUST is under it. Four layers, complications that were never switched on up top, and
the first place you can build something to carry things in.

INTO THE CORE is the bottom. Six layers, severe, and it does not end at a line - it ends at a
battery. Every chip knows to bring the battery up. None of them has ever been told why.

A region is difficulty plus feature flags plus a zone list. Everything else in the game reads
those, so a region is a set of pressures and not a reskin.
"""
import json
import os

PROGRESS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stuff", "progress.json")


# ---------------------------------------------------------------- the ground itself
# Down here "cold" runs negative, which the warmth model already reads as heat.
CRUST_ZONES = [
    {
        "key": "shaft", "name": "The Shaft Head", "at": 0.0, "danger": 0.18, "cold": 0.06,
        "gather": {"scrap": 4, "cord": 3, "cloth": 3, "water": 2, "shard": 2, "branch": 1,
                   "ration": 2},
        "blurb": "A bore going straight down with rungs set into it by something that had "
                 "hands and a plan. The air coming up is warmer than the air going down.",
    },
    {
        "key": "galleries", "name": "The Galleries", "at": 22.0, "danger": 0.40, "cold": 0.02,
        "gather": {"shard": 4, "scrap": 4, "glowmoss": 3, "water": 2, "resin": 2,
                   "coagulant": 1, "hide": 2, "ration": 2, "meat": 1},
        "blurb": "Rooms cut into rock and left furnished. Somebody worked down here for a long "
                 "time and stopped in the middle of a sentence.",
    },
    {
        "key": "roots", "name": "The Root Level", "at": 48.0, "danger": 0.55, "cold": -0.14,
        "gather": {"branch": 5, "resin": 4, "meat": 5, "glowmoss": 3, "cord": 3, "water": 4,
                   "antisepsis": 1, "hide": 2},
        "blurb": "Something grew down here without light and got large about it. The walls are "
                 "root and the root is warm and it moves when you are not looking at it.",
    },
    {
        "key": "thermals", "name": "The Thermals", "at": 74.0, "danger": 0.62, "cold": -0.22,
        "gather": {"scrap": 4, "charcoal": 4, "shard": 3, "water": 1, "stim": 1,
                   "nerveblock": 1, "ration": 1, "meat": 1},
        "blurb": "Vents breathing wet heat in shifts, and standing water that is too hot to "
                 "cross and too wide to go round.",
    },
]

CORE_ZONES = [
    {
        "key": "descent", "name": "The Long Descent", "at": 0.0, "danger": 0.30, "cold": -0.10,
        "gather": {"scrap": 4, "cord": 3, "water": 4, "cloth": 2, "coagulant": 1, "shard": 2,
                   "ration": 2},
        "blurb": "The rungs stop and the rock takes over the job of holding you up, badly. "
                 "Everything below this was made by pressure and not by anybody.",
    },
    {
        "key": "boneyard", "name": "The Boneyard", "at": 20.0, "danger": 0.58, "cold": -0.12,
        "gather": {"shard": 5, "scrap": 3, "hide": 2, "marrow": 1, "antisepsis": 1,
                   "water": 3, "ration": 2, "meat": 2, "stabiliser": 1},
        "blurb": "Other subjects, at the ends of other runs, in the postures they stopped in. "
                 "Some of them are your build. One of them has a chip scar behind the ear.",
    },
    {
        "key": "glassways", "name": "The Glassways", "at": 38.0, "danger": 0.66, "cold": -0.20,
        "gather": {"shard": 6, "scrap": 3, "water": 2, "nerveblock": 1, "stim": 1,
                   "ration": 1, "stabiliser": 1},
        "blurb": "Tunnels lined with something that cooled too fast, holding the shape of the "
                 "last thing that went through them at speed.",
    },
    {
        "key": "furnace", "name": "The Furnace Floor", "at": 56.0, "danger": 0.74, "cold": -0.34,
        "gather": {"charcoal": 5, "scrap": 4, "water": 1, "stabiliser": 2},
        "blurb": "Heat with a direction to it. The floor is hot enough through your pads that "
                 "you start counting steps as a way of not thinking about them.",
    },
    {
        "key": "hollow", "name": "The Hollow", "at": 76.0, "danger": 0.70, "cold": -0.18,
        "gather": {"glowmoss": 4, "water": 5, "meat": 4, "marrow": 1, "stabiliser": 1,
                   "scrap": 2, "ration": 2, "stabiliser": 1},
        "blurb": "A void the size of weather, with its own wind. Nothing here was excavated. "
                 "Something was removed.",
    },
    {
        "key": "cradle", "name": "The Cradle", "at": 96.0, "danger": 0.60, "cold": -0.24,
        "gather": {"scrap": 3, "shard": 2, "stabiliser": 1, "water": 3, "ration": 2},
        "blurb": "The bottom of the world, and it is a made room. Cables the thickness of your "
                 "body converge on something that is still, after all this, faintly lit.",
    },
]


REGIONS = [
    {
        "key": "outside",
        "name": "OUTSIDE",
        "label": "the surface test - walk it to the line",
        "goal": 100.0,
        "goal_kind": "horizon",
        "zones": "outside",
        "order": 0,
        # difficulty dials, read by the systems that already exist
        "danger_mult": 1.00, "drain_mult": 1.00, "crisis_mult": 1.00, "heal_mult": 1.00,
        "complication_mult": 1.00, "link_noise": 1.00,
        # features
        "complications": False,   # the issues system is not switched on up here
        "bags": False,
        "medical_hell": False,
        "escape": True,
        "intel_start": 14.0,
        "brief": ("The surface. One axis, eight zones, a line at the end that somebody drew "
                  "and is waiting behind. Nothing down-well is switched on yet: no "
                  "complications, no bags, and the only medicine is what you can boil or "
                  "crush yourself."),
    },
    {
        "key": "crust",
        "name": "INTO THE CRUST",
        "label": "four layers under it - complications begin",
        "goal": 100.0,
        "goal_kind": "horizon",
        "zones": "crust",
        "order": 1,
        "danger_mult": 1.55, "drain_mult": 1.28, "crisis_mult": 1.45, "heal_mult": 0.88,
        "complication_mult": 1.60, "link_noise": 1.60,
        "complications": True,
        "bags": True,
        "medical_hell": False,
        "escape": False,
        "intel_start": 22.0,
        "brief": ("Under the test. Four layers, warmer as you go, and the complications system "
                  "comes on: wounds acquire opinions of their own and each one has to be "
                  "addressed by name. There is manufactured medicine down here, and you will "
                  "not be able to read the labels at first. You can build a bag."),
    },
    {
        "key": "core",
        "name": "INTO THE CORE",
        "label": "six layers, severe - and a battery at the bottom",
        "goal": 120.0,
        "goal_kind": "battery",
        "zones": "core",
        "order": 2,
        "danger_mult": 1.80, "drain_mult": 1.24, "crisis_mult": 1.60, "heal_mult": 0.78,
        "complication_mult": 2.10, "link_noise": 2.30,
        "complications": True,
        "bags": True,
        "medical_hell": True,
        "escape": False,
        "intel_start": 30.0,
        "brief": ("The bottom. Six layers, severe, and MEDICAL HELL is live: injuries stop "
                  "arriving one at a time and some of what happens down here has no treatment "
                  "at all. It does not end at a line. It ends at a battery, which you are to "
                  "bring back up. You have never been told why, and it is going to ask."),
    },
]

BY_KEY = {r["key"]: r for r in REGIONS}
DEFAULT = "outside"
ORDER = [r["key"] for r in sorted(REGIONS, key=lambda r: r["order"])]


# ---------------------------------------------------------------- progress on disk
def _blank():
    return {"unlocked": [DEFAULT], "beaten": [], "lore": [], "destiny": [], "final": [],
            "carry": {}, "fslot": {}}


# What comes down the hole with you. Finishing a region in normal does not put the subject back
# in a clean room - it goes straight on into the next one carrying what it was carrying and
# wearing what the last act did to it. Stored per subject, because the body is the subject's.
CARRY_KEYS = ("inv", "limbs", "truths", "known_items", "bags", "intel",
              "mood", "will", "chip", "weird", "blood", "pain", "infection",
              "hunger", "thirst", "fatigue", "strain", "warmth", "snap", "phones",
              "lies", "honest", "refusals", "overrides", "requests", "trait_drift")


def store_carry(s):
    """Snapshot the subject at the end of a finished region."""
    d = load_progress()
    snap = {}
    for k in CARRY_KEYS:
        v = getattr(s, k, None)
        if v is not None:
            snap[k] = v
    snap["from_region"] = s.region
    snap["day"] = getattr(s, "day", 1)
    d.setdefault("carry", {})[getattr(s, "subject", "")] = snap
    save_progress(d)
    return snap


def record_win(s, key, verdict, carried):
    """Every finish goes on the board whether or not the body can walk on from it."""
    d = load_progress()
    d.setdefault("wins", []).append({
        "region": getattr(s, "region", ""),
        "destiny": bool(getattr(s, "destiny", False)),
        "subject": getattr(s, "subject", ""),
        "ending": key,
        "verdict": verdict,
        "day": int(getattr(s, "day", 1)),
        "carried": bool(carried),
    })
    d["wins"] = d["wins"][-60:]
    save_progress(d)


def wins():
    return load_progress().get("wins") or []


def wins_lines():
    from . import subjects as SUB
    rows = wins()
    if not rows:
        return ["No region has been finished yet."]
    L = ["FINISHED RUNS", ""]
    for w in rows[-14:]:
        reg = BY_KEY.get(w.get("region"), {}).get("name", w.get("region", "?"))
        sub = SUB.BY_ID.get(w.get("subject"), {}).get("name", w.get("subject", "?"))
        L.append("  %-16s %-18s %-18s day %-3d %s"
                 % (reg + ("/" + DESTINY_NAME if w.get("destiny") else ""),
                    sub, w.get("ending", "?"), w.get("day", 1),
                    "walked on" if w.get("carried") else "ended there"))
    L.append("")
    L.append("'walked on' means that body started the next act. The rest were finishes too -")
    L.append("they just were not free to carry on from, so the next act starts clean.")
    return L


def take_carry(sid):
    return (load_progress().get("carry") or {}).get(sid)


def clear_carry(sid):
    d = load_progress()
    if (d.get("carry") or {}).pop(sid, None) is not None:
        save_progress(d)


def apply_carry(s, snap):
    """Put a finished subject back on its feet at the top of the next act."""
    import copy
    if not snap:
        return []
    for k in CARRY_KEYS:
        if k in snap:
            setattr(s, k, copy.deepcopy(snap[k]))
    s.day = int(snap.get("day", 1))
    # the walk down is not free, and it is not a rest either
    s.fatigue = min(100.0, float(getattr(s, "fatigue", 0.0)) + 8.0)
    s.distance = 0.0
    note = ["YOU DID NOT START AGAIN.",
            "  It is the same body. It is carrying what it was carrying, it is hurt where the "
            "last act hurt it, and it knows what it had worked out.",
            "  Nothing was cleaned up for you and there is no calibration this time - the chip "
            "is already seated and it already works."]
    return note


# The Destiny ruleset. Not a region and not a fourth act - it is a multiplier sat on top of
# whichever region you picked, and it is only offered with a subject that has already walked
# the core. Everything it touches is a dial that already existed.
DESTINY = {
    "danger_mult": 1.45, "drain_mult": 1.22, "crisis_mult": 1.50, "heal_mult": 0.70,
    "complication_mult": 1.75, "link_noise": 2.20,
}
DESTINY_NAME = "DESTINY"

# Destiny is not the same test run harder. The surface act happens somewhere else entirely -
# another rock, no line to walk to, and a house at the end of it instead. The layers under it
# are still layers, just longer.
DESTINY_ZONES = {"outside": "rock", "crust": "warrens", "core": "deep"}
DESTINY_GOAL = {"outside": 140.0, "crust": 110.0, "core": 130.0}
DESTINY_GOAL_KIND = {"outside": "house", "crust": "descent", "core": "chamber"}
DESTINY_BRIEF = {
    "outside": ("Not the surface. Not that planet. The chip comes up in a body lying on bare "
                "rock under a sky the wrong colour, and what it is sent for is a house - said "
                "to be completely safe and completely calm once you are inside the zone. "
                "Nobody recorded who said it. Nobody has been."),
    "crust": ("Not the crust. The cairns on the surface went somewhere, and this is where: six "
              "layers of dug passage under the rock, made by something with hands, and it is "
              "the longest act in the game by a wide margin. Almost none of that length is "
              "danger. It is time - food, wounds, and keeping the thing on the end of the link "
              "willing for a week rather than an afternoon."),
    "core": ("Not the core. Under the warrens the digging stops being a route and starts being "
             "a search, and six layers down there is a room at the end of it with the answer "
             "in it. There is no battery here and nobody is waiting at the top."),
}



# ---------------------------------------------------------------- THE FINAL
# The fourth tier and the last one. It is earned per subject by finishing the bottom of
# DESTINY with that subject, exactly the way Destiny itself is earned by finishing the bottom
# of normal, and like Destiny it is not transferable.
#
# Mechanically it sits on top of Destiny rather than beside it: `on_destiny` stays true, so
# everything Destiny switches on stays switched on, and these multiply again on top. The two
# that go DOWN are deliberate. link_noise collapses because inside the fence the link is
# perfect, and the act is built on that being the frightening part rather than the safe one;
# heal_mult comes up because the act is an hour long and a body that cannot mend anything over
# an hour is not difficulty, it is a clock.
FINAL = {
    "danger_mult": 0.92, "drain_mult": 0.94, "crisis_mult": 0.90, "heal_mult": 1.45,
    "complication_mult": 0.80, "link_noise": 0.08,
}
FINAL_NAME = "THE FINAL"
FINAL_ZONE_KEY = "building"
FINAL_GOAL_KIND = "bench"
FINAL_BRIEF = ("Not a walk and not away. The only direction this body has never been sent is "
               "back, and the building is still running with nobody in it. It starts on the "
               "grass outside the wire with nothing, and every way in is shut, and the way "
               "through is made rather than found. It is long. It saves.")


def on_final(s):
    return bool(getattr(s, "final", False))


def final_open(sid):
    return sid in load_progress().get("final", [])


def any_final():
    return bool(load_progress().get("final"))


def stretch_key(s):
    """Which stretch table this act is on. The Final has its own so that it can never pick up
    the core's 1.8x multipliers by way of sharing a region key with it."""
    if on_final(s):
        return "final"
    return info(s)["key"]


# ---------------------------------------------------------------- the slot
# The Final is the only act in the game that is picked up where it was put down. Nothing else
# needs this because nothing else is long enough to be worth interrupting.
def final_slot(sid):
    return load_progress().get("fslot", {}).get(sid)


def save_final(s, why="checkpoint"):
    """Write the run down. Called on reaching new ground, on `leave`, and after a repair."""
    from . import body as B
    sid = getattr(s, "subject", "")
    if not sid or not on_final(s):
        return None
    # the checkpoint is also where a repaired body is put back down, so it has to be written
    # into the act's own state and not only into the slot on disk
    st = getattr(s, "fstate", None)
    if not isinstance(st, dict):
        st = s.fstate = {}
    st["cp_distance"] = float(s.distance)
    d = load_progress()
    d.setdefault("fslot", {})
    d["fslot"][sid] = {
        "why": why, "turn": s.turn, "distance": float(s.distance),
        "fstate": dict(getattr(s, "fstate", {}) or {}),
        "flags": list(getattr(s, "flags", []) or []),
        "truths": list(s.truths), "intel": float(s.intel),
        "inv": dict(s.inv), "limbs": {k: dict(v) for k, v in s.limbs.items()},
        "phones": dict(getattr(s, "phones", {}) or {}),
        "mood": s.mood, "will": s.will, "chip": s.chip, "weird": s.weird,
        "snap": getattr(s, "snap", 0.0), "lies": getattr(s, "lies", 0),
        "stats": dict(getattr(s, "stats", {}) or {}),
    }
    save_progress(d)
    return d["fslot"][sid]


def apply_final_slot(s, slot):
    """Put a saved Final back on its feet. The body is NOT restored to what it was when the
    run was put down - it comes back rested and fed, because the alternative is a save that
    punishes you for stopping, and this one exists so that stopping is allowed."""
    s.distance = float(slot.get("distance", 0.0))
    s.fstate = dict(slot.get("fstate", {}) or {})
    s.flags = list(slot.get("flags", []) or [])
    s.truths = list(slot.get("truths", []) or [])
    s.intel = float(slot.get("intel", s.intel))
    s.inv = dict(slot.get("inv", {}) or {})
    for k, v in (slot.get("limbs", {}) or {}).items():
        if k in s.limbs:
            s.limbs[k] = dict(v)
    if slot.get("phones"):
        s.phones = dict(slot["phones"])
    for k in ("mood", "will", "chip", "weird", "snap"):
        if k in slot:
            setattr(s, k, slot[k])
    s.lies = int(slot.get("lies", 0))
    s.stats = dict(slot.get("stats", {}) or {})
    st = s.fstate
    st["sweep_at"] = 0
    return ["IT IS STILL WHERE YOU LEFT IT. The link comes up on a body that has been sitting "
            "in the dark in the back of a room in the building for however long you were "
            "gone, and it has not moved, and it has not been found.",
            "  Ground: %s.  Count so far: %d.  Repairs on it: %d."
            % (str(slot.get("why", "")), int(st.get("count", 0)), int(st.get("wear", 0)))]


def clear_final(sid):
    d = load_progress()
    if sid in d.get("fslot", {}):
        del d["fslot"][sid]
        save_progress(d)

def zone_set_key(s):
    """Which zone table this run is walking. Destiny moves the surface act off-world, and
    the Final is not on the planet's tables at all."""
    if on_final(s):
        return FINAL_ZONE_KEY
    reg = info(s)
    if on_destiny(s):
        return DESTINY_ZONES.get(reg["key"], reg["zones"])
    return reg["zones"]


def base_goal(s):
    if on_final(s):
        from . import thebuilding as TB
        return float(TB.BUILDING_GOAL)
    reg = info(s)
    if on_destiny(s):
        return float(DESTINY_GOAL.get(reg["key"], reg["goal"]))
    return float(reg["goal"])


def goal_kind(s):
    if on_final(s):
        return FINAL_GOAL_KIND
    reg = info(s)
    if on_destiny(s):
        return DESTINY_GOAL_KIND.get(reg["key"], reg["goal_kind"])
    return reg["goal_kind"]


def brief(s):
    if on_final(s):
        return FINAL_BRIEF
    reg = info(s)
    if on_destiny(s):
        return DESTINY_BRIEF.get(reg["key"], reg["brief"])
    return reg["brief"]

# Destiny does not just turn the dials up, it makes the ground longer - per layer, so the
# shape of the descent changes and not only its size. One multiplier per zone, in order.
#
# The Galleries is the point of the crust table. On Destiny the second layer is most of the
# act: 156 units of a 330-unit walk, which is longer than the entire normal crust. Nothing
# about it is harder than the layers either side of it. It is just long, and long is its own
# problem - food runs out, wounds have time to go septic, and the thing on the end of the link
# has to be kept willing for days rather than hours.
DESTINY_STRETCH = {
    # Every act Destiny runs is its own place at its own length now, so none of these is a
    # stretched version of a normal one - the multipliers shape the descent inside its own
    # table. The Burrow is the point of the warrens: 65 units of a 185-unit walk, longer on
    # its own than two thirds of the entire normal crust, and nothing in it is harder than the
    # layers either side of it. It is just long, and long is its own problem.
    #
    # These were larger - 262 and 356 - and those numbers read well on paper and were not long
    # in play at all. A well-run body survives somewhere around four to six hundred turns of
    # this, which buys roughly a hundred and ten moves once maintenance is interleaved, and an
    # act needing a hundred and sixty of them simply ends early every time. Length has to sit
    # inside what a careful run can reach or it is never experienced as length.
    "outside": [1.0] * 8,
    "crust": [1.3, 3.6, 1.3, 1.4, 1.3, 1.2],
    "core": [1.8, 1.8, 1.8, 1.9, 1.8, 1.7],
    # the building is written at its real length and is never stretched
    "final": [1.0] * 12,
}


def _stretched(zs, mults, base_goal):
    """Rebuild a zone list with each layer scaled. Returns (zones, goal)."""
    ends = [z["at"] for z in zs[1:]] + [float(base_goal)]
    out, at = [], 0.0
    for i, z in enumerate(zs):
        m = mults[i] if i < len(mults) else 1.0
        span = (ends[i] - z["at"]) * m
        c = dict(z)
        c["at"] = round(at, 2)
        out.append(c)
        at += span
    return out, round(at, 2)


_STRETCH_CACHE = {}


def stretched_zones(key, zs, base_goal):
    """Cached, because zones() is called several times a turn and these never change."""
    hit = _STRETCH_CACHE.get(key)
    if hit is None:
        hit = _STRETCH_CACHE[key] = _stretched(zs, DESTINY_STRETCH.get(key, [1.0] * 12),
                                               base_goal)
    return hit


def load_progress():
    try:
        with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
            d = json.load(f)
        if not isinstance(d, dict) or "unlocked" not in d:
            return _blank()
        d.setdefault("beaten", [])
        d.setdefault("lore", [])
        d.setdefault("destiny", [])
        d.setdefault("final", [])
        d.setdefault("fslot", {})
        if DEFAULT not in d["unlocked"]:
            d["unlocked"].append(DEFAULT)
        return d
    except (OSError, ValueError):
        return _blank()


def save_progress(d):
    os.makedirs(os.path.dirname(PROGRESS_PATH), exist_ok=True)
    try:
        with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=1)
    except OSError:
        pass


def unlocked():
    return load_progress()["unlocked"]


def is_unlocked(key):
    return key in unlocked()


def next_key(key):
    try:
        i = ORDER.index(key)
    except ValueError:
        return None
    return ORDER[i + 1] if i + 1 < len(ORDER) else None


def beat(key, subject=None, destiny=False):
    """Record that a region was finished properly, and open the one below it.

    Finishing the bottom does two more things, both tied to the subject that did it: it opens
    that one's history to be read on the picker, and it opens DESTINY for that one and no
    other. Walking the core is the qualification, and it is not transferable.
    """
    d = load_progress()
    if key not in d["beaten"]:
        d["beaten"].append(key)
    nxt = next_key(key)
    opened = None
    if nxt and nxt not in d["unlocked"]:
        d["unlocked"].append(nxt)
        opened = nxt
    if key == ORDER[-1] and subject:
        if subject not in d["lore"]:
            d["lore"].append(subject)
        if subject not in d["destiny"]:
            d["destiny"].append(subject)
        # and the bottom of DESTINY opens the last tier, on the same terms: that subject,
        # permanently, not transferable.
        if destiny:
            d.setdefault("final", [])
            if subject not in d["final"]:
                d["final"].append(subject)
    save_progress(d)
    return opened


def lore_open(sid):
    return sid in load_progress()["lore"]


def destiny_open(sid):
    return sid in load_progress()["destiny"]


def any_destiny():
    return bool(load_progress()["destiny"])


def on_destiny(s):
    return bool(getattr(s, "destiny", False))


def length_factor(s):
    """How much longer this act is than it was written to be. 1.0 for anything unstretched."""
    if not on_destiny(s):
        return 1.0
    from . import world as W
    base = base_goal(s)
    if base <= 0:
        return 1.0
    return max(1.0, W.goal(s) / base)


def destiny_label(s):
    if on_final(s):
        return "  [%s]" % FINAL_NAME
    return "  [%s]" % DESTINY_NAME if on_destiny(s) else ""


def resolve(text):
    """Accept 'crust', 'into the crust', or an index."""
    t = (text or "").strip().lower()
    for lead in ("into the ", "the "):
        if t.startswith(lead):
            t = t[len(lead):]
    if not t:
        return BY_KEY[DEFAULT]
    if t in BY_KEY:
        return BY_KEY[t]
    if t.isdigit() and 1 <= int(t) <= len(REGIONS):
        return REGIONS[int(t) - 1]
    for k in BY_KEY:
        if k.startswith(t):
            return BY_KEY[k]
    return None


# ---------------------------------------------------------------- reading it off state
def info(s):
    return BY_KEY.get(getattr(s, "region", DEFAULT), BY_KEY[DEFAULT])


def name(s):
    if on_final(s):
        return FINAL_NAME
    return info(s)["name"] + (" / " + DESTINY_NAME if on_destiny(s) else "")


def flag(s, key):
    # Destiny switches on the things the region was holding back. Whatever the act was going
    # to spare you, it does not.
    if on_destiny(s) and key in ("medical_hell", "bags"):
        return True
    return info(s).get(key)


def dial(s, key):
    v = info(s).get(key, 1.0)
    v = v if isinstance(v, (int, float)) else 1.0
    if on_destiny(s) and key in DESTINY:
        v *= DESTINY[key]
    if on_final(s) and key in FINAL:
        v *= FINAL[key]
    return v


def apply_start(s, reg, destiny=False, final=False):
    s.region = reg["key"]
    s.intel = float(reg.get("intel_start", 14.0))
    s.distance = 0.0
    # The Final sits on top of Destiny rather than replacing it, so the Destiny flag stays up
    # and everything it forces on stays forced on. It pins the region to the core because the
    # core's dials are the floor it wants; the zone table it walks is its own either way.
    s.final = bool(final)
    if s.final:
        s.region = ORDER[-1]
        destiny = True
        s.fstate = {}
    s.destiny = bool(destiny)
    if s.destiny:
        # it has done this before, so it does not arrive as ignorant. That is the only
        # concession the ruleset makes.
        s.intel = min(100.0, s.intel + 12.0)
    if s.final:
        # it has walked every act in the game to get here, twice over
        s.intel = min(100.0, s.intel + 10.0)


def roster(current=None):
    """The picker. Says what each act is, because difficulty is not a thing to hide - but
    says nothing about what is down there."""
    un = unlocked()
    L = ["WHERE THE CHIP IS BEING RUN", ""]
    for i, r in enumerate(REGIONS, 1):
        ok = r["key"] in un
        mark = ">>" if r["key"] == (current or DEFAULT) else "  "
        lock = "" if ok else "   [LOCKED - finish the one above it]"
        L.append("%s %d)  %-16s %s%s" % (mark, i, r["name"], r["label"], lock))
    L.append("")
    L.append("Pick with:  .\\run.bat new <region> <subject>      e.g.  .\\run.bat new crust 3")
    L.append("Only OUTSIDE is open to begin with. Finish a region and the next one unlocks and")
    L.append("stays unlocked. Each one is a harder ruleset, not a longer walk.")
    d = load_progress()
    if d["destiny"]:
        from . import subjects as SUB
        who = ", ".join(SUB.BY_ID[x]["name"] for x in d["destiny"] if x in SUB.BY_ID)
        L.append("")
        L.append("MODE      normal        the ruleset above, as written")
        L.append("          %s       every dial again, harder, and nothing held back"
                 % DESTINY_NAME.lower())
        L.append("Add it on the end:  .\\run.bat new core 680 destiny")
        L.append("%s is open to %s, and to nothing else. Walking the core is how it is"
                 % (DESTINY_NAME, who))
        L.append("earned and it is not earned on anybody else's behalf.")
    return "\n".join(L)
