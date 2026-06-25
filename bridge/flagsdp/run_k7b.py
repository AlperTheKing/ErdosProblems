#!/usr/bin/env python3
"""GPT Q42, STRONGER separation: vectorized random-restart MaxCut that returns MULTIPLE violated k=7 cuts
per type per iteration (the single-cut greedy plateaued at +1.6e-7). Goal: push eta below 0 (closure).
Same 107 k=7 root types + k<=5 base + rank-one moment cuts. eta<0 => save state for EXACT cert.
"""
import sys, time, pickle, random
import numpy as np
from scipy.optimize import linprog
import flag_engine as fe
import flag_cutgen as fc
import flag_localizer as floc
import cpp_precompute as cpp

def precompute_k7(states, nthreads=32):
    cpp.compile_cpp()
    types7 = fe.enumerate_graphs(7, triangle_free=True)
    out = []
    for (k, A) in types7:
        E, S, cls = cpp.precompute_type_cpp(states, 7, A, nthreads=nthreads)
        out.append((7, A, E, S, cls))
    return out

def sep_multi(E, S, x, t, v, tol, exhaustive_max=14, restarts=400, keep=5):
    """Vectorized weighted profile-MaxCut: return up to `keep` distinct cuts p with deficit g < v - tol."""
    import itertools
    M = np.tensordot(x, E, axes=(0, 0)); Sx = float(x @ S); nc = M.shape[0]
    Mu1 = np.triu(M, 1)                                # strict upper
    base = float(Mu1.sum()); trM = float(np.trace(M))
    W = M + M.T; np.fill_diagonal(W, 0.0)             # symmetric off-diag weights
    def same_sum(s):                                  # s in {+1,-1}; same-side pairs a<=b
        cross = float(s @ Mu1 @ s)                     # sum_{a<b} M[a,b] s_a s_b
        return (base + cross) / 2.0 + trM
    found = {}
    if nc <= exhaustive_max:
        for p in itertools.product((0, 1), repeat=nc):
            s = np.array([1 if pi == 0 else -1 for pi in p])
            g = same_sum(s) - t * Sx
            if g < v - tol:
                found[p] = g
        items = sorted(found.items(), key=lambda kv: kv[1])[:keep]
        return [list(p) for (p, g) in items], [g for (_, g) in items]
    for _ in range(restarts):
        s = np.where(np.random.rand(nc) < 0.5, 1, -1).astype(float)
        for _pass in range(40):
            h = W @ s
            gain = s * h                              # flip a with largest s_a h_a > 0 to decrease s^T W s
            a = int(np.argmax(gain))
            if gain[a] > 1e-12:
                s[a] = -s[a]
            else:
                break
        g = same_sum(s) - t * Sx
        if g < v - tol:
            p = tuple((s < 0).astype(int).tolist())   # s=+1 -> side 0, s=-1 -> side 1
            if p not in found or g < found[p]:
                found[p] = g
    items = sorted(found.items(), key=lambda kv: kv[1])[:keep]
    return [list(p) for (p, g) in items], [g for (_, g) in items]

def run(band=(0.2486, 0.3197), maxit=40, tol=1e-7):
    C = pickle.load(open("cache_n9.pkl", "rb"))
    states = C["states"]; ns = len(states); dedge = C["dedge"]; t = C["t"]
    deftypes = C["deftypes"]
    Pmom = [(lab, tt, Pf.T.reshape(ns, tt, tt)) for (lab, tt, sg, fl, s, Pf, Pi) in C["moments"]]
    print("precomputing k=7 types...", flush=True); t0 = time.time()
    dt7 = precompute_k7(states); print(f"  k=7 precompute [{time.time()-t0:.0f}s], {len(dt7)} types", flush=True)
    alltypes = list(deftypes) + dt7
    Gdef = [C["Gbase"][i] for i in range(C["Gbase"].shape[0])]; Mrows = []
    lo, hi = band
    def solve():
        c = np.zeros(ns + 1); c[-1] = -1.0
        Aeq = np.zeros((1, ns + 1)); Aeq[0, :ns] = 1.0
        ub = [np.concatenate([-dedge, [0.0]]), np.concatenate([dedge, [0.0]])]; ubb = [-lo, hi]
        Gd = np.asarray(Gdef); A1 = np.concatenate([-Gd, np.ones((Gd.shape[0], 1))], axis=1)
        parts = [np.array(ub), A1]
        if Mrows:
            Mn = floc._norm_rows(Mrows); parts.append(np.concatenate([-Mn, np.zeros((Mn.shape[0], 1))], axis=1))
        A_ub = np.vstack(parts); b_ub = np.array(ubb + [0.0] * (A_ub.shape[0] - 2))
        r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=Aeq, b_eq=[1.0], bounds=[(0, None)] * ns + [(None, None)], method="highs-ipm")
        if not r.success or r.x is None:
            r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=Aeq, b_eq=[1.0], bounds=[(0, None)] * ns + [(None, None)], method="highs")
        return (-float(r.fun), np.asarray(r.x[:ns])) if (r.success and r.x is not None) else (0.0, np.ones(ns) / ns)
    v, x = solve(); t0 = time.time()
    print(f"iter0: eta={v:+.7e}", flush=True)
    for it in range(1, maxit + 1):
        added = 0; a7 = 0; ts = time.time()
        for (k, A, E, S, cls) in alltypes:
            ps, gs = sep_multi(E, S, x, t, v, tol, keep=5)
            for p in ps:
                Gdef.append(fc.cut_from_p(E, S, p, t)); added += 1
                if k == 7:
                    a7 += 1
        tsep = time.time() - ts
        madded = 0; mn = 0.0
        for (lab, tt, P) in Pmom:
            mr, lam2, _ = fc.separate_moment(P, x, maxvecs=8); mn = min(mn, lam2)
            for r in mr:
                Mrows.append(r); madded += 1
        if added == 0 and madded == 0:
            print(f"CONVERGED it{it} eta={v:+.7e}", flush=True); break
        v, x = solve()
        print(f"it{it}: +{added}d (k7={a7}) +{madded}m eta={v:+.7e} meig={mn:+.1e} sep={tsep:.0f}s [{time.time()-t0:.0f}s]", flush=True)
        if v < -tol:
            print(f"it{it}: eta={v:+.7e} < 0 -> CLOSED (float)! saving for exact cert", flush=True)
            with open("k7b_cert_state.pkl", "wb") as f:
                pickle.dump(dict(Gdef=[r.tolist() for r in Gdef], Mrows=[r.tolist() for r in Mrows], eta=v), f, protocol=4)
            break
    print(f"FINAL k7b eta={v:+.7e}", flush=True)
    if v >= 0:
        print("eta>=0 after stronger k=7 separation.", flush=True)
    return v

if __name__ == "__main__":
    print("=== order-9 k=7 STRONGER multi-cut separation (GPT Q42) ===", flush=True)
    run()
    print("DONE", flush=True)
