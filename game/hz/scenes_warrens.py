"""Scenarios for the two acts Destiny opens under the rock - the warrens and the deep.

Same house rules as every other bank: every option does something mechanical, anything that
needs a limb or an item is gated with req so it is never offered as a lie, and nothing here
explains the setting.

The through-line carried down from the surface is the cairns. Somebody counted their way
through all of this. The count is not a distance and the game does not say so until the very
bottom.
"""
from . import body as B
from . import items as I


def _hurt(s, limb, amount, kind="blunt"):
    return B.hurt(s, limb, amount, kind)


def _leg(s):
    return s.rng.choice(["left leg", "right leg"])


def _arm(s):
    return s.rng.choice(["left arm", "right arm"])


# ---------------------------------------------------------------- the warrens
def _count_stone(s):
    s.flag("cairn_read")
    from . import intel as IN
    ln = IN.gain(s, "read")
    if ln:
        s.feedback.append(ln)
    s.learn("The marks on the cairns are a count, and the count is going up, not down.")
    B.tick(s, 35)
    return ("It holds still while you read the face of the stone through its eyes. The same "
            "three marks as the last one and then a fourth that is new. Not a distance. "
            "Somebody has been counting something up, one stone at a time, for the whole "
            "length of this.")


def _pull_strut(s):
    B.tick(s, 45, exertion=1.6)
    if s.rng.random() < 0.34:
        limb = _arm(s)
        _hurt(s, limb, s.rng.uniform(14, 26), "crush")
        return ("It gets both hands round one of the curved struts and works it out of the "
                "wall, and about two feet of roof comes with it, onto its %s." % limb)
    I.give(s, "marrow", 1)
    I.give(s, "scrap", 1)
    return ("It works one of the struts loose and the roof stays up, which neither of you had "
            "any right to expect. What comes out is not scrap. It is dense and warm at the "
            "core and there is something in it worth having.")


def _wade_silt(s):
    B.tick(s, 80, exertion=1.7)
    s.add_eff("wet", 240)
    if s.rng.random() < 0.42:
        s.infection = B.clamp(s.infection + 10.0)
        return ("It goes through the standing water rather than round it and something in the "
                "silt opens under its foot and closes on nothing. It does not stop walking. "
                "It comes out the far side with the leg already going hot.")
    I.give(s, "water", 2)
    return ("It goes straight through, slowly, feeling for the floor each time before it puts "
            "weight down. An hour and a half of that, and it comes out with the skins full.")


def _sit_with_it(s):
    B.tick(s, 60, resting=True)
    s.mood = B.clamp(s.mood + 8.0)
    s.weird = B.clamp(s.weird + 5.0)
    return ("You have it sit down beside the thing in the passage and do nothing at all for an "
            "hour. Whatever the shape in the dark was doing, it goes on doing it, and neither "
            "of them moves, and eventually the shape is not there any more. Its mood is better "
            "afterwards. You do not entirely want to know why.")


def _eat_cave_meat(s):
    B.tick(s, 30)
    if s.rng.random() < 0.30:
        s.infection = B.clamp(s.infection + 16.0)
        s.hunger = B.clamp(s.hunger - 24.0)
        return ("It eats what is in the passage. It was warm when it started eating and that "
                "is the most that can be said for it. It goes down and mostly stays down.")
    I.give(s, "meat", 2)
    s.hunger = B.clamp(s.hunger - 18.0)
    return ("There is meat down here and some of it has not been dead long. It eats its fill "
            "on the spot and carries what is left.")


def _rot_air(s):
    B.tick(s, 40, exertion=1.2)
    s.strain = B.clamp(s.strain + 12.0)
    s.pending_issues.append("ash lung")
    return ("You send it through at pace with its head down. The air in the rot has been "
            "breathed before, repeatedly, and it goes into the chest like something with an "
            "opinion. It is coughing before it is halfway.")


def _rot_wait(s):
    B.tick(s, 150, resting=True)
    s.fatigue = B.clamp(s.fatigue - 8.0)
    s.hunger = B.clamp(s.hunger + 6.0)
    return ("You hold it at the edge of the warm stretch and wait for the air to turn over, "
            "which it does, on a slow count, the way the whole of this place seems to do "
            "everything. Two and a half hours. It costs you food and it costs its lungs "
            "nothing.")


def _dig_through(s):
    B.tick(s, 110, exertion=2.0)
    s.strain = B.clamp(s.strain + 18.0)
    s.fatigue = B.clamp(s.fatigue + 14.0)
    s.distance = min(s.distance + 1.2, s.distance + 1.2)
    return ("It digs. Not well - it has hands and not the right hands - but the fall is loose "
            "and it moves it a handful at a time for the better part of two hours until there "
            "is a gap it can get a shoulder into, and then it is through.")


def _go_round_fall(s):
    B.tick(s, 70, exertion=1.3)
    s.distance = max(0.0, s.distance - 0.6)
    return ("You take it back and round through a side passage that is going roughly the right "
            "way. It is longer, it costs ground, and the roof stays where it is the whole way.")


def _listen_burrow(s):
    B.tick(s, 25, resting=True)
    from . import intel as IN
    ln = IN.gain(s, "read")
    if ln:
        s.feedback.append(ln)
    s.weird = B.clamp(s.weird + 6.0)
    return ("You have it put its head against the wall and hold it there. What comes through "
            "the rock is not water and it is not air. It is regular, and it is a long way off, "
            "and it is below.")


def _mark_wall(s):
    B.tick(s, 30)
    s.flag("marked_wall")
    s.mood = B.clamp(s.mood + 5.0)
    s.learn("Leaving a mark for whatever comes next is something this body will do without "
            "being asked twice.")
    return ("It cuts a mark into the wall at the junction, on the side you came from, without "
            "any real instruction beyond the general one. It looks at it for a moment "
            "afterwards. Then it does another one, slightly better.")


# ---------------------------------------------------------------- the deep
def _weave_map(s):
    B.tick(s, 90, exertion=1.1)
    from . import intel as IN
    ln = IN.gain(s, "read")
    if ln:
        s.feedback.append(ln)
    s.learn("Whatever dug this was not going anywhere. It was looking for something and it did "
            "not know where it was.")
    return ("You walk it through the crossings deliberately, taking every left, and it comes "
            "back to the same junction three times. None of these passages leads anywhere. "
            "They were not made to lead anywhere. They were made to find out whether anything "
            "was there.")


def _kiln_cross(s):
    B.tick(s, 55, exertion=1.8)
    s.heat = B.clamp(float(getattr(s, "heat", 0.0) or 0.0) + 14.0)
    s.warmth = B.clamp(s.warmth + 12.0)
    if s.rng.random() < 0.35:
        limb = _leg(s)
        _hurt(s, limb, s.rng.uniform(12, 22), "burn")
        return ("You run it across the glazed floor. The glaze is not cool. It goes over in "
                "one push and the %s comes off it in a state." % limb)
    return ("You run it across the glazed floor in one push, fast, and it does not stop and it "
            "does not look down, and it is across.")


def _well_drink(s):
    B.tick(s, 40)
    s.thirst = B.clamp(s.thirst - 46.0)
    I.give(s, "water", 3)
    s.warmth = B.clamp(s.warmth - 6.0)
    return ("The water coming up the shaft is cold and clean and moving, which nothing else "
            "down here is. It drinks until it stops and then fills everything that holds "
            "water. It is the best thing that has happened in this act.")


def _well_down(s):
    B.tick(s, 70, exertion=1.9)
    limb = _arm(s)
    if s.rng.random() < 0.45:
        _hurt(s, limb, s.rng.uniform(10, 20), "blunt")
    I.give(s, "marrow", 1)
    I.give(s, "stabiliser", 1)
    s.weird = B.clamp(s.weird + 7.0)
    return ("You put it over the lip and down the wet shaft on its hands and feet. There is a "
            "ledge a long way down with things on it that somebody put there on purpose, for "
            "somebody, and it takes two of them and comes back up.")


def _lung_count(s):
    B.tick(s, 45, resting=True)
    s.weird = B.clamp(s.weird - 8.0)
    s.mood = B.clamp(s.mood + 6.0)
    s.learn("The pressure down here keeps a count, and it has been keeping it since long "
            "before anything walked in to notice.")
    return ("You have it match its breathing to the floor. It takes a while to find it and "
            "then it has it, and the two of you sit inside something that has been doing this "
            "without an audience for longer than the building upstairs has existed. Some of "
            "the wrongness goes out of it.")


def _lung_push(s):
    B.tick(s, 50, exertion=1.9)
    s.strain = B.clamp(s.strain + 16.0)
    s.fatigue = B.clamp(s.fatigue + 10.0)
    return ("You push it through against the count rather than with it, which means half of "
            "every stride is uphill against a wall of moving air. It gets through. It costs "
            "more than it needed to.")


def _kiln_soak(s):
    """Written out rather than chained with 'or' - I.take() returns True, which quietly ate
    the return text the first time this was an inline lambda."""
    I.take(s, "water", 1)
    B.tick(s, 45, exertion=1.6)
    s.heat = B.clamp(float(getattr(s, "heat", 0.0) or 0.0) + 6.0)
    return ("You have it empty a skin over its own back and go. The water is gone off it "
            "before it is halfway across, and it is over the other side, and it is not "
            "burned.")


def _hand_print(s):
    B.tick(s, 20)
    s.learn("Whatever dug all of this had hands, and used them until there was nothing left "
            "of them.")
    s.weird = B.clamp(s.weird + 4.0)
    return ("It fits its own hand into the print, which is a thing you did not ask it to do "
            "and did not have to. Its hand does not come close to filling it. It stays like "
            "that for a while.")


def _ring_read(s):
    s.flag("cairn_read")
    from . import intel as IN
    ln = IN.gain(s, "read")
    if ln:
        s.feedback.append(ln)
    s.learn("The count on the stones is a number of attempts, and every one of them came "
            "here.")
    B.tick(s, 50)
    return ("It goes along the stones one at a time with its face close to them. The count is "
            "on all of them and it is the same count and it is enormous. Whatever has been "
            "doing this has done it more times than there are stones to say so with.")


def build_warrens(SC, O):
    W_Z = ["stacks", "burrow", "ribs", "rot", "silt", "throat"]
    D_Z = ["deep", "weave", "kiln", "well", "lung", "chamber"]
    out = [
        SC("wr_count",
           "There is a cairn at the side of the passage, stacked properly, and the flat stone "
           "at the top of it has marks cut into its face. The same marks as the last one, and "
           "one more.",
           [O("Have it hold still while you read the stone", _count_stone),
            O("Have it cut a mark of its own into the wall", _mark_wall),
            O("Leave it and keep going", lambda s: (B.tick(s, 10) or
              "It walks past without looking at it, because you did not ask it to look."))],
           zones=W_Z, w=11),
        SC("wr_strut",
           "The roof here is held up by curved struts set into both walls every few paces. "
           "They are not cut stone and they are not scrap. They were inside something once, "
           "and they are dense, and there is marrow in the ends of them.",
           [O("Have it work one out of the wall", _pull_strut),
            O("Have it take only what has already fallen",
              lambda s: (B.tick(s, 30) or I.give(s, "shard", 2) or
                         "It picks over what has already come down rather than pulling on "
                         "anything holding the roof up. Two usable pieces, and the roof stays "
                         "where it is.")),
            O("Leave the roof alone", lambda s: (B.tick(s, 12) or
              "You do not let it touch them. It goes through at a walk, under all of them."))],
           zones=["ribs", "throat"], w=10),
        SC("wr_silt",
           "Standing water over grey silt, ankle deep, going on further than the light does. "
           "There are shapes under the surface at intervals. Most of them are objects.",
           [O("Have it wade straight through", _wade_silt),
            O("Have it go along the wall instead",
              lambda s: (B.tick(s, 100, exertion=1.4) or
                         "It goes the whole way with one shoulder on the rock and both feet on "
                         "the narrow dry strip at the edge. It takes most of two hours and it "
                         "does not once put a foot in the silt.")),
            O("Have it feel through the silt for what is in it",
              lambda s: (B.tick(s, 60, exertion=1.2) or I.give(s, "scrap", 2) or
                         I.give(s, "cloth", 2) or
                         "It puts its arms into the silt up to the shoulder and brings things "
                         "out one at a time. Cloth, mostly, and metal. Somebody came through "
                         "here carrying more than they left with."),
              req=lambda s: B.arms_usable(s) >= 1)],
           zones=["silt"], w=11),
        SC("wr_rot",
           "The passage ahead is warm and wet and the air coming out of it has been breathed "
           "already. Everything grows in there. None of it is clean.",
           [O("Send it through at pace with its head down", _rot_air),
            O("Wait at the edge for the air to turn over", _rot_wait),
            O("Have it eat while it is in there", _eat_cave_meat)],
           zones=["rot", "silt"], w=10),
        SC("wr_fall",
           "The passage is shut. Something came down across it - not recently, and not all at "
           "once - and the fall is loose rock from the roof to about chest height.",
           [O("Have it dig through", _dig_through, req=lambda s: B.arms_usable(s) >= 1),
            O("Go round through the side passage", _go_round_fall),
            O("Have it put its head against the rock and listen first", _listen_burrow)],
           zones=W_Z, w=10),
        SC("wr_shape",
           "There is something in the passage ahead of it that is not moving. It has been "
           "there a while. It is between you and the way on, and it is the wrong shape to "
           "climb over politely.",
           [O("Have it sit down and wait it out", _sit_with_it),
            O("Have it go past at the wall, fast",
              lambda s: (B.tick(s, 20, exertion=1.7) or
                         (_hurt(s, _arm(s), s.rng.uniform(8, 18), "blunt")
                          if s.rng.random() < 0.40 else None) or
                         "It goes past with its back on the rock and its eyes on the thing the "
                         "whole way, and whatever it is does not do anything about it.")),
            O("Have it go at the thing", lambda s: (B.tick(s, 25, exertion=2.0) or
              _hurt(s, _arm(s), s.rng.uniform(10, 24), "bite") or
              "It goes at it. The thing turns out to have been alive after all, and to have "
              "been waiting for exactly that."))],
           zones=W_Z, w=9),
        SC("wr_smooth",
           "This stretch is round in cross-section and polished, and nothing that has hands "
           "polishes a mile of rock. Something went through here head first, over and over, "
           "for a very long time.",
           [O("Have it put its head against the wall and listen", _listen_burrow),
            O("Have it keep moving and not think about it",
              lambda s: (B.tick(s, 25, exertion=1.1) or
                         "It goes through at a steady pace without looking at the walls, which "
                         "is what you asked for, and the walls go on being that shape."))],
           zones=["burrow", "throat"], w=9),

        # ------------------------------------------------------------ the deep
        SC("dp_weave",
           "Passages crossing passages crossing passages. You have come through this junction "
           "before. You are reasonably sure you have come through it twice.",
           [O("Walk it deliberately and work out the pattern", _weave_map),
            O("Have it pick a direction and commit",
              lambda s: (B.tick(s, 60, exertion=1.4) or
                         "You point it and it goes, and it does not slow down at any of the "
                         "crossings, and eventually the crossings stop. That is one way of "
                         "solving it.")),
            O("Have it mark the junction before going on", _mark_wall)],
           zones=["weave", "deep"], w=11),
        SC("dp_kiln",
           "The walls here have gone to a glaze, and the glaze has run and set and run again. "
           "The floor is the same. It is not cool and the far side is a long way.",
           [O("Run it across in one push", _kiln_cross),
            O("Have it go round the edge where the glaze is thin",
              lambda s: (B.tick(s, 95, exertion=1.3) or
                         "It picks its way round the rim where the glaze never took, one paw "
                         "at a time, for most of two hours. Nothing burns.")),
            O("Have it pour water over itself first", _kiln_soak,
              req=lambda s: I.has(s, "water"))],
           zones=["kiln"], w=11),
        SC("dp_well",
           "A shaft in the floor with water coming up it - cold, clean, and moving. Moving "
           "means it is going somewhere. Nothing else down here is going anywhere.",
           [O("Have it drink and fill everything", _well_drink),
            O("Have it climb down the shaft", _well_down,
              req=lambda s: B.arms_usable(s) >= 1 and B.legs_usable(s) >= 1),
            O("Leave it alone", lambda s: (B.tick(s, 12) or
              "You walk it past the water. It looks back at it twice."))],
           zones=["well", "lung"], w=11),
        SC("dp_lung",
           "The space fills and empties. The pressure comes up through the floor on a count "
           "and goes back down on the same count, and it has been doing it without anybody "
           "here to notice for a very long time.",
           [O("Have it match its breathing to the floor", _lung_count),
            O("Push it through against the count", _lung_push),
            O("Have it wait out one full cycle before moving",
              lambda s: (B.tick(s, 80, resting=True) or
                         "You hold it at the edge for one full turn of the thing, in and out, "
                         "and then send it. It goes through on the slack and nothing pushes "
                         "back at it once."))],
           zones=["lung", "deep"], w=11),
        SC("dp_ring",
           "There are cairns at the edge of the light, in a line, going the way you are going. "
           "They are better stacked than the ones on the surface. Whoever did these had had a "
           "great deal of practice by the time they got this far down.",
           [O("Have it read the count on them", _ring_read),
            O("Have it add one", _mark_wall),
            O("Keep going", lambda s: (B.tick(s, 10) or
              "It goes past them. It slows down at each one and does not stop."))],
           zones=["chamber", "lung", "deep", "weave"], w=10),
        SC("dp_hands",
           "There is a print in the floor where the rock went soft once and set again. It is a "
           "hand. It is far too large and there are too many fingers on it and the ends of the "
           "fingers are worn flat.",
           [O("Have it put its own hand in the print", _hand_print,
              req=lambda s: B.arms_usable(s) >= 1),
            O("Have it look for more of them",
              lambda s: (B.tick(s, 50, exertion=1.1) or
                         "There are more. They go both ways, thousands of them, and every one "
                         "of them is going down.")),
            O("Move on", lambda s: (B.tick(s, 10) or "You move it on."))],
           zones=D_Z, w=9),
    ]
    return out
