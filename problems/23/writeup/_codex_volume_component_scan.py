"""Scout the per-K-component volume Hall condition in level transport.

In `_level_transport.py`, volume sinks must be paid inside the same K-component
with causal arcs i<=j.  For each component C this one-dimensional causal
transport is feasible iff every prefix has nonnegative cumulative balance:

    Source_C(k) - Volume_C(k) >= 0.

Here alpha_j=25*(N+eta-(t_j+t_{j+1})), eta=N^2/25-|M|, and source/volume
use Delta_j*|alpha_j|*|H_j cap C| according to the sign of alpha_j.
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
    _comp_map, find = kcomponents(n, cyc)
    comps = sorted(set(find(v) for v in range(n)))
    balance = defaultdict(F)
    out = []
    for idx, (a, b) in enumerate(zip(levels, levels[1:]), start=1):
        width = b - a
        if width <= 0:
            continue
        H = {v for v, t in enumerate(T) if F(t) > a}
        if not H:
            continue
        alpha = 25 * (F(n) + eta - (a + b))
        for c in comps:
            hc = sum(1 for v in H if find(v) == c)
            amount = width * alpha * hc
            balance[c] += amount
            out.append((balance[c], name, n, beta, idx, c, a, b, len(H), hc, alpha))
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
