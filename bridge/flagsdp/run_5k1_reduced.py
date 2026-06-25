#!/usr/bin/env python3
"""GPT Q33: add the exact S5-reduced 5K1 cone (blocks 46,57,41,17,13,1) to the existing exact S4-reduced
4K1 cone (31,31,16,7) and the k<=2 cones; full band + deficit + localizers; SDPA. Moments for 4K1(177)
and 5K1(650) regenerated via the validated C++ moment_tensor (sanity-checked vs fs.P_sigma), normalized,
then projected to the reduced blocks via the validated symmetry-adapted bases. Does eta drop below the
4K1-only ~+2.30e-5? Any eta<0 -> exact Fraction certificate before any claim.
"""
import sys, os, time, pickle
from math import comb
import numpy as np
import cvxpy as cp
import flag_engine as fe
import flag_cutgen as fc
import flag_localizer as floc
import multi_loc as ml
import flag_sdp as fs
import cpp_precompute as cpp

def denom_vec(states, k, s):
    out = []
    for (n, A) in states:
        nk = 1
        for i in range(k):
            nk *= (n - i)
        out.append(nk * comb(n - k, s) ** 2 if (nk > 0 and n - k >= s) else 1)
    return np.array(out, float)

def cpp_moments(states, k, flags, sanity_state=7):
    """M^{kK1}(H) normalized (densities), via C++; sanity-check vs fs.P_sigma on one state."""
    Asig = [0] * k
    raw = cpp.precompute_moment_cpp(states, k, Asig, flags, nthreads=16)   # (ns,t,t) raw counts (modest: coexist with Codex)
    den = denom_vec(states, k, 2)
    # sanity: compare raw[sanity_state] to fs.P_sigma raw
    Mchk = np.array(fs.P_sigma(states[sanity_state][0], [states[sanity_state]], (k, Asig), flags)[0])
    err = np.abs(Mchk - raw[sanity_state]).max()
    print(f"  k={k}: C++ vs P_sigma raw sanity (state {sanity_state}) = {err:.2e}", flush=True)
    assert err < 1e-6, f"C++ moment mismatch k={k}"
    return raw / den[:, None, None]

def reduced_blocks(Mall, Bdict):
    out = {}; dimv = {}; ns = Mall.shape[0]
    for lab, Bl in Bdict.items():
        tmp = np.einsum('Hab,bj->Haj', Mall, Bl, optimize=True)
        Tl = np.einsum('ai,Haj->Hij', Bl, tmp, optimize=True)
        out[lab] = (Tl.reshape(ns, -1).T.copy(), Bl.shape[1])
    return out

def run(band=(0.2486, 0.3197), use_loc=True, maxit=40, tol=1e-7):
    C = pickle.load(open("cache_n9.pkl", "rb"))
    states = C["states"]; ns = len(states); dedge = C["dedge"]; t = C["t"]; deftypes = C["deftypes"]
    Pflats = [(lab, tt, Pf) for (lab, tt, sg, fl, s, Pf, Pi) in C["moments"]]
    cpp.compile_moment()
    # 4K1
    B4 = pickle.load(open("s4_basis_4k1.pkl", "rb"))
    flags4 = fs.enumerate_flags((4, [0, 0, 0, 0]), 6, triangle_free=True)
    M4 = cpp_moments(states, 4, flags4); red4 = reduced_blocks(M4, B4); del M4
    # 5K1
    d5 = pickle.load(open("sk_basis_5K1.pkl", "rb")); B5 = {s: np.array(v) for s, v in d5["blocks"].items()}
    flags5 = fs.enumerate_flags((5, [0, 0, 0, 0, 0]), 7, triangle_free=True)
    M5 = cpp_moments(states, 5, flags5); red5 = reduced_blocks(M5, B5); del M5
    allred = {('4K1', lab): red4[lab] for lab in red4}
    allred.update({('5K1', lab): red5[lab] for lab in red5})
    print(f"reduced cones: 4K1 {[red4[l][1] for l in red4]} + 5K1 {[red5[l][1] for l in red5]}", flush=True)
    G = C["Gbase"].copy(); Mrows = []
    locs = ml.build_locs(C, ["C5", "C4", "2K2", "P4", "K13"], t) if use_loc else []
    def solve():
        x = cp.Variable(ns, nonneg=True); eta = cp.Variable()
        cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1], G @ x >= eta]
        for (lab, tt, Pf) in Pflats:
            cons.append(cp.reshape(Pf @ x, (tt, tt), order="C") >> 0)
        for key, (flat, m) in allred.items():
            cons.append(cp.reshape(flat @ x, (m, m), order="C") >> 0)
        if Mrows:
            cons.append(floc._norm_rows(Mrows) @ x >= 0)
        pr = cp.Problem(cp.Maximize(eta), cons)
        sv = os.environ.get("SOLVER", "SDPA")
        val = pr.solve(solver=cp.SDPA) if sv == "SDPA" else pr.solve(solver=cp.CLARABEL)
        return val, np.array(x.value).ravel(), pr.status
    def cmin(x):
        return min(float(np.linalg.eigvalsh((flat @ x).reshape(m, m)).min()) for (flat, m) in allred.values())
    v, x, st = solve(); t0 = time.time()
    print(f"iter0: eta={v:+.7e} ({st}) conemin={cmin(x):+.2e}", flush=True)
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
            print(f"CONVERGED it{it} eta={v:+.7e}", flush=True); break
        if newcuts:
            G = np.vstack([G] + newcuts)
        v, x, st = solve()
        print(f"it{it}: +{added}d +{ladded}L eta={v:+.7e} ({st}) conemin={cmin(x):+.1e} Leig={lmn:+.1e} [{time.time()-t0:.0f}s]", flush=True)
        if v < -tol:
            print(f"it{it}: eta={v:+.7e} < 0 -> CLOSED; MUST verify exact!", flush=True)
            with open("k45_reduced_cert_state.pkl", "wb") as f:
                pickle.dump(dict(Gdef=[r.tolist() for r in G], Mrows=[r.tolist() for r in Mrows], eta=v), f, protocol=4)
            break
    print(f"FINAL 4K1+5K1 eta={v:+.7e} ({st})", flush=True)
    return v

if __name__ == "__main__":
    use_loc = not (len(sys.argv) > 1 and sys.argv[1] == "noloc")
    print(f"=== order-9 4K1+5K1 reduced cones (GPT Q33), loc={use_loc}, solver={os.environ.get('SOLVER','SDPA')} ===", flush=True)
    run(use_loc=use_loc)
    print("DONE", flush=True)
