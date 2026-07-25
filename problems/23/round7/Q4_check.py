"""Q4: independent numerical audit of a solved certificate (no reuse of the builder's matrices).

Recomputes, from scratch and from the raw solution arrays:
  R1  nu >= 0 (min entry)
  R2  || sum_S nu_S - c*L^{2d} ||_inf   over coefficients
  R3  T(x) := L^{2d+2} - sum_S nu_S(x) q_S(x)  evaluated directly at random x >= 0,
      compared with  v(y)^T Q v(y)  at y = sqrt(x)      (this tests the whole Gram indexing)
  R4  min eigenvalue of every Gram block
  R5  T at the induced-C5 concentrations (must be ~0: the certificate is tight there)
"""
import sys, pickle
import numpy as np
from itertools import combinations
from Q4_sos import monomials, multinom, parity_blocks
from Q4_graphs import induced_C5s

f = sys.argv[1]
sol = pickle.load(open(f, "rb"))
n, E, cuts, d, c = sol['n'], sol['E'], sol['cuts'], sol['d'], sol['c']
nu, Qb = sol['nu'], sol['Q']
D, DT = 2 * d, 2 * d + 2
monsD, monsT = monomials(n, D), monomials(n, DT)
print(f"{f}: n={n} cuts={len(cuts)} d={d} c={c}")

print(f"R1 min nu entry = {nu.min():.3e}")

# R2
res = []
for i, m in enumerate(monsD):
    res.append(nu[:, i].sum() - c * multinom(m))
print(f"R2 ||sum_S nu_S - c L^{D}||_inf = {max(abs(np.array(res))):.3e}")

rng = np.random.default_rng(0)


def evalpoly_nuq(x):
    tot = 0.0
    for S, (_mask, mono) in enumerate(cuts):
        nuval = sum(nu[S, i] * np.prod(x ** np.array(m)) for i, m in enumerate(monsD))
        qval = sum(x[E[k][0]] * x[E[k][1]] for k in mono)
        tot += nuval * qval
    return tot


def gram_val(y):
    tot = 0.0
    for B, M in Qb:
        v = np.array([np.prod(y ** np.array(b)) for b in B])
        tot += v @ M @ v
    return tot


worst = 0.0
for _ in range(6):
    x = rng.random(n)
    T_direct = x.sum() ** DT - evalpoly_nuq(x)
    T_gram = gram_val(np.sqrt(x))
    worst = max(worst, abs(T_direct - T_gram))
    print(f"R3 x-sample: T_direct={T_direct:.12f}  v^T Q v={T_gram:.12f}  diff={T_direct-T_gram:.2e}")
print(f"R3 worst |T_direct - v^T Q v| = {worst:.3e}")

mins = []
for B, M in Qb:
    mins.append(np.linalg.eigvalsh(M).min() if len(B) > 1 else M.min())
print(f"R4 min eigenvalue over all {len(Qb)} blocks = {min(mins):.3e}")

for C in induced_C5s(n, E):
    x = np.zeros(n)
    for v in C:
        x[v] = 1.0 / 5
    print(f"R5 induced C5 {C}: T = {x.sum()**DT - evalpoly_nuq(x):.3e} "
          f"(min_S q_S = {min(sum(x[E[k][0]]*x[E[k][1]] for k in mono) for _m, mono in cuts):.8f})")
