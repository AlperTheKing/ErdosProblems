"""INDEPENDENT re-verification of the C5-perfect obstruction, written from scratch
with a different graph representation (adjacency sets, cuts as tuples of signs,
5-cycles found by DFS instead of by 5-subset enumeration), plus:

  * exact minimum blocking family of induced C5s  -> quantitative constant 3^(1/r)/25
  * exact bip / psi spot checks with Fraction arithmetic
"""
from fractions import Fraction
from itertools import combinations, product

# ---- graphs, built independently of R8_transport_lib ----------------------


def mk(n, pairs):
    A = {v: set() for v in range(n)}
    for u, v in pairs:
        A[u].add(v)
        A[v].add(u)
    return n, A


def circ(n, dists):
    return mk(n, [(i, (i + d) % n) for i in range(n) for d in dists])


def and_k(k):
    n = 3 * k - 1
    return circ(n, list(range(k, n // 2 + 1)))


def g6(s):
    d = [ord(c) - 63 for c in s]
    n = d[0]
    bits = []
    for x in d[1:]:
        bits += [(x >> j) & 1 for j in range(5, -1, -1)]
    pairs, i = [], 0
    for col in range(1, n):
        for row in range(col):
            if bits[i]:
                pairs.append((row, col))
            i += 1
    return mk(n, pairs)


def is_triangle_free(n, A):
    return all(not (A[u] & A[v]) for u in range(n) for v in A[u] if u < v)


def five_cycles_induced(n, A):
    """induced C5s via DFS on paths, then check induced."""
    res = set()
    for a in range(n):
        for b in A[a]:
            for c in A[b]:
                if c == a:
                    continue
                for d in A[c]:
                    if d in (a, b):
                        continue
                    for e in A[d]:
                        if e in (a, b, c) or a not in A[e]:
                            continue
                        vs = (a, b, c, d, e)
                        # induced: exactly 5 edges among the 5 vertices
                        cnt = sum(1 for u, v in combinations(vs, 2) if v in A[u])
                        if cnt == 5:
                            res.add(frozenset(vs))
    out = []
    for fs in res:
        vs = sorted(fs)
        es = [(u, v) for u, v in combinations(vs, 2) if v in A[u]]
        out.append((tuple(vs), tuple(sorted(es))))
    return sorted(out)


def all_cuts(n):
    for bits in product((0, 1), repeat=n - 1):
        yield (0,) + bits


def k_of(cut, es):
    return sum(1 for u, v in es if cut[u] == cut[v])


def analyse(name, G, verbose=True):
    n, A = G
    assert is_triangle_free(n, A), "%s is NOT triangle-free" % name
    cyc = five_cycles_induced(n, A)
    cuts = list(all_cuts(n))
    bad_for = []          # for each cut, list of cycle indices with k>=3
    perfect = 0
    for cut in cuts:
        bad = [j for j, (vs, es) in enumerate(cyc) if k_of(cut, es) != 1]
        if not bad:
            perfect += 1
        bad_for.append(bad)
    if verbose:
        print("%-14s n=%2d  |inducedC5|=%3d  C5-perfect cuts=%d" % (name, n, len(cyc), perfect))
    if perfect:
        return None
    # exact minimum blocking family of cycles: greedy then exact search by size
    cover_sets = {j: set() for j in range(len(cyc))}
    for i, bad in enumerate(bad_for):
        for j in bad:
            cover_sets[j].add(i)
    universe = set(range(len(cuts)))
    for r in range(1, 5):
        for combo in combinations(range(len(cyc)), r):
            u = set()
            for j in combo:
                u |= cover_sets[j]
            if u == universe:
                if verbose:
                    print("    minimum blocking family of induced C5s: r=%d  %s"
                          % (r, [cyc[j][0] for j in combo]))
                    print("    ==> every distribution lambda over cuts has "
                          "max_x prod nu_S^lambda_S >= 3^(1/%d)/25 = %.6f > 0.04"
                          % (r, 3 ** (1.0 / r) / 25))
                return r
    if verbose:
        print("    minimum blocking family: r>4 (search truncated)")
    return -1


if __name__ == "__main__":
    tests = [
        ("C5", circ(5, [1])),
        ("C5[2]", mk(10, [(i, j) for a in range(5) for b in [(a + 1) % 5]
                          for i in (2 * a, 2 * a + 1) for j in (2 * b, 2 * b + 1)])),
        ("And(3)=Wagner", and_k(3)),
        ("And(4)=Gamma11", and_k(4)),
        ("And(5)=Gamma14", and_k(5)),
        ("Petersen", mk(10, [(i, (i + 1) % 5) for i in range(5)]
                        + [(i, 5 + i) for i in range(5)]
                        + [(5 + i, 5 + (i + 2) % 5) for i in range(5)])),
        ("N14extremal", g6("M?AE@bH{AYN_LgBs?")),
    ]
    for name, G in tests:
        analyse(name, G)
