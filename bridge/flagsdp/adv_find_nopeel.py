#!/usr/bin/env python3
"""Re-run the family loop and PRINT every has_safe_peel False instance with edges, for inspection."""
import itertools
from peel_check import check_instance

def Cm_blowup(parts):
    L=len(parts); n=sum(parts); off=[0]*(L+1)
    for i in range(L): off[i+1]=off[i]+parts[i]
    adj=[set() for _ in range(n)]
    def vid(i,a): return off[i]+a
    for i in range(L):
        j=(i+1)%L
        for a in range(parts[i]):
            for b in range(parts[j]):
                u=vid(i,a); v=vid(j,b); adj[u].add(v); adj[v].add(u)
    return n,adj

def check(name,n,adj):
    r=check_instance(n,adj)
    if not (r.get("ok") and r.get("B_connected") and r.get("m",0)>=2 and r.get("gamma") is not None):
        return
    if r["has_safe_peel"] is False:
        edges=[(u,v) for u in range(n) for v in sorted(adj[u]) if v>u]
        print(f"NOPEEL {name}: N={n} m={r['m']} gamma={r['gamma']} n2={r['n2']} ratio={r['gamma']/r['n2']:.5f} tight={r['tight']}")
        print(f"   edges={edges}")
        print(f"   detail={r['detail']}")

seen=set()
for parts in itertools.product(range(1,6),repeat=5):
    if sum(parts)>22: continue
    rots=[]
    for s in range(5):
        r1=parts[s:]+parts[:s]; rots.append(r1); rots.append(r1[::-1])
    canon=min(rots)
    if canon!=list(parts) and tuple(canon) in seen: continue
    seen.add(tuple(canon))
    n,adj=Cm_blowup(list(parts)); check(f"C5{parts}",n,adj)
for q in range(1,4):
    n,adj=Cm_blowup([q]*7)
    if n<=24: check(f"C7[{q}]",n,adj)
for q in range(1,3):
    n,adj=Cm_blowup([q]*9)
    if n<=24: check(f"C9[{q}]",n,adj)
print("done")
