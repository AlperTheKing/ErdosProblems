#!/usr/bin/env python3
"""
Phase F/G: margin-color SDP (GPT Q16 plateau-break).
4 colors: 0=A_L,1=A_H,2=B_L,3=B_H; side(c)=c//2, mark(c)=c%2; mono edge = same side (-> beta).
Primal: max d_mono s.t. M^sigma(x) PSD (4-colored types), edge-band, margin consistency LOCALIZERS,
margin-conditioned SWITCH. Target d_mono <= 2/25 = 0.08 (current plateau 0.10 = 1/20; bad-cut 3/32=0.09375).
"""
import itertools, time
import numpy as np
import cvxpy as cp
import flag_engine as fe
import flag_engine_col as fc
import flag_engine_kcol as kc
import flag_sdp_col as fs

NCOL = 4
def side(c): return c // 2
def mark(c): return c % 2

def enumerate_flags_kcol(sigma, m, triangle_free=True):
    k, Asig, colsig = sigma
    slots = [(i, j) for i in range(k) for j in range(k, m)] + \
            [(i, j) for i in range(k, m) for j in range(i+1, m)]
    seen = {}
    for cfree in itertools.product(range(NCOL), repeat=(m-k)):
        col = list(colsig) + list(cfree)
        for bits in itertools.product((0, 1), repeat=len(slots)):
            A = [0]*m
            for i in range(k):
                for j in range(i+1, k):
                    if (Asig[i] >> j) & 1: A[i] |= 1 << j; A[j] |= 1 << i
            for (slot, b) in zip(slots, bits):
                if b: i, j = slot; A[i] |= 1 << j; A[j] |= 1 << i
            if triangle_free and not fe.is_triangle_free(m, A): continue
            ck = fc.canonical_col(m, A, col, roots=k)
            if ck not in seen:
                seen[ck] = (m, fe.graph_from_key(m, ck[1]), list(ck[0]))
    return list(seen.values())

def kcolored_types(N, kmax=2):
    out = []
    for k in range(1, kmax+1):
        for (kk, A, col) in kc.enumerate_kcolored(k, NCOL, triangle_free=True):
            sigma = (k, A, tuple(col))
            smax = (N - k) // 2
            for s in range(1, smax+1):
                fl = enumerate_flags_kcol(sigma, k + s)
                if len(fl) >= 2:
                    out.append((sigma, fl))
    return out

def d_mono_vec(states):
    out = []
    for (n, A, col) in states:
        mono = sum(1 for (i, j) in fe.edges_of(n, A) if side(col[i]) == side(col[j]))
        out.append(2.0*mono/(n*(n-1)) if n > 1 else 0.0)
    return np.array(out)

def d_edge_vec(states):
    return np.array([2.0*fe.num_edges(n, A)/(n*(n-1)) if n > 1 else 0.0 for (n, A, col) in states])

def localizer_vecs(states, t=1.0/8):
    """For each color c: g_c(H) = (cut_c - mono_c) - t*colc  (hom densities).
    Low colors {0,2}: constraint g_c <= 0; High {1,3}: g_c >= 0 (return -g for <=0)."""
    vecs = []
    for c in range(NCOL):
        g = []
        for (n, A, col) in states:
            colc = sum(1 for v in range(n) if col[v] == c) / n
            cut_c = mono_c = 0
            for u in range(n):
                if col[u] != c: continue
                Au = A[u]
                for v in range(n):
                    if v != u and (Au >> v) & 1:
                        if side(col[v]) != side(col[u]): cut_c += 1
                        else: mono_c += 1
            val = (cut_c - mono_c)/(n*n) - t*colc
            g.append(val)
        g = np.array(g)
        vecs.append(g if mark(c) == 0 else -g)   # Low: g<=0 ; High: -g<=0
    return vecs

def margin_switch_vec(states):
    """Limit functional of GPT's low-low cut-edge switch: 2-root cut edge a in A_L(0), b in B_L(2);
    S = (N(a) cap B_L) u (N(b) cap A_L); SW = sum_edges chi(p_u+p_v-2p_up_v) <= 0."""
    g = []
    for (n, A, col) in states:
        tot = 0
        for a in range(n):
            if col[a] != 0: continue
            Aa = A[a]
            for b in range(n):
                if b == a or col[b] != 2 or not ((Aa >> b) & 1): continue
                Ab = A[b]
                p = [0]*n
                for w in range(n):
                    if w == a or w == b: continue
                    if (col[w] == 2 and (A[w] >> a) & 1) or (col[w] == 0 and (A[w] >> b) & 1):
                        p[w] = 1
                for u in range(n):
                    if u == a or u == b: continue
                    Au = A[u]
                    for v in range(u+1, n):
                        if v == a or v == b or not ((Au >> v) & 1): continue
                        w_uv = p[u] + p[v] - 2*p[u]*p[v]
                        if w_uv:
                            tot += w_uv if side(col[u]) == side(col[v]) else -w_uv
        g.append(float(tot))
    return np.array(g)

def side_sw0_vec(states, dmono, dedge):
    """0-root side switch (a=b=1/2): mono <= cut  ->  2*d_mono - d_edge <= 0."""
    return 2.0*dmono - dedge

def side_sw1_vec(states, root_side):
    """SW1 limit functional by SIDE (cut-deg/mono-deg use side(col)): e(P,R)+e(Q,T) <= e(R,T),
    rooted at a vertex v of side `root_side`. P=side-rs nbrs, Q=other-side nbrs, R=side-rs non-nbrs,
    T=other-side non-nbrs (all !=v). Returns g with constraint g@x <= 0."""
    def sside(c): return c // 2
    g = []
    for (n, A, col) in states:
        tot = 0
        for v in range(n):
            if sside(col[v]) != root_side: continue
            nb = [(A[v] >> u) & 1 for u in range(n)]
            P = [u for u in range(n) if u != v and sside(col[u]) == root_side and nb[u]]
            Q = [u for u in range(n) if u != v and sside(col[u]) != root_side and nb[u]]
            R = [u for u in range(n) if u != v and sside(col[u]) == root_side and not nb[u]]
            T = [u for u in range(n) if u != v and sside(col[u]) != root_side and not nb[u]]
            def eb(X, Y): return sum(1 for a in X for b in Y if (A[a] >> b) & 1)
            tot += eb(P, R) + eb(Q, T) - eb(R, T)
        g.append(float(tot))
    return np.array(g)

def solve(N, kmax=2, band=(0.2486, 0.32), use_basic_switch=True, use_localizers=True,
          use_switch=True, solver=cp.SCS):
    t0 = time.time()
    states = kc.enumerate_kcolored(N, NCOL, triangle_free=True)
    ns = len(states)
    tf = kcolored_types(N, kmax=kmax)
    dmono = d_mono_vec(states); dedge = d_edge_vec(states)
    x = cp.Variable(ns, nonneg=True)
    cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1]]
    npsd = 0
    for (sigma, flags) in tf:
        mats = fs.P_sigma_col(states, sigma, flags); t = len(flags)
        if t < 2: continue
        Pflat = np.stack([m.ravel() for m in mats], axis=1)
        M = cp.reshape(Pflat @ x, (t, t), order='C')
        cons.append(0.5*(M + M.T) >> 0); npsd += 1
    nbasic = nloc = nsw = 0
    if use_basic_switch:
        cons.append(side_sw0_vec(states, dmono, dedge) @ x <= 0); nbasic += 1
        cons.append(side_sw1_vec(states, 0) @ x <= 0); nbasic += 1
        cons.append(side_sw1_vec(states, 1) @ x <= 0); nbasic += 1
    if use_localizers:
        for g in localizer_vecs(states):
            cons.append(g @ x <= 0); nloc += 1
    if use_switch:
        gsw = margin_switch_vec(states)
        cons.append(gsw @ x <= 0); nsw = 1
    prob = cp.Problem(cp.Maximize(dmono @ x), cons)
    val = prob.solve(solver=solver, max_iters=40000) if solver == cp.SCS else prob.solve(solver=solver)
    print(f"  N={N} states={ns} types={len(tf)} PSD={npsd} basic={nbasic} loc={nloc} sw={nsw} | "
          f"max d_mono = {val:.6f} (beta/N^2<= {val/2:.5f}) [{time.time()-t0:.0f}s] {prob.status}")
    return val

if __name__ == "__main__":
    import sys
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    print(f"=== margin-color SDP N={N} (target d_mono<=0.08; plateau 0.10; bad-cut 3/32=0.09375) ===")
    print("basic side switching only (no margin loc/switch) [should ~match 2-color plateau]:")
    solve(N, use_basic_switch=True, use_localizers=False, use_switch=False)
    print("+ margin consistency localizers:")
    solve(N, use_basic_switch=True, use_localizers=True, use_switch=False)
    print("+ localizers + margin-conditioned switch [does it break <0.09375?]:")
    solve(N, use_basic_switch=True, use_localizers=True, use_switch=True)
    print("DONE")
