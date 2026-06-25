#!/usr/bin/env python3
"""
ATTACK H2 at n=3 (N=15) by SEARCHING FOR A COUNTEREXAMPLE.

H2 (n=3): every triangle-free G on 15 vertices admits a 5-set S with
    beta(G) - beta(G-S) <= 2n-1 = 5.
Trivial when beta<=5 (then beta(G-S)>=0>=beta-5). Nontrivial band: 6<=beta<=9.

A COUNTEREXAMPLE = a triangle-free 15-vtx graph with beta>=6 whose MIN over all
3003 5-sets of [beta(G)-beta(G-S)] is > 5. We were warned the danger zone is the
NON-C5-homomorphic hard core (Petersen-/Grotzsch-like). This script generates many
high-beta triangle-free graphs (blow-ups, perturbations, random-maximal, and
explicit non-hom cores extended to 15 vtx), and flags ANY H2 violation.

beta via exact brute-force MaxCut (2^V). No heuristics.
"""
import itertools
import random

random.seed(20260620)  # fixed seed: deterministic, reproducible

N = 15
TARGET = 5  # 2n-1 for n=3
BAND_LO = 6


def maxcut_adj(adj, verts):
    """exact MaxCut on induced subgraph `verts`, adj = full adjacency (set per vtx)."""
    m = len(verts)
    if m <= 1:
        return 0, 0
    idx = {v: i for i, v in enumerate(verts)}
    badj = [0] * m
    E = 0
    for a in verts:
        for b in adj[a]:
            if b in idx and a < b:
                ia, ib = idx[a], idx[b]
                badj[ia] |= (1 << ib)
                badj[ib] |= (1 << ia)
                E += 1
    best = 0
    for half in range(1 << (m - 1)):
        side1 = half << 1
        cut = 0
        x = side1
        while x:
            low = x & (-x)
            v = low.bit_length() - 1
            cut += bin(badj[v] & ~side1).count('1')
            x ^= low
        if cut > best:
            best = cut
    return best, E


def beta_of(adj, verts):
    mc, E = maxcut_adj(adj, verts)
    return E - mc


def has_triangle(adj):
    for u in range(len(adj)):
        for v in adj[u]:
            if v > u:
                if adj[u] & adj[v]:
                    return True
    return False


def min_5set_drop(adj):
    allv = list(range(N))
    bG = beta_of(adj, allv)
    if bG < BAND_LO:
        return bG, None  # trivial
    mn = None
    arg = None
    for S in itertools.combinations(allv, 5):
        Sset = set(S)
        rem = [v for v in allv if v not in Sset]
        d = bG - beta_of(adj, rem)
        if mn is None or d < mn:
            mn = d
            arg = S
            if mn <= TARGET:
                break  # H2 satisfied; no need to find the exact min
    return bG, (mn, arg)


def edges_to_adj(edges):
    adj = [set() for _ in range(N)]
    for (u, v) in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


# ---- generators -------------------------------------------------------------

def gen_c5_blowup(parts):
    """C5 blow-up with given 5 part sizes (sum=15). Vertices laid out by part."""
    assert sum(parts) == N and len(parts) == 5
    groups = []
    idx = 0
    for s in parts:
        groups.append(list(range(idx, idx + s)))
        idx += s
    edges = []
    for p in range(5):
        q = (p + 1) % 5
        for u in groups[p]:
            for v in groups[q]:
                edges.append((u, v))
    return edges_to_adj(edges)


def gen_random_maximal():
    """random maximal triangle-free graph on N vertices."""
    adj = [set() for _ in range(N)]
    pairs = [(u, v) for u in range(N) for v in range(u + 1, N)]
    random.shuffle(pairs)
    for (u, v) in pairs:
        if adj[u] & adj[v]:
            continue  # common neighbour -> would make triangle
        adj[u].add(v)
        adj[v].add(u)
    return adj


def perturb_high_beta(base_adj, steps=400):
    """hill-climb beta from base by random triangle-free edge toggles (greedy)."""
    adj = [set(s) for s in base_adj]
    allv = list(range(N))
    cur = beta_of(adj, allv)
    for _ in range(steps):
        u, v = random.sample(allv, 2)
        if v in adj[u]:
            # try removing
            adj[u].discard(v); adj[v].discard(u)
            nb = beta_of(adj, allv)
            if nb >= cur:
                cur = nb
            else:
                adj[u].add(v); adj[v].add(u)
        else:
            if adj[u] & adj[v]:
                continue  # would create triangle
            adj[u].add(v); adj[v].add(u)
            nb = beta_of(adj, allv)
            if nb >= cur:
                cur = nb
            else:
                adj[u].discard(v); adj[v].discard(u)
    return adj


PETERSEN = [(0,1),(1,2),(2,3),(3,4),(4,0),  # outer C5
            (5,7),(7,9),(9,6),(6,8),(8,5),   # inner pentagram
            (0,5),(1,6),(2,7),(3,8),(4,9)]    # spokes

GROTZSCH = [(0,1),(0,2),(0,3),(0,4),(0,5),   # hub 0 to inner C5 verts? build standard
            ]


def gen_petersen_plus5():
    """Petersen (10 vtx, non-C5-hom, beta=3) + 5 extra vertices attached
    triangle-free at random; many variants."""
    adj = [set() for _ in range(N)]
    for (u, v) in PETERSEN:
        adj[u].add(v); adj[v].add(u)
    # attach vertices 10..14 greedily triangle-free
    extra = [10, 11, 12, 13, 14]
    pairs = []
    for x in extra:
        for y in range(N):
            if y != x:
                pairs.append((min(x, y), max(x, y)))
    pairs = list(set(pairs))
    random.shuffle(pairs)
    for (u, v) in pairs:
        if v in adj[u]:
            continue
        if adj[u] & adj[v]:
            continue
        adj[u].add(v); adj[v].add(u)
    return adj


def grotzsch_adj():
    """Standard Mycielskian of C5 = Grotzsch graph (11 vtx, tri-free, chi=4,
    non-C5-hom, beta=5). Vertices 0..4 = C5; 5..9 = shadow; 10 = apex."""
    e = []
    C5 = [(0,1),(1,2),(2,3),(3,4),(4,0)]
    e += C5
    # shadow i (5+i) connects to neighbours of i in C5, and to apex 10
    nbr = {0:[1,4],1:[0,2],2:[1,3],3:[2,4],4:[0,3]}
    for i in range(5):
        for j in nbr[i]:
            e.append((5 + i, j))
        e.append((5 + i, 10))
    return e


def gen_grotzsch_plus4():
    """Grotzsch (11) + 4 vertices attached triangle-free."""
    base = grotzsch_adj()
    # remap to 0..10 already; add 11,12,13,14
    adj = [set() for _ in range(N)]
    for (u, v) in base:
        adj[u].add(v); adj[v].add(u)
    extra = [11, 12, 13, 14]
    pairs = []
    for x in extra:
        for y in range(N):
            if y != x:
                pairs.append((min(x, y), max(x, y)))
    pairs = list(set(pairs))
    random.shuffle(pairs)
    for (u, v) in pairs:
        if v in adj[u]:
            continue
        if adj[u] & adj[v]:
            continue
        adj[u].add(v); adj[v].add(u)
    return adj


# ---- run --------------------------------------------------------------------

def check(adj, tag, results):
    if has_triangle(adj):
        return
    bG, info = min_5set_drop(adj)
    if info is None:
        return  # trivial band
    mn, arg = info
    results['tested'] += 1
    results['beta_hist'][bG] = results['beta_hist'].get(bG, 0) + 1
    margin = mn - TARGET  # >0 means H2 VIOLATION
    if margin > results['worst_margin']:
        results['worst_margin'] = margin
        results['worst'] = (tag, bG, mn, arg)
    if margin > 0:
        results['violations'].append((tag, bG, mn, arg))


def main():
    results = {'tested': 0, 'beta_hist': {}, 'worst_margin': -99,
               'worst': None, 'violations': []}

    # 1. all C5 blow-up compositions of 15 into 5 positive parts
    for parts in itertools.product(range(1, 12), repeat=5):
        if sum(parts) == 15:
            check(gen_c5_blowup(list(parts)), f"blowup{parts}", results)

    # 2. random maximal triangle-free
    for _ in range(4000):
        check(gen_random_maximal(), "randmax", results)

    # 3. perturbation hill-climb from C5[3] and from random seeds
    base = gen_c5_blowup([3, 3, 3, 3, 3])
    for _ in range(150):
        check(perturb_high_beta(base, steps=250), "perturb_c5", results)
    for _ in range(150):
        check(perturb_high_beta(gen_random_maximal(), steps=250), "perturb_rand", results)

    # 4. non-C5-hom hard cores extended to 15
    for _ in range(800):
        check(gen_petersen_plus5(), "petersen+5", results)
    for _ in range(800):
        check(gen_grotzsch_plus4(), "grotzsch+4", results)
    # hill-climb the hard cores to push beta up while staying tri-free
    for _ in range(120):
        check(perturb_high_beta(gen_petersen_plus5(), steps=250), "pert_pet", results)
    for _ in range(120):
        check(perturb_high_beta(gen_grotzsch_plus4(), steps=250), "pert_grot", results)

    print(f"tested (beta>=6) : {results['tested']}")
    print(f"beta histogram   : {dict(sorted(results['beta_hist'].items()))}")
    print(f"worst margin (min_drop - 5): {results['worst_margin']}  "
          f"(>0 would be an H2 VIOLATION)")
    print(f"worst case       : {results['worst']}")
    print(f"# H2 violations  : {len(results['violations'])}")
    for v in results['violations'][:20]:
        print("  VIOLATION:", v)


if __name__ == "__main__":
    main()
