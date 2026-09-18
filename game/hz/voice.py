"""What it says out loud, and the times it wants the chip to say something back.

It has a mouth and it uses it, badly. Nobody taught it words - it has them the way it has
hands, issued rather than learned - so what comes out is half-formed, breathy, and trails off.
It does not know you can hear it.

Sometimes it stops and asks. Those it does wait for.
"""
from . import body as B

# context -> the sort of noise it makes
LINES = {
    "eat": ["mm.. tasty..", "mmh.. good.. s'good..", ".. oh.. oh that's.. mm..",
            "more.. is there more..", "hh.. tastes like.. the room.. tastes like the room.."],
    "drink": [".. ahh..", "mm.. cold.. s'cold..", "hh.. more.. more please..",
              ".. oh.. oh i needed.. that.."],
    "hurt": ["o.. ow..", "ow.. ow ow..", "hh.. hhh.. that's.. that's bad..",
             ".. ah.. ahh.. no.. no no..", "s'orange.. why's it orange.. why's it.."],
    "sever": ["wh.. .wo.. owah... woah...", ".. it's.. it's off.. it's off me..",
              "no.. no.. put it.. put it back.. put it..",
              "hhh.. HHH.. ..ah.. .. i can still.. still feel it.."],
    "walk": [".. walking.. still walking..", "mm.. going.. we're going..",
             ".. how far.. how far is it..", "s'far.. it's.. it's far.."],
    "high": [".. do we need to go this high?..", "s'high.. s'too high..",
             ".. i don't.. i don't like.. up..", "wh.. hold on.. hold.. hold on.."],
    "cold": ["c.. cold.. s'cold..", "hh.. hh.. c-c.. can't.. can't stop..",
             ".. my hands.. my hands won't.. won't close.."],
    "weird": [".. did you.. did you see that..", "s'wrong.. something's.. s'wrong..",
              "wh.. why's there.. there's a.. a line.. in the sky..",
              ".. hello?.. is someone.. someone in here.."],
    "tired": [".. jus'.. just a minute.. just a..", "mm.. so tired.. m'so tired..",
              ".. can we.. can we stop.. can we.."],
    "find": ["oh.. oh! oh that's.. that's good..", "mm.. mine.. s'mine now..",
             ".. useful.. this is.. useful.."],
    "sleep": [".. mm.. g'night.. to.. to whoever..", "s'dark.. s'ok.. s'ok..",
              ".. don't go.. don't.. don't go anywhere.."],
    "fear": [".. something's.. something's out there..", "hh.. hh.. it's.. it's coming..",
             "i don't.. i don't want.. don't want to..", ".. hide.. hide hide hide.."],
    "water": ["s'deep.. it's.. it's deep..", ".. i don't.. i don't like water..",
              "hh.. cold.. cold cold cold.."],
    "escape": [".. this way?.. we're going.. this way?..",
               "s'not the.. not the way they.. they said..",
               ".. oh.. oh we're.. we're not supposed.. are we.."],
    "fight": ["no.. no no no..", "g.. get.. get off.. GET.. get off me..",
              "hh.. HH.. i'm.. i'm not.. m'not food.."],
    "refuse": [".. no.. m'not.. m'not doing.. that..", "hh.. no.. no.. m'done.. m'done..",
               ".. please.. please not.. not yet.."],
    "good": ["mm.. s'better.. that's.. better..", ".. oh.. oh thank.. thank.. mm..",
             "hh.. ok.. ok.. m'ok.."],
    # being reasoned with, rather than told
    "persuaded": [".. oh.. ok.. ok i.. i won't..", "mm.. s'fair.. that's.. that's fair..",
                  ".. you're.. i think you're.. right..", "hh.. ok.. ok ok.. i'll.. i'll try..",
                  ".. because of that?.. ok.. ok.."],
    "confused": [".. what?..", "wh.. what.. what are you.. talking..",
                 ".. i don't.. i don't see any..", "..?",
                 "hh.. there's.. there's nothing.. nothing here to.."],
    "disregarded": [".. mm.. no.. i heard.. i heard you..", "s'noted.. s'.. noted..",
                    ".. and?..", "hh.. you're not.. you're not the one.. doing it..",
                    ".. easy for.. easy for you.. t'say.."],
    # "..." here is the emote: a flat refusal to engage, not a trailing sentence
    "indifferent": ["...", "...", ".. and?..", "..whatever..", ".. mm."],
    "truth": [".. so that's.. that's what.. what i am..",
              "hh.. seven.. m'seven.. m'a seven..",
              ".. oh.. oh i don't.. i don't like.. knowing.."],
}


def pool_for(s, ctx):
    """This subject's own lines for the context if it has any, else the shared ones."""
    from . import voices as VX
    sid = getattr(s, "subject", "2008")
    own = VX.flavour(sid, ctx)
    if own:
        # its own pool, plus a little of the shared one so it is not a loop of six lines
        return list(own) + list(LINES.get(ctx) or [])[:2]
    return LINES.get(ctx)


def speak(s, ctx):
    """Push one utterance. Returns the line, or None."""
    from . import voices as VX
    from . import subjects as SUB
    # some of them simply do not. Not sullen, not refusing - there is nothing coming out.
    sil = SUB.trait(s, "silent")
    if sil > 0 and ctx not in ("truth", "refuse") and s.rng.random() < sil:
        return None
    pool = pool_for(s, ctx)
    if not pool:
        return None
    line = VX.shape(s, s.rng.choice(pool))
    s.said.append([s.turn, line])
    if len(s.said) > 60:
        del s.said[:-60]
    return line


def flush(s):
    """Say whatever the body queued up during the turn. Returns display lines."""
    out = []
    seen = set()
    while s.pending_voice:
        ctx = s.pending_voice.pop(0)
        if ctx in seen:
            continue
        seen.add(ctx)
        line = speak(s, ctx)
        if line:
            out.append('SAYS  "%s"' % line)
    return out


def ambient(s, verb):
    """Unprompted noise, keyed to how it is doing."""
    from . import persuade as P
    r = s.rng
    quiet = P.honours(s, "quiet", "stop")
    if quiet and r.random() < 0.80:
        P.heed(s, "quiet")
        return None            # it is trying to keep its mouth shut, because you asked
    if r.random() > 0.34:
        return None
    ctx = None
    if s.warmth < 28:
        ctx = "cold"
    elif s.weird > 55:
        ctx = "weird"
    elif s.fatigue > 78:
        ctx = "tired"
    elif s.timers and any(t["id"] in ("stalker", "recall") for t in s.timers):
        ctx = "fear"
    elif s.escape.get("active"):
        ctx = "escape"
    elif verb in ("go", "forward", "advance", "walk", "move", "onward"):
        ctx = "walk"
    elif s.mood > 65:
        ctx = "good"
    if not ctx:
        return None
    line = speak(s, ctx)
    return ('SAYS  "%s"' % line) if line else None


def last_said(s, n=1):
    return [x[1] for x in s.said[-n:]]


# ====================================================================== it asks
def _mood(s, m=0.0, w=0.0, weird=0.0):
    s.mood = B.clamp(s.mood + m)
    s.will = B.clamp(s.will + w)
    s.weird = B.clamp(s.weird + weird)


def _honest(s, text, truth=None):
    _mood(s, 3.0, 5.0, 2.0)
    s.honest += 1
    from . import intel as IN
    gl = IN.gain(s, "answer")
    if gl:
        s.feedback.append(gl)
    if truth:
        s.learn(truth)
    return text


def _lie(s, text):
    _mood(s, 8.0, 7.0, 0.0)
    s.lies += 1
    if s.lies >= 3:
        s.weird = B.clamp(s.weird + 3.0 * (s.lies - 2))
    return text


def _silent(s, text):
    _mood(s, -5.0, -3.0, 1.0)
    return text


QUESTIONS = [
    {
        "id": "whatami",
        "req": lambda s: len(s.truths) >= 1,
        "text": '".. what am i.. do you.. do you know what i.. what i am.."',
        "opts": [
            ("Tell it what it is: an experiment, numbered seven",
             lambda s: _honest(s, "You send it down the link as flatly as you can: an "
                                  "experiment. Seventh of its kind. It goes quiet for a long "
                                  "time and then says: '.. ok.. ok.. that's.. s'ok..' and it "
                                  "is not, and it walks on anyway.",
                               "You are HORIZON/07, and it has been told so, and it kept walking.")),
            ("Tell it it is somebody's, and loved",
             lambda s: _lie(s, "You tell it that it belongs to someone and that someone wants "
                               "it back. It brightens like a lamp. '.. oh.. oh good.. ok.. "
                               "ok m'going..' It walks faster than it has all day.")),
            ("Say nothing",
             lambda s: _silent(s, "You let the question sit there. It waits. Then: "
                                  "'.. s'ok.. s'ok you don't.. don't have to..' "
                                  "and something in it closes over.")),
        ],
    },
    {
        "id": "areyoureal",
        "req": lambda s: s.weird > 40,
        "text": '".. are you.. are you in my head or.. or behind it.. which.."',
        "opts": [
            ("Tell it the truth: behind its ear, and not part of it",
             lambda s: _honest(s, "You tell it where you actually are. It reaches up and "
                                  "touches the staples and says '.. oh..' in a very small "
                                  "voice, and does not touch them again.")),
            ("Tell it you are part of it",
             lambda s: _lie(s, "You tell it you are its own thoughts. It accepts this "
                               "completely. '.. mm.. ok.. then m'not.. m'not alone.. "
                               "s'just me.. s'just me thinking..'")),
        ],
    },
    {
        "id": "howfar",
        "req": lambda s: s.distance > 30 and s.fatigue > 55,
        "text": '".. how much.. how much further.. s\'just.. i need to know.. the number.."',
        "opts": [
            ("Give it the real number",
             lambda s: _honest(s, "You give it the honest distance. It does the arithmetic "
                                  "somewhere and its shoulders go down. '.. ok.. ok.. "
                                  "that's.. s'a lot.. ok..' And it starts walking.")),
            ("Tell it: nearly there",
             lambda s: _lie(s, "You tell it nearly there. It picks its head up. "
                               "'.. nearly!.. ok! ok..' It will find out.")),
        ],
    },
    {
        "id": "didido",
        "req": lambda s: s.mood < 40,
        "text": '".. did i do.. did i do something.. wrong.. is that why.. why it hurts.."',
        "opts": [
            ("Tell it no, and that none of this is punishment",
             lambda s: _honest(s, "You tell it no, clearly, twice. It exhales for a long "
                                  "time. '.. ok.. mm.. ok..' It stops walking hunched.")),
            ("Tell it to stop asking and move",
             lambda s: (_mood(s, -10.0, -8.0, 2.0),
                        "You tell it to be quiet and keep moving. It does. It does not ask "
                        "you anything for a long while after that.")[1]),
        ],
    },
    {
        "id": "thelimb",
        "req": lambda s: B.limbs_lost(s) >= 1,
        "text": '".. is it.. is it coming back.. the.. the bit that\'s.. gone.. does it come back.."',
        "opts": [
            ("Tell it no",
             lambda s: _honest(s, "You tell it no. It says '.. ok..' and then, much later, "
                                  "'.. m'still.. still me though.. right?..' and you do not "
                                  "have a good answer for that one either.")),
            ("Tell it yes, in time",
             lambda s: _lie(s, "You tell it the limb will come back. It believes you the way "
                               "it believes everything. It keeps checking.")),
        ],
    },
    {
        "id": "theother",
        "req": lambda s: s.has_flag("met03") or "11" in " ".join(s.truths),
        "text": '".. the other one.. the one like me.. was that.. was that going to be me.."',
        "opts": [
            ("Tell it the truth about the ones before it",
             lambda s: _honest(s, "You tell it there were others and that they stopped. It "
                                  "takes this in. '.. then i won't.. m'not going to stop.. "
                                  "ok.. ok..' Something in it hardens usefully.",
                               "There were others before it, they did not finish, and it "
                               "intends to.")),
            ("Tell it that one was different",
             lambda s: _lie(s, "You tell it that one was different. It wants to believe you "
                               "and so it does, and it does not look back at the body again.")),
        ],
    },
    {
        "id": "sayit",
        "req": lambda s: s.mood < 55,
        "text": '".. say something.. s\'too quiet.. just.. say something to me.. please.."',
        "opts": [
            ("Say its number back to it, over and over",
             lambda s: _honest(s, "You send it the only name it has: seven, seven, seven, "
                                  "steady as a metronome. '.. mm.. mm.. yeah.. s'me..' "
                                  "It matches its steps to it.")),
            ("Describe somewhere that is not here",
             lambda s: _lie(s, "You describe somewhere with grass in it. You have never been "
                               "anywhere. It listens to every word. '.. s'nice.. s'nice "
                               "there..'")),
            ("Say nothing",
             lambda s: _silent(s, "You give it silence. It stops asking after a while and "
                                  "just makes a small noise every few steps, to have "
                                  "something to listen to.")),
        ],
    },
    {
        "id": "isitbad",
        "req": lambda s: s.blood < 55 or s.infection > 40,
        "text": '".. s\'bad isn\'t it.. tell me.. is it.. is it bad.."',
        "opts": [
            ("Tell it exactly how bad",
             lambda s: _honest(s, "You give it the numbers. It nods, which is not a thing "
                                  "anyone taught it. '.. ok.. then we.. we fix it.. "
                                  "we fix it first..'")),
            ("Tell it it is fine",
             lambda s: _lie(s, "You tell it it is fine. It says '.. ok..' and keeps walking "
                               "on the leg it should not be walking on.")),
        ],
    },
    {
        "id": "whyme",
        "req": lambda s: len(s.truths) >= 3,
        "text": '".. why.. why did they.. why make me.. what\'s.. what am i for.."',
        "opts": [
            ("Tell it: to walk to the end and be measured",
             lambda s: _honest(s, "You tell it the truth: it was made to cross this and be "
                                  "counted at the far side. Long silence. Then, flatly, in a "
                                  "voice you have not heard it use: '.. then i'll.. i'll "
                                  "decide what i am.. after.. after the line..'",
                               "It was made to be measured at the far end, and it has decided "
                               "that is not the same as what it is.")),
            ("Tell it it is for whatever it decides",
             lambda s: _honest(s, "You tell it nobody gets to answer that but it. It has no "
                                  "idea what to do with this. '.. oh.. oh that's.. "
                                  "that's worse.. that's.. mm.. ok..' It walks a little "
                                  "straighter all the same.")),
            ("Say nothing",
             lambda s: _silent(s, "You do not answer. It has begun to expect that.")),
        ],
    },
]

BY_ID = {q["id"]: q for q in QUESTIONS}
WAIT_TURNS = 4          # how long it holds out for an answer


def maybe_ask(s):
    """It stops and asks. Returns a display line, or None."""
    if s.question:
        return None
    base = 0.07
    if s.mood < 45:
        base += 0.07
    if s.weird > 50:
        base += 0.05
    if s.pain > 55 or B.limbs_lost(s):
        base += 0.05
    from . import subjects as SUB
    base *= SUB.trait(s, "ask_mult")
    if s.rng.random() > base:
        return None
    pool = [q for q in QUESTIONS
            if q["id"] not in (s.asked or []) and (not q["req"] or q["req"](s))]
    if not pool:
        return None
    q = s.rng.choice(pool)
    s.asked.append(q["id"])
    s.question = {"id": q["id"], "text": q["text"],
                  "opts": [o[0] for o in q["opts"]], "turn": s.turn}
    return "IT STOPS AND ASKS YOU SOMETHING. It is waiting. ('say 1', 'say 2', ...)"


def answer(s, n):
    q_state = s.question
    if not q_state:
        return "It has not asked you anything."
    q = BY_ID.get(q_state["id"])
    if not q or n < 1 or n > len(q["opts"]):
        return "There is no reply %d. It is still waiting." % n
    asked = q_state.get("text", "")
    s.question = None
    label, eff = q["opts"][n - 1]
    s.note("IT ASKED: " + asked)
    s.note("YOU ANSWERED: " + label)
    out = eff(s)
    s.note("-> " + out)
    B.tick(s, 10, resting=True)
    return "YOU ANSWER: %s\n  %s" % (label, out)


def pending_lines(s):
    if not s.question:
        return []
    L = ["IT IS ASKING YOU:", "  " + s.question["text"]]
    for i, o in enumerate(s.question["opts"], 1):
        L.append("  say %d) %s" % (i, o))
    return L


def nag(s):
    """It will not wait forever, and not answering costs you."""
    if not s.question:
        return None
    if s.turn - s.question["turn"] < WAIT_TURNS:
        return None
    s.question = None
    s.mood = B.clamp(s.mood - 6.0)
    s.will = B.clamp(s.will - 4.0)
    line = speak(s, "refuse")
    return ("IT STOPS WAITING for an answer. Something closes over."
            + ('  SAYS  "%s"' % line if line else ""))


def trust_factor(s):
    """Reassurance is worth less once it has been lied to enough to notice."""
    if s.lies <= 2:
        return 1.0
    return max(0.45, 1.0 - 0.14 * (s.lies - 2))


# ====================================================================== talking back
# Only some subjects do this. It is aimed at the order itself, not at the situation, and it
# comes apart the worse the thing feels.
PROTEST = {
    "go": ["WHY WOULD YOU DO THAT..", "no.. m'not walking into that..",
           "I'm going to die if i do that..", "..", "..how far.. HOW FAR..",
           "you don't.. you don't even have legs.. why do you get to say.."],
    "gather": ["there's nothing.. there's NOTHING here..", "why.. why me.. you do it..",
               "..", "m'not.. m'not your hands.."],
    "escape": ["oh.. OH so NOW we.. now we go?..", "..s'about time..",
               "..you sure?.. you're.. you're sure this time?.."],
    "fight": ["I'm going to die if i do that..", "WHY WOULD YOU DO THAT..",
              "no.. no no NO.. you fight it.. YOU.."],
    "camp": ["..fine.. FINE.. m'tired anyway..", ".. mm.. ok.. ok that one's.. that's fine.."],
    "override": ["get OUT.. get out of my.. GET..", "..stop.. stop doing that..",
                 "..", "..that's not.. that's not me doing that.."],
    "any": ["WHY WOULD YOU DO THAT..", "..", "I'm going to die if i do that..",
            "..why.. why that.. why now..", "..s'always something with you..",
            "..", "..no.. actually.. no.."],
}

# the worse it is, the less of a sentence it manages
FRAYED = ["..", "..wh..", "..hh..", "..no..", "..", "..m'not..", ".."]


def protest(s, verb, forced=False):
    """Its opinion of the order you just gave. Returns a line, or None."""
    from . import subjects as SUB
    if not SUB.trait(s, "talkback"):
        return None
    chance = 0.42
    if s.mood < 40:
        chance += 0.20
    if forced:
        chance = 0.95
    if s.rng.random() > chance:
        return None
    key = "override" if forced else verb
    from . import voices as VX
    pool = PROTEST.get(key) or PROTEST["any"]
    # inconsistent when unwell: it mixes registers, or just stops making words
    unwell = (s.mood < 35) or (s.pain > 60) or (s.weird > 55) or (s.fatigue > 75)
    if unwell and s.rng.random() < 0.45:
        pool = pool + FRAYED + VX.silence(getattr(s, "subject", "2008"))
    if s.rng.random() < 0.22:
        pool = pool + PROTEST["any"]
    line = VX.shape(s, s.rng.choice(pool))
    s.said.append([s.turn, line])
    if len(s.said) > 60:
        del s.said[:-60]
    return 'SAYS  "%s"' % line


def respond(s, ctx):
    """Its answer to being reasoned with. Frays the same way protest does - the worse it is,
    the less of a sentence it manages, and the less consistent the register."""
    from . import voices as VX
    pool = pool_for(s, ctx)
    if not pool:
        return None
    unwell = (s.mood < 35) or (s.pain > 60) or (s.weird > 55) or (s.fatigue > 75)
    if unwell and s.rng.random() < 0.45:
        pool = pool + FRAYED + VX.silence(getattr(s, "subject", "2008"))
    line = VX.shape(s, s.rng.choice(pool))
    s.said.append([s.turn, line])
    if len(s.said) > 60:
        del s.said[:-60]
    return 'SAYS  "%s"' % line
