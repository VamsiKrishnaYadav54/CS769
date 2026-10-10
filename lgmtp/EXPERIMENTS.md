# Experiment tracker — Linguistically Guided Drafting & Verification

Tick `[x]` when done. Fill in the Slurm job ID and a one-line result. Commit after each tick.

## Setup
- [✅] S1. GitHub repo created, cloned on HPC login node
- [✅] S2. `scripts/setup_env.sh` ran — conda env `lgmtp` + Spec-Bench cloned
- [✅] S3. Llama licences accepted on HF + `huggingface-cli login`
- [✅] S4. `download_models.py qwen` done
- [✅] S5. `download_models.py llama` done

## Midterm (deadline: PDF on Moodle Oct 10, 11:59 PM)
| ID | Experiment | Command | Job ID | Status | Result |
|---|---|---|---|---|---|
| E0 | Correctness check, Qwen (fp32) | `sbatch slurm/00_check.sbatch qwen` | 347024 and 347025 | [✅] | PASS both pairs; word-start reject ratio 1.2–2.1× |
| E1 | Main run, Qwen, 60 prompts — fixed 2/4/6/8, entropy 0.6/0.8, word 1/2/3 | `sbatch slurm/01_main.sbatch qwen` | | [ ] | best MAT = |
| E2 | Main run, Llama, 60 prompts (generalisation) | `sbatch slurm/01_main.sbatch llama` | | [ ] | best MAT = |
| E3 | Tokenizer fertility, EN/HI/TE/TA (login node, optional) | `python code/fertility.py` | — | [ ] | EN = , HI = |
| E4 | Rejection-position finding pulled from E1 table | (in `results/qwen/main_n10_table.md`) | — | [ ] | __% vs __% |
| M1 | Slide 4 filled with E1 (+E2) numbers | | — | [ ] | |
| M2 | Slides exported to PDF, uploaded to Moodle | | — | [ ] | |

## After midterm (to final submission)
### Drafting (direction 1)
- [ ] F1. Chunk-boundary drafting (spaCy noun chunks)
- [ ] F2. Named-entity-boundary drafting (spaCy NER)
- [ ] F3. Measure spaCy overhead per round (does it cancel the speedup?)

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
