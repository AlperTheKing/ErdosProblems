"""Gate Codex 437 component-local B-overload split on gamma-min battery.
   C = positive-K component of V(P) (clique on each shortest geodesic's vertex set).  m=|C|.
   Gamma_C = sum_{g: exists geodesic Q in cyc[g] with set(Q) subset C} ell[g]^2.   Def_C = m*N - Gamma_C.
   S(P) = sum_{v in P} T[v] / N.
   (B-local)  25*N*max(0, S-L) <= (4L/5)*Def_C.
   (Def-sub)  Def_C <= N^2 - Gamma  (Gamma=sum_g ell[g]^2).
   Both => global B: 25N*max(0,S-L) <= (4L/5)(N^2-Gamma).  Exact.
   Usage: python _blocal_gate.py <family>   families: cen10|theta|grotzsch|myc23|chains|islands|blowups|rand:S:C
"""
import sys, subprocess, random
from fractions import Fraction as F
from collections import deque
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, add_edges, mycielski, is_triangle_free
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
    N=F(n); Gamma=sum(ell[g]**2 for g in M)
    for f in M:
        L=ell[f]
        if L%2==0: continue
        for P in cyc[f]:
            if len(P)!=L: continue
            C=Kcomp(n,M,cyc,set(P)); m=F(len(C))
            GammaC=sum(ell[g]**2 for g in M if any(set(Q)<=C for Q in cyc[g]))
            Def_C=m*N-GammaC
            S=sum(T[P[i]] for i in range(L))/N
            acc['rows']+=1
            # (B-local)
            lhs=25*N*max(0,S-L); rhs=F(4*L,5)*Def_C
            if lhs>rhs:
                acc['blocal_fail']+=1
                if acc['bl_ex'] is None: acc['bl_ex']=(name,n,''.join(map(str,side)),f,tuple(P),str(lhs),str(rhs))
            mb=rhs-lhs
            if acc['bl_min'] is None or mb<acc['bl_min']: acc['bl_min']=mb
            # (Def-sub)
            if Def_C > N*N-Gamma:
                acc['defsub_fail']+=1
                if acc['ds_ex'] is None: acc['ds_ex']=(name,n,tuple(P),str(Def_C),str(N*N-Gamma))
            md=(N*N-Gamma)-Def_C
            if acc['ds_min'] is None or md<acc['ds_min']: acc['ds_min']=md

def gfam(name,n,E,acc):
    if not E: return
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

def run(family,acc):
    if family=="cen10":
        for nn in range(5,11):
            for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
                n,E=dec(g6); gfam("cen%d"%nn,n,E,acc)
            print("census N=%d: rows=%d blocal=%d defsub=%d"%(nn,acc['rows'],acc['blocal_fail'],acc['defsub_fail']),flush=True)
    elif family=="theta":
        n,E=dec("H?AFBo]"); gfam("thw",n,E,acc)
    elif family=="grotzsch":
        grN,grE=mycielski(5,Cn(5)); gfam("Grotzsch",grN,grE,acc)
    elif family=="myc23":
        grN,grE=mycielski(5,Cn(5)); n,E=mycielski(grN,grE)
        adj=[set() for _ in range(n)]
        for x,y in E: adj[x].add(y); adj[y].add(x)
        side=maxcut_ls(n,adj)
        if Bconn(n,adj,side): scan("Myc23",n,adj,side,acc)
    elif family=="chains":
        for q in range(2,14):
            n,E,side=glued_c5_chain(q)
            adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            if Bconn(n,adj,side): scan("chain_q%d"%q,n,adj,side,acc)
    elif family=="islands":
        isl=(5,Cn(5)); g15=mycielski(7,Cn(7))
        n,E=union_disjoint(isl,g15); n,E=add_edges((n,E),[(0,5)])
        if n<=14: gfam("isl",n,E,acc)
    elif family=="blowups":
        for sizes in [(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(2,2,2,1,1),(3,1,3,1,3)]:
            n,E=odd_blowup(5,list(sizes))
            if n<=14: gfam("blow%s"%(sizes,),n,E,acc)
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
            made+=1; gfam("rand%d"%made,nn,E,acc)
        acc['rand_made']=made
    else:
        print("unknown",family); sys.exit(2)

def main():
    family=sys.argv[1] if len(sys.argv)>1 else "theta"
    acc=dict(rows=0,blocal_fail=0,defsub_fail=0,bl_ex=None,ds_ex=None,bl_min=None,ds_min=None)
    run(family,acc)
    print("FAMILY=%s rows=%d"%(family,acc['rows']))
    print("  (B-local) 25N max(0,S-L)<=(4L/5)Def_C  fail=%d  min margin=%s %s"%(acc['blocal_fail'],str(acc['bl_min']),acc['bl_ex'] or ''))
    print("  (Def-sub) Def_C<=N^2-Gamma             fail=%d  min margin=%s %s"%(acc['defsub_fail'],str(acc['ds_min']),acc['ds_ex'] or ''))
    if 'rand_made' in acc: print("  random graphs:",acc['rand_made'])
    print("  VERDICT_%s: %s"%(family,"PASS" if acc['blocal_fail']==0 and acc['defsub_fail']==0 else "FAIL"))

if __name__=="__main__":
    main()
