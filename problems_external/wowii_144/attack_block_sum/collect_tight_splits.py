#!/usr/bin/env python3
"""Collect the first exact equality splits for the W144 1-sum rooted bound."""
from __future__ import annotations
import itertools,json,sys
from pathlib import Path
import networkx as nx
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'attack_ind2_multicycle'))
from analyze_tight_deletions import records,girth,center_depth
from audit_block_sum import tree_order


def shortest_cycle_distance(H,v,g):
    D=nx.single_source_shortest_path_length(H,v);best=len(H)+1;witness=None
    for S in itertools.combinations(H.nodes(),g):
        J=H.subgraph(S)
        if J.number_of_edges()==g and nx.is_connected(J) and all(J.degree[x]==2 for x in J):
            q=min(D[x] for x in S)
            if q<best:best=q;witness=sorted(S)
    assert witness is not None
    return best,witness


def center_side(C,A,B,v):
    left=set(C)&(set(A)-{v});right=set(C)&(set(B)-{v})
    if left and right:return 'both_nonroot' # should be impossible
    if left:return 'side1'
    if right:return 'side2'
    return 'cut_vertex'

out=[]
seen_splits=set()
for n in range(5,14):
    for codeb,G in records(n):
        g=girth(G)
        if g is None or g<5:continue
        e,C=center_depth(G);target=g-1+e
        for v in sorted(nx.articulation_points(G)):
            comps=[set(Q) for Q in nx.connected_components(nx.subgraph_view(G,filter_node=lambda x,v=v:x!=v))]
            for A0 in comps:
                for A in (A0,set(G)-A0-{v}):
                    B=set(G)-A-{v};X=G.subgraph(A|{v}).copy();Y=G.subgraph(B|{v}).copy()
                    if girth(X)!=g:continue
                    splitkey=(codeb.decode(),v,tuple(sorted(X)))
                    if splitkey in seen_splits:continue
                    seen_splits.add(splitkey)
                    rho1=tree_order(X,v);rho2=tree_order(Y,v);rooted=rho1+rho2-1
                    if rooted!=target:continue
                    R1=nx.eccentricity(X,v);R2=nx.eccentricity(Y,v)
                    h,K=shortest_cycle_distance(X,v,g)
                    basic=max(R1+1,g-1+h)+R2
                    gx=girth(X);gy=girth(Y)
                    ex,Cx=center_depth(X);ey,Cy=center_depth(Y)
                    out.append({'index':len(out)+1,'graph6':codeb.decode(),'order':n,'edges':[sorted(z) for z in G.edges()],
                                'cut_vertex':v,'side1':sorted(X),'side2':sorted(Y),'g':g,'eta':e,
                                'global_center':sorted(C),'center_side':center_side(C,X,Y,v),
                                'R1':R1,'R2':R2,'rho1':rho1,'rho2':rho2,'rooted_sum':rooted,
                                'target':target,'side1_kind':'cyclic','side2_kind':'cyclic' if gy else 'tree',
                                'g1':gx,'g2':gy,'eta1':ex,'eta2':ey,'center1':sorted(Cx),'center2':sorted(Cy),
                                'd_root_shortest_cycle':h,'shortest_cycle':K,'basic_geodesic_cycle_bound':basic,
                                'basic_deficit':target-basic})
                    if len(out)==20:break
                if len(out)==20:break
            if len(out)==20:break
        if len(out)==20:break
    if len(out)==20:break
(HERE/'tight_splits_first20.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
