#!/usr/bin/env python3
"""HORIZONS - entry point.

    run.bat                  play interactively (also fine with piped stdin)
    run.bat new              start a fresh run, open the watch window
    run.bat new crust 3      pick region and subject (regions unlock as you finish them)
    run.bat lore 680         read a subject's history, once it has walked the core
    run.bat cmd go           apply ONE command to the saved run, print the frame, save
    run.bat watch            open the watch window only
    run.bat auto 300         let the built-in bot play the saved run (smoke test / demo)
    run.bat status           print the current frame without changing anything

The 'cmd' mode is what an outside agent should use: every call is a complete turn, so the
process never blocks waiting on input.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from hz import body as B                     # noqa: E402
from hz import commands as C                 # noqa: E402
from hz import items as I                    # noqa: E402
from hz import link as LK                    # noqa: E402
from hz import render as R                   # noqa: E402
from hz import regions as REG
from hz import subjects as SUB               # noqa: E402
from hz import tutorial as TUT               # noqa: E402
from hz import watcher as WATCH              # noqa: E402
from hz import will as WILL                  # noqa: E402
from hz import world as W                    # noqa: E402
from hz.state import SAVE_PATH, State, save_exists   # noqa: E402


# ------------------------------------------------------------------ watch window
def launch_watcher(quiet=False):
    """Start the Tk watch window as its own detached process, once."""
    if os.environ.get("HORIZONS_NO_WATCH"):
        return False
    if WATCH.already_running():
        return False
    import subprocess
    exe = sys.executable or "python"
    pyw = exe.replace("python.exe", "pythonw.exe")
    if os.path.exists(pyw):
        exe = pyw
    flags = 0
    if os.name == "nt":
        flags = 0x00000008 | 0x00000200        # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    try:
        subprocess.Popen([exe, os.path.join(HERE, "horizons.py"), "watch"],
                         creationflags=flags, close_fds=True,
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, cwd=HERE)
        if not quiet:
            print("[watch window opening in its own Python window]")
        return True
    except Exception as e:
        if not quiet:
            print("[could not open watch window: %s]" % e)
        return False


# ------------------------------------------------------------------ helpers
def new_game(seed=None, subject=None, region=None, destiny=False, final=False):
    s = State(seed=seed)
    reg = REG.resolve(region) or REG.BY_KEY[REG.DEFAULT]
    REG.apply_start(s, reg, destiny, final)
    sub = SUB.resolve(subject) or SUB.BY_ID[SUB.DEFAULT]
    SUB.apply_start(s, sub)
    # Continuing down in normal: the same body walks on into the next act with what it had.
    # Destiny never carries - it is a different world and a different body on it.
    carried = None
    resumed = None
    if final:
        # the only act in the game that is picked up rather than started
        slot = REG.final_slot(sub["id"])
        if slot:
            resumed = REG.apply_final_slot(s, slot)
    if not destiny and reg["key"] != REG.DEFAULT:
        snap = REG.take_carry(sub["id"])
        if snap and snap.get("from_region") != reg["key"]:
            carried = REG.apply_carry(s, snap)
            REG.clear_carry(sub["id"])
    if carried:
        s.note("It came down into %s on its own legs, carrying its own kit." % reg["name"])
        s.activity = "carrying on, one act further down"
        s.carried_in = True
    elif resumed:
        s.note("It was where it was left.")
        s.activity = "picking it back up"
        s.feedback = list(resumed)
    elif final:
        s.note("It comes round in long grass, a hundred paces outside a fence it knows.")
        s.inner("You have been walked away from this in every direction there is.")
        s.activity = "outside the wire"
    elif destiny:
        s.note("It comes round on bare rock, under a sky that is the wrong colour.")
        s.inner("This is not the room. This has never been the room.")
        s.activity = "awake somewhere else"
    else:
        s.note("You wake up on a clean floor in a room with the lights still on.")
        s.inner("You do not remember being anywhere before this.")
        s.activity = "waking up - chip not yet calibrated"
    TUT.setup(s)
    if carried:
        s.feedback = list(carried)
    s.save()
    return s


def load_or_new(seed=None):
    if save_exists():
        try:
            return State.load()
        except Exception:
            pass
    return new_game(seed)


def _final_bot(s):
    """Shut door -> make the thing that opens it, and get out of the way of the sweep."""
    from hz import thebuilding as TB
    from hz import world as W
    from hz import items as I
    from hz import body as B

    st = getattr(s, "fstate", {}) or {}
    # one turn of warning before the sweep comes through, and hiding is a whole turn
    if int(st.get("sweep_at", 0)) - s.turn == 1 and not s.eff("sheltered"):
        return "hide"

    step, _m = B.move_cost(s)
    nxt = W.zone_at(s, min(W.goal(s), s.distance + step))
    if nxt["key"] == W.zone(s)["key"]:
        return None
    shut, _why = TB.gate_for(s, nxt["key"])
    if not shut:
        return None
    for want in TB.GATES[nxt["key"]]["any"]:
        if want not in I.RECIPES:
            continue
        need = I.RECIPES[want]["need"]
        missing = [k for k, v in need.items() if not I.has(s, k, v)]
        if not missing:
            return "craft " + want
        return "gather"
    # nothing craftable answers this door - it is found or learned, so keep turning the
    # ground over until something in here produces it
    return "gather"


# ------------------------------------------------------------------ the bot
def bot_command(s):
    """A plain heuristic player, used by 'auto'. Keeps itself alive, answers scenes, walks."""
    r = s.rng

    # The Final is the one act where walking into the next ground is not automatic, so
    # the bot needs to know that a shut door is a crafting problem. It reads the gate
    # table rather than naming any tool, the same way it reads the issue table rather
    # than naming conditions.
    if REG.on_final(s) and not s.crisis and not s.scene:
        cmd = _final_bot(s)
        if cmd:
            return cmd

    # nothing reaches it while the link is off, so there is exactly one thing worth sending
    if LK.is_down(s):
        return "reconnect"

    # on the ground: nothing else matters, and the clock is in seconds
    if s.crisis:
        k = s.crisis["kind"]
        if k == "tachy":
            return "calm"
        if k == "edema":
            return "drain" if not s.crisis["drained"] else "breathe"
        if k == "apnea":
            return "breathe"
        if k == "catatonia":
            return "speak"
        if k == "freeze":
            return "warm" if s.crisis["warmed"] < 3 else "pulse"
        if k == "faint":
            return "check"
        return "pulse"

    # calibration first - the door will not open otherwise
    if not TUT.done(s):
        return TUT.current(s)["cmd"]

    # a will-block is not a refusal and override does not answer it - fix what it is looking
    # at instead, and if there is nothing to fix, make the case
    if s.last_result.startswith("ITS WILL PREVENTS"):
        if B.bleed_rate(s) > 0.05:
            return "tend " + max(s.limbs, key=lambda n: s.limbs[n]["bleed"])
        if s.thirst > 70 and I.has(s, "water"):
            return "use water"
        if s.hunger > 72 and (I.has(s, "ration") or I.has(s, "meat")
                              or I.has(s, "dust fungus")):
            for food in ("ration", "meat", "dust fungus"):
                if I.has(s, food):
                    return "use " + food
        if s.fatigue > 70:
            return "camp 6"
        if s.issues:
            return s.issues[0]["fix"]
        return "persuade please keep going because the line is not far and stopping here is worse"

    # if it just refused, do not simply repeat the order
    if s.last_result.startswith("REFUSED"):
        verb = s.last_command.split()[0] if s.last_command else "go"
        if s.weird > 50:
            return "recalibrate"
        if not s.eff("reassured"):
            return "reassure"
        return "override " + (s.last_command or "go")

    # if it asked you something, answer it - it is waiting and it will not wait long
    if s.question:
        return "say %d" % r.randint(1, len(s.question["opts"]))

    # whatever is on a countdown outranks everything else
    for t in sorted(s.timers, key=lambda x: x["left"]):
        if t["left"] > 3:
            continue
        if t["id"] == "bleedout":
            limb = max(s.limbs, key=lambda n: s.limbs[n]["bleed"])
            return "tend " + limb
        if t["id"] == "chipwindow":
            return "recalibrate"
        if t["id"] == "storm" and not s.eff("sheltered"):
            return "shelter"
        if t["id"] == "stalker" and not s.eff("fire") and I.has(s, "torch"):
            return "use torch"
        if t["id"] == "recall" and not s.eff("hidden"):
            return "hide"

    # clear complications before they compound
    for it in s.issues:
        k = it["kind"]
        # medical hell: these are what the core actually kills with
        if k == "haemorrhage" and I.has(s, "coagulant"):
            return "use coagulant"
        if k == "cooked" and I.has(s, "antisepsis"):
            return "use antisepsis"
        if k == "unravelling" and I.has(s, "stabiliser"):
            return "use stabiliser"
        if k == "crush" and I.has(s, "marrow"):
            return "use marrow"
        if k == "seizure":
            if I.has(s, "nerveblock"):
                return "use nerveblock"
            return "rest 4"
        if k == "denial":
            return "persuade this is happening to you, and it will not stop because you stopped"
        if k == "blind":
            return "rest 2"
        if k == "reopened" and it.get("limb"):
            return "tend " + it["limb"]
        if k == "chip fault":
            return "recalibrate"
        if k in ("dead nerve", "fever") and I.has(s, "salve"):
            return "use salve"
        if k == "phantom":
            return "reassure"
        if k == "ash lung":
            return "rest 3"
        if k == "cold shock" and I.has(s, "torch") and not s.eff("fire"):
            return "use torch"
        # everything the named branches above do not cover, read straight off the table:
        # what it needs, or failing that the first verb that clears it. Medical hell has far
        # more conditions in it than anyone wants to hand-write branches for.
        from hz import issues as ISS
        spec = ISS.TYPES.get(k) or {}
        need = spec.get("needs")
        if need and I.has(s, need):
            return "use " + need
        if not need:
            for verb in spec.get("clears") or ():
                if verb in ("tend", "bind", "treat", "patch"):
                    return "tend " + (it.get("limb") or "right leg")
                if verb in ("recalibrate", "reassure"):
                    return verb
                if verb in ("rest", "camp", "sleep"):
                    return "rest 3"
                if verb in ("persuade", "please", "reason"):
                    return ("persuade please hold on because this passes and stopping here "
                            "does not help it")

    if s.scene:
        if s.scene.get("sid") == "the_line":
            return "1"          # the bot always walks across, so the crossing gets tested
        opts = s.scene["opts"]
        low = [o.lower() for o in opts]
        for i, o in enumerate(low):
            if any(k in o for k in ("bind", "salve", "ground yourself", "sit down",
                                    "drink", "make camp", "shelter")):
                if r.random() < 0.7:
                    return str(i + 1)
        return str(r.randint(1, len(opts)))

    if B.bleed_rate(s) > 0.05:
        limb = max(s.limbs, key=lambda n: s.limbs[n]["bleed"])
        if s.limbs[limb]["bleed"] > 0:
            return "tend " + limb
    # an open wound that has stopped running is still how the heat gets in
    if s.infection > 20:
        for n, L in s.limbs.items():
            if L["state"] in B.OPEN_WOUNDS and not L["bound"] and L["state"] != "lost":
                return "tend " + n
    if s.thirst > 55 and I.has(s, "water"):
        return "drink"
    if s.hunger > 62 and (I.has(s, "ration") or I.has(s, "meat")
                          or I.has(s, "dust fungus")):
        for food in ("ration", "meat", "dust fungus"):
            if I.has(s, food):
                return "use " + food
    # stock up before and during the dry stretches
    if s.thirst > 40 and not I.has(s, "water"):
        return "gather"
    if not I.has(s, "ration") and not I.has(s, "meat") and s.hunger > 45:
        return "gather"
    if s.infection > 45 and I.has(s, "antisepsis"):
        return "use antisepsis"
    if s.infection > 45 and I.has(s, "salve"):
        return "use salve"
    if (getattr(s, "heat", 0.0) or 0.0) > 55:
        return "rest 2"
    if s.warmth < 30:
        if I.has(s, "torch") and not s.eff("fire"):
            return "use torch"
        if not s.eff("sheltered") and (I.has(s, "branch", 2) or I.has(s, "hide")):
            return "shelter"
    if s.weird > 62 and I.has(s, "stabiliser"):
        return "use stabiliser"
    if s.weird > 66:
        return "recalibrate"
    if s.fatigue > 74:
        if not s.eff("sheltered") and (I.has(s, "branch", 2) or I.has(s, "hide")):
            return "shelter"
        return "camp 6"
    if s.strain > 82:
        return "rest 2"
    # keep it willing, and repair the link before it degrades badly
    if s.mood < 40 or s.will < 45:
        return "reassure"
    if (s.chip < 55 or s.weird > 55) and r.random() < 0.5:
        return "recalibrate"
    can = I.craftable(s)
    for want in ("bandage", "coat", "boots", "spear", "salve", "torch", "tinder",
                 "brace", "mask", "strut", "splint"):
        if want in can and not I.has(s, want) and r.random() < 0.6:
            return "craft " + want
    if B.load_of(s) > B.carry_cap(s):
        junk = [k for k in s.inv if k in ("charcoal", "scrap", "shard", "cloth", "cord")]
        if junk:
            return "drop " + max(junk, key=lambda k: s.inv[k])
    if B.load_of(s) < B.carry_cap(s) - 4 and r.random() < 0.14:
        return "gather"
    if r.random() < 0.06:
        return "think"
    return "go"


def run_auto(turns, quiet=False):
    s = load_or_new()
    last = ""
    for _ in range(turns):
        if s.over:
            break
        cmd = bot_command(s)
        last = C.step(s, cmd)
        if not quiet:
            print("\n$ " + cmd)
            print(last)
    s.save()
    if quiet:
        print(last)
    print("\n[auto stopped: turn %d, distance %.1f, %s]"
          % (s.turn, s.distance, s.ending or "still going"))
    return 0


# ------------------------------------------------------------------ modes
def mode_new(argv):
    seed = None
    if "--seed" in argv:
        try:
            seed = int(argv[argv.index("--seed") + 1])
        except Exception:
            seed = None
    words = []
    destiny = False
    final = False
    for a in argv:
        if not a.startswith("-") and not a.isspace():
            if seed is not None and a == str(seed):
                continue
            if a.strip().lower() in ("destiny", "hard"):
                destiny = True
                continue
            if a.strip().lower() in ("final", "thefinal"):
                final = True
                continue
            words.append(a)
    # 'new', 'new 3', 'new crust', 'new crust 3' - a leading region name is optional
    reg = None
    if words and not words[0].isdigit():
        reg = REG.resolve(words[0])
    rest = words[1:] if reg is not None else words
    picked = rest[0] if rest else None

    if reg is not None and not REG.is_unlocked(reg["key"]):
        print("%s is not open yet. Finish the region above it first.\n" % reg["name"])
        print(REG.roster())
        return 2
    if words and reg is None and not words[0].isdigit() and not SUB.resolve(words[0]):
        print("There is no region or subject called '%s'.\n" % words[0])
        print(REG.roster())
        print()
        print(SUB.roster())
        return 2
    sub = SUB.resolve(picked)
    if picked and not sub:
        print("There is no subject '%s'.\n" % picked)
        print(SUB.roster())
        return 2
    if not words:
        # a fresh player has to be able to see that both choices exist at all
        print(REG.roster(REG.DEFAULT))
        print()
        print(SUB.roster(SUB.DEFAULT))
        print()
        print("Nothing chosen, so: %s, in %s."
              % (REG.BY_KEY[REG.DEFAULT]["name"], SUB.BY_ID[SUB.DEFAULT]["name"]))
        print()
    reg = reg or REG.BY_KEY[REG.DEFAULT]
    sub = sub or SUB.BY_ID[SUB.DEFAULT]
    if final and not REG.final_open(sub["id"]):
        if REG.any_final():
            print("%s has not walked the bottom of %s, so %s is not open to it. It is "
                  "earned per subject, the same way, and it is not lent out.\n"
                  % (sub["name"], REG.DESTINY_NAME, REG.FINAL_NAME))
        else:
            print("%s is not open to anything yet. Finish the bottom of %s with a "
                  "subject and that subject gets it.\n"
                  % (REG.FINAL_NAME, REG.DESTINY_NAME))
        print(SUB.roster(sub["id"]))
        return 2
    if destiny and not REG.destiny_open(sub["id"]):
        if REG.any_destiny():
            print("%s has not walked the core, so %s is not open to it. It is earned per "
                  "subject and it is not lent out.\n" % (sub["name"], REG.DESTINY_NAME))
        else:
            print("%s is not open to anything yet. Finish the core with a subject and that "
                  "subject gets it.\n" % REG.DESTINY_NAME)
        print(SUB.roster(sub["id"]))
        return 2
    s = new_game(seed, sub["id"], reg["key"], destiny, final)
    launch_watcher()
    print(R.intro(reg, destiny=destiny, carried=bool(getattr(s, "carried_in", False)),
                  final=final, resumed=bool(REG.final_slot(sub["id"])) and final))
    print()
    print(SUB.implantation(sub))
    print()
    print(C.step(s, "look"))
    s.save()
    return 0


def mode_lore(argv):
    """What a subject was before the chip. Only for one that has walked the core."""
    if not argv:
        opened = [x["id"] for x in SUB.SUBJECTS if REG.lore_open(x["id"])]
        if not opened:
            print("No history is open yet. Finish the core with a subject and that subject's "
                  "history opens.")
            return 2
        print("Open:  " + ", ".join(opened))
        print("Read one with:  .\\run.bat lore " + opened[0])
        return 0
    sub = SUB.resolve(argv[0])
    if not sub:
        print("There is no subject '%s'." % argv[0])
        return 2
    if not REG.lore_open(sub["id"]):
        print("%s has not walked the core. Nothing of its history is open.\n"
              "  Finish INTO THE CORE with it and the file opens." % sub["name"])
        return 2
    text = SUB.lore(sub["id"])
    if not text:
        print("There is nothing written down about %s." % sub["name"])
        return 2
    print("=" * 74)
    print("%s - WHAT IT WAS BEFORE THE CHIP" % sub["name"].upper())
    print("=" * 74)
    print()
    print(text)
    print()
    return 0


def mode_cmd(argv):
    if not argv:
        print("usage: run.bat cmd <command>")
        return 2
    if not save_exists():
        s = new_game()
        print(R.intro())
    else:
        s = State.load()
    launch_watcher(quiet=True)
    if s.over:
        from hz import endings as E
        print("This run is over: %s\n\n%s\n\n%s"
              % (s.ending, s.ending_text, E.scorecard(s)))
        print("\nStart another with:  .\\run.bat new")
        return 0
    try:
        print(C.step(s, " ".join(argv)))
    except Exception as e:
        import traceback
        s.note("[the world stuttered: %s]" % e)
        print("[that turn did not resolve: %s: %s]" % (type(e).__name__, e))
        print("[state preserved - try a different command, or 'status']")
        traceback.print_exc(file=sys.stderr)
    s.save()
    return 0


def mode_status():
    if not save_exists():
        print("No run yet. Start one with:  .\\run.bat new")
        return 1
    s = State.load()
    if s.over:
        from hz import endings as E
        print(R.frame(s, s.ending_text + "\n\n" + E.scorecard(s), show_cmds=False))
    else:
        print(R.frame(s, "(no action taken)"))
    return 0


def mode_play(argv):
    fresh = "--new" in argv
    seed = None
    if "--seed" in argv:
        try:
            seed = int(argv[argv.index("--seed") + 1])
        except Exception:
            seed = None
    s = new_game(seed) if fresh else load_or_new(seed)
    if "--no-watch" not in argv:
        launch_watcher()
    print(R.intro())
    print(C.step(s, "look"))
    s.save()
    while not s.over:
        try:
            sys.stdout.write("\n> ")
            sys.stdout.flush()
            line = sys.stdin.readline()
        except KeyboardInterrupt:
            print("\n[stopped. progress saved]")
            break
        if not line:
            print("\n[input closed. progress saved - resume with .\\run.bat or .\\run.bat cmd <x>]")
            break
        line = line.strip()
        if line.lower() in ("quit", "exit"):
            print("[saved. resume with .\\run.bat]")
            break
        if line.lower() == "save":
            s.save()
            print("[saved]")
            continue
        print(C.step(s, line))
        s.save()
    s.save()
    if s.over:
        print("\n[run over: %s]  Start again with:  .\\run.bat new" % s.ending)
    return 0


def main(argv):
    if argv and argv[0] in ("watch", "--watch"):
        return WATCH.run(SAVE_PATH)
    if argv and argv[0] == "new":
        return mode_new(argv[1:])
    if argv and argv[0] in ("cmd", "do", "step"):
        return mode_cmd(argv[1:])
    if argv and argv[0] in ("status", "frame"):
        return mode_status()
    if argv and argv[0] == "auto":
        turns = 250
        if len(argv) > 1:
            try:
                turns = int(argv[1])
            except ValueError:
                pass
        return run_auto(turns, quiet="--quiet" in argv)
    if argv and argv[0] in ("lore", "history", "file"):
        return mode_lore(argv[1:])
    if argv and argv[0] == "help":
        print(C.HELP)
        return 0
    return mode_play(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
