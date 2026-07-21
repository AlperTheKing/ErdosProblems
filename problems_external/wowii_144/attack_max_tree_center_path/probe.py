from __future__ import annotations
import itertools, subprocess, sys
from pathlib import Path
import networkx as nx
ROOT=Path(__file__).resolve().parents[3]
GENG=ROOT/'tools'/'nauty2_8_9'/'geng.exe'

def girth(G):
    best=None
    for s in G:
        d={s:0}; p={s:None}; q=[s]
        for u in q:
            for v in G[u]:
                if v not in d: d[v]=d[u]+1; p[v]=u; q.append(v)
                elif p[u]!=v:
                    z=d[u]+d[v]+1
                    best=z if best is None or z<best else best
    return best

def is_tree_sub(G,S):
    if not S:return False
    H=G.subgraph(S)
    return H.number_of_edges()==len(S)-1 and nx.is_connected(H)

def paths(G,x,c):
    return list(nx.all_shortest_paths(G,x,c))

def check(G,code):
    g=girth(G)
    if g is None or g<5:return None
    ecc=nx.eccentricity(G); r=min(ecc.values()); C={v for v,e in ecc.items() if e==r}
    ds=nx.multi_source_shortest_path_length if False else nx.multi_source_dijkstra_path_length
    dep=ds(G,C); eta=max(dep.values())
    if eta==0:return None
    X=[v for v,d in dep.items() if d==eta]
    target=g-1+eta; n=len(G)
    if target>n:return {'kind':'W144_fail','code':code,'n':n,'g':g,'eta':eta,'target':target}
    for x in X:
      for c in C:
       if nx.shortest_path_length(G,x,c)!=eta:continue
       for Q in paths(G,x,c):
        qs=set(Q); maxsz=-1; trees=[]
        rest=[v for v in G if v not in qs]
        for mask in range(1<<len(rest)):
            S=qs|{rest[i] for i in range(len(rest)) if mask>>i&1}
            if len(S)<maxsz:continue
            if is_tree_sub(G,S):
                if len(S)>maxsz:maxsz=len(S); trees=[]
                trees.append(S)
        if maxsz>=target:
            return {'kind':'direct_tree','code':code,'n':n,'g':g,'eta':eta,'target':target,'x':x,'c':c,'Q':Q,'size':maxsz}
        for S in trees:
            T=G.subgraph(S)
            for z in set(G)-S:
                N=list(set(G[z])&S)
                if len(N)<2:continue
                for a,b in itertools.combinations(N,2):
                    R=set(nx.shortest_path(T,a,b))
                    if len(R&qs)<=1:
                        return {'kind':'boundary_pair','code':code,'n':n,'g':g,'eta':eta,'target':target,'x':x,'c':c,'Q':Q,'size':maxsz,'z':z,'a':a,'b':b,'intersection':len(R&qs)}
    return {'kind':'counterexample','code':code,'n':n,'m':G.number_of_edges(),'g':g,'eta':eta,'target':target,'C':sorted(C),'X':X,'edges':sorted(map(list,G.edges()))}

def main():
    mx=int(sys.argv[1]) if len(sys.argv)>1 else 10
    counts={}
    for n in range(5,mx+1):
      p=subprocess.Popen([str(GENG),'-ctfq',str(n)],stdout=subprocess.PIPE)
      seen=0
      for line in p.stdout:
        b=line.strip()
        if not b:continue
        G=nx.from_graph6_bytes(b)
        if G.number_of_edges()-G.number_of_nodes()+1<2:continue
        out=check(G,b.decode())
        if out:
          seen+=1; counts[out['kind']]=counts.get(out['kind'],0)+1
          if out['kind']=='counterexample':
            print(out); print('COUNTS',counts); p.kill(); return 1
      assert p.wait()==0
      print('n',n,'checked',seen,'counts',counts,flush=True)
    print('PASS',counts); return 0
if __name__=='__main__':raise SystemExit(main())