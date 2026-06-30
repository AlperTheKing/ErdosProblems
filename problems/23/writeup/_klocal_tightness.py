"""Probe WHERE the GLOBAL K-local lemma 5*Tail0_N(P) >= Var_N(K(P)) binds.
   For each no-port gamma-min row with Var_N>0, compute exact ratio R = 5*Tail0 / Var_N and absolute
   margin 5*Tail0-Var_N.  Track global min ratio + argmin family.  Dense near-extremal sampling via
   unbalanced C5 blow-ups C5[a,b,c,d,e] (the stability direction off the uniform-load extremal).
   If min ratio -> 1 on a specific near-C5[t] family, THAT is the binding case a stability proof must nail.
   Exact Fraction.
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
            K=Kcomp(n,M,cyc,set(P))
            VarN=sum((T[v]-N)**2 for v in K)
            acc['rows']+=1
            if VarN==0:
                acc['var0']+=1
                if Tail0<0: acc['atomfail']+=1
                return_check=Tail0  # uniform-load: atom must be >=0
                if Tail0<0 and acc['atom_ex'] is None: acc['atom_ex']=(name,n,tuple(P),str(Tail0))
                continue
            R=F(5)*Tail0/VarN
            marg=5*Tail0-VarN
            if marg<0: acc['fail']+=1
            if acc['minR'] is None or R<acc['minR']:
                acc['minR']=R
                acc['argmin']=(name,n,tuple(P),str(R),float(R),str(5*Tail0),str(VarN),len(K))

def fam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    a2,cuts=gmins(n,E)
    for side in cuts: check_cut(name,n,adj,side,acc,len(E)*n*n+1)

def main():
    acc=dict(rows=0,fail=0,var0=0,atomfail=0,minR=None,argmin=None,atom_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d fail=%d minR=%s(%.4f)"%(nn,acc['rows'],acc['fail'],
              acc['minR'],float(acc['minR']) if acc['minR'] else 0),flush=True)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw",n,E,acc)
    # DENSE near-extremal: unbalanced C5 blow-ups (the stability direction)
    blowups=[(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2),(1,1,1,1,1),(3,2,3,2,3),(3,3,3,3,2),(3,3,3,2,2),
             (2,2,3,2,2),(4,3,4,3,4),(3,2,2,2,2),(2,1,1,1,1),(3,1,3,1,3),(4,4,4,4,3),(2,2,2,2,1)]
    for sizes in blowups:
        nn,EE=odd_blowup(5,list(sizes)); fam("C5%s"%(sizes,),nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    for q in range(2,12):
        n,E,side=glued_c5_chain(q)
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        if Bconn(n,adj,side): check_cut("chain_q%d"%q,n,adj,side,acc,len(E)*n*n+1)
    print("="*55)
    print("total rows:",acc['rows']," Var0(uniform) rows:",acc['var0']," atom<0 on uniform:",acc['atomfail'],acc['atom_ex'] or '')
    print("K-local 5*Tail0>=VarN failures:",acc['fail'])
    print("MIN RATIO 5*Tail0/VarN = %s = %.6f"%(acc['minR'],float(acc['minR'])))
    print("  realized at:",acc['argmin'])

if __name__=="__main__":
    main()
