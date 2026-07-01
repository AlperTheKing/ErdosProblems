"""Mine relation between R[v], Psi, and selected cap-expansion margins."""

import itertools
import subprocess
from collections import Counter
from fractions import Fraction as F

from _h import Bconn, GENG, dec, maxcut_all
from _satzmu_conn import struct_for_side
from _csmspec import build_K2
from _seedmoat_gate import find_seedmoat, vertex_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _codex_k2t_switch_signature_gate import terminal_shadow_details


def mask_of(vertices):
    out = 0
    for v in vertices:
        out |= 1 << v
    return out


def laminar_pair(a, b):
    return a <= b or b <= a or a.isdisjoint(b)


def leaves(miss_sets):
    nonempty = [set(s) for s in miss_sets if s]
    if any(not laminar_pair(a, b) for i, a in enumerate(nonempty) for b in nonempty[i + 1 :]):
        return None
    out = []
    for s in nonempty:
        if not any(t < s for t in nonempty):
            if not any(t == s for t in out):
                out.append(s)
    return out


def cap_min_gap(cap, exits_of_f, fset):
    best = None
    for r in range(1, len(cap) + 1):
        for sub in itertools.combinations(list(cap), r):
            y = set(sub)
            nbr = {f for f in fset if exits_of_f[f] & y}
            gap = len(nbr) - len(y)
            best = gap if best is None else min(best, gap)
    return best


def process_graph(name, n, edges, rows, hist):
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
            det = terminal_shadow_details(n, adj, side, st, mask_of(set(seed) | set(moat)))
            if det is None:
                continue
            fset = tuple(sorted(det["cross_m"]))
            eset = tuple(sorted(det["bdy_b"]))
            witnesses = {e: set(fs) for e, fs in det["witnesses"].items()}
            exits_of_f = {f: {e for e in eset if f in witnesses[e]} for f in fset}
            miss_sets = [set(eset) - exits_of_f[f] for f in fset]
            leaf_sets = leaves(miss_sets) or []
            gaps = tuple(sorted(cap_min_gap(cap, exits_of_f, fset) for cap in leaf_sets))
            margins = []
            for cap in leaf_sets:
                A = {f for f in fset if cap <= (set(eset) - exits_of_f[f])}
                margins.append(len(eset) - len(cap) - len(A))
            margins = tuple(sorted(margins))
            row = (name, n, "".join(map(str, side)), v, str(rv), det["psi"], len(fset), len(eset), tuple(sorted(seed)), tuple(sorted(moat)), gaps, margins)
            rows.append(row)
            hist[(str(-rv), det["psi"], gaps, margins)] += 1


def main():
    rows = []
    hist = Counter()
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, edges = dec(g6)
            process_graph(f"cen{nn}:{g6}", n, edges, rows, hist)
    hn, he = dec("H?AFBo]")
    n, edges = vertex_blowup(hn, he, 2)
    process_graph("H?AFBo]x2", n, edges, rows, hist)
    print("rows", len(rows))
    print("top hist")
    for k, c in hist.most_common(30):
        print(" ", k, c)
    print("sample")
    for row in rows[:30]:
        print(" ", row)


if __name__ == "__main__":
    main()
