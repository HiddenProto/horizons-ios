"""What it does that nobody asked it to do.

Two channels, one call from the turn loop, and neither of them is ever explained in the game.

GESTURES is the loose one: a subject with `playful` in a good mood does things for no reason.
It is not a reward and it does not mean anything is going well - it means the mood is high
right now, and the same animal goes all the way down later.

TELLS is the other one. Every subject does a small number of specific things that do not fit
what the picker says about it, and each set adds up to one fact the game never states.
Rules for writing one:

  - it is BEHAVIOUR. Never an interpretation, never a hint, never a line telling the reader it
    was significant. If the text explains it, it is not a tell.
  - it has to be checkable. The ones that pay off repeat identically, or correlate with
    something the player can measure - 681's refusals against the real state of the body,
    682's humming against the link readout.
  - it stays true after the lore opens. The lore is the confirmation, not the content.

They surface as bare lines in the frame - no parentheses, which is what separates them from
the internal monologue - so a narrator reads them as events that happened rather than as
colour, and can put them together across a run.
"""
from . import subjects as SUB
from . import phones as PH

WINDOW = 55          # turns before the same tell can come round again
RATE = 0.115         # per turn, before the conditions cut it down
GESTURE_RATE = 0.17  # per turn, multiplied by `playful`


def _mood_ok(s, floor=58.0):
    return s.mood >= floor and not s.eff("clarity")


def _quiet(s):
    """Nothing is happening. Half of these only read right in a gap."""
    return not s.scene and not s.question and not getattr(s, "down", False)


# ---------------------------------------------------------------- small conditions
def _out(s):
    return getattr(s, "region", "outside") == "outside"


def _carried(s):
    inv = getattr(s, "inv", None) or {}
    return sum(v for v in inv.values() if isinstance(v, (int, float)))


def _night(s):
    return bool(getattr(s, "night", False))


def _cold(s):
    return s.warmth < 40


def _hot(s):
    return getattr(s, "heat", 0.0) > 25


def _hungry(s):
    return s.hunger > 60


def _tired(s):
    return s.fatigue > 60


def _hurt(s):
    return s.pain > 30


def _high(s):
    return s.mood >= 66


def _low(s):
    return s.mood < 40


def _flat(s):
    return s.mood < 25


# ---------------------------------------------------------------- the silly ones
# Every one of these is the same animal that catatonia happens to. That is the point of it:
# 0041 is the one that was kept in a room with people for years, and this is what it learned
# there, and it is still doing it out here where there is nobody to do it at.
# Entries are either a bare line or (weight, condition-or-None, line).
GESTURES = {
    "0041": [
        "Its tongue is out. Just the tip of it, off to one side, and it stays out for a while "
        "with nothing else about it changing, and then goes back in.",
        "It drops its front end flat to the ground and leaves its back end up, tail going, and "
        "holds the position for a second and a half. Nothing takes it up on it. It gets up.",
        "It picks up a stone that is no use to anybody, carries it a while, and sets it down "
        "somewhere else with what looks like satisfaction.",
        "It rolls over onto its back, all the way, feet in the air, in the middle of the "
        "ground you are trying to cross, and lies there.",
        "It taps the ground twice with one paw and looks up and waits. There is a shape to the "
        "waiting - it is waiting for a specific thing, and the specific thing does not come.",
        "It bumps the top of its head gently against the nearest solid surface and leaves it "
        "resting there.",
        "It chases something. There is nothing there. It stops, looks at where the nothing "
        "was, and goes back to what it was doing without embarrassment.",
        "It makes a sound you have not heard out of it before, high and short and twice, and "
        "then goes quiet and looks pleased with itself.",
        "Its tongue is out again. It has forgotten about it. It walks a good long way like that.",
        "It sneezes, looks startled by it, and then sneezes again on purpose, to see whether it "
        "happens the same way the second time.",
        "It pounces on its own shadow. Lands on it. Lifts one paw and looks underneath. "
        "Pounces again.",
        "It hops. Not over anything - a hop, all four feet at once - and then walks on as if "
        "that were an ordinary way to walk.",
        "It wriggles on its back in the dirt, grunting, until something has been scratched to "
        "its satisfaction, and gets up covered in it.",
        "It runs. Three wide loops at full speed, ears blown inside out, for no reason at all, "
        "and then stops dead and stands there panting with its mouth open.",
        "It tilts its head at a sound. Then all the way the other way. Then back again, "
        "further.",
        "It lies down with its chin on the stone it has been carrying, as though the stone were "
        "a pillow and it had chosen it.",
        "It catches its own tail in its mouth. Gently. Holds it. Lets go and looks at it as if "
        "the tail had done something interesting.",
        "It paws at the air in front of its face, slowly, one side then the other, as though "
        "there were a moth there made of nothing.",
        "It blows out hard through its nose at a pebble. The pebble does not move. It does it "
        "again, harder, and the pebble still does not move, and it seems fine with that.",
        "It is carrying a stone again. It is a different stone. This one has been chosen with "
        "more care.",
        "It gives one low 'wuff' at nothing and then holds very still, ears up, as though "
        "waiting to see whether anything wuffs back.",
        "It sits, lifts one front paw, and holds it out into the empty air at about the height "
        "of a hand. It holds it there a while. It puts it down.",
        "It noses a small round thing along the ground, follows it, noses it again, loses it "
        "into a crack, and looks into the crack for a very long time.",
        "It goes flat on its belly and creeps forward, very slowly, at nothing, and then "
        "springs up and away from the nothing all at once.",
        "It rubs one cheek along a rock, then the other cheek, then goes back and does the "
        "first cheek again because apparently the first one did not take.",
        "One ear is up and one is down. It stays like that for a long time and it does not "
        "seem to know.",
        "It yawns so wide that it squeaks at the end of it, and then looks round at the squeak.",
        "'m.. mm..' It is humming. No tune in it at all, eyes half shut, pleased.",
        "It sits down in the middle of the way, scratches one ear with great concentration, "
        "and then carries on exactly where it stopped.",
        "It lies on its side and lets its legs go in the air, slowly, running nowhere.",
        (2, lambda s: s.hunger < 25,
         "It licks its lips for a long time after there is nothing left on them."),
        (2, lambda s: _carried(s) >= 4,
         "It has put one of the things it is carrying on top of its own head and is walking "
         "very, very carefully so that it does not fall off."),
        (2, lambda s: _out(s),
         "It stops to sniff one single stalk of something growing, very thoroughly, from the "
         "bottom to the top, and sneezes on it."),
        (2, lambda s: _out(s) and not _night(s),
         "It finds a patch of light on the ground and sits in it. When the light moves, it "
         "shuffles over and sits in it again."),
        (3, lambda s: _out(s) and _night(s),
         "It lies on its back and looks up at the dark for a long time, and its tail moves "
         "slowly against the ground the whole time."),
        (2, lambda s: _cold(s),
         "It tucks its nose under its own tail and curls into a circle, and one eye stays open "
         "and on the way you are going."),
        (2, lambda s: s.distance > 30,
         "It turns round, looks at how far it has come, and its whole back end wags."),
    ],
    "2008": [
        "It shakes itself out, ears first, the way something does when it is comfortable.",
        "It puts its face into a handful of the ground for no reason and comes up with its "
        "nose covered, and does nothing about it.",
        "It snaps at a bit of something drifting in the air, catches it, and looks surprised "
        "to have done it.",
        "It trots a few steps sideways for no reason, and then straightens out as though it "
        "had meant to.",
        "It sneezes three times in a row, and after the third one it sits down to think about "
        "it.",
    ],
    "682": [
        "It bats at something moving, misses, and bats at it again far harder than the thing "
        "needed. The thing is now in pieces. It seems to feel this went well.",
        "It shoulder-checks a standing rock on the way past. Nothing was wrong with the rock.",
        "It chases its own tail round once at full speed, catches it, and bites down hard "
        "enough to yelp. It glares at the tail.",
        "It pounces on a clump of something growing and wrestles it thoroughly. The clump "
        "loses.",
        "It headbutts the air, twice, in time with something only it can hear.",
    ],
}


# ---------------------------------------------------------------- the ordinary ones
# Not mood-gated the way GESTURES is and not a secret the way TELLS is: just what this
# particular body does with itself when nobody is asking it for anything. Every subject has
# some, the lines shift with how it feels, and 0041's go down with it.
IDLES = {
    "0041": [
        (2, lambda s: not _low(s),
         "It grooms one foreleg carefully all the way down, starts on the other one, and "
         "wanders off halfway through it."),
        (2, lambda s: not _low(s),
         "It walks close to the nearest wall so that its side brushes along it the whole way."),
        (2, lambda s: not _low(s),
         "It lies down at every stop now, even the short ones, and gets up the moment it is "
         "asked."),
        (2, lambda s: _tired(s),
         "It falls asleep sitting up, tips slowly sideways, wakes as it goes over, and looks "
         "round to see who saw."),
        (2, lambda s: _hungry(s),
         "It sniffs at what it is carrying, then looks up, then sniffs at it again, and waits "
         "politely."),
        (3, lambda s: _low(s),
         "It lies down where it stopped with its chin flat to the ground. Its eyes follow the "
         "next order. Its head does not."),
        (3, lambda s: _low(s),
         "It picks up a stone and holds it in its mouth for a while and lets it drop. It does "
         "not carry it anywhere."),
        (3, lambda s: _low(s),
         "Its tail moves once when the link opens, and then not again."),
        (3, lambda s: _low(s),
         "It starts to roll over onto its back, gets halfway, stops, and rolls back."),
        (3, lambda s: _low(s),
         "It taps the ground twice with one paw. It does not look up this time."),
        (4, lambda s: _flat(s),
         "It has been looking at the same patch of ground for a long while. The tongue is not "
         "out. Nothing is."),
    ],
    "2008": [
        (2, None,
         "It stretches, front legs out long and its back end up, and then the other way round, "
         "back legs one at a time."),
        (2, None,
         "It scratches behind one ear with a hind foot, fast, and its mouth hangs open while "
         "it does."),
        (2, None,
         "It sniffs along the ground in a wide curve and comes back round to exactly where it "
         "started."),
        (2, None,
         "It yawns, and then shakes its head as though the yawn had got into its ears."),
        (2, lambda s: _high(s),
         "Its tail is up and it swings with the step."),
        (2, lambda s: _out(s) and _night(s),
         "It keeps glancing up. There is nothing up there it has a name for. It keeps "
         "glancing up."),
        (2, lambda s: _cold(s),
         "It fluffs out, all of it at once, and walks on at twice its size."),
        (2, lambda s: _hungry(s),
         "Its stomach makes a noise. It looks down at its own stomach as though the noise had "
         "come from somewhere else."),
        (2, lambda s: _tired(s),
         "It sits down in the middle of a step and has to be asked to finish it."),
        (2, lambda s: _out(s),
         "It licks the damp off a cold stone, methodically, until the stone is dry."),
    ],
    "1278": [
        (3, None,
         "It stands exactly where it was last put. It has not shifted its weight."),
        (2, None,
         "It sits square - front feet together, back straight, eyes forward - and holds it."),
        (2, None,
         "It grooms in quick short strokes and stops each time it thinks something is about "
         "to come down the link."),
        (2, None,
         "It rests lying down with its head up and facing forward. Its eyes do not close."),
        (2, None,
         "It has lined its front feet up with the edge of a flat stone."),
        (2, lambda s: _tired(s),
         "It is swaying on its feet. It does not sit down. Nobody has told it to."),
        (2, lambda s: _hurt(s),
         "It licks the sore place once, stops, and goes still as though it had been caught."),
        (2, lambda s: _cold(s),
         "It is shivering, and standing perfectly still, and the shivering is the only thing "
         "about it that moves."),
        (2, lambda s: _hungry(s),
         "It looks at the food it is carrying, and then forward, and then back at the food, "
         "and does nothing."),
        (2, lambda s: _night(s),
         "It keeps its eyes on the dark in the exact direction it was last sent."),
    ],
    "101": [
        (2, None,
         "It kicks a stone on purpose, watches where it goes, and then goes a different way."),
        (2, None,
         "It sits down facing away from the way you want to go. It is not refusing anything. "
         "It is sitting."),
        (2, None,
         "It yawns. Long, slow, and aimed."),
        (2, None,
         "It scratches its ear with the particular slowness of something that has been told "
         "to hurry."),
        (2, None,
         "'hm,' it says flatly, at a view that has not done anything to deserve it."),
        (2, None,
         "It goes the long way round a rock it could have stepped over, and then looks back "
         "at the rock."),
        (2, None,
         "It picks up something useless and holds on to it with great firmness for a while."),
        (2, lambda s: _tired(s),
         "It lies down without being told, and then looks up as though it is waiting to be "
         "told."),
        (2, lambda s: _hungry(s),
         "It chews a root it has found with its mouth open, noisily, staring straight ahead."),
        (3, lambda s: _low(s),
         "It is muttering, too low to make out. It stops when the link opens, and starts "
         "again when it closes."),
        (2, lambda s: _high(s),
         "It walks ahead a little, then stops and waits, then walks ahead again."),
    ],
    "7": [
        (3, None,
         "It sits where it can see the most ground at once. It did not look for the place. It "
         "went straight to it."),
        (2, None,
         "It rubs at an old scar along its foreleg with its thumb, slowly, back and forth."),
        (2, None,
         "It eats without looking at the food, eyes on the distance, and stops before it is "
         "finished and puts the rest away."),
        (2, None,
         "It checks every strap and tie on what it carries, in the same order, fast."),
        (2, lambda s: _out(s),
         "It tests the air, nose up, twice, and then shifts its line by a few degrees."),
        (2, lambda s: _tired(s),
         "It sleeps a few seconds standing up, wakes, and nothing else about it has changed."),
        (2, lambda s: _night(s),
         "It walks slower than it is asked to in the dark, and puts its feet down flat and "
         "silent."),
        (2, lambda s: _cold(s),
         "It gets its back to the wind before it stops anywhere. Every time."),
        (2, lambda s: _hurt(s),
         "It looks at the wound the way you look at a bill, and then gets on with the day."),
        (2, lambda s: _low(s),
         "It sits with its eyes shut for a while. It is not asleep. Its ears are still "
         "working."),
    ],
    "3350": [
        (3, None,
         "It cannot stand still. When it is stopped, its feet keep shifting underneath it as "
         "though it were still going."),
        (2, None,
         "It stretches its legs out one at a time, very long, the way something warms up."),
        (2, None,
         "It stops, presses one hand flat to its own chest, waits, and goes on as though it "
         "had not."),
        (2, None,
         "It sprints a short way for nothing - three, four strides, flat out - and drops back "
         "to a walk."),
        (2, None,
         "It lies still with one ear pressed against its own forearm. It is listening to "
         "something."),
        (2, lambda s: s.strain > 40,
         "Its breathing takes a long moment to come down. It stands with its mouth open until "
         "it does."),
        (2, lambda s: _high(s),
         "It bounces on the spot, twice, before it moves off."),
        (2, lambda s: _tired(s),
         "It lies flat out on its side with its legs stretched, sides going."),
        (2, lambda s: _hot(s),
         "It pants with its tongue out to the air and moves itself into the only patch of "
         "shade."),
    ],
    "680": [
        (3, None,
         "It sits with its back to something solid. It always sits with its back to something "
         "solid."),
        (2, None,
         "It cleans itself slowly and completely, the way a thing does when it has nowhere to "
         "be."),
        (2, None,
         "It goes a long time without making any sound at all. Not a breath you can hear."),
        (2, None,
         "It runs one hand over the plated places on its own body, checking the seams, and "
         "moves on."),
        (2, None,
         "It watches a moving thing at the edge of sight until the thing is gone. Nothing else "
         "about it moves."),
        (2, lambda s: _night(s),
         "It does not lie down. It sits up through the dark, and the eyes are the only light "
         "for a long way."),
        (2, lambda s: _hurt(s),
         "It does not favour the hurt limb. It walks on it exactly as it walked before."),
        (2, lambda s: _low(s),
         "It turns its face to the nearest wall and stays that way until the next order."),
    ],
    "682": [
        (3, None,
         "It startles at a sound - its own footstep - and spins round to face it."),
        (2, None,
         "It is chewing something. A strap. A stone. It does not appear to have chosen."),
        (2, None,
         "Its ears go two different ways, then both the other way, then both at once."),
        (2, None,
         "It flicks its head sideways, then again, then shakes all over, hard, like something "
         "wet."),
        (2, lambda s: SUB.trait(s, "phones"),
         "It scratches at the band of the headphones, stops, and scratches at it again."),
        (2, None,
         "It growls at a rock. Low and long. The rock is the same as the other rocks."),
        (2, lambda s: _tired(s),
         "It dozes, and its legs run in the doze."),
        (2, lambda s: _hungry(s),
         "It eats fast, with its whole head, and then looks round as though something were "
         "about to take it."),
        (2, lambda s: _hurt(s),
         "It snaps at the hurt place and snarls at it, as though the hurt place had started "
         "it."),
    ],
    "681": [
        (2, None,
         "It trips over nothing, loudly, and rights itself with one very precise step."),
        (2, None,
         "It flops down all at once, as though it had been shot, and watches from the ground "
         "with interest."),
        (2, None,
         "It sniffs something it has already sniffed. Loudly."),
        (2, None,
         "It scratches with a hind foot, and the rhythm is perfectly even."),
        (2, None,
         "It licks one paw and wipes its whole face with it, twice, fast."),
        (2, lambda s: _high(s),
         "It prances a few steps - there is no other word for it - and then glances inward, "
         "at the link."),
        (2, lambda s: _tired(s),
         "It lies down in exactly the spot you would have picked for it."),
        (3, lambda s: _low(s),
         "It chews at the fur on its own forearm until there is a bare patch, and stops when "
         "the link opens."),
        (3, lambda s: _low(s) and _out(s),
         "It walks to the edge of a drop and looks over it for a long time."),
    ],
    "4400": [
        (3, None,
         "It is looking at its own hand. Turning it over. Opening it and closing it."),
        (2, None,
         "It copies a sound - the wind, a stone falling - almost perfectly, and then does it "
         "again to check."),
        (2, None,
         "It sits down hard, on purpose, to find out how that feels."),
        (2, None,
         "It touches everything it passes, once, lightly, with one finger."),
        (2, None,
         "It sniffs its own arm, and then sniffs the other arm to compare."),
        (2, None,
         "It walks back a few steps in its own footprints, and then forward again, carefully, "
         "in the same ones."),
        (2, lambda s: _high(s),
         "'mm..' it says, to hear it, and then again, lower."),
        (2, lambda s: _out(s) and _night(s),
         "It stares up for a long time with its mouth a little open."),
        (2, lambda s: _cold(s),
         "It watches its own breath come out, and breathes out again to watch it."),
        (2, lambda s: _hungry(s),
         "It holds its stomach and looks down at it, as though the stomach had said something."),
        (2, lambda s: _hurt(s),
         "It looks at the blood on its fur for a long time. It touches it and looks at its "
         "finger. Orange."),
    ],
}

GESTURE_WINDOW = 30  # turns before the same gesture can come round again
IDLE_WINDOW = 40
IDLE_RATE = 0.085    # per quiet turn


def _entries(pool):
    for e in pool:
        if isinstance(e, str):
            yield 2, None, e
        else:
            yield e


def _pick(s, tag, pool, window):
    """Weighted pick from (w, cond, text) entries, skipping failed conditions and anything
    seen inside `window` turns. Shared by every channel so none of them repeats itself."""
    sid = getattr(s, "subject", "")
    seen = getattr(s, "tells_seen", None) or {}
    live = []
    for i, (w, cond, text) in enumerate(_entries(pool)):
        if cond is not None:
            try:
                if not cond(s):
                    continue
            except Exception:
                continue
        key = "%s%s:%d" % (tag, sid, i)
        if s.turn - int(seen.get(key, -999)) < window:
            continue
        live.append((w, key, text))
    if not live:
        return None
    r = s.rng.random() * sum(w for w, _, _ in live)
    for w, key, text in live:
        r -= w
        if r <= 0:
            if not isinstance(getattr(s, "tells_seen", None), dict):
                s.tells_seen = {}
            s.tells_seen[key] = s.turn
            return text
    return None


def gesture(s):
    p = SUB.trait(s, "playful")
    if p <= 0 or not _quiet(s) or not _mood_ok(s, 62.0):
        return None
    if s.pain > 45 or s.fatigue > 78 or s.blood < 55:
        return None
    if s.rng.random() >= GESTURE_RATE * p:
        return None
    return _pick(s, "g/", GESTURES.get(getattr(s, "subject", ""), []), GESTURE_WINDOW)


def idle(s):
    if not _quiet(s) or getattr(s, "crisis", None) or s.eff("clarity"):
        return None
    if s.rng.random() >= IDLE_RATE:
        return None
    return _pick(s, "i/", IDLES.get(getattr(s, "subject", ""), []), IDLE_WINDOW)


# ---------------------------------------------------------------- the ones that mean something
# sid -> list of (weight, condition-or-None, text)
TELLS = {
    # It thinks the number is a name. It is telling you its name, and nobody has ever answered.
    "2008": [
        (3, None,
         "It taps the ground with one claw. Twice. Then a long nothing, and another long "
         "nothing, and then eight taps, evenly spaced. Then it looks up and waits, and then "
         "goes back to what it was doing."),
        (2, lambda s: _carried(s) >= 4,
         "It has put what it is carrying into two groups on the ground, counted them, moved "
         "one item from the bigger group into the smaller, and picked it all up again."),
        (2, lambda s: s.hunger > 55,
         "There is one of something left and it will not open it. It turns it over twice and "
         "puts it back where it was."),
        (2, None,
         "It stops at a patch of ground that is the same as all the other ground and stands "
         "on it until you tell it to move."),
    ],
    # The pause is gone out of the decision. It is still in the body, and it arrives late.
    "1278": [
        (3, None,
         "It is moving before the order has finished arriving. Half a second later something "
         "goes through its shoulders - a flinch, a whole one - and by then it is committed, "
         "and it does not stop."),
        (3, None,
         "Its ears go flat after it obeys. Never before. Every time."),
        (2, None,
         "You have not asked it to watch behind you. It has done it nine times in the last "
         "hour, at almost even intervals."),
        (2, lambda s: s.pain > 30,
         "It dips its head at you after an order, the way something dips its head to be let "
         "off a thing."),
        (2, lambda s: (s.scene or {}).get("danger", 0.0) > 0.4,
         "It goes in. On the way its tail tucks so far under it that its whole gait changes, "
         "and it does not slow down, and it does not look at you."),
    ],
    # It is having an argument. It is not having it with you.
    "101": [
        (3, None,
         "It answers something. You have not said anything for a while. Whatever it is "
         "answering, it answers the way you answer a thing you have answered before."),
        (3, None,
         "It calls you something. Four syllables, the same four it used yesterday, and when "
         "you ask it to repeat them it does not."),
        (2, None,
         "'you said that last time,' it says. You have not said it. Nobody has said it."),
        (2, lambda s: s.chip < 85,
         "It stops arguing, reaches up and puts two fingers on the back of its own skull where "
         "the seating is, holds them there a moment, and carries straight on arguing."),
        (2, lambda s: s.weird > 40,
         "'how many of you have there been,' it says. It is not a question it waits on."),
    ],
    # It is still waiting for the room, and it has not stopped being ready for it.
    "0041": [
        (3, None,
         "It sets down what it is carrying and then moves it, so there is a clear space beside "
         "it exactly wide enough for something to sit in. Then it sits in the other half."),
        (3, None,
         "It holds its head still at about waist height, out in the open, for several seconds. "
         "Nothing arrives. It carries on."),
        (2, None,
         "One paw is clean. It has been keeping one paw clean all day and the rest of it is "
         "filthy."),
        (2, lambda s: s.mood < 45,
         "It has started looking at the horizon less and at the middle distance more, at about "
         "the height a doorway would be."),
    ],
    # The body remembers the walk. The part that saw it is the part they wipe.
    "7": [
        (3, None,
         "It takes a line across the broken ground that is shorter than the one you were about "
         "to give it. It takes it before it has looked at the ground."),
        (3, None,
         "It will not put weight on one particular patch of ground. There is nothing wrong with "
         "the patch. It goes round, and afterwards does not appear to know that it did."),
        (2, None,
         "It checks the strut without looking at it - two fingers, one turn, done - the way you "
         "check something you have checked every day for years."),
        (2, lambda s: s.distance > 40,
         "You have never told it what is at the end of this. It has never once asked."),
        (2, lambda s: s.weird > 35,
         "It says a word that is not in its vocabulary, clearly, and then looks as though the "
         "word arrived from outside it."),
    ],
    # Built for a distance nobody told it. It is pacing against a number it was never given.
    "3350": [
        (3, None,
         "It looks back the way it came more often than it looks the way it is going."),
        (3, lambda s: s.distance > 25,
         "It is holding an exact pace. The ground has changed three times and the pace has not, "
         "and the pace does not suit any of the three."),
        (2, lambda s: s.strain > 40,
         "It eases off. Nothing has changed - same ground, same light - and a moment later it "
         "goes again, harder, as though it had been handed back something it had spent."),
        (2, lambda s: s.distance > 55,
         "Its breathing has gone into a pattern with a shape to it. Three and three and three. "
         "It is not a breathing pattern. It is a counting one."),
    ],
    # It is what they practised on. The silence is not damage, and the tapping is not a
    # nervous habit - the spacing does not vary.
    "680": [
        (3, None,
         "It taps a solid surface with one knuckle. Short, short, long. The gaps are identical "
         "to the last time it did it, and to the time before that."),
        (3, None,
         "It has put itself between the body and the nearest thing again, without being told, "
         "and it has done it on the side where you cannot see."),
        (2, lambda s: s.issues or s.pain > 40,
         "It moves the limb into position before you have said which limb."),
        (2, None,
         "It watches what is being done to it with something that is not fear. It is checking "
         "the work."),
        (2, lambda s: s.weird > 40,
         "It looks at a wall a while. Then it puts one hand flat on it at head height and "
         "leaves it there, and takes it away again, and does not react."),
    ],
    # The file says the sound predates the set, which is not possible, and nobody followed it
    # up. The link readout is the only instrument in here that agrees with the file.
    "682": [
        (3, None,
         "It is keeping time with one foot. The time does not match anything - not its step, "
         "not its pulse, not the ground."),
        (3, lambda s: SUB.trait(s, "phones") and not PH.playing(s),
         "The cups are dead. Nothing is coming out of them, and it is still keeping time, at "
         "exactly the rate it was keeping before they broke."),
        (3, None,
         "It hums. Two notes a tone apart, over and over. While it does, the link figure on "
         "your own readout moves in time with it."),
        (2, None,
         "It turns its head sharply at nothing. To the left. It is always to the left, and it "
         "is always the same angle."),
        (2, lambda s: s.snap > 40,
         "It puts one hand over the cup on the left side and presses, hard, and holds it "
         "there, and then lets go."),
    ],
    # The one the file is careful about. It is not what the picker says it is, and it is going
    # to real trouble to make sure that is what you think.
    "681": [
        (4, None,
         "It takes the wire out on the way past without breaking stride and without appearing "
         "to look at it. Then it goes back and sniffs at it loudly and makes a performance of "
         "having found it."),
        (4, lambda s: _carried(s) >= 3,
         "What it is carrying is in an order. You did not put it in an order. When it wants "
         "something it does not look for it."),
        (4, lambda s: s.distance > 15,
         "Everything it has gone at today has been between the body and the direction you have "
         "been sending it. Every one. It has not gone at a single thing that was not."),
        (3, None,
         "It sets the light down at the mouth of the passage instead of carrying it in. Coming "
         "back out an hour later, the passage is lit."),
        (3, None,
         "It is making a great deal of noise and its feet are doing something extremely "
         "careful, and the two do not go together at all."),
        (3, lambda s: s.turn > 20,
         "It answers a question you asked it a long time ago. Correctly. While doing something "
         "else, without stopping, and without checking whether you noticed."),
        (3, None,
         "It looks at the printed side of something for slightly too long. Not the way an "
         "animal looks at a pattern. It puts it down the moment it notices you watching."),
        (2, lambda s: (s.scene or {}).get("danger", 0.0) > 0.3,
         "The noise stops the instant the ground changes and starts again when the ground is "
         "good. Both times, the noise is the part that is deliberate."),
        (2, lambda s: s.refusals >= 3,
         "It has refused you several times today. Reading back what it was doing each time, "
         "there is nothing in common in what it said, and something in common in the body."),
    ],
    # It has never had a thought arrive from anywhere else, and it has no word for the chip.
    "4400": [
        (4, None,
         "'we should go,' it says. And then, a moment later and quieter: 'i should go.'"),
        (4, None,
         "It answers a question. You had not asked it. You were about to."),
        (3, lambda s: s.intel > 20,
         "It reads the label out. The label is about it. Nothing in its voice changes at any "
         "point while it does."),
        (3, lambda s: s.chip < 90,
         "It apologises. Not for anything it has done - it apologises for the noise, as though "
         "the noise were something it was doing."),
        (2, None,
         "It says one of your own words back to you, in your own construction, flatly, as its "
         "own observation."),
        (2, lambda s: s.weird > 45,
         "'which of this is me,' it says. It does not appear distressed by the question. It "
         "appears to be trying to do arithmetic."),
    ],
}


def _pool(s):
    sid = getattr(s, "subject", "")
    seen = getattr(s, "tells_seen", None) or {}
    out = []
    for i, (w, cond, text) in enumerate(TELLS.get(sid, [])):
        if cond is not None:
            try:
                if not cond(s):
                    continue
            except Exception:
                continue
        key = "%s:%d" % (sid, i)
        if s.turn - int(seen.get(key, -999)) < WINDOW:
            continue
        out.append((w, key, text))
    return out


def tell(s):
    if not _quiet(s):
        return None
    if s.rng.random() >= RATE:
        return None
    pool = _pool(s)
    if not pool:
        return None
    total = sum(w for w, _, _ in pool)
    r = s.rng.random() * total
    for w, key, text in pool:
        r -= w
        if r <= 0:
            if not isinstance(getattr(s, "tells_seen", None), dict):
                s.tells_seen = {}
            s.tells_seen[key] = s.turn
            return text
    return None


def maybe(s):
    """One line at most per turn: the tell first, then the silly one, then the ordinary one."""
    if getattr(s, "over", False):
        return None
    t = tell(s)
    if t:
        return t
    return gesture(s) or idle(s)
