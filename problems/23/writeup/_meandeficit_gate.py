"""Gate Codex 415 mean-deficit split of K-local.  C=K(P), m=|C|, mean_C=Gamma_C/m=(1/m)sum_{v in C}T(v).
   Variance decomposition (exact):  Var_N(C) = m*(N-mean_C)^2 + VarKc,  VarKc=sum_{v in C}(T(v)-mean_C)^2.
   Gate:
     (a) STRUCTURAL  Gamma_C <= m*N            (component average load <= N)
     (b) MEAN-DEFICIT  5*Tail0 >= m*(N-mean_C)^2  = (m*N-Gamma_C)^2/m
     (c) RESIDUAL CENTERED  5*Tail0 - m*(N-mean_C)^2 >= VarKc   (== full K-local, since Var_N splits)
   Note mean_C uses Gamma_C = sum over bad edges with geodesics in C (NOT sum_{v in C}T(v) if some v in C
   carry load from bad edges leaving C); verify mean_C=Gamma_C/m matches sum_{v in C}T(v)/m on these rows.
   Full K-local battery.  Exact Fraction.
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
from _bdef_construct import Cn, mycielski
from _Klocal_gate import glued_c5_chain

def Kcomp(n,M,cyc,Pset):
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
            em0=ell_map(n,adj,side); noport=True
            for i in range(L):
                Hi,W,d=Hi_and_best(n,adj,side,em0,P,i,Lam)
                if Hi is not None and Hi<0: noport=False; break
            if not noport: continue
            _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
            Tail0=sum((2*r+1)*Z[r] for r in range(n))
            C=Kcomp(n,M,cyc,set(P)); m=F(len(C))
            GammaC=0
            for g in M:
                if any(set(Q)<=C for Q in cyc[g]): GammaC+=ell[g]**2
            sumT_C=sum(T[v] for v in C)
            mean_C=GammaC/m
            acc['rows']+=1
            # consistency: Gamma_C vs sum_{v in C}T(v)
            if GammaC!=sumT_C: acc['gamma_ne_sumT']+=1
            # (a) structural
            if GammaC> m*N: acc['a_fail']+=1
            if acc['a_min'] is None or (m*N-GammaC)<acc['a_min']: acc['a_min']=m*N-GammaC
            # (b) mean-deficit
            meandef=m*(N-mean_C)**2
            if 5*Tail0 < meandef:
                acc['b_fail']+=1
                if acc['b_ex'] is None: acc['b_ex']=(name,n,tuple(P),str(5*Tail0),str(meandef))
            # (c) residual centered (= full K-local)
            VarKc=sum((T[v]-mean_C)**2 for v in C)
            resid=5*Tail0-meandef
            if resid<VarKc:
                acc['c_fail']+=1
                if acc['c_ex'] is None: acc['c_ex']=(name,n,tuple(P),str(resid),str(VarKc))
            # tightness of (b): track min ratio 5*Tail0/meandef when meandef>0
            if meandef>0:
                Rb=5*Tail0/meandef
                if acc['b_minR'] is None or Rb<acc['b_minR']:
                    acc['b_minR']=Rb; acc['b_argmin']=(name,n,float(Rb))

def fam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    a2,cuts=gmins(n,E)
    for side in cuts: check_cut(name,n,adj,side,acc,len(E)*n*n+1)

def main():
    acc=dict(rows=0,gamma_ne_sumT=0,a_fail=0,a_min=None,b_fail=0,b_ex=None,c_fail=0,c_ex=None,
             b_minR=None,b_argmin=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d a_fail=%d b_fail=%d c_fail=%d"%(nn,acc['rows'],acc['a_fail'],acc['b_fail'],acc['c_fail']),flush=True)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2),(1,1,1,1,1),(3,2,3,2,3),(3,3,3,3,2),(2,2,3,2,2),(4,3,4,3,4)]:
        nn,EE=odd_blowup(5,list(sizes)); fam("C5%s"%(sizes,),nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    for q in range(2,16):
        n,E,side=glued_c5_chain(q)
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        if Bconn(n,adj,side): check_cut("chain_q%d"%q,n,adj,side,acc,len(E)*n*n+1)
    print("="*55)
    print("total rows:",acc['rows'])
    print("Gamma_C != sum_{v in C}T(v) rows:",acc['gamma_ne_sumT'])
    print("(a) STRUCTURAL Gamma_C<=m*N failures:",acc['a_fail']," (min slack m*N-Gamma_C =",acc['a_min'],")")
    print("(b) MEAN-DEFICIT 5*Tail0>=m*(N-mean_C)^2 failures:",acc['b_fail'],acc['b_ex'] or '')
    print("    (b) min ratio 5*Tail0/meandef:",float(acc['b_minR']) if acc['b_minR'] else None,acc['b_argmin'])
    print("(c) RESIDUAL CENTERED (==K-local) failures:",acc['c_fail'],acc['c_ex'] or '')
    print("VERDICT:", "MEAN-DEFICIT SPLIT HOLDS" if acc['a_fail']==acc['b_fail']==acc['c_fail']==0 else "SOME FAIL")

if __name__=="__main__":
    main()
