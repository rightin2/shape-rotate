# Benchmark: does shape rotate help?

100 realistic "my work is stuck" requests. Each one was answered twice by the same model, once with the skill loaded and once without. Two blind Claude Opus 5.5 judges compared every pair, with the A/B order swapped between them so position bias cancels out. The full run was done on two models.

## Headline

**On Opus 5.5, the skill gives sharper, better-structured, more faithful and shorter answers, and wins more head-to-heads than it loses (44 to 34). On the small Haiku 4.5 model, the method still sharpens the thinking, but Haiku invents details when it rebuilds a draft, so the result is a draw.**

| Model | Skill version | Skill wins | Plain wins | Ties | Decisive win rate |
|---|---|---|---|---|---|
| Opus 5.5 (high effort) | v1.1 | **44** | 34 | 22 | 56% (p = 0.31) |
| Haiku 4.5 | v1.1 | 45 | 50 | 5 | 47% (p = 0.68) |
| Haiku 4.5 | v1.0 | 27 | 58 | 15 | 32% (p = 0.001) |

A case counts as a win when both judges pick the same side. If they split, it's a tie.

### What changed, criterion by criterion

The table counts how many of the 200 judgements scored the skill answer higher or lower than the plain one.

| Criterion | Opus 5.5: higher / lower | Haiku 4.5: higher / lower |
|---|---|---|
| Through-line (a clear central idea) | **98 / 14** (p < 0.001) | **115 / 39** (p < 0.001) |
| Structure (the pieces now fit) | **101 / 44** (p < 0.001) | **107 / 47** (p < 0.001) |
| Fidelity (sticks to the person's facts) | **141 / 29** (p < 0.001) | 37 / 142 (worse) |
| Concision | **111 / 60** (p < 0.001) | 9 / 175 (worse) |
| Usefulness (ready to use) | 65 / 94 (slightly worse, p = 0.03) | **106 / 60** (p < 0.001) |
| Overall | 110 / 84 (p = 0.07) | 94 / 105 |

The method does what it is designed to do on both models: a clearer central idea and a better arrangement of the pieces. On Opus, it also made answers more faithful to the person's own material and about a quarter shorter (a median of 573 words against 748).

### By category (Opus 5.5)

| Category | Skill | Plain | Tie |
|---|---|---|---|
| Op-eds and essays | 5 | 1 | 4 |
| Research talks | 5 | 1 | 4 |
| Academic writing | 6 | 4 | 0 |
| Strategy | 6 | 4 | 0 |
| Team and org problems | 6 | 4 | 0 |
| Proposals and grants | 4 | 2 | 4 |
| Pitches | 4 | 4 | 2 |
| Positioning and copy | 4 | 5 | 1 |
| Life decisions | 3 | 2 | 5 |
| Business decisions | 1 | 7 | 2 |

**Known weak spot: business decisions.** Here the judges preferred plain answers that checked the person's arithmetic (break-even points, repayment periods) and led straight with the recommendation. They found the "spine / what moved" layout to be extra scaffolding for a decision.

## What we learned

- **v1.0 told the reader about the method.** Haiku printed the click test, the piece inventory and every rotation it tried, so its answers were 2.7 times longer than the plain ones. v1.1 keeps all of that private, starts with the answer, forbids invented facts and caps the commentary. On Haiku, that moved the result from a clear loss to a draw.
- **Model size matters.** When a small model fully rewrites someone's draft, it has more room to misquote a figure or move a citation. Opus doesn't have this problem: with the skill it was *more* faithful than without.
- **Decisions need the numbers checked.** That is the next improvement to make.

## Caveats

- The judges are AI (Opus 5.5), not people. On the Opus run they were judging answers from their own model, though both arms come from that model, so any self-preference applies to both equally.
- The Opus overall lean (56% of decisive cases) is not yet statistically significant. The criterion-level gains are.
- Multi-agent mode was not tested.

## Method

- **Cases:** 10 categories x 10, written by Opus 5.5 at high effort. Each is 232 to 348 words with the person's real material in it. All people and data are fictional. See [`data/cases.json`](data/cases.json).
- **Answers:** the skill arm had `SKILL.md` and its reference files in the system prompt. The plain arm had a one-line system prompt. Haiku runs used `claude-haiku-4-5-20251001`. Opus runs used `claude-opus-5-5` at high effort.
- **Judges:** `claude-opus-5-5` at high effort, with no labels saying which answer used the skill. They were told not to reward length. Each judge scored 1 to 10 on six criteria, picked a winner and gave a reason.
- **Cost:** $21.00 in total through the Message Batches API: $10.29 for Haiku (including generating the cases) and $10.71 for Opus.
- **Rerun it:** `uv run --with anthropic python evals/bench.py` (the docstring lists the steps). Raw answers, verdicts and per-case reasons are in [`data/`](data) (Haiku) and [`data-opus/`](data-opus) (Opus). The full tables are in [`results_v1.0.md`](results_v1.0.md), [`results_v1.1.md`](results_v1.1.md) and [`results_v1.1_opus.md`](results_v1.1_opus.md). The v1.0 skill is kept in [`skill-v1.0/`](skill-v1.0).
