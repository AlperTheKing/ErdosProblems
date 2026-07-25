"""Independent audit library for Erdos #23 family F2 report.
Written from scratch; NO import of the author's switch_lib / witness_verify.
All arithmetic exact integer.
"""
from itertools import combinations, product


def sigma_set(S, E, side):
    """sigma(S) computed DIRECTLY from the edge list and the side vector.
    sigma(S) = (# B-edges with exactly one end in S) - (# M-edges with exactly one end in S).
    Equivalently: cut(before) - cut(after switching S).
    """
    s = 0
    for (u, v) in E:
        inu = u in S
        inv = v in S
        if inu != inv:                       # boundary edge
            s += 1 if side[u] != side[v] else -1
    return s


def cutsize(E, side):
    return sum(1 for (u, v) in E if side[u] != side[v])


def sigma_by_recut(S, E, side):
    """Cross-check of sigma_set via literally recomputing the cut after switching."""
    ns = list(side)
    for v in S:
        ns[v] ^= 1
    return cutsize(E, side) - cutsize(E, ns)


def blowup(h_edges, sizes):
    """Blow-up of a pattern; returns (N, E, part_of, start)."""
    start, tot = [], 0
    for s in sizes:
        start.append(tot)
        tot += s
    part_of = []
    for i, s in enumerate(sizes):
        part_of += [i] * s
    E = []
    for (a, b) in h_edges:
        for x in range(start[a], start[a] + sizes[a]):
            for y in range(start[b], start[b] + sizes[b]):
                E.append((min(x, y), max(x, y)))
    return tot, E, part_of, start


def adj_of(N, E):
    adj = [set() for _ in range(N)]
    for (u, v) in E:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def is_triangle_free(N, E):
    adj = adj_of(N, E)
    for (u, v) in E:
        if adj[u] & adj[v]:
            return False
    return True


def maxcut_brute(N, E):
    best = -1
    arg = []
    for mask in range(1 << (N - 1)):
        side = [0] + [(mask >> i) & 1 for i in range(N - 1)]
        c = cutsize(E, side)
        if c > best:
            best, arg = c, [side]
        elif c == best:
            arg.append(side)
    return best, arg


def named_families(N, E, side):
    """Yield (name, frozenset S) for the classical local families, computed ON THE GRAPH."""
    adj = adj_of(N, E)
    for v in range(N):
        yield ("vertex", frozenset([v]))
        NB = [a for a in adj[v] if side[a] != side[v]]
        yield ("star {v}uN_B(v)", frozenset([v]) | frozenset(NB))
        yield ("N(v)", frozenset(adj[v]))
        yield ("N[v]", frozenset(adj[v]) | frozenset([v]))
        ball = set([v]) | set(adj[v])
        for a in list(adj[v]):
            ball |= adj[a]
        yield ("B(v,2)", frozenset(ball))
    for (u, v) in E:
        yield ("N[u]uN[v]", frozenset(adj[u]) | frozenset(adj[v]) | frozenset([u, v]))


def sharp_stars(N, E, side, cap=None):
    """All sets {v} u A with A subset N_B(v).  cap limits |N_B(v)| to avoid blow-up."""
    adj = adj_of(N, E)
    for v in range(N):
        NB = sorted(a for a in adj[v] if side[a] != side[v])
        if cap is not None and len(NB) > cap:
            continue
        for r in range(len(NB) + 1):
            for A in combinations(NB, r):
                yield ("sharp star", frozenset([v]) | frozenset(A))


def independent_sets(N, E):
    """All independent sets (exponential; small graphs only)."""
    adj = adj_of(N, E)
    res = []

    def rec(i, cur):
        if i == N:
            res.append(frozenset(cur))
            return
        rec(i + 1, cur)
        if not (adj[i] & cur):
            cur.add(i)
            rec(i + 1, cur)
            cur.discard(i)
    rec(0, set())
    return res
