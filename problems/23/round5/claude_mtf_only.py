"""Filter graph6 to MAXIMAL triangle-free graphs (complete pattern space: adding edges only
increases psi pointwise, so every pattern is dominated by a maximal one on the same vertex set)."""
import sys
from itertools import combinations
def g6(s):
    b=[ord(c)-63 for c in s]; n=b[0]; i=1
    if n==63: n=(b[1]<<12)|(b[2]<<6)|b[3]; i=4
    bits=[]
    for x in b[i:]: bits.extend((x>>k)&1 for k in (5,4,3,2,1,0))
    adj=[set() for _ in range(n)]; p=0
    for j in range(1,n):
        for k in range(j):
            if bits[p]: adj[k].add(j); adj[j].add(k)
            p+=1
    return n,adj
kept=tot=0
for line in sys.stdin:
    s=line.strip()
    if not s: continue
    tot+=1
    n,adj=g6(s)
    ok=True
    for a,b in combinations(range(n),2):
        if b in adj[a]:
            if adj[a]&adj[b]: ok=False; break          # triangle
        else:
            if not (adj[a]&adj[b]): ok=False; break     # not maximal
    if ok: print(s); kept+=1
sys.stderr.write(f"kept {kept} of {tot}\n")
