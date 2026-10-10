#!/bin/bash
# Run ONCE on the LOGIN node (needs internet). Creates the conda env and folders.
set -e
source "$(dirname "$0")/../config.sh"

mkdir -p $ROOT/slurm_logs $ROOT/results $ROOT/external $HF_HOME

source ~/miniconda3/bin/activate
if ! conda env list | grep -q "^$CONDA_ENV "; then
    conda create -y -n $CONDA_ENV python=3.11
fi
conda activate $CONDA_ENV

# torch 2.8 + CUDA 12.8 wheels: same build already verified on your DGX and A40 nodes
pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cu128
pip install -r $ROOT/requirements.txt
python -m spacy download en_core_web_sm    # needed later for chunk / entity boundaries

# Spec-Bench prompts (we only use its data file, never edit the repo)
if [ ! -d $ROOT/external/Spec-Bench ]; then
    git clone --depth 1 https://github.com/hemingkx/Spec-Bench $ROOT/external/Spec-Bench
fi
test -f $SPECBENCH && echo "Spec-Bench prompts: OK ($(wc -l < $SPECBENCH) questions)"

python -c "import torch, transformers; print('torch', torch.__version__, '| transformers', transformers.__version__)"
echo "=== env ready ==="
