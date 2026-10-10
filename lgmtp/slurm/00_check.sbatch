#!/bin/bash
#SBATCH --job-name=lgmtp_check
#SBATCH --partition=a40
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=8
#SBATCH --time=00:45:00
#SBATCH --qos=a40
#SBATCH --output=/home/cccp/25m2125/VAMSI/CS769/lgmtp/slurm_logs/%j_%x.out
#SBATCH --error=/home/cccp/25m2125/VAMSI/CS769/lgmtp/slurm_logs/%j_%x.err

# E0: correctness check. In fp32 the speculative loop must reproduce plain greedy output exactly.
# Usage: sbatch slurm/00_check.sbatch qwen      (or llama)

PAIR=${1:-qwen}
source /home/cccp/25m2125/VAMSI/CS769/lgmtp/config.sh
source ~/miniconda3/bin/activate $CONDA_ENV
export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1
set -e

if [ "$PAIR" = "llama" ]; then DRAFT=$LLAMA_DRAFT; TARGET=$LLAMA_TARGET; else DRAFT=$QWEN_DRAFT; TARGET=$QWEN_TARGET; fi
OUT=$ROOT/results/$PAIR/check
echo "=== $SLURM_JOB_ID on $(hostname) | $(nvidia-smi --query-gpu=name --format=csv,noheader) | $PAIR ==="

cd $ROOT/code
python spec_exp.py --draft $DRAFT --target $TARGET --questions $SPECBENCH \
    --dtype fp32 --per_task 1 --max_new 64 \
    --configs ar,fixed:4,entropy:0.8,word:2 --out $OUT

python - <<EOF
import json
s = json.load(open("$OUT" + "_summary.json"))
bad = {k: v["exact_match_vs_ar"] for k, v in s.items() if k != "ar" and v["exact_match_vs_ar"] != 1.0}
print("\nCORRECTNESS:", "PASS - all policies reproduce greedy output" if not bad else f"FAIL {bad}")
EOF
echo "=== Done ==="
