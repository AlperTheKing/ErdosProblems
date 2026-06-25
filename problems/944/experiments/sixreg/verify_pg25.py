"""Independent verification: PG(2,5) incidence graph vertices are unfrozen.
Builds the graph from scratch, finds+VERIFIES witnesses for v=0 (point) and
v=31 (line): proper 3-colouring of G-v with N(v) colour counts (2,2,2)."""
import itertools, sys
pts = [(x,y,1) for x in range(5) for y in range(5)] + [(x,1,0) for x in range(5)] + [(1,0,0)]
assert len(pts) == 31
N = 62
adj = [set() for _ in range(N)]
for p in range(31):
    for l in range(31):
        if (pts[p][0]*pts[l][0] + pts[p][1]*pts[l][1] + pts[p][2]*pts[l][2]) % 5 == 0:
            adj[p].add(31+l); adj[31+l].add(p)
assert all(len(adj[v]) == 6 for v in range(N))
# girth check (should be 6: no 4-cycles - two points share exactly one line)
for p in range(31):
    for q in range(p+1, 31):
        assert len(adj[p] & adj[q]) == 1   # exactly one common line
print("graph OK: 6-regular bipartite, any two points on exactly 1 common line (girth 6)")
def find_witness(v):
    nv = sorted(adj[v])
    order = nv + [u for u in range(N) if u != v and u not in adj[v]]
    col = {}; cnt = [0,0,0]
    def bt(i):
        if i == len(order): return True
        w = order[i]
        for c in range(3):
            if w in adj[v] and cnt[c] >= 2: continue
            if any(col.get(u) == c for u in adj[w] if u != v): continue
            col[w] = c
            if w in adj[v]: cnt[c] += 1
            if bt(i+1): return True
            if w in adj[v]: cnt[c] -= 1
            del col[w]
        return False
    if not bt(0): return None
    return dict(col)
for v in [0, 31]:
    wit = find_witness(v)
    assert wit is not None, f"v={v} FROZEN?!"
    # VERIFY independently
    for u in range(N):
        if u == v: continue
        for w2 in adj[u]:
            if w2 == v or w2 <= u: continue
            assert wit[u] != wit[w2], "improper!"
    cnts = [0,0,0]
    for u in adj[v]: cnts[wit[u]] += 1
    assert cnts == [2,2,2], f"counts {cnts}"
    print(f"v={v}: VERIFIED unfrozen (proper colouring of G-v, N(v) counts (2,2,2))")
print("CONCLUSION: by point/line-transitivity + self-duality, ALL 62 vertices unfrozen.")
print("Lemma D (general form, q=0 included) is REFUTED at n=62, girth 6.")
