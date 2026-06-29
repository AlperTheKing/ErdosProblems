"""Exact-test Codex block-193 CLOSED-OVERLAP-SWEEP proof of (M) on the full battery.
For interior-overlapping P-contained rows [p1,q1],[p2,q2] (p1<=p2, r=min(q1,q2)>p2): claim EXISTS k in
[p2, r-1] with cl({x_0..x_k}) OR cl({x_{k+1}..x_{L-1}}) having positive cut gain (flip strictly increases cut).
cl(S)=S union {off-path B-component C : A(C) nonempty and A(C) subset S}. => interior-overlap impossible on a
global max cut => (M). Battery: census N<=9 all connB + N=26-38 nested/crossing/chain + leaf/detour ballast +
glued + Mycielskians. Report caught, min over pairs of (max_k best gain), B-connectivity after switch."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _M_tailswitch_gate import build_pd, tri_free
from _closed_tail_gate import gain, offpath_components, closed
from _codex190_ismax_check import add_cut_leaves
from _tail_positive_extra_counterexample import add_cut_path

def check_cut(n,adj,s,name,acc):
    if not Bconn(n,adj,s): return
    st=struct_for_side(n,adj,s)
    if st is None: return
    M,ell,T,mu,cyc=st
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        chords=[]
        for g in M:
            if g==f: continue
            for Q in cyc[g]:
                if set(Q)<=Pset:
                    pp=sorted(pos[v] for v in Q)
                    if pp[-1]-pp[0]==len(pp)-1: chords.append((pp[0],pp[-1])); break
        if len(chords)<2: continue
        comps=offpath_components(n,adj,s,Pset,pos)
        for i in range(len(chords)):
            for j in range(i+1,len(chords)):
                a1,b1=chords[i]; a2,b2=chords[j]
                if a1>a2: a1,b1,a2,b2=a2,b2,a1,b1
                r=min(b1,b2)
                if a2<r:
                    acc['ov']+=1
                    best=None; bestset=None
                    for k in range(a2, r):  # p2 <= k < r
                        cL=closed(set(P_f[0:k+1]),comps); cR=closed(set(P_f[k+1:L]),comps)
                        gL=gain(n,adj,s,cL); gR=gain(n,adj,s,cR)
                        for gg,SS in ((gL,cL),(gR,cR)):
                            if best is None or gg>best: best=gg; bestset=SS
                    if best is not None and best>0:
                        acc['caught']+=1
                        s2=s[:]
                        for v in bestset: s2[v]^=1
                        if not Bconn(n,adj,s2): acc['bdisc']+=1
                    else:
                        acc['miss']+=1
                        if acc['first'] is None: acc['first']=(name,''.join(map(str,s)),f,P_f,(a1,b1),(a2,b2),best)
                    if best is not None and best<acc['minbest']: acc['minbest']=best; acc['minbestrec']=(name,f,(a1,b1),(a2,b2),best)

def run():
    acc={'ov':0,'caught':0,'miss':0,'first':None,'minbest':10**9,'minbestrec':None,'bdisc':0}
    for nn in range(6,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        o0=acc['ov']; m0=acc['miss']
        for g6 in outg:
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            for m in range(1<<(n-1)):
                s=[(m>>v)&1 for v in range(n)]
                check_cut(n,adj,s,g6,acc)
        print(f"  census N={nn} all connB: overlaps(+{acc['ov']-o0}) miss(+{acc['miss']-m0})",flush=True)
    for name,pend,chords in [("nested",12,[(0,8),(2,6)]),("crossing",12,[(0,6),(2,8)]),
                             ("nested2",16,[(0,12),(2,10),(4,8)]),("nested-c6",18,[(0,12),(3,9)]),
                             ("chain",12,[(0,4),(4,8),(8,12)])]:
        n,E=build_pd(pend,chords); adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        if not tri_free(n,adj): continue
        o0=acc['ov']; m0=acc['miss']
        check_cut(n,adj,[v%2 for v in range(n)],name,acc)
        print(f"  {name} N={n} parity: overlaps(+{acc['ov']-o0}) miss(+{acc['miss']-m0})",flush=True)
    # leaf + two-sided detour ballast (m=0..5)
    n0,E0=build_pd(12,[(0,8),(2,6)]); s0=[v%2 for v in range(n0)]
    for attach in [[(0,1)],[(0,3),(8,3)]]:
        n,E,s=add_cut_leaves(n0,E0,s0,attach); adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        o0=acc['ov']; m0=acc['miss']
        check_cut(n,adj,s,f"leaf{attach}",acc)
        print(f"  leaf{attach} N={n}: overlaps(+{acc['ov']-o0}) miss(+{acc['miss']-m0})",flush=True)
    for mdet in range(0,6):
        n,E,s=n0,list(E0),list(s0)
        for _ in range(mdet):
            n,E,s=add_cut_path(n,E,s,0,3,5); n,E,s=add_cut_path(n,E,s,8,5,5)
        adj=[set() for _ in range(n)]
        for a,b in sorted(set(E)): adj[a].add(b); adj[b].add(a)
        o0=acc['ov']; m0=acc['miss']
        check_cut(n,adj,s,f"detour-m{mdet}",acc)
        print(f"  detour-m{mdet} N={n}: overlaps(+{acc['ov']-o0}) miss(+{acc['miss']-m0})",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("C7|brg|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),
                        ("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),("Grotzsch",grot),("Myc(Grotzsch)",mycg)]:
        adj,cuts=gmins(nn,E); o0=acc['ov']; m0=acc['miss']
        for s in cuts: check_cut(nn,adj,s,name,acc)
        print(f"  {name} N={nn} gmin: overlaps(+{acc['ov']-o0}) miss(+{acc['miss']-m0})",flush=True)
    print(f"\n  TOTAL interior-overlaps={acc['ov']} CAUGHT={acc['caught']} MISS={acc['miss']} (B-disc after switch={acc['bdisc']})",flush=True)
    print(f"  MIN best gain over pairs = {acc['minbest']} at {acc['minbestrec']}",flush=True)
    if acc['first']: print(f"  first MISS: {acc['first']}",flush=True)
    print(f"  === {'CLOSED-SWEEP FAILS (miss)' if acc['miss'] else 'CLOSED-SWEEP proves (M): every interior-overlap has a sliding-closed switch with positive cut gain => not global max'} ===",flush=True)

if __name__=="__main__": run()
