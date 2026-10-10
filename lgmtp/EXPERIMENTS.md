# Experiment tracker — Linguistically Guided Drafting & Verification

Tick `[✅]` when done. Fill in the Slurm job ID and a one-line result. Commit after each tick.

## Setup
- [✅] S1. GitHub repo `CS769` created, cloned on HPC login node
- [✅] S2. Environment `cs769` created (Python 3.11, torch 2.8.0+cu128) + Spec-Bench cloned (480 prompts)
- [✅] S3. Llama licences accepted on HF + `huggingface-cli login`
- [✅] S4. Qwen models downloaded (0.5B: 954 MB, 7B: 15 GB)
- [✅] S5. Llama models downloaded (1B: 2.4 GB, 8B: 15 GB)

## Midterm (deadline: PDF on Moodle Oct 10, 11:59 PM)
| ID | Experiment | Command | Job ID | Status | Result |
|---|---|---|---|---|---|
| E0 | Correctness check, both pairs (fp32, 6 prompts) | `sbatch slurm/00_check.sbatch qwen` / `llama` | 347024, 347025 | [✅] | PASS both pairs — all policies reproduce greedy output exactly |
| E1 | Main run, Qwen, 60 prompts — fixed 2/4/6/8, entropy 0.6/0.8, word 1/2/3 | `sbatch slurm/01_main.sbatch qwen` | 347032 | [✅] | Best MAT 3.51 (fixed:8); no speedup (all < 1×) |
| E2 | Main run, Llama, 60 prompts (generalisation) | `sbatch slurm/01_main.sbatch llama` | 347033 | [✅] | Best MAT 4.67 (fixed:8); best speedup 1.30× (entropy:0.6) |
| E3 | Tokenizer fertility, EN/HI/TE/TA (login node, optional) | `python code/fertility.py` | — | [ ] | EN = , HI = |
| E4 | Rejection analysis: word-start vs continuation | `python code/analyze_rejections.py results/qwen/main_n10 results/llama/main_n10` | — | [✅] | Word-starts rejected 1.4–1.9× more often; p < 10⁻⁴ |
| E5 | `wconf` policy (confidence check only at word starts), Llama | `sbatch slurm/02_custom.sbatch llama wconf ar,fixed:4,entropy:0.6,entropy:0.8,wconf:0.6,wconf:0.8,wconf:0.9` | 347042 | [✅] | wconf beats fixed (+0.21 to +0.26 MAT at equal length) but trails entropy (−0.06 to −0.11); speedup 1.31× vs entropy 1.34× |
| E6 | `wconf` policy, Qwen | `sbatch slurm/02_custom.sbatch qwen wconf ar,fixed:4,entropy:0.6,entropy:0.8,wconf:0.6,wconf:0.8,wconf:0.9` | 347044 | [✅] | Same pattern: vs fixed +0.13 to +0.23, vs entropy −0.05 to −0.08; all < 1× speed |
| E7 | Lossless check at scale, Llama (fp32, 60 prompts) | `sbatch slurm/02_custom.sbatch llama fp32_lossless ar,fixed:4,word:2 fp32` | 347045 | [✅] | 100% exact match on all 60 prompts × 128 tokens; fp32 speedup 1.48× (fixed:4) |
| M1 | Slides filled with results | | — | [ ] | |
| M2 | Slides exported to PDF, uploaded to Moodle | | — | [ ] | |

## Key findings so far
1. **Loop is correct:** in fp32, every policy reproduces plain greedy decoding exactly (E0).
2. **Rejections concentrate at word starts:** the target rejects word-start tokens 1.4–1.9× more often than word-continuation tokens, on both pairs and all 9 policies (E4). Qwen fixed:4: 27.7% vs 16.1% (p < 10⁻¹⁴); Llama fixed:4: 17.6% vs 12.3% (p < 10⁻⁴).
3. **At equal draft length, word-boundary drafting ≈ fixed window** (+0.01 to +0.05 MAT); **entropy drafting is clearly better** (+0.22 to +0.33 MAT) (E1, E2).
4. **Speedup depends on drafter cost:** Llama up to 1.30×; Qwen < 1× despite MAT up to 3.5. MAT is the fair metric.
5. **15–20% of round boundaries split a word under every drafting policy** — the bonus token usually starts a new word, so this needs a verification-side fix (direction 3).
6. **Lossless at scale:** in fp32, 100% exact match on all 60 prompts × 128 tokens (E7). bf16 exact match ≈ 45% comes from near-tie argmax flips caused by bf16 rounding (batched verify vs single-step), not a logic bug. Don't report the bf16 exact-match column.
7. **`wconf` (confidence check only at word starts) lands between fixed and entropy** (E5, E6): +0.13 to +0.26 MAT over fixed, −0.05 to −0.11 below entropy at equal draft length. Dropping the check on continuations lets low-confidence continuations through, and their reject rate rises to word-start levels (Llama 7.5% → 12.2%). → Position adds information, but confidence is needed at **both** positions. Next: separate thresholds for word starts and continuations.
8. **Timing is reproducible:** fixed:4 / entropy on Llama gave identical MAT and speedup within ±0.01× across two separate jobs (E2 vs E5).

## After midterm (to final submission)
### Drafting (direction 1)
- [ ] F1. Chunk-boundary drafting (spaCy noun chunks)
- [ ] F2. Named-entity-boundary drafting (spaCy NER)
- [ ] F3. Measure spaCy overhead per round (does it cancel the speedup?)
- [ ] F4. Two-threshold policy: separate confidence thresholds for word starts and continuations (follows from E5/E6)

### Verification (direction 3)
- [ ] V1. Speculative rejection sampling (temperature > 0), lossless
- [ ] V2. Typical acceptance (Medusa-style), lossy
- [ ] V3. Boundary roll-back: cut accepted span back to last complete word/unit (lossless)
- [ ] V4. Unit completion: finish a started idiom (MAGPIE) / entity, lossy
- [ ] V5. Quality metrics for lossy rules: GSM8K accuracy, QA exact match, translation BLEU

### Evaluation
- [ ] X1. Full Spec-Bench (`01_main.sbatch qwen 80`, `01_main.sbatch llama 80`)
- [ ] X2. Idiom-heavy slice from MAGPIE; entity-heavy slice
- [ ] X3. (Stretch) Indic slice via named entities

## Log
<!-- date — what happened, what changed, anything surprising -->
- 2026-10-10 — project scaffold created
- 2026-10-10 — env renamed to `cs769`; prompts now sampled evenly within each Spec-Bench task (MT-bench file is sorted by category)
- 2026-10-10 — fixed: inherited `TRANSFORMERS_CACHE` from another project overrode the project cache; now unset in `config.sh`
- 2026-10-10 — E0 passed on both pairs; added `analyze_rejections.py` (counts only tokens the target actually judged)
- 2026-10-10 — E1/E2 done; added `wconf` policy and `slurm/02_custom.sbatch`; submitted E5–E7
- 2026-10-10 — E5–E7 done; experiments frozen for the midterm, moving to slides
