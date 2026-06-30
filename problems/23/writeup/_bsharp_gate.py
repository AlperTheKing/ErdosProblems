"""Gate Codex 439 SHARPENED component-local B split on gamma-min battery.
   Over(P) = sum_{v in P} T[v] - L*N.   C=Kcomp(P), Gamma_C, Def_C=|C|*N-Gamma_C.
   (B7) if L>=7:  Over(P) <= 0.
   (B5) if L==5:  15*Over(P) <= 2*Def_C.
   These imply B-local (L>=7 => Over_+=0; L=5 => Over_+ <= (2/15)Def_C <= (4/25)Def_C).  Exact.
   Usage: python _bsharp_gate.py <family>   families as _blocal_gate.
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
    N=F(n)
    for f in M:
        L=ell[f]
        if L%2==0: continue
        for P in cyc[f]:
            if len(P)!=L: continue
            C=Kcomp(n,M,cyc,set(P)); m=F(len(C))
            GammaC=sum(ell[g]**2 for g in M if any(set(Q)<=C for Q in cyc[g]))
            Def_C=m*N-GammaC
            Over=sum(T[P[i]] for i in range(L))-L*N
            acc['rows']+=1
            if Over>0:
                acc['posover']+=1
                # (Bpos-struct): Over>0 => L=5 and all bad edges in Gamma_C have ell=5
                ellsC=set(ell[g] for g in M if any(set(Q)<=C for Q in cyc[g]))
                if L!=5 or ellsC!={5}:
                    acc['bstruct_fail']+=1
                    if acc['bs_ex'] is None: acc['bs_ex']=(name,n,tuple(P),L,sorted(ellsC))
                # (Bpos-whole): Over>0 => |C|=N
                if len(C)!=n:
                    acc['bwhole_fail']+=1
                    if acc['bw_ex'] is None: acc['bw_ex']=(name,n,tuple(P),len(C))
            if L>=7:
                if Over>0:
                    acc['b7_fail']+=1
                    if acc['b7_ex'] is None: acc['b7_ex']=(name,n,''.join(map(str,side)),f,tuple(P),L,str(Over))
            elif L==5:
                if 15*Over>2*Def_C:
                    acc['b5_fail']+=1
                    if acc['b5_ex'] is None: acc['b5_ex']=(name,n,''.join(map(str,side)),f,tuple(P),str(Over),str(Def_C))
                if Over>0:
                    rt=F(Over,1)/Def_C if Def_C!=0 else None
                    if rt is not None and (acc['b5_maxratio'] is None or rt>acc['b5_maxratio']):
                        acc['b5_maxratio']=rt; acc['b5_argmax']=(name,n,tuple(P))

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
            print("census N=%d: rows=%d b7=%d b5=%d posover=%d"%(nn,acc['rows'],acc['b7_fail'],acc['b5_fail'],acc['posover']),flush=True)
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
    acc=dict(rows=0,posover=0,b7_fail=0,b5_fail=0,b7_ex=None,b5_ex=None,b5_maxratio=None,b5_argmax=None,
             bstruct_fail=0,bs_ex=None,bwhole_fail=0,bw_ex=None)
    run(family,acc)
    print("FAMILY=%s rows=%d positive-overload=%d"%(family,acc['rows'],acc['posover']))
    print("  (B7) L>=7 => Over<=0  fail=%d %s"%(acc['b7_fail'],acc['b7_ex'] or ''))
    print("  (B5) L=5 => 15 Over<=2 Def_C  fail=%d  maxratio Over/Def_C=%s @ %s %s"%(acc['b5_fail'],str(acc['b5_maxratio']),acc['b5_argmax'],acc['b5_ex'] or ''))
    print("  (Bpos-struct) Over>0 => L=5 and all Gamma_C bad edges ell=5  fail=%d %s"%(acc['bstruct_fail'],acc['bs_ex'] or ''))
    print("  (Bpos-whole) Over>0 => |C|=N  fail=%d %s"%(acc['bwhole_fail'],acc['bw_ex'] or ''))
    if 'rand_made' in acc: print("  random graphs:",acc['rand_made'])
    print("  VERDICT_%s: %s"%(family,"PASS" if acc['b7_fail']==0 and acc['b5_fail']==0 else "FAIL"))

if __name__=="__main__":
    main()
