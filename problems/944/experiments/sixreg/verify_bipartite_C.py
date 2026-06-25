"""VERIFY round-4 Lemma 1 (backbone of Theorem C): every connected bipartite
graph H with maxdeg<=6, e=3n-3, sum(6-deg)=6, that passes [C] (every proper
3-colouring has deficiency-weighted boundary vector a permutation of (6,0,0),
(3,3,0),(4,1,1),(2,2,2)) has its deficiency CONCENTRATED as two b=3 vertices
(one per side, or two on one side).
We feed every connected bipartite candidate from geng -b -c -D6 n <e>:<e>.
"""
import sys, itertools
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
    """yield all proper 3-colourings (as tuples)"""
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
        v = [0,0,0]
        for u in range(n): v[col[u]] += b[u]
        if tuple(v) not in ALLOWED:
            return False
    return True
def deficiency_concentrated_33(n, adj, b, sides):
    pos = [u for u in range(n) if b[u] > 0]
    weights = sorted(b[u] for u in pos)
    if weights != [3,3]: return False
    return True   # the 3+3 pattern (positions checked separately if needed)
total = 0; cpass = 0; viol = 0
for line in sys.stdin:
    line = line.strip()
    if not line or line[0] == '>': continue
    n, adj = g6decode(line)
    b = [6 - len(adj[u]) for u in range(n)]
    if sum(b) != 6: continue
    # connected check
    seen = {0}; st = [0]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen: seen.add(y); st.append(y)
    if len(seen) != n: continue
    total += 1
    if passes_C(n, adj, b):
        cpass += 1
        # bipartition sides
        side = {0:0}; st=[0]
        while st:
            x=st.pop()
            for y in adj[x]:
                if y not in side: side[y]=1-side[x]; st.append(y)
        wpos = sorted(b[u] for u in range(n) if b[u]>0)
        if wpos != [3,3]:
            viol += 1
            print(f"VIOLATION g6={line} weights={wpos}")
print(f"n={n if 'n' in dir() else '?'} bipartite_connected_def6={total} passC={cpass} viol_not_33={viol}")
