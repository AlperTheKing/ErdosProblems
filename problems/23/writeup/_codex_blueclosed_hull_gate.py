"""Gate the blue-closed hull proof atom for terminal-shadow SDR.

For every neutral terminal-shadow switch S and every subfamily X of crossing
bad edges, let Y=Wit(X).  Build U from all terminal prefixes of edges in X,
then close U inside S under blue/cut edges.  The checked sufficient conditions
for Hall are:

  1. X subset delta_M(U).
  2. The extra-exit graph delta_B(U)\\Y -- delta_M(U)\\X has a matching
     saturating delta_B(U)\\Y, using the original witness relation.

Then max-cut gives |Y|>=|X|.  This is a proof-atom gate, not the proof.
"""

import argparse
import subprocess

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import max_bipartite_matching, terminal_shadow_details
from _codex_sidedoor_prefix_hull_gate import crossing_prefixes, edge_boundary


def mask_tuple(n, mask):
    return tuple(i for i in range(n) if (mask >> i) & 1)


def blue_close_inside_s(n, adj, side, mask_s, mask_u):
    changed = True
    while changed:
        changed = False
        for u in range(n):
            if not ((mask_u >> u) & 1):
                continue
            for v in adj[u]:
                if ((mask_s >> v) & 1) and not ((mask_u >> v) & 1) and side[u] != side[v]:
                    mask_u |= 1 << v
                    changed = True
    return mask_u


def scan_graph(name, n, edges, acc, cap):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        cyc = st[4]
        for mask_s in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask_s) != 0:
                continue
            det = terminal_shadow_details(n, adj, side, st, mask_s)
            if det is None or not det["cross_m"] or len(det["cross_m"]) != len(det["bdy_b"]):
                continue
            cross = list(det["cross_m"])
            witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
            exits_of_f = {f: set() for f in cross}
            for e, fs in witnesses.items():
                for f in fs:
                    exits_of_f[f].add(e)
            prefixes = {f: crossing_prefixes(mask_s, f, cyc[f]) for f in cross}
            for bits in range(1, 1 << len(cross)):
                x_set = {cross[i] for i in range(len(cross)) if (bits >> i) & 1}
                y_set = set().union(*(exits_of_f[f] for f in x_set))
                mask_u = 0
                for f in x_set:
                    for e in exits_of_f[f]:
                        for pmask in prefixes[f].get(e, ()):
                            mask_u |= pmask
                mask_u = blue_close_inside_s(n, adj, side, mask_s, mask_u)
                bdu, mdu = edge_boundary(n, adj, side, mask_u)
                extra_b = tuple(sorted(bdu - y_set))
                extra_m = tuple(sorted(mdu - x_set))
                acc["subsets"] += 1
                if not x_set <= mdu:
                    acc["fail"] += 1
                    if acc["first_fail"] is None:
                        acc["first_fail"] = (
                            name,
                            n,
                            "".join(map(str, side)),
                            mask_tuple(n, mask_s),
                            "X-not-in-dM",
                            tuple(sorted(x_set)),
                            mask_tuple(n, mask_u),
                            tuple(sorted(mdu)),
                        )
                    return False
                if extra_b:
                    extra_adj = {
                        e: [f for f in witnesses.get(e, set()) if f in extra_m]
                        for e in extra_b
                    }
                    match_size, _matching = max_bipartite_matching(extra_b, extra_m, extra_adj)
                    acc["extra_cases"] += 1
                    if match_size < len(extra_b):
                        acc["fail"] += 1
                        if acc["first_fail"] is None:
                            acc["first_fail"] = (
                                name,
                                n,
                                "".join(map(str, side)),
                                mask_tuple(n, mask_s),
                                "extra-SDR",
                                tuple(sorted(x_set)),
                                tuple(sorted(y_set)),
                                mask_tuple(n, mask_u),
                                extra_b,
                                extra_m,
                                match_size,
                            )
                        return False
                if cap and acc["subsets"] >= cap:
                    return True
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=10)
    parser.add_argument("--cap", type=int, default=0, help="Optional global subset cap.")
    args = parser.parse_args()

    acc = dict(subsets=0, extra_cases=0, fail=0, first_fail=None)
    for nn in range(args.min_n, args.max_n + 1):
        before = acc["subsets"]
        before_extra = acc["extra_cases"]
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            if not scan_graph(g6, n, edges, acc, args.cap):
                break
            if args.cap and acc["subsets"] >= args.cap:
                break
        print(
            "N=%d subsets=%d extra_cases=%d fail=%d"
            % (nn, acc["subsets"] - before, acc["extra_cases"] - before_extra, acc["fail"]),
            flush=True,
        )
        if acc["fail"] or (args.cap and acc["subsets"] >= args.cap):
            break
    print("=" * 72)
    print("subsets:", acc["subsets"])
    print("extra cases:", acc["extra_cases"])
    print("fail:", acc["fail"], acc["first_fail"] or "")
    print("VERDICT:", "PASS" if acc["fail"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
