"""Probe the PROOF of the spread-geodesic congestion bound rho_B <= n^2/(25t) on atoms.

Route each bad edge e=uv over all shortest B-geodesics (uniform). Define:
  - per-B-EDGE load cong(b)  (what we bound directly)
  - per-VERTEX load lam_v = total geodesic weight through v.
Facts: sum_v lam_v = sum_e d_B(e) + ... (each geodesic has d_B(e)+1 vertices incl endpoints -> internal
       d_B(e)-1, but endpoints carry weight too). Let's compute exactly and test the Cauchy chain:
  (sum_e d_B(e))^2 <= (#B-vertices) * sum_b cong(b)^2  ... vs n.

KEY THEORETICAL TARGET: bound rho_B via cycle-degree inequality. The geodesic e+path is an odd cycle C_e
of length ell_e=d_B(e)+1. Cycle-degree: sum_{v in C_e} deg(v) <= n(ell_e-1)/2 = n d_B(e)/2.
Summing weighted: sum_e sum_{v in C_e} deg(v) <= (n/2) sum_e d_B(e).
LHS = sum_v deg(v) lam_v. So  sum_v deg(v) lam_v <= (n/2) sum_e d_B(e) = (n/2) sum_v (lam_v - (endpoint corr)).
Test these identities and the resulting bound on max cong.

Also test the SPARSEST-CUT dual: rho_B = max over B-vertex-weightings... compute via LP and read the
tight cut, then see if the cut is a 'layer prefix' (connecting to the PROVED coherent-P5 block lemma).
"""
import numpy as np
from collections import deque, defaultdict
import verify_D25_lemma16 as L
from primal_packing_attempt import all_geodesics_load
from test_qfc_atoms import rho_spread


def best_sig_routing(N, A):
    adj = L.adjset(N, A)
    edges = [frozenset((u, v)) for u in range(N) for v in adj[u] if v > u]
    mc, side = L.maxcut(N, adj); tau = len(edges)-mc
    sigs = L.min_signatures(N, adj, edges, tau)
    deg = [len(adj[u]) for u in range(N)]
    best = None
    for S in sigs:
        Bset = set(edges)-set(S)
        adjB = [[] for _ in range(N)]
        for b in Bset:
            a, c = tuple(b); adjB[a].append(c); adjB[c].append(a)
        cong = defaultdict(float); vload = np.zeros(N); ok = True; sumdB = 0.0
        for e in S:
            u, v = tuple(e)
            d = [-1]*N; d[u] = 0; q = deque([u])
            while q:
                x = q.popleft()
                for y in adjB[x]:
                    if d[y] < 0:
                        d[y] = d[x]+1; q.append(y)
            if d[v] < 0:
                ok = False; break
            res = all_geodesics_load(N, adjB, u, v, d[v])
            if res is None:
                ok = False; break
            load, vl = res
            for b, f in load.items():
                cong[b] += f
            vload += vl; sumdB += d[v]
        if not ok:
            continue
        maxc = max(cong.values()) if cong else 0.0
        if best is None or maxc < best[0]:
            best = (maxc, S, dict(cong), vload, sumdB, deg, tau)
    return best


def analyze(builder, lab):
    N, A = builder
    res = best_sig_routing(N, A)
    if res is None:
        print(f"{lab}: skip"); return
    maxc, S, cong, vload, sumdB, deg, tau = res
    deg = np.array(deg)
    sum_deg_lam = (deg*vload).sum()
    print(f"\n{lab}: n={N} t={tau} rho_B={maxc:.4f}  n^2/25t={N*N/(25*tau):.4f}")
    print(f"   sum_e d_B = {sumdB:.2f}   sum_v lam_v = {vload.sum():.2f}  (lam includes endpoint mass)")
    print(f"   sum_v deg*lam = {sum_deg_lam:.2f}   (n/2)*sum_e d_B = {N/2*sumdB:.2f}  "
          f"[cycle-deg gives <=]: {sum_deg_lam <= N/2*sumdB + 1e-6}")
    print(f"   max vertex load = {vload.max():.4f}   sum lam^2 = {(vload**2).sum():.2f}")
    # Cauchy: (sum_e d_B)^2 <= n * sum_b cong^2 ?  edge-version
    congvals = np.array(list(cong.values()))
    print(f"   #B-edges loaded={len(congvals)}  sum cong = {congvals.sum():.2f}  sum cong^2={np.square(congvals).sum():.2f}")


for b, lab in [(L.c5(), 'C5'), (L.c5n(2), 'C5[2]'), (L.petersen(), 'Petersen'),
               (L.gpt_k23(), 'K23-N13'), (L.c5n(3), 'C5[3]')]:
    analyze(b, lab)
