#!/usr/bin/env python3
from __future__ import annotations
import argparse,sys,json
from pathlib import Path
import networkx as nx
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from analyze_tight_deletions import records,girth,center_depth,cycle_rank

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--max-n',type=int,default=13);a=ap.parse_args()
 total=residual=0
 for n in range(5,a.max_n+1):
  rn=0
  for code,G in records(n):
   g=girth(G)
   if g is None or g<5 or cycle_rank(G)<2:continue
   total+=1;eta,C=center_depth(G);Delta=max(dict(G.degree()).values())
   if Delta>=eta:continue
   residual+=1;rn+=1;good=[];rows=[]
   for v in G:
    if G.degree[v]>2:continue
    H=G.copy();H.remove_node(v)
    if not nx.is_connected(H) or cycle_rank(H)<1:continue
    eh,Ch=center_depth(H);rows.append((v,G.degree[v],eh,sorted(Ch)))
    if eh>=eta:good.append(v)
   if not good:
    out={'graph6':code.decode(),'n':n,'m':G.number_of_edges(),'g':g,'eta':eta,'Delta':Delta,'beta':cycle_rank(G),'center':sorted(C),'degrees':dict(G.degree()),'low_rows':rows,'edges':sorted(map(list,G.edges()))}
    print('FAIL',json.dumps(out));return 1
  print(n,'residual',rn,'cumulative',residual,flush=True)
 print('PASS total',total,'residual',residual);return 0
if __name__=='__main__':raise SystemExit(main())