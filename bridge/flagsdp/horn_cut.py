#!/usr/bin/env python3
"""GPT Q27-A: completely-positive (Horn) localizer cuts at order 9.
L^{C5,p}(x) in CP_11 (h(theta)>=0, d(theta)>=0). DNN (L>>0 & L>=0) is weaker; CP/DNN first differ at
n=5. For 5 profile classes I and ordering, <H5, L_I(x)> >= 0 is valid (H5 copositive, L_I CP) but NOT
implied by DNN. Scan unscaled Horn cycles; diagonal-scaling separation on the most-violated.
Linear LP rows -> easy exact cert. Conic = full moment-PSD; + deficit + PSD localizers + Horn cuts."""
import sys, time, pickle, itertools
import numpy as np
import cvxpy as cp
import flag_engine as fe
import flag_cutgen as fc
import flag_localizer as floc
import multi_loc as ml

H5 = np.array([[1, -1, 1, 1, -1], [-1, 1, -1, 1, 1], [1, -1, 1, -1, 1],
               [1, 1, -1, 1, -1], [-1, 1, 1, -1, 1]], float)

def L_per_state(C, p, sup, CONST, GRAD):
    """11x11 localizer L^{C5,p}(G) per support state -> array (ns, nc, nc)."""
    Q = floc.qmat(p); ns = len(C["states"]); nc = CONST[sup[0]].shape[0]
    Larr = np.zeros((ns, nc, nc))
    for hi in sup:
        Larr[hi] = CONST[hi] + np.einsum("abcd,cd->ab", GRAD[hi], Q)
    return Larr

def horn_separate(Larr, x, classes_idx, topk=40, tol=1e-9):
    """Scan 5-subsets x orderings; return list of (subset-ordering tuple J, value) most-violated <H5,L_J(x*)>."""
    Lx = np.tensordot(x, Larr, axes=(0, 0)); Lx = 0.5 * (Lx + Lx.T)
    nc = Lx.shape[0]
    found = []
    for I in itertools.combinations(range(nc), 5):
        # distinct cyclic orderings: fix I[0], permute rest, dedup reflections
        seen = set()
        for perm in itertools.permutations(I[1:]):
            J = (I[0],) + perm
            # canonical under reflection (reverse of the cycle keeping I[0] first)
            rev = (I[0],) + tuple(reversed(perm))
            key = min(J, rev)
            if key in seen:
                continue
            seen.add(key)
            sub = Lx[np.ix_(J, J)]
            val = float(np.sum(H5 * sub))
            if val < -tol:
                found.append((J, val))
    found.sort(key=lambda z: z[1])
    return found[:topk]

def diag_sep(Larr, x, J, restarts=30, iters=200, seed=0):
    """min_{s>=0,|s|=1} s^T (H5 o L_J(x*)) s ; return (s, val) best (val<0 => violated scaled cut)."""
    Lx = np.tensordot(x, Larr, axes=(0, 0)); Lx = 0.5 * (Lx + Lx.T)
    M = H5 * Lx[np.ix_(J, J)]; M = 0.5 * (M + M.T)
    rng = np.random.default_rng(seed); best = (None, 1e18)
    for r in range(restarts):
        s = np.abs(rng.standard_normal(5)) if r else np.ones(5)
        s /= np.linalg.norm(s)
        for _ in range(iters):
            g = 2 * M @ s
            s = s - 0.1 * g
            s = np.maximum(s, 0)
            nrm = np.linalg.norm(s)
            if nrm < 1e-12:
                break
            s /= nrm
        val = float(s @ M @ s)
        if val < best[1]:
            best = (s.copy(), val)
    return best

def run(C, names=("C5", "C4", "2K2", "P4", "K13"), band=(0.2486, 0.3197), maxit=40, tol=1e-7, use_diag=True):
    states = C["states"]; ns = len(states); dedge = C["dedge"]; t = C["t"]
    deftypes = C["deftypes"]
    Pflats = [(lab, tt, Pf) for (lab, tt, sigma, flags, s, Pf, Pint) in C["moments"]]
    G = C["Gbase"].copy(); Mrows = []
    locs = ml.build_locs(C, names, t)
    C5 = C["C5"]; classes5 = fc.profile_classes(*C5); sup5 = list(C["sup"])
    # C5 localizer CONST/GRAD
    Csup = C["Csup"]; Gsup = C["Gsup"]
    CONST = {hi: Csup[i] for i, hi in enumerate(sup5)}; GRAD = {hi: Gsup[i] for i, hi in enumerate(sup5)}
    Lcache = {}  # p-key -> Larr
    def Larr_for(p):
        key = tuple(np.round(p, 6))
        if key not in Lcache:
            Lcache[key] = L_per_state(C, p, sup5, CONST, GRAD)
        return Lcache[key]
    for p in floc.c5_extremal_ps(classes5):
        Larr_for(p)
    print(f"  built {len(locs)} PSD localizers + {len(Lcache)} Horn L-caches", flush=True)
    def solve():
        x = cp.Variable(ns, nonneg=True); eta = cp.Variable()
        cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1], G @ x >= eta]
        for (lab, tt, Pf) in Pflats:
            cons.append(cp.reshape(Pf @ x, (tt, tt), order="C") >> 0)
        if Mrows:
            cons.append(floc._norm_rows(Mrows) @ x >= 0)
        pr = cp.Problem(cp.Maximize(eta), cons); val = pr.solve()
        return val, np.array(x.value).ravel(), pr.status
    v, x, st = solve(); t0 = time.time()
    print(f"  iter0: eta={v:+.7f} ({st})", flush=True)
    for it in range(1, maxit + 1):
        added = 0; newcuts = []
        for (k, A, E, S, cls) in deftypes:
            g, p = fc.separate(E, S, x, t, exhaustive_max=13)
            if g < v - tol:
                newcuts.append(fc.cut_from_p(E, S, p, t)); added += 1
        ladded = 0; lmn = 0.0
        for (nm, sig, CONST2, GRAD2, sup2) in locs:
            res = floc.separate_localizer_p(CONST2, GRAD2, sup2, x)
            if res is not None:
                p, lam, w = res; lmn = min(lmn, lam); Q = floc.qmat(p); r = np.zeros(ns)
                for hi in sup2:
                    r[hi] = float(w @ (CONST2[hi] + np.einsum("abcd,cd->ab", GRAD2[hi], Q)) @ w)
                Mrows.append(r); ladded += 1
                if nm == "C5":
                    Larr_for(np.asarray(p))
        # binding C5 deficit p
        for (k, A, E, S, cls) in deftypes:
            if k == 5:
                _, p5 = fc.separate(E, S, x, t)
                Larr_for(np.array([float(p5[i]) for i in range(len(classes5))]))
        # Horn separation over all cached p's
        hadded = 0; hworst = 0.0
        for key, Larr in list(Lcache.items()):
            cuts = horn_separate(Larr, x, None, topk=30)
            for (J, val) in cuts:
                row = np.einsum("ij,Hij->H", H5, Larr[:, J, :][:, :, J])
                Mrows.append(row); hadded += 1; hworst = min(hworst, val)
            if use_diag and cuts:
                for (J, val) in cuts[:5]:
                    s, dv = diag_sep(Larr, x, J)
                    if dv < -1e-8:
                        DHD = np.outer(s, s) * H5
                        row = np.einsum("ij,Hij->H", DHD, Larr[:, J, :][:, :, J])
                        Mrows.append(row); hadded += 1; hworst = min(hworst, dv)
        if added == 0 and ladded == 0 and hadded == 0:
            print(f"  CONVERGED it{it} eta={v:+.7f} ({st})", flush=True); break
        if newcuts:
            G = np.vstack([G] + newcuts)
        v, x, st = solve()
        print(f"  it{it}: +{added}d +{ladded}L +{hadded}H eta={v:+.7f} ({st}) Leig={lmn:+.1e} Hworst={hworst:+.1e} [{time.time()-t0:.0f}s]", flush=True)
        if v < -tol:
            print(f"  it{it}: eta={v:+.7f} < 0 -> CLOSED at t={t}!", flush=True); break
    print(f"FINAL order-9 + Horn/CP cuts eta={v:+.7f} ({st})", flush=True)
    return v

if __name__ == "__main__":
    C = pickle.load(open("cache_n9.pkl", "rb"))
    print("=== order-9 + Horn/CP localizer cuts (GPT Q27-A) ===", flush=True)
    run(C)
    print("DONE", flush=True)
