"""Pin the EXACT residual gap. We have RIGOROUSLY (provable):
  (L1) bad edges never cross a K-component boundary.
  (L2) interior(C) vertices (no B-neighbor outside C) have ALL neighbors inside C.
  (L3) [frozen-max] induced cut is max cut of G[C] among boundary-frozen re-cuts (global max).
  (L4) [frozen-gamma-min, via STAB-GAMMA] induced cut minimizes Gamma_C among boundary-frozen connected-max
       re-cuts of C (global gamma-min).
The INDUCTION wants: load bound T(v)<=|C| on the induced cut. IH = load bound on gamma-min connected max cut
of any graph with < N vertices.
GAP: induced cut might not be the FULL gamma-min connected max cut of G[C]; it's only frozen-gamma-min.
Two ways to close:
  (G-a) Prove induced == full gamma-min of G[C]. (verified true; not proven)
  (G-b) Prove load bound holds for frozen-gamma-min cuts too (weaker IH won't give this directly).

MEASURE: For each component C, is the boundary-frozen-gamma-min cut (= induced) ALSO the full gamma-min?
  AND: are ALL boundary-incident vertices forced? i.e. is the frozen set = whole C (then frozen=trivially the
  only cut, induction degenerate) or proper?
We classify each component by |interior(C)| and whether frozen-max == full-max == full-gammamin, to see if the
gap is ever ACTIVE (frozen strictly weaker than full) on real data."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side, kcomponents

def build_adj(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj
def cutsize(n,adj,side):
    return sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
def gamma_of(n,adj,side):
    if not Bconn(n,adj,side): return None
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    G=0
    for (u,v) in M:
        d=bdist_restr(adj,side,u,v)
        if d<0: return None
        G+=(d+1)**2
    return G
def induced_graph(adj, Cset):
    Cl=sorted(Cset); idx={v:i for i,v in enumerate(Cl)}
    E=[(idx[u],idx[v]) for u in Cl for v in adj[u] if v in Cset and v>u]
    return len(Cl), E, Cl, idx

stats={'comps':0,'interior_eq_0':0,'frozen_lt_full_max':0,'induced_ne_fullgammamin':0,'gap_active':0}
for nn in [10,11]:
    step=1 if nn==10 else 7
    for g6 in subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::step]:
        n,E=dec(g6); adj=build_adj(n,E)
        for side in maxcut_all(n,adj):
            if not Bconn(n,adj,side): continue
            st=struct_for_side(n,adj,side)
            if st is None: continue
            M,ell,T,mu,cyc=st
            comps,find=kcomponents(n,cyc)
            pos=[set(v for v in C if T[v]>0) for C in comps.values() if any(T[v]>0 for v in C)]
            if len(pos)<=1: continue
            for Cset in pos:
                stats['comps']+=1
                m,EC,Cl,idx=induced_graph(adj,Cset); adjc=build_adj(m,EC)
                interior=[v for v in Cset if not any(w not in Cset and side[v]!=side[w] for w in adj[v])]
                if len(interior)==0: stats['interior_eq_0']+=1
                # full max cut size of G[C]
                fullmax=max(cutsize(m,adjc,s) for s in maxcut_all(m,adjc))
                # induced cut size
                cur=[side[v] for v in Cl]
                indsize=sum(1 for u in range(m) for v in adjc[u] if v>u and cur[u]!=cur[v])
                if indsize<fullmax: stats['frozen_lt_full_max']+=1
                # full gamma-min of G[C]
                best=None
                for s in maxcut_all(m,adjc):
                    if cutsize(m,adjc,s)!=fullmax: continue
                    g=gamma_of(m,adjc,s)
                    if g is None: continue
                    best=g if best is None else min(best,g)
                indgamma=gamma_of(m,adjc,cur)
                if best is not None and indgamma!=best:
                    stats['induced_ne_fullgammamin']+=1
                # gap active = there EXISTS a boundary-unfrozen connected max cut of G[C] with strictly
                # smaller gamma than induced (would need G-a to rule out)
                gapactive=False
                for s in maxcut_all(m,adjc):
                    if cutsize(m,adjc,s)!=fullmax: continue
                    g=gamma_of(m,adjc,s)
                    if g is None: continue
                    if g<indgamma:
                        gapactive=True
                if gapactive: stats['gap_active']+=1
            break
    print(f"N={nn} done: {stats}",flush=True)
print("FINAL", stats)
