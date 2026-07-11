#!/usr/bin/env python3
"""My independent gate of Codex's N=20 sigma-gap CE (r36_freepair_proof).
Claims: triangle-free; maxcut=20 (exhaustive 2^20) attained by the displayed shores; bad set = the 4
closing edges; f0's complete row family = exactly {(0,2,3,4,1),(0,7,10,15,1)}; pair (0,5): same shore,
pairCount 0, 0-5 not an edge (so neither half ScopedReserved); dB=3, dM=2, sigma=1 < 2 => production
TerminalData.Valid (dM+2<=dB) FAILS while maxcut only guarantees sigma>=0.
Everything re-derived from the raw construction; ASCII prints only."""
from itertools import combinations

N = 20
# cycles: path r0..r4 (blue) + closing bad edge (r0,r4)
CYC = [(0, 2, 3, 4, 1), (5, 7, 8, 9, 6), (10, 12, 13, 14, 11), (15, 17, 18, 19, 16)]
EXTRA = [(0, 7), (7, 10), (10, 15), (15, 1)]
E = set()
for r in CYC:
    for i in range(4):
        E.add(frozenset((r[i], r[i + 1])))
    E.add(frozenset((r[0], r[4])))
for u, v in EXTRA:
    E.add(frozenset((u, v)))
assert len(E) == 24, len(E)

adj = [set() for _ in range(N)]
for e in E:
    u, v = sorted(e)
    adj[u].add(v)
    adj[v].add(u)

# 1. triangle-free
tri = any(w in adj[u] for u, v in combinations(range(N), 2) if v in adj[u] for w in adj[u] & adj[v])
assert not tri, "triangle found"

# 2. exhaustive maxcut over 2^20 masks (my own bit implementation)
edges_idx = [tuple(sorted(e)) for e in E]
best = 0
for mask in range(1 << N):
    c = 0
    for u, v in edges_idx:
        c += ((mask >> u) ^ (mask >> v)) & 1
    if c > best:
        best = c
TRUE_SIDE = {0, 3, 1, 5, 8, 6, 10, 13, 11, 17, 19}
side = [v in TRUE_SIDE for v in range(N)]
shown = sum(1 for u, v in edges_idx if side[u] != side[v])
assert best == 20 and shown == 20, (best, shown)

# 3. bad set under the displayed cut == the 4 closing edges
bads = {(u, v) for u, v in edges_idx if side[u] == side[v]}
assert bads == {(0, 1), (5, 6), (10, 11), (15, 16)}, bads

# 4. complete 4-edge blue-path family 0 -> 1 (my own DFS)
def blue(u, v):
    return v in adj[u] and side[u] != side[v]

rows01 = []
def dfs(path):
    if len(path) == 5:
        if path[-1] == 1:
            rows01.append(tuple(path))
        return
    for w in range(N):
        if w not in path and blue(path[-1], w):
            if len(path) == 4 and w != 1:
                continue
            dfs(path + [w])
dfs([0])
assert sorted(rows01) == [(0, 2, 3, 4, 1), (0, 7, 10, 15, 1)], rows01

# 5. the probe pair (0,5)
assert side[0] == side[5]
selected = [tuple(r) for r in CYC]
pc = sum(1 for r in selected if 0 in r and 5 in r)
assert pc == 0, pc
assert 5 not in adj[0]  # 0-5 not an edge => not blue => neither half ScopedReserved
S = {0, 5}
dB = sum(1 for u, v in edges_idx if (u in S) != (v in S) and side[u] != side[v])
dM = sum(1 for u, v in edges_idx if (u in S) != (v in S) and side[u] == side[v])
assert (dB, dM) == (3, 2), (dB, dM)
sigma = dB - dM
assert sigma == 1
assert not (dM + 2 <= dB)  # production terminal FAILS
# owner v=7: blue to both 0 (off-support) and 5 (support edge of f1's row)
assert blue(7, 0) and blue(7, 5)
support = {tuple(sorted((r[i], r[i + 1]))) for r in selected for i in range(4)}
assert (5, 7) in support and (0, 7) not in support

print("CLAUDE-GATE=PASS")
print("triangle_free=True maxcut_exhaustive=20 displayed=20 bads={(0,1),(5,6),(10,11),(15,16)}")
print("f0_complete_rows=[(0,2,3,4,1),(0,7,10,15,1)] pairCount(0,5)=0 edge05=absent")
print("dB=3 dM=2 sigma=1 terminal_dM+2<=dB FAILS -> R37 free-branch does NOT imply production CommonBlueOwner")
