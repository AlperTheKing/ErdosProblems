"""Mine residuals at inside endpoints of side-cap subsets.

This compares selected R[v]<0 seed+moat caps with broader positive-Psi
two-cap switches.  It is meant to identify the selector ingredient behind
strict cap expansion.
"""

import argparse
import itertools
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _codex_k2t_switch_probe import adj_from_edges, boundary_delta
from _codex_k2t_switch_signature_gate import terminal_shadow_details


def mask_of(vertices):
    out = 0
    for v in vertices:
        out |= 1 << v
    return out


def inside_endpoint(edge, smask):
    a, b = edge
    ain = (smask >> a) & 1
    bin_ = (smask >> b) & 1
    if ain and not bin_:
        return a
    if bin_ and not ain:
        return b
    return None


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


def inspect_switch(tag, name, n, adj, side, st, R, smask, rows, hist, limit_fail=8):
    det = terminal_shadow_details(n, adj, side, st, smask)
    if det is None or det["psi"] <= 0:
        return
    fset = tuple(sorted(det["cross_m"]))
    eset = tuple(sorted(det["bdy_b"]))
    witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
    exits_of_f = {f: {e for e in eset if f in witnesses[e]} for f in fset}
    miss_sets = [set(eset) - exits_of_f[f] for f in fset]
    leaves = leaf_caps(miss_sets)
    if leaves is None or len(leaves) > 2:
        return
    leaf_union = set().union(*leaves) if leaves else set()
    if any(witnesses[e] != set(fset) for e in set(eset) - leaf_union):
        return
    for ms in miss_sets:
        rebuilt = set()
        for leaf in leaves:
            if leaf <= ms:
                rebuilt |= leaf
        if rebuilt != ms:
            return

    for cap in leaves:
        cap = list(cap)
        for r in range(1, len(cap) + 1):
            for sub in itertools.combinations(cap, r):
                y = set(sub)
                nbr = {f for f in fset if exits_of_f[f] & y}
                gap = len(nbr) - len(y)
                inside = tuple(sorted({inside_endpoint(e, smask) for e in y}))
                rvals = tuple(sorted(str(R[x]) for x in inside))
                hist[(tag, gap, len(y), len(nbr), rvals)] += 1
                if gap <= 0 and len(rows) < limit_fail:
                    rows.append((tag, name, n, "".join(map(str, side)), tuple(i for i in range(n) if (smask >> i) & 1), det["psi"], tuple(sorted(y)), tuple(sorted(nbr)), gap, inside, rvals))


def scan_selected(rows, hist):
    def process(name, n, edges):
        adj = adj_from_edges(n, edges)
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
            gamma0 = sum(ell[f] ** 2 for f in M)
            for v, rv in enumerate(R):
                if rv >= 0:
                    continue
                sm = find_seedmoat(n, adj, side, v, M, ell, cyc, gamma0, max_moat=1)
                if sm is None:
                    continue
                seed, moat, _drop = sm
                inspect_switch("selected", name, n, adj, side, st, R, mask_of(set(seed) | set(moat)), rows, hist)

    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            process(f"cen{nn}:{g6}", n, edges)
    hn, he = dec("H?AFBo]")
    n, edges = vertex_blowup(hn, he, 2)
    process("H?AFBo]x2", n, edges)


def scan_broad(rows, hist, max_n):
    for nn in range(5, max_n + 1):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            adj = adj_from_edges(n, edges)
            for side in maxcut_all(n, adj):
                if not Bconn(n, adj, side):
                    continue
                st = struct_for_side(n, adj, side)
                if st is None:
                    continue
                M, _ell, T, _mu, cyc = st
                if not M:
                    continue
                K2 = build_K2(n, M, cyc)
                R = [F(n) * T[v] - sum(K2[v][w] * T[w] for w in range(n)) for v in range(n)]
                for mask in range(1, (1 << n) - 1):
                    if boundary_delta(n, adj, side, mask) != 0:
                        continue
                    inspect_switch("broad", g6, n, adj, side, st, R, mask, rows, hist)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--broad-max-n", type=int, default=10)
    args = ap.parse_args()
    rows = []
    hist = Counter()
    scan_selected(rows, hist)
    scan_broad(rows, hist, args.broad_max_n)
    print("hist top")
    for k, c in hist.most_common(40):
        print(" ", k, c)
    print("gap<=0 examples")
    for row in rows:
        print(" ", row)


if __name__ == "__main__":
    main()
