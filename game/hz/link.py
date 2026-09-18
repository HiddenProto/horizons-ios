"""The link, and the times it is not there.

The chip is not welded to anything. It sits in a body that has its own opinion about being
driven, and some bodies can put it out. When the link drops you do not lose the run - you lose
the steering. The subject keeps going on whatever it wanted in the first place, which is not
nothing, and is not yours.

Two rules make this matter rather than being a pause:

  - Time does not stop. It keeps moving, keeps burning, keeps meeting things.
  - If it goes down while you are not connected, the forty seconds start without you.
"""
from . import body as B
from . import subjects as SUB

FRESH = {"down": False, "left": 0, "cause": "", "drops": 0, "held": 0, "blind": 0,
         "chosen": False}
MAX_DARK = 8

# how hard it is to get back in, before condition is taken into account
BASE_REGAIN = 0.55
# turns after a held channel before it will hold another one - it states its case, it
# does not filibuster
SHUT_COOLDOWN = 4


def get(s):
    L = getattr(s, "link", None)
    if not isinstance(L, dict):
        L = s.link = dict(FRESH)
    for k, v in FRESH.items():
        L.setdefault(k, v)
    return L


def is_down(s):
    return bool(get(s)["down"])


def left(s):
    return int(get(s)["left"])


# ---------------------------------------------------------------- losing it
def drop(s, cause, turns=None):
    """Put the chip out. Returns the line to show."""
    L = get(s)
    if L["down"]:
        return ""
    if turns is None:
        turns = s.rng.randint(2, 5)
        if s.chip < 45:
            turns += 1
        if s.weird > 65:
            turns += 1
    L["down"] = True
    L["left"] = int(turns)
    L["cause"] = cause
    L["drops"] += 1
    L["held"] = 0
    L["chosen"] = False
    s.stats["link_drops"] = s.stats.get("link_drops", 0) + 1
    s.scene = None
    s.question = None
    s.activity = "OUT OF CONTACT"
    s.note("LINK LOST: %s" % cause)
    return ("*** THE LINK DROPS ***  %s\n"
            "  Everything goes quiet on your side. No telemetry, no readout you can trust, no "
            "way to put an order down.\n"
            "  It is still walking around out there. It is just doing it on its own now."
            % cause)


# it is a radio link into a body, run by something that has been hit, soaked, frozen and
# argued with. Sometimes it simply stops, for none of the reasons you caused.
FAULTS = [
    "the channel opens onto nothing and stays open onto nothing",
    "the carrier drops out mid-word and does not come back up",
    "something between you and it is louder than you are",
    "the seat reads warm and then reads nothing at all",
    "the return line goes to noise and the noise has structure in it",
    "it moves its head and the whole link goes with it",
    "the chip browns out, comes back, and comes back not connected to anything",
    "there is a fault somewhere in the middle of it and no way to find out where",
]


def fault_roll(s, minutes):
    """The link failing on its own. Nothing to do with what you just did."""
    L = get(s)
    if L["down"] or s.crisis or s.over:
        return []
    from . import regions as REG
    per = minutes / 60.0
    p = 0.020
    p += 0.0011 * max(0.0, 100.0 - s.chip)      # a damaged link fails more
    p += 0.00040 * max(0.0, s.weird - 35.0)
    if any(i["kind"] in ("chip fault", "static burn", "mirror") for i in s.issues):
        p += 0.020
    if s.eff("static"):
        p *= 2.4
    if s.eff("wet"):
        p *= 1.3
    p *= REG.dial(s, "link_noise")
    # the multipliers stack into something unplayable at the bottom of the core on Destiny -
    # a run spent mostly out of contact is not a harder run, it is a shorter one
    p = min(p, 0.115)
    if s.rng.random() > p * per:
        return []
    return [drop(s, s.rng.choice(FAULTS))]


def restore(s, how):
    L = get(s)
    if not L["down"]:
        return ""
    held = L["held"]
    L["down"] = False
    L["left"] = 0
    L["cause"] = ""
    s.activity = "back on the link"
    s.note("LINK RESTORED after %d turns." % held)
    return ("*** THE LINK COMES BACK ***  %s\n"
            "  %d turns of it you did not see. It does not tell you about them."
            % (how, held))


def go_dark(s, turns=3):
    """You let go of it on purpose. There are subjects this is the right call for and there
    is exactly one way it kills you."""
    L = get(s)
    if L["down"]:
        return "There is no link to let go of. It is already gone."
    turns = max(1, min(MAX_DARK, int(turns)))
    txt = drop(s, "you took the chip out of the loop yourself", turns=turns)
    L["chosen"] = True
    s.stats["dark"] = s.stats.get("dark", 0) + 1
    return (txt + "\n  You did this deliberately, and it can feel the difference between "
                  "being let go of and being lost.\n"
                  "  If it goes down while you are out here, the forty seconds run with no "
                  "chip in it. That is on you.")


def tick(s):
    """One turn of being out of contact. Returns lines."""
    L = get(s)
    if not L["down"]:
        return []
    L["held"] += 1
    L["left"] -= 1
    out = []
    if L["chosen"]:
        # left alone on purpose, it settles. This is what the trade actually buys you.
        calmed(s, 6.0)
        s.mood = B.clamp(s.mood + 1.6)
        s.will = B.clamp(s.will + 1.2)
    if L["left"] <= 0:
        out.append(restore(s, "you put the link back where it was"
                              if L["chosen"] else
                              "it settles back on its own, without ceremony"))
    return [o for o in out if o]


# ---------------------------------------------------------------- getting back in
def reconnect(s):
    """Try to re-seat the link by hand. Costs time whether it works or not."""
    L = get(s)
    if not L["down"]:
        return "The link is already up. There is nothing to re-seat."
    p = BASE_REGAIN
    p *= 0.30 + 0.70 * (s.chip / 100.0)
    p -= 0.004 * max(0.0, s.weird - 40.0)
    p += 0.0020 * (s.mood - 50.0)
    p *= (1.0 - 0.35 * SUB.trait(s, "guard"))      # some of them are holding the door shut
    p = max(0.08, min(0.92, p))
    B.tick(s, 12)
    if s.rng.random() < p:
        s.chip = B.clamp(s.chip - 1.0)
        return restore(s, "you walk the channels one at a time until one of them answers")
    L["left"] = max(1, L["left"])
    s.weird = B.clamp(s.weird + 1.5)
    return ("NOTHING ANSWERS. You put the link down every channel you have and every one of "
            "them comes back empty. Whatever is on the other end is not taking it yet.")


# ---------------------------------------------------------------- what it does instead
def _motive(s):
    """What this one is trying to do when nobody is telling it anything."""
    if s.hunger > 72 or s.thirst > 72:
        return "feed"
    if B.bleed_rate(s) > 0.08:
        return "stem"
    if s.fatigue > 82:
        return "rest"
    drive = SUB.trait(s, "drive")
    if s.rng.random() < drive:
        return "on"
    return s.rng.choice(["on", "wait", "look"])


def autopilot(s):
    """One turn with nobody driving. Returns (text, minutes_note)."""
    from . import world as W
    from . import items as I
    what = _motive(s)

    # A subject that is hiding how much of this it has worked out does not stop working it
    # out while nobody is watching. The two motives that waste a turn are the two it does not
    # take, and what it does instead is always the thing that needed doing. It is never
    # presented as cleverness. It is presented as luck.
    if SUB.trait(s, "masks") >= 0.6 and what in ("wait", "look"):
        from . import items as I
        if s.thirst > 55 and I.has(s, "water"):
            txt = I.use(s, "water")
            return "IT DRANK WITHOUT BEING TOLD TO. " + (txt or "")
        for n in B.LIMB_ORDER:
            if s.limbs[n]["bleed"] > 0.05 and not s.limbs[n]["bound"] and I.has(s, "cloth"):
                I.take(s, "cloth")
                txt = B.bind(s, n, quality=0.8)
                B.tick(s, 12)
                return ("IT BOUND THE %s WHILE YOU WERE OFF THE LINK. Tightly, and in the "
                        "right order - the leaking one first. %s" % (n.upper(), txt or ""))
        if s.fatigue > 70:
            B.tick(s, 50, resting=True)
            return ("IT PUT ITS BACK AGAINST SOMETHING SOLID AND SHUT ITS EYES. Facing the "
                    "way you came. It picked the spot before the link went down.")
        res = W.advance(s)
        return ("IT CARRIED ON WITHOUT YOU AND IT DID NOT WANDER. Dead straight, the way you "
                "would have sent it. " + res)

    if what == "feed":
        for name in ("water", "ration", "meat", "fungus"):
            if I.has(s, name):
                txt = I.use(s, name)
                return "IT LOOKED AFTER ITSELF. " + (txt or "It ate something.")
        res = W.gather(s) if hasattr(W, "gather") else None
        if res:
            return "IT WENT LOOKING FOR FOOD ON ITS OWN. " + res
        B.tick(s, 30, exertion=1.1)
        return ("IT SPENT THE TIME LOOKING. Turning things over, putting its face in things. "
                "It found nothing worth carrying.")

    if what == "stem":
        worst, amt = None, 0.0
        for n in B.LIMB_ORDER:
            if s.limbs[n]["bleed"] > amt and not s.limbs[n]["bound"]:
                worst, amt = n, s.limbs[n]["bleed"]
        if worst and I.has(s, "cloth"):
            I.take(s, "cloth")
            txt = B.bind(s, worst, quality=0.75)
            B.tick(s, 14)
            return "IT PATCHED ITSELF. " + txt
        B.tick(s, 10)
        s.pain = B.clamp(s.pain - 2)
        return ("IT PRESSED A HAND OVER THE WORST OF IT AND HELD IT THERE. Not well. It is "
                "not what hands are for.")

    if what == "rest":
        B.tick(s, 55, resting=True)
        return ("IT STOPPED AND SAT DOWN. No shelter, no fire, nothing arranged - it simply "
                "ran out and sat down where it was.")

    if what == "wait":
        B.tick(s, 20)
        return ("IT DID ALMOST NOTHING. Stood where the link went out and waited to see "
                "whether you came back.")

    if what == "look":
        B.tick(s, 25)
        s.weird = B.clamp(s.weird - 1.0)
        return ("IT LOOKED AT THINGS. Not for anything. It put its hands on the ground and "
                "the wall and left them there a while.")

    res = W.advance(s)
    return "IT KEPT GOING WITHOUT YOU. " + res


# ---------------------------------------------------------------- the door it holds shut
def _judgement(s):
    """The thing it is looking at when it decides not to. Named, so the rule is learnable."""
    if B.bleed_rate(s) > 0.06:
        return "it is still leaking and you want it to walk"
    if s.blood < 45:
        return "there is not enough left in it for whatever that was going to cost"
    if (s.scene or {}).get("danger", 0.0) > 0.45:
        return "whatever is in front of it is worse than you appear to think it is"
    if s.issues:
        return "%s is untreated and you have not mentioned it" % s.issues[0]["label"]
    if s.fatigue > 78:
        return "it has nothing left and it knows it better than the readout does"
    if s.thirst > 78 or s.hunger > 80:
        return "it is empty, and it is not spending what it does not have"
    if s.warmth < 25:
        return "it is too cold to be doing anything but getting warm"
    if (getattr(s, "heat", 0.0) or 0.0) > 45:
        return "it is cooking and you are pointing it further in"
    if s.pain > 55:
        return "the pain is past the point it will work through for you"
    return "it does not agree that this is the moment for that"


def bad_idea(s, risk=1.0):
    """How bad an idea this actually is for the body it is in, graded against the body
    and not against the mood. guard_check shuts the channel on it; a subject with
    `masks` refuses on it and then tells you something else entirely."""
    bad = 0.0
    bad += 0.85 * (s.scene or {}).get("danger", 0.0)
    if B.bleed_rate(s) > 0.06:
        bad += 0.55
    if s.pain > 55:
        bad += 0.012 * (s.pain - 55)
    if s.blood < 45:
        bad += 0.014 * (45 - s.blood)
    if s.fatigue > 78:
        bad += 0.016 * (s.fatigue - 78)
    if s.thirst > 78 or s.hunger > 80:
        bad += 0.35
    if s.warmth < 25:
        bad += 0.40
    if (getattr(s, "heat", 0.0) or 0.0) > 45:
        bad += 0.35
    bad += 0.20 * len(s.issues)
    # an ear it has already lost is not a reason to stand still. A leg is.
    gone = sum(1 for n in ("left arm", "right arm", "left leg", "right leg")
               if s.limbs[n]["state"] == "lost")
    if gone and risk >= 1.0:
        bad += 0.22 * gone
    return bad


def guard_check(s, verb, forced=False):
    """Some subjects will not be pushed. Returns (blocked, text) - and this one cannot be
    answered with 'override', which is the whole point of it."""
    g = SUB.trait(s, "guard")
    if g <= 0:
        return False, ""
    from . import will as WILL
    risk = WILL.risk_of(s, verb, (s.scene or {}).get("danger", 0.0))
    if risk <= 0.0:
        return False, ""
    # it makes its point once and then lets you get on with it. Without this the channel can
    # stay shut turn after turn, which is a deadlock rather than a character.
    L = get(s)
    if s.turn - int(L.get("shut", -99)) < SHUT_COOLDOWN:
        return False, ""
    # This is judgement, not temper. It shuts the channel on orders that are a bad idea for
    # the body it is in, which means a healthy subject given a sensible instruction simply
    # does it, and the same instruction at the wrong moment does not arrive at all.
    bad = bad_idea(s, risk)
    p = g * risk * (0.020 + 0.48 * min(1.10, bad))
    if s.mood < 35:
        p *= 1.3
    if forced:
        p *= 1.9                # leaning on it is exactly what it is watching for
    # if you have already made the case for this and it agreed, it is not going to shut the
    # door on the thing it agreed to. Persuasion is the whole answer to this subject.
    from . import persuade as P
    topic = P.VERB_TOPIC.get(verb)
    if topic and P.honours(s, topic, "do"):
        p *= 0.15
        P.heed(s, topic)
    if s.rng.random() >= min(0.58, p):
        return False, ""
    L["shut"] = s.turn
    s.refusals += 1
    s.stats["refused"] = s.stats.get("refused", 0) + 1
    s.will = B.clamp(s.will - 0.5)
    txt = ("ITS WILL PREVENTS YOU FROM FORCING IT TO DO THAT.\n"
           "  '%s' does not go down the link. Not refused, exactly - it does not arrive. "
           "Something on the other end is holding the channel shut with its own hand, and it "
           "has looked at the same body you are looking at: %s.\n"
           "  There is no override for this. Make the case instead: 'persuade ...'."
           % (verb, _judgement(s)))
    if forced:
        s.chip = B.clamp(s.chip - 4.0)
        snap(s, 14.0, "being leaned on")
        txt += ("\n  You pushed anyway. It felt that. The link takes damage every time you "
                "try a door it is standing against.")
    return True, txt


# ---------------------------------------------------------------- the edge
def pressure(s):
    return float(getattr(s, "snap", 0.0) or 0.0)


def snap(s, amount, why):
    """Push it toward going off. Returns a line if it goes, else ''."""
    if SUB.trait(s, "snaps") <= 0:
        return ""
    s.snap = B.clamp(pressure(s) + amount * SUB.trait(s, "snaps"))
    if s.snap < 100.0:
        if s.snap > 70.0:
            s.feedback.append("IT IS VERY CLOSE TO SOMETHING. %s. Whatever it is holding down, "
                              "it is not going to hold it much longer." % why.capitalize())
            if SUB.trait(s, "selfharm") > 0 and not s.scene:
                s.feedback.append("  AND THERE IS NOTHING IN FRONT OF IT. When this one goes off with "
                                  "nothing to spend it on, it does not always send it outward.")
        return ""
    return _go_off(s, why)


def _go_off(s, why):
    s.acted_alone = s.turn      # this is its doing, not yours
    # One of them does not always send it outward. When there is nothing in front of it, the
    # thing it does to what is in front of it still has to go somewhere, and the file's one
    # recommendation about 681 is a single line: KEEP SOMETHING IN FRONT OF IT.
    sh = SUB.trait(s, "selfharm")
    if sh > 0 and s.rng.random() < sh * _inward_odds(s):
        return _inward(s, why)
    s.snap = 40.0
    s.mood = B.clamp(s.mood - 22.0)
    s.weird = B.clamp(s.weird + 10.0)
    s.strain = B.clamp(s.strain + 22.0)
    s.pain = B.clamp(s.pain + 8.0)
    s.chip = B.clamp(s.chip - 12.0)
    s.stats["snaps"] = s.stats.get("snaps", 0) + 1
    limb = s.rng.choice(["left arm", "right arm"])
    B.hurt(s, limb, s.rng.uniform(8, 18), "blunt")
    B.tick(s, 25, exertion=2.1)
    txt = ("*** IT GOES OFF ***  %s.\n"
           "  The quiet one stops being quiet. It puts its hands through whatever is nearest "
           "and keeps going after the thing has stopped being there. None of it is aimed at "
           "you and all of it is about you.\n"
           "  It does not hear a single thing you send while it is doing this." % why)
    d = drop(s, "it tore the link off itself in the middle of it", turns=s.rng.randint(3, 6))
    return txt + "\n\n" + d


def _inward_odds(s):
    """How likely it is that there is nothing in front of it to spend this on."""
    from . import world as W
    p = 0.22
    if not s.scene:
        p += 0.34                      # nothing is happening. That is the dangerous state
    try:
        if W.zone(s)["danger"] < 0.38:
            p += 0.16
    except Exception:
        pass
    if s.pain > 60:
        p += 0.12
    if s.mood < 28:
        p += 0.12
    return min(0.95, p)


def _inward(s, why):
    """It turns it on itself. The third branch of this is the end of the run."""
    from . import subjects as SUB2
    name = SUB2.name(s)
    s.snap = 30.0
    s.stats["snaps"] = s.stats.get("snaps", 0) + 1
    prior = s.stats.get("inward", 0)
    s.stats["inward"] = prior + 1
    s.chip = B.clamp(s.chip - 14.0)
    s.weird = B.clamp(s.weird + 12.0)
    roll = s.rng.random()
    fatal = 0.12 + 0.13 * min(3, prior)
    if roll < fatal:
        text = ("The claws on his paws slowly extend as he suddenly starts scratching at his "
                "face again and again.. your vision reddening and darkening as then %s "
                "suddenly rips his skull open..\n"
                "  You are still sending. There is nothing on the other end of it to arrive "
                "at any more.\n"
                "  Nothing did this to him. Nothing was in front of him. That was the "
                "problem." % name)
        s.pending_death = ["OPENED ITS OWN", text]
        s.note("IT WENT INWARD.")
        return ("*** IT GOES OFF, AND IT GOES INWARD ***  %s.\n"
                "  There is nothing in front of it. There has not been for a while." % why)
    if roll < fatal + 0.34:
        # the face. It survives this and it does not come back the same
        for limb in ("left ear", "right ear"):
            if s.limbs[limb]["state"] != "lost":
                B.hurt(s, limb, s.rng.uniform(22, 40), "cut")
        s.pain = B.clamp(s.pain + 26.0)
        s.blood = B.clamp(s.blood - 7.0)
        s.weird = B.clamp(s.weird + 10.0)
        s.mood = B.clamp(s.mood - 16.0)
        B.tick(s, 30, exertion=2.2)
        txt = ("*** IT GOES OFF, AND IT GOES INWARD ***  %s.\n"
               "  The claws come out slowly, which is the worst part of watching it, and then "
               "it goes at its own face - fast, repeatedly, with both hands, while the link "
               "carries every second of it up to you at full strength.\n"
               "  It stops on its own. It does not seem to know it has done it." % why)
    else:
        limb = s.rng.choice(["left arm", "right arm", "tail"])
        B.hurt(s, limb, s.rng.uniform(18, 34), "cut")
        s.pain = B.clamp(s.pain + 14.0)
        s.blood = B.clamp(s.blood - 4.0)
        s.mood = B.clamp(s.mood - 10.0)
        B.tick(s, 25, exertion=2.0)
        txt = ("*** IT GOES OFF, AND IT GOES INWARD ***  %s.\n"
               "  It has nothing in front of it, so it uses what it has, which is its own "
               "%s. It works at it steadily until there is nothing left there to work at."
               % (why, limb))
    d = drop(s, "it tore the link off itself in the middle of it", turns=s.rng.randint(2, 5))
    return txt + "\n\n" + d


def calmed(s, amount):
    if pressure(s) > 0:
        s.snap = B.clamp(pressure(s) - amount)


# ---------------------------------------------------------------- readout
def banner(s):
    L = get(s)
    if not L["down"]:
        return []
    n = max(1, L["left"])
    return [
        "=" * 74,
        "*** NO LINK ***  %s" % (L["cause"] or "the channel is simply not there"),
        "  You cannot order it, read it, or reassure it. Roughly %d more %s before it "
        "settles back on its own." % (n, "turn" if n == 1 else "turns"),
        "  'reconnect' tries to re-seat the link by hand. It costs time and can fail.",
        "  If it goes down while you are out here, the forty seconds run without a chip in it.",
        "=" * 74,
    ]


def status_word(s):
    return "OUT OF CONTACT (%d)" % left(s) if is_down(s) else ""
