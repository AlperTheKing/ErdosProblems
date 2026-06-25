"""STRATEGY B, connected-B core. Now B is a CONNECTED bipartite graph on N vertices.
M = bad edges (within-side), each ell=d_B(u,v)+1 odd, >=5. CD holds.
Want: Gamma = sum_M ell^2 <= N^2.

Test several candidate proofs:

(A) DIAMETER/eccentricity: ell <= d_B(u,v)+1. In connected B, can we bound sum ell^2 by N^2?
    For C5[q]: B = C5[q] cut edges form... B is bipartite connected, every bad-edge d_B=4.

(B) The SHELL second-moment from a single root, summed via Cauchy.
    Pick root r. Shells S_0..S_D (D=diameter). a_i=|S_i|. sum a_i = N.
    Each bad edge uv: |d_B(r,u)-d_B(r,v)| <= ... in bipartite same-side so d_B(r,u),d_B(r,v) same parity.

(C) The eigenvalue/spectral bound (skip).

(D) MAIN TEST: is there always a root r such that the bad edges decompose by their geodesic shells and
    Gamma <= (sum_i a_i)^2 = N^2 via a 5-term product? Probably needs the actual mechanism.

We just empirically characterize the TIGHT connected-B cases (Gamma=N^2) to see what structure forces equality.
"""
import verify_D25_lemma16 as L
from collections import deque
import flag_engine as fe

def adjset(n,A): return [set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
def all_maxcuts(n,adj):
    best=-1; cuts=[]
    for mask in range(1<<(n-1)):
        side=[(mask>>u)&1 for u in range(n)]
        c=sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
        if c>best: best=c; cuts=[side]
        elif c==best: cuts.append(side)
    return best,cuts
def bdist(n,adjB,src):
    d=[-1]*n; d[src]=0; q=deque([src])
    while q:
        u=q.popleft()
        for w in adjB[u]:
            if d[w]<0: d[w]=d[u]+1; q.append(w)
    return d

def connectedB_instances(N):
    """yield (n, adjB, M, ell-list) for B-connected max-cut instances."""
    states=fe.enumerate_graphs(N,triangle_free=True)
    out=[]
    for (n,A) in states:
        adj=adjset(n,A)
        E=[(u,v) for u in range(n) for v in adj[u] if v>u]
        if not E: continue
        mc,cuts=all_maxcuts(n,adj)
        for side in cuts[:1]:
            adjB=[set() for _ in range(n)]
            for (u,v) in E:
                if side[u]!=side[v]: adjB[u].add(v); adjB[v].add(u)
            # B connected?
            seen=set([0]); q=deque([0])
            while q:
                u=q.popleft()
                for w in adjB[u]:
                    if w not in seen: seen.add(w); q.append(w)
            if len(seen)!=n: continue
            M=[(u,v) for (u,v) in E if side[u]==side[v]]
            if not M: continue
            ells=[]
            ok=True
            for (u,v) in M:
                d=bdist(n,adjB,u)[v]
                if d<4 or d%2: ok=False; break
                ells.append(d+1)
            if not ok: continue
            out.append((n,adjB,M,ells))
    return out

if __name__=="__main__":
    for N in [5,6,7,8,9,10]:
        inst=connectedB_instances(N)
        tight=[x for x in inst if sum(e*e for e in x[3])>=N*N-1e-9]
        worst=max((sum(e*e for e in x[3])/(N*N) for x in inst), default=0)
        print(f"N={N}: B-connected maxcut instances={len(inst)}, worst Gamma/N^2={worst:.4f}, #tight(Gamma=N^2)={len(tight)}")
        for (n,adjB,M,ells) in tight[:3]:
            degs=sorted(len(adjB[v]) for v in range(n))
            print(f"   tight: m={len(M)} ells={sorted(ells)} Bdeg-seq={degs}")
    print("DONE")
