"""The scenario bank.

Every scene is data plus small effect functions. Which scenes can fire, and which options
inside them are even offered, both depend on the body's current condition.
"""
from . import body as B
from . import escape as ESC
from . import items as I
from . import world as W


def _route_known(s):
    return W.zone(s)["key"] in (s.escape.get("known") or [])


def _route_desc(s):
    return ESC.ROUTES.get(W.zone(s)["key"], "A way out that is not forward.")


def O(label, eff, req=None):
    return {"label": label, "eff": eff, "req": req}


def SC(sid, text, opts, zones=None, w=10, once=False, req=None, danger=0.0, urgent=False):
    return {"id": sid, "text": text, "opts": opts, "zones": zones, "w": w,
            "once": once, "req": req, "danger": danger, "urgent": urgent}


def _t(s, x):
    return x(s) if callable(x) else x


# ============================================================ urgent (condition) scenes
def _e_press(s):
    limb = _worst_bleeder(s)
    if limb is None:
        return "The bleeding has already stopped."
    return I.tend(s, limb)


def _worst_bleeder(s):
    best, val = None, 0.0
    for n, L in s.limbs.items():
        r = L["bleed"] * (0.22 if L["bound"] else 1.0)
        if r > val:
            best, val = n, r
    return best


def _e_cauterise(s):
    limb = _worst_bleeder(s)
    if limb is None:
        return "Nothing left to close."
    s.limbs[limb]["bleed"] = 0.0
    s.limbs[limb]["bound"] = True
    B.hurt(s, limb, 12, "burn")
    B.tick(s, 20, exertion=1.4)
    return ("You hold the hot edge against your %s until the orange stops and the smell arrives. "
            "You do not make a sound, which surprises you." % limb)


def _e_ignore_bleed(s):
    B.tick(s, 25, exertion=1.0)
    return "You decide it can wait. The orange disagrees, quietly, all the way down your leg."


def _e_drink_anything(s):
    if I.has(s, "water"):
        return I.use(s, "water")
    if I.has(s, "filter"):
        s.thirst = B.clamp(s.thirst - 40)
        B.tick(s, 30, exertion=0.8)
        return "You wring standing water through the filter and drink what comes out."
    s.thirst = B.clamp(s.thirst - 28)
    s.infection = B.clamp(s.infection + 11)
    B.tick(s, 25, exertion=0.9)
    return "You drink from a hoofprint. It is wet. That is all you can say for it."


def _e_sit_down(s):
    B.tick(s, 70, resting=True, cold=W.cold(s))
    return "You sit down where you are and let your ribs stop arguing for a while."


def _e_amputate(s):
    limb = _worst_rot(s)
    if limb is None:
        return "Nothing needs taking."
    B.sever(s, limb)
    s.limbs[limb]["bleed"] *= 0.4
    s.limbs[limb]["bound"] = True
    s.infection = B.clamp(s.infection - 55)
    s.pain = B.clamp(s.pain + 30)
    I.take(s, "shard")
    B.tick(s, 60, exertion=1.6)
    s.learn("You heal wrong and fast, and you can survive things that should end you.")
    return ("You take your %s off yourself with the shard and close it with heat. "
            "By the time you are finished the stump is already knitting, far too quickly, "
            "and that frightens you more than the cutting did." % limb)


def _worst_rot(s):
    worst, val = None, 0
    order = ["lost", "mangled", "gashed"]
    for n, L in s.limbs.items():
        if L["state"] in order:
            v = 3 - order.index(L["state"])
            if v > val:
                worst, val = n, v
    return worst


def _e_ride_it_out(s):
    s.weird = B.clamp(s.weird - 14)
    s.strain = B.clamp(s.strain + 9)
    B.tick(s, 45, resting=True)
    return ("You put your back to something solid and name things out loud until they stay named. "
            "Ground. Hand. Ground. Hand. It passes.")


def _e_lean_in(s):
    s.weird = B.clamp(s.weird + 12)
    got = s.learn("Something is watching through your eyes, and it can be looked back at.")
    B.tick(s, 25)
    return ("You stop resisting it. For a moment you are above yourself, looking down at a "
            "furred thing with two lit orange points where its eyes should be, walking a line "
            "somebody drew." + (" You keep that." if got else ""))


URGENT = [
    SC("bleeding_bad",
       lambda s: ("Orange is coming out of you faster than you can replace it. It is bright "
                  "enough to read by and it is leaving a trail anything could follow."),
       [O("Bind it with what you have", _e_press),
        O("Burn it shut", _e_cauterise, lambda s: s.eff("fire") or I.has(s, "torch")),
        O("Keep moving and hope", _e_ignore_bleed)],
       req=lambda s: B.bleed_rate(s) > 0.12 and s.blood < 72, w=100, urgent=True, danger=0.5),

    SC("thirst_crisis",
       "Your mouth has gone to paper. Swallowing is a decision now, not a reflex.",
       [O("Drink whatever is nearest", _e_drink_anything),
        O("Ration it and push on", lambda s: (B.tick(s, 30, exertion=1.2),
                                              "You hold out. Your pulse ticks in your ears.")[1])],
       req=lambda s: s.thirst > 82, w=90, urgent=True),

    SC("strain_wall",
       "Every joint you own is filing a complaint at once. Your legs are borrowing against "
       "something you do not have.",
       [O("Sit down and stop", _e_sit_down),
        O("Use a stim", lambda s: I.use(s, "stim"), lambda s: I.has(s, "stim")),
        O("Walk through it", lambda s: (B.tick(s, 40, exertion=1.6),
                                        "You keep walking. Something in your hip goes quiet in a "
                                        "way that is not good news.")[1])],
       req=lambda s: s.strain > 84, w=80, urgent=True),

    SC("rot",
       lambda s: ("The wound is hot and the skin around it has gone the colour of a bad sunset. "
                  "The smell is sweet. You know, without being taught, what sweet means."),
       [O("Salve it", lambda s: I.use(s, "salve"), lambda s: I.has(s, "salve")),
        O("Cut the limb off", _e_amputate,
          lambda s: I.has(s, "shard") and (s.eff("fire") or I.has(s, "torch"))
          and B.arms_usable(s) >= 1),
        O("Bind it tighter and keep going",
          lambda s: I.tend(s, _worst_rot(s) or "tail"))],
       req=lambda s: s.infection > 52, w=95, urgent=True),

    SC("wrongness",
       "The world loses a frame. Your own hand arrives somewhere before you send it. "
       "There is a sound underneath the sound.",
       [O("Ground yourself", _e_ride_it_out),
        O("Let it happen and watch", _e_lean_in)],
       req=lambda s: s.weird > 62, w=95, urgent=True),

    SC("too_tired",
       "You have been putting one foot in front of the other for so long that the feet have "
       "started doing it without you. You lost the last hundred steps entirely.",
       [O("Make camp and sleep", lambda s: W.camp(s, 6.5)),
        O("Sleep rough right here", lambda s: W.camp(s, 4.0)),
        O("Use a stim", lambda s: I.use(s, "stim"), lambda s: I.has(s, "stim"))],
       req=lambda s: s.fatigue > 86, w=85, urgent=True),
]


# ============================================================ zone scenes
def _mirror(s):
    s.learn("Your eyes make their own light, and your blood is the same colour as the light.")
    B.tick(s, 10)
    return ("You lean in until your nose touches cold glass. Fur, grey and matted. A muzzle. "
            "Two eyes putting out a steady orange glow that does not come from the room. "
            "You bleed that colour too. You do not know which fact is worse.")


def _tank(s):
    s.learn("You were grown or kept in a tank, and the tank has your number on it.")
    I.give(s, "tag")
    B.tick(s, 14)
    return ("The tank is cracked from the inside. There is a plate bolted to the frame: "
            "HORIZON/07 - SUBJECT - VIABLE. You pull the plate free and keep it.")


def _handler(s):
    I.give(s, "keycard")
    I.give(s, "ration", 2)
    B.tick(s, 18)
    return ("The handler has been dead long enough to be quiet about it. You take the card off "
            "the body and two ration blocks out of the coat. The hand is small. "
            "Yours is not shaped like that at all.")


def _door(s):
    if I.has(s, "keycard"):
        s.distance += 1.4
        B.tick(s, 10)
        return "The card wakes the panel and the door walks itself open. You step through."
    if B.arms_usable(s) >= 2:
        B.hurt(s, "left arm", 10, "cut")
        B.tick(s, 45, exertion=1.5)
        s.distance += 1.0
        return "You lever the door with scrap until it gives, and pay for it with your left arm."
    B.tick(s, 30, exertion=1.2)
    return "You cannot shift it. You go the long way round, through the vents."


def _wire_crawl(s):
    if s.rng.random() < 0.55:
        B.hurt(s, s.rng.choice(["left leg", "right leg", "tail"]), s.rng.uniform(14, 26), "cut")
        s.distance += 1.2
        B.tick(s, 30, exertion=1.4)
        return "You go under the wire on your belly. It takes a strip off you on the way through."
    s.distance += 1.4
    B.tick(s, 25, exertion=1.2)
    return "You find a dug-out hollow under the wire and go through clean. Something dug it. Not you."


def _pylon(s):
    s.add_eff("static", 120)
    s.weird = B.clamp(s.weird + 7)
    I.give(s, "cord", 2)
    B.tick(s, 30, exertion=1.1)
    return ("You strip cable off the pylon base. The hum climbs into your teeth and stays there, "
            "saying something with no words in it.")


def _drone(s):
    if s.eff("hidden") or I.has(s, "charcoal"):
        I.take(s, "charcoal")
        s.add_eff("hidden", 150)
        B.tick(s, 35, exertion=0.9)
        return ("You rub charcoal over your face until your eyes stop shining through it, and lie "
                "still. The drone passes close enough to move your fur, and goes on.")
    B.hurt(s, s.rng.choice(["left arm", "right arm", "right leg"]), s.rng.uniform(16, 30), "burn")
    B.tick(s, 20, exertion=1.5)
    return ("The drone finds the glow of your eyes in open ground and puts a line of heat across "
            "you before you are under cover.")


def _subject11(s):
    s.learn("You are not the only one they made, and the others did not get this far.")
    I.give(s, "map scrap")
    I.give(s, "cloth", 2)
    B.tick(s, 22)
    return ("There is a body in the grass wearing fur like yours. The plate on its collar says "
            "HORIZON/11. Its eyes are open and dark - whatever lit them has gone out. "
            "You take the map scrap out of its hand. It let you.")


def _ash_cough(s):
    s.strain = B.clamp(s.strain + 12)
    s.thirst = B.clamp(s.thirst + 10)
    B.tick(s, 40, exertion=1.3)
    return "You cross open flats and cough grey for an hour afterwards."


def _ash_crate(s):
    I.give(s, "ration", 2)
    I.give(s, "water", 2)
    if s.rng.random() < 0.4:
        I.give(s, "stim")
    B.tick(s, 30, exertion=1.2)
    return "You dig out a supply crate half-buried in ash. Rations, water, and luck."


def _storm(s):
    if s.eff("sheltered"):
        B.tick(s, 90, resting=True)
        return "The ash storm arrives and breaks over your shelter without finding you."
    B.hurt(s, "left ear", s.rng.uniform(8, 14), "cut")
    s.thirst = B.clamp(s.thirst + 14)
    s.strain = B.clamp(s.strain + 14)
    B.tick(s, 80, exertion=1.4)
    return ("The storm comes across the flats in a wall. You lie down facing away and let it "
            "sand the edges off you.")


def _take_route(s):
    line = ESC.find_route(s)
    B.tick(s, 25, exertion=1.1)
    return line or "You already knew about this one."


def _ignore_route(s):
    s.mood = B.clamp(s.mood - 3)
    B.tick(s, 12, exertion=0.9)
    return ("You log it and walk past. The line you were given runs the other way, and the "
            "chip is what decides which way you go.")


def _dry_wash(s):
    n = 2 + (1 if I.has(s, "filter") else 0)
    if B.arms_usable(s) == 0:
        B.tick(s, 20, exertion=1.0)
        return "There is water under the wash and no way to dig for it."
    I.give(s, "water", n)
    B.tick(s, 55, exertion=1.35)
    return ("You dig where the ash goes darker and hit damp at arm's depth. It comes up grey and "
            "gritty and you get %d swallows out of it.%s"
            % (n, " The filter earns its keep." if I.has(s, "filter") else ""))


def _mirage(s):
    s.weird = B.clamp(s.weird + 10)
    B.tick(s, 35, exertion=1.2)
    return ("The Holding is there on the horizon again, lit up, doors open, exactly as you left "
            "it - in the direction you have been walking away from all day.")


def _longone(s):
    s.stats["fights"] = s.stats.get("fights", 0) + 1
    name, rating = I.weapon(s)
    edge = I.weapon_edge(s)
    if s.eff("burning"):
        edge = min(1.0, edge + 0.18)
    if name == "charge":
        I.take(s, "charge")
        I.give(s, "meat", 3)
        I.give(s, "hide", 2)
        B.tick(s, 35, exertion=1.4)
        return ("It does not wait for it to come in. It puts the charge down in the gap "
                "between them, backs off four paces, and the long one arrives on top of it. "
                "There is a great deal of meat afterwards and most of it is still worth "
                "taking.")
    if name:
        win = 0.46 + 0.42 * edge
        if s.rng.random() < win:
            I.give(s, "meat", 2)
            I.give(s, "hide")
            B.tick(s, 30, exertion=1.7)
            if name == "line gun":
                return ("It comes in low and fast and the line takes it through the shoulder "
                        "at eight paces and puts it into the ground still running. It takes a "
                        "long time to stop. You wind the coil back on while it does.")
            if name == "sling":
                return ("It is still working out how to come in when the stone arrives. It "
                        "goes down on its front end, gets up wrong, and decides against the "
                        "whole business - and bleeds out four hundred paces away where you "
                        "find it later.")
            return ("It comes in low and it goes onto the %s on the way. It dies badly and "
                    "for a long time. You take meat and hide off it." % name)
        limb = s.rng.choice(["left arm", "right arm", "tail"])
        B.hurt(s, limb, s.rng.uniform(16, 32), "bite")
        B.tick(s, 25, exertion=1.8)
        return ("The %s turns on bone. It gets the %s in its mouth before the two of you get "
                "it off." % (name, limb))
    limb = s.rng.choice(["left arm", "right arm", "right leg", "tail"])
    if s.rng.random() < 0.28:
        B.sever(s, limb)
        B.tick(s, 30, exertion=1.9)
        return ("Bare-handed against a long one. It takes the %s away with it into the trees "
                "and the body is alive, which is the only good thing there is to say about "
                "it." % limb)
    B.hurt(s, limb, s.rng.uniform(20, 34), "bite")
    B.tick(s, 28, exertion=1.8)
    return ("Bare-handed against a long one. It is off again before either of you has "
            "finished, and it takes a piece of the %s with it." % limb)

def _flee_longone(s):
    if B.can_run(s) and s.rng.random() < 0.7:
        s.distance += 1.0
        B.tick(s, 25, exertion=1.9)
        return "You run. It follows for a hundred metres and then decides you are not worth it."
    B.hurt(s, "right leg", s.rng.uniform(14, 26), "bite")
    B.tick(s, 25, exertion=1.9)
    return "You try to run on legs that will not do it, and it catches you from behind."


def _snare(s):
    if s.rng.random() < 0.5 and I.has(s, "shard"):
        I.take(s, "shard")
        B.hurt(s, "right leg", s.rng.uniform(10, 18), "cut")
        B.tick(s, 45, exertion=1.4)
        return "Cable snare, up to the hock. You cut yourself out of it and keep the leg."
    B.sever(s, "right leg")
    B.tick(s, 60, exertion=1.9)
    return ("The snare is cable and it does not care what you are. By the time you tear free "
            "your right leg is not coming with you.")


def _scrap_tree(s):
    I.give(s, "branch", 2)
    I.give(s, "resin", 2)
    if s.rng.random() < 0.4:
        I.give(s, "glowmoss", 2)
    B.tick(s, 35, exertion=1.2)
    return "You strip a scrap tree for branch and resin. Moss grows in the joints, glowing your colour."


def _ford(s):
    s.add_eff("wet", 240)
    s.warmth = B.clamp(s.warmth - 18)
    s.distance += 1.4
    B.tick(s, 45, exertion=1.5, cold=W.cold(s))
    return ("You wade the sink chest-deep. The cold closes on you like a hand and does not "
            "let go when you come out.")


def _long_way(s):
    B.tick(s, 110, exertion=1.2, cold=W.cold(s))
    return "You go the long way round the water and stay dry. It costs you most of a day's light."


def _leeches(s):
    n = s.rng.randint(2, 5)
    for _ in range(n):
        limb = s.rng.choice(list(s.limbs))
        s.limbs[limb]["bleed"] = max(s.limbs[limb]["bleed"], 0.05)
    s.blood = B.clamp(s.blood - 6)
    B.tick(s, 30, exertion=1.0, cold=W.cold(s))
    return ("Things have attached themselves to you under the water. You pull off %d of them and "
            "each one leaves a hole that will not close." % n)


def _sunken_truck(s):
    I.give(s, "scrap", 2)
    I.give(s, "cloth", 2)
    if s.rng.random() < 0.5:
        I.give(s, "ration", 1)
    s.add_eff("wet", 180)
    B.tick(s, 40, exertion=1.5, cold=W.cold(s))
    return "You dive the cab of a sunken truck and come up with an armful of usable material."


def _reflection(s):
    s.weird = B.clamp(s.weird + 13)
    B.tick(s, 30, exertion=1.1)
    return ("There is a you out on the glass, walking parallel, half a second late. When you "
            "stop, it takes one more step before it stops.")


def _talk_reflection(s):
    s.weird = B.clamp(s.weird + 8)
    got = s.learn("The world you are crossing is projected, and the projection has seams.")
    B.tick(s, 25)
    return ("You say the only word you are sure of out loud: seven. The reflection says it back "
            "half a second early, and behind it, for a moment, the sky has a grid in it."
            + (" You keep that." if got else ""))


def _glass_field(s):
    B.hurt(s, s.rng.choice(["left leg", "right leg"]), s.rng.uniform(10, 20), "cut")
    s.distance += 1.6
    B.tick(s, 40, exertion=1.5)
    return "You cross the glass field directly. It takes its toll on your pads and you make good time."


def _tower(s):
    s.add_eff("static", 200)
    s.weird = B.clamp(s.weird + 14)
    I.give(s, "scrap", 2)
    I.give(s, "cord", 2)
    B.tick(s, 40, exertion=1.3)
    return ("You climb into the tower's base and strip it. The static rides in on your spine and "
            "puts a memory in you that is not yours: a white room, a clipboard, and your own "
            "face on a monitor, younger, screaming.")


def _terminal(s):
    s.learn("You were made to be released and measured, and the horizon is the end of the test.")
    B.tick(s, 30)
    return ("The terminal still has power. SUBJECT HORIZON/07. OBJECTIVE: TRAVERSE. "
            "NOTES: subject exhibits self-repair, aggression suppression, and no recollection of "
            "origin - as designed. TERMINATION AT SHELF IF NON-VIABLE.")


def _subject03(s):
    s.learn("Another of you got further, and chose to stay rather than finish the walk.")
    I.give(s, "water", 2)
    I.give(s, "salve", 1)
    B.tick(s, 45)
    return ("There is something like you sitting against a tower with its legs out in front of it. "
            "HORIZON/03. It has been out here years. It says: they only watch the end. "
            "It gives you water and salve and will not stand up.")


def _03_warns(s):
    s.learn("Reaching the end is the point at which they decide what to do with you.")
    B.tick(s, 25)
    return ("03 says: you get to the line and they either open it or they close you. "
            "I decided not to find out. It looks at your legs. You have better legs than I had.")


def _ridge_climb(s):
    if B.can_climb(s):
        s.distance += 2.0
        B.tick(s, 50, exertion=1.7)
        return "You take the ridge face directly, hand over hand, and gain real ground."
    B.hurt(s, s.rng.choice(["left arm", "right arm"]), s.rng.uniform(16, 30), "fall")
    B.tick(s, 45, exertion=1.7)
    return "You try the face without the limbs for it and come off it partway up."


def _shelf_edge(s):
    s.flag("seam_seen")
    s.learn("You have seen the edge of the world from close enough to touch the seam.")
    B.tick(s, 25)
    return ("You lie on your belly at the lip and look over. There is no down. There is a "
            "surface, and the surface has a grid in it, and the grid is the sky continued at a "
            "right angle. The world is a room with a picture in it.")


def _last_handler(s):
    s.learn("They are still there at the end, waiting to see what you turned out to be.")
    B.tick(s, 30)
    return ("A figure in grey is standing where the ground stops, and it has been standing there "
            "for a long time. It does not move toward you. It has a clipboard. It is writing "
            "down what you do next.")


SCENES = [
    # ---- holding
    SC("mirror", "There is a black panel on the corridor wall with a person in it, moving when "
                 "you move.",
       [O("Look at yourself properly", _mirror),
        O("Walk past it", lambda s: (B.tick(s, 8), "You keep your face away from the glass.")[1])],
       zones=["holding"], once=True, w=40),
    SC("tank", "A tank stands open in the middle of the room, full of drained fluid, cracked "
               "outward from the inside.",
       [O("Read the plate on the frame", _tank),
        O("Leave it alone", lambda s: (B.tick(s, 6), "You do not want to know. You move on.")[1])],
       zones=["holding"], once=True, w=40),
    SC("handler", "Someone in a grey coat is face-down in the corridor, and has been for a while.",
       [O("Search the body", _handler),
        O("Step over it", lambda s: (B.tick(s, 5), "You step over the coat and keep walking.")[1])],
       zones=["holding"], once=True, w=35),
    SC("door", "A heavy door stands between you and the outside. There is a panel beside it.",
       [O("Open it", _door),
        O("Find another way", lambda s: (B.tick(s, 40, exertion=1.2),
                                         "You crawl the ducts instead and come out in daylight.")[1])],
       zones=["holding"], once=True, w=45),

    # ---- fence
    SC("wire", "The wire fence runs left and right further than you can see. There is a hollow "
               "worn under it.",
       [O("Crawl under", _wire_crawl),
        O("Climb it", lambda s: (B.hurt(s, "right arm", 18, "cut"),
                                 "You go over the top and it charges you for the privilege.")[1],
          lambda s: B.can_climb(s)),
        O("Follow it and look for a gate", lambda s: (B.tick(s, 70, exertion=1.2),
          "You walk the line for an hour and find a gate standing open. Nobody closed it.")[1])],
       zones=["fence"], w=30),
    SC("pylon", "A pylon stands with its base panel hanging off. There is cable inside.",
       [O("Strip the cable", _pylon),
        O("Keep clear of it", lambda s: (B.tick(s, 10), "You give the hum a wide berth.")[1])],
       zones=["fence", "ridge"], w=22),
    SC("drone", "Something is crossing the sky in a straight line, low, with a lens on the front.",
       [O("Hide and dull your eyes", _drone),
        O("Run for cover", lambda s: (B.tick(s, 20, exertion=1.7), s.distance,
           "You break for the treeline. It does not follow, this time.")[2],
          lambda s: B.can_run(s)),
        O("Stand still in the open", lambda s: (B.hurt(s, "right arm", 24, "burn"),
           "You hold still. Standing still is not the same as being hidden.")[1])],
       zones=["fence", "flats", "ridge"], w=26, danger=0.6),
    SC("subject11", "There is a shape in the dead grass with fur on it.",
       [O("Go and look", _subject11),
        O("Leave it", lambda s: (B.tick(s, 8), "You do not go and look.")[1])],
       zones=["fence"], once=True, w=38),

    # ---- flats
    SC("ashcross", "The flats open up with nothing standing on them for miles.",
       [O("Cross in the open", _ash_cough),
        O("Wait out the heat, then move", lambda s: (B.tick(s, 150, resting=True),
           "You lie in the lee of a rock until the heat drops off, then walk in the cool.")[1])],
       zones=["flats"], w=24),
    SC("crate", "There is a corner of something square sticking out of the ash.",
       [O("Dig it out", _ash_crate),
        O("Not worth the water", lambda s: (B.tick(s, 10), "You leave it buried.")[1])],
       zones=["flats"], once=True, w=34),
    SC("storm", "The horizon behind you has gone the colour of a bruise and it is coming this way.",
       [O("Build something and get under it", lambda s: (W.build_shelter(s), _storm(s))[1],
          lambda s: I.has(s, "branch", 2) or I.has(s, "hide")),
        O("Lie down and take it", _storm),
        O("Outrun it", lambda s: (B.tick(s, 50, exertion=1.9),
           "You run ahead of it for an hour. It arrives anyway, with interest.")[1],
          lambda s: B.can_run(s))],
       zones=["flats"], w=26, danger=0.5),
    SC("drywash", "A dry watercourse cuts across the flats. The ash in the bottom of it is a "
                  "darker grey than the ash everywhere else.",
       [O("Dig for water", _dry_wash),
        O("Walk the wash for shade instead", lambda s: (B.tick(s, 60, resting=True),
           "You follow the wash and use its bank for shade until the heat drops.")[1])],
       zones=["flats", "steppe"], w=34),
    SC("mirage", "There is a building on the horizon with its lights on.",
       [O("Walk toward it", _mirage),
        O("Ignore it and hold your line", lambda s: (B.tick(s, 20, exertion=1.2),
           "You keep your bearing. When you look again it is gone, or it was never lit.")[1])],
       zones=["flats", "steppe"], w=20),

    # ---- woods
    SC("longone", "Something long and low is moving between the scrap trees, and it has stopped "
                  "pretending you have not seen it.",
       [O("Fight it", _longone),
        O("Run", _flee_longone),
        O("Climb a tree", lambda s: (B.tick(s, 60, exertion=1.5),
           "You get up into the scrap canopy and wait it out. It circles for an hour, then goes.")[1],
          lambda s: B.can_climb(s))],
       zones=["woods", "sink"], w=32, danger=0.7),
    SC("snare", "Your foot is in something before you see it, and the something closes.",
       [O("Cut yourself out", _snare),
        O("Tear free", lambda s: (B.sever(s, "right leg"),
           "You pull against cable with everything you have. Cable wins.")[1])],
       zones=["woods"], once=True, w=22, danger=0.8),
    SC("scraptree", "A scrap tree has come down across the path, shedding branch and resin.",
       [O("Strip it", _scrap_tree),
        O("Step over and move on", lambda s: (B.tick(s, 8), "You climb over and keep going.")[1])],
       zones=["woods"], w=28),
    SC("nest", "There is a nest of something in the roots, and the something is not home.",
       [O("Take what is in it", lambda s: (I.give(s, "meat", 2), I.give(s, "hide"),
          B.tick(s, 25, exertion=1.1),
          "You rob the nest. Meat and a hide, and a bad feeling about being watched.")[3]),
        O("Leave it be", lambda s: (B.tick(s, 6), "You leave the nest alone.")[1])],
       zones=["woods"], w=18),

    # ---- sink
    SC("ford", "The water crosses your whole line of travel, dark and still and deeper in the middle.",
       [O("Wade it", _ford),
        O("Go around", _long_way),
        O("Raft across on scrap", lambda s: (I.take(s, "scrap", 2), s.__setattr__(
            "distance", s.distance + 1.6), B.tick(s, 60, exertion=1.3),
            "You lash scrap into something that floats badly and cross mostly dry.")[3],
          lambda s: I.has(s, "scrap", 2) and B.arms_usable(s) >= 2)],
       zones=["sink"], w=34),
    SC("leeches", "There is a weight on your legs under the water that was not there a moment ago.",
       [O("Pull them off now", _leeches),
        O("Get to dry land first", lambda s: (B.tick(s, 25, exertion=1.3), _leeches(s))[1])],
       zones=["sink"], w=24),
    SC("truck", "The roof of a vehicle breaks the surface out in the middle of the basin.",
       [O("Dive it", _sunken_truck, lambda s: B.arms_usable(s) >= 1),
        O("Leave it under", lambda s: (B.tick(s, 8), "You let it stay down there.")[1])],
       zones=["sink"], once=True, w=26),
    SC("mossbank", "A bank of glowmoss puts out the same orange as your eyes, in quantity.",
       [O("Harvest it", lambda s: (I.give(s, "glowmoss", 3), B.tick(s, 30, exertion=1.0),
          "You take armfuls of moss. It is warm, which moss should not be.")[2]),
        O("Sit in it a while", lambda s: (B.tick(s, 60, resting=True),
          s.__setattr__("weird", B.clamp(s.weird - 8)),
          "You sit in the moss and the colour of it and feel, briefly, unremarkable.")[2])],
       zones=["sink"], w=20),

    # ---- steppe
    SC("reflection", "You are not alone on the glass. There is another one of you out there, "
                     "keeping pace.",
       [O("Speak to it", _talk_reflection),
        O("Keep your eyes down and walk", _reflection)],
       zones=["steppe"], w=30),
    SC("glassfield", "The direct line runs across bare fused glass. The long way round is sand.",
       [O("Cross the glass", _glass_field),
        O("Take the sand", lambda s: (B.tick(s, 80, exertion=1.3),
           "You take the soft way round. Slower, and your feet stay whole.")[1])],
       zones=["steppe"], w=26),
    SC("spires", "Fused spires stand in a rough circle, and there is shade inside them.",
       [O("Shelter and rest", lambda s: (s.add_eff("sheltered", 400), B.tick(s, 90, resting=True),
          "You get in among the spires and sleep sitting up in shade.")[2]),
        O("Push on through the heat", lambda s: (B.tick(s, 45, exertion=1.5),
          "You keep going in the open. The glass throws the heat back up at you.")[1])],
       zones=["steppe"], w=20),

    # ---- ridge
    SC("tower", "One of the towers has a service hatch at the base, and the hum inside it is loud.",
       [O("Go in and strip it", _tower),
        O("Leave the towers alone", lambda s: (B.tick(s, 12), "You walk the ridge and let them talk.")[1])],
       zones=["ridge"], w=28),
    SC("terminal", "There is a shed at the foot of the ridge with a terminal in it, still lit.",
       [O("Read your file", _terminal),
        O("Smash it", lambda s: (s.__setattr__("weird", B.clamp(s.weird + 6)), B.tick(s, 15, exertion=1.3),
          "You put scrap through the screen. It does not make you feel better for long.")[2]),
        O("Walk away", lambda s: (B.tick(s, 8), "You leave the light on and go.")[1])],
       zones=["ridge"], once=True, w=40),
    SC("subject03", "Something is sitting against the base of the third tower, and it has fur.",
       [O("Approach it", _subject03),
        O("Ask what happens at the end", _03_warns, lambda s: s.has_flag("met03")),
        O("Go around it", lambda s: (B.tick(s, 10), "You give it a wide berth. It watches you go.")[1])],
       zones=["ridge"], once=True, w=42),
    SC("ridgeface", "The ridge stands up in front of you. There is a face to climb, or a gully to walk.",
       [O("Climb the face", _ridge_climb),
        O("Walk the gully", lambda s: (B.tick(s, 90, exertion=1.3),
           "You take the gully. It doubles back twice and eats your afternoon.")[1])],
       zones=["ridge"], w=24),

    # ---- ways out, one per zone, found rather than given
    SC("sideways",
       lambda s: ("Something here runs across your heading instead of along it.\n  %s\n"
                  "Nothing is guarding it. Nothing was ever expected to want it."
                  % _route_desc(s)),
       [O("Fix it in memory as a way out", _take_route),
        O("Note it and stay on the route", _ignore_route)],
       w=20, req=lambda s: not _route_known(s)),

    # ---- shelf
    SC("edge", "The ground ahead stops. Not a cliff - stops.",
       [O("Crawl to the lip and look", _shelf_edge),
        O("Stay back from it", lambda s: (B.tick(s, 12), "You keep your distance from the stopping place.")[1])],
       zones=["shelf"], once=True, w=60),
    SC("handler2", "There is a figure in grey standing where the world ends.",
       [O("Walk toward it", _last_handler),
        O("Circle wide and keep going", lambda s: (B.tick(s, 30, exertion=1.2),
           "You go the long way round it. It writes something down.")[1])],
       zones=["shelf"], once=True, w=50),
]

BY_ID = {sc["id"]: sc for sc in (SCENES + URGENT)}


# ============================================================ selection
def _allowed(s, sc):
    if sc["once"] and sc["id"] in s.seen:
        return False
    if sc["zones"] and W.zone(s)["key"] not in sc["zones"]:
        return False
    if sc["req"] and not sc["req"](s):
        return False
    return True


def build(s, sc):
    opts, idx = [], []
    for i, o in enumerate(sc["opts"]):
        if o["req"] and not o["req"](s):
            continue
        opts.append(o["label"])
        idx.append(i)
    if not opts:
        opts, idx = ["Endure it"], [0]
    return {"sid": sc["id"], "text": _t(s, sc["text"]), "opts": opts, "map": idx,
            "age": 0, "danger": sc["danger"]}


def chain(s, sid):
    sc = BY_ID.get(sid)
    if sc:
        s.scene = build(s, sc)
        if sc["once"] and sid not in s.seen:
            s.seen.append(sid)


URGENT_COOLDOWN = 7      # turns before the same condition nags again


def _cool(s, sid):
    if not hasattr(s, "cool") or s.cool is None:
        s.cool = {}
    return s.turn - s.cool.get(sid, -999) < URGENT_COOLDOWN


def pick(s, chance=0.35):
    """Choose the next scene, urgent conditions first. Returns scene dict or None."""
    for sc in URGENT:
        if _allowed(s, sc) and not _cool(s, sc["id"]) and s.rng.random() < 0.85:
            s.stats["scenes"] = s.stats.get("scenes", 0) + 1
            s.cool[sc["id"]] = s.turn
            if sc["once"]:
                s.seen.append(sc["id"])
            return build(s, sc)
    pool = [sc for sc in SCENES if _allowed(s, sc)]
    if not pool:
        return None
    if s.rng.random() > chance:
        return None
    sc = s.rng.choices(pool, weights=[c["w"] for c in pool], k=1)[0]
    s.stats["scenes"] = s.stats.get("scenes", 0) + 1
    if sc["once"]:
        s.seen.append(sc["id"])
    if sc["id"] == "subject03":
        s.flag("met03")
    return build(s, sc)


def choose(s, n):
    """Apply displayed option n (1-based). Returns text."""
    sc_state = s.scene
    if not sc_state:
        return "There is nothing in front of you to answer."
    if n < 1 or n > len(sc_state["opts"]):
        return "There is no option %d." % n
    sc = BY_ID[sc_state["sid"]]
    real = sc_state["map"][n - 1]
    label = sc_state["opts"][n - 1]
    s.scene = None
    # two separate records: what the chip decided, and what came of it. The watch window
    # shows the decision as its own line, because "what happened" without "what you picked"
    # is only half of what somebody reading over your shoulder needs.
    s.note("YOU CHOSE: %s   (%s)" % (label, sc_state.get("title") or sc_state["sid"]))
    out = sc["opts"][real]["eff"](s)
    # an option that returns nothing is a bug in that option, not a reason to lose the run
    if not out:
        out = "It does it. Nothing about it is worth describing."
    s.note("-> " + out)
    return out


MOVE_VERBS = ("go", "forward", "advance", "walk", "move", "onward", "north")


def expired(s, verb):
    """A situation you walked away from, or left standing too long, stops being in front of you."""
    sc = s.scene
    if not sc:
        return False
    bank = BY_ID.get(sc["sid"])
    if bank and bank["zones"] and W.zone(s)["key"] not in bank["zones"]:
        return True
    if verb in MOVE_VERBS:
        return True
    return sc.get("age", 0) >= 3


def leave_behind(s):
    sc = s.scene
    s.scene = None
    bank = BY_ID.get(sc["sid"]) if sc else None
    if bank and bank.get("urgent"):
        return "You leave it unanswered. It is still true."
    return "Whatever that was, it is behind you now."


def escalate(s):
    """Called when the player does something else while a dangerous scene waits."""
    sc = s.scene
    if not sc:
        return None
    sc["age"] = sc.get("age", 0) + 1
    if sc["danger"] <= 0 or sc["age"] < 2:
        return None
    if s.rng.random() > sc["danger"] * 0.7:
        return None
    limb = s.rng.choice(list(s.limbs))
    B.hurt(s, limb, s.rng.uniform(10, 22), "bite")
    return "You took too long. It did not wait for you."


# ---------------------------------------------------------------- the ground under the test
# The crust and core banks live in their own module; they are handed the constructors from here
# so that neither file has to import the other.
from . import scenes_deep as _DEEP          # noqa: E402
from . import scenes_rock as _ROCK          # noqa: E402
from . import traps as _TRAP                # noqa: E402
from . import scenes_warrens as _WARR      # noqa: E402
from . import scenes_building as _BLDG     # noqa: E402
SCENES += _DEEP.build_deep(SC, O)
SCENES += _ROCK.build_rock(SC, O)
SCENES += _WARR.build_warrens(SC, O)
SCENES += _BLDG.build_building(SC, O)
# Trap scenes are never drawn from the random pool - traps.roll() chains them by id after it
# has already decided whether the body saw the thing. The impossible zone key is what keeps
# _allowed() from ever offering one as an ordinary encounter.
SCENES += _TRAP.build_traps(SC, O)
# the id index is built above, so it has to be rebuilt once the other banks are in
BY_ID = {sc["id"]: sc for sc in (SCENES + URGENT)}
