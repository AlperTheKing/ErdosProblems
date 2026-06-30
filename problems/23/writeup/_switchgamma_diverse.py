"""HARDEN SWITCH-GAMMA with DIVERSE violators (not just H?AFBo]). Generate non-gamma-min max cuts of structured
graphs by neutral flips from the gamma-min cut, find PATH-GAMMA violators, test for a Gamma-decreasing neutral
switch. Report ALSO dGamma vs the violation margin (Codex's KKT question)."""
from itertools import combinations
from fractions import Fraction as F
from _h import Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane

def cut_size(n,E,side): return sum(1 for x,y in E if side[x]!=side[y])
def struct(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    return sum(T),M,ell,T,cyc
def worst_violation(n,Gamma,M,ell,T,cyc):
    slack=F(n*n)-Gamma; worst=None
    for f in M:
        rhs=F(ell[f])*slack/25
        for P in cyc[f]:
            Ex=sum(T[v]-F(n) for v in P)
            v=Ex-rhs
            if v>0 and (worst is None or v>worst): worst=v
    return worst  # >0 means violation amount

def neutral_maxcuts_near(n,E,adj,base,maxcut,radius=2):
    seen=set(); out=[]
    btup=tuple(base)
    # single + pair neutral flips that stay max
    cand=[base]
    for k in range(1,radius+1):
        for W in combinations(range(n),k):
            nb=base[:]
            for v in W: nb[v]^=1
            if cut_size(n,E,nb)==maxcut and Bconn(n,adj,nb):
                t=tuple(nb)
                if t not in seen: seen.add(t); out.append(nb)
    return out

def find_decr_switch(n,E,adj,side,maxcut,Gamma0):
    for k in range(1,4):
        for W in combinations(range(n),k):
            nb=side[:]
            for v in W: nb[v]^=1
            if cut_size(n,E,nb)!=maxcut: continue
            if not Bconn(n,adj,nb): continue
            s2=struct(n,adj,nb)
            if s2 and s2[0]<Gamma0: return k,W,s2[0]
    return None

def test(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    g=gmins(n,E)
    if not g[1]: return
    adj=g[0]; gcuts=g[1]
    maxcut=cut_size(n,E,gcuts[0])
    for base in gcuts[:2]:
        for side in neutral_maxcuts_near(n,E,adj,base,maxcut,radius=2):
            s=struct(n,adj,side)
            if s is None: continue
            Gamma0,M,ell,T,cyc=s
            wv=worst_violation(n,Gamma0,M,ell,T,cyc)
            if wv is None: continue  # not a violator
            acc['violators']+=1
            res=find_decr_switch(n,E,adj,side,maxcut,Gamma0)
            if res is None:
                acc['noswitch']+=1
                if acc['fnoswitch'] is None: acc['fnoswitch']=(name,n,str(Gamma0),str(wv))
            else:
                k,W,g2=res
                acc['ksizes'][k]=acc['ksizes'].get(k,0)+1
                dG=g2-Gamma0
                if len(acc['kkt'])<12: acc['kkt'].append((name,n,str(dG),str(wv),k))

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def bridge_g(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc=dict(violators=0,noswitch=0,fnoswitch=None,ksizes={},kkt=[])
    for cyc in (5,7,9):
        for t in range(1,5):
            n,E=blowup([t]*cyc)
            if n>22: continue
            test("C%d[%d]"%(cyc,t),n,E,acc)
    for parts in ([2,1,2,1,2],[3,2,3,2,3],[3,1,3,1,3]):
        n,E=blowup(parts)
        if n<=20: test("C5%s"%parts,n,E,acc)
    for nm,(nn,E) in [("Grotzsch",mycielski(5,Cn(5))),("M(C7)",mycielski(7,Cn(7))),
                      ("C7|Grotzsch",bridge_g((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C5|C7",bridge_g((5,Cn(5)),(7,Cn(7)),0,0)),
                      ("C5|C5",bridge_g((5,Cn(5)),(5,Cn(5)),0,0))]:
        test(nm,nn,E,acc)
    for L in (8,12):
        n,E,side,bad=build_two_lane(L)
        # for two-lane use its explicit cut as base
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        maxcut=cut_size(n,E,side)
        for s2 in neutral_maxcuts_near(n,E,adj,side,maxcut,radius=2):
            st=struct(n,adj,s2)
            if st is None: continue
            Gamma0,M,ell,T,cyc=st
            wv=worst_violation(n,Gamma0,M,ell,T,cyc)
            if wv is None: continue
            acc['violators']+=1
            res=find_decr_switch(n,E,adj,s2,maxcut,Gamma0)
            if res is None:
                acc['noswitch']+=1
                if acc['fnoswitch'] is None: acc['fnoswitch']=("twolane%d"%L,n,str(Gamma0),str(wv))
            else: acc['ksizes'][res[0]]=acc['ksizes'].get(res[0],0)+1
    print("  DIVERSE violators (neutral-flip-near-gamma-min on structured graphs)=%d"%acc['violators'])
    print("  with Gamma-decreasing neutral switch |W|<=3: %d ; WITHOUT: %d %s"%(acc['violators']-acc['noswitch'],acc['noswitch'],acc['fnoswitch'] or ''))
    print("  switch sizes: %s"%acc['ksizes'])
    print("  KKT (name,N,dGamma,violation_margin,|W|):")
    for d in acc['kkt']: print("    %s"%(d,))
    print("  === DIVERSE SWITCH-GAMMA %s ==="%("HOLDS (every diverse violator has a small switch)" if acc['noswitch']==0 and acc['violators']>0 else ("no violators found near gamma-min" if acc['violators']==0 else "%d switch-less"%acc['noswitch'])))
