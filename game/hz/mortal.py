"""The hits that are not injuries.

Everything else in this game does damage to a limb and the limb degrades through a state
table. This module is for the other kind: a thing that arrives through the middle of the body,
where there is no limb to degrade, and either kills it where it stands or does not.

FOUR OUTCOMES, and which one you get is a resistance roll, not a coin:

  TURNED ASIDE - the body was already moving. This is not luck and it is not armour; it is
      `autonomy`, the trait that makes a subject act without being told, and it is why 681
      walks away from things that kill other subjects. It did not dodge because you sent it a
      dodge. There was no time for anything you sent to arrive.
  THROUGH AND STANDING - it goes through and the body does not go down. This is the worst
      outcome and it is meant to be: a wound that does not stop, a body that is still upright,
      and a clock. The line the user wrote is this one - it looks down at it.
  THROUGH AND DOWN - the legs go. It is alive at the bottom of it and it has minutes.
  KILLED OUTRIGHT - straight into endings.die, which means the `grit` roll still happens, so
      the one-more-try can fire on an impalement the same as on anything else.

A chest wound also does the thing no other damage in the game does: it can stop the heart or
the lungs without the body first being in one of the extreme states crisis.roll needs. That is
deliberate. Until this module existed there was no way to see an arrest that did not involve
being nearly exsanguinated first.
"""
from . import body as B
from . import subjects as SUB


def resistance(s):
    """How much body there is between the thing arriving and the thing mattering.

    Frailty and armour are the build. Power is what is left to run on. Grit is whether it
    goes down when it should. None of it is a shield - the best resistance in the game still
    loses to a mine.
    """
    r = 0.50
    r += 0.45 * (1.0 - SUB.trait(s, "frailty"))
    r += 0.30 * (1.0 - SUB.trait(s, "armor"))
    r += 0.22 * SUB.trait(s, "grit")
    r += 0.18 * (SUB.trait(s, "power") - 1.0)
    r -= 0.004 * max(0.0, 70.0 - s.blood)
    r -= 0.003 * max(0.0, s.pain - 40.0)
    r -= 0.004 * max(0.0, s.fatigue - 60.0)
    r -= 0.10 * B.limbs_lost(s)
    if s.eff("burning"):
        r += 0.20          # it is running on something and it does not stop as easily
    if s.eff("clarity"):
        r += 0.35          # it is already up on something that is not blood
    return max(0.05, min(1.60, r))


def _moved_first(s):
    """Did it get out of the way on its own? Nothing you send arrives in time to matter."""
    a = SUB.trait(s, "autonomy") + 0.30 * SUB.trait(s, "wary") + 0.20 * SUB.trait(s, "violent")
    if s.eff("burning"):
        a += 0.25
    a *= 1.0 - 0.5 * SUB.trait(s, "jitter")
    if s.pain > 70 or s.fatigue > 85:
        a *= 0.5
    return s.rng.random() < min(0.62, a * 0.62)


# ---------------------------------------------------------------- the chest
def chest_wound(s, severity, cause):
    """A hole through the middle. No limb takes this - blood, pain, and the two organs.

    severity is roughly 'how much of the body it went through', 0.4 to 1.0.
    """
    s.blood = B.clamp(s.blood - 22.0 * severity)
    s.pain = B.clamp(s.pain + 42.0 * severity)
    s.strain = B.clamp(s.strain + 20.0 * severity)
    s.add_eff("holed", int(240 * severity))
    st = getattr(s, "chest", None)
    if not isinstance(st, dict):
        st = s.chest = {"holes": 0, "bleed": 0.0, "why": ""}
    st["holes"] = int(st.get("holes", 0)) + 1
    st["bleed"] = float(st.get("bleed", 0.0)) + 0.22 * severity
    st["why"] = cause
    s.note("CHEST: %s" % cause)
    # the only route to a stopped heart or stopped lungs that does not require the body to
    # already be in an extreme state first
    from . import crisis as CR
    if not s.crisis and severity >= 0.55:
        p = 0.22 * severity * SUB.trait(s, "frailty")
        if s.rng.random() < p:
            kind = "edema" if s.rng.random() < 0.55 else "arrest"
            if SUB.trait(s, "lungs") > SUB.trait(s, "heart"):
                kind = "edema" if s.rng.random() < 0.7 else "apnea"
            CR.begin(s, kind, "a hole through the chest")
            s.feedback.append(
                "*** IT GOES DOWN *** %s - a hole through the chest. The chip is on residual "
                "power now: %d seconds." % (CR.KINDS[kind]["label"], s.crisis["left"]))


def chest_tick(s, minutes):
    """A chest wound does not close on its own and nothing in the pack reaches it.

    The blood is NOT taken here. body.bleed_rate counts the chest along with every limb, and
    the per-minute loop takes it there - which is also what stops the body quietly replacing
    what it is losing. This only closes the hole, slowly, and a little faster once packed.
    """
    st = getattr(s, "chest", None)
    if not isinstance(st, dict) or st.get("bleed", 0.0) <= 0:
        return
    close = 0.00012 if s.eff("packed") else 0.00002
    st["bleed"] = max(0.0, float(st["bleed"]) - close * minutes)


def holed(s):
    st = getattr(s, "chest", None)
    return bool(isinstance(st, dict) and st.get("bleed", 0.0) > 0.01)


def pack_chest(s):
    """The only thing that can be done about it, and it is not a repair."""
    from . import items as I
    st = getattr(s, "chest", None)
    if not isinstance(st, dict) or st.get("bleed", 0.0) <= 0.01:
        return "There is nothing through the chest."
    if not I.has(s, "cloth"):
        return "Packing a hole like that takes cloth, and it is not carrying any."
    I.take(s, "cloth", 1)
    st["bleed"] *= 0.45
    s.add_eff("packed", 200)
    s.pain = B.clamp(s.pain + 8.0)
    B.tick(s, 25)
    return ("You have it push cloth into the hole with two fingers, which hurts it more than "
            "the hole did, and hold it there until it stops coming through. It does not stop "
            "coming through. It slows down.")


# ---------------------------------------------------------------- the funnel
def strike(s, kind, cause, power=1.0, texts=None):
    """One lethal event. Returns (lines, ending_key_or_None).

    `texts` is a dict of the four outcome strings for the specific thing that happened - a
    harpoon does not read like a mine. Anything left out falls back to a generic line.
    """
    T = dict(texts or {})
    res = resistance(s) / max(0.35, power)
    lines = []

    if _moved_first(s) and s.rng.random() < 0.55:
        lines.append(T.get("aside",
                     "It is not where it was. Nothing you sent had time to arrive and it went "
                     "anyway, sideways and low and before the thing had finished happening."))
        B.hurt(s, s.rng.choice(["left arm", "right arm", "tail"]), s.rng.uniform(6, 14), "cut")
        B.tick(s, 12, exertion=1.4)
        return lines, None

    # how far over its resistance this thing is. 1 is an even match.
    x = max(0.35, float(power)) / res
    p_kill = max(0.02, min(0.42, 0.055 * x))
    p_down = max(0.05, min(0.42, 0.150 * x))
    p_through = max(0.08, min(0.50, 0.210 * x))
    roll = s.rng.random()
    if roll < p_kill:
        text = T.get("killed",
                     "It does not get to look down at this one. It is standing and then it is "
                     "not standing, and the distance between those two things is nothing at "
                     "all.")
        # queued rather than fired, so it goes through the one death funnel and gets the
        # same grit roll everything else gets - a body that does not go down the first time
        # it should does not go down the first time it should for this either
        s.pending_death = [kind, text]
        return [text], kind
    if roll < p_kill + p_down:
        chest_wound(s, 0.85, cause)
        lines.append(T.get("down",
                     "It goes through and the legs go with it. It is down on its side with "
                     "its own weight on the wound and it is still looking at you."))
        B.tick(s, 30, exertion=1.2)
        return lines, None
    if roll < p_kill + p_down + p_through:
        chest_wound(s, 0.62, cause)
        lines.append(T.get("standing",
                     "It stays up. That is the part neither of you expected."))
        B.tick(s, 20, exertion=1.1)
        return lines, None

    # it went through something that was not the middle of it
    limb = s.rng.choice(["left arm", "right arm", "left leg", "right leg"])
    B.hurt(s, limb, s.rng.uniform(26, 44), "cut")
    lines.append(T.get("graze",
                 "It goes through the %s instead of through the middle of it, which is the "
                 "whole of the difference between this and the other thing." % limb))
    B.tick(s, 18, exertion=1.2)
    return lines, None


# The user's line, and the shape everything else in here is written against: the body finds
# out what has happened to it by looking down at it.
IMPALED = ("You are suddenly alerted as %s is impaled clean through the chest.\n"
           "It stops. It does not make a sound. It slowly looks down at the shaft standing "
           "out of it, and its weight goes, and it folds down onto the floor around the thing "
           "still holding it up - and it lies there and watches itself bleed out, orange and "
           "unhurried, and it does not look away from it and it does not look at you.")


def impaled_text(s):
    return IMPALED % SUB.name(s)
