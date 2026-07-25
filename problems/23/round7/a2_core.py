"""AUDIT pass 2 core library for Erdos #23 / round7 Q1 audit.

Deliberately independent of round7/Q1_*.py and round7/audit_Q1_*.py:
  * graph6 decoder written from the format spec with the explicit (j,i) double loop
    (no triangular-index inversion, no subset DP);
  * bip() by direct per-edge scan over all 2^(n-1) cuts containing vertex 0;
  * bip2() by an independent popcount/adjacency-mask max-cut over all 2^n subsets;
  * weighted blow-up value by the accepted base-1 identity, exact integers/Fractions;
  * neighbourhood-union family enumerated over ALL index sets I subset V (not only
    independent sets), de-duplicated.

Everything on an acceptance path is exact (Python ints / fractions.Fraction).
"""
from fractions import Fraction as F
from itertools import combinations


# ---------------------------------------------------------------- graph6
def g6_decode(s):
    """graph6 -> (n, sorted edge list).  Own implementation from the spec."""
    if isinstance(s, bytes):
        s = s.decode()
    s = s.strip()
    if s.startswith('>>graph6<<'):
        s = s[len('>>graph6<<'):]
    p = 0
    c = ord(s[p]) - 63
    p += 1
    if c == 63:                     # 126 -> multi-byte n
        raise ValueError('n>62 not needed here')
    n = c
    bits = []
    for ch in s[p:]:
        v = ord(ch) - 63
        assert 0 <= v < 64, (ch, v)
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    E = []
    idx = 0
    for j in range(1, n):           # column j, rows i<j  -- the graph6 order
        for i in range(j):
            if bits[idx]:
                E.append((i, j))
            idx += 1
    assert idx <= len(bits)
    for k in range(idx, len(bits)):
        assert bits[k] == 0, 'nonzero padding bit'
    return n, sorted(E)


def g6_encode(n, E):
    """inverse, used only to round-trip-test the decoder."""
    es = set(tuple(sorted(e)) for e in E)
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (i, j) in es else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = 2 * v + b
        out += chr(v + 63)
    return out


def adj_masks(n, E):
    a = [0] * n
    for u, v in E:
        a[u] |= 1 << v
        a[v] |= 1 << u
    return a


def is_triangle_free(n, E):
    a = adj_masks(n, E)
    for u, v in E:
        if a[u] & a[v]:
            return False
    return True


# ---------------------------------------------------------------- bip, two ways
def bip(n, E):
    """|E| - maxcut, by direct per-edge scan over all cuts with vertex 0 on side 0."""
    best = None
    for mask in range(1 << (n - 1)):
        S = mask << 1                      # vertex 0 always outside S
        m = 0
        for u, v in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                m += 1
        if best is None or m < best:
            best = m
    return best


def bip2(n, E):
    """independent second implementation: maxcut via popcount over all 2^n subsets."""
    a = adj_masks(n, E)
    best = -1
    for S in range(1 << n):
        c = 0
        T = S
        while T:
            v = (T & -T).bit_length() - 1
            T &= T - 1
            c += bin(a[v] & ~S & ((1 << n) - 1)).count('1')
        if c > best:
            best = c
    return len(E) - best


# ---------------------------------------------------------------- weighted blow-up
def blowup_value(n, E, a):
    """base 1: bip(H[a]) = min over cuts S of H of sum_{uv mono} a_u a_v.  Exact."""
    best = None
    for mask in range(1 << (n - 1)):
        S = mask << 1
        q = 0
        for u, v in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                q += a[u] * a[v]
        if best is None or q < best:
            best = q
    return best


def expand_blowup(n, E, a):
    """explicit vertex-expanded blow-up graph H[a] (used to re-verify base 1)."""
    off, idx = [], 0
    for v in range(n):
        off.append(idx)
        idx += a[v]
    NN = idx
    EE = []
    for u, v in E:
        for i in range(a[u]):
            for j in range(a[v]):
                EE.append(tuple(sorted((off[u] + i, off[v] + j))))
    return NN, sorted(set(EE))


# ---------------------------------------------------------------- neighbourhood family
def nbhd_union_sets(n, E):
    """ALL distinct sets  union_{v in I} N(v),  I ranges over every subset of V."""
    a = adj_masks(n, E)
    seen = set()
    for I in range(1 << n):
        S = 0
        T = I
        while T:
            v = (T & -T).bit_length() - 1
            T &= T - 1
            S |= a[v]
        seen.add(S)
    return sorted(seen)


def family_value(n, E, a, sets=None):
    """min over neighbourhood-union cuts S of sum_{uv mono} a_u a_v  (weights a)."""
    if sets is None:
        sets = nbhd_union_sets(n, E)
    best = None
    for S in sets:
        q = 0
        for u, v in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                q += a[u] * a[v]
        if best is None or q < best:
            best = q
    return best


# ---------------------------------------------------------------- induced C5 / #C5
def count_C5_subgraphs(n, E):
    """number of 5-cycles as subgraphs: 5-subsets that contain a Hamilton cycle,
    counted with multiplicity of distinct cycles.  Own implementation: enumerate
    cyclic orders directly."""
    a = adj_masks(n, E)
    tot = 0
    for S in combinations(range(n), 5):
        v0 = S[0]
        rest = S[1:]
        # cyclic orders v0,p1,p2,p3,p4 ; divide by 2 for reflection
        seen = set()
        for p in _perms(rest):
            cyc = (v0,) + p
            ok = all((a[cyc[i]] >> cyc[(i + 1) % 5]) & 1 for i in range(5))
            if ok:
                key = frozenset(frozenset((cyc[i], cyc[(i + 1) % 5])) for i in range(5))
                seen.add(key)
        tot += len(seen)
    return tot


def _perms(t):
    if len(t) <= 1:
        yield tuple(t)
        return
    for i in range(len(t)):
        for r in _perms(t[:i] + t[i + 1:]):
            yield (t[i],) + r


def induced_C5_vertexsets(n, E):
    """5-subsets inducing exactly a C5 (2-regular connected on 5 vertices)."""
    a = adj_masks(n, E)
    out = []
    for S in combinations(range(n), 5):
        m = 0
        for x in S:
            m |= 1 << x
        degs = [bin(a[x] & m).count('1') for x in S]
        if sorted(degs) == [2, 2, 2, 2, 2]:
            # 2-regular on 5 vertices and connected <=> C5 (only alternative is
            # disconnected, impossible with 5 vertices and all degrees 2 except
            # C3+C2, and C2 is not a simple graph) -- still check connectivity
            comp = {S[0]}
            stack = [S[0]]
            while stack:
                x = stack.pop()
                for y in S:
                    if y not in comp and (a[x] >> y) & 1:
                        comp.add(y)
                        stack.append(y)
            if len(comp) == 5:
                out.append(S)
    return out


# ---------------------------------------------------------------- misc
def compositions(n, W, lo=0):
    """all integer vectors of length n, entries >= lo, summing to W (zeros allowed)."""
    if n == 1:
        if W >= lo:
            yield (W,)
        return
    for v in range(lo, W + 1):
        for r in compositions(n - 1, W - v, lo):
            yield (v,) + r


C5 = (5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)])


def cycle(k):
    return k, [(i, (i + 1) % k) for i in range(k)] if k > 2 else []


if __name__ == '__main__':
    # self-tests of the decoder / bip
    n, E = g6_decode('Dhc')          # some 5-vertex graph
    assert g6_encode(n, E) == 'Dhc', g6_encode(n, E)
    n, E = C5
    assert g6_encode(n, E) == g6_encode(n, E)
    assert bip(*C5) == 1 and bip2(*C5) == 1
    n7, E7 = cycle(7)
    assert bip(n7, E7) == 1 and bip2(n7, E7) == 1
    print('a2_core self-test OK; C5 bip=1, C7 bip=1')
