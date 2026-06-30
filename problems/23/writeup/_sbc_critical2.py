"""Lean SBC critical test (fast: no maxcut_all on huge N). Uniform C(2k+1)[t] is PROVABLY tight (margin 0),
skip it. Real threats: NEAR-EXTREMAL non-uniform odd blow-ups (perturb C5[t] -> does margin go negative?),
two-lane, Mycielskians, merged-detour. SBC margin = (N+N^2/25) - (rho(O)+|M|); flag margin < -1e-6."""
from fractions import Fraction as F
import numpy as np
from _h import Bconn
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
from _verify_two_lane import build_two_lane, Ogram
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _M_tailswitch_gate import build_pd

def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def sbc(name,n,adj,side,rows):
    if not Bconn(n,adj,side): return
    res=Ogram(n,adj,side)
    if res is None: return
    M,ell,O=res; m=len(M)
    if m==0: return
    Of=np.array([[float(x) for x in r] for r in O])
    rho=float(max(abs(np.linalg.eigvals(Of))))
    maxrow=float(max(sum(O[i]) for i in range(m)))
    rhs=n+n*n/25.0
    rows.append((round(rhs-(rho+m),4), name, n, m, round(rho,4), round(rho/n,4), round(rhs-(maxrow+m),4)))
def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))

rows=[]
# NEAR-EXTREMAL non-uniform odd blow-ups (small enough for gmins, N<=25)
nu=[[2,2,2,2,3],[2,2,2,3,3],[3,3,3,3,2],[1,3,2,2,3],[2,3,2,3,2],[1,4,2,2,4],[1,5,2,2,5],
    [2,2,2,2,2,2,3],[2,2,3,2,2,3,2],[1,3,2,3,2,3,2],[1,4,2,4,2,4,2]]
for parts in nu:
    n,E=blowup(parts)
    if n>26: continue
    adj,cuts=gmins(n,E)
    for s in (cuts[:1] if cuts else []): sbc("nu%s"%parts,n,adj,s,rows)
# uniform small (gmins-feasible) to SEE the tight margin -> 0
for cyc in (5,7):
    for t in (1,2,3):
        n,E=blowup([t]*cyc)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): sbc("C%d[%d]"%(cyc,t),n,adj,s,rows)
# two-lane
for L in range(8,19,2):
    n,E,side,_=build_two_lane(L); sbc("two-lane-L%d"%L,n,adj_of(n,E),side,rows)
# Mycielskians
grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7)))]:
    adj,cuts=gmins(nn,E)
    for s in cuts[:1]: sbc(name,nn,adj,s,rows)
# merged-detour
n,E=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]; n,E,side=add_cut_path(n,list(E),side,0,12,14); E=sorted(set(E+[(13,27)]))
sbc("merged-detour-N39",n,adj_of(n,E),side,rows)

rows.sort()
print("=== SBC LEAN critical gate: margin=(N+N^2/25)-(rho+|M|) ===",flush=True)
print("  TIGHTEST 14 (margin,name,N,|M|,rho,rho/N,SBCrow-margin):",flush=True)
for r in rows[:14]: print("   ",r,flush=True)
viol=[r for r in rows if r[0]<-1e-6]
print("  total=%d  REAL SBC violations=%d"%(len(rows),len(viol)),flush=True)
print("  === %s ==="%("SBC FALSE: %s"%viol[:3] if viol else "SBC HOLDS on all near-extremal/adversarial critical configs -> repaired certificate robust"),flush=True)
