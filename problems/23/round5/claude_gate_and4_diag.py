"""ROOT-AGENT DIAGNOSTIC (Claude): the minor says odd-K5, the covering number says 3, not 4.

Exactly one of these is wrong and I will not record either until I know which:
  (i)  claude_gate_and4_oddk5.py --and4 verifies branch sets {0,4,8},{1,5,9},{2,6,10},{3},{7}
       of Gamma_11 are connected + bipartite and that all 10 pairs carry a connecting edge with
       equal switching label, i.e. an ODD-K5 minor;
  (ii) with weight 0 on the 6 contracted edges, 1 on the 10 kept edges and M on the 6 deleted
       ones, tau_w = 3 for every M >= 4 -- but covering all 10 triangles of K5 needs 4 edges.

So I build the clutter minor of the odd-cycle clutter EXPLICITLY,
       C \\ Z / Y  =  minimal sets among { C \\ Y : C an odd cycle, C disjoint from Z },
and compare it against the odd-cycle clutter of odd-K5 (the 10 triangles + 12 five-cycles).
Whichever member is missing tells me which step of the lifting argument fails.
"""
from itertools import combinations


def gamma(n):
    return [(u, v) for u in range(n) for v in range(u + 1, n)
            if 3 * min((u - v) % n, (v - u) % n) > n]


n = 11
E = gamma(n)
idx = {e: i for i, e in enumerate(E)}
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)

branch = [{0, 4, 8}, {1, 5, 9}, {2, 6, 10}, {3}, {7}]
bof = {v: i for i, T in enumerate(branch) for v in T}
Y = {idx[tuple(sorted((u, v)))] for T in branch for u, v in combinations(sorted(T), 2) if v in A[u]}
KEEP = [(0, 1, (1, 8)), (0, 2, (2, 8)), (0, 3, (3, 8)), (0, 4, (0, 7)), (1, 2, (2, 9)),
        (1, 3, (3, 9)), (1, 4, (1, 7)), (2, 3, (3, 10)), (2, 4, (2, 7)), (3, 4, (3, 7))]
keep = {idx[e]: (i, j) for i, j, e in KEEP}
Z = set(range(len(E))) - Y - set(keep)
print(f"Y (contracted) {sorted(Y)}   keep {sorted(keep)}   Z (deleted) {sorted(Z)}")

# ---- all odd cycles of Gamma_11
odd = set()
for s in range(n):
    def dfs(u, path, elist):
        for v in sorted(A[u]):
            if v == s and len(path) >= 3 and len(path) % 2 == 1:
                odd.add(frozenset(elist + [idx[tuple(sorted((u, v)))]]))
            elif v > s and v not in path:
                dfs(v, path | {v}, elist + [idx[tuple(sorted((u, v)))]])
    dfs(s, {s}, [])
print(f"odd cycles of Gamma_11: {len(odd)}")

# ---- the clutter minor
raw = {frozenset(c - Y) for c in odd if not (c & Z)}
mem = sorted((m for m in raw if not any(o < m for o in raw)), key=lambda m: (len(m), sorted(m)))
print(f"clutter minor C\\Z/Y: {len(mem)} members, sizes {sorted({len(m) for m in mem})}")

pair = {i: p for i, p in keep.items()}
tri_present = set()
for m in mem:
    if len(m) == 3:
        tri_present.add(frozenset().union(*[set(pair[i]) for i in m]))
alltri = {frozenset(t) for t in combinations(range(5), 3)}
print(f"triangles of K5 realised as 3-element members: {len(tri_present)} of 10")
for t in sorted(alltri - tri_present, key=sorted):
    tedges = [i for i, p in pair.items() if set(p) <= set(t)]
    print(f"  MISSING triangle {sorted(t)}  (kept edges {[(pair[i], E[i]) for i in tedges]})")
    for i in tedges:
        pass

# ---- tau of the clutter minor, brute force over the 10 kept edges
ks = sorted(keep)
best = None
for r in range(0, 11):
    for S in combinations(ks, r):
        Ss = set(S)
        if all(m & Ss for m in mem):
            best = S
            break
    if best:
        break
print(f"tau(clutter minor) = {len(best)}  via {[ (pair[i], E[i]) for i in best ]}")
print(f"tau(odd-K5) would be 4  ->  {'MATCH' if len(best) == 4 else 'MISMATCH: the minor is NOT odd-K5'}")

# ---- which lift fails: check each triangle's lift explicitly
print("\nlift check per triangle (branch indices -> lifted cycle in Gamma_11):")
for t in sorted(alltri, key=sorted):
    tedges = [i for i, p in pair.items() if set(p) <= set(t)]
    verts = set()
    for i in tedges:
        verts |= set(E[i])
    print(f"  {sorted(t)}: kept edges {[E[i] for i in tedges]}, endpoints {sorted(verts)}, "
          f"{'realised' if frozenset(t) in tri_present else 'NOT realised'}")
