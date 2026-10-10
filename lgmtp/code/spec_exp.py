"""
Speculative decoding experiments: drafting policies x greedy verification.

Normally launched through the Slurm scripts in ../slurm (see README.md).

Policies:
  ar          plain autoregressive decoding with the target (baseline)
  fixed:k     draft exactly k tokens
  entropy:p   draft until the drafter's top-token probability drops below p (cap = --max_draft)
  word:w      draft until w new words have started (cap = --max_draft)
"""
import argparse, json, time, functools
from collections import defaultdict
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, DynamicCache

ap = argparse.ArgumentParser()
ap.add_argument("--draft", default="Qwen/Qwen2.5-0.5B-Instruct")
ap.add_argument("--target", default="Qwen/Qwen2.5-7B-Instruct")
ap.add_argument("--questions", default="Spec-Bench/data/spec_bench/question.jsonl")
ap.add_argument("--per_task", type=int, default=10)
ap.add_argument("--max_new", type=int, default=128)
ap.add_argument("--max_draft", type=int, default=8)
ap.add_argument("--dtype", default="bf16", choices=["bf16", "fp32"])
ap.add_argument("--configs", default="ar,fixed:2,fixed:4,fixed:6,fixed:8,entropy:0.6,entropy:0.8,word:1,word:2,word:3")
ap.add_argument("--out", default="results", help="output prefix, e.g. ../results/qwen/run")
args = ap.parse_args()

import os
os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
json.dump(vars(args), open(f"{args.out}_args.json", "w"), indent=2)  # record exactly how this run was made

dev = "cuda"
dtype = torch.bfloat16 if args.dtype == "bf16" else torch.float32
tok = AutoTokenizer.from_pretrained(args.target)
target = AutoModelForCausalLM.from_pretrained(args.target, torch_dtype=dtype).to(dev).eval()
draft = AutoModelForCausalLM.from_pretrained(args.draft, torch_dtype=dtype).to(dev).eval()

eos = set()
for e in [tok.eos_token_id, target.generation_config.eos_token_id]:
    if e is not None:
        eos.update(e if isinstance(e, list) else [e])


@functools.lru_cache(maxsize=None)
def starts_word(t):
    """True if token t begins a new word (byte-level BPE: leading space/newline marker, or punctuation)."""
    s = tok.convert_ids_to_tokens(int(t))
    if not s:
        return True
    if s[0] in "ĠĊĉ":
        return True
    return not any(c.isalnum() for c in s)


# ---------- data: first turn of each Spec-Bench question, grouped by task ----------
MAIN = {"translation", "summarization", "qa", "math_reasoning", "rag"}
by_task = defaultdict(list)
with open(args.questions) as f:
    for line in f:
        q = json.loads(line)
        task = q.get("category", "mt_bench")
        task = task if task in MAIN else "mt_bench"
        if len(by_task[task]) < args.per_task:
            by_task[task].append(q["turns"][0])
prompts = [(t, p) for t, ps in by_task.items() for p in ps]


def encode(text):
    s = tok.apply_chat_template([{"role": "user", "content": text}], tokenize=False, add_generation_prompt=True)
    return tok(s, return_tensors="pt", add_special_tokens=False).input_ids.to(dev)


# ---------- decoding ----------
@torch.no_grad()
def run_ar(ids, max_new):
    cache = DynamicCache()
    nxt = target(ids, past_key_values=cache, use_cache=True).logits[:, -1].argmax(-1, keepdim=True)
    gen = []
    for _ in range(max_new):
        gen.append(nxt.item())
        if gen[-1] in eos:
            break
        nxt = target(nxt, past_key_values=cache, use_cache=True).logits[:, -1].argmax(-1, keepdim=True)
    return gen, []


@torch.no_grad()
def run_spec(ids, max_new, policy, param):
    tc, dc = DynamicCache(), DynamicCache()
    target(ids[:, :-1], past_key_values=tc, use_cache=True)   # caches always hold everything except the last token
    draft(ids[:, :-1], past_key_values=dc, use_cache=True)
    gen, rounds = [], []
    gmax = int(param) if policy == "fixed" else args.max_draft
    while len(gen) < max_new:
        # 1) draft
        cur, dtoks, words = ids[:, -1:], [], 0
        for k in range(gmax):
            pr = draft(cur, past_key_values=dc, use_cache=True).logits[:, -1].float().softmax(-1)
            ptop, t = pr.max(-1)
            t = t.item()
            if k > 0:
                if policy == "entropy" and ptop.item() < param:
                    break
                if policy == "word" and starts_word(t):
                    words += 1
                    if words >= param:
                        break
            dtoks.append(t)
            cur = torch.tensor([[t]], device=dev)
            if t in eos:
                break
        n = len(dtoks)
        # 2) verify: one target pass over last token + draft
        inp = torch.tensor([[ids[0, -1].item()] + dtoks], device=dev)
        tpred = target(inp, past_key_values=tc, use_cache=True).logits[0].argmax(-1).tolist()
        # 3) accept the longest matching prefix, plus the target's own next token
        m = 0
        while m < n and dtoks[m] == tpred[m]:
            m += 1
        new = dtoks[:m] + [tpred[m]]
        cut = next((i for i, x in enumerate(new) if x in eos), None)
        if cut is not None:
            new = new[:cut + 1]
        rounds.append({
            "n": n, "m": m, "len": len(new),
            "drafted_ws": [starts_word(x) for x in dtoks],
            "rej_ws": starts_word(dtoks[m]) if m < n else None,
        })
        gen += new
        ids = torch.cat([ids, torch.tensor([new], device=dev)], 1)
        if cut is not None:
            break
        # 4) roll caches back to the accepted prefix
        L = ids.shape[1] - 1
        tc.crop(L)
        dl = dc.get_seq_length()
        if dl > L:
            dc.crop(L)
            dl = L
        if dl < L:
            draft(ids[:, dl:L], past_key_values=dc, use_cache=True)
    return gen, rounds


def timed(fn, *a):
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    r = fn(*a)
    torch.cuda.synchronize()
    return r, time.perf_counter() - t0


def midword_splits(gen, rounds):
    """Count round boundaries that fall inside a word (next token is a continuation)."""
    pos, split, total = 0, 0, 0
    for r in rounds:
        pos += r["len"]
        if pos < len(gen):
            total += 1
            split += not starts_word(gen[pos])
    return split, total


# ---------- main ----------
encoded = [(t, encode(p)) for t, p in prompts]
run_ar(encoded[0][1], 16)
run_spec(encoded[0][1], 16, "fixed", 4)  # warm-up

ar_out, summary, raw = {}, {}, open(f"{args.out}_raw.jsonl", "w")
for cfg in args.configs.split(","):
    policy, param = (cfg.split(":") + [None])[:2]
    param = float(param) if param else None
    per_task = defaultdict(lambda: {"tok": 0, "time": 0.0, "rounds": 0})
    rej_ws, all_ws, splits, bounds, acc, drafted, exact, compared = [], [], 0, 0, 0, 0, 0, 0
    for i, (task, ids) in enumerate(encoded):
        if policy == "ar":
            (gen, rounds), dt = timed(run_ar, ids, args.max_new)
            ar_out[i] = gen
        else:
            (gen, rounds), dt = timed(run_spec, ids, args.max_new, policy, param)
            if i in ar_out:
                ref = ar_out[i]
                compared += 1
                exact += gen[:len(ref)] == ref
        pt = per_task[task]
        pt["tok"] += len(gen); pt["time"] += dt; pt["rounds"] += len(rounds) or len(gen)
        for r in rounds:
            acc += r["m"]; drafted += r["n"]
            all_ws += r["drafted_ws"]
            if r["rej_ws"] is not None:
                rej_ws.append(r["rej_ws"])
        s, b = midword_splits(gen, rounds)
        splits += s; bounds += b
        raw.write(json.dumps({"cfg": cfg, "task": task, "i": i, "time": dt, "gen": gen, "rounds": rounds}) + "\n")

    tot_tok = sum(v["tok"] for v in per_task.values())
    tot_time = sum(v["time"] for v in per_task.values())
    tot_rounds = sum(v["rounds"] for v in per_task.values())
    summary[cfg] = {
        "tok_per_s": tot_tok / tot_time,
        "MAT": tot_tok / tot_rounds,
        "accept_rate": acc / drafted if drafted else None,
        "mean_draft_len": drafted / tot_rounds if policy != "ar" else None,
        "rejections_at_word_start": sum(rej_ws) / len(rej_ws) if rej_ws else None,
        "base_rate_word_start": sum(all_ws) / len(all_ws) if all_ws else None,
        "midword_split_rate": splits / bounds if bounds else None,
        "exact_match_vs_ar": exact / compared if compared else None,
        "per_task": {t: {"tok_per_s": v["tok"] / v["time"], "MAT": v["tok"] / v["rounds"]} for t, v in per_task.items()},
    }
    base = summary.get("ar", {}).get("tok_per_s")
    if base:
        summary[cfg]["speedup"] = summary[cfg]["tok_per_s"] / base
    json.dump(summary, open(f"{args.out}_summary.json", "w"), indent=2)  # saved after every config
    print(cfg, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in summary[cfg].items() if k != "per_task"}, flush=True)
raw.close()
