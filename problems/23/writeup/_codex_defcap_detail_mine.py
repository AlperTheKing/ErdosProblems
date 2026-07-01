"""Print the exact deficient-cap cases behind the negative-residual scope gate.

This is a read-only diagnostic for the selected K2T Hall proof target.  It
lists positive-Psi two-cap switches with a deficient side-cap subset and their
residual signs on the switch vertices.
"""

import argparse
import itertools
import subprocess
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
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


def two_cap_data(det):
    fset = tuple(sorted(det["cross_m"]))
    eset = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: {e for e in eset if f in witnesses[e]} for f in fset}
    miss_sets = [set(eset) - exits_of_f[f] for f in fset]
    leaves = leaf_caps(miss_sets)
    if leaves is None or len(leaves) > 2:
        return None
    leaf_union = set().union(*leaves) if leaves else set()
    if any(witnesses[e] != set(fset) for e in set(eset) - leaf_union):
        return None
    for ms in miss_sets:
        rebuilt = set()
        for leaf in leaves:
            if leaf <= ms:
                rebuilt |= leaf
        if rebuilt != ms:
            return None
    return fset, eset, witnesses, exits_of_f, leaves


def deficient_subsets(leaves, exits_of_f, fset):
    out = []
    for cap in leaves:
        cap = list(cap)
        for r in range(1, len(cap) + 1):
            for sub in itertools.combinations(cap, r):
                y = set(sub)
                nbr = {f for f in fset if exits_of_f[f] & y}
                gap = len(nbr) - len(y)
                if gap <= 0:
                    out.append((tuple(sorted(y)), tuple(sorted(nbr)), gap))
    return out


def scan_graph(name, n, edges, limit):
    adj = adj_from_edges(n, edges)
    printed = 0
    for side in maxcut_all(n, adj):
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, _mu, cyc = st
        if not M:
            continue
        K2 = build_K2(n, M, cyc)
        R = [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
        for mask in range(1, (1 << n) - 1):
            if boundary_delta(n, adj, side, mask) != 0:
                continue
            det = terminal_shadow_details(n, adj, side, st, mask)
            if det is None or det["psi"] <= 0:
                continue
            data = two_cap_data(det)
            if data is None:
                continue
            fset, eset, witnesses, exits_of_f, leaves = data
            bads = deficient_subsets(leaves, exits_of_f, fset)
            if not bads:
                continue
            s_vertices = tuple(i for i in range(n) if (mask >> i) & 1)
            print("CASE", name, "n", n, "side", "".join(map(str, side)), "S", s_vertices, "psi", det["psi"])
            print("  crossM", fset)
            print("  bdyB", eset)
            print("  ell", {f: ell[f] for f in fset})
            print("  witnesses", {e: tuple(sorted(witnesses[e])) for e in eset})
            print("  leaves", tuple(tuple(sorted(c)) for c in leaves))
            print("  deficient", bads)
            print("  R_on_S", tuple((v, str(R[v])) for v in s_vertices))
            print("  min_R_on_S", min(R[v] for v in s_vertices))
            printed += 1
            if limit and printed >= limit:
                return printed
    return printed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=5)
    ap.add_argument("--max-n", type=int, default=10)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    total = 0
    for nn in range(args.min_n, args.max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            total += scan_graph(g6, n, edges, None if args.limit == 0 else args.limit - total)
            if args.limit and total >= args.limit:
                break
        if args.limit and total >= args.limit:
            break
    print("TOTAL", total)


if __name__ == "__main__":
    main()
