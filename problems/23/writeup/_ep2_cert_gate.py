"""Gate Codex 400 / GPT-Pro ENDPOINT-PAIR C5-shadow switch certificate for (A) (fixes failed one-color PF-A).
   Fold(P): rho on path indices with C5-edge constraint (rho(i+1)-rho(i) in {1,4} mod5, rho(0)-rho(L-1) in {1,4}).
   A_rho={rho[0],rho[L-1]} (an edge of C5). Trace: x_i in U iff rho[i] in A_rho (endpoint-pair density 2/5).
   Completion over B-comps C, Att_rho(C)={rho[i]: x_i has B-nbr in C}: Att subset A_rho->all; disjoint->none;
   else one bipartition side (tau). Disconnected B^U forbidden.
   K_EP2 = min_{rho,tau,connected}[ Lambda*mu(U)+DeltaGamma(U) ], Lambda=|E|N^2+1.
   TEST  R_EP2 := Lambda*(D_all-(5/L)*Tax0) - K_EP2 >= 0.  (R_EP2>=0 + gamma-min => K_EP2>=0 => A.)
   gamma-min rows, exact Fraction.  Compare cen7 P=(4,0,6,2,5) (the PF-A failure).
"""
import subprocess, itertools
from fractions import Fraction as F
from _crux_extract import components_off_path
from _singleton_core import ell_map
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import deltas, flip, gamma_of, odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, mycielski

CAP=1<<14

def f5_maps(L):
    res=[]
    for start in range(5):
        for steps in itertools.product((1,4),repeat=L-1):
            rho=[start]
            for s in steps: rho.append((rho[-1]+s)%5)
            if (rho[0]-rho[-1])%5 in (1,4): res.append(tuple(rho))
    return res

def comp_info(n,adj,side,P,rho):
    Pset=set(P); comps=components_off_path(n,adj,side,Pset); info=[]
    for C in comps:
        att=set()
        for v in C:
            for w in adj[v]:
                if w in Pset and side[w]!=side[v]: att.add(rho[P.index(w)])
        col={}; stk=[next(iter(C))]; col[stk[0]]=0
        while stk:
            u=stk.pop()
            for w in adj[u]:
                if w in C and side[w]!=side[u] and w not in col: col[w]=col[u]^1; stk.append(w)
        cls0={v for v in C if col.get(v,0)==0}; cls1={v for v in C if col.get(v,0)==1}
        info.append((C,att,cls0,cls1))
    return info

def K_EP2(n,adj,side,P,Gamma,Lam):
    L=len(P); best=None; cnt=0
    for rho in f5_maps(L):
        Arho={rho[0],rho[-1]}
        info=comp_info(n,adj,side,P,rho)
        straddlers=[]
        for (C,att,c0,c1) in info:
            if not att: continue
            if att<=Arho: pass
            elif att & Arho: straddlers.append((c0,c1))
        base={P[i] for i in range(L) if rho[i] in Arho}
        forced=set(base)
        for (C,att,c0,c1) in info:
            if att and att<=Arho: forced|=C
        taus=[()] if not straddlers else itertools.product((0,1),repeat=len(straddlers))
        for tau in taus:
            cnt+=1
            if cnt>CAP: break
            W=set(forced)
            for si,pick in enumerate(tau): W|=(straddlers[si][0] if pick==0 else straddlers[si][1])
            if not W or len(W)==n: continue
            s2=flip(side,list(W))
            if not Bconn(n,adj,s2): continue
            g1=gamma_of(n,adj,s2)
            if g1 is None: continue
            dB,dM=deltas(n,adj,side,W); mu=dB-dM
            val=Lam*mu+(g1-Gamma)
            if best is None or val<best: best=val
        if cnt>CAP: break
    return best

def run(name,n,adj,E,cuts,acc):
    Lam=len(E)*n*n+1
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        N=F(n); Gamma=sum(ell[g]**2 for g in M)
        for f in M:
            L=ell[f]
            if L%2==0: continue
            for P in cyc[f]:
                if len(P)!=L: continue
                h=[T[P[i]]/N for i in range(L)]; S=sum(h); q=min(h[i]*h[(i+1)%L] for i in range(L))
                C_L=((S/L)**2-q)*L*L
                chiP=[0]*n
                for end in (P[0],P[-1]):
                    ch=endpt_chi(n,adj,side,end,M,n)
                    for r in range(n): chiP[r]+=ch[r]
                E0=sum((2*r+1)*chiP[r] for r in range(n))
                D_all=N*N-Gamma; Tax0=E0+C_L
                K=K_EP2(n,adj,side,P,Gamma,Lam)
                acc['rows']+=1
                if K is None:
                    acc['noK']+=1; continue
                R=Lam*(D_all-F(5,L)*Tax0)-K
                if R<0:
                    acc['fail']+=1
                    if acc['ex'] is None: acc['ex']=(name,n,tuple(P),str(K),str(D_all-F(5,L)*Tax0),str(R))

def fam(name,n,E,acc):
    adj,cuts=gmins(n,E); run(name,n,adj,E,cuts,acc)

def main():
    acc=dict(rows=0,noK=0,fail=0,ex=None)
    for nn in range(5,10):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: rows=%d noK=%d fail=%d"%(nn,acc['rows'],acc['noK'],acc['fail']),flush=True)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2)]:
        nn,EE=odd_blowup(5,list(sizes)); fam("C5%s"%(sizes,),nn,EE,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    print("="*55)
    print("rows:",acc['rows']," no-K(no valid EP2 switch):",acc['noK'])
    print("R_EP2<0 failures:",acc['fail'],acc['ex'] or '')
    ok=(acc['fail']==0 and acc['noK']==0)
    print("VERDICT:", "EP2 CERTIFICATE FEASIBLE (R_EP2>=0) => gamma-min PROVES (A)" if ok else "FAILS")

if __name__=="__main__":
    main()
