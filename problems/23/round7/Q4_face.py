"""Q4: DECISIVE test -- is the degree-2d scheme exactly feasible at c = 25, or only approached?

Every exactly-feasible certificate at c = 25 must satisfy (both proved in Q4.md):
  (F1) nu_{S,m} = 0 whenever supp(m) is contained in supp(x) for some maximiser x in Z at which
       the cut S is not tight (q_S(x) > L(x)^2/25);
  (F2) Q_b U_b = 0, where U_b spans { v_b(x) : x in Z } (T must vanish on Z and Q_b is PSD).
Restricting to that face and maximising the margin  Q_b >= t * P_b  (P_b = orthogonal projector
onto the complement of the forced kernel) decides the question:  t* > 0 means an exact certificate
exists (and is well conditioned, so rational rounding is safe);  t* <= 0 means c = 25 is a
supremum that the scheme does not attain at this degree.
"""
import sys, pickle, time
import numpy as np
import scipy.sparse as sp
import cvxpy as cp
from fractions import Fraction as F
from Q4_graphs import graph_by_key as gamma_graph, all_cuts, nondominated_cuts
from Q4_sos import monomials, multinom, parity_blocks
from Q4_zeroset import zero_points, block_kernel


def face_data(n, E, cuts, d, Z):
    """(F1) allowed multiplier entries, (F2) exact kernel bases + numerical projectors."""
    monsD = monomials(n, 2 * d)
    allowed = np.ones((len(cuts), len(monsD)), dtype=bool)
    for x in Z:
        supp = [i for i in range(n) if x[i] != 0]
        tgt = sum(x) ** 2 / 25
        for S, (_mask, mono) in enumerate(cuts):
            if sum(x[E[k][0]] * x[E[k][1]] for k in mono) != tgt:
                for i, m in enumerate(monsD):
                    if all(m[v] == 0 for v in range(n) if v not in supp):
                        allowed[S, i] = False
    blocks = []
    for B in parity_blocks(n, 2 * d + 2):
        K = block_kernel(n, B, Z)
        k = len(B)
        if K:
            Kf = np.array([[float(v) for v in row] for row in K])
            P = np.eye(k) - Kf.T @ np.linalg.solve(Kf @ Kf.T, Kf)
        else:
            P = np.eye(k)
        blocks.append((B, K, P))
    return allowed, blocks


def build_face(n, E, cuts, d, Z, cval=25.0, margin=True):
    D, DT = 2 * d, 2 * d + 2
    monsD, monsT = monomials(n, D), monomials(n, DT)
    idxD = {m: i for i, m in enumerate(monsD)}
    idxT = {a: i for i, a in enumerate(monsT)}
    nD, nT, nC = len(monsD), len(monsT), len(cuts)
    allowed, blocks = face_data(n, E, cuts, d, Z)
    print(f"   (F1) allowed multiplier entries: {allowed.sum()} of {nC*nD}")
    print(f"   (F2) forced kernel dims: total {sum(len(K) for _B,K,_P in blocks)} "
          f"of {sum(len(B) for B,_K,_P in blocks)}")

    NU = cp.Variable((nC, nD), nonneg=True)
    t = cp.Variable()
    cons = [NU[~allowed] == 0]
    muD = np.array([multinom(m) for m in monsD], float)
    cons.append(cp.sum(NU, axis=0) == cval * muD)

    Qs, gram_terms = [], []
    for B, K, P in blocks:
        k = len(B)
        Q = cp.Variable((k, k), symmetric=True)
        Qs.append(Q)
        if K:
            Kf = np.array([[float(v) for v in row] for row in K])
            cons.append(Q @ Kf.T == 0)
        # the margin is only meaningful on blocks of size > 1: a 1x1 block is a single coefficient
        # of T that may legitimately be 0 without obstructing anything
        cons.append(Q - t * P >> 0 if k > 1 else Q >= 0)
        rows, cols, vals = [], [], []
        for i in range(k):
            for j in range(k):
                a = tuple((B[i][x] + B[j][x]) // 2 for x in range(n))
                rows.append(idxT[a]); cols.append(i * k + j); vals.append(1.0)
        M = sp.csr_matrix((vals, (rows, cols)), shape=(nT, k * k))
        gram_terms.append(M @ cp.vec(Q, order='C'))

    rows, cols, vals = [], [], []
    for S, (_mask, mono) in enumerate(cuts):
        for k_ in mono:
            u, v = E[k_]
            for a_i, alpha in enumerate(monsT):
                if alpha[u] >= 1 and alpha[v] >= 1:
                    b = list(alpha); b[u] -= 1; b[v] -= 1
                    rows.append(a_i); cols.append(S * nD + idxD[tuple(b)]); vals.append(1.0)
    A_nu = sp.csr_matrix((vals, (rows, cols)), shape=(nT, nC * nD))
    b_T = np.array([multinom(a) for a in monsT], float)
    cons.append(A_nu @ cp.vec(NU, order='C') + sum(gram_terms) == b_T)
    prob = cp.Problem(cp.Maximize(t) if margin else cp.Maximize(0), cons)
    return prob, t, NU, Qs, blocks, allowed


if __name__ == "__main__":
    m = sys.argv[1] if len(sys.argv) > 1 else 8
    d = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    cval = float(sys.argv[3]) if len(sys.argv) > 3 else 25.0
    solver = sys.argv[4] if len(sys.argv) > 4 else 'CLARABEL'
    n, E = gamma_graph(m)
    cuts = nondominated_cuts(all_cuts(n, E))
    Z = zero_points(n, E, cuts)
    print(f"Gamma_{m} d={d} c={cval}: |Z|={len(Z)} cuts={len(cuts)}", flush=True)
    t0 = time.time()
    prob, t, NU, Qs, blocks, allowed = build_face(n, E, cuts, d, Z, cval)
    print(f"   build {time.time()-t0:.1f}s", flush=True)
    t0 = time.time()
    kw = dict(eps_abs=1e-11, eps_rel=1e-11, max_iters=400000) if solver == 'SCS' else {}
    prob.solve(solver=solver, verbose=False, **kw)
    print(f"RESULT face-restricted Gamma_{m} d={d} c={cval} [{solver}]: status={prob.status} "
          f"margin t* = {t.value}  ({time.time()-t0:.1f}s)")
    if prob.status in ('optimal', 'optimal_inaccurate'):
        pickle.dump(dict(m=m, d=d, c=cval, n=n, E=E, cuts=cuts, Z=Z, t=t.value,
                         nu=np.asarray(NU.value), allowed=allowed,
                         Q=[(B, np.asarray(Q.value)) for (B, K, P), Q in zip(blocks, Qs)],
                         K=[K for _B, K, _P in blocks]),
                    open(f"Q4_face_g{m}_d{d}.pkl", "wb"))
        print(f"   saved Q4_face_g{m}_d{d}.pkl")
