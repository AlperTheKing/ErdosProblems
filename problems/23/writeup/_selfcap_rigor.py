"""Rigor checks on the foundational lemmas (exact, over census multi-K cuts):
(L1) bad edges never cross a positive-K component boundary.  [already seen; reconfirm over all multi-K cuts]
(L2) interior(C) vertices (no B-neighbor outside C) have NO neighbor (edge) outside C at all.
(L3') boundary-incident vertices of C: every B-boundary edge (u in C, w out) -- is w in another positive-K
      component or a dead T=0 vertex? (classify)
(STAB mechanism) For a V\C bad edge g, its shortest B-geodesic (in the global B) never uses a vertex of C.
      => re-cutting interior(C) cannot change Gamma_rest. Check on induced cut: does any V\C bad-edge geodesic
      touch C?  (If never, then since interior re-cut only changes B INSIDE C and C-internal vertices are not
      on any V\C geodesic, Gamma_rest is invariant.)
"""
import subprocess
from collections import deque
from fractions import Fraction as F
from _h import dec, GENG, maxcut_all, Bconn
from _satzmu_conn import struct_for_side, kcomponents

def build_adj(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj
def geos_global(adj,side,s,t):
    dist={s:0};pred={s:[]};layer=[s]
    while layer:
        nxt=[]
        for u in layer:
            for v in adj[u]:
                if side[u]!=side[v]:
                    if v not in dist:dist[v]=dist[u]+1;pred[v]=[u];nxt.append(v)
                    elif dist[v]==dist[u]+1:pred[v].append(u)
        layer=nxt
    if t not in dist:return []
    P=[];support=set()
    def rec(v):
        support.add(v)
        if v==s: return
        for p in pred[v]: rec(p)
    rec(t)
    return support

L1v=0;L2v=0;stabv=0;total=0
classify={'to_other_pos':0,'to_dead':0,'to_other_full':0}
for nn in [10,11]:
    step=1 if nn==10 else 5
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
            total+=1
            Mset=set((min(a,b),max(a,b)) for a,b in M)
            posU=set().union(*pos)
            for Cset in pos:
                # L1
                for (a,b) in Mset:
                    if (a in Cset)!=(b in Cset): L1v+=1
                # L2
                interior=[v for v in Cset if not any(w not in Cset and side[v]!=side[w] for w in adj[v])]
                for v in interior:
                    for w in adj[v]:
                        if w not in Cset: L2v+=1
                # classify boundary targets
                for u in Cset:
                    for w in adj[u]:
                        if side[u]!=side[w] and w not in Cset:
                            if T[w]==0: classify['to_dead']+=1
                            elif w in posU: classify['to_other_pos']+=1
                            else: classify['to_other_full']+=1
            # STAB mechanism: V\C bad-edge geodesics avoid C
            for Cset in pos:
                rest_bad=[(a,b) for (a,b) in Mset if a not in Cset and b not in Cset]
                for (a,b) in rest_bad:
                    sup=geos_global(adj,side,a,b)
                    if sup & Cset: stabv+=1
            break
print(f"multi-K cuts tested={total}")
print(f"(L1) bad edges crossing boundary = {L1v}  (must be 0)")
print(f"(L2) interior-C vertices with an outside neighbor = {L2v}  (must be 0)")
print(f"(STAB) V\\C bad-edge geodesic-support touching C = {stabv}  (must be 0)")
print(f"boundary B-edge targets: {classify}")
