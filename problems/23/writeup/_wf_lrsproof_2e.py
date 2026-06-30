"""Last constructive attempt: relate per-path excess to GLOBAL underload pool (non-local but maybe non-circular).

Define U_over = sum_{v: T>N}(T-N), U_under = sum_{v: T<N}(N-T). Load identity sum_v T=Gamma so
U_over - U_under = Gamma - N*N0 where ... actually sum_v(T-N)=Gamma-N^2. So U_over-U_under = Gamma - N^2.
=> Gamma<=N^2  <=>  U_over<=U_under.  (This is EXACTLY the global Erdos statement in pooled form!)

So 'excess(P) <= ell(f)/N * U_under' type bounds, IF they held with U_under replaced by the budget, would
need U_under to be >= the per-path excess scaled -- but U_under itself is only bounded by N^2/25-|M| via Erdos.
=> circular. CONFIRM by measuring:
  (a) excess(P) vs (ell(f)/N)*U_under   [global pool bound]
  (b) U_over vs U_under (= Gamma<=N^2 directly) -- show this pooled ineq is the SAME hardness
  (c) whether per-path excess(P) <= (ell(f)/N)*U_over EVER (self-referential, expect tight/circular)

This DOCUMENTS that path-LRS's global content = pooled U_over<=U_under = Gamma<=N^2 (no reduction)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn
from _verify_two_lane import build_two_lane

def pf_field(M,cyc):
    pf={}
    for g in M:
        k=len(cyc[g]); d={}
        for P in cyc[g]:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
    return pf

def analyze(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    N=n; m=len(M); Gamma=sum(ell[g]**2 for g in M)
    Uover=sum(T[v]-N for v in range(n) if T[v]>N)
    Uunder=sum(N-T[v] for v in range(n) if T[v]<N)
    # sanity: Uover-Uunder = Gamma-N^2
    assert Uover-Uunder==Gamma-N*N, (Uover,Uunder,Gamma,N)
    for f in M:
        for P in cyc[f]:
            excess=sum(T[v]-N for v in P)
            if excess<=0: continue
            # (a) global pool bound
            a_rhs=F(ell[f],N)*Uunder
            mar_a=a_rhs-excess
            if mar_a<acc['a'][0]: acc['a']=(mar_a,name,N,m,str(f),str(excess),str(Uunder))
            if mar_a<0: acc['a_v']+=1
            # (c) self bound with Uover
            c_rhs=F(ell[f],N)*Uover
            mar_c=c_rhs-excess
            if mar_c<acc['c'][0]: acc['c']=(mar_c,name,N,m,str(f),str(excess),str(Uover))
            if mar_c<0: acc['c_v']+=1
    # (b) pooled global Erdos form on this graph
    if Gamma>N*N: acc['gamma_gt']+=1

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

if __name__=="__main__":
    acc=dict(a=(F(10**9),'','','','','',''),c=(F(10**9),'','','','','',''),a_v=0,c_v=0,gamma_gt=0)
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); analyze("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: analyze("cen%s"%g6,n,adj,s,acc)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): analyze("C%d[%d]"%(cyc,t),n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)N23",mycg),("M(C7)",mycielski(7,Cn(7)))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: analyze(name,nn,adj,s,acc)
    print("=== global pool reformulation (documenting non-reduction) ===",flush=True)
    print("  (a) excess(P) <= (ell/N)*U_under : min margin=%s viol=%d at %s"%(float(acc['a'][0]),acc['a_v'],acc['a'][1:]),flush=True)
    print("  (c) excess(P) <= (ell/N)*U_over  : min margin=%s viol=%d at %s"%(float(acc['c'][0]),acc['c_v'],acc['c'][1:]),flush=True)
    print("  graphs with Gamma>N^2 in battery = %d (expect 0; Erdos holds on gate)"%acc['gamma_gt'],flush=True)
    print("  NOTE U_over<=U_under  <=>  Gamma<=N^2 exactly (pooled global Erdos); identity asserted per-config.",flush=True)
