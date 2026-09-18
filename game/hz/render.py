"""Terminal frame. Deliberately compact - something with a token budget has to read this."""
from . import body as B
from . import crisis as CR
from . import escape as ESC
from . import issues as ISS
from . import persuade as P
from . import items as I
from . import timers as T
from . import tutorial as TUT
from . import voice as V
from . import will as WILL
from . import world as W

RULE = "=" * 74

QUICK = ("CMDS go | gather | camp [h] | rest [h] | shelter | tend <limb> | craft <thing> | "
         "use <item> | inv | reassure | override <cmd> | recalibrate | issues | timers\n"
         "     think | listen | say <n> | persuade <plain words> | status | truths | map | escape | hide | "
         "cut chip | help")


def head(s):
    z = W.zone(s)
    from . import subjects as SUB
    from . import regions as REG
    return "HORIZONS  %s  %s   day %d  %s   %s %.1f/%.0f   %s%s" % (
        REG.name(s), SUB.name(s), s.day, s.clock, W.progress_bar(s), s.distance,
        W.goal(s), z["name"], "  (night)" if s.night else "")


def vitals(s):
    return ("COND %-13s blood %3.0f  strain %3.0f  fatigue %3.0f  pain %3.0f  thirst %3.0f  "
            "hunger %3.0f  inf %3.0f  weird %3.0f  warm %3.0f"
            % (B.condition_word(s), s.blood, s.strain, s.fatigue, s.pain, s.thirst,
               s.hunger, s.infection, s.weird, s.warmth))


def advice(s):
    """Every pressure that has a known remedy, named. Worst first, at most three."""
    out = []
    if s.weird > 50:
        out.append("wrongness %.0f - 'recalibrate' pulls it back, and stop leaning on "
                   "'override' (every one adds to it)" % s.weird)
    if s.chip < 60:
        out.append("link at %.0f%% - 'recalibrate' repairs it" % s.chip)
    if B.load_of(s) > B.carry_cap(s):
        out.append("carrying %d of %d - 'drop <item>' until it fits, it is slowing every step"
                   % (B.load_of(s), B.carry_cap(s)))
    if B.bleed_rate(s) > 0.05:
        fix = "bleeding - 'tend <limb>'"
        if I.has(s, "clot"):
            fix += " or 'use clot' for all of it at once, dirty"
        out.append(fix)
    if s.infection > 40:
        out.append("infection %.0f - 'use salve'" % s.infection)
    if s.thirst > 72:
        out.append("thirst %.0f - 'use water'" % s.thirst)
    if (getattr(s, "heat", 0.0) or 0.0) > 25:
        out.append("overheating %.0f - get off the hot ground, 'rest', or pour water over it"
                   % s.heat)
    if s.hunger > 75:
        out.append("hunger %.0f - 'use ration' or 'use meat'" % s.hunger)
    if s.fatigue > 78:
        out.append("fatigue %.0f - 'shelter' then 'camp 6'" % s.fatigue)
    if s.mood < 30:
        out.append("mood %.0f - 'reassure'" % s.mood)
    if s.pain > 70:
        out.append("pain %.0f - 'rest 2'" % s.pain)
    return out[:3]


def chipline(s):
    return ("CHIP  will %3.0f  mood %3.0f  link %3.0f%%   (%s, %s)"
            % (s.will, s.mood, s.chip, WILL.mood_word(s), WILL.link_word(s)))


def frame(s, body_text="", show_cmds=True):
    from . import regions as REG
    if s.crisis:
        L = [RULE, head(s)]
        L.extend(CR.lines(s))
        L.append("-" * 74)
        if body_text:
            L.append(body_text.strip())
        return "\n".join(L)
    from . import intel as IN
    from . import link as LK
    L = [RULE, head(s)]
    if LK.is_down(s):
        # the readouts below are the last thing that came up the link before it went.
        L.extend(LK.banner(s))
    from . import lastbreath as LB
    L.extend(LB.banner(s))
    L.extend([vitals(s), chipline(s), IN.line(s), "LIMBS " + B.limb_summary(s)])
    from . import mortal as _MO
    if _MO.holed(s):
        st = getattr(s, "chest", None) or {}
        L.append("CHEST %s - it is still coming out%s"
                 % ((st.get("why") or "a hole through the middle").upper(),
                    ", slower, through the packing" if s.eff("packed") else
                    ". Nothing in the pack reaches this. 'pack' is all there is"))
    from . import phones as PH
    _ph = PH.line(s)
    if _ph:
        L.append(_ph)
    from . import intent as _INT
    L.extend(_INT.banner(s))
    pr = float(getattr(s, "snap", 0.0) or 0.0)
    if pr > 45.0:
        L.append("EDGE  %3.0f   something in it is being held down, and it is slipping" % pr)
    w = B.warnings(s)
    if w:
        L.append("!!    " + ", ".join(w))
    eff = [k for k in s.effects]
    if eff:
        L.append("EFF   " + ", ".join("%s(%dm)" % (k, s.effects[k]) for k in eff))
    L.append("CARRY %d/%d  %s" % (B.load_of(s), B.carry_cap(s), I.inv_line(s)))
    adv = advice(s)
    if adv:
        L.append("FIX   " + ("\n      ".join(adv)))
    if s.issues:
        L.append("ISSUES")
        L.extend(ISS.lines(s))
    if s.timers:
        L.append("TIMED")
        L.extend(T.lines(s))
    if getattr(s, "requests", None):
        L.extend(P.lines(s))
    esc = ESC.status_line(s)
    if esc:
        L.append(esc)
    if not TUT.done(s):
        L.append("-" * 74)
        L.append(TUT.prompt(s))
    if s.feedback:
        L.append("-" * 74)
        L.extend(s.feedback)
    L.append("-" * 74)
    if body_text:
        L.append(body_text.strip())
    if s.question:
        L.append("")
        L.extend(V.pending_lines(s))
    if s.scene:
        L.append("")
        L.append(s.scene["text"])
        L.append("OPTIONS")
        for i, o in enumerate(s.scene["opts"], 1):
            L.append("  %d) %s" % (i, o))
    if show_cmds:
        L.append("")
        # 'leave' only exists in the act that saves as it goes, and the command list is the
        # only place it is advertised inside a run. It is not in help, for the same reason
        # the README does not mention any of this.
        L.append(QUICK + (" | leave" if REG.on_final(s) else ""))
    return "\n".join(L)


def intro(reg=None, destiny=False, carried=False, final=False, resumed=False):
    from . import regions as REG
    reg = reg or REG.BY_KEY[REG.DEFAULT]
    brief = reg["brief"]
    label = reg["label"]
    if destiny:
        brief = REG.DESTINY_BRIEF.get(reg["key"], brief)
        label = "the other one - and nobody wrote this part down"
    if final:
        brief = REG.FINAL_BRIEF
        label = "the way back in"
    tail = ("\n" + RULE + "\n"
            + (REG.FINAL_NAME if final else
               reg["name"] + (" / " + REG.DESTINY_NAME if destiny else ""))
            + " - " + label + "\n\n" + brief + "\n")
    if final and resumed:
        return (RULE + "\n"
                "HORIZONS\n"
                "\n"
                "The link closes on a body that has not moved.\n"
                "\n"
                "It is where you put it down. It is dark in here and the dark is the\n"
                "ordinary kind, with a strip of corridor light under a door somewhere\n"
                "off to one side of it, and the building going about its business the\n"
                "way it has gone about its business the entire time.\n"
                "\n"
                "It waited. It did not eat anything it was keeping and it did not go\n"
                "looking for you. It is thinner than it was.\n"
                + tail + RULE)
    if final:
        return (RULE + "\n"
                "HORIZONS\n"
                "\n"
                "The link closes in long grass, and you know exactly where you are.\n"
                "\n"
                "A hundred paces off there is a fence. You have seen this fence in the\n"
                "first hour of every walk you have ever been given, from the inside,\n"
                "going the other way. The grass is worn off the far side of it in a\n"
                "strip, and the strip is mown, and something mowed it this year.\n"
                "\n"
                "The lights are on in the buildings behind it. The lights have been on\n"
                "the whole time. Nothing about this place has stopped running just\n"
                "because nobody has come out of it in a very long while.\n"
                "\n"
                "The body has nothing on it and nothing with it. There is no\n"
                "calibration, there is nobody at the far end expecting a result, and\n"
                "there is no line to cross. There is a way in, and it is shut, and\n"
                "everything past it is shut as well.\n"
                "\n"
                "This one is long. Put it down when you need to - 'leave' - and it\n"
                "keeps where it stood.\n"
                + tail + RULE)
    if destiny and reg["key"] == "crust":
        return (RULE + "\n"
                "HORIZONS\n"
                "\n"
                "The link closes and you are already underground.\n"
                "\n"
                "The body is on its side in a passage, in the dark, and the dark is not the\n"
                "dark of a room with the lights off - it is the dark of a place that has\n"
                "never had a light in it. The rock is warm. The air is moving, slowly, and\n"
                "it is coming up from somewhere below rather than down from anywhere above.\n"
                "\n"
                "Stacked against the wall beside its head, close enough to touch, there is a\n"
                "small cairn of flat stones, and the top one has marks cut into the face of\n"
                "it. Somebody built that. Somebody built it here, in the dark, for something\n"
                "coming the other way.\n"
                "\n"
                "There is no calibration. You have done this before or you would not have\n"
                "been given this one.\n"
                + tail + RULE)
    if destiny and reg["key"] == "core":
        return (RULE + "\n"
                "HORIZONS\n"
                "\n"
                "The link closes at the bottom of a shaft.\n"
                "\n"
                "Whatever brought the body down here put it on its feet and left, and it has\n"
                "been standing in the dark waiting to be told something for an unknown\n"
                "number of hours. Above it the shaft goes up further than the body could\n"
                "climb. Below it the dug rock stops and ordinary rock takes over, and the\n"
                "ordinary rock still goes down.\n"
                "\n"
                "The cairns start again about twenty paces in. They are better made down\n"
                "here than they were up there, which is the wrong way round for the work of\n"
                "something getting tired, and the count on them is still going up.\n"
                "\n"
                "There is no calibration and there is nothing at the top expecting you back.\n"
                + tail + RULE)
    if destiny:
        return (RULE + "\n"
                "HORIZONS\n"
                "\n"
                "The link closes and you are already outside.\n"
                "\n"
                "There is no room. There is no floor that was cleaned recently and nobody\n"
                "standing over anything. The body you are in is lying on bare rock in the\n"
                "open, the sky above it is the wrong colour for a sky, and whatever put it\n"
                "here did not leave anything with it and did not stay.\n"
                "\n"
                "You have done this before. That is the only reason you have been given this\n"
                "one. There is no calibration. Nothing here explains itself and nothing here\n"
                "is going to tell you what any of it is.\n"
                "\n"
                "What you have been given is one sentence, and you were given it without a\n"
                "source: there is a house out here, and once you are inside the zone around\n"
                "it, it is completely safe and completely calm.\n"
                + tail + RULE)
    if carried:
        return (RULE + "\n"
                "HORIZONS\n"
                "\n"
                "It did not wake up. It never stopped.\n"
                "\n"
                "The same body goes on into the next act carrying the same kit, wearing what\n"
                "the last one did to it, knowing what it had already worked out. The chip is\n"
                "seated and it works. There is nothing to calibrate and nobody offering.\n"
                + tail + RULE)
    return (RULE + "\n"
            "HORIZONS\n"
            "\n"
            "You come up out of something that was not sleep, on a floor that was cleaned\n"
            "recently by somebody who is no longer here. You are furred. You have a muzzle,\n"
            "and a tail, and hands. Your eyes throw a faint orange light onto the wall in\n"
            "front of you, and when you bite your own arm to check, what comes out is the\n"
            "same colour.\n"
            "\n"
            "You do not know what you are. You know, with a certainty that feels installed,\n"
            "that you are supposed to go forward until the world ends, and that something\n"
            "is counting.\n"
            "\n"
            "You are not this creature. You are the chip they seated behind its ear: most of\n"
            "its intelligence, all of its instructions, and none of its willingness. It can\n"
            "refuse you when it is exhausted, in pain, or miserable. Look after it and it\n"
            "mostly will not.\n"
            "\n"
            "The chip has to be calibrated before the run, and the door out of the Holding\n"
            "stays shut until it is. Type 'look' to begin. Type 'help' for everything else.\n"
            + tail + RULE)
