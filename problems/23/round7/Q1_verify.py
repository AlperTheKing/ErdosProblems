"""Q1_verify.py -- independent exact re-verification (pure Python, exact integers /Fractions)
of the C++ findings:
  * bip(G) by brute force over all 2^n cuts
  * fam(G) = min over independent sets I of mono(N(I))
  * the n=11 falsifier for the N(I)-cut family
  * exact rational psi values on named weighted instances
No floating point anywhere on an acceptance path.
"""
from fractions import Fraction
from itertools import combinations


def g6_decode(s):
    """graph6 -> (n, adjacency list of frozensets)"""
    data = [ord(c) - 63 for c in s]
    n = data[0]
    bits = []
    for x in data[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    adj = [set() for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i].add(j)
                adj[j].add(i)
            idx += 1
    return n, adj


def edges(n, adj):
    return [(i, j) for i in range(n) for j in adj[i] if i < j]


def is_triangle_free(n, adj):
    for i, j in edges(n, adj):
        if adj[i] & adj[j]:
            return False
    return True


def mono_count(E, A):
    """A = frozenset of one side; count monochromatic edges"""
    return sum(1 for (u, v) in E if (u in A) == (v in A))


def bip_bruteforce(n, adj):
    E = edges(n, adj)
    best = len(E)
    for mask in range(1 << n):
        A = {i for i in range(n) if mask >> i & 1}
        m = mono_count(E, A)
        if m < best:
            best = m
    return best


def independent_sets(n, adj):
    """all independent sets as frozensets"""
    out = []

    def rec(v, cur, forbidden):
        if v == n:
            out.append(frozenset(cur))
            return
        rec(v + 1, cur, forbidden)
        if v not in forbidden:
            rec(v + 1, cur | {v}, forbidden | adj[v])

    rec(0, set(), set())
    return out


def fam_bruteforce(n, adj):
    """min over independent sets I of mono(N(I)); returns (value, witness I, witness N(I))"""
    E = edges(n, adj)
    best = (len(E), None, None)
    for I in independent_sets(n, adj):
        NI = set()
        for v in I:
            NI |= adj[v]
        m = mono_count(E, NI)
        if m < best[0]:
            best = (m, I, frozenset(NI))
    return best


def psi_weighted(n, adj, x):
    """min over all 2^n cuts of sum_{uv monochromatic} x_u x_v  (exact Fractions)"""
    E = edges(n, adj)
    best = None
    arg = None
    for mask in range(1 << n):
        A = mask
        tot = Fraction(0)
        for (u, v) in E:
            if ((A >> u) & 1) == ((A >> v) & 1):
                tot += x[u] * x[v]
        if best is None or tot < best:
            best = tot
            arg = frozenset(i for i in range(n) if mask >> i & 1)
    return best, arg


def psi_family_ind(n, adj, x):
    """min over independent sets I of the weighted mono value of the cut N(I)"""
    E = edges(n, adj)
    best = None
    arg = None
    for I in independent_sets(n, adj):
        NI = set()
        for v in I:
            NI |= adj[v]
        tot = Fraction(0)
        for (u, v) in E:
            if (u in NI) == (v in NI):
                tot += x[u] * x[v]
        if best is None or tot < best:
            best = tot
            arg = (I, frozenset(NI))
    return best, arg


def report(name, s):
    n, adj = g6_decode(s)
    E = edges(n, adj)
    tf = is_triangle_free(n, adj)
    b = bip_bruteforce(n, adj)
    f, I, NI = fam_bruteforce(n, adj)
    print(f"--- {name}  g6={s}")
    print(f"    n={n} |E|={len(E)} triangle-free={tf}")
    print(f"    degrees: {sorted(len(adj[i]) for i in range(n))}")
    print(f"    bip={b}   fam=min_I mono(N(I))={f}   n^2/25={Fraction(n*n,25)}")
    print(f"    25*fam - n^2 = {25*f - n*n}   (positive => family fails the 1/25 target)")
    print(f"    fam witness I={sorted(I)} N(I)={sorted(NI)}")
    print(f"    edges: {E}")
    return n, adj, b, f


if __name__ == "__main__":
    # the n=11 falsifier found by Q1_indcut.exe
    report("n11-falsifier", "J?BD@g]Qvo?")
    # the three n=11 graphs where fam > bip but the 1/25 target still holds
    for g in ["J??EDagM_]?", "J??EDawM_]?", "J?AA@b@\\AY?"]:
        report("n11-fam>bip", g)
    # calibration: C5 and Petersen
    report("C5", "DUW")
    # Petersen graph, standard graph6
    report("Petersen", "IheA@GUAo")
