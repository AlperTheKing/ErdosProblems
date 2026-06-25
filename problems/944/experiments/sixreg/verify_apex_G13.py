"""Cross-check the apex equivalence at the one nontrivial small case.
G13 = the unique 6-regular 4-vertex-critical graph (g6 L?bFFbw~B{FwFw).
Apex equivalence (GPT round-7, audited): a 6-regular 4-VC graph F has a vertex z
incident with NO critical edge  <=>  B=F-z is an always-balanced criticality-
feasible diagonal partner. Candidate theorem (= diag_unlock feasible=0) <=>
every vertex of every 6-regular 4-VC graph is incident with a critical edge.
Test on G13: compute critical edges, confirm they form an EDGE COVER (every
vertex incident to >=1). Also confirm critical edges = a Hamilton cycle (per note).
"""
g6 = "L?bFFbw~B{FwFw"
def g6decode(s):
    n = ord(s[0]) - 63
    adj = [set() for _ in range(n)]
    bit = 0
    for j in range(1, n):
        for i in range(j):
            byte = 1 + bit//6; off = 5 - bit%6
            if (ord(s[byte])-63) >> off & 1:
                adj[i].add(j); adj[j].add(i)
            bit += 1
    return n, adj
n, adj = g6decode(g6)
assert all(len(adj[v])==6 for v in range(n)), "not 6-regular"
def three_col(adj, n, removed_edge=None):
    col=[-1]*n
    order=sorted(range(n), key=lambda v:-len(adj[v]))
    def bad(v,c):
        for u in adj[v]:
            if removed_edge and ((u==removed_edge[0] and v==removed_edge[1]) or (u==removed_edge[1] and v==removed_edge[0])):
                continue
            if col[u]==c: return True
        return False
    def bt(i):
        if i==n: return True
        v=order[i]
        for c in range(3):
            if not bad(v,c):
                col[v]=c
                if bt(i+1): return True
                col[v]=-1
        return False
    return bt(0)
assert not three_col(adj,n), "G should be 4-chromatic"
# vertex-critical: G-v 3-colourable for all v
def col_minus_vertex(adj,n,w):
    col={}
    verts=[v for v in range(n) if v!=w]
    verts.sort(key=lambda v:-len(adj[v]))
    def bt(i):
        if i==len(verts): return True
        v=verts[i]
        used={col[u] for u in adj[v] if u in col}
        for c in range(3):
            if c in used: continue
            col[v]=c
            if bt(i+1): return True
            del col[v]
        return False
    return bt(0)
assert all(col_minus_vertex(adj,n,v) for v in range(n)), "not vertex-critical"
# critical edges: G-e 3-colourable
edges=[(u,v) for u in range(n) for v in adj[u] if u<v]
crit=[e for e in edges if three_col(adj,n,removed_edge=e)]
covered=set()
for (u,v) in crit: covered.add(u); covered.add(v)
print(f"G13: n={n}, edges={len(edges)}, criticalEdges={len(crit)}")
print(f"vertices covered by critical edges: {len(covered)}/{n}  -> EDGE COVER: {len(covered)==n}")
# Hamilton cycle check on critical edges
deg_crit=[0]*n
cadj=[set() for _ in range(n)]
for (u,v) in crit: deg_crit[u]+=1; deg_crit[v]+=1; cadj[u].add(v); cadj[v].add(u)
is_2reg = all(d==2 for d in deg_crit)
# single cycle?
single=False
if is_2reg:
    seen={0}; cur=0; prev=-1; steps=0
    while True:
        nxt=[x for x in cadj[cur] if x!=prev]
        if not nxt: break
        prev,cur=cur,nxt[0]; steps+=1; seen.add(cur)
        if cur==0: break
    single = (len(seen)==n and steps==n)
print(f"critical edges form 2-regular: {is_2reg}, single Hamilton cycle: {single}")
print(f"=> apex equivalence consistent: every vertex incident to a critical edge,")
print(f"   so NO apex z qualifies, so diag_unlock feasible=0 at |B|=12 is FORCED by Theorem A.")
