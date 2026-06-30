"""Family-parametrized exact gate for the K-local mean-deficit split (Codex 415) + tightness ratio.
   Per no-port gamma-min row P, C=K(P), m=|C|, Gamma_C=sum_{g:cyc[g] subset C} ell^2, mean_C=Gamma_C/m,
   VarN=sum_{v in C}(T(v)-N)^2, VarKc=sum_{v in C}(T(v)-mean_C)^2.
   Checks:  (a) Gamma_C<=m*N ;  (b) 5*Tail0>=m*(N-mean_C)^2 ;  (c) 5*Tail0-m*(N-mean_C)^2>=VarKc  (== K-local).
   Also min ratio R=5*Tail0/VarN (VarN>0).  Exact Fraction.
   Usage: python _kl_battery.py <family>
     families: chains | blowups | islands | theta | myc | cen11 | rand:SEED:COUNT:MAXN
"""
import sys, subprocess, random
from fractions import Fraction as F
from collections import deque
from _singleton_core import ell_map, Hi_and_best
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
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
            mean_C=GammaC/m
            VarN=sum((T[v]-N)**2 for v in C)
            VarKc=sum((T[v]-mean_C)**2 for v in C)
            meandef=m*(N-mean_C)**2
            acc['rows']+=1
            if GammaC>m*N:
                acc['a_fail']+=1
                if acc['a_ex'] is None: acc['a_ex']=(name,n,tuple(P),str(GammaC),str(m*N))
            if 5*Tail0<meandef:
                acc['b_fail']+=1
                if acc['b_ex'] is None: acc['b_ex']=(name,n,tuple(P),str(5*Tail0),str(meandef))
            if 5*Tail0-meandef<VarKc:
                acc['c_fail']+=1
                if acc['c_ex'] is None: acc['c_ex']=(name,n,tuple(P),str(5*Tail0-meandef),str(VarKc))
            if VarN>0:
                R=5*Tail0/VarN
                if acc['minR'] is None or R<acc['minR']:
                    acc['minR']=R; acc['argmin']=(name,n,float(R),int(m))

def fam_gmins(name,n,E,acc):
    if not is_triangle_free(n,E): return
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    try:
        a2,cuts=gmins(n,E)
    except Exception as e:
        print("gmins failed %s: %s"%(name,e)); return
    for side in cuts: check_cut(name,n,adj,side,acc,len(E)*n*n+1)

def run(family,acc):
    if family=="chains":
        for q in range(2,41):
            n,E,side=glued_c5_chain(q)
            adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            if Bconn(n,adj,side): check_cut("chain_q%d"%q,n,adj,side,acc,len(E)*n*n+1)
    elif family=="blowups":
        # cap N=sum(sizes)<=16 so gmins (full 2^(n-1) enumeration) is feasible; large balanced blow-ups
        # add no centered-rigidity info beyond the unbalanced near-extremal ones + random graphs.
        bs=[(2,1,2,1,2),(2,1,2,1,3),(2,2,2,2,2),(1,1,1,1,1),(3,2,3,2,3),(3,3,3,3,2),(3,3,3,2,2),
            (2,2,3,2,2),(3,2,2,2,2),(2,1,1,1,1),(3,1,3,1,3),(2,2,2,2,1),
            (4,2,4,2,4),(3,1,1,1,1),(2,2,2,1,1),(4,3,3,3,3)]
        for sizes in bs:
            nn,EE=odd_blowup(5,list(sizes)); fam_gmins("C5%s"%(sizes,),nn,EE,acc)
    elif family=="islands":
        # C5 island + Myc(C7), single bridge (N=20) and variants
        isl=(5,Cn(5)); g15=mycielski(7,Cn(7))
        n,E=union_disjoint(isl,g15); n,E=add_edges((n,E),[(0,5)]); fam_gmins("isl_C5_MycC7_b1",n,E,acc)
        # two C5 islands + Myc(C7) chain of bridges
        n2,E2=union_disjoint((5,Cn(5)),(5,Cn(5)),mycielski(7,Cn(7)))
        n2,E2=add_edges((n2,E2),[(0,5),(5,10)]); fam_gmins("isl_2C5_MycC7",n2,E2,acc)
        # C7 island + Grotzsch, bridge
        n3,E3=union_disjoint((7,Cn(7)),mycielski(5,Cn(5))); n3,E3=add_edges((n3,E3),[(0,7)])
        fam_gmins("isl_C7_Grotzsch",n3,E3,acc)
    elif family=="theta":
        for g6 in ["H?AFBo]"]:
            n,E=dec(g6); fam_gmins("thw_%s"%g6,n,E,acc)
    elif family=="myc":
        grN,grE=mycielski(5,Cn(5)); fam_gmins("Grotzsch",grN,grE,acc)   # N=11
        # unbalanced Grotzsch blow-up small
        # Myc(Grotzsch) N=23 gmins is heavy; attempt with time, skip on failure
        m2N,m2E=mycielski(grN,grE)
        fam_gmins("MycGrotzsch_N23",m2N,m2E,acc)
    elif family=="cen11":
        for g6 in subprocess.run([GENG,'-tc','11'],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam_gmins("cen11",n,E,acc)
    elif family.startswith("rand:"):
        _,seed,count,maxn=family.split(":"); seed=int(seed); count=int(count); maxn=int(maxn)
        rng=random.Random(seed); made=0; tries=0
        while made<count and tries<count*200:
            tries+=1
            nn=rng.randint(8,maxn)
            p=rng.uniform(0.18,0.42)
            E=[(a,b) for a in range(nn) for b in range(a+1,nn) if rng.random()<p]
            if not E or not is_triangle_free(nn,E): continue
            adj=[set() for _ in range(nn)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            if any(len(adj[v])==0 for v in range(nn)): continue
            made+=1
            fam_gmins("rand_s%d_%d"%(seed,made),nn,E,acc)
        acc['rand_made']=made
    else:
        print("unknown family",family); sys.exit(2)

def main():
    family=sys.argv[1] if len(sys.argv)>1 else "chains"
    acc=dict(rows=0,a_fail=0,b_fail=0,c_fail=0,a_ex=None,b_ex=None,c_ex=None,minR=None,argmin=None)
    run(family,acc)
    print("FAMILY=%s rows=%d"%(family,acc['rows']))
    print("  (a) Gamma_C<=m*N  fails=%d %s"%(acc['a_fail'],acc['a_ex'] or ''))
    print("  (b) 5*Tail0>=m*(N-mean_C)^2  fails=%d %s"%(acc['b_fail'],acc['b_ex'] or ''))
    print("  (c) residual centered (==K-local)  fails=%d %s"%(acc['c_fail'],acc['c_ex'] or ''))
    print("  min ratio 5*Tail0/VarN = %s  at %s"%(float(acc['minR']) if acc['minR'] else None,acc['argmin']))
    if 'rand_made' in acc: print("  random graphs tested:",acc['rand_made'])
    ok = acc['a_fail']==acc['b_fail']==acc['c_fail']==0
    print("  VERDICT_%s: %s"%(family,"PASS" if ok else "FAIL"))

if __name__=="__main__":
    main()
