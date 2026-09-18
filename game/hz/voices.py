"""Per-subject speech. Seven of them, and they should not sound like one creature with a number.

Two rules hold across all of them:

  ".."   is breath and hesitation, and belongs inside a sentence that is coming apart.
  "..."  is EMOTING ONLY. It is a deliberate silence - a refusal to answer, a stare, a thing
         it will not say - and it never gets used as decoration at the end of a line. Anything
         that wants to trail off uses "..".

Each subject has a register that says what it is like without anybody explaining what it is
like: 2008 flat and cooperative, 1278 eager and entirely without self-preservation, 101 with a
permanent edge of annoyance, 0041 apologising for existing, 7 clipped and almost fluent because
it has had this conversation before, 3350 breathless because its chest cannot keep up, and
680 almost entirely absent - a word at a time, and mostly not that.
"""

# stutter: how often a word gets broken. trail: how often a line ends unfinished.
# fluent: strips the leading ".." that the shared pools open with.
STYLES = {
    "2008": {"stutter": 0.30, "trail": 0.55, "fluent": 0.25, "tag": None},
    "1278": {"stutter": 0.22, "trail": 0.40, "fluent": 0.35, "tag": "eager"},
    "101":  {"stutter": 0.40, "trail": 0.45, "fluent": 0.30, "tag": "annoyed"},
    "0041": {"stutter": 0.50, "trail": 0.75, "fluent": 0.05, "tag": "sorry"},
    "7":    {"stutter": 0.06, "trail": 0.15, "fluent": 0.85, "tag": "tired"},
    "3350": {"stutter": 0.34, "trail": 0.50, "fluent": 0.20, "tag": "breathless"},
    "680":  {"stutter": 0.00, "trail": 0.10, "fluent": 0.95, "tag": "flat"},
}
DEFAULT_STYLE = {"stutter": 0.30, "trail": 0.55, "fluent": 0.25, "tag": None}

# things each one says that the others would not. These replace the shared pool when present.
FLAVOUR = {
    "2008": {
        "walk": ["mm.. still going..", "s'fine.. this is.. fine..",
                 "how far.. how far now.."],
        "hurt": ["o.. ow..", "mm.. that's.. that's bad..", "hh.. ok.. ok.."],
        "good": ["mm.. s'better..", "that's.. that's alright.."],
        "tired": [".. can we stop.. for a bit..", "mm.. m'tired.. s'ok though.."],
    },
    "1278": {
        "walk": ["where next.. tell me where next..", "m'going.. m'going, look..",
                 "yes.. yes ok.. which way.."],
        "hurt": ["s'fine.. m'fine.. keep going..", "o.. ow.. no it's.. it's fine..",
                 "don't stop for.. for that.."],
        "good": ["did i.. did i do it right.. did i..", "mm.. good.. was that good.."],
        "fear": ["you want me to.. ok.. ok i'll go..", "s'fine.. you said.. so s'fine.."],
        "refuse": [".. but you said.. you said to..", "no i.. i will.. m'going.."],
    },
    "101": {
        "walk": ["yeah.. yeah m'WALKING..", "s'this it.. s'just this.. forever..",
                 "how much.. how much FURTHER.."],
        "hurt": ["AGH.. that's.. that's on YOU..", "o.. OW.. thanks.. thanks for that..",
                 "hh.. you felt that?.. no.. no you didn't.."],
        "good": ["mm.. finally..", "s'about.. s'about time.."],
        "tired": ["m'DONE.. m'done, i said..", "no.. no more.. m'sitting.."],
        "eat": ["mm.. s'food at least..", "finally.. something.. that isn't walking.."],
        "fear": ["oh GREAT.. that's.. that's great..", "s'fine.. s'FINE.. everything's fine.."],
    },
    "0041": {
        "walk": [".. m'sorry.. m'going as fast as..", ".. s'ok.. i can.. i can keep up..",
                 ".. am i.. am i doing it right.."],
        "hurt": [".. m'sorry.. m'sorry i.. i didn't mean to..",
                 ".. oh.. oh no.. did i.. did i break it..",
                 ".. s'my fault.. s'my.. m'sorry.."],
        "good": [".. oh.. oh thank.. thank you..", ".. m'ok.. m'ok now.. thank.."],
        "tired": [".. m'sorry.. can we.. can we just for a minute.. m'sorry..",
                  ".. i don't.. i don't want to stop but.."],
        "refuse": [".. m'sorry.. i can't.. i can't do that one.. m'sorry..",
                   ".. please don't.. please don't make me.."],
    },
    "7": {
        "walk": ["still walking.", "this part i remember.", "it's further than it looks.",
                 "mm. going."],
        "eat": ["mm. that's food.", "s'the grey stuff again.", "i remember this tasting worse."],
        "drink": ["that's better.", "mm. needed that."],
        "find": ["useful.", "that's worth carrying.", "mm. keep that."],
        "sleep": ["wake me if it comes back.", "s'fine. i'll sleep anywhere now."],
        "fear": ["something's out there.", "s'the same one as before, probably.",
                 "i'd move if i were you. you're not, though."],
        "cold": ["cold.", "hands've stopped closing."],
        "hurt": ["that one's bad.", "hh. yes. that's the one.", "s'fine. i've had worse off you."],
        "good": ["better.", "mm. that helps."],
        "tired": ["m'done for today.", "we stop here or i stop here. your choice."],
        "weird": ["s'started again.", "the sky does that. ignore it.",
                  "it's not real. keep walking."],
        "truth": ["yes. i know.", "i'd worked that out.", "s'not new to me."],
        "refuse": ["no.", "not that one. ask me something else.",
                   "i've done that before. it didn't work."],
    },
    # 680 does not talk. What it has is four or five words a day and a lot of not saying
    # anything, so almost every context here is a silence and the rest are as short as a
    # thing can be while still being a thing.
    "680": {
        "walk": ["mm.", "going."],
        "hurt": ["hn.", "mm."],
        "good": ["mm."],
        "eat": ["mm."],
        "fear": ["(it stops walking and looks at it)"],
        "cold": ["(it does not say anything about the cold)"],
        "tired": ["(it sits down without a word and looks at you waiting to be told to get up)"],
        "weird": ["(it shuts the eye that still closes)"],
        "truth": ["yes."],
        "refuse": ["no.", "(it does not answer and does not move)"],
        "sever": ["hn."],
    },
    "3350": {
        "walk": ["hh.. hh.. still.. still going..", "mm.. fast.. can go.. faster.. hh..",
                 "hh.. how far.. how.. far.."],
        "hurt": ["hh.. HH.. ow..", "o.. ow.. hh.. can't.. can't get.. breath.."],
        "good": ["hh.. better.. mm..", "s'good.. hh.. s'good.."],
        "tired": ["hh.. hh.. need.. need to stop.. chest.. m'chest..",
                  "can't.. hh.. can't keep.. this up.."],
    },
}

# the deliberate silences. These are the only places "..." belongs.
SILENCE = {
    "2008": ["..."],
    "1278": ["..."],
    "101": ["...", "...", ".. no."],
    "0041": ["...", ".. (it does not answer)"],
    "7": ["...", "(it looks at nothing and says nothing)"],
    "3350": ["..."],
    "680": ["...", "(it looks at you for a long moment and says nothing)",
            "(nothing. it has already gone back to what it was doing)"],
}


def style(sid):
    return STYLES.get(sid, DEFAULT_STYLE)


def flavour(sid, ctx):
    return (FLAVOUR.get(sid) or {}).get(ctx)


def silence(sid):
    return SILENCE.get(sid, ["..."])


def _defluent(line):
    """Strip the shared pools' habitual leading hesitation."""
    out = line
    while out.startswith(".."):
        out = out[2:].lstrip()
    while out.startswith(". "):
        out = out[2:]
    return out or line


def _detrail(line):
    """Finish a sentence that the shared pool left hanging."""
    if line.endswith(".."):
        return line[:-2].rstrip().rstrip(",") + "."
    return line


def _destutter(line):
    """Close up broken words: 'm'not.. m'not doing' -> 'm'not doing'."""
    parts = [p for p in line.split("..") if p.strip()]
    if len(parts) <= 1:
        return line
    keep = []
    for p in parts:
        k = p.strip()
        if not k:
            continue
        if keep:
            prev = keep[-1]
            # "going" then "we're going" is one restarted phrase, not two
            if k.startswith(prev) or k.endswith(prev):
                keep[-1] = k
                continue
            if prev.startswith(k) or prev.endswith(k):
                continue
        keep.append(k)
    return " ".join(keep)


def shape(s, line, sid=None):
    """Push a shared-pool line into this subject's register.

    A line that is pure emoting - '...' and its variants - is never touched.
    """
    if not line:
        return line
    bare = line.strip()
    if set(bare) <= set(". ") or bare.startswith("(") or "..." in bare:
        return line          # emote, or a deliberate silence. Leave it exactly as written.
    sid = sid or getattr(s, "subject", "2008")
    st = style(sid)
    r = s.rng
    out = line
    if r.random() < st["fluent"]:
        out = _defluent(out)
    if st["stutter"] < 0.15 and r.random() < 0.8:
        out = _destutter(out)
    if out.endswith("..") and r.random() > st["trail"]:
        out = _detrail(out)
    tag = st.get("tag")
    if tag and r.random() < 0.14:
        out = _tagged(out, tag, r)
    # a nearly fluent subject should not be left without punctuation
    if st["stutter"] < 0.15 and out and out[-1] not in ".?!":
        out += "."
    return out


def _tagged(line, tag, r):
    # a tag that opens with ".." reads wrong welded onto a finished sentence
    if line.endswith(".") and not line.endswith(".."):
        line = line[:-1]
    if tag == "annoyed":
        return line + r.choice(["", "", " .. obviously..", " .. whatever..", " .. thanks.."])
    if tag == "sorry":
        return line + r.choice(["", "", " .. m'sorry..", " .. sorry.."])
    if tag == "eager":
        return line + r.choice(["", "", " .. ok?..", " .. tell me..", " .. i can do more.."])
    if tag == "tired":
        return line + r.choice(["", "", " been here before.", " same as last time."])
    if tag == "breathless":
        return line + r.choice(["", "", " hh..", " .. hh.."])
    return line
