"""The chip and the creature on the end of it.

The chip supplies most of this thing's intelligence - the orders come from outside. What the
chip does NOT supply is willingness. A body in pain, starving, frightened or plainly
miserable starts declining instructions, and the only way past that is to look after it or to
force the link and damage it.
"""
from . import body as B
from . import subjects as SUB

# how much of an imposition each kind of order is
RISK = {
    "go": 1.00, "forward": 1.00, "advance": 1.00, "walk": 1.00, "move": 1.00, "onward": 1.00,
    "gather": 0.75, "search": 0.75, "scavenge": 0.75, "forage": 0.75, "loot": 0.75,
    "shelter": 0.45, "build": 0.45, "craft": 0.35, "graft": 1.25,
    "escape": 1.55, "evade": 1.10, "hide": 0.40,
}
SCENE_RISK = 1.15          # answering a dangerous option
NEVER_REFUSED = (
    "tend", "bind", "treat", "patch", "rest", "camp", "sleep", "use", "eat", "drink",
    "apply", "read", "reassure", "recalibrate", "override", "status", "inv", "i",
    "inventory", "bag", "look", "l", "where", "scene", "map", "help", "?", "commands",
    "think", "monologue", "mind", "truths", "know", "recipes", "recipe", "log", "history",
    "issues", "timers", "drop", "self", "body", "condition", "save", "quit", "cut",
    "persuade", "please", "reason", "plead", "convince", "listen", "say", "reconnect",
    "relink", "reseat", "disconnect", "letgo", "godark", "dark", "mend", "phones",
    "wins", "board", "finished", "region",
)


def target_will(s):
    t = (s.mood * 0.70 + 38.0
         - s.pain * 0.22 - s.fatigue * 0.18 - s.weird * 0.15
         - B.limbs_lost(s) * 4.0
         - len(s.issues) * 3.0)
    if s.eff("rested"):
        t += 10.0
    if s.eff("fire") or s.eff("sheltered"):
        t += 4.0
    if s.chip < 40:
        t -= (40.0 - s.chip) * 0.35
    return B.clamp(t)


def drift(s, minutes, resting=False):
    """Called from the clock. Mood answers to condition; will answers to mood."""
    lost = B.limbs_lost(s)
    pressure = (s.pain * 0.010 + s.fatigue * 0.006 + s.hunger * 0.004
                + s.thirst * 0.004 + s.weird * 0.008 + s.infection * 0.006
                + lost * 0.8 + len(s.issues) * 0.35
                + (2.0 if B.bleed_rate(s) > 0 else 0.0))
    relief = 0.0
    if resting:
        relief += 2.2
    if s.eff("fire"):
        relief += 0.8
    if s.eff("sheltered"):
        relief += 0.6
    if s.eff("rested"):
        relief += 0.6
    if s.warmth > 45 and s.thirst < 50 and s.hunger < 50:
        relief += 0.5
    vol = SUB.trait(s, "volatility")
    from . import persuade as P
    if P.honours(s, "calm", "do") or P.honours(s, "calm", "stop"):
        vol *= 0.70            # it is actively trying not to spiral, because you asked
    delta = (relief - pressure) * 0.012 * minutes * vol
    desp = SUB.trait(s, "despair")
    if desp and s.mood < 32 and delta < 0:
        delta *= 1.0 + desp          # the floor is a long way down for some of them
    s.mood = B.clamp(s.mood + delta)
    s.will = B.clamp(s.will + (target_will(s) - s.will) * 0.003 * minutes)
    # whatever it is holding down settles again if it is left alone - slowly, and faster if
    # it is resting. Pain and wrongness keep it up.
    pr = float(getattr(s, "snap", 0.0) or 0.0)
    if pr > 0.0:
        ease = 0.010 * minutes * (2.0 if resting else 1.0)
        ease -= 0.00008 * minutes * (s.pain + s.weird)
        s.snap = B.clamp(pr - max(0.0, ease))


def mood_word(s):
    m = s.mood
    if m > 75:
        return "steady"
    if m > 55:
        return "willing"
    if m > 38:
        return "flagging"
    if m > 22:
        return "sullen"
    if m > 10:
        return "despondent"
    return "given up"


def link_word(s):
    c = s.chip
    if c > 80:
        return "link clean"
    if c > 55:
        return "link noisy"
    if c > 30:
        return "link degraded"
    if c > 12:
        return "link failing"
    return "link almost gone"


def risk_of(s, verb, scene_danger=0.0):
    if verb in NEVER_REFUSED:
        return 0.0
    if verb.isdigit() or verb in ("choose", "pick", "opt", "option"):
        return SCENE_RISK * (0.4 + scene_danger)
    return RISK.get(verb, 0.5)


def refuses(s, verb, scene_danger=0.0):
    """Returns (True, reason) if the subject will not do it."""
    risk = risk_of(s, verb, scene_danger)
    if risk <= 0.0:
        return False, ""
    if s.eff("clarity"):
        # it got up off the ground on its own. For as long as that lasts it is not arguing
        # with anybody about anything.
        return False, ""
    held = ""
    p = (1.0 - s.will / 100.0) * risk * 0.48 - 0.10
    p *= SUB.trait(s, "refusal_mult")
    if s.mood < 20:
        p += 0.18
    if s.question:
        p += 0.15          # it wants an answer before it wants an instruction
    if s.fatigue > 88:
        p += 0.15
    if s.pain > 75:
        p += 0.12
    from . import persuade as P
    # a numbered scene option is an order too. "Climb it" has to answer to an agreement about
    # climbing, or the agreement is decorative.
    if verb.isdigit() and s.scene:
        try:
            label = str(s.scene["opts"][int(verb) - 1]).lower()
        except (IndexError, ValueError, KeyError):
            label = ""
        for tid, r in (s.requests or {}).items():
            spec = P.TOPICS.get(tid)
            if not spec or not any(k in label for k in spec["keys"]):
                continue
            if r.get("pol") == "stop":
                p += 0.30
                held = r.get("label", "")
            else:
                p *= 0.60
            P.heed(s, tid)
            break
    topic = P.VERB_TOPIC.get(verb)
    if topic:
        if P.honours(s, topic, "do"):
            p *= 0.55          # you talked it into this already, and it remembers agreeing
            P.heed(s, topic)
        elif P.honours(s, topic, "stop"):
            p += 0.22          # you are the one who told it not to. It holds you to that
            held = (P.get(s, topic) or {}).get("label", "")
            P.heed(s, topic)
    # Some of them have a reason and will not give you the reason. For those, the odds
    # stop tracking the mood and start tracking the body: it declines the orders that are
    # actually a bad idea, at close to the rate 680 shuts the channel on them - and then
    # it hands you something that is not the reason. The pattern is the only thing that
    # gives it away, and the pattern is there to be found.
    # what it thinks you are up to is a refusal pressure of its own, and unlike the
    # others it does not come off with a reassurance
    from . import intent as INT
    p += INT.refusal_bonus(s)
    # some of them go anyway. 1278 has had the pause bred out of it and will walk on a
    # leg it should not walk on, because refusing is not available to it.
    # a burn does not make it braver. It removes the two things it was refusing on.
    if s.eff("burning"):
        p *= 0.55
    elif s.eff("blocked"):
        p *= 0.80
    push = SUB.trait(s, "pushes")
    if push > 0 and (s.pain > 60 or s.fatigue > 80):
        p *= 1.0 - 0.75 * push
    m = SUB.trait(s, "masks")
    if m > 0:
        from . import link as LK
        bad = min(1.10, LK.bad_idea(s, risk))
        p = p * (1.0 - 0.72 * m) + m * risk * 0.70 * bad
    p = max(0.0, min(0.85, p))
    if s.rng.random() >= p:
        s.will = B.clamp(s.will - 1.2 * risk)
        return False, ""

    s.will = B.clamp(s.will - 0.6)
    s.refusals += 1
    s.stats["refused"] = s.stats.get("refused", 0) + 1
    if held:
        # not a mood - it is keeping an agreement, and it should say which one
        return True, "it agreed with you to %s, and it is holding to that" % held
    if SUB.trait(s, "masks") > 0:
        return True, _masked_reason(s)
    reason = _reason(s)
    return True, reason


# What it says instead. None of these are reasons and none of them are lies either - it
# simply declines to put the real one on the link. Rarely the mask is not up in time.
MASK_REASONS = [
    "it does not want to, and it does not offer anything behind that",
    "it turns its head away from the order the way something turns away from a smell",
    "it snaps at nothing, twice, and stays exactly where it is",
    "it makes a short sound that is not a word, and does not move",
    "it has found something on the ground more interesting than the chip",
    "it is already doing something else. It is not doing anything else",
    "it looks at the thing you pointed it at for a long moment and then does not go",
]


def _masked_reason(s):
    """One time in eleven it does not bother to cover it, and what comes back is exact."""
    from . import link as LK
    if s.rng.random() < 0.09:
        why = LK._judgement(s)
        return ("%s - it says so plainly, once, in a register you have not heard out of it "
                "before, and then it is back to whatever it was doing" % why)
    return s.rng.choice(MASK_REASONS)


def _reason(s):
    if s.fatigue > 85:
        return ("it is too tired to be told anything - it sits down where it is and does not "
                "answer the chip")
    if s.pain > 72:
        return "it will not move on that much pain"
    if s.mood < 20:
        return ("it has stopped caring what the chip wants. It does not refuse angrily. "
                "It just does not get up")
    if B.bleed_rate(s) > 0.1:
        return "it will not go anywhere while it is still leaking"
    if s.thirst > 80:
        return "it wants water before it wants instructions"
    if s.hunger > 82:
        return "it is too empty to spend itself on that"
    if s.weird > 62:
        return "it does not trust where the order is coming from"
    if s.question:
        return "it asked you something several steps ago and is still waiting on an answer"
    if s.lies > 3:
        return "it has stopped taking what comes down the link at face value"
    if s.issues:
        return "it is unwilling while %s is untreated" % s.issues[0]["label"]
    return "it balks, for no reason it can give you"


def refusal_text(s, verb, reason):
    # a refusal that comes from an agreement has a different answer to one that comes from a
    # mood: settling it down will not talk it out of something it thinks it promised you.
    if SUB.trait(s, "silent") > 0.6 and "it is holding to that" not in reason:
        # it does not argue with you. It simply is not doing it, and you get to work out why.
        return ("REFUSED: '%s'.\n  Nothing comes back. No complaint, no reason, no sign it "
                "even weighed the order - it does the next thing it was going to do anyway.\n"
                "  %s  (or force it: 'override %s')" % (verb, suggestion(s), verb))
    if "it is holding to that" in reason:
        fix = ("Reassuring it will not shift this - it is not upset, it is being consistent. "
               "Talk it round the other way with 'persuade ...'.")
    else:
        fix = suggestion(s)
    return ("REFUSED: '%s' - %s.\n  The chip carries the order; it does not carry obedience.\n"
            "  %s  (or force it: 'override %s')" % (verb, reason, fix, verb))


def suggestion(s):
    if s.fatigue > 80:
        return "Let it sleep: 'camp 6' (better after 'shelter')."
    if B.bleed_rate(s) > 0.05:
        return "Stop the bleeding first: 'tend <limb>'."
    if s.thirst > 75:
        return "Give it water: 'use water'."
    if s.hunger > 78:
        return "Feed it: 'use ration' or 'use meat'."
    if s.pain > 70:
        return "Rest it: 'rest 2', and salve what is hot."
    if s.issues:
        return "Deal with the issue: '%s'." % s.issues[0]["fix"]
    if s.mood < 35:
        return "Settle it: 'reassure'."
    return "Try 'reassure', or look after whatever the warnings list."


# -------------------------------------------------------------------- the two levers
def reassure(s):
    """Spend time bringing it round. Diminishing if you lean on it."""
    recent = s.eff("reassured")
    from . import voice as V
    trust = V.trust_factor(s)
    gain_m = (4.0 if recent else 9.0) * trust
    gain_w = (3.0 if recent else 7.0) * trust
    s.mood = B.clamp(s.mood + gain_m)
    s.will = B.clamp(s.will + gain_w)
    s.add_eff("reassured", 150)
    B.tick(s, 18, resting=True)
    if recent:
        return ("You hold the link open and say the same things again. It has heard them. "
                "It settles a little anyway.")
    return ("You stop giving orders and just keep the link warm - no instruction, no pressure, "
            "the equivalent of a hand on the shoulder from something that has no hand. "
            "Its breathing lengthens. It is willing again, for now.")


def override(s):
    """Force the next action through the chip. It works. It always costs."""
    s.will = B.clamp(s.will - 8.0)
    s.mood = B.clamp(s.mood - 6.0)
    s.weird = B.clamp(s.weird + 4.0)
    s.pain = B.clamp(s.pain + 2.0)
    s.chip = B.clamp(s.chip - 1.5)
    s.overrides += 1
    s.stats["overridden"] = s.stats.get("overridden", 0) + 1
    if s.chip < 40 and s.rng.random() < 0.28:
        s.pending_issues.append("chip fault")
    txt = ("OVERRIDE. You push the order down the chip rather than asking. Its body does it. "
           "Its body did not agree to it, and both of you know that now.")
    from . import link as LK
    # forcing something that decides for itself is how the link gets torn off
    went = LK.snap(s, 9.0, "being driven instead of asked")
    if went:
        return txt + "\n\n" + went
    frag = SUB.trait(s, "link_fragile")
    if frag > 0:
        p = frag * (0.10 + 0.20 * (1.0 - s.chip / 100.0))
        if s.rng.random() < p:
            return txt + "\n\n" + LK.drop(s, "it put the chip out rather than be driven again")
    return txt


def recalibrate(s):
    s.chip = B.clamp(s.chip + 9.0)
    s.weird = B.clamp(s.weird - 17.0)
    s.will = B.clamp(s.will + 3.0)
    B.tick(s, 35, resting=True)
    return ("You walk the chip through its own diagnostic - every channel, one at a time. "
            "The doubled edges on things pull back into single edges. The link steadies.")


# register with the clock (see body.MOOD_HOOK) - no circular import needed
B.MOOD_HOOK = drift
