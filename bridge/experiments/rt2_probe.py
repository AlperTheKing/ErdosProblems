import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from h2_redteam2 import build, beta, has_triangle
import itertools

def conn_set(N, gens):
    S=set()
    for g in gens: S.add(g%N); S.add((-g)%N)
    S.discard(0); return S
def circ_edges(N, gens):
    S=conn_set(N,gens); E=set()
    for v in range(N):
        for s in S:
            w=(v+s)%N; E.add((min(v,w),max(v,w)))
    return sorted(E)

def degseq(N, edges):
    d=[0]*N
    for u,v in edges: d[u]+=1; d[v]+=1
    return sorted(d)

# Is Cay(Z15,{1,4,6}) isomorphic to C5[3]? Compare invariants.
def c5n(n):
    e=[]
    for p in range(5):
        q=(p+1)%5
        for j in range(n):
            for k in range(n): e.append((p*n+j,q*n+k))
    return sorted(set((min(a,b),max(a,b)) for a,b in e))

g1 = circ_edges(15,(1,4,6))
g2 = c5n(3)
print("Cay(Z15,{1,4,6}) degseq:", degseq(15,g1))
print("C5[3]            degseq:", degseq(15,g2))

# count 5-cycles? count co-degree (common nbrs) distribution over nonedges as fingerprint
def codeg_hist(N, edges):
    adj=[set() for _ in range(N)]
    for u,v in edges: adj[u].add(v); adj[v].add(u)
    from collections import Counter
    c=Counter()
    for u in range(N):
        for v in range(u+1,N):
            if v not in adj[u]:
                c[len(adj[u]&adj[v])]+=1
    return dict(sorted(c.items()))
print("Cay codeg-of-nonedge hist:", codeg_hist(15,g1))
print("C5[3] codeg-of-nonedge hist:", codeg_hist(15,g2))

# girth / number of 5-cycles via trace? quick: count induced C5? approximate by counting closed 5-walks
# Use independence number alpha as another invariant
def alpha(N, edges):
    adj=[set() for _ in range(N)]
    for u,v in edges: adj[u].add(v); adj[v].add(u)
    best=0
    # brute over subsets is 2^15 - feasible-ish; use greedy bound then exact small
    import itertools as it
    # exact via bitmask DP is heavy; do bron-kerbosch on complement
    full=set(range(N))
    def bk(R,P,X):
        nonlocal best
        if not P and not X:
            best=max(best,len(R)); return
        for v in list(P):
            comp_nb = full-adj[v]-{v}
            bk(R|{v}, P&comp_nb, X&comp_nb)
            P=P-{v}; X=X|{v}
    bk(set(), set(range(N)), set())
    return best
print("Cay alpha:", alpha(15,g1), " C5[3] alpha:", alpha(15,g2))

# the minimizing 5-set of the circulant: does removing it give a graph hom to C5? 
# print one argmin and the induced subgraph on it
adj1=[set() for _ in range(15)]
for u,v in g1: adj1[u].add(v); adj1[v].add(u)
# find a min-drop 5set and show induced edges
bG=beta(15, build(15,g1), list(range(15)))
best=None; bestd=99
for S in itertools.combinations(range(15),5):
    rem=[v for v in range(15) if v not in S]
    d=bG-beta(15,build(15,g1),rem)
    if d<bestd: bestd=d; best=S
ind=[(a,b) for a,b in itertools.combinations(best,2) if b in adj1[a]]
print(f"Cay min-drop={bestd} argmin5set={best} induced edges on it={ind}")
