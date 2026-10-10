# shape-rotate v1.1 benchmark results

100 test cases. Model under test: `claude-opus-5-5` at high effort. Judges: `claude-opus-5-5` at high effort, blind, two per case with A/B order swapped.

| | Skill wins | Baseline wins | Ties |
|---|---|---|---|
| Cases (both judges' votes combined) | **44** | 34 | 22 |
| Individual judgements | **110** | 90 | 0 |

Win rate on decisive cases: **56%** (sign test p = 0.31). Both judges agreed on 78 of 100 cases.

## Average scores (1 to 10)

| Criterion | With skill | Without |
|---|---|---|
| through line | 8.86 | 8.32 |
| structure | 8.4 | 7.96 |
| usefulness | 8.2 | 8.31 |
| fidelity | 8.59 | 7.63 |
| concision | 7.29 | 6.74 |
| overall | 8.18 | 7.96 |

Median answer length: 573 words with the skill, 748 without.

## By category

| Category | Skill | Baseline | Tie |
|---|---|---|---|
| oped | 5 | 1 | 4 |
| business-decision | 1 | 7 | 2 |
| talk | 5 | 1 | 4 |
| pitch | 4 | 4 | 2 |
| academic | 6 | 4 | 0 |
| strategy | 6 | 4 | 0 |
| life-decision | 3 | 2 | 5 |
| proposal | 4 | 2 | 4 |
| positioning | 4 | 5 | 1 |
| team | 6 | 4 | 0 |

API cost: opus_runsv1_1 $7.53, opus_judgesv1_1 $3.18 (total $10.71).
