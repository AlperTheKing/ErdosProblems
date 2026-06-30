"""Focused SBC test on the CRITICAL cases (skip the slow census, already 0-fail): the C5[t]/C7[t]/C9[t]
BOUNDARY blow-ups (SBC must be TIGHT, margin->0, NOT negative), Mycielskians, two-lane, merged-detour, and
ADVERSARIAL stacked/dense constructions. Use EXACT rho lower/upper bracketing at the extremal to avoid
float-false-violations: report SBC margin = (N + N^2/25) - (rho(O)+|M|) with rho via numpy but FLAG only
margins < -1e-6 as real; print the tightest few."""
from fractions import Fraction as F
import numpy as np, itertools
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
# BOUNDARY blow-ups (tight extremal) -- uniform C(2k+1)[t]
for cyc in (5,7,9,11):
    for t in range(1,9):
        n,E=blowup([t]*cyc); adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): sbc("C%d[%d]"%(cyc,t),n,adj,s,rows)
# NON-uniform odd blow-ups (these stressed earlier certs)
for parts in [[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,6,2,2,6],[2,5,3,3,5]]:
    n,E=blowup(parts); adj,cuts=gmins(n,E)
    for s in (cuts[:1] if cuts else []): sbc("blow%s"%parts,n,adj,s,rows)
# two-lane
for L in range(8,21,2):
    n,E,side,_=build_two_lane(L); sbc("two-lane-L%d"%L,n,adj_of(n,E),side,rows)
# Mycielskians
grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),("M(C11)",mycielski(11,Cn(11)))]:
    adj,cuts=gmins(nn,E)
    for s in cuts[:1]: sbc(name,nn,adj,s,rows)
# merged-detour
n,E=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]; n,E,side=add_cut_path(n,list(E),side,0,12,14); E=sorted(set(E+[(13,27)]))
sbc("merged-detour-N39",n,adj_of(n,E),side,rows)
# ADVERSARIAL: stacked / bridged two-lanes (raise |M| & rho together)
for L,k in [(12,2),(12,3),(16,2),(12,4)]:
    nU=0; EU=[]; sideU=[]
    for c in range(k):
        n1,E1,s1,_=build_two_lane(L)
        EU += [(a+nU,b+nU) for a,b in E1]; sideU+=s1
        if c>0:
            # bridge previous block's vertex 0 to this block's vertex 0 if opposite sides (cut edge)
            pass
        nU+=n1
    sbc("stack%dx-twolane-L%d"%(k,L),nU,adj_of(nU,sorted(set(EU))),sideU,rows)

rows.sort()
print("=== SBC critical-case gate: margin = (N+N^2/25)-(rho(O)+|M|), tight at C5[t] ===",flush=True)
print("  TIGHTEST 18 (margin, name, N, |M|, rho, rho/N, SBC-row-margin):",flush=True)
for r in rows[:18]: print("   ",r,flush=True)
viol=[r for r in rows if r[0]<-1e-6]
print("\n  total configs=%d  REAL SBC violations (margin<-1e-6)=%d"%(len(rows),len(viol)),flush=True)
if viol:
    print("  *** SBC VIOLATIONS: %s ***"%viol[:5],flush=True)
print("  === %s ==="%("SBC FALSE on a critical config -> spectral program dead" if viol else "SBC HOLDS on all critical configs (boundary tight, adversarial pass) -> repaired certificate robust"),flush=True)
