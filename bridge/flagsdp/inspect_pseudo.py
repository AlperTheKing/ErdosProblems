#!/usr/bin/env python3
"""
Inspect the primal pseudo-graphon x* the switching flag-SDP cannot beat (the ~1/20 plateau).
Solve N with band + full k<=2 switching, extract x*, and report the high-weight colored states
with their edge/mono/cut densities and structure — to see what fake extremal the SDP exploits,
and whether max-cut-margin color refinement would break it.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, cvxpy as cp
import flag_engine as fe, flag_engine_col as fc, flag_sdp_col as fs, flag_switch as sw

def main(N=6):
    states = fc.enumerate_colored(N, triangle_free=True)
    tf = fs.colored_types(N, kmax=2)
    ns = len(states)
    dmono = fs.d_mono_vec(states); dedge = fs.d_edge_vec(states)
    Pmats = [fs.P_sigma_col(states, sig, fl) for (sig, fl) in tf if len(fl) >= 2]
    cuts = sw.all_switching(states, include_sw1=True)
    # add full k<=2 fractional via gen_switches
    cuts = sw.gen_switches(states, kmax=2)
    x = cp.Variable(ns, nonneg=True)
    cons = [cp.sum(x) == 1, dedge @ x >= 0.2486, dedge @ x <= 0.32]
    for mats in Pmats:
        cons.append(sum(x[h]*mats[h] for h in range(ns)) >> 0)
    for g in cuts:
        cons.append(g @ x <= 0)
    prob = cp.Problem(cp.Maximize(dmono @ x), cons)
    val = prob.solve(solver=cp.SCS, max_iters=40000)
    xv = np.array(x.value)
    print(f"N={N}: max d_mono = {val:.5f} (beta/N^2<= {val/2:.5f}); d_edge*={dedge@xv:.4f}")
    print(f"  (in-band edge-density used; 0.32=top of band => x=e/N^2=0.16)")
    # top-weight states
    order = np.argsort(-xv)
    m00 = fc.mono_edge(); m11 = fc.mono_edge_11(); ce = fc.cut_edge()
    print(f"  top-weight colored states (weight, n, e, #col0, mono-frac of edges):")
    shown = 0
    for h in order:
        if xv[h] < 1e-3: break
        n, A, col = states[h]
        e = fe.num_edges(n, A)
        n0 = sum(1 for c in col if c == 0)
        mono = sum(1 for u in range(n) for v in range(u+1,n) if (A[u]>>v)&1 and col[u]==col[v])
        print(f"    w={xv[h]:.4f}  n={n} e={e} col0={n0} mono={mono}/{e} edges  col={col}")
        shown += 1
        if shown >= 12: break
    # how much weight on each (e, mono) profile
    print(f"  aggregate: E[mono/edge among weighted states] = "
          f"{sum(xv[h]*( (sum(1 for u in range(states[h][0]) for v in range(u+1,states[h][0]) if (states[h][1][u]>>v)&1 and states[h][2][u]==states[h][2][v])) / max(1,fe.num_edges(states[h][0],states[h][1])) ) for h in range(ns)):.4f}")

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 6)
