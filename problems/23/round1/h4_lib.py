"""H4 shared exact primitives: graph6 I/O, exhaustive maxcut, bip, triangle-free, maximality.

Everything here is integer-exact.  No floating point on any acceptance path.
"""

from itertools import combinations


# ---------------------------------------------------------------- graph6 -----

def g6_encode(n, adj):
    """adj = list of n bitmasks.  Returns graph6 string (n < 63)."""
    assert n < 63
    out = chr(n + 63)
    cur = nb = 0
    for j in range(1, n):
        for i in range(j):
            cur = (cur << 1) | ((adj[i] >> j) & 1)
            nb += 1
            if nb == 6:
                out += chr(cur + 63)
                cur = nb = 0
    if nb:
        out += chr((cur << (6 - nb)) + 63)
    return out


def g6_decode(s):
    """Returns (n, adj) with adj a list of bitmasks."""
    s = s.strip()
    assert s and s[0] != '>', s
    n = ord(s[0]) - 63
    assert 0 <= n < 63, "only n<63 supported here"
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    adj = [0] * n
    p = 0
    for j in range(1, n):
        for i in range(j):
            if bits[p]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            p += 1
    return n, adj


# ------------------------------------------------------------ graph facts ----

def edges_of(n, adj):
    return [(i, j) for i in range(n) for j in range(i + 1, n) if (adj[i] >> j) & 1]


def num_edges(n, adj):
    return sum(bin(a).count("1") for a in adj) // 2


def is_triangle_free(n, adj):
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1:
                if adj[i] & adj[j]:
                    return False
    return True


def is_maximal_triangle_free(n, adj):
    """triangle-free and no non-edge can be added (== every non-adjacent pair
    has a common neighbour)."""
    if not is_triangle_free(n, adj):
        return False
    for i in range(n):
        for j in range(i + 1, n):
            if not ((adj[i] >> j) & 1):
                if not (adj[i] & adj[j]):
                    return False
    return True


def is_bipartite(n, adj):
    color = [-1] * n
    for s in range(n):
        if color[s] >= 0:
            continue
        color[s] = 0
        stack = [s]
        while stack:
            v = stack.pop()
            a = adj[v]
            while a:
                b = a & -a
                u = b.bit_length() - 1
                a ^= b
                if color[u] < 0:
                    color[u] = color[v] ^ 1
                    stack.append(u)
                elif color[u] == color[v]:
                    return False
    return True


# ----------------------------------------------------------------- maxcut ----

def maxcut_exact(n, adj):
    """Exhaustive maximum cut over all 2^(n-1) bipartitions, Gray-code walk.
    Returns (maxcut_value, best_side_mask).  Vertex 0 is always outside S."""
    deg = [bin(a).count("1") for a in adj]
    S = 1
    cut = deg[0]
    best, best_S = cut, S
    for k in range(1, 1 << (n - 1)):
        v = (k & -k).bit_length()          # 1..n-1
        a = bin(adj[v] & S).count("1")
        if (S >> v) & 1:
            cut += 2 * a - deg[v]
            S &= ~(1 << v)
        else:
            cut += deg[v] - 2 * a
            S |= 1 << v
        if cut > best:
            best, best_S = cut, S
    return best, best_S


def min_mono_exact(n, adj):
    """min over all bipartitions of #monochromatic edges = bip(G).
    Returns (bip, argmin_mask)."""
    m = num_edges(n, adj)
    mc, mask = maxcut_exact(n, adj)
    return m - mc, mask


def bip(n, adj):
    return num_edges(n, adj) - maxcut_exact(n, adj)[0]


# ------------------------------------------------------------- cut helpers ---

def mono_pairs(n, mask, pairs):
    """indices into `pairs` of the pairs monochromatic under bitmask `mask`."""
    return [k for k, (u, v) in enumerate(pairs)
            if ((mask >> u) & 1) == ((mask >> v) & 1)]


def all_cut_masks(n):
    """one representative per bipartition: vertex 0 always on side 0."""
    return range(1 << (n - 1))


# ------------------------------------------------------------- self-check ----

if __name__ == "__main__":
    # C5 : bip 1
    n = 5
    adj = [0] * 5
    for i in range(5):
        j = (i + 1) % 5
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    assert is_triangle_free(n, adj) and not is_bipartite(n, adj)
    assert bip(n, adj) == 1, bip(n, adj)
    g6 = g6_encode(n, adj)
    n2, adj2 = g6_decode(g6)
    assert (n2, adj2) == (n, adj)
    print("C5 ok  g6 =", g6)

    # C5[2] : bip 4
    def blowup(parts):
        n = sum(parts)
        off = []
        s = 0
        for p in parts:
            off.append(s)
            s += p
        adj = [0] * n
        for i in range(5):
            j = (i + 1) % 5
            for a in range(off[i], off[i] + parts[i]):
                for b in range(off[j], off[j] + parts[j]):
                    adj[a] |= 1 << b
                    adj[b] |= 1 << a
        return n, adj

    for k in (1, 2, 3):
        n, adj = blowup([k] * 5)
        assert is_triangle_free(n, adj)
        assert bip(n, adj) == k * k, (k, bip(n, adj))
    print("C5[k] k=1,2,3 ok")

    # known extremal graphs from the round-1 census
    for g6s, expect in (("K?ABBBwerwBw", 5), ("L??ED@_~?~^_Fw", 6),
                        ("M?AE@bH{AYN_LgBs?", 7)):
        n, adj = g6_decode(g6s)
        assert is_triangle_free(n, adj)
        assert bip(n, adj) == expect, (g6s, bip(n, adj))
    print("census extremals ok")
