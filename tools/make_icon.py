"""Draw the HORIZONS icon: an old engraved seal. Needs Pillow; run locally, commit the PNGs.

    python tools/make_icon.py

A dial ring (the chip's calibration), a hatched etching of sky, the route running to a flat
horizon, and the sun coming up over it as the creature's own orange eye. Writes
ios/icon-1024.png (actool builds every size from it) and web/emblem.png for the page.
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = 2048                     # drawn at 2x, then reduced - that is the anti-aliasing
C = S // 2
INK = (43, 33, 24)
SEPIA = (120, 88, 52)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def paper(size, rng):
    img = Image.new("RGB", (size, size))
    px = img.load()
    mid = size / 2
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - mid, y - mid) / (mid * 1.42)
            base = lerp((238, 226, 196), (176, 146, 98), min(1.0, d ** 1.8))
            n = rng.randint(-7, 7)
            px[x, y] = tuple(max(0, min(255, v + n)) for v in base)
    return img


def main():
    rng = random.Random(680)
    # paper at quarter size, scaled up: the grain stays soft and it is fast
    img = paper(S // 4, rng).resize((S, S), Image.BICUBIC)
    d = ImageDraw.Draw(img)

    R = int(S * 0.40)           # the seal
    horizon = C + int(S * 0.07)

    # the window of the seal: sky and ground, masked to a circle
    win = Image.new("RGB", (S, S), (233, 219, 186))
    wd = ImageDraw.Draw(win)
    for y in range(C - R, horizon):
        t = (horizon - y) / R
        wd.line([(0, y), (S, y)], fill=lerp((240, 224, 188), (214, 190, 146), t))
    # engraving: horizontal hatching in the sky, tighter towards the top
    y = horizon - 34
    gap = 30.0
    while y > C - R:
        w = 3 if gap > 18 else 4
        wd.line([(0, int(y)), (S, int(y))], fill=lerp((150, 116, 74), INK, 1 - gap / 34), width=w)
        gap = max(12.0, gap * 0.93)
        y -= gap
    # the ground, and the route running into the vanishing point
    wd.rectangle([0, horizon, S, S], fill=(160, 124, 80))
    for i in range(0, S, 22):
        wd.line([(0, horizon + i * 0.55), (S, horizon + i * 0.55)], fill=(138, 104, 64), width=3)
    for k in range(-9, 10):
        wd.line([(C, horizon), (C + k * 240, S)], fill=(92, 66, 40), width=5 if k else 9)
    # sun rays behind the eye
    sun_r = int(S * 0.15)
    for a in range(0, 181, 6):
        ang = math.radians(180 + a)
        x0, y0 = C + math.cos(ang) * (sun_r + 40), horizon + math.sin(ang) * (sun_r + 40)
        x1, y1 = C + math.cos(ang) * R, horizon + math.sin(ang) * R
        wd.line([(x0, y0), (x1, y1)], fill=(170, 120, 60), width=5 if a % 12 else 9)

    # the eye, coming up over the line
    eye = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ep = eye.load()
    for yy in range(horizon - sun_r - 4, horizon + 1):
        for xx in range(C - sun_r - 4, C + sun_r + 5):
            dd = math.hypot(xx - C, yy - horizon) / sun_r
            if dd > 1.0:
                continue
            col = lerp((255, 214, 120), (236, 110, 24), min(1, dd / 0.7)) if dd < 0.7 else \
                lerp((236, 110, 24), (120, 40, 6), (dd - 0.7) / 0.3)
            ep[xx, yy] = col + (255,)
    edraw = ImageDraw.Draw(eye)
    # slit pupil, and a glint
    edraw.ellipse([C - 34, horizon - sun_r + 40, C + 34, horizon + sun_r - 40], fill=INK + (255,))
    edraw.ellipse([C - 110, horizon - sun_r + 70, C - 60, horizon - sun_r + 120], fill=(255, 246, 220, 230))
    edraw.arc([C - sun_r, horizon - sun_r, C + sun_r, horizon + sun_r], 180, 360, fill=INK + (255,), width=14)
    edraw.rectangle([0, horizon + 1, S, S], fill=(0, 0, 0, 0))   # only the half that is up
    glow = eye.filter(ImageFilter.GaussianBlur(40))
    win.paste(glow, (0, 0), glow)
    win.paste(eye, (0, 0), eye)
    wd = ImageDraw.Draw(win)
    wd.line([(0, horizon), (S, horizon)], fill=INK, width=14)

    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([C - R, C - R, C + R, C + R], fill=255)
    img.paste(win, (0, 0), mask)

    # the dial ring
    d = ImageDraw.Draw(img)
    for r, w in ((R, 26), (R + 70, 10), (R + 150, 6)):
        d.ellipse([C - r, C - r, C + r, C + r], outline=INK, width=w)
    for i in range(120):
        a = math.radians(i * 3)
        long = i % 10 == 0
        r0, r1 = R + 22, R + (66 if long else 44)
        d.line([(C + math.cos(a) * r0, C + math.sin(a) * r0), (C + math.cos(a) * r1, C + math.sin(a) * r1)],
               fill=INK, width=8 if long else 4)
    # four rivets on the outer band, as on an instrument
    for a in (45, 135, 225, 315):
        x, y = C + math.cos(math.radians(a)) * (R + 110), C + math.sin(math.radians(a)) * (R + 110)
        d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=SEPIA, outline=INK, width=5)

    out = img.resize((1024, 1024), Image.LANCZOS)
    os.makedirs(os.path.join(HERE, "ios"), exist_ok=True)
    out.save(os.path.join(HERE, "ios", "icon-1024.png"))
    out.resize((320, 320), Image.LANCZOS).save(os.path.join(HERE, "web", "emblem.png"))
    print("wrote ios/icon-1024.png and web/emblem.png")


if __name__ == "__main__":
    main()
