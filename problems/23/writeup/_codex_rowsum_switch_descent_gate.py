"""Gate: ROWSUM-violating max cuts should have a neutral Gamma descent.

This is a diagnostic for the full-set ROWSUM crux, not a proof.  It searches
connected-B maximum cuts.  When some bad edge has ROWSUM(f)>N, it looks for a
small vertex flip W such that:

  * delta_B(W)=delta_M(W), so the cut size is unchanged;
  * B remains connected after the flip;
  * Gamma strictly decreases.

The hard-H3 inherited cut is included because it is a useful non-gamma-min
model where ROWSUM fails and Gamma-minimality must supply a descent.
"""

import argparse
import itertools
import subprocess
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta, flip_side, gamma_of
from _codex_length_tier_matching_gate import h_blowup


def cut_size(n, adj, side):
    return sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])


def rowsum_violations(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, _T, _mu, cyc = st
    S = [F(0) for _ in range(n)]
    pf = {}
    for g in M:
        d = {}
        rows = cyc[g]
        for P in rows:
            for v in P:
                d[v] = d.get(v, F(0)) + F(1, len(rows))
        pf[g] = d
        for v, pv in d.items():
            S[v] += pv
    out = []
    for f, d in pf.items():
        row = sum(pv * S[v] for v, pv in d.items())
        if row > n:
            out.append((f, row, ell[f]))
    return st, out


def find_descent(n, adj, side, gamma0, max_k):
    for k in range(1, max_k + 1):
        for W in itertools.combinations(range(n), k):
            mask = sum(1 << v for v in W)
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            side2 = flip_side(side, mask)
            if not Bconn(n, adj, side2):
                continue
            gamma2 = gamma_of(n, adj, side2)
            if gamma2 is not None and gamma2 < gamma0:
                return W, gamma2
    return None


def scan_cut(name, n, adj, side, max_k, acc):
    if not Bconn(n, adj, side):
        return
    got = rowsum_violations(n, adj, side)
    if got is None:
        return
    st, viols = got
    if not viols:
        return
    gamma0 = sum(st[2])
    acc["violating_cuts"] += 1
    acc["violating_rows"] += len(viols)
    res = find_descent(n, adj, side, gamma0, max_k)
    if res is None:
        acc["no_descent"] += 1
        if acc["first"] is None:
            acc["first"] = {
                "name": name,
                "n": n,
                "side": "".join(map(str, side)),
                "gamma": gamma0,
                "violations": [(f, str(row), ell) for f, row, ell in viols[:5]],
            }
        return
    W, gamma2 = res
    acc["has_descent"] += 1
    acc["switch_sizes"][len(W)] = acc["switch_sizes"].get(len(W), 0) + 1
    if len(acc["examples"]) < 10:
        acc["examples"].append({
            "name": name,
            "n": n,
            "gamma": gamma0,
            "after": gamma2,
            "W": W,
            "violations": [(f, str(row), ell) for f, row, ell in viols[:3]],
        })


def scan_graph(name, n, edges, max_k, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        scan_cut(name, n, adj, side, max_k, acc)


def new_acc():
    return {
        "violating_cuts": 0,
        "violating_rows": 0,
        "has_descent": 0,
        "no_descent": 0,
        "switch_sizes": {},
        "examples": [],
        "first": None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--max-k", type=int, default=4)
    ap.add_argument("--h3-hard", action="store_true")
    args = ap.parse_args()

    acc = new_acc()
    if args.h3_hard:
        n, edges, _ = h_blowup(3)
        adj = adj_from_edges(n, edges)
        side = [int(c) for c in "111111111111111100000000000"]
        scan_cut("H3-hard", n, adj, side, args.max_k, acc)

    for nn in range(5, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph("cen%d_%s" % (nn, g6), n, edges, args.max_k, acc)
        print("census N=%d done: violating_cuts=%d no_descent=%d" %
              (nn, acc["violating_cuts"], acc["no_descent"]), flush=True)

    print("violating_cuts:", acc["violating_cuts"])
    print("violating_rows:", acc["violating_rows"])
    print("has_descent:", acc["has_descent"])
    print("no_descent:", acc["no_descent"])
    print("switch_sizes:", acc["switch_sizes"])
    print("examples:", acc["examples"])
    print("first:", acc["first"] or "")
    print("VERDICT:", "PASS" if acc["no_descent"] == 0 else "FAIL")


if __name__ == "__main__":
    main()
