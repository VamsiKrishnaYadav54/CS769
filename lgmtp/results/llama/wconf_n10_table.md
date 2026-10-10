## Overall

| Policy | MAT | Accept % | Draft len | Speedup | Mid-word splits | Rejected at word-start | Base rate word-start | Exact match |
|---|---|---|---|---|---|---|---|---|
| ar | 1.00 | — | — | 1.00x | — | — | — | — |
| fixed:4 | 3.52 | 63.7% | 3.98 | 1.29x | 18.5% | 84.5% | 79.9% | 46.7% |
| entropy:0.6 | 3.79 | 72.5% | 3.87 | 1.33x | 19.9% | 84.1% | 78.0% | 46.7% |
| entropy:0.8 | 3.20 | 80.7% | 2.74 | 1.31x | 18.2% | 83.8% | 76.6% | 45.0% |
| wconf:0.6 | 3.85 | 68.6% | 4.18 | 1.31x | 19.0% | 75.1% | 75.8% | 48.3% |
| wconf:0.8 | 3.29 | 76.1% | 3.02 | 1.29x | 17.6% | 72.1% | 73.3% | 46.7% |
| wconf:0.9 | 3.00 | 78.4% | 2.57 | 1.26x | 16.7% | 71.8% | 71.7% | 46.7% |

## MAT per task

| Policy | math_reasoning | mt_bench | qa | rag | summarization | translation |
|---|---|---|---|---|---|---|
| ar | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| fixed:4 | 3.97 | 3.75 | 3.53 | 3.35 | 3.36 | 2.98 |
| entropy:0.6 | 4.64 | 4.21 | 3.57 | 3.44 | 3.48 | 3.35 |
| entropy:0.8 | 3.84 | 3.64 | 2.91 | 2.95 | 2.93 | 2.87 |
| wconf:0.6 | 4.72 | 4.31 | 3.64 | 3.50 | 3.50 | 3.38 |
| wconf:0.8 | 4.03 | 3.76 | 2.99 | 3.02 | 2.97 | 2.95 |
| wconf:0.9 | 3.52 | 3.45 | 2.74 | 2.78 | 2.73 | 2.78 |

## Headline

- Best MAT: wconf:0.6 with 3.85 tokens per target pass
- Under fixed:4, 84.5% of rejected tokens are word-starts, vs 79.9% of all drafted tokens
