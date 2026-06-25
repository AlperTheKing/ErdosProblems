"""Verify the per-B-component reduction is a VALID sub-instance:
For a max cut (X,Y) of triangle-free G, take a B-component K (vertex set W, |W|=n_j).
The induced subgraph G[W] has:
  - all its B-edges (cut edges within W) + all bad edges with both endpoints in W.
  Bad edges with an endpoint outside W: NONE, since a bad edge uv has d_B(u,v)<inf => same B-comp.
Claim to verify:
  (i) (X cap W, Y cap W) is a MAX cut of G[W]  (so the local structure is a valid max-cut instance);
  (ii) d_B(u,v) computed in G[W] equals d_B(u,v) in G (since B-paths stay in the component);
  (iii) G[W] triangle-free (inherited).
If (i)-(iii) hold, then Gamma_j = Gamma(G[W]) and proving Gamma<=n^2 for B-CONNECTED triangle-free graphs
suffices. Test (i): is the restricted cut a max cut of G[W]?
"""
import verify_D25_lemma16 as L
from collections import deque
import flag_engine as fe

def adjset(n,A): return [set(v for v in range(n) if (A[u]>>v)&1) for u in range(n)]
def maxcut_val(n,adj,side):
    return sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
def all_maxcuts(n,adj):
    best=-1; cuts=[]
    for mask in range(1<<(n-1)):
        side=[(mask>>u)&1 for u in range(n)]
        c=maxcut_val(n,adj,side)
        if c>best: best=c; cuts=[side]
        elif c==best: cuts.append(side)
    return best,cuts

def induced_maxcut(verts, adj):
    """max cut of induced subgraph on `verts` (list)."""
    k=len(verts); idx={v:i for i,v in enumerate(verts)}
    iadj=[[] for _ in range(k)]
    for v in verts:
        for w in adj[v]:
            if w in idx: iadj[idx[v]].append(idx[w])
    best=-1
    for mask in range(1<<(max(0,k-1))):
        s=[(mask>>i)&1 for i in range(k)]
        c=sum(1 for i in range(k) for j in iadj[i] if j>i and s[i]!=s[j])
        if c>best: best=c
    return best

def check(N,A,name=""):
    adj=adjset(N,A)
    E=[(u,v) for u in range(N) for v in adj[u] if v>u]
    if not E: return None
    mc,cuts=all_maxcuts(N,adj)
    bad_local_notmax=0; total_comp=0
    for side in cuts[:1]:  # test first max cut
        adjB=[set() for _ in range(N)]
        for (u,v) in E:
            if side[u]!=side[v]: adjB[u].add(v); adjB[v].add(u)
        comp=[-1]*N; nc=0
        for s in range(N):
            if comp[s]<0:
                comp[s]=nc; q=deque([s])
                while q:
                    u=q.popleft()
                    for w in adjB[u]:
                        if comp[w]<0: comp[w]=nc; q.append(w)
                nc+=1
        for j in range(nc):
            verts=[v for v in range(N) if comp[v]==j]
            if len(verts)<2: continue
            total_comp+=1
            # restricted cut value on G[verts]
            idx=set(verts)
            rv=sum(1 for u in verts for v in adj[u] if v>u and v in idx and side[u]!=side[v])
            mcj=induced_maxcut(verts,adj)
            if rv<mcj: bad_local_notmax+=1
    return total_comp, bad_local_notmax

if __name__=="__main__":
    for name,(N,A) in [("Petersen",L.petersen()),("K23-N13",L.gpt_k23()),("C5[2]",L.c5n(2))]:
        r=check(N,A,name)
        print(f"{name:10s}: comps={r[0]} restricted-cut-NOT-max={r[1]}")
    for N in [5,6,7,8,9]:
        states=fe.enumerate_graphs(N,triangle_free=True)
        tc=0; bad=0
        for (n,A) in states:
            r=check(n,A)
            if r: tc+=r[0]; bad+=r[1]
        print(f"N={N}: components tested={tc}, restricted cut NOT a max cut of G[comp]: {bad}")
    print("DONE")
