"""Structural check for lemma (B): are ALL negative singleton ports at row ENDPOINTS (index 0 or L-1)?
   If NPort(P) subset {0, L-1} for every row, (B) reduces from L-term to a 2-ENDPOINT-term dominance:
     Tail_k(P) >= Suf_0(k) + Suf_{L-1}(k).
   Report negative ports split by position: endpoint vs interior; flag any interior negative port.
   Full battery (census N<=10 all max cuts + theta + glued + blowups + Grotzsch + Myc23).  Exact Fraction.
"""
import subprocess, random
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, union_disjoint, mycielski

def fam(name,n,E,acc,cuts=None):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    Lam=len(E)*n*n+1
    if cuts is None: _,cuts=cx.all_max_cuts(n,adj,E)
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st[0],st[1],st[2],st[4]
        if not M: continue
        em0=ell_map(n,adj,side)
        for f in M:
            if ell[f]%2==0: continue
            for P in cyc[f]:
                if len(P)!=ell[f]: continue
                L=len(P)
                for i in range(L):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None or Hi>=0: continue
                    acc['ports']+=1
                    if i==0 or i==L-1: acc['endpt']+=1
                    else:
                        acc['interior']+=1
                        if acc['int_ex'] is None: acc['int_ex']=(name,n,''.join(map(str,side)),f,tuple(P),i,str(Hi))

def maxcut_ls(n,adj,seeds=50):
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
    acc=dict(ports=0,endpt=0,interior=0,int_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: ports=%d endpoint=%d interior=%d"%(nn,acc['ports'],acc['endpt'],acc['interior']),flush=True)
    for g6 in ["H?AFBo]"]:
        n,E=dec(g6); fam("thw",n,E,acc)
    n5,E5=5,Cn(5); n7,E7=7,Cn(7)
    for (a,b,br) in [((n5,E5),(n5,E5),[(0,5)]),((n5,E5),(n7,E7),[(0,5)]),((n7,E7),(n5,E5),[(0,7)])]:
        n,E=union_disjoint(a,b); E=E+br
        if n<=14: fam("glue",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3)]:
        n,E=odd_blowup(5,list(sizes))
        if n<=13: fam("blow",n,E,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    n,E=mycielski(grN,grE); adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): fam("Myc23",n,E,acc,cuts=[side])
    print("="*55)
    print("negative ports total:",acc['ports'])
    print("  at ENDPOINT (i=0 or L-1):",acc['endpt'])
    print("  INTERIOR (0<i<L-1):",acc['interior'],acc['int_ex'] or '')
    print("VERDICT:", "NPort subset {endpoints} -- (B) is 2-ENDPOINT-TERM" if acc['interior']==0 else "INTERIOR negative ports EXIST")

if __name__=="__main__":
    main()
