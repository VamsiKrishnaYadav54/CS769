#!/bin/bash
#SBATCH --job-name=lgmtp_custom
#SBATCH --partition=a40
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=8
#SBATCH --time=03:00:00
#SBATCH --qos=a40
#SBATCH --output=/home/cccp/25m2125/VAMSI/CS769/lgmtp/slurm_logs/%j_%x.out
#SBATCH --error=/home/cccp/25m2125/VAMSI/CS769/lgmtp/slurm_logs/%j_%x.err

# Any chosen set of policies. Always include "ar" so speedups are measured in the same job.
# Usage: sbatch slurm/02_custom.sbatch PAIR TAG CONFIGS [DTYPE] [PER_TASK]
#   e.g. sbatch slurm/02_custom.sbatch llama wconf ar,fixed:4,entropy:0.6,wconf:0.6
#        sbatch slurm/02_custom.sbatch llama fp32_lossless ar,fixed:4 fp32

PAIR=$1
TAG=$2
CONFIGS=$3
DTYPE=${4:-bf16}
PER_TASK=${5:-10}
source /home/cccp/25m2125/VAMSI/CS769/lgmtp/config.sh
source ~/miniconda3/bin/activate $CONDA_ENV
export TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1
set -e

if [ "$PAIR" = "llama" ]; then DRAFT=$LLAMA_DRAFT; TARGET=$LLAMA_TARGET; else DRAFT=$QWEN_DRAFT; TARGET=$QWEN_TARGET; fi
OUT=$ROOT/results/$PAIR/${TAG}_n${PER_TASK}
echo "=== $SLURM_JOB_ID on $(hostname) | $(nvidia-smi --query-gpu=name --format=csv,noheader) | $PAIR | $TAG | $DTYPE | $CONFIGS ==="

cd $ROOT/code
python spec_exp.py --draft $DRAFT --target $TARGET --questions $SPECBENCH \
    --per_task $PER_TASK --max_new 128 --dtype $DTYPE --configs $CONFIGS --out $OUT

python make_table.py $OUT
python analyze_rejections.py $OUT
echo "=== Done ==="
