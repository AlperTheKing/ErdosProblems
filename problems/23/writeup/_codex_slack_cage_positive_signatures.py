"""Extract structural signatures of positive Slack-CAGE prebank cases.

This is a diagnostic for the Flat5 eta-bank branch.  It reuses the exact
positive-prebank classifier and compresses each case to row-intersection data:

  * number, lengths, and geodesic denominators of counted rows;
  * intersections of counted rows with Q;
  * union size versus U size;
  * pairwise row intersections;
  * zero/flat/strict switch counts and switch sizes.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import multiprocessing as mp
import subprocess
from collections import Counter

with contextlib.redirect_stdout(io.StringIO()):
    from _h import GENG, dec
    from _stark1 import gmins
    from _codex_slack_cage_switch_gate import build_data
    from _codex_slack_cage_prebank_classifier import run_graph


def row_denominators(case):
    n, edges = dec(case["g6"])
    _adj, cuts = gmins(n, edges)
    side = [int(c) for c in cuts[case["cut"]]]
    data = build_data(n, edges, side)
    if data is None:
        return ()
    _E, _B, M, _Mset, cyc = data
    den = {tuple(g): len(cyc[g]) for g in M}
    return tuple(sorted(den[tuple(g)] for g, _P in case["counted"]))


def signature(case):
    Q = set(case["Q"])
    U = set(case["U"])
    rows = [(tuple(g), tuple(P)) for g, P in case["counted"]]
    row_sets = [set(P) for _g, P in rows]
    union = set().union(*row_sets) if row_sets else set()
    pair_inters = []
    for i in range(len(row_sets)):
        for j in range(i + 1, len(row_sets)):
            pair_inters.append(len(row_sets[i] & row_sets[j]))
    flat_sizes = sorted(len(s[2]) for s in case["flat"])
    zero_sizes = sorted(len(s[2]) for s in case["zero"])
    strict_sizes = sorted(len(s[2]) for s in case["strict"])
    return (
        ("n", case["n"]),
        ("m", case["m"]),
        ("pre", str(case["prebank"])),
        ("eta", str(case["eta"])),
        ("U", len(U)),
        ("rows", len(rows)),
        ("row_lengths", tuple(sorted(len(P) for _g, P in rows))),
        ("row_denominators", row_denominators(case)),
        ("Q_inters", tuple(sorted(len(set(P) & Q) for _g, P in rows))),
        ("row_pair_inters", tuple(sorted(pair_inters))),
        ("union", len(union)),
        ("U_eq_union", U == union),
        ("zero_count", len(case["zero"])),
        ("flat_count", len(case["flat"])),
        ("strict_count", len(case["strict"])),
        ("zero_sizes", tuple(zero_sizes)),
        ("flat_sizes", tuple(flat_sizes)),
        ("strict_sizes", tuple(strict_sizes)),
    )


def worker(g6):
    return run_graph(g6, None)


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

    sigs = Counter()
    examples = {}
    total = 0
    done = 0
    with mp.Pool(processes=args.workers) as pool:
        for cases in pool.imap_unordered(worker, graphs, chunksize=args.chunksize):
            done += 1
            for case in cases:
                total += 1
                sig = signature(case)
                sigs[sig] += 1
                examples.setdefault(sig, case)
            if done % 5000 == 0 or done == len(graphs):
                print(f"progress graphs={done}/{len(graphs)} cases={total}", flush=True)

    print("=== positive prebank signatures ===")
    print("n:", args.n)
    print("graphs:", len(graphs))
    print("cases:", total)
    print("unique_signatures:", len(sigs))
    for idx, (sig, count) in enumerate(sigs.most_common(), 1):
        print(f"--- signature {idx} count={count} ---")
        print(dict(sig))
        ex = examples[sig]
        print(
            {
                "g6": ex["g6"],
                "cut": ex["cut"],
                "side": ex["side"],
                "Q": ex["Q"],
                "U": ex["U"],
                "counted": ex["counted"],
                "zero": ex["zero"],
                "flat": ex["flat"],
                "strict": ex["strict"],
            }
        )


if __name__ == "__main__":
    main()
