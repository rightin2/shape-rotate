"""Draw the README benchmark charts in light and dark versions from evals/ data.

Usage: uv run --with matplotlib python assets/charts/make_charts.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[2]
EVALS = ROOT / "evals"
OUT = Path(__file__).resolve().parent

# Palette validated with the dataviz validator against GitHub's light and dark surfaces.
THEMES = {
    "light": dict(bg="#ffffff", text="#1f2328", muted="#59636e", grid="#d1d9e0",
                  skill="#2a78d6", plain="#eb6834", tie="#c8d0d8"),
    "dark": dict(bg="#0d1117", text="#e6edf3", muted="#9198a1", grid="#30363d",
                 skill="#3987e5", plain="#d95926", tie="#3d444d"),
}

for f in ("/System/Library/Fonts/HelveticaNeue.ttc", "/System/Library/Fonts/Helvetica.ttc"):
    if Path(f).exists():
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Helvetica Neue", "Helvetica", "DejaVu Sans"]

CRITERIA = [("through_line", "Clear central idea"), ("structure", "Pieces fit together"),
            ("fidelity", "Faithful to the facts"), ("concision", "Concise"),
            ("usefulness", "Ready to use"), ("overall", "Overall")]

CATEGORY_NAMES = {"oped": "Op-eds and essays", "talk": "Research talks", "academic": "Academic writing",
                  "strategy": "Strategy", "team": "Team problems", "proposal": "Proposals and grants",
                  "pitch": "Pitches", "positioning": "Positioning and copy", "life-decision": "Life decisions",
                  "business-decision": "Business decisions"}


def load(p):
    return json.loads(Path(p).read_text())


def criterion_counts(verdicts, prefix):
    """Per criterion: judgements where the skill answer scored higher / lower."""
    out = {c: [0, 0] for c, _ in CRITERIA}
    for k, v in verdicts.items():
        tail = k.split("__")[1]
        if tail not in (f"{prefix}j0", f"{prefix}j1"):
            continue
        sk, bs = ("A", "B") if tail.endswith("0") else ("B", "A")
        for c, _ in CRITERIA:
            d = v[c][sk] - v[c][bs]
            out[c][0] += d > 0
            out[c][1] += d < 0
    return out


def style(ax, t, grid_axis="x"):
    ax.set_facecolor(t["bg"])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(colors=t["muted"], length=0, labelsize=10)
    if grid_axis:
        ax.grid(axis=grid_axis, color=t["grid"], linewidth=0.8)
        ax.set_axisbelow(True)


def header(fig, t, title, subtitle, legend=(("With shape rotate", "skill"), ("Tie", "tie"), ("Without", "plain"))):
    fig.text(0.035, 0.94, title, fontsize=17, fontweight="bold", color=t["text"], va="top")
    fig.text(0.035, 0.865, subtitle, fontsize=11, color=t["muted"], va="top")
    x = 0.035
    fig.canvas.draw()
    for label, key in legend:
        fig.text(x, 0.79, "\u25A0", color=t[key], fontsize=13, va="center")
        txt = fig.text(x + 0.02, 0.79, label, fontsize=10.5, color=t["text"], va="center")
        bb = txt.get_window_extent(renderer=fig.canvas.get_renderer())
        x = fig.transFigure.inverted().transform((bb.x1, 0))[0] + 0.03


def chart_head_to_head(t, name):
    runs = [("Opus 5.5", "skill v1.1", load(EVALS / "data-opus/results_v1.1_opus.json")),
            ("Haiku 5.5", "skill v1.1", load(EVALS / "data-haiku55/results_v1.1_haiku55.json")),
            ("Haiku 4.5", "skill v1.1", load(EVALS / "data/results_v1.1.json")),
            ("Haiku 4.5", "skill v1.0", load(EVALS / "data/results_v1.0.json"))]
    fig = plt.figure(figsize=(10, 5.2), facecolor=t["bg"])
    header(fig, t, "Head to head on 100 stuck-work requests",
           "Cases won when both blind judges agreed. Same model with and without the skill.")
    ax = fig.add_axes([0.2, 0.05, 0.76, 0.68])
    style(ax, t, grid_axis=None)
    for i, (model, ver, r) in enumerate(runs):
        y = len(runs) - 1 - i
        w = r["case_wins"]
        segs = [(w.get("skill", 0), "skill", "won"), (w.get("tie", 0), "tie", "ties"), (w.get("base", 0), "plain", "won")]
        left = 0
        for n, key, word in segs:
            ax.barh(y, n, left=left, height=0.62, color=t[key], edgecolor=t["bg"], linewidth=2)
            if n >= 5:
                ink = t["text"] if key == "tie" else "#ffffff"
                ax.text(left + n / 2, y, f"{n}", ha="center", va="center", fontsize=12,
                        fontweight="bold", color=ink)
            left += n
        ax.text(-2, y + 0.1, model, ha="right", va="center", fontsize=12, fontweight="bold", color=t["text"])
        ax.text(-2, y - 0.2, ver, ha="right", va="center", fontsize=10, color=t["muted"])
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, len(runs) - 0.5)
    ax.set_yticks([])
    ax.set_xticks([])
    fig.savefig(OUT / f"{name}-{t['mode']}.png", dpi=200, facecolor=t["bg"])
    plt.close(fig)


def chart_criteria(t, name):
    panels = [("Opus 5.5", criterion_counts(load(EVALS / "data-opus/verdicts.json"), "v1_1_")),
              ("Haiku 5.5", criterion_counts(load(EVALS / "data-haiku55/verdicts.json"), "v1_1_")),
              ("Haiku 4.5", criterion_counts(load(EVALS / "data/verdicts.json"), "v1_1_"))]
    fig = plt.figure(figsize=(10, 5.4), facecolor=t["bg"])
    header(fig, t, "What the skill changes",
           "Of 200 blind judgements per model, how often the skill answer scored higher or lower (skill v1.1).",
           legend=(("Skill scored higher", "skill"), ("Skill scored lower", "plain")))
    for pi, (model, counts) in enumerate(panels):
        ax = fig.add_axes([0.22 + pi * 0.265, 0.07, 0.235, 0.6])
        style(ax, t)
        ax.set_title(model, fontsize=12.5, fontweight="bold", color=t["text"], loc="center", pad=8)
        for i, (c, label) in enumerate(CRITERIA):
            y = len(CRITERIA) - 1 - i
            hi, lo = counts[c]
            ax.barh(y, hi, height=0.6, color=t["skill"])
            ax.barh(y, -lo, height=0.6, color=t["plain"])
            ax.text(hi + 5, y, str(hi), va="center", ha="left", fontsize=8.5, color=t["text"])
            ax.text(-lo - 5, y, str(lo), va="center", ha="right", fontsize=8.5, color=t["text"])
            if pi == 0:
                ax.text(-225, y, label, va="center", ha="right", fontsize=10.5, color=t["text"])
        ax.axvline(0, color=t["muted"], linewidth=1)
        ax.set_xlim(-200, 200)
        ax.set_xticks([-150, -75, 0, 75, 150])
        ax.set_xticklabels(["150", "75", "0", "75", "150"])
        ax.tick_params(labelsize=8.5)
        ax.set_yticks([])
        ax.set_ylim(-0.6, len(CRITERIA) - 0.4)
    fig.savefig(OUT / f"{name}-{t['mode']}.png", dpi=200, facecolor=t["bg"])
    plt.close(fig)


def chart_categories(t, name):
    r = load(EVALS / "data-opus/results_v1.1_opus.json")
    rows = sorted(r["by_category"].items(),
                  key=lambda kv: (kv[1].get("skill", 0) - kv[1].get("base", 0), kv[1].get("skill", 0)))
    fig = plt.figure(figsize=(10, 6.2), facecolor=t["bg"])
    header(fig, t, "Where it helps most",
           "Opus 5.5 with and without the skill, 10 cases per category. Cases won; ties shown on the right.",
           legend=(("With shape rotate", "skill"), ("Without", "plain")))
    ax = fig.add_axes([0.26, 0.05, 0.6, 0.66])
    style(ax, t)
    for y, (cat, v) in enumerate(rows):
        s, b, tie = v.get("skill", 0), v.get("base", 0), v.get("tie", 0)
        ax.barh(y, s, height=0.62, color=t["skill"])
        ax.barh(y, -b, height=0.62, color=t["plain"])
        if s:
            ax.text(s + 0.15, y, str(s), va="center", fontsize=10, color=t["text"])
        if b:
            ax.text(-b - 0.15, y, str(b), va="center", ha="right", fontsize=10, color=t["text"])
        ax.text(-8.6, y, CATEGORY_NAMES[cat], va="center", ha="right", fontsize=11, color=t["text"])
        ax.text(8.4, y, f"{tie} tie{'s' if tie != 1 else ''}" if tie else "", va="center", fontsize=9.5, color=t["muted"])
    ax.axvline(0, color=t["muted"], linewidth=1)
    ax.set_xlim(-8, 8)
    ax.set_xticks(range(-8, 9, 2))
    ax.set_xticklabels([str(abs(x)) for x in range(-8, 9, 2)])
    ax.set_yticks([])
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.text(-0.3, len(rows) - 0.25, "← without wins", ha="right", fontsize=9.5, color=t["muted"])
    ax.text(0.3, len(rows) - 0.25, "with shape rotate wins →", ha="left", fontsize=9.5, color=t["muted"])
    fig.savefig(OUT / f"{name}-{t['mode']}.png", dpi=200, facecolor=t["bg"])
    plt.close(fig)


if __name__ == "__main__":
    for mode, t in THEMES.items():
        t["mode"] = mode
        chart_head_to_head(t, "head-to-head")
        chart_criteria(t, "criteria")
        chart_categories(t, "categories")
    print(sorted(p.name for p in OUT.glob("*.png")))
