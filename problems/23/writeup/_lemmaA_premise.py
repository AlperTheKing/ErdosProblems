"""Gate Codex 425 Lemma A structural premise (sorted-length dominance) for every negative singleton port:
   With em0=ell_map(side), em1=ell_map(flip(side,W_i)), added=bad in em1 not em0, removed=bad in em0 not em1,
   retained=common bad whose length changes:
     (1) mu = delta_B(W_i)-delta_M(W_i) == 0   (neutral),
     (2) |added| == |removed|,
     (3) sorted(added lengths) <= sorted(removed lengths) componentwise,
     (4) retained: em1[h] <= em0[h]  (lengths never increase).
   If all hold, Codex's Lemma A prefix<=0 proof goes through.  Full battery, exact.
"""
import subprocess, random
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _wf_deficit_farkas import deltas, flip, odd_blowup
from _h import dec, GENG, Bconn
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
                for i in range(len(P)):
                    Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                    if Hi is None or Hi>=0 or W is None: continue
                    acc['ports']+=1
                    dB,dM=deltas(n,adj,side,W); mu=dB-dM
                    em1=ell_map(n,adj,flip(side,W))
                    k0=set(em0);k1=set(em1);added=k1-k0;removed=k0-k1;ret=k0&k1
                    al=sorted(em1[e] for e in added); rl=sorted(em0[g] for g in removed)
                    if mu!=0: acc['mu']+=1; acc['ex']=acc['ex'] or (name,tuple(P),i,'mu=%d'%mu)
                    if len(added)!=len(removed): acc['card']+=1; acc['ex']=acc['ex'] or (name,tuple(P),i,'|A|=%d|B|=%d'%(len(added),len(removed)))
                    if not all(a<=b for a,b in zip(al,rl)): acc['sort']+=1; acc['ex']=acc['ex'] or (name,tuple(P),i,'A=%s>B=%s'%(al,rl))
                    if any(em1[h]>em0[h] for h in ret): acc['ret']+=1; acc['ex']=acc['ex'] or (name,tuple(P),i,'retained increased')

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
    acc=dict(ports=0,mu=0,card=0,sort=0,ret=0,ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); fam("cen%d"%nn,n,E,acc)
        print("census N=%d: ports=%d mu=%d card=%d sort=%d ret=%d"%(nn,acc['ports'],acc['mu'],acc['card'],acc['sort'],acc['ret']),flush=True)
    n,E=dec("H?AFBo]"); fam("thw",n,E,acc)
    for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3)]:
        n,E=odd_blowup(5,list(sizes))
        if n<=13: fam("blow",n,E,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    n,E=mycielski(grN,grE); adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): fam("Myc23",n,E,acc,cuts=[side])
    # random N=11,12
    rng=random.Random(13); made=0; tries=0
    while made<120 and tries<40000:
        tries+=1
        nn=rng.choice([11,12]); p=rng.uniform(0.14,0.34)
        E=[(a,b) for a in range(nn) for b in range(a+1,nn) if rng.random()<p]
        if not E or not is_triangle_free(nn,E): continue
        adj=[set() for _ in range(nn)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        if any(len(adj[v])==0 for v in range(nn)): continue
        made+=1; fam("rand%d"%made,nn,E,acc)
    print("="*55)
    print("negative ports:",acc['ports'],"  random N=11/12 graphs:",made)
    print("(1) mu!=0:",acc['mu'])
    print("(2) |added|!=|removed|:",acc['card'])
    print("(3) sorted added > removed (componentwise viol):",acc['sort'])
    print("(4) retained length increased:",acc['ret'])
    print("first ex:",acc['ex'] or 'none')
    print("VERDICT:", "LEMMA A PREMISE HOLDS" if acc['mu']==acc['card']==acc['sort']==acc['ret']==0 else "PREMISE FAILS")

if __name__=="__main__":
    main()
