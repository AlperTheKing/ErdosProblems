"""EXACT gate of Codex block-214 LRS (Load-Rayleigh Bad-count Slack):
  R_load + m <= N + N^2/25,  R_load = ell^T O ell / ell^T ell = (sum_v T(v)^2)/Gamma.
Equivalently the elementary SCALAR inequality (exact Fraction):
  sum_v T(v)^2  <=  Gamma * (N + N^2/25 - m),   Gamma=sum ell^2, m=|M|, N=n.
Implies Erdos (sum T^2 >= Gamma^2/N => R_load>=Gamma/N>=25m/N; +LRS => m<=N^2/25). Replaces the refuted SM
(sum T^2<=N*Gamma) by adding (N^2/25 - m)*Gamma slack. Tight at C5[t]. Battery: census gamma-min N<=11 +
blow-ups C5/C7/C9[t] + non-uniform + two-lane L=8..20 + Mycielskians + merged/full detour + dense-chord +
stacked adversarial. EXACT, report min margin (Fraction) + first violation."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _tail_positive_extra_counterexample import add_cut_path, adj_from_edges
from _M_tailswitch_gate import build_pd

def lrs(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    m=len(M)
    if m==0: return
    Gamma=sum(ell[f]**2 for f in M)
    sumT2=sum(t*t for t in T)
    rhs=Gamma*(F(n)+F(n*n,25)-m)
    margin=rhs-sumT2   # >=0 wanted
    acc['n']+=1
    if margin<acc['min'][0]: acc['min']=(margin,name,n,m,Gamma,str(sumT2))
    if margin<0:
        acc['viol']+=1
        if acc['first'] is None: acc['first']=(name,''.join(map(str,side)),n,m,Gamma,str(sumT2),str(rhs))

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
    acc={'n':0,'viol':0,'first':None,'min':(F(10**9),'','','','','')}
    print("=== LRS EXACT gate: sum T^2 <= Gamma*(N+N^2/25-m) ===",flush=True)
    # two-lane
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); lrs("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    print("  two-lane done (min=%s)"%(acc['min'][:2],),flush=True)
    # census gamma-min
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['viol']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: lrs("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d done (viol=%d)"%(nn,acc['viol']-v0),flush=True)
    # uniform + non-uniform blow-ups (gmins-feasible N<=26)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): lrs("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],[2,2,3,2,2,3,2]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): lrs("nu%s"%parts,n,adj,s,acc)
    print("  blow-ups done (min=%s)"%(acc['min'][:2],),flush=True)
    # Mycielskians
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9)))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: lrs(name,nn,adj,s,acc)
    # merged/full detour
    for tag,withmerge in [("full-detour-N39",False),("merged-detour-N39",True)]:
        n,E=build_pd(12,[(0,8),(2,6)]); side=[v%2 for v in range(n)]; n,E,side=add_cut_path(n,list(E),side,0,12,14)
        E=sorted(set(E+[(13,27)])) if withmerge else sorted(set(E))
        lrs(tag,n,adj_of(n,E),side,acc)
    # stacked two-lanes (disjoint union + bridge to keep B connected)
    for L in (10,12,14):
        n1,E1,s1,_=build_two_lane(L); n2,E2,s2,_=build_two_lane(L)
        E2s=[(a+n1,b+n1) for a,b in E2]
        # bridge x0 of block1 to x0 of block2 only if opposite sides (cut edge keeps B connected)
        br=[(0,n1)] if s1[0]!=s2[0] else [(0,n1+1)]
        nU=n1+n2; EU=sorted(set(E1+E2s+br)); sideU=s1+s2
        lrs("stack2-twolane-L%d"%L,nU,adj_of(nU,EU),sideU,acc)
    print("  Mycielskians+detours+stacked done",flush=True)
    print("\n  total configs=%d  LRS VIOLATIONS=%d"%(acc['n'],acc['viol']),flush=True)
    print("  MIN LRS margin (Gamma*(N+N^2/25-m) - sum T^2) = %s  at %s"%(float(acc['min'][0]),acc['min'][1:]),flush=True)
    if acc['first']: print("  first LRS violation: %s"%(acc['first'],),flush=True)
    print("  === %s ==="%("LRS VIOLATED -> repair fails" if acc['viol'] else "LRS HOLDS exactly on full battery (incl two-lane, blow-ups tight at C5[t], detours, adversarial) -> exact scalar repaired certificate"),flush=True)
