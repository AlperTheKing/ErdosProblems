"""Gate Codex 413 K-LOCAL RECOMBINATION (reduces K-local lemma to intrinsic single-component target).
   C=K(P) positive-K component, m=|C|, Gamma_C=sum_{g: cyc[g] subset C} ell_g^2.
   Var_N(C)=sum_{v in C}(T(v)-N)^2; Var_m(C)=sum_{v in C}(T(v)-m)^2.  S_P=sum_{x in P}T(x).
   h_i^C=T(x_i)/m; C_m(P)=(sum_i h_i^C)^2 - L^2 min_i h_i^C h_{i+1}^C.
   B_C(P)=L*(m^2-Gamma_C) - 25*(S_P-L*m) - C_m(P).
   RECOMBINATION:  5*Tail0_N(P) - Var_N(C) >= 5*B_C(P) - Var_m(C).
   Then K-local <= intrinsic 5*B_C>=Var_m.  Also check single-component (C=whole loaded support): Tail0_N=B_C.
   gamma-min no-port rows + glued chains.  Exact Fraction.
"""
import subprocess
from fractions import Fraction as F
from collections import deque
from _Klocal_gate import glued_c5_chain
from _singleton_core import ell_map, Hi_and_best
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, mycielski

def Kcomp(n,M,cyc,Pset):
    adjK=[set() for _ in range(n)]
    geo_in={}
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

def check_cut(name,n,adj,side,acc,Lam):
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    if not M: return
    N=F(n)
    for f in M:
        L=ell[f]
        if L%2==0: continue
        for P in cyc[f]:
            if len(P)!=L: continue
            noport=True; em0=ell_map(n,adj,side)
            for i in range(L):
                Hi,W,d=Hi_and_best(n,adj,side,em0,P,i,Lam)
                if Hi is not None and Hi<0: noport=False; break
            if not noport: continue
            _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
            Tail0=sum((2*r+1)*Z[r] for r in range(n))
            C=Kcomp(n,M,cyc,set(P)); m=F(len(C))
            # Gamma_C: bad edges whose geodesics lie within C
            GammaC=0
            for g in M:
                inC=any(set(Q)<=C for Q in cyc[g])
                if inC: GammaC+=ell[g]**2
            VarN=sum((T[v]-N)**2 for v in C)
            Varm=sum((T[v]-m)**2 for v in C)
            S_P=sum(T[P[i]] for i in range(L))
            hC=[T[P[i]]/m for i in range(L)]
            C_m=(sum(hC))**2 - (L*L)*min(hC[i]*hC[(i+1)%L] for i in range(L))
            B_C=L*(m*m-GammaC) - 25*(S_P-L*m) - C_m
            acc['rows']+=1
            lhs=5*Tail0-VarN; rhs=5*B_C-Varm
            if lhs<rhs:
                acc['fail']+=1
                if acc['ex'] is None: acc['ex']=(name,n,tuple(P),len(C),str(GammaC),str(5*Tail0),str(B_C),str(VarN),str(Varm))
            if len(C)==n:   # single full component
                acc['single']+=1
                if Tail0!=B_C: acc['single_neq']+=1

def fam(name,n,E,acc):
    adj,cuts=gmins(n,E)
    for side in cuts: check_cut(name,n,adj,side,acc,len(E)*n*n+1)

def main():
    acc=dict(rows=0,fail=0,single=0,single_neq=0,ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d fail=%d single=%d single_neq=%d"%(nn,acc['rows'],acc['fail'],acc['single'],acc['single_neq']),flush=True)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2),(1,1,1,1,1)]:
        nn,EE=odd_blowup(5,list(sizes)); fam("C5%s"%(sizes,),nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    # glued chains supplied cut
    for q in range(2,16):
        n,E,side=glued_c5_chain(q)
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        if Bconn(n,adj,side): check_cut("chain_q%d"%q,n,adj,side,acc,len(E)*n*n+1)
    print("="*55)
    print("rows:",acc['rows'])
    print("RECOMBINATION 5*Tail0-VarN >= 5*B_C-Varm failures:",acc['fail'],acc['ex'] or '')
    print("single-component rows:",acc['single']," with Tail0 != B_C:",acc['single_neq'])
    print("VERDICT:", "RECOMBINATION HOLDS => K-local <= intrinsic single-component 5*B_C>=Varm" if acc['fail']==0 else "FAILS")

if __name__=="__main__":
    main()
