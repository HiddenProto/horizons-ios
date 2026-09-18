"""Scenarios for THE FINAL - the facility, walked back into from the grass outside.

Same house rules as every other bank: every option does something mechanical, anything needing
a limb or an item is gated with `req` so it is never offered as a lie, and nothing in here
explains the setting.

Three of these scenes are load-bearing and the rest are the act. The load-bearing ones are the
three numbered records - the scale in intake, the shelf labels in the stores, the log on the
spine terminal - because holding two of the three is what opens the last option in the last
room. None of them is marked as important and all three can be walked past.

One scene pays off a tell. 682 taps a rhythm at walls all game, short short long, identically
spaced. The intake grille is waiting for a sound, and the sound is that.
"""
from . import body as B
from . import items as I
from . import subjects as SUB


def _hurt(s, limb, amount, kind="blunt"):
    return B.hurt(s, limb, amount, kind)


def _leg(s):
    return s.rng.choice(["left leg", "right leg"])


def _arm(s):
    return s.rng.choice(["left arm", "right arm"])


def _read_gain(s, why="read"):
    from . import intel as IN
    ln = IN.gain(s, why)
    if ln:
        s.feedback.append(ln)


# ---------------------------------------------------------------- the approach
def _follow_ruts(s):
    B.tick(s, 50, exertion=1.1)
    I.give(s, "scrap", 1)
    I.give(s, "cord", 1)
    return ("It walks the ruts instead of the grass, which is easier going and completely "
            "exposed. They run to a gate in the fence that is shut, and the shutting of it is "
            "recent enough that the grass under the bar has not grown back.")


def _grass_lie(s):
    B.tick(s, 70, resting=True)
    s.add_eff("hidden", 60)
    s.mood = B.clamp(s.mood + 3.0)
    return ("It lies down in the long grass with its chin on its front feet and watches the "
            "fence for an hour and does not get bored. Nothing comes out. Nothing goes in. A "
            "light in one of the buildings changes from one window to another and comes back.")


def _test_wire(s):
    B.tick(s, 20)
    _hurt(s, _arm(s), s.rng.uniform(4, 9), "burn")
    return ("It puts the back of one hand against the wire, the way you test a thing you "
            "intend to survive testing, and takes it off again immediately. There is current "
            "in it. Not enough to kill this body. Enough to make the point.")


def _walk_line(s):
    B.tick(s, 110, exertion=1.2)
    if s.rng.random() < 0.55:
        s.flag("gate_code")
        _read_gain(s, "read")
        return ("It walks the fence line for two hours and finds, a long way round the back, a "
                "panel where somebody has already done this - wire cut and bent back and wired "
                "shut again afterwards, neatly, from the inside. There is a keypad on the post "
                "beside it and the numbers that get used are worn paler than the ones that do "
                "not.\n"
                "  (The way through the wire is open to you.)")
    I.give(s, "cord", 2)
    I.give(s, "scrap", 1)
    return ("Two hours of fence. It is the same fence the whole way. It comes back with wire "
            "offcuts and a fence-post cap and nothing else.")


# ---------------------------------------------------------------- inside the wire
def _mower(s):
    B.tick(s, 30)
    if s.eff("hidden") or s.rng.random() < 0.45:
        return ("The thing that keeps the strip mown comes along it at walking pace, blind, "
                "cutting. It goes past close enough to throw grass onto the body and does not "
                "register it at all. It is not looking for anything. It is only mowing.")
    limb = _leg(s)
    _hurt(s, limb, s.rng.uniform(16, 30), "cut")
    return ("The thing that keeps the strip mown comes along it at walking pace, blind, and "
            "the body does not get out of the way in time, and it does not stop or slow or "
            "notice. It takes a strip out of the %s and carries on to the end of the run." % limb)


def _open_ground(s):
    B.tick(s, 45, exertion=1.3)
    s.distance = min(s.distance + 2.0, s.distance + 2.0)
    return ("It crosses the mown strip fast and flat with its belly low, which is not "
            "something anybody trained into it, and gets into the shadow of the first "
            "building without stopping once.")


# ---------------------------------------------------------------- the yard
def _burn_pit(s):
    B.tick(s, 80, exertion=1.5)
    s.mood = B.clamp(s.mood - 5.0)
    s.learn("The building disposes of what it finishes with, in a pit, with a lid on it.")
    if s.rng.random() < 0.5:
        I.give(s, "scrap", 2)
    return ("It gets the lid off the pit and goes down into it to the shoulder.\n"
            "Ash, and under the ash the parts of a fire that do not burn: staples, and plates, "
            "and seatings, and the small bright rings that go through an ear. Hundreds of the "
            "rings. It brings a handful up and turns them over and puts them down in a row on "
            "the lid, which is a thing it does for no reason you can see.")


def _strip_vehicle(s):
    B.tick(s, 60, exertion=1.3)
    I.give(s, "scrap", 3)
    I.give(s, "cord", 2)
    if s.rng.random() < 0.4:
        I.give(s, "resin", 2)
    return ("It works a panel off one of the vehicles and takes the loom out from behind it. "
            "The keys are in the thing. Nobody who parked it thought they were parking it for "
            "the last time.")


def _the_pen(s):
    B.tick(s, 35)
    s.snap = min(100.0, getattr(s, "snap", 0.0) + 6.0)
    s.mood = B.clamp(s.mood - 4.0)
    return ("The pen is six paces by six and the gate stands open and the latch works "
            "perfectly. It goes in. It walks the inside of the fence line twice, in the worn "
            "channel that is already there, and then stands in the middle facing the gate, and "
            "stays standing there until you tell it to come out.")


# ---------------------------------------------------------------- the dock
def _pallets(s):
    B.tick(s, 55, exertion=1.1)
    I.give(s, "ration", 3)
    I.give(s, "cloth", 2)
    if s.rng.random() < 0.5:
        I.give(s, "antisepsis", 1)
    return ("Pallets, shrink-wrapped, delivered and signed for and never broken down. Feed, "
            "dressings, cleaning stock. The dates on the outer wrap are the most recent dates "
            "you have seen anywhere in here and they are not recent.")


def _office(s):
    if s.intel < 26 and SUB.trait(s, "reads") <= 0:
        B.tick(s, 30)
        return ("There is paper pinned up behind the glass and it is covered in the small "
                "black marks. It looks at them for a while. They stay marks.")
    B.tick(s, 45)
    s.flag("door_code")
    _read_gain(s, "read")
    return ("Pinned behind the glass, under a rota that stops mid-month, there is a laminated "
            "card headed ENTRY - INTAKE, and under the heading a sequence written as three "
            "lengths: short, short, long.\n"
            "  (You know what intake wants now.)")


def _roller(s):
    if not I.has(s, "pry bar"):
        B.tick(s, 25, exertion=1.2)
        _hurt(s, _arm(s), s.rng.uniform(5, 11), "crush")
        return ("It gets its fingers into the gap at the bottom of the roller door and lifts "
                "with everything it has, and the door moves about the width of a claw and "
                "comes back down on its hand.")
    B.tick(s, 40, exertion=1.4)
    return ("The bar goes under the lip and the door comes up in four heaves, and it holds it "
            "on its shoulder while it works out how to prop it, which it does, with a length "
            "of pallet, without being told to.")


# ---------------------------------------------------------------- intake
def _grille(s):
    sid = getattr(s, "subject", "")
    if s.has_flag("door_code") or sid == "680":
        B.tick(s, 20)
        s.flag("door_code")
        if sid == "680":
            return ("Before you have decided anything it has put one knuckle against the "
                    "grille and tapped. Short, short, long. The same spacing it has been "
                    "putting into walls the entire way here.\n"
                    "The door opens. It waits for it to finish opening, and then it goes "
                    "through, and it does not look at you.")
        return ("You have it knock the sequence into the grille - short, short, long - and the "
                "grille chirps back the same shape an octave down, and the door opens.")
    B.tick(s, 30)
    s.weird = B.clamp(s.weird + 2.0)
    return ("The grille makes a sound when the body comes near it: two notes, rising, and then "
            "it waits. After a while it makes them again, more slowly, the way you repeat "
            "something to somebody who has not understood it. Then it stops.")


def _scales(s):
    B.tick(s, 25)
    s.flag("intake_log")
    _read_gain(s, "read")
    s.mood = B.clamp(s.mood - 3.0)
    return ("It steps onto the scale set into the floor. You did not tell it to. It steps on, "
            "and squares itself up, and stands still with its head down, and waits.\n"
            "The display above it wakes and takes the weight, and then it prints a line to the "
            "board beside the door, and the line has a number at the front of it that is not "
            "the weight. The number is nine digits long and the last three of them are close "
            "to the number cut into the stones.")


def _hose(s):
    B.tick(s, 35)
    I.give(s, "water", 4)
    s.warmth = B.clamp(s.warmth - 4.0)
    s.infection = B.clamp(s.infection - 6.0)
    return ("The hose on the reel still has pressure. It stands in the middle of the drain and "
            "lets you run it over the whole of it, ears flat, absolutely still, because this "
            "is a thing that has been done to it on this exact tile more times than either of "
            "you could count.")


# ---------------------------------------------------------------- the wing
def _doors(s):
    B.tick(s, 60)
    if s.rng.random() < 0.35:
        s.weird = B.clamp(s.weird + 6.0)
        s.mood = B.clamp(s.mood - 6.0)
        return ("It goes down the corridor opening doors. Clean floor, clean drain, a bowl, a "
                "light left on. Clean floor, clean drain, a bowl. Clean floor, clean drain, a "
                "bowl, and something in the corner of that one that has been there a long "
                "time and is not going to be a problem for anybody.\n"
                "It shuts that door. It shuts it properly, with its shoulder, and stands "
                "against it for a moment.")
    I.give(s, "cloth", 2)
    I.give(s, "ration", 2)
    return ("It goes down the corridor opening doors. Most of the rooms are made up and empty "
            "and have been for years - a bowl, a drain, a light on a timer still keeping to a "
            "day nobody is having. It strips the bedding out of three of them.")


def _own_room(s):
    B.tick(s, 40)
    s.mood = B.clamp(s.mood - 4.0)
    if not I.has(s, "plate key"):
        I.give(s, "plate key", 1)
        return ("One of the doors is its door. There is nothing about it that is different "
                "from the others and it walks straight to it anyway, and stops outside it "
                "without going in.\n"
                "Hanging on the hook beside the frame, where the chart goes, there is a "
                "lanyard with a thin card on the end of it and a name worn off the front. "
                "Whoever was working this corridor hung it up at the end of a shift and did "
                "not come back for it.")
    return ("It stands outside its own door again. It does not go in and it does not ask to.")


def _bowl(s):
    B.tick(s, 20)
    s.mood = B.clamp(s.mood + 4.0)
    s.hunger = B.clamp(s.hunger - 6.0)
    return ("There is a bowl in the room with its number over the door and there is still "
            "something in the bottom of it, dried to the glaze. It eats it. Of course it eats "
            "it. It is the only food it has ever had that arrived because somebody meant it "
            "to.")


# ---------------------------------------------------------------- the runs
def _lane(s):
    B.tick(s, 55, exertion=1.6)
    s.strain = B.clamp(s.strain + 6.0)
    s.mood = B.clamp(s.mood + 5.0)
    return ("It gets into the worn channel down the middle of one of the lanes and runs it. "
            "End to end, turn, end to end, turn, at the pace the channel was worn at. Nobody "
            "asked. There is a counter on the wall at the far end and it is still counting.")


def _glass_roof(s):
    B.tick(s, 45, exertion=1.2)
    if s.rng.random() < 0.3:
        limb = _arm(s)
        _hurt(s, limb, s.rng.uniform(10, 20), "cut")
        I.give(s, "shard", 3)
        return ("It goes up the mesh to the wired glass to see out and puts a pane through "
                "with its %s on the way down." % limb)
    I.give(s, "shard", 2)
    I.give(s, "cord", 2)
    return ("It goes up the mesh as far as the roof and hangs there looking out through the "
            "wired glass at the yard and the fence and the grass past the fence, for a long "
            "time, and then comes down and does not look up again.")


# ---------------------------------------------------------------- the theatre
def _the_table(s):
    sid = getattr(s, "subject", "")
    B.tick(s, 30)
    if sid == "680":
        s.snap = min(100.0, getattr(s, "snap", 0.0) + 14.0)
        s.mood = B.clamp(s.mood - 10.0)
        return ("It stops in the doorway of the theatre and does not come in.\n"
                "Nothing comes down the link. Nothing has come down the link from this one in "
                "seven years. It stands in the doorway looking at a table with the restraints "
                "left open, in a room it has been in more times than anybody in this building "
                "has been in any room, and the thing you can feel through the chip is not fear "
                "and it is not anger. It is recognition, and it has nowhere to go.")
    s.snap = min(100.0, getattr(s, "snap", 0.0) + 6.0)
    s.weird = B.clamp(s.weird + 4.0)
    return ("The table is at working height and the restraints are open and the paper on it is "
            "fresh. It walks all the way round it twice. Then it puts one hand flat on the "
            "paper, briefly, the way you touch a thing to find out whether it is warm.")


def _the_tray(s):
    B.tick(s, 35)
    I.give(s, "antisepsis", 2)
    I.give(s, "salve", 2)
    if s.rng.random() < 0.5:
        I.give(s, "coagulant", 1)
    _read_gain(s, "use")
    return ("The tray is laid out in order of use and every instrument on it has been cleaned "
            "and put back. You have it take what will still work outside this room: the tubes, "
            "the sealed packets, the small bright things that stop bleeding.")


def _the_lights(s):
    B.tick(s, 25)
    s.weird = B.clamp(s.weird + 5.0)
    s.learn("The building is still running its procedures. Nobody has to be in it.")
    return ("The lights over the table come on when the body walks under them, all of them, at "
            "full, and a fan starts somewhere behind the wall, and a screen on the trolley "
            "wakes up and asks a question in a language of numbers and then answers it itself "
            "and goes back to sleep. The room got ready. There is nobody in the building to "
            "have got it ready for.")


# ---------------------------------------------------------------- the stores
def _shelves(s):
    if s.intel < 24 and SUB.trait(s, "reads") <= 0:
        B.tick(s, 30)
        return ("Every shelf has a plate on the end of it with marks on it. The marks are the "
                "same kind of marks as on the stones and they mean as much to this body as the "
                "stones did.")
    B.tick(s, 50)
    s.flag("shelf_count")
    _read_gain(s, "read")
    s.learn("The shelves are numbered in the same series as the marks on the cairns.")
    return ("You read the plates off the ends of the racking as it walks the aisle. They are "
            "numbers and they are in a series and the series does not restart at the end of "
            "the aisle - it carries on, into the next aisle, and the next, back past where the "
            "light reaches.\n"
            "  It is the same series as the stones. Not similar. The same.")


def _own_shelf(s):
    B.tick(s, 40)
    s.mood = B.clamp(s.mood - 6.0)
    I.give(s, "cloth", 2)
    I.give(s, "cord", 1)
    return ("There is a shelf with this subject's own number on the plate. There is a box on "
            "it. In the box: a folded coat its size, a collar with its number stamped into the "
            "tag, a spare set of the rings that go through an ear, and a sealed packet of the "
            "grey blocks.\n"
            "It is a kit. It was made up in advance, for this one, and it has been sitting "
            "here waiting for the day somebody needed to fit it out again.")


def _deep_racking(s):
    B.tick(s, 70, exertion=1.2)
    if s.rng.random() < 0.3:
        limb = _leg(s)
        _hurt(s, limb, s.rng.uniform(14, 26), "crush")
        return ("It goes back into the dark end of the racking, where the light does not, and "
                "something stacked badly forty years ago finishes coming down on its %s." % limb)
    I.give(s, "ration", 4)
    I.give(s, "resin", 2)
    I.give(s, "map scrap", 1)
    return ("It goes back into the dark end of the racking and comes out with an armful. The "
            "aisles keep going. Whatever else this place ran out of, it did not run out of "
            "stock.")


# ---------------------------------------------------------------- the archive
def _the_files(s):
    if s.intel < 30 and SUB.trait(s, "reads") <= 0:
        B.tick(s, 40)
        I.give(s, "cloth", 2)
        return ("Paper, in rooms of it, on rails. It pulls a folder out and holds it open for "
                "you and the marks do not resolve into anything at this distance through these "
                "eyes. It is patient about it for longer than you are.")
    B.tick(s, 65)
    _read_gain(s, "read")
    s.learn("Every subject in here has a file, and every file ends the same way.")
    return ("Folder after folder, and they are all the same folder: a number, a line of "
            "measurements, a list of what was done and on what date, and at the end of every "
            "single one of them a short entry in a different hand from the rest. The entries "
            "do not vary much. Recovered. Not recovered. Recovered, repaired, returned to "
            "programme. Not worth repairing.")


def _the_rails(s):
    B.tick(s, 45, exertion=1.3)
    if s.rng.random() < 0.28:
        limb = _arm(s)
        _hurt(s, limb, s.rng.uniform(12, 22), "crush")
        return ("The stacks run on rails and close up against each other when the wheel is "
                "turned, and it turns the wheel with the wrong hand in the wrong place.")
    I.give(s, "map scrap", 2)
    I.give(s, "cloth", 1)
    return ("It winds the stacks apart and goes down between them. There are floor plans in "
            "here - the whole site, every corridor, with the rooms named.")


# ---------------------------------------------------------------- the spine
def _cable(s):
    B.tick(s, 40, exertion=1.2)
    I.give(s, "cord", 4)
    I.give(s, "scrap", 2)
    s.chip = max(20.0, s.chip - 6.0)
    s.weird = B.clamp(s.weird + 8.0)
    return ("It takes a hand to one of the smaller bundles and pulls a run of it out of the "
            "tray, and something goes through your own picture while it does - a lag, a grey "
            "frame, the sound arriving before the movement.\n"
            "This is the first room in the world where the thing on the end of the link can "
            "reach the link.")


def _terminal(s):
    B.tick(s, 50)
    s.flag("chip_log")
    _read_gain(s, "read")
    s.weird = B.clamp(s.weird + 6.0)
    return ("There is a station at the end of the row with a keyboard and a screen, and the "
            "screen is not asleep. It is showing a session. It is showing THIS session - the "
            "vitals you have been reading, the link figure you have been reading, the last "
            "order you gave, arriving here as fast as it happens.\n"
            "At the top of it there is a serial and a count, and the serial is not the "
            "subject's. Nothing on this screen is about the animal at all.")


def _heat(s):
    B.tick(s, 35, exertion=1.1)
    s.heat = min(100.0, getattr(s, "heat", 0.0) + 14.0)
    s.thirst = B.clamp(s.thirst + 8.0)
    s.add_eff("warmed", 120)
    return ("The column of heat coming off the deck is the warmest thing on this site and the "
            "body wants to lie down in it, and does, and you have to get it up again. It is "
            "the first comfortable floor it has been on since the room it woke up in.")


# ---------------------------------------------------------------- the bank
def build_building(SC, O):
    """Nineteen scenes. The act is meant to be dense - this is a building, not a plain."""
    return [
        SC("fb_ruts", "Tyre ruts come out of the grass and run at the fence, and the grass in "
                      "them is flattened rather than grown over.",
           [O("Follow the ruts to where they go", _follow_ruts),
            O("Lie up in the long grass and watch the fence", _grass_lie)],
           zones=["outfield"], w=10),
        SC("fb_fence", "The fence. Four times the height of the body, wire, and the grass worn "
                       "off the far side of it in a strip that is mown.",
           [O("Have it test the wire", _test_wire),
            O("Walk the whole fence line looking for a way", _walk_line),
            O("Lie up and watch instead", _grass_lie)],
           zones=["outfield", "wire"], w=12, danger=0.2),
        SC("fb_mower", "Something is coming along the mown strip at walking pace. It is not "
                       "hurrying and it is not looking. It is cutting.",
           [O("Get out of the strip and let it pass", _mower),
            O("Cross behind it while it is going away", _open_ground)],
           zones=["wire"], w=12, danger=0.35, urgent=True),
        SC("fb_burnpit", "There is a pit in the corner of the yard with a steel lid on it and "
                         "a smell coming out from under the lid that the body reacts to before "
                         "you do.",
           [O("Get the lid off and go down into it", _burn_pit),
            O("Leave it and strip a vehicle instead", _strip_vehicle)],
           zones=["yard"], w=11),
        SC("fb_vehicles", "Vehicles, parked in marked bays, square to the lines. Flat tyres, "
                          "full windows, keys in them.",
           [O("Strip one for parts", _strip_vehicle),
            O("Look in the pen with the open gate", _the_pen)],
           zones=["yard"], w=10),
        SC("fb_pallets", "Inside the dock there are pallets still wrapped, stacked three high, "
                         "with delivery paper taped to the outside of every one.",
           [O("Break them open", _pallets),
            O("Get into the shuttered office instead", _office)],
           zones=["dock"], w=12),
        SC("fb_roller", "A roller door, down and seated, with a lip at the bottom of it and "
                        "daylight under the lip.",
           [O("Get it up", _roller),
            O("Try the office window instead", _office)],
           zones=["dock"], w=10),
        SC("fb_grille", "There is a grille beside the intake door at head height, and when the "
                        "body comes near it, it makes a sound and then waits.",
           [O("Have it answer the grille", _grille),
            O("Stand and listen to what it does", _grille)],
           zones=["intake"], w=13),
        SC("fb_scales", "A scale set flush into the floor of the intake bay, with a board on "
                        "the wall above it and a hose coiled on a reel beside it.",
           [O("Let it do what it is already doing", _scales),
            O("Use the hose on it", _hose)],
           zones=["intake"], w=12),
        SC("fb_doors", "The corridor has doors down both sides of it. Every one of them is "
                       "shut and none of them is locked.",
           [O("Open them", _doors),
            O("Go to the one it keeps looking at", _own_room)],
           zones=["wing"], w=13),
        SC("fb_ownroom", "It has stopped outside a door that is identical to all the other "
                         "doors, and it is not going in, and it is not moving on either.",
           [O("Let it stand there", _own_room),
            O("Send it in", _bowl)],
           zones=["wing"], w=11),
        SC("fb_lane", "Fenced lanes under wired glass, with the floor worn into a channel down "
                      "the middle of each one and a counter on the wall at the far end.",
           [O("Let it run the lane", _lane),
            O("Send it up the mesh to the roof", _glass_roof)],
           zones=["runs"], w=12),
        SC("fb_table", "The theatre. Lights over a table at working height, restraints left "
                       "open, fresh paper on it.",
           [O("Let it look at the table", _the_table),
            O("Clear the instrument tray", _the_tray),
            O("Walk it under the lights and see what the room does", _the_lights)],
           zones=["theatre"], w=14, danger=0.25),
        SC("fb_tray", "Instruments laid out in order of use, cleaned, on a cloth, in a room "
                      "where nothing has been done for years.",
           [O("Take what still works outside this room", _the_tray),
            O("Leave it and move through", _the_lights)],
           zones=["theatre"], w=11),
        SC("fb_shelves", "Racking to the ceiling with a plate on the end of every run, and "
                         "marks on every plate.",
           [O("Read the plates", _shelves),
            O("Go back into the dark end instead", _deep_racking)],
           zones=["stores"], w=14),
        SC("fb_ownshelf", "One of the shelves has this subject's own number on the end plate, "
                          "and there is a box on it.",
           [O("Open the box", _own_shelf),
            O("Read the plates along the aisle", _shelves)],
           zones=["stores"], w=12),
        SC("fb_files", "Rooms of paper on rails, and a wheel at the end of every stack for "
                       "winding them apart.",
           [O("Read the files", _the_files),
            O("Wind the stacks and go down between them", _the_rails)],
           zones=["archive"], w=14),
        SC("fb_spine", "Cable in bundles thicker than a leg, heat coming up off the deck in a "
                       "column, and a station at the end of the row with its screen awake.",
           [O("Go and look at the screen", _terminal),
            O("Pull a run of cable out of the tray", _cable),
            O("Let it lie down in the heat a while", _heat)],
           zones=["spine"], w=15, danger=0.3),
        SC("fb_heat", "The deck is warm. Properly warm - the first warm floor since the room "
                      "it woke up in, and it has noticed.",
           [O("Let it lie in it", _heat),
            O("Get it up and on", _terminal)],
           zones=["spine"], w=10),
    ]
