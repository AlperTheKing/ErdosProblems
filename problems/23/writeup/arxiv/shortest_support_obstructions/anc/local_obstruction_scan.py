"""
GAP#1 TASK D3, Comp 2: LOCAL-OBSTRUCTION search.

A minimal Hall violator S of Ell5SupportExpansion (|S| = m) forces the following LOCAL structure
(all conditions NECESSARY, proven in the writeup):
  F := E_short(S) is a CONNECTED BIPARTITE graph with |F| = m-1 edges (F subset of blue graph B);
  each atom (u,v) has d_F(u,v) = 4 exactly, and its F-support = union of edges of all length-4
    F-paths u..v equals its true support P_e (since P_e subset F and every F-geodesic is a B-geodesic);
  the m atoms are m DISTINCT vertex pairs; the atom graph H (edges = atom pairs) is TRIANGLE-FREE
    (atoms are edges of the ambient triangle-free G);
  union of supports = F  (definition of E_short);
  every edge of F lies in >= 2 supports  (no private edge, compiled minimal_hall_obstruction_no_private_edge).

LocalObstruction(m) := exists such (F, A) with |A| = m = |F|+1.
This script decides LocalObstruction(m) for m in a range by exhaustive enumeration of F
(geng -c -b, n = 5..e+1 vertices, e = m-1 edges) + DFS over atom sets.
If no LocalObstruction(m) exists for all m <= M, every minimal violator has |S| > M.
"""
import sys, subprocess, json, os
from collections import deque
from itertools import combinations
from multiprocessing import Pool

GENG = os.environ.get("GENG", "geng")

def parse_g6(s):
    s = s.strip()
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for x in data[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    adj = [[] for _ in range(n)]
    idx = 0
    edges = []
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i].append(j)
                adj[j].append(i)
                edges.append((i, j))
            idx += 1
    return n, adj, edges

def bfs(adj, n, s):
    d = [-1]*n
    d[s] = 0
    q = deque([s])
    while q:
        x = q.popleft()
        for y in adj[x]:
            if d[y] < 0:
                d[y] = d[x]+1
                q.append(y)
    return d

NODE_CAP = 5_000_000

def check_F(args):
    """Return (found_witness_or_None, aborted_flag, npairs)."""
    g6, = args
    n, adj, edges = parse_g6(g6)
    e = len(edges)
    m = e + 1
    eidx = {}
    for k, (i, j) in enumerate(edges):
        eidx[(i, j)] = k
        eidx[(j, i)] = k
    dist = [bfs(adj, n, s) for s in range(n)]
    # pairs at distance exactly 4, with their F-support bitmask
    pairs = []
    for u in range(n):
        for v in range(u+1, n):
            if dist[u][v] == 4:
                du, dv = dist[u], dist[v]
                sup = 0
                for (x, y) in edges:
                    if (du[x] + 1 + dv[y] == 4) or (du[y] + 1 + dv[x] == 4):
                        sup |= 1 << eidx[(x, y)]
                pairs.append(((u, v), sup))
    if len(pairs) < m:
        return None, False, len(pairs)
    full = (1 << e) - 1
    # union of ALL supports must be able to reach full
    tot = 0
    for _, s in pairs:
        tot |= s
    if tot != full:
        return None, False, len(pairs)
    P = len(pairs)
    # suffix availability per edge: how many pairs with index >= i contain edge c
    avail = [[0]*e for _ in range(P+1)]
    for i in range(P-1, -1, -1):
        s = pairs[i][1]
        for c in range(e):
            avail[i][c] = avail[i+1][c] + ((s >> c) & 1)
    # DFS: choose exactly m pairs, triangle-free H, coverage mult>=2 each edge
    mult = [0]*e
    nb = {}   # vertex -> set of chosen H-neighbors
    chosen = []
    nodes = [0]
    aborted = [False]

    def dfs(i, need):
        if aborted[0]:
            return None
        nodes[0] += 1
        if nodes[0] > NODE_CAP:
            aborted[0] = True
            return None
        if need == 0:
            if all(mm >= 2 for mm in mult):
                return list(chosen)
            return None
        if P - i < need:
            return None
        # coverage feasibility
        for c in range(e):
            if mult[c] + avail[i][c] < 2:
                return None
        (u, v), s = pairs[i]
        # try include (if triangle-free)
        if not (nb.get(u, frozenset()) & nb.get(v, frozenset())):
            nb.setdefault(u, set()).add(v)
            nb.setdefault(v, set()).add(u)
            b = s
            while b:
                c = (b & -b).bit_length() - 1
                mult[c] += 1
                b &= b - 1
            chosen.append(i)
            r = dfs(i+1, need-1)
            if r is not None:
                return r
            chosen.pop()
            b = s
            while b:
                c = (b & -b).bit_length() - 1
                mult[c] -= 1
                b &= b - 1
            nb[u].discard(v)
            nb[v].discard(u)
        return dfs(i+1, need)

    # convert nb sets: use frozenset check trick -> plain sets fine
    def nbint(u, v):
        return nb.get(u, set()) & nb.get(v, set())
    # patch: redo include-check with sets
    # (dfs above uses frozenset default; set() & set() fine)
    w = dfs(0, m)
    if w is not None:
        return (g6, [(pairs[i][0], pairs[i][1]) for i in w]), aborted[0], P
    return None, aborted[0], P

def run_m(m, workers=16):
    e = m - 1
    witnesses = []
    aborted_count = 0
    total = 0
    maxpairs = 0
    for n in range(5, e + 2):
        p = subprocess.run([GENG, "-q", "-c", "-b", str(n), f"{e}:{e}"],
                           capture_output=True, text=True)
        lines = [l for l in p.stdout.splitlines() if l.strip()]
        total += len(lines)
        if not lines:
            continue
        with Pool(workers) as pool:
            for res, ab, np_ in pool.imap_unordered(check_F, [(l,) for l in lines],
                                                    chunksize=max(1, len(lines)//(workers*4) or 1)):
                if ab:
                    aborted_count += 1
                if np_ > maxpairs:
                    maxpairs = np_
                if res is not None:
                    witnesses.append(res)
    return {"m": m, "e": e, "graphs": total, "witnesses": witnesses[:5],
            "n_witnesses": len(witnesses), "aborted": aborted_count, "max_pairs_seen": maxpairs}

def spider_test(t):
    """Spider: center 0, legs (mid_i, leaf_i); e = 2t edges; test LocalObstruction(2t+1)."""
    e = 2 * t
    m = e + 1
    n = 1 + 2 * t
    edges = []
    for i in range(t):
        mid = 1 + 2*i
        leaf = 2 + 2*i
        edges.append((0, mid))
        edges.append((mid, leaf))
    adj = [[] for _ in range(n)]
    for (a, b) in edges:
        adj[a].append(b)
        adj[b].append(a)
    eidx = {}
    for k, (a, b) in enumerate(edges):
        eidx[(a, b)] = k
        eidx[(b, a)] = k
    dist = [bfs(adj, n, s) for s in range(n)]
    leaves = [2 + 2*i for i in range(t)]
    # pairs at distance 4 = leaf pairs; support = both legs (4 edges)
    # triangle-free H on t leaves with 2t+1 edges, covering every leg >= 2: take bipartite split
    half = t // 2
    A, Bv = leaves[:half], leaves[half:]
    H = [(a, b) for a in A for b in Bv]
    if len(H) < m:
        return {"t": t, "e": e, "m": m, "feasible": False,
                "reason": f"Mantel: max TF edges {len(H)} (balanced split) < {m}"}
    H = H[:m]
    # check coverage: every leaf used >= ... every leg edge needs mult>=2 => every leaf in >=2 pairs
    from collections import Counter
    cnt = Counter()
    for (a, b) in H:
        cnt[a] += 1
        cnt[b] += 1
    ok = all(cnt[l] >= 2 for l in leaves)
    return {"t": t, "e": e, "m": m, "feasible": bool(ok), "H_size": len(H),
            "min_leaf_mult": min(cnt[l] for l in leaves) if ok or True else None}

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "scan":
        mlo, mhi = int(sys.argv[2]), int(sys.argv[3])
        workers = int(sys.argv[4]) if len(sys.argv) > 4 else 16
        for m in range(mlo, mhi + 1):
            r = run_m(m, workers)
            print(json.dumps(r, default=str), flush=True)
    elif mode == "spider":
        for t in range(4, 11):
            print(json.dumps(spider_test(t)), flush=True)

