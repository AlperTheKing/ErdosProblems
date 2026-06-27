import probe_int_gap as P
import flag_engine
from mycielskian_check import gamma_min_cut, edges_of
# We have empirically: Rfrac <= R01 + deficit/K  (tight). 
# GPI = Rfrac<=1. Sufficient via this route: R01 + deficit/K <= 1  <=> K*R01 <= K-deficit = N.
# So test (D): K*R01 <= N, i.e. the 0/1-Hall MAX-LOAD <= N  (not K).
#   K*R01 = max_S [ sum_e h_e min_P|P cap S| / |S| ].  Claim: this <= N.
# That is a PURE 0/1 statement: for every S, sum_e h_e min_P|P cap S| <= N|S|.
worstD=-9; rowD=None
for N in range(5,11):
    for (n,A) in flag_engine.enumerate_graphs(N, triangle_free=True):
        adj=[set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
        E=edges_of(adj); res,mc=gamma_min_cut(N,adj,E)
        if res is None: continue
        side,G,M=res
        if not M: continue
        K=N+(N*N-G)
        r01,S=P.R01(N,adj,side,G,M)
        d=K*r01 - N
        if d>worstD: worstD=d; rowD=(N,G,K*r01,N,sorted(S) if S else None)
print(f"(D) max[ K*R01 - N ] = {worstD:.6e}  (<=0 means: for all S, sum_e h_e min_P|P cap S| <= N|S|)  at {rowD}")
