"""Exact-verify Codex 414 counterexample: naive intrinsic target 5*B_C>=Var_m is FALSE.
   Witness g6=H?AFBo], find gamma-min cut whose bad-edge row P=(1,6,8,3,7) has K(P) with Gamma_C>m^2.
   Confirm: (a) 5*B_C-Var_m < 0  (intrinsic target FALSE),
            (b) recombination 5*Tail0_N-Var_N >= 5*B_C-Var_m  (still holds),
            (c) global K-local 5*Tail0_N >= Var_N  (still holds).
   Exact Fraction.
"""
from fractions import Fraction as F
from collections import deque
from _singleton_core import ell_map, Hi_and_best
from _h import dec
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _stark1 import gmins

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

def analyze(n,adj,side,Lam):
    st=struct_for_side(n,adj,side)
    if st is None: return []
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    if not M: return []
    N=F(n); out=[]
    for f in M:
        L=ell[f]
        if L%2: pass
        else: continue
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
            VarN=sum((T[v]-N)**2 for v in C)
            Varm=sum((T[v]-m)**2 for v in C)
            S_P=sum(T[P[i]] for i in range(L))
            hC=[T[P[i]]/m for i in range(L)]
            C_m=(sum(hC))**2 - (L*L)*min(hC[i]*hC[(i+1)%L] for i in range(L))
            B_C=L*(m*m-GammaC) - 25*(S_P-L*m) - C_m
            out.append(dict(P=tuple(P),C=sorted(C),m=int(m),GammaC=int(GammaC),
                            Tail0=Tail0,VarN=VarN,Varm=Varm,B_C=B_C,
                            Tsorted=sorted(int(T[v]) for v in C),
                            intrinsic=5*B_C-Varm, recomb=(5*Tail0-VarN)-(5*B_C-Varm),
                            klocal=5*Tail0-VarN, badedges=sorted(M)))
    return out

def main():
    g6="H?AFBo]"; n,E=dec(g6)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    Lam=len(E)*n*n+1
    _,cuts=gmins(n,E)
    hits=0
    worst_intr=None
    for side in cuts:
        for d in analyze(n,adj,side,Lam):
            if d['intrinsic']<0:
                hits+=1
                if worst_intr is None or d['intrinsic']<worst_intr['intrinsic']:
                    worst_intr=d
            if d['P']==(1,6,8,3,7) or d['P']==(7,3,8,6,1):
                print("=== MATCHED Codex witness row P=(1,6,8,3,7) ===")
                for k in ['P','C','m','GammaC','Tsorted','badedges']: print("  %s=%s"%(k,d[k]))
                print("  B_C = %s"%d['B_C'])
                print("  Var_m = %s"%d['Varm'])
                print("  5*B_C - Var_m = %s  (intrinsic target; <0 => FALSE)"%d['intrinsic'])
                print("  5*Tail0_N = %s , Var_N = %s"%(5*d['Tail0'],d['VarN']))
                print("  global K-local 5*Tail0_N - Var_N = %s  (>=0 => holds)"%d['klocal'])
                print("  recombination (5*Tail0-VarN)-(5*B_C-Varm) = %s  (>=0 => holds)"%d['recomb'])
    print("="*55)
    print("intrinsic-target failures (5*B_C<Var_m) on H?AFBo] gamma-min rows:",hits)
    if worst_intr: print("worst intrinsic margin:",worst_intr['intrinsic']," at P=",worst_intr['P']," GammaC=",worst_intr['GammaC']," m=",worst_intr['m'])

if __name__=="__main__":
    main()
