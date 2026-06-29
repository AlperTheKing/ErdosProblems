"""M-HUNT chord-rich: triangle-free graphs that ACTUALLY produce P-contained chords,
verified GLOBAL maximum via maxcut_all (exact, N<=24).

Family #1 (pure odd-cycle blow-ups) yields zero P-contained chords (a single odd cycle has one
monochromatic part-pair => one bad-edge bundle => no other bad edges to serve as chords on P).
To genuinely stress lemma (M) we need graphs where two bad edges have geodesics that are contiguous
subpaths of P and interior-overlap. Construction:

  build_pd2(pend,chords): a path 0..pend + a parity-matched detour making f=(0,pend) a
  unique-geodesic bad edge on the parity cut, plus chords realized as length-2 alternating paths
  a-w-b via a fresh vertex w (triangle-free), each contributing a bad edge whose geodesic is the
  P-subpath [a..b] when (b-a) is even. We brute chord layouts (nested/crossing/chaining) and
  verify global-max EXACTLY via maxcut_all.

A hit requires a connected-B GLOBAL MAX cut (size==true max) with a P-contained interior-overlap.
Overlaps on non-global (locally-max) cuts are NEAR-MISSES.
EXACT Fraction via struct_for_side. Run from .../problems/23/writeup."""
import itertools
from _h import maxcut_all
from _satzmu_conn import struct_for_side
from _wf_mhunt_1 import find_overlaps_on_cut, cutsize

def adj_of(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E:
        a,b=min(a,b),max(a,b); adj[a].add(b); adj[b].add(a)
    return adj
def tri_free(n,adj):
    for u in range(n):
        for v in adj[u]:
            if v>u and (adj[u]&adj[v]): return False
    return True

def build_pd2(pend, chord_pairs):
    E=[(i,i+1) for i in range(pend)]
    nxt=pend+1
    det=[0]
    for _ in range(pend-1):
        det.append(nxt); nxt+=1
    det.append(pend)
    for a,b in zip(det,det[1:]): E.append((min(a,b),max(a,b)))
    E.append((0,pend))  # bad edge f
    for (a,b) in chord_pairs:
        if (b-a)%2!=0: continue
        w=nxt; nxt+=1
        E.append((a,w)); E.append((w,b))
    return nxt, sorted(set((min(a,b),max(a,b)) for a,b in E))

def scan_graph(n,E,name,acc,Ncap=24):
    """Single maxcut_all + full 2^(n-1) brute. Records: overlaps on GLOBAL-max cuts (witness) and
    overlaps on SUB-max cuts (near-miss). EXACT."""
    if n>Ncap: return
    adj=adj_of(n,E)
    if not tri_free(n,adj): return
    cuts=maxcut_all(n,adj); truemax=cutsize(n,adj,cuts[0])
    for m in range(1<<(n-1)):
        s=[(m>>v)&1 for v in range(n)]
        c=cutsize(n,adj,s)
        st,ov=find_overlaps_on_cut(n,adj,s)
        if st!='ok' or not ov: continue
        if c==truemax:
            acc['nm_global']+=1
            if acc['witness'] is None:
                acc['witness']=dict(name=name,n=n,side=s[:],truemax=truemax,
                                    edges=sorted(E),rec=ov[0],allrecs=ov)
        else:
            acc['nm_sub']+=1

if __name__=="__main__":
    print("=== M-HUNT chord-rich: exact-global-max stress of lemma (M) ===",flush=True)
    acc={'witness':None,'nm_global':0,'nm_sub':0}
    layouts=[]
    for pend in [6,8,10,12]:
        evens=[(a,b) for a in range(0,pend+1) for b in range(a+2,pend+1) if (b-a)%2==0]
        for c1,c2 in itertools.combinations(evens,2):
            layouts.append((pend,[c1,c2]))
        for tri in itertools.combinations(evens,3):
            if sum(b-a for a,b in tri)>16: continue
            layouts.append((pend,list(tri)))
    print(f"  layouts: {len(layouts)}",flush=True)
    tested=0
    for pend,chords in layouts:
        n,E=build_pd2(pend,chords)
        if n>24: continue
        scan_graph(n,E,f"pd2(pend={pend},{chords})",acc)
        tested+=1
        if tested%300==0:
            print(f"    ...tested {tested} overlap_on_GLOBAL={acc['nm_global']} overlap_on_SUB(nearmiss)={acc['nm_sub']}"
                  + (" WITNESS!" if acc['witness'] else ""),flush=True)
        if acc['witness'] is not None:
            w=acc['witness']
            print(f"  *** GLOBAL-MAX OVERLAP: {w['name']} N={w['n']} truemax={w['truemax']}",flush=True)
            print(f"      side={w['side']} f={w['rec']['f']} P={w['rec']['P']} c1={w['rec']['c1']} c2={w['rec']['c2']}",flush=True)
            break
    print(f"\n  tested={tested}",flush=True)
    print(f"  overlaps on GLOBAL-max cuts = {acc['nm_global']}   overlaps on SUB-max cuts (near-miss) = {acc['nm_sub']}",flush=True)
    if acc['witness']:
        w=acc['witness']
        print(f"  WITNESS {w['name']} N={w['n']} truemax={w['truemax']}",flush=True)
        print(f"  WITNESS side={w['side']}",flush=True)
        print(f"  WITNESS edges={w['edges']}",flush=True)
        print(f"  WITNESS rec={w['rec']}",flush=True)
    else:
        print("  NO verified-global-max P-contained interior-overlap (chord-rich family).",flush=True)
