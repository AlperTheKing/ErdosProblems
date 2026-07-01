"""Mine deficient-cap template signatures.

Signature fields:
  (|C|, sorted crossing lengths, sorted witness-degree multiset, |Y|, gap)

Here C=delta_M(S), Y is the first deficient cap subset found by the shared
deficient_cap_subset helper, and gap=|N(Y)|-|Y| <= 0.
"""

import argparse
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details
from _codex_defcap_negative_scope_gate import two_cap_data, deficient_cap_subset


def scan_graph(n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        _M, ell, _T, _mu, _cyc = st
        for mask in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            det = terminal_shadow_details(n, adj, side, st, mask)
            if det is None or det["psi"] <= 0:
                continue
            data = two_cap_data(det)
            if data is None:
                continue
            fset, eset, exits_of_f, leaves = data
            bad = deficient_cap_subset(leaves, exits_of_f, fset)
            if bad is None:
                continue
            y, nbr, gap = bad
            witnesses = {e: set(det["witnesses"][e]) for e in eset}
            sig = (
                len(fset),
                tuple(sorted(ell[f] for f in fset)),
                tuple(sorted(len(witnesses[e]) for e in eset)),
                len(y),
                gap,
            )
            acc["defcap"] += 1
            acc["sig"][sig] += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=11)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--progress", type=int, default=5000)
    args = ap.parse_args()
    acc = {"defcap": 0, "sig": Counter()}
    g6s = subprocess.run([GENG, "-tc", str(args.n)], capture_output=True, text=True).stdout.split()
    processed = 0
    for idx, g6 in enumerate(g6s):
        if idx % args.nshards != args.shard:
            continue
        n, edges = dec(g6)
        scan_graph(n, edges, acc)
        processed += 1
        if args.progress and processed % args.progress == 0:
            print(
                "progress",
                "shard",
                args.shard,
                "/",
                args.nshards,
                "processed",
                processed,
                "defcap",
                acc["defcap"],
                flush=True,
            )
    print("N", args.n)
    print("shard", args.shard, "nshards", args.nshards, "processed", processed, "total_graphs", len(g6s))
    print("defcap", acc["defcap"])
    print("signatures")
    for sig, count in sorted(acc["sig"].items(), key=lambda kv: (-kv[1], kv[0])):
        print(count, sig)
    print("VERDICT: DONE")


if __name__ == "__main__":
    main()
