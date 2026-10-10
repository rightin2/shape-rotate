"""Render the shape-rotate README hero image (concept designed with the skill itself).

Usage: python3 assets/render_hero.py  ->  assets/hero.png
"""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, S = 1600, 800, 2  # S = supersampling factor for anti-aliasing
BG = (22, 22, 26)
GRID = (58, 58, 70)
CREAM = (237, 230, 214)
GREY = (138, 138, 148)
CORAL = (232, 115, 90)

# Standard 7-piece tangram in a 4x4 unit square (x right, y down).
PIECES = [
    ("L1", [(0, 0), (4, 0), (2, 2)], (62, 142, 138)),
    ("L2", [(0, 0), (2, 2), (0, 4)], (91, 108, 143)),
    ("M", [(2, 4), (4, 2), (4, 4)], (227, 176, 75)),
    ("S1", [(4, 0), (4, 2), (3, 1)], CREAM),
    ("S2", [(2, 2), (3, 3), (1, 3)], (169, 184, 160)),
    ("SQ", [(3, 1), (4, 2), (3, 3), (2, 2)], (201, 150, 58)),
    ("P", [(0, 4), (1, 3), (3, 3), (2, 4)], CORAL),
]

PIECES = [(n, [(4 - x, 4 - y) for x, y in pts], c) for n, pts, c in PIECES]

OUT = Path(__file__).with_name("hero.png")
rng = random.Random(7)


def centroid(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def place(pts, cx, cy, scale, angle_deg):
    """Centre the piece on (cx, cy), scale it (px per unit) and rotate it."""
    ox, oy = centroid(pts)
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for x, y in pts:
        dx, dy = (x - ox) * scale, (y - oy) * scale
        out.append(((cx + dx * ca - dy * sa) * S, (cy + dx * sa + dy * ca) * S))
    return out


def layer():
    return Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))


def poly(img, pts, fill=None, outline=None, width=1):
    d = ImageDraw.Draw(img)
    if fill:
        d.polygon(pts, fill=fill)
    if outline:
        d.line(pts + [pts[0]], fill=outline, width=width * S, joint="curve")


base = Image.new("RGBA", (W * S, H * S), BG + (255,))

# Dot grid fading in from x=600 to x=1000.
grid = layer()
gd = ImageDraw.Draw(grid)
for gx in range(0, W + 1, 40):
    t = min(1, max(0, (gx - 600) / 400))
    if t == 0:
        continue
    for gy in range(0, H + 1, 40):
        r = 1 * S
        gd.ellipse((gx * S - r, gy * S - r, gx * S + r, gy * S + r), fill=GRID + (int(255 * t),))
base.alpha_composite(grid)

# Locked square: side 440, centred at (1190, 410). Unit = 110 px.
U, SX, SY = 110, 1190 - 220, 410 - 220
locked = layer()
for name, pts, col in PIECES:
    world = [((SX + x * U) * S, (SY + y * U) * S) for x, y in pts]
    if name == "P":
        poly(locked, world, fill=BG + (255,))
        slot = world
        continue
    poly(locked, world, fill=col + (255,))
# Seams: background-coloured edges so it reads as interlocked parts.
seams = ImageDraw.Draw(locked)
for name, pts, _ in PIECES:
    if name == "P":
        continue
    world = [((SX + x * U) * S, (SY + y * U) * S) for x, y in pts]
    seams.line(world + [world[0]], fill=BG + (255,), width=3 * S)
poly(locked, slot, outline=CORAL + (200,), width=3)
base.alpha_composite(locked)

# Scattered zone (x 0..620): small pieces at random angles, fading in left to right.
scatter = layer()
title_box = (40, 30, 600, 230)
placed = []
tries = 0
while len(placed) < 20 and tries < 4000:
    tries += 1
    cx, cy = rng.uniform(50, 600), rng.uniform(60, 760)
    if title_box[0] < cx < title_box[2] and title_box[1] < cy < title_box[3]:
        continue
    if any(math.hypot(cx - px, cy - py) < 72 for px, py in placed):
        continue
    placed.append((cx, cy))
for i, (cx, cy) in enumerate(placed):
    name, pts, col = PIECES[i % 6]  # coral stays unique
    ang = rng.uniform(0, 360)
    alpha = int(255 * (0.55 + 0.35 * cx / 620))
    poly(scatter, place(pts, cx, cy, 27, ang - 30), outline=CREAM + (46,), width=1)
    poly(scatter, place(pts, cx, cy, 27, ang), fill=col + (alpha,))
base.alpha_composite(scatter)

# Transit zone (x 620..940): angles converge toward multiples of 45 degrees.
transit = layer()
for i, (cx, cy) in enumerate([(660, 250), (700, 560), (770, 380), (840, 640), (880, 190), (915, 470)]):
    name, pts, col = PIECES[(i * 2 + 1) % 6]
    progress = (cx - 620) / 320
    target = 45 * rng.randint(0, 7)
    off = rng.choice([-1, 1]) * (70 * (1 - progress) + 8)
    for k, step in enumerate((2.2, 1.5)):
        poly(transit, place(pts, cx - 18 * step, cy, 44, target + off * step), outline=CREAM + (30 + 15 * k,), width=1)
    poly(transit, place(pts, cx, cy, 44, target + off), fill=col + (235,))
base.alpha_composite(transit)

# The click moment: coral parallelogram 22 degrees off, lifted up-right of its slot.
P = PIECES[-1][1]
slot_cx = SX + centroid(P)[0] * U
slot_cy = SY + centroid(P)[1] * U
hx, hy = slot_cx + 70, slot_cy - 120

ghosts = layer()
for ang, a, dx in ((14, 31, 25), (8, 51, 50), (3, 77, 75)):
    poly(ghosts, place(P, slot_cx + (hx - slot_cx) * dx / 95, slot_cy + (hy - slot_cy) * dx / 95, U, ang), outline=CORAL + (a,), width=2)
base.alpha_composite(ghosts)

hero_pts = place(P, hx, hy, U, 22)
shadow = layer()
poly(shadow, [(x, y + 10 * S) for x, y in hero_pts], fill=(0, 0, 0, 90))
base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12 * S)))
hero = layer()
poly(hero, hero_pts, fill=CORAL + (255,))
base.alpha_composite(hero)

# Title.
d = ImageDraw.Draw(base)
font_path = "/System/Library/Fonts/Avenir Next.ttc"
title_font = ImageFont.truetype(font_path, 70 * S, index=0)
sub_font = ImageFont.truetype(font_path, 26 * S, index=7)
d.text((80 * S, 70 * S), "shape rotate", font=title_font, fill=CREAM)
d.text((84 * S, 160 * S), "rotate until it clicks", font=sub_font, fill=GREY)

base.resize((W, H), Image.LANCZOS).convert("RGB").save(OUT, optimize=True)
print(OUT)
