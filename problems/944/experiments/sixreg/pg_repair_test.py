"""Test A (GPT round-4): PG(2,5)-repair 3+3 surgery — does it pass [T]+[K]?
Surgery: pick point p, line l. Delete 3 edges at p (to lines L1..L3) and 3 at l
(to points P1..P3); repair the 6 unit deficits by a non-incidence matching
Pj-Lpi(j). Result: b(p)=b(l)=3, all others full, sum b=6, bipartite simple.
[C] automatic (3+3). Check [T] (comparable nonadjacent full pairs) and [K]
(boundary-shortfall: every v has a colouring of H-v with shortfall <= b(v)).
"""
import itertools, random, sys
rng = random.Random(944)
pts = [(x,y,1) for x in range(5) for y in range(5)] + [(x,1,0) for x in range(5)] + [(1,0,0)]
N = 62
def base_adj():
    adj = [set() for _ in range(N)]
    for p in range(31):
        for l in range(31):
            if (pts[p][0]*pts[l][0] + pts[p][1]*pts[l][1] + pts[p][2]*pts[l][2]) % 5 == 0:
                adj[p].add(31+l); adj[31+l].add(p)
    return adj
def witness_shortfall(adj, v, b_v, cap=2_000_000):
    """exists colouring of H-v with sum max(0,2-cnt_i) <= b_v? returns True/False/None(cap)"""
    nv = sorted(adj[v])
    order = nv + sorted((u for u in range(N) if u != v and u not in adj[v]),
                        key=lambda u: -len(adj[u]))
    col = {}; cnt = [0,0,0]; nodes = [0]
    def short(c):
        return sum(max(0, 2-x) for x in c)
    def bt(i):
        nodes[0] += 1
        if nodes[0] > cap: return None
        if i == len(order): return short(cnt) <= b_v
        w = order[i]
        for c in range(3):
            if any(col.get(u) == c for u in adj[w] if u != v): continue
            col[w] = c
            if w in adj[v]: cnt[c] += 1
            r = bt(i+1)
            if w in adj[v]: cnt[c] -= 1
            del col[w]
            if r: return True
            if r is None: return None
        return False
    return bt(0)
def surgery(adj, p, l):
    """returns modified adj or None"""
    A = [set(s) for s in adj]
    Ls = rng.sample(sorted(A[p]), 3)              # 3 lines at p
    Ps = rng.sample(sorted(A[31+l] if 31+l in range(N) else A[l]), 3)  # careful: l is line index 0..30 -> vertex 31+l
    lv = 31 + l
    Ps = rng.sample(sorted(A[lv]), 3)
    if p in Ps or lv in Ls: return None
    for L in Ls: A[p].discard(L); A[L].discard(p)
    for P in Ps: A[lv].discard(P); A[P].discard(lv)
    # repair: match Ps to Ls via non-incidences
    for perm in itertools.permutations(range(3)):
        ok = all(Ls[perm[j]] not in adj[Ps[j]] and Ls[perm[j]] not in A[Ps[j]] for j in range(3))
        if ok:
            for j in range(3): A[Ps[j]].add(Ls[perm[j]]); A[Ls[perm[j]]].add(Ps[j])
            return A
    return None
base = base_adj()
trials = 0
for attempt in range(40):
    p = rng.randrange(31); l = rng.randrange(31)
    A = surgery(base, p, l)
    if A is None: continue
    b = [6 - len(A[v]) for v in range(N)]
    if sum(b) != 6 or sorted(x for x in b if x) != [3,3]: continue
    # connectivity
    seen = {0}; st = [0]
    while st:
        x = st.pop()
        for y in A[x]:
            if y not in seen: seen.add(y); st.append(y)
    if len(seen) != N: continue
    trials += 1
    # [T]: full u,v nonadjacent with N(u) subset N(v): impossible deg-6 vs deg-6 unless equal nbhd; quick check
    badT = False
    fulls = [v for v in range(N) if b[v] == 0]
    # only same-side pairs can have containment (bipartite)
    for u in fulls:
        for v in fulls:
            if u == v or v in A[u]: continue
            if A[u] <= A[v]: badT = True; break
        if badT: break
    # [K] all vertices
    frozen_at = None; capped = None
    for v in range(N):
        r = witness_shortfall(A, v, b[v])
        if r is None: capped = v; break
        if not r: frozen_at = v; break
    print(f"instance {trials}: p={p} l={l} [T]ok={not badT} [K]frozenAt={frozen_at} capped={capped}", flush=True)
    if trials >= 3: break
