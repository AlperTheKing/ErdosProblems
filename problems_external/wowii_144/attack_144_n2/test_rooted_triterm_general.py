#!/usr/bin/env python3
from __future__ import annotations
import subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE));import verify_component_capacity as v
from invariants import all_pairs_dist,girth,eccentricities,ecc_of_set,dist_to_set
from run_sweep import parse_graph6,shortest_cycle_vertex_sets
from test_gpt_n2 import bits,components_outside
GENG=ROOT/'tools'/'nauty2_8_9'/'geng.exe'
def check(g6):
 n,adj=parse_graph6(g6);g=girth(n,adj)
 if g<5:return 0,None
 dist=all_pairs_dist(n,adj); ecc=eccentricities(n,dist); r=min(ecc); C=sum(1<<v for v in range(n) if ecc[v]==r); e=ecc_of_set(n,dist,C);
 if e==0 or e<=max(ecc)-g//2:return 0,None
 cycles,cap=shortest_cycle_vertex_sets(n,adj,g,5000)
 if cap:raise RuntimeError
 tests=0
 for K in cycles:
  km=sum(1<<a for a in K);comps=components_outside(adj,((1<<n)-1)&~km)
  for H in comps:
   for m in K:
    for z in bits(adj[m]&km):
     if not (set(v.attachment_set(adj,K,H))-{z}):continue
     mu,F=v.mu_component(adj,K,H,z)
     for x in bits(H):
      h=min(dist[x][a] for a in K)
      if dist_to_set(dist,x,C)!=e or h>=e or dist[x][m]!=h:continue
      for y in bits(H):
       tests+=1;need=(h+dist[m][y]+dist[x][y]+1)//2-1
       if mu<need:return tests,dict(graph6=g6,n=n,g=g,K=K,H=list(bits(H)),m=m,z=z,x=x,y=y,h=h,dmy=dist[m][y],dxy=dist[x][y],mu=mu,forest=list(bits(F)),need=need)
 return tests,None
def main():
 total=0
 for n in range(5,13):
  p=subprocess.run([str(GENG),'-c','-t','-f','-q',str(n)],capture_output=True,text=True,check=True)
  for g6 in p.stdout.split():
   t,ce=check(g6);total+=t
   if ce:print('COUNTEREXAMPLE',ce);return
  print(n,total,flush=True)
 print('NO FAIL',total)
if __name__=='__main__':main()


