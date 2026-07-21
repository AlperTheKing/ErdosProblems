#!/usr/bin/env python3
import random,sys,networkx as nx
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from test_wrapped_n2 import evaluate

def tree_from_prufer(n,rng):
    if n==1:return nx.empty_graph(1)
    seq=[rng.randrange(n) for _ in range(n-2)]; deg=[1]*n
    for x in seq:deg[x]+=1
    G=nx.Graph();G.add_nodes_from(range(n))
    for x in seq:
        leaf=next(i for i,d in enumerate(deg) if d==1)
        G.add_edge(leaf,x);deg[leaf]-=1;deg[x]-=1
    a=[i for i,d in enumerate(deg) if d==1];G.add_edge(*a);return G

def make(rng):
    g=rng.randint(5,14); q=rng.randint(2,8)
    G=nx.cycle_graph(g); T=tree_from_prufer(q,rng); mp={v:g+v for v in T}
    G.add_edges_from((mp[u],mp[v]) for u,v in T.edges())
    # Attach 2..min(q,5) distinct H vertices, each to one K root.
    ac=rng.randint(2,min(q,5)); hv=rng.sample(range(q),ac); roots=[]
    for j,v in enumerate(hv):
        valid=[]
        for a in range(g):
            G.add_edge(g+v,a)
            cyc=nx.cycle_basis(G)
            ok=cyc and min(map(len,cyc))>=g
            G.remove_edge(g+v,a)
            if ok:valid.append(a)
        if not valid:return None
        a=rng.choice(valid);roots.append(a);G.add_edge(g+v,a)
    # Optional independent pendant tails on cycle roots or H vertices.
    for _ in range(0):
        base=rng.randrange(g+q); L=rng.randint(1,4)
        for _ in range(L):
            w=len(G);G.add_edge(base,w);base=w
    return G

def main():
 rng=random.Random(14420260718); residual=0; best=None
 for it in range(20000):
    G=make(rng)
    if G is None or not nx.is_connected(G):continue
    rec=evaluate(G)
    if rec is None:continue
    residual+=1; slack,data=rec
    if best is None or slack<best[0]:
        line=nx.to_graph6_bytes(nx.convert_node_labels_to_integers(G),header=False).decode().strip()
        best=(slack,line,data);print('best',it,residual,best,flush=True)
    if slack<0:break
 print('done residual',residual,'best',best)
if __name__=='__main__':main()

