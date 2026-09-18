"""Game state: one flat, JSON-serialisable blob. No behaviour lives here."""
import json
import os
import random
import time

LIMB_ORDER = [
    "left arm", "right arm", "left leg", "right leg",
    "tail", "left ear", "right ear",
]

# degradation ladder, worst last
LIMB_STATES = ["intact", "bruised", "gashed", "broken", "mangled", "lost"]

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stuff")
SAVE_PATH = os.path.join(SAVE_DIR, "session.json")

# a few stats the new systems keep
EXTRA_STATS = ("refused", "overridden", "issues_fixed", "timers_missed", "escape_tries")


class State:
    def __init__(self, seed=None):
        self.seed = int(seed) if seed is not None else random.randrange(1 << 30)
        self.rng = random.Random(self.seed)

        # clock
        self.turn = 0
        self.day = 1
        self.minutes = 5 * 60 + 40      # minutes past midnight
        self.distance = 0.0             # 0 -> 100, the horizon

        # vitals (0..100 unless noted)
        self.blood = 100.0
        self.strain = 6.0
        self.fatigue = 14.0
        self.hunger = 18.0
        self.thirst = 22.0
        self.pain = 3.0
        self.infection = 0.0
        self.weird = 5.0
        self.warmth = 62.0
        self.heat = 0.0         # hyperthermia load - climbs while the core is too hot

        self.limbs = {
            n: {"state": "intact", "hp": 100.0, "bleed": 0.0,
                "bound": False, "strut": False}
            for n in LIMB_ORDER
        }

        self.inv = {"cloth": 2, "scrap": 1, "water": 1}
        self.truths = []        # what it has learned about itself
        self.flags = []         # one-shot world markers
        self.effects = {}       # name -> minutes remaining
        self.log = []           # [turn, text]
        self.mono = []          # internal monologue feed
        self.seen = []          # scenario ids already used (for once-only scenes)
        self.cool = {}          # scenario id -> turn it last fired

        # the chip: it is most of this creature's intelligence, and it is your leash
        self.mood = 55.0        # low mood = it starts refusing
        self.will = 70.0        # willingness to take an order right now
        self.chip = 100.0       # link integrity; overrides burn it
        self.issues = []        # active complications, each needing addressing
        self.pending_issues = []   # kinds raised by damage, materialised next tick
        self.timers = []        # timed events: [{"id","label","left","on","hint","data"}]
        self.feedback = []      # this turn's refusals / warnings / blocks
        self.tutorial = 0       # calibration step index
        self.escape = {"route": None, "active": False, "progress": 0.0,
                       "needed": 6.0, "chip_cut": False, "known": []}
        self.refusals = 0
        self.overrides = 0
        # things it has agreed to try to do on its own, from being reasoned with
        self.requests = {}      # topic -> {"pol","reason","turn","label","heeded"}

        # it talks. it does not know you can hear it.
        self.said = []          # [[turn, utterance]]
        self.pending_voice = []  # contexts queued by the body during a turn
        self.tells_seen = {}     # key -> turn, so a tell does not come round twice quickly
        self.chest = None       # a hole through the middle: no limb takes it, see mortal.py
        self.suspicion = 0.0    # what it has worked out about your intentions
        self.intent_run = 0     # harm-with-nothing-gained, in a row
        self.intent_before = None
        self.acted_alone = -99  # the turn it last did something off its own bat
        self.question = None    # {"id","text","opts","turn"} - it is waiting on you
        self.asked = []         # questions already put to you
        self.lies = 0
        self.honest = 0
        self.last_action_ok = True

        # where this run is being made, and how much the chip understands of what it sees
        self.region = "outside"
        self.destiny = False    # the harder ruleset, earned per subject by walking the core
        self.intel = 14.0       # gates recipes and reading a label off a manufactured thing
        self.known_items = []   # things it has worked out the identity of
        self.bags = 0           # built containers; each one buys carry
        self.battery = False    # the thing at the bottom of the core, once it is held

        # which one the chip is seated in, and how this run has bent it
        self.subject = "2008"
        self.trait_drift = {}
        self.crisis = None      # {"kind","left","total","pumps","air",...} - it is on the ground
        # the link is not guaranteed. Some of them can put the chip out and go on without it.
        self.link = {"down": False, "left": 0, "cause": "", "drops": 0, "held": 0, "blind": 0}
        self.snap = 0.0         # how close it is to going off, for the one that can
        self.pending_death = None   # an ending raised mid-turn, collected by check_fail
        self.trap_seen = False  # did it see the last one coming - set before the scene
        # the turns after the one it should have stopped on. See lastbreath.py
        self.laststand = {"active": False, "left": 0, "cause": "", "used": 0, "turns": 0}
        # a shell over the ears (armour, and only where it sits) with a sound inside it
        # (not armour, and the only thing holding the rest of it together)
        self.phones = None

        self.scene = None       # {"sid","text","opts":[{"label","idx"}],"age","danger"}
        self.last_command = ""
        self.last_result = ""
        self.activity = "waking up"

        self.over = False
        self.ending = None
        self.ending_text = ""
        self.cause = ""
        self.stats = {"crafted": 0, "scenes": 0, "sleeps": 0, "gathers": 0,
                      "fights": 0, "limbs_lost": 0, "steps": 0}

    # ---------- helpers ----------
    @property
    def clock(self):
        m = int(self.minutes) % (24 * 60)
        return "%02d:%02d" % (m // 60, m % 60)

    @property
    def night(self):
        h = (int(self.minutes) % (24 * 60)) // 60
        return h >= 21 or h < 5

    def has_flag(self, f):
        return f in self.flags

    def flag(self, f):
        if f not in self.flags:
            self.flags.append(f)

    def note(self, text):
        self.log.append([self.turn, text])
        if len(self.log) > 220:
            del self.log[:-220]

    def inner(self, text):
        self.mono.append([self.turn, text])
        if len(self.mono) > 80:
            del self.mono[:-80]

    def learn(self, truth):
        if truth not in self.truths:
            self.truths.append(truth)
            self.weird = max(0.0, self.weird - 4.0)
            self.note("You understand something new: " + truth)
            from . import intel as IN
            line = IN.gain(self, "truth")
            if line:
                self.feedback.append(line)
            return True
        return False

    def eff(self, name):
        return self.effects.get(name, 0) > 0

    def add_eff(self, name, minutes):
        self.effects[name] = max(self.effects.get(name, 0), int(minutes))

    # ---------- persistence ----------
    def to_dict(self):
        st = self.rng.getstate()
        d = {k: v for k, v in self.__dict__.items() if k != "rng"}
        d["_rng"] = [st[0], list(st[1]), st[2]]
        return d

    @classmethod
    def from_dict(cls, d):
        s = cls(seed=d.get("seed", 0))
        rs = d.pop("_rng", None)
        for k, v in d.items():
            setattr(s, k, v)
        if rs:
            try:
                s.rng.setstate((rs[0], tuple(int(x) for x in rs[1]), rs[2]))
            except Exception:
                pass
        # sets were stored as lists; keep them lists for stability
        return s

    def save(self, path=SAVE_PATH):
        """Atomic, and patient: the watch window reads this file on a timer, and on Windows a
        reader holding it open makes os.replace fail outright. Retry rather than lose the turn."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f)
        last = None
        for attempt in range(12):
            try:
                os.replace(tmp, path)
                return
            except OSError as e:
                last = e
                time.sleep(0.05 * (attempt + 1))
        # last resort: write in place rather than drop the turn on the floor
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f)
            try:
                os.remove(tmp)
            except OSError:
                pass
        except OSError:
            raise last

    @classmethod
    def load(cls, path=SAVE_PATH):
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


def save_exists(path=SAVE_PATH):
    return os.path.exists(path)
