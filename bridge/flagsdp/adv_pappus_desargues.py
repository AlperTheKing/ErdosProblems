#!/usr/bin/env python3
"""Pappus (N=18) and Desargues (N=20): within-part chords, efficient.

For these the natural parity bipartition cuts all original edges. We add within-part
chords (monochromatic = bad edges). We test whether parity is still THE max cut using
a fast branch-and-bound max-cut, and only call the (expensive but exact) safe-peel /
cut-dom check via check_instance with side=parity when parity is confirmed maximal.

We bias to far-apart chord pairs to maximize Gamma. Writes results incrementally.
"""
import itertools, sys
from collections import deque
from peel_check import check_instance, is_triangle_free

def lcf_graph(n, lcf):
    adj = [set() for _ in range(n)]
    for i in range(n):
        j = (i + 1) % n
        adj[i].add(j); adj[j].add(i)
    for i in range(n):
        j = (i + lcf[i]) % n
        adj[i].add(j); adj[j].add(i)
    return adj

def maxcut_value_bb(n, edges):
    """exact max-cut value via simple DFS branch-and-bound on vertex colors."""
    adj = [[] for _ in range(n)]
    for (u, v) in edges:
        adj[u].append(v); adj[v].append(u)
    best = [0]
    color = [-1] * n
    # order vertices by degree desc for better pruning
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    pos = {v: i for i, v in enumerate(order)}
    def rem_upper(i):
        # crude upper bound: all remaining edges among unassigned could be cut
        return None
    def dfs(i, cut):
        if i == n:
            if cut > best[0]:
                best[0] = cut
            return
        # simple bound: cut + (#edges not yet both-assigned)
        v = order[i]
        for c in (0, 1):
            color[v] = c
            add = 0
            for w in adj[v]:
                if color[w] != -1 and color[w] != c:
                    add += 1
            # prune: optimistic remaining = edges with >=1 endpoint unassigned
            # compute optimistic bound
            dfs(i + 1, cut + add)
        color[v] = -1
    # optimistic bound prune
    # to keep it fast we add a bound based on remaining edges
    sys.setrecursionlimit(10000)
    dfs(0, 0)
    return best[0]

NAMED = {
    "Pappus":    (18, [5, 7, -7, 7, -7, -5] * 3),
    "Desargues": (20, [5, -5, 9, -9] * 5),
}

def within_part_cands(n, adj, side):
    cs = []
    for u in range(n):
        for v in range(u + 1, n):
            if side[u] != side[v]: continue
            if v in adj[u]: continue
            if adj[u] & adj[v]: continue
            cs.append((u, v))
    return cs

def Bdist(n, adj, side, s, t):
    d = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if side[u] != side[w] and w not in d:
                d[w] = d[u] + 1; q.append(w)
    return d.get(t, None)

LOG = open("adv_pappus_desargues_results.txt", "w")
def out(*a):
    s = " ".join(str(x) for x in a)
    sys.stdout.write(s + "\n"); sys.stdout.flush()
    LOG.write(s + "\n"); LOG.flush()

def run():
    tested = 0
    obstructions = 0
    near = []
    for name, (n, lcf) in NAMED.items():
        adj0 = lcf_graph(n, lcf)
        side = [v % 2 for v in range(n)]
        assert all(side[u] != side[v] for u in range(n) for v in adj0[u]), name
        base_edges = [(u, v) for u in range(n) for v in adj0[u] if v > u]
        E = len(base_edges)
        out(f"=== {name} N={n} |E|={E} parity-cut=ALL ===")
        cands = within_part_cands(n, adj0, side)
        scored = sorted(cands, key=lambda uv: -(Bdist(n, adj0, side, uv[0], uv[1]) or 0))
        # exhaustive singles + many doubles + sampled triples, but ONLY run the
        # expensive check_instance when parity stays max.
        def attempt(chords):
            nonlocal tested, obstructions
            adj = [set(s) for s in adj0]
            for (x, y) in chords:
                if y in adj[x] or (adj[x] & adj[y]):
                    return
                adj[x].add(y); adj[y].add(x)
            edges = base_edges + list(chords)
            mc = maxcut_value_bb(n, edges)
            paritycut = E  # parity cuts all original edges, none of the within-part chords
            if mc != paritycut:
                return  # parity not max -> harness would reject; skip (true maxcut differs)
            tested += 1
            r = check_instance(n, adj, side=side)
            if not r.get("ok") or r.get("m", 0) < 2 or not r.get("B_connected"):
                return
            g = r["gamma"]; n2 = r["n2"]; ratio = g / n2
            if ratio >= 0.7:
                near.append((ratio, name, tuple(chords), r["m"], g, n2, r["tight"], r.get("has_safe_peel")))
            if r.get("ge_n2") and r.get("has_safe_peel") is False:
                obstructions += 1
                out(f"  OBSTRUCTION {name} chords={chords} m={r['m']} gamma={g} n2={n2} detail={r['detail']}")

        for ch in scored:
            attempt([ch])
        for a, b in itertools.combinations(scored, 2):
            attempt([a, b])
        # triples among the top-distance candidates
        top = scored[:18]
        cnt = 0
        for trip in itertools.combinations(top, 3):
            attempt(list(trip)); cnt += 1
            if cnt >= 1500: break
        out(f"  [{name}] done. running tested={tested} obstructions={obstructions}")

    out(f"\n===== TESTED {tested}  OBSTRUCTIONS {obstructions} =====")
    near.sort(reverse=True)
    out("TOP near-tight:")
    for t in near[:20]:
        out("  ", t)

if __name__ == "__main__":
    run()
