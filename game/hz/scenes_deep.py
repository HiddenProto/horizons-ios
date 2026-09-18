"""Scenarios for the ground under the test: the four crust layers and the six core layers.

Kept out of scenarios.py so that file stays the surface bank. build_deep() is handed the SC and
O constructors by scenarios.py at import time, which is what keeps this from being a circular
import.

House rules followed here: every option does something mechanical, options that need a limb or
an item are gated with req so they are never offered as a lie, and the deeper banks lean on the
systems the deeper regions switch on - complications, manufactured medicine, intelligence.
"""
from . import body as B
from . import items as I


def _hurt(s, limb, amount, kind="blunt"):
    B.hurt(s, limb, amount, kind)


def _issue(s, kind):
    s.pending_issues.append(kind)


def _sleep_nest(s):
    """Sleeping in something else's bed, with the something else still alive."""
    B.tick(s, 240, resting=True)
    s.add_eff("rested", 200)
    s.stats["sleeps"] = s.stats.get("sleeps", 0) + 1
    if s.rng.random() < 0.30:
        limb = s.rng.choice(["left leg", "right leg"])
        _hurt(s, limb, s.rng.uniform(14, 26), "bite")
        return ("Something comes back for its bed while you are still in it. You get out of the "
                "hollow with your %s in its mouth for part of the way." % limb)
    return ("You sleep in something else's bed, in something else's smell, and nothing comes "
            "back for it. You wake up warm and obscurely ashamed of how well you slept.")


def _water_the_dying(s):
    if not I.take(s, "water", 1):
        return "You have no water to give it."
    s.mood = B.clamp(s.mood + 12)
    s.will = B.clamp(s.will + 6)
    B.tick(s, 20)
    return ("You put water into its mouth a swallow at a time, and it drinks. It does not get "
            "up and it does not stop watching you, and in the end you have to be the one who "
            "leaves.")


def _take_food_only(s):
    I.give(s, "ration", 2)
    s.mood = B.clamp(s.mood + 5)
    B.tick(s, 8)
    return ("You take the two blocks and put the flap back the way it was. It matters to you "
            "that it is left the way it was, and you could not say why.")


def build_deep(SC, O):
    # ============================================================ CRUST: the shaft head
    def _climb_down(s):
        B.tick(s, 26, exertion=1.5)
        s.distance += 2.2
        if s.rng.random() < 0.30:
            limb = s.rng.choice(["left arm", "right arm"])
            _hurt(s, limb, s.rng.uniform(9, 17), "cut")
            return ("You take the rungs. One of them is not a rung any more and your %s pays "
                    "for finding that out. You keep going down." % limb)
        return ("You take the rungs hand over hand. The shaft swallows the light above you at "
                "a rate you can measure against your own breathing.")

    def _ride_bucket(s):
        B.tick(s, 12, exertion=0.7)
        s.distance += 4.0
        if s.rng.random() < 0.22:
            _hurt(s, "tail", s.rng.uniform(10, 20), "crush")
            s.weird = B.clamp(s.weird + 5)
            return ("The counterweight bucket takes you down fast and then stops the way a "
                    "dropped thing stops. Your tail is under you when it lands.")
        return ("You fold into the counterweight bucket and let the shaft do the work. It is "
                "the first time since the room that something has carried you.")

    def _read_board(s):
        s.learn("The test above is one stage of something with stages below it.")
        from . import intel as IN
        IN.gain(s, "read")
        B.tick(s, 8)
        return ("A board at the shaft head, hand-corrected many times: SURFACE TRIAL / CRUST / "
                "CORE, and a column of numbers beside each. The surface column has the most "
                "entries in it. The core column has two.")

    crust_shaft = [
        SC("shafthead_down",
           "The bore goes down in a straight line with rungs on one wall and a counterweight "
           "bucket on a cable on the other. Warm air comes up past your face on the way.",
           [O("Take the rungs down", _climb_down, lambda s: B.arms_usable(s) >= 1),
            O("Ride the counterweight bucket", _ride_bucket),
            O("Read the board bolted at the head of it", _read_board)],
           zones=["shaft"], w=34),

        SC("shafthead_kit",
           "Somebody's kit is stacked at the head of the shaft, squared away by a person who "
           "expected to come back for it.",
           [O("Take all of it", lambda s: (I.give(s, "cord", 2), I.give(s, "cloth", 2),
                                           I.give(s, "ration", 2), B.tick(s, 14),
                                           "You take the cord, the cloth and the food. "
                                           "Whoever squared this away is not coming back for "
                                           "it, and you know that without being able to say "
                                           "how you know it.")[-1]),
            O("Take only the food and leave the rest squared away", _take_food_only),
            O("Leave it", lambda s: (B.tick(s, 3), "You leave it where it is.")[-1])],
           zones=["shaft"], once=True, w=30),

        SC("shafthead_hot",
           "The air coming up the shaft is warmer than the air going down, and it smells of "
           "something working.",
           [O("Go down into it anyway",
              lambda s: (B.tick(s, 20, exertion=1.2), s.__setattr__(
                  "warmth", B.clamp(s.warmth + 8)),
                  "You go down into the warm. Your hands stop aching for the first time since "
                  "the wire.")[-1]),
            O("Rest here where the temperature suits you",
              lambda s: (B.tick(s, 120, resting=True), s.add_eff("rested", 200),
                         "You sleep at the lip of the shaft in air that is finally the right "
                         "temperature, and wake up with most of yourself back.")[-1])],
           zones=["shaft"], w=22),
    ]

    # ============================================================ CRUST: the galleries
    def _open_locker(s):
        from . import intel as IN
        I.give(s, "coagulant", 1)
        if s.rng.random() < 0.5:
            I.give(s, "antisepsis", 1)
        B.tick(s, 16)
        known = IN.identified(s, "coagulant")
        tail = ("You know what they are." if known else
                "You have no idea what either of them is. They go in the pack anyway.")
        return ("A medical locker, forced once already and then closed again. Inside: flat "
                "sealed packets and a crush tube. " + tail)

    def _read_log(s):
        s.learn("The ones running this write things down about you, and the notes are not kind.")
        from . import intel as IN
        IN.gain(s, "read")
        B.tick(s, 12)
        return ("A log book, left open. The last legible line is about a subject that 'declines "
                "instruction under load but resumes unprompted', and there is a number beside "
                "it, and the number is not yours. There are pages of this.")

    def _sleep_bunk(s):
        B.tick(s, 300, resting=True)
        s.add_eff("rested", 260)
        s.add_eff("sheltered", 200)
        s.mood = B.clamp(s.mood + 10)
        s.stats["sleeps"] = s.stats.get("sleeps", 0) + 1
        return ("You sleep in a made bunk, in a room with a door that closes, for the first "
                "time in your life. You wake up in it warm and you lie there a while not "
                "getting up.")

    def _drink_tank(s):
        I.give(s, "water", 4)
        B.tick(s, 14)
        if s.rng.random() < 0.28:
            s.infection = B.clamp(s.infection + 14)
            _issue(s, "fever")
            return ("The gallery tank still holds water. You fill up and drink deep, and about "
                    "an hour later your gut starts telling you what was living in it.")
        return "The gallery tank still holds clean water. You fill everything you have."

    crust_galleries = [
        SC("gal_locker",
           "A steel locker set into the gallery wall with a red cross scratched into the paint "
           "and then painted over.",
           [O("Force it open", _open_locker, lambda s: B.arms_usable(s) >= 1),
            O("Leave it - whatever is in there is not for you",
              lambda s: (B.tick(s, 4), "You leave it shut.")[-1])],
           zones=["galleries"], w=32),

        SC("gal_log",
           "There is a desk down here, and a chair pushed back from it, and a log book open on "
           "the desk with a pen still lying in the gutter of it.",
           [O("Read the log", _read_log),
            O("Close it and move on",
              lambda s: (B.tick(s, 4), s.__setattr__("weird", B.clamp(s.weird + 3)),
                         "You close the book. Something about the handwriting stays with you.")[-1])],
           zones=["galleries"], once=True, w=34),

        SC("gal_bunk",
           "Sleeping quarters, four bunks, all of them made. The dust says nobody has been in "
           "here for a very long time and the made beds say they meant to come back.",
           [O("Sleep in one", _sleep_bunk),
            O("Fill up from the water tank instead", _drink_tank),
            O("Strip the bedding for cloth",
              lambda s: (I.give(s, "cloth", 4), B.tick(s, 12),
                         "You strip all four bunks. It feels like doing damage, and you do it "
                         "anyway, because cloth is cloth.")[-1])],
           zones=["galleries"], w=30),
    ]

    # ============================================================ CRUST: the root level
    def _cut_through(s):
        s.stats["fights"] = s.stats.get("fights", 0) + 1
        B.tick(s, 30, exertion=1.5)
        if I.armed(s) or I.has(s, "shard"):
            s.distance += 2.6
            roll = s.rng.random()
            if roll < 0.10:
                limb = s.rng.choice(["left arm", "right arm", "tail"])
                B.sever(s, limb)
                _issue(s, "haemorrhage")
                return ("You cut a way through the root wall and it closes on you while you are "
                        "inside it. You get out. Your %s does not come with you." % limb)
            if roll < 0.40:
                limb = s.rng.choice(["left arm", "right arm", "tail"])
                _hurt(s, limb, s.rng.uniform(12, 24), "cut")
                _issue(s, "reopened")
                return ("You cut a way through the root wall. It closes on your %s while you "
                        "are halfway through and you have to cut yourself out of it too." % limb)
            return ("You cut a way through the root wall, strand by strand. It bleeds something "
                    "that is not orange and does not stop.")
        limb = s.rng.choice(["left arm", "right arm"])
        _hurt(s, limb, s.rng.uniform(16, 28), "cut")
        return ("You try to tear the root wall open with your hands. The wall wins and your %s "
                "is what it wins with." % limb)

    def _go_around(s):
        B.tick(s, 70, exertion=1.25)
        s.distance += 0.8
        return ("You follow the root wall until it gives you a gap. It costs most of an "
                "afternoon and almost no ground, and nothing bites you.")

    def _eat_root(s):
        I.give(s, "meat", 2)
        B.tick(s, 18)
        if s.rng.random() < 0.30:
            s.weird = B.clamp(s.weird + 12)
            s.pending_voice.append("weird")
            return ("You cut flesh out of the root and eat some of it on the spot. It is warm "
                    "and it tastes like the inside of your own mouth, and for a while "
                    "afterwards you are not sure which of you is eating.")
        return ("You cut flesh out of the root wall. It is warm, it is edible, and it does not "
                "appear to mind.")

    crust_roots = [
        SC("root_wall",
           "The tunnel ends in root - not blocked by it, made of it. Warm to the hand, and "
           "it is moving slowly in a way you can only see by looking away from it.",
           [O("Cut through it", _cut_through),
            O("Follow it until it gives you a gap", _go_around),
            O("Cut flesh out of it and eat", _eat_root)],
           zones=["roots"], w=36, danger=0.5),

        SC("root_thing",
           "Something long is coming down the root corridor toward you and it is not hurrying, "
           "which is worse than if it were.",
           [O("Put something between you and it",
              lambda s: (s.stats.__setitem__("fights", s.stats.get("fights", 0) + 1),
                         B.tick(s, 20, exertion=1.4),
                         "It sets the %s and holds it there, and the thing stops short of it, "
                         "considers, and goes back the way it came. Neither of you relaxes for "
                         "an hour." % (I.weapon(s)[0] or "haft"))[-1],
              lambda s: I.armed(s)),
            O("Get into the root wall and hold still",
              lambda s: (s.add_eff("hidden", 40), B.tick(s, 40, exertion=0.8),
                         "You press yourself into the warm wall and hold. It goes past close "
                         "enough that you feel the air move.")[-1]),
            O("Run", lambda s: (B.tick(s, 18, exertion=1.9),
                                s.__setattr__("strain", B.clamp(s.strain + 18)),
                                s.__setattr__("distance", s.distance + 1.6),
                                "You run. It does not follow, or it does not need to.")[-1])],
           zones=["roots"], w=30, danger=0.7),

        SC("root_nest",
           "A hollow in the root packed with something's bedding, and the something is not in "
           "it right now.",
           [O("Take what is worth taking, fast",
              lambda s: (I.give(s, "hide", 2), I.give(s, "cord", 2), I.give(s, "meat", 1),
                         B.tick(s, 12, exertion=1.3),
                         "Hide, cord and a piece of meat, and you are out of the hollow before "
                         "you have finished deciding to be.")[-1]),
            O("Sleep in it - it is the warmest thing down here", _sleep_nest),
            O("Leave it alone", lambda s: (B.tick(s, 4), "You leave the nest alone.")[-1])],
           zones=["roots"], w=26, danger=0.55),
    ]

    # ============================================================ CRUST: the thermals
    def _cross_hot(s):
        B.tick(s, 26, exertion=1.5)
        s.distance += 2.4
        for limb in ("left leg", "right leg"):
            _hurt(s, limb, s.rng.uniform(10, 20), "burn")
        s.warmth = B.clamp(s.warmth + 22)
        _issue(s, "cooked")
        if s.rng.random() < 0.12:
            B.sever(s, "tail")
        return ("You wade the hot water. It comes to your chest and it is past the temperature "
                "where it hurts and into the temperature where it simply removes things. You "
                "get across. Your legs are not the same afterwards.")

    def _wait_shift(s):
        B.tick(s, 150, resting=True)
        s.distance += 1.0
        return ("You wait the vents out. They breathe in shifts, and between two of them there "
                "is a window where the water is only very hot, and you use it.")

    def _build_raft(s):
        if not I.has(s, "branch", 2):
            return "You have nothing to build a float out of."
        I.take(s, "branch", 2)
        B.tick(s, 44, exertion=1.1)
        s.distance += 2.8
        return ("You lash branches into something that floats badly and cross on top of it, "
                "keeping everything you care about out of the water.")

    crust_thermals = [
        SC("therm_water",
           "Standing water across the whole width of the passage, breathing steam in slow "
           "shifts. Too hot to cross and too wide to go round.",
           [O("Wade it now and take the burns", _cross_hot),
            O("Wait for the vents to shift", _wait_shift),
            O("Build a float out of branches", _build_raft, lambda s: I.has(s, "branch", 2))],
           zones=["thermals"], w=38, danger=0.6),

        SC("therm_vent",
           "A vent in the floor with a grid over it, breathing dry heat upward hard enough to "
           "move the fur on your legs.",
           [O("Stand over it and get warm through",
              lambda s: (s.__setattr__("warmth", B.clamp(s.warmth + 26)),
                         B.tick(s, 40, resting=True),
                         "You stand over the grid until the cold is out of your bones. It is "
                         "the best you have felt since you woke up.")[-1]),
            O("Dry everything you are carrying over it",
              lambda s: (s.effects.pop("wet", None), I.give(s, "charcoal", 2), B.tick(s, 30),
                         "You dry yourself and your kit out over the grid, and char a couple of "
                         "branch ends black while you are at it.")[-1]),
            O("Look down through the grid",
              lambda s: (s.learn("There is something below the crust that the crust was dug "
                                 "to reach."), B.tick(s, 8),
                         "You put your eye to the grid. A long way down there is light that is "
                         "not fire and is not your eyes, and it is arranged in lines.")[-1])],
           zones=["thermals"], w=30),

        SC("therm_body",
           "A subject is sitting against the wall in the heat, and it has been sitting there "
           "long enough for the heat to have finished with it.",
           [O("Search it", lambda s: (I.give(s, "nerveblock", 1), I.give(s, "cloth", 2),
                                      s.__setattr__("mood", B.clamp(s.mood - 8)),
                                      s.__setattr__("weird", B.clamp(s.weird + 6)),
                                      B.tick(s, 16),
                                      "An ampoule with a folded needle, and cloth. Its build is "
                                      "your build. Its number is not your number.")[-1]),
            O("Sit with it a while",
              lambda s: (B.tick(s, 60, resting=True), s.__setattr__("mood", B.clamp(s.mood - 3)),
                         s.__setattr__("will", B.clamp(s.will + 6)),
                         "You sit down beside it in the heat and do nothing useful for an hour. "
                         "Afterwards you take orders better, and neither of you could say why.")[-1]),
            O("Go past it", lambda s: (B.tick(s, 4), s.__setattr__(
                "weird", B.clamp(s.weird + 4)), "You go past without looking at it again.")[-1])],
           zones=["thermals"], once=True, w=28),
    ]

    # ============================================================ CORE: the long descent
    def _free_climb(s):
        B.tick(s, 34, exertion=1.7)
        if s.rng.random() < 0.40:
            limb = s.rng.choice(["left leg", "right leg", "left arm", "right arm"])
            _hurt(s, limb, s.rng.uniform(16, 30), "blunt")
            _issue(s, "crush")
            return ("You climb down rock that was never meant to be climbed and it lets go of "
                    "you twice. The second time your %s takes the whole fall." % limb)
        s.distance += 3.0
        return ("You climb down rock that was never meant to be climbed, and it holds, and you "
                "arrive at the bottom of it with everything you started with.")

    def _rope_down(s):
        if not I.has(s, "cord", 2):
            return "You do not have the cord for it."
        I.take(s, "cord", 2)
        B.tick(s, 44, exertion=1.2)
        s.distance += 3.4
        return ("You run cord around a spur and lower yourself on it in stages. It is slow and "
                "it is correct and nothing about it hurts.")

    core_descent = [
        SC("desc_drop",
           "The rungs stop. Below them the rock goes down in a series of drops, each one about "
           "the height of the room you woke up in.",
           [O("Free climb it", _free_climb),
            O("Rig cord and lower yourself", _rope_down, lambda s: I.has(s, "cord", 2)),
            O("Look for a way that is not straight down",
              lambda s: (B.tick(s, 80, exertion=1.1), s.__setattr__(
                  "distance", s.distance + 1.2),
                  "You spend hours finding a ramp instead of a drop. It works. It costs the "
                  "afternoon.")[-1])],
           zones=["descent"], w=36, danger=0.55),

        SC("desc_pressure",
           "Your ears have stopped equalising and something behind your eyes is keeping time "
           "with your pulse. The air down here is thicker than air should be.",
           [O("Sit until it settles",
              lambda s: (B.tick(s, 90, resting=True), s.__setattr__(
                  "weird", B.clamp(s.weird - 8)), s.__setattr__("pain", B.clamp(s.pain - 6)),
                  "You sit with your head down until the pressure becomes ordinary. It does, "
                  "eventually, which is its own kind of bad news.")[-1]),
            O("Push on through it",
              lambda s: (B.tick(s, 30, exertion=1.4), s.__setattr__(
                  "weird", B.clamp(s.weird + 10)), s.__setattr__("distance", s.distance + 2.0),
                  "You keep going down with your head full of your own heartbeat.")[-1])],
           zones=["descent"], w=28),

        SC("desc_voice",
           "Something is transmitting down here, faintly, on whatever channel the chip uses, "
           "and it is not you.",
           [O("Listen to it",
              lambda s: (s.learn("The chip is not the only thing that has ever spoken into "
                                 "this body, and it will not be the last."),
                         s.__setattr__("weird", B.clamp(s.weird + 9)), B.tick(s, 20),
                         "You hold the link open and let it come through. It is instructions. "
                         "They are not in your voice and they are not for it.")[-1]),
            O("Shut the channel and keep walking",
              lambda s: (s.__setattr__("chip", B.clamp(s.chip - 4)), B.tick(s, 10),
                         "You close the link down to the narrowest thing that still carries an "
                         "order. The interference stops. So does some of your bandwidth.")[-1])],
           zones=["descent"], once=True, w=26),
    ]

    # ============================================================ CORE: the boneyard
    def _search_own_build(s):
        from . import intel as IN
        s.learn("There have been others with your build, and this is where their runs ended.")
        IN.gain(s, "read")
        I.give(s, "marrow", 1)
        s.mood = B.clamp(s.mood - 14)
        s.weird = B.clamp(s.weird + 10)
        B.tick(s, 24)
        return ("You go through one that is built like you. Behind its ear there is a scar in "
                "the shape of the thing behind your ear. In its kit there is a cold grey sleeve "
                "you take without knowing what it is for.")

    def _take_chip(s):
        s.weird = B.clamp(s.weird + 11)
        s.chip = B.clamp(s.chip + 6)
        s.mood = B.clamp(s.mood - 10)
        B.tick(s, 30)
        s.learn("A chip can be taken out of a subject, and the subject goes on without it.")
        return ("You dig the chip out of the dead one with a shard. It is inert and it is the "
                "same shape as the pressure behind your own ear. Yours runs a little cleaner "
                "for having seen one from the outside.")

    def _bury(s):
        B.tick(s, 120, exertion=1.2)
        s.mood = B.clamp(s.mood + 16)
        s.will = B.clamp(s.will + 10)
        s.fatigue = B.clamp(s.fatigue + 12)
        return ("You spend the better part of a day moving rock over the ones that are your "
                "build. It achieves nothing that can be measured. Afterwards it takes orders "
                "from you like something that has decided to keep going.")

    core_boneyard = [
        SC("bone_field",
           "The floor is other subjects. Not piled - stopped, each one where it stopped, in the "
           "posture it stopped in. Some of them are your build.",
           [O("Search the one built like you", _search_own_build),
            O("Cut the chip out of one and look at it", _take_chip,
              lambda s: B.arms_usable(s) >= 1 and I.has(s, "shard")),
            O("Cover them over", _bury)],
           zones=["boneyard"], once=True, w=44),

        SC("bone_still_going",
           "One of them is not finished. It is lying on its side with its eyes lit the same "
           "orange as yours and it is watching you arrive without moving anything else.",
           [O("Give it water", _water_the_dying, lambda s: I.has(s, "water")),
            O("End it",
              lambda s: (s.__setattr__("mood", B.clamp(s.mood - 20)),
                         s.__setattr__("weird", B.clamp(s.weird + 12)),
                         s.__setattr__("will", B.clamp(s.will - 8)), B.tick(s, 14),
                         "You do it quickly. It does not resist you at all, which is the part "
                         "you keep.")[-1]),
            O("Leave it as it is",
              lambda s: (s.__setattr__("mood", B.clamp(s.mood - 10)),
                         s.__setattr__("weird", B.clamp(s.weird + 8)), B.tick(s, 6),
                         "You walk on. The light behind you does not go out for a long time.")[-1])],
           zones=["boneyard"], once=True, w=34, danger=0.2),

        SC("bone_kit",
           "Kit, scattered across the floor of the boneyard in the quantity that comes off "
           "twenty bodies.",
           [O("Take everything medical you can carry",
              lambda s: (I.give(s, "coagulant", 1), I.give(s, "antisepsis", 1),
                         I.give(s, "bandage", 2), B.tick(s, 26),
                         "Packets, a tube, and dressings. You cannot read most of it and you "
                         "take all of it.")[-1]),
            O("Take hide and cord for building",
              lambda s: (I.give(s, "hide", 3), I.give(s, "cord", 3), B.tick(s, 22),
                         "Hide and cord, enough to build something with.")[-1]),
            O("Take nothing off them",
              lambda s: (s.__setattr__("mood", B.clamp(s.mood + 6)), B.tick(s, 4),
                         "You take nothing. It is not a practical decision and you make it "
                         "anyway.")[-1])],
           zones=["boneyard"], w=30),
    ]

    # ============================================================ CORE: the glassways
    def _walk_glass(s):
        B.tick(s, 28, exertion=1.4)
        s.distance += 2.6
        if s.rng.random() < 0.45:
            limb = s.rng.choice(["left leg", "right leg"])
            _hurt(s, limb, s.rng.uniform(14, 26), "cut")
            _issue(s, "haemorrhage")
            return ("You walk the glass. It holds your weight right up until it does not, and "
                    "what is under it opens your %s along its length." % limb)
        return ("You walk the glass tunnel on the flats of your pads, slowly, and it holds.")

    def _pad_feet(s):
        if not I.has(s, "cloth", 2):
            return "You have no cloth to bind your feet with."
        I.take(s, "cloth", 2)
        B.tick(s, 38, exertion=1.2)
        s.distance += 2.2
        return ("You bind cloth around both feet in pads and cross on those. The glass still "
                "breaks. It stops mattering that it breaks.")

    core_glassways = [
        SC("glass_floor",
           "The tunnel is lined with something that cooled too fast, and it is holding the "
           "shape of the last thing that came through here at speed. The floor of it is edges.",
           [O("Walk it as you are", _walk_glass),
            O("Bind cloth round your feet first", _pad_feet, lambda s: I.has(s, "cloth", 2)),
            O("Crawl it and spread your weight",
              lambda s: (B.tick(s, 60, exertion=1.3), s.__setattr__(
                  "distance", s.distance + 1.6), s.__setattr__(
                      "strain", B.clamp(s.strain + 12)),
                  "You go along on all fours with your weight spread wide. It takes twice as "
                  "long and your shoulders pay for it instead of your feet.")[-1])],
           zones=["glassways"], w=40, danger=0.6),

        SC("glass_shape",
           "There is a shape held in the glass of the wall: something long, mid-stride, caught "
           "when whatever happened here happened. It is not built like anything you have seen.",
           [O("Look at it properly",
              lambda s: (s.learn("Whatever the core is for, something was already living in it."),
                         s.__setattr__("weird", B.clamp(s.weird + 12)), B.tick(s, 14),
                         "You look at it until you have it. Six limbs, no eyes anywhere you "
                         "would put eyes, and it was running when the glass took it.")[-1]),
            O("Break a piece off the wall and keep it",
              lambda s: (I.give(s, "shard", 3), B.tick(s, 16),
                         "You knock three good edges off the wall and pocket them.")[-1]),
            O("Do not look at it", lambda s: (B.tick(s, 4), "You keep your eyes on the floor, "
                                              "which is also the safer place for them.")[-1])],
           zones=["glassways"], once=True, w=30),

        SC("glass_echo",
           "Something is coming up the glassway behind you at a speed the glass should not "
           "allow, and the sound of it arrives in pieces.",
           [O("Get off the floor and into a side seam",
              lambda s: (s.add_eff("hidden", 30), B.tick(s, 24, exertion=1.2),
                         "You wedge yourself into a seam and it goes by underneath you, and it "
                         "is long, and it does not slow down.")[-1]),
            O("Stand and face it",
              lambda s: (s.stats.__setitem__("fights", s.stats.get("fights", 0) + 1),
                         B.tick(s, 20, exertion=1.6),
                         _hurt(s, s.rng.choice(["left arm", "right arm"]),
                               s.rng.uniform(10, 22), "cut"),
                         "It sets the %s. Something hits it hard enough to take it out of its "
                         "hands and is gone before either of you has finished falling over."
                         % (I.weapon(s)[0] or "haft"))[-1],
              lambda s: I.armed(s)),
            O("Run ahead of it",
              lambda s: (B.tick(s, 22, exertion=2.0), s.__setattr__(
                  "strain", B.clamp(s.strain + 22)), s.__setattr__(
                      "distance", s.distance + 3.0),
                  "You run on glass. You cover ground you would not have covered otherwise and "
                  "you leave most of the skin of your pads behind you.")[-1])],
           zones=["glassways"], w=28, danger=0.75),
    ]

    # ============================================================ CORE: the furnace floor
    def _sprint_floor(s):
        B.tick(s, 18, exertion=1.9)
        s.distance += 3.2
        for limb in ("left leg", "right leg"):
            _hurt(s, limb, s.rng.uniform(12, 22), "burn")
        s.warmth = B.clamp(s.warmth + 28)
        if s.rng.random() < 0.5:
            _issue(s, "cooked")
        return ("You run it. The floor takes the pads off your feet in the first twenty strides "
                "and you keep running on what is under them, and you get across.")

    def _plate_feet(s):
        if not I.has(s, "scrap", 2):
            return "You have no plate to stand on."
        I.take(s, "scrap", 2)
        B.tick(s, 50, exertion=1.4)
        s.distance += 2.4
        _hurt(s, "left leg", s.rng.uniform(4, 9), "burn")
        return ("You cross by moving two scrap plates ahead of yourself and standing on them, "
                "one, then the other, all the way over. It is slow and stupid and it works.")

    core_furnace = [
        SC("furn_floor",
           "The floor here has a direction of heat to it. You start counting your own steps as "
           "a way of not thinking about what the floor is doing to them.",
           [O("Run across it", _sprint_floor),
            O("Cross on scrap plates", _plate_feet, lambda s: I.has(s, "scrap", 2)),
            O("Go along the wall where it is cooler",
              lambda s: (B.tick(s, 90, exertion=1.3), s.__setattr__(
                  "distance", s.distance + 1.4), s.__setattr__(
                      "warmth", B.clamp(s.warmth + 10)),
                  "You work along the wall where the heat is merely bad. It takes most of a "
                  "day to cross a room.")[-1])],
           zones=["furnace"], w=42, danger=0.7),

        SC("furn_store",
           "A store cut into the furnace wall, sealed, and the seal has held. Inside it is "
           "cooler than outside it.",
           [O("Break the seal and take what is in there",
              lambda s: (I.give(s, "stabiliser", 1), I.give(s, "water", 3),
                         I.give(s, "ration", 2), B.tick(s, 24),
                         "Water, food, and a heavy grey cylinder that hums against your palm. "
                         "You have no idea what the cylinder is. It comes with you.")[-1],
              lambda s: B.arms_usable(s) >= 1),
            O("Shelter in it and sleep out the heat",
              lambda s: (B.tick(s, 280, resting=True), s.add_eff("rested", 240),
                         s.add_eff("sheltered", 200),
                         s.stats.__setitem__("sleeps", s.stats.get("sleeps", 0) + 1),
                         "You sleep in the cool of the store with the door pulled to, and the "
                         "furnace goes on being a furnace without you in it.")[-1])],
           zones=["furnace"], w=32),

        SC("furn_burn",
           "Your own body has stopped being able to shed the heat. Everything you touch is "
           "warmer than you and there is nowhere to put the excess.",
           [O("Pour water over yourself",
              lambda s: (I.take(s, "water", 2), s.__setattr__(
                  "warmth", B.clamp(s.warmth - 18)), B.tick(s, 16),
                  "You put two swallows of water over your own head instead of into yourself. "
                  "It is the correct decision and your throat disagrees for an hour.")[-1],
              lambda s: I.has(s, "water", 2)),
            O("Lie flat on the coolest stone you can find",
              lambda s: (B.tick(s, 100, resting=True), s.__setattr__(
                  "warmth", B.clamp(s.warmth - 10)), s.__setattr__(
                      "strain", B.clamp(s.strain - 14)),
                  "You lie flat and let the stone take what it will take.")[-1]),
            O("Keep going and let it cook you",
              lambda s: (B.tick(s, 30, exertion=1.5), s.__setattr__(
                  "warmth", B.clamp(s.warmth + 16)), _issue(s, "cooked"),
                  s.__setattr__("distance", s.distance + 2.0),
                  "You keep going. The heat gets in past the skin and goes on working after "
                  "you are out of the room.")[-1])],
           zones=["furnace"], w=30, danger=0.5),
    ]

    # ============================================================ CORE: the hollow
    def _cross_hollow(s):
        B.tick(s, 60, exertion=1.5)
        s.distance += 3.4
        if s.rng.random() < 0.3:
            s.weird = B.clamp(s.weird + 9)
            s.pending_voice.append("weird")
            return ("You cross the floor of the hollow with its own wind in your face. Halfway "
                    "over, the scale of it arrives all at once and you have to sit down until "
                    "you can be a size again.")
        return ("You cross the floor of the hollow. It has its own weather and the weather has "
                "an opinion about you, and you cross it anyway.")

    core_hollow = [
        SC("holl_void",
           "A void the size of weather, with a wind of its own coming across it. Nothing here "
           "was dug out. Something was taken out, and the hole is the shape of what was taken.",
           [O("Cross the floor of it", _cross_hollow),
            O("Work around the rim where there is cover",
              lambda s: (B.tick(s, 110, exertion=1.2), s.__setattr__(
                  "distance", s.distance + 1.8), s.add_eff("hidden", 30),
                  "You keep to the rim where there is rock to put your shoulder against. It is "
                  "longer and nothing sees you do it.")[-1]),
            O("Stand and work out what was removed",
              lambda s: (s.learn("Something was taken out of the middle of this planet, and "
                                 "the battery is what is left where it was."),
                         s.__setattr__("weird", B.clamp(s.weird + 10)), B.tick(s, 30),
                         "You stand at the lip and read the shape of the hole. Something was "
                         "lifted out of here. The cables all still run to where it was.")[-1])],
           zones=["hollow"], w=40, danger=0.5),

        SC("holl_growth",
           "The walls of the hollow are furred with glowmoss the same orange as your blood, "
           "for hundreds of feet in every direction.",
           [O("Harvest as much as you can carry",
              lambda s: (I.give(s, "glowmoss", 5), B.tick(s, 34),
                         "You strip moss until your hands are the colour of your own insides.")[-1]),
            O("Eat some of it",
              lambda s: (s.__setattr__("hunger", B.clamp(s.hunger - 26)),
                         s.__setattr__("infection", B.clamp(s.infection - 10)),
                         s.__setattr__("weird", B.clamp(s.weird + 8)), B.tick(s, 16),
                         "You eat the moss. It tastes of your own mouth again, and the heat "
                         "goes out of your wounds, and something in your head goes further "
                         "away than it was.")[-1]),
            O("Sleep in it",
              lambda s: (B.tick(s, 300, resting=True), s.add_eff("rested", 260),
                         s.__setattr__("infection", B.clamp(s.infection - 18)),
                         s.stats.__setitem__("sleeps", s.stats.get("sleeps", 0) + 1),
                         "You sleep in a bed of something that glows the same colour you do, "
                         "and whatever is in it takes the heat out of everything open on you.")[-1])],
           zones=["hollow"], w=34),

        SC("holl_wind",
           "The hollow's wind changes direction and comes up out of the middle of it, carrying "
           "warm air and a sound that is being made by something with lungs.",
           [O("Find cover and let it pass",
              lambda s: (s.add_eff("hidden", 40), B.tick(s, 50, resting=True),
                         "You get under rock and wait. Whatever is breathing down there "
                         "breathes for a long time and then stops.")[-1]),
            O("Answer it",
              lambda s: (s.pending_voice.append("weird"),
                         s.__setattr__("weird", B.clamp(s.weird + 8)),
                         s.__setattr__("mood", B.clamp(s.mood - 6)), B.tick(s, 20),
                         "You have it call down into the hollow. Something answers in the same "
                         "register, and then closer, and then you stop doing it.")[-1]),
            O("Press on into it",
              lambda s: (B.tick(s, 30, exertion=1.5), s.__setattr__(
                  "distance", s.distance + 2.4), "You walk into the wind and the sound, "
                  "because the battery is that way.")[-1])],
           zones=["hollow"], w=28, danger=0.65),
    ]

    # ============================================================ CORE: the cradle
    core_cradle = [
        SC("crad_cables",
           "Cables the thickness of your own body come in from every direction and converge, "
           "and where they converge there is light.",
           [O("Follow the cables in",
              lambda s: (B.tick(s, 24, exertion=1.2), s.__setattr__(
                  "distance", s.distance + 2.6),
                  "You follow the cables in toward the light. They are warm. Something is "
                  "still running.")[-1]),
            O("Cut one open to see what is in it",
              lambda s: (_hurt(s, s.rng.choice(["left arm", "right arm"]),
                               s.rng.uniform(16, 30), "burn"),
                         s.__setattr__("weird", B.clamp(s.weird + 10)), B.tick(s, 20),
                         "You open a cable. What is inside it is not wire, and it is under "
                         "pressure, and it takes the skin off your arm as it goes past.")[-1],
              lambda s: B.arms_usable(s) >= 1)],
           zones=["cradle"], w=36, danger=0.4),

        SC("crad_room",
           "This is a made room. Floor, ceiling, corners. After six layers of rock the right "
           "angles are almost more than the body can take.",
           [O("Search the room properly",
              lambda s: (I.give(s, "stabiliser", 1), I.give(s, "ration", 2),
                         s.learn("This was built by the same hands that built the room you "
                                 "woke up in."), B.tick(s, 40),
                         "The fittings are the fittings of the Holding. The same grey, the same "
                         "screws, the same hand. Whoever kept you kept this too.")[-1]),
            O("Sit down in the corner of it",
              lambda s: (B.tick(s, 120, resting=True), s.add_eff("rested", 200),
                         s.__setattr__("mood", B.clamp(s.mood + 10)),
                         "It sits in the corner of a made room with its back in the angle of "
                         "two walls, which is the first time it has been able to do that since "
                         "the Holding, and something in it lets go.")[-1])],
           zones=["cradle"], once=True, w=34),
    ]

    return (crust_shaft + crust_galleries + crust_roots + crust_thermals
            + core_descent + core_boneyard + core_glassways + core_furnace
            + core_hollow + core_cradle)
