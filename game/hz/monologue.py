"""The voice inside it. Condition-keyed, so the monologue is a readout as much as flavour."""
from . import body as B
from . import world as W

BASE = [
    "You do not remember being small.",
    "You keep checking your hands. They are still hands, still yours, still furred.",
    "Nobody has said your name. You are not sure you have one that is a name.",
    "There is a word for what you are and you have not been given it.",
    "You want to go forward. Wanting to go forward is the oldest thing in you.",
]

BY_STATE = [
    (lambda s: B.bleed_rate(s) > 0.1,
     ["The orange is bright and it is yours and there is less of it than there was.",
      "You can smell your own blood. It smells like the inside of a machine."]),
    (lambda s: s.blood < 45,
     ["You are cold at the edges and the cold is moving inward.",
      "Everything is a long way away and slightly to the left."]),
    (lambda s: s.thirst > 70,
     ["You would trade a limb for water. You have limbs to spare now.",
      "Your tongue has gone to leather."]),
    (lambda s: s.hunger > 72,
     ["There is a hole under your ribs asking questions.",
      "You have started looking at things as food that are not food."]),
    (lambda s: s.fatigue > 75,
     ["Your eyes shut on their own and you lose seconds.",
      "You have started dreaming while walking. The dreams have a white room in them."]),
    (lambda s: s.pain > 60,
     ["Pain has stopped being an event and become weather.",
      "Every step is a bill arriving."]),
    (lambda s: s.infection > 40,
     ["The wound is hot and it is talking to you.",
      "Something under your skin is doing work you did not ask for."]),
    (lambda s: s.warmth < 28,
     ["Your jaw will not hold still.",
      "The cold has got past your fur and into the plumbing."]),
    (lambda s: s.weird > 55,
     ["The world has a grain to it, like something printed.",
      "You are being looked at from inside your own head.",
      "Sometimes the ground arrives after your foot does."]),
    (lambda s: B.limbs_lost(s) >= 1,
     ["The missing part still sends instructions. You still try to follow them.",
      "You are less of yourself than you were, and still the same amount of hungry."]),
    (lambda s: s.eff("rested"),
     ["You slept and woke up still here, which is a kind of answer."]),
]

BY_ZONE = {
    "holding": ["The corridors are the shape of a place that expected you to stay in it.",
                "You know how this room smells. You do not know anything else."],
    "fence": ["The wire was put here by hands. Hands are a fact you keep running into."],
    "flats": ["Nothing lives out here and it has never occurred to the flats to hide it."],
    "woods": ["The trees are made of the same stuff as the walls you came from."],
    "sink": ["Water holds you up and takes your heat as the fee."],
    "steppe": ["You can see yourself for miles. So can everything else."],
    "ridge": ["The towers are not talking to each other. They are talking about you."],
    "shelf": ["Ahead of you the world runs out of world.",
              "You have been walking toward a line somebody ruled with a straight edge."],
}

TRUTH_PUSH = [
    "Question: if they made you, what did they make you for?",
    "Question: why does the walking feel like obedience?",
    "Question: who is 07 counted against?",
]


def line(s):
    pool = []
    for test, lines in BY_STATE:
        if test(s):
            pool.extend(lines)
    pool.extend(BY_ZONE.get(W.zone(s)["key"], []))
    if not pool or s.rng.random() < 0.3:
        pool.extend(BASE)
    if len(s.truths) >= 1 and s.rng.random() < 0.35:
        pool.extend(TRUTH_PUSH)
    return s.rng.choice(pool)


def think(s):
    """Explicit 'think' command: a line, plus what it currently understands."""
    out = [line(s)]
    if s.truths:
        out.append("What you are sure of: " + " / ".join(s.truths))
    else:
        out.append("What you are sure of: nothing about yourself. Only the direction.")
    s.inner(out[0])
    B.tick(s, 6, exertion=0.4)
    return "\n".join(out)


def maybe(s):
    """Ambient monologue, fired occasionally by the turn loop."""
    if s.rng.random() < 0.34:
        t = line(s)
        s.inner(t)
        return t
    return None
