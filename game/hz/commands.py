"""Command parsing and the per-turn loop. One text command in, one full report out.

Order of business each turn: the calibration gate, then whether the subject will even do it,
then the action, then complications, timed events, scene pressure, and death.
"""
from . import body as B
from . import crisis as CR
from . import endings as E
from . import escape as ESC
from . import issues as ISS
from . import intel as IN
from . import items as I
from . import lastbreath as LB
from . import link as LK
from . import monologue as M
from . import tells as TE
from . import thebuilding as TB
from . import persuade as P
from . import regions as REG
from . import render as R
from . import rock as RK
from . import warrens as WR
from . import scenarios as SCN
from . import subjects as SUB
from . import timers as T
from . import traps as TR
from . import tutorial as TUT
from . import voice as V
from . import will as WILL
from . import world as W
from .state import LIMB_ORDER

# how likely a fresh scene is after each kind of action - walking is what finds trouble
SCENE_ODDS = {
    "go": 0.52, "forward": 0.52, "advance": 0.52, "walk": 0.52, "move": 0.52, "onward": 0.52,
    "gather": 0.26, "search": 0.26, "scavenge": 0.26, "forage": 0.26, "loot": 0.26,
    "camp": 0.30, "sleep": 0.30, "shelter": 0.16, "build": 0.16, "rest": 0.12,
}

MOVE = ("go", "forward", "advance", "walk", "move", "onward", "north")
PERSUADE_VERBS = ("persuade", "please", "reason", "plead", "convince")

HELP = """HORIZONS - commands

MOVING     go / forward        push toward the horizon (or, off-route, away from the test)
           map                 the route, and how far along it you are
SCENES     1 / 2 / 3 ...       answer the numbered option in front of you
           look                reprint the current situation
THE CHIP   reassure            no orders, just hold the link - raises mood and willingness
           override <cmd>      force an order it refused. Costs mood, will and link integrity
           persuade <words>    reason with it in plain words instead of ordering it. Free.
                               Say what to stop or keep doing, and WHY - a stated reason is
                               most of what makes it land:
                                 persuade please do not eat too much because no more food
                                 persuade please keep going because we are nearly there
                                 persuade don't run, you'll tear the leg open
                               If it agrees, that becomes a standing request it tries to keep
                               on its own, listed as ASKED OF IT, until its mood is too low to
                               hold it. Raise it at a moment it makes no sense and it will not
                               understand what you are talking about. Some of them will hear
                               you out and carry on regardless.
           recalibrate         walk the chip through its diagnostic; clears faults, cuts weird
           disconnect [turns]  take the chip out of the loop on purpose (1-8, default 3). It
                               runs itself for that long: no orders, no reading it, no settling
                               it down - and being left alone is the only thing that properly
                               takes the pressure off some of them.
           mend                patch a cracked shell back up (scrap + cord), if it is wearing
                               one. The shell is armour and only over what it covers; what is
                               playing underneath it is not armour and cannot be replaced.
           reconnect           re-seat a link that has come off. Costs time, and can fail.
                               While there is no link, nothing you type reaches it - it carries
                               on by itself and the turn happens anyway. If it goes down out
                               there while you are not connected, the forty seconds run
                               without a chip in it, and only 'reconnect' is worth anything.
BODY       status              full readout, limb by limb
           tend <limb>         bind bleeding, splint breaks, salve what is hot
           graft <limb>        fit a crafted strut where a limb is gone
           issues              active complications and how to clear each one
           timers              what is on a countdown right now
           rest [hours]        short rest (default 1)
           camp [hours]        sleep properly (default 6) - safer with shelter and fire
           shelter             build a lean-to from branches or hide
THINGS     inv                 inventory          gather   search this area
           craft <thing>       make something     recipes  what you can make right now
           use <item>          drink, eat, salve, stim, light a torch, read a thing
           drop <item>         put something down
MIND       think               internal monologue and what it currently understands
           truths              what it knows about itself
           region              which act this is, and what it switches on
           wins                every region that has been finished, by whom, and whether that
                               body walked on into the next act or ended there

INTELLIGENCE
    The MIND line on the frame is what the chip understands of what it is looking at. It only
    goes up: truths it works out, straight answers you give it, the first time it builds a
    thing, anything with writing on it, new ground.
    Manufactured objects below a threshold have NO NAME - the inventory shows what it looks
    like instead ("a flat sealed packet, cold to the touch"). You can still use one, and about
    a third of the time you will use it wrong and lose it. Reading a recipe's parts needs the
    same understanding, so intelligence gates what you can build.
IT TALKS   listen              the last few things it said out loud
           say <n>             answer it when it stops and asks you something
LEAVING    escape              a known off-route way out. OUTSIDE only - under the surface
                               there is no off the route
           hide                break line of sight (charcoal helps)
           cut chip            take the chip out. Read that twice before you do it
META       save / quit / help

Limbs: left arm, right arm, left leg, right leg, tail, left ear, right ear
       (short forms work: "tend leg", "tend arm" pick the worst one)
"""


def resolve_limb(s, text):
    t = (text or "").strip().lower()
    if not t:
        return None
    if t in s.limbs:
        return t
    exact = [n for n in LIMB_ORDER if t == n]
    if exact:
        return exact[0]
    part = [n for n in LIMB_ORDER if t in n]
    if part:
        order = ["lost", "mangled", "broken", "gashed", "bruised", "intact"]
        part.sort(key=lambda n: order.index(s.limbs[n]["state"]))
        return part[0]
    return None


def resolve_item(s, text):
    t = (text or "").strip().lower()
    if not t:
        return None
    if t in s.inv:
        return t
    for k in s.inv:
        if k.startswith(t) or t in k:
            return k
    for k in I.CATALOG:
        if k.startswith(t):
            return k
    return None


def _the_line(s):
    """The terminal decision, once the horizon is actually underfoot."""
    text = ("You are at the line. The ground ends and does not fall. The air past it has a grain "
            "in it like something printed at a scale slightly too large.")
    opts = ["Walk across it"]
    if s.has_flag("seam_seen") or len(s.truths) >= 2:
        text += ("\nThere is a seam where the ground stops, and it is a seam, and seams can be "
                 "taken hold of.")
        opts.append("Tear the seam open")
    opts.append("Sit down and refuse")
    return {"sid": "the_line", "text": text, "opts": opts,
            "map": list(range(len(opts))), "age": 0, "danger": 0.0}


def _the_cradle(s):
    """The bottom of the core. A made room, and the thing every chip is sent for."""
    text = ("The cables come together here and they come together on a housing, and the housing "
            "is warm, and inside it something is still lit after however long this has been "
            "down here.\nIt is a battery. You know it is a battery the way you know your own "
            "number: it was in you before anything else was. Bring the battery up.\n"
            "The body it is standing in has no idea what it is looking at, and is waiting to be "
            "told what to do with it.")
    opts = ["Have it lift the battery out", "Leave it where it is and sit down with it"]
    return {"sid": "cradle", "text": text, "opts": opts,
            "map": list(range(len(opts))), "age": 0, "danger": 0.0}


def _why_battery(s):
    """It has asked. You do not have the answer and it is going to notice that."""
    text = ("It has both arms under the thing and it has not lifted yet. It is looking at the "
            "housing, and then up, at nothing, which is where it thinks you are.\n"
            'SAYS  "..why a battery.."\n'
            'SAYS  "..s\'all the way down here.. and it\'s.. it\'s a battery.. why.. '
            'why a battery.."\n'
            "You do not know. Nobody told the chip either. The instruction arrived in you "
            "already finished, with nothing behind it, and this is the first time anything has "
            "asked you to show your working.")
    opts = ["Tell it the truth: you were told to fetch it, and never told why",
            "Tell it the battery is the way out of here",
            "Tell it the battery is its own, and it has earned it",
            "Say nothing"]
    return {"sid": "whybattery", "text": text, "opts": opts,
            "map": list(range(len(opts))), "age": 0, "danger": 0.0}


def _cradle_choice(s, label):
    if label.startswith("Leave"):
        return E.battery_finish(s, "refuse")
    s.battery = True
    s.flag("battery_lifted")
    s.scene = _why_battery(s)
    return None, None


def _why_choice(s, label):
    if label.startswith("Tell it the truth"):
        s.honest += 1
        return E.battery_finish(s, "honest")
    if label.startswith("Say nothing"):
        return E.battery_finish(s, "silent")
    s.lies += 1
    return E.battery_finish(s, "lie")


def _house_choice(s, label):
    if label.startswith("Have it go in"):
        return E.house_finish(s, "in")
    if label.startswith("Have it knock"):
        return E.house_finish(s, "knock")
    if label.startswith("Walk the fence"):
        return E.house_finish(s, "fence")
    return E.house_finish(s, "refuse")


def _throat_choice(s, label):
    if label.startswith("Have it go down"):
        return E.throat_finish(s, "down")
    if label.startswith("Have it add a stone"):
        return E.throat_finish(s, "stone")
    if label.startswith("Have it close"):
        return E.throat_finish(s, "seal")
    return E.throat_finish(s, "back")


def _chamber_choice(s, label):
    if label.startswith("Have it go to the thing"):
        return E.chamber_finish(s, "look")
    if label.startswith("Have it stack"):
        return E.chamber_finish(s, "count")
    if label.startswith("Have it lie down"):
        return E.chamber_finish(s, "stop")
    return E.chamber_finish(s, "back")


def _line_choice(s, label):
    if label.startswith("Walk"):
        return E.finish(s, "cross")
    if label.startswith("Tear"):
        return E.finish(s, "tear")
    return E.finish(s, "refuse")


def _autonomy(s, verb):
    """Some of them do not wait for the chip. Returns (feedback, result) or (None, None)."""
    if not TUT.done(s) or s.escape.get("active"):
        return None, None
    chance = SUB.trait(s, "autonomy")
    if chance <= 0:
        return None, None
    if s.mood < 35:
        chance *= 1.6          # the worse its temper, the less it consults you
    if verb in WILL.NEVER_REFUSED and verb not in ("use", "eat", "drink"):
        return None, None
    if s.rng.random() > chance:
        return None, None

    # it is about to do something of its own. Whatever that costs it, it does not get
    # charged to you - see intent._blameable.
    s.acted_alone = s.turn
    r = s.rng
    picks = ["wander", "forage", "sit"]
    if I.has(s, "ration") or I.has(s, "meat") or I.has(s, "water"):
        picks.append("help itself")
    if s.fatigue > 60:
        picks += ["sit", "sit"]
    if s.timers and any(t["id"] in ("stalker", "recall") for t in s.timers):
        picks += ["bolt", "bolt"]
    # it will not do a thing it has just agreed with you not to do
    BLOCKS = {"help itself": "eat", "wander": "wander", "forage": "wander",
              "bolt": "bolt", "sit": "rest"}
    kept = [p for p in picks
            if not (BLOCKS.get(p) and P.honours(s, BLOCKS[p], "stop"))]
    if not kept:
        for tid in set(BLOCKS.values()):
            if P.honours(s, tid, "stop"):
                P.heed(s, tid)
        return ("IT NEARLY DID SOMETHING OF ITS OWN, AND DIDN'T. It got as far as starting, "
                "remembered it had agreed with you, and stayed where it was.",
                "It shifts its weight, half-turns toward something, and then does not go.")
    if len(kept) < len(picks):
        for p in picks:
            if p not in kept and BLOCKS.get(p):
                P.heed(s, BLOCKS[p])
    picks = kept
    # the one that goes at things does not weigh it up first. A scene in front of it is most
    # of the reason, and the sound stopping is the rest.
    vio = SUB.trait(s, "violent")
    if vio > 0:
        from . import phones as PH
        heat = vio * (1.0 + 1.6 * (s.scene or {}).get("danger", 0.0))
        if not PH.playing(s) and PH.get(s) is not None:
            heat *= 1.8
        if float(getattr(s, "snap", 0.0) or 0.0) > 55:
            heat *= 1.4
        if r.random() < min(0.75, 0.22 * heat):
            picks = ["lash out"]
    what = r.choice(picks)

    if what == "lash out":
        s.stats["fights"] = s.stats.get("fights", 0) + 1
        # going at things costs the heart, and this fires often enough that 16 a time made
        # HEART FAILED the only way 682 ever ended
        s.strain = B.clamp(s.strain + 10)
        s.pain = B.clamp(s.pain + 5)
        hand = r.choice(["left arm", "right arm"])
        B.hurt(s, hand, r.uniform(5, 13), "blunt")
        B.tick(s, 18, exertion=2.0)
        if s.scene and (s.scene or {}).get("danger", 0.0) > 0.25:
            s.scene = None
            res = ("It goes at the thing in front of it before anybody decides anything, and "
                   "it is still going after the thing has stopped. Whatever the situation was, "
                   "it is not that any more.")
            note = "it went at it. No order, no pause, no plan past the first contact"
        else:
            res = ("It turns on the nearest solid thing and hits it until the thing gives or "
                   "its hand does. Nothing was threatening it. Nothing needed doing.")
            note = "it hits something that was not in the way"
        from . import link as LK
        went = LK.snap(s, 6.0, "going off at something on its own")
        if went:
            res += "\n\n" + went
        s.stats["autonomous"] = s.stats.get("autonomous", 0) + 1
        s.will = B.clamp(s.will - 2)
        return ("IT ACTS ON ITS OWN. You ordered '%s'; %s. The chip is not the only thing in "
                "there with an opinion." % (verb, note), res)

    if what == "wander":
        res = W.advance(s)
        note = "it simply starts walking, at its own pace, in roughly the right direction"
    elif what == "bolt":
        res = W.advance(s)
        s.strain = B.clamp(s.strain + 10)
        note = "it bolts - no instruction, no warning, straight away from whatever it heard"
    elif what == "forage":
        res = W.gather(s)
        note = "it stops and starts going through the ground with its hands"
    elif what == "help itself":
        item = ("water" if I.has(s, "water") else
                "ration" if I.has(s, "ration") else "meat")
        res = I.use(s, item)
        note = "it gets into the pack and helps itself to the %s without asking" % item
    else:
        B.tick(s, 45, resting=True, cold=W.cold(s))
        res = "It sits down and does not get up for the better part of an hour."
        note = "it sits down. Not refusing, exactly. It simply had other plans"
    s.stats["autonomous"] = s.stats.get("autonomous", 0) + 1
    s.will = B.clamp(s.will - 2)
    fb = ("IT ACTS ON ITS OWN. You ordered '%s'; %s. The chip is not the only thing in there "
          "with an opinion." % (verb, note))
    return fb, res


def _bench_choice(s, label):
    """The last room in the game. Five ways out of it and only one is not about the chip."""
    t = (label or "").lower()
    if "chair" in t:
        return E.bench_finish(s, "chair")
    if "log" in t or "read" in t:
        return E.bench_finish(s, "count")
    if "take the chip" in t or "chip out" in t or "reach up" in t:
        return E.bench_finish(s, "unseat")
    if "back out" in t or "turn it round" in t:
        return E.bench_finish(s, "back")
    return E.bench_finish(s, "bench")


# every act ends at exactly one of these, and each one owns its own set of labels
TERMINALS = {
    "the_line": _line_choice,
    "the_house": _house_choice,
    "the_throat": _throat_choice,
    "the_chamber": _chamber_choice,
    "the_bench": _bench_choice,
}


def _close(s, key, text, out):
    """Finish the run and hand back the final frame.

    Getting to the end of a region alive is what opens the one below it, and the unlock is
    written to disk, so it survives the run that earned it."""
    if key is None:
        # it did not die. E.die() handed back a reprieve instead of an ending, and the run
        # carries on from here with a window open - see lastbreath.py.
        s.activity = "up again, briefly"
        s.last_result = text
        return R.frame(s, ((out + "\n\n") if out else "") + text)
    s.activity = "over: " + key
    s.last_result = text
    finished = E.finished_region(key)
    # The UNLOCK is unconditional on finishing and it is permanent: reaching the end of the
    # core with a subject opens that subject's history and its DESTINY for good, on disk,
    # whatever state the body was in when it got there.
    unlocked = (REG.beat(s.region, getattr(s, "subject", None), REG.on_destiny(s))
                if finished else None)
    carry_on, why_not = (False, "")
    if finished:
        carry_on, why_not = E.walks_on(s, key)
        REG.record_win(s, key, E.OUTCOME.get(key, ("", ""))[0], carry_on)
        # Destiny does not carry at all, in either direction: every act of it is a different
        # world and a different body on it. A Destiny finish must neither write a snapshot
        # (a later NORMAL act would pick it up) nor clear one (it would wipe a legitimate
        # normal carry this subject earned).
        if not REG.on_destiny(s):
            if carry_on:
                REG.store_carry(s)      # the next act starts in this body, not a clean one
            else:
                # it finished, and it is not walking anywhere from here. Do not leave an
                # older snapshot lying about for the next act to pick up.
                REG.clear_carry(getattr(s, "subject", ""))
    if REG.on_final(s):
        # whichever way it ended, the slot goes. Finishing leaves nothing to pick up,
        # and dying past the repair limit must not be undoable by loading the last
        # checkpoint - six repairs is the budget for the whole act.
        REG.clear_final(getattr(s, "subject", ""))
    nxt_key = REG.next_key(s.region)
    body = ((out + "\n\n") if out else "") + text + "\n\n" + E.scorecard(s)
    if unlocked:
        nxt = REG.BY_KEY[unlocked]
        body += ("\n\nREGION FINISHED. UNLOCKED: %s - %s\n  %s\n  Start it with:  "
                 ".\\run.bat new %s <subject>"
                 % (nxt["name"], nxt["label"], nxt["brief"], unlocked))
    elif finished and nxt_key:
        body += ("\n\nREGION FINISHED. %s is already open to you.  .\\run.bat new %s <subject>"
                 % (REG.BY_KEY[nxt_key]["name"], nxt_key))
    elif finished and not nxt_key:
        body += ("\n\nREGION FINISHED. There is nothing under the core. That is the whole "
                 "planet, and it has been walked.")
        who = SUB.name(s)
        body += ("\n\n  %s'S HISTORY IS OPEN. It is on the picker now - what it was before the "
                 "chip, and what was done to it. Nobody was ever going to tell it.\n"
                 "  DESTINY IS OPEN TO %s. Every dial again, harder, and nothing held back: "
                 "the hell arrives on the surface, the link fails on its own, and what the act "
                 "was going to spare you it does not.\n"
                 "    .\\run.bat new outside %s destiny\n"
                 "  It is open to this one and to nothing else, it is written to disk, and it "
                 "stays open from here on whatever happens in any run after this."
                 % (who.upper(), who.upper(), getattr(s, "subject", "")))
    # finishing the bottom of DESTINY is what opens the last tier, and the frame has to
    # say so - it is the only place the player is ever told the Final exists.
    if (finished and REG.on_destiny(s) and not REG.on_final(s)
            and s.region == REG.ORDER[-1]):
        body += ("\n\n  %s IS OPEN TO %s. Not another ruleset and not another planet: it "
                 "is the building, entered from the grass outside the fence, and it is "
                 "long. It writes itself down as it goes and it can be put down and "
                 "picked up.\n    .\\run.bat new %s final"
                 % (REG.FINAL_NAME, SUB.name(s).upper(), getattr(s, "subject", "")))
    if finished and REG.on_final(s):
        st = getattr(s, "fstate", {}) or {}
        n = int(st.get("wear", 0))
        body += ("\n\n  THAT IS THE LAST GROUND THERE IS. There is no act under this one, "
                 "no ruleset behind it and nothing left to open. It went to the horizon, "
                 "and to the bottom of the world, and across another one, and down "
                 "through the dug rock under that - and then it walked back in through "
                 "the fence it spent every other act on the wrong side of.\n"
                 "  It was put back together %d time%s on the way here, and the count "
                 "went up by exactly that much." % (n, "" if n == 1 else "s"))
    elif finished and REG.on_destiny(s):
        body += ("\n\n  NOTHING CARRIES OUT OF %s. Every act of it is a different world with a "
                 "different body put down on it, and what this one learned, carried and "
                 "survived stops here with it." % REG.DESTINY_NAME)
    elif finished:
        if carry_on:
            body += ("\n\n  THIS BODY WALKS ON. It is alive, it is free, and it is standing. "
                     "Whatever it is carrying and whatever is wrong with it comes with it into "
                     "the next act - there is no clean room and no calibration waiting.")
        else:
            body += ("\n\n  THIS BODY DOES NOT WALK ON: %s.\n"
                     "  The finish counts and the unlock is permanent. The next act just "
                     "starts with a fresh one instead of this one." % why_not)
    elif nxt_key:
        why = E.NOT_A_FINISH.get(key)
        if why:
            body += ("\n\nNOT A FINISH. %s stays shut: %s.\n  It is still an ending, and two "
                     "of the ways out of here are wins. But the ground underneath only opens "
                     "to something that went all the way to the end of this one."
                     % (REG.BY_KEY[nxt_key]["name"], why))
        else:
            body += ("\n\n%s stays shut - this run did not reach the end of %s."
                     % (REG.BY_KEY[nxt_key]["name"], REG.name(s)))
    return R.frame(s, body, show_cmds=False)


# -------------------------------------------------------------------- dispatch
def step(s, raw):
    raw = (raw or "").strip()
    if not raw:
        return R.frame(s, "(no command)")
    if s.over:
        return R.frame(s, "This run is already over: %s\n\n%s\n\n%s\n\nStart another with:  "
                          "run.bat new" % (s.ending, s.ending_text, E.scorecard(s)),
                       show_cmds=False)
    s.turn += 1
    s.last_command = raw
    s.feedback = []
    low = raw.lower()
    # the watch window's record should read as a transcript of the two of you, so the order
    # goes in the log beside what it did about it
    if low.split() and low.split()[0] not in (
            "look", "l", "status", "inv", "i", "inventory", "map", "issues", "timers",
            "recipes", "recipe", "truths", "listen", "think", "help", "?", "commands",
            "log", "history", "region", "scene", "where"):
        s.note("YOU SENT: " + raw.strip())

    # ---- it is on the ground. Nothing in the normal command set reaches it from here.
    if s.crisis:
        cmd = low.split()[0] if low.split() else "check"
        if cmd in ("help", "?", "commands"):
            s.turn -= 1
            return R.frame(s, "While it is down you have only: %s.\n  Everything else has to "
                              "wait until it is upright." % ", ".join(CR.ACTIONS))
        if cmd in ("persuade", "please", "reason", "plead", "convince"):
            s.feedback.append("It is on the ground. Reasoning with it is not a plan down here - "
                              "all that reaches it is the link, held open, which is 'speak'.")
            cmd = "speak"
        text, death = CR.act(s, cmd)
        s.last_result = text
        if death:
            key, dtext = E.die(s, death[0], death[1])
            return _close(s, key, dtext, text)
        return R.frame(s, text)

    # ---- the link is off. Orders do not arrive, so there is nothing to carry one. Time
    #      still runs, and it still does things - its own things.
    if LK.is_down(s):
        cmd = low.split()[0] if low.split() else "wait"
        if cmd in ("reconnect", "relink", "reseat", "retry"):
            txt = LK.reconnect(s)
            s.last_result = txt
            fb, ending = T.tick(s, 1)
            s.feedback.extend(fb)
            for ln in LK.tick(s):
                s.feedback.append(ln)
            if ending:
                key, dtext = E.die(s, ending[0], ending[1])
                return _close(s, key, dtext, txt)
            onset = CR.roll(s, "reconnect")
            if onset:
                s.feedback.append(onset)
            return R.frame(s, txt)
        if cmd in ("help", "?", "commands", "log", "history", "think", "monologue", "mind"):
            s.turn -= 1
            return R.frame(s, "\n".join(LK.banner(s)))
        txt = LK.autopilot(s)
        s.activity = "out of contact"
        s.last_result = txt
        s.feedback.append("THAT DID NOT GO ANYWHERE. '%s' went down a link that is not "
                          "connected to anything. The turn happened anyway." % cmd)
        fb, ending = T.tick(s, 1)
        s.feedback.extend(fb)
        for ln in LK.tick(s):
            s.feedback.append(ln)
        lb_lines, lb_end = LB.tick(s)
        s.feedback.extend(lb_lines)
        if lb_end:
            key, dtext = E.die(s, lb_end[0], lb_end[1], forced=True)
            return _close(s, key, dtext, txt)
        if ending:
            key, dtext = E.die(s, ending[0], ending[1])
            return _close(s, key, dtext, txt)
        death = B.check_fail(s, W.danger(s))
        if death:
            key, dtext = E.die(s, death[0], death[1])
            return _close(s, key, dtext, txt)
        onset = CR.roll(s, "_own")
        if onset:
            s.feedback.append(onset)
        return R.frame(s, txt)

    # ---- 'override <command>' wraps whatever follows it. The cost is charged below, only
    #      once we know the order is actually going to be attempted.
    # what the turn looked like before it happened, so intent.py can compare afterwards
    from . import intent as INT
    INT.before(s)
    forced = False
    if low.split(None, 1)[0] in ("override", "force", "compel"):
        rest = low.split(None, 1)
        if len(rest) < 2:
            return R.frame(s, "Override what? Give it the order to force, e.g. 'override go'.")
        forced = True
        low = rest[1].strip()

    parts = low.split(None, 1)
    verb = parts[0]
    arg = parts[1].strip() if len(parts) > 1 else ""
    if verb == "cut":
        verb, arg = ("cutchip", "") if arg.startswith("chip") else ("cuthint", "")

    had_scene = s.scene is not None
    answered = False
    out = None
    no_time = False

    # ---- calibration gate. A locked door does not care how hard you push the link, so this
    #      comes before the override is paid for.
    block = TUT.blocked(s, verb, s.distance)
    if block:
        if forced:
            block += ("\n  Forcing it changes nothing here, so the link was not spent on it.")
        s.feedback.append(block)
        s.activity = "held at the Holding door"
        s.last_result = block
        return R.frame(s, block)
    # ---- some of them hold the channel shut. This is not a refusal and override does not
    #      answer it, so it is checked before the override is paid for.
    if TUT.done(s):
        blocked, gtext = LK.guard_check(s, verb, forced)
        if blocked and forced:
            # it shut the channel on an order you were leaning on. That is the clearest
            # reading it ever gets of what you were about to do with it.
            from . import intent as _INT
            _INT._set(s, _INT.get(s) + 7.0 * SUB.trait(s, "insight"))
        if blocked:
            B.tick(s, 10)
            s.feedback.append(gtext)
            s.activity = "will not carry: " + verb
            fb, ending = T.tick(s, 1)
            s.feedback.extend(fb)
            if ending:
                key, text = E.die(s, ending[0], ending[1])
                return _close(s, key, text, gtext)
            s.last_result = gtext
            return R.frame(s, gtext)
    if forced:
        s.feedback.append(WILL.override(s))
        if LK.is_down(s):
            s.last_result = s.feedback[-1]
            return R.frame(s, s.feedback[-1])
    # some of them have an opinion about the order itself - but reasoning with it is not an
    # order, and it gets its own answer further down
    pro = None if verb in PERSUADE_VERBS else V.protest(s, verb, forced)
    if pro:
        s.feedback.append(pro)
    aid = TUT.assist(s)
    if aid:
        s.feedback.append(aid)

    # ---- will it even do it?  (never during calibration - step 8 is where that is taught)
    if not forced and TUT.done(s):
        danger = s.scene["danger"] if s.scene else 0.0
        refused, reason = WILL.refuses(s, verb, danger)
        if refused:
            B.tick(s, 18, resting=True)
            txt = WILL.refusal_text(s, verb, reason)
            s.feedback.append(txt)
            s.activity = "refusing: " + verb
            fb, ending = T.tick(s, 1)
            s.feedback.extend(fb)
            if ending:
                key, text = E.die(s, ending[0], ending[1])
                return _close(s, key, text, txt)
            s.last_result = txt
            return R.frame(s, txt)

    # ---- does it even do what you said, or something of its own?
    own_fb, own_res = _autonomy(s, verb)
    if own_fb:
        s.feedback.append(own_fb)
        out = own_res
        no_time = False
        s.activity = "acting on its own"
        verb = "_own"

    # ---- numbered option?
    num = None
    if verb.isdigit():
        num = int(verb)
    elif verb in ("choose", "pick", "opt", "option") and arg.split():
        try:
            num = int(arg.split()[0])
        except ValueError:
            num = None

    if verb == "_own":
        pass                      # it already did something of its own; out is set
    elif num is not None:
        if s.question and not s.scene:
            # it asked you something and nothing else is pending - take the bare number for it
            out = V.answer(s, num)
            s.activity = "answering it"
        elif not s.scene:
            out, no_time = ("Nothing is waiting on an answer. Try 'go'." if not s.question
                            else "Answer its question with 'say %d', not '%d'." % (num, num)), True
        elif s.scene["sid"] in ("cradle", "whybattery"):
            if 1 <= num <= len(s.scene["opts"]):
                label = s.scene["opts"][num - 1]
                sid = s.scene["sid"]
                s.scene = None
                key, text = (_cradle_choice(s, label) if sid == "cradle"
                             else _why_choice(s, label))
                if key:
                    return _close(s, key, text, "")
                out, no_time = "", True
            else:
                out, no_time = "There is no option %d." % num, True
        elif s.scene["sid"] in ("the_line", "the_house", "the_throat", "the_chamber"):
            if 1 <= num <= len(s.scene["opts"]):
                label = s.scene["opts"][num - 1]
                sid = s.scene["sid"]
                s.scene = None
                key, text = TERMINALS[sid](s, label)
                return _close(s, key, text, "")
            out, no_time = "There is no option %d." % num, True
        else:
            out = SCN.choose(s, num)
            answered = True
            s.activity = "answered option %d" % num

    elif verb in MOVE:
        if s.escape.get("active"):
            out = ESC.push(s)
            s.activity = "getting clear of the route"
        else:
            out = W.advance(s)
            s.activity = "moving forward"
    elif verb in ("gather", "search", "scavenge", "forage", "loot"):
        out = W.gather(s)
        s.activity = "gathering"
        if not ESC.known_here(s) and s.rng.random() < 0.18:
            found = ESC.find_route(s)
            if found:
                s.feedback.append(found)
    elif verb in ("camp", "sleep"):
        out = W.camp(s, _num(arg, 6.0))
        s.activity = "sleeping"
    elif verb == "rest":
        h = _num(arg, 1.0)
        B.tick(s, int(h * 60), resting=True, cold=W.cold(s))
        out = "You rest %.1f hours without making camp." % h
        s.activity = "resting"
    elif verb in ("shelter", "build"):
        # in the Final a made place is also where the act saves, so it is worth more
        # than it is out on the route
        if REG.on_final(s):
            out = TB.shelter(s)
            if s.eff("sheltered"):
                REG.save_final(s, W.zone(s)["name"] + " (shelter)")
        else:
            out = W.build_shelter(s)
        s.activity = "building shelter"
    elif verb in ("pack", "plug", "stuff"):
        from . import mortal as MO
        out = MO.pack_chest(s)
        s.activity = "packing a hole"
    elif verb in ("tend", "bind", "treat", "patch"):
        limb = resolve_limb(s, arg)
        out = I.tend(s, limb) if limb else "Tend which limb? (%s)" % ", ".join(LIMB_ORDER)
        no_time = limb is None
        s.activity = "tending " + (limb or "nothing")
    elif verb == "graft":
        limb = resolve_limb(s, arg)
        if not limb:
            out, no_time = "Graft onto which limb?", True
        elif not I.has(s, "strut"):
            out, no_time = "You have no strut. Craft one: scrap x2, cord x2, resin x1.", True
        elif s.limbs[limb]["state"] != "lost":
            out, no_time = B.graft_strut(s, limb), True
        else:
            I.take(s, "strut")
            out = B.graft_strut(s, limb)
            B.tick(s, 40, exertion=1.2)
        s.activity = "grafting"
    elif verb == "craft":
        if not arg:
            out, no_time = "Craft what? Try 'recipes'.", True
        else:
            out = I.craft(s, arg)
        s.activity = "crafting " + arg
    elif verb in ("recipes", "recipe"):
        can = I.craftable(s)
        lines = ["RECIPES (you can make now: %s)" % (", ".join(can) if can else "nothing")]
        for k, r in sorted(I.RECIPES.items()):
            need = ", ".join("%s x%d" % (a, b) for a, b in r["need"].items())
            lines.append("  %-10s <- %-34s [%d arm%s]"
                         % (k, need, r["arms"], "" if r["arms"] == 1 else "s"))
        out, no_time = "\n".join(lines), True
    elif verb in ("use", "eat", "drink", "apply", "read"):
        if verb == "drink" and not arg:
            arg = "water"
        item = resolve_item(s, arg)
        out = I.use(s, item) if item else "You have no %s." % (arg or "that")
        no_time = item is None
        s.activity = "using " + (item or "nothing")
    elif verb in ("inv", "i", "inventory", "bag"):
        out = "CARRY %d/%d\n%s" % (B.load_of(s), B.carry_cap(s), I.inv_line(s))
        for k in sorted(s.inv):
            out += "\n  %-10s %s" % (k, I.CATALOG.get(k, ""))
        no_time = True
    elif verb == "drop":
        item = resolve_item(s, arg)
        out = ("You put down the %s." % item) if (item and I.take(s, item)) \
            else "You are not carrying that."
        no_time = True
    elif verb in ("say", "reply", "tell", "answer"):
        n = None
        if arg.split():
            try:
                n = int(arg.split()[0])
            except ValueError:
                n = None
        if n is None:
            if s.question:
                out = "\n".join(V.pending_lines(s))
            else:
                out = ("It has not asked you anything. When it does, reply with 'say 1', "
                       "'say 2' and so on.")
            no_time = True
        else:
            out = V.answer(s, n)
            no_time = s.question is not None
        s.activity = "answering it"
    elif verb in ("listen", "heard", "voice", "said"):
        ls = V.last_said(s, 8)
        out = ("WHAT IT HAS BEEN SAYING\n" + "\n".join('  "%s"' % x for x in ls)) \
            if ls else "It has not said anything yet."
        no_time = True
    elif verb in PERSUADE_VERBS:
        fb, ctx = P.attempt(s, arg)
        ln = V.respond(s, ctx) if ctx else None
        out = fb + (("\n" + ln) if ln else "")
        no_time = True
        s.activity = "reasoning with it"
    elif verb in ("reassure", "calm", "settle"):
        out = WILL.reassure(s)
        LK.calmed(s, 5.0)
        s.activity = "holding the link open"
    elif verb in ("wins", "board", "finished"):
        out, no_time = "\n".join(REG.wins_lines()), True
    elif verb in ("reconnect", "relink", "reseat"):
        out, no_time = LK.reconnect(s), True
        s.activity = "re-seating the link"
    elif verb in ("mend", "patch phones", "phones"):
        from . import phones as PH
        out, no_time = PH.mend(s), not PH.wants_repair(s)
        s.activity = "patching the shell"
    elif verb in ("disconnect", "letgo", "godark", "dark"):
        out, no_time = LK.go_dark(s, _num(arg, 3)), True
        s.activity = "letting go of it"
    elif verb in ("recalibrate", "calibrate", "diagnostic"):
        out = WILL.recalibrate(s)
        s.activity = "recalibrating the chip"
    elif verb == "escape":
        out = ESC.begin(s)
        s.activity = "leaving the route"
    elif verb in ("hide", "evade", "cover"):
        # out on the route hiding is about the handlers looking for an escapee. Inside
        # the building it is about the sweep, which is looking for anything at all.
        out = TB.hide(s) if REG.on_final(s) else ESC.hide(s)
        s.activity = "hiding"
    elif verb == "cutchip":
        key, text = ESC.cut_chip(s)
        if key:
            k, t = E.end_with(s, key)
            return _close(s, k, t, "")
        out, no_time = text, True
        s.activity = "cutting at the chip"
    elif verb == "cuthint":
        out = ("Cut what? The only thing you can cut out of it is the chip: 'cut chip'."
               "\n  That ends your control of it. Read the consequences before you do that.")
        no_time = True
    elif verb in ("leave", "put it down", "stop for now"):
        if not REG.on_final(s):
            out = ("Only the last act can be put down and picked up. Everything else is one "
                   "sitting, and the save carries it between turns anyway.")
            no_time = True
        else:
            REG.save_final(s, W.zone(s)["name"] + " (put down)")
            st = getattr(s, "fstate", {}) or {}
            out = ("PUT DOWN. The run is written to %s's slot: %s, %.1f of %.0f, count %d, "
                   "repairs %d.\n"
                   "  It goes and sits in the back of the room out of the line of the doors, "
                   "and it does not ask how long.\n"
                   "  Pick it up with:  .\\run.bat new %s final"
                   % (SUB.name(s), W.zone(s)["name"], s.distance, W.goal(s),
                      int(st.get("count", 0)), int(st.get("wear", 0)),
                      getattr(s, "subject", "")))
            no_time = True
    elif verb in ("region", "regions", "act", "where"):
        r = REG.info(s)
        on = [k for k in ("complications", "bags", "medical_hell", "escape") if r.get(k)]
        out = ("%s - %s\n  %s\n\n  goal: %s at %.0f\n  switched on here: %s\n\n%s"
               % (r["name"], r["label"], r["brief"],
                  REG.goal_kind(s) if REG.on_final(s) or REG.on_destiny(s) else
                  ("the battery" if r["goal_kind"] == "battery" else "the horizon line"),
                  W.goal(s), ", ".join(on) if on else "nothing beyond the basics",
                  REG.roster(s.region)))
        no_time = True
    elif verb in ("subject", "subjects", "who", "roster"):
        out = ("The chip is currently seated in %s.\n\n%s"
               % (SUB.name(s), SUB.roster(s.subject)))
        no_time = True
    elif verb in ("issues", "problems", "complications"):
        ls = ISS.lines(s)
        out = ("ACTIVE ISSUES\n" + "\n".join(ls)) if ls else "No complications right now."
        no_time = True
    elif verb in ("timers", "clocks", "timed"):
        ls = T.lines(s)
        out = ("ON THE CLOCK\n" + "\n".join(ls)) if ls else "Nothing is on a countdown."
        no_time = True
    elif verb in ("think", "monologue", "mind"):
        out = M.think(s)
        s.activity = "thinking"
    elif verb in ("truths", "know", "self-knowledge"):
        out = ("What it is sure of:\n" + "\n".join("  - " + t for t in s.truths)) \
            if s.truths else "It is sure of nothing about itself."
        no_time = True
    elif verb in ("status", "self", "body", "condition"):
        out, no_time = _status(s), True
    elif verb in ("look", "l", "where", "scene"):
        out, no_time = W.zone(s)["blurb"], True
    elif verb == "map":
        out, no_time = _map(s), True
    elif verb in ("help", "?", "commands"):
        out, no_time = HELP, True
    elif verb in ("log", "history"):
        out = "\n".join("  t%-4d %s" % (t, x) for t, x in s.log[-14:]) or "(nothing yet)"
        no_time = True
    else:
        out = "You do not know how to '%s'. Type 'help'." % verb
        no_time = True

    # ---- calibration progress
    tut = TUT.check(s, verb, arg)
    if tut:
        s.feedback.append(tut)

    # ---- complications and clocks
    extra = []
    if not no_time:
        mins = 30
        s.feedback.extend(P.tick(s))
        s.feedback.extend(ISS.materialise(s))
        s.feedback.extend(ISS.resolve(s, verb, arg))
        ISS.roll(s, mins)
        s.feedback.extend(ISS.hell(s, mins))
        s.feedback.extend(ISS.deep_complications(s, mins))
        s.feedback.extend(ISS.tick(s, mins))
        # the borrowed turns run down here, and when they run out they either hold or they
        # kill - and that death is forced, because there is no getting up from it twice
        lb_lines, lb_end = LB.tick(s)
        s.feedback.extend(lb_lines)
        if lb_end:
            key, text = E.die(s, lb_end[0], lb_end[1], forced=True)
            return _close(s, key, text, out)
        s.feedback.extend(IN.tick(s))
        s.feedback.extend(LK.fault_roll(s, mins))
        spawn = T.maybe_spawn(s, W.zone(s)["key"], verb)
        if spawn:
            s.feedback.append(spawn)
        # something acute, which suspends everything else
        onset = CR.roll(s, verb)
        if onset:
            s.feedback.append(onset)
            s.last_result = onset
            return R.frame(s, (out or "") + "\n" + onset)
        fb, ending = T.tick(s, 1)
        s.feedback.extend(fb)
        if ending:
            if ending[0] == "CAUGHT":
                key, text = E.end_with(s, "CAUGHT")
            else:
                key, text = E.die(s, ending[0], ending[1])
            return _close(s, key, text, out)

    # ---- escape resolution
    if ESC.complete(s):
        key = "CUT LOOSE" if s.escape.get("chip_cut") else "OFF THE LEASH"
        k, t = E.end_with(s, key)
        return _close(s, k, t, out)

    # ---- scene pressure
    if had_scene and not answered and not no_time:
        esc = SCN.escalate(s)
        if esc:
            extra.append(esc)
        if SCN.expired(s, verb):
            extra.append(SCN.leave_behind(s))

    fail = B.check_fail(s, danger=W.danger(s))
    if fail:
        key, text = E.die(s, fail[0], fail[1])
        return _close(s, key, text, out)

    if s.distance >= W.goal(s) and not s.over and not s.escape.get("active"):
        kind = REG.goal_kind(s)
        if kind == "battery":
            if not s.has_flag("battery_lifted"):
                s.scene = _the_cradle(s)
        elif kind == "house":
            s.scene = RK.the_house(s)
        elif kind == "descent":
            s.scene = WR.the_throat(s)
        elif kind == "chamber":
            s.scene = WR.the_chamber(s)
        elif kind == "bench":
            s.scene = TB.the_bench(s)
        else:
            s.scene = _the_line(s)
    elif not s.scene and not no_time and not s.escape.get("active"):
        # the ground gets first refusal on a move - a trap is decided before any encounter is
        # rolled, because it was decided before either of you arrived
        sprung = TR.roll(s, verb)
        if sprung:
            extra.append(sprung)
        if not s.scene:
            sc = SCN.pick(s, SCENE_ODDS.get(verb, 0.10))
            if sc:
                s.scene = sc

    # ---- what it says about all this
    extra.extend(V.flush(s))
    if not no_time:
        nag = V.nag(s)
        if nag:
            s.feedback.append(nag)
        amb = V.ambient(s, verb)
        if amb:
            extra.append(amb)
        if TUT.done(s) and not s.question:
            ask = V.maybe_ask(s)
            if ask:
                s.feedback.append(ask)
        amb2 = M.maybe(s)
        if amb2:
            extra.append("(" + amb2 + ")")
        # Behaviour, not commentary - no parentheses, because this is a thing that
        # happened rather than a thing the chip thought about.
        obs = TE.maybe(s)
        if obs:
            extra.append(obs)
        # and what it made of the order it has just been given
        crossed = INT.after(s, verb, forced)
        if crossed:
            extra.append(crossed)
        # the building is still looking for loose subjects, on a schedule
        if REG.on_final(s) and not s.over:
            for ln in TB.sweep_tick(s, W.zone(s)["key"]):
                extra.append(ln)

    body_text = out or ""
    if extra:
        body_text += "\n" + "\n".join(extra)
    s.last_result = body_text.strip()
    return R.frame(s, body_text)


def _num(arg, default):
    try:
        return max(0.25, min(14.0, float(arg.split()[0])))
    except Exception:
        return default


def _status(s):
    L = ["CONDITION   %s | %s | %s"
         % (B.condition_word(s), WILL.mood_word(s), WILL.link_word(s))]
    L.append("VITALS      blood %.0f | strain %.0f | fatigue %.0f | pain %.0f | infection %.0f"
             % (s.blood, s.strain, s.fatigue, s.pain, s.infection))
    L.append("            thirst %.0f | hunger %.0f | warmth %.0f | wrongness %.0f"
             % (s.thirst, s.hunger, s.warmth, s.weird))
    L.append("CHIP        will %.0f | mood %.0f | link integrity %.0f%%"
             % (s.will, s.mood, s.chip))
    for n in LIMB_ORDER:
        Lb = s.limbs[n]
        tags = []
        if Lb["bound"]:
            tags.append("bound")
        if Lb["bleed"] > 0:
            tags.append("bleeding %.2f/min" % Lb["bleed"])
        if Lb["strut"]:
            tags.append("strut fitted")
        L.append("  %-10s %-8s hp %3.0f %s" % (n, Lb["state"], Lb["hp"],
                                               ("[" + ", ".join(tags) + "]") if tags else ""))
    st, mins = B.move_cost(s)
    L.append("MOBILITY    %d arms, %d legs usable | %.2f distance per push, %d min"
             % (B.arms_usable(s), B.legs_usable(s), st, mins))
    L.append("CARRY       %d / %d" % (B.load_of(s), B.carry_cap(s)))
    if s.effects:
        L.append("EFFECTS     " + ", ".join("%s %dm" % (k, v) for k, v in s.effects.items()))
    if s.issues:
        L.append("ISSUES")
        L.extend(ISS.lines(s))
    L.append("KNOWN       %d of 6 truths" % len(s.truths))
    return "\n".join(L)


def _map(s):
    L = ["%s - %s  (you are at %.1f of %.0f)"
         % (REG.name(s), REG.info(s)["label"], s.distance, W.goal(s))]
    here = W.zone(s)
    known = s.escape.get("known") or []
    for z in W.zones(s):
        mark = ">>" if z is here else "  "
        seen = "seen" if s.distance >= z["at"] else "ahead"
        route = "  [way out known]" if z["key"] in known else ""
        L.append("%s %-18s from %5.1f  danger %.2f  %s%s"
                 % (mark, z["name"], z["at"], z["danger"], seen, route))
    L.append("   %-18s at %5.1f" % (
        "THE BATTERY" if REG.goal_kind(s) == "battery" else "THE HORIZON", W.goal(s)))
    if s.escape.get("active"):
        L.append("   - you are OFF this line now. 'go' buys distance from it, not along it.")
    return "\n".join(L)
