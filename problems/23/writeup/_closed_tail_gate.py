"""Exact-test Codex block-191 CLOSED-TAIL switch proof of (M) on the full battery.
cl(S) = S union {off-path B-component C : A(C) nonempty and A(C) subset S}, A(C)=path vtxs with cut-edges into C.
For each P-contained interior-overlap pair [p1,q1],[p2,q2] (p1<=p2, r=min(q1,q2)>p2):
  S_L=P[0..p2], S_R=P[r..end]; test gain(cl(S_L)), gain(cl(S_R)) (delta_M-delta_B); one positive => not max.
Report caught, min(gain sum), B-connectivity after the improving closed switch. Battery: census N<=9 all connB +
N=26-38 nested/crossing + glued + Mycielskians + the leaf-augmented non-max regressions. Exact."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _M_tailswitch_gate import build_pd, tri_free

def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def gain(n,adj,s,Sset):
    dB=0; dM=0
    for u in Sset:
        for w in adj[u]:
            if w in Sset: continue
            if s[u]!=s[w]: dB+=1
            else: dM+=1
    return dM-dB
def offpath_components(n,adj,s,Pset,pos):
    rest=[v for v in range(n) if v not in Pset]; par={v:v for v in rest}
    def find(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for u in rest:
        for w in adj[u]:
            if w not in Pset and s[u]!=s[w]: par[find(u)]=find(w)
    cd={}
    for v in rest: cd.setdefault(find(v),set()).add(v)
    comps=[]
    for r,C in cd.items():
        A=set(x for u in C for x in adj[u] if x in Pset and s[u]!=s[x])  # path attach vtxs (cut edges)
        comps.append((C,A))
    return comps
def closed(Sset, comps):
    cl=set(Sset)
    for C,A in comps:
        if A and A<=Sset: cl|=C
    return cl

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
                    SL=set(P_f[0:a2+1]); SR=set(P_f[r:L])
                    cL=closed(SL,comps); cR=closed(SR,comps)
                    gL=gain(n,adj,s,cL); gR=gain(n,adj,s,cR)
                    if gL>0 or gR>0:
                        acc['caught']+=1
                        # B-connectivity after the improving closed switch
                        Sbest=cL if gL>=gR else cR
                        s2=s[:]
                        for v in Sbest: s2[v]^=1
                        if not Bconn(n,adj,s2): acc['bdisc']+=1
                    else:
                        acc['miss']+=1
                        if acc['first'] is None: acc['first']=(name,''.join(map(str,s)),f,P_f,(a1,b1),(a2,b2),gL,gR)
                    ssum=gL+gR
                    if ssum<acc['minsum']: acc['minsum']=ssum; acc['minsumrec']=(name,f,(a1,b1),(a2,b2),gL,gR)

def run():
    acc={'ov':0,'caught':0,'miss':0,'first':None,'minsum':10**9,'minsumrec':None,'bdisc':0}
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
                             ("nested2",16,[(0,12),(2,10),(4,8)]),("nested-c6",18,[(0,12),(3,9)])]:
        n,E=build_pd(pend,chords); adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        if not tri_free(n,adj): continue
        o0=acc['ov']; m0=acc['miss']
        check_cut(n,adj,[v%2 for v in range(n)],name,acc)
        print(f"  {name} N={n} parity: overlaps(+{acc['ov']-o0}) miss(+{acc['miss']-m0})",flush=True)
    # leaf-augmented non-max regressions (the block-190 examples)
    from _codex190_ismax_check import add_cut_leaves
    n0,E0=build_pd(12,[(0,8),(2,6)]); s0=[v%2 for v in range(n0)]
    for attach in [[(0,1)],[(0,3),(8,3)]]:
        n,E,s=add_cut_leaves(n0,E0,s0,attach); adj=[set() for _ in range(n)]
        for a,b in E: adj[a].add(b); adj[b].add(a)
        o0=acc['ov']; m0=acc['miss']
        check_cut(n,adj,s,f"leafaug{attach}",acc)
        print(f"  leafaug{attach} N={n}: overlaps(+{acc['ov']-o0}) miss(+{acc['miss']-m0})",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for name,(nn,E) in [("C7|brg|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),
                        ("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),("Grotzsch",grot),("Myc(Grotzsch)",mycg)]:
        adj,cuts=gmins(nn,E); o0=acc['ov']; m0=acc['miss']
        for s in cuts: check_cut(nn,adj,s,name,acc)
        print(f"  {name} N={nn} gmin: overlaps(+{acc['ov']-o0}) miss(+{acc['miss']-m0})",flush=True)
    print(f"\n  TOTAL interior-overlaps={acc['ov']} CAUGHT={acc['caught']} MISS={acc['miss']} (B-disconnect after switch={acc['bdisc']})",flush=True)
    print(f"  MIN closed gain sum={acc['minsum']} at {acc['minsumrec']}",flush=True)
    if acc['first']: print(f"  first MISS: {acc['first']}",flush=True)
    print(f"  === {'CLOSED-TAIL FAILS (miss)' if acc['miss'] else 'CLOSED-TAIL proves (M): every P-contained interior-overlap has a cut-increasing CLOSED tail switch => not global max'} ===",flush=True)

if __name__=="__main__": run()
