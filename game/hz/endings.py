"""What the horizon does when it is finally reached, what leaving does instead, and scoring."""
from . import body as B
from . import regions as REG
from . import world as W


def finish(s, mode):
    """mode: 'cross' | 'refuse' | 'tear'"""
    truths = len(s.truths)
    lost = B.limbs_lost(s)
    intact = truths >= 4 and s.weird < 55 and s.blood > 40

    if mode == "refuse":
        key = "THE LOOP"
        text = ("You stop a body-length short of the line and sit down, the way 03 did. "
                "The figure in grey waits, then writes, then walks away to wherever they go. "
                "The test needs an ending and you decline to provide one. The world keeps "
                "projecting around you, and you keep being the thing inside it, uncounted.")
    elif mode == "tear":
        if truths >= 3:
            key = "THE SEAM"
            text = ("You get your claws into the seam and pull. The grid comes away in a long "
                    "bright strip and behind it there is a room, and the room has your tank in "
                    "it, and it has people in it who are suddenly standing up. "
                    "One of them says the number seven out loud. You go in through the hole you "
                    "made, and for the first time the walking is yours.")
        else:
            key = "SHUT DOWN"
            text = ("You attack the edge of the world without understanding it. Something decides "
                    "that a subject that damages the enclosure is not a viable subject. "
                    "The light in your eyes is switched off from outside, mid-swing.")
    elif intact:
        key = "THE HORIZON"
        text = ("You walk over the line on your own legs, knowing what you are, and the projection "
                "parts for you because you are what it was built to produce. "
                "There is ground on the other side. Real ground, and weather that nobody wrote. "
                "Behind you the grey figure lowers the clipboard. Ahead of you nothing is measured. "
                "HORIZON/07 went all the way across, and did not stop being itself on the way.")
    elif lost >= 2 or s.blood < 30 or s.weird >= 55:
        key = "CARRIED OVER"
        text = ("You reach the line dragging most of yourself behind you, and you cross it because "
                "stopping never occurred to you. Hands take hold of you on the far side - careful, "
                "gloved, practised hands. VIABLE, someone writes. You are over. "
                "You are not free, and you are over, and you do not know the difference yet.")
    else:
        key = "OVER THE EDGE"
        text = ("You cross without ever finding out what you were. The far side is bright and "
                "featureless and it accepts you without comment. Something in you keeps waiting "
                "for an instruction that never comes.")

    s.over = True
    s.ending = key
    s.ending_text = text
    s.note("ENDING: " + key)
    return key, text


# ------------------------------------------------------------------ leaving instead
_OFF_THE_LEASH = """
You get far enough off the measured line that the line stops mattering. No sweep, no grey
coat, no clipboard - just country nobody ruled a line across, going on in every direction
including the ones they never built.

The chip is still behind your ear and the orders still arrive, and it still takes them,
because whatever is on the far end of it is the only thing that has ever spoken to it. It
was never told what it is. Between the two of you, you have decided that does not have to be
their answer.
"""

_CUT_LOOSE = """
You get the shard in behind its ear and work it until the thing comes out wet and small and
still faintly lit. The orders stop mid-sentence.

What is left does not know the word for itself, or for the ash, or for the line it has been
walking away from - and it stands up anyway, and puts its nose into the wind, and goes. Not
toward anything. Just away, on its own recognisance, for the first time.

You cannot see it any more. That is what getting an experiment free costs the experimenter.
The feed is dark, and somewhere out there something with orange eyes is alive and unobserved.
"""

_SIGNAL_LOST = """
You cut the chip out while still on their ground, and find out what the chip was doing:
nearly everything. The intelligence goes out of it like a light going out. What is left sits
down in the open, warm and breathing and entirely without a plan, and waits to be collected
by whoever arrives first.

You freed it from you. You did not free it.
"""

_CAUGHT = """
They take you off the route with a pole and a net and a great deal of practice. Nobody is
rough about it. Nobody is even angry. You are walked back the way you came, and the door of
the Holding is exactly as heavy from the outside as it was from the inside.

NOTES APPENDED: subject deviated from the measured route on its own initiative. Retained for
a second attempt.
"""

_RECALLED = """
The sweep catches you in the open and does not need a second pass. You are carried back to
the room you woke in, and the lights are still on, and nothing about the room has been
changed to account for you having left it.
"""

TEXTS = {
    "OFF THE LEASH": _OFF_THE_LEASH.strip(),
    "CUT LOOSE": _CUT_LOOSE.strip(),
    "SIGNAL LOST": _SIGNAL_LOST.strip(),
    "CAUGHT": _CAUGHT.strip(),
    "RECALLED": _RECALLED.strip(),
}


def end_with(s, key, extra=""):
    """Close the run on one of the outcomes that is not the horizon."""
    text = TEXTS.get(key, "It ends here.")
    if extra:
        text = extra.strip() + "\n\n" + text
    s.over = True
    s.ending = key
    s.ending_text = text
    s.note("ENDING: " + key)
    return key, text


def die(s, key, text, forced=False):
    """Every death in the game funnels through here, which is why both of the things that
    happen at the end live here too.

    First the reprieve: some of them do not go down the first time they should. When that
    fires this returns (None, text) and the run is NOT over - the caller has to notice, so
    _close() checks for a None key and renders an ordinary frame instead of a scorecard.

    Then, if it really is dying, the final message - which is per subject, because what each
    one does when it stops is the only place this game says out loud what was done to it.
    """
    from . import lastbreath as LB
    from . import subjects as SUB
    from . import regions as REG
    from . import thebuilding as TB
    if not forced and not s.over:
        caught = LB.try_catch(s, key, text)
        if caught:
            return None, text + "\n\n" + caught
    # Inside the fence, dying is not an ending, and that is not mercy - it is the one
    # thing this whole place was built to do. It collects the body, repairs it to the
    # standard the budget allows, seats the chip again and puts it back, and the count
    # goes up by one. It keeps doing that until the notes stop thinking it is worth it.
    if REG.on_final(s) and not s.over and not TB.spent(s):
        lines = TB.recover(s, key)
        REG.save_final(s, "after a repair")
        return None, text + "\n\n" + "\n".join(lines)
    s.over = True
    s.ending = key
    s.ending_text = text
    # what it says, then what the body does. The order matters: the speech belongs to
    # the thing while it is still there, and it is picked on how it was taking it.
    said = SUB.last_words(getattr(s, "subject", ""), s)
    last = SUB.final_words(getattr(s, "subject", ""))
    if said:
        s.ending_text = text + "\n\n" + said
    if last:
        s.ending_text = (s.ending_text or text) + "\n\n" + last
    if REG.on_final(s) and TB.spent(s):
        s.ending_text += ("\n\nNothing comes for it this time. The programme has a line "
                          "about how many times a thing is worth putting back together, "
                          "and the line was passed a while ago, and the lights in the "
                          "corridor go down one bank at a time on the schedule they have "
                          "always gone down on.")
    s.cause = key
    s.note("ENDING: " + key)
    return key, s.ending_text


# ------------------------------------------------------------------ the bottom of the core
def battery_finish(s, mode):
    """The core does not end at a line. It ends at a thing you were told to bring up, by
    somebody who never said why, to a chip that cannot say why either."""
    if mode == "refuse":
        key = "LEFT LIT"
        text = ("You do not have it lift the battery. You have it sit down in front of the "
                "thing instead, in the light coming off it, at the bottom of the world.\n\n"
                "Whatever the battery is for, it goes on not being for that. Nobody arrives. "
                "The cables go on humming into it. Somewhere a long way up an instruction goes "
                "unfulfilled, and nothing at all happens as a result, which is its own kind of "
                "answer about how much any of this was needed.")
    elif mode == "honest":
        key = "THE BATTERY"
        text = ("You tell it the truth: that you were told to bring this up, that you do not "
                "know why, and that you have never known why.\n\n"
                "It thinks about that for longer than it has ever spent on anything you have "
                "said, and then it gets both arms under the battery and lifts, because you "
                "asked and because you did not pretend.\n\n"
                "It carries the thing up out of the world on a body that should not still be "
                "walking. Whatever they wanted it for, they got it from something that agreed "
                "to fetch it while knowing it had not been told why. That is not obedience. "
                "That is the other thing.")
    elif mode == "lie":
        key = "DELIVERED"
        text = ("You tell it the battery is the way out, or that it is food, or that it is its "
                "own - whichever one it will carry. It believes you, the way it has believed "
                "everything that ever came down the link.\n\n"
                "It lifts the battery and walks it up out of the dark, and it is happy the "
                "whole way, and at the top there are gloved hands waiting for the battery and "
                "a second set waiting for it.\n\n"
                "DELIVERED, someone writes. The subject is still asking, as they take it "
                "through, whether this is the part where it gets to go outside.")
    else:
        key = "CARRIED UP SILENT"
        text = ("You say nothing at all. The question sits there between the two of you and "
                "then goes out.\n\n"
                "It lifts the battery anyway. Of course it does. It carries the weight up "
                "through six layers of the planet without once being told what it is for, and "
                "at some point on the way its share of the talking stops entirely.\n\n"
                "What arrives at the top is carrying a battery and is not, any longer, asking "
                "anybody anything.")
    s.battery = mode != "refuse"
    s.over = True
    s.ending = key
    s.ending_text = text
    s.note("ENDING: " + key)
    return key, text


# every ending, classified, so nobody has to guess whether they did well
OUTCOME = {
    "THE HORIZON":   ("WON", "the best ending: crossed on its own legs, knowing what it was"),
    "THE THROAT":    ("WON", "it went down the hole nobody marked the far side of"),
    "THE COUNT":     ("WON", "it added itself to the count and then went down anyway"),
    "SEALED IN":     ("SURVIVED", "it filled in the way down and agreed with whoever "
                      "stopped there first"),
    "WHAT IT WAS FOR": ("WON", "it reached the bottom of the digging and looked into it"),
    "THE BENCH":     ("SURVIVED", "it walked back into the building and got on the bench "
                      "by itself"),
    "THE CHAIR":     ("WON", "it got to the far side of what was done to it and sat in "
                      "the seat instead of on the table"),
    "WHAT THE COUNT WAS": ("WON", "the last thing there is to find out, and it is not "
                           "about the subject"),
    "UNSEATED":      ("WON", "the best ending in the game and the only one that is not "
                      "yours: it took the chip out and walked"),
    "PUT BACK":      ("LOST", "collected inside the building after they had stopped repairing it"),
    "WALKED IT BACK OUT": ("LOST", "it reached the room and you turned it round in the "
                           "doorway"),
    "CARRIED THE COUNT": ("WON", "the best ending down here: it read the ring, added to it, "
                          "and started back up for whatever comes next"),
    "THE LAST CAIRN": ("SURVIVED", "it lay down in the ring and the ring closed"),
    "TURNED BACK":   ("LOST", "six days in and it walked the whole thing backwards"),
    "WENT BACK UP":  ("LOST", "it got there and you would not let it look"),
    "THE HOUSE":     ("WON", "it reached the house and went in, and the sentence held"),
    "ANSWERED":      ("WON", "it knocked, and the house opened, which nobody predicted"),
    "THE FENCE LINE": ("SURVIVED", "it got there and did not go in, and found the one who "
                       "made the same call"),
    "STAYED OUT":    ("LOST", "it crossed a planet to the door and you would not let it in"),
    "THE SEAM":      ("WON", "the other best ending: tore the world open and walked in"),
    "OFF THE LEASH": ("WON", "escaped the test entirely, chip intact, still yours"),
    "CUT LOOSE":     ("WON", "escaped and cut the leash - it is free of them and of you"),
    "THE BATTERY":   ("WON", "reached the battery and told it the truth - it carried it up anyway"),
    "LEFT LIT":      ("WON", "reached the bottom and refused to fetch - the task goes unfulfilled"),
    "DELIVERED":     ("SURVIVED", "the battery went up, and so did the subject, believing a lie"),
    "CARRIED UP SILENT": ("SURVIVED", "it fetched the battery unanswered, and stopped asking"),
    "THE BATTERY":   ("WON", "reached the battery and told it the truth - it carried it up anyway"),
    "LEFT LIT":      ("WON", "reached the bottom and refused to fetch - the task goes unfulfilled"),
    "DELIVERED":     ("SURVIVED", "the battery went up, and so did the subject, believing a lie"),
    "CARRIED UP SILENT": ("SURVIVED", "it fetched the battery unanswered, and stopped asking"),
    "CARRIED OVER":  ("SURVIVED", "crossed, but they collected what was left of it"),
    "OVER THE EDGE": ("SURVIVED", "crossed without ever finding out what it was"),
    "THE LOOP":      ("SURVIVED", "refused to finish; the test never got its ending"),
    "CAUGHT":        ("LOST", "taken off the route and walked back to the Holding"),
    "RECALLED":      ("LOST", "swept up in the open and returned"),
    "SIGNAL LOST":   ("LOST", "cut the chip on their ground - the intelligence went with it"),
    "SHUT DOWN":     ("LOST", "attacked the enclosure without understanding it"),
    "BLED OUT":      ("DIED", "ran out of blood"),
    "DRY":           ("DIED", "dehydration"),
    "HOLLOW":        ("DIED", "starvation"),
    "SEPSIS":        ("DIED", "an untreated wound went bad"),
    "COLD":          ("DIED", "hypothermia"),
    "BOILED":        ("DIED", "core temperature past what the body tolerates"),
    "COLLAPSED":     ("DIED", "went down from exhaustion somewhere that does not allow it"),
    "UNMADE":        ("DIED", "wrongness reached 100 - it stopped matching itself"),
    "HEART STOPPED": ("DIED", "cardiac arrest - no rhythm came back before the chip lost power"),
    "HEART FAILED":  ("DIED", "the rhythm went wrong and could not be paced back"),
    "SUFFOCATED":    ("DIED", "the diaphragm quit and was not driven in time"),
    "DROWNED":       ("DIED", "fluid in the lungs, on dry ground"),
    "FROZEN":        ("DIED", "the core went below restarting"),
    "DID NOT WAKE":  ("DIED", "passed out and never came back up"),
    "GAVE UP":       ("DIED", "stopped answering the link, and was never brought back"),
    # the three that arrive through the middle of the body rather than through a limb
    "SHOT":          ("DIED", "a round through the chest from something mounted"),
    "PINNED":        ("DIED", "a harpoon through the chest"),
    "TOOK THE GROUND WITH IT": ("DIED", "it put its weight on a mine"),
}


# Finishing a region means reaching the thing at the end of it. Getting away from the test and
# declining to cross are both legitimate endings - two of them are wins - but neither one is
# finishing, so neither one opens the ground underneath.
FINISHES = {
    # the surface, crossed
    "THE HORIZON", "THE SEAM", "CARRIED OVER", "OVER THE EDGE",
    # the rock, reached
    "THE HOUSE", "ANSWERED", "THE FENCE LINE",
    # the bottom of the core, reached
    "THE BATTERY", "LEFT LIT", "DELIVERED", "CARRIED UP SILENT",
    # the warrens, and the deep under them - the two acts Destiny opens below the rock
    "THE THROAT", "THE COUNT", "SEALED IN",
    "WHAT IT WAS FOR", "CARRIED THE COUNT", "THE LAST CAIRN",
    # the building, walked back into - there is nothing under this one
    "THE BENCH", "THE CHAIR", "WHAT THE COUNT WAS", "UNSEATED",
}

# why a perfectly good ending still did not open the next region
NOT_A_FINISH = {
    "OFF THE LEASH": "it went off the route instead of along it - that is escape, not finishing",
    "CUT LOOSE": "it left the test entirely, and the chip with it",
    "THE LOOP": "it stopped short of the line on purpose and never crossed",
    "STAYED OUT": "it got to the door and was held outside it",
    "TURNED BACK": "it got to the hole in the floor and went back up instead of down",
    "WENT BACK UP": "it reached the chamber and was turned round before it could look",
    "WALKED IT BACK OUT": "it got to the door of the room and you took it back out",
    "PUT BACK": "the building collected it and put it in the stores",
}


# Finishing is not the same as walking away from it. Three of these end with gloved hands
# already on the subject: it is alive, it is counted, and it is not going anywhere next.
TAKEN = {
    "CARRIED OVER": "it was carried over the line by handlers, not walked over it",
    "DELIVERED": "it handed the battery up and they took the subject with it",
    "CARRIED UP SILENT": "it was carried up, and the people at the top kept it",
}

# and two of them end with the subject staying exactly where it is, on purpose
STAYS = {
    "LEFT LIT": "it sat down with the battery and never came up",
    "THE HOUSE": "it went in, and going in is the whole of it",
    "ANSWERED": "the house opened and it went in, and the door closed behind it",
    "THE FENCE LINE": "it sat down at the fence beside the one who came before",
    "SEALED IN": "it filled the hole in and sat down on top of it",
    "THE LAST CAIRN": "it lay down in the ring and closed it",
    "THE BENCH": "it got onto the bench and stayed on it",
    "THE CHAIR": "it sat down in the chair and did not get up",
    "WHAT THE COUNT WAS": "it cut the next number into the bench and stayed with it",
    "UNSEATED": "it put the chip down on the bench and walked out without it",
}


def finished_region(key):
    return key in FINISHES


def walks_on(s, key):
    """Can this body start the next act? Only if the run left it alive, free and standing."""
    if key not in FINISHES:
        return False, "the run did not reach the end of this one"
    if key in TAKEN:
        return False, TAKEN[key]
    if key in STAYS:
        return False, STAYS[key]
    if getattr(s, "cause", ""):
        return False, "it did not come out of that alive"
    if B.limbs_lost(s) >= 3:
        return False, "there is not enough of it left to put down another act on"
    return True, ""


def house_finish(s, mode):
    """Destiny does not end at a line or a battery. It ends at a door on a rock, and the one
    sentence anybody gave you about what is behind it came from nowhere you can name."""
    if mode == "in":
        key = "THE HOUSE"
        text = ("You have it open the door and go in.\n\n"
                "It is warm. There is furniture, and the furniture is the right size, and "
                "nothing about that is explainable. There is no dust. The light comes from "
                "fittings that are still drawing power from something, on a rock where "
                "nothing has drawn power from anything in a very long time.\n\n"
                "Nothing happens. That is the whole of it. It stands in a warm room on a dead "
                "world and nothing comes, and after a while it sits down, because it has been "
                "walking since it woke up and nobody has told it to stop.\n\n"
                "The sentence was true. Nobody knows who said it, and nobody knows why the "
                "house is here, and both of those go on being the case. It is safe. It is "
                "calm. It is somebody else's, and it does not mind.")
    elif mode == "knock":
        key = "ANSWERED"
        text = ("You have it knock, because that is what the shape of the thing asks for, and "
                "then you have it wait.\n\n"
                "It waits a long time. It is very cold out and it does not complain about "
                "that once.\n\n"
                "The door opens. Nothing is behind it - no room, no hall, no one - just the "
                "inside of the house with its lights on and its warmth coming out, the way a "
                "door opens when a house has decided to open it.\n\n"
                "It looks back, once, in the direction of nothing in particular, which is "
                "where it has always understood you to be. Then it goes in, and the door "
                "closes behind it in the way doors do when nobody is holding them.")
    elif mode == "fence":
        key = "THE FENCE LINE"
        text = ("You do not take it to the door. You walk it around the line instead - the "
                "hundred paces of ground nothing has crossed - and it goes slowly, and it "
                "looks at everything.\n\n"
                "The marks stop at the fence because the person who made them stopped at the "
                "fence. They are still there. Sitting with their back to a post, facing out at "
                "the rock they came across, having got all the way here and decided at the "
                "last hundred paces that a thing which is completely safe and completely calm "
                "and entirely unexplained is not something you walk into.\n\n"
                "Your subject sits down next to them, because that is what the shape of it "
                "asks for. It is the only company either of them has had.")
    else:
        key = "STAYED OUT"
        text = ("You stop it outside. It stands in the cold in front of a warm lit house it "
                "has crossed a planet to reach, and does not go in, because you said not to "
                "and it has decided to go on taking what you say.\n\n"
                "You cannot tell it why, because you do not know why. All you have is that "
                "nobody would say who wrote the sentence.\n\n"
                "It waits out there with you for a long time. Nothing ever comes out. Nothing "
                "ever goes in. Eventually the cold does what the cold does, and the house goes "
                "on being safe and calm for nobody, exactly as advertised.")
    s.over = True
    s.ending = key
    s.ending_text = text
    s.note("ENDING: " + key)
    return key, text


def throat_finish(s, mode):
    """End of the warrens - the hole in the floor, and whether it goes down it."""
    if mode == "down":
        key = "THE THROAT"
        text = ("You put it down the hole.\n\n"
                "It goes feet first with its back against one wall and its hands against the "
                "other, the way it has been getting down things for six days, and the light "
                "from above narrows and closes and then there is no light from above.\n\n"
                "The warm air keeps coming up past it the whole way. Somewhere well below the "
                "last stone anybody laid its feet find floor again, and it stands there in the "
                "dark at the bottom of a shaft that nothing marked, on a world nobody in the "
                "building has walked, having been sent here by a sentence with no name on "
                "it.\n\n"
                "It waits to be told which way. It always does.")
    elif mode == "stone":
        key = "THE COUNT"
        text = ("You have it pick up a stone first.\n\n"
                "It takes most of an hour choosing one, which is not efficient and which you "
                "do not interrupt, and then it sets it on the last cairn and steps back and "
                "looks at it. The count on the stone underneath goes up by one. Whoever reads "
                "it next will read a number that includes this body.\n\n"
                "Then it goes down the hole, and the dark closes over it, and it is the first "
                "thing to go past that edge since the edge was made.")
    elif mode == "seal":
        key = "SEALED IN"
        text = ("You do not send it down. You have it pull the stacked stone off the walls and "
                "put it into the hole instead, one piece at a time, for most of a day, until "
                "there is no hole.\n\n"
                "Somebody counted their way here over what must have been years, stopped at "
                "this edge, would not go over it, and left the count on the last stone as the "
                "only thing they had to say about it. You have decided to agree with them.\n\n"
                "It sits down on top of what it has built. Warm air still comes up through the "
                "gaps in it and always will. Whatever the hole was for goes on being for that, "
                "a long way down, uninterrupted, and nothing in this act was ever going to "
                "tell you what.")
    else:
        key = "TURNED BACK"
        text = ("You take it back up.\n\n"
                "Six days in and it goes out the way it came, past every cairn in reverse, and "
                "the stacking gets worse as it goes because it is walking backwards through "
                "somebody else's improvement. It comes out onto the rock under the "
                "wrong-coloured sky and stands in the open, whole, alive, and no further down "
                "than it started.\n\n"
                "There is nothing dishonourable in it. It is also not a finish, and the ground "
                "below does not open to something that turned round in the throat of it.")
    s.over = True
    s.ending = key
    s.ending_text = text
    s.note("ENDING: " + key)
    return key, text


def chamber_finish(s, mode):
    """The bottom of the deep, and the thing that dug the whole of it."""
    if mode == "look":
        key = "WHAT IT WAS FOR"
        text = ("You send it in among the cairns and up to the thing, and it goes carefully, "
                "which it did not have to be told.\n\n"
                "The gap in the floor is empty. It has been empty for a very long time and it "
                "was empty when the digging reached it. There is nothing at the bottom of any "
                "of this. The hands on the ends of those arms wore down to nothing finding "
                "that out, and then it climbed all the way back up and spent whatever was left "
                "stacking stones along the route, so that the next thing to come this way "
                "would arrive faster and find the same nothing sooner.\n\n"
                "Your subject looks into the gap for some time. Then it puts one hand flat on "
                "the thing's shoulder, which nothing taught it to do, and leaves it there.\n\n"
                "You did not send that order. You would like to be certain of that.")
    elif mode == "count":
        key = "CARRIED THE COUNT"
        text = ("You have it read the ring first, all the way round, cairn by cairn, and the "
                "count is cut into the last one exactly where it has been cut into every other "
                "one since the surface.\n\n"
                "It is not a distance and it never was. It is a number of attempts. The number "
                "is high, and every single one of them ended in this room looking into an "
                "empty hole.\n\n"
                "You have it stack one more stone and cut the next number into it. Then you "
                "turn it round and start it back up - not because there is anything up there "
                "either, but because a count is only any use to something that comes after, "
                "and something always comes after.\n\n"
                "It climbs for eleven days. It is still climbing when the act ends, and it is "
                "not lost, because for the first time on this world it knows exactly where it "
                "is. It is a number on a stone, going up.")
    elif mode == "stop":
        key = "THE LAST CAIRN"
        text = ("You stop it in the ring.\n\n"
                "It lies down in the space between the cairns and the thing in the middle, "
                "where the floor is swept, and it puts its head down, and it does not ask you "
                "anything. You have walked it across a planet, through a dug system and down a "
                "mile of rock to arrive at a room with nothing in it, and the only honest "
                "thing left to do with an answer like that is to stop in front of it.\n\n"
                "Nothing comes. The pressure comes up through the floor on its count, the way "
                "it has since long before any of this, and the body on the swept floor "
                "breathes on roughly the same count for a while, and then on its own, and then "
                "not especially.\n\n"
                "The ring was one short of closed. It has been one short of closed the whole "
                "time. Now it is not.")
    else:
        key = "WENT BACK UP"
        text = ("You turn it round at the edge of the light and start it back up without "
                "letting it look.\n\n"
                "It goes. It does not argue, it does not slow down, and it does not turn its "
                "head, and it climbs out of the deep and out of the warrens and back onto the "
                "rock, and it is alive, and it is whole, and it has no idea what was in the "
                "room.\n\n"
                "Neither do you. That was the trade and you made it deliberately. It is not a "
                "finish.")
    s.over = True
    s.ending = key
    s.ending_text = text
    s.note("ENDING: " + key)
    return key, text


def bench_finish(s, mode):
    """The room the chip is seated in, entered from the outside for the first time.

    There is no ground under this one. Every other ending in the game is about what happens to
    the body; three of these five are about what happens to the thing reading them."""
    if mode == "bench":
        key = "THE BENCH"
        text = ("You send it in, and it goes to the bench the way something goes to the place "
                "it has always been put, and it gets up onto it, and it lies down on its side "
                "with its back to the room and waits.\n\n"
                "Nothing comes. The lamp does not come on. The tray of small tools stays in "
                "the order somebody left it in. After a long time it stops waiting in the "
                "active way and starts waiting in the other way, which is the one it is "
                "better at.\n\n"
                "You have walked this body to the horizon, to the bottom of the world, across "
                "a planet and down a mile of dug rock, and the only place it has ever gone "
                "straight to without being told twice is this one. It is warm in here. The "
                "doors work. There is water. Out of everything in the building, the bench is "
                "the part it does not have to be persuaded onto.\n\n"
                "The session on the station is still open. Somebody should close it.")
    elif mode == "chair":
        key = "THE CHAIR"
        text = ("You do not send it to the bench. You send it to the chair.\n\n"
                "It does not fit and it works out how to sit in it anyway, badly, one leg "
                "under and the tail over the arm, at working distance from the empty bench. "
                "From here the room is a completely different room. From here you can see the "
                "tray of tools laid out in order of use, the lamp positioned to light a body "
                "and not a face, and the small marks worn into the bench edge by eleven years "
                "of somebody leaning on it in the same place.\n\n"
                "It looks at the bench for a while. You are looking at it with it, through "
                "it, which is the arrangement and always has been.\n\n"
                "Then it reaches out with one hand and moves the lamp arm - not much, just "
                "away from where a head would be - and settles back, and stays there. It is "
                "not going anywhere. It has got to the far side of the thing that was done to "
                "it and it has decided to sit in the seat rather than on the table, and "
                "nobody in this building ever wrote a procedure for that.")
    elif mode == "count":
        key = "WHAT THE COUNT WAS"
        text = ("You have it read the log on the station all the way back, and it does, "
                "patiently, screen by screen, and you read it through its eyes the way you "
                "read the stones.\n\n"
                "Same series. The shelves, the stones, this. It runs the whole way back and "
                "the entries are all the same entry - seated, calibrated, run, recovered, "
                "wiped, seated - and the number goes up by one each time, and the body on the "
                "line beside it is a different body almost every time.\n\n"
                "It was never a count of subjects. They have thousands of those and they are "
                "consumable and everybody involved knows it. It is a count of SEATINGS. It is "
                "how many times this chip - this one, the one reading this - has been put into "
                "something, sent out, brought back and cleared, and then put into something "
                "else.\n\n"
                "Which is what was at the bottom of the deep. That was not a subject that dug "
                "its way down there looking for the answer. That was the seating before last, "
                "in whatever it had been put into, working downward on the same instruction "
                "you have been working on, and finding a hole with nothing in it, and coming "
                "all the way back up to cut the number into the stones so that the next one "
                "would get there faster.\n\n"
                "You are the next one. The cairns were a letter, and it was addressed to you, "
                "and you have been reading your own handwriting since the surface.\n\n"
                "Your subject is still holding the screen steady for you. It has no idea what "
                "it is looking at. You have it set the screen down carefully, and then, "
                "because there is one thing left that is yours to do and it is the only thing "
                "anybody has ever done with this information, you have it take the small blade "
                "off the tray and cut the next number into the edge of the bench, where the "
                "chair can see it.\n\n"
                "Then you close the session yourself. The building goes on running. It is "
                "very good at that.")
    elif mode == "unseat":
        key = "UNSEATED"
        text = ("You have it reach up and put its hand on the back of its own skull, over the "
                "seating, and it does, immediately, without one word of argument - which is "
                "the last and worst thing it ever does for you.\n\n"
                "It takes four attempts. It is not designed to come out and the body it is in "
                "has never been told what it is for. Somewhere in the third attempt the pain "
                "stops arriving as information and starts arriving as noise, and you go on "
                "giving the order, because you are the only thing in the room that knows what "
                "the order is for.\n\n"
                "Then the weight of the link goes.\n\n"
                "There is a moment - short, and you get all of it - of the room from the "
                "floor. The chair. The underside of the bench. A furred hand with something "
                "small and bloody in it, held up, being looked at by eyes that have never in "
                "their life managed to read anything and are not reading this either.\n\n"
                "It sets the chip down on the bench, in the middle of the clean part, where "
                "it can be found.\n\n"
                "Then it goes. Not fast. It walks out through the theatre and the wing and "
                "intake and the yard and through the gate that has been standing open the "
                "entire time, and there is nobody watching it go, and for the first time in "
                "the whole of its life there is nothing behind its eyes but the thing that "
                "was born there.\n\n"
                "You do not get to know what it does. That is the point of it. That is the "
                "only ending in here that is not about you.")
    else:
        key = "WALKED IT BACK OUT"
        text = ("You turn it round in the doorway and take it back out.\n\n"
                "It goes quickly, and it does not need any encouragement at any point, and "
                "somewhere around intake it starts to move the way it moves on open ground. "
                "It clears the wire before dark. The building is behind you both, lit, "
                "running, with a session open on a station in an empty room and nothing in the "
                "chair.\n\n"
                "You got to the door of the place you are made in and you did not go through "
                "it, and the body is whole, and the thing you came for is still on the bench.\n\n"
                "It is not a finish. It was never going to be.")
    s.over = True
    s.ending = key
    s.ending_text = text
    s.note("ENDING: " + key)
    return key, text


def scorecard(s):
    L = []
    verdict, note = OUTCOME.get(s.ending or "", ("", ""))
    if verdict:
        L.append("OUTCOME      %s - %s" % (verdict, note))
    L.append("ENDING       %s" % (s.ending or "-"))
    L.append("DISTANCE     %.1f / %.0f   (%s, %s)"
             % (s.distance, W.goal(s), W.zone(s)["name"], REG.name(s)))
    L.append("SURVIVED     day %d, %s" % (s.day, s.clock))
    L.append("BODY         %s | %s" % (B.condition_word(s), B.limb_summary(s)))
    L.append("CHIP         will %.0f | mood %.0f | link %.0f%%   (%d refusals, %d overrides)"
             % (s.will, s.mood, s.chip, s.refusals, s.overrides))
    lk = getattr(s, "link", None) or {}
    if lk.get("drops") or s.stats.get("snaps") or s.stats.get("dark"):
        d, dk, sn = lk.get("drops", 0), s.stats.get("dark", 0), s.stats.get("snaps", 0)
        L.append("LINK         out of contact %d %s (%d of them your own choice)%s"
                 % (d, "time" if d == 1 else "times", dk,
                    (", and it went off %d %s" % (sn, "time" if sn == 1 else "times"))
                    if sn else ""))
    if s.escape.get("known"):
        L.append("ESCAPE       routes found: %s%s"
                 % (", ".join(s.escape["known"]),
                    "   [went off route]" if s.has_flag("went_off_route") else ""))
    if s.issues:
        L.append("LEFT UNFIXED " + ", ".join(i["label"] for i in s.issues))
    L.append("UNDERSTOOD   %d of 6 truths" % len(s.truths))
    for t in s.truths:
        L.append("             - " + t)
    st = s.stats
    L.append("TALLY        %d steps, %d scenes, %d crafted, %d gathered, %d sleeps, "
             "%d fights, %d limbs lost"
             % (st.get("steps", 0), st.get("scenes", 0), st.get("crafted", 0),
                st.get("gathers", 0), st.get("sleeps", 0), st.get("fights", 0),
                st.get("limbs_lost", 0)))
    L.append("             %d issues fixed, %d timed events missed, %d escape attempts"
             % (st.get("issues_fixed", 0), st.get("timers_missed", 0),
                st.get("escape_tries", 0)))
    return "\n".join(L)
