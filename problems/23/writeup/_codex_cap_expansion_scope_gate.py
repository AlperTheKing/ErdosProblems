"""Scope test for strict side-cap expansion.

Question: does strict cap expansion need the full R[v]<0 selected seed+moat
hypothesis, or does it already follow from a broader package such as
neutral terminal-shadow + two-cap decomposition + Psi>0?
"""

import argparse
import itertools
import subprocess
from collections import Counter

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details


def laminar_pair(a, b):
    return a <= b or b <= a or a.isdisjoint(b)


def leaf_caps(miss_sets):
    nonempty = [set(s) for s in miss_sets if s]
    if any(not laminar_pair(a, b) for i, a in enumerate(nonempty) for b in nonempty[i + 1 :]):
        return None
    leaves = []
    for s in nonempty:
        if not any(t < s for t in nonempty):
            if not any(t == s for t in leaves):
                leaves.append(s)
    return leaves


def cap_expands(cap, exits_of_f, fset):
    cap = list(cap)
    for r in range(1, len(cap) + 1):
        for sub in itertools.combinations(cap, r):
            y = set(sub)
            nbr = {f for f in fset if exits_of_f[f] & y}
            if len(nbr) <= len(y):
                return False, (tuple(sorted(y)), tuple(sorted(nbr)), len(nbr) - len(y))
    return True, None


def scan_graph(name, n, edges, acc):
    adj = adj_from_edges(n, edges)
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        for mask in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            det = terminal_shadow_details(n, adj, side, st, mask)
            if det is None or not det["cross_m"] or len(det["cross_m"]) != len(det["bdy_b"]):
                continue
            acc["neutral_terminal"] += 1
            if det["psi"] <= 0:
                continue
            acc["positive_psi"] += 1
            fset = tuple(sorted(det["cross_m"]))
            eset = tuple(sorted(det["bdy_b"]))
            witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
            exits_of_f = {f: {e for e in eset if f in witnesses[e]} for f in fset}
            miss_sets = [set(eset) - exits_of_f[f] for f in fset]
            leaves = leaf_caps(miss_sets)
            if leaves is None or len(leaves) > 2:
                continue
            leaf_union = set().union(*leaves) if leaves else set()
            if any(witnesses[e] != set(fset) for e in set(eset) - leaf_union):
                continue
            ok_union = True
            for ms in miss_sets:
                rebuilt = set()
                for leaf in leaves:
                    if leaf <= ms:
                        rebuilt |= leaf
                if rebuilt != ms:
                    ok_union = False
                    break
            if not ok_union:
                continue
            acc["two_cap_positive"] += 1
            for cap in leaves:
                ok, bad = cap_expands(cap, exits_of_f, fset)
                acc["caps"] += 1
                if not ok:
                    acc["fail"] += 1
                    if acc["first"] is None:
                        acc["first"] = (name, n, "".join(map(str, side)), tuple(i for i in range(n) if (mask >> i) & 1), det["psi"], tuple(sorted(cap)), bad)
                    return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    args = ap.parse_args()
    acc = Counter()
    acc["first"] = None
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            scan_graph(g6, n, edges, acc)
            if acc["first"] is not None:
                break
        print("N", nn, dict(acc), flush=True)
        if acc["first"] is not None:
            break
    print("VERDICT:", "PASS" if acc["first"] is None else "FAIL")


if __name__ == "__main__":
    main()
