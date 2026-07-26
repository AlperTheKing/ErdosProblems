"""
R9 / Erdos #23 -- shared exact library for the DISCHARGING-WITH-A-GLOBAL-POTENTIAL round.

Everything decisive is exact: integers or fractions.Fraction.  Floats appear only in
printed diagnostics, never in an acceptance test.

Graph representation: n = number of vertices, adj = list of int bitmasks.
"""
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
import sys

# ----------------------------------------------------------------------------- graph6

def g6_decode(s):
    """graph6 string -> (n, adj-bitmask-list). Handles n <= 62 (single-byte header)."""
    data = [ord(c) - 63 for c in s.strip()]
    n = data[0]
    assert n <= 62, "only small graph6 supported"
    bits = []
    for x in data[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    adj = [0] * n
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            idx += 1
    return n, adj


def edges(n, adj):
    return [(i, j) for i in range(n) for j in range(i + 1, n) if (adj[i] >> j) & 1]


def num_edges(n, adj):
    return sum(bin(a).count("1") for a in adj) // 2


def degrees(n, adj):
    return [bin(a).count("1") for a in adj]


def is_triangle_free(n, adj):
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1 and (adj[i] & adj[j]):
                return False
    return True


def induced(n, adj, keepmask):
    """Induced subgraph on the vertices of keepmask; returns (m, adj2, vertex list)."""
    verts = [v for v in range(n) if (keepmask >> v) & 1]
    idx = {v: k for k, v in enumerate(verts)}
    m = len(verts)
    adj2 = [0] * m
    for v in verts:
        a = adj[v] & keepmask
        b = 0
        while a:
            low = a & -a
            u = low.bit_length() - 1
            b |= 1 << idx[u]
            a ^= low
        adj2[idx[v]] = b
    return m, adj2, verts


# ----------------------------------------------------------------------------- graphs

def make_cycle(n):
    adj = [0] * n
    for i in range(n):
        j = (i + 1) % n
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    return n, adj


def make_complete_bipartite(a, b):
    n = a + b
    adj = [0] * n
    for i in range(a):
        for j in range(a, n):
            adj[i] |= 1 << j
            adj[j] |= 1 << i
    return n, adj


def make_blowup(base_n, base_adj, sizes):
    """Blow-up of a base graph by given class sizes (0 allowed)."""
    start, cur = [], 0
    for s in sizes:
        start.append(cur)
        cur += s
    n = cur
    adj = [0] * n
    for i in range(base_n):
        for j in range(base_n):
            if i < j and (base_adj[i] >> j) & 1:
                for u in range(start[i], start[i] + sizes[i]):
                    for v in range(start[j], start[j] + sizes[j]):
                        adj[u] |= 1 << v
                        adj[v] |= 1 << u
    return n, adj


def make_c5_blowup(sizes):
    b_n, b_adj = make_cycle(5)
    return make_blowup(b_n, b_adj, sizes)


def make_circulant_dist(n, pred):
    """u ~ v iff pred(circular distance)."""
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            d = min(j - i, n - (j - i))
            if pred(d):
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    return n, adj


def make_andrasfai(k):
    """And(k) = Gamma_{3k-1}: n = 3k-1 vertices, u ~ v iff 3*circdist > n.
    And(2) = C5, And(3) = Mobius-Kantor/Wagner V8, And(4) = Gamma_11."""
    n = 3 * k - 1
    return make_circulant_dist(n, lambda d: 3 * d > n)


def make_petersen():
    n = 10
    adj = [0] * n
    def add(i, j):
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    for i in range(5):
        add(i, (i + 1) % 5)           # outer C5
        add(i, i + 5)                 # spokes
        add(5 + i, 5 + (i + 2) % 5)   # inner pentagram
    return n, adj


def make_grotzsch():
    """Mycielskian of C5: 11 vertices, triangle-free, chi = 4."""
    n = 11
    adj = [0] * n
    def add(i, j):
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    for i in range(5):
        add(i, (i + 1) % 5)
    for i in range(5):                # u_i copies
        for j in range(5):
            if (adj[i] >> j) & 1:
                add(5 + i, j)
    for i in range(5):
        add(10, 5 + i)
    return n, adj


N14_G6 = "M?AE@bH{AYN_LgBs?"


def witnesses():
    """The mandated test suite.  Returns list of (name, n, adj) with n small enough
    for exhaustive cut enumeration; the N=45 witness is handled by the blow-up formula."""
    W = []
    W.append(("C5", ) + make_cycle(5))
    W.append(("C5[2]", ) + make_c5_blowup([2, 2, 2, 2, 2]))
    W.append(("C5[3,1,2,2,1]", ) + make_c5_blowup([3, 1, 2, 2, 1]))
    W.append(("C5[2,2,2,2,0](zero part)", ) + make_c5_blowup([2, 2, 2, 2, 0]))
    W.append(("Petersen", ) + make_petersen())
    W.append(("Grotzsch", ) + make_grotzsch())
    W.append(("Wagner=And(3)", ) + make_andrasfai(3))
    W.append(("Gamma11=And(4)", ) + make_andrasfai(4))
    W.append(("C7", ) + make_cycle(7))
    W.append(("K33", ) + make_complete_bipartite(3, 3))
    W.append(("N14_bip7", ) + g6_decode(N14_G6))
    return W


# ----------------------------------------------------------------------------- bip

def bip_exact(n, adj):
    """min over bipartitions of #monochromatic edges, by full enumeration (v0 fixed)."""
    E = edges(n, adj)
    best = len(E)
    for S in range(1 << (n - 1)):
        s = S << 1              # vertex 0 always on side 0
        m = 0
        for (i, j) in E:
            if ((s >> i) & 1) == ((s >> j) & 1):
                m += 1
                if m >= best:
                    break
        if m < best:
            best = m
    return best


def bip_and_cuts(n, adj):
    """(bip, list of optimal side-masks with vertex 0 on side 0)."""
    E = edges(n, adj)
    best = len(E) + 1
    opt = []
    for S in range(1 << (n - 1)):
        s = S << 1
        m = sum(1 for (i, j) in E if ((s >> i) & 1) == ((s >> j) & 1))
        if m < best:
            best, opt = m, [s]
        elif m == best:
            opt.append(s)
    return best, opt


def bip_blowup_c5(sizes):
    """bip(C5[a0..a4]) = min_i a_i a_{i+1} (proved: class-respecting cuts are optimal)."""
    return min(sizes[i] * sizes[(i + 1) % 5] for i in range(5))


def mono_count(n, adj, sidemask):
    return sum(1 for (i, j) in edges(n, adj)
               if ((sidemask >> i) & 1) == ((sidemask >> j) & 1))


# ----------------------------------------------------------------------------- psi (weighted)

def psi_exact(n, adj, x):
    """psi(H,x) = min over bipartitions of sum of x_u x_v over monochromatic edges.
    x: list of Fractions."""
    E = edges(n, adj)
    best = None
    for S in range(1 << (n - 1)):
        s = S << 1
        tot = Fraction(0)
        for (i, j) in E:
            if ((s >> i) & 1) == ((s >> j) & 1):
                tot += x[i] * x[j]
        if best is None or tot < best:
            best = tot
    return best


def W_mass(n, adj, x):
    return sum(x[i] * x[j] for (i, j) in edges(n, adj))


# ----------------------------------------------------------------------------- deletion DP

def dp_delete_cost(n, adj, cost_fn):
    """min over deletion orderings of sum of cost_fn(subgraph-state, v).

    cost_fn(mask, v, adj) -> integer/Fraction cost of deleting v from G[mask].
    Returns (value, best ordering).  Exact DP over 2^n subsets.
    """
    full = (1 << n) - 1
    INF = None
    val = [None] * (1 << n)
    choice = [-1] * (1 << n)
    val[0] = 0
    # process masks in increasing popcount so subsets are ready
    order = sorted(range(1 << n), key=lambda m: bin(m).count("1"))
    for mask in order:
        if mask == 0:
            continue
        best = None
        bv = -1
        mm = mask
        while mm:
            low = mm & -mm
            v = low.bit_length() - 1
            mm ^= low
            c = cost_fn(mask, v, adj)
            cand = val[mask ^ low] + c
            if best is None or cand < best:
                best, bv = cand, v
        val[mask] = best
        choice[mask] = bv
    # reconstruct
    seq = []
    mask = full
    while mask:
        v = choice[mask]
        seq.append(v)
        mask ^= (1 << v)
    return val[full], seq


def cost_floor_half_degree(mask, v, adj):
    """The canonical sound insertion cost:  bip(G) <= bip(G-v) + floor(d(v)/2)."""
    return bin(adj[v] & mask).count("1") // 2


def dp_greedy_value(n, adj):
    return dp_delete_cost(n, adj, cost_floor_half_degree)


def dp_true_drop(n, adj):
    """DP with the EXACT cost c(G,v) = bip(G) - bip(G-v) (the circular instantiation).
    Value must equal bip(G) for every ordering; used as a self-test."""
    bipcache = {}

    def bip_mask(mask):
        if mask in bipcache:
            return bipcache[mask]
        m, adj2, _ = induced(n, adj, mask)
        r = 0 if m == 0 else bip_exact(m, adj2)
        bipcache[mask] = r
        return r

    def cost(mask, v, _adj):
        return bip_mask(mask) - bip_mask(mask ^ (1 << v))

    return dp_delete_cost(n, adj, cost)


# ----------------------------------------------------------------------------- pentagons

def induced_pentagons(n, adj):
    """List of vertex-tuples inducing a C5 (as frozensets)."""
    out = []
    for S in combinations(range(n), 5):
        mask = 0
        for v in S:
            mask |= 1 << v
        degs = [bin(adj[v] & mask).count("1") for v in S]
        if all(d == 2 for d in degs):
            # 2-regular on 5 vertices and connected => C5
            # connectivity check
            seen = 1 << S[0]
            stack = [S[0]]
            while stack:
                u = stack.pop()
                a = adj[u] & mask & ~seen
                while a:
                    low = a & -a
                    w = low.bit_length() - 1
                    seen |= low
                    stack.append(w)
                    a ^= low
            if seen == mask:
                out.append(frozenset(S))
    return out


def odd_cycles_upto(n, adj, maxlen):
    """All chordless (induced) odd cycles of length <= maxlen, as vertex frozensets."""
    out = []
    for L in range(5, maxlen + 1, 2):
        for S in combinations(range(n), L):
            mask = 0
            for v in S:
                mask |= 1 << v
            if all(bin(adj[v] & mask).count("1") == 2 for v in S):
                seen = 1 << S[0]
                stack = [S[0]]
                while stack:
                    u = stack.pop()
                    a = adj[u] & mask & ~seen
                    while a:
                        low = a & -a
                        w = low.bit_length() - 1
                        seen |= low
                        stack.append(w)
                        a ^= low
                if seen == mask:
                    out.append(frozenset(S))
    return out


# ----------------------------------------------------------------------------- switching

def sigma_values(n, adj, sidemask, x=None):
    """sigma(v) = (mass of neighbours on the other side) - (mass on same side).
    Unweighted if x is None."""
    out = []
    for v in range(n):
        same = other = 0
        a = adj[v]
        while a:
            low = a & -a
            u = low.bit_length() - 1
            a ^= low
            w = 1 if x is None else x[u]
            if ((sidemask >> u) & 1) == ((sidemask >> v) & 1):
                same += w
            else:
                other += w
        out.append(other - same)
    return out


def switch_delta(n, adj, sidemask, S):
    """Change in the number of monochromatic edges when flipping the set S (bitmask)."""
    before = mono_count(n, adj, sidemask)
    after = mono_count(n, adj, sidemask ^ S)
    return after - before


def min_improving_switch(n, adj, sidemask):
    """(size, set) of a smallest improving switch, by exhaustive search over subsets."""
    base = mono_count(n, adj, sidemask)
    best = None
    for S in range(1, 1 << n):
        if bin(S).count("1") >= (best[0] if best else n + 1):
            continue
        if mono_count(n, adj, sidemask ^ S) < base:
            k = bin(S).count("1")
            if best is None or k < best[0]:
                best = (k, S)
    return best


if __name__ == "__main__":
    print("witness table: name N |E| bip  N^2/25  25*bip<=N^2 ?")
    for (name, n, adj) in witnesses():
        b = bip_exact(n, adj)
        print(f"  {name:26s} N={n:3d} |E|={num_edges(n,adj):4d} bip={b:3d} "
              f"N^2/25={Fraction(n*n,25)}  ok={25*b <= n*n}  tf={is_triangle_free(n,adj)}")
    s = [7, 7, 12, 7, 12]
    print(f"  C5{s}: N=45 |E|=385 bip={bip_blowup_c5(s)} N^2/25={Fraction(2025,25)}")
