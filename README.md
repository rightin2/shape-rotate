<p align="center">
  <img src="assets/hero.png" alt="shape rotate: scattered tangram pieces drift in from the left and lock into a square, with the last coral piece caught mid-turn above its slot" width="100%">
</p>

<h1 align="center">shape rotate</h1>

<p align="center"><b>A Claude skill that makes stuck work click into place.</b><br>
Lay out every piece. See the shape. Rotate it until it locks.</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude-skill-E8735A" alt="Claude skill">
  <img src="https://img.shields.io/badge/Claude%20Code-plugin-3E8E8A" alt="Claude Code plugin">
  <img src="https://img.shields.io/badge/license-MIT-5B6C8F" alt="MIT license">
</p>

---

You have all the pieces. The research is done, the notes are there, the draft exists. And it still doesn't land.

Usually nothing is missing. The pieces are just **arranged in the wrong shape**. Good thinkers fix this by holding the whole thing in their head as a picture and turning it until it snaps together. Claude can do the same thing, but only if you ask it to. Asking a model to *visualize* the argument and then *rotate* it draws on a different part of what it knows than asking it to "improve this draft".

**shape rotate** makes that move explicit and repeatable.

## What it does

```mermaid
flowchart LR
    A["1. Pin the click<br/>job, friction, test"] --> B["2. Break into pieces<br/>every claim, fact, objection"]
    B --> C["3. Draw the shape<br/>tree, tension map, 2x2..."]
    C --> D["4. Rotate<br/>re-center, invert, re-order,<br/>change reader, scale, modality"]
    D --> E{"5. Does it click?"}
    E -- no --> D
    E -- yes --> F["6. Rebuild the work<br/>around the shape"]
```

1. **Pin what "click" means.** What the work has to do, what feels wrong, and how you'll know it's fixed.
2. **Break it into pieces.** Every claim, piece of evidence, constraint and objection becomes a labelled piece. Pieces can be moved or cut on purpose, but never dropped quietly.
3. **Draw the current shape.** An argument tree, a tension map, a 2x2, hub and spoke. Problems you can't see in paragraphs are obvious in a diagram.
4. **Rotate.** Put a different piece at the center. Argue the opposite. Lead with the reader's problem. Rebuild it for a skeptic. Zoom into one case. Turn it into a metaphor. Remove the weakest piece. Merge two pieces that are secretly one.
5. **Run the click test.** A one-sentence spine. Every piece has a home. Nothing load-bearing is weak. The strongest objection is housed. The order feels inevitable.
6. **Rebuild.** You get the restructured draft, talk, plan or decision in your own voice, built from your own material.

### Multi-agent mode

When subagents are available, shape rotate sends 3 to 5 agents to rotate the same pieces in parallel. Each agent starts from a **different picture** and uses a **different set of rotations**. Where the agents converge, the structure is load-bearing. Where one of them sees something the others missed, that idea gets grafted onto the winning shape.

## What you get back

```
## The spine          one sentence a reader would repeat
## The shape that clicked   the diagram, and which rotation unlocked it
## What moved         every piece that moved, was cut, or is missing
## Rebuilt            the restructured work, ready to use
```

<details>
<summary><b>Example: a newspaper op-ed that "just doesn't land"</b></summary>

**Input:** a draft that opens with "AI is changing everything", lists clinic problems (staff shortages, long wait lists, 15% no-shows), mentions privacy, and buries a real result in sentence nine: one regional clinic cut no-shows from 14% to 5% for $200 a month.

**What unlocked it:** *Merge* plus *Re-center*. Long wait lists and no-shows were listed as two separate problems. They're **one problem**: patients wait weeks while one booked chair in seven sits empty. Put the empty chair at the center instead of "AI", and every other piece finds its place.

**Spine:** *In regional towns where patients wait weeks to see a doctor, about one appointment in seven goes unused, and a $200-a-month tool that fills those empty chairs is the cheapest fix to the wait list that nobody is funding.*

```
                 THE EMPTY CHAIR
                        |
     +------------------+-------------------+
     |                  |                   |
  THE WASTE          THE FIX            THE ASK
  no-shows +         reminders +        $200/month vs the
  wait lists +       rebooking,         cost of empty chairs:
  burnt-out staff    14% -> 5%          fund it
                        |
                OBJECTIONS HOUSED
         privacy, "it's just an SMS", older patients
```

The AI hype got cut, the Ballarat result became the opening, and privacy moved from a lone worried sentence to an answered objection. The output was a full rebuilt op-ed, with bracketed gaps for facts the writer still had to check.

</details>

## Does it actually help?

Each test prompt ran twice, once with the skill and once without, and **blind judges** compared the two answers without knowing which was which. The prompts were:

- an op-ed that wouldn't land
- a seed-versus-bootstrap founder decision
- a 15-minute research talk with no through-line

| | Wins |
|---|---|
| **With shape rotate** | **5 of 6** blind comparisons |
| Without | 1 of 6 |

Judges said the skill's answers found sharper spines and delivered finished rebuilds rather than advice. They also kept every piece of the user's material in play. Their one complaint was clutter: a full scorecard of every rotation. That scorecard is gone from v1.0, so you now get the shape and the rebuilt work, and the rotation log only if you ask for it.

## Install

**Claude Code (plugin):**

```bash
/plugin marketplace add rightin2/shape-rotate
/plugin install shape-rotate@shape-rotate
```

**Claude Code (manual):**

```bash
git clone https://github.com/rightin2/shape-rotate.git
cp -r shape-rotate/skills/shape-rotate ~/.claude/skills/
```

**Claude.ai / Claude desktop:** download `skills/shape-rotate` as a zip and upload it under *Settings > Capabilities > Skills*.

## Use it

It triggers on its own when you say things like:

- *"This draft doesn't land, help me find the angle."*
- *"I keep going round in circles on this decision."*
- *"My findings feel like a pile of facts with no through-line."*
- *"Shape rotate this."*

It works on essays, reports, strategy docs, pitch decks, thesis chapters, research syntheses, talks and hard decisions. Anything where the pieces are there but the shape isn't.

## What's inside

```
skills/shape-rotate/
├── SKILL.md                    the method, click test and output format
└── references/
    ├── rotations.md            10 rotations, 9 starting shapes, agent assignments
    └── agent-brief.md          the brief each parallel agent receives
assets/
├── hero.png
└── render_hero.py              the code that draws the image above
```

## About the image

The hero image was designed **with the skill itself**. A shape-rotate pass tried a three-panel timeline (6/10), order dissolving into chaos (3/10) and fragments orbiting a center (7/10). It landed on this (9/10): tangram pieces drift left to right, lose their randomness and lock into a square. The last piece is frozen mid-turn above its empty slot, so the picture shows the moment of the click instead of the finished result. It's drawn in plain Python with Pillow ([`assets/render_hero.py`](assets/render_hero.py)), with no image model involved.

## Origin

The idea comes from a conversation between Emad Mostaque and Raoul Pal on Real Vision (September 2026). Raoul said his market analysis "isn't quite clicking". Emad's tip was to have the AI visualize every angle of the argument, then shape-rotate it until it clicks into place, using several agents and keeping the best result. His point was that this works because of how the model's latent space is organized. This repo turns that tip into a repeatable method.

## License

MIT
