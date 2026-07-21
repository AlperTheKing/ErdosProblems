#!/usr/bin/env python3
"""Exact audit of the direct W144 1-sum rooted-tree bound and end-block phi deletion."""
from __future__ import annotations
import argparse,itertools,json,sys
from pathlib import Path
import networkx as nx

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'attack_ind2_multicycle'))
from analyze_tight_deletions import records,girth,center_depth,cycle_rank


def tree_order(H: nx.Graph, root: int|None=None)->int:
    nodes=list(H); n=len(nodes); pos={x:i for i,x in enumerate(nodes)}
    adj=[0]*n
    for x,y in H.edges():
        i,j=pos[x],pos[y];adj[i]|=1<<j;adj[j]|=1<<i
    required=0 if root is None else 1<<pos[root]
    full=(1<<n)-1
    for k in range(n,0,-1):
        for comb in itertools.combinations(range(n),k):
            mask=sum(1<<i for i in comb)
            if required and not(mask&required):continue
            edges=sum((adj[i]&mask).bit_count() for i in comb)//2
            if edges!=k-1:continue
            seen=0;front=mask&-mask
            while front:
                seen|=front; nbr=0;f=front
                while f:
                    bit=f&-f;i=bit.bit_length()-1;nbr|=adj[i];f-=bit
                front=(nbr&mask)&~seen
            if seen==mask:return k
    return 1


def end_block_rows(G,g,e,C):
    arts=set(nx.articulation_points(G)); blocks=[set(B) for B in nx.biconnected_components(G)]
    ends=[B for B in blocks if len(B&arts)==1 and not(B&C)]
    rows=[]
    for bi,B in enumerate(ends):
        for v in sorted(B-arts):
            H=G.copy();H.remove_node(v)
            if not nx.is_connected(H) or cycle_rank(H)<1:
                rows.append({'block':bi,'v':v,'status':'inadmissible'});continue
            gh=girth(H);eh,Ch=center_depth(H)
            rows.append({'block':bi,'v':v,'girth':gh,'eta':eh,'phi':gh+eh,'center':sorted(Ch)})
    return arts,blocks,ends,rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--min-n',type=int,default=5);ap.add_argument('--max-n',type=int,default=11);args=ap.parse_args()
    per={};first_root=None;first_end=None;first_end_multi=None;root_graphs=root_splits=0;end_graphs=0
    for n in range(args.min_n,args.max_n+1):
        ng=ns=ne=0
        for codeb,G in records(n):
            g=girth(G)
            if g is None or g<5:continue
            arts=list(nx.articulation_points(G))
            if not arts:continue
            e,C=center_depth(G);target=g-1+e;ng+=1
            if first_end is None or (cycle_rank(G)>=2 and first_end_multi is None):
                aa,blocks,ends,rows=end_block_rows(G,g,e,C)
                if ends:
                    ne+=1
                    if not any(r.get('phi',-1)>=g+e for r in rows):
                        rec={'graph6':codeb.decode(),'order':n,'edges':[sorted(x) for x in G.edges()],
                             'cycle_rank':cycle_rank(G),'girth':g,'eta':e,'phi':g+e,'center':sorted(C),
                             'articulations':sorted(aa),'blocks':[sorted(B) for B in blocks],
                             'exterior_end_blocks':[sorted(B) for B in ends],'deletions':rows}
                        if first_end is None:first_end=rec
                        if cycle_rank(G)>=2 and first_end_multi is None:first_end_multi=rec
            # Every elementary component-vs-rest 1-sum, quotient side exchange.
            for v in arts:
                comps=[set(Q) for Q in nx.connected_components(nx.subgraph_view(G,filter_node=lambda x,v=v:x!=v))]
                seen=set()
                for A in comps:
                    B=set(G)-A-{v}; key=tuple(sorted(A if len(A)<=len(B) else B))
                    if key in seen:continue
                    seen.add(key);ns+=1
                    X=G.subgraph(A|{v}).copy();Y=G.subgraph(B|{v}).copy()
                    rx=tree_order(X,v);ry=tree_order(Y,v);bound=rx+ry-1
                    if bound<target and first_root is None:
                        first_root={'graph6':codeb.decode(),'order':n,'edges':[sorted(x) for x in G.edges()],
                                    'cut_vertex':v,'side1':sorted(X),'side2':sorted(Y),'girth':g,'eta':e,
                                    'center':sorted(C),'target':target,'rho1':rx,'rho2':ry,'rooted_sum':bound,
                                    'tau1':tree_order(X),'tau2':tree_order(Y),'tauG':tree_order(G),
                                    'side1_girth':girth(X),'side2_girth':girth(Y)}
                        break
                if first_root is not None:break
            if first_root is not None:break
        per[str(n)]={'cut_graphs':ng,'elementary_splits':ns,'end_block_graphs_until_first':ne}
        root_graphs+=ng;root_splits+=ns;end_graphs+=ne
        print(n,per[str(n)],flush=True)
        if first_root is not None:break
    out={'range':[args.min_n,args.max_n],'per_order':per,'cut_graphs':root_graphs,
         'elementary_splits':root_splits,'rooted_sum_first_failure':first_root,
         'end_block_first_failure':first_end,'end_block_first_multicyclic_failure':first_end_multi}
    (HERE/'block_sum_audit_results.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
