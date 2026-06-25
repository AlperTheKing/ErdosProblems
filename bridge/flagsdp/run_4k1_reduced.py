#!/usr/bin/env python3
"""GPT Pick A, STEP 3: run the FULL reduced cone with SDPA.
Moment cone = k<=2 (cache, exact conic) + the EXACT 4K1 (k=4) cone, S4-block-reduced to PSD blocks
31,31,16,7 (validated in s4_blocks.py: eig(M^4K1(H)) reconstructs from the 4 blocks to 1e-12).
Plus band + deficit cuts (separated) + cut-deficit localizers. The previous rank-one run NEVER enforced
the k=4 cone (min eig stuck at -4e-4); here it is enforced EXACTLY. Question: does eta drop below the
+2.8e-5 plateau (ideally <0)? Any eta<0 must then be verified with an EXACT Fraction certificate.
Box is free (Codex stopped). SOLVER env: SDPA (default) or CLARABEL.
"""
import sys, os, time, pickle
import numpy as np
import cvxpy as cp
import flag_engine as fe
import flag_cutgen as fc
import flag_localizer as floc
import multi_loc as ml
import flag_sdp as fs

SIG = (4, [0, 0, 0, 0])

def reduced_blocks(Pf4, B):
    out = {}; ns = Pf4.shape[0]
    for lab, Bl in B.items():
        tmp = np.einsum('Hab,bj->Haj', Pf4, Bl, optimize=True)
        Tl = np.einsum('ai,Haj->Hij', Bl, tmp, optimize=True)     # (ns,m,m)
        out[lab] = Tl.reshape(ns, -1).T.copy()                    # (m*m, ns)
    return out

def run(band=(0.2486, 0.3197), use_loc=True, maxit=40, tol=1e-7):
    C = pickle.load(open("cache_n9.pkl", "rb"))
    states = C["states"]; ns = len(states); dedge = C["dedge"]; t = C["t"]; deftypes = C["deftypes"]
    Pflats = [(lab, tt, Pf) for (lab, tt, sg, fl, s, Pf, Pi) in C["moments"]]
    B = pickle.load(open("s4_basis_4k1.pkl", "rb"))
    print("loading moments_hi (5.9GB)...", flush=True)
    H = pickle.load(open("moments_hi_n9.pkl", "rb"))
    blk = [b for b in H["blocks"] if b["k"] == 4 and b["name"] == "4K1"][0]
    Pf4 = blk["Pf"]
    # SANITY: pickle 4K1 flag ordering must match enumerate_flags used to build B
    from math import comb
    flags = fs.enumerate_flags(SIG, 6, triangle_free=True)
    assert len(flags) == Pf4.shape[1] == 177, f"flag count {len(flags)} vs {Pf4.shape[1]}"
    n7 = states[7][0]; nk = 1
    for i in range(4):
        nk *= (n7 - i)
    den7 = nk * comb(n7 - 4, 2) ** 2          # pickle Pf = raw P_sigma / denom (precompute_hi_moments)
    Mchk = np.array(fs.P_sigma(9, [states[7]], SIG, flags)[0]) / den7
    derr = np.abs(Mchk - Pf4[7]).max()
    print(f"  flag-ordering sanity: |P_sigma(state7)/denom - pickle[7]| = {derr:.2e} (must be ~0)", flush=True)
    assert derr < 1e-9, "FLAG ORDERING MISMATCH between pickle and enumerate_flags -> abort"
    del H
    red = reduced_blocks(Pf4, B); del Pf4
    sizes = {lab: int(round(red[lab].shape[0] ** 0.5)) for lab in red}
    print(f"reduced 4K1 blocks: {sizes}", flush=True)
    G = C["Gbase"].copy(); Mrows = []
    locs = ml.build_locs(C, ["C5", "C4", "2K2", "P4", "K13"], t) if use_loc else []
    sv = os.environ.get("SOLVER", "SDPA")
    def solve():
        x = cp.Variable(ns, nonneg=True); eta = cp.Variable()
        cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1], G @ x >= eta]
        for (lab, tt, Pf) in Pflats:
            cons.append(cp.reshape(Pf @ x, (tt, tt), order="C") >> 0)
        for lab in red:
            m = sizes[lab]; cons.append(cp.reshape(red[lab] @ x, (m, m), order="C") >> 0)
        if Mrows:
            cons.append(floc._norm_rows(Mrows) @ x >= 0)
        pr = cp.Problem(cp.Maximize(eta), cons)
        val = pr.solve(solver=cp.SDPA) if sv == "SDPA" else (pr.solve(solver=cp.CLARABEL) if sv == "CLARABEL" else pr.solve())
        return val, np.array(x.value).ravel(), pr.status
    v, x, st = solve(); t0 = time.time()
    def k4min(x):
        return min(float(np.linalg.eigvalsh((red[lab] @ x).reshape(sizes[lab], sizes[lab])).min()) for lab in red)
    print(f"iter0: eta={v:+.7e} ({st}) 4K1min={k4min(x):+.2e}", flush=True)
    for it in range(1, maxit + 1):
        added = 0; newcuts = []
        for (k, A, E, S, cls) in deftypes:
            g, p = fc.separate(E, S, x, t, exhaustive_max=13)
            if g < v - tol:
                newcuts.append(fc.cut_from_p(E, S, p, t)); added += 1
        ladded = 0; lmn = 0.0
        if use_loc:
            for (nm, sig, CON, GRA, sup) in locs:
                res = floc.separate_localizer_p(CON, GRA, sup, x)
                if res is not None:
                    p, lam, w = res; lmn = min(lmn, lam); Q = floc.qmat(p); r = np.zeros(ns)
                    for hh in sup:
                        r[hh] = float(w @ (CON[hh] + np.einsum("abcd,cd->ab", GRA[hh], Q)) @ w)
                    Mrows.append(r); ladded += 1
        if added == 0 and ladded == 0:
            print(f"CONVERGED it{it} eta={v:+.7e} ({st})", flush=True); break
        if newcuts:
            G = np.vstack([G] + newcuts)
        v, x, st = solve()
        print(f"it{it}: +{added}d +{ladded}L eta={v:+.7e} ({st}) 4K1min={k4min(x):+.1e} Leig={lmn:+.1e} [{time.time()-t0:.0f}s]", flush=True)
        if v < -tol:
            print(f"it{it}: eta={v:+.7e} < 0 -> CLOSED (LP/SDP); MUST verify exact!", flush=True)
            with open("k4_reduced_cert_state.pkl", "wb") as f:
                pickle.dump(dict(Gdef=[r.tolist() for r in G], Mrows=[r.tolist() for r in Mrows], eta=v), f, protocol=4)
            break
    print(f"FINAL reduced-4K1 eta={v:+.7e} ({st})", flush=True)
    return v

if __name__ == "__main__":
    use_loc = not (len(sys.argv) > 1 and sys.argv[1] == "noloc")
    print(f"=== order-9 reduced-4K1 cone (GPT Pick A), localizers={use_loc}, solver={os.environ.get('SOLVER','SDPA')} ===", flush=True)
    run(use_loc=use_loc)
    print("DONE", flush=True)
