"""Verify Codex's block-190 positive-extra 'counterexamples' (N=26 nested + cut leaves) are NOT global max
cuts -> they do not refute (M) (which holds on global-max: _chord_overlap_maxness 0 interior-overlap on max).
Reconstruct base (path 0..12, detour, bad chords (0,8),(0,12),(2,6)) parity + leaf attachments; check for ANY
cut-increasing flip (single vertex + the base improving subset). If a flip increases cut, cut is non-max."""
from _M_tailswitch_gate import build_pd, tri_free
from _h import Bconn
import itertools

def adj_from(n, edges):
    adj=[set() for _ in range(n)]
    for a,b in edges: adj[a].add(b); adj[b].add(a)
    return adj
def cutsize(n,adj,s): return sum(1 for u in range(n) for v in adj[u] if v>u and s[u]!=s[v])
def add_cut_leaves(n, edges, side, attachments):
    edges=list(edges); side=list(side)
    for parent,count in attachments:
        for _ in range(count):
            leaf=n; n+=1; edges.append((min(parent,leaf),max(parent,leaf))); side.append(side[parent]^1)
    return n, sorted(set(edges)), side
def best_improving(n,adj,s,maxk=2):
    cs=cutsize(n,adj,s); best=None
    cand=list(range(n))
    for k in range(1,maxk+1):
        for combo in itertools.combinations(cand,k):
            s2=s[:]
            for v in combo: s2[v]^=1
            c=cutsize(n,adj,s2)
            if c>cs and (best is None or c>best[1]): best=(combo,c)
        if best: break
    return cs,best
def improve_with_leaves(n,adj,s,core):
    # flip core path vertices PLUS all pendant leaves attached to them (keep leaf edges cut)
    cs=cutsize(n,adj,s); s2=s[:]
    flip=set(core)
    for v in list(core):
        for w in adj[v]:
            if len(adj[w])==1: flip.add(w)  # pendant leaf
    for v in flip: s2[v]^=1
    return cs, cutsize(n,adj,s2), sorted(flip)

# base: pend=12, chords (0,8),(2,6) [bad-edge (0,12)=f is the (0,pend) edge already]
n0,E0=build_pd(12,[(0,8),(2,6)])
s0=[v%2 for v in range(n0)]
adj0=adj_from(n0,E0)
print(f"BASE N={n0} tri-free={tri_free(n0,adj0)} Bconn={Bconn(n0,adj0,s0)} cutsize={cutsize(n0,adj0,s0)}")
cs,bi=best_improving(n0,adj0,s0,maxk=3)
print(f"  base: cutsize={cs} improving-flip(<=3 vtx)={bi}  => {'NON-MAX' if bi else 'no small improving flip found'}")
for attach in [[(0,1)],[(0,3),(8,3)]]:
    n,E,s=add_cut_leaves(n0,E0,s0,attach)
    adj=adj_from(n,E)
    cs,c2,flip=improve_with_leaves(n,adj,s,[0,1,2])
    print(f"AUG +leaves{attach}: N={n} Bconn={Bconn(n,adj,s)} cutsize={cs} -> flip {{0,1,2}}+leaves {flip} gives cut={c2} => {'NON-MAX (improving move exists; does not refute M)' if c2>cs else 'NO gain (would be concerning)'}")
