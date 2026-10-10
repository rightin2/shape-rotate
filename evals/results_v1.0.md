# shape-rotate v1.0 benchmark results

100 test cases. Model under test: `claude-haiku-4-5-20251001`. Judges: `claude-opus-5-5` at high effort, blind, two per case with A/B order swapped.

| | Skill wins | Baseline wins | Ties |
|---|---|---|---|
| Cases (both judges' votes combined) | **27** | 58 | 15 |
| Individual judgements | **69** | 131 | 0 |

Win rate on decisive cases: **32%** (sign test p = 0.001). Both judges agreed on 85 of 100 cases.

## Average scores (1 to 10)

| Criterion | With skill | Without |
|---|---|---|
| through line | 7.58 | 7.12 |
| structure | 7.0 | 6.53 |
| usefulness | 7.09 | 6.47 |
| fidelity | 4.72 | 6.79 |
| concision | 3.82 | 7.95 |
| overall | 6.05 | 6.82 |

Median answer length: 1082 words with the skill, 399 without.

## By category

| Category | Skill | Baseline | Tie |
|---|---|---|---|
| oped | 3 | 6 | 1 |
| business-decision | 4 | 5 | 1 |
| talk | 3 | 7 | 0 |
| pitch | 1 | 8 | 1 |
| academic | 1 | 8 | 1 |
| strategy | 4 | 6 | 0 |
| life-decision | 6 | 3 | 1 |
| proposal | 3 | 6 | 1 |
| positioning | 0 | 6 | 4 |
| team | 2 | 3 | 5 |

API cost: generate_cases $2.77, haiku_runs $0.89, opus_judges $3.59 (total $7.25).
