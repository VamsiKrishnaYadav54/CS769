"""
E3 (optional, CPU only, run on the LOGIN node - streams Wikipedia, needs internet).
Tokenizer fertility = average tokens per space-separated word, per language and tokenizer.
Higher fertility -> more tokens inside each word -> more room for word-level multi-token drafting.

  source ../config.sh && conda activate lgmtp && python fertility.py
"""
import os, json
from datasets import load_dataset
from transformers import AutoTokenizer

LANGS = {"English": "en", "Hindi": "hi", "Telugu": "te", "Tamil": "ta"}
TOKENIZERS = {"Qwen2.5": os.environ["QWEN_TARGET"], "Llama-3.1": os.environ["LLAMA_TARGET"]}
N_DOCS, CHARS = 300, 2000

texts = {}
for lang, code in LANGS.items():
    ds = load_dataset("wikimedia/wikipedia", f"20231101.{code}", split="train", streaming=True)
    texts[lang] = [d["text"][:CHARS] for _, d in zip(range(N_DOCS), ds)]
    print(f"loaded {lang}", flush=True)

res = {}
for tname, repo in TOKENIZERS.items():
    tok = AutoTokenizer.from_pretrained(repo)
    for lang, docs in texts.items():
        words = sum(len(d.split()) for d in docs)
        toks = sum(len(tok(d, add_special_tokens=False).input_ids) for d in docs)
        res.setdefault(tname, {})[lang] = round(toks / words, 2)

print("\nTokens per word:")
print("| Tokenizer | " + " | ".join(LANGS) + " |")
print("|---" * (len(LANGS) + 1) + "|")
for tname, r in res.items():
    print(f"| {tname} | " + " | ".join(str(r[l]) for l in LANGS) + " |")

out = os.path.join(os.environ["ROOT"], "results", "fertility.json")
json.dump(res, open(out, "w"), indent=2)
print(f"\nsaved {out}")
