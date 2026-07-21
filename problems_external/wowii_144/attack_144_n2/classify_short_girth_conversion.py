from __future__ import annotations
import subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];W=R/'problems_external/wowii_144';sys.path[:0]=[str(R/'problems_external/wowii_141/oracle'),str(W/'oracle'),str(W/'oracle_exhaustive'),str(W/'proverC'),str(W/'wave2'),str(W/'attack_144_n2')]
from invariants import *
from run_sweep import parse_graph6,shortest_cycle_vertex_sets
from test_gpt_n2 import bits,components_outside
from verify_component_capacity import mu_component
from verify_ordinary_triameter_n14 import jmetric,atts
best={5:(999,None),6:(999,None)}
for n in range(5,13):
 p=subprocess.run([str(R/'tools/nauty2_8_9/geng.exe'),'-c','-t','-f','-q',str(n)],capture_output=True,text=True,check=True)
 for g6 in p.stdout.split():
  N,a=parse_graph6(g6);g=girth(N,a)
  if g not in best:continue
  d=all_pairs_dist(N,a);ec=eccentricities(N,d);r,D=min(ec),max(ec);C=sum(1<<v for v in range(N)if ec[v]==r);e=ecc_of_set(N,d,C)
  if e==0 or e<=D-g//2:continue
  rr=[v for v in range(N)if dist_to_set(d,v,C)==e];cy,_=shortest_cycle_vertex_sets(N,a,g,5000)
  for K in cy:
   km=sum(1<<v for v in K);cs=components_outside(a,((1<<N)-1)&~km);aa=[atts(a,K,H)for H in cs];mh=max(dist_to_set(d,x,km)for x in rr)
   for x in rr:
    h=dist_to_set(d,x,km)
    if h!=mh or h>=e:continue
    xi=next((i for i,H in enumerate(cs)if H>>x&1),None)
    for m in [u for u in K if d[x][u]==h]:
     de=e-h;WW=[u for u in K if d[u][m]<=de-1];EH=[[s for s in WW if max(d[s][y]for y in bits(H))>=r+1]for H in cs]
     for z in bits(a[m]&km):
      if not all(not(set(aa[i])=={z} and EH[i])for i in range(len(cs))):continue
      for i,H in enumerate(cs):
       if i==xi or not EH[i] or not(set(aa[i])-{z}):continue
       P,_=jmetric(a,K,H,z);mu,F=mu_component(a,K,H,z);sl=2*mu-P
       if sl<best[g][0]:best[g]=(sl,dict(graph6=g6,n=N,g=g,r=r,D=D,e=e,K=K,x=x,h=h,m=m,z=z,delta=de,W=WW,H=list(bits(H)),A=sorted(aa[i]),E=EH[i],P=P,mu=mu,F=list(bits(F)),conversion_slack=sl,O_slack=2*mu-len(EH[i])-(2*r+1-g)))
print(best)