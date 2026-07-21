#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
import networkx as nx
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'attack_ind2_multicycle'))
from analyze_tight_deletions import records,girth,center_depth

def shortest_cycle_vertices(G,g):
    out=set()
    for a,b in list(G.edges()):
        G.remove_edge(a,b)
        try:
            p=nx.shortest_path(G,a,b)
            if len(p)==g: out.update(p)
        except nx.NetworkXNoPath: pass
        G.add_edge(a,b)
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--max-n',type=int,default=13);args=ap.parse_args()
    count=0; first=None; per={}
    for n in range(5,args.max_n+1):
      cn=0
      for codeb,G in records(n):
        gg=girth(G)
        if gg is None or gg<5: continue
        etaG,_=center_depth(G)
        for v in nx.articulation_points(G):
          comps=[set(Q) for Q in nx.connected_components(nx.subgraph_view(G,filter_node=lambda x,v=v:x!=v))]
          seen=set()
          for A0 in comps:
            B0=set(G)-A0-{v}; key=tuple(sorted(A0 if len(A0)<=len(B0) else B0))
            if key in seen: continue
            seen.add(key)
            for Araw,Braw in ((A0,B0),(B0,A0)):
              A=G.subgraph(Araw|{v}).copy(); B=G.subgraph(Braw|{v}).copy()
              ga=girth(A)
              if ga!=gg: continue
              etaA,_=center_depth(A); Rb=nx.eccentricity(B,v)
              cyc=shortest_cycle_vertices(A,ga)
              d=min(nx.shortest_path_length(A,v,k) for k in cyc)
              rhs=max(etaA,d+Rb); count+=1;cn+=1
              if etaG>rhs:
                first={'graph6':codeb.decode(),'n':n,'edges':sorted(map(list,G.edges())),'cut':v,'A':sorted(A),'B':sorted(B),'g':gg,'etaG':etaG,'etaA':etaA,'Rb':Rb,'d':d,'rhs':rhs,'C_G':sorted(center_depth(G)[1]),'C_A':sorted(center_depth(A)[1])}
                print('FAIL',json.dumps(first)); return 1
      per[n]=cn;print(n,cn,'total',count,flush=True)
    print('PASS',count,per);return 0
if __name__=='__main__':raise SystemExit(main())