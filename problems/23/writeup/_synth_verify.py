"""Fully independent from-scratch verifier for claim U. No census_GPI import."""
from fractions import Fraction
from itertools import product
from collections import deque

def dec_g6(s):
    # nauty graph6 decoder
    data = [ord(c)-63 for c in s]
    n = data[0]
    bits = []
    for d in data[1:]:
        for k in range(5,-1,-1):
            bits.append((d>>k)&1)
    adj = [[0]*n for _ in range(n)]
    idx = 0
    for j in range(1,n):
        for i in range(j):
            if idx < len(bits) and bits[idx]:
                adj[i][j]=adj[j][i]=1
            idx += 1
    edges = [(i,j) for j in range(n) for i in range(j) if adj[i][j]]
    return n, adj, edges

def is_triangle_free(n, adj):
    for i in range(n):
        for j in range(i+1,n):
            if adj[i][j]:
                for k in range(j+1,n):
                    if adj[i][k] and adj[j][k]:
                        return False
    return True

def all_max_cuts(n, edges):
    best = -1; cuts=[]
    for mask in range(1<<(n-1)):  # fix vertex 0 to side 0
        side=[(mask>>i)&1 for i in range(n-1)]
        side=[0]+side
        cv=sum(1 for (u,v) in edges if side[u]!=side[v])
        if cv>best:
            best=cv; cuts=[side[:]]
        elif cv==best:
            cuts.append(side[:])
    return best, cuts

def B_edges(edges, side):
    # bipartite (cut) edges = good edges; bad = monochromatic
    return [(u,v) for (u,v) in edges if side[u]!=side[v]]

def bad_edges(edges, side):
    return [(u,v) for (u,v) in edges if side[u]==side[v]]

def B_connected_spanning(n, side, bedges):
    # the "B" graph = cut edges; require it spans all n vertices and is connected
    g=[[] for _ in range(n)]
    for (u,v) in bedges:
        g[u].append(v); g[v].append(u)
    seen=[False]*n
    dq=deque([0]); seen[0]=True; cnt=1
    while dq:
        x=dq.popleft()
        for y in g[x]:
            if not seen[y]:
                seen[y]=True; cnt+=1; dq.append(y)
    return cnt==n

def bfs_dist_and_geos(n, bedges, s, t):
    # shortest path s->t in B-graph; return dist and all shortest paths (as vertex lists)
    g=[[] for _ in range(n)]
    for (u,v) in bedges:
        g[u].append(v); g[v].append(u)
    dist=[-1]*n; dist[s]=0
    parents=[[] for _ in range(n)]
    dq=deque([s])
    while dq:
        x=dq.popleft()
        for y in g[x]:
            if dist[y]==-1:
                dist[y]=dist[x]+1; parents[y]=[x]; dq.append(y)
            elif dist[y]==dist[x]+1:
                parents[y].append(x)
    if dist[t]==-1:
        return -1, []
    # backtrack all shortest paths
    paths=[]
    def back(node, acc):
        if node==s:
            paths.append([s]+acc[::-1])
            return
        for p in parents[node]:
            back(p, acc+[node])
    back(t, [])
    return dist[t], paths

def gamma_min_cut(n, adj, edges, cuts):
    # among all max cuts, those with connected-spanning B and >=1 bad edge; pick min Gamma
    best=None
    for side in cuts:
        bedges=B_edges(edges, side)
        if not B_connected_spanning(n, side, bedges):
            continue
        bad=bad_edges(edges, side)
        if not bad:
            continue
        # compute ell and Gamma
        ell={}; ok=True
        for (u,v) in bad:
            d,_=bfs_dist_and_geos(n, bedges, u, v)
            if d==-1:
                ok=False; break
            ell[(u,v)]=d+1
        if not ok: continue
        Gamma=sum(e*e for e in ell.values())
        if best is None or Gamma<best[0]:
            best=(Gamma, side, bad, ell, bedges)
    return best

def T_uniform(n, bad, ell, bedges):
    T=[Fraction(0) for _ in range(n)]
    for f in bad:
        u,v=f
        d, paths = bfs_dist_and_geos(n, bedges, u, v)
        nf=len(paths)
        share=Fraction(ell[f], nf)
        for P in paths:
            for w in P:
                T[w]+=share
    return T

def check(g6, label=""):
    n, adj, edges = dec_g6(g6)
    tf = is_triangle_free(n, adj)
    best, cuts = all_max_cuts(n, edges)
    res = gamma_min_cut(n, adj, edges, cuts)
    if res is None:
        return (g6, label, n, tf, None, None, None, None, "no gamma-min connected-B cut with bad edges")
    Gamma, side, bad, ell, bedges = res
    T = T_uniform(n, bad, ell, bedges)
    maxT = max(T)
    K = n + (n*n - Gamma)
    slack = K - maxT
    viol = maxT > K
    return (g6, label, n, tf, Gamma, K, maxT, slack, viol)

if __name__=="__main__":
    import sys
    cases = [
        ("DUW","C5"),
        ("F?bd_","?"),
        ("G?`F`w","n8 witness"),
        ("K?ABBBwerwBw","n12 min-slack worst"),
        ("L?`DAboU`w@{hS","n13 partial worst"),
        ("H?bB@_W","C9"),
        ("I?rFf_{N?","C5[2]"),
        ("J?AEB?oE?W?","C11"),
    ]
    for g6,lab in cases:
        out=check(g6,lab)
        print(out)
