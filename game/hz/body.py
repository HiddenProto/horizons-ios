"""The body: injuries, bleeding (orange), strain, sleep, temperature, and how it fails."""
from . import regions as REG
from . import subjects as SUB
from .state import LIMB_ORDER, LIMB_STATES

ARMS = ["left arm", "right arm"]
LEGS = ["left leg", "right leg"]
OPEN_WOUNDS = ("gashed", "mangled", "lost")

# per-minute drift while awake
R_FATIGUE = 0.062
R_HUNGER = 0.030
R_THIRST = 0.055
R_WEIRD = 0.009

# it heals wrong and fast - this is the mechanical half of that fact
R_KNIT = 0.045          # limb hp per minute
R_CLOSE_BOUND = 0.0022  # bleed closed per minute when bound
R_CLOSE_OPEN = 0.0006   # bleed closed per minute when left open
R_BLOOD = 0.030         # blood replaced per minute once nothing is leaking


# will.py registers itself here, so mood/will answer to the clock without a circular import
MOOD_HOOK = None


def clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


# ---------------------------------------------------------------- capability
def usable(s, limb):
    st = s.limbs[limb]["state"]
    if st == "lost":
        return s.limbs[limb]["strut"]
    return st != "mangled"


def arms_usable(s):
    return sum(1 for a in ARMS if usable(s, a))


def legs_usable(s):
    return sum(1 for a in LEGS if usable(s, a))


def limbs_lost(s):
    return sum(1 for n in LIMB_ORDER if s.limbs[n]["state"] == "lost")


def can_walk(s):
    return legs_usable(s) >= 1


def can_run(s):
    return legs_usable(s) == 2 and s.strain < 82 and s.pain < 70


def can_craft(s):
    return arms_usable(s) >= 1


def can_climb(s):
    return arms_usable(s) >= 2 and legs_usable(s) >= 1


def carry_cap(s):
    # a built bag is the only way past what two hands can hold - and a sled is the other way,
    # which costs you speed instead of nothing
    from . import items as I
    return (8 + 4 * arms_usable(s) + 7 * int(getattr(s, "bags", 0) or 0)
            + int(I.worn_num(s, "carry", add=True))
            + int(SUB.trait(s, "carry_bonus")))


def load_of(s):
    return sum(s.inv.values())


def bleed_rate(s):
    """blood lost per minute"""
    # a hole through the middle counts. Without this the body reads as "not leaking",
    # stops warning about it, and quietly replaces the blood it is losing.
    from . import mortal as _MO
    _ch = getattr(s, "chest", None)
    _extra = float(_ch.get("bleed", 0.0)) if isinstance(_ch, dict) else 0.0
    total = 0.0
    for n in LIMB_ORDER:
        L = s.limbs[n]
        if L["bleed"] > 0:
            r = L["bleed"]
            if L["bound"]:
                r *= 0.22
            total += r
    return (total if total > 0.004 else 0.0) + _extra


# hp needed to climb out of a state, and where it climbs to
_RECOVER = {"mangled": (35.0, "broken"), "broken": (70.0, "bruised"),
            "gashed": (70.0, "bruised"), "bruised": (96.0, "intact")}


def knit(s, minutes=1.0):
    """Self-repair. Wounds close, limbs come back - slowly, and never a lost one."""
    fed = s.hunger < 82 and s.thirst < 82
    rate = R_KNIT * (1.0 if fed else 0.2) * SUB.trait(s, "heal_mult")
    if s.eff("salved"):
        rate *= 1.6
    if s.infection > 50:
        rate *= 0.3
    for n in LIMB_ORDER:
        L = s.limbs[n]
        if L["bleed"] > 0:
            L["bleed"] -= (R_CLOSE_BOUND if L["bound"] else R_CLOSE_OPEN) * minutes
            if L["bleed"] < 0.006:
                L["bleed"] = 0.0
                if L["state"] not in OPEN_WOUNDS:
                    L["bound"] = False      # still open? the dressing stays on
        if L["state"] == "lost":
            continue
        L["hp"] = clamp(L["hp"] + rate * minutes)
        step = _RECOVER.get(L["state"])
        if step and L["bleed"] == 0.0 and L["hp"] >= step[0]:
            L["state"] = step[1]
            if L["state"] not in OPEN_WOUNDS:
                L["bound"] = False


def move_cost(s):
    """(distance units per 'go', minutes it takes)"""
    legs = legs_usable(s)
    if legs == 2:
        step, mins = 2.2, 26
    elif legs == 1:
        step, mins = 1.2, 40
    else:
        step, mins = 0.55, 60          # crawling on the arms
    for leg in LEGS:
        if s.limbs[leg]["state"] in ("broken", "gashed"):
            step *= 0.8
            mins += 5
    if arms_usable(s) == 0:
        step *= 0.8
    # pain and strain take the pace off - unless it is one of the ones that does not
    # stop. That is not toughness, and world.advance charges it for the difference.
    _push = SUB.trait(s, "pushes")
    if s.eff("clarity"):
        _push = 1.0        # for the length of the window it is not feeling any of it
    if s.eff("burning") or s.eff("blocked"):
        _push = max(_push, 0.85)   # it is not being told what the leg is doing
    step *= clamp(1.15 - (s.pain / 200.0) * (1.0 - 0.78 * _push)
                  - (s.strain / 260.0) * (1.0 - 0.45 * _push), 0.35, 1.15)
    step *= SUB.trait(s, "speed")
    from . import items as I
    step *= I.worn_num(s, "step")          # a sled is bought with pace
    if s.eff("rested"):
        step *= 1.12
    if s.eff("burning"):
        step *= 1.18
    cap = carry_cap(s)
    over = load_of(s) - cap
    if over > 0:
        # the penalty scales with how badly overloaded, so hoarding cannot be free
        ratio = over / float(cap)
        step *= max(0.28, 0.85 - 0.45 * ratio)
        mins += int(6 + 8 * min(2.0, ratio))
    return round(step, 2), int(mins)


# ---------------------------------------------------------------- damage
def hurt(s, limb, amount, kind="blunt"):
    """Escalate a limb's state. Returns a plain-language line."""
    L = s.limbs[limb]
    if L["state"] == "lost":
        return "There is nothing left of your %s to hurt." % limb
    # some of them have been rebuilt harder than they started. A severing is a severing -
    # plate does not help you once the thing is already off.
    if kind != "sever":
        amount *= SUB.trait(s, "armor")
    from . import items as I
    if kind != "sever" and limb in LEGS:
        amount *= 1.0 - I.worn_num(s, "leg_soak", add=True)
    if kind != "sever" and limb in ARMS:
        amount *= 1.0 - I.worn_num(s, "hit_soak", add=True)
    # a body that cannot feel it does not pull away from it, and takes more of it
    if s.eff("blocked"):
        amount *= 1.22
    # directional armour comes off the top, and only where it actually sits
    from . import phones as PH
    if kind != "sever":
        amount, _ph = PH.soak(s, limb, amount)
        for ln in _ph:
            s.feedback.append(ln)
    L["hp"] = clamp(L["hp"] - amount)
    s.pain = clamp(s.pain + amount * 0.55)
    s.strain = clamp(s.strain + amount * 0.18)

    old = L["state"]
    if L["hp"] <= 0:
        newst = "lost" if kind == "sever" else "mangled"
    elif L["hp"] < 22:
        newst = "mangled"
    elif L["hp"] < 45:
        newst = "broken" if kind in ("blunt", "crush", "fall") else "gashed"
    elif L["hp"] < 74:
        newst = "gashed" if kind in ("cut", "bite", "burn", "sever") else "bruised"
    else:
        newst = "bruised"
    if LIMB_STATES.index(newst) > LIMB_STATES.index(old):
        L["state"] = newst
        L["bound"] = False
    if kind == "sever":
        L["state"] = "lost"
        L["hp"] = 0.0
        L["strut"] = False
        s.stats["limbs_lost"] = s.stats.get("limbs_lost", 0) + 1

    if L["state"] in OPEN_WOUNDS:
        base = {"gashed": 0.09, "mangled": 0.20, "lost": 0.34}[L["state"]]
        if kind == "burn":
            base *= 0.5
        L["bleed"] = max(L["bleed"], base)
    if kind == "burn":
        s.pain = clamp(s.pain + 6)

    s.pending_voice.append("sever" if L["state"] == "lost" else "hurt")
    word = {"lost": "torn away", "mangled": "ruined", "broken": "broken",
            "gashed": "split open", "bruised": "bruised"}[L["state"]]
    line = "Your %s is %s." % (limb, word)
    if L["bleed"] > 0:
        line += " Orange runs out of it, too bright against the ground."
    s.note(line)
    return line


def sever(s, limb):
    # plate through the hide does not make a thing unkillable, but it does mean the cable
    # sometimes stops on something that will not part.
    a = SUB.trait(s, "armor")
    if a < 1.0 and s.rng.random() < (1.0 - a) * 0.80:
        out = hurt(s, limb, 999, "crush")
        return out + " It did not come off. Something under the hide would not part."
    return hurt(s, limb, 999, "sever")


def bind(s, limb, quality=1.0):
    L = s.limbs[limb]
    if L["bleed"] <= 0 and L["state"] not in OPEN_WOUNDS and L["state"] != "broken":
        return "Your %s does not need binding." % limb
    if L["bleed"] <= 0 and L["state"] in OPEN_WOUNDS:
        L["bound"] = True
        s.pain = clamp(s.pain - 3 * quality)
        return ("You dress your %s. It had stopped running on its own, but it is still open, "
                "and open is what the heat gets in through." % limb)
    L["bound"] = True
    L["bleed"] *= max(0.0, 1.0 - 0.55 * quality)
    if L["bleed"] < 0.02:
        L["bleed"] = 0.0
    s.pain = clamp(s.pain - 7 * quality)
    return "You bind your %s. The orange slows to a seep." % limb


def graft_strut(s, limb):
    L = s.limbs[limb]
    if L["state"] != "lost":
        return "Your %s is still attached. A strut would only get in the way." % limb
    L["strut"] = True
    s.pain = clamp(s.pain + 10)
    # a strut is the answer to both of the missing-structure conditions, so fitting one has
    # to clear them outright rather than wait for the generic resolver to notice
    from . import issues as ISS
    if limb in LEGS:
        # only the leg that just got one. A strut on an arm does not answer for the other side
        ISS.clear_kind(s, "stump", limb)
    if arms_usable(s) > 0:
        ISS.clear_kind(s, "handless")
    return ("You lash the strut to the stump of your %s and cinch it down. "
            "It answers, badly, when you ask it to move." % limb)


# ---------------------------------------------------------------- time
def tick(s, minutes, exertion=1.0, resting=False, cold=0.0):
    # a hole through the middle is not a limb and does not knit. It drains until it
    # is packed, and packed only slows it.
    from . import mortal as MO
    MO.chest_tick(s, minutes)
    minutes = int(minutes)
    for _ in range(minutes):
        if resting:
            s.fatigue = clamp(s.fatigue - 0.16)
            s.strain = clamp(s.strain - 0.09)
            s.pain = clamp(s.pain - 0.03)
        else:
            s.fatigue = clamp(s.fatigue + R_FATIGUE * (0.7 + 0.5 * exertion))
            from . import items as I
            s.strain = clamp(s.strain + 0.021 * exertion * SUB.trait(s, "strain_mult")
                             * I.worn_num(s, "strain"))
            s.pain = clamp(s.pain - 0.012 + 0.004 * exertion)
        # the borrowed turns: it is entirely present and it is not feeling any of this. The
        # damage underneath goes on exactly as it was - only the experience of it stops.
        if s.eff("clarity"):
            s.pain = clamp(s.pain - 0.06)
        dr = REG.dial(s, "drain_mult")
        lf = REG.length_factor(s)      # >1 only on a stretched act; see the notes below
        if s.warmth > 84:
            over = (s.warmth - 84) / 16.0
            s.thirst = clamp(s.thirst + 0.055 * over * dr)
            s.strain = clamp(s.strain + 0.020 * over)
            s.fatigue = clamp(s.fatigue + 0.015 * over)
        # heat load: it takes sustained overheating to kill, and it sheds once you cool off
        h = getattr(s, "heat", 0.0) or 0.0
        # Same trap as wrongness: this climbs per minute toward a fixed cap, and shedding it
        # does not get faster on a longer act. A stretched Furnace Floor boiled every run.
        # Damp what goes in, never what comes out - getting off the hot ground must still work.
        hl = lf ** 0.75
        if s.warmth > 90:
            s.heat = clamp(h + 0.055 * ((s.warmth - 90) / 10.0 + 0.35) / hl)
        elif s.warmth > 78:
            s.heat = clamp(h + 0.006 / hl)
        else:
            s.heat = clamp(h - 0.075)
        ap = SUB.trait(s, "appetite")
        s.hunger = clamp(s.hunger + R_HUNGER * (0.75 if resting else 1.0) * dr * ap)
        s.thirst = clamp(s.thirst + R_THIRST * (0.8 if resting else 1.0) * dr * ap)

        # What is missing costs something every minute, everywhere, including up on the
        # surface where the complications system is switched off entirely. A leg that is not
        # there is worked around by the rest of the body; no arm that answers means it cannot
        # feed or water itself properly and loses most of what it tries to take.
        bare = sum(1 for n in LEGS
                   if s.limbs[n]["state"] == "lost" and not s.limbs[n]["strut"])
        if bare:
            s.strain = clamp(s.strain + 0.020 * bare * (0.4 if resting else 1.0))
            s.pain = clamp(s.pain + 0.008 * bare * (0.3 if resting else 1.0))
        if arms_usable(s) == 0:
            s.hunger = clamp(s.hunger + 0.014)
            s.thirst = clamp(s.thirst + 0.012)

        wr = R_WEIRD * (1.9 if s.night else 1.0)
        if s.eff("static"):
            wr *= 3.0
        # One of them has never had a thought arrive from anywhere else, so it has no second
        # opinion to check the link against. A degraded link is not an inconvenience to 4400.
        # It is the experience of becoming untrue, and it is the thing that kills it.
        dis = SUB.trait(s, "dissolves")
        if dis > 0:
            wr *= 1.0 + dis * 2.0 * (1.0 - s.chip / 100.0)
        # Wrongness accrues per minute, and recalibrate removes a fixed amount - so on an act
        # that is three times longer, three times as much of it arrives and none of the cure
        # scales. Left alone that turns a long region into a wrongness race and nothing else.
        # Damp it by the length, but not all the way: it is still relatively harsher.
        if lf > 1.0:
            wr /= lf ** 0.75
        s.weird = clamp(s.weird + wr)

        br = bleed_rate(s)
        if br > 0:
            s.blood = clamp(s.blood - br)
        elif s.hunger < 78 and s.thirst < 78:
            s.blood = clamp(s.blood + R_BLOOD * (1.6 if resting else 1.0))
        knit(s, 1.6 if resting else 1.0)

        open_count = sum(1 for n in LIMB_ORDER
                         if s.limbs[n]["state"] in OPEN_WOUNDS
                         and not s.limbs[n]["bound"])
        if open_count:
            from . import items as I
            s.infection = clamp(s.infection
                                + 0.016 * open_count * I.worn_num(s, "infection"))
        elif s.eff("salved"):
            s.infection = clamp(s.infection - 0.05)

        # warmth chases a target set by the ground you are on and what you have arranged
        tgt = 70.0 - 260.0 * cold
        if s.night:
            tgt -= 14.0
        if s.eff("fire"):
            tgt += 26.0
        if s.eff("sheltered"):
            tgt += 14.0
        from . import items as I
        tgt += I.worn_num(s, "warmth", add=True)
        tgt = clamp(tgt, 0.0, 95.0)
        s.warmth = clamp(s.warmth + (tgt - s.warmth) * 0.004)
        if s.warmth < 12.0:
            s.warmth = clamp(s.warmth - 0.02)   # below this it keeps sliding on its own

        s.minutes += 1
        if s.minutes % (24 * 60) == 0:
            s.day += 1

    for k in list(s.effects):
        s.effects[k] -= minutes
        if s.effects[k] <= 0:
            del s.effects[k]
            if k == "burning":
                # everything it was told to wait for arrives at once
                s.fatigue = clamp(s.fatigue + 26.0)
                s.strain = clamp(s.strain + 22.0)
                s.pain = clamp(s.pain + 16.0)
                s.mood = clamp(s.mood - 8.0)
                s.feedback.append(
                    "THE BURN LETS GO. Everything it was holding off arrives in one "
                    "piece - the legs, the chest, the whole of what it has been doing "
                    "on credit - and it has to stop where it is standing.")
                from . import crisis as CR
                if not s.crisis and s.rng.random() < 0.06 * SUB.trait(s, "heart"):
                    CR.begin(s, "tachy", "the burn wearing off on a heart that was "
                                          "running on it")
                    s.feedback.append(
                        "*** IT GOES DOWN *** heart running away - the burn wearing "
                        "off. The chip is on residual power now: %d seconds."
                        % s.crisis["left"])
            if k == "blocked":
                s.pain = clamp(s.pain + 30.0)
                s.feedback.append(
                    "THE BLOCK COMES OFF and the body finds out what it has been "
                    "doing to itself. All of it at once, and none of it is new.")

    if MOOD_HOOK and minutes > 0:
        MOOD_HOOK(s, minutes, resting)
    if minutes > 0:
        from . import phones as PH
        for ln in PH.tick(s, minutes):
            s.feedback.append(ln)

    # derived pressure
    if s.infection > 40:
        s.pain = clamp(s.pain + 0.02 * minutes)
    if s.warmth < 20:
        s.strain = clamp(s.strain + 0.03 * minutes)
    if s.thirst > 80 or s.hunger > 85:
        s.strain = clamp(s.strain + 0.02 * minutes)


def sleep(s, hours, safety=1.0, cold=0.0):
    """Returns (text, interrupted)."""
    mins = int(hours * 60)
    got = 0
    interrupted = False
    while got < mins:
        chunk = min(30, mins - got)
        tick(s, chunk, resting=True, cold=cold)
        got += chunk
        if s.rng.random() < (0.055 / max(0.25, safety)):
            interrupted = True
            break
    s.stats["sleeps"] = s.stats.get("sleeps", 0) + 1
    if got >= 300 and not interrupted:
        s.add_eff("rested", 420)
        s.weird = clamp(s.weird - 5)
    txt = "You sleep %.1f hours." % (got / 60.0)
    if interrupted:
        txt += " Something wakes you before you are finished."
    s.note(txt)
    return txt, interrupted


# ---------------------------------------------------------------- failure
def check_fail(s, danger=0.3):
    """Returns (ending_key, text) or None."""
    from . import lastbreath as LB
    if LB.active(s):
        # it is already up off the ground on borrowed turns. Nothing kills it until the
        # window closes, and closing the window is lastbreath's job, not this one's.
        LB.hold(s)
        return None
    # something in the turn already decided this - a thing that kills by happening rather
    # than by a number crossing a line. It queues here so it goes through the same funnel.
    pend = getattr(s, "pending_death", None)
    if pend:
        s.pending_death = None
        return (pend[0], pend[1])
    if s.blood <= 0:
        return ("BLED OUT",
                "The orange has all gone out of you. It pools, and it glows, and it cools. "
                "Your eyes are the last things still lit, and then they are not.")
    if s.thirst >= 100:
        return ("DRY",
                "Your tongue is a dry strap. You stop being able to swallow, and then to stand.")
    if s.hunger >= 100:
        return ("HOLLOW",
                "Your body finishes eating itself and finds nothing else to eat.")
    if s.infection >= 100:
        return ("SEPSIS",
                "The heat in the wound becomes the heat in all of you. You go down talking to no one.")
    if s.warmth <= 0:
        return ("COLD",
                "The shivering stops, which feels like mercy, and is not.")
    if (getattr(s, "heat", 0.0) or 0.0) >= 100:
        return ("BOILED",
                "It has been too hot for too long and there is nowhere left to put any of it. "
                "The core of it goes past the temperature protein tolerates, and everything "
                "that was holding its shape stops holding it. It goes down in the heat with "
                "its eyes still lit.")
    if s.weird >= 100:
        return ("UNMADE",
                "You stop matching yourself. The edges of you disagree about where you are, and the "
                "disagreement wins. Whatever has been running you closes the window.")
    if s.fatigue >= 100:
        if s.rng.random() < danger:
            return ("COLLAPSED",
                    "Your legs fold mid-step. You are unconscious in the open, in a place that does "
                    "not leave things lying in the open for long.")
        sleep(s, 4.5, safety=0.6)
        s.fatigue = clamp(s.fatigue - 55)
        s.note("You black out standing up and wake in the dirt hours later.")
    return None


# ---------------------------------------------------------------- readouts
def limb_summary(s):
    bad = []
    for n in LIMB_ORDER:
        L = s.limbs[n]
        if L["state"] == "intact":
            continue
        t = "%s %s" % (n, L["state"])
        if L["state"] == "lost" and L["strut"]:
            t += "+strut"
        if L["bound"]:
            t += "(bound)"
        if L["bleed"] > 0 and not L["bound"]:
            t += "(BLEEDING)"
        bad.append(t)
    return ", ".join(bad) if bad else "all intact"


def warnings(s):
    w = []
    if bleed_rate(s) > 0:
        w.append("BLEEDING %.2f/min" % bleed_rate(s))
    if s.blood < 45:
        w.append("blood low")
    if s.thirst > 72:
        w.append("thirsty")
    if (getattr(s, "heat", 0.0) or 0.0) > 20:
        w.append("OVERHEATING %.0f" % s.heat)
    if s.hunger > 75:
        w.append("starving")
    if s.fatigue > 78:
        w.append("failing to stay awake")
    if s.strain > 80:
        w.append("strained to the limit")
    if s.infection > 35:
        w.append("wound is hot")
    if s.warmth < 25:
        w.append("cold")
    if s.weird > 60:
        w.append("WRONG")
    if load_of(s) > carry_cap(s):
        w.append("overloaded")
    if s.mood < 30:
        w.append("miserable")
    if s.will < 35:
        w.append("BALKING")
    if s.chip < 45:
        w.append("link degraded")
    return w


def condition_word(s):
    score = (s.blood * 0.9 - s.pain * 0.5 - s.strain * 0.3 - s.infection * 0.4
             - s.weird * 0.3 - limbs_lost(s) * 12)
    if score > 78:
        return "sound"
    if score > 58:
        return "scuffed"
    if score > 38:
        return "hurt"
    if score > 18:
        return "failing"
    return "coming apart"
