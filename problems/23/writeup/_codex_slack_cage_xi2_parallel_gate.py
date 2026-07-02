"""Parallel graph-sharded Xi2 gate for Slack-CAGE zero-slack cages.

This is a thin wrapper around _codex_slack_cage_xi2_gate.analyze_graph.
It does not change the exact Fraction gate; it only shards graph6 inputs
across worker processes.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import multiprocessing as mp
import subprocess
from collections import Counter
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG
    from _codex_slack_cage_xi2_gate import analyze_graph, print_case


def fmt_frac(x):
    if isinstance(x, F):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def worker(g6):
    try:
        return {"ok": True, "g6": g6, "cases": analyze_graph(g6), "error": None}
    except Exception as exc:  # pragma: no cover - diagnostic path
        return {"ok": False, "g6": g6, "cases": [], "error": repr(exc)}


def summarize_case(cases):
    stats = Counter()
    bad = []
    max_prebank = None
    max_prebank_case = None
    for c in cases:
        if max_prebank is None or c["prebank"] > max_prebank:
            max_prebank = c["prebank"]
            max_prebank_case = c
        for z in c["zero"]:
            stats["zero"] += 1
            if z["Flat5"]:
                stats["flat5"] += 1
            xi = z["Xi2"]
            if xi is None:
                stats["xi2_none"] += 1
            elif xi > 0:
                stats["xi2_positive"] += 1
            elif xi == 0:
                stats["xi2_zero"] += 1
            else:
                stats["xi2_negative"] += 1
            if (not z["Flat5"]) and (xi is None or xi <= 0):
                bad.append((c, z))
    return stats, bad, max_prebank, max_prebank_case


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=11)
    ap.add_argument("--workers", type=int, default=60)
    ap.add_argument("--chunksize", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    graphs = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True, check=True).stdout.split()
    if args.limit is not None:
        graphs = graphs[: args.limit]

    all_cases = []
    errors = []
    done = 0
    with mp.Pool(processes=args.workers) as pool:
        for rec in pool.imap_unordered(worker, graphs, chunksize=args.chunksize):
            done += 1
            if rec["ok"]:
                all_cases.extend(rec["cases"])
            else:
                errors.append((rec["g6"], rec["error"]))
            if done % 5000 == 0 or done == len(graphs):
                print(
                    f"progress graphs={done}/{len(graphs)} cases={len(all_cases)} errors={len(errors)}",
                    flush=True,
                )

    stats, bad, max_prebank, max_prebank_case = summarize_case(all_cases)

    print("=== Parallel Slack-CAGE Xi2 gate ===")
    print("n:", args.n)
    print("graphs:", len(graphs))
    print("positive_cases:", len(all_cases))
    print("stats:", dict(stats))
    print("max_prebank:", fmt_frac(max_prebank))
    if max_prebank_case is not None:
        print_case("max_prebank_case:", max_prebank_case)
    if errors:
        print("first_error:", errors[0])
    if bad:
        c, z = bad[0]
        print_case("first_bad_case:", c)
        print("first_bad_zero:", z)
    print("VERDICT:", "PASS_XI2_CORE" if all_cases and not errors and not bad else "CHECK")


if __name__ == "__main__":
    main()
