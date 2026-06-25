#!/usr/bin/env python3
"""PROTOTYPE / AUDIT of GPT Pro's disjunctive-multiplicativity route (chat 6a3b5aba).
Step 1 (decisive premise test): extract the order-9 fooling optimum x* (LP primal) and measure the EDGE-DENSITY
VARIANCE Var_x*(t(K2)) of the mixture. GPT's claim: the eta plateau (~+6e-5, the 2/25 bound) is caused by a
nontrivial real-graph mixture (Cov != 0). If Var(t(K2))>0 the mixture spans densities -> the interval localizer
t((K2-a)(b-K2))>=0 on a narrow band excludes it (the simplest Q=K2 case). If ~0, need the adaptive Q (top
covariance eigenvector). Also reports the second-moment spread to gauge the mixture width.
"""
import numpy as np
from scipy.optimize import linprog
import prove_cert as pc

LO, HI = 0.2486, 0.3197

def solve_xstar(states, ns, dedge, rows, prov):
    """Reconstruct the order-9 contradiction LP and return (eta, x*)."""
    nv = ns + 1   # [x_0..x_{ns-1}, eta]
    c = np.zeros(nv); c[-1] = -1.0   # max eta
    A_ub = []; b_ub = []
    # band: -dedge.x <= -lo ; dedge.x <= hi
    A_ub.append(np.concatenate([-dedge, [0.0]])); b_ub.append(-LO)
    A_ub.append(np.concatenate([dedge, [0.0]])); b_ub.append(HI)
    for i, row in enumerate(rows):
        r = np.asarray(row, float)
        if prov[i][0] in ("deficit", "deficit_pmap"):
            A_ub.append(np.concatenate([-r, [1.0]])); b_ub.append(0.0)   # -g.x + eta <= 0  => g.x >= eta
        else:  # moment / localizer: m.x >= 0  => -m.x <= 0
            A_ub.append(np.concatenate([-r, [0.0]])); b_ub.append(0.0)
    A_eq = [np.concatenate([np.ones(ns), [0.0]])]; b_eq = [1.0]
    bounds = [(0, None)] * ns + [(None, None)]
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=bounds, method="highs-ipm")
    if not res.success:
        res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                      bounds=bounds, method="highs")
    return -res.fun, res.x[:ns]

def main():
    C = pc.load(9)
    print("running cutting_plane (maxit=12)...", flush=True)
    states, ns, dedge, t, rows, prov, v = pc.cutting_plane(C, maxit=12, target=-1e-6, mom_maxvecs=8, verbose=False)
    print(f"cutting_plane eta*={v:+.7e}, {len(rows)} cuts", flush=True)
    eta, x = solve_xstar(states, ns, dedge, rows, prov)
    x = np.maximum(x, 0); x = x / x.sum()
    print(f"reconstructed LP eta={eta:+.7e}, sum x*={x.sum():.4f}, support(|x*|>1e-6)={int((x>1e-6).sum())}", flush=True)
    # edge-density mean + variance under x*
    mean = float(x @ dedge)
    var = float(x @ (dedge**2)) - mean**2
    print(f"x* edge-density: mean(t(K2))={mean:.5f}  Var(t(K2))={var:.3e}  std={var**0.5:.4f}", flush=True)
    # how spread: min/max dedge in support
    sup = x > 1e-6
    print(f"x* support d_edge range: [{dedge[sup].min():.4f}, {dedge[sup].max():.4f}]  (band [{LO},{HI}])", flush=True)
    if var > 1e-6:
        print(">>> Var(t(K2))>0 => fooling x* SPANS edge densities; the interval localizer t((K2-a)(b-K2))>=0 on a", flush=True)
        print("    narrow sub-band can EXCLUDE it (GPT's simplest Q=K2 case). Method APPLICABLE.", flush=True)
    else:
        print(">>> Var(t(K2))~0 => mixture has ~constant edge density; need the ADAPTIVE Q (top covariance", flush=True)
        print("    eigenvector over higher statistics), not just edge density. Method still applies via adaptive Q.", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
