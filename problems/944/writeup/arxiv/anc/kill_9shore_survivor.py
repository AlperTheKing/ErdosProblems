"""Local kill test for the unique 9-shore survivor H = HEzftz{.

For each internal vertex v (b(v)=0, so N_G(v) = N_H(v) entirely inside A):
enumerate ALL proper 3-colourings of H - v and check the colour counts on N_H(v).
In a target, chi(G-v)=3 gives a proper colouring phi of G-v whose restriction to
H - v is proper; Lemma 1.1 forces every colour to appear >= 2 times in N(v) under
phi (count 0 => G 3-colourable; count 1 => critical edge). The counts depend only
on phi|N(v), and N(v) is inside H - v. So:
  if EVERY proper 3-colouring of H - v has some colour count <= 1 on N_H(v),
  then H cannot be a 9-shore of any 6-regular target.  (KILL)
"""
EDGES = [(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(1,3),(1,4),(1,5),(1,6),(1,8),
         (2,4),(2,5),(2,6),(2,7),(2,8),(3,6),(3,7),(3,8),(4,6),(4,7),(4,8),
         (5,7),(5,8)]
N = 9
adj = [set() for _ in range(N)]
for a,b in EDGES: adj[a].add(b); adj[b].add(a)
internal = [v for v in range(N) if len(adj[v]) == 6]
print('internal vertices:', internal)

def colourings(verts, adjacency):
    verts = list(verts); out = []; col = {}
    def bt(i):
        if i == len(verts): out.append(dict(col)); return
        v = verts[i]
        used = {col[u] for u in adjacency[v] if u in col}
        for c in range(3):
            if c not in used:
                col[v] = c; bt(i+1); del col[v]
    bt(0)
    return out

all_killed = True
for v in internal:
    others = [u for u in range(N) if u != v]
    cols = colourings(others, adj)
    ok_exists = []
    for phi in cols:
        cnt = [0,0,0]
        for u in adj[v]: cnt[phi[u]] += 1
        if min(cnt) >= 2: ok_exists.append((phi, cnt))
    print(f'v={v}: colourings of H-v: {len(cols)}, with all counts>=2 on N(v): {len(ok_exists)}')
    if ok_exists:
        all_killed = False
        ex = ok_exists[0]
        print('   example surviving colouring:', [ex[0][u] for u in sorted(ex[0])], 'counts', ex[1])
print('H KILLED (9-shores fully excluded)' if all_killed else 'H NOT killed by this test')
