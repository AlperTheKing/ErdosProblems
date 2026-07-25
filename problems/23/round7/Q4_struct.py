"""Q4: structure of the numerical certificate -- Gram ranks, predicted kernel vectors, nu support.

Predicted kernel (proved): T vanishes at every induced-C5 concentration x* = 1_C/5, hence for each
parity block b and each induced C5 C with supp(parity) subset C, the 0/1 vector
u_{C,b} = indicator{ beta in b : supp(beta) subset C } lies in ker(Q_b).
"""
import sys, pickle
import numpy as np
from Q4_sos import monomials
from Q4_graphs import induced_C5s

sol = pickle.load(open(sys.argv[1], "rb"))
n, E, cuts, d, c = sol['n'], sol['E'], sol['cuts'], sol['d'], sol['c']
nu, Qb = sol['nu'], sol['Q']
C5s = induced_C5s(n, E)
print(f"n={n} d={d} c={c}  induced C5s: {len(C5s)}")

tot_pred, tot_ker = 0, 0
for bi, (B, M) in enumerate(Qb):
    k = len(B)
    par = tuple(x % 2 for x in B[0])
    ev = np.linalg.eigvalsh(M) if k > 1 else np.array([M[0, 0]])
    nker = int((ev < 1e-7 * max(1.0, ev.max())).sum())
    U = []
    for C in C5s:
        if all(par[i] == 0 for i in range(n) if i not in C):
            U.append(np.array([1.0 if all(b[i] == 0 for i in range(n) if i not in C) else 0.0 for b in B]))
    rk = np.linalg.matrix_rank(np.array(U)) if U else 0
    tot_pred += rk
    tot_ker += nker
    if k > 1 and (nker or rk):
        res = max((np.linalg.norm(M @ u) / max(np.linalg.norm(u), 1e-12) for u in U), default=0.0)
        print(f"  block {bi} size {k} parity {par}: numerical kernel dim {nker}, "
              f"predicted {rk}, max |M u|/|u| = {res:.2e}, eig[0:3]={ev[:3]}")
print(f"TOTAL numerical kernel {tot_ker}, predicted {tot_pred}")

# nu support versus the complementarity pattern
monsD = monomials(n, 2 * d)
bad = 0
print("\nforced-zero pattern check (nu_{S,m} must vanish when supp(m) subset C and S is not a max cut on C):")
worst = 0.0
for S, (_mask, mono) in enumerate(cuts):
    for C in C5s:
        qc = sum(1 for k_ in mono if E[k_][0] in C and E[k_][1] in C)
        if qc >= 2:
            for i, m in enumerate(monsD):
                if all(m[v] == 0 for v in range(n) if v not in C):
                    worst = max(worst, nu[S, i])
                    bad += nu[S, i] > 1e-6
print(f"  max nu on a forced-zero entry = {worst:.3e}  (entries > 1e-6: {bad})")
