"""What is under the rock, and what is under that.

Destiny does not run the normal acts harder. It runs somewhere else entirely, and it does it
three times: the surface is another planet (rock.py), and the two acts below it are not the
crust and the core at all. They are a dug system and the thing it was dug toward.

  THE WARRENS   six layers, and every one of them was made by something with hands. It is the
                longest act in the game by a distance, and almost none of that length is
                danger - it is time. Food runs out. Wounds have days to turn. The thing on the
                end of the link has to be kept willing for a week rather than an afternoon.

  THE DEEP      six layers under the warrens, going toward whatever the digging was for.

The through-line started on the surface with the cairns - somebody walked the rock before you,
marked the whole route, and did not come back along it. The warrens are where the marks go.
None of this is explained anywhere outside the game and the README does not mention Destiny at
all, which is the point: this act assumes you have already walked the normal one.
"""

# ------------------------------------------------------------------ act two: the warrens
# Cold runs mild and turns over into heat near the bottom. These are the natural lengths; the
# stretch table in regions.py is what makes this act take a week.
WARREN_ZONES = [
    {
        "key": "stacks", "name": "The Stacks", "at": 0.0, "danger": 0.24, "cold": 0.09,
        "gather": {"scrap": 4, "shard": 3, "cord": 3, "water": 3, "cloth": 2,
                   "dust fungus": 3, "ration": 1,
                   "salve": 1},
        "blurb": "The cairns do not stop at the surface. They go in, and down, and the stacking "
                 "gets better the further in it goes, which is the wrong way round for "
                 "something built by a thing that was getting tired.",
    },
    {
        "key": "burrow", "name": "The Burrow", "at": 16.0, "danger": 0.40, "cold": 0.05,
        "gather": {"scrap": 3, "cord": 4, "hide": 3, "water": 3, "dust fungus": 4,
                   "meat": 2, "shard": 2, "coagulant": 1,
                   "salve": 1},
        "blurb": "Round in cross-section and smooth, which no tool does. Something went through "
                 "this rock the long way, repeatedly, over a length of time that does not bear "
                 "thinking about, and it went through it head first.",
    },
    {
        "key": "ribs", "name": "The Ribs", "at": 34.0, "danger": 0.56, "cold": 0.02,
        "gather": {"shard": 5, "scrap": 3, "marrow": 1, "hide": 3, "water": 2,
                   "antisepsis": 1, "meat": 3, "ration": 1, "charcoal": 2,
                   "salve": 1},
        "blurb": "The passage is held open by curved struts set every few paces, and the struts "
                 "are not struts. They were in something once, and something took them out, and "
                 "somebody put them here to hold a roof up.",
    },
    {
        "key": "rot", "name": "The Rot", "at": 54.0, "danger": 0.60, "cold": -0.08,
        "gather": {"glowmoss": 5, "water": 4, "meat": 4, "resin": 3, "dust fungus": 4,
                   "antisepsis": 1, "salve": 1, "branch": 2, "charcoal": 2},
        "blurb": "Warm, wet, and alive in the way a wound is alive. Everything grows here and "
                 "nothing here is clean, and the air goes into the lungs like it has been "
                 "breathed already.",
    },
    {
        "key": "silt", "name": "The Silt", "at": 74.0, "danger": 0.52, "cold": 0.04,
        "gather": {"cloth": 3, "cord": 3, "scrap": 4, "water": 5, "shard": 2,
                   "map scrap": 1, "coagulant": 1, "ration": 2,
                   "salve": 1,
                   "antisepsis": 1},
        "blurb": "Standing water over a floor of fine grey silt, ankle deep for most of a day's "
                 "walk. Things are in the silt. Most of them are objects. Not all of them.",
    },
    {
        "key": "throat", "name": "The Throat", "at": 94.0, "danger": 0.66, "cold": -0.14,
        "gather": {"scrap": 3, "shard": 3, "stabiliser": 1, "water": 2, "nerveblock": 1,
                   "ration": 2,
                   "salve": 1,
                   "antisepsis": 1},
        "blurb": "The passage narrows to something a body fits through and no more, and there "
                 "is air coming up it that is warmer than anything behind you, and the cairns "
                 "are stacked three deep along both walls here like a crowd.",
    },
]

WARREN_GOAL = 110.0


# ------------------------------------------------------------------ act three: the deep
DEEP_ZONES = [
    {
        "key": "deep", "name": "The Long Deep", "at": 0.0, "danger": 0.38, "cold": -0.16,
        "gather": {"scrap": 3, "water": 3, "shard": 3, "cord": 2, "ration": 2,
                   "coagulant": 1, "glowmoss": 3,
                   "salve": 1},
        "blurb": "Below the throat the dug part stops and the rock takes over, and the rock is "
                 "not interested. It goes down for a day and a half without changing once.",
    },
    {
        "key": "weave", "name": "The Weave", "at": 20.0, "danger": 0.62, "cold": -0.12,
        "gather": {"cord": 5, "resin": 4, "hide": 3, "shard": 3, "meat": 3,
                   "glowmoss": 3, "water": 3, "stabiliser": 1,
                   "antisepsis": 1,
                   "salve": 1},
        "blurb": "Passages crossing passages crossing passages, all of them dug, none of them "
                 "going anywhere. Whatever made this was not travelling. It was looking for "
                 "something and it did not know where.",
    },
    {
        "key": "kiln", "name": "The Kiln", "at": 42.0, "danger": 0.72, "cold": -0.34,
        "gather": {"charcoal": 5, "scrap": 4, "shard": 3, "stabiliser": 2, "water": 1,
                   "salve": 1},
        "blurb": "Fired. The walls have gone to a glaze and the glaze has run and set and run "
                 "again, which takes more heat than a planet gives away for free.",
    },
    {
        "key": "well", "name": "The Well", "at": 64.0, "danger": 0.68, "cold": 0.10,
        "gather": {"water": 6, "glowmoss": 4, "cloth": 3, "marrow": 1, "meat": 2,
                   "antisepsis": 1, "scrap": 2, "ration": 2,
                   "salve": 1},
        "blurb": "A shaft going down with water coming up it, cold, clean, and moving - which "
                 "means it is going somewhere, and everything else down here has stopped.",
    },
    {
        "key": "lung", "name": "The Lung", "at": 86.0, "danger": 0.74, "cold": -0.22,
        "gather": {"glowmoss": 4, "resin": 3, "water": 3, "nerveblock": 1, "marrow": 1,
                   "stabiliser": 1, "meat": 3,
                   "antisepsis": 1},
        "blurb": "A space that fills and empties. Not wind - the pressure comes up through the "
                 "floor on a count you can set your steps to, and it has been keeping that "
                 "count since long before anything walked in here to notice it.",
    },
    {
        "key": "chamber", "name": "The Chamber", "at": 108.0, "danger": 0.58, "cold": -0.10,
        "gather": {"scrap": 3, "shard": 2, "stabiliser": 1, "water": 3, "ration": 2,
                   "cloth": 2,
                   "salve": 1,
                   "antisepsis": 1},
        "blurb": "It opens out. Cut, not worn - walls squared off by something working to a "
                 "plan, and the floor swept, and cairns at the edge of the light in a ring "
                 "going all the way round.",
    },
]

DEEP_GOAL = 130.0


# ------------------------------------------------------------------ the two terminal scenes
def the_throat(s):
    """End of the warrens. The way down, and whether to take it."""
    text = (
        "The passage stops being a passage. There is a hole in the floor of it going straight "
        "down, worked smooth, wide enough for a body and not wide enough to change its mind "
        "partway.\n"
        "The cairns are stacked along both walls to the lip of it and then they stop. They do "
        "not go down. Whoever counted the whole way here counted up to this and put the last "
        "stone on the edge and did not carry the count over.\n"
        "Warm air comes up out of it steadily, and it smells of nothing at all, which after "
        "six days of this smelling of everything is the part that is difficult."
    )
    opts = ["Have it go down"]
    if s.has_flag("cairn_read") or len(s.truths) >= 3:
        text += ("\nYou have been reading the marks the whole way. The count on the last stone "
                 "is not a distance. It is a number of times.")
        opts.append("Have it add a stone to the last cairn before it goes")
    opts.append("Have it close the hole and stay up here")
    opts.append("Have it climb back out the way it came")
    return {"sid": "the_throat", "text": text, "opts": opts,
            "map": list(range(len(opts))), "age": 0, "danger": 0.0}


def the_chamber(s):
    """The bottom of the deep. What all of the digging was toward."""
    text = (
        "The ring of cairns closes around a low place in the middle of the floor, and in the "
        "low place there is something lying on its side with its back to you.\n"
        "It is enormous and it has been here a long time and it is not a machine. The hands on "
        "the ends of its arms are the shape that digs, worn down past the point of being any "
        "use, and there are more of them than a thing should have. It is curled around a gap "
        "in the floor about the size of a held breath, and the gap is empty, and the edges of "
        "the gap have been worked smooth by something going over them again and again.\n"
        "It dug all of it. The burrow, the weave, the whole system, looking for this, and it "
        "found it, and what it found was a space with nothing in it.\n"
        "Then it went back up and stacked every stone on the route so the next one would not "
        "have to look as long. That is what the count is. It is not a distance. It is how many "
        "times it has done this."
    )
    opts = ["Have it go to the thing and look at what is in the gap"]
    if s.has_flag("cairn_read") or len(s.truths) >= 3:
        opts.append("Have it stack the last stone and carry the count on")
    opts.append("Have it lie down in the ring and stop")
    opts.append("Have it turn round and start back up")
    return {"sid": "the_chamber", "text": text, "opts": opts,
            "map": list(range(len(opts))), "age": 0, "danger": 0.0}
