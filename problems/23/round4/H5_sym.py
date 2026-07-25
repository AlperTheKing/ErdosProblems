"""H5 round 4: solve the QMC SDP on C5 (rotation cuts) then D5-symmetrise the multiplier family
and print lambda_{(0,1)} in the 9-parameter reflection-invariant basis, to expose a rational guess.
"""
import itertools
import numpy as np
import cvxpy as cp
from H5_cert import build_and_solve

n = 5
out = build_and_solve('C5', 'rot')
cuts = out['cuts']
edge_of = {s: cuts[s][0] for s in range(len(cuts))}
print("cut index -> mono edge:", edge_of)

# quadratic form matrix of lambda_s :  lambda_s(z) = z^T L_s z  with L symmetric
L = []
for s in range(len(cuts)):
    Ms = np.array(out['M'][s].value)
    Cs = np.array(out['C'][s].value)
    L.append(Ms + Cs / 2.0)          # C contributes c_jk z_j z_k = 2*(c_jk/2) z_j z_k

# also keep the split so we can certify K2 membership later
Msp = [np.array(out['M'][s].value) for s in range(len(cuts))]
Csp = [np.array(out['C'][s].value) for s in range(len(cuts))]

# ---- D5 as permutations of {0..4}
def rot(k):
    return [(i + k) % 5 for i in range(5)]
def refl(k):
    return [(k - i) % 5 for i in range(5)]
D5 = [rot(k) for k in range(5)] + [refl(k) for k in range(5)]

def permmat(g):
    P = np.zeros((5, 5))
    for i in range(5):
        P[g[i], i] = 1.0
    return P

def edge_img(g, e):
    u, v = g[e[0]], g[e[1]]
    return (min(u, v), max(u, v))

idx_of_edge = {edge_of[s]: s for s in range(len(cuts))}

Lsym = [np.zeros((5, 5)) for _ in range(len(cuts))]
Msym = [np.zeros((5, 5)) for _ in range(len(cuts))]
Csym = [np.zeros((5, 5)) for _ in range(len(cuts))]
for g in D5:
    P = permmat(g)
    ginv = [0] * 5
    for i in range(5):
        ginv[g[i]] = i
    for s in range(len(cuts)):
        e = edge_of[s]                       # target edge e'
        epre = edge_img(ginv, e)             # g^{-1}(e')
        sp = idx_of_edge[epre]
        Lsym[s] += P @ L[sp] @ P.T / len(D5)
        Msym[s] += P @ Msp[sp] @ P.T / len(D5)
        Csym[s] += P @ Csp[sp] @ P.T / len(D5)

np.set_printoptions(precision=6, suppress=True, linewidth=220)
s01 = idx_of_edge[(0, 1)]
print("\nsymmetrised L for edge (0,1)  [lambda(z) = z^T L z]:")
print(Lsym[s01])
print("\nsymmetrised M (PSD part):")
print(Msym[s01])
print("eigs M:", np.linalg.eigvalsh(Msym[s01]))
print("\nsymmetrised C (nonneg off-diagonal part):")
print(Csym[s01])

# check (SUM): sum_e L_e = J/... coefficient identity sum lambda = (sum z)^2 <=> sum L = ones
print("\nsum_e L_e (should be the all-ones matrix):")
print(sum(Lsym))

# 9-parameter reflection basis (reflection sigma: 0<->1, 2<->4, 3 fixed)
Lm = Lsym[s01]
print("\n9-parameter form of lambda_{(0,1)} = c1(z0^2+z1^2)+c2(z2^2+z4^2)+c3 z3^2"
      "+c4 z0z1+c5(z0z2+z1z4)+c6(z0+z1)z3+c7(z0z4+z1z2)+c8(z2+z4)z3+c9 z2z4")
c = dict(c1=Lm[0, 0], c2=Lm[2, 2], c3=Lm[3, 3], c4=2 * Lm[0, 1], c5=2 * Lm[0, 2],
         c6=2 * Lm[0, 3], c7=2 * Lm[0, 4], c8=2 * Lm[2, 3], c9=2 * Lm[2, 4])
for k in sorted(c):
    print(f"   {k} = {c[k]:.8f}    1/x = {1/c[k] if abs(c[k])>1e-12 else float('inf'):.6f}")
print("check symmetry: L00-L11", Lm[0, 0] - Lm[1, 1], " L22-L44", Lm[2, 2] - Lm[4, 4],
      " L02-L14", Lm[0, 2] - Lm[1, 4], " L03-L13", Lm[0, 3] - Lm[1, 3],
      " L04-L12", Lm[0, 4] - Lm[1, 2], " L23-L34", Lm[2, 3] - Lm[3, 4])
print("linear constraints: 2c1+2c2+c3 =", 2 * c['c1'] + 2 * c['c2'] + c['c3'],
      "  c4+2c7+2c8 =", c['c4'] + 2 * c['c7'] + 2 * c['c8'],
      "  2c5+2c6+c9 =", 2 * c['c5'] + 2 * c['c6'] + c['c9'])
