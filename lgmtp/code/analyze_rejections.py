"""
Do rejections cluster at word starts?
Counts only tokens the target actually judged in each round (accepted ones + the first rejected one),
then compares the rejection rate of word-start tokens vs word-continuation tokens.

Usage: python analyze_rejections.py ../results/qwen/main_n10 [more prefixes ...]
"""
import json, sys
from collections import defaultdict

for prefix in sys.argv[1:]:
    c = defaultdict(lambda: {"ws_tested": 0, "ws_rej": 0, "cont_tested": 0, "cont_rej": 0})
    for line in open(f"{prefix}_raw.jsonl"):
        r = json.loads(line)
        if r["cfg"] == "ar":
            continue
        s = c[r["cfg"]]
        for rd in r["rounds"]:
            n, m, ws = rd["n"], rd["m"], rd["drafted_ws"]
            for i in range(min(m + 1, n)):          # tokens the target judged
                rejected = (i == m)
                key = "ws" if ws[i] else "cont"
                s[f"{key}_tested"] += 1
                s[f"{key}_rej"] += rejected

    print(f"\n######## {prefix} ########")
    print("| Policy | Reject rate: word-start | Reject rate: continuation | Ratio | Word-start tokens judged | Continuation tokens judged |")
    print("|---|---|---|---|---|---|")
    out = {}
    for cfg, s in c.items():
        p_ws = s["ws_rej"] / s["ws_tested"] if s["ws_tested"] else float("nan")
        p_ct = s["cont_rej"] / s["cont_tested"] if s["cont_tested"] else float("nan")
        ratio = p_ws / p_ct if p_ct else float("nan")
        out[cfg] = {"reject_rate_word_start": p_ws, "reject_rate_continuation": p_ct, "ratio": ratio, **s}
        print(f"| {cfg} | {100*p_ws:.1f}% | {100*p_ct:.1f}% | {ratio:.2f}x | {s['ws_tested']} | {s['cont_tested']} |")
    json.dump(out, open(f"{prefix}_rejections.json", "w"), indent=2)
