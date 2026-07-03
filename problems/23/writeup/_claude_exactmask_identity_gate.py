"""ExactMask repair (B1) — identity + assembly gate.

Checks, fully symbolically (sympy, exact rationals):
 1. CLEARING: X(A) <= (1+25/N)*eta, cleared by 75N, equals
    D_A^1 := (75+3N)(N^2-25m) - 75N*sum_J |A cap J| y_J + 375|A|m >= 0,
    under the row-atom expansion s_i = sum_{J ni i} y_J and tau = 5m/N,
    eta = (N^2-25m)/25.  (GPT-Pro repair reply 2026-07-03.)
 2. EMPTY MASK: A = empty gives D_empty^1 = (75+3N)(N^2-25m); nonneg of this
    <=> eta >= 0 (coefficient 75+3N > 0) — the eta-provenance instance.
 3. ASSEMBLY: sum_i (s_i - tau)_+ = X(P) for P = {i : s_i > tau} — trivially
    max(0, s_i-tau) = s_i-tau on P and 0 off P (checked on random exact data).
 4. OLD vs NEW coefficient: old A1 used (75+2N) = clearing of the 2/3-comparison
    X(A) <= (2/3)*(...)  — confirm (75+3N) is the EXACT final coefficient, i.e.
    75N*(1+25/N)/25 = 3N+75.
"""

from fractions import Fraction as F
from itertools import combinations
import random

import sympy as sp

N, m = sp.symbols("N m", positive=True)
# row atoms indexed by nonempty subsets J of Z5
Z5 = (0, 1, 2, 3, 4)
Js = [frozenset(c) for k in range(1, 6) for c in combinations(Z5, k)]
y = {J: sp.Symbol(f"y_{''.join(map(str, sorted(J)))}", nonnegative=True) for J in Js}

s = {i: sum(y[J] for J in Js if i in J) for i in Z5}
tau = 5 * m / N
eta = (N**2 - 25 * m) / 25

ok = True
for size in range(0, 6):
    for A in combinations(Z5, size):
        Aset = frozenset(A)
        X_A = sum(s[i] - tau for i in A)
        lhs_cleared = sp.expand(75 * N * ((1 + sp.Rational(25) / N) * eta - X_A))
        D_A1 = sp.expand(
            (75 + 3 * N) * (N**2 - 25 * m)
            - 75 * N * sum(len(Aset & J) * y[J] for J in Js)
            + 375 * len(Aset) * m
        )
        if sp.simplify(lhs_cleared - D_A1) != 0:
            print(f"FAIL clearing mask {A}: diff = {sp.simplify(lhs_cleared - D_A1)}")
            ok = False

# 2. empty mask
D_empty = sp.expand(75 * N * ((1 + sp.Rational(25) / N) * eta))
assert sp.simplify(D_empty - (75 + 3 * N) * (N**2 - 25 * m)) == 0, "empty-mask form"
print("empty-mask instance = (75+3N)(N^2-25m): OK  (nonneg <=> eta>=0, coeff>0)")

# 4. exact coefficient
assert sp.simplify(75 * N * (1 + sp.Rational(25) / N) / 25 - (3 * N + 75)) == 0
print("exact final coefficient 75N(1+25/N)/25 = 3N+75: OK")

# 3. assembly on random exact data
rng = random.Random(23)
for trial in range(2000):
    n_val = rng.randint(6, 60)
    m_val = rng.randint(1, (n_val * n_val) // 25 + 8)  # allow eta<0 shapes too
    tau_v = F(5 * m_val, n_val)
    s_v = [F(rng.randint(0, 3 * n_val), rng.randint(1, 4)) for _ in range(5)]
    P = tuple(i for i in Z5 if s_v[i] > tau_v)
    lhs = sum(max(F(0), sv - tau_v) for sv in s_v)
    X_P = sum(s_v[i] - tau_v for i in P)
    assert lhs == X_P, (trial, s_v, tau_v)
print("assembly sum(s_i-tau)_+ = X(P) on 2000 exact random rows: OK")

print("ALL PASS" if ok else "FAILURES PRESENT")
