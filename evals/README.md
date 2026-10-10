# Benchmark: does shape rotate help?

100 realistic "my work is stuck" requests, each answered twice by Claude Haiku 4.5: once with the skill loaded, once without. Two blind Claude Opus 5.5 judges compared every pair, with the A/B order swapped between them so position bias cancels out.

## Headline

**The skill makes the thinking better, but on a small model it costs accuracy and brevity, so the overall result is a draw.**

| Version | Skill wins | Plain wins | Ties | Decisive win rate |
|---|---|---|---|---|
| v1.0 | 27 | 58 | 15 | 32% (p = 0.001) |
| v1.1 | 45 | 50 | 5 | 47% (p = 0.68, no real difference) |

What the judges scored, as the number of the 200 judgements in which the skill answer scored higher or lower than the plain one (v1.1):

| Criterion | Skill higher | Skill lower | Significant? |
|---|---|---|---|
| Through-line (a clear central idea) | 115 | 39 | yes, p < 0.001 |
| Structure (the pieces now fit) | 107 | 47 | yes, p < 0.001 |
| Usefulness (ready to use) | 106 | 60 | yes, p < 0.001 |
| Fidelity (sticks to the person's facts) | 37 | 142 | worse, p < 0.001 |
| Concision | 9 | 175 | worse, p < 0.001 |
| Overall | 94 | 105 | no difference |

**Where it helped most:** strategy (7 wins to 3) and personal decisions (6 to 4).
**Where it hurt:** academic writing (2 to 6) and marketing positioning (3 to 7). In both, exact wording and citations matter.

## What we learned

- **The method itself works.** The skill reliably produced a sharper spine, a better arrangement and a more usable result, which are the things it is designed to do.
- **v1.0 told the reader about the method.** Haiku printed the click test, the piece inventory and every rotation it tried, so answers were 2.7 times longer. v1.1 keeps all of that private and starts with the answer. That fix moved the result from a clear loss to a draw.
- **A small model invents facts when it rebuilds a draft.** Fully rewriting the person's work gives it more room to misquote a figure or move a citation. The plain answers rewrote less, so they slipped less.

## Method

- **Cases:** 10 categories x 10, written by Opus 5.5 at high effort: op-eds, business decisions, talks, pitches, academic writing, strategy, life decisions, proposals, positioning and team problems. They run 232 to 348 words each, with the person's real material in them. All people and data are fictional. See [`data/cases.json`](data/cases.json).
- **Answers:** `claude-haiku-4-5-20251001`. The skill arm had `SKILL.md` and its reference files in the system prompt. The plain arm had a one-line system prompt.
- **Judges:** `claude-opus-5-5` at high effort, with no labels saying which answer used the skill. They were told not to reward length. Each judge scored 1 to 10 on six criteria, picked a winner and gave a reason. Both judges agreed on 95 of 100 cases for v1.1.
- **Case result:** if both judges agree, that side wins. If they split, it's a tie.
- **Cost:** $10.29 in total through the Message Batches API.
- **Rerun it:** `uv run --with anthropic python evals/bench.py --help`. Raw answers, verdicts and per-case results are in [`data/`](data). [`results_v1.0.md`](results_v1.0.md) and [`results_v1.1.md`](results_v1.1.md) have the full tables, and the v1.0 skill is kept in [`skill-v1.0/`](skill-v1.0).

## Not yet tested

- Larger models (Sonnet, Opus), which is how most people run Claude Code.
- Multi-agent mode.
- Whether a human reader prefers the same answers the AI judges do.
