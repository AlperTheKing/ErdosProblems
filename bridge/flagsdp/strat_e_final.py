#!/usr/bin/env python3
"""STRATEGY E FINAL VERDICT TEST.

The single decisive question: is there a SPECTRAL (rank-controlled, eigenvalue/
Rayleigh) lower bound L(G) with  nu*(G) >= L(G) >= 25 t^2 / N^2 ?

We test the strongest natural candidate: the SDP/vector relaxation of the odd-cycle
packing, which equals the eigenvalue optimum of the 'odd-cocycle' quadratic form.
Concretely, nu* >= 25t^2/N^2 with EQUALITY at C5[n]. At C5[n] the tight packing is
the q^2 five-cycles, and the dual is uniform edge-price 1/5. The spectral surrogate
that EXACTLY reproduces C5[n] tightness is the second-eigenvalue / Cheeger quantity
of the bipartite part B:

    Candidate (E*):  nu* >= e_M^2 / (N * lambda1(B))   [a Rayleigh/Hoffman LB]

where e_M = |M| = t edges of M (= beta), lambda1(B) = top eigenvalue of bipartite B.
RATIONALE: on C5[q], B = C5[q] cut part is bipartite (q,q)-biregular pieces; we test
whether this Rayleigh form (a) lower-bounds nu* and (b) reaches 25t^2/N^2.

We ALSO test the GPT-stated 'quadratic/spectral GENUINELY FALSE on band' by directly
exhibiting whether any Rayleigh form of fixed type can separate the band.
"""
import itertools
import numpy as np
from strat_e_probe import (adjset, maxcut, nu_star, tau_int, lambda_eigs,
                           petersen, c5n, gpt_k23, theta46)
import flag_engine as fe


def bipartite_lambda1(N, adj, side):
    AB = np.zeros((N, N))
    for u in range(N):
        for v in adj[u]:
            if side[u] != side[v]:
                AB[u][v] = 1.0
    w = np.linalg.eigvalsh(AB)
    return w[-1]


def candidates(N, adj):
    mc, side = maxcut(N, adj)
    t = tau_int(N, adj)              # = |M| = beta
    lamB = bipartite_lambda1(N, adj, side)
    lams = lambda_eigs(N, adj)
    lmin = lams[0]
    lam1 = lams[-1]
    e = sum(1 for u in range(N) for v in adj[u] if v > u)
    out = {}
    # (E1) Rayleigh:  t^2 / (N * lambdaB)   -- candidate spectral LB on nu*
    out['E1_t2_over_NlamB'] = (t * t) / (N * lamB) if lamB > 1e-9 else 0.0
    # (E2) -lam_min * t / something
    out['E2_neglmin_t_over_N'] = (-lmin) * t / N
    # (E3)  t^2 / (N * (-lmin))  -- frustration spectral
    out['E3_t2_over_Nneglmin'] = (t * t) / (N * (-lmin)) if -lmin > 1e-9 else 0.0
    return t, out


def run():
    named = [(*petersen(), "Petersen"), (*gpt_k23(), "K23-N13"), (*theta46(), "theta46"),
             (*c5n(1), "C5[1]"), (*c5n(2), "C5[2]"), (*c5n(3), "C5[3]")]
    print("=== Strategy E final: candidate spectral lower bounds vs nu* and vs 25t^2/N^2 ===", flush=True)
    print("A valid spectral LB must satisfy  cand <= nu*  AND  cand >= 25t^2/N^2 (to finish).", flush=True)
    for (N, A, label) in named:
        adj = adjset(N, A)
        ns, _, _ = nu_star(N, adj)
        t, cands = candidates(N, adj)
        target = 25.0 * t * t / (N * N)
        print(f"  {label:10s} N={N:2d} t={t:2d} nu*={ns:6.3f} 25t^2/N^2={target:6.3f}", flush=True)
        for name, val in cands.items():
            le = "<=nu* OK" if val <= ns + 1e-6 else "<=nu* FAIL"
            ge = ">=tgt OK" if val >= target - 1e-6 else ">=tgt FAIL"
            print(f"      {name:24s}={val:7.3f}  [{le}] [{ge}]", flush=True)

    # The decisive sweep: over exhaustive N<=9, does ANY of E1/E3 stay between target and nu*?
    print("\n=== Exhaustive N<=9: fraction of graphs where each candidate is a VALID LB (<=nu*) AND finishes (>=target) ===", flush=True)
    for N in range(6, 10):
        states = fe.enumerate_graphs(N, triangle_free=True)
        stat = {}
        tot = 0
        for (n, A) in states:
            adj = adjset(n, A)
            t = tau_int(n, adj)
            if t == 0:
                continue
            ns, _, _ = nu_star(n, adj)
            _, cands = candidates(n, adj)
            target = 25.0 * t * t / (n * n)
            tot += 1
            for name, val in cands.items():
                d = stat.setdefault(name, {'le': 0, 'ge': 0, 'both': 0, 'le_fail_min': 1e9})
                isle = val <= ns + 1e-6
                isge = val >= target - 1e-6
                if isle:
                    d['le'] += 1
                else:
                    d['le_fail_min'] = min(d['le_fail_min'], ns - val)  # negative = overshoot
                if isge:
                    d['ge'] += 1
                if isle and isge:
                    d['both'] += 1
        print(f"  N={N} ({tot} graphs):", flush=True)
        for name, d in stat.items():
            print(f"     {name:24s} valid_LB(<=nu*):{d['le']}/{tot}  finishes(>=tgt):{d['ge']}/{tot}  "
                  f"BOTH:{d['both']}/{tot}", flush=True)


if __name__ == "__main__":
    run()
