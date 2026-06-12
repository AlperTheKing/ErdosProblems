import networkx as nx
from itertools import combinations
import random

def i_number(G):
    n=G.number_of_nodes(); nodes=list(G.nodes()); best=n+1
    for r in range(1,n+1):
        if r>=best: break
        for S in combinations(nodes,r):
            ok=True
            for u,v in combinations(S,2):
                if G.has_edge(u,v): ok=False;break
            if not ok: continue
            dom=set(S)
            for s in S: dom|=set(G.neighbors(s))
            if len(dom)==n: best=r; break
        if best==r: break
    return best

def mmm(G):
    edges=list(G.edges()); best=len(edges)+1
    for r in range(1,len(edges)+1):
        if r>=best: break
        for S in combinations(edges,r):
            used=set(); ok=True
            for u,v in S:
                if u in used or v in used: ok=False;break
                used.add(u);used.add(v)
            if not ok: continue
            if all((a in used or b in used) for a,b in edges):
                best=r; break
        if best==r: break
    return best

random.seed(7)
seen=[]
def isnew(G):
    for H in seen:
        if H.number_of_nodes()==G.number_of_nodes() and nx.is_isomorphic(G,H): return False
    return True

results=[]; viol=0; tight=0; tested=0
# cubic graphs n=4,6,8,10,12 (sample many random 3-regular, dedup)
for n in [4,6,8,10,12]:
    cnt=0; attempts=0
    while cnt<60 and attempts<4000:
        attempts+=1
        try: G=nx.random_regular_graph(3,n,seed=random.randint(0,10**9))
        except Exception: break
        if not nx.is_connected(G): continue
        if not isnew(G): continue
        seen.append(G.copy()); cnt+=1
        if G.number_of_edges()>20: continue
        i_=i_number(G); mm=mmm(G); tested+=1
        if i_>mm: viol+=1; print("VIOL C3 cubic n=%d i=%d mm=%d"%(n,i_,mm))
        if i_==mm: tight+=1
# also 4-regular small
for n in [5,6,8,10]:
    cnt=0; attempts=0
    while cnt<40 and attempts<3000:
        attempts+=1
        try: G=nx.random_regular_graph(4,n,seed=random.randint(0,10**9))
        except Exception: break
        if not nx.is_connected(G): continue
        if not isnew(G): continue
        seen.append(G.copy()); cnt+=1
        if G.number_of_edges()>22: continue
        i_=i_number(G); mm=mmm(G); tested+=1
        if i_>mm: viol+=1; print("VIOL C3 4reg n=%d i=%d mm=%d"%(n,i_,mm))
        if i_==mm: tight+=1
print("C3 cubic+4reg sampled: tested=%d tight(equality)=%d violations=%d"%(tested,tight,viol))
