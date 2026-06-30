"""Extend Codex 433 levelwise R1/R2 gate to the standing stress families NOT in _levelwise_gate.py:
   Myc(Grotzsch) N=23 (supplied near-min cut), glued C5 chains (supplied), random N=11/12 (gmins).
   Reuses _levelwise_gate.run (exact R1_k>=0, R2_k>=0, ID).  Exact Fraction.
"""
import random
import _levelwise_gate as lw
from _h import dec, Bconn
from _stark1 import gmins
from _bdef_construct import Cn, mycielski, is_triangle_free
from _Klocal_gate import glued_c5_chain

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
    acc=dict(k=0,R1_fail=0,R2_fail=0,ID_fail=0,R1_ex=None,R2_ex=None)
    # Myc(Grotzsch) N=23
    grN,grE=mycielski(5,Cn(5)); n,E=mycielski(grN,grE)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): lw.run("Myc23",n,adj,E,[side],acc)
    print("after Myc23: kchecks=%d R1=%d R2=%d ID=%d"%(acc['k'],acc['R1_fail'],acc['R2_fail'],acc['ID_fail']),flush=True)
    # glued C5 chains q=2..14 (supplied cut)
    for q in range(2,15):
        n,E,sd=glued_c5_chain(q)
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        if Bconn(n,adj,sd): lw.run("chain_q%d"%q,n,adj,E,[sd],acc)
    print("after chains: kchecks=%d R1=%d R2=%d ID=%d"%(acc['k'],acc['R1_fail'],acc['R2_fail'],acc['ID_fail']),flush=True)
    # random N=11/12 (gmins)
    rng=random.Random(23); made=0; tries=0
    while made<80 and tries<30000:
        tries+=1
        nn=rng.choice([11,12]); p=rng.uniform(0.14,0.34)
        E=[(a,b) for a in range(nn) for b in range(a+1,nn) if rng.random()<p]
        if not E or not is_triangle_free(nn,E): continue
        adj=[set() for _ in range(nn)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        if any(len(adj[v])==0 for v in range(nn)): continue
        seen={0};stk=[0]
        while stk:
            u=stk.pop()
            for w in adj[u]:
                if w not in seen: seen.add(w); stk.append(w)
        if len(seen)!=nn: continue
        try: a2,cuts=gmins(nn,E)
        except Exception: continue
        made+=1; lw.run("rand%d"%made,nn,adj,E,cuts,acc)
    print("="*55)
    print("random N=11/12 graphs:",made)
    print("k-checks:",acc['k'])
    print("(R1) R1_k>=0 failures:",acc['R1_fail'],acc['R1_ex'] or '')
    print("(R2) R2_k>=0 failures:",acc['R2_fail'],acc['R2_ex'] or '')
    print("identity failures:",acc['ID_fail'])
    ok=acc['R1_fail']==0 and acc['R2_fail']==0 and acc['ID_fail']==0
    print("VERDICT:", "R1/R2 HOLD on N=23 + chains + random N11/12" if ok else "FAILS")

if __name__=="__main__":
    main()
