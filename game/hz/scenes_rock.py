"""Scenarios for the other planet - the eight layers of rock that Destiny opens on.

Same house rules as the other banks: every option does something mechanical, anything that
needs a limb or an item is gated with req so it is never offered as a lie, and nothing here
explains the setting. The rock is learned by being walked.

The through-line is that somebody came this way before. It is never stated outright and it is
never resolved until the fence.
"""
from . import body as B
from . import items as I


def _hurt(s, limb, amount, kind="blunt"):
    B.hurt(s, limb, amount, kind)


def _weird(s, n):
    s.weird = B.clamp(s.weird + n)


def _plate_fall(s):
    """The flats are loose plate over holes and the holes have a bottom."""
    leg = s.rng.choice(["left leg", "right leg"])
    _hurt(s, leg, s.rng.uniform(16, 30), "fall")
    B.tick(s, 50, exertion=1.7)
    if I.has(s, "grapple"):
        return ("The plate goes out from under it and it drops. The grapple catches rock on "
                "the way past and it hauls itself back into daylight on one arm, which is not "
                "what an arm is for.")
    return ("The plate goes out from under it and it drops into the dark under the flats. "
            "Getting out takes most of an hour and takes the skin off its %s." % leg)


def _cairn_read(s):
    s.flag("cairn_read")
    from . import intel as IN
    ln = IN.gain(s, "read")
    if ln:
        s.feedback.append(ln)
    s.learn("Somebody walked this rock before, all the way, and marked the route for whoever "
            "came next.")
    B.tick(s, 30)
    return ("There is a flat stone set into the third cairn with marks cut into it - not "
            "writing exactly, or not writing you know. A direction, a count, and a shape that "
            "is a house. Whoever stacked these was counting down to something.")


def _dust_wade(s):
    B.tick(s, 70, exertion=1.6)
    s.add_eff("wet", 0)
    if s.rng.random() < 0.40:
        _weird(s, 8)
        return ("You put it into the dust and it goes in to the chest and keeps going, and "
                "then stops going, and stands there a long moment before it starts wading "
                "again. It does not say what touched it. It does not have the words.")
    return ("You put it through the dust sea rather than around. Grey to the chest, and it "
            "comes out the far side grey to the eyes, and an hour of the day is gone.")


def _glass_cross(s):
    B.tick(s, 60, exertion=1.4)
    s.heat = B.clamp(getattr(s, "heat", 0.0) + 9)
    if s.rng.random() < 0.35:
        foot = s.rng.choice(["left leg", "right leg"])
        _hurt(s, foot, s.rng.uniform(10, 20), "cut")
        return ("Straight out across the glass. It holds, mostly. Where it does not hold it "
                "is an edge, and the edge finds its %s." % foot)
    I.give(s, "shard", 3)
    return ("Straight out across the glass, and the glass holds the whole way. It picks up "
            "three good edges on the way past without being asked to.")


def _eat_fungus(s):
    I.give(s, "dust fungus", 1)
    txt = I.use(s, "dust fungus")
    B.tick(s, 15)
    return txt or "It eats some of the grey stuff where it stands."


def build_rock(SC, O):
    """Sixteen for the rock. Handed the constructors so this stays a leaf module."""
    return [
        # ---------------------------------------------------------- the waking ground
        SC("rock_wake",
           "There is a shape pressed into the dust a little way off, about the size of the "
           "body you are driving, and nothing in it.",
           [O("Have it lie down in the shape", lambda s: (B.tick(s, 25, resting=True),
              _weird(s, 6), "It fits. It fits exactly. It gets up faster than it lay down.")[-1]),
            O("Search around it", lambda s: (I.give(s, "cloth", 2), I.give(s, "cord"),
              B.tick(s, 30), "Cut cloth and a length of cord, half buried. Somebody was here "
              "and was not taken from here.")[-1]),
            O("Leave it", lambda s: (B.tick(s, 6), "It goes around the shape rather than "
              "through it, which nobody taught it to do.")[-1])],
           zones=["wake"], once=True, w=40, danger=0.1),

        SC("rock_sky",
           "It has stopped walking and put its head back. The sky up there is not doing what "
           "a sky does, and it has noticed, and it is waiting for you to explain.",
           [O("Tell it the truth - you do not know either",
              lambda s: (s.__setattr__("mood", B.clamp(s.mood + 5)), _weird(s, -4),
              B.tick(s, 12), "You tell it you have never seen this either. It takes that "
              "better than it has taken anything you have told it.")[-1]),
            O("Tell it to keep walking", lambda s: (s.__setattr__("mood",
              B.clamp(s.mood - 6)), _weird(s, 5), B.tick(s, 8),
              "It keeps walking. It looks up twice more and does not ask again.")[-1])],
           zones=["wake", "grey"], once=True, w=34),

        SC("rock_cold_start",
           "The ground here holds no heat at all. Whatever warmth is in the body is the only "
           "warmth for a very long way.",
           [O("Build something to get off the rock",
              lambda s: (s.add_eff("sheltered", 220), B.tick(s, 55, exertion=1.2),
              "You get it up off the stone on cloth and scrap. It stops losing heat downward, "
              "which is where all of it was going.")[-1],
              lambda s: I.has(s, "cloth") or I.has(s, "hide")),
            O("Keep moving instead", lambda s: (B.tick(s, 40, exertion=1.5),
              s.__setattr__("warmth", B.clamp(s.warmth + 3)),
              "Moving makes its own heat. It also spends what it is making.")[-1])],
           zones=["wake", "grey"], w=26),

        # ---------------------------------------------------------- the grey flats
        SC("rock_plate",
           "The flat ground ahead rings hollow under the first step onto it. It is not ground. "
           "It is a lid.",
           [O("Cross it anyway", _plate_fall),
            O("Go the long way round", lambda s: (B.tick(s, 85, exertion=1.3),
              "An hour and a half added to the day, and nothing falls through anything.")[-1]),
            O("Break a hole and look in", lambda s: (I.give(s, "scrap", 3),
              I.give(s, "shard", 2), _weird(s, 5), B.tick(s, 45, exertion=1.4),
              "Under the plate is a space with made things in it, none of them explicable, "
              "several of them worth carrying.")[-1])],
           zones=["grey"], w=32, danger=0.5),

        SC("rock_fungus",
           "Grey growth across the plate in a patch the size of a room, the only living thing "
           "anybody has seen on this rock.",
           [O("Take as much as it will carry", lambda s: (I.give(s, "dust fungus", 3),
              B.tick(s, 25), "It comes away in wet handfuls. It is not good. It is wet, and "
              "wet is the whole argument.")[-1]),
            O("Have it eat some here", _eat_fungus),
            O("Leave it alone", lambda s: (B.tick(s, 5),
              "You decide against the only living thing on the planet. It looks back at it "
              "twice.")[-1])],
           zones=["grey", "dust"], w=30),

        # ---------------------------------------------------------- the stone teeth
        SC("rock_teeth_thing",
           "Something is between two of the stones and it has been watching you approach for "
           "a while without moving. It is built low and wide and it is not afraid.",
           [O("Put whatever it is holding into it", lambda s: (s.stats.__setitem__("fights",
              s.stats.get("fights", 0) + 1), I.give(s, "meat", 2), I.give(s, "hide"),
              B.tick(s, 35, exertion=1.8), "It goes down hard and takes a long time about it. "
              "There is meat on it and the hide comes off in one piece.")[-1],
              lambda s: I.armed(s)),
            O("Back away slowly", lambda s: (B.tick(s, 25), s.add_eff("hidden", 60),
              "You walk it backwards out of the gap. The thing does not follow, which means "
              "it did not have to.")[-1]),
            O("Walk straight past it", lambda s: (_hurt(s, s.rng.choice(["left leg",
              "right leg"]), s.rng.uniform(14, 28), "bite"), B.tick(s, 30),
              "It lets you get level with it before it moves.")[-1])],
           zones=["teeth"], w=34, danger=0.7),

        SC("rock_windbreak",
           "The stones make a pocket here that the weather has not got into. There is old "
           "bedding in it, and the bedding is cloth, and cloth does not grow.",
           [O("Take the bedding and sleep here", lambda s: (I.give(s, "cloth", 2),
              s.add_eff("sheltered", 300), B.tick(s, 300, resting=True),
              s.add_eff("rested", 400), s.stats.__setitem__("sleeps",
              s.stats.get("sleeps", 0) + 1),
              "You sleep in somebody else's bed, on a planet nobody has been to, and wake up "
              "properly rested for the first time since the rock.")[-1]),
            O("Take the cloth and move on", lambda s: (I.give(s, "cloth", 3), B.tick(s, 20),
              "Good cloth, cut to a shape, by hands.")[-1])],
           zones=["teeth", "cairns"], once=True, w=30),

        # ---------------------------------------------------------- the dust sea
        SC("rock_dust",
           "The dust runs out ahead further than seeing goes. Around costs a day. Through "
           "costs whatever is under it.",
           [O("Wade through", _dust_wade),
            O("Go around", lambda s: (B.tick(s, 150, exertion=1.2),
              "Most of a day spent on the margin of it, and it never once looks at the dust.")[-1]),
            O("Drag the sled over it", lambda s: (B.tick(s, 60, exertion=1.1),
              I.give(s, "dust fungus", 2),
              "The sled floats where feet sink. It is the first time the thing has been worth "
              "what it costs.")[-1], lambda s: I.has(s, "sled"))],
           zones=["dust"], w=36, danger=0.4),

        SC("rock_dust_hand",
           "Something is standing out of the dust ahead, thin and pale and about the height of "
           "an arm.",
           [O("Pull it out", lambda s: (I.give(s, "scrap", 2), _weird(s, 10), B.tick(s, 25),
              "It is a strut. A made one, bent, with a cuff on the end sized for a limb that "
              "is not the size of yours.")[-1]),
            O("Go around it", lambda s: (_weird(s, 4), B.tick(s, 12),
              "It gives the thing a wide berth without being told to.")[-1])],
           zones=["dust"], once=True, w=26),

        # ---------------------------------------------------------- the cairns
        SC("rock_cairn",
           "Stacked stone, deliberate, in a line going exactly the way you are going. There "
           "are hundreds of them and they are all the same height.",
           [O("Read the marks on them", _cairn_read),
            O("Follow them and nothing else", lambda s: (s.__setattr__("distance",
              s.distance + 3.0), B.tick(s, 55, exertion=1.2),
              "You stop navigating and just follow the stones. They do not go wrong once.")[-1]),
            O("Knock one over", lambda s: (_weird(s, 12), s.__setattr__("mood",
              B.clamp(s.mood - 8)), B.tick(s, 10),
              "It puts the top stone off with one hand. Nothing happens. It stands there a "
              "while afterwards and then puts the stone back.")[-1])],
           zones=["cairns"], w=38),

        SC("rock_cache",
           "One of the cairns is hollow. There is a bundle inside it, wrapped and tied, left "
           "by somebody who expected somebody.",
           [O("Open it", lambda s: (I.give(s, "ration", 2), I.give(s, "water", 2),
              I.give(s, "coagulant"), I.give(s, "map scrap"), B.tick(s, 20),
              "Food, water, a sealed packet, and half a print with a line on it. Left for "
              "whoever came next. That is you.")[-1]),
            O("Leave it for whoever it was meant for", lambda s: (s.__setattr__("mood",
              B.clamp(s.mood + 6)), _weird(s, -4), B.tick(s, 10),
              "You leave another creature's supplies where they were put. The subject does not "
              "understand and does it anyway.")[-1])],
           zones=["cairns"], once=True, w=34),

        # ---------------------------------------------------------- the glass pan
        SC("rock_glass",
           "The rock ahead has been glass since something very hot happened here, and the "
           "glass goes on for most of a day's walk.",
           [O("Cross it", _glass_cross),
            O("Skirt the edge", lambda s: (B.tick(s, 110, exertion=1.2),
              "The long way round the pan, on rock that has not been turned into "
              "anything.")[-1]),
            O("Break some up to carry", lambda s: (I.give(s, "shard", 5), B.tick(s, 40),
              _hurt(s, "right arm", s.rng.uniform(4, 10), "cut"),
              "Five good edges and one bad cut getting them.")[-1])],
           zones=["pan"], w=34, danger=0.5),

        SC("rock_reflection",
           "It has stopped in front of its own reflection in the glass and it is not moving. "
           "It has never seen itself before.",
           [O("Let it look", lambda s: (B.tick(s, 30, resting=True), _weird(s, 6),
              s.__setattr__("mood", B.clamp(s.mood - 4)),
              s.learn("It has a face, and the face is not like the ones it half-remembers "
                      "standing over it."),
              "It looks for a long time. It touches its own muzzle, then the glass, then its "
              "muzzle again.")[-1]),
            O("Move it on", lambda s: (s.__setattr__("mood", B.clamp(s.mood - 7)),
              B.tick(s, 8), "You move it on. It walks the next stretch looking at the ground "
              "in front of its feet and nothing else.")[-1])],
           zones=["pan"], once=True, w=28),

        # ---------------------------------------------------------- the slope
        SC("rock_wind",
           "There is weather on the slope - actual moving air, the first on this rock - and it "
           "is coming down the hill hard enough to lean on.",
           [O("Push up into it", lambda s: (B.tick(s, 70, exertion=1.9),
              s.__setattr__("warmth", B.clamp(s.warmth - 10)),
              "Up into it, at a lean, for an hour and a half. The cold goes straight through "
              "whatever is not covered.")[-1]),
            O("Wait it out in cover", lambda s: (B.tick(s, 120, resting=True),
              s.add_eff("sheltered", 120),
              "Two hours behind a rock, out of it. The wind does not stop, exactly, but it "
              "stops being the main fact.")[-1]),
            O("Put the coat on and go", lambda s: (B.tick(s, 60, exertion=1.6),
              s.__setattr__("distance", s.distance + 2.0),
              "The coat does what it was cut for. You get up the slope in one push.")[-1],
              lambda s: I.has(s, "coat"))],
           zones=["slope"], w=36, danger=0.4),

        SC("rock_bones",
           "There is a body on the slope. Not a creature's - it is wearing cut cloth and it "
           "has a pack, and the pack is still fastened.",
           [O("Open the pack", lambda s: (I.give(s, "ration", 2), I.give(s, "cord", 2),
              I.give(s, "antisepsis"), I.give(s, "tinder"), _weird(s, 6), B.tick(s, 30),
              "Food, cord, a crush tube, and cloth worked through with resin. Everything in it "
              "was chosen by somebody who knew exactly what this walk costs.")[-1]),
            O("Look at what killed it", lambda s: (_weird(s, 9), B.tick(s, 25),
              s.learn("Nothing killed the one who came before. It simply stopped, "
                      "sitting down, facing the way it had come."),
              "Nothing killed it. There is no wound and nothing has been at it. It sat down "
              "facing back the way it came and it did not get up.")[-1]),
            O("Leave it be", lambda s: (s.__setattr__("mood", B.clamp(s.mood + 4)),
              B.tick(s, 8), "You leave it where it is. It goes past at a distance.")[-1])],
           zones=["slope"], once=True, w=34),

        # ---------------------------------------------------------- the approach
        SC("rock_tended",
           "The ground here has been cleared. Stones moved to the sides, in lines. Not grown - "
           "tended, by something with a plan and a lot of time.",
           [O("Follow the cleared ground", lambda s: (s.__setattr__("distance",
              s.distance + 2.5), B.tick(s, 40), "Walking on ground somebody swept. It is the "
              "easiest going on the entire rock and it is deeply unpleasant.")[-1]),
            O("Walk beside it instead", lambda s: (B.tick(s, 60, exertion=1.3), _weird(s, -3),
              "You keep it off the cleared ground the whole way. Nothing objects.")[-1])],
           zones=["approach"], w=30),

        SC("rock_lights",
           "The building is in sight and the lights in it have not flickered once in the hours "
           "it has taken to get this close. Nothing is moving around it. Nothing ever has.",
           [O("Have it sit and watch the house a while",
              lambda s: (B.tick(s, 90, resting=True), _weird(s, 4),
              "An hour and a half of watching a lit house on a dead rock. Nothing comes out. "
              "Nothing goes in. The lights do not change.")[-1]),
            O("Close the distance", lambda s: (s.__setattr__("distance", s.distance + 3.0),
              B.tick(s, 45, exertion=1.2), "Straight at it. It gets larger and it does not "
              "get any more explicable.")[-1])],
           zones=["approach"], w=32),
    ]
