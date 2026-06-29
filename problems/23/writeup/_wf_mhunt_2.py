"""ADVERSARIAL hunt for a counterexample to LEMMA (M), Family #2 = GLUED ISLANDS.
Triangle-free graphs built as union_disjoint of (C5/C7 island)+(Myc gadget)+tree bridges
+ pendant/anchored idle B-pins. For EACH graph ONE single 2^(n-1) brute pass simultaneously:
  - records true global max cut size,
  - collects ALL global-max cuts,
  - on each connected-B cut (max OR not) checks unique-geodesic P-contained interior-overlaps.
A COUNTEREXAMPLE = an interior-overlap on a cut whose size == true global max AND Bconn.
Near-miss = interior-overlap on a connected-B cut that is NOT global-max (locally max but +1 exists).

EXACT integer cut sizes; maximality verified EXACTLY by the single brute pass (no heuristic).
N capped so 2^(n-1) brute is feasible. Run from E:/Projects/ErdosProblems/problems/23/writeup.
"""
import itertools
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _bdef_construct import mycielski, Cn, union_disjoint, is_triangle_free

NCAP=21   # 2^(NCAP-1) brute per graph; 2^20 ~1M pure-python loop iters

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E:
        if a!=b: adj[a].add(b); adj[b].add(a)
    return adj

def overlaps_on_cut(n,adj,s):
    """interior-overlap records for unique-geodesic bad edges on cut s, or None if not Bconn."""
    if not Bconn(n,adj,s): return None
    st=struct_for_side(n,adj,s)
    if st is None: return []
    M,ell,T,mu,cyc=st
    res=[]
    for f in M:
        if len(cyc[f])!=1: continue
        P_f=cyc[f][0]; L=len(P_f); pos={x:i for i,x in enumerate(P_f)}; Pset=set(P_f)
        chords=[]
        for g in M:
            if g==f: continue
            for Q in cyc[g]:
                if set(Q)<=Pset:
                    pp=sorted(pos[v] for v in Q)
                    if pp[-1]-pp[0]==len(pp)-1:
                        chords.append((pp[0],pp[-1],g)); break
        for i in range(len(chords)):
            for j in range(i+1,len(chords)):
                a1,b1,g1=chords[i]; a2,b2,g2=chords[j]
                if a1>a2: a1,b1,g1,a2,b2,g2=a2,b2,g2,a1,b1,g1
                r=min(b1,b2)
                if a2<r:
                    res.append((f,tuple(P_f),(a1,b1),(a2,b2)))
    return res

def hunt_graph(name,n,E,acc,verbose=True):
    if n-1>NCAP: return
    if not is_triangle_free(n,E): return
    adj=adj_of(n,E)
    edges=[(u,v) for u in range(n) for v in adj[u] if v>u]
    acc['graphs']+=1
    # single brute pass: find max and collect all cut bitmasks by cutsize
    best=-1; bycut={}
    for m in range(1<<(n-1)):
        c=0
        for u,v in edges:
            if ((m>>u)^(m>>v))&1: c+=1
        if c>best: best=c
        bycut.setdefault(c,[]).append(m)
    mx=best
    # global-max cuts -> counterexample check
    for m in bycut.get(mx,[]):
        s=[(m>>u)&1 for u in range(n)]
        ov=overlaps_on_cut(n,adj,s)
        if ov:
            for (f,P_f,c1,c2) in ov:
                acc['gmax_overlaps']+=1
                rec=dict(name=name,n=n,E=list(E),side=list(s),f=f,P=P_f,c1=c1,c2=c2,
                         cutsize=mx,truemax=mx)
                acc['witnesses'].append(rec)
                if verbose:
                    print(f"  !!! GLOBAL-MAX OVERLAP {name} N={n}: f={f} P={P_f} chords={c1},{c2} cut={mx}",flush=True)
    # near-miss: connected-B non-max cuts with overlaps (just count; cheap since we already have bycut)
    if n<=15:
        for c,masks in bycut.items():
            if c==mx: continue
            for m in masks:
                s=[(m>>u)&1 for u in range(n)]
                ov=overlaps_on_cut(n,adj,s)
                if ov: acc['nearmiss']+=len(ov)

def bridge_union(blocks, bridges):
    offs=[]; n=0; E=[]
    for (bn,bE) in blocks:
        offs.append(n); E+=[(a+n,b+n) for (a,b) in bE]; n+=bn
    for (ba,la,bb,lb) in bridges:
        E.append((offs[ba]+la, offs[bb]+lb))
    return n,E

def add_pendants(nE, pins):
    n,E=nE; E=list(E)
    for (anchor,clen) in pins:
        prev=anchor
        for _ in range(clen):
            E.append((prev,n)); prev=n; n+=1
    return n,E

if __name__=="__main__":
    print(f"=== FAMILY #2 (glued islands) hunt for LEMMA (M) counterexample (NCAP={NCAP}) ===",flush=True)
    acc=dict(graphs=0,gmax_overlaps=0,nearmiss=0,witnesses=[])

    grot=mycielski(5,Cn(5))      # N=11, has O
    mycC7=mycielski(7,Cn(7))     # N=15, has O
    islands=[(5,Cn(5)),(7,Cn(7))]

    # battery A: C5/C7 island + Grotzsch(N11) gadget, single bridge various anchors (N<=18)
    cfgs=0
    for (iN,iE) in islands:
        for la in range(iN):
            for lb in range(min(grot[0],6)):
                n,E=bridge_union([(iN,iE),grot],[(0,la,1,lb)])
                hunt_graph(f"isl{iN}+Grot+brg({la},{lb})",n,E,acc); cfgs+=1
    print(f"  battery A done: configs={cfgs} graphs={acc['graphs']} gmax-overlaps={acc['gmax_overlaps']} nearmiss={acc['nearmiss']}",flush=True)

    # battery B: two islands + bridge + pendant pins (idle B-pins to push a locally-max cut)
    cfgs=0
    for (iN,iE) in islands:
        for la in range(iN):
            base=bridge_union([(iN,iE),(5,Cn(5))],[(0,la,1,0)])
            for pin in [[(0,1)],[(0,2)],[(iN,1)],[(iN,2)],[(0,1),(iN,1)]]:
                n,E=add_pendants(base,pin)
                if n-1<=NCAP:
                    hunt_graph(f"isl{iN}+C5+brg{la}+pin{pin}",n,E,acc); cfgs+=1
    print(f"  battery B done: configs={cfgs} graphs={acc['graphs']} gmax-overlaps={acc['gmax_overlaps']} nearmiss={acc['nearmiss']}",flush=True)

    # battery C: Grotzsch + pendant pins (idle B-pins on a graph that has O)
    cfgs=0
    for anchor in range(grot[0]):
        for pin in [[(anchor,1)],[(anchor,2)],[(anchor,3)],[(anchor,4)]]:
            n,E=add_pendants(grot,pin)
            if n-1<=NCAP:
                hunt_graph(f"Grot+pin@{anchor}{pin}",n,E,acc); cfgs+=1
    print(f"  battery C done: configs={cfgs} graphs={acc['graphs']} gmax-overlaps={acc['gmax_overlaps']} nearmiss={acc['nearmiss']}",flush=True)

    # battery D: C7 + C5 + C5 chained by two bridges (longer geodesic P through the chain)
    cfgs=0
    for la in range(7):
        for lb in range(5):
            n,E=bridge_union([(7,Cn(7)),(5,Cn(5)),(5,Cn(5))],[(0,la,1,0),(1,lb,2,0)])
            if n-1<=NCAP:
                hunt_graph(f"C7+C5+C5 chain brg({la},{lb})",n,E,acc); cfgs+=1
    print(f"  battery D done: configs={cfgs} graphs={acc['graphs']} gmax-overlaps={acc['gmax_overlaps']} nearmiss={acc['nearmiss']}",flush=True)

    # battery E: Myc(C7) N15 gadget + C5 island, single bridge (N=20, has O on gadget)
    cfgs=0
    for la in range(5):
        for lb in range(min(mycC7[0],6)):
            n,E=bridge_union([(5,Cn(5)),mycC7],[(0,la,1,lb)])
            if n-1<=NCAP:
                hunt_graph(f"C5+MycC7+brg({la},{lb})",n,E,acc); cfgs+=1
    print(f"  battery E done: configs={cfgs} graphs={acc['graphs']} gmax-overlaps={acc['gmax_overlaps']} nearmiss={acc['nearmiss']}",flush=True)

    print(f"\n  === TOTAL: graphs={acc['graphs']} GLOBAL-MAX interior-overlaps={acc['gmax_overlaps']} "
          f"near-miss(non-max overlaps,N<=15)={acc['nearmiss']} ===",flush=True)
    if acc['witnesses']:
        print(f"  COUNTEREXAMPLES FOUND: {len(acc['witnesses'])}",flush=True)
        for w in acc['witnesses'][:8]:
            print(f"    {w['name']} N={w['n']} f={w['f']} P={w['P']} c1={w['c1']} c2={w['c2']} "
                  f"cut={w['cutsize']}==truemax={w['truemax']} side={''.join(map(str,w['side']))}",flush=True)
    else:
        print(f"  NO counterexample: lemma (M) HOLDS on all {acc['graphs']} Family-#2 graphs (global-max cuts).",flush=True)
