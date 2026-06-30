"""Gate Codex 426 INTERIOR-NEUTRAL NONDECREASE lemma (proof of (C) NPort subset endpoints):
   For every INTERIOR index 0<i<L-1 of a row P, and EVERY singleton_completion W (not just minimizer) with
   switched-B connected + struct valid and mu=delta_B(W)-delta_M(W)==0, we have DeltaGamma(W) >= 0.
   => no interior negative port (H_i<0 forces mu=0 and DeltaGamma=H_i<0, contradiction).
   Also report the weaker minimizer form: min_W [Lambda*mu+DeltaGamma] >= 0 for interior i.
   Full battery + random N=11/12.  Exact.
"""
import subprocess, random
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best, singleton_completions
from _wf_deficit_farkas import deltas, flip, gamma_of, odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, mycielski, is_triangle_free

def scan(name,n,adj,E,cuts,acc):
    Lam=len(E)*n*n+1
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        Gamma=sum(T); em0=ell_map(n,adj,side)
        for f in M:
            if ell[f]%2==0: continue
            for P in cyc[f]:
                if len(P)!=ell[f]: continue
                L=len(P)
                for i in range(1,L-1):  # interior only
                    minc=None
                    for W in singleton_completions(n,adj,side,P,i):
                        if not W: continue
                        s2=flip(side,W)
                        if not Bconn(n,adj,s2): continue
                        g1=gamma_of(n,adj,s2)
                        if g1 is None: continue
                        dB,dM=deltas(n,adj,side,W); mu=dB-dM; dG=g1-Gamma
                        acc['comp']+=1
                        if mu==0:
                            acc['neutral']+=1
                            if dG<0:
                                acc['fail']+=1
                                if acc['ex'] is None: acc['ex']=(name,n,''.join(map(str,side)),f,tuple(P),i,str(dG))
                        c=Lam*mu+dG
                        if minc is None or c<minc: minc=c
                    if minc is not None and minc<0:
                        acc['minfail']+=1
                        if acc['minex'] is None: acc['minex']=(name,tuple(P),i,str(minc))

def fam(name,n,E,acc,cuts=None):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    if cuts is None: _,cuts=cx.all_max_cuts(n,adj,E)
    scan(name,n,adj,E,cuts,acc)

def maxcut_ls(n,adj,seeds=60):
    best=None;bv=-1;rng=random.Random(9)
    for _ in range(seeds):
        s=[rng.randint(0,1) for _ in range(n)];imp=True
        while imp:
            imp=False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w]==s[v])>sum(1 for w in adj[v] if s[w]!=s[v]):s[v]^=1;imp=True
        val=sum(1 for v in range(n) for w in adj[v] if w>v and s[v]!=s[w])
        if val>bv:bv=val;best=s[:]
    return best

def main():
    acc=dict(comp=0,neutral=0,fail=0,minfail=0,ex=None,minex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: comp=%d neutral=%d fail=%d minfail=%d"%(nn,acc['comp'],acc['neutral'],acc['fail'],acc['minfail']),flush=True)
    n,E=dec("H?AFBo]"); fam("thw",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3)]:
        n,E=odd_blowup(5,list(sizes))
        if n<=13: fam("blow",n,E,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    n,E=mycielski(grN,grE); adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): fam("Myc23",n,E,acc,cuts=[side])
    rng=random.Random(13); made=0; tries=0
    while made<100 and tries<40000:
        tries+=1
        nn=rng.choice([11,12]); p=rng.uniform(0.14,0.34)
        E=[(a,b) for a in range(nn) for b in range(a+1,nn) if rng.random()<p]
        if not E or not is_triangle_free(nn,E): continue
        adj=[set() for _ in range(nn)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        if any(len(adj[v])==0 for v in range(nn)): continue
        made+=1; fam("rand%d"%made,nn,E,acc)
    print("="*55)
    print("interior singleton completions:",acc['comp']," neutral(mu=0):",acc['neutral']," random N11/12:",made)
    print("INTERIOR NEUTRAL NONDECREASE (mu=0 => DeltaGamma>=0) failures:",acc['fail'],acc['ex'] or '')
    print("weaker minimizer (min Lambda*mu+dG >=0 interior) failures:",acc['minfail'],acc['minex'] or '')
    print("VERDICT:", "INTERIOR NONDECREASE HOLDS => no interior negative port" if acc['fail']==0 else "FAILS (interior neutral Gamma-decrease exists)")

if __name__=="__main__":
    main()
