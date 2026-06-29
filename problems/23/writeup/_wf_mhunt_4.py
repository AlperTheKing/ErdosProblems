"""Family #4 adversarial hunt for a counterexample to LEMMA (M).
Dense random triangle-free graphs N=14..24 (random edge insertion rejecting triangles), many seeds.
For each graph: get EXACT global-max cuts via maxcut_all (N<=22 feasible). For each connected-B
global-max cut, scan all unique-geodesic bad edges f, find P-contained chords, test interior-overlap.

A counterexample = a triangle-free graph + a VERIFIED GLOBAL MAX cut (size==true max) that is
connected-B and has a P-contained interior-overlap. Non-max (locally-max-but-+1-exists) overlaps =
near-misses, reported but do NOT count.

EXACT Fraction arithmetic only (maxcut_all is integer-exact brute force).
"""
import random
from fractions import Fraction as F
from _h import dec, maxcut_all, Bconn, geos
from _satzmu_conn import struct_for_side


def make_random_trifree(n, seed, density_target=1.0):
    """Random triangle-free graph: shuffle all non-edges, insert if no triangle created.
    density_target=1.0 => maximal (add as many as possible)."""
    rng = random.Random(seed)
    adj = [set() for _ in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rng.shuffle(pairs)
    nmax = int(density_target * len(pairs))
    added = 0
    for (i, j) in pairs:
        if added >= nmax:
            break
        # adding i-j creates a triangle iff adj[i] & adj[j] nonempty
        if adj[i] & adj[j]:
            continue
        adj[i].add(j); adj[j].add(i)
        added += 1
    return adj


def edges_of(adj):
    n = len(adj)
    return [(u, v) for u in range(n) for v in adj[u] if v > u]


def maxcut_all_fast(n, adj):
    """EXACT all global-max cuts via bitmask brute force (integer-exact).
    side stored as bitmask; vertex 0 fixed to side 0 (halves the search).
    For each vertex u, popcount of (neighbors_above_mask & opposite-side) summed = cut size.
    """
    # neighbor bitmask per vertex restricted to higher-index neighbors (each edge counted once)
    nbr_hi = [0] * n
    for u in range(n):
        for v in adj[u]:
            if v > u:
                nbr_hi[u] |= (1 << v)
    best = -1
    cuts = []
    pc = int.bit_count if hasattr(int, "bit_count") else (lambda x: bin(x).count("1"))
    for m in range(1 << (n - 1)):  # vertex 0 = side 0
        # side bitmask: bit u set => side 1
        side_mask = m << 1  # bits 1..n-1 from m; bit 0 = 0
        c = 0
        for u in range(n):
            if nbr_hi[u]:
                hi = nbr_hi[u]
                if (side_mask >> u) & 1:
                    # u on side1 -> count higher neighbors on side0
                    c += pc(hi & ~side_mask)
                else:
                    c += pc(hi & side_mask)
        if c > best:
            best = c
            cuts = [m]
        elif c == best:
            cuts.append(m)
    # convert masks to side lists
    out = []
    for m in cuts:
        side_mask = m << 1
        out.append([(side_mask >> u) & 1 for u in range(n)])
    return out, best


def tri_free(adj):
    n = len(adj)
    for u in range(n):
        for v in adj[u]:
            if v > u and (adj[u] & adj[v]):
                return False
    return True


def find_overlap_on_cut(n, adj, side):
    """Return list of (f, P_f, (a1,b1), (a2,b2)) P-contained interior-overlaps on this cut.
    Only considers unique-geodesic bad edges f."""
    if not Bconn(n, adj, side):
        return None  # not connected-B
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, ell, T, mu, cyc = st
    results = []
    for f in M:
        if len(cyc[f]) != 1:
            continue  # f must be unique-geodesic
        P_f = cyc[f][0]
        L = len(P_f)
        pos = {x: i for i, x in enumerate(P_f)}
        Pset = set(P_f)
        chords = []
        for g in M:
            if g == f:
                continue
            for Q in cyc[g]:
                if set(Q) <= Pset:
                    pp = sorted(pos[v] for v in Q)
                    if pp[-1] - pp[0] == len(pp) - 1:  # contiguous subpath
                        chords.append((pp[0], pp[-1], g))
                        break
        for i in range(len(chords)):
            for j in range(i + 1, len(chords)):
                a1, b1, gi = chords[i]
                a2, b2, gj = chords[j]
                if a1 > a2:
                    a1, b1, a2, b2 = a2, b2, a1, b1
                r = min(b1, b2)
                if a2 < r:  # interior-overlap (share more than one position)
                    results.append((f, P_f, (a1, b1), (a2, b2)))
    return results


def to_g6_edgelist(adj):
    return edges_of(adj)


def run():
    counterexamples = []
    near_misses = 0
    near_miss_sample = []
    graphs_scanned = 0
    cuts_scanned = 0
    connB_max_cuts = 0

    # N range capped at 20 for maxcut_all feasibility (2^(n-1) pure-Python brute force;
    # n=20 -> 2^19=512K side-vectors/graph, n=22 -> 2.1M is too slow for many seeds).
    # densities: maximal (1.0) and partial fills to vary structure.
    configs = []
    for n in range(14, 21):
        for dens in (1.0, 0.85, 0.7):
            for seed in range(30):
                configs.append((n, seed, dens))

    print(f"Total configs: {len(configs)}", flush=True)

    for idx, (n, seed, dens) in enumerate(configs):
        adj = make_random_trifree(n, seed * 1000 + int(dens * 100) + n, dens)
        if not tri_free(adj):
            continue  # safety
        E = edges_of(adj)
        if len(E) < n:
            continue  # too sparse, skip
        graphs_scanned += 1
        cuts, truemax = maxcut_all_fast(n, adj)  # EXACT all global-max cuts
        for side in cuts:
            cuts_scanned += 1
            # verify this is genuinely global max (maxcut_all guarantees, but double-check exact)
            csize = sum(1 for u, v in E if side[u] != side[v])
            assert csize == truemax, "maxcut_all invariant broken"
            if not Bconn(n, adj, side):
                continue
            connB_max_cuts += 1
            ov = find_overlap_on_cut(n, adj, side)
            if ov:
                # THIS IS A GLOBAL-MAX connected-B cut WITH a P-contained interior-overlap
                counterexamples.append((n, seed, dens, E, side[:], ov[0]))
                print(f"  *** COUNTEREXAMPLE n={n} seed={seed} dens={dens} truemax={truemax}", flush=True)
                print(f"      side={side}", flush=True)
                print(f"      overlap={ov[0]}", flush=True)

        if (idx + 1) % 30 == 0:
            print(f"  ...{idx+1}/{len(configs)} scanned (n={n}); graphs={graphs_scanned} "
                  f"connB-max-cuts={connB_max_cuts} CE={len(counterexamples)}", flush=True)

    # Now separately quantify near-misses: overlaps on LOCALLY-max-but-not-global cuts.
    # We re-scan a sample: for each graph, look at all connected-B cuts (any size), find overlaps,
    # and check if they were on a non-global-max cut.
    print("\n--- Near-miss scan (overlaps on non-global-max connected-B cuts) ---", flush=True)
    nm_graphs = 0
    for (n, seed, dens) in configs:
        if n > 18:
            continue  # cap full 2^(n-1) overlap scan at n<=18 for tractability
        adj = make_random_trifree(n, seed * 1000 + int(dens * 100) + n, dens)
        if not tri_free(adj):
            continue
        E = edges_of(adj)
        if len(E) < n:
            continue
        nm_graphs += 1
        _cuts, truemax = maxcut_all_fast(n, adj)
        # scan ALL cuts (not just max) for overlaps on connected-B cuts
        for m in range(1 << (n - 1)):
            side = [(m >> u) & 1 for u in range(n)]
            csize = sum(1 for u, v in E if side[u] != side[v])
            if csize == truemax:
                continue  # already handled as global-max above
            if not Bconn(n, adj, side):
                continue
            ov = find_overlap_on_cut(n, adj, side)
            if ov:
                near_misses += 1
                if len(near_miss_sample) < 5:
                    near_miss_sample.append((n, seed, dens, csize, truemax, ov[0]))
        if nm_graphs >= 30:
            break  # near-miss scan is expensive (full 2^(n-1)); sample is enough

    print(f"\n=== SUMMARY ===", flush=True)
    print(f"graphs_scanned={graphs_scanned} cuts_scanned={cuts_scanned} "
          f"connB_max_cuts={connB_max_cuts}", flush=True)
    print(f"GLOBAL-MAX COUNTEREXAMPLES = {len(counterexamples)}", flush=True)
    print(f"near_misses (overlap on non-global-max connected-B cut) = {near_misses}", flush=True)
    for nm in near_miss_sample:
        print(f"  near-miss: {nm}", flush=True)
    if counterexamples:
        ce = counterexamples[0]
        print(f"\nFIRST COUNTEREXAMPLE:", flush=True)
        print(f"  n={ce[0]} seed={ce[1]} dens={ce[2]}", flush=True)
        print(f"  edges={ce[3]}", flush=True)
        print(f"  side={ce[4]}", flush=True)
        print(f"  overlap f/P/intervals={ce[5]}", flush=True)
    return counterexamples, near_misses


if __name__ == "__main__":
    run()
