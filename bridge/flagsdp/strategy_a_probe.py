"""STRATEGY A: probabilistic / max-entropy signature distribution.

The dual LP for lemma (16):
  kappa* = max_{w>=0, sum w=1} min_{omega} sum_a w_a L_omega(a)
         = max_w  min_{S min sig}  sum_{e in S} cheapest_private_toll(e, S, w)
where cheapest_private_toll(e,S,w) = min over odd cycles C with C cap S = {e} of w(C).

We want: for the WORST toll w, there is a DISTRIBUTION p over signatures (+private cycle choices) with
  E_{S~p} sum_{e in S} cheapest_private_toll(e,S,w)  <=  n^2/(25t).
By LP duality, kappa* <= n^2/(25t) iff such a p exists for every w. We KNOW kappa*=1.2 at K23 < 1.69.

This probe:
 1. Finds the WORST toll w* (the dual maximizer) at K23.
 2. For that w*, computes the per-signature cost c(S,w*)=sum_e cheapest_private_toll, and asks:
    - what is min_S c(S,w*)?  (= kappa* by strong duality, the single best signature suffices!)
    - is a single signature enough, or does the optimal p mix?  (memory says rotation among sigs).
 3. Tests Gibbs distribution p(S) prop exp(-lambda c(S,w)) and whether E_p cost decreases below single-S.
"""
import numpy as np
from collections import deque
from itertools import combinations
import verify_D25_lemma16 as L


def build(N, A):
    adj = L.adjset(N, A)
    edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mc, side = L.maxcut(N, adj); tau = len(edges)-mc
    sigs = L.min_signatures(N, adj, edges, tau)
    cyc = L.all_odd_cycles_v(N, adj)
    return adj, edges, tau, sigs, cyc


def cost_of_sig(S, w, cyc):
    """sum over e in S of min over odd C with C cap S = {e} of w(C)."""
    total = 0.0
    detail = {}
    for e in S:
        best = float('inf')
        for C in cyc:
            inter = C & S
            if len(inter) == 1 and e in inter:
                wc = sum(w[a] for a in C)
                if wc < best:
                    best = wc
        detail[e] = best
        total += best
    return total, detail


def solve_kappa_and_worst_w(N, A):
    """Solve the full min-max LP to get kappa* and the dual-optimal toll w*."""
    from scipy.optimize import linprog
    adj, edges, tau, sigs, cyc = build(N, A)
    # We solve the PRIMAL congestion LP (as in verify) to get kappa*, then read dual w from edge constraints.
    varlist = []
    for si, S in enumerate(sigs):
        for e in S:
            for ci, C in enumerate(cyc):
                inter = C & S
                if len(inter) == 1 and e in inter:
                    varlist.append((si, e, ci))
    nv = len(varlist); nS = len(sigs); KAP = nv+nS; nvar = nv+nS+1
    c = np.zeros(nvar); c[KAP] = 1.0
    A_eq = []; b_eq = []
    row = np.zeros(nvar)
    for s in range(nS):
        row[nv+s] = 1.0
    A_eq.append(row); b_eq.append(1.0)
    se = {}
    for vi, (si, e, ci) in enumerate(varlist):
        se.setdefault((si, e), []).append(vi)
    for (si, e), vis in se.items():
        row = np.zeros(nvar)
        for vi in vis:
            row[vi] = 1.0
        row[nv+si] = -1.0
        A_eq.append(row); b_eq.append(0.0)
    A_ub = []; b_ub = []
    edge_rows = []
    for a in edges:
        row = np.zeros(nvar)
        for vi, (si, e, ci) in enumerate(varlist):
            if a in cyc[ci]:
                row[vi] += 1.0
        row[KAP] = -1.0
        A_ub.append(row); b_ub.append(0.0); edge_rows.append(a)
    res = linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub), A_eq=np.array(A_eq), b_eq=np.array(b_eq),
                  bounds=[(0, None)]*nvar, method="highs")
    kappa = res.fun
    # dual variables for the edge inequalities give the worst toll w
    w_dual = -res.ineqlin.marginals  # shadow prices; nonneg
    w = {a: max(0.0, w_dual[i]) for i, a in enumerate(edge_rows)}
    s = sum(w.values())
    if s > 0:
        w = {a: w[a]/s for a in w}
    return kappa, w, edges, tau, sigs, cyc, N


def main():
    for builder, lab in [(L.gpt_k23(), 'K23-N13'), (L.petersen(), 'Petersen'), (L.c5n(2), 'C5[2]')]:
        kappa, w, edges, tau, sigs, cyc, N = solve_kappa_and_worst_w(*builder)
        target = N*N/(25.0*tau)
        print(f"\n=== {lab}: kappa*={kappa:.4f} target n^2/25t={target:.4f} (#sigs={len(sigs)}) ===")
        # per-signature cost under worst w
        costs = []
        for S in sigs:
            ct, det = cost_of_sig(S, w, cyc)
            costs.append(ct)
        costs = np.array(costs)
        print(f"  per-sig cost under w*: min={costs.min():.4f} mean={costs.mean():.4f} max={costs.max():.4f}")
        print(f"  best single signature cost = {costs.min():.4f}  (kappa* = {kappa:.4f})")
        print(f"  #sigs achieving min cost = {int(np.sum(costs < costs.min()+1e-6))}")
        # is a single signature enough? compare best-single to kappa*
        if abs(costs.min()-kappa) < 1e-4:
            print("  >>> SINGLE best signature ACHIEVES kappa* (no mixing needed for THIS w)")
        else:
            print(f"  >>> MIXING needed: best single {costs.min():.4f} > kappa* {kappa:.4f}")
        # show the worst toll support
        supp = {a: round(v, 4) for a, v in w.items() if v > 1e-6}
        print(f"  worst toll w* support ({len(supp)} edges): {sorted([(tuple(sorted(a)), v) for a, v in supp.items()], key=lambda z:-z[1])[:8]}")


if __name__ == "__main__":
    main()
