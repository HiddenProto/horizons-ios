"""The other planet, and the house on it.

Destiny does not start where normal starts. The chip comes up in a body lying on rock under a
sky the wrong colour, on a world nobody in the building has walked, and the thing it is sent
for is not a line and not a battery. It is a house.

What the chip is given about the house is one sentence, and the sentence is confident: inside
the zone it is completely safe and completely calm, and nothing reaches you there. Where that
sentence came from is not recorded. Nobody has been. It is a building on a rock that nobody
built for anybody, and it happens to be there, and the confidence is somebody else's.

None of this is explained to the player anywhere but in the game. The README does not mention
Destiny at all, on purpose - this act assumes you have already walked the normal one.
"""

# Eight of them, and the ground gets less like ground the further in it goes. Cold runs high:
# there is not enough air here to hold heat, and the dark side of a rock is the dark side of a
# rock. "at" values are the natural length; Destiny's stretch table scales them.
ROCK_ZONES = [
    {
        "key": "wake", "name": "The Waking Ground", "at": 0.0, "danger": 0.20, "cold": 0.10,
        "gather": {"scrap": 3, "shard": 3, "cloth": 2, "water": 2, "cord": 2,
                   "dust fungus": 2, "ration": 1},
        "blurb": "Bare rock, and a sky that is the wrong colour for a sky. Whatever put this "
                 "body down here did not leave anything with it, and did not stay.",
    },
    {
        "key": "grey", "name": "The Grey Flats", "at": 16.0, "danger": 0.30, "cold": 0.13,
        "gather": {"scrap": 4, "shard": 3, "dust fungus": 3, "water": 2, "cord": 2, "hide": 1,
                   "salve": 1},
        "blurb": "Flat to the edge of seeing, and the flatness is a lie - it is all loose plate "
                 "over holes, and it rings under the feet like something hollow.",
    },
    {
        "key": "teeth", "name": "The Stone Teeth", "at": 34.0, "danger": 0.52, "cold": 0.11,
        "gather": {"shard": 5, "scrap": 3, "resin": 2, "water": 2, "dust fungus": 2, "meat": 1,
                   "antisepsis": 1},
        "blurb": "Rock standing up in rows, worn to points by a wind that is not blowing now. "
                 "Things shelter between them and some of the things are still here.",
    },
    {
        "key": "dust", "name": "The Dust Sea", "at": 52.0, "danger": 0.46, "cold": 0.15,
        "gather": {"dust fungus": 5, "cloth": 2, "scrap": 2, "water": 2, "cord": 2,
                   "salve": 1},
        "blurb": "Grey to the knee and it moves when you move. There is no bottom to it that "
                 "anybody has found and nothing that lives in it wants finding.",
    },
    {
        "key": "cairns", "name": "The Cairns", "at": 70.0, "danger": 0.50, "cold": 0.12,
        "gather": {"scrap": 4, "cloth": 3, "cord": 3, "hide": 2, "ration": 2, "shard": 2,
                   "coagulant": 1, "map scrap": 1, "antisepsis": 1},
        "blurb": "Stacked stone, deliberate, hundreds of them, in rows going the way you are "
                 "going. Somebody walked this before and marked it, and did not come back "
                 "along it.",
    },
    {
        "key": "pan", "name": "The Glass Pan", "at": 88.0, "danger": 0.60, "cold": 0.17,
        "gather": {"shard": 6, "scrap": 3, "water": 3, "resin": 2, "antisepsis": 1,
                   "dust fungus": 2},
        "blurb": "Something got hot enough here to turn the rock to glass, over a stretch it "
                 "takes most of a day to cross, and then it cooled and nobody came to look.",
    },
    {
        "key": "slope", "name": "The Windward Slope", "at": 106.0, "danger": 0.58, "cold": 0.20,
        "gather": {"branch": 2, "cord": 3, "hide": 2, "water": 2, "dust fungus": 2, "meat": 2,
                   "salve": 1},
        "blurb": "Up, into weather. There is air moving here and it is the first thing on this "
                 "world that has behaved the way weather behaves.",
    },
    {
        "key": "approach", "name": "The Approach", "at": 124.0, "danger": 0.34, "cold": 0.08,
        "gather": {"ration": 3, "water": 3, "cloth": 2, "cord": 2, "hide": 2, "salve": 1},
        "blurb": "The ground levels and gets tended. Not planted - tended. And there is a "
                 "building at the end of it with its lights on, which is the first lit thing "
                 "on this entire rock.",
    },
]

ROCK_GOAL = 140.0


def the_house(s):
    """The terminal scene. It is a door, and nobody knows what is behind it."""
    text = (
        "The house is a house. That is the first wrong thing about it - it is the shape people "
        "build when there is nothing making them build it that shape, and there has never been "
        "anybody on this rock to have the habit.\n"
        "It is warm. The windows are lit from inside and the light does not flicker. Nothing "
        "out here is moving toward it and nothing out here is moving away from it either, and "
        "the ground for a hundred paces around is the only ground on this world that nothing "
        "has crossed.\n"
        "What you were given about it was one sentence: inside the zone it is completely safe "
        "and completely calm. You have carried that sentence the entire way. Standing here you "
        "notice, for the first time, that you were never told who said it."
    )
    opts = ["Have it go in", "Have it knock and wait"]
    if len(s.truths) >= 3 or s.has_flag("cairn_read"):
        text += ("\nThe cairns pointed here. Somebody walked this before, marked the whole "
                 "route, and the marks stop at the fence.")
        opts.append("Walk the fence line instead of the door")
    opts.append("Stop outside and refuse to go in")
    return {"sid": "the_house", "text": text, "opts": opts,
            "map": list(range(len(opts))), "age": 0, "danger": 0.0}
