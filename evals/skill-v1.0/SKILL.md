---
name: shape-rotate
description: Make a stuck argument, report, plan, pitch or decision "click into place". Lay out every piece as a visual structure, rotate it through deliberate lenses (invert, re-center, re-order, change audience, scale or modality) until the pieces lock together, then rebuild the work around the shape that clicked. With subagents, several agents rotate from different starting shapes and the best result is merged. Use when the user says something "doesn't land", "isn't clicking", "feels off", "I can't find the angle", "the pieces don't fit", "too many ideas and no spine", "help me see this differently", "shape rotate this", or asks to restructure, reframe or find the through-line of a draft, essay, strategy, research synthesis, thesis, pitch deck or hard decision, even if they never say "rotate".
---

# Shape Rotate

Some work fails not because a piece is missing but because the pieces are arranged in the wrong shape. Strong thinkers fix this by holding the whole thing in mind as a picture and turning it until it snaps together. Language models can do the same thing, but only when asked to: visualizing first and then rotating pulls on different parts of the model's knowledge than editing prose line by line does. This skill makes that move explicit and repeatable.

The output is not a list of suggestions. It is the shape that clicked, shown, plus the work rebuilt around it.

## When it is worth it

Use the full method on substantive work: a report, strategy, essay, thesis chapter, pitch, research synthesis, or a decision with several competing factors. For a single paragraph or a quick reframe, run the solo pass with three rotations and keep the output short.

## The method

### 1. Pin what "click" means

Write two or three lines before touching anything:

- **The job**: what this piece of work has to do, and for whom.
- **The friction**: what feels wrong right now, in the user's words if they gave them. If they did not, name the symptom you see (no spine, buried lead, two arguments fighting, evidence that does not support the claim, a reader who would stop at page two).
- **The click test**: what would be true if it worked. Use the checklist in step 5 and add anything specific to this job.

### 2. Break it into pieces

List every atomic piece as a short line with an ID: claims, evidence, examples, constraints, objections, stakeholders and what each one needs, numbers, open questions. Include pieces that are implied but missing, and mark them `(missing)`. This inventory is the raw material for every rotation. Rotations rearrange pieces; they never quietly drop one. If a piece leaves the final shape, say so and say why.

### 3. Draw the current shape

Render the pieces as a structure, not prose. Pick the representation that best shows how things are arranged right now: argument tree, causal chain, 2x2, tension map, layered stack, timeline, hub and spoke, Venn of stakeholder needs. Use a Mermaid diagram or a clean ASCII sketch. Then name the misfit you can now *see*: which piece is orphaned, which is carrying weight it cannot bear, where two branches contradict, what sits at the center that should not.

Seeing the shape is the point. Problems that are invisible in paragraphs are often obvious in a diagram.

### 4. Rotate

Turn the shape through at least five lenses. The full catalog with prompts is in [references/rotations.md](references/rotations.md); the core set is:

| Rotation | The question it asks |
|---|---|
| **Re-center** | Put a different piece at the middle. What orbits it now? |
| **Invert** | Argue the opposite well. What would have to be true, and what does that expose? |
| **Re-order** | Lead with the conclusion, the reader's problem, or the strongest evidence instead. |
| **Change the reader** | A skeptic, an expert, a decision-maker with two minutes, a smart 12-year-old. |
| **Change scale** | Zoom into one concrete case. Zoom out to the ten-year system. |
| **Change modality** | Express it as a picture, a story, a table, an equation, a metaphor. |
| **Subtract** | Remove the weakest piece. What collapses, and what gets stronger? |
| **Merge** | Which two pieces are secretly the same piece? |

For each rotation, redraw or briefly describe the new shape, then record in one or two lines: what snapped into place, what is still loose, and a fit score from 1 to 10 against the click test. Keep going past the first good one; the best shape often comes from combining two rotations (for example re-center plus change the reader).

### 5. Run the click test

A shape has clicked when:

- The whole thing fits in **one sentence** (the spine) that a reader would repeat.
- **Every piece has a home**, or has been deliberately cut with a reason.
- **Nothing load-bearing is weak**: the claims that carry the most weight have the strongest support.
- **The strongest objection has a place** inside the structure, not tacked on.
- **The order feels inevitable**: each part makes the next one necessary.

If no rotation passes, combine the two best and rotate again. If it still does not click after two rounds, the problem is probably a missing piece, not the arrangement; say which piece and what it would take to get it.

### 6. Rebuild

Rebuild the work around the winning shape. If the user gave a draft, deliver the restructured draft (or a section-by-section outline for long work, with the rewritten opening in full). Preserve the user's voice and their material; the job is arrangement, not replacing their ideas with yours.

## Multi-agent mode

When subagents are available and the work is substantive, rotation is much stronger in parallel, because each agent explores from a different starting picture and they do not anchor on each other.

1. Do steps 1 and 2 yourself so every agent works from the same job, click test and piece inventory.
2. Spawn 3 to 5 agents. Give each one the job, the click test, the full piece list, the source material, and a **different starting representation plus a different subset of rotations**. Use the template in [references/agent-brief.md](references/agent-brief.md).
3. Each agent returns: its clicked shape (diagram), the one-sentence spine, a fit score with reasons, and what it had to cut or flag as missing.
4. Compare the results side by side. Where agents converge on the same center or spine, that is load-bearing structure you can trust. Where one agent found something the others missed, it is a candidate graft. Pick the strongest shape and graft the best ideas from the runners-up. "Averaging" means this synthesis, not blending everything into mush.
5. Run the click test on the merged shape, then rebuild (step 6).

## Output format

Keep the working visible but compact. Use this structure:

```
## The spine
<one sentence>

## The shape that clicked
<diagram>
<two or three lines: which rotation unlocked it and why it works>

## What moved
- <piece> : <from where> -> <to where>, because <reason>
- Cut: <piece>, because <reason>
- Missing: <piece the work needs and does not have yet>

## Rebuilt
<the restructured draft, outline or decision>
```

Do the rotations and scoring in your own working, not in the reply. Readers in testing found a scorecard of every rotation to be clutter: they want the shape and the rebuilt work. Mention only the rotation that unlocked it (in "The shape that clicked") and offer the full rotation log if the user wants to see it. Keep the diagram; it is what lets the user see why the new arrangement works.
