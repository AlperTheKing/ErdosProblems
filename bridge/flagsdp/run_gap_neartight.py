import probe_int_gap as P
import flag_engine
from mycielskian_check import gamma_min_cut, edges_of
# Focus: relation between deficit (N^2-Gamma) and fractional ratio Rfrac and gap.
rows=[]
for N in range(5,11):
    for (n,A) in flag_engine.enumerate_graphs(N, triangle_free=True):
        adj=[set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
        E=edges_of(adj); res,mc=gamma_min_cut(N,adj,E)
        if res is None: continue
        side,G,M=res
        if not M: continue
        rf,phi=P.Rfrac(N,adj,side,G,M)
        r01,S=P.R01(N,adj,side,G,M)
        rows.append((N,G,N*N-G,rf,rf-r01))
# bucket: among graphs with small deficit, is Rfrac near 1 and gap near 0?
rows.sort(key=lambda r:r[3], reverse=True)
print("Top 12 by Rfrac (N,Gamma,deficit,Rfrac,gap):")
for r in rows[:12]: print(f"  N={r[0]} G={r[1]} def={r[2]} Rfrac={r[3]:.5f} gap={r[4]:.5f}")
rows.sort(key=lambda r:r[4], reverse=True)
print("Top 12 by gap (Rfrac-R01):")
for r in rows[:12]: print(f"  N={r[0]} G={r[1]} def={r[2]} Rfrac={r[3]:.5f} gap={r[4]:.5f}")
# correlation: for graphs with Rfrac>0.5, what's max gap?
hi=[r for r in rows if r[3]>0.5]
print("among Rfrac>0.5:",len(hi),"max gap=",max((r[4] for r in hi),default=None))
