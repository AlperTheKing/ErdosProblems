import probe_int_gap as P
from fractions import Fraction
import flag_engine
from mycielskian_check import gamma_min_cut, edges_of, all_shortest_geos
# KEY CLAIM (B), exact-rational form:  L_frac - L_01 <= deficit = N^2 - Gamma
#   where L_frac = max_{phi>=0, sum phi=1} sum_e h_e m_phi(e)  (=K*Rfrac)
#         L_01   = max_S (1/|S|) sum_e h_e min_P |P cap S|     (=K*R01)
# We recompute L_frac, L_01 directly (no /K), in floats but check margin, and report tightness cases.
worst=-9; tightcases=[]; n_tight=0; total=0
for N in range(5,11):
    for (n,A) in flag_engine.enumerate_graphs(N, triangle_free=True):
        adj=[set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
        E=edges_of(adj); res,mc=gamma_min_cut(N,adj,E)
        if res is None: continue
        side,G,M=res
        if not M: continue
        total+=1
        K=N+(N*N-G); deficit=N*N-G
        rf,phi=P.Rfrac(N,adj,side,G,M); r01,S=P.R01(N,adj,side,G,M)
        Lf=K*rf; L0=K*r01
        slack = deficit - (Lf-L0)
        if -slack>worst: worst=-slack
        if abs(slack)<1e-6:
            n_tight+=1
            if len(tightcases)<8: tightcases.append((N,G,deficit,round(Lf,3),round(L0,3)))
print(f"scanned {total} graphs. KEY CLAIM  L_frac - L_01 <= N^2-Gamma:  max violation = {worst:.3e} (<=0 OK)")
print(f"tight (equality) count = {n_tight}; samples (N,Gamma,deficit,Lfrac,L01) = {tightcases}")
