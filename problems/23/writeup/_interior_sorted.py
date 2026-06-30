"""Answer Codex 427 logic-check: for INTERIOR NEUTRAL singleton completions (0<i<L-1, mu=0), report the sorted
   length-comparison DIRECTION and whether retained-edge terms are essential.
   Per neutral interior W: added lengths A, removed lengths B (|A|=|B|? record), retained (old->new) pairs.
   Check:  sorted(A) >= sorted(B) componentwise (Codex's interior invariant)?  retained new>=old (nondecrease)?
           DeltaGamma_no_ret = sumA^2 - sumB^2 ;  DeltaGamma = that + sum(new^2-old^2).
   Report how DeltaGamma>=0 is achieved (added/removed alone vs retained essential).  Exact.
"""
import subprocess, random
import _crux_extract as cx
from _singleton_core import ell_map, singleton_completions
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
                for i in range(1,L-1):
                    for W in singleton_completions(n,adj,side,P,i):
                        if not W: continue
                        s2=flip(side,W)
                        if not Bconn(n,adj,s2): continue
                        g1=gamma_of(n,adj,s2)
                        if g1 is None: continue
                        dB,dM=deltas(n,adj,side,W)
                        if dB-dM!=0: continue   # neutral only
                        em1=ell_map(n,adj,s2)
                        k0=set(em0);k1=set(em1);added=k1-k0;removed=k0-k1;ret=k0&k1
                        A=sorted(em1[e] for e in added); B=sorted(em0[g] for g in removed)
                        retpairs=[(em0[h],em1[h]) for h in ret if em0[h]!=em1[h]]
                        acc['neutral']+=1
                        # direction checks
                        addge = (len(A)==len(B)) and all(a>=b for a,b in zip(A,B))
                        addle = (len(A)==len(B)) and all(a<=b for a,b in zip(A,B))
                        if addge: acc['added_ge_removed']+=1
                        if addle: acc['added_le_removed']+=1
                        if len(A)!=len(B): acc['card_ne']+=1
                        retdec=any(nw<od for od,nw in retpairs)
                        retinc=any(nw>od for od,nw in retpairs)
                        if retdec: acc['ret_dec']+=1
                        if retpairs: acc['has_ret']+=1
                        dG_noret=sum(a*a for a in A)-sum(b*b for b in B)
                        dG=g1-Gamma
                        if dG_noret<0: acc['noret_neg']+=1  # added/removed alone would drop Gamma (retained essential)
                        # record a sample
                        if acc['sample'] is None and retpairs:
                            acc['sample']=(name,tuple(P),i,A,B,retpairs,str(dG_noret),str(dG))
                        if acc['sample_noret'] is None and not retpairs:
                            acc['sample_noret']=(name,tuple(P),i,A,B,str(dG))

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
    acc=dict(neutral=0,added_ge_removed=0,added_le_removed=0,card_ne=0,ret_dec=0,has_ret=0,noret_neg=0,
             sample=None,sample_noret=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
    n,E=dec("H?AFBo]"); fam("thw",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3)]:
        n,E=odd_blowup(5,list(sizes))
        if n<=13: fam("blow",n,E,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    n,E=mycielski(grN,grE); adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): fam("Myc23",n,E,acc,cuts=[side])
    print("="*55)
    print("NEUTRAL interior completions:",acc['neutral'])
    print("  sorted(added) >= sorted(removed) componentwise:",acc['added_ge_removed'])
    print("  sorted(added) <= sorted(removed) componentwise:",acc['added_le_removed'])
    print("  |added| != |removed|:",acc['card_ne'])
    print("  with retained length-change:",acc['has_ret']," of which retained DECREASES:",acc['ret_dec'])
    print("  added/removed-only DeltaGamma<0 (retained ESSENTIAL to keep >=0):",acc['noret_neg'])
    print("  sample (with retained):",acc['sample'])
    print("  sample (no retained):",acc['sample_noret'])

if __name__=="__main__":
    main()
