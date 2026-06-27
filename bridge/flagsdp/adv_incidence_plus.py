#!/usr/bin/env python3
"""Adversarial angle: incidence-bipartite-plus.
High-girth bipartite (triangle-free) named graphs (Heawood, Pappus, Desargues,
Mobius-Kantor, Wagner/V8, plus the Levi/incidence graphs) with a few added chords
to force m>=2 bad edges, then check the safe-peel lemma.

We add chords carefully to preserve triangle-freeness, then enumerate which chords
land monochromatically under the max cut (the harness auto-picks the Gamma-minimizing
max cut and reports m, gamma, has_safe_peel).
"""
import itertools
from peel_check import check_instance

# ---- named graphs as edge lists (vertices 0..n-1) ----

def heawood():
    # Heawood graph: incidence graph of Fano plane. Standard LCF [5,-5]^7 on 14 vertices.
    n = 14
    edges = set()
    for i in range(n):
        edges.add((i, (i + 1) % n))
    # LCF [5,-5]^7
    lcf = [5, -5] * 7
    for i in range(n):
        j = (i + lcf[i]) % n
        edges.add((min(i, j), max(i, j)))
    return n, edges

def mobius_kantor():
    # Mobius-Kantor graph, 16 vertices, LCF [5,-5]^8
    n = 16
    edges = set()
    for i in range(n):
        edges.add((min(i, (i + 1) % n), max(i, (i + 1) % n)))
    lcf = [5, -5] * 8
    for i in range(n):
        j = (i + lcf[i]) % n
        edges.add((min(i, j), max(i, j)))
    return n, edges

def pappus():
    # Pappus graph, 18 vertices, LCF [5,7,-7,7,-7,-5]^3
    n = 18
    edges = set()
    for i in range(n):
        edges.add((min(i, (i + 1) % n), max(i, (i + 1) % n)))
    lcf = [5, 7, -7, 7, -7, -5] * 3
    for i in range(n):
        j = (i + lcf[i]) % n
        edges.add((min(i, j), max(i, j)))
    return n, edges

def desargues():
    # Desargues graph, 20 vertices, LCF [5,-5,9,-9]^5
    n = 20
    edges = set()
    for i in range(n):
        edges.add((min(i, (i + 1) % n), max(i, (i + 1) % n)))
    lcf = [5, -5, 9, -9] * 5
    for i in range(n):
        j = (i + lcf[i]) % n
        edges.add((min(i, j), max(i, j)))
    return n, edges

def wagner():
    # Wagner graph (Mobius-Kantor V8): 8-cycle plus 4 diameters. NOT bipartite (has odd cycles).
    n = 8
    edges = set()
    for i in range(n):
        edges.add((min(i, (i + 1) % n), max(i, (i + 1) % n)))
    for i in range(4):
        edges.add((i, i + 4))
    return n, edges

def to_adj(n, edges):
    adj = [set() for _ in range(n)]
    for (u, v) in edges:
        if u != v:
            adj[u].add(v); adj[v].add(u)
    return adj

def add_chords_tf(n, edges, chords):
    """Add chords only if they keep the graph triangle-free. Returns (adj, added)."""
    adj = to_adj(n, edges)
    added = []
    for (u, v) in chords:
        if u == v or v in adj[u]:
            continue
        # adding u-v creates a triangle iff u,v share a neighbor
        if adj[u] & adj[v]:
            continue
        adj[u].add(v); adj[v].add(u); added.append((u, v))
    return adj, added

NAMED = {
    "Heawood": heawood,
    "MobiusKantor": mobius_kantor,
    "Pappus": pappus,
    "Desargues": desargues,
    "Wagner": wagner,
}

def all_chord_candidates(n, adj):
    """Pairs not already adjacent and not sharing a neighbor (triangle-safe)."""
    cands = []
    for u in range(n):
        for v in range(u + 1, n):
            if v in adj[u]:
                continue
            if adj[u] & adj[v]:
                continue
            cands.append((u, v))
    return cands

def report(tag, r):
    if not r.get("ok"):
        return f"  [{tag}] SKIP ok=False tf={r.get('triangle_free')} detail={r.get('detail')}"
    line = (f"  [{tag}] N={r['N']} m={r.get('m')} gamma={r.get('gamma')} n2={r.get('n2')} "
            f"tight={r.get('tight')} ge_n2={r.get('ge_n2')} Bconn={r.get('B_connected')} "
            f"safe_peel={r.get('has_safe_peel')}")
    obstruction = (r.get('ok') and r.get('triangle_free') and r.get('B_connected')
                   and r.get('ge_n2') and r.get('m', 0) >= 2 and r.get('has_safe_peel') is False)
    if obstruction:
        line += "  <<< OBSTRUCTION"
    return line

if __name__ == "__main__":
    interesting = []   # near-tight or obstruction
    obstructions = []
    tested = 0

    for name, gen in NAMED.items():
        n, edges = gen()
        adj0 = to_adj(n, edges)
        tf0 = all(not (adj0[u] & adj0[v]) for u in range(n) for v in adj0[u] if v > u)
        print(f"=== {name}: N={n} edges={len(edges)} triangle_free={tf0} ===")
        # base (no chords): empty M -> harness will report no finite-Gamma config or m=0
        cands = all_chord_candidates(n, adj0)
        # Try single, double, and triple chord additions (limited, but many combos).
        # singles
        for (a, b) in cands:
            adj, added = add_chords_tf(n, edges, [(a, b)])
            if len(added) < 1:
                continue
            r = check_instance(n, adj)
            tested += 1
            if r.get("ok") and r.get("m", 0) >= 2 and r.get("ge_n2"):
                interesting.append((name, ("single", (a, b)), r))
            if (r.get('ok') and r.get('triangle_free') and r.get('B_connected')
                    and r.get('ge_n2') and r.get('m', 0) >= 2 and r.get('has_safe_peel') is False):
                obstructions.append((name, ("single", (a, b)), r))
        # doubles (sample to keep runtime bounded)
        import random
        random.seed(12345)
        pairs = list(itertools.combinations(cands, 2))
        random.shuffle(pairs)
        for ((a, b), (c, d)) in pairs[:4000]:
            adj, added = add_chords_tf(n, edges, [(a, b), (c, d)])
            if len(added) < 2:
                continue
            r = check_instance(n, adj)
            tested += 1
            if r.get("ok") and r.get("m", 0) >= 2 and r.get("ge_n2"):
                interesting.append((name, ("double", ((a, b), (c, d))), r))
            if (r.get('ok') and r.get('triangle_free') and r.get('B_connected')
                    and r.get('ge_n2') and r.get('m', 0) >= 2 and r.get('has_safe_peel') is False):
                obstructions.append((name, ("double", ((a, b), (c, d))), r))

    print(f"\nTESTED {tested} instances.")
    print(f"INTERESTING (m>=2, gamma>=N^2): {len(interesting)}")
    for (name, how, r) in interesting[:50]:
        print(report(f"{name} {how}", r))
    print(f"\nOBSTRUCTIONS: {len(obstructions)}")
    for (name, how, r) in obstructions[:50]:
        print(report(f"{name} {how}", r))
