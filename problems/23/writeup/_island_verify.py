"""Rigorously verify whether the C5-island in C5+Myc(C7)+bridge is a genuine Q-only bad-carrying
K-component on a GAMMA-MIN connected max cut. N=20 is too big for full maxcut_all(2^19),
but the graph is a near-disjoint union (bridge 0-5), so we can reason:
 maxcut(G) = maxcut(C5 island side) + maxcut(Myc(C7) side) adjusted by the single bridge edge.
We compute true maxcut via an ILP-free argument: enumerate the two blocks' cuts independently
(C5: 2^5, Myc(C7)=15 vtx: 2^15) and combine, choosing bridge orientation to maximize.
Then among ALL max cuts that are B-connected, find min Gamma and check the island component.
Also test C-alltie hypothesis: is there a saturated v with a dead B-neighbor z, Kcomp(v) disjoint from O?
"""
from fractions import Fraction as F
from collections import deque
from itertools import product
from _bdef_construct import mycielski, union_disjoint, add_edges, Cn
from _h import bdist_restr, geos

isl_n, isl_E = 5, Cn(5)
myc_n, myc_E = mycielski(7, Cn(7))
n, E = union_disjoint((isl_n,isl_E),(myc_n,myc_E))
n, E = add_edges((n,E),[(0,5)])   # bridge between island vtx0 and myc vtx0(=global 5)
adj=[set() for _ in range(n)]
for a,b in E: adj[a].add(b); adj[b].add(a)
edges=[(min(a,b),max(a,b)) for a,b in E]
edges=sorted(set(edges))

def cutsize(side):
    return sum(1 for u,v in edges if side[u]!=side[v])

# True maxcut by block independence. Island vertices 0..4, myc vertices 5..19. Bridge (0,5).
# For each island cut and myc cut, total = islandcut + myccut + (1 if side[0]!=side[5] else 0).
def block_cuts(verts, bedges):
    res=[]
    base=verts[0]
    for bits in product([0,1],repeat=len(verts)):
        s={verts[i]:bits[i] for i in range(len(verts))}
        c=sum(1 for u,v in bedges if s[u]!=s[v])
        res.append((s,c))
    return res

isl_verts=list(range(0,5)); isl_edges=[(min(a,b),max(a,b)) for a,b in isl_E]
myc_verts=list(range(5,20)); myc_edges=[(min(a,b),max(a,b)) for a,b in edges if a>=5 and b>=5]
# island internal best
isl_best=max(c for _,c in block_cuts(isl_verts,isl_edges))
myc_best=max(c for _,c in block_cuts(myc_verts,myc_edges))
print("island maxcut(internal)=",isl_best," (C5 -> 4)")
print("myc(C7) maxcut(internal)=",myc_best)
# total maxcut: can we get island=4, myc=best, bridge cut all simultaneously? bridge only constrains side0 vs side5.
# Both blocks have cuts achieving their max with side0 free / side5 free, so bridge can be cut. Total = isl_best+myc_best+1.
true_max = isl_best+myc_best+1
print("true maxcut(G)=",true_max)

def Bconn(side):
    seen={0};q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if side[u]!=side[v] and v not in seen: seen.add(v);q.append(v)
    return len(seen)==n

def gamma_and_struct(side):
    if not Bconn(side): return None
    M=[(u,v) for u,v in edges if side[u]==side[v]]
    G=0
    for (u,v) in M:
        d=bdist_restr(adj,side,u,v)
        if d<0: return None
        G+=(d+1)**2
    return G,M

# enumerate ALL max cuts (island free 2^5 x myc-cuts achieving myc_best, but that's many). Instead:
# We only need: is there ANY connected max cut with Gamma < Gamma(island-split)? And does island-split
# achieve the maxcut? Build the island-split cut explicitly and a 'merged' alternative.
# Island-split: island internally cut as C5 (one bad edge), bridge cut, myc cut optimally.
# Use loads() side we already found = a max cut with cutsize 28? but true_max computed above:
print("Is cutsize 28 the true max? true_max=",true_max)
