"""audit_P4_regression — MANDATORY regression of every rule discussed in P4.md against the nine
recorded witnesses in round5/claude_witness_regression.py, plus P4's own W8/W9/W10.

Rules tested
  A                = W - 2T                     (the half-arc AVERAGE)
  bound_k          k = 0..50                    (the g^k-weighted hierarchy)
  cert7 = min(A, min_k bound_k)                 (the certificate item 7 asserts always closes)
  minm  = min_b m(b)                            (the structural floor of the hierarchy)
  half  = min over arcs of length <= 1/2        (superset of 'exactly 1/2' -> weaker rule)
  third = min over arcs of length <= 1/3        (superset of 'exactly 1/3' -> weaker rule)
  R     = min(half, third)                      (P4's surviving suggestion)
  ARCBOUND / psi                                (ground truth)
"""
import sys
import os
from fractions import Fraction as F

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "round5")))
from claude_witness_regression import WITNESSES, gamma  # noqa: E402
from audit_P4_core import (adj_matrix, normalise, W_of, T_of, A_of, g_of, m_of, bound_k,
                           arcbound, psi_bruteforce, mono, sliding_half_arcs,
                           sliding_third_arcs)  # noqa: E402

ONE25 = F(1, 25)

EXTRA = [
    ("W8  (P4)", 20, [0, 3, 4, 0, 1, 0, 0, 2, 4, 4, 0, 0, 0, 0, 4, 4, 3, 1, 0, 0]),
    ("W9  (P4)", 20, [0, 0, 5, 5, 5, 0, 0, 0, 0, 5, 5, 2, 0, 0, 0, 3, 5, 5, 0, 0]),
    ("W10 (P4)", 20, [0, 5, 5, 0, 0, 0, 0, 6, 4, 5, 0, 0, 0, 0, 5, 4, 6, 0, 0, 0]),
]


def profile(m, w, kmax=50):
    adj = adj_matrix(m)
    assert adj == gamma(m), "adjacency convention differs from the round-5 harness"
    x = normalise(w)
    W = W_of(x, adj)
    T = T_of(x, adj, m)
    A = A_of(x, adj, m)
    supp = [i for i in range(m) if x[i] != 0]
    bs = [bound_k(k, x, adj, m) for k in range(kmax + 1)]
    bs = [b for b in bs if b is not None]
    minb = min(bs) if bs else None
    minm = min(m_of(b, x, adj, m) for b in supp)
    cert7 = min([A] + bs) if bs else A
    half = min(mono(x, adj, s) for s in sliding_half_arcs(m))
    third = min(mono(x, adj, s) for s in sliding_third_arcs(m))
    ab = arcbound(x, adj, m)
    ps = psi_bruteforce(x, adj, m) if len(supp) <= 22 else None
    return dict(W=W, T=T, A=A, minb=minb, minm=minm, cert7=cert7, half=half, third=third,
                R=min(half, third), ab=ab, psi=ps)


if __name__ == "__main__":
    rows = [(n, m, w) for (n, m, w, _) in WITNESSES] + EXTRA
    print(f"{'witness':28s} {'W':>9s} {'A':>9s} {'min_k bnd':>9s} {'min_b m':>9s} "
          f"{'cert7':>9s} {'half':>9s} {'third':>9s} {'R':>9s} {'ARCBND':>9s} {'psi':>9s}")
    fail_cert = []
    fail_R = []
    for name, m, w in rows:
        p = profile(m, w)
        f = lambda v: ("--" if v is None else f"{float(v):.6f}")
        print(f"{name:28s} {f(p['W']):>9s} {f(p['A']):>9s} {f(p['minb']):>9s} {f(p['minm']):>9s} "
              f"{f(p['cert7']):>9s} {f(p['half']):>9s} {f(p['third']):>9s} {f(p['R']):>9s} "
              f"{f(p['ab']):>9s} {f(p['psi']):>9s}"
              + ("   <== cert7 > 1/25" if p['cert7'] > ONE25 else "")
              + ("   <== R > 1/25" if p['R'] > ONE25 else ""))
        if p['cert7'] > ONE25:
            fail_cert.append((name, p['cert7']))
        if p['R'] > ONE25:
            fail_R.append((name, p['R']))
        if p['psi'] is not None and p['psi'] > ONE25:
            print(f"    *** {name} VIOLATES ERDOS 23 (psi = {p['psi']}) ***")
    print()
    print(f"cert7 = min(A, min_k bound_k)  fails on: {[n for n, _ in fail_cert] or 'nothing'}")
    print(f"R = min(half-arc, third-arc)   fails on: {[n for n, _ in fail_R] or 'nothing'}")
    print("\nNOTE ON THE ROUND-5 ANNOTATIONS (checked, not assumed):")
    for name, m, w, why in WITNESSES:
        p = profile(m, w)
        print(f"  {name:26s} W={str(p['W']):>10s}={float(p['W']):.6f}  ARCBOUND={str(p['ab']):>8s}"
              f"  psi={str(p['psi']):>8s}   [{why[:60]}]")
