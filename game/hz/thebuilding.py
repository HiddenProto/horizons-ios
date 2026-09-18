"""THE FINAL - the building, from outside it.

Every act before this one walks AWAY. The horizon is away, the battery is away, the house on
the rock is away, and the empty room at the bottom of the deep is as far away as away goes.
When a subject has done all of that and come back up there is exactly one direction left that
it has never been sent, and it is the one it started from.

So the last act is the facility. Not a ruin - it is running. The lights are on, the doors still
answer, the taps still have pressure, and there is nobody in any of the rooms. A programme this
size does not stop because the people stopped; it simply runs, and the thing it runs is a loop
that begins with a body on a clean floor and ends with a number cut into a stone.

WHAT MAKES IT DIFFERENT FROM THE OTHER ACTS

  - It is very long and it is not a walk. Twelve grounds and three hundred-odd units, and the
    ground is not what stops you - DOORS stop you. Getting from the grass outside the wire to
    the bench is a chain of problems that have to be solved with things that have to be made,
    and the act starts on open ground with nothing, exactly like the first hour of the first
    walk, and ends inside the room where that walk was planned.
  - It saves. Every new ground is a checkpoint written to that subject's own slot on disk, and
    `leave` puts the run down and keeps it. Come back tomorrow and it picks up where it stood.
    Nothing else in the game does this, because nothing else in the game is an hour long.
  - It does not let you off with dying, and that is not mercy. Die inside the fence and the
    programme does what the programme is for: it collects the body, repairs it to the standard
    the budget allows, seats the chip again and puts it back. You resume at the checkpoint with
    the count one higher and the body carrying the repair for good. There is a limit on how
    many times a thing is worth repairing.
  - THE SWEEP. The building is still looking for loose subjects on a schedule. It gives one
    turn of warning and then it comes through, and the answer is shelter or `hide`, not speed.
  - THE LINK IS PERFECT HERE AND THAT IS THE PROBLEM. Every other act is a fight to stay in
    contact; inside the wire the noise drops to nothing and the chip sits clean all the way in,
    and the body does not want to be here and keeps saying so.
  - THE COUNT RESOLVES. The cairns counted something. The shelves are numbered in the same
    series, so is the log at the bench, and the three together are the only place the game says
    what has been happening. It is optional, and it is the best ending.

Nothing here is in the README, which does not mention Destiny either.
"""
from . import body as B
from . import items as I
from . import subjects as SUB

# ---------------------------------------------------------------- the ground
# Twelve of them. Cold runs very low once it is inside - the heating works - and the danger
# curve is flatter than Destiny's, because what kills you in here is time and the sweep rather
# than the ground itself.
BUILDING_ZONES = [
    {
        "key": "outfield", "name": "The Approach", "at": 0.0, "danger": 0.24, "cold": 0.15,
        "gather": {"scrap": 3, "cloth": 2, "cord": 3, "water": 4, "shard": 3, "ration": 3,
                   "resin": 2, "meat": 2, "glowmoss": 2, "branch": 2},
        "blurb": "Long grass and old tyre ruts, and at the end of it a fence with the grass "
                 "worn off the far side. This fence. The one from the first hour of the first "
                 "walk. You have only ever seen this side of it going the other way.",
    },
    {
        "key": "wire", "name": "Inside The Wire", "at": 24.0, "danger": 0.30, "cold": 0.13,
        "gather": {"scrap": 4, "cord": 3, "cloth": 2, "water": 3, "shard": 3, "resin": 2,
                   "salve": 1, "ration": 2, "meat": 2, "branch": 2},
        "blurb": "The strip between the fence and the buildings, mown at some point this year "
                 "by something that is still doing it. Nothing grows tall enough in here to "
                 "get behind.",
    },
    {
        "key": "yard", "name": "The Yard", "at": 52.0, "danger": 0.36, "cold": 0.11,
        "gather": {"scrap": 6, "cord": 4, "resin": 3, "cloth": 2, "water": 2, "shard": 2,
                   "salve": 1, "ration": 1},
        "blurb": "Vehicles parked properly and not moved in years. A burn pit with a lid on "
                 "it. A pen with the gate standing open and the latch in perfect order.",
    },
    {
        "key": "dock", "name": "The Loading Dock", "at": 80.0, "danger": 0.44, "cold": 0.09,
        "gather": {"scrap": 6, "cord": 4, "cloth": 3, "resin": 3, "ration": 3, "shard": 2,
                   "water": 2, "map scrap": 1},
        "blurb": "Roller doors down, a shuttered office, and pallets of things that were "
                 "delivered after everybody stopped coming in to receive them.",
    },
    {
        "key": "intake", "name": "Intake", "at": 108.0, "danger": 0.46, "cold": 0.05,
        "gather": {"water": 5, "cloth": 3, "antisepsis": 3, "salve": 2, "scrap": 2,
                   "ration": 2, "cord": 2},
        "blurb": "A scale set into the floor, a hose on a reel, a drain, and a run of doors "
                 "that open on a timer. The timer is still keeping time.",
    },
    {
        "key": "wing", "name": "The Holding Wing", "at": 136.0, "danger": 0.50, "cold": 0.04,
        "gather": {"ration": 4, "water": 4, "cloth": 4, "salve": 2, "scrap": 2,
                   "antisepsis": 2, "cord": 2},
        "blurb": "The corridor it woke up in. It is longer than it was at the time and it has "
                 "a great many more doors on it than it had at the time.",
    },
    {
        "key": "runs", "name": "The Exercise Runs", "at": 164.0, "danger": 0.54, "cold": 0.08,
        "gather": {"water": 4, "cloth": 3, "cord": 3, "scrap": 3, "meat": 2, "ration": 2,
                   "hide": 2},
        "blurb": "Fenced lanes under a roof of wired glass, floor worn into a channel down the "
                 "middle of each one. The doors at both ends of every lane stand open now.",
    },
    {
        "key": "theatre", "name": "The Theatre", "at": 192.0, "danger": 0.62, "cold": 0.05,
        "gather": {"antisepsis": 6, "salve": 4, "coagulant": 3, "cloth": 3, "cord": 2,
                   "scrap": 2, "shard": 2, "water": 2},
        "blurb": "Lights that come on when something walks under them, instruments laid out in "
                 "order of use, and a table with the restraints left open. Everything in here "
                 "is clean and nothing in here is new.",
    },
    {
        "key": "stores", "name": "The Stores", "at": 220.0, "danger": 0.56, "cold": 0.03,
        "gather": {"ration": 6, "cloth": 4, "scrap": 3, "cord": 3, "resin": 3, "water": 2,
                   "map scrap": 2, "marrow": 1},
        "blurb": "Racking floor to ceiling, going back further than the light does. Every "
                 "shelf is labelled, the labels are numbers, the numbers are a series, and the "
                 "series is very long.",
    },
    {
        "key": "archive", "name": "The Archive", "at": 248.0, "danger": 0.58, "cold": 0.04,
        "gather": {"map scrap": 4, "cloth": 3, "scrap": 3, "cord": 2, "water": 2, "resin": 2,
                   "ration": 1},
        "blurb": "Paper. Rooms of it, on rails, and a card reader on the door that has been "
                 "waiting patiently for a card since before any of this started.",
    },
    {
        "key": "spine", "name": "The Spine", "at": 276.0, "danger": 0.74, "cold": 0.02,
        "gather": {"scrap": 6, "cord": 6, "resin": 3, "shard": 3, "water": 2, "cloth": 1},
        "blurb": "The floor the machines are on. Heat coming off it in a column, cable in "
                 "bundles thicker than a leg, and a sound the chip hears and the body does not.",
    },
    {
        "key": "bench", "name": "The Bench", "at": 300.0, "danger": 0.60, "cold": 0.04,
        "gather": {"antisepsis": 3, "cloth": 3, "water": 3, "salve": 2, "scrap": 2,
                   "ration": 2},
        "blurb": "One room at the end of one corridor, with a bench in it and a chair pulled "
                 "up to the bench at working distance. The light over it is the only light in "
                 "the building that was left on for somebody.",
    },
]

BUILDING_GOAL = 316.0


# ---------------------------------------------------------------- the doors
# What stops you in here is not the ground, it is a door, and every door has exactly one
# answer that is findable from inside the act. The message names the shape of the problem and
# never the recipe - working out that a cut fence needs something to cut it with is the act.
GATES = {
    "wire": {"any": ["cutters", "gate code"],
             "text": "The fence is four times the height of the body and there is no gap "
                     "under it anywhere it has walked. It is wire, and wire is a thing that "
                     "can be cut, by something that cuts."},
    "dock": {"any": ["pry bar"],
             "text": "The roller door is down and seated in its channel and the body cannot "
                     "get fingers under it. There is a lip. A lip wants a lever."},
    "intake": {"any": ["tone key", "door code"],
               "text": "The intake door has no handle on this side. There is a small grille "
                       "beside it that makes a sound when something comes near, and it is "
                       "waiting for a sound back."},
    "theatre": {"any": ["mask"],
                "text": "The air past the theatre doors is doing something to the back of its "
                        "throat within two steps and it will not go further, and it is right "
                        "not to. Whatever is in there needs filtering out of it."},
    "archive": {"any": ["plate key"],
                "text": "The archive door takes a card. There is a slot the size and shape of "
                        "a thin plate, and the reader beside it is lit and patient."},
    "spine": {"any": ["lagging"],
              "text": "The floor past the spine doors carries current through the deck plate "
                      "itself and the body can feel it through its feet from here. Nothing "
                      "crosses that barefoot."},
}


def gate_for(s, zone_key):
    """(blocked, text). The one hook that makes the Final a chain of problems and not a walk."""
    g = GATES.get(zone_key)
    if not g:
        return False, ""
    for need in g["any"]:
        if I.has(s, need) or s.has_flag(need.replace(" ", "_")):
            return False, ""
    return True, ("THE WAY ON IS SHUT. " + g["text"])


# ---------------------------------------------------------------- the sweep
# The building has not stopped looking for loose subjects. It is on a schedule, it gives one
# turn of warning, and the answer to it is shelter or cover - never speed.
SWEEP_EVERY = {"outfield": 0, "wire": 26, "yard": 24, "dock": 22, "intake": 18, "wing": 15,
               "runs": 16, "theatre": 14, "stores": 16, "archive": 15, "spine": 12,
               "bench": 14}


def _st(s):
    """The act's own bag of state. `s.final` is the flag; this is what the flag drags along."""
    if not isinstance(getattr(s, "fstate", None), dict):
        s.fstate = {}
    return s.fstate


def sweep_tick(s, zone_key):
    """Returns a list of lines. May call recover() if it walks into the body."""
    every = SWEEP_EVERY.get(zone_key, 0)
    if not every:
        return []
    st = _st(s)
    due = int(st.get("sweep_at", 0))
    if due <= 0:
        st["sweep_at"] = s.turn + every + s.rng.randint(0, 6)
        return []
    if s.turn == due - 1:
        return ["THE TONE IN THE ROOM CHANGES. Two notes, descending, and then the lights step "
                "up a level one bank at a time, coming this way. Something is about to come "
                "through here counting what it finds."]
    if s.turn < due:
        return []
    st["sweep_at"] = s.turn + every + s.rng.randint(0, 6)
    if s.eff("hidden") or s.eff("sheltered"):
        return ["IT CAME THROUGH. Slow, thorough, and close enough to hear the mechanism in "
                "it. It did not find anything worth logging, and the lights went back down "
                "behind it."]
    return ["IT CAME THROUGH AND THE BODY WAS STANDING IN THE OPEN."] + list(caught(s))


def caught(s):
    """Found in the open. It is not a fight and it was never going to be.

    Once the repair budget is gone, being collected is not a setback - a thing they have
    stopped putting back together does not get carried back to where it was working."""
    txt = ("What comes round the corner is not a person and it is not an animal. It is the "
           "thing they built to move subjects, and it has been doing that for longer than "
           "anything alive in here. It does not hurry. It takes hold of the body properly, "
           "the way you take hold of something you do not want to damage, and the body - "
           "which has walked a planet, and gone down a mile of rock, and come back - stops "
           "fighting almost at once, because this is the one grip it has known since before "
           "it could see.")
    if spent(s):
        end = (txt + "\n\nIt does not put the body down at the last place it was "
               "working. It carries it the other way, through intake, past the wing, "
               "and into the stores, and it puts it on the shelf with its own number "
               "on the end plate, beside the box that was made up for it in advance.\n"
               "The link stays up for a surprisingly long time afterwards. Long enough "
               "to establish that nothing else is going to happen.")
        s.pending_death = ["PUT BACK", end]
        return [txt, "  (There is nothing left in the repair budget.)"]
    return [txt] + list(recover(s, "collected in the open", walked_back=True))


# ---------------------------------------------------------------- being repaired
WEAR_LIMIT = 8


def recover(s, why, walked_back=False):
    """The programme does what the programme is for. This is the Final's answer to dying, and
    the cost is that the count goes up and the body keeps the repair."""
    st = _st(s)
    wear = int(st.get("wear", 0)) + 1
    st["wear"] = wear
    st["count"] = int(st.get("count", 0)) + 1
    s.note("RECOVERED (%s) - wear %d" % (why, wear))
    # put it back together to the standard the budget allows
    for n, L in s.limbs.items():
        if L["state"] == "lost":
            continue          # they do not put one back. They never have
        if L["state"] in ("mangled", "broken", "gashed"):
            L["state"] = "bruised"
        L["hp"] = max(L["hp"], 62.0)
        L["bleed"] = 0.0
        L["bound"] = False
    s.blood = max(s.blood, 78.0)
    s.pain = min(s.pain, 22.0 + 4.0 * wear)
    s.infection = 0.0
    s.strain = 20.0
    s.fatigue = 30.0
    s.hunger = 35.0
    s.thirst = 35.0
    s.warmth = 62.0
    s.heat = 0.0
    s.snap = max(0.0, s.snap - 30.0)
    s.issues = []
    s.scene = None
    s.question = None
    # and what it keeps. Every repair leaves something that does not come out again.
    s.weird = min(96.0, max(s.weird, 6.0 * wear))
    s.chip = max(40.0, min(s.chip, 100.0 - 3.0 * wear))
    s.mood = B.clamp(s.mood - 6.0)
    s.will = B.clamp(s.will - 4.0)
    back = float(st.get("cp_distance", 0.0))
    s.distance = back
    s.add_eff("sheltered", 40)
    lines = [
        "IT IS PUT BACK TOGETHER. Not by anybody - by the room, on the schedule the room "
        "keeps, to the standard the budget allows. The chip comes up on a clean floor with "
        "the lights on, which is the oldest thing it knows, and the body under it has been "
        "closed up and dressed and is already standing.",
        "The number on the board by the door has gone up by one. It is the %d%s time it has "
        "gone up since you came through the wire." % (wear, _ord(wear)),
    ]
    if walked_back:
        lines.append("You are back where you were sleeping two grounds ago, because that is "
                     "where they put things down.")
    if wear >= WEAR_LIMIT - 1:
        lines.append("THE REPAIR IS NOT WHAT IT WAS. There is a stiffness through the whole "
                     "of it that was not there before, and the wrongness does not clear any "
                     "more, and somewhere in the notes there is a line about how many times a "
                     "thing is worth doing this to.")
    return lines


def _ord(n):
    return {1: "st", 2: "nd", 3: "rd"}.get(n if n < 20 else n % 10, "th")


def spent(s):
    return int(_st(s).get("wear", 0)) >= WEAR_LIMIT


# ---------------------------------------------------------------- shelter and cover
def hide(s):
    """One turn spent getting out of sight. It is the wary ones' act."""
    from . import world as W
    z = W.zone(s)["key"]
    p = 0.40 + 0.34 * SUB.trait(s, "wary") + 0.22 * SUB.trait(s, "silent")
    p -= 0.26 * SUB.trait(s, "jitter")
    p -= 0.18 if s.eff("lamp") else 0.0
    p += 0.12 if z in ("stores", "archive", "dock", "runs") else 0.0
    p -= 0.10 if z in ("intake", "bench") else 0.0
    p -= 0.004 * max(0.0, s.fatigue - 50.0)
    B.tick(s, 20, exertion=0.5)
    if s.rng.random() < max(0.08, min(0.94, p)):
        s.add_eff("hidden", 70)
        return ("It gets itself out of sight - under, behind, into - and goes still in the way "
                "it goes still, which is completely. You lose most of your own picture doing "
                "this. That is what it costs.")
    return ("It tries. There is nothing in here to get behind that is big enough for it, and "
            "it ends up pressed against a wall in plain view, which it appears to know.")


def shelter(s):
    """A made place, not a found one. This is where the act saves."""
    from . import world as W
    z = W.zone(s)["key"]
    have = I.has(s, "cloth") and (I.has(s, "cord") or I.has(s, "scrap"))
    if not have:
        return ("Making a place in here takes something soft and something to hold it up with, "
                "and it is carrying one or neither.")
    I.take(s, "cloth", 1)
    if I.has(s, "cord"):
        I.take(s, "cord", 1)
    else:
        I.take(s, "scrap", 1)
    B.tick(s, 90, resting=True)
    s.add_eff("sheltered", 300)
    s.add_eff("rested", 200)
    s.snap = max(0.0, s.snap - 8.0)
    s.mood = B.clamp(s.mood + 6.0)
    return ("It builds a place. Not a good one - a pocket wedged into the back of the %s out "
            "of the line of the doors, lined with what it was carrying, with one way in and "
            "that way facing a wall.\n"
            "It does not lie down in it straight away. It sits in the mouth of it for a while "
            "first, looking out, and then it does.\n"
            "  (This ground is held. The sweep does not find a made place, and the run is "
            "written down here.)" % W.zone(s)["name"].lower())


def the_bench(s):
    """The terminal scene: the room the chip is seated in, seen from the wrong end of it."""
    read = sum(1 for f in ("shelf_count", "chip_log", "intake_log") if s.has_flag(f))
    text = (
        "It is a workshop and it is not a large one. A bench, a chair at working distance, a "
        "lamp with its arm folded down, and a tray of very small tools laid out in the order "
        "you would use them. There is a cup on the bench with something dried in the bottom "
        "of it.\n"
        "The station is live. It has been live the whole time. There is a session open on it "
        "and the session is this one - your telemetry, your link figure, the last order you "
        "gave - arriving here at the speed it happens and being written down by nothing. "
        "Nobody has sat in the chair for a long time. The programme did not need anybody to.\n"
        "Your subject has stopped in the doorway. It has not been told to stop. It knows this "
        "room the way it knows how to breathe: this is the room where it is put on the bench. "
        "It has come all the way here on its own legs. The bench is right there and nothing is "
        "holding it."
    )
    opts = ["Have it get on the bench", "Have it sit in the chair instead"]
    if read >= 2:
        text += ("\nThe log on the station is numbered. It is the same series as the shelves, "
                 "and the same series as the stones.")
        opts.append("Read the log all the way back")
    opts.append("Have it reach up and take the chip out")
    opts.append("Turn it round and walk it back out")
    return {"sid": "the_bench", "text": text, "opts": opts,
            "map": list(range(len(opts))), "age": 0, "danger": 0.0}
