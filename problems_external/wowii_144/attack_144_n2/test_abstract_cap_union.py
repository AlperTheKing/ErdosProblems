#!/usr/bin/env python3
from __future__ import annotations
import subprocess,sys,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];W0=ROOT/'problems_external/wowii_144';sys.path[:0]=[str(ROOT/'problems_external/wowii_141/oracle'),str(W0/'oracle'),str(W0/'oracle_exhaustive'),str(W0/'proverC'),str(W0/'wave2'),str(W0/'attack_144_n2')]
from invariants import all_pairs_dist,ecc_of_set,eccentricities,girth
from run_sweep import parse_graph6,shortest_cycle_vertex_sets
from test_gpt_n2 import bits,components_outside
from verify_ordinary_triameter_n14 import jmetric,atts
GENG=ROOT/'tools/nauty2_8_9/geng.exe'
def main():
 bad=[];mins={};cnt=collections.Counter()
 for n in range(5,13):
  p=subprocess.run([str(GENG),'-c','-t','-f','-q',str(n)],capture_output=True,text=True,check=True)
  for g6 in p.stdout.split():
   N,a=parse_graph6(g6);g=girth(N,a)
   if g<5:continue
   d=all_pairs_dist(N,a);ec=eccentricities(N,d);r=min(ec);C=sum(1<<v for v in range(N)if ec[v]==r);e=ecc_of_set(N,d,C)
   if e==0:continue
   cy,_=shortest_cycle_vertex_sets(N,a,g,5000);lam=2*r+1-g
   for K in cy:
    km=sum(1<<v for v in K);cs=components_outside(a,((1<<N)-1)&~km)
    for m in K:
     for z in bits(a[m]&km):
      for de in range(1,e+1):
       WW=[s for s in K if d[s][m]<=de-1]
       for H in cs:
        A=atts(a,K,H)
        if not(set(A)-{z}):continue
        P,_=jmetric(a,K,H,z);B=[u for u in bits(H)if a[u]&(km&~(1<<z))];U=[]
        for y in bits(H):
         py=1+min(d[y][u]for u in B);roots={aa for u in B if d[y][u]+1==py for aa in K if aa!=z and a[u]>>aa&1};U += [s for s in WW if all(d[s][aa]>=r+1-py for aa in roots)]
        U=set(U)
        if not U:continue
        sl=P-len(U)-lam;key='g7'if g>=7 else'g56';cnt[key]+=1;mins[key]=min(mins.get(key,999),sl)
        if sl<0 and len(bad)<20:bad.append(dict(g6=g6,n=N,g=g,r=r,e=e,K=K,m=m,z=z,delta=de,W=WW,H=list(bits(H)),A=A,U=sorted(U),P=P,lam=lam,sl=sl))
 print(cnt,mins,'badn',len(bad));
 for x in bad:print(x)
if __name__=='__main__':main()