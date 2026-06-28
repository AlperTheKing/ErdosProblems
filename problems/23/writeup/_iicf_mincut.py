"""Dump the IICF MIN-CUT structure at tight cases (Codex's question: do min-cuts reduce to prefix/suffix
intervals inside each layer system => a finite reduction of the all-y Hall family?).
For a tight (graph,y): min cut partition (SRC side / SINK side). The Hall set U = vertices on the SINK side
(their v->SINK edge is cut). A demand (f,i,j) is on SRC side (its SRC->d edge cut) iff Corr(f,i,j) NOT subset U.
Report: U per edge intersected with each edge's layers -> is U∩(layers of f) a PREFIX/SUFFIX/contiguous interval?"""
import numpy as np, networkx as nx
from _h import dec, loads
from _layerprice import layers_of
from _iicf_test import setup, maxflow_iicf, wvals, INF

def mincut_struct(g6, info, y, label):
    L,S,N,n,triples=setup(info)
    W=wvals(L,y)
    G=nx.DiGraph()
    total=0.0
    for t,(ei,i,j,corr) in enumerate(triples):
        d=np.sqrt(max(W[ei][i],0.)*max(W[ei][j],0.))
        if d<=0: continue
        total+=d; G.add_edge('SRC',('d',t),capacity=d)
        for v in corr: G.add_edge(('d',t),('v',v),capacity=INF)
    for v in range(n):
        cap=0.5*(N-S[v])*y[v]
        if cap>0: G.add_edge(('v',v),'SINK',capacity=cap)
    if total<=0:
        print(f"  {label}: no demand"); return
    cut_val,(src,sink)=nx.minimum_cut(G,'SRC','SINK')
    U=sorted(v for kind,v in [(x[0],x[1]) for x in sink if isinstance(x,tuple) and x[0]=='v'])
    Uset=set(U)
    print(f"  {label} {g6}: total demand={total:.4f} mincut={cut_val:.4f} (tight:{abs(total-cut_val)<1e-7}) | U(sink-side vtxs)={U}")
    # per edge: U intersect layers, check contiguous / prefix / suffix
    for ei,(f,lay,pf,h) in enumerate(L):
        hit=[i for i in range(h+1) if any(v in Uset for v in lay[i])]
        full=[i for i in range(h+1) if lay[i] and all(v in Uset for v in lay[i])]
        contig = (hit==list(range(hit[0],hit[-1]+1))) if hit else True
        kind="-"
        if hit:
            if hit[0]==0 and contig: kind="PREFIX"
            elif hit[-1]==h and contig: kind="SUFFIX"
            elif contig: kind="MIDDLE-interval"
            else: kind="NON-contiguous"
        print(f"      edge {f} (h={h}): layers touched by U = {hit} [{kind}] ; layers fully in U = {full}")

if __name__=="__main__":
    # tight extremals at y=1
    for g6 in ["FCp`_","H?bB@_W","J?AEB?oE?W?"]:
        n,E=dec(g6); info=loads(n,E)
        mincut_struct(g6,info,[1.0]*n,"y=1")
    # a non-extremal at its worst-y (near-tight) — use overload-concentrated y
    for g6 in ["I?BD@g]Qo","I?ABCc]}?"]:
        n,E=dec(g6); info=loads(n,E); T=info['T']; N=n
        y=[max(float(T[v])-N,0.0)+0.01 for v in range(n)]  # concentrate on overloaded
        mincut_struct(g6,info,y,"y=overload")
