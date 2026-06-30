"""Gate Codex 428 split of (B') into:
   (Bhigh) Tail_k(P) >= 0 for every row and every k>=1.
   (B0)    Tail_0(P) >= -24*e(P), e(P)=# negative endpoint ports (i in {0,L-1}, H_i<0), <=2.
   Tail_k=sum_{r>=k}(2r+1)Z_r from _layer_gate.Zr_row; H_i from _singleton_core.Hi_and_best.
   Full battery.  Exact.  Usage: python _bsplit_gate.py <family>
     families: cen10 | theta | grotzsch | myc23 | chains | islands | blowups | rand:S:C
"""
import sys, subprocess, random
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain

def scan(name,n,adj,E,cuts,acc):
    Lam=len(E)*n*n+1
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
                _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                tail=[sum((2*r+1)*Z[r] for r in range(k,n)) for k in range(n)]
                acc['rows']+=1
                # Bhigh: Tail_k>=0 for k>=1
                for k in range(1,n):
                    if tail[k]<0:
                        acc['bhigh_fail']+=1
                        if acc['bhigh_ex'] is None: acc['bhigh_ex']=(name,n,''.join(map(str,side)),f,tuple(P),k,str(tail[k]))
                        break
                # B0: Tail_0 >= -24*e(P)
                e=0
                for i in (0,L-1):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is not None and Hi<0: e+=1
                if tail[0] < -24*e:
                    acc['b0_fail']+=1
                    if acc['b0_ex'] is None: acc['b0_ex']=(name,n,''.join(map(str,side)),f,tuple(P),str(tail[0]),e)
                m=tail[0]+24*e
                if acc['b0_min'] is None or m<acc['b0_min']: acc['b0_min']=m

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

def run(family,acc):
    if family=="cen10":
        for nn in range(5,11):
            for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
                n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
    elif family=="theta":
        n,E=dec("H?AFBo]"); fam("thw",n,E,acc)
    elif family=="grotzsch":
        grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    elif family=="myc23":
        grN,grE=mycielski(5,Cn(5)); n,E=mycielski(grN,grE)
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        side=maxcut_ls(n,adj)
        if Bconn(n,adj,side): fam("Myc23",n,E,acc,cuts=[side])
    elif family=="chains":
        for q in range(2,12):
            n,E,side=glued_c5_chain(q)
            adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            if Bconn(n,adj,side): scan("chain_q%d"%q,n,adj,E,[side],acc)
        for q in [2,3]:
            n,E,side=glued_c5_chain(q); fam("chainAll_q%d"%q,n,E,acc)
    elif family=="islands":
        isl=(5,Cn(5)); g15=mycielski(7,Cn(7))
        n,E=union_disjoint(isl,g15); n,E=add_edges((n,E),[(0,5)])
        if n<=14: fam("isl",n,E,acc)
    elif family=="blowups":
        for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(2,2,2,1,1)]:
            n,E=odd_blowup(5,list(sizes))
            if n<=13: fam("blow%s"%(sizes,),n,E,acc)
    elif family.startswith("rand:"):
        _,seed,count=family.split(":"); seed=int(seed); count=int(count)
        rng=random.Random(seed); made=0; tries=0
        while made<count and tries<count*300:
            tries+=1
            nn=rng.choice([11,12]); p=rng.uniform(0.14,0.34)
            E=[(a,b) for a in range(nn) for b in range(a+1,nn) if rng.random()<p]
            if not E or not is_triangle_free(nn,E): continue
            adj=[set() for _ in range(nn)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            if any(len(adj[v])==0 for v in range(nn)): continue
            made+=1; fam("rand%d"%made,nn,E,acc)
        acc['rand_made']=made
    else:
        print("unknown",family); sys.exit(2)

def main():
    family=sys.argv[1] if len(sys.argv)>1 else "theta"
    acc=dict(rows=0,bhigh_fail=0,b0_fail=0,bhigh_ex=None,b0_ex=None,b0_min=None)
    run(family,acc)
    print("FAMILY=%s rows=%d"%(family,acc['rows']))
    print("  (Bhigh) Tail_k>=0 for k>=1: fail=%d %s"%(acc['bhigh_fail'],acc['bhigh_ex'] or ''))
    print("  (B0) Tail_0>=-24*e(P): fail=%d  min margin=%s %s"%(acc['b0_fail'],str(acc['b0_min']),acc['b0_ex'] or ''))
    if 'rand_made' in acc: print("  random graphs:",acc['rand_made'])
    print("  VERDICT_%s: %s"%(family,"PASS" if acc['bhigh_fail']==0 and acc['b0_fail']==0 else "FAIL"))

if __name__=="__main__":
    main()
