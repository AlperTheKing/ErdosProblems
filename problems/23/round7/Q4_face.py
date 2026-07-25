"""Q4: DECISIVE test -- is the degree-2d scheme exactly feasible at c = 25, or only approached?

Every exactly-feasible certificate at c = 25 must satisfy (both proved in Q4.md):
  (F1) nu_{S,m} = 0 whenever supp(m) is contained in supp(x) for some maximiser x in Z at which
       the cut S is not tight (q_S(x) > L(x)^2/25);
  (F2) Q_b U_b = 0, where U_b spans { v_b(x) : x in Z } (T must vanish on Z and Q_b is PSD).
Restricting to that face and maximising the margin  Q_b >= t * P_b  (P_b = projector onto the
complement of the forced kernel) decides the question:  t* > 0 means an exact certificate exists
(and is well conditioned, so rational rounding is safe);  t* <= 0 means c = 25 is a supremum that
the scheme does not attain at this degree.
"""
import sys, pickle, time
import numpy as np
import scipy.sparse as sp
import cvxpy as cp
from fractions import Fraction as F
from Q4_graphs import gamma_graph, all_cuts, nondominated_cuts
from Q4_sos import monomials, multinom, parity_blocks
from Q4_zeroset import zero_points, block_kernel


def build_face(n, E, cuts, d, Z, cval=25):
    D, DT = 2 * d, 2 * d + 2
    monsD, monsT = monomials(n, D), monomials(n, DT)
    idxT = {a: i for i, a in enumerate(monsT)}
    nD, nT, nC = len(monsD), len(monsT), len(cuts)

    # ---- (F1) allowed multiplier entries
    qS = []
    for _mask, mono in cuts:
        qS.append(mono)
    allowed = np.ones((nC, nD), dtype=bool)
    Lsq = lambda x: sum(x) ** 2
    for x in Z:
        supp = [i for i in range(n) if x[i] != 0]
        tgt = Lsq(x) / 25
        for S, mono in enumerate(qS):
            val = sum(x[E[k][0]] * x[E[k][1]] for k in mono)
            if val != tgt:
                for i, m in enumerate(monsD):
                    if all(m[v] == 0 for v in range(n) if v not in supp):
                        allowed[S, i] = False
    print(f"   (F1) allowed multiplier entries: {allowed.sum()} of {nC*nD}")

    # ---- (F2) forced kernels, numerical complement bases
    blocks = []
    for B in parity_blocks(n, DT):
        K = block_kernel(n, B, Z)                      # exact rational rows
        k = len(B)
        if K:
            Kf = np.array([[float(v) for v in row] for row in K])
            # orthonormal complement
            U, s, Vt = np.linalg.svd(Kf, full_matrices=True)
            W = Vt[len(K):].T                           # k x (k - dim K)
        else:
            W = np.eye(k)
        blocks.append((B, K, W))
    dims = [W.shape[1] for _, _, W in blocks]
    print(f"   (F2) face dimensions: total {sum(dims)} of {sum(len(B) for B,_,_ in blocks)}; "
          f"biggest block {max(dims)}")

    NU = cp.Variable((nC, nD), nonneg=True)
    t = cp.Variable()
    cons = [NU[~allowed] == 0]
    muD = np.array([multinom(m) for m in monsD], float)
    cons.append(cp.sum(NU, axis=0) == cval * muD)

    Rs, gram_terms = [], []
    for B, K, W in blocks:
        k, r = len(B), W.shape[1]
        if r == 0:
            Rs.append(None)
            continue
        R = cp.Variable((r, r), symmetric=True)
        Rs.append(R)
        cons.append(R - t * np.eye(r) >> 0 if r > 1 else R >= t)
        Qb = W @ R @ W.T
        rows, cols, vals = [], [], []
        for i in range(k):
            for j in range(k):
                a = tuple((B[i][x] + B[j][x]) // 2 for x in range(n))
                rows.append(idxT[a]); cols.append(i * k + j); vals.append(1.0)
        M = sp.csr_matrix((vals, (rows, cols)), shape=(nT, k * k))
        gram_terms.append(M @ cp.vec(Qb, order='C'))

    idxD = {mm: i for i, mm in enumerate(monsD)}
    rows, cols, vals = [], [], []
    for S, mono in enumerate(qS):
        for k_ in mono:
            u, v = E[k_]
            for a_i, alpha in enumerate(monsT):
                if alpha[u] >= 1 and alpha[v] >= 1:
                    b = list(alpha); b[u] -= 1; b[v] -= 1
                    rows.append(a_i); cols.append(S * nD + idxD[tuple(b)]); vals.append(1.0)
    A_nu = sp.csr_matrix((vals, (rows, cols)), shape=(nT, nC * nD))
    b_T = np.array([multinom(a) for a in monsT], float)
    cons.append(A_nu @ cp.vec(NU, order='C') + sum(gram_terms) == b_T)
    prob = cp.Problem(cp.Maximize(t), cons)
    return prob, t, NU, Rs, blocks, allowed


if __name__ == "__main__":
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    d = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    cval = F(sys.argv[3]) if len(sys.argv) > 3 else F(25)
    n, E = gamma_graph(m)
    cuts = nondominated_cuts(all_cuts(n, E))
    Z = zero_points(n, E, cuts)
    print(f"Gamma_{m} d={d} c={cval}: |Z|={len(Z)} cuts={len(cuts)}")
    t0 = time.time()
    prob, t, NU, Rs, blocks, allowed = build_face(n, E, cuts, d, Z, float(cval))
    print(f"   build {time.time()-t0:.1f}s", flush=True)
    prob.solve(solver='CLARABEL', verbose=False)
    print(f"RESULT face-restricted Gamma_{m} d={d} c={cval}: status={prob.status} margin t* = {t.value}")
    if prob.status in ('optimal', 'optimal_inaccurate'):
        pickle.dump(dict(m=m, d=d, c=float(cval), n=n, E=E, cuts=cuts, Z=Z, t=t.value,
                         nu=np.asarray(NU.value), allowed=allowed,
                         R=[None if R is None else np.asarray(R.value) for R in Rs],
                         blocks=[(B, K, W) for B, K, W in blocks]),
                    open(f"Q4_face_g{m}_d{d}.pkl", "wb"))
        print(f"   saved Q4_face_g{m}_d{d}.pkl")
