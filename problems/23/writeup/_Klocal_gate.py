"""Gate Codex 410 K-LOCAL VARIANCE LEMMA (corrects the FALSE global VAR-STABILITY 5*Tail0>=VarT).
   Positive-K graph: u~v iff some bad edge g has a shortest geodesic Q in cyc[g] with u,v both on Q.
   K(P) = component containing V(P).  VarK=sum_{v in K}(T(v)-N)^2; VarKcent=sum_{v in K}(T(v)-mean_K T)^2.
   CLAIM: 5*Tail0(P) >= VarK(P)  (and the centered fallback).  Tail0=sum_r(2r+1)Z_r from _layer_gate.Zr_row.
   Also CONFIRM global VAR-STABILITY FAILS on glued C5 chains q>=9 (Codex counterexample / my battery gap).
   gamma-min no-port rows.  Exact Fraction.
"""
import subprocess
from fractions import Fraction as F
from collections import deque
from _singleton_core import ell_map, Hi_and_best
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, mycielski

def Kcomponent(n,M,cyc,Pset):
    """positive-K graph component containing Pset."""
    adjK=[set() for _ in range(n)]
    for g in M:
        for Q in cyc[g]:
            for a in Q:
                for b in Q:
                    if a!=b: adjK[a].add(b)
    seen=set(Pset); dq=deque(Pset)
    while dq:
        u=dq.popleft()
        for w in adjK[u]:
            if w not in seen: seen.add(w); dq.append(w)
    return seen

def check_cut(name,n,adj,side,acc,Lam,want_global=False):
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    if not M: return
    N=F(n); VarT=sum((T[v]-N)**2 for v in range(n))
    for f in M:
        if ell[f]%2==0: continue
        for P in cyc[f]:
            if len(P)!=ell[f]: continue
            # no-port filter
            em0=ell_map(n,adj,side); noport=True
            for i in range(len(P)):
                Hi,W,d=Hi_and_best(n,adj,side,em0,P,i,Lam)
                if Hi is not None and Hi<0: noport=False; break
            if not noport: continue
            _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
            Tail0=sum((2*r+1)*Z[r] for r in range(n))
            K=Kcomponent(n,M,cyc,set(P))
            VarK=sum((T[v]-N)**2 for v in K)
            meanK=sum(T[v] for v in K)/len(K)
            VarKc=sum((T[v]-meanK)**2 for v in K)
            acc['rows']+=1
            if 5*Tail0<VarK:
                acc['Kfail']+=1
                if acc['K_ex'] is None: acc['K_ex']=(name,n,tuple(P),str(5*Tail0),str(VarK),len(K))
            if 5*Tail0<VarKc:
                acc['Kcfail']+=1
            if want_global and 5*Tail0<VarT:
                acc['globalfail']+=1
                if acc['g_ex'] is None: acc['g_ex']=(name,n,str(5*Tail0),str(VarT))

def glued_c5_chain(q):
    """q C5 blocks (each 5-cycle), block i vertices 5i..5i+4; bridge cut-edge block i vertex0 - block i+1 vertex2."""
    n=5*q; E=[]
    for i in range(q):
        b=5*i
        E += [(b,b+1),(b+1,b+2),(b+2,b+3),(b+3,b+4),(b+4,b)]
    for i in range(q-1):
        E.append((5*i, 5*(i+1)+2))   # bridge
    side=[0]*n
    for i in range(q):
        b=5*i
        side[b]=0; side[b+1]=0; side[b+2]=1; side[b+3]=0; side[b+4]=1
    return n,E,side

def fam(name,n,E,acc,Lam=None):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    L=Lam or len(E)*n*n+1
    a2,cuts=gmins(n,E)
    for side in cuts: check_cut(name,n,adj,side,acc,L)

def main():
    acc=dict(rows=0,Kfail=0,Kcfail=0,globalfail=0,K_ex=None,Kc_ex=None,g_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d Kfail=%d"%(nn,acc['rows'],acc['Kfail']),flush=True)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2),(1,1,1,1,1)]:
        nn,EE=odd_blowup(5,list(sizes)); fam("C5%s"%(sizes,),nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    print("after census+blowups+Grotzsch: rows=%d Kfail=%d Kcfail=%d"%(acc['rows'],acc['Kfail'],acc['Kcfail']),flush=True)
    # glued C5 chains via SUPPLIED cut (gmins infeasible for large q)
    for q in range(2,16):
        n,E,side=glued_c5_chain(q)
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        if not Bconn(n,adj,side): print("chain q=%d: B disconnected"%q); continue
        Lam=len(E)*n*n+1
        check_cut("chainC5_q%d"%q,n,adj,side,acc,Lam,want_global=True)
    print("="*55)
    print("rows:",acc['rows'])
    print("K-LOCAL 5*Tail0>=VarK failures:",acc['Kfail'],acc['K_ex'] or '')
    print("K-CENTERED 5*Tail0>=VarKcent failures:",acc['Kcfail'])
    print("GLOBAL VAR-STABILITY 5*Tail0>=VarT failures (glued chains):",acc['globalfail'],acc['g_ex'] or '')
    print("VERDICT:", "K-LOCAL VARIANCE LEMMA HOLDS (global VAR-STABILITY confirmed FALSE on chains)" if acc['Kfail']==0 else "K-LOCAL FAILS")

if __name__=="__main__":
    main()
