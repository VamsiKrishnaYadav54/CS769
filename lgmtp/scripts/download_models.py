"""
Run on the LOGIN node (compute nodes have no internet). Downloads the 4 models into $HF_HOME.
Llama models are gated: accept the licence on their HF pages, then run `huggingface-cli login` once.

  source config.sh && conda activate lgmtp && python scripts/download_models.py          # all
  python scripts/download_models.py qwen                                                 # only one family
"""
import os, sys
from huggingface_hub import snapshot_download

FAMILIES = {
    "qwen": [os.environ["QWEN_DRAFT"], os.environ["QWEN_TARGET"]],
    "llama": [os.environ["LLAMA_DRAFT"], os.environ["LLAMA_TARGET"]],
}
# Only what transformers needs. Skips Llama's 'original/' folder (a second 16 GB copy of the weights).
PATTERNS = ["*.json", "*.safetensors", "tokenizer*", "*.model", "*.txt"]

which = sys.argv[1:] or list(FAMILIES)
for fam in which:
    for repo in FAMILIES[fam]:
        print(f"--> {repo}", flush=True)
        path = snapshot_download(repo, allow_patterns=PATTERNS)
        print(f"    saved to {path}")
print("=== downloads done ===")
