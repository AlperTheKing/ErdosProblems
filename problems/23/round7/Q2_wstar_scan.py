"""Q2_wstar_scan.py -- the two-parameter obstruction family W*(u,r).

W*(u,r):  G = C5[2u, 2u, 3u, 2u, 3u]   (classes c0~c1~c2~c3~c4~c0),  N = 12u.
Cut:      X = c0 u c2 u (c3 minus r vertices),   Y = c1 u c4 u (those r vertices).

Exact closed forms (verified below):
  |E| = 2u*2u + 2u*3u + 3u*2u + 2u*3u + 3u*2u = 28u^2
  |M| = 3u(2u-r) + 3u*r = 6u^2      -- INDEPENDENT of r
  25|M| - N^2 = 150u^2 - 144u^2 = 6u^2 > 0        (|M|/N^2 = 1/24)
  bip(G) = min_i w_i w_{i+1} = 4u^2 = N^2/36      (G itself obeys the conjecture)
  sigma:  c0 = c1 = 5u,  c2 = 2r,  c3nX = c3nY = 0,  c4 = 4u - 2r

This scan reports for each (u,r) whether sigma>=0, all switch-stars, and the
whole family (*)  Delta(N(v) u T) <= 0  hold, and the exact minimum improving
switch size.
"""
from fractions import Fraction as Fr
from itertools import combinations
import sys


def build(u, r):
    w = [2 * u, 2 * u, 3 * u, 2 * u, 3 * u]
    cls, V = [], 0
    for i in range(5):
        cls.append(list(range(V, V + w[i]))); V += w[i]
    n = V
    adj = [set() for _ in range(n)]
    for i in range(5):
        j = (i + 1) % 5
        for x in cls[i]:
            for y in cls[j]:
                adj[x].add(y); adj[y].add(x)
    side = [0] * n
    for v in cls[1] + cls[4]:
        side[v] = 1
    for v in cls[3][:r]:
        side[v] = 1
    return n, adj, side, cls, w


def analyse(u, r, do_min=True):
    n, adj, side, cls, w = build(u, r)
    E = sum(len(adj[v]) for v in range(n)) // 2
    M = sum(1 for v in range(n) for x in adj[v] if x > v and side[x] == side[v])
    sig = [sum(1 if side[x] != side[v] else -1 for x in adj[v]) for v in range(n)]
    sigok = all(s >= 0 for s in sig)
    ssok = all(sig[v] >= sum(2 - sig[a] for a in adj[v] if side[a] != side[v] and sig[a] <= 1)
               for v in range(n))
    # groups of twins: (class, side)
    groups = {}
    for v in range(n):
        for i in range(5):
            if v in cls[i]:
                groups.setdefault((i, side[v]), []).append(v)
    gk = sorted(groups)
    # family (*): linear in T, T independent  <=>  union of groups whose class
    # indices are pairwise non-adjacent in C5.
    starok, worst = True, None
    seen = set()
    for v in range(n):
        key = tuple(sorted(adj[v])), side[v]
        gv = next(g for g in gk if v in groups[g])
        if gv in seen:
            continue
        seen.add(gv)
        Nv = adj[v]
        base = -sum(sig[a] for a in Nv)
        cw = {}
        for x in range(n):
            if x in Nv:
                continue
            b = sum(1 for t in adj[x] if t in Nv and side[t] != side[x])
            m = sum(1 for t in adj[x] if t in Nv and side[t] == side[x])
            cw[x] = -sig[x] + 2 * b - 2 * m
        cand = [g for g in gk if all(x not in Nv for x in groups[g])]
        best = base
        for rr in range(len(cand) + 1):
            for sel in combinations(cand, rr):
                idx = [g[0] for g in sel]
                if any((abs(p - q) % 5) in (1, 4) for p, q in combinations(idx, 2)):
                    continue
                tot = base + sum(max(cw[x], 0) for g in sel for x in groups[g])
                best = max(best, tot)
        if best > 0:
            starok = False
            worst = (gv, best)
    # minimum improving switch (twins => only group counts matter)
    minS = None
    if do_min:
        gl = [groups[g] for g in gk]
        sz = [len(g) for g in gl]
        sigg = [sig[g[0]] for g in gl]
        # inter-group edge type
        et = [[0] * len(gl) for _ in range(len(gl))]
        for A in range(len(gl)):
            for B in range(A + 1, len(gl)):
                a0, b0 = gl[A][0], gl[B][0]
                if b0 in adj[a0]:
                    et[A][B] = -2 if side[a0] == side[b0] else 2

        def rec(k, cur, tot):
            nonlocal minS
            if minS is not None and tot >= minS[0]:
                return
            if k == len(gl):
                d = -sum(cur[i] * sigg[i] for i in range(len(gl)))
                for A in range(len(gl)):
                    for B in range(A + 1, len(gl)):
                        if et[A][B]:
                            d += et[A][B] * cur[A] * cur[B]
                if d > 0 and (minS is None or tot < minS[0]):
                    minS = (tot, tuple(cur), d)
                return
            for c in range(sz[k] + 1):
                rec(k + 1, cur + [c], tot + c)
        rec(0, [], 0)
    return dict(n=n, E=E, M=M, sig=sig, sigok=sigok, ssok=ssok, starok=starok,
                worst=worst, minS=minS, groups=[(g, len(groups[g])) for g in gk])


if __name__ == "__main__":
    umax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    print("u  r |  N |  |E| | |M| | 25|M|-N^2 | |M|/N^2 | sigma>=0 switch-star family(*) | min improving |S| (/N)")
    for u in range(1, umax + 1):
        for r in range(1, 2 * u):
            d = analyse(u, r, do_min=(u <= 6))
            n, M = d["n"], d["M"]
            ok = d["sigok"] and d["ssok"]
            if not ok:
                continue
            ms = d["minS"]
            mstr = (f"{ms[0]} = {Fr(ms[0], n)}N = {float(Fr(ms[0],n)):.4f}" if ms else "n/a")
            print(f"{u:2d} {r:2d} | {n:2d} | {d['E']:4d} | {M:3d} | {25*M-n*n:9d} | "
                  f"{str(Fr(M,n*n)):7s} | {str(d['sigok']):5s} {str(d['ssok']):5s} "
                  f"{'PASSES(*)' if d['starok'] else 'caught by (*)':13s} | {mstr}")
