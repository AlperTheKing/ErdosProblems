#!/usr/bin/env python3
"""Targeted falsifier for the W144 ordinary rooted-triameter metric lemma."""
from __future__ import annotations
import random,sys
from pathlib import Path
import networkx as nx
HERE=Path(__file__).resolve().parent;PROVER=HERE.parent/'proverC';sys.path[:0]=[str(PROVER),str(HERE)]
from test_gpt_n2 import all_pairs_dist,bits,components_outside,dist_to_set,ecc_of_set,eccentricities,girth,graph6,nx_to_bitadj,shortest_cycles

def atts(adj,K,H):return {a for a in K if any(adj[v]>>a&1 for v in bits(H))}
def jperim(adj,K,H,z):
 hv=list(bits(H));loc={v:i for i,v in enumerate(hv)};rho=len(hv);ja=[0]*(rho+1);km=sum(1<<v for v in K)&~(1<<z)
 for v in hv:
  i=loc[v]
  for w in bits(adj[v]&H):ja[i]|=1<<loc[w]
  if adj[v]&km:ja[i]|=1<<rho;ja[rho]|=1<<i
 def bfs(s):
  d=[10**9]*len(ja);d[s]=0;q=[s]
  for u in q:
   for v in bits(ja[u]):
    if d[v]==10**9:d[v]=d[u]+1;q.append(v)
  return d
 dd=[bfs(i)for i in range(len(ja))]
 return max(dd[rho][u]+dd[rho][v]+dd[u][v]for u in range(rho)for v in range(rho))
def evaluate(G):
 if not nx.is_connected(G):return None
 G=nx.convert_node_labels_to_integers(G);n,adj=nx_to_bitadj(G);g=girth(n,adj)
 if g<5 or n-g>18:return None
 d=all_pairs_dist(n,adj);ec=eccentricities(n,d);r,D=min(ec),max(ec);C=sum(1<<v for v in range(n)if ec[v]==r);e=ecc_of_set(n,d,C)
 if e==0 or e<=D-g//2:return None
 rr=[v for v in range(n)if dist_to_set(d,v,C)==e];best=None;rec=None
 for KK in shortest_cycles(G,g):
  K=sorted(KK);km=sum(1<<v for v in K);cs=components_outside(adj,((1<<n)-1)&~km);aa=[atts(adj,K,H)for H in cs];mh=max(dist_to_set(d,x,km)for x in rr)
  for x in rr:
   h=dist_to_set(d,x,km)
   if h!=mh or h>=e:continue
   xi=next((i for i,H in enumerate(cs)if H>>x&1),None)
   for m in [a for a in K if d[x][a]==h]:
    de=e-h;W=[a for a in K if d[a][m]<=de-1];EH=[[s for s in W if max(d[s][y]for y in bits(H))>=r+1]for H in cs]
    for z in bits(adj[m]&km):
     if not all(not(aa[i]=={z} and EH[i])for i in range(len(cs))):continue
     for i,H in enumerate(cs):
      if i==xi or not EH[i] or not(aa[i]-{z}):continue
      P=jperim(adj,K,H,z);sl=P-len(EH[i])-(2*r+1-g)
      if best is None or sl<best:best=sl;rec=(n,g,r,D,e,K,x,h,m,z,de,W,list(bits(H)),sorted(aa[i]),EH[i],P,sl)
 return None if best is None else (best,rec)
def seed_graph(g,rng):
 G=nx.cycle_graph(g);n=g
 # Add rooted legs and occasional long ears, preserving them only after girth filter.
 for root in range(g):
  if rng.random()<.55:
   prev=root
   for _ in range(rng.randrange(1,5)):
    G.add_edge(prev,n);prev=n;n+=1
 # Join random outside vertices to make branched components.
 out=list(range(g,n))
 for _ in range(rng.randrange(0,5)):
  if len(out)>=2:
   u,v=rng.sample(out,2)
   if not G.has_edge(u,v):G.add_edge(u,v)
 return G
def mutate(G,rng):
 H=G.copy();n=len(H)
 if rng.random()<.45 and n<28:
  v=n;H.add_edge(v,rng.randrange(n))
  if rng.random()<.5:H.add_edge(v,rng.randrange(n))
 elif rng.random()<.8:
  u,v=rng.sample(range(n),2)
  if u!=v:H.add_edge(u,v)
 else:
  es=list(H.edges())
  if es:H.remove_edge(*rng.choice(es))
 return H
def main():
 rng=random.Random(14420260718);seeds=[seed_graph(g,rng)for g in range(5,14)for _ in range(350)];pop=seeds;seen=set();checked=residual=frontier=0;best=None
 for gen in range(10):
  scored=[]
  for G in pop:
   if not nx.is_connected(G):continue
   key=graph6(nx.convert_node_labels_to_integers(G))
   if key in seen:continue
   seen.add(key);checked+=1;out=evaluate(G)
   if out is None:continue
   frontier+=1;sl,rec=out;scored.append((sl,key,G,rec))
   if best is None or sl<best[0]:best=(sl,key,rec);print('BEST',best,flush=True)
   if sl<0:print('COUNTEREXAMPLE',key,rec,flush=True);return
  scored.sort(key=lambda x:x[0]);parents=[x[2]for x in scored[:120]] or rng.sample(seeds,min(120,len(seeds)));pop=[mutate(rng.choice(parents),rng)for _ in range(2500)];print({'generation':gen,'checked':checked,'frontier':frontier,'best':best},flush=True)
 print({'checked':checked,'frontier':frontier,'best':best})
if __name__=='__main__':main()