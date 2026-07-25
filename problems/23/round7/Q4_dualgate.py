"""Q4 ROOT GATE for a DUAL certificate: independent proof that the degree-2d scheme cannot reach
c = 25 on Gamma_m.  Rebuilds the graph and the cuts from the definitions and re-derives the weak
duality inequality with its own arithmetic.

Claim verified: for every primal-feasible (c, nu, Q) of the scheme,

  sum_alpha muT(alpha) z_alpha
      = sum_{S,m} nu_{S,m} zhat_S(m) + sum_b <Z_b, Q_b>      [the coefficient identity, paired
                                                              with z]
     >= sum_m (sum_S nu_{S,m}) * min_S zhat_S(m)              [nu >= 0]
      = c * sum_m muD(m) * min_S zhat_S(m)                    [the normalisation]

with <Z_b, Q_b> >= 0 because both are PSD.  So c <= num/den whenever den > 0.
"""
import sys, pickle
from fractions import Fraction as F
from math import factorial
from itertools import combinations


def monomials(n, deg):
    out = []

    def rec(i, rem, cur):
        if i == n - 1:
            out.append(tuple(cur + [rem]))
            return
        for v in range(rem + 1):
            rec(i + 1, rem - v, cur + [v])
    rec(0, deg, [])
    return out


def multinom(a):
    r = factorial(sum(a))
    for t in a:
        r //= factorial(t)
    return r


def ldl_psd(M):
    k = len(M)
    A = [[F(M[i][j]) for j in range(k)] for i in range(k)]
    for step in range(k):
        p = max(range(step, k), key=lambda i: A[i][i])
        if A[p][p] < 0:
            return False
        if A[p][p] == 0:
            return all(A[i][j] == 0 for i in range(step, k) for j in range(step, k))
        A[step], A[p] = A[p], A[step]
        for r in range(k):
            A[r][step], A[r][p] = A[r][p], A[r][step]
        d = A[step][step]
        for i in range(step + 1, k):
            f = A[i][step] / d
            if f:
                for j in range(step, k):
                    A[i][j] -= f * A[step][j]
    return True


C = pickle.load(open(sys.argv[1] if len(sys.argv) > 1 else "Q4_dualcert_g11_d1.pkl", "rb"))
m, d, z = C['m'], C['d'], C['z']
n = m
E = [(i, j) for i in range(n) for j in range(i + 1, n) if 3 * min(j - i, n - (j - i)) > n]
adj = [[False] * n for _ in range(n)]
for u, v in E:
    adj[u][v] = adj[v][u] = True
assert not any(adj[u][v] and adj[v][w] and adj[u][w] for u, v, w in combinations(range(n), 3))
print(f"DUAL GATE on Gamma_{m}: {len(E)} edges, triangle-free, multiplier degree {2*d}")

monsD, monsT = monomials(n, 2 * d), monomials(n, 2 * d + 2)
# 1. PSD of every parity block (this also forces z >= 0, since z_alpha is a diagonal entry)
groups = {}
for b in monsT:
    groups.setdefault(tuple(x % 2 for x in b), []).append(b)
for p, B in groups.items():
    k = len(B)
    M = [[z[tuple((B[i][t] + B[j][t]) // 2 for t in range(n))] for j in range(k)] for i in range(k)]
    assert ldl_psd(M), f"moment block {p} is not PSD"
print(f"  all {len(groups)} moment blocks PSD (max size {max(len(B) for B in groups.values())})")
assert all(v >= 0 for v in z.values())

# 2. den = sum_m muD(m) * min over ALL cuts of zhat_S(m)   (all 2^(n-1) cuts, not a subfamily)
num = sum(F(multinom(a)) * z[a] for a in monsT)
den = F(0)
for mm in monsD:
    best = None
    for mask in range(1 << (n - 1)):
        side = [0 if v == 0 else (mask >> (v - 1)) & 1 for v in range(n)]
        s = F(0)
        for u, v in E:
            if side[u] == side[v]:
                a = list(mm)
                a[u] += 1
                a[v] += 1
                s += z[tuple(a)]
        if best is None or s < best:
            best = s
    den += F(multinom(mm)) * best
r = num / den
print(f"  num = {num}")
print(f"  den = {den}  (> 0: {den > 0})")
print(f"DUAL GATE PASSED: every degree-{2*d} certificate for Gamma_{m} has c <= {r} = {float(r):.9f}"
      f"  -> {'CANNOT reach 25' if r < 25 else 'no obstruction'}")
