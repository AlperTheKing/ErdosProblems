"""Gate Codex 449 B5 equality/stability classification on the full B battery.
   For each gamma-min row P with ell(f)=5: I(P)=sum_g (1/|cyc[g]|) sum_Q |V(P) cap V(Q)|, Def=N^2-25|M|,
   B5_margin = (2/75)Def - (I(P)-N).  Over(P)=5*(I(P)-N).
   Classify B5_margin==0 rows: Over=0 (Def=0 family = balanced C5[t]) vs Over>0 (the frontier; check Petersen-iso
   invariants N=10,|M|=3,Def=25,I=32/3).  Min positive margin among Over>0 non-equality rows.  Exact.
"""
import subprocess, random
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, mycielski, is_triangle_free
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

def scan(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    if not M: return
    N=F(n)
    for f in M:
        if ell[f]!=5: continue
        for P in cyc[f]:
            if len(P)!=5: continue
            C=Kcomp(n,M,cyc,set(P))
            if len(C)!=n: continue
            if set(ell[g] for g in M if any(set(Q)<=C for Q in cyc[g]))!={5}: continue
            Pset=set(P)
            I=sum(F(1,len(cyc[g]))*sum(len(Pset & set(Q)) for Q in cyc[g]) for g in M)
            Def=N*N-25*len(M)
            margin=F(2,75)*Def-(I-N)
            Over=5*(I-N)
            acc['rows']+=1
            if margin==0:
                if Over>0:
                    acc['eq_pos']+=1
                    key=(n,len(M),str(Def),str(I))
                    acc['pos_tuples'][key]=acc['pos_tuples'].get(key,0)+1
                    if (n,len(M),Def,I)!=(10,3,25,F(32,3)):
                        acc['nonpetersen']+=1
                        if acc['np_ex'] is None: acc['np_ex']=(name,n,tuple(P),len(M),str(Def),str(I))
                else:
                    acc['eq_zero']+=1   # Over<=0, Def=0 family (C5[t])
            elif margin<0:
                acc['B5_fail']+=1
                if acc['fail_ex'] is None: acc['fail_ex']=(name,n,tuple(P),str(margin))
            else:
                if Over>0:
                    if acc['minposmargin'] is None or margin<acc['minposmargin']:
                        acc['minposmargin']=margin; acc['mpm_ex']=(name,n,tuple(P),str(margin))

def gfam(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    try: _,cuts=gmins(n,E)
    except Exception: return
    for side in cuts: scan(name,n,adj,side,acc)

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
    acc=dict(rows=0,eq_pos=0,eq_zero=0,B5_fail=0,nonpetersen=0,minposmargin=None,
             pos_tuples={},np_ex=None,fail_ex=None,mpm_ex=None)
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); gfam("cen%d"%nn,n,E,acc)
    grN,grE=mycielski(5,Cn(5)); n,E=mycielski(grN,grE)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): scan("Myc23",n,adj,side,acc)
    for q in range(2,12):
        n,E,side=glued_c5_chain(q)
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        if Bconn(n,adj,side): scan("chain_q%d"%q,n,adj,side,acc)
    for sizes in [(2,2,2,2,2),(3,3,3,3,3),(2,1,2,1,2)]:
        nn,EE=odd_blowup(5,list(sizes))
        if nn<=16: gfam("blow%s"%(sizes,),nn,EE,acc)
    rng=random.Random(7); made=0; tries=0
    while made<150 and tries<40000:
        tries+=1
        nn=rng.choice([11,12]); p=rng.uniform(0.14,0.34)
        EE=[(a,b) for a in range(nn) for b in range(a+1,nn) if rng.random()<p]
        if not EE or not is_triangle_free(nn,EE): continue
        adj=[set() for _ in range(nn)]
        for a,b in EE: adj[a].add(b); adj[b].add(a)
        if any(len(adj[v])==0 for v in range(nn)): continue
        made+=1; gfam("rand%d"%made,nn,EE,acc)
    print("pure-C5 whole-component ell=5 rows:",acc['rows']," (random N=11/12 graphs:",made,")")
    print("B5_margin<0 (B5 FAILURES):",acc['B5_fail'],acc['fail_ex'] or '')
    print("zero-margin Over=0 (C5[t]/Def=0 family):",acc['eq_zero'])
    print("zero-margin Over>0 (frontier equality):",acc['eq_pos'])
    print("  positive-overload equality invariant-tuples (N,|M|,Def,I):",dict(acc['pos_tuples']))
    print("  non-Petersen-invariant positive equality rows:",acc['nonpetersen'],acc['np_ex'] or '')
    print("min positive B5_margin among Over>0 non-equality rows:",str(acc['minposmargin']),acc['mpm_ex'] or '')
    print("VERDICT:", "B5 holds; pos-overload equality is PETERSEN-INVARIANT only" if acc['B5_fail']==0 and acc['nonpetersen']==0 else "see failures")

if __name__=="__main__":
    main()
