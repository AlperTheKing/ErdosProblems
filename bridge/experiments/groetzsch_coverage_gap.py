#!/usr/bin/env python3
"""
GRÖTZSCH COVERAGE GAP (from GPT Q12 intermediate trace, independently confirmed 2026-06-20).

The 4-template coverage proof of CF claims the menu {edge, C5, Petersen, Clebsch} (+ A7 for C5-free)
certifies tau_K <= RHS=(N^2/5-e)/2 on every band triangle-free graph. GPT Q12 flagged a structured
counterexample TO THE PROOF METHOD (not to CF): the Grötzsch graph (Mycielskian of C5, 11 vtx, 20 edges,
triangle-free, chi=4) blown up and padded with a small isolated set sits in-band with tau_K=0 (so CF
HOLDS), yet BOTH cheap templates (edge-root, C5-root F_C) fail.

This script confirms it and maps the gap regime. tau_K=0 means a perfect Clebsch homomorphism exists, so
CF is TRUE on all these graphs (0 <= RHS) — this is a gap in the explicit-template proof, NOT a CF
counterexample. Grötzsch CONTAINS induced C5s (F_C is finite), which falsifies the earlier claim that the
C5-root covers every C5-containing band graph.

Scaling (verified): F_C(Grötzsch[t]) = 3 t^2 ; edge-root bound = 6 t^2 ; e = 20 t^2 ; N = 11 t + s.
In-band (x=e/N^2 <= 0.16): s >= 0.18 t. C5-root covers iff s >= 0.40 t; edge-root iff s >= 1.65 t.
=> for s in [0.18 t, 0.40 t): in-band AND both cheap certificates fail.

Pure Python, tiny graphs. Keep t small (min_FC enumerates all 5-subsets: O(C(N,5))).
"""
import random
from verify_4branch_coverage import adj_list, tau_K_ub, edge_root_bound, min_FC, dedup
random.seed(7)

def groetzsch():
    E = []
    for i in range(5):
        E.append((i, (i + 1) % 5))                      # C5 on 0..4
    for i in range(5):                                  # shadow u_i = i+5
        E.append((i + 5, (i - 1) % 5)); E.append((i + 5, (i + 1) % 5))
    for i in range(5):
        E.append((10, i + 5))                           # apex w=10 ~ all shadows
    return 11, E

def blowup(N0, E0, t, iso=0):
    E = [(a * t + x, b * t + y) for (a, b) in E0 for x in range(t) for y in range(t)]
    return N0 * t + iso, E

def main():
    N0, E0 = groetzsch(); E0 = dedup(E0); A0 = adj_list(N0, E0)
    trifree = not any((v in A0[u] and w in A0[u] and w in A0[v])
                      for u in range(N0) for v in range(N0) for w in range(N0) if u < v < w)
    print(f"Grötzsch base: N={N0} e={len(E0)} x={len(E0)/N0**2:.4f} triangle_free={trifree} "
          f"tau_K_ub={tau_K_ub(N0, A0)} (0 => Clebsch-homomorphic, CF holds)")
    print("\nt  s   N    e   x       RHS    tauK_ub  edge(ok)   F_C(ok)  cheapOK  note")
    gaps = 0
    for t in (3, 5):                                    # keep small: min_FC is O(C(N,5))
        for s in range(0, int(0.7 * t) + 2):
            N, E = blowup(N0, E0, t, s); E = dedup(E); A = adj_list(N, E); e = len(E)
            x = e / (N * N); rhs = (N * N / 5.0 - e) / 2.0
            if not (0.1243 <= x <= 0.16):
                continue
            tk = tau_K_ub(N, A); er, _ = edge_root_bound(N, A, E); fc = min_FC(N, A, E)
            er_ok = er <= rhs + 1e-9; fc_ok = (fc is not None) and fc <= rhs + 1e-9
            cheap = er_ok or fc_ok
            note = "<== COVERAGE GAP (in-band, tauK=0, both cheap fail; CF still holds)" if (not cheap and tk == 0) else ""
            if note:
                gaps += 1
            print(f"{t} {s:2d} {N:4d} {e:4d} {x:.4f}  {rhs:6.1f}  {tk:3d}   "
                  f"{er:6.1f}({int(er_ok)})  {fc:4d}({int(fc_ok)})   {int(cheap)}  {note}", flush=True)
    print(f"\nConfirmed coverage gaps: {gaps}. CF is NOT violated (tau_K=0 <= RHS on every gap).")
    print("Implication: the explicit cheap-template menu is INCOMPLETE; need a 5th template or the")
    print("Clebsch-HOM-existence argument directly. CF / Step-2 truth UNAFFECTED.")
    print("DONE")

if __name__ == "__main__":
    main()
