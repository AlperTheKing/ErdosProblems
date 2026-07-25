"""audit_f8_lib.py -- INDEPENDENT re-implementation (adversarial audit of f8.md).
Nothing here imports f8_core; graph6 decoding, triangle-freeness, maximality,
twin-freeness, exact bip, canonical form and psi are all written from scratch.
"""
from fractions import Fraction
from itertools import permutations, combinations


# ---------------------------------------------------------------- graph6 I/O
def g6dec(s):
    s = s.strip()
    if not s or s[0] == '>':
        return None
    d = [ord(c) - 63 for c in s]
    if d[0] == 63:
        n = (d[1] << 12) | (d[2] << 6) | d[3]
        rest = d[4:]
    else:
        n = d[0]
        rest = d[1:]
    bits = []
    for b in rest:
        bits += [(b >> k) & 1 for k in (5, 4, 3, 2, 1, 0)]
    adj = [0] * n
    t = 0
    for j in range(1, n):
        for i in range(j):
            if bits[t]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            t += 1
    return n, adj


def g6enc(n, adj):
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append((adj[i] >> j) & 1)
    while len(bits) % 6:
        bits.append(0)
    if n <= 62:
        out = [chr(n + 63)]
    else:
        out = [chr(126), chr(((n >> 12) & 63) + 63), chr(((n >> 6) & 63) + 63), chr((n & 63) + 63)]
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = v * 2 + b
        out.append(chr(v + 63))
    return ''.join(out)


def edges(n, adj):
    return [(i, j) for j in range(n) for i in range(j) if (adj[i] >> j) & 1]


def trifree(n, adj):
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1 and (adj[i] & adj[j]):
                return False
    return True


def maximal_tf(n, adj):
    """every non-adjacent pair has a common neighbour"""
    for i in range(n):
        for j in range(i + 1, n):
            if not (adj[i] >> j) & 1 and not (adj[i] & adj[j]):
                return False
    return True


def twinfree(n, adj):
    return len(set(adj)) == n


def connected(n, adj):
    seen, st = 1, [0]
    while st:
        v = st.pop()
        w = adj[v] & ~seen
        while w:
            b = w & -w
            seen |= b
            st.append(b.bit_length() - 1)
            w ^= b
    return seen == (1 << n) - 1


def mindeg(n, adj):
    return min(bin(a).count('1') for a in adj)


# ---------------------------------------------------------------- exact bip
def _same_matrix(n, adj):
    """boolean array (2^(n-1), m): entry [s,k] = edge k monochromatic under cut s"""
    import numpy as np
    E = edges(n, adj)
    side = np.arange(1 << (n - 1), dtype=np.int64) << 1     # vertex 0 always side 0
    M = np.empty((1 << (n - 1), len(E)), dtype=bool)
    for k, (i, j) in enumerate(E):
        M[:, k] = (((side >> i) ^ (side >> j)) & 1) == 0
    return E, M


def bip_exact(n, adj):
    """|E| - maxcut, exact, by enumerating all 2^(n-1) bipartitions (vertex 0 fixed)."""
    E, M = _same_matrix(n, adj)
    return int(M.sum(1).min()), len(E)


def mono_masks(n, adj):
    """(edge list, list of inclusion-minimal monochromatic edge-sets as bitmasks)"""
    import numpy as np
    E, M = _same_matrix(n, adj)
    m = len(E)
    assert m <= 63
    w = (np.uint64(1) << np.arange(m, dtype=np.uint64))
    masks = (M.astype(np.uint64) * w).sum(1, dtype=np.uint64)
    masks = np.unique(masks)
    pc = np.array([bin(int(x)).count('1') for x in masks])
    masks = masks[np.argsort(pc, kind='stable')]
    acc = np.zeros(0, dtype=np.uint64)
    minimal = []
    for x in masks:
        if acc.size and np.any((acc & x) == acc):
            continue
        minimal.append(int(x))
        acc = np.append(acc, x)
    return E, minimal


def psi_int(E, minimal, a):
    """min over minimal mono sets of sum a_i a_j  (a integers or Fractions)"""
    best = None
    for msk in minimal:
        s = 0
        mm = msk
        while mm:
            k = (mm & -mm).bit_length() - 1
            i, j = E[k]
            s += a[i] * a[j]
            mm &= mm - 1
            if best is not None and s >= best:
                break
        else:
            if best is None or s < best:
                best = s
    return best


def psi_int_np(pairs, offs, a):
    """vectorised: pairs = (I,J) index arrays over all minimal sets concatenated,
    offs = boundaries.  Returns min_F sum_{ij in F} a_i a_j."""
    import numpy as np
    av = np.asarray(a, dtype=np.int64)
    prod = av[pairs[0]] * av[pairs[1]]
    cs = np.concatenate([[np.int64(0)], np.cumsum(prod)])
    return int((cs[offs[1:]] - cs[offs[:-1]]).min())


def ragged(E, minimal):
    import numpy as np
    I, J, offs = [], [], [0]
    for msk in minimal:
        mm = msk
        while mm:
            k = (mm & -mm).bit_length() - 1
            i, j = E[k]
            I.append(i)
            J.append(j)
            mm &= mm - 1
        offs.append(len(I))
    return (np.array(I), np.array(J)), np.array(offs)


# ---------------------------------------------------------------- canonical form
def _refine(n, adj, col):
    while True:
        sig = [(col[v], tuple(sorted(col[u] for u in range(n) if (adj[v] >> u) & 1)))
               for v in range(n)]
        rank = {s: i for i, s in enumerate(sorted(set(sig)))}
        new = [rank[s] for s in sig]
        if new == col:
            return col
        col = new


def canon(n, adj):
    """Canonical form by individualization-refinement: min over all leaves of the
    IR tree of the upper-triangle adjacency code.  Target-cell choice (first
    smallest non-singleton cell in colour order) is isomorphism-invariant, so the
    minimum over leaves is a genuine canonical invariant."""
    best = [None]
    leaves = [0]

    def rec(col):
        col = _refine(n, adj, col)
        cells = {}
        for v in range(n):
            cells.setdefault(col[v], []).append(v)
        big = [c for c in sorted(cells) if len(cells[c]) > 1]
        if not big:
            perm = [None] * n
            for v in range(n):
                perm[col[v]] = v
            code = []
            for j in range(n):
                for i in range(j):
                    code.append((adj[perm[i]] >> perm[j]) & 1)
            code = tuple(code)
            leaves[0] += 1
            if best[0] is None or code < best[0]:
                best[0] = code
            return
        sz = min(len(cells[c]) for c in big)
        tgt = next(c for c in big if len(cells[c]) == sz)
        for v in cells[tgt]:
            nc = [x + 1 if x >= col[v] else x for x in col]
            nc[v] = col[v]
            rec(nc)
            if leaves[0] > 400000:
                raise RuntimeError("canon: IR tree too large")

    rec([0] * n)
    return best[0]


def canon_str(n, adj):
    c = canon(n, adj)
    a2 = [0] * n
    t = 0
    for j in range(n):
        for i in range(j):
            if c[t]:
                a2[i] |= 1 << j
                a2[j] |= 1 << i
            t += 1
    return g6enc(n, a2)


# ---------------------------------------------------------------- misc builders
def mk(n, E):
    adj = [0] * n
    for (i, j) in E:
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    return n, adj


def cayleyZ(n, S):
    S = set(x % n for x in S) | set((-x) % n for x in S)
    S.discard(0)
    return mk(n, [(i, j) for i in range(n) for j in range(i + 1, n) if (j - i) % n in S])


def blowup(n, adj, sizes):
    st, s = [0] * n, 0
    for i in range(n):
        st[i] = s
        s += sizes[i]
    E = []
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1:
                for x in range(sizes[i]):
                    for y in range(sizes[j]):
                        E.append((st[i] + x, st[j] + y))
    return mk(s, E)


def hom_exists(n1, a1, n2, a2):
    """does a homomorphism G1 -> G2 exist? (backtracking, fine for n1<=20, n2<=6)"""
    order = sorted(range(n1), key=lambda v: -bin(a1[v]).count('1'))
    pos = {v: k for k, v in enumerate(order)}
    asg = [-1] * n1

    def bt(k):
        if k == n1:
            return True
        v = order[k]
        for c in range(n2):
            ok = True
            for u in range(n1):
                if asg[u] >= 0 and (a1[v] >> u) & 1 and not (a2[c] >> asg[u]) & 1:
                    ok = False
                    break
            if ok:
                asg[v] = c
                if bt(k + 1):
                    return True
                asg[v] = -1
        return False
    return bt(0)
