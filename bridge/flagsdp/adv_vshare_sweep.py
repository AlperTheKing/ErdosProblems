#!/usr/bin/env python3
import sys
sys.path.insert(0,'/e/Projects/ErdosProblems/bridge/flagsdp')
from peel_check import check_instance
def blowup(n0,adj0,mult):
    parts=[];s=0
    for v in range(n0): parts.append(list(range(s,s+mult[v])));s+=mult[v]
    N=s;adj=[set() for _ in range(N)]
    for u in range(n0):
        for v in adj0[u]:
            if v>u:
                for a in parts[u]:
                    for b in parts[v]: adj[a].add(b);adj[b].add(a)
    return N,adj
edges=[(0,1),(1,2),(2,3),(3,4),(4,0),(4,5),(5,6),(6,7),(7,8),(8,4)]
n0=9;a0=[set() for _ in range(9)]
for u,v in edges: a0[u].add(v);a0[v].add(u)
for mult in [[3,3,3,3,2,3,3,3,3],[2,2,2,2,2,2,2,2,2],[3,3,3,3,1,3,3,3,3],[2,3,2,3,1,2,3,2,3],
             [2,2,2,2,1,2,2,2,2],[3,3,3,3,3,3,3,3,3]]:
    N=sum(mult)
    if N>26:
        print('skip',mult,N); continue
    N,adj=blowup(n0,a0,mult)
    r=check_instance(N,adj)
    rr=(r['gamma']/r['n2']) if r.get('gamma') else 0
    print(mult,'N=',N,'m=',r.get('m'),'g=',r.get('gamma'),'n2=',r.get('n2'),
          'ratio=%.4f'%rr,'tight=',r.get('tight'),'sp=',r.get('has_safe_peel'))
print("DONE")
