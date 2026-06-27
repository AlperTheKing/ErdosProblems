import probe_int_gap as P
import flag_engine
from mycielskian_check import gamma_min_cut, edges_of
# Test candidate gap bounds:
#  (A) Rfrac <= 1 always (the GPI itself)
#  (B) Rfrac - R01 <= (N^2-Gamma)/K   (gap controlled by deficit/K)
#  (C) K*Rfrac <= K - deficit_slack? i.e. is K*Rfrac <= N + something? 
# Most useful certifiable surrogate: define LHS_frac = K*Rfrac = max_phi sum h_e m_phi /sum phi.
# Claim to test: K*Rfrac <= N  ALWAYS? (i.e. fractional load max is <= N, stronger than <=K!)
worstB=-9; worstC=-9; rows=[]
for N in range(5,11):
    for (n,A) in flag_engine.enumerate_graphs(N, triangle_free=True):
        adj=[set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
        E=edges_of(adj); res,mc=gamma_min_cut(N,adj,E)
        if res is None: continue
        side,G,M=res
        if not M: continue
        K=N+(N*N-G); deficit=N*N-G
        rf,phi=P.Rfrac(N,adj,side,G,M)
        r01,S=P.R01(N,adj,side,G,M)
        # (B): gap - deficit/K
        b=(rf-r01) - deficit/K
        if b>worstB: worstB=b
        # (C): K*rf <= N ?  (normalized: rf <= N/K)
        c=rf - N/K
        if c>worstC: worstC=c; rowc=(N,G,deficit,rf,N/K)
print(f"(B) max[(Rfrac-R01) - deficit/K] = {worstB:.6e}  (<=0 means gap<=deficit/K)")
print(f"(C) max[Rfrac - N/K]            = {worstC:.6e}  (<=0 means K*Rfrac<=N, i.e. frac load max <= N)  at {rowc}")
