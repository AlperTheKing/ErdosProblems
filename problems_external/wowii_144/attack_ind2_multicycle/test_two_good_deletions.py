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
 global_min=999; first=None; total=0
 for n in range(5,a.max_n+1):
  mn=999; rec=None; cnt=0
  for code,G in records(n):
   g=girth(G)
   if g is None or g<5 or cycle_rank(G)<2:continue
   cnt+=1;total+=1;e,_=center_depth(G);good=[]
   for v in G:
    H=G.copy();H.remove_node(v)
    if not nx.is_connected(H) or cycle_rank(H)<1:continue
    eh,_=center_depth(H)
    if eh>=e:good.append(v)
   if len(good)<mn:
    mn=len(good);rec={'graph6':code.decode(),'n':n,'m':G.number_of_edges(),'g':g,'eta':e,'good':good,'edges':sorted(map(list,G.edges()))}
   if len(good)<2:
    print('FAIL',json.dumps(rec));return 1
  global_min=min(global_min,mn);print(n,cnt,'min_good',mn,'record',rec,flush=True)
 print('PASS',total,'global_min',global_min);return 0
if __name__=='__main__':raise SystemExit(main())