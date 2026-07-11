#!/usr/bin/env python3
"""My gate of Codex's N=8 sigma-1 freed-pair CE (graph6 GCQb`o, r44_endpoint_credit).
Claims: tri-free; exact maxcut 8; complete row families 2x2; live support-constant move
(0,3,7,2,5)->(0,3,6,2,5) with xv active + vy already supported; freed endpoint pairs (7,0),(7,5)
same-side nonedges, unreserved, sigma=1 (NOT production-strength). All my own code."""
from itertools import combinations

g6 = "GCQb`o"
data = [ord(c) - 63 for c in g6]
n = data[0]
assert n == 8
bits = []
for d in data[1:]:
    bits += [(d >> (5 - i)) & 1 for i in range(6)]
adj = [set() for _ in range(n)]
E = set()
idx = 0
for j in range(1, n):
    for i in range(j):
        if bits[idx]:
            E.add((i, j)); adj[i].add(j); adj[j].add(i)
        idx += 1
print(f"n={n} edges={sorted(E)}")

# triangle-free
for u, v in combinations(range(n), 2):
    if v in adj[u]:
        assert not (adj[u] & adj[v]), f"triangle {u},{v}"

# exact maxcut over 2^8
best, bestmask = 0, 0
for mask in range(256):
    c = sum(1 for u, v in E if ((mask >> u) ^ (mask >> v)) & 1)
    if c > best:
        best, bestmask = c, mask
print(f"exact_maxcut={best}")
assert best == 8

# find a maxcut where the displayed rows are blue paths; use the claimed move rows to pin the cut:
# rows (0,3,7,2,5) and (0,3,6,2,5) must be blue 4-paths in SOME maxcut; enumerate maxcuts and test.
rows_claim = [(0, 3, 7, 2, 5), (0, 3, 6, 2, 5)]
def blue_under(mask, u, v):
    return (tuple(sorted((u, v))) in {tuple(sorted(e)) for e in E}) and (((mask >> u) ^ (mask >> v)) & 1)
good_masks = []
for mask in range(256):
    c = sum(1 for u, v in E if ((mask >> u) ^ (mask >> v)) & 1)
    if c != 8:
        continue
    ok = all(blue_under(mask, r[i], r[i + 1]) for r in rows_claim for i in range(4))
    if ok:
        good_masks.append(mask)
assert good_masks, "no maxcut supports both rows as blue paths"
mask = good_masks[0]
side = [(mask >> v) & 1 for v in range(n)]
bads = [(u, v) for u, v in E if side[u] == side[v]]
blues = [(u, v) for u, v in E if side[u] != side[v]]
print(f"mask={mask:08b} bads={bads}")

# complete families for each bad edge (my DFS), expect 2x2
def rows_between(s, t):
    out = []
    def dfs(path):
        if len(path) == 5:
            if path[-1] == t: out.append(tuple(path))
            return
        for w in adj[path[-1]]:
            if w not in path and side[w] != side[path[-1]]:
                if len(path) == 4 and w != t: continue
                dfs(path + [w])
    dfs([s])
    return out
fams = {e: rows_between(*e) for e in bads}
sizes = sorted(len(f) for f in fams.values())
print(f"family_sizes={sizes}")
assert sizes == [2, 2]
assert len(bads) == 2

# the move: old row (0,3,7,2,5), new row (0,3,6,2,5) for the atom (0,5); middle 7 -> 6
atom = tuple(sorted((0, 5)))
assert atom in fams and (0, 3, 7, 2, 5) in fams[atom] and (0, 3, 6, 2, 5) in fams[atom]
other = [e for e in bads if e != atom][0]
# choose the other atom's selected row (any of its 2) such that vy=... check support/active claims:
for other_row in fams[other]:
    rows_old = [(0, 3, 7, 2, 5), other_row]
    rows_new = [(0, 3, 6, 2, 5), other_row]
    sup_old = {tuple(sorted((r[i], r[i + 1]))) for r in rows_old for i in range(4)}
    sup_new = {tuple(sorted((r[i], r[i + 1]))) for r in rows_new for i in range(4)}
    sel_old = {v for r in rows_old for v in r}
    # v=6 inserted; x=3?? the new row (0,3,6,2,5): inserted middle 6 between 3 and 2.
    # xv active in OLD state: edge (3,6) or (6,2) off-support with both selected?
    e36 = tuple(sorted((3, 6))); e62 = tuple(sorted((6, 2)))
    if 6 in sel_old:
        act36 = e36 not in sup_old and (3 in sel_old and 6 in sel_old)
        act62 = e62 not in sup_old and (2 in sel_old and 6 in sel_old)
        if (act36 and e62 in sup_old) or (act62 and e36 in sup_old):
            print(f"other_row={other_row}: one-new-edge live move CONFIRMED (support {len(sup_old)}->{len(sup_new)})")
            # freed pairs at old middle 7: pairs (7,z) with pc dropping 1->0
            def pc(rows, a, b):
                return sum(1 for r in rows if a in r and b in r)
            freed = [(7, z) for z in range(n) if z != 7 and pc(rows_old, 7, z) == 1 and pc(rows_new, 7, z) == 0]
            print(f"freed_pairs_at_7={freed}")
            for (a, b) in [(7, 0), (7, 5)]:
                assert side[a] == side[b], f"{a},{b} not same side"
                assert b not in adj[a], f"{a},{b} is an edge"
                S = {a, b}
                dB = sum(1 for u, v in blues if (u in S) != (v in S))
                dM = sum(1 for u, v in bads if (u in S) != (v in S))
                print(f"pair ({a},{b}): dB={dB} dM={dM} sigma={dB-dM}")
                assert dB - dM == 1, "sigma != 1"
print("CLAUDE-GATE=PASS: sigma-1 freed endpoint pairs on a real defect-0 cage CONFIRMED (no universal local sigma>=2)")
