"""Traps: the ground itself, arranged by somebody, waiting.

A trap is not an encounter. The difference that matters is that a trap is decided BEFORE the
scene appears - either the body noticed it or it did not, and that single roll decides whether
you are looking at a problem or standing in one. Everything after that is damage control.

Noticing is a real faculty and not a dice roll dressed up: it is what the chip understands
(intel), whether this particular body reads ground before standing on it (the "wary" trait),
and whether its eyes hold still long enough to resolve a wire (the "jitter" trait, which is
why 682 walks into nearly everything). Fatigue, wrongness and the dark all take from it.

Traps are everywhere down-well and they are the texture of Destiny in particular - see
TRAP_RATE. The rock and the two cave acts under it were laid out by something that expected
company.
"""
from . import body as B
from . import items as I
from . import subjects as SUB

# per-move chance that the ground has something in it, before the ground multiplier
BASE_RATE = 0.07

# Keyed on the ZONE SET rather than the region, because Destiny walks different
# ground and not the same ground harder. The surface was never prepared for
# anybody; everything below it was, and every act Destiny opens on was laid out by
# something that expected company and left the welcome in the floor.
TRAP_RATE = {"outside": 0.35, "crust": 1.00, "core": 1.25,
             "rock": 1.20, "warrens": 1.35, "deep": 1.50}
DESTINY_RATE = 1.55


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def spot_chance(s, difficulty):
    """How likely this body is to see it coming. Difficulty is subtracted flat."""
    p = 0.48
    p += 0.0060 * float(getattr(s, "intel", 14.0))
    p += 0.40 * SUB.trait(s, "wary")
    p -= 0.38 * SUB.trait(s, "jitter")
    p -= 0.0030 * max(0.0, s.fatigue - 50.0)
    p -= 0.0030 * max(0.0, s.weird - 40.0)
    p -= 0.0020 * max(0.0, s.pain - 50.0)
    if s.night:
        p -= 0.12
    if s.eff("rested"):
        p += 0.06
    if I.has(s, "lamp") or s.eff("lit"):
        p += 0.08
    return _clamp(p - difficulty, 0.03, 0.92)


# ---------------------------------------------------------------- what is in the ground
def _leg(s):
    return s.rng.choice(["left leg", "right leg"])


def _arm(s):
    return s.rng.choice(["left arm", "right arm"])


def _hit_snare(s):
    leg = _leg(s)
    B.hurt(s, leg, s.rng.uniform(14, 26), "cut")
    B.tick(s, 20, exertion=1.5)
    return ("The cable comes up out of the dust and closes on its %s, and the whole body goes "
            "over sideways into the rock." % leg)


def _hit_pit(s):
    leg = _leg(s)
    B.hurt(s, leg, s.rng.uniform(20, 34), "fall")
    B.tick(s, 35, exertion=1.7)
    return ("The cover was sticks and dust over a hole somebody dug, and it is at the bottom "
            "of the hole before it has finished putting its weight down. The %s takes all of "
            "it." % leg)


def _hit_deadfall(s):
    part = s.rng.choice(["left arm", "right arm", "tail"])
    B.hurt(s, part, s.rng.uniform(24, 40), "crush")
    B.tick(s, 25, exertion=1.6)
    return ("Something gives above it and a great deal of rock comes down in one piece. It is "
            "most of the way clear when it lands. Most of the way is not clear - its %s is "
            "under the edge of it." % part)


def _hit_glass(s):
    leg = _leg(s)
    B.hurt(s, leg, s.rng.uniform(10, 20), "cut")
    B.hurt(s, _leg(s), s.rng.uniform(6, 14), "cut")
    B.tick(s, 18, exertion=1.3)
    return ("Shards set upright in the ground with the points up, under a finger of dust. It "
            "is four paces into them before the first one goes all the way through.")


def _hit_tripline(s):
    limb = s.rng.choice(["left ear", "right ear", "tail"])
    B.hurt(s, limb, s.rng.uniform(16, 30), "cut")
    s.blood = B.clamp(s.blood - 4.0)
    B.tick(s, 15, exertion=1.2)
    return ("A line strung at head height, thin enough that nothing sees it and hard enough "
            "that it does not break. It catches it across the %s at walking speed." % limb)


def _hit_jaws(s):
    leg = _leg(s)
    B.hurt(s, leg, s.rng.uniform(30, 48), "crush")
    B.tick(s, 30, exertion=1.8)
    return ("Steel, buried, older than anything else here and still working. It shuts on the "
            "%s hard enough that the sound arrives before the pain does." % leg)


def _hit_spores(s):
    s.infection = B.clamp(s.infection + 7.0)
    s.weird = B.clamp(s.weird + 9.0)
    s.add_eff("static", 90)
    B.tick(s, 20, exertion=1.1)
    return ("It puts a foot through a swelling in the floor and the swelling goes off - a "
            "grey column of it, straight up, and it is standing in the middle of the column "
            "breathing.")


def _hit_net(s):
    B.hurt(s, _arm(s), s.rng.uniform(8, 16), "blunt")
    s.strain = B.clamp(s.strain + 14.0)
    B.tick(s, 30, exertion=1.4)
    return ("The ground takes it and the sky arrives. It is six feet up and upside down in a "
            "net of cord before it has worked out which way it is facing.")


def _hit_vent(s):
    limb = s.rng.choice(["left leg", "right leg", "left arm", "right arm"])
    B.hurt(s, limb, s.rng.uniform(18, 30), "burn")
    s.heat = B.clamp(float(getattr(s, "heat", 0.0) or 0.0) + 10.0)
    B.tick(s, 20, exertion=1.3)
    return ("A plate in the floor sinks half an inch under its weight and the vent beside it "
            "opens. What comes out is not steam, quite, and it goes up the %s." % limb)


def _hit_wire(s):
    for _ in range(2):
        B.hurt(s, s.rng.choice(list(s.limbs)), s.rng.uniform(7, 14), "cut")
    s.blood = B.clamp(s.blood - 5.0)
    B.tick(s, 28, exertion=1.6)
    return ("Wire, coiled loose across a gap, every foot of it barbed. Getting into it takes "
            "one step. Every movement after that is another cut.")


def _hit_sink(s):
    B.hurt(s, _leg(s), s.rng.uniform(22, 38), "fall")
    B.hurt(s, _arm(s), s.rng.uniform(8, 18), "blunt")
    B.tick(s, 55, exertion=1.9)
    return ("The floor is a floor until it is a lid. It goes through in one piece and lands a "
            "long way down in the dark with something soft underneath it that it does not "
            "look at.")


def _hit_barbs(s):
    B.hurt(s, _leg(s), s.rng.uniform(13, 23), "cut")
    s.infection = B.clamp(s.infection + 4.0)
    B.tick(s, 22, exertion=1.4)
    return ("Bone, split lengthways and set point-up in rows. Not grown that way. Cut that "
            "way, by somebody, and pushed into the floor one at a time.")


def _hit_hum(s):
    s.chip = B.clamp(s.chip - 14.0)
    s.weird = B.clamp(s.weird + 16.0)
    s.add_eff("static", 120)
    B.tick(s, 20, exertion=1.0)
    return ("There is no wire and nothing moves. It walks into a volume of air and the link "
            "goes to noise inside it - your orders arrive somewhere behind where you sent "
            "them, and its own body reports back in the wrong order.")


def _hit_hook(s):
    limb = s.rng.choice(["left arm", "right arm", "tail"])
    B.hurt(s, limb, s.rng.uniform(20, 34), "cut")
    s.blood = B.clamp(s.blood - 6.0)
    B.tick(s, 26, exertion=1.5)
    return ("A weighted arm swings down out of the dark on a cord and what is on the end of "
            "it is a hook, and the hook finds its %s and keeps going." % limb)


# ---------------------------------------------------------------- the ones that can kill you
# These three do not degrade a limb and then hand you a problem. They go through the middle of
# the body and mortal.strike decides what that means - see hz/mortal.py. All three can end the
# run in the turn they happen, and all three can also be walked away from by a subject that was
# already moving, which is a trait and not luck.
def _hit_gun(s):
    from . import mortal as MO
    lines, _key = MO.strike(
        s, "SHOT", "a round through the chest", power=1.05, texts={
            "aside": ("The report and the body moving are the same event. It is flat behind a "
                      "rise with grit still coming down and a furrow in the ground where it "
                      "was standing, and nothing you sent had anything to do with it."),
            "killed": MO.impaled_text(s).replace("impaled clean through the chest",
                                                 "shot clean through the chest")
                        .replace("the shaft standing out of it", "the hole in itself"),
            "down": ("The round goes through it and the sound arrives afterwards, which is "
                     "the wrong order and is the last thing either of you notices about it. "
                     "It sits down hard, as if it had been asked to."),
            "standing": ("It is hit and it does not go down. It turns around once, all the "
                         "way, looking for what did it - and there is a post with a housing "
                         "on top of it a hundred paces back, already tracking to the next "
                         "thing that moves. Orange is coming out of the front of it and the "
                         "back of it at the same rate."),
            "graze": ("The round goes through the %s. Through - in one side and out the "
                      "other, clean, and the wound is a neat thing and the leg under it is "
                      "not." % s.rng.choice(["left arm", "right arm"])),
        })
    return "\n".join(lines)


def _hit_harpoon(s):
    from . import mortal as MO
    lines, _key = MO.strike(
        s, "PINNED", "a harpoon through the chest", power=1.15, texts={
            "aside": ("It is already going the other way when the line lets go. The head "
                      "buries itself in the rock where the body was and the cord behind it "
                      "goes tight and sings."),
            "killed": MO.impaled_text(s),
            "down": ("It goes through and takes it off its feet and puts it into the wall "
                     "behind it, and the head opens on the far side the way it was built to, "
                     "and it is pinned there, upright, with its feet not quite on the floor."),
            "standing": ("It is standing with a shaft through it and a cord running back into "
                         "the dark, and the cord is taut, and something at the other end of "
                         "the cord has started taking up the slack."),
            "graze": ("The head takes the %s and drags the whole body two paces sideways "
                      "before the barb tears back out through the muscle."
                      % s.rng.choice(["left leg", "right leg"])),
        })
    return "\n".join(lines)


def _hit_mine(s):
    from . import mortal as MO
    leg = _leg(s)
    # a mine is under it, so the leg goes first and the rest is what is left over
    B.hurt(s, leg, s.rng.uniform(55, 95), "sever" if s.rng.random() < 0.45 else "crush")
    lines, _key = MO.strike(
        s, "TOOK THE GROUND WITH IT", "a mine under the foot", power=0.85, texts={
            "aside": ("It puts weight down and takes it off again in the same movement, and "
                      "the ground where its foot was goes up behind it. It is fifteen paces "
                      "away before the dirt has finished coming down. Nothing you sent had "
                      "time to be part of that."),
            "killed": ("The ground opens under it. There is no moment where it looks down at "
                       "anything, because the part that would have done the looking is not "
                       "where it was, and the sound goes on rolling away down the passage "
                       "long after everything else has stopped."),
            "down": ("The ground goes off under its foot and puts the whole body in the air "
                     "sideways. It lands badly and a long way from where it started and does "
                     "not get up, and there is a great deal less of the %s than there was."
                     % leg),
            "standing": ("It is still up. One leg is ruined and it is still up, swaying, with "
                         "its ears flat and grit coming down out of its fur, and it has not "
                         "worked out yet that it should not be."),
            "graze": ("The charge was old and half of it did not go. It still takes the %s "
                      "out from under it." % leg),
        })
    return "\n".join(lines)


TRAPS = [
    # --- the three that can kill outright. Note the low `diff` on the gun: it is not hidden,
    # it is mounted in the open and it simply outranges noticing. What the spot roll buys you
    # is the chance to see the post before you are in its arc, not the chance to see a wire.
    {"id": "gun", "pins": False, "name": "a mounted gun on a post", "diff": 0.28, "w": 7,
     "zones": ["ridge", "shelf", "steppe", "glassways", "galleries", "pan", "cairns",
               "approach", "wire", "yard", "runs", "throat", "kiln", "lung"],
     "hit": _hit_gun,
     "seen": "There is a post ahead with a housing on top of it, and the housing turns when "
             "the body moves and stops when the body stops. It has been tracking for a while. "
             "Whatever it is waiting for, it is patient and it is powered and it is pointed "
             "down the only line through here.",
     "in": "It is hit. There is a post a hundred paces back with a housing on top of it that "
           "has already finished with this and is looking at something else."},
    {"id": "harpoon", "name": "a line gun in the dark", "diff": 0.20, "w": 7,
     "zones": ["sink", "silt", "rot", "burrow", "well", "lung", "chamber", "deep", "weave",
               "dock", "spine", "stores", "theatre"],
     "hit": _hit_harpoon,
     "seen": "Set into the wall at chest height, back in a recess, there is a tube on a frame "
             "with a coil of cord behind it, and the cord runs away into the dark and does not "
             "slacken anywhere you can see. It is aimed across the only gap.",
     "in": "There is a shaft through it and a cord coming off the end of the shaft, running "
           "back into a recess in the wall, and the cord is not slack."},
    {"id": "mine", "pins": False, "name": "something buried under the route", "diff": 0.34, "w": 8,
     "zones": ["flats", "steppe", "fence", "grey", "dust", "cairns", "pan", "descent",
               "stacks", "silt", "weave", "kiln", "outfield", "wire", "yard", "runs"],
     "hit": _hit_mine,
     "seen": "The dust in one place sits differently to the dust everywhere else - a disc of "
             "it, a pace across, settled rather than blown. Under the disc there is a plate, "
             "and the plate is waiting for weight.",
     "in": "The ground went off under it. There is a crater where its foot was and the rest "
           "of it is a considerable distance away from the crater."},
    {"id": "snare", "name": "a cable snare", "diff": 0.10, "w": 10,
     "zones": ["woods", "fence", "grey", "teeth", "roots", "galleries", "stacks", "burrow",
               "rot", "weave"],
     "hit": _hit_snare,
     "seen": "It stops with one foot up. There is a loop of cable lying in the dust with the "
             "dust arranged over it, and a bent sapling of scrap behind it holding the "
             "tension. Somebody set this, and set it well, and did not come back for it.",
     "in": "It is on its side with the cable closed above the hock and the tension still "
           "coming off the scrap behind it. Every movement it makes tightens it."},
    {"id": "pit", "name": "a covered pit", "diff": 0.16, "w": 10,
     "zones": ["flats", "dust", "grey", "wake", "shaft", "galleries", "descent", "stacks",
               "silt", "deep", "weave"],
     "hit": _hit_pit,
     "seen": "The ground ahead is the same colour as the ground everywhere else and it is "
             "sitting a finger lower than it should be, over a square. Dug, covered, and "
             "swept.",
     "in": "It is at the bottom of a dug hole with dust coming down on it and daylight a body "
           "and a half above its head."},
    {"id": "deadfall", "name": "a deadfall", "diff": 0.22, "w": 9,
     "zones": ["teeth", "galleries", "glassways", "shaft", "ribs", "throat", "weave", "kiln",
               "chamber"],
     "hit": _hit_deadfall,
     "seen": "There is a prop under a great deal of rock and a line off the prop across the "
             "way through. The whole of the ceiling here is waiting on one piece of timber.",
     "in": "It is down with rock across it and the rock is not going to move because it wants "
           "to."},
    {"id": "glass", "name": "a bed of set shards", "diff": 0.14, "w": 9,
     "zones": ["steppe", "pan", "glassways", "teeth", "slope", "throat", "kiln"],
     "hit": _hit_glass,
     "seen": "The dust in front of it has a grain to it that the dust either side does not. "
             "Under the grain there are points, set upright, in rows, for twenty paces.",
     "in": "It is standing in the middle of them with both back feet through and no clean "
           "ground within two paces in any direction."},
    {"id": "tripline", "name": "a line at head height", "diff": 0.26, "w": 8,
     "zones": ["woods", "ridge", "cairns", "galleries", "approach", "ribs", "silt", "weave",
               "lung"],
     "hit": _hit_tripline,
     "seen": "There is a thread of something across the way through at the height of its head, "
             "catching light along one edge of itself and nowhere else.",
     "in": "It is down on its side with a line of orange coming off the side of its head and "
           "the wire still humming above it."},
    {"id": "jaws", "name": "buried steel", "diff": 0.20, "w": 8,
     "zones": ["fence", "flats", "boneyard", "cairns", "galleries", "roots", "burrow", "silt",
               "well", "weave"],
     "hit": _hit_jaws,
     "seen": "Two hand-widths of disturbed ground with a shine at the edge of it. Old steel, "
             "set, and still under tension after however long it has been there.",
     "in": "The steel is shut on its leg and the two halves of it are held together by a "
           "spring nothing on this body is strong enough to open by pulling."},
    {"id": "spores", "name": "a swelling in the floor", "diff": 0.18, "w": 8,
     "zones": ["roots", "dust", "hollow", "sink", "rot", "silt", "lung", "well"],
     "hit": _hit_spores,
     "seen": "The floor ahead is domed, over about a pace, and the dome is breathing - very "
             "slightly, and not in time with anything.",
     "in": "It is standing inside a grey column that has not finished going up yet, and it "
           "has already taken a breath."},
    {"id": "net", "name": "a lift net", "diff": 0.24, "w": 7,
     "zones": ["woods", "cairns", "approach", "galleries", "slope", "ribs", "rot", "lung",
               "chamber"],
     "hit": _hit_net,
     "seen": "There is cord under the leaf litter running to a bent thing overhead, and the "
             "cord is laid in a circle about the size of a body.",
     "in": "It is off the ground and upside down in a bag of cord, turning slowly, with "
           "everything it was carrying now underneath it."},
    {"id": "vent", "name": "a pressure plate", "diff": 0.28, "w": 7,
     "zones": ["thermals", "furnace", "glassways", "pan", "throat", "kiln", "lung"],
     "hit": _hit_vent,
     "seen": "One plate in the floor sits proud of the others and there is a slot beside it "
             "with heat coming off the slot.",
     "in": "The vent is open and it is in front of the vent and the vent has not finished."},
    {"id": "wire", "name": "barbed coil", "diff": 0.12, "w": 7,
     "zones": ["fence", "ridge", "boneyard", "shelf", "stacks", "throat", "weave", "kiln"],
     "hit": _hit_wire,
     "seen": "A gap in the rock with wire coiled loose across it, barbed every hand's width, "
             "put there to be gone into rather than climbed over.",
     "in": "It is in the coil and the coil has closed the way coils do. Every movement is "
           "another cut and standing still is also not free."},
    {"id": "sinkhole", "name": "a lid of floor", "diff": 0.30, "w": 6,
     "zones": ["dust", "grey", "hollow", "descent", "sink", "silt", "rot", "deep", "well",
               "chamber"],
     "hit": _hit_sink,
     "seen": "It stops and will not go on. The floor ahead rings differently under one paw "
             "and there is no edge to the part that rings.",
     "in": "It is a long way down in the dark, on top of what broke its fall, and the hole it "
           "came through is a shape of light a very long way above it."},
    {"id": "barbs", "name": "set bone", "diff": 0.15, "w": 6,
     "zones": ["boneyard", "roots", "wake", "cairns", "ribs", "rot", "stacks", "deep"],
     "hit": _hit_barbs,
     "seen": "Bone in the floor, split and set with the points up, in rows going across the "
             "way through rather than along it. Somebody cut every one of these.",
     "in": "It is standing in the rows with two of them through the pad of a foot and the "
           "rows going on for some distance in front of it."},
    {"id": "hum", "name": "a volume of bad air", "diff": 0.34, "w": 6,
     "zones": ["ridge", "glassways", "furnace", "pan", "steppe", "throat", "deep", "kiln",
               "lung"],
     "hit": _hit_hum,
     "seen": "The chip loses a word and gets it back. Then loses two. There is a shape of air "
             "in front of it that the link does not like and the shape has an edge.",
     "in": "It is inside it. Everything you send arrives late and slightly to one side of "
           "what you meant, and the body is reporting in an order that is not the order it "
           "happened in."},
    {"id": "hook", "name": "a weighted arm", "diff": 0.32, "w": 5,
     "zones": ["galleries", "glassways", "hollow", "teeth", "burrow", "ribs", "throat",
               "weave", "chamber"],
     "hit": _hit_hook,
     "seen": "There is a counterweight in the dark overhead on a short cord, and a line off "
             "the counterweight to something at chest height across the way through.",
     "in": "The arm has swung and the hook is in and the cord above it is still moving."},
]

BY_ID = {t["id"]: t for t in TRAPS}


# ---------------------------------------------------------------- the roll
def rate(s):
    """Per move. Deliberately NOT multiplied by danger_mult as well - the ground
    multiplier and the Destiny multiplier already stack, and putting a third one on
    top of them took Destiny to a trap every other step, which is not a hazard, it
    is a wall."""
    from . import regions as REG
    r = BASE_RATE * TRAP_RATE.get(REG.zone_set_key(s), 1.0)
    if REG.on_destiny(s):
        r *= DESTINY_RATE
    return r


def _pool(s):
    from . import world as W
    z = W.zone(s)["key"]
    out = [t for t in TRAPS if z in t["zones"]]
    return out or TRAPS


def roll(s, verb):
    """Called after a move. Returns a line, having already set the scene, or None."""
    from . import scenarios as SCN
    if s.over or s.crisis or s.scene or s.escape.get("active"):
        return None
    if verb not in ("go", "forward", "advance", "walk", "move", "onward", "escape", "evade"):
        return None
    if s.rng.random() > rate(s):
        return None
    t = s.rng.choices(_pool(s), weights=[x["w"] for x in _pool(s)], k=1)[0]
    seen = s.rng.random() < spot_chance(s, t["diff"])
    s.trap_seen = bool(seen)
    s.stats["traps"] = s.stats.get("traps", 0) + 1
    line = None
    if not seen:
        s.stats["traps_hit"] = s.stats.get("traps_hit", 0) + 1
        line = "*** IT WALKED INTO IT ***  " + t["hit"](s)
        s.note("TRAP: " + t["name"])
        s.pending_voice.append("hurt")
    else:
        s.note("TRAP SPOTTED: " + t["name"])
    SCN.chain(s, "trap_" + t["id"])
    return line


# ---------------------------------------------------------------- shared reactions
def _disarm(s, tid):
    """Take it apart rather than walk round it. There is kit in every one of these."""
    t = BY_ID[tid]
    B.tick(s, 30, exertion=1.1)
    hard = t["diff"] + 0.25 - 0.004 * float(getattr(s, "intel", 14.0))
    if B.arms_usable(s) == 0:
        return ("It has nothing that closes to take this apart with. It stands over the thing "
                "and looks at it and that is the whole of what it can do.")
    if s.rng.random() < max(0.08, hard):
        limb = _arm(s)
        B.hurt(s, limb, s.rng.uniform(8, 18), "cut")
        return ("It gets both hands into the mechanism and the mechanism goes off while its "
                "hands are in it. Its %s takes it. The thing is disarmed, at least." % limb)
    from . import intel as IN
    ln = IN.gain(s, "read")
    if ln:
        s.feedback.append(ln)
    # The three that can kill you outright are the only things in the game worth more taken
    # apart than avoided. Walk round a harpoon and you have walked round a harpoon; take it
    # apart and you are carrying it.
    PRIZE = {"harpoon": ("line gun", 1,
                         " It comes off the frame in one piece with the coil still on it, and "
                         "the body carries it away pointed at the floor, which nobody taught "
                         "it either."),
             "mine": ("charge", 1,
                      " It lifts the whole thing out of its seat with two fingers under the "
                      "lip, sets it down, and looks at you. It has not gone off. It is still "
                      "entirely willing to."),
             "gun": ("cell", 1,
                     " The housing is bolted to the post and none of it is coming with you, "
                     "but the thing behind the housing is a cell, and the cell is still warm.")}
    if tid in PRIZE:
        name, n, extra = PRIZE[tid]
        I.give(s, name, n)
        return ("It takes the thing apart from the side, slowly, the way you take apart "
                "something that is still live." + extra)
    got = s.rng.choice([("cord", 2), ("scrap", 2), ("shard", 1), ("cord", 1)])
    I.give(s, got[0], got[1])
    return ("It takes the thing apart from the side, slowly, the way you take apart something "
            "that is still under tension. %d %s off it, and one more piece of evidence that "
            "somebody stood here and built this." % (got[1], got[0]))


def _around(s):
    B.tick(s, 45, exertion=1.2)
    s.distance = max(0.0, s.distance - 0.4)
    return ("It goes the long way round, well clear, and keeps looking back at the place the "
            "whole time it is passing it. It costs most of an hour and it costs a little "
            "ground and it costs nothing else.")


def _through(s, tid):
    """Walk it anyway. Sometimes that is the right call and sometimes it is not."""
    t = BY_ID[tid]
    if s.rng.random() < 0.55:
        B.tick(s, 15, exertion=1.3)
        return ("It goes through on the line you gave it, placing each foot exactly, and "
                "nothing happens at all. The thing is still sitting there behind it.")
    return "It goes through on the line you gave it. " + t["hit"](s)


def _tear(s, tid):
    """Get out fast and pay for it."""
    t = BY_ID[tid]
    B.tick(s, 20, exertion=2.0)
    limb = _leg(s) if tid in ("snare", "jaws", "barbs", "glass") else _arm(s)
    B.hurt(s, limb, s.rng.uniform(14, 30), "cut")
    s.strain = B.clamp(s.strain + 12.0)
    return ("It does not wait to be told twice. It comes out of %s by taking what is holding "
            "it and pulling until something gives, and what gives is its %s."
            % (t["name"], limb))


def _work(s, tid):
    """Get out slowly and pay in time."""
    B.tick(s, 70, exertion=1.3)
    s.fatigue = B.clamp(s.fatigue + 8.0)
    if s.rng.random() < 0.18:
        limb = _leg(s)
        B.hurt(s, limb, s.rng.uniform(6, 14), "blunt")
        return ("You talk it through it a piece at a time. It takes over an hour, it is worse "
                "than it needed to be, and its %s is not right afterwards - but it is out and "
                "it is out whole." % limb)
    return ("You talk it through it a piece at a time, and it holds still for all of it, which "
            "for a thing in a trap is the hardest instruction there is. It takes over an hour. "
            "It comes out of it with nothing new wrong.")


def _cut(s, tid):
    B.tick(s, 35, exertion=1.2)
    I.take(s, "shard", 1)
    return ("It gets an edge onto whatever is holding it and works it until the hold parts. "
            "The edge does not survive it. The leg does.")


def _clear_arc(s):
    """Nothing is holding it. What it needs is to not be where it is."""
    B.tick(s, 20, exertion=1.6)
    s.strain = B.clamp(s.strain + 10.0)
    if s.rng.random() < 0.72:
        return ("You get it moving and keep it moving, low, in a line that is not the line it "
                "was hit on, until there is something solid between the body and whatever did "
                "it. It sits down behind the solid thing. It is still leaking.")
    from . import mortal as MO
    MO.chest_wound(s, 0.35, "a second one on the way out")
    return ("You get it up and moving and it takes another one on the way out of the arc. "
            "This one goes through the top of the shoulder and out again and it keeps going, "
            "because you told it to keep going.")


def _lie_still(s):
    """Some of them have worked out that moving is what the thing is looking for."""
    B.tick(s, 40, resting=True)
    s.pain = B.clamp(s.pain - 4.0)
    if SUB.trait(s, "wary") > 0.5 or s.rng.random() < 0.5:
        return ("It goes flat and stops. Completely - not breathing in any way that shows, for "
                "long enough that you start checking the readout. Whatever was tracking it "
                "stops tracking it and goes back to looking at the place it expects things to "
                "come from.")
    return ("It lies still. It lies still for a long time, bleeding, and nothing changes "
            "except how much of it there is.")


def _pack(s):
    from . import mortal as MO
    return MO.pack_chest(s)


def build_traps(SC, O):
    """One scene per trap, built off the table. Two faces: seen, and already in it."""
    out = []
    for t in TRAPS:
        tid = t["id"]

        def _text(s, t=t):
            return (("IT HAS STOPPED.\n  " + t["seen"] + "\n  It has not moved and it is not "
                     "going to until you say something.")
                    if getattr(s, "trap_seen", False)
                    else ("IT IS IN IT.\n  " + t["in"]))

        def _seen(s):
            return bool(getattr(s, "trap_seen", False))

        def _stuck(s):
            return not bool(getattr(s, "trap_seen", False))

        opts = [
            O("Have it take the thing apart", lambda s, tid=tid: _disarm(s, tid), req=_seen),
            O("Go around it, well clear", lambda s: _around(s), req=_seen),
            O("Send it through anyway", lambda s, tid=tid: _through(s, tid), req=_seen),
            O("Have it tear itself out now", lambda s, tid=tid: _tear(s, tid), req=_stuck),
            O("Talk it through getting out slowly",
              lambda s, tid=tid: _work(s, tid), req=_stuck),
            O("Cut it free", lambda s, tid=tid: _cut(s, tid),
              req=lambda s: _stuck(s) and I.has(s, "shard")),
        ]
        # a gun and a mine do not hold onto anything. Being hit by one is not being caught in
        # one, so the three getting-out-of-it options are replaced by the three things there
        # actually are to do about a hole.
        if not t.get("pins", True):
            opts = [o for o in opts if o["req"] is not _stuck] + [
                O("Get it out of the line of it", lambda s: _clear_arc(s), req=_stuck),
                O("Pack the wound", lambda s: _pack(s), req=_stuck),
                O("Have it lie completely still", lambda s: _lie_still(s), req=_stuck),
            ]
        out.append(SC("trap_" + tid, _text, opts, zones=["__sprung__"], w=1,
                      danger=0.45))
    return out
