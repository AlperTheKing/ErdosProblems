"""Canonical form of the item-7 falsifier: exhaustive sweep over ROTATION-SYMMETRIC measures.

The hill-climber's witness on Gamma_20 has g == 3/8 constant and every bound_k == A == 3/64.
That smells like a symmetric family, so here every r-fold symmetric integer measure on Gamma_M
(r = 3 and r = 5) with small weights is enumerated exactly and scored on

    A ,  min_b m(b) ,  ARCBOUND ,  min_supp g   (the delta > 1/3 hypothesis) .

A configuration with min(A, min_b m(b)) > 1/25 refutes item 7; if in addition min g > 1/3 it
refutes item 7 inside the exact class that the Brandt-Thomasse reduction delivers.
"""
import itertools
from fractions import Fraction as F
from P4_core import (from_gamma, sort_cyclic, adjacency, W_of, T_of, A_of, g_of, m_values,
                     arcbound, psi, TARGET)

BEST = []


def sweep(M, r, wmax):
    d = M // r
    found = []
    for base in itertools.product(range(wmax + 1), repeat=d):
        if sum(base) == 0 or base[0] == 0:
            continue
        w = list(base) * r
        pos, wt = sort_cyclic(*from_gamma(M, w))
        adj = adjacency(pos)
        Wv = W_of(pos, wt, adj)
        if Wv == 0:
            continue
        A = A_of(pos, wt, adj)
        if A <= TARGET:
            continue
        mv = m_values(pos, wt, adj)
        mm = min(mv)
        if mm <= TARGET:
            continue
        g = g_of(pos, wt, adj)
        ab = arcbound(pos, wt, adj)
        found.append((min(A, mm), A, mm, min(g), ab, tuple(base), len(pos)))
    found.sort(reverse=True)
    return found


if __name__ == '__main__':
    print("=" * 104)
    print("exhaustive sweep of r-fold symmetric integer measures: which ones defeat BOTH A and the")
    print("whole g^k hierarchy (i.e. min(A, min_b m(b)) > 1/25) ?")
    print("=" * 104)
    for M, r, wmax in ((15, 3, 4), (18, 3, 4), (21, 3, 3), (24, 3, 3), (12, 3, 5),
                       (20, 5, 4), (25, 5, 3), (15, 5, 4), (30, 5, 2)):
        f = sweep(M, r, wmax)
        print(f"\n  Gamma_{M}, {r}-fold symmetric, weights <= {wmax}: {len(f)} configurations "
              f"defeat both certificates")
        for rec in f[:4]:
            j1, A, mm, ming, ab, base, natoms = rec
            print(f"    base weights {base} (x{r})  atoms={natoms}  "
                  f"A={A}={float(A):.6f}  min m={mm}={float(mm):.6f}  "
                  f"min g={ming}={float(ming):.4f}{' >1/3 OK' if ming > F(1,3) else ' (<=1/3)'}  "
                  f"ARCBOUND={ab}={float(ab):.6f}")
            BEST.append((j1, M, r, base))
    BEST.sort(reverse=True)
    print("\n" + "=" * 104)
    print("BEST OVERALL (largest min(A, min_b m(b))):")
    for j1, M, r, base in BEST[:8]:
        w = list(base) * r
        pos, wt = sort_cyclic(*from_gamma(M, w))
        adj = adjacency(pos)
        print(f"  Gamma_{M} base {base} x{r}: min(A,min m) = {j1} = {float(j1):.6f} = "
              f"{float(j1)*25:.4f}/25   psi = {psi(pos,wt,adj)}")
