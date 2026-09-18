"""Complications. An injury is an event; an issue is what the injury leaves behind.

Every issue costs something every turn until it is addressed, and every issue prints the
command that addresses it, so the thing playing this is never guessing.
"""
from . import body as B
from . import items as I

# how many separate complications a body can carry at once - see add()
MAX_CONCURRENT = 6


def _per(s, minutes):
    """Hours elapsed, damped by how much longer this act is than it was written to be.

    Every hazard in here ARRIVES per minute. Stretch a region to three times the distance and
    the same journey collects three times the complications, which is not "harder" - it is
    unsurvivable, and it was: Destiny crust killed a subject standing still in 317 turns while
    the walk needs six hundred. Damping by length keeps the hazard per unit of GROUND as
    designed, and leaves the long act's real difficulty where it belongs - keeping something
    fed, watered and willing for three times as long.

    Only ARRIVAL is damped. tick()'s per-turn costs are not: those are the price of leaving a
    condition open, and the effort to close one does not get cheaper on a long walk.
    """
    from . import regions as REG
    return (minutes / 60.0) / (REG.length_factor(s) ** 0.85)

# kind -> label, fix hint, what clears it, description
TYPES = {
    # ------------------------------------------------------------------ MEDICAL HELL
    # Fifteen more, and the shape of the set matters more than any one of them: about two
    # thirds answer to something you can carry, a few answer only to being talked to, and
    # three do not answer to anything at all. Each carries its own per-turn cost in "cost",
    # which tick() applies generically - see the note there.
    "rejection": {
        "label": "TISSUE REJECTION",
        "fix": "use stabiliser",
        "clears": ("use", "apply"),
        "needs": "stabiliser",
        "hell": True,
        "cost": {"pain": 1.6, "infection": 1.3, "mood": -0.8},
        "desc": "it has decided the repaired parts of itself are not itself and has begun "
                "taking them apart",
    },
    "cascade": {
        "label": "ORGAN CASCADE",
        "fix": "use marrow, then rest",
        "clears": ("use", "apply"),
        "needs": "marrow",
        "hell": True,
        "cost": {"blood": -1.2, "strain": 1.8, "fatigue": 1.5},
        "desc": "one thing inside has stopped and the things that depended on it are stopping "
                "in order, politely, one after another",
    },
    "liquefaction": {
        "label": "LIQUEFACTION",
        "fix": "use stabiliser",
        "clears": ("use", "apply"),
        "needs": "stabiliser",
        "hell": True,
        "limb": True,
        "cost": {"pain": 1.9, "limb_hp": -2.2, "blood": -0.6},
        "desc": "the muscle under the hide has stopped being muscle and has started being "
                "something that runs",
    },
    "fusion": {
        "label": "BONE FUSION",
        "fix": "use nerveblock, then tend <limb>",
        "clears": ("use", "apply"),
        "needs": "nerveblock",
        "hell": True,
        "limb": True,
        "cost": {"pain": 1.5, "strain": 1.6},
        "desc": "the joint has begun setting solid in whatever position it was last in",
    },
    "swarm": {
        "label": "SOMETHING LIVING IN IT",
        "fix": "use antisepsis",
        "clears": ("use", "apply"),
        "needs": "antisepsis",
        "hell": True,
        "limb": True,
        "cost": {"infection": 2.4, "pain": 1.0, "mood": -1.0},
        "desc": "the wound is moving on its own and it is not the wound doing it",
    },
    "mirror": {
        "label": "MIRRORED",
        "fix": "recalibrate",
        "clears": ("recalibrate",),
        "hell": True,
        "cost": {"weird": 1.2, "strain": 1.2, "will": -1.0},
        "desc": "the left side is doing what the right side was told and neither of them is "
                "apologising for it",
    },
    "hollowing": {
        "label": "HOLLOWING",
        "fix": "use marrow",
        "clears": ("use", "apply"),
        "needs": "marrow",
        "hell": True,
        "cost": {"strain": 2.0, "pain": 0.9, "blood": -0.5},
        "desc": "the bone is going light and porous and it can feel the difference when it "
                "puts weight on itself",
    },
    "screaming": {
        "label": "IT WILL NOT STOP SCREAMING",
        "fix": "use nerveblock  (reassure buys a little)",
        "clears": ("use", "apply"),
        "needs": "nerveblock",
        "hell": True,
        "cost": {"pain": 2.4, "fatigue": 1.6, "mood": -1.4},
        "desc": "there is no wound making this. Something upstream of the wound has stuck "
                "open and will not close",
    },
    "forgetting": {
        "label": "FORGETTING",
        "fix": "persuade, or answer what it asks",
        "clears": ("persuade", "please", "reason", "say"),
        "hell": True,
        "cost": {"weird": 1.3, "mood": -1.2},
        "desc": "it is losing what it had worked out about itself, in order, oldest first",
    },
    "second": {
        "label": "SECOND HEARTBEAT",
        "fix": "there is no fix for this one",
        "clears": (),
        "hell": True,
        "cost": {"weird": 0.5, "strain": 1.0, "blood": -0.35},
        "desc": "there is a second rhythm in the chest running at a different rate to the "
                "first and nothing in here put it there",
    },
    "rooted": {
        "label": "ROOTED",
        "fix": "tend <limb>  (cut it free)",
        "clears": ("tend", "bind", "treat", "patch"),
        "hell": True,
        "limb": True,
        "cost": {"pain": 1.3, "limb_hp": -1.5, "fatigue": 1.2},
        "desc": "something has grown out of the ground into the wound and is holding on",
    },
    "saturation": {
        "label": "SATURATED",
        "fix": "use coagulant",
        "clears": ("use", "apply"),
        "needs": "coagulant",
        "hell": True,
        "cost": {"blood": -1.5, "strain": 1.0, "warmth": -0.9},
        "desc": "it is full of fluid and the fluid is not blood and it is coming out of "
                "places that are not wounds",
    },
    "delamination": {
        "label": "DELAMINATION",
        "fix": "tend <limb>",
        "clears": ("tend", "bind", "treat", "patch"),
        "hell": True,
        "limb": True,
        "cost": {"pain": 1.2, "infection": 1.4, "limb_hp": -1.3},
        "desc": "the hide has stopped being attached to what is under it and is sliding",
    },
    "static burn": {
        "label": "STATIC BURN",
        "fix": "recalibrate",
        "clears": ("recalibrate",),
        "hell": True,
        "cost": {"weird": 1.0, "pain": 1.5, "chip": -0.9},
        "desc": "the chip is cooking the tissue it is seated in and the tissue is cooking back",
    },
    "wrong count": {
        "label": "WRONG COUNT",
        "fix": "there is no fix for this one",
        "clears": (),
        "hell": True,
        "cost": {"weird": 0.6, "mood": -1.0, "will": -0.7},
        "desc": "it has counted its own limbs twice now and got a different answer each time, "
                "and one of the answers is too high",
    },
    "reopened": {
        "label": "wound reopened",
        "fix": "tend <limb>",
        "clears": ("tend", "bind", "treat", "patch"),
        "desc": "the closed edge of it has split again and it is running orange",
    },
    "bone shard": {
        "label": "bone shard",
        "fix": "tend <limb> (needs a splint)",
        "clears": ("tend", "bind", "treat", "patch"),
        "needs": "splint",
        "desc": "something broken inside is grinding on something else every time it moves",
    },
    "dead nerve": {
        "label": "dead nerve",
        "fix": "use salve",
        "clears": ("use", "apply"),
        "needs": "salve",
        "desc": "the limb has gone numb and answers late, or not at all",
    },
    "ash lung": {
        "label": "ash lung",
        "fix": "rest 3",
        "clears": ("rest", "camp", "sleep"),
        "desc": "it cannot get a clean breath and coughs grey between steps",
    },
    "phantom": {
        "label": "phantom limb",
        "fix": "reassure",
        "clears": ("reassure",),
        "desc": "the part that is gone keeps sending pain and instructions from nowhere",
    },
    "fever": {
        "label": "fever",
        "fix": "use salve, then camp",
        "clears": ("use", "camp", "sleep"),
        "needs": "salve",
        "desc": "it is running hot and the heat is winning",
    },
    "chip fault": {
        "label": "chip fault",
        "fix": "recalibrate",
        "clears": ("recalibrate",),
        "desc": "orders arrive doubled, or arrive as something else entirely",
    },
    # ---------------------------------------------------------- what is missing
    # Losing a limb used to be priced entirely in move_cost and carry_cap - a quiet tax the
    # chip was never told about. These are the same fact said out loud, and both of them name
    # the only thing that answers them, which is a strut.
    "stump": {
        "label": "STANDING ON A STUMP",
        "fix": "graft <limb>  (needs a strut)",
        "clears": ("graft",),
        "needs": "strut",
        "limb": True,
        "cost": {"pain": 1.4, "strain": 1.9, "fatigue": 1.1, "mood": -0.8},
        "desc": "it is putting weight on the end of a leg that is not there and the end of it "
                "is taking that weight anyway",
    },
    "handless": {
        "label": "NOTHING TO DO IT WITH",
        "fix": "graft left arm / graft right arm  (needs a strut)",
        "clears": ("graft",),
        "needs": "strut",
        "cost": {"hunger": 1.3, "thirst": 1.1, "mood": -1.3, "strain": 0.8},
        "desc": "it has no arm left that answers, so it cannot dress itself, cannot hold "
                "water, and gets at food with its face or not at all",
    },
    "cold shock": {
        "label": "cold shock",
        "fix": "use torch / shelter",
        "clears": ("use", "shelter", "build", "camp"),
        "desc": "it cannot stop shaking and its hands have stopped closing properly",
    },

    # ------------------------------------------------------------ MEDICAL HELL
    # Core only. These do not arrive one at a time, several of them have no treatment at all,
    # and the ones that do want manufactured medicine you have to be able to read first.
    "unravelling": {
        "label": "DESTROYED DNA",
        "fix": "use stabiliser  (nothing else touches it)",
        "clears": ("use", "apply"),
        "needs": "stabiliser",
        "hell": True,
        "desc": "it is not holding its own pattern any more - the wrong tissue is growing in "
                "the wrong places and none of it is stopping",
    },
    "denial": {
        "label": "DENIAL",
        "fix": "persuade, or answer what it asks  (reassure will not reach it)",
        "clears": ("persuade", "please", "reason", "say"),
        "hell": True,
        "desc": "it has stopped accepting that any of this is happening to it, and an order "
                "that contradicts that does not arrive at all",
    },
    "crush": {
        "label": "CRUSH INJURY",
        "fix": "use marrow, then rest",
        "clears": ("use", "apply"),
        "needs": "marrow",
        "hell": True,
        "desc": "something came down on it and the limb is the wrong shape along its whole length",
    },
    "cooked": {
        "label": "COOKED THROUGH",
        "fix": "use antisepsis, then camp",
        "clears": ("use", "apply"),
        "needs": "antisepsis",
        "hell": True,
        "desc": "the heat got in past the skin and went on working after it stopped touching it",
    },
    "haemorrhage": {
        "label": "INTERNAL HAEMORRHAGE",
        "fix": "use coagulant  (dressing will not reach this)",
        "clears": ("use", "apply"),
        "needs": "coagulant",
        "hell": True,
        "desc": "it is bleeding somewhere you cannot put a hand on, and the orange is going "
                "inward instead of out",
    },
    "seizure": {
        "label": "SEIZURE CLUSTER",
        "fix": "use nerveblock, or rest 4",
        "clears": ("use", "apply", "rest", "camp"),
        "needs": "nerveblock",
        "hell": True,
        "desc": "the whole body fires at once, at intervals, and each one costs it more than "
                "the last",
    },
    "blind": {
        "label": "BLINDED",
        "fix": "there is no fix - rest, and work around it",
        "clears": ("rest", "camp", "sleep"),
        "hell": True,
        "desc": "the orange has gone out of its eyes and nothing is coming in through them",
    },
}


def add(s, kind, limb=None, quiet=False):
    from . import regions as REG
    if not REG.flag(s, "complications"):
        return None            # the system is not switched on up on the surface
    t = TYPES.get(kind)
    if not t:
        return None
    for ex in s.issues:
        if ex["kind"] == kind and ex.get("limb") == limb:
            return None
    # There is a limit to how many separate things can be wrong before one of them finishes
    # it, and without a limit this runs away: hell()'s own rate scales with how many issues
    # are already open, so every arrival makes the next one likelier. Long runs were ending
    # with eight concurrent conditions and no path back. Two of these can never be cleared,
    # and them occupying a slot for good is the intended shape, not a bug.
    if len(s.issues) >= MAX_CONCURRENT:
        return None
    it = {"kind": kind, "limb": limb, "label": t["label"], "fix": t["fix"], "age": 0}
    if limb and "<limb>" in t["fix"]:
        it["fix"] = t["fix"].replace("<limb>", limb)
    s.issues.append(it)
    if not quiet:
        s.note("ISSUE: %s%s - %s" % (t["label"], (" (%s)" % limb) if limb else "", t["desc"]))
    return it


def describe(s, it):
    t = TYPES[it["kind"]]
    where = (" [%s]" % it["limb"]) if it.get("limb") else ""
    return "  - %s%s: %s  ->  %s" % (it["label"], where, t["desc"], it["fix"])


def lines(s):
    return [describe(s, it) for it in s.issues]


def _worst_limb(s, prefer_open=True):
    order = ["mangled", "gashed", "broken", "bruised", "intact", "lost"]
    cands = sorted(s.limbs, key=lambda n: order.index(s.limbs[n]["state"]))
    return cands[0] if cands else "tail"


def clear_kind(s, kind, limb=None):
    """Remove an issue outright, whatever the normal fix would have been. Returns True if
    something was actually there. Pass a limb to clear only the one on that limb."""
    before = len(s.issues)
    s.issues = [i for i in s.issues
                if i["kind"] != kind or (limb is not None and i.get("limb") != limb)]
    gone = len(s.issues) < before
    if gone:
        s.stats["issues_fixed"] = s.stats.get("issues_fixed", 0) + 1
    return gone


def materialise(s):
    """Turn damage markers into real issues. Returns feedback lines."""
    from . import regions as REG
    if not REG.flag(s, "complications"):
        s.pending_issues = []
        return []
    out = []
    while s.pending_issues:
        kind = s.pending_issues.pop(0)
        limb = None
        if kind in ("reopened", "bone shard", "dead nerve"):
            limb = _worst_limb(s)
        it = add(s, kind, limb)
        if it:
            out.append("NEW ISSUE: %s%s - %s"
                       % (it["label"], (" in the %s" % limb) if limb else "", it["fix"]))
    return out


def roll(s, minutes):
    """Chance of new complications, driven by what is already wrong."""
    from . import regions as REG
    if not REG.flag(s, "complications"):
        return
    per = _per(s, minutes) * REG.dial(s, "complication_mult")
    r = s.rng
    for n, L in s.limbs.items():
        if L["state"] in ("gashed", "mangled") and not L["bound"]:
            if r.random() < 0.05 * per:
                add(s, "reopened", n)
        if L["state"] == "broken" and r.random() < 0.04 * per:
            add(s, "bone shard", n)
        if L["state"] == "lost" and r.random() < 0.03 * per:
            add(s, "phantom", n)
    # missing structure, rather than a wound. These arrive quickly, because the body notices
    # immediately, and they clear the moment something is lashed on in place of what is gone.
    for n in B.LEGS:
        if s.limbs[n]["state"] == "lost" and not s.limbs[n]["strut"]:
            if r.random() < 0.55 * per:
                add(s, "stump", n)
    if B.arms_usable(s) == 0 and r.random() < 0.70 * per:
        add(s, "handless")
    if s.infection > 55 and r.random() < 0.10 * per:
        add(s, "fever")
    if s.warmth < 22 and r.random() < 0.12 * per:
        add(s, "cold shock")
    if s.chip < 30 and r.random() < 0.07 * per:
        add(s, "chip fault")


def tick(s, minutes):
    """What untreated issues cost you. Called from the turn loop, not the clock."""
    if not s.issues:
        return []
    warn = []
    # ARRIVAL is damped in _per() so a long act does not collect three times the conditions.
    # The per-turn COST is damped too, but far more gently and for a different reason: with
    # medical hell on and six concurrent conditions, an hour of the stretched crust cost 7
    # infection an hour and killed the body at unit 38 of a 262-unit walk. The act was never
    # long in play - it just ended early. Half the exponent keeps a long act harder in total,
    # because more of these arrive over more hours, without making any single hour lethal.
    from . import regions as REG
    per = (minutes / 60.0) / (REG.length_factor(s) ** 0.5)
    for it in s.issues:
        it["age"] = it.get("age", 0) + 1
        k = it["kind"]
        limb = it.get("limb")
        if k == "reopened" and limb:
            L = s.limbs[limb]
            L["bleed"] = max(L["bleed"], 0.07)
            L["bound"] = False
        elif k == "bone shard" and limb:
            s.pain = B.clamp(s.pain + 1.6 * per)
            s.limbs[limb]["hp"] = B.clamp(s.limbs[limb]["hp"] - 0.8 * per)
        elif k == "dead nerve":
            s.strain = B.clamp(s.strain + 1.2 * per)
        elif k == "ash lung":
            s.strain = B.clamp(s.strain + 2.0 * per)
            s.fatigue = B.clamp(s.fatigue + 1.4 * per)
        elif k == "phantom":
            s.mood = B.clamp(s.mood - 1.5 * per)
            s.pain = B.clamp(s.pain + 0.8 * per)
        elif k == "fever":
            s.infection = B.clamp(s.infection + 1.8 * per)
            s.fatigue = B.clamp(s.fatigue + 1.2 * per)
        elif k == "chip fault":
            s.weird = B.clamp(s.weird + 1.6 * per)
        elif k == "cold shock":
            s.warmth = B.clamp(s.warmth - 1.5 * per)
            s.strain = B.clamp(s.strain + 1.0 * per)
        elif k == "unravelling":
            s.weird = B.clamp(s.weird + 2.0 * per)
            s.blood = B.clamp(s.blood - 0.9 * per)
            s.pain = B.clamp(s.pain + 1.4 * per)
        elif k == "denial":
            s.mood = B.clamp(s.mood - 2.4 * per)
            s.will = B.clamp(s.will - 3.0 * per)
            s.weird = B.clamp(s.weird + 1.2 * per)
        elif k == "crush" and limb:
            s.pain = B.clamp(s.pain + 3.0 * per)
            s.limbs[limb]["hp"] = B.clamp(s.limbs[limb]["hp"] - 2.6 * per)
            s.strain = B.clamp(s.strain + 1.6 * per)
        elif k == "cooked":
            s.infection = B.clamp(s.infection + 3.2 * per)
            s.pain = B.clamp(s.pain + 1.8 * per)
        elif k == "haemorrhage":
            s.blood = B.clamp(s.blood - 2.6 * per)
            s.pain = B.clamp(s.pain + 1.2 * per)
        elif k == "seizure":
            s.strain = B.clamp(s.strain + 3.4 * per)
            s.fatigue = B.clamp(s.fatigue + 2.6 * per)
            s.weird = B.clamp(s.weird + 1.4 * per)
        elif k == "blind":
            s.weird = B.clamp(s.weird + 1.0 * per)
            s.mood = B.clamp(s.mood - 1.2 * per)
        else:
            # everything added after the original set carries its own numbers in "cost", so
            # the chain above does not have to grow a branch per condition. Signed: positive
            # raises the stat, negative lowers it, and "limb_hp" eats the limb it is on.
            for stat, amt in (TYPES[k].get("cost") or {}).items():
                if stat == "limb_hp":
                    if limb:
                        s.limbs[limb]["hp"] = B.clamp(s.limbs[limb]["hp"] + amt * per)
                    continue
                setattr(s, stat, B.clamp(getattr(s, stat, 0.0) + amt * per))
        if it["age"] == 6:
            warn.append("ISSUE UNADDRESSED: %s is getting worse. %s" % (it["label"], it["fix"]))
    return warn


def resolve(s, verb, arg=""):
    """Clear whatever the action just dealt with. Returns feedback lines."""
    out = []
    for it in list(s.issues):
        t = TYPES[it["kind"]]
        if verb not in t["clears"]:
            continue
        need = t.get("needs")
        if need and not I.has(s, need) and verb in ("use", "apply", "tend", "bind"):
            continue
        if it.get("limb") and verb in ("tend", "bind", "treat", "patch", "graft"):
            if arg and arg not in it["limb"] and it["limb"] not in arg:
                continue
        if it["kind"] == "ash lung" and verb == "rest":
            pass
        s.issues.remove(it)
        s.stats["issues_fixed"] = s.stats.get("issues_fixed", 0) + 1
        out.append("ISSUE CLEARED: %s." % it["label"])
        if it["kind"] == "reopened" and it.get("limb"):
            B.bind(s, it["limb"], 1.0)
    return out


# ====================================================================== MEDICAL HELL
HELL_KINDS = [k for k, v in TYPES.items() if v.get("hell")]
LIMB_HELL = tuple(["crush", "cooked", "unravelling"]
                 + [k for k, v in TYPES.items() if v.get("limb")])


def deep_complications(s, minutes):
    """Crust-and-below: complications that want manufactured medicine.

    This is the crust's own hazard and the reason intelligence matters there. Nothing you can
    boil out of moss touches these two - they need a packet or a tube you probably cannot read
    the label on yet.
    """
    from . import regions as REG
    if not REG.flag(s, "complications") or s.over:
        return []
    if REG.flag(s, "medical_hell"):
        return []               # the core has its own, worse version of this
    r = s.rng
    per = _per(s, minutes)
    out = []
    hot = max(0.0, (s.warmth - 84.0) / 16.0)
    if hot > 0 and r.random() < 0.05 * per * (0.5 + hot):
        if add(s, "cooked", None, quiet=True) is not None:
            out.append("COMPLICATION: %s - %s" % (TYPES["cooked"]["label"],
                                                  TYPES["cooked"]["desc"]))
    bleeding = B.bleed_rate(s) > 0.04 or s.blood < 70
    if bleeding and r.random() < 0.045 * per:
        if add(s, "haemorrhage", None, quiet=True) is not None:
            out.append("COMPLICATION: %s - %s" % (TYPES["haemorrhage"]["label"],
                                                 TYPES["haemorrhage"]["desc"]))
    return out


def hell(s, minutes):
    """Core only. Injuries stop arriving politely.

    The difference from roll() is not the rate, it is the shape: when this fires it fires in
    a cluster, it does not care whether you have dealt with the last one, and several of the
    things it can hand you have no treatment in the game at all.
    """
    from . import regions as REG
    if not REG.flag(s, "medical_hell") or s.over:
        return []
    r = s.rng
    per = _per(s, minutes)
    # it feeds on how badly the run is already going
    pressure = (s.pain * 0.006 + s.infection * 0.008 + s.weird * 0.006
                + (100.0 - s.blood) * 0.006 + B.limbs_lost(s) * 0.05
                + len(s.issues) * 0.03)
    chance = (0.030 + pressure * 0.055) * per
    if r.random() > chance:
        return []
    out = []
    # a cluster, weighted small but with a real tail
    # These odds are tuned against how often the draws COLLIDE, because add() dedupes on
    # (kind, limb). With seven conditions in the pool a three-draw cluster usually collapsed
    # into one or two; with twenty-two it almost never collides, so the same numbers would
    # silently be handing out twice the load. Do not raise these when adding conditions.
    n = 1 + (1 if r.random() < 0.28 else 0) + (1 if r.random() < 0.08 else 0)
    # weighted: the ones with a treatment are the common ones. The ones without are the
    # tail, because a run decided by an untreatable roll is not a run anybody played.
    WEIGHT = {
        # treatable with something you can carry - the bulk of it
        "crush": 5, "cooked": 5, "haemorrhage": 5, "seizure": 4,
        "swarm": 4, "delamination": 4, "rooted": 4, "saturation": 3,
        "hollowing": 3, "fusion": 3, "screaming": 3, "rejection": 3,
        "cascade": 2, "liquefaction": 2,
        # answers only to the chip or to being talked to
        "mirror": 3, "static burn": 3, "forgetting": 2, "denial": 2,
        # no treatment exists. The tail, deliberately thin
        "unravelling": 2, "second": 1, "wrong count": 1, "blind": 1,
    }
    pool = [k for k in HELL_KINDS if not any(i["kind"] == k for i in s.issues)]
    if pool:
        weights = [WEIGHT.get(k, 3) for k in pool]
        picked, seen = [], set()
        while pool and len(picked) < 3:
            k = r.choices(pool, weights=weights, k=1)[0]
            i = pool.index(k)
            pool.pop(i)
            weights.pop(i)
            if k not in seen:
                seen.add(k)
                picked.append(k)
        pool = picked
    added = []
    for kind in pool[:n]:
        limb = None
        if kind in LIMB_HELL:
            cands = [x for x in s.limbs if s.limbs[x]["state"] != "lost"]
            limb = r.choice(cands) if cands else None
        line = add(s, kind, limb, quiet=True)
        if line is not None or any(i["kind"] == kind for i in s.issues):
            added.append(TYPES[kind]["label"] + (" [%s]" % limb if limb else ""))
        if kind in LIMB_HELL and limb:
            B.hurt(s, limb, r.uniform(14, 30), "crush")
    if not added:
        return []
    s.stats["hell"] = s.stats.get("hell", 0) + 1
    head = ("*** IT IS COMING APART ***  %s" % ", ".join(added))
    out.append(head)
    out.append("  This is what the core does. Some of it you can treat. Some of it you cannot.")
    s.pending_voice.append("hell")
    return out
