"""Calibration.

Before the run proper, the chip has to be walked in. Ten steps inside the Holding: each one
teaches the thing at the other end of the link one verb it will need, and the door out stays
shut until all ten are done.
"""

STEPS = [
    {"cmd": "look", "verbs": ("look", "l", "where", "scene"),
     "say": "Open your eyes and see where you are.",
     "why": "CALIBRATION 1/10 - sight. Command: look",
     "done": "Sight is yours. It sees what you tell it to see."},
    {"cmd": "status", "verbs": ("status", "self", "body", "condition"),
     "say": "Feel the body you have been given. All of it, limb by limb.",
     "why": "CALIBRATION 2/10 - proprioception. Command: status",
     "done": "You can read its body now. Read it often; it will not always tell you."},
    {"cmd": "inv", "verbs": ("inv", "i", "inventory", "bag"),
     "say": "Find out what it is carrying.",
     "why": "CALIBRATION 3/10 - inventory. Command: inv",
     "done": "What it holds, you know it holds."},
    {"cmd": "think", "verbs": ("think", "monologue", "mind"),
     "say": "Listen to it instead of talking to it.",
     "why": "CALIBRATION 4/10 - the inward channel. Command: think",
     "done": ("You can hear it. It does not know that it is being heard, and it does not know "
              "what it is. Neither of those is your doing.")},
    {"cmd": "gather", "verbs": ("gather", "search", "scavenge", "forage", "loot"),
     "say": "Make its hands work. Take something off the floor of this place.",
     "why": "CALIBRATION 5/10 - manipulation. Command: gather",
     "done": "Its hands answer. Note that they are hands and not paws."},
    {"cmd": "craft bandage", "verbs": ("craft",),
     "say": "Make something out of what it holds. Cloth into a bandage.",
     "why": "CALIBRATION 6/10 - fabrication. Command: craft bandage",
     "done": "It can build. Most of what keeps it alive later, it will have to build."},
    {"cmd": "tend left ear", "verbs": ("tend", "bind", "treat", "patch"),
     "say": ("There is a cut behind its left ear from where they seated the chip. "
             "Close it. Learn what closing something costs."),
     "why": "CALIBRATION 7/10 - first aid. Command: tend left ear",
     "done": ("You have seen what comes out of it: orange, and bright, and lit from inside. "
              "So are its eyes. Nobody has explained this to it.")},
    {"cmd": "reassure", "verbs": ("reassure",),
     "say": ("The link carries orders. It does not carry willingness. Hold the channel open "
             "and give it nothing but that."),
     "why": "CALIBRATION 8/10 - the other lever. Command: reassure",
     "done": ("It settles. Remember this: when it refuses you later - and it will refuse you - "
              "this, 'persuade', or 'override' are your three answers. "
              "Only one of them costs the chip.")},
    {"cmd": "map", "verbs": ("map",),
     "say": "Look at the route they have laid out for it.",
     "why": "CALIBRATION 9/10 - the route. Command: map",
     "done": "Eight zones and a line at the end of them. That line is the whole point of it."},
    {"cmd": "go", "verbs": ("go", "forward", "advance", "walk", "move", "onward", "north"),
     "say": "Now make it walk.",
     "why": "CALIBRATION 10/10 - locomotion. Command: go",
     "done": "It walks when told. Calibration complete."},
]

GATE_AT = 7.0        # it cannot leave the Holding until calibration is finished


def wanted(s):
    """Calibration happens once, at the very top of a normal run.

    Coming down into the crust or the core you are already seated and already working, so
    there is nothing to calibrate. Destiny never gets it at all: that act assumes you have
    walked the normal one and the README says nothing about it on purpose.
    """
    from . import regions as REG
    if REG.on_destiny(s):
        return False
    return getattr(s, "region", REG.DEFAULT) == REG.DEFAULT


def done(s):
    if not wanted(s):
        return True
    return s.tutorial >= len(STEPS)


def current(s):
    if done(s):
        return None
    return STEPS[s.tutorial]


def prompt(s):
    st = current(s)
    if not st:
        return None
    return "%s\n  %s" % (st["why"], st["say"])


def check(s, verb, arg=""):
    """Did this command satisfy the current step? Returns a feedback line or None."""
    st = current(s)
    if not st:
        return None
    if verb not in st["verbs"]:
        return None
    if st["cmd"] == "craft bandage":
        # the step is making the thing, not typing the words
        if "bandage" not in (arg or "") or not s.last_action_ok:
            return None
    s.tutorial += 1
    out = ["CALIBRATION STEP PASSED. " + st["done"]]
    if done(s):
        s.flag("calibrated")
        s.will = min(100.0, s.will + 10.0)
        s.mood = min(100.0, s.mood + 8.0)
        s.note("Calibration complete. The door out of the Holding releases.")
        out.append("")
        out.append("CALIBRATION COMPLETE. The door at the end of the corridor unlatches itself.")
        out.append("You have the whole set of verbs now. Everything past this point is the run: "
                   "100 units of distance, eight zones, and something counting at the far end.")
        out.append("It still does not know what it is. That part is findable - try 'think', and "
                   "read everything you come across.")
    # the frame prints the current prompt above the feedback already - repeating it here is
    # what made every calibration step announce itself twice
    return "\n".join(x for x in out if x is not None)


def assist(s):
    """Never let calibration strand you for want of two strips of cloth."""
    st = current(s)
    if not st or st["cmd"] != "craft bandage":
        return None
    short = 2 - s.inv.get("cloth", 0)
    if short <= 0:
        return None
    s.inv["cloth"] = s.inv.get("cloth", 0) + short
    s.note("The wall dispenser lets go of more wrap when you lean on it.")
    return ("CALIBRATION AID: there was not enough cloth left to make a bandage. The wall "
            "dispenser gives up %d more strip%s when you lean on it."
            % (short, "" if short == 1 else "s"))


def blocked(s, verb, distance):
    """Refuse to leave the Holding before calibration is finished."""
    if done(s):
        return None
    if verb not in ("go", "forward", "advance", "walk", "move", "onward", "north"):
        return None
    if distance < GATE_AT:
        return None
    st = current(s)
    return ("BLOCKED: the door at the end of the Holding will not release until the chip is "
            "calibrated.\n  Outstanding: %s\n  %s" % (st["why"], st["say"]))


def setup(s):
    """Scripted starting state: the incision they left behind the ear."""
    if not wanted(s):
        s.tutorial = len(STEPS)
        return
    L = s.limbs["left ear"]
    L["state"] = "gashed"
    L["hp"] = 68.0
    L["bleed"] = 0.12
    s.note("There is a fresh incision behind your left ear, held with two staples.")
    s.inner("Something is behind your ear. It does not feel like it grew there.")
