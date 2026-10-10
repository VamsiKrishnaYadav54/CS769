## Overall

| Policy | MAT | Accept % | Draft len | Speedup | Mid-word splits | Rejected at word-start | Base rate word-start | Exact match |
|---|---|---|---|---|---|---|---|---|
| ar | 1.00 | — | — | 1.00x | — | — | — | — |
| fixed:4 | 2.96 | 49.3% | 3.98 | 0.82x | 17.6% | 88.3% | 82.7% | 48.3% |
| entropy:0.6 | 2.86 | 64.6% | 2.89 | 0.86x | 15.6% | 86.7% | 78.8% | 41.7% |
| entropy:0.8 | 2.54 | 71.6% | 2.16 | 0.89x | 15.4% | 86.2% | 77.4% | 46.7% |
| wconf:0.6 | 2.89 | 60.8% | 3.12 | 0.82x | 14.7% | 81.5% | 75.5% | 41.7% |
| wconf:0.8 | 2.60 | 67.0% | 2.40 | 0.86x | 14.2% | 79.6% | 72.8% | 46.7% |
| wconf:0.9 | 2.44 | 68.2% | 2.11 | 0.85x | 13.9% | 80.1% | 71.4% | 48.3% |

## MAT per task

| Policy | math_reasoning | mt_bench | qa | rag | summarization | translation |
|---|---|---|---|---|---|---|
| ar | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| fixed:4 | 3.92 | 3.28 | 2.34 | 2.70 | 2.89 | 2.93 |
| entropy:0.6 | 4.79 | 3.49 | 2.10 | 2.46 | 2.54 | 2.93 |
| entropy:0.8 | 4.03 | 2.94 | 1.93 | 2.21 | 2.31 | 2.58 |
| wconf:0.6 | 4.88 | 3.53 | 2.14 | 2.47 | 2.54 | 2.93 |
| wconf:0.8 | 4.25 | 3.07 | 1.97 | 2.27 | 2.31 | 2.60 |
| wconf:0.9 | 3.86 | 2.84 | 1.90 | 2.13 | 2.18 | 2.26 |

## Headline

- Best MAT: fixed:4 with 2.96 tokens per target pass
- Under fixed:4, 88.3% of rejected tokens are word-starts, vs 82.7% of all drafted tokens
