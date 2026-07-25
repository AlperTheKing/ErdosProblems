"""Q4: build an EXACT rational certificate  max_x psi(Gamma_m, x) <= 1/25  at multiplier degree 2d.

Pipeline
  1. numerical solve restricted to the face forced by the maximisers Z (Q4_face);
  2. rationalise the minimal-face kernel of every Gram block (Q4_rational) -- only STEERS the search;
  3. re-solve with that kernel imposed, maximising the margin, so the solution is well conditioned;
  4. round the multipliers, repair the normalisation exactly, freeze the target T over Q;
  5. round the Gram inside the kernel-preserving cone and repair the 330/1716 coefficient identities
     exactly with rank-one probes P e_alpha (P = exact rational projector), solving the residual
     system with Q4_modsolve;
  6. verify everything from scratch with Q4_verify (own polynomial expansion + rational LDL^T).
"""
import sys, pickle, time
from fractions import Fraction as F
import numpy as np
import cvxpy as cp
from Q4_graphs import graph_by_key as gamma_graph, all_cuts, nondominated_cuts
from Q4_sos import monomials, multinom, parity_blocks
from Q4_zeroset import zero_points, block_kernel
from Q4_rational import rref_rational, check_contains
from Q4_modsolve import solve_exact
from Q4_verify import verify, exact_psd
import Q4_face as FACE


def proj_exact(U, k):
    """Exact rational orthogonal projector onto the complement of rowspace(U) (U: list of rows)."""
    if not U:
        return [[F(1) if i == j else F(0) for j in range(k)] for i in range(k)]
    r = len(U)
    G = [[sum(U[i][t] * U[j][t] for t in range(k)) for j in range(r)] for i in range(r)]
    # invert G exactly (Gauss-Jordan)
    A = [row[:] + [F(1) if i == j else F(0) for j in range(r)] for i, row in enumerate(G)]
    for c in range(r):
        p = next(i for i in range(c, r) if A[i][c] != 0)
        A[c], A[p] = A[p], A[c]
        pv = A[c][c]
        A[c] = [v / pv for v in A[c]]
        for i in range(r):
            if i != c and A[i][c] != 0:
                f = A[i][c]
                A[i] = [vi - f * vc for vi, vc in zip(A[i], A[c])]
    Ginv = [row[r:] for row in A]
    P = [[F(1) if i == j else F(0) for j in range(k)] for i in range(k)]
    for i in range(k):
        for j in range(k):
            s = F(0)
            for a in range(r):
                if U[a][i] == 0:
                    continue
                for b in range(r):
                    if U[b][j] == 0 or Ginv[a][b] == 0:
                        continue
                    s += U[a][i] * Ginv[a][b] * U[b][j]
            P[i][j] -= s
    return P


def main(m="8", d=1, den=10**6, tol=1e-8):
    n, E = gamma_graph(m)
    cuts = nondominated_cuts(all_cuts(n, E))
    Z = zero_points(n, E, cuts)
    monsD, monsT = monomials(n, 2 * d), monomials(n, 2 * d + 2)
    idxT = {a: i for i, a in enumerate(monsT)}
    print(f"Gamma_{m} d={d}: cuts={len(cuts)} |Z|={len(Z)} monsD={len(monsD)} monsT={len(monsT)}",
          flush=True)

    # ---- 1/2: face solve, then rationalise the minimal-face kernel ----------------------
    prob, t, NU, Qs, blocks, allowed = FACE.build_face(n, E, cuts, d, Z, 25.0)
    prob.solve(solver='SCS', eps_abs=1e-11, eps_rel=1e-11, max_iters=200000, verbose=False)
    print(f"   stage-1 margin {t.value:.3e} ({prob.status})", flush=True)
    Uex = []
    for (B, K, Pnum), Q in zip(blocks, Qs):
        k = len(B)
        Qv = np.asarray(Q.value)
        if k == 1:
            Uex.append(K if K else ([[F(1)]] if abs(Qv[0, 0]) < tol else []))
            continue
        ev, V = np.linalg.eigh(Qv)
        ker = V[:, ev < tol * max(1.0, ev.max())].T
        U, piv, err = rref_rational(ker) if len(ker) else ([], [], 0.0)
        assert check_contains(U, K), "rationalised kernel lost a proved evaluation vector"
        Uex.append(U)
    print(f"   stage-2 rationalised kernels: dims {[len(u) for u in Uex][:6]}... "
          f"total {sum(len(u) for u in Uex)}", flush=True)

    # ---- 3: re-solve with the full kernel imposed, maximising the margin -----------------
    import scipy.sparse as sp
    NU2 = cp.Variable((len(cuts), len(monsD)), nonneg=True)
    tt = cp.Variable()
    cons = [NU2[~allowed] == 0]
    muD = np.array([multinom(mm) for mm in monsD], float)
    cons.append(cp.sum(NU2, axis=0) == 25 * muD)
    Q2, gram_terms, Pex = [], [], []
    for (B, K, _P), U in zip(blocks, Uex):
        k = len(B)
        Pe = proj_exact(U, k)
        Pex.append(Pe)
        Pf = np.array([[float(v) for v in row] for row in Pe])
        Qb = cp.Variable((k, k), symmetric=True)
        Q2.append(Qb)
        if U:
            Uf = np.array([[float(v) for v in row] for row in U])
            cons.append(Qb @ Uf.T == 0)
        cons.append((Qb - tt * Pf >> 0) if k > 1 else (Qb >= tt * Pf))
        rows, cols, vals = [], [], []
        for i in range(k):
            for j in range(k):
                a = tuple((B[i][x] + B[j][x]) // 2 for x in range(n))
                rows.append(idxT[a]); cols.append(i * k + j); vals.append(1.0)
        gram_terms.append(sp.csr_matrix((vals, (rows, cols)), shape=(len(monsT), k * k))
                          @ cp.vec(Qb, order='C'))
    idxD = {mm: i for i, mm in enumerate(monsD)}
    rows, cols, vals = [], [], []
    for S, (_mask, mono) in enumerate(cuts):
        for kk in mono:
            u, v = E[kk]
            for a_i, alpha in enumerate(monsT):
                if alpha[u] >= 1 and alpha[v] >= 1:
                    bb = list(alpha); bb[u] -= 1; bb[v] -= 1
                    rows.append(a_i); cols.append(S * len(monsD) + idxD[tuple(bb)]); vals.append(1.0)
    A_nu = sp.csr_matrix((vals, (rows, cols)), shape=(len(monsT), len(cuts) * len(monsD)))
    b_T = np.array([multinom(a) for a in monsT], float)
    cons.append(A_nu @ cp.vec(NU2, order='C') + sum(gram_terms) == b_T)
    pr2 = cp.Problem(cp.Maximize(tt), cons)
    pr2.solve(solver='SCS', eps_abs=1e-12, eps_rel=1e-12, max_iters=400000, verbose=False)
    print(f"   stage-3 margin on the rationalised face: {tt.value:.6e} ({pr2.status})", flush=True)
    if tt.value is None or tt.value <= 0:
        print("   STOP: no strictly-feasible point on this face")
        return None
    # 3b: pin the multiplier entries that are numerically zero and re-solve with a margin on the
    # survivors, so that rounding + repair can never push a live entry negative
    eps = 1e-6
    allowed = allowed & (np.asarray(NU2.value) > eps)
    cons2 = [c for c in cons if c is not cons[0]] + [NU2[~allowed] == 0, NU2[allowed] >= tt]
    pr3 = cp.Problem(cp.Maximize(tt), cons2)
    pr3.solve(solver='SCS', eps_abs=1e-12, eps_rel=1e-12, max_iters=400000, verbose=False)
    print(f"   stage-3b margin with live multipliers bounded below: {tt.value:.6e} ({pr3.status}), "
          f"live entries {int(allowed.sum())}", flush=True)
    if tt.value is None or tt.value <= 0:
        print("   STOP: no strictly-feasible point after pinning")
        return None

    # ---- 4: round the multipliers, repair the normalisation exactly ----------------------
    nuv = np.asarray(NU2.value)
    nu = {}
    for S in range(len(cuts)):
        for i, mm in enumerate(monsD):
            if not allowed[S, i]:
                continue
            val = F(int(round(nuv[S, i] * den)), den)
            if val < 0:
                val = F(0)
            if val != 0:
                nu[(S, mm)] = val
    for i, mm in enumerate(monsD):
        tgt = F(25 * multinom(mm))
        cur = sum(nu.get((S, mm), F(0)) for S in range(len(cuts)))
        if cur == tgt:
            continue
        cand = max((S for S in range(len(cuts)) if allowed[S, i]),
                   key=lambda S: nu.get((S, mm), F(0)))
        nu[(cand, mm)] = nu.get((cand, mm), F(0)) + (tgt - cur)
        assert nu[(cand, mm)] >= 0, "normalisation repair went negative"
    print(f"   stage-4 multipliers: {len(nu)} nonzero entries, denominator {den}", flush=True)

    # ---- 5: exact target coefficients, then the Gram -------------------------------------
    tcoef = {a: F(multinom(a)) for a in monsT}
    for (S, mm), val in nu.items():
        for kk in cuts[S][1]:
            u, v = E[kk]
            a = list(mm); a[u] += 1; a[v] += 1
            tcoef[tuple(a)] -= val
    Q0, probes = [], []
    for (B, _K, _P), Pe in zip(blocks, Pex):
        k = len(B)
        Qv = np.asarray(Q2[len(Q0)].value)
        R = [[F(int(round(Qv[i, j] * den)), den) for j in range(k)] for i in range(k)]
        R = [[(R[i][j] + R[j][i]) / 2 for j in range(k)] for i in range(k)]
        PR = [[sum(Pe[i][a] * R[a][j] for a in range(k) if Pe[i][a] and R[a][j]) for j in range(k)]
              for i in range(k)]
        PRP = [[sum(PR[i][a] * Pe[a][j] for a in range(k) if PR[i][a] and Pe[a][j]) for j in range(k)]
               for i in range(k)]
        Q0.append(PRP)
    # residual
    res = {a: tcoef[a] for a in monsT}
    for (B, _K, _P), M in zip(blocks, Q0):
        k = len(B)
        for i in range(k):
            for j in range(k):
                if M[i][j]:
                    res[tuple((B[i][x] + B[j][x]) // 2 for x in range(n))] -= M[i][j]
    print(f"   stage-5 max |residual| = {max(abs(v) for v in res.values())}", flush=True)

    # probes  P (E_ij + E_ji) P  (kernel-preserving by construction); pick a well-conditioned
    # subset of exactly rank-many columns by rank-revealing QR, then repair exactly on those.
    import scipy.linalg as sla
    cand = []
    # (a) multiplier directions that preserve the normalisation exactly: e_{S,m} - e_{S0,m},
    #     restricted to entries that are strictly positive so the correction cannot go negative
    posthr = 1e-3
    for i, mm in enumerate(monsD):
        pos = [S for S in range(len(cuts)) if allowed[S, i] and nu.get((S, mm), F(0)) > posthr]
        if len(pos) < 2:
            continue
        S0 = pos[0]
        for S in pos[1:]:
            # applying nu[S] += x, nu[S0] -= x changes T's coefficients by -x*(q_S - q_S0), so the
            # column that must appear on the same side as the Gram columns is +q_S - q_S0
            vec = {}
            for kk in cuts[S][1]:
                u, v = E[kk]
                a = list(mm); a[u] += 1; a[v] += 1
                vec[tuple(a)] = vec.get(tuple(a), F(0)) + 1
            for kk in cuts[S0][1]:
                u, v = E[kk]
                a = list(mm); a[u] += 1; a[v] += 1
                vec[tuple(a)] = vec.get(tuple(a), F(0)) - 1
            vec = {k_: v for k_, v in vec.items() if v}
            if vec:
                cand.append(('nu', (S, S0, mm), None, None, None, vec))
    nnu = len(cand)
    for bi, ((B, _K, _P), Pe) in enumerate(zip(blocks, Pex)):
        k = len(Pe)
        for i in range(k):
            for j in range(i, k):
                pi = [Pe[r][i] for r in range(k)]
                pj = [Pe[r][j] for r in range(k)]
                vec = {}
                for r in range(k):
                    for s in range(k):
                        w = pi[r] * pj[s] + pj[r] * pi[s]
                        if w:
                            key = tuple((B[r][x] + B[s][x]) // 2 for x in range(n))
                            vec[key] = vec.get(key, F(0)) + w
                if vec:
                    cand.append((bi, i, j, pi, pj, vec))
    Af = np.zeros((len(monsT), len(cand)))
    for c, (_bi, _i, _j, _pi, _pj, vec) in enumerate(cand):
        for a, v in vec.items():
            Af[idxT[a], c] = float(v)
    _q, _r, pivcols = sla.qr(Af, pivoting=True, mode='economic')
    dg = np.abs(np.diag(_r))
    rank = int((dg > 1e-9 * dg[0]).sum())
    print("   stage-5 QR diagonal decay near the cut: "
          f"{np.array2string(dg[max(0,rank-3):rank+3], precision=3)}", flush=True)
    sel = list(pivcols[:min(len(cand), max(rank, int(sys.argv[4]) if len(sys.argv) > 4 else rank))])
    print(f"   stage-5 probes: {nnu} multiplier + {len(cand)-nnu} Gram candidates, "
          f"numerical rank {rank}", flush=True)
    rowsM = [[cand[c][5].get(a, F(0)) for c in sel] for a in monsT]
    rhs = [res[a] for a in monsT]
    t0 = time.time()
    sol = solve_exact(rowsM, rhs)
    print(f"   stage-5 exact repair solve: {'ok' if sol else 'FAILED'} ({time.time()-t0:.1f}s)",
          flush=True)
    if sol is None:
        return None
    maxcorr = max((abs(v) for v in sol), default=F(0))
    print(f"   stage-5 largest correction {float(maxcorr):.3e}", flush=True)
    for cval, c in zip(sol, sel):
        if cval == 0:
            continue
        if cand[c][0] == 'nu':
            S, S0, mm = cand[c][1]
            nu[(S, mm)] = nu.get((S, mm), F(0)) + cval
            nu[(S0, mm)] = nu.get((S0, mm), F(0)) - cval
            continue
        bi, i, j, pi, pj, _vec = cand[c]
        k = len(pi)
        M = Q0[bi]
        for r in range(k):
            for s in range(k):
                w = pi[r] * pj[s] + pj[r] * pi[s]
                if w:
                    M[r][s] += cval * w
    nu = {k_: v for k_, v in nu.items() if v != 0}

    # ---- 6: independent exact verification ----------------------------------------------
    Qblocks = [(B, M) for (B, _K, _P), M in zip(blocks, Q0)]
    ok, msg = verify(n, E, cuts, d, F(25), nu, Qblocks)
    print(f"   stage-6 EXACT VERIFICATION: {ok}  {msg}", flush=True)
    if ok:
        pickle.dump(dict(m=m, d=d, c=F(25), n=n, E=E, cuts=cuts, nu=nu, Q=Qblocks),
                    open(f"Q4_cert_g{m}_d{d}.pkl", "wb"))
        print(f"   saved Q4_cert_g{m}_d{d}.pkl")
    return ok


if __name__ == "__main__":
    m = sys.argv[1] if len(sys.argv) > 1 else 8
    d = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    den = int(sys.argv[3]) if len(sys.argv) > 3 else 10**6
    main(m, d, den)
