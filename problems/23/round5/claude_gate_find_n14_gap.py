"""ROOT-AGENT GATE (Claude): find my own witness for (or against) registry entry A5.

A5 records "bip = 7 but nu* = tau* = 32/5 on the N = 14 extremal graph, integrality gap 35/32".
Uniform weights are a product weight, so if that is right, product-weight integrality (PWI) is
REFUTED outright, not merely conjecture-strength.  I could not reproduce it: C5[3,3,3,3,2] has
tau = 6 (not 7) and no gap, and ten other named triangle-free graphs show no gap either.

So I search the 1274 maximal triangle-free 14-vertex patterns directly: compute tau exactly at
uniform weights (integer minimum over all 8192 bipartitions), keep those attaining the maximum, and
run the odd-cycle covering LP on them.  A rational cover of cost < tau, feasible against every odd
cycle, is an exact refutation of PWI.
"""
import sys
from fractions import Fraction as F

import numpy as np
from scipy.optimize import linprog


def g6(s):
    b = [ord(c) - 63 for c in s]
    n = b[0]
    i = 1
    if n == 63:
        n = (b[1] << 12) | (b[2] << 6) | b[3]
        i = 4
    bits = []
    for x in b[i:]:
        bits.extend((x >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
    E, p = [], 0
    for j in range(1, n):
        for k in range(j):
            if bits[p]:
                E.append((k, j))
            p += 1
    return n, E


def tau_uniform(n, E, B):
    u = np.array([e[0] for e in E])
    v = np.array([e[1] for e in E])
    mono = (B[:, u] == B[:, v]).sum(axis=1)
    k = int(mono.argmin())
    return int(mono[k]), k


def odd_cycles(n, E, cap=400000):
    idx = {e: i for i, e in enumerate(E)}
    A = [set() for _ in range(n)]
    for a, b in E:
        A[a].add(b)
        A[b].add(a)
    out = set()
    sys.setrecursionlimit(10000)
    for s in range(n):
        def dfs(x, seen, el):
            if len(out) > cap:
                return
            for y in sorted(A[x]):
                if y == s and len(seen) >= 3 and len(seen) % 2 == 1:
                    out.add(frozenset(el + [idx[tuple(sorted((x, y)))]]))
                elif y > s and y not in seen:
                    dfs(y, seen | {y}, el + [idx[tuple(sorted((x, y)))]])
        dfs(s, {s}, [])
    return sorted(out, key=lambda c: (len(c), sorted(c)))


def gap_test(name, n, E, tau):
    oc = odd_cycles(n, E)
    Aub = np.zeros((len(oc), len(E)))
    for k, c in enumerate(oc):
        for i in c:
            Aub[k, i] = -1.0
    res = linprog(np.ones(len(E)), A_ub=Aub, b_ub=-np.ones(len(oc)),
                  bounds=[(0, None)] * len(E), method='highs')
    if not res.success:
        return f"{name}: LP failed"
    line = f"{name}: |E|={len(E)} odd cycles={len(oc)} tau={tau} tau*~{res.fun:.6f}"
    if res.fun < tau - 1e-7:
        for D in (2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 16, 20, 24, 30, 60):
            y = [F(int(round(t * D)), D) for t in res.x]
            if any(t < 0 for t in y):
                continue
            if all(sum(y[i] for i in c) >= 1 for c in oc) and sum(y) < tau:
                return line + f"   EXACT GAP cover cost {sum(y)} < {tau} (1/{D}) -> PWI REFUTED"
        return line + "   numeric gap, no small-denominator exact cover"
    return line + "   no gap"


def main(path):
    B = np.array([[(m >> i) & 1 for i in range(14)] for m in range(1 << 13)], dtype=np.int8)
    rows = []
    for line in open(path):
        s = line.strip()
        if not s:
            continue
        n, E = g6(s)
        if n != 14:
            continue
        t, _ = tau_uniform(n, E, B)
        rows.append((t, s, E))
    rows.sort(key=lambda r: -r[0])
    best = rows[0][0]
    print(f"{len(rows)} maximal triangle-free 14-vertex patterns; max tau at uniform weight = {best}"
          f"  (conjecture ceiling floor(196/25) = 7)", flush=True)
    top = [r for r in rows if r[0] == best]
    print(f"attaining it: {len(top)}", flush=True)
    for t, s, E in top[:12]:
        print("  " + gap_test(s, 14, E, t), flush=True)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'mtfall_14.g6')
