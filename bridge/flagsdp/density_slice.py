#!/usr/bin/env python3
"""GPT Q30 Pick B: density-slice / band-localized deficit products.
Restrict to slice [a,b]; for the binding C5 deficit rule g_r add (with E*g_r a DISJOINT U-statistic):
   h-_r = (E*g_r) - a*g_r >= 0 ,   h+_r = b*g_r - (E*g_r) >= 0 ,   band row (E-a)(b-E) >= 0.
Sound: counterexample W has g_r(W)>=0 and a<=e(W)<=b. Attacks edge-density<->deficit correlation
(the broad-density fooling mixture). Order-9, stays a HiGHS LP. If slice closes -> tile the band.
"""
import sys, time, pickle, itertools
import numpy as np
from scipy.optimize import linprog
import flag_engine as fe
import flag_cutgen as fc
import flag_localizer as floc
import multi_loc as ml

def e2_disj(states):
    """E^2 disjoint U-statistic: avg over {4 distinct vertices, 3 perfect matchings} of [m1 edge][m2 edge].
    For a graphon -> phi(E)^2."""
    out = np.zeros(len(states))
    for hi, (n, A) in enumerate(states):
        if n < 4:
            continue
        adj = [[(A[u] >> v) & 1 for v in range(n)] for u in range(n)]
        s = 0; cnt = 0
        for quad in itertools.combinations(range(n), 4):
            a, b, c, d = quad
            # 3 matchings: (ab,cd),(ac,bd),(ad,bc)
            s += adj[a][b] * adj[c][d] + adj[a][c] * adj[b][d] + adj[a][d] * adj[b][c]
            cnt += 3
        out[hi] = s / cnt if cnt else 0.0
    return out

def egr_and_gr(states, sigma, p, t, classes, sup):
    """Return (E*g_r)_disj(H) and g_r(H) per state for the C5 rule with cut prob vector p over classes.
    (E*g_r)_disj: for each C5-tuple R, the 4 non-roots split into deficit pair {u,v} + edge pair {p,q}
    (6 ways); avg deficit(u,v;R)*[pq edge]. g_r: avg over the C(4,2)=6 deficit pairs."""
    k, Asig = sigma
    cidx = {c: i for i, c in enumerate(classes)}
    ns = len(states)
    EG = np.zeros(ns); GR = np.zeros(ns)
    for hi in sup:
        n, A = states[hi]
        adj = [[bool((A[u] >> v) & 1) for v in range(n)] for u in range(n)]
        nk = 1
        for i in range(k):
            nk *= (n - i)
        if nk == 0:
            continue
        npair = (n - k) * (n - k - 1) // 2          # C(n-k,2) deficit pairs for g_r
        eg = 0.0; gr = 0.0
        for R in itertools.permutations(range(n), k):
            if not fc.fs._induces_sigma_ordered(A, R, sigma):
                continue
            W = [w for w in range(n) if w not in R]
            q = {}
            for w in W:
                prof = frozenset(i for i in range(k) if adj[w][R[i]])
                q[w] = p[cidx[prof]]
            # g_r contribution: avg over all pairs {u,v} in W of deficit
            gloc = 0.0
            for ui in range(len(W)):
                u = W[ui]
                for vi in range(ui + 1, len(W)):
                    v = W[vi]
                    qc = q[u] * q[v] + (1 - q[u]) * (1 - q[v])
                    gloc += (qc if adj[u][v] else 0.0) - t
            gr += gloc / npair
            # (E*g_r)_disj: 6 splits of the 4 non-roots into {u,v} (deficit) + complement {p,q} (edge)
            if len(W) == 4:
                egloc = 0.0
                for uv in itertools.combinations(range(4), 2):
                    u, v = W[uv[0]], W[uv[1]]
                    pq = [W[j] for j in range(4) if j not in uv]
                    pe, qe = pq
                    qc = q[u] * q[v] + (1 - q[u]) * (1 - q[v])
                    defv = (qc if adj[u][v] else 0.0) - t
                    egloc += defv * (1.0 if adj[pe][qe] else 0.0)
                eg += egloc / 6.0
        EG[hi] = eg / nk; GR[hi] = gr / nk
    return EG, GR

def egr_gen(states, sigma, p, t, classes, sup):
    """General-k disjoint density product. (E*g_r)_disj(H): per root-tuple R inducing sigma, avg over
    {deficit pair {u,v}} x {disjoint edge pair {pp,qq}} (both from the n-k non-roots) of
    deficit(u,v;R)*[edge(pp,qq)]. g_r as usual. For a graphon -> phi(E)*phi(g_r) (disjoint vtx sets
    => independent). Reduces to egr_and_gr on the C5 type (m=4). Needs m=n-k >= 4 for the edge pair."""
    k, Asig = sigma
    cidx = {c: i for i, c in enumerate(classes)}
    ns = len(states)
    EG = np.zeros(ns); GR = np.zeros(ns)
    for hi in sup:
        n, A = states[hi]
        adj = [[bool((A[u] >> v) & 1) for v in range(n)] for u in range(n)]
        nk = 1
        for i in range(k):
            nk *= (n - i)
        if nk == 0:
            continue
        m = n - k
        npair = m * (m - 1) // 2
        ndisj = npair * ((m - 2) * (m - 3) // 2) if m >= 4 else 0
        eg = 0.0; gr = 0.0
        for R in itertools.permutations(range(n), k):
            if not fc.fs._induces_sigma_ordered(A, R, sigma):
                continue
            W = [w for w in range(n) if w not in R]
            q = {}
            for w in W:
                prof = frozenset(i for i in range(k) if adj[w][R[i]])
                q[w] = p[cidx[prof]]
            gloc = 0.0
            for ui in range(len(W)):
                u = W[ui]
                for vi in range(ui + 1, len(W)):
                    v = W[vi]
                    qc = q[u] * q[v] + (1 - q[u]) * (1 - q[v])
                    gloc += (qc if adj[u][v] else 0.0) - t
            gr += gloc / npair
            if m >= 4:
                egloc = 0.0
                for ui in range(len(W)):
                    u = W[ui]
                    for vi in range(ui + 1, len(W)):
                        v = W[vi]
                        qc = q[u] * q[v] + (1 - q[u]) * (1 - q[v])
                        defv = (qc if adj[u][v] else 0.0) - t
                        rem = [w for w in W if w != u and w != v]
                        es = 0
                        for ai in range(len(rem)):
                            ra = rem[ai]
                            for bi in range(ai + 1, len(rem)):
                                if adj[ra][rem[bi]]:
                                    es += 1
                        egloc += defv * es
                eg += egloc / ndisj
        EG[hi] = eg / nk; GR[hi] = gr / nk
    return EG, GR


def run_slice(C, a, b, maxit=200, tol=1e-7, verbose=True, rich=False):
    states = C["states"]; ns = len(states); dedge = C["dedge"]; t = C["t"]
    deftypes = C["deftypes"]
    C5 = C["C5"]; classes5 = fc.profile_classes(*C5); sup5 = list(C["sup"])
    locs = ml.build_locs(C, ["C5", "C4", "2K2", "P4", "K13"], t)
    e2 = e2_disj(states)
    band_row = (a + b) * dedge - a * b - e2           # (E-a)(b-E) ; >=0
    # k<=2 moment-PSD blocks (incl empty-type K0) as CONIC constraints (exact -> variance bound bites)
    import cvxpy as cp
    Pflats = [(lab, tt, Pf) for (lab, tt, sg, fl, s, Pf, Pi) in C["moments"]]   # (tt*tt, ns)
    Gdef = [C["Gbase"][i] for i in range(C["Gbase"].shape[0])]
    Mrows = [band_row]
    print(f"  slice [{a:.4f},{b:.4f}]; localizers {len(locs)}; conic k<=2 blocks {[l for l,_,_ in Pflats]}", flush=True)
    lo, hi = a, b
    def solve():
        x = cp.Variable(ns, nonneg=True); eta = cp.Variable()
        cons = [cp.sum(x) == 1, dedge @ x >= lo, dedge @ x <= hi, np.array(Gdef) @ x >= eta]
        for (lab, tt, Pf) in Pflats:
            cons.append(cp.reshape(Pf @ x, (tt, tt), order="C") >> 0)
        cons.append(floc._norm_rows(Mrows) @ x >= 0)
        pr = cp.Problem(cp.Maximize(eta), cons); val = pr.solve()
        return val, np.array(x.value).ravel()
    v, x = solve(); t0 = time.time()
    print(f"  iter0: eta={v:+.7f}", flush=True)
    seen_p = set()
    for it in range(1, maxit + 1):
        added = 0
        for (k, A, E, S, cls) in deftypes:
            g, p = fc.separate(E, S, x, t, exhaustive_max=13)
            if g < v - tol:
                Gdef.append(fc.cut_from_p(E, S, p, t)); added += 1
        # binding deficit rule(s) -> density-slice rows. rich: all dual-active types (k=2,4,5); else C5 only
        dadded = 0
        dtypes = deftypes if rich else [d for d in deftypes if d[0] == 5]
        for (kk, Ak, Ek, Sk, clk) in dtypes:
            if kk > 5:
                continue
            clsk = fc.profile_classes(kk, Ak)
            if len(clsk) > 16:                       # keep separation/egr tractable
                continue
            gk, pk = fc.separate(Ek, Sk, x, t)
            pv = np.array([float(pk[i]) for i in range(len(clsk))])
            key = (kk, tuple(np.round(pv, 6)))
            if key in seen_p:
                continue
            seen_p.add(key)
            supk = [i for i in range(ns) if Sk[i] > 0]
            EG, GR = egr_gen(states, (kk, Ak), pv, t, clsk, supk)
            Mrows.append(EG - a * GR)                 # h- = (E-a) g_r >= 0
            Mrows.append(b * GR - EG)                 # h+ = (b-E) g_r >= 0
            dadded += 2
        ladded = 0; lmn = 0.0
        for (nm, sig, CON, GRA, sup) in locs:
            res = floc.separate_localizer_p(CON, GRA, sup, x)
            if res is not None:
                pp, lam, w = res; lmn = min(lmn, lam); Q = floc.qmat(pp); r = np.zeros(ns)
                for hh in sup:
                    r[hh] = float(w @ (CON[hh] + np.einsum("abcd,cd->ab", GRA[hh], Q)) @ w)
                Mrows.append(r); ladded += 1
        if added == 0 and dadded == 0 and ladded == 0:
            print(f"  CONVERGED it{it} eta={v:+.7f}", flush=True); break
        v, x = solve()
        if verbose and (it <= 8 or it % 5 == 0):
            print(f"  it{it}: +{added}d +{dadded}dens +{ladded}L eta={v:+.7f} rows={len(Mrows)} Leig={lmn:+.1e} [{time.time()-t0:.0f}s]", flush=True)
        if v < -tol:
            print(f"  it{it}: eta={v:+.7f} < 0 -> SLICE [{a},{b}] CLOSED!", flush=True); break
    print(f"FINAL slice [{a:.4f},{b:.4f}] eta={v:+.7f}", flush=True)
    return v

if __name__ == "__main__":
    C = pickle.load(open("cache_n9.pkl", "rb"))
    a = float(sys.argv[1]) if len(sys.argv) > 1 else 0.30
    b = float(sys.argv[2]) if len(sys.argv) > 2 else 0.31
    rich = (len(sys.argv) > 3 and sys.argv[3] == "rich")
    print(f"=== order-9 density-slice [{a},{b}] (GPT Q30 Pick B{' RICH all-type' if rich else ''}) ===", flush=True)
    run_slice(C, a, b, rich=rich)
    print("DONE", flush=True)
