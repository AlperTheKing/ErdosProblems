"""Scout a component-surplus Hall form for the corrected level transport.

For PREFIX-LOAD-PSC-5, write eta=N^2/25-|M| and
alpha_j=25*(N+eta-(t_j+t_{j+1})).  Positive alpha bands are source;
negative alpha bands are volume sinks.  Pressure demand in band j is
5*N*sigma_j*width_j.

This diagnostic tests the prefix inequality

    pressure(prefix) <= sum_C max(0, source_C(prefix)-volume_C(prefix))

where C ranges over K-components from kcomponents().  It is stronger than
plain prefix positivity because it reserves each component's own surplus for
volume before allowing the remaining bank to pay global pressure.
"""

from collections import defaultdict
from fractions import Fraction as F
import subprocess

from _h import dec, GENG
from _stark1 import gmins
from _satzmu_conn import kcomponents, struct_for_side
from _codex_prefix_loadpsc_gate import adj_of, structured_cases


def rows(name, n, edges, side):
    adj = adj_of(n, edges)
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, _ell, T, _mu, cyc = st
    if not M:
        return []
    beta = len(M)
    eta = F(n * n, 25) - beta
    theta = (F(n) + eta) / 2
    levels = set([F(0), theta]) | set(F(t) for t in T if t > 0)
    levels = sorted(x for x in levels if x >= 0)
    comp_map, find = kcomponents(n, cyc)
    comps = sorted(set(find(v) for v in range(n)))
    edge = {(min(u, v), max(u, v)) for u, v in edges}
    bad = {(min(u, v), max(u, v)) for u, v in M}
    pressure = F(0)
    src = defaultdict(F)
    vol = defaultdict(F)
    out = []
    for idx, (a, b) in enumerate(zip(levels, levels[1:]), start=1):
        width = b - a
        if width <= 0:
            continue
        H = {v for v, t in enumerate(T) if F(t) > a}
        if not H:
            continue
        alpha = 25 * (F(n) + eta - (a + b))
        db = dm = 0
        for u, v in edge:
            if (u in H) ^ (v in H):
                e = (min(u, v), max(u, v))
                if e in bad:
                    dm += 1
                elif side[u] != side[v]:
                    db += 1
        sigma = db - dm
        for c in comps:
            hc = sum(1 for v in H if find(v) == c)
            amount = width * abs(alpha) * hc
            if alpha > 0:
                src[c] += amount
            elif alpha < 0:
                vol[c] += amount
        pressure += width * 5 * n * sigma
        bank = sum(max(F(0), src[c] - vol[c]) for c in comps)
        margin = bank - pressure
        out.append((margin, name, n, beta, idx, a, b, len(H), sigma, bank, pressure))
    return out


def census_cases(max_n):
    for nn in range(7, max_n + 1):
        out = subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True, check=True)
        count = 0
        for g6 in out.stdout.split():
            n, edges = dec(g6)
            _adj, cuts = gmins(n, edges)
            for side in cuts:
                count += 1
                yield f"cen{g6}", n, edges, side
        print(f"census N={nn} yielded {count} gamma-min cuts", flush=True)


def main():
    total = viol = 0
    best = None
    first = None
    for case in list(census_cases(11)) + list(structured_cases()):
        for row in rows(*case):
            total += 1
            if best is None or row[0] < best[0]:
                best = row
            if row[0] < 0:
                viol += 1
                if first is None:
                    first = row
    print("rows", total)
    print("violations", viol)
    print("best", best)
    print("first", first)


if __name__ == "__main__":
    main()
