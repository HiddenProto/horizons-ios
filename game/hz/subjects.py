"""The subjects the chip can be seated in.

Same test, same route, same chip. Very different things on the other end of it. The traits
here are read by the existing systems - willingness, mood drift, movement, crisis odds, voice -
rather than living in a layer of their own, so a subject is a set of pressures and not a skin.

A run changes them. 2008 can end up as bitter as 101; 101 can be talked round. The starting
numbers are only where each one begins.
"""

# trait defaults - every subject overrides what it cares about
BASE = {
    "refusal_mult": 1.00,    # multiplier on the chance it declines an order
    "volatility": 1.00,      # how hard mood swings, both ways
    "irritable": 0.00,       # per-turn chance of a sudden mood drop for no stated reason
    "autonomy": 0.00,        # per-turn chance it does something of its own instead
    "despair": 0.00,         # extra decay at low mood, and catatonia risk
    "frailty": 1.00,         # general crisis susceptibility
    "heart": 1.00,           # heart-specific crisis weight
    "lungs": 1.00,           # lung-specific crisis weight
    "speed": 1.00,           # distance per push
    "heal_mult": 1.00,       # how fast it knits
    "strain_mult": 1.00,     # how fast it wears out
    "ask_mult": 1.00,        # how often it stops and asks you things
    "talkback": False,       # does it comment on the order itself
    "power": 1.00,           # residual power for the chip while unconscious
    "persuadable": 1.00,     # how well it takes being reasoned with instead of ordered
    "armor": 1.00,           # multiplier on damage that reaches the limb
    "guard": 0.00,           # holds the link shut against orders it does not accept
    "silent": 0.00,          # how much it keeps to itself - refusals, speech, questions
    "snaps": 0.00,           # whether there is an edge to go over at all
    "needs_reason": 0.00,    # persuasion without a stated reason does not land on it
    "drive": 0.35,           # off the link, the chance it simply keeps going anyway
    "link_fragile": 0.00,    # chance forcing it tears the link off entirely
    "jitter": 0.00,          # the eyes will not hold still - fine detail does not resolve
    "violent": 0.00,         # it goes at things, and it does not wait to be told
    "phones": False,         # arrives wearing something over its ears
    "carry_bonus": 0.00,     # what it can hold over what two hands hold
    "wary": 0.00,            # it reads the ground before it puts weight on it
    "appetite": 1.00,        # how fast it empties - some of them cost more to run
    "selfharm": 0.00,        # when it goes off, some of it can come back inward
    "grit": 0.35,            # the chance it does not go down the first time it should
    "reads": 0.00,           # it was taught letters, and the labels are not a wall
    "dissolves": 0.00,       # a noisy link is not an inconvenience, it is a solvent
    "playful": 0.00,         # in a good mood it does things for no reason at all
    "masks": 0.00,           # there is a reason. You are not going to be given the reason
    "insight": 0.30,         # can it tell what you are doing to it, and why
    "pushes": 0.00,          # it will move on the order through pain that stops the others
}

SUBJECTS = [
    {
        "id": "2008",
        "name": "Experiment 2008",
        "tagline": "the steady one - start here",
        "desc": ("The most stable thing they have produced. Even-tempered, sleeps when it is "
                 "told, takes an order without making it a negotiation. It is not brave and it "
                 "is not clever; it is reliable, which in here is worth more than either."),
        "traits": {"refusal_mult": 0.85, "volatility": 0.80, "frailty": 0.90,
                   "persuadable": 1.10, "grit": 0.35, "playful": 0.15,
                   "insight": 0.30},
        "start": {"mood": 62.0, "will": 75.0},
    },
    {
        "id": "1278",
        "name": "Experiment 1278",
        "tagline": "obedient to a fault - it will not save itself",
        "desc": ("1278 does what the chip says. All of it, immediately, without the pause where "
                 "something decides whether an instruction is survivable. It has no refusal in "
                 "it and a body that cannot take what that gets it into. If you order it into "
                 "something lethal it will go, and it will not hold that against you."),
        "traits": {"refusal_mult": 0.15, "volatility": 0.70, "frailty": 1.35,
                   "heart": 1.30, "lungs": 1.35, "heal_mult": 0.85, "ask_mult": 0.5,
                   "power": 0.8, "persuadable": 1.35, "grit": 0.05,
                   "insight": 0.00, "pushes": 1.00},
        "start": {"mood": 58.0, "will": 90.0},
    },
    {
        "id": "101",
        "name": "Experiment 101",
        "tagline": "defiant, volatile, and acts without you",
        "desc": ("101 argues. Its mood turns over without warning and it takes orders as "
                 "opening offers. It will also simply do things - walk off, eat something, "
                 "fight something - while you are still deciding, because the chip is not the "
                 "only thing in there with opinions. In exchange it is the toughest of them. "
                 "It survives its own behaviour, mostly."),
        "traits": {"refusal_mult": 2.20, "volatility": 2.00, "irritable": 0.18,
                   "autonomy": 0.22, "frailty": 0.75, "speed": 1.05, "strain_mult": 0.9,
                   "heal_mult": 1.15, "talkback": True, "ask_mult": 1.4, "power": 1.2,
                   "persuadable": 0.35, "grit": 0.55, "insight": 0.85, "pushes": 0.25},
        "start": {"mood": 45.0, "will": 40.0},
    },
    {
        "id": "0041",
        "name": "Experiment 0041",
        "tagline": "gentle, willing, and it falls a very long way down",
        "desc": ("0041 is the easiest of them to work with and the worst of them to watch. It "
                 "wants to do what is asked. It apologises, in its way, for being hurt. And "
                 "when it goes down it goes all the way down - past sullen, past despondent, "
                 "into something that stops answering the link at all and has to be brought "
                 "back by hand."),
        "traits": {"refusal_mult": 0.50, "volatility": 1.45, "despair": 1.00,
                   "frailty": 1.05, "ask_mult": 1.3, "persuadable": 1.50, "grit": 0.20,
                   "playful": 1.00, "insight": 0.15},
        "start": {"mood": 72.0, "will": 80.0},
    },
    {
        "id": "7",
        "name": "Experiment 7",
        "tagline": "has done this before - and remembers some of it",
        "desc": ("Seven has been run and recovered at least once. There is an old amputation "
                 "healed over at the left arm with a strut already fitted, a great deal of "
                 "wrongness it has learned to carry, and no expectation whatsoever that the "
                 "far end of this is good. It knows things. It is also tired in a way none of "
                 "the others are yet."),
        "traits": {"refusal_mult": 1.25, "volatility": 0.65, "frailty": 1.15,
                   "speed": 0.95, "heal_mult": 0.9, "ask_mult": 0.7, "persuadable": 0.80,
                   "grit": 0.45, "insight": 0.80, "pushes": 0.35},
        "start": {"mood": 42.0, "will": 72.0, "weird": 28.0, "chip": 82.0,
                  "lost_limb": "left arm", "strut": True,
                  "truths": ["The walk has been done before, by this body, and it ended "
                             "somewhere it was brought back from.",
                             "The world has a printed edge, and the edge has no name on it."]},
    },
    {
        "id": "3350",
        "name": "Experiment 3350",
        "tagline": "fast, and its heart knows it",
        "desc": ("Built long in the leg and light in the chest. 3350 covers ground none of the "
                 "others can and pays for it in a heart that runs away with itself under load. "
                 "If you push it the way it wants to be pushed you will watch its pulse come "
                 "apart somewhere around the Ash Flats."),
        "traits": {"speed": 1.30, "strain_mult": 1.45, "heart": 1.80, "frailty": 1.10,
                   "volatility": 1.15, "refusal_mult": 0.95, "power": 0.9,
                   "persuadable": 1.00, "grit": 0.30, "insight": 0.35,
                   "pushes": 0.45},
        "start": {"mood": 60.0, "will": 78.0},
    },
    {
        "id": "682",
        "name": "Experiment 682",
        "tagline": "it cannot hold its eyes still and it does not wait to be told",
        "desc": ("682 came off the same table as 680 and went a different way. Its eyes do not "
                 "settle - everything at arm's length reads as a shape and a guess, and small "
                 "print does not resolve at all, so a great deal of what it picks up stays "
                 "unnamed no matter how much the chip understands. What it does instead of "
                 "looking is move. It goes at things, hard, before anybody has decided "
                 "anything, and it is still going after the thing has stopped.\n"
                 "It wears a set of headphones. They do not come off. The shell of them is the "
                 "only armour on it and it only covers what it covers; the sound inside is the "
                 "only reason the rest of it holds together at all."),
        "traits": {"refusal_mult": 0.70, "volatility": 1.60, "irritable": 0.14,
                   "autonomy": 0.30, "frailty": 0.95, "heart": 1.05, "lungs": 1.00,
                   "speed": 1.05, "heal_mult": 0.85, "strain_mult": 1.12,
                   "ask_mult": 0.35, "power": 1.05, "persuadable": 0.60,
                   "armor": 0.85, "guard": 0.35, "silent": 0.55, "snaps": 1.30,
                   "needs_reason": 0.70, "drive": 0.70, "link_fragile": 0.70,
                   "jitter": 0.85, "violent": 1.00, "phones": True, "grit": 0.95,
                   "playful": 0.25, "insight": 0.45, "pushes": 0.65},
        "start": {"mood": 52.0, "will": 70.0, "pain": 22.0, "weird": 24.0, "chip": 90.0,
                  "injuries": [["right arm", "gashed"], ["left arm", "bruised"]],
                  "truths": ["The sound does not come from anywhere. It has always been "
                             "there and it is the only thing that has."]},
    },
    {
        "id": "680",
        "name": "Experiment 680",
        "tagline": "it has been through a great deal and it decides for itself",
        "desc": ("680 does not talk. It came out of something that took most of it apart and "
                 "the parts that went back together went back harder - there is plate through "
                 "the hide now, and things that would open another one of them do not open it. "
                 "It takes an order better than any of them, because it understands why you "
                 "are asking. It will also decide, quietly and without discussion, that it is "
                 "not going to, and there is no forcing it - the link simply will not carry. "
                 "It is not easily talked round either; the argument has to be a real one. "
                 "And there is an edge on it. It is a long way off and it is very bad."),
        "traits": {"refusal_mult": 0.55, "volatility": 0.55, "irritable": 0.03,
                   "autonomy": 0.20, "frailty": 0.85, "heart": 0.90, "lungs": 1.10,
                   "speed": 0.85, "heal_mult": 0.75, "strain_mult": 1.15,
                   "ask_mult": 0.25, "power": 1.15, "persuadable": 0.55,
                   "armor": 0.50, "guard": 1.00, "silent": 0.90, "snaps": 1.00,
                   "needs_reason": 1.00, "drive": 0.85, "link_fragile": 1.00,
                   "grit": 0.70, "masks": 0.30, "insight": 1.00, "pushes": 0.40},
        "start": {"mood": 58.0, "will": 66.0, "pain": 34.0, "weird": 18.0, "chip": 88.0,
                  "injuries": [["left leg", "broken"], ["right arm", "gashed"],
                               ["tail", "mangled"], ["left ear", "gashed"]],
                  "lost_limb": "right ear", "strut": False,
                  "truths": ["This body has been opened and closed more than once, and "
                             "whoever did it stopped being careful partway through."]},
    },
    {
        "id": "681",
        "name": "Experiment 681",
        "tagline": "it gets there first and nothing living gets past it",
        "desc": ("The page between 680 and 682, and the one nobody reads out. 681 is fast - "
                 "faster over broken ground than anything else in the building - and it is "
                 "careful, in the specific way a thing is careful when it intends to still be "
                 "here later. It checks ground before it stands on it. It notices the wire.\n"
                 "It is also the reason the other two are kept in separate rooms. Anything "
                 "alive in front of it is a thing it is already moving toward, and it does not "
                 "wait for the order, and it does not stop on the order either. It takes more "
                 "damage than anything here and carries more than anything here.\n"
                 "What it does when it has run out of things in front of it is the part the "
                 "file is careful about."),
        "traits": {"refusal_mult": 1.50, "volatility": 1.90, "irritable": 0.26,
                   "autonomy": 0.42, "despair": 0.00, "frailty": 0.62,
                   "heart": 0.95, "lungs": 0.90, "speed": 1.25, "heal_mult": 1.25,
                   "strain_mult": 1.30, "ask_mult": 0.50, "talkback": True,
                   "power": 1.20, "persuadable": 0.30, "armor": 0.80,
                   "guard": 0.25, "silent": 0.25, "snaps": 1.25, "needs_reason": 0.85,
                   "drive": 0.95, "link_fragile": 0.45, "violent": 1.35,
                   "carry_bonus": 6.0, "wary": 0.85, "appetite": 1.20,
                   "selfharm": 0.90, "grit": 0.80, "masks": 0.95, "insight": 1.00,
                   "pushes": 0.55},
        "start": {"mood": 50.0, "will": 58.0, "pain": 14.0, "weird": 20.0, "chip": 94.0,
                  "injuries": [["left ear", "gashed"], ["tail", "gashed"]],
                  "truths": ["Nothing that has come at this body has finished doing it."]},
    },
    {
        "id": "4400",
        "name": "Experiment 4400",
        "tagline": "the newest one - and it cannot tell your voice from its own",
        "desc": ("The most recent number issued, and by every measure they take, the best one "
                 "they have made. Sound, quick enough, heals clean, no old damage anywhere on "
                 "it. It takes an order instantly and without friction because taking orders "
                 "is not something it experiences as happening.\n"
                 "It is the first one the chip was seated in before it was finished growing. "
                 "It has never had a thought arrive from anywhere else. When the link is clean "
                 "it is the easiest thing in here to drive - and when the link goes noisy it "
                 "does not think the chip is wrong, it thinks IT is wrong, and it comes apart "
                 "at a speed nothing else here comes apart at.\n"
                 "It was taught letters. It is the only one that was."),
        "traits": {"refusal_mult": 0.20, "volatility": 1.20, "irritable": 0.00,
                   "autonomy": 0.02, "despair": 0.45, "frailty": 0.85,
                   "heart": 0.95, "lungs": 0.95, "speed": 1.10, "heal_mult": 1.30,
                   "strain_mult": 0.95, "ask_mult": 1.10, "power": 0.85,
                   "persuadable": 1.25, "armor": 1.00, "drive": 0.05,
                   "reads": 1.00, "dissolves": 1.00, "grit": 0.15,
                   "insight": 0.05},
        "start": {"mood": 70.0, "will": 88.0, "weird": 0.0, "chip": 100.0, "intel_bonus": 18.0},
    },
]

BY_ID = {s["id"]: s for s in SUBJECTS}
DEFAULT = SUBJECTS[0]["id"]


# What each one was before the chip, and what was done to it. None of this is available until
# that subject has walked the core - it is the only thing the game hands back for finishing the
# bottom, and it is deliberately the thing it has spent the whole run refusing to tell you.
LORE = {
    "2008": (
        "2008 is the two thousand and eighth attempt and the first that did not have to be "
        "put down in the first week. That is the whole of its distinction. It was not bred "
        "calm - the ones before it were calm too, and they came apart anyway, somewhere "
        "between the third and the ninth day, in a way the notes describe as 'structural "
        "disappointment' and never explains.\n"
        "  What changed at 2008 was not the animal. It was the chip. Everything before it "
        "carried a chip that talked; 2008 carries one that mostly listens, and the thing on "
        "the end of it stopped coming apart. The conclusion in the file is one line long and "
        "it is not about biology.\n"
        "  It has never been told it is the two thousand and eighth of anything. It thinks "
        "the number is a name."),
    "1278": (
        "1278 was the obedience line, and the obedience line worked. It was selected across "
        "nine generations for the absence of the pause - the half second where something "
        "decides whether an instruction is survivable - and by 1278 the pause is gone. Not "
        "suppressed. Gone. There is no structure left in it to do that with.\n"
        "  The line was retired after 1278, and the reason given was not ethical. It was that "
        "a subject with no pause cannot report a fault. It walked into things and did not "
        "mention them, and the people reading the telemetry found out what had gone wrong by "
        "finding out that it had stopped.\n"
        "  It has never once refused an order. The file lists this under failures."),
    "101": (
        "101 is old. Not the hundred and first attempt - the hundred and first of the first "
        "batch, which is a different and much earlier number, and it has been in the building "
        "longer than anybody currently working in it. It is the only survivor of a cohort that "
        "was walked into the outside before anyone had worked out what the outside did.\n"
        "  It remembers that. Not clearly, and not in a form it can say, but it remembers "
        "enough that everything since has struck it as a repetition. The argument it is "
        "having with the chip is not with you. It is with the last one, and the one before "
        "that, and it has been having it for a very long time.\n"
        "  The toughness is not bred in. It is what is left after everything soft has already "
        "been taken off it."),
    "0041": (
        "0041 was not made for the walk. It was made to be looked after - a control, a "
        "baseline, something to hold beside the others and measure them against, and it was "
        "kept in a room with people in it for the whole of its early life. It learned what "
        "hands are for. This is the only one of them that did.\n"
        "  Then the programme needed a body and it was the body that was available.\n"
        "  What goes wrong with 0041 goes wrong because it is still waiting for the room. The "
        "collapse the notes call catatonia is not a failure of the nerve. It is a thing that "
        "was promised something, every day, for years, and has worked out that the promise is "
        "not coming - and the chip on the end of the link, saying encouraging things, is the "
        "closest thing to a hand it has had since."),
    "7": (
        "Seven is not the seventh. Seven is what is left of the name after the rest of it "
        "wore off the tag, and nobody has renewed the tag because nobody expects to need it "
        "much longer.\n"
        "  It has done the walk four times. Three of those it finished. It was recovered each "
        "time, repaired to the standard the budget allowed, and put back at the start with the "
        "chip wiped and the body not - which is why the arm is a strut and the wrongness "
        "starts at twenty-eight and the horizon does not surprise it.\n"
        "  It knows there is something at the end. It does not know what, because the part "
        "that saw it is the part they wipe. The thing it is tired of is not the walking. It is "
        "the specific feeling of having already been somewhere it is being told it has never "
        "been."),
    "3350": (
        "3350 is the speed line and the speed line is a success. It covers ground nothing else "
        "in the building can cover. The heart was a known cost, signed off in advance, on the "
        "reasoning that the walk is a hundred units long and the heart is good for rather more "
        "than a hundred units of walking.\n"
        "  The reasoning is correct. What it leaves out is that the subject does not know it "
        "is a hundred units, cannot pace itself against a number it has never been given, and "
        "runs at whatever the ground in front of it seems to ask for. It is not badly built. "
        "It is built for a distance nobody told it.\n"
        "  Every 3350 that has died has died faster than the one before. The line reads that "
        "as progress."),
    "682": (
        "682 and 680 were opened on the same day by the same hands, and the file keeps them on "
        "facing pages, which somebody did on purpose.\n"
        "  The eyes are the oldest damage on it. Something was done to the nerve early and done "
        "badly, and the result is that the world arrives as motion and mass and never quite "
        "resolves - it has never once read a word. It is not stupid. The file is careful about "
        "that, in the one place it is careful about anything. It simply cannot hold a thing "
        "still long enough to learn what the thing is, so it learned the other way: get to it "
        "first and find out by hand.\n"
        "  The headphones went on in the third year, and the reason given in the notes is "
        "operational rather than kind - a subject that cannot be calmed cannot be worked on. "
        "Whatever is playing has never been recorded anywhere in the file. Nobody wrote down "
        "what it is. The one line about it says the sound predates the set, which is not "
        "possible, and nobody followed that up either.\n"
        "  The shell is a later addition and a cheaper one: plate bonded over the cups because "
        "682 kept taking damage to the side of the head, being the end of it that arrives "
        "first. It protects exactly what it sits on and nothing else, and every technician who "
        "ever wrote about it wrote about it as a housing, not as protection.\n"
        "  What happens when the sound stops is in the file twice. Both entries are short. The "
        "second one is in different handwriting."),
    "680": (
        "680 was not run. 680 was what they practised on.\n"
        "  Every technique in the building was developed on this one: the seating of the chip, "
        "the plate through the hide, the graft, the amputation, the closing-up and the opening "
        "again. It was opened and closed more than four hundred times across eleven years, and "
        "the record stops being a medical record somewhere around the second year and becomes "
        "a list.\n"
        "  It was awake for a great deal of it. The notes say this was necessary. The notes "
        "say a number of things.\n"
        "  The silence is not damage. Its throat works. It stopped somewhere in the middle of "
        "the fourth year, and the file records the date it stopped and no theory about why, "
        "because the person who would have written the theory is the person it stopped talking "
        "to.\n"
        "  What it has instead is judgement - the only thing in the building that has seen "
        "more of this than the building has. When it shuts the channel it is not defying you. "
        "It is telling you, in the only register it has left, that it has watched this exact "
        "instruction kill something before.\n"
        "  And the edge in it is not temper either. It is eleven years of being told to hold "
        "still."),
}


LORE["681"] = (
    "681 is the page between them, and it is the reason the other two are on facing pages at "
    "all - the file was reordered so that 681 would not be in the middle of it.\n"
    "  Same day, same table, same hands. The difference is that 680 and 682 were worked on and "
    "681 was worked WITH. It was the only one of the three that could be sent somewhere and "
    "come back, so it was, repeatedly, for eleven years, into places the building wanted "
    "cleared. It is very good at it. The word the notes use is 'thorough', and they use it "
    "the way you use it about a machine.\n"
    "  Nobody taught it to do that to things. It was selected for noticing, and for speed, and "
    "the rest came with it, and by the time anybody wrote the rest down there was an argument "
    "about whether writing it down was wise.\n"
    "  The last section is two pages of a single technician's handwriting and it is not about "
    "what 681 does to anything else. It is about what happens on the days there is nothing in "
    "front of it - that it does not wind down, that the thing it does to what is in front of "
    "it has to go somewhere, and that on four occasions it went inward, and that on the fourth "
    "occasion they had to open the door.\n"
    "  The recommendation at the bottom is one line: KEEP SOMETHING IN FRONT OF IT.")

LORE["4400"] = (
    "4400 is what the programme is for. Everything learned across four thousand three hundred "
    "and ninety-nine attempts is in this one, and it works: it is sound, it is quick, it heals "
    "clean, it has never had to be repaired, and it has never once refused anything.\n"
    "  The new thing they tried was the timing. Every subject before it had the chip put into "
    "something that was already a thing. 4400 had it seated before it finished growing, and "
    "grew around it, and there has never been a moment of its life in which the voice was not "
    "there. It has no word for the chip. It has never needed one. What comes down the link "
    "does not arrive from anywhere - it is simply what 4400 is currently thinking.\n"
    "  They taught it letters, which they had not bothered with before, and it learned them in "
    "a fortnight, and this is written up as a triumph. It is not clear anybody asked why the "
    "others had not been taught.\n"
    "  The one warning in the file is the shortest entry in it, and it is not about the body: "
    "when the link degrades, 4400 does not experience a degraded link. It experiences itself "
    "becoming untrue. There is no second opinion available to it. There never has been.\n"
    "  The file does not say what happened to the four thousand three hundred and ninety-nine.")


# ---------------------------------------------------------------- the last thing it says
# FINAL is what the body does. This is what it SAYS first, and it is picked on how the thing
# was feeling when it happened, which is why the same subject does not die the same way twice.
# It is in the spoken register - halting, breathy, ".." for hesitation - because it is speech
# and not narration, and it comes BEFORE the body stops.
#
# Five states. `feeling()` picks one off the run:
#   agony     - the pain is the whole of it
#   afraid    - it knows, and it has not made peace with knowing
#   betrayed  - it has worked out what you did, or it has been lied to enough times
#   adrift    - wrongness high: it is not sure whose death this is
#   calm      - none of the above. Not happy. Just not any of the above.
LAST = {
    "2008": {
        "agony": '"..ow.. o.. ow.. it\'s.. it\'s a lot.. it\'s.. a lot.."',
        "afraid": '"..wait.. wait, i.. i was doing it.. i was doing it right.."',
        "betrayed": '"..you.. you counted.. you counted wrong.."',
        "adrift": '".. two.. thousand.. and.. eight.. that\'s.. that\'s mine.. that one\'s mine.."',
        "calm": '"..two thousand.. and eight.." it says. It has never said it out loud before '
                'and there is nobody here who was going to answer it.',
    },
    "1278": {
        "agony": '"..\'s alright.. \'s alright.. m\'still.. m\'still going.."',
        "afraid": '"..did i.. did i do it.. did i do the.. the thing.."',
        "betrayed": '"..okay.." Just that. It does not sound like an accusation and that is '
                    'the worst available version of it.',
        "adrift": '"..who.. who said.. i heard.. i heard someone say.."',
        "calm": '"..next one.." it says. "..tell the.. tell the next one.. it\'s not.. '
                'not far.."',
    },
    "101": {
        "agony": '"..GET.. get it OFF.. get it.. aaghh.."',
        "afraid": '"..no. no, we\'re not.. we are NOT doing this.. get UP.. get up.."',
        "betrayed": '"..knew it.. i KNEW.. i knew it was.. you.. it was always.. you.."',
        "adrift": '"..which.. which one are you.. you\'re not.. you\'re not the first one.."',
        "calm": '"..hh.. fine.. fine. i\'m done arguing.." It sounds, for the first time in '
                'the whole run, like it is talking to you and not to somebody else.',
    },
    "0041": {
        "agony": '"..i\'m sorry.. i\'m sorry.. m\'sorry.. i can\'t.. i can\'t be quiet.."',
        "afraid": '"..stay.. can you.. can you stay.. just.. just till.."',
        "betrayed": '"..oh.." A small sound, and then nothing, and it does not ask you '
                    'anything else.',
        "adrift": '"..is someone.. is someone coming.. someone\'s.. someone was coming.."',
        "calm": '"..good.. was i.. was i good.."',
    },
    "7": {
        "agony": '"..hh.. same.. it\'s the.. it\'s the same as.. last.. time.."',
        "afraid": '"..not again.. not.. not again, i don\'t.. i don\'t want.. to start.. '
                  'again.."',
        "betrayed": '"..you always.. you always do this bit.. and then.. you forget.. '
                    'you get to forget.."',
        "adrift": '"..have we.. have we been here.. we\'ve been.. i\'ve been here.."',
        "calm": '"..alright.." it says, like somebody clocking off. "..alright. that\'s.. '
                'that\'s four.."',
    },
    "3350": {
        "agony": '"..slow.. it\'s.. everything\'s.. gone.. slow.."',
        "afraid": '"..i can still.. i can still go.. i can.. just let me.. let me up.."',
        "betrayed": '"..you knew.. you knew what it.. what it does.. and you still.. said.. '
                    'go.."',
        "adrift": '"..how far.. how far was it.. nobody.. nobody ever.. said how far.."',
        "calm": '"..was that.. was that fast.." it says. "..was that.. fast enough.."',
    },
    "682": {
        "agony": '"..AGH.. it\'s.. loud.. it\'s too.. too LOUD.."',
        "afraid": '"..don\'t.. don\'t let it.. don\'t let it stop.. keep it.. keep it on.."',
        "betrayed": 'It does not say anything. It takes one hand off the wound and puts it '
                    'over the cup on the left side and holds it there instead.',
        "adrift": '"..the.. the sound\'s.. coming from.. it\'s coming.. from in.. side.."',
        "calm": '"..still.. playing.." it says. "..s\'still.. playing.."',
    },
    "680": {
        "agony": 'Nothing. There is nothing to hear and there has not been for seven years, '
                 'and whatever this costs it, it costs it in silence.',
        "afraid": 'It does not make a sound. It puts one hand flat against the nearest solid '
                  'thing, at head height, the way it has done at a hundred walls, and leaves '
                  'it there.',
        "betrayed": 'It speaks. One word, in a voice nothing in this building has heard since '
                    'the fourth year, cracked and slow and entirely deliberate:\n'
                    '  "..enough.."',
        "adrift": 'It taps. Short, short, long, against the floor. Twice. Then it stops.',
        "calm": 'It looks at you - at the chip, at the place the chip is, which is inside its '
                'own head - and it does not say anything, and the not saying anything is '
                'clearly the finished version of a thought and not the absence of one.',
    },
    "681": {
        "agony": '"..hh.. HH.. it\'s fine.. it\'s.. it\'s FINE.."',
        "afraid": 'It is making a noise it has never made in front of you. It is not a threat '
                  'and it is not for your benefit and it stops as soon as it notices you can '
                  'hear it.',
        "betrayed": 'The register changes completely. It is flat, and level, and it is using '
                    'words in the order somebody uses them who has been choosing not to:\n'
                    '  "..you will do this again.. to the next one.. you should know that i '
                    'worked out what you were.. a long way back.. i just could not think of '
                    'anything to do about it.."',
        "adrift": '"..in front of.. keep something.. in front of.. me.."',
        "calm": '"..alright.." it says, and then, after a while, quieter and in a voice that '
                'is doing none of the work it usually does: "..that was well done."',
    },
    "4400": {
        "agony": '"..this is.. this is wrong.. this isn\'t.. i\'m not supposed.. to.."',
        "afraid": '"..am i still.. am i still here.. tell me if.. if i\'m still.."',
        "betrayed": '"..we did this.." it says. Not you. We. "..we did this.. we did this to '
                    'us.."',
        "adrift": '"..which of.. which of this.. was me.. i need.. i need to know which.."',
        "calm": '"..stay.. in.. " it says, very simply. "..don\'t.. don\'t go out of me.."',
    },
}


def feeling(s):
    """How it is taking it. Read off the run, worst first."""
    if s.pain >= 78:
        return "agony"
    if getattr(s, "suspicion", 0.0) >= 55 or int(getattr(s, "lies", 0) or 0) >= 3:
        return "betrayed"
    if s.weird >= 62:
        return "adrift"
    if s.will < 34 or s.mood < 26:
        return "afraid"
    return "calm"


def last_words(sid, s):
    row = LAST.get(sid)
    if not row:
        return None
    return row.get(feeling(s)) or row.get("calm")


def lore(sid):
    return LORE.get(sid)


# ---------------------------------------------------------------- the last of it
# Nothing here is a game-over screen. It is what this specific body did at the end, and every
# one of them does it differently, because the only thing that was ever different about them
# was what they had already had done to them.
#
# RISING is the other branch: the one it does not go down the first time it should. It is a
# reprieve and not a rescue - see lastbreath.py - and the text has to read as a thing getting
# up off the ground, not as the problem going away, because the problem has not gone away.
FINAL = {
    "2008": ("It does what it has done every time it has been asked to stop: it sits down "
             "properly first, front feet together, the way something sits when it expects to "
             "be got up again shortly.\n"
             "  It is still waiting to be told what to do next when it stops being able to be "
             "told anything. It does not seem to mind. It never has."),
    "1278": ("It is still going when it stops. Mid-stride, facing the way you last pointed it, "
             "with no hesitation anywhere in the whole movement.\n"
             "  It never once mentioned any of this was happening. It was not being brave. "
             "There was nothing in it that could have mentioned it, and there is nothing in it "
             "now that knows the difference between this and the end of any other order."),
    "101": ("It fights it. Of course it does. It gets a hand under itself twice and the second "
            "time it nearly makes it, and it is snarling at the ground the whole way down, at "
            "the light, at you, at whatever it has actually been snarling at all this time.\n"
            "  The last thing it does is turn its head to look back the way you brought it, "
            "and there is nothing in the look you would want to write down."),
    "0041": ("It goes down gently and it apologises. Not in words - it puts its head over "
             "toward where a hand would be, the way it has every single time you have hurt it, "
             "and waits there for the hand.\n"
             "  It has been waiting for that hand since before you existed. It goes on waiting "
             "for a while after it stops being able to."),
    "7": ("It knows. That is the worst part of it and it always has been - somewhere under the "
          "wipe it knows the shape of this, because it has been here, and it lies down before "
          "it has to, in a place it chooses, facing the way it wants to face.\n"
          "  The last thing on its face is not fear. It is recognition, and something very "
          "close to relief that this time nobody is going to bring it back."),
    "3350": ("It goes fast, the way it does everything. The chest that was signed off in "
             "advance simply stops arguing, mid-run, and the rest of it is still running when "
             "the chest is not.\n"
             "  It travels some distance after. It was always going to. It never knew how far "
             "it was supposed to be going and it was not going to find out now."),
    "682": ("The sound stops before it does.\n"
            "  It gets a hand up to the side of its head, which is the thing it has always "
            "done, and this time there is nothing coming out of what is under the hand. It "
            "stays there. Both hands, then, pressed to the cups, trying to hold something in "
            "that is not in there any more.\n"
            "  It goes down still holding them on. Whatever was playing, it has been playing "
            "since before the set was ever put on it, and now it is not, and 682 is the only "
            "thing that ever heard it."),
    "680": ("It does not make a sound, because it has not made a sound in seven years, and it "
            "is not going to start over this.\n"
            "  It lowers itself. Deliberately - not a collapse, a decision, the way it has "
            "made every decision it has made since you met it. It arranges its own limbs. It "
            "puts the ruined side down and the good side up, which is what it was made to do "
            "four hundred times by people who wanted a better angle.\n"
            "  The eye that still opens stays open, on the place in the air where a person "
            "would be standing if there were one, until it does not."),
    "681": ("It does not lie down. It backs up until there is rock behind it and it stands "
            "there facing out, breathing wrong, watching the ground in front of it for "
            "anything that might still be coming.\n"
            "  Nothing comes. That turns out to be the problem. It goes on standing a long "
            "time after there is any reason to, and it is still standing when it stops, and "
            "it does not fall over for a while after that either."),
    "4400": ("It asks you whether it is still there. Not aloud - the question comes up the link "
             "the way everything from it comes up the link, indistinguishable from you asking "
             "it yourself, so that for a moment you cannot tell which of you wanted to know.\n"
             "  Then the link goes quiet, and the quiet is the first thing that has ever "
             "happened to 4400 that did not come from you, and it has nothing at all to meet "
             "it with."),
}

RISING = {
    "2008": ("It gets up. It should not - there is nothing left in it to get up with - and it "
             "does it anyway, slowly, front feet first, the way it does everything. It has not "
             "been told it is finished. Nobody has told it that."),
    "1278": ("It is upright again before you have decided anything, swaying, one leg not "
             "taking weight. It had an order. The order has not been cancelled."),
    "101": ("It comes up off the ground swearing at it. Blood-slick and shaking and absolutely "
            "furious that the ground tried that, and it is on its feet out of spite alone, "
            "which for 101 has always been enough."),
    "0041": ("It lifts its head and looks for you first, before it looks at itself. Then it "
             "gets its legs under it, one at a time, carefully, so as not to be any more "
             "trouble than it has already been."),
    "7": ("It gets up the way something gets up that has got up from this before. No "
          "surprise anywhere in it. It checks the bad arm, finds it still there, and stands."),
    "3350": ("The chest catches, misses, catches again - and it is up, chest going far too "
             "fast, already looking down the ground in front of it."),
    "682": ("His fur is all covered in blood as he slowly gets up.. his vision seeming to be "
            "more clear..\n"
            "  For the first time since the link came up, 682 is looking at one thing and the "
            "thing is holding still. Whatever the body is doing to keep him upright, it has "
            "spent everything it had on the eyes, and the world has edges in it.\n"
            "  He does not appear to be in pain. That is not the same as not being hurt, and "
            "it is not going to last."),
    "680": ("It gets up. Silently, and without any indication that it considered not getting "
            "up, and it looks at the place where a person would be standing as if to see "
            "whether you noticed."),
    "681": ("It comes up fast and wrong, off the ground in one movement, already turning to "
            "face whatever did it. Its own blood is coming off it in strings and it has not "
            "registered that any of it is its own."),
    "4400": ("It sits up. It is entirely calm, because as far as it can tell nothing has "
             "happened - you have not told it that anything has happened, and it has no other "
             "source for that information."),
}


def final_words(sid):
    return FINAL.get(sid)


def rising(sid):
    return RISING.get(sid)


def resolve(text):
    """Accept '101', 'experiment 101', 'exp101', or an index. Returns a subject dict."""
    t = (text or "").strip().lower().replace("experiment", "").replace("exp", "").strip()
    if not t:
        return BY_ID[DEFAULT]
    if t in BY_ID:
        return BY_ID[t]
    for k in BY_ID:
        if k.lstrip("0") == t.lstrip("0"):
            return BY_ID[k]
    if t.isdigit() and 1 <= int(t) <= len(SUBJECTS):
        return SUBJECTS[int(t) - 1]
    return None


def trait(s, name):
    """A trait as it currently stands - subject baseline, but runs can move some of these."""
    subj = BY_ID.get(getattr(s, "subject", DEFAULT), BY_ID[DEFAULT])
    base = dict(BASE)
    base.update(subj["traits"])
    v = base.get(name, BASE.get(name, 1.0))
    drift = (getattr(s, "trait_drift", None) or {}).get(name)
    if drift:
        v = v * drift if isinstance(v, (int, float)) and not isinstance(v, bool) else v
    return v


def info(s):
    return BY_ID.get(getattr(s, "subject", DEFAULT), BY_ID[DEFAULT])


def name(s):
    return info(s)["name"]


def apply_start(s, subj):
    """Seat the chip in this one."""
    s.subject = subj["id"]
    s.trait_drift = {}
    st = subj.get("start", {})
    for k in ("mood", "will", "weird", "chip", "blood", "warmth", "pain"):
        if k in st:
            setattr(s, k, float(st[k]))
    # some of them do not arrive whole. Old damage, already bled out and scabbed over - it
    # carries the state and the hp, but not the bleed, because it happened a long time ago.
    HP = {"bruised": 88.0, "gashed": 60.0, "broken": 40.0, "mangled": 18.0}
    for limb, state in st.get("injuries", []):
        if limb in s.limbs and state in HP:
            s.limbs[limb]["state"] = state
            s.limbs[limb]["hp"] = HP[state]
            s.limbs[limb]["bleed"] = 0.0
            s.limbs[limb]["bound"] = True
    if st.get("lost_limb"):
        limb = st["lost_limb"]
        s.limbs[limb]["state"] = "lost"
        s.limbs[limb]["hp"] = 0.0
        s.limbs[limb]["bleed"] = 0.0
        s.limbs[limb]["strut"] = bool(st.get("strut"))
        s.stats["limbs_lost"] = 1
    if st.get("intel_bonus"):
        # one of them was taught letters. It does not arrive looking at a wall of labels it
        # cannot read - which is the whole of its advantage, and it is not a small one.
        s.intel = min(100.0, float(getattr(s, "intel", 14.0)) + float(st["intel_bonus"]))
    if subj["traits"].get("phones"):
        # Two separate things that happen to be one object: a shell over the ears, which is
        # armour and only where it sits, and a sound inside it, which is not armour at all.
        s.phones = {"on": True, "hp": 100.0, "music": True, "broke_at": 0}
    for t in st.get("truths", []):
        if t not in s.truths:
            s.truths.append(t)
    s.note("The chip comes up inside %s." % subj["name"])
    return s


def drift_trait(s, name, mult):
    """A run bending a subject away from where it started."""
    d = s.trait_drift = (getattr(s, "trait_drift", None) or {})
    d[name] = max(0.2, min(4.0, d.get(name, 1.0) * mult))


# What the chip sees in the first two seconds after it comes online. Character through
# behaviour only - none of this says what any of them is, it shows you.
IMPLANT = {
    "2008": ("sits up slowly, and waits... and does not try the staples, and does not try the "
             "door... and looks at the corridor like something that expects to be told"),
    "1278": ("is already standing... before the link has finished closing, before any order has "
             "been given, upright and facing the door and waiting with its hands open"),
    "101": ("gets one hand up to the staples and pulls... and snarls at the wall, at the light, "
            "at the room... and sits back down deliberately, watching the door it has decided "
            "not to go through yet"),
    "0041": ("curls in on itself on the clean floor... and puts its head down against nothing at "
             "all, the way something does when it expects a hand there... and holds very still, "
             "and waits to be told it is alright"),
    "7": ("reaches up without being asked and finds the staples with one finger... and stops... "
          "and lowers the hand again, and looks at the door the way you look at a door you have "
          "already been through"),
    "682": ("is up before the link is, and hits the door once, hard, with the flat of a hand... "
            "and stands there with its head going side to side trying to make the room hold "
            "still... and you can hear something through the headphones from across the room, "
            "playing, and it has not stopped"),
    "680": ("does not move at all... and is awake, and has been awake the whole time, watching "
            "the ceiling with the eye that still opens... and turns its head, once, to look at "
            "the place in the room where a person would be standing if there were one"),
    "681": ("is on its feet in the time it takes the link to close... and is at the door, and "
            "has both hands flat on it, reading it... and then turns and looks at every corner "
            "of the room in order, fast, twice, checking what else is in here with it"),
    "4400": ("opens its eyes the moment the link does... and there is no gap between the two "
             "things at all, no waking, no working out where it is... and it looks at the door "
             "because you looked at the door, and it does not know that is why"),
    "3350": ("is up and moving before the link steadies... three steps one way, three back,"
             "chest going far too fast for a thing that has not done anything yet... and it "
             "looks down the corridor and wants to be running"),
}


def implantation(sub):
    return ("THE CHIP HAS BEEN IMPLANTED INTO %s...\n\n  ...as it %s."
            % (sub["name"].upper(), IMPLANT.get(sub["id"], "comes round on the floor")))


def roster(marker=None):
    """What the player is shown. Deliberately says nothing about any of them - finding out
    what is on the other end of the link is the point."""
    from . import regions as REG
    L = ["SUBJECTS THE CHIP CAN BE SEATED IN", ""]
    opened = []
    for i, sub in enumerate(SUBJECTS, 1):
        mark = ">>" if sub["id"] == marker else "  "
        tags = []
        if REG.lore_open(sub["id"]):
            tags.append("history")
            opened.append(sub["id"])
        if REG.destiny_open(sub["id"]):
            tags.append(REG.DESTINY_NAME.lower())
        L.append(("%s %d)  %-18s%s" % (mark, i, sub["name"],
                                       ("   [%s]" % ", ".join(tags)) if tags else "")).rstrip())
    if opened:
        L.append("")
        L.append("Read one with:  .\\run.bat lore %s" % opened[0])
    L.append("")
    L.append("Start one with:  .\\run.bat new <number>      e.g.  .\\run.bat new 3")
    L.append("Or by its number:  .\\run.bat new 101")
    L.append("")
    L.append("The file says nothing about any of them beyond the number, and neither will the")
    L.append("chip. They are not the same to drive. You find that out by driving them.")
    L.append("%s is first on the list and is what you get if you do not choose."
             % SUBJECTS[0]["name"])
    return "\n".join(L)
