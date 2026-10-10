"""Draw the README method diagram (six steps with the rotate / click-test loop), light and dark.

Usage: uv run --with matplotlib python assets/charts/make_diagram.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent

THEMES = {
    "light": dict(bg="#ffffff", card="#f6f8fa", edge="#d1d9e0", text="#1f2328", muted="#59636e",
                  accent="#2a78d6", accent_fill="#e8f1fc", done="#1f2328"),
    "dark": dict(bg="#0d1117", card="#161b22", edge="#30363d", text="#e6edf3", muted="#9198a1",
                 accent="#3987e5", accent_fill="#12233a", done="#e6edf3"),
}

for f in ("/System/Library/Fonts/HelveticaNeue.ttc", "/System/Library/Fonts/Helvetica.ttc"):
    if Path(f).exists():
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Helvetica Neue", "Helvetica", "DejaVu Sans"]

STEPS = [
    ("Pin the click", "the job, what feels\nwrong, how you'll\nknow it's fixed"),
    ("Break into pieces", "every claim, fact\nand objection\nbecomes a piece"),
    ("Draw the shape", "argument tree,\ntension map, 2x2,\nhub and spoke"),
    ("Rotate", "re-center, invert,\nre-order, change\nreader or format"),
    ("Click test", "one-line spine,\nevery piece placed,\nobjections housed"),
    ("Rebuild", "the work rebuilt\naround the shape,\nin your own words"),
]
LOOP = {3, 4}  # zero-based indexes of the steps inside the rotate loop

W, H = 10.0, 3.25
CARD_W, CARD_H, GAP = 1.38, 1.5, 0.21
X0 = (W - (6 * CARD_W + 5 * GAP)) / 2
Y0 = 1.08


def draw(t, mode):
    fig = plt.figure(figsize=(W, H), facecolor=t["bg"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    # Shaded band behind the loop steps.
    lx = X0 + 3 * (CARD_W + GAP) - 0.09
    ax.add_patch(FancyBboxPatch((lx, 0.12), 2 * CARD_W + GAP + 0.18, Y0 + CARD_H + 0.12 - 0.12,
                                boxstyle="round,pad=0,rounding_size=0.14",
                                facecolor=t["accent_fill"], edgecolor="none", zorder=0))
    ax.text(lx + (2 * CARD_W + GAP + 0.18) / 2, 0.27, "repeat until it clicks", ha="center",
            va="center", fontsize=9.5, color=t["accent"], fontweight="bold")

    for i, (title, body) in enumerate(STEPS):
        x = X0 + i * (CARD_W + GAP)
        in_loop = i in LOOP
        edge = t["accent"] if in_loop else t["edge"]
        ax.add_patch(FancyBboxPatch((x, Y0), CARD_W, CARD_H, boxstyle="round,pad=0,rounding_size=0.1",
                                    facecolor=t["card"], edgecolor=edge, linewidth=1.6 if in_loop else 1.0,
                                    zorder=2))
        # Number badge.
        bx, by = x + 0.2, Y0 + CARD_H - 0.22
        ax.add_patch(plt.Circle((bx, by), 0.115, color=t["accent"] if in_loop else t["muted"], zorder=3))
        ax.text(bx, by - 0.005, str(i + 1), ha="center", va="center", fontsize=9, color=t["bg"],
                fontweight="bold", zorder=4)
        ax.text(x + 0.12, by - 0.3, title, ha="left", va="center", fontsize=10, fontweight="bold",
                color=t["text"], zorder=4)
        ax.text(x + 0.12, by - 0.5, body, ha="left", va="top", fontsize=8.6,
                color=t["muted"], linespacing=1.45, zorder=4)

        if i < len(STEPS) - 1:
            ax.add_patch(FancyArrowPatch((x + CARD_W + 0.03, Y0 + CARD_H / 2),
                                         (x + CARD_W + GAP - 0.03, Y0 + CARD_H / 2),
                                         arrowstyle="-|>", mutation_scale=11, linewidth=1.3,
                                         color=t["accent"] if i in (3, 4) else t["muted"], zorder=3))

    # Loop arrow: from the click test back to rotate, under the cards.
    x4 = X0 + 3 * (CARD_W + GAP) + CARD_W / 2
    x5 = X0 + 4 * (CARD_W + GAP) + CARD_W / 2
    ax.add_patch(FancyArrowPatch((x5, Y0 - 0.03), (x4, Y0 - 0.03), connectionstyle="arc3,rad=-0.45",
                                 arrowstyle="-|>", mutation_scale=12, linewidth=1.5, color=t["accent"],
                                 zorder=3))
    ax.text((x4 + x5) / 2, 0.52, "not yet", ha="center", va="center", fontsize=9, color=t["accent"])
    ax.text(X0, H - 0.2, "How shape rotate works", ha="left", va="top", fontsize=14, fontweight="bold",
            color=t["text"])
    fig.savefig(OUT / f"method-{mode}.png", dpi=200, facecolor=t["bg"])
    plt.close(fig)


if __name__ == "__main__":
    for mode, t in THEMES.items():
        draw(t, mode)
    print("ok")
