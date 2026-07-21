#!/usr/bin/env python3
import random,sys,networkx as nx
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from test_wrapped_n2 import evaluate
from search_multiroot_tree import tree_from_prufer

def make(rng):
 g=rng.randint(5,11);q=rng.randint(1,6);G=nx.cycle_graph(g)
 # asymmetric shallow legs, including the tight C5-two-leaf seed
 for root in rng.sample(range(g),2):
  base=root
  for _ in range(1):
   w=len(G);G.add_edge(base,w);base=w
 off=len(G);T=tree_from_prufer(q,rng);G.add_edges_from((off+u,off+v) for u,v in T.edges())
 ac=rng.randint(1,min(q,4)); hv=rng.sample(range(q),ac)
 for v in hv:
  valid=[]
  for a in range(g):
   G.add_edge(off+v,a);cyc=nx.cycle_basis(G);ok=cyc and min(map(len,cyc))>=g;G.remove_edge(off+v,a)
   if ok:valid.append(a)
  if not valid:return None
  G.add_edge(off+v,rng.choice(valid))
 return G

def main():
 rng=random.Random(990144);best=None;res=non=0
 for it in range(20000):
  G=make(rng)
  if G is None:continue
  rec=evaluate(G)
  if rec is None:continue
  res+=1;slack,data=rec
  if data and data[0]!='tail':non+=1
  if data and data[0]=='tail':continue
  if best is None or slack<best[0]:
   line=nx.to_graph6_bytes(nx.convert_node_labels_to_integers(G),header=False).decode().strip();best=(slack,line,data)
   print('best',it,res,non,best,flush=True)
  if slack<0:break
 print('done',res,non,best)
if __name__=='__main__':main()

