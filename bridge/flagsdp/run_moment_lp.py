#!/usr/bin/env python3
"""GPT Q28 Pick A: rank-one moment-cut LP route (HiGHS) with INTEGER eigenvectors, all k<=4 moment
blocks + deficit + PSD localizers. Integer v => exact rational rows (h_{sigma,v}(H)=v^T M^sigma(H) v).
LP eta >= SDP eta, so any finite family with eta<0 is a rigorous certificate (then verify exactly).
"""
import sys, time, pickle
from math import gcd
from functools import reduce
import numpy as np
from scipy.optimize import linprog
import flag_engine as fe
import flag_cutgen as fc
import flag_localizer as floc
import multi_loc as ml

def load_blocks(C, H):
    """Return list of (name, k, sigma, s, Pfloat (ns,tt,tt), Pint (list of int arrays), denom)."""
    states = C["states"]; ns = len(states); blocks = []
    for (lab, tt, sigma, flags, s, Pf, Pint) in C["moments"]:        # k<=2 from cache
        Pflo = Pf.T.reshape(ns, tt, tt)
        # denom per state for these
        from math import comb
        k = sigma[0]; denom = []
        for (n, _A) in states:
            nk = 1
            for i in range(k):
                nk *= (n - i)
            d = nk * (comb(n - k, s) ** 2) if (nk > 0 and n - k >= s) else 1
            denom.append(d)
        blocks.append((lab, k, sigma, s, Pflo, Pint, denom))
    import os
    k3 = os.environ.get("INCLUDE_K3", "0") == "1"
    for b in H["blocks"]:                                            # k=3,4
        if b["k"] == 3 and not k3:                                   # drop slow 308-dim k=3 by default
            continue
        blocks.append((b["name"], b["k"], b["sigma"], b["s"], b["Pf"], b["Pint"], b["denom"]))
    return blocks

def prim_int(vec, Mx, scales=(2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 128, 256, 512)):
    vec = vec / (np.abs(vec).max() + 1e-30)
    for D in scales:
        vi = np.rint(vec * D).astype(np.int64)
        g = reduce(gcd, [abs(int(z)) for z in vi if z != 0], 0)
        if g > 1:
            vi = vi // g
        if np.any(vi) and float(vi @ Mx @ vi) < -1e-11:
            return vi
    return None

def run(C, H, band=(0.2486, 0.3197), maxit=400, tol=1e-7, eig_per=4, target=-1e-7, verbose=True):
    states = C["states"]; ns = len(states); dedge = C["dedge"]; t = C["t"]
    deftypes = C["deftypes"]; lo, hi = band
    blocks = load_blocks(C, H)
    locs = ml.build_locs(C, ["C5", "C4", "2K2", "P4", "K13"], t)
    print(f"  moment blocks: {[(b[0],b[4].shape[1]) for b in blocks]}", flush=True)
    Gdef = [C["Gbase"][i] for i in range(C["Gbase"].shape[0])]
    Mrows = []; prov = []   # prov parallels Mrows for the exact cert
    def solve():
        c = np.zeros(ns + 1); c[-1] = -1.0
        Aeq = np.zeros((1, ns + 1)); Aeq[0, :ns] = 1.0
        ub = [np.concatenate([-dedge, [0.0]]), np.concatenate([dedge, [0.0]])]; ubb = [-lo, hi]
        Gd = np.asarray(Gdef); ub.append(None)
        A1 = np.concatenate([-Gd, np.ones((Gd.shape[0], 1))], axis=1)
        parts = [np.array(ub[:2]), A1]
        if Mrows:
            Mn = floc._norm_rows(Mrows)
            parts.append(np.concatenate([-Mn, np.zeros((Mn.shape[0], 1))], axis=1))
        A_ub = np.vstack(parts)
        b_ub = np.array(ubb + [0.0] * (A_ub.shape[0] - 2))
        r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=Aeq, b_eq=[1.0], bounds=[(0, None)] * ns + [(None, None)], method="highs-ipm")
        if not r.success or r.x is None:
            r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=Aeq, b_eq=[1.0], bounds=[(0, None)] * ns + [(None, None)], method="highs")
        return (-float(r.fun), np.asarray(r.x[:ns])) if (r.success and r.x is not None) else (0.0, np.ones(ns) / ns)
    v, x = solve(); t0 = time.time()
    print(f"  iter0: eta={v:+.7f}", flush=True)
    for it in range(1, maxit + 1):
        added = 0
        for (k, A, E, S, cls) in deftypes:
            g, p = fc.separate(E, S, x, t, exhaustive_max=13)
            if g < v - tol:
                row = fc.cut_from_p(E, S, p, t); Gdef.append(row); added += 1
        ladded = 0
        for (nm, sig, CONST, GRAD, sup) in locs:
            res = floc.separate_localizer_p(CONST, GRAD, sup, x)
            if res is not None:
                p, lam, w = res; Q = floc.qmat(p); r = np.zeros(ns)
                for hi_ in sup:
                    r[hi_] = float(w @ (CONST[hi_] + np.einsum("abcd,cd->ab", GRAD[hi_], Q)) @ w)
                Mrows.append(r); prov.append(("loc", sig, w.copy(), p.copy())); ladded += 1
        madded = 0; worst = 0.0
        for (lab, k, sigma, s, Pflo, Pint, denom) in blocks:
            Mx = np.tensordot(x, Pflo, axes=(0, 0)); Mx = 0.5 * (Mx + Mx.T)
            w_, V_ = np.linalg.eigh(Mx)
            for j in range(min(eig_per, len(w_))):
                if w_[j] < -1e-9:
                    vi = prim_int(V_[:, j], Mx)
                    if vi is not None:
                        # row(H) = vi^T Pf(H) vi  (== exact vi^T Pint(H) vi / denom(H), since Pf=mat/denom);
                        # vectorized float; exact Pint version regenerated only at cert time
                        vf = vi.astype(float)
                        row = np.einsum("Hi,i->H", np.einsum("Hij,j->Hi", Pflo, vf), vf)
                        Mrows.append(row); prov.append(("mom", lab, sigma, s, vi.copy())); madded += 1
                        worst = min(worst, float(vi @ Mx @ vi))
        if added == 0 and ladded == 0 and madded == 0:
            print(f"  CONVERGED it{it} eta={v:+.7f}", flush=True); break
        v, x = solve()
        if verbose and (it <= 10 or it % 5 == 0):
            print(f"  it{it}: +{added}d +{ladded}L +{madded}m eta={v:+.7f} rows={len(Mrows)} mworst={worst:+.1e} [{time.time()-t0:.0f}s]", flush=True)
        if v < target:
            print(f"  it{it}: eta={v:+.7f} < 0 -> CLOSED (LP>=SDP rigorous, float)!", flush=True)
            with open("momentlp_cert_n9.pkl", "wb") as f:
                pickle.dump(dict(Gdef=[r.tolist() for r in Gdef], Mrows=[r.tolist() for r in Mrows], prov=prov, eta=v), f, protocol=4)
            print("  saved momentlp_cert_n9.pkl (for exact verification)", flush=True)
            break
    print(f"FINAL moment-LP eta={v:+.7f} [{time.time()-t0:.0f}s]", flush=True)
    return v

if __name__ == "__main__":
    C = pickle.load(open("cache_n9.pkl", "rb"))
    H = pickle.load(open("moments_hi_n9.pkl", "rb"))
    print("=== order-9 rank-one moment-cut LP route, k<=2 + k=4 (GPT Q28-A, k3 dropped) ===", flush=True)
    run(C, H, eig_per=10, maxit=600)
    print("DONE", flush=True)
