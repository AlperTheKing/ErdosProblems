"""Filter a graph6 stream to MAXIMAL triangle-free, TWIN-FREE graphs.
maximal triangle-free  <=>  triangle-free and every non-adjacent pair has a common neighbour
twin-free              <=>  no two vertices have identical neighbourhoods (non-adjacent twins)
Both reductions are proved: adding edges increases psi pointwise, and some maximiser of psi is
constant on twin classes."""
import sys
from itertools import combinations

def g6(s):
    b=[ord(c)-63 for c in s]
    i=0; n=b[0]; i=1
    if n==63: n=(b[1]<<12)|(b[2]<<6)|b[3]; i=4
    bits=[]
    for x in b[i:]: bits.extend((x>>k)&1 for k in (5,4,3,2,1,0))
    adj=[set() for _ in range(n)]; p=0
    for j in range(1,n):
        for i2 in range(j):
            if bits[p]: adj[i2].add(j); adj[j].add(i2)
            p+=1
    return n,adj

kept=tot=0
for line in sys.stdin:
    s=line.strip()
    if not s: continue
    tot+=1
    n,adj=g6(s)
    if any(len(adj[a]&adj[b])>0 for a,b in combinations(range(n),2) if b in adj[a]): continue   # triangle
    if any(len(adj[a]&adj[b])==0 for a,b in combinations(range(n),2) if b not in adj[a]): continue  # not maximal
    if any(adj[a]==adj[b] for a,b in combinations(range(n),2)): continue                        # twins
    print(s); kept+=1
sys.stderr.write(f"kept {kept} of {tot}\n")
