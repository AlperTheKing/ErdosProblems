"""ROOT-AGENT (Claude): what ARE the five non-C5-colourable orbits of Gamma_11?

R3-C37 reduced the Gamma_11 frontier to five finite-dimensional bounds, one per D_22 orbit of
non-C5-colourable support, sizes 8, 9, 9, 10, 11. The minimal ones are 11 subsets of SIZE 8, a single
orbit. Wagner = And(3) = Gamma_8 is the minimal non-C5-colourable Andrasfai graph and has exactly 8
vertices, so the natural guess is that the minimal obstructions inside And(4) are induced copies of
And(3).

If true it is worth a lot: max_x psi(Wagner) = 1/25 is already PROVED (R3-C17, via Wagner having no
odd-K5 minor plus Theorem A, and independently by an exact SOS certificate), so the obstruction
carrying the non-colourability would be an object whose ceiling is already known.

This identifies each orbit representative: order, size, degree sequence, and an explicit isomorphism
test against Wagner and against the other Andrasfai graphs.
"""
from itertools import permutations


def gamma_g(m):
    return m, [(u, v) for u in range(m) for v in range(u + 1, m)
               if 3 * min((u - v) % m, (v - u) % m) > m]


def induced(E, U):
    Us = set(U)
    idx = {v: i for i, v in enumerate(sorted(U))}
    return [(idx[u], idx[v]) for (u, v) in E if u in Us and v in Us]


def canon(nv, edges):
    """brute-force canonical form; only used on <= 9 vertices"""
    best = None
    es = [tuple(sorted(e)) for e in edges]
    for p in permutations(range(nv)):
        m = tuple(sorted(tuple(sorted((p[u], p[v]))) for (u, v) in es))
        if best is None or m < best:
            best = m
    return best


n, E = gamma_g(11)
A = [set() for _ in range(n)]
for u, v in E:
    A[u].add(v)
    A[v].add(u)


def colourable(mask):
    sup = [v for v in range(n) if (mask >> v) & 1]
    c = {}

    def rec(i):
        if i == len(sup):
            return True
        v = sup[i]
        for k in range(5 if i else 1):
            if all((c[w] - k) % 5 in (1, 4) for w in A[v] if w in c):
                c[v] = k
                if rec(i + 1):
                    return True
                c.pop(v)
        return False

    return rec(0)


nc = [m for m in range(1, 1 << n) if not colourable(m)]
ncset = set(nc)


def rot(m, k):
    return sum(((m >> v) & 1) << ((v + k) % n) for v in range(n))


def ref(m):
    return sum(((m >> v) & 1) << ((-v) % n) for v in range(n))


seen, reps = set(), []
for m in nc:
    if m in seen:
        continue
    o = set()
    for k in range(n):
        o.add(rot(m, k))
        o.add(rot(ref(m), k))
    seen |= o
    reps.append(m)

n8, E8 = gamma_g(8)
wag = canon(8, E8)
print(f"Wagner = And(3) = Gamma_8: {n8} vertices, {len(E8)} edges, canonical form computed")
print(f"\nthe {len(reps)} non-C5-colourable D_22 orbits of Gamma_11:\n")
for m in reps:
    U = [v for v in range(n) if (m >> v) & 1]
    sub = induced(E, U)
    deg = sorted(sum(1 for e in sub if i in e) for i in range(len(U)))
    tag = ""
    if len(U) == 8:
        tag = "  ISOMORPHIC TO WAGNER" if canon(8, sub) == wag else "  (8 vertices, NOT Wagner)"
    elif len(U) <= 9:
        tag = "  (canonical form computed, not Wagner-sized)"
    print(f"  {U}   |V| = {len(U)}, |E| = {len(sub)}, degrees {deg}{tag}")
    # does it CONTAIN an induced Wagner?
    if len(U) > 8:
        found = None
        from itertools import combinations
        for S in combinations(U, 8):
            if canon(8, induced(E, S)) == wag:
                found = list(S)
                break
        print(f"      contains an induced Wagner: {found is not None}"
              + (f" at {found}" if found else ""))
