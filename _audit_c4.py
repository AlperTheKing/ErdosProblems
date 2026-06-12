import networkx as nx
from itertools import combinations
import random

def min_maximal_matching(G):
    edges = list(G.edges())
    m = len(edges)
    best = m+1
    nodes=list(G.nodes())
    # greedy upper bound to prune
    for r in range(1, m+1):
        if r>=best: break
        found=False
        for S in combinations(edges, r):
            used=set(); ok=True
            for u,v in S:
                if u in used or v in used: ok=False;break
                used.add(u); used.add(v)
            if not ok: continue
            maximal=True
            for (a,b) in edges:
                if a not in used and b not in used:
                    maximal=False;break
            if maximal:
                best=r;found=True;break
        if found:break
    return best

def harmonic_index(G):
    s=0.0
    for u,v in G.edges():
        s += 2.0/(G.degree(u)+G.degree(v))
    return s

def check(G,label):
    if G.number_of_nodes()<2 or not nx.is_connected(G): return None
    if G.number_of_edges()>26: return None  # keep mm brute force feasible
    mm=min_maximal_matching(G); H=harmonic_index(G)
    return (mm,H,H-mm,label)

random.seed(1)
worst=(99,None)
viol=[]
families=[]
# structured: complete split graphs, double stars, friendship, wheels, books, spiders, coronas
for n in range(3,15):
    families.append((nx.path_graph(n),"P%d"%n))
    families.append((nx.cycle_graph(n),"C%d"%n))
    families.append((nx.star_graph(n),"star%d"%n))
    families.append((nx.wheel_graph(n),"wheel%d"%n))
    if n>=4: families.append((nx.complete_graph(n),"K%d"%n))
for k in range(1,7):
    families.append((nx.complete_bipartite_graph(k,k),"K%d,%d"%(k,k)))
    families.append((nx.complete_bipartite_graph(1,k),"K1,%d"%k))
    families.append((nx.complete_bipartite_graph(2,k),"K2,%d"%k))
    families.append((nx.complete_bipartite_graph(k,k+1),"K%d,%d"%(k,k+1)))
# friendship / windmills, books
for k in range(1,6):
    try: families.append((nx.windmill_graph(k,3),"windmill(%d,3)"%k))
    except Exception: pass
# double stars S(a,b): two centers joined, a and b leaves
for a in range(1,6):
    for b in range(1,6):
        G=nx.Graph(); G.add_edge('x','y')
        for i in range(a): G.add_edge('x','a%d'%i)
        for j in range(b): G.add_edge('y','b%d'%j)
        families.append((G,"DS(%d,%d)"%(a,b)))
# random graphs adversarial
for trial in range(4000):
    n=random.randint(4,13)
    p=random.random()*0.7+0.1
    G=nx.gnp_random_graph(n,p,seed=trial)
    if nx.is_connected(G) and G.number_of_edges()<=24:
        families.append((G,"gnp%d"%trial))
# random regular-ish and trees
for trial in range(1500):
    n=random.randint(4,14)
    G=nx.random_labeled_tree(n,seed=trial)
    families.append((G,"tree%d"%trial))

for G,label in families:
    r=check(G,label)
    if r is None: continue
    mm,H,margin,lab=r
    if mm>H+1e-9:
        viol.append(r)
    if margin<worst[0]:
        worst=(margin,r)

print("C4 large probe: families checked, violations=%d"%len(viol))
for v in viol[:20]: print("  VIOLATION",v)
print("tightest margin (H-mu*):", round(worst[0],5), worst[1])
EOF
