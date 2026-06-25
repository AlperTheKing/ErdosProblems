#!/usr/bin/env python3
"""
Separation oracle / cutting-plane loop for the switching flag-SDP (Phase C refinement).
Precompute, per colored type sigma and per state H, the class-pair tensor
   M_H[c,d] = sum over ordered roots R inducing sigma, over edges uv (u,v non-root) with
              {class(u),class(v)}={c,d}, of chi(uv)  [chi=+1 mono, -1 cut],
where class(w) = (color(w), adjacency-bits of w to R).  For a switch p in [0,1]^classes the
limit functional is  g_p(H) = sum_{c<=d} M_H[c,d] * w_{cd}(p),  w_{cd}=p_c+p_d-2p_cp_d (c<d),
w_{cc}=2p_c-2p_c^2;  the valid constraint is sum_H x_H g_p(H) <= 0.
ORACLE: given primal optimum x*, Ubar[c,d]=sum_H x*_H M_H[c,d]; maximize violation
   V(p)=sum_{c<=d} Ubar[c,d] w_{cd}(p) over a p-grid; add the most-violated switch; re-solve.
"""
import itertools, time
import numpy as np
import cvxpy as cp
import flag_engine_col as fc
import flag_sdp_col as fs


def precompute_M(states, sigma):
    k, Asig, colsig = sigma
    classes = [(c,) + ab for c in (0, 1) for ab in itertools.product((0, 1), repeat=k)]
    cidx = {cl: i for i, cl in enumerate(classes)}
    m = len(classes)
    Ms = []
    for (n, A, col) in states:
        M = np.zeros((m, m))
        for R in itertools.permutations(range(n), k):
            ok = all(col[R[a]] == colsig[a] for a in range(k))
            if ok:
                for a in range(k):
                    for b in range(a+1, k):
                        if ((A[R[a]] >> R[b]) & 1) != ((Asig[a] >> b) & 1): ok = False; break
                    if not ok: break
            if not ok: continue
            Rset = set(R)
            cls = {}
            for w in range(n):
                if w in Rset: continue
                cls[w] = cidx[(col[w],) + tuple((A[w] >> r) & 1 for r in R)]
            for u in range(n):
                if u in Rset: continue
                Au = A[u]
                for v in range(u+1, n):
                    if v in Rset or not ((Au >> v) & 1): continue
                    chi = 1 if col[u] == col[v] else -1
                    cu, cv = cls[u], cls[v]
                    a, b = (cu, cv) if cu <= cv else (cv, cu)
                    M[a, b] += chi
        Ms.append(M)
    # prune classes that are zero in every M (never edge-incident) to reduce oracle dimension
    total = sum(np.abs(M) for M in Ms)
    keep = [i for i in range(m) if (total[i, :].sum() + total[:, i].sum()) > 1e-9]
    if len(keep) < m:
        classes = [classes[i] for i in keep]
        Ms = [M[np.ix_(keep, keep)] for M in Ms]
    return classes, Ms


def _wmat(p):
    m = len(p)
    W = np.zeros((m, m))
    for c in range(m):
        for d in range(c, m):
            W[c, d] = (2*p[c]-2*p[c]*p[c]) if c == d else (p[c]+p[d]-2*p[c]*p[d])
    return W

def g_of_p(Ms, p):
    W = _wmat(p)
    return np.array([np.sum(M*W) for M in Ms])

def _Vval(Ubar, p):
    return float(np.sum(Ubar * _wmat(p)))

def _coord_ascent(Ubar, p0, iters=30):
    m = Ubar.shape[0]
    p = p0.copy()
    Us = Ubar + Ubar.T - np.diag(np.diag(Ubar))  # symmetric helper: Us[c,d]=Ub(c,d) for c!=d
    for _ in range(iters):
        changed = False
        for c in range(m):
            # V as quadratic in p_c: a*p_c^2 + b*p_c + const
            a = -2.0*Ubar[c, c]
            b = 2.0*Ubar[c, c] + sum(Us[c, d]*(1-2*p[d]) for d in range(m) if d != c)
            cands = [0.0, 1.0]
            if a < -1e-12:
                cands.append(min(1.0, max(0.0, -b/(2*a))))
            best_pc = max(cands, key=lambda z: a*z*z + b*z)
            if abs(best_pc - p[c]) > 1e-9:
                p[c] = best_pc; changed = True
        if not changed:
            break
    return _Vval(Ubar, p), p

def _best_binary(Ubar):
    """EXACT max over binary p in {0,1}^m of V(p) = sum_{c<d} Ub(c,d)*[exactly one of c,d in S].
    (diagonal w=0 for binary). Returns (val, p). For binary this is a weighted Max-Cut on the
    symmetric pair matrix; enumerate all 2^m subsets (m<=16) with incremental Gray-code updates."""
    m = Ubar.shape[0]
    sym = np.triu(Ubar, 1)              # off-diagonal pair weights (c<d)
    sym = sym + sym.T                   # symmetric
    rowsum = sym.sum(axis=1)            # rowsum[c] = sum_d sym[c,d]
    # V(S) = sum_{c in S} (rowsum[c] - 2*sum_{d in S} sym[c,d]) / 1 ... cut value:
    # cut(S) = sum_{c in S, d notin S} sym[c,d] = (1_S . rowsum) - sum_{c,d in S} sym[c,d]
    best = (0.0, np.zeros(m))
    # Gray-code enumeration: incremental cut update when toggling vertex k.
    inS = np.zeros(m, dtype=bool)
    cur = 0.0
    # delta to add vertex k (not in S): edges to (notin S) become cut, edges to (in S) leave
    # cut(S+k) - cut(S) = sum_{d notin S, d!=k} sym[k,d] - sum_{d in S} sym[k,d]
    order = []
    g = 0
    for i in range(1, 1 << m):
        k = (i & -i).bit_length() - 1     # bit that changes in Gray code step
        # gray code: toggle bit k
        if not inS[k]:
            # adding k
            cur += rowsum[k] - 2.0*sym[k, inS].sum()
            inS[k] = True
        else:
            inS[k] = False
            cur -= rowsum[k] - 2.0*sym[k, inS].sum()
        if cur > best[0]:
            best = (cur, inS.astype(float).copy())
    return best

def best_switch(Ubar, pgrid, grid_max_dim=9, binary_max_dim=16):
    m = Ubar.shape[0]
    best = (0.0, None)
    # EXACT binary separation (catches binary switches like the bad-Clebsch-cut switch)
    if m <= binary_max_dim:
        vb, pb = _best_binary(Ubar)
        if vb > best[0]:
            best = (vb, pb)
    # fractional refinement: full grid for small m, coordinate-ascent restarts for large m
    if m <= grid_max_dim:
        for p in itertools.product(pgrid, repeat=m):
            v = np.sum(Ubar * _wmat(np.array(p)))
            if v > best[0]:
                best = (v, np.array(p))
    else:
        starts = [np.full(m, 0.5)]
        rng = np.random.default_rng(0)
        for _ in range(8):
            starts.append(rng.choice(np.array(pgrid), size=m))
        if best[1] is not None:
            starts.append(best[1].copy())   # refine the binary optimum fractionally
        for p0 in starts:
            v, p = _coord_ascent(Ubar, np.asarray(p0, float))
            if v > best[0]:
                best = (v, p)
    return best


def separation_loop(N, kmax_types=2, oracle_kmax=2, band=(0.2486, 0.32),
                    pgrid=(0.0, 0.5, 1.0), max_iters=60, tol=1e-5, solver=cp.CLARABEL):
    t0 = time.time()
    states = fc.enumerate_colored(N, triangle_free=True)
    tf = fs.colored_types(N, kmax=kmax_types)
    ns = len(states)
    print(f"  N={N}: states={ns} types={len(tf)}  (build {time.time()-t0:.1f}s)")
    # precompute moment matrices for PSD blocks
    Pmats = []   # store flattened (t*t, ns) for vectorized moment-matrix build
    for (sigma, flags) in tf:
        mats = fs.P_sigma_col(states, sigma, flags); t = len(flags)
        if t >= 2:
            Pmats.append((np.stack([m.ravel() for m in mats], axis=1), t))
    # precompute switch tensors for oracle types (k=0..oracle_kmax)
    oracle_types = []
    for k in range(0, oracle_kmax+1):
        for (kk, A, col) in fc.enumerate_colored(k, triangle_free=True):
            sigma = (k, A, tuple(col))
            classes, Ms = precompute_M(states, sigma)
            oracle_types.append((sigma, classes, Ms))
    dmono = fs.d_mono_vec(states); dedge = fs.d_edge_vec(states)
    print(f"  precompute done ({time.time()-t0:.1f}s); oracle types={len(oracle_types)}")

    cuts = []   # list of g-vectors, each constraint g@x <= 0
    def solve():
        x = cp.Variable(ns, nonneg=True)
        cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1]]
        for (Pflat, t) in Pmats:
            M = cp.reshape(Pflat @ x, (t, t), order='C')
            cons.append(0.5*(M + M.T) >> 0)
        for g in cuts:
            cons.append(g @ x <= 0)
        prob = cp.Problem(cp.Maximize(dmono @ x), cons)
        val = prob.solve(solver=solver)
        return val, prob.status, np.array(x.value)

    bound = None
    for it in range(max_iters):
        val, status, xstar = solve()
        if xstar is None:
            print(f"  iter {it}: solve failed ({status})"); break
        # oracle: find most violated switch across all oracle types
        bestv, bestg, bestinfo = tol, None, None
        for (sigma, classes, Ms) in oracle_types:
            Ubar = sum(xstar[h]*Ms[h] for h in range(ns))
            v, p = best_switch(Ubar, pgrid)
            if v > bestv:
                bestv = v; bestg = g_of_p(Ms, p); bestinfo = (sigma[0], p)
        print(f"  iter {it:2d}: d_mono={val:.6f} (beta/N^2<= {val/2:.5f}) cuts={len(cuts)} "
              f"max_viol={bestv:.5f} {status}")
        bound = val
        if bestg is None:
            print("  no violated switch -> converged"); break
        cuts.append(bestg)
    print(f"  FINAL N={N}: d_mono <= {bound:.6f}  beta/N^2 <= {bound/2:.6f}  (target 0.04)  [{time.time()-t0:.1f}s]")
    return bound


if __name__ == "__main__":
    import sys
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    okmax = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    separation_loop(N, kmax_types=2, oracle_kmax=okmax)
    print("DONE")
