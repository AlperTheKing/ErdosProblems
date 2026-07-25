"""ROOT-AGENT probe (Claude, round 3): the ARC-CUT conjecture for the Andrasfai family.

And(k) is the circular complete graph K_{(3k-1)/k}: vertices Z_m with m = 3k-1, and u ~ v iff the
CIRCULAR DISTANCE between u and v is at least k.  (Verified here, independently of the G8 report.)

R3-C1 says a proof must read the weights: no fixed distribution of cuts can certify 1/25.  The
cheapest weight-reading rule available on a circular graph is "choose the best ARC":

        ARCBOUND(x) := min over all arcs A = {i, i+1, ..., i+l-1} of
                       [ weight of adjacent pairs inside A  +  weight of adjacent pairs inside V-A ].

Since every arc cut is a cut, psi(And(k), x) <= ARCBOUND(x) always.  The question is whether the
arc family alone already certifies the ceiling:

        CONJECTURE (arc-cut).   ARCBOUND(x) <= (sum x)^2 / 25   for every nonnegative x on And(k).

Two facts make it plausible and non-vacuous:
  * on the 5-point uniform weighting (an induced C5) every good arc gives exactly 1/25, so the
    conjecture is TIGHT there and cannot be proved by slack;
  * on the uniform weighting the best arc is a half-circle and gives 1/36 asymptotically, which is
    the true value, so the family is not merely tight in one place.
A single counterexample kills the mechanism; exhaustive search over integer weightings decides it
for each k in a finite computation.  All arithmetic is Fraction.
"""
from fractions import Fraction as F
from itertools import combinations
import random
import sys


def andrasfai(k):
    m = 3 * k - 1
    adj = [[False] * m for _ in range(m)]
    for u in range(m):
        for v in range(m):
            if u != v:
                d = min((u - v) % m, (v - u) % m)
                adj[u][v] = (d >= k)
    return m, adj


def check_definition(k):
    """circular-distance form must agree with the residue-1-mod-3 circulant, up to isomorphism"""
    m = 3 * k - 1
    S = {s for s in range(1, m) if s % 3 == 1}
    m2, adj = andrasfai(k)
    # the multiplier v -> k*v mod m carries {1,4,...} onto the distance form
    ok = True
    for u in range(m):
        for v in range(m):
            if u == v:
                continue
            a = ((v - u) % m) in S
            b = adj[(k * u) % m][(k * v) % m]
            if a != b:
                ok = False
    return ok


def arc_bound(m, adj, x):
    """min over arcs of the monochromatic weight"""
    best = None
    for i in range(m):
        for l in range(0, m + 1):
            A = [(i + t) % m for t in range(l)]
            Aset = set(A)
            B = [v for v in range(m) if v not in Aset]
            s = F(0)
            for u, v in combinations(A, 2):
                if adj[u][v]:
                    s += x[u] * x[v]
            for u, v in combinations(B, 2):
                if adj[u][v]:
                    s += x[u] * x[v]
            if best is None or s < best:
                best = s
    return best


def psi_all_cuts(m, adj, x):
    best = None
    E = [(u, v) for u in range(m) for v in range(u + 1, m) if adj[u][v]]
    for msk in range(1 << (m - 1)):
        S = (msk << 1) | 1
        s = F(0)
        for (u, v) in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                s += x[u] * x[v]
        if best is None or s < best:
            best = s
    return best


def exhaustive(k, qmax, verbose=True):
    """all integer weight vectors with sum q <= qmax, canonicalised by rotation/reflection"""
    m, adj = andrasfai(k)
    worst = None                      # largest 25*ARCBOUND - q^2 seen
    worst_vec = None
    for q in range(1, qmax + 1):
        parts = [0] * m

        def rec(i, rem):
            nonlocal worst, worst_vec
            if i == m - 1:
                parts[i] = rem
                # canonical form under rotation only (cheap)
                if any(tuple(parts[(r + t) % m] for t in range(m)) < tuple(parts)
                       for r in range(1, m)):
                    return
                x = [F(p) for p in parts]
                b = arc_bound(m, adj, x)
                val = 25 * b - F(q * q)
                if worst is None or val > worst:
                    worst, worst_vec = val, list(parts)
                return
            for t in range(rem + 1):
                parts[i] = t
                rec(i + 1, rem - t)
            parts[i] = 0

        rec(0, q)
        if verbose:
            print(f"   k={k} m={m} q={q:3d}: max over all weightings of 25*ARCBOUND - q^2 = {worst}"
                  f"   {'*** ARC CUTS INSUFFICIENT ***' if worst > 0 else ''}")
        if worst > 0:
            print("   witness weights:", worst_vec)
            return False
    return True


if __name__ == '__main__':
    print("definition check (circular-distance form == residue circulant):",
          {k: check_definition(k) for k in range(2, 8)})
    print()
    # sanity: the 5-point uniform weighting inside And(7) (m=20, points 0,4,8,12,16)
    m, adj = andrasfai(7)
    x = [F(0)] * m
    for p in (0, 4, 8, 12, 16):
        x[p] = F(1, 5)
    print("And(7), uniform on 5 equally spaced points: ARCBOUND =", arc_bound(m, adj, x),
          " (1/25 =", F(1, 25), ")")
    # sanity: uniform weighting on And(k)
    for k in (3, 4, 5, 6, 7):
        m, adj = andrasfai(k)
        x = [F(1, m)] * m
        ab = arc_bound(m, adj, x)
        print(f"And({k}) uniform: ARCBOUND = {ab} = {float(ab):.6f}   (1/25 = 0.04, "
              f"asymptotic half-circle value 1/36 = 0.02778)")
    print()
    qmax = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    for k in (2, 3, 4):
        ok = exhaustive(k, qmax)
        print(f"   => k={k}: arc-cut conjecture {'SURVIVES' if ok else 'FALSE'} for all "
              f"integer weightings with sum <= {qmax}\n")
