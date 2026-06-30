"""HIGH-PRECISION SCOUT (NOT an acceptance gate -- lambda,x,h are algebraic; floats only suggest) for Codex
block-224 PSC-50:  lambda + m + Xi(h)/50 <= N + N^2/25,  margin = 50*(N+N^2/25-m-lambda) - Xi(h).
h(v)=N*Phi(v)^2/lambda, Phi(v)=sum_f x_f p_f(v), x=Perron vector of O=P^T P (sum x_f^2=1), Xi(h)=TV_B(h)-TV_M(h).
At C5[t]: lambda=N, Phi uniform => h const => Xi=0, m=N^2/25 => margin=0 (TIGHT). Reports margins + min ratio.
Reminder: exact reduction is via SBC (lambda+m<=N+N^2/25) / LRS (elementary), already EXACT-validated; PSC-50
is the cut-pressure PROOF route. This scout corroborates Codex's float scout only."""
import numpy as np, subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
from _verify_two_lane import build_two_lane, Ogram
from _wf_lrsbreak_0 import build_k_lane, trifree, cutsize
from _wf_lrsbreak_0c import greedy_chords

def psc(name,n,adj,side):
    if not Bconn(n,adj,side): return None
    res=Ogram(n,adj,side)
    if res is None: return None
    M,ell,O=res; m=len(M)
    if m==0: return None
    Of=np.array([[float(x) for x in r] for r in O])
    w,V=np.linalg.eigh(Of)
    lam=float(w[-1]); x=np.array(V[:,-1]); x=x/np.linalg.norm(x)
    if x.sum()<0: x=-x
    # Phi(v)=sum_f x_f p_f(v): need p_f(v) -> rebuild from struct
    st=struct_for_side(n,adj,side); _M,_ell,T,_mu,cyc=st
    pf={}
    for gi,g in enumerate(M):
        k=len(cyc[g]); d={}
        for P in cyc[g]:
            for v in P: d[v]=d.get(v,0.0)+1.0/k
        pf[g]=(gi,d)
    Phi=[0.0]*n
    for g in M:
        gi,d=pf[g]
        for v,pv in d.items(): Phi[v]+=x[gi]*pv
    h=[n*Phi[v]*Phi[v]/lam for v in range(n)]
    TVb=sum(abs(h[u]-h[v]) for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
    TVm=sum(abs(h[u]-h[v]) for u in range(n) for v in adj[u] if v>u and side[u]==side[v])
    Xi=TVb-TVm
    rhs=n+n*n/25.0
    margin=50*(rhs-m-lam)-Xi
    ratio=(rhs-m-lam)/Xi if Xi>1e-9 else None
    return (margin,name,n,m,round(lam,4),round(Xi,4),ratio)

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

rows=[]
print("=== PSC-50 HIGH-PRECISION SCOUT (NOT exact acceptance gate) ===",flush=True)
# C5[t] (tight, margin->0)
for cyc in (5,7,9):
    for t in range(1,5):
        n,E=blowup([t]*cyc); adj,cuts=gmins(n,E)
        if cuts:
            r=psc("C%d[%d]"%(cyc,t),n,adj,cuts[0])
            if r: rows.append(r)
# two-lane
for L in (8,12,16,20):
    n,E,side,_=build_two_lane(L); r=psc("two-lane-L%d"%L,n,adj_of(n,E),side)
    if r: rows.append(r)
# k-lane B1/B2 breakers
for (L,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
    bad=greedy_chords(L,k,gap); n,E,side,bad=build_k_lane(L,k,bad)
    r=psc("klane-L%dk%d"%(L,k),n,adj_of(n,E),side)
    if r: rows.append(r)
# census sample N<=10
for nn in (8,9,10):
    outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[:400]
    for g6 in outg:
        n,E=dec(g6); adj,cuts=gmins(n,E)
        for s in cuts[:1]:
            r=psc("cen%s"%g6,n,adj,s)
            if r: rows.append(r)
rows.sort()
print("  TIGHTEST 14 (margin, name, N, m, lambda, Xi, ratio):",flush=True)
for r in rows[:14]: print("   ",r,flush=True)
viol=[r for r in rows if r[0]<-1e-6]
ratios=[r[6] for r in rows if r[6] is not None]
print("\n  configs=%d  float-margin<0 (SCOUT)=%d  min ratio (N+N^2/25-m-lambda)/Xi = %s"%(len(rows),len(viol),min(ratios) if ratios else 'na'),flush=True)
print("  NOTE: float scout only; the exact-verified reduction is SBC/LRS. PSC-50 = cut-pressure PROOF route.",flush=True)
print("  === %s ==="%("SCOUT found a float-negative margin (investigate exactly)" if viol else "PSC-50 float-scout: 0 negative margins; min ratio>0 (cut-pressure within 50x budget) -- corroborates Codex"),flush=True)
