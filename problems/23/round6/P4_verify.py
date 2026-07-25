"""Exact (Fraction) verification of any candidate produced by P4_search.py.

usage:  python P4_verify.py M w0,w1,...,w_{M-1}
Prints the full certificate: W, T, A, g, m(b), bound_k for k=0..24, min_b m(b), ARCBOUND, psi.
"""
import sys
from fractions import Fraction as F
from P4_core import (from_gamma, adjacency, sort_cyclic, W_of, T_of, A_of, g_of, m_values,
                     bound_k, arcbound, psi, TARGET)


def report(m, weights, kmax=24, do_psi=True):
    pos, wt = from_gamma(m, weights)
    pos, wt = sort_cyclic(pos, wt)
    adj = adjacency(pos)
    W = W_of(pos, wt, adj)
    T = T_of(pos, wt, adj)
    A = A_of(pos, wt, adj)
    g = g_of(pos, wt, adj)
    mv = m_values(pos, wt, adj)
    var = sum(wt[i] * g[i] ** 2 for i in range(len(pos))) - (2 * W) ** 2
    print(f"Gamma_{m}, integer weights {weights}  (q = {sum(weights)})")
    print(f"  support  : {[str(p) for p in pos]}")
    print(f"  x        : {[str(t) for t in wt]}")
    print(f"  W        = {W} = {float(W):.8f}      (open region for bound_0 is (1/20,1/5))")
    print(f"  T        = {T} = {float(T):.8f}   T/W = {float(T/W):.6f}" if W else "  W = 0")
    print(f"  Var(g)   = {var} = {float(var):.8f}")
    print(f"  A = W-2T = {A} = {float(A):.8f}   {'FAILS (>1/25)' if A > TARGET else 'closes (<=1/25)'}")
    print(f"  g        : {[str(t) for t in g]}")
    print(f"  m(b)     : {[str(t) for t in mv]}")
    print(f"  min m(b) = {min(mv)} = {float(min(mv)):.8f}  "
          f"{'*** > 1/25: EVERY bound_k FAILS ***' if min(mv) > TARGET else '(<=1/25)'}")
    bs = []
    for k in range(kmax + 1):
        b = bound_k(pos, wt, k, adj)
        bs.append(b)
        if k <= 8 or k == kmax:
            print(f"  bound_{k:<2d}  = {b} = {float(b):.8f}   {'FAILS' if b > TARGET else 'closes'}")
    ab = arcbound(pos, wt, adj)
    print(f"  ARCBOUND = {ab} = {float(ab):.8f}   {'*** > 1/25: ARC ROUTE DEAD ***' if ab > TARGET else '(<=1/25, arc route intact)'}")
    if do_psi and len(pos) <= 22:
        ps = psi(pos, wt, adj)
        print(f"  psi      = {ps} = {float(ps):.8f}   "
              f"{'*** > 1/25: COUNTEREXAMPLE TO ERDOS 23 ***' if ps > TARGET else '(<=1/25, conjecture intact)'}")
    print(f"  25*A = {25*A},  25*min m = {25*min(mv)},  25*ARCBOUND = {25*ab}")
    return dict(W=W, T=T, A=A, g=g, m=mv, bk=bs, arcbound=ab)


if __name__ == '__main__':
    m = int(sys.argv[1])
    w = [int(t) for t in sys.argv[2].replace('[', '').replace(']', '').split(',')]
    assert len(w) == m, f"{len(w)} weights for m={m}"
    report(m, w)
