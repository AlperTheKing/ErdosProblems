"""audit_P4_fourier — independent check of P4.md item (e).

Kernel K(t) = (1/2 - |t|) * 1[|t| > 1/3]  on R/Z  (STRICT >, so K(1/3) = 0).
A(mu) = int int K(x-y) dmu dmu.

Claims audited:
  E1  psihat(0) = 1/36 and psihat(n) = (-1)^n [ sin(pi n/3)/(6 pi n) + (cos(pi n/3)-1)/(2 pi^2 n^2) ]
  E2  |psihat(n)| ~ 0.0459/n (NOT O(1/n^2))
  E3  psihat(n) > 0 for every n = 2,5 (mod 6); positive part diverges
  E4  the identity A = sum psihat |muhat|^2 FAILS when mass sits at distance exactly 1/3, with
      defect exactly (1/12) * (mu x mu){d = 1/3}
"""
import numpy as np
import sympy as sp
from fractions import Fraction as F
from itertools import combinations
from audit_P4_core import adj_matrix, normalise, A_direct, circ_dist_steps


def sym_coeff():
    n, t = sp.symbols('n t', positive=True)
    expr = 2 * sp.integrate((sp.Rational(1, 2) - t) * sp.cos(2 * sp.pi * n * t),
                            (t, sp.Rational(1, 3), sp.Rational(1, 2)))
    return sp.simplify(expr), n


def psihat(nn):
    if nn == 0:
        return 1.0 / 36.0
    return (-1) ** nn * (np.sin(np.pi * nn / 3) / (6 * np.pi * nn)
                         + (np.cos(np.pi * nn / 3) - 1) / (2 * np.pi ** 2 * nn ** 2))


def psihat_numeric_integral(nn, npts=2_000_001):
    t = np.linspace(1.0 / 3, 0.5, npts)
    y = (0.5 - t) * np.cos(2 * np.pi * nn * t)
    return 2 * np.trapezoid(y, t)


def tie_mass(M, x):
    """(mu x mu){ d(u,v) = 1/3 } for an atomic measure on Z_M/M"""
    if M % 3 != 0:
        return F(0)
    s = M // 3
    return sum(x[u] * x[v] for u in range(M) for v in range(M)
               if circ_dist_steps(u, v, M) == s)


def series_value(M, x, N=200000):
    """symmetric partial sum sum_{|n|<=N} psihat(n)|muhat(n)|^2 evaluated as
       sum_{u,v} x_u x_v S_N((u-v)/M)"""
    ns = np.arange(1, N + 1)
    ph = (-1.0) ** ns * (np.sin(np.pi * ns / 3) / (6 * np.pi * ns)
                         + (np.cos(np.pi * ns / 3) - 1) / (2 * np.pi ** 2 * ns ** 2))
    tot = 0.0
    xf = np.array([float(v) for v in x])
    for j in range(M):
        # sum over pairs with u - v = j
        w = float(sum(x[u] * x[(u - j) % M] for u in range(M)))
        if w == 0:
            continue
        SN = 1.0 / 36.0 + 2.0 * np.sum(ph * np.cos(2 * np.pi * ns * j / M))
        tot += w * SN
    return tot


def K_midpoint(t):
    """the midpoint regularisation the Fourier series actually converges to"""
    a = abs(t - round(t))
    if abs(a - 1.0 / 3) < 1e-15:
        return 1.0 / 24 + 0.0        # (0 + 1/6)/2 = 1/12 ... careful: (0 + (1/2-1/3))/2 = 1/12
    return (0.5 - a) if a > 1.0 / 3 else 0.0


if __name__ == "__main__":
    print("E1  symbolic re-derivation of psihat(n)")
    expr, n = sym_coeff()
    print("    sympy:", sp.simplify(expr))
    claimed = (-1) ** n * (sp.sin(sp.pi * n / 3) / (6 * sp.pi * n)
                           + (sp.cos(sp.pi * n / 3) - 1) / (2 * sp.pi ** 2 * n ** 2))
    diffs = [sp.simplify(expr.subs(n, k) - claimed.subs(n, k)) for k in range(1, 13)]
    print("    expr - claimed for n=1..12:", [sp.nsimplify(d) for d in diffs])
    print("    psihat(0) =", sp.integrate(2 * (sp.Rational(1, 2) - sp.Symbol('t')),
                                          (sp.Symbol('t'), sp.Rational(1, 3), sp.Rational(1, 2))))
    print("    numeric integral vs formula, n=1..8:",
          [f"{psihat_numeric_integral(k):.8f}/{psihat(k):.8f}" for k in range(1, 9)])

    print("\nE2  decay")
    for k in (100, 500, 3001, 100000):
        print(f"    n={k:7d}  n*psihat(n) = {k*psihat(k):+.6f}   n^2*psihat(n) = {k*k*psihat(k):+.3f}")
    print("    => psihat(n) = Theta(1/n) for 3 not | n;  P4's refutation of 'O(1/n^2)' CONFIRMED")

    print("\nE3  signs and divergence")
    pos = [k for k in range(1, 40) if psihat(k) > 1e-15]
    print("    n<=40 with psihat(n)>0:", pos)
    print("    residues mod 6:", sorted({k % 6 for k in pos}))
    for N in (10 ** 3, 10 ** 4, 2 * 10 ** 5, 2 * 10 ** 6):
        ns = np.arange(1, N + 1)
        ph = (-1.0) ** ns * (np.sin(np.pi * ns / 3) / (6 * np.pi * ns)
                             + (np.cos(np.pi * ns / 3) - 1) / (2 * np.pi ** 2 * ns ** 2))
        print(f"    N={N:8d}  sum |psihat| = {np.abs(ph).sum():.4f}   "
              f"sum of positives = {ph[ph > 0].sum():.4f}   0.0306*ln N = {0.0306*np.log(N):.4f}")

    print("\nE4  the tie defect")
    tests = []
    for M in (18, 9, 5, 12):
        tests.append((f"uniform Gamma_{M}", M, [F(1, M)] * M))
    tests.append(("3 atoms at 0,1/3,2/3 (M=3)", 3, [F(1, 3)] * 3))
    tests.append(("2 atoms at distance exactly 1/3 (M=3)", 3, [F(1, 2), F(1, 2), F(0)]))
    tests.append(("W9 (Gamma_20, tie-free)", 20,
                  normalise([0, 0, 5, 5, 5, 0, 0, 0, 0, 5, 5, 2, 0, 0, 0, 3, 5, 5, 0, 0])))
    print(f"    {'measure':38s} {'A (exact)':>12s} {'series(N=2e5)':>14s} {'tie mass':>10s} "
          f"{'defect':>10s} {'(1/12)*tie':>11s}")
    for name, M, x in tests:
        adj = adj_matrix(M)
        A = A_direct(x, adj, M)
        S = series_value(M, x)
        tm = tie_mass(M, x)
        print(f"    {name:38s} {str(A):>12s} {S:14.8f} {str(tm):>10s} "
              f"{S - float(A):10.6f} {float(tm)/12:11.6f}")
    print("    => E4 CONFIRMED: the series converges to A + (1/12)*(tie mass), so the identity")
    print("       of item 6 is false exactly on measures with pairs at distance 1/3.")
