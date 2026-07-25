"""audit_Q2_v2_core.py -- AUDITOR's own independent primitives for round7/Q2.md.

Deliberately different data structures from Q2_*.py:
  * graphs are bitmask adjacency lists (list of ints), not sets;
  * a cut is an int bitmask of side-Y vertices, not a list;
  * Delta(S) is obtained by RECOMPUTING the cut value after the switch
    (never from the claimed formula) -- the formula is then checked against it;
  * all arithmetic is Python int / Fraction (exact).
"""
from fractions import Fraction as F
from itertools import combinations

# ---------------------------------------------------------------- graph6

def g6(line):
    """own graph6 decoder -> (n, adjmask list).  Handles n<63 only."""
    s = line.strip()
    n = ord(s[0]) - 63
    assert 0 <= n < 63, "this decoder only handles n<63"
    bits = 0
    nb = 0
    for ch in s[1:]:
        bits = (bits << 6) | (ord(ch) - 63)
        nb += 6
    adj = [0] * n
    # graph6 order: (0,1),(0,2),(1,2),(0,3),(1,3),(2,3),...
    pos = 0
    for j in range(1, n):
        for i in range(j):
            bit = (bits >> (nb - 1 - pos)) & 1
            pos += 1
            if bit:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    return n, adj


def g6_encode(n, adj):
    assert n < 63
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (adj[i] >> j) & 1 else 0)
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        out += chr(v + 63)
    return out


def pc(x):
    return bin(x).count("1")


def edges(n, adj):
    return [(i, j) for i in range(n) for j in range(i + 1, n) if (adj[i] >> j) & 1]


def is_trianglefree(n, adj):
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1 and (adj[i] & adj[j]):
                return False
    return True


def is_maximal_tf(n, adj):
    if not is_trianglefree(n, adj):
        return False
    for i in range(n):
        for j in range(i + 1, n):
            if not (adj[i] >> j) & 1:
                if adj[i] & adj[j] == 0:
                    return False
    return True


# ---------------------------------------------------------------- cuts

def mono(n, adj, Y):
    """number of monochromatic edges for the cut with side-Y = bitmask Y."""
    m = 0
    for i in range(n):
        same = adj[i] & (Y if (Y >> i) & 1 else ~Y)
        m += pc(same & ~((1 << (i + 1)) - 1))
    return m


def maxcut_bip(n, adj):
    """bip(G) = |E| - maxcut(G), by brute force over 2^(n-1) cuts."""
    best = None
    for Y in range(1 << (n - 1)):
        m = mono(n, adj, Y)
        if best is None or m < best:
            best = m
    return best


def sigma(n, adj, Y):
    sg = []
    for i in range(n):
        yi = (Y >> i) & 1
        dB = pc(adj[i] & (Y if not yi else ~Y) & ((1 << n) - 1))
        dM = pc(adj[i] & ((Y if yi else ~Y) & ((1 << n) - 1)))
        sg.append(dB - dM)
    return sg


def delta_recompute(n, adj, Y, S):
    """Delta(S) = mono(Y) - mono(Y xor S)  (gain in crossing edges)."""
    return mono(n, adj, Y) - mono(n, adj, Y ^ S)


def delta_formula(n, adj, Y, S, sg):
    """-sum_S sigma - 2 e_M(S) + 2 e_B(S)."""
    v = -sum(sg[i] for i in range(n) if (S >> i) & 1)
    for i in range(n):
        if not (S >> i) & 1:
            continue
        nb = adj[i] & S & ~((1 << (i + 1)) - 1)
        j = nb
        while j:
            b = j & -j
            k = b.bit_length() - 1
            v += -2 if ((Y >> i) & 1) == ((Y >> k) & 1) else 2
            j ^= b
    return v


def is_maxcut(n, adj, Y):
    m = mono(n, adj, Y)
    for Z in range(1 << (n - 1)):
        if mono(n, adj, Z) < m:
            return False
    return True


# --------------------------------------------- families of switching sets

def star_sets(n, adj, Y):
    """S = {v} u T, T subset of N_B(v):  the accepted 'switch-star' family."""
    out = []
    for v in range(n):
        yv = (Y >> v) & 1
        NB = adj[v] & (Y if not yv else ~Y) & ((1 << n) - 1)
        sub = NB
        while True:
            out.append((1 << v) | sub)
            if sub == 0:
                break
            sub = (sub - 1) & NB
    return out


def indep_sets(n, adj, mask):
    """all independent subsets of `mask` (brute force; small n only)."""
    verts = [i for i in range(n) if (mask >> i) & 1]
    res = []

    def rec(k, cur):
        if k == len(verts):
            res.append(cur)
            return
        rec(k + 1, cur)
        v = verts[k]
        if adj[v] & cur == 0:
            rec(k + 1, cur | (1 << v))
    rec(0, 0)
    return res


def family_star_ineq(n, adj, Y):
    """family (*): S = N(v) u T, T independent, T cap N(v) = empty."""
    out = []
    full = (1 << n) - 1
    for v in range(n):
        Nv = adj[v]
        for T in indep_sets(n, adj, full & ~Nv):
            out.append(Nv | T)
    return out
