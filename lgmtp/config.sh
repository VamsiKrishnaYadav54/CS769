# Shared settings, sourced by every script. Edit ROOT if you put the project elsewhere.
export ROOT=/home/cccp/25m2125/VAMSI/CS769/lgmtp
export CONDA_ENV=cs769

export HF_HOME=$ROOT/hf_cache
export HF_HUB_CACHE=$HF_HOME/hub
export HF_DATASETS_CACHE=$HF_HOME/datasets
export PYTHONUNBUFFERED=1

export SPECBENCH=$ROOT/external/Spec-Bench/data/spec_bench/question.jsonl

# Model pairs: drafter and target must come from the same family (shared tokenizer)
export QWEN_DRAFT=Qwen/Qwen2.5-0.5B-Instruct
export QWEN_TARGET=Qwen/Qwen2.5-7B-Instruct
export LLAMA_DRAFT=meta-llama/Llama-3.2-1B-Instruct
export LLAMA_TARGET=meta-llama/Llama-3.1-8B-Instruct
