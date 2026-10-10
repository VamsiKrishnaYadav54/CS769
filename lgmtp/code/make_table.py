"""
Turn a run's summary JSON into slide-ready tables.
Usage: python make_table.py ../results/qwen/main_n10 [more prefixes ...]
Writes <prefix>_table.md and <prefix>_table.csv next to the summary.
"""
import json, sys
import pandas as pd


def fmt(x, pct=False):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "—"
    return f"{100 * x:.1f}%" if pct else f"{x:.2f}"


for prefix in sys.argv[1:]:
    s = json.load(open(f"{prefix}_summary.json"))

    rows = []
    for cfg, v in s.items():
        rows.append({
            "policy": cfg,
            "MAT": v["MAT"],
            "accept_rate": v["accept_rate"],
            "mean_draft_len": v["mean_draft_len"],
            "speedup": v.get("speedup"),
            "tok_per_s": v["tok_per_s"],
            "midword_split_rate": v["midword_split_rate"],
            "rej_at_word_start": v["rejections_at_word_start"],
            "base_word_start": v["base_rate_word_start"],
            "exact_match_vs_ar": v["exact_match_vs_ar"],
        })
    df = pd.DataFrame(rows)
    df.to_csv(f"{prefix}_table.csv", index=False)

    lines = ["## Overall", "",
             "| Policy | MAT | Accept % | Draft len | Speedup | Mid-word splits | Rejected at word-start | Base rate word-start | Exact match |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['policy']} | {fmt(r['MAT'])} | {fmt(r['accept_rate'], True)} | {fmt(r['mean_draft_len'])} | "
                     f"{fmt(r['speedup'])}x | {fmt(r['midword_split_rate'], True)} | {fmt(r['rej_at_word_start'], True)} | "
                     f"{fmt(r['base_word_start'], True)} | {fmt(r['exact_match_vs_ar'], True)} |")

    tasks = sorted({t for v in s.values() for t in v["per_task"]})
    lines += ["", "## MAT per task", "", "| Policy | " + " | ".join(tasks) + " |", "|---" * (len(tasks) + 1) + "|"]
    for cfg, v in s.items():
        lines.append(f"| {cfg} | " + " | ".join(fmt(v["per_task"].get(t, {}).get("MAT")) for t in tasks) + " |")

    # Headline numbers for slide 4
    spec = [r for r in rows if r["policy"] != "ar"]
    best = max(spec, key=lambda r: r["MAT"])
    fixed4 = next((r for r in spec if r["policy"] == "fixed:4"), None)
    lines += ["", "## Headline", ""]
    lines.append(f"- Best MAT: {best['policy']} with {fmt(best['MAT'])} tokens per target pass")
    if fixed4 and fixed4["rej_at_word_start"] is not None:
        lines.append(f"- Under fixed:4, {fmt(fixed4['rej_at_word_start'], True)} of rejected tokens are word-starts, "
                     f"vs {fmt(fixed4['base_word_start'], True)} of all drafted tokens")

    text = "\n".join(lines)
    open(f"{prefix}_table.md", "w").write(text + "\n")
    print(f"\n######## {prefix} ########\n{text}")
