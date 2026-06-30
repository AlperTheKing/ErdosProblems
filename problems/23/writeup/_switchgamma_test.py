"""SWITCH-GAMMA LEMMA test (proof-facing): for each connected-B MAX cut that VIOLATES PATH-GAMMA, does a
NEUTRAL (cut-preserving) Gamma-DECREASING switch W exist? If yes for every violator, the lemma holds and a
gamma-minimal cut cannot violate PATH-GAMMA => PATH-GAMMA => Gamma<=n^2 => beta<=n^2/25.
Search W: single vertices, pairs, triples (and report smallest). EXACT.
PATH-GAMMA: for each bad edge f, path P: sum_{v in P}(T[v]-n) <= (ell_f/25)(n^2-Gamma)."""
import subprocess
from itertools import combinations
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side

def cut_size(n,E,side): return sum(1 for x,y in E if side[x]!=side[y])
def gamma_of(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None,None
    M,ell,T,mu,cyc=st
    return sum(T),(M,ell,T,cyc)

def violates_pathgamma(n,info):
    M,ell,T,cyc=info
    if not M: return False
    Gamma=sum(T); slack=F(n*n)-Gamma
    for f in M:
        rhs=F(ell[f])*slack/25
        for P in cyc[f]:
            Ex=sum(T[v]-F(n) for v in P)
            if Ex>rhs: return True
    return False

def find_gamma_decreasing_switch(n,E,adj,side,maxcut,Gamma0,maxk=3):
    # search neutral (cut-size==maxcut) switch with Gamma < Gamma0
    for k in range(1,maxk+1):
        for W in combinations(range(n),k):
            nb=side[:]
            for v in W: nb[v]^=1
            if cut_size(n,E,nb)!=maxcut: continue
            if not Bconn(n,adj,nb): continue
            g,info=gamma_of(n,adj,nb)
            if g is not None and g<Gamma0:
                return k,W,g
    return None

def test_graph(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj)
    if not cuts: return
    maxcut=cut_size(n,E,cuts[0])
    # info per cut
    data=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        g,info=gamma_of(n,adj,side)
        if g is None: continue
        data.append((g,side,info))
    if not data: return
    for Gamma0,side,info in data:
        if not violates_pathgamma(n,info): continue
        acc['violators']+=1
        res=find_gamma_decreasing_switch(n,E,adj,side,maxcut,Gamma0,maxk=3)
        if res is None:
            acc['noswitch']+=1
            if acc['fnoswitch'] is None: acc['fnoswitch']=(name,n,str(Gamma0))
        else:
            k,W,g=res
            acc['hasswitch']+=1
            acc['ksizes'][k]=acc['ksizes'].get(k,0)+1

if __name__=="__main__":
    acc=dict(violators=0,hasswitch=0,noswitch=0,fnoswitch=None,ksizes={})
    # H?AFBo] (known PATH-GAMMA violator at non-gamma-min cut)
    n,E=dec('H?AFBo]'); test_graph('H?AFBo]',n,E,acc)
    print("  after H?AFBo]: violators=%d hasswitch=%d noswitch=%d ksizes=%s"%(acc['violators'],acc['hasswitch'],acc['noswitch'],acc['ksizes']),flush=True)
    for nn in range(5,10):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); test_graph('cen%s'%g6,n,E,acc)
        print("  census N=%d done (violators=%d hasswitch=%d noswitch=%d)"%(nn,acc['violators'],acc['hasswitch'],acc['noswitch']),flush=True)
    print("\n  SWITCH-GAMMA: PATH-GAMMA-violating max cuts=%d"%acc['violators'],flush=True)
    print("  with a Gamma-decreasing neutral switch (|W|<=3): %d ; WITHOUT: %d %s"%(acc['hasswitch'],acc['noswitch'],acc['fnoswitch'] or ''),flush=True)
    print("  switch sizes |W|: %s"%acc['ksizes'],flush=True)
    if acc['noswitch']==0 and acc['violators']>0:
        print("  === SWITCH-GAMMA HOLDS: every violator has a Gamma-decreasing neutral switch (|W|<=3) ===",flush=True)
    elif acc['noswitch']>0:
        print("  === SWITCH-GAMMA: %d violators have NO small (|W|<=3) Gamma-decreasing switch -- need larger/structured W ==="%acc['noswitch'],flush=True)
