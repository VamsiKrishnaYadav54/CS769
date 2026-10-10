## Overall

| Policy | MAT | Accept % | Draft len | Speedup | Mid-word splits | Rejected at word-start | Base rate word-start | Exact match |
|---|---|---|---|---|---|---|---|---|
| ar | 1.00 | — | — | 1.00x | — | — | — | — |
| fixed:4 | 3.50 | 63.1% | 3.97 | 1.48x | 18.6% | 85.2% | 80.4% | 100.0% |
| word:2 | 2.79 | 71.7% | 2.51 | 1.38x | 18.1% | 80.7% | 71.5% | 100.0% |

## MAT per task

| Policy | math_reasoning | mt_bench | qa | rag | summarization | translation |
|---|---|---|---|---|---|---|
| ar | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| fixed:4 | 3.98 | 3.70 | 3.40 | 3.39 | 3.33 | 2.98 |
| word:2 | 2.93 | 2.88 | 2.69 | 2.75 | 2.68 | 2.76 |

## Headline

- Best MAT: fixed:4 with 3.50 tokens per target pass
- Under fixed:4, 85.2% of rejected tokens are word-starts, vs 80.4% of all drafted tokens
