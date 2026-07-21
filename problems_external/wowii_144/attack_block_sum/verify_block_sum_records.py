#!/usr/bin/env python3
"""Independent small-order/formula and named-record verifier for W144-BLOCK."""
from __future__ import annotations
import itertools,json
from pathlib import Path
import networkx as nx
HERE=Path(__file__).resolve().parent

def girth(G):
    best=None
    for s in G:
        d={s:0};p={s:None};q=[s]
        for x in q:
            for y in G[x]:
                if y not in d:d[y]=d[x]+1;p[y]=x;q.append(y)
                elif p[x]!=y:
                    z=d[x]+d[y]+1;best=z if best is None else min(best,z)
    return best

def inv(G):
    D=dict(nx.all_pairs_shortest_path_length(G));E={x:max(D[x].values()) for x in G};r=min(E.values());C={x for x in G if E[x]==r};eta=max(min(D[x][c] for c in C) for x in G);return D,E,r,C,eta

def cap(G,root=None):
    V=list(G);best=1
    for k in range(2,len(V)+1):
        for S in itertools.combinations(V,k):
            if root is not None and root not in S:continue
            if nx.is_tree(G.subgraph(S)):best=k
    return best

def hshort(H,v,g):
    D=nx.single_source_shortest_path_length(H,v);z=len(H)+1
    for S in itertools.combinations(H,g):
        J=H.subgraph(S)
        if J.number_of_edges()==g and nx.is_connected(J) and all(J.degree[x]==2 for x in J):z=min(z,min(D[x] for x in S))
    return z

def check_record(code,expected):
    G=nx.from_graph6_bytes(code.encode());D,E,r,C,e=inv(G);g=girth(G)
    assert (len(G),g,e,C)==expected['global']
    rows=[]
    for v in expected['delete']:
        H=G.copy();H.remove_node(v);_,_,rh,Ch,eh=inv(H);rows.append({'v':v,'girth':girth(H),'eta':eh,'center':sorted(Ch)})
        assert (girth(H),eh)==(5,1)
    return {'graph6':code,'edges':[sorted(x) for x in G.edges()],'radius':r,'tau':cap(G),'deletions':rows}

def main():
    graphs=splits=0
    for G0 in nx.graph_atlas_g():
        if len(G0)<3 or not nx.is_connected(G0):continue
        G=nx.convert_node_labels_to_integers(G0);g=girth(G)
        if g is None or g<5:continue
        D,E,r,C,e=inv(G)
        for v in nx.articulation_points(G):
            comps=[set(Q) for Q in nx.connected_components(nx.subgraph_view(G,filter_node=lambda x,v=v:x!=v))]
            for A in comps:
                B=set(G)-A-{v};X=G.subgraph(A|{v}).copy();Y=G.subgraph(B|{v}).copy();splits+=1
                DX,EX,rx,CX,ex=inv(X);DY,EY,ry,CY,ey=inv(Y);a1=EX[v];a2=EY[v]
                pred={}
                for x in X:pred[x]=max(EX[x],DX[x][v]+a2)
                for x in Y:pred[x]=max(pred.get(x,-1),max(EY[x],DY[x][v]+a1))
                assert pred==E
                rr=min(pred.values());CC={x for x in G if pred[x]==rr};assert (rr,CC)==(r,C)
                assert cap(G)==max(cap(X),cap(Y),cap(X,v)+cap(Y,v)-1)
                if girth(X) is not None:
                    gx=girth(X);assert cap(X,v)>=gx-1+hshort(X,v,gx)
                assert cap(X,v)>=EX[v]+1
                assert cap(Y,v)>=EY[v]+1
        if list(nx.articulation_points(G)):graphs+=1
    named=[check_record('F?bao',{'global':(7,5,2,{1}),'delete':[2,3]}),
           check_record('G?`e_w',{'global':(8,5,2,{7}),'delete':[2]})]
    out={'status':'PASS','atlas_cut_graphs':graphs,'atlas_oriented_component_splits':splits,'named_records':named}
    (HERE/'block_sum_record_verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
