#!/bin/bash
#SBATCH --job-name=lgmtp_main
#SBATCH --partition=a40
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=8
#SBATCH --time=03:00:00
#SBATCH --qos=a40
#SBATCH --output=/home/cccp/25m2125/VAMSI/CS769/lgmtp/slurm_logs/%j_%x.out
#SBATCH --error=/home/cccp/25m2125/VAMSI/CS769/lgmtp/slurm_logs/%j_%x.err

# E1/E2: all drafting policies on Spec-Bench, bf16, greedy verification.
# All configs of one pair run in ONE job on ONE GPU, so their timings are comparable.
# Usage: sbatch slurm/01_main.sbatch qwen [PER_TASK]      (or llama)
#        PER_TASK = prompts per Spec-Bench task (default 10 -> 60 prompts; 80 = full benchmark)

PAIR=${1:-qwen}
PER_TASK=${2:-10}
source /home/cccp/25m2125/VAMSI/CS769/lgmtp/config.sh
source ~/miniconda3/bin/activate $CONDA_ENV
export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1
set -e

if [ "$PAIR" = "llama" ]; then DRAFT=$LLAMA_DRAFT; TARGET=$LLAMA_TARGET; else DRAFT=$QWEN_DRAFT; TARGET=$QWEN_TARGET; fi
OUT=$ROOT/results/$PAIR/main_n${PER_TASK}
echo "=== $SLURM_JOB_ID on $(hostname) | $(nvidia-smi --query-gpu=name --format=csv,noheader) | $PAIR | $PER_TASK per task ==="

cd $ROOT/code
python spec_exp.py --draft $DRAFT --target $TARGET --questions $SPECBENCH \
    --per_task $PER_TASK --max_new 128 \
    --configs ar,fixed:2,fixed:4,fixed:6,fixed:8,entropy:0.6,entropy:0.8,word:1,word:2,word:3 \
    --out $OUT

python make_table.py $OUT
echo "=== Done ==="
