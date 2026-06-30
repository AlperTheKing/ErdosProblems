"""HARDEN + MECHANISM: SWITCH-GAMMA on a larger violator set (census N<=10 all max cuts + H?AFBo]), AND dump the
switch STRUCTURE per violator to read off the analytic mechanism: which vertex flips, dGamma, whether the flipped
vertex is ON the violating path, its load T[v]-n, its dM-dB margin."""
import subprocess
from itertools import combinations
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side

def cut_size(n,E,side): return sum(1 for x,y in E if side[x]!=side[y])
def struct(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    return sum(T),M,ell,T,cyc

def violating_paths(n,Gamma,M,ell,T,cyc):
    out=[]; slack=F(n*n)-Gamma
    for f in M:
        rhs=F(ell[f])*slack/25
        for P in cyc[f]:
            Ex=sum(T[v]-F(n) for v in P)
            if Ex>rhs: out.append((f,P,Ex,rhs))
    return out

def test_graph(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj)
    if not cuts: return
    maxcut=cut_size(n,E,cuts[0])
    for side in cuts:
        if not Bconn(n,adj,side): continue
        s=struct(n,adj,side)
        if s is None: continue
        Gamma0,M,ell,T,cyc=s
        vp=violating_paths(n,Gamma0,M,ell,T,cyc)
        if not vp: continue
        acc['violators']+=1
        # smallest Gamma-decreasing neutral switch
        found=None
        for k in range(1,5):
            for W in combinations(range(n),k):
                nb=side[:]
                for v in W: nb[v]^=1
                if cut_size(n,E,nb)!=maxcut: continue
                if not Bconn(n,adj,nb): continue
                s2=struct(n,adj,nb)
                if s2 is None: continue
                if s2[0]<Gamma0: found=(k,W,s2[0]); break
            if found: break
        if found is None:
            acc['noswitch']+=1
            if acc['fnoswitch'] is None: acc['fnoswitch']=(name,n,str(Gamma0))
            continue
        k,W,g=found
        acc['ksizes'][k]=acc['ksizes'].get(k,0)+1
        # mechanism: is flipped vertex on a violating path? its load excess? dM-dB margin?
        if len(acc['dump'])<14:
            f,P,Ex,rhs=vp[0]
            winfo=[]
            for v in W:
                dM=sum(1 for w in adj[v] if side[w]==side[v]); dB=len(adj[v])-dM
                onpath = v in set().union(*[set(Q) for Q in cyc[f]])
                winfo.append((v,'onP' if v in P else ('onbundle' if onpath else 'off'),str(T[v]-F(n)),'dM=%d dB=%d'%(dM,dB)))
            acc['dump'].append((name,n,str(Gamma0),str(g),k,list(W),winfo,str(Ex),str(rhs)))

if __name__=="__main__":
    acc=dict(violators=0,noswitch=0,fnoswitch=None,ksizes={},dump=[])
    n,E=dec('H?AFBo]'); test_graph('H?AFBo]',n,E,acc)
    for nn in range(5,11):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); test_graph('cen%s'%g6,n,E,acc)
        print("  census N=%d done (violators=%d noswitch=%d ksizes=%s)"%(nn,acc['violators'],acc['noswitch'],acc['ksizes']),flush=True)
    print("\n  SWITCH-GAMMA HARDENED: violators=%d  with Gamma-decreasing switch |W|<=4: %d  WITHOUT: %d %s"%(
        acc['violators'],acc['violators']-acc['noswitch'],acc['noswitch'],acc['fnoswitch'] or ''),flush=True)
    print("  switch sizes: %s"%acc['ksizes'],flush=True)
    print("  MECHANISM dumps (name,N,Gamma0,Gamma_after,|W|,W,[vertex info: pos,T-n,degs],Ex,rhs):",flush=True)
    for d in acc['dump']: print("    %s"%(d,),flush=True)
    print("  === SWITCH-GAMMA %s ==="%("HOLDS (all violators have a small Gamma-decreasing switch)" if acc['noswitch']==0 else "has %d switch-less violators"%acc['noswitch']),flush=True)
