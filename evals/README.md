# Benchmark: does shape rotate help?

100 realistic "my work is stuck" requests. Each one was answered twice by the same model, once with the skill loaded and once without. Two blind Claude Opus 5.5 judges compared every pair, with the A/B order swapped between them so position bias cancels out. The full run was done on three models.

## Headline

**On Haiku 5.5, the skill wins clearly: 48 cases to 27, a 64% decisive win rate that is statistically significant (p = 0.02). On Opus 5.5, it gives sharper, better-structured, more faithful and shorter answers, and wins more head-to-heads than it loses (44 to 34). On the older Haiku 4.5, the method still sharpens the thinking, but Haiku 4.5 invents details when it rebuilds a draft, so the result is a draw.**

| Model | Skill version | Skill wins | Plain wins | Ties | Decisive win rate |
|---|---|---|---|---|---|
| Haiku 5.5 (medium effort) | v1.1 | **48** | 27 | 25 | **64% (p = 0.02)** |
| Opus 5.5 (high effort) | v1.1 | **44** | 34 | 22 | 56% (p = 0.31) |
| Haiku 4.5 | v1.1 | 45 | 50 | 5 | 47% (p = 0.68) |
| Haiku 4.5 | v1.0 | 27 | 58 | 15 | 32% (p = 0.001) |

A case counts as a win when both judges pick the same side. If they split, it's a tie.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/charts/head-to-head-dark.png">
  <img src="../assets/charts/head-to-head-light.png" alt="Head to head on 100 requests: with Opus 5.5 the skill won 44, plain won 34, 22 ties; Haiku 5.5 48 to 27 with 25 ties; Haiku 4.5 v1.1 45 to 50 with 5 ties; Haiku 4.5 v1.0 27 to 58 with 15 ties" width="100%">
</picture>

### What changed, criterion by criterion

The table counts how many of the 200 judgements scored the skill answer higher or lower than the plain one.

| Criterion | Opus 5.5: higher / lower | Haiku 5.5: higher / lower | Haiku 4.5: higher / lower |
|---|---|---|---|
| Through-line (a clear central idea) | **98 / 14** (p < 0.001) | **112 / 28** (p < 0.001) | **115 / 39** (p < 0.001) |
| Structure (the pieces now fit) | **101 / 44** (p < 0.001) | **109 / 39** (p < 0.001) | **107 / 47** (p < 0.001) |
| Fidelity (sticks to the person's facts) | **141 / 29** (p < 0.001) | **97 / 64** (p = 0.01) | 37 / 142 (worse) |
| Concision | **111 / 60** (p < 0.001) | 71 / 86 (p = 0.26) | 9 / 175 (worse) |
| Usefulness (ready to use) | 65 / 94 (slightly worse, p = 0.03) | **93 / 60** (p = 0.01) | **106 / 60** (p < 0.001) |
| Overall | 110 / 84 (p = 0.07) | **121 / 77** (p = 0.002) | 94 / 105 |


<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/charts/criteria-dark.png">
  <img src="../assets/charts/criteria-light.png" alt="Of 200 judgements per model, how often the skill scored higher or lower on six criteria, for Opus 5.5, Haiku 5.5 and Haiku 4.5" width="100%">
</picture>

The method does what it is designed to do on all three models: a clearer central idea and a better arrangement of the pieces. Haiku 5.5 is the only model where the skill also won on every reader-facing measure at once: more faithful, more ready to use and better overall, at about the same length (a median of 581 words against 608). On Opus, it also made answers more faithful to the person's own material and about a quarter shorter (a median of 573 words against 748).

### By category (Opus 5.5)

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/charts/categories-dark.png">
  <img src="../assets/charts/categories-light.png" alt="Opus 5.5 cases won per category, with shape rotate versus without" width="100%">
</picture>

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
- **Model generation matters more than size.** Haiku 4.5 misquoted figures and moved citations when it rewrote a draft. Haiku 5.5, the same size class, did not: with the skill it was *more* faithful than without, and it gave the strongest overall result of the three models. Opus was more faithful with the skill too.
- **Decisions need the numbers checked.** Business decisions were the weak spot on Opus (1 to 7) and on Haiku 5.5 (2 to 5). Haiku 5.5 also lost on positioning and copy (2 to 6). That is the next improvement to make.

## Caveats

- The judges are AI (Opus 5.5), not people. On the Opus run they were judging answers from their own model, though both arms come from that model, so any self-preference applies to both equally.
- The Opus overall lean (56% of decisive cases) is not yet statistically significant. The criterion-level gains are.
- Multi-agent mode was not tested.

## Method

- **Cases:** 10 categories x 10, written by Opus 5.5 at high effort. Each is 232 to 348 words with the person's real material in it. All people and data are fictional. See [`data/cases.json`](data/cases.json).
- **Answers:** the skill arm had `SKILL.md` and its reference files in the system prompt. The plain arm had a one-line system prompt. Haiku 4.5 runs used `claude-haiku-4-5-20251001`. Haiku 5.5 runs used `claude-haiku-5-5` at medium effort. Opus runs used `claude-opus-5-5` at high effort.
- **Judges:** `claude-opus-5-5` at high effort, with no labels saying which answer used the skill. They were told not to reward length. Each judge scored 1 to 10 on six criteria, picked a winner and gave a reason.
- **Cost:** $24.06 in total through the Message Batches API: $10.29 for Haiku 4.5 (including generating the cases), $10.71 for Opus 5.5 and $3.06 for Haiku 5.5.
- **Rerun it:** `uv run --with anthropic python evals/bench.py` (the docstring lists the steps). Raw answers, verdicts and per-case reasons are in [`data/`](data) (Haiku 4.5), [`data-haiku55/`](data-haiku55) (Haiku 5.5) and [`data-opus/`](data-opus) (Opus). The full tables are in [`results_v1.0.md`](results_v1.0.md), [`results_v1.1.md`](results_v1.1.md) [`results_v1.1_haiku55.md`](results_v1.1_haiku55.md) and [`results_v1.1_opus.md`](results_v1.1_opus.md). The v1.0 skill is kept in [`skill-v1.0/`](skill-v1.0).
