#!/usr/bin/env python3
from __future__ import annotations
import argparse,sys,json
from pathlib import Path
import networkx as nx
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'attack_ind2_multicycle'))
from analyze_tight_deletions import records,girth,center_depth,cycle_rank

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--max-n',type=int,default=13);a=ap.parse_args();tot=0;mint=999
 for n in range(5,a.max_n+1):
  cn=0
  for code,G in records(n):
   g=girth(G)
   if g is None or g<5 or cycle_rank(G)<2 or not nx.is_biconnected(G):continue
   eta,C=center_depth(G);D=nx.diameter(G);Delta=max(dict(G.degree()).values());sl=max(Delta-1,D-g//2)-eta
   tot+=1;cn+=1;mint=min(mint,sl)
   if sl<0:
    out={'graph6':code.decode(),'n':n,'m':G.number_of_edges(),'g':g,'eta':eta,'D':D,'Delta':Delta,'rhs':max(Delta-1,D-g//2),'C':sorted(C),'degrees':dict(G.degree()),'edges':sorted(map(list,G.edges()))};print('FAIL',json.dumps(out));return 1
  print(n,cn,'total',tot,'min_slack',mint,flush=True)
 print('PASS',tot,'min_slack',mint);return 0
if __name__=='__main__':raise SystemExit(main())