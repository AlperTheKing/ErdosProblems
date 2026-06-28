"""Is the induced cut on a positive-K component C a GAMMA-MIN connected max cut of G[C]?
For each multi-K component C: compute induced-cut Gamma_C (sum ell^2 over internal bad edges), and compare
to the gamma-min over ALL connected max cuts of G[C]. If induced == gamma-min, induction via gamma-min applies.
Also: is induced cut even a MAX cut of G[C]? (re-confirm) And does the GLOBAL gamma-minimality force the
induced cut to be gamma-min on C? (the dead-net forcing should help here.)"""
import subprocess
from fractions import Fraction as F
from collections import deque
from _h import dec, GENG, maxcut_all, Bconn, bdist_restr
from _satzmu_conn import struct_for_side, kcomponents

def build_adj(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj

def induced_graph(adj, Cset):
    Cl=sorted(Cset); idx={v:i for i,v in enumerate(Cl)}
    E=[(idx[u],idx[v]) for u in Cl for v in adj[u] if v in Cset and v>u]
    return len(Cl), E, Cl, idx

def gammamin_of(m, EC):
    adjc=build_adj(m,EC)
    cuts=maxcut_all(m,adjc)
    best=None; maxcutsize=-1
    # max cut size
    edges=[(u,v) for u in range(m) for v in adjc[u] if v>u]
    for side in cuts:
        sz=sum(1 for u,v in edges if side[u]!=side[v])
        maxcutsize=max(maxcutsize,sz)
    for side in cuts:
        if not Bconn(m,adjc,side): continue
        Mloc=[(u,v) for u in range(m) for v in adjc[u] if v>u and side[u]==side[v]]
        if not Mloc:
            best=0 if best is None else min(best,0); continue
        G=0; ok=True
        for (u,v) in Mloc:
            d=bdist_restr(adjc,side,u,v)
            if d<0: ok=False; break
            G+=(d+1)**2
        if ok and (best is None or G<best): best=G
    return best

def induced_gamma(adj,side,Cset,M,ell,cyc):
    badin=[f for f in M if set().union(*[set(P) for P in cyc[f]])<=Cset]
    return sum(ell[f]**2 for f in badin)

bad=0; total=0; firstbad=None
for nn in [10,11]:
    step=1 if nn==10 else 9
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
                total+=1
                m,EC,Cl,idx=induced_graph(adj,Cset)
                Gind=induced_gamma(adj,side,Cset,M,ell,cyc)
                Gmin=gammamin_of(m,EC)
                if Gmin is not None and Gind!=Gmin:
                    bad+=1
                    if firstbad is None:
                        firstbad=(g6,sorted(Cset),Gind,Gmin)
            break
    print(f"N={nn} done")
print(f"total components={total}  #induced!=gammamin = {bad}")
if firstbad: print(f"FIRST: g6={firstbad[0]} C={firstbad[1]} Gamma_induced={firstbad[2]} Gamma_min(G[C])={firstbad[3]}")
