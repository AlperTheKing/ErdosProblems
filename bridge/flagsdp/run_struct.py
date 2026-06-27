import probe_int_gap as P
import flag_engine
from mycielskian_check import gamma_min_cut, edges_of, all_shortest_geos
# For the binding graphs (Rfrac near 1), inspect optimal phi support vs B-side structure.
# Also test a CLEAN candidate inequality unifying everything:
#   sum_e h_e m_phi(e) <= sum_v phi_v * N  +  sum_v phi_v*(N^2-Gamma)?  that's K sum phi (=GPI).
# Instead: decompose GPI RHS as N*sum phi + (N^2-Gamma)*sum phi. Test if a SHARPER
# per-edge accounting holds: sum_e h_e m_phi(e) <= N sum phi + sum_e h_e(N - h_e) * (phi-mass on geodesic)? 
# Simplest: check the GPI in the form  sum_e h_e m_phi <= sum_v phi_v (N + N^2 - Gamma) with equality structure.
# Print, for the 3 highest-Rfrac sub-tight graphs, the phi and which vertices carry it.
data=[]
for N in range(5,11):
    for (n,A) in flag_engine.enumerate_graphs(N, triangle_free=True):
        adj=[set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
        E=edges_of(adj); res,mc=gamma_min_cut(N,adj,E)
        if res is None: continue
        side,G,M=res
        if not M: continue
        rf,phi=P.Rfrac(N,adj,side,G,M)
        data.append((rf,N,G,side,phi,M))
data.sort(key=lambda r:-r[0])
for rf,N,G,side,phi,M in data[:6]:
    supp=[v for v in range(N) if phi[v]>1e-7]
    sides_on_supp=set(side[v] for v in supp)
    print(f"Rfrac={rf:.4f} N={N} G={G} def={N*N-G} |M|={len(M)} | phi-support={supp} on B-side(s)={sides_on_supp} phivals={[round(phi[v],3) for v in supp]}")
