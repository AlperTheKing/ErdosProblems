from __future__ import annotations
import subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];W0=R/'problems_external/wowii_144';sys.path[:0]=[str(R/'problems_external/wowii_141/oracle'),str(W0/'oracle'),str(W0/'oracle_exhaustive'),str(W0/'proverC'),str(W0/'wave2'),str(W0/'attack_144_n2')]
from invariants import *
from run_sweep import parse_graph6,shortest_cycle_vertex_sets
from test_gpt_n2 import bits,components_outside
from verify_ordinary_triameter_n14 import atts,jmetric
GENG=R/'tools/nauty2_8_9/geng.exe';bad=[];tests=0;mn=999
for n in range(5,13):
 p=subprocess.run([str(GENG),'-c','-t','-f','-q',str(n)],capture_output=True,text=True,check=True)
 for g6 in p.stdout.split():
  N,a=parse_graph6(g6);g=girth(N,a)
  if g<5:continue
  d=all_pairs_dist(N,a);ec=eccentricities(N,d);r,D=min(ec),max(ec);C=sum(1<<v for v in range(N)if ec[v]==r);e=ecc_of_set(N,d,C)
  if e==0 or e<=D-g//2:continue
  rr=[v for v in range(N)if dist_to_set(d,v,C)==e];cy,_=shortest_cycle_vertex_sets(N,a,g,5000)
  for K in cy:
   km=sum(1<<v for v in K);cs=components_outside(a,((1<<N)-1)&~km);AA=[atts(a,K,H)for H in cs];mh=max(dist_to_set(d,x,km)for x in rr)
   for x in rr:
    h=dist_to_set(d,x,km)
    if h!=mh or h>=e:continue
    xi=next((i for i,H in enumerate(cs)if H>>x&1),None)
    for m in [u for u in K if d[x][u]==h]:
     de=e-h;WW=[u for u in K if d[u][m]<=de-1];vals=[[max(d[s][y]for y in bits(H))for s in WW]for H in cs];EH=[[WW[j]for j,v in enumerate(vals[i])if v>=r+1]for i in range(len(cs))]
     for z in bits(a[m]&km):
      if not all(not(set(AA[i])=={z} and EH[i])for i in range(len(cs))):continue
      for i,H in enumerate(cs):
       if i==xi or not EH[i] or not(set(AA[i])-{z}):continue
       P,_=jmetric(a,K,H,z);ex=sum(max(0,v-r)for v in vals[i]);sl=P-(2*r+1-g)-ex;tests+=1;mn=min(mn,sl)
       if sl<0 and len(bad)<20:bad.append((g6,g,r,D,e,K,m,z,list(bits(H)),WW,vals[i],EH[i],P,ex,sl))
print('tests',tests,'min',mn,'bad',bad)