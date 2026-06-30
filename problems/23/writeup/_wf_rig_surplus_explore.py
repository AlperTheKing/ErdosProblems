"""EXPLORATORY (not the gate): measure surplus-route quantities exactly on the full battery.
For each config compute:
  N, beta=|M|, Gamma=sum ell^2,
  budget5 = Gamma*(N^2/25 - beta)
  Uplus = sum_v (T_v - N)_+
  sumT_TminN = sum_v T_v(T_v-N)              [LHS first term of LOAD-PSC]
  TVcut, TVbad                                [for the cut-pressure deficit]
  S1 = sum_f (ell_f - 5)        (linear surplus)
  S2 = sum_f (ell_f^2 - 25)     (quadratic surplus) = Gamma - 25*beta
  GS1 = sum_f ell_f*(ell_f-5)   (ell-weighted linear surplus)
We want to understand the ratios:  Uplus / S1 , Uplus / S2 , Uplus / budget5, etc.
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def measure(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    N=n; beta=len(M)
    Gamma=sum(ell[f]**2 for f in M)
    budget5=Gamma*(F(N*N,25)-beta)
    Uplus=sum((t-N) for t in T if t>N)
    sumT_TminN=sum(t*(t-N) for t in T)
    badset=set((min(a,b),max(a,b)) for a,b in M)
    TVcut=F(0); TVbad=F(0)
    for u in range(n):
        for v in adj[u]:
            if v>u:
                d=abs(T[u]-T[v])
                if side[u]!=side[v]: TVcut+=d
                else: TVbad+=d
    S1=sum((ell[f]-5) for f in M)
    S2=sum((ell[f]**2-25) for f in M)   # = Gamma - 25*beta
    GS1=sum(ell[f]*(ell[f]-5) for f in M)
    # LOAD-PSC-5 LHS / budget
    lhs5 = sumT_TminN + F(N,5)*(TVcut-TVbad)
    acc.append((name,N,beta,Gamma,budget5,Uplus,sumT_TminN,TVcut,TVbad,S1,S2,GS1,lhs5))

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

def full_battery(measure_fn):
    acc=[]
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); measure_fn("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); measure_fn("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: measure_fn("cen%s"%g6,n,adj,s,acc)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): measure_fn("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],[1,6,2,2,6]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): measure_fn("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    def bridge(b1,b2,u,v):
        nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u, n1+v)]
    extra=[("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
           ("C7|brg|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]
    for name,(nn,E) in extra:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: measure_fn(name,nn,adj,s,acc)
    return acc

if __name__=="__main__":
    acc=full_battery(measure)
    print("total configs measured =",len(acc),flush=True)
    # ratios of interest
    def show_extreme(label, keyfn, want='max'):
        best=None
        for row in acc:
            k=keyfn(row)
            if k is None: continue
            if best is None or (k>best[0] if want=='max' else k<best[0]): best=(k,row[0],row[1],row[2])
        print("  %-28s %s = %s at %s"%(label,want,(float(best[0]) if best else None),best[1:] if best else None),flush=True)
    # row = name,N,beta,Gamma,budget5,Uplus,sumT_TminN,TVcut,TVbad,S1,S2,GS1,lhs5
    show_extreme("Uplus/S2", lambda r: F(r[5],r[10]) if r[10]>0 else None, 'max')
    show_extreme("Uplus/S1", lambda r: F(r[5],r[9]) if r[9]>0 else None, 'max')
    show_extreme("Uplus/GS1", lambda r: F(r[5],r[11]) if r[11]>0 else None, 'max')
    show_extreme("Uplus/budget5", lambda r: F(r[5],r[4]) if r[4]>0 else None, 'max')
    show_extreme("sumT_TminN/budget5", lambda r: F(r[6],r[4]) if r[4]>0 else None, 'max')
    show_extreme("lhs5/budget5", lambda r: F(r[12],r[4]) if r[4]>0 else None, 'max')
    show_extreme("(TVcut-TVbad)", lambda r: r[7]-r[8], 'min')
    # configs where S1==0 (all ell=5) but Uplus>0
    print("  --- configs with S1=0 (all ell=5):",flush=True)
    for row in acc:
        if row[9]==0:
            print("     %s N=%d beta=%d Uplus=%s budget5=%s S2=%s"%(row[0],row[1],row[2],row[5],row[4],row[10]),flush=True)
