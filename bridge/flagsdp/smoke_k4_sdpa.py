#!/usr/bin/env python3
"""Smoke test: can SDPA (or default) solve the slice conic with k<=2 + ONE k=4 moment-PSD block
without the CLARABEL crash? Just iter0 (band + deficit base + the block). Reports status/eta/time/dim.
Usage: python smoke_k4_sdpa.py [blockname] [SOLVER]   e.g.  python smoke_k4_sdpa.py 4K1 SDPA"""
import sys, time, pickle, os
import numpy as np
import cvxpy as cp

def main():
    bn = sys.argv[1] if len(sys.argv) > 1 else "4K1"
    sv = sys.argv[2] if len(sys.argv) > 2 else "DEFAULT"
    band = (0.30, 0.31)
    C = pickle.load(open("cache_n9.pkl", "rb"))
    H = pickle.load(open("moments_hi_n9.pkl", "rb"))
    states = C["states"]; ns = len(states); dedge = C["dedge"]
    Pflats = [(lab, tt, Pf) for (lab, tt, sg, fl, s, Pf, Pi) in C["moments"]]
    blk = None
    for b in H["blocks"]:
        if b["k"] == 4 and b["name"] == bn:
            blk = (b["name"], b["tt"], b["Pf"].reshape(ns, -1).T.copy()); break
    if blk is None:
        print("k=4 blocks available:", [b["name"] for b in H["blocks"] if b["k"] == 4], flush=True); return
    G = C["Gbase"].copy()
    print(f"smoke: k<=2 {[l for l,_,_ in Pflats]} + k4 block {blk[0]} (tt={blk[1]}); solver={sv}", flush=True)
    t0 = time.time()
    x = cp.Variable(ns, nonneg=True); eta = cp.Variable()
    cons = [cp.sum(x) == 1, dedge @ x >= band[0], dedge @ x <= band[1], G @ x >= eta]
    for (lab, tt, Pf) in Pflats:
        cons.append(cp.reshape(Pf @ x, (tt, tt), order="C") >> 0)
    cons.append(cp.reshape(blk[2] @ x, (blk[1], blk[1]), order="C") >> 0)
    pr = cp.Problem(cp.Maximize(eta), cons)
    try:
        if sv == "SDPA":
            val = pr.solve(solver=cp.SDPA)
        elif sv == "SCS":
            val = pr.solve(solver=cp.SCS, eps=1e-6, max_iters=20000)
        elif sv == "CLARABEL":
            val = pr.solve(solver=cp.CLARABEL)
        else:
            val = pr.solve()
        print(f"  RESULT eta={val:+.7e} status={pr.status} [{time.time()-t0:.0f}s]", flush=True)
    except Exception as e:
        print(f"  CRASH/EXC: {type(e).__name__}: {str(e)[:200]} [{time.time()-t0:.0f}s]", flush=True)

if __name__ == "__main__":
    main()
    print("DONE", flush=True)
