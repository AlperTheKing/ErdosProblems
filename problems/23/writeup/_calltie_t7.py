"""WHY does the gamma-min cut refuse the C-alltie contrapositive?
For the glued adversary graphs (overloaded gadget + saturated-dead gadget), examine on the
gamma-min cut: (a) is O empty? (b) is the saturated-dead vertex's K-comp merged with O?
This identifies the enforcing mechanism (kill-overload vs merge-components)."""
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side, kcomponents

def all_gmin(n, E):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj); cand=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        Mloc=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
        if not Mloc: continue
        G=0; ok=True
        for (u,v) in Mloc:
            d=bdist_restr(adj,side,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok: cand.append((side,G))
    if not cand: return adj,[]
    gm=min(G for _,G in cand)
    return adj,[(side,G) for side,G in cand if G==gm]

def analyze(name,n,E):
    adj,cuts=all_gmin(n,E)
    n_Oempty=0; n_sat_inOcomp=0; n_nosat=0; tot=len(cuts)
    for side,G in cuts:
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,mu,cyc=st; N=n
        O=set(v for v in range(N) if T[v]>N)
        if not O: n_Oempty+=1; continue
        comp,find=kcomponents(n,cyc)
        # any saturated vertex with dead nb?
        found_sat=False
        for v in range(N):
            if T[v]!=N: continue
            deadnb=[z for z in adj[v] if side[z]!=side[v] and T[z]==0]
            if deadnb:
                found_sat=True
                Cv=comp[find(v)]
                if Cv & O: n_sat_inOcomp+=1
        if not found_sat: n_nosat+=1
    print(f"  {name}: gmin-cuts={tot} | O-empty={n_Oempty} | (O nonempty:) sat-dead-in-O-comp={n_sat_inOcomp} no-sat-dead={n_nosat}")

if __name__=="__main__":
    print("=== mechanism enforcing C-alltie on glued adversary graphs ===")
    OVER=dec("I?BD@g]Qo")
    C5p=(6,[(0,1),(1,2),(2,3),(3,4),(4,0),(0,5)])
    N=0;EU=[]
    for (nn,Es) in [OVER,C5p]:
        EU+=[(a+N,b+N) for (a,b) in Es]; N+=nn
    for bv in range(OVER[0], N):
        EUb=EU+[(0,bv)]
        analyze(f"bridge 0-{bv}", N, EUb)
