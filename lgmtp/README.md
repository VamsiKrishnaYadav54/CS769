# Linguistically Guided Drafting & Verification for Speculative Decoding

Course project. Inference-only: a small drafter proposes tokens, a large target verifies them.
We compare *where drafting stops* (fixed / confidence / word boundary) and, later, *what gets accepted*.

## Layout
```
config.sh              paths, model names — edit ROOT here only
requirements.txt
EXPERIMENTS.md         tracker: tick experiments as they finish
scripts/setup_env.sh   login node: conda env + Spec-Bench
scripts/download_models.py  login node: models into hf_cache/
code/spec_exp.py       the speculative decoding loop + all metrics
code/make_table.py     summary JSON -> slide-ready markdown/CSV tables
code/fertility.py      tokens-per-word across languages (optional)
slurm/00_check.sbatch  correctness check (fp32)
slurm/01_main.sbatch   main run, all drafting policies
results/<pair>/        outputs (summary, tables, args)
```

## Run order
On the login node (has internet):
```bash
bash scripts/setup_env.sh
source config.sh && source ~/miniconda3/bin/activate lgmtp
huggingface-cli login                      # once, for Llama
python scripts/download_models.py qwen
python scripts/download_models.py llama
```
Then submit:
```bash
sbatch slurm/00_check.sbatch qwen          # ~10 min, must print CORRECTNESS: PASS
sbatch slurm/01_main.sbatch qwen           # ~45 min
sbatch slurm/01_main.sbatch llama          # ~45 min, runs in parallel on another node
```

## Metrics
- **MAT** — mean tokens produced per target forward pass (lead metric; hardware-independent)
- **Accept %** — fraction of drafted tokens the target accepted
- **Speedup** — tokens/s vs plain decoding on the same GPU, same job
- **Mid-word split rate** — fraction of round boundaries that fall inside a word
- **Rejected at word-start vs base rate** — do rejections cluster at the start of words?
- **Exact match** — output identical to plain greedy decoding (should be ~100%; tiny bf16 drift is expected)
