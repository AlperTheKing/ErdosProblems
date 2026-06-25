"""Broader check of round-4 Lemma 1: over ALL connected bipartite graphs with
maxdeg<=6 and sum(6-deg)=6 (NOT requiring e=3n-3), confirm:
  H passes [C]  <=>  deficiency support is {3,3} (one per side or two on a side).
Feeds: geng -b -c -D6 n  (all connected bipartite, maxdeg<=6, any edge count),
filter to sum b = 6 in Python.  Also report any [C]-pass whose support != [3,3]
(would refute Lemma 1) and any 3+3 graph that FAILS [C] (would refute the <=).
"""
import sys
def g6decode(s):
    n = ord(s[0]) - 63
    adj = [set() for _ in range(n)]
    bit = 0
    for j in range(1, n):
        for i in range(j):
            byte = 1 + bit // 6; off = 5 - bit % 6
            if (ord(s[byte]) - 63) >> off & 1:
                adj[i].add(j); adj[j].add(i)
            bit += 1
    return n, adj
def proper_colourings(n, adj):
    col = [-1]*n
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    def bt(i):
        if i == n:
            yield tuple(col); return
        v = order[i]
        used = {col[u] for u in adj[v] if col[u] >= 0}
        for c in range(3):
            if c in used: continue
            col[v] = c
            yield from bt(i+1)
            col[v] = -1
    yield from bt(0)
ALLOWED = {(6,0,0),(0,6,0),(0,0,6),(3,3,0),(3,0,3),(0,3,3),
           (4,1,1),(1,4,1),(1,1,4),(2,2,2)}
def passes_C(n, adj, b):
    for col in proper_colourings(n, adj):
        v=[0,0,0]
        for u in range(n): v[col[u]] += b[u]
        if tuple(v) not in ALLOWED: return False
    return True
total=0; cpass=0; viol_forward=0; viol_back=0
for line in sys.stdin:
    line=line.strip()
    if not line or line[0]=='>': continue
    n, adj = g6decode(line)
    b=[6-len(adj[u]) for u in range(n)]
    if sum(b)!=6: continue
    seen={0}; st=[0]
    while st:
        x=st.pop()
        for y in adj[x]:
            if y not in seen: seen.add(y); st.append(y)
    if len(seen)!=n: continue
    total+=1
    wpos=sorted(b[u] for u in range(n) if b[u]>0)
    is33 = (wpos==[3,3])
    pc = passes_C(n,adj,b)
    if pc: cpass+=1
    if pc and not is33:
        viol_forward+=1; print(f"FWD-VIOL (passC, not 3+3) g6={line} w={wpos}")
    if is33 and not pc:
        viol_back+=1; print(f"BACK-VIOL (3+3, fails C) g6={line}")
print(f"connected_bip_def6={total} passC={cpass} fwdViol={viol_forward} backViol={viol_back}")
