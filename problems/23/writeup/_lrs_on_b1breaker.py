"""Confirm the LRS family survives the B1-breaker (L=16,k=5,gap=8, N=102, R_load/N=2.17, CP-SAT global-max).
If LRS/ROW-LRS/PATH-LRS all hold here while B1/B2 fail, then the |M| slack is ESSENTIAL and the proof must use
bad-count structurally (no |M|-free bound works)."""
from fractions import Fraction as F
from _wf_lrsbreak_0 import build_k_lane, trifree, cutsize, cpmax
from _wf_lrsbreak_0c import greedy_chords
from _satzmu_conn import struct_for_side
from _h import Bconn

L,k,gap=16,5,8
bad=greedy_chords(L,k,gap); n,E,side,bad=build_k_lane(L,k,bad)
adj=[set() for _ in range(n)]
for a,b in E: adj[a].add(b); adj[b].add(a)
pc=cutsize(n,adj,side); opt,bd,iso=cpmax(n,E,60)
st=struct_for_side(n,adj,side); M,ell,T,mu,cyc=st
m=len(M); Gamma=sum(ell[f]**2 for f in M); sumT2=sum(t*t for t in T)
Rload=F(sumT2,Gamma); Tmax=max(T); rhs=F(n)+F(n*n,25)
print("L=%d k=%d gap=%d N=%d global-max=%s |M|=%d N^2/25=%s"%(L,k,gap,n,pc==opt==bd,m,F(n*n,25)))
print("  R_load/N=%.4f (B1 %s, vs 2N)  Tmax/N=%.4f (B2 %s)"%(float(Rload/n),"FAILS" if Rload>2*n else "ok",float(Tmax/n),"FAILS" if Tmax>2*n else "ok"))
print("  LRS: R_load+|M|=%.3f vs N+N^2/25=%.3f -> %s (margin %.3f)"%(float(Rload+m),float(rhs),"HOLDS" if Rload+m<=rhs else "FAILS",float(rhs-(Rload+m))))
# ROW-LRS + PATH-LRS
pf={}
for g in M:
    kk=len(cyc[g]); d={}
    for P in cyc[g]:
        for v in P: d[v]=d.get(v,F(0))+F(1,kk)
    pf[g]=d
rowmin=None; pathmin=None
for f in M:
    Af=sum(pf[f][v]*T[v] for v in pf[f])/ell[f]
    rm=rhs-(Af+m); rowmin=rm if rowmin is None else min(rowmin,rm)
    for P in cyc[f]:
        ap=sum(T[v] for v in P)/ell[f]; pm=rhs-(ap+m); pathmin=pm if pathmin is None else min(pathmin,pm)
print("  ROW-LRS min margin=%.3f -> %s"%(float(rowmin),"HOLDS" if rowmin>=0 else "FAILS"))
print("  PATH-LRS min margin=%.3f -> %s"%(float(pathmin),"HOLDS" if pathmin>=0 else "FAILS"))
print("  === %s ==="%("LRS FAMILY SURVIVES the B1-breaker: |M| slack ESSENTIAL, no |M|-free bound works" if (Rload+m<=rhs and rowmin>=0 and pathmin>=0) else "LRS family also fails here!"))
