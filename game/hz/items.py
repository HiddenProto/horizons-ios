"""Materials, recipes, and what happens when you use a thing."""
from . import body as B

# name -> (short description, weight-ish note)
CATALOG = {
    "cloth": "Strip of grey wrap. Binds wounds, wicks water, burns well.",
    "scrap": "Bent plate metal. Cuts your pads if you are careless.",
    "shard": "A cutting edge. Glass, ceramic, or something that used to be a tooth.",
    "branch": "Dry limb of a scrap tree. Levers, splints, hafts.",
    "cord": "Sinew or stripped cable. Holds things to other things.",
    "resin": "Amber sap that sets hard and stinks of solvent.",
    "glowmoss": "Moss that answers your eyes with the same orange. Medicinal.",
    "charcoal": "Cold black. Filters water, hides your shine.",
    "hide": "Cured skin off something that had less luck than you.",
    "water": "A swallow of drinkable water.",
    "ration": "Sealed block of grey protein. Tastes of the room you woke in.",
    "meat": "Raw. Risky. Filling.",
    "bandage": "Boiled cloth, tight-rolled. Stops orange leaving you.",
    "salve": "Glowmoss mashed into resin. Drives heat out of a wound.",
    "splint": "Branch and cord. Makes a broken limb carry weight again.",
    "torch": "Light and warmth in one hand, for a while.",
    "spear": "Reach, and a point at the end of it.",
    "waterskin": "Holds three swallows instead of one.",
    "filter": "Cloth over charcoal. Makes bad water survivable.",
    "strut": "A crude armature. Can be grafted where a limb used to be.",
    "stim": "Recovered injector. Burns tomorrow to buy an hour now.",
    "tag": "Your own identity plate. HORIZON/07.",
    "keycard": "Handler's card, edges chewed by your own teeth.",
    "wrap": "A hide cut and worked soft. Binds a wound as well as cloth does.",
    "map scrap": "Half a survey print. The far edge is marked with a line and no label.",
    # manufactured, found from the crust down. These are the ones intelligence gates.
    "coagulant": "A single-use clotting charge. Shuts a bleed that dressing cannot.",
    "antisepsis": "Sterilising gel in a crush tube. Takes the heat out of an infection outright.",
    "nerveblock": "An ampoule that switches a limb off. Pain goes; so does the use of it.",
    "marrow": "Grafting marrow in a cold sleeve. Rebuilds what is broken inside a limb.",
    "stabiliser": "A gene stabiliser, mostly full. Holds a body to its own pattern.",
    "bag": "A carrier built from hide and cord. Things go in it instead of in your hands.",
    "battery": "Heavier than it has any right to be, and still faintly lit. They want this.",
    # worn or carried, and working the whole time you have them - see WORN below
    "coat": "Hide sewn into something that goes over the shoulders. Keeps the core warm.",
    "boots": "Hide bound over the feet and up the shin. The ground stops taking its toll.",
    "mask": "Cloth over charcoal, tied across the muzzle. Filters what the air is carrying.",
    "brace": "Scrap and cord strapped across the back. Takes load off everything else.",
    "sled": "A dragging frame. Holds a great deal and makes every step heavier.",
    "grapple": "A hooked shard on a long cord. Turns a climb into a haul.",
    "condenser": "A folded scrap trap that pulls water out of air that has none to spare.",
    # used once, for a specific problem
    "lamp": "Glowmoss sealed in resin behind scrap. Light that does not need feeding.",
    "poultice": "Mashed glowmoss bound in cloth. Draws the heat out over hours, not seconds.",
    "flare": "Packed resin and charcoal. Burns white and very loud.",
    "tinder": "Resin-soaked cloth. Makes a fire out of a bad night.",
    "snare": "Cord and bent scrap. Left set, it does the hunting while you sleep.",
    "club": "A branch weighted with scrap. Simpler than a spear and harder to drop.",
    "dust fungus": "Grey growth off the flats. Edible, barely, and it holds water.",
    # the last act is a chain of shut doors, and these are the answers to four of them
    "cutters": "Two plates of scrap ground to an edge and pinned through the middle. Bites wire.",
    "pry bar": "A length of something structural, flattened at one end by hitting it with something else structural.",
    "lagging": "Layered hide and resin, bound to the feet. Nothing gets through it, including current.",
    "plate key": "A thin card on a lanyard with a name worn off it. Doors here were built to want one.",
    # --- things made to put between the body and whatever is coming
    "blade": "A long shard seated in a split haft and bound down hard. It is a knife the size of an arm.",
    "hook": "Bent plate ground to a point on a short handle. It goes in and it does not come out on its own.",
    "sling": "Cord and a hide pouch. It puts something heavy somewhere you are not.",
    "plate": "Scrap beaten flat and strapped along the forearm. Ugly, heavy, and between you and the teeth.",
    "line gun": "The tube and coil off a trap, carried instead of walked into. It fires once and then it is a stick until you wind it.",
    "charge": "A mine, lifted whole and not gone off. It is patient and it does not care whose weight it is under.",
    "cell": "A power cell out of something that was pointed at you. Still warm, still charged, and the chip can drink it.",
    # --- things made to put into the body
    "burn": "Marrow cooked down into moss. It takes the brakes off and sends the bill later.",
    "blocker": "Moss and resin, crude, and it works. Nothing hurts. Nothing hurting is not the same as nothing being wrong.",
    "clot": "Charred resin. Packed into a wound it goes hard and stops the orange, and it is not clean.",
    "damper": "Dark water, steeped and settled. It takes the edge off whatever is standing on the edge.",
}

# name -> what it takes to recognise it, and what it looks like until you can
MANUFACTURED = {
    "coagulant": {"intel": 30.0, "looks": "a flat sealed packet, cold to the touch"},
    "antisepsis": {"intel": 36.0, "looks": "a crush tube with a bitter smell at the seam"},
    "nerveblock": {"intel": 46.0, "looks": "a glass ampoule with a needle folded against it"},
    "marrow": {"intel": 58.0, "looks": "a sleeve of something grey that is colder than the rock"},
    "stabiliser": {"intel": 70.0, "looks": "a heavy grey cylinder that hums when held"},
    "stim": {"intel": 24.0, "looks": "an injector with the label worn off"},
}

RECIPES = {
    "bandage": {"need": {"cloth": 2}, "make": {"bandage": 1}, "arms": 1,
                "text": "You tear and roll the cloth tight."},
    "wrap": {"need": {"hide": 1}, "make": {"bandage": 1}, "arms": 1,
             "text": "You cut a hide into a long strip and work it soft enough to bind with."},
    "salve": {"need": {"glowmoss": 2, "resin": 1}, "make": {"salve": 1}, "arms": 1,
              "text": "You crush moss into resin until it glows like your own blood."},
    "splint": {"need": {"branch": 1, "cord": 1}, "make": {"splint": 1}, "arms": 2,
               "text": "You lash branch to cord into a rigid sleeve."},
    "torch": {"need": {"branch": 1, "cloth": 1, "resin": 1}, "make": {"torch": 1}, "arms": 1,
              "text": "You wrap resin-soaked cloth around a branch."},
    "spear": {"need": {"branch": 1, "shard": 1, "cord": 1}, "make": {"spear": 1}, "arms": 2,
              "text": "You seat the shard in a split haft and bind it down."},
    "waterskin": {"need": {"hide": 1, "resin": 1}, "make": {"waterskin": 1}, "arms": 2,
                  "text": "You seal a hide pouch with resin at the seams."},
    "filter": {"need": {"cloth": 1, "charcoal": 1}, "make": {"filter": 1}, "arms": 1,
               "text": "You pack charcoal into a cloth funnel."},
    "strut": {"need": {"scrap": 2, "cord": 2, "resin": 1}, "make": {"strut": 1}, "arms": 1,
              "text": "You bend scrap into a bone-shape and bind it. It is ugly. It is a limb-shape."},
    "cord": {"need": {"hide": 1}, "make": {"cord": 2}, "arms": 1,
             "text": "You cut hide into strips and twist them."},
    "charcoal": {"need": {"branch": 2}, "make": {"charcoal": 2}, "arms": 1,
                 "text": "You char branches down in a smothered fire."},
    "coat": {"need": {"hide": 3, "cord": 2}, "make": {"coat": 1}, "arms": 2,
             "text": "You cut hide to a shape that goes over the shoulders and lash it shut at "
                     "the front. It is not warm. It is the difference between the cold getting "
                     "at the core and the cold getting at the hide."},
    "boots": {"need": {"hide": 2, "cord": 1}, "make": {"boots": 1}, "arms": 2,
              "text": "You bind hide over both feet and up the shin. It walks differently "
                      "almost at once - less flinching, more ground covered per flinch."},
    "mask": {"need": {"cloth": 2, "charcoal": 1}, "make": {"mask": 1}, "arms": 1,
             "text": "Charcoal between two layers of cloth, tied across the muzzle. What it "
                     "breathes now has been through something first."},
    "brace": {"need": {"scrap": 2, "cord": 2}, "make": {"brace": 1}, "arms": 2, "intel": 20.0,
              "text": "Scrap bent to the line of the back and strapped across it. The load "
                      "stops going through the parts that were carrying it badly."},
    "club": {"need": {"branch": 1, "scrap": 1, "cord": 1}, "make": {"club": 1}, "arms": 1,
             "text": "A branch with plate lashed to the heavy end. No reach and no point, and "
                     "it does not come out of your hand when the thing you hit moves."},
    "snare": {"need": {"cord": 2, "scrap": 1}, "make": {"snare": 2}, "arms": 2,
              "text": "Bent scrap, a loop, and enough tension to hold. Set it and something "
                      "else does the hunting while you are asleep."},
    "tinder": {"need": {"resin": 1, "cloth": 1}, "make": {"tinder": 2}, "arms": 1,
               "text": "Cloth worked full of resin until it will not stop burning once lit."},
    "poultice": {"need": {"glowmoss": 3, "cloth": 1}, "make": {"poultice": 1}, "arms": 1,
                 "text": "Glowmoss mashed and bound into cloth. It works over hours instead of "
                         "seconds, which is the only way anything out here actually heals."},
    "flare": {"need": {"resin": 2, "charcoal": 1}, "make": {"flare": 1}, "arms": 1,
              "intel": 22.0,
              "text": "Resin packed around charcoal until it will go up all at once. It is not "
                      "light for seeing by. It is light for being seen by, or for making "
                      "something else look away."},
    "blade": {"need": {"shard": 2, "branch": 1, "cord": 2, "resin": 1},
              "make": {"blade": 1}, "arms": 2,
              "text": "You split the haft, seat the longest shard you have in the split, and bind it down until the binding is harder than the haft."},
    "hook": {"need": {"scrap": 2, "cord": 1}, "make": {"hook": 1}, "arms": 2,
             "text": "You bend plate back on itself, grind the end to a point, and wrap the grip so it does not take your own pads off."},
    "sling": {"need": {"cord": 2, "hide": 1}, "make": {"sling": 1}, "arms": 2,
              "text": "Two lengths of cord and a pouch of hide. It is the only thing you can make that reaches something without you reaching it."},
    "plate": {"need": {"scrap": 3, "cord": 2, "cloth": 1}, "make": {"plate": 1},
              "arms": 2,
              "text": "You beat scrap flat, pad the back of it, and strap the whole thing along the forearm. It is heavy and it is in the way and it is worth it."},
    "burn": {"need": {"marrow": 1, "glowmoss": 2}, "make": {"burn": 2}, "arms": 1,
             "text": "You cook marrow down into crushed moss until it goes thin and will not settle. Two doses. Neither of them is free."},
    "blocker": {"need": {"glowmoss": 3, "resin": 1}, "make": {"blocker": 1},
                "arms": 1,
                "text": "Moss worked into resin until it stops smelling of moss. It is not medicine. It is a way of not being told."},
    "clot": {"need": {"charcoal": 1, "resin": 2}, "make": {"clot": 2}, "arms": 1,
             "text": "You char resin down to a black paste that sets the moment it touches anything warm."},
    "damper": {"need": {"glowmoss": 1, "charcoal": 1, "water": 2}, "make": {"damper": 2},
               "arms": 1,
               "text": "Moss and char steeped until the water goes dark. It tastes like the flats smell and it works."},
    "cutters": {"need": {"scrap": 2, "shard": 2, "cord": 1}, "make": {"cutters": 1},
                "arms": 2,
                "text": "You put two plates back to back, grind an edge into both, and pin them through the middle so they close on each other. It is a jaw. It is the first thing this body has ever made that was meant to take something apart."},
    "pry bar": {"need": {"scrap": 3, "cord": 1}, "make": {"pry bar": 1}, "arms": 2,
                "text": "You fold plate over on itself until it stops bending, and flatten one end by beating it against the other."},
    "lagging": {"need": {"hide": 2, "resin": 2, "cord": 2}, "make": {"lagging": 1},
                "arms": 2,
                "text": "You build up hide and resin in layers and bind the whole lot around both feet until nothing is touching the floor but the lagging."},
    "grapple": {"need": {"shard": 1, "cord": 3}, "make": {"grapple": 1}, "arms": 2,
                "intel": 24.0,
                "text": "A shard bent to a hook and a long cord onto it. Somewhere above you "
                        "stops being somewhere you cannot get to."},
    "sled": {"need": {"hide": 2, "cord": 3, "branch": 2}, "make": {"sled": 1}, "arms": 2,
             "intel": 18.0,
             "text": "A frame with hide stretched over it and a cord to pull. It carries a "
                     "great deal. It also has to be dragged, every step, by something that was "
                     "already tired."},
    "lamp": {"need": {"scrap": 2, "resin": 2, "glowmoss": 2}, "make": {"lamp": 1}, "arms": 2,
             "intel": 32.0,
             "text": "Glowmoss sealed in resin behind bent scrap. It does not burn, it does not "
                     "go out, and it does not need anything from you again."},
    "condenser": {"need": {"scrap": 2, "cloth": 2, "resin": 1}, "make": {"condenser": 1},
                  "arms": 2, "intel": 34.0,
                  "text": "Scrap folded so the cold side faces up and the cloth catches what "
                          "runs off it. On a world with no water in the air it still finds "
                          "some, slowly, which is most of what slowly is worth."},
    "antisepsis": {"need": {"glowmoss": 3, "charcoal": 2, "resin": 1},
                   "make": {"antisepsis": 1}, "arms": 2, "intel": 40.0,
                   "text": "You cook glowmoss down through charcoal and bind what is left in "
                           "resin. It is cruder than the tubes you find and it does the same "
                           "job to an infection."},
    "coagulant": {"need": {"hide": 1, "resin": 2, "charcoal": 1}, "make": {"coagulant": 1},
                  "arms": 2, "intel": 34.0,
                  "text": "Rendered down out of hide and set in resin. Pressed into a wound it "
                          "shuts it, which dressing alone will not always do."},
    "bag": {"need": {"hide": 2, "cord": 2}, "make": {"bag": 1}, "arms": 2, "intel": 26.0,
            "region": "bags",
            "text": "You cut, fold and lash hide into something with an inside. It hangs off "
                    "the shoulder and it takes the weight off your hands."},
}


# Things that do their work by being in the pack, with no command to spend. Kept as one table
# so the body can ask a single question instead of the body knowing about kit.
WORN = {
    "coat":  {"warmth": 9.0,  "note": "the coat is holding the core"},
    "boots": {"leg_soak": 0.30, "note": "the ground is not taking its usual toll"},
    "mask":  {"infection": 0.55, "note": "it is breathing through charcoal"},
    "brace": {"strain": 0.82, "note": "the brace is taking the load"},
    "sled":  {"carry": 9, "step": 0.88, "note": "the sled holds a great deal and drags"},
    "grapple": {"note": "a hook and a long cord, for the ways up"},
    "condenser": {"water_per_hour": 0.055, "note": "the condenser is working on the air"},
    "lamp":  {"note": "the lamp does not need feeding"},
    "club":  {"note": "something heavy in its hand"},
    "blade": {"note": "a long edge on a haft, carried where it can be reached"},
    "hook":  {"note": "a point on a short handle"},
    "sling": {"note": "a sling, and something to put in it"},
    "plate": {"hit_soak": 0.18, "strain": 1.06,
              "note": "plate strapped along one arm, taking what the arm would"},
    "line gun": {"note": "a trap carried the right way round"},
    "lagging": {"leg_soak": 0.22, "note": "nothing is reaching its feet"},
    "pry bar": {"note": "a lever, and it is heavy enough to be an argument"},
    "cutters": {"note": "it is carrying something that opens wire"},
}


# What it has to put between itself and whatever is coming, and how much good it does.
# Nothing in this game has a combat stat; a weapon is a multiplier on the odds a scene already
# had, and it is read through armed() so that a new one works everywhere the old ones did.
#
# The two at the top of the table cannot be made. They are taken off the two traps that can
# kill you outright, by disarming one instead of walking into it, which is the only place in
# the game where the ground hands you something worth more than what it costs.
WEAPONS = {
    "charge": 3.2,      # once, and then there is a hole where the thing was
    "line gun": 2.6,    # off a harpoon trap
    "blade": 1.9,
    "spear": 1.6,
    "hook": 1.3,
    "club": 1.0,
    "sling": 1.1,       # it does not win a fight. It stops one starting
}


def weapon(s):
    """(name, rating) of the best thing it is carrying, or (None, 0.0)."""
    best, val = None, 0.0
    for n, r in WEAPONS.items():
        if has(s, n) and r > val:
            best, val = n, r
    return best, val


def armed(s):
    """Is there anything in its hands at all? The gate every weapon option should use."""
    return weapon(s)[0] is not None


def weapon_edge(s):
    """0.0 unarmed, up to ~1.0 with the best thing in the game. Scales odds, never sets them."""
    return min(1.0, weapon(s)[1] / 3.2)


def worn(s, name):
    """Is this piece of kit in the pack and therefore doing its job?"""
    return s.inv.get(name, 0) > 0


def worn_num(s, key, default=1.0, add=False):
    """Combine every carried piece of kit that touches one number."""
    out = 0.0 if add else default
    for name, spec in WORN.items():
        if key in spec and s.inv.get(name, 0) > 0:
            if add:
                out += spec[key]
            else:
                out *= spec[key]
    return out


def has(s, name, n=1):
    return s.inv.get(name, 0) >= n


def give(s, name, n=1):
    s.inv[name] = s.inv.get(name, 0) + n
    return "%s x%d" % (name, n)


def take(s, name, n=1):
    if not has(s, name, n):
        return False
    s.inv[name] -= n
    if s.inv[name] <= 0:
        del s.inv[name]
    return True


def inv_line(s):
    from . import intel as IN
    if not s.inv:
        return "(nothing)"
    return ", ".join("%s x%d" % (IN.label(s, k), v) for k, v in sorted(s.inv.items()))


def gated(s, r):
    """Why this recipe is unavailable, or None. Region first, then understanding."""
    from . import intel as IN
    from . import regions as REG
    need_region = r.get("region")
    if need_region and not REG.flag(s, need_region):
        return "not here - nothing on the surface is built that way"
    if r.get("intel") and IN.level(s) < r["intel"]:
        return "you cannot picture how it goes together yet"
    for k in r["need"]:
        if k in MANUFACTURED and not IN.identified(s, k):
            return "you do not know what one of the parts is"
    return None


def craftable(s):
    out = []
    for name, r in RECIPES.items():
        if all(has(s, k, v) for k, v in r["need"].items()):
            if B.arms_usable(s) >= r["arms"] and not gated(s, r):
                out.append(name)
    return out


def craft(s, name):
    s.last_action_ok = False
    r = RECIPES.get(name)
    if not r:
        near = [k for k in RECIPES if k.startswith(name[:3])]
        return "You do not know how to make '%s'.%s" % (
            name, (" Did you mean %s?" % near[0]) if near else "")
    if B.arms_usable(s) < r["arms"]:
        return "That needs %d working arms. You have %d." % (r["arms"], B.arms_usable(s))
    why = gated(s, r)
    if why:
        return "You cannot make a %s: %s." % (name, why)
    missing = [("%s x%d" % (k, v - s.inv.get(k, 0)))
               for k, v in r["need"].items() if not has(s, k, v)]
    if missing:
        return "You are short: " + ", ".join(missing)
    for k, v in r["need"].items():
        take(s, k, v)
    made = []
    for k, v in r["make"].items():
        give(s, k, v)
        made.append("%s x%d" % (k, v))
    s.stats["crafted"] = s.stats.get("crafted", 0) + 1
    s.last_action_ok = True
    if name == "bag":
        take(s, "bag", 1)
        s.bags = int(getattr(s, "bags", 0) or 0) + 1
    if not s.has_flag("made_" + name):
        s.flag("made_" + name)
        from . import intel as IN
        gl = IN.gain(s, "craft")
        if gl:
            s.feedback.append(gl)
    B.tick(s, 22, exertion=1.1)
    return "%s You have %s." % (r["text"], ", ".join(made))


# ------------------------------------------------------------------ use
def _use_water(s):
    take(s, "water")
    s.pending_voice.append("drink")
    s.thirst = B.clamp(s.thirst - 45)
    return "You drink. It is flat and metallic and it is everything."


def _use_ration(s):
    take(s, "ration")
    s.pending_voice.append("eat")
    s.hunger = B.clamp(s.hunger - 55)
    s.thirst = B.clamp(s.thirst + 5)
    return "You eat the block in four bites and feel the room you woke in."


def _use_meat(s):
    take(s, "meat")
    s.pending_voice.append("eat")
    s.hunger = B.clamp(s.hunger - 60)
    if s.rng.random() < 0.34:
        s.infection = B.clamp(s.infection + 14)
        return "You eat it raw. Halfway down your gut starts to argue."
    return "You eat it raw and your body takes it without complaint."


def _use_salve(s):
    take(s, "salve")
    s.pending_voice.append("good")
    s.infection = B.clamp(s.infection - 38)
    s.pain = B.clamp(s.pain - 10)
    s.add_eff("salved", 300)
    return "You work salve into the wound. The heat backs off."


def _use_stim(s):
    take(s, "stim")
    s.fatigue = B.clamp(s.fatigue - 52)
    s.pain = B.clamp(s.pain - 22)
    s.strain = B.clamp(s.strain + 16)
    s.weird = B.clamp(s.weird + 9)
    s.add_eff("stimmed", 180)
    return ("The injector bites your thigh. Everything sharpens and something behind your eyes "
            "starts keeping a different kind of time.")


def _use_burn(s):
    take(s, "burn")
    s.pain = B.clamp(s.pain - 38)
    s.fatigue = B.clamp(s.fatigue - 18)
    s.add_eff("burning", 140)
    s.weird = B.clamp(s.weird + 4)
    return ("It goes in under the jaw and for about four seconds nothing happens. Then the "
            "whole body comes up - ears, shoulders, weight forward - and everything that was "
            "hurting stops reporting. It is not gone. It has been told to wait.")


def _use_blocker(s):
    take(s, "blocker")
    s.pain = B.clamp(s.pain - 52)
    s.add_eff("blocked", 220)
    return ("Everything below the neck goes quiet. It stands there testing the quiet, putting "
            "weight on the leg that should not take weight, and the leg does not object, "
            "because nothing is going to object to anything for a while.")


def _use_clot(s):
    take(s, "clot")
    stopped = []
    for n in B.LIMB_ORDER:
        if s.limbs[n]["bleed"] > 0:
            s.limbs[n]["bleed"] *= 0.15
            stopped.append(n)
    ch = getattr(s, "chest", None)
    if isinstance(ch, dict) and ch.get("bleed", 0.0) > 0:
        ch["bleed"] *= 0.45
        stopped.append("the chest")
    s.infection = B.clamp(s.infection + 9.0)
    s.pain = B.clamp(s.pain + 6.0)
    if not stopped:
        return "Nothing is leaking. You put it back."
    return ("The black paste goes into %s and sets hard almost at once, and the orange stops "
            "coming. It is not clean and it was never going to be - whatever was on it is "
            "sealed in there now with everything else." % ", ".join(stopped))


def _use_damper(s):
    take(s, "damper")
    s.snap = B.clamp(float(getattr(s, "snap", 0.0) or 0.0) - 26.0)
    s.mood = B.clamp(s.mood + 7.0)
    s.add_eff("damped", 200)
    s.fatigue = B.clamp(s.fatigue + 6.0)
    return ("It drinks it without being asked twice. Whatever was standing up in it sits back "
            "down - not gone, sitting - and its shoulders come off its ears for the first "
            "time in a while.")


def _use_cell(s):
    take(s, "cell")
    s.chip = B.clamp(min(100.0, s.chip + 26.0))
    s.weird = B.clamp(s.weird - 8.0)
    return ("You have it hold the cell against the seating at the back of its own skull, which "
            "it does without any sign of thinking the request is strange, and the link comes "
            "up out of the noise like something surfacing. The cell goes cold in its hand.")


def _use_charge(s):
    take(s, "charge")
    s.add_eff("charge_set", 300)
    B.tick(s, 30, exertion=1.1)
    return ("It sets the thing down in the middle of the ground you have just crossed, on the "
            "line anything following you would take, and scrapes dust over the top of it with "
            "the side of one foot. Then it walks away from it without looking back, which it "
            "has clearly done before.")


def _use_torch(s):
    if not s.eff("fire"):
        s.add_eff("fire", 150)
        return "You light the torch. The dark stands off, and your hands stop shaking."
    return "Your torch is already burning."


def _use_tag(s):
    s.learn("You are HORIZON/07, and 07 means there were six before you.")
    return ("You turn the plate over and over. HORIZON/07. SUBJECT. VIABLE. "
            "The word SUBJECT sits in you badly.")


def _use_map(s):
    s.learn("The world has a printed edge, and the edge has no name on it.")
    return ("The survey print shows the flats, the woods, the sink, the ridge - and then a hard "
            "line ruled across the far side with nothing written past it.")


# ---------------------------------------------------------------- manufactured medicine
# These are the ones intelligence gates. Using one you cannot name still works - it is just
# that nobody tells you what you did, and a third of the time you do it wrong.
def _worst_limb(s, states):
    best, worst = None, -1.0
    for n, L in s.limbs.items():
        if L["state"] in states:
            score = 100.0 - L["hp"] + (L["bleed"] * 400.0)
            if score > worst:
                best, worst = n, score
    return best


def _use_coagulant(s):
    take(s, "coagulant")
    hit = [n for n, L in s.limbs.items() if L["bleed"] > 0]
    if not hit:
        return "Nothing on you is leaking. Whatever that was, it is spent on the floor."
    for n in hit:
        s.limbs[n]["bleed"] = 0.0
        s.limbs[n]["bound"] = True
    s.pain = B.clamp(s.pain + 9)
    return ("It goes off against the wound with a heat that makes the whole limb jump, and the "
            "orange stops. All of it, everywhere, at once.")


def _use_antisepsis(s):
    take(s, "antisepsis")
    if s.infection <= 1:
        return "Nothing in you is hot. You have used it on a body that did not need it."
    s.infection = B.clamp(s.infection - 62)
    for L in s.limbs.values():
        L["hot"] = False
    from . import issues as ISS
    ISS.clear_kind(s, "fever")
    return ("You work the gel into everything that is open. It stings in a clean way, and the "
            "heat goes out of you over the next few minutes like a tide leaving.")


def _use_nerveblock(s):
    take(s, "nerveblock")
    limb = _worst_limb(s, ("gashed", "broken", "mangled"))
    if not limb:
        s.pain = B.clamp(s.pain - 30)
        return "You put it into the thigh for want of anywhere better. The edges come off things."
    s.pain = B.clamp(s.pain - 44)
    s.add_eff("blocked_" + limb.replace(" ", "_"), 420)
    s.limbs[limb]["numb"] = True
    from . import issues as ISS
    ISS.clear_kind(s, "dead nerve")
    return ("You put the needle in beside the %s and the pain goes out of it completely. So "
            "does the feedback. It will carry weight and it will not tell you when it is "
            "failing." % limb)


def _use_marrow(s):
    take(s, "marrow")
    limb = _worst_limb(s, ("broken", "mangled"))
    if not limb:
        return "Nothing in you is broken badly enough for this to have anywhere to go."
    L = s.limbs[limb]
    L["state"] = "gashed" if L["state"] == "broken" else "broken"
    L["hp"] = max(L["hp"], 46.0)
    s.pain = B.clamp(s.pain + 14)
    from . import issues as ISS
    ISS.clear_kind(s, "bone shard")
    return ("You open the %s and pack the graft in against the break. It is the worst thing you "
            "have made it do. Over the next hour the limb starts arguing less." % limb)


def _use_stabiliser(s):
    take(s, "stabiliser")
    s.weird = B.clamp(s.weird - 46)
    from . import issues as ISS
    cleared = ISS.clear_kind(s, "unravelling") or ISS.clear_kind(s, "denial")
    extra = " Something that was coming apart settles back into its own shape." if cleared else ""
    return ("The cylinder empties into the shoulder over a slow count. The wrongness backs off "
            "like a held breath let out.%s" % extra)


def _use_lamp(s):
    s.add_eff("fire", 600)
    return ("You get the lamp out and the dark backs off a long way. It does not need feeding "
            "and it will not go out, which is the first thing out here that is simply true.")


def _use_tinder(s):
    s.add_eff("fire", 260)
    s.warmth = B.clamp(s.warmth + 6)
    return ("The resin-soaked cloth takes at once and keeps taking. There is a fire now, and "
            "it did not cost an hour of trying to make one.")


def _use_poultice(s):
    s.add_eff("salved", 420)
    s.infection = B.clamp(s.infection - 26)
    s.pain = B.clamp(s.pain - 6)
    B.tick(s, 20)
    return ("You bind the poultice over the worst of it. It does not do anything you can see. "
            "In four hours the heat will be out of the wound, which is how this is supposed "
            "to work.")


def _use_flare(s):
    s.add_eff("fire", 40)
    dropped = []
    for tm in list(s.timers):
        if tm["id"] in ("stalker", "recall", "pack"):
            s.timers.remove(tm)
            dropped.append(tm.get("label", tm["id"]))
    if dropped:
        return ("The flare goes up white and far too loud. Whatever was working its way "
                "toward you decides against it: %s." % ", ".join(dropped))
    return ("The flare goes up and burns out, white on nothing. Everything out here that was "
            "going to look now knows exactly where you are.")


def _use_snare(s):
    s.add_eff("snared", 300)
    return ("You set the snare in a run something has been using and back off. It will either "
            "be holding something in a few hours or it will not.")


def _use_condenser(s):
    give(s, "water", 1)
    B.tick(s, 45)
    return ("You leave the condenser out and wait on it. It gives up one swallow, eventually, "
            "which is one more than the air had in it.")


def _use_grapple(s):
    return ("The grapple is not something you use on its own - it is what makes a climb "
            "possible when the ground says no. Keep it on you.")


def _use_fungus(s):
    s.hunger = B.clamp(s.hunger - 16)
    s.thirst = B.clamp(s.thirst - 8)
    if s.rng.random() < 0.22:
        s.infection = B.clamp(s.infection + 7)
        return ("It eats the grey stuff off the flats. It holds water, which is the only good "
                "thing about it, and something in it disagrees with the body afterwards.")
    return ("It eats the grey stuff off the flats. Not food exactly - but it is wet, and it "
            "stops the stomach complaining for a while.")


USE = {
    "water": _use_water,
    "ration": _use_ration,
    "meat": _use_meat,
    "salve": _use_salve,
    "stim": _use_stim,
    "torch": _use_torch,
    "lamp": _use_lamp,
    "burn": _use_burn,
    "blocker": _use_blocker,
    "clot": _use_clot,
    "damper": _use_damper,
    "cell": _use_cell,
    "charge": _use_charge,
    "tinder": _use_tinder,
    "poultice": _use_poultice,
    "flare": _use_flare,
    "snare": _use_snare,
    "condenser": _use_condenser,
    "grapple": _use_grapple,
    "dust fungus": _use_fungus,
    "tag": _use_tag,
    "map scrap": _use_map,
    "coagulant": _use_coagulant,
    "antisepsis": _use_antisepsis,
    "nerveblock": _use_nerveblock,
    "marrow": _use_marrow,
    "stabiliser": _use_stabiliser,
}


FOODS = ("meat", "ration", "root", "berry", "berries", "fish", "bug", "grub", "jerky")


def _rationing(s, name):
    """If it agreed to go easy on the stores, it goes easy on the stores - including when the
    order to eat comes from you. It is keeping your agreement, not disobeying you."""
    from . import persuade as P
    topic = ("eat" if name in FOODS else "drink" if name == "water" else None)
    if not topic or not P.honours(s, topic, "stop"):
        return None
    need = s.hunger if topic == "eat" else s.thirst
    if need >= 50:
        return None
    P.heed(s, topic)
    r = (s.requests or {}).get(topic) or {}
    why = ("  You said: %s" % r["reason"]) if r.get("reason") else ""
    return ("It puts the %s back. It agreed with you to %s and it is not hungry or thirsty "
            "enough yet to break that.%s" % (name, r.get("label", "go easy"), why))


MISUSE = {
    "coagulant": ("It goes off in the wrong place, against skin that was not open. The heat of "
                  "it takes a patch of you with it.", "burn"),
    "antisepsis": ("You get it in your mouth instead of in the wound. It is not for that, and "
                   "your gut spends the next hour explaining so.", "gut"),
    "nerveblock": ("The needle goes somewhere it should not and the whole side of it stops "
                   "answering for a while, including the parts that were holding it up.", "numb"),
    "marrow": ("You pack the graft into a wound that is not the kind of wound it is for. It "
               "sets. It sets wrong.", "bone"),
    "stabiliser": ("You empty the cylinder into it at the wrong rate and something in it "
                   "objects to the entire procedure.", "shock"),
    "stim": ("You put the whole injector in at once. Everything happens, all of it now.", "stim"),
}


def _misuse(s, name):
    """Returns a text if the guess went wrong, else None."""
    from . import intel as IN
    if name not in MANUFACTURED or IN.identified(s, name):
        return None
    if s.rng.random() >= 0.35:
        return None
    take(s, name)
    text, kind = MISUSE.get(name, ("It does nothing you can identify.", "none"))
    if kind == "burn":
        limb = s.rng.choice(["left arm", "right arm", "left leg", "right leg"])
        B.hurt(s, limb, s.rng.uniform(10, 20), "burn")
    elif kind == "gut":
        s.infection = B.clamp(s.infection + 12)
        s.hunger = B.clamp(s.hunger + 14)
    elif kind == "numb":
        s.strain = B.clamp(s.strain + 20)
        s.fatigue = B.clamp(s.fatigue + 16)
    elif kind == "bone":
        limb = s.rng.choice(["left leg", "right leg"])
        B.hurt(s, limb, s.rng.uniform(14, 24), "blunt")
        s.pain = B.clamp(s.pain + 16)
    elif kind == "shock":
        s.weird = B.clamp(s.weird + 14)
        s.blood = B.clamp(s.blood - 8)
    elif kind == "stim":
        s.strain = B.clamp(s.strain + 30)
        s.weird = B.clamp(s.weird + 12)
        s.fatigue = B.clamp(s.fatigue - 20)
    B.tick(s, 8)
    return ("YOU GUESSED WRONG. " + text +
            "\n  You still do not know what it was. Raising what the chip understands is the "
            "only way to stop this being a coin toss.")


def use(s, name):
    if not has(s, name):
        return "You have no %s." % name
    held = _rationing(s, name)
    if held:
        return held
    wrong = _misuse(s, name)
    if wrong:
        return wrong
    fn = USE.get(name)
    if fn:
        out = fn(s)
        B.tick(s, 4, exertion=0.6)
        return out
    if name == "bandage":
        return "Bandages are applied to a limb: try 'tend <limb>'."
    if name == "splint":
        return "A splint is applied to a limb: try 'tend <limb>'."
    if name == "strut":
        return "A strut is grafted where a limb is gone: try 'graft <limb>'."
    if name == "waterskin":
        if take(s, "waterskin"):
            give(s, "water", 3)
            return "You unstopper the skin: three swallows."
        return "Nothing in it."
    return "You turn the %s over in your hand. %s" % (name, CATALOG.get(name, ""))


def tend(s, limb):
    """Best available first aid on one limb."""
    L = s.limbs[limb]
    if L["state"] == "intact":
        return "Your %s is fine." % limb
    if B.arms_usable(s) == 0:
        return "You cannot tend anything without a working arm."
    out = []
    if L["state"] == "broken" and has(s, "splint"):
        take(s, "splint")
        L["hp"] = B.clamp(L["hp"] + 26)
        L["state"] = "gashed" if L["bleed"] > 0 else "bruised"
        out.append("You splint your %s until it will take weight again." % limb)
    if L["bleed"] > 0 or (L["state"] in B.OPEN_WOUNDS and not L["bound"]):
        if has(s, "bandage"):
            take(s, "bandage")
            out.append(B.bind(s, limb, 1.0))
        elif has(s, "cloth"):
            take(s, "cloth")
            out.append(B.bind(s, limb, 0.6))
        else:
            out.append("You press your palm to it. Nothing to bind with." )
            s.pain = B.clamp(s.pain - 2)
    if has(s, "salve") and s.infection > 12:
        out.append(_use_salve(s))
    B.tick(s, 12, exertion=0.7)
    if out:
        return " ".join(out)
    if L["bleed"] == 0 and L["state"] in ("gashed", "bruised", "mangled"):
        return ("Your %s has already stopped bleeding and is closing by itself, far faster than "
                "it should. There is nothing left to do but let it." % limb)
    return "You do what you can for your %s, which is not much." % limb
