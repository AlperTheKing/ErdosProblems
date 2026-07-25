"""G10_c5point.py -- EXACT verification of the two local-structure theorems at a
C5-concentration point of an arbitrary triangle-free host H.

Setup.  H triangle-free, C5 = v_1..v_5 induced, x* = (1/5 on the C5, 0 elsewhere).
Admissible direction: d with sum(d)=0 and d_w >= 0 for every w outside the C5.
Active cuts at x*: exactly those with precisely ONE monochromatic C5-edge (the
weight-0 vertices contribute nothing), with the outside vertices on arbitrary sides.

For an active cut with mono C5-edge (i,i+1) the directional derivative is
    5 * (dQ/dt) = d_i + d_{i+1} + sum_w m(w) d_w ,      m(w) = |A_w cap side(w)|,
with A_w = N(w) cap C5 (an independent set of C5, so |A_w| <= 2).  The adversary
minimises, so the minimum over the outside sides is

    F_i(d) := d_i + d_{i+1} + D_i + D_{i-1},        D_j := sum_{w : A_w = P_j} d_w,
    P_j := {v_j, v_{j+2}}   (the five "diagonal" pairs; the only |A_w| = 2 shapes).

THEOREM G10-1 (no first-order ascent).
    F_1 + F_2 + F_3 + F_4 + F_5 = -2 * sum_{w outside, |A_w| <= 1} d_w  <= 0 .
    Hence the F_i cannot all be positive: x* is first-order stationary in EVERY
    triangle-free host.

THEOREM G10-2 (the flat face is C5-colourable).
    If F_1 = ... = F_5 = 0 then d_w = 0 for every w with |A_w| <= 1, and
    S := C5 cup {w : d_w > 0} induces a subgraph of H that is homomorphic to C5
    (send w with A_w = P_j to the colour j+1).  Hence psi(H,y) <= 1/25 for EVERY y
    supported in S, i.e. the whole flat face is capped at 1/25.

This file verifies both statements exactly (Fractions / integers) on generated
triangle-free hosts and random admissible directions.
"""
import sys, os, random
from fractions import Fraction
from itertools import combinations
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from G10_core import adjacency, is_triangle_free, all_cut_monoedges, psi_exact, g6_to_edges


def c5_diagonal_type(n, edges, cyc):
    """For each vertex outside the C5 `cyc` return A_w = N(w) cap C5 as a frozenset
    of POSITIONS 0..4 in the cycle order."""
    adj = adjacency(n, edges)
    pos = {v: k for k, v in enumerate(cyc)}
    out = {}
    for w in range(n):
        if w in pos:
            continue
        A = frozenset(pos[u] for u in cyc if (adj[w] >> u) & 1)
        out[w] = A
    return out


def F_vector(n, edges, cyc, d):
    """The five minimised first-order derivatives (times 5), exactly."""
    types = c5_diagonal_type(n, edges, cyc)
    # P_j = {j, j+2}
    D = [Fraction(0)] * 5
    low = Fraction(0)
    for w, A in types.items():
        if len(A) == 2:
            a, b = sorted(A)
            j = None
            for k in range(5):
                if {k, (k + 2) % 5} == set(A):
                    j = k
            assert j is not None, (A,)   # any independent pair of C5 is a diagonal
            D[j] += d[w]
        else:
            low += d[w]
    F = []
    for i in range(5):
        F.append(d[cyc[i]] + d[cyc[(i + 1) % 5]] + D[i] + D[(i - 1) % 5])
    return F, D, low


def brute_first_order(n, edges, cyc, d):
    """Independent brute-force: minimise <grad Q_c, d> over ALL active cuts."""
    adj = adjacency(n, edges)
    cycset = set(cyc)
    best = None
    for mask in range(1 << (n - 1)):
        m = mask << 1
        mono = [(u, v) for (u, v) in edges if ((m >> u) & 1) == ((m >> v) & 1)]
        monoc5 = [(u, v) for (u, v) in mono if u in cycset and v in cycset]
        if len(monoc5) != 1:
            continue                      # not an active cut
        # grad_v = sum over mono-neighbours u of x*_u ; x* = 1/5 on the C5
        g = [Fraction(0)] * n
        for (u, v) in mono:
            if v in cycset:
                g[u] += Fraction(1, 5)
            if u in cycset:
                g[v] += Fraction(1, 5)
        val = sum(g[v] * d[v] for v in range(n))
        if best is None or val < best:
            best = val
    return best


def hom_to_c5(n, edges):
    adj = adjacency(n, edges)
    nb = [(1 << ((c + 1) % 5)) | (1 << ((c - 1) % 5)) for c in range(5)]
    col = [-1] * n
    order = sorted(range(n), key=lambda v: -bin(adj[v]).count('1'))

    def dfs(k):
        if k == n:
            return True
        v = order[k]
        dom = 31
        m = adj[v]
        for u in range(n):
            if (m >> u) & 1 and col[u] >= 0:
                dom &= nb[col[u]]
        if k == 0:
            dom &= 1
        for c in range(5):
            if (dom >> c) & 1:
                col[v] = c
                if dfs(k + 1):
                    return True
                col[v] = -1
        return False
    return dfs(0)


def induced(n, edges, S):
    idx = {v: i for i, v in enumerate(sorted(S))}
    e = [(idx[u], idx[v]) for (u, v) in edges if u in idx and v in idx]
    return len(idx), e


def random_tf_host(n, cyc_first=True, rng=None):
    """Random triangle-free graph on n vertices containing an induced C5 on 0..4."""
    rng = rng or random.Random()
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]
    es = set(edges)
    adj = adjacency(n, edges)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if (i, j) not in es]
    # never add a chord of the C5 (keeps it induced)
    pairs = [(i, j) for (i, j) in pairs if not (i < 5 and j < 5)]
    rng.shuffle(pairs)
    for (i, j) in pairs:
        if rng.random() < 0.5:
            continue
        if adj[i] & adj[j]:
            continue
        es.add((i, j)); adj[i] |= 1 << j; adj[j] |= 1 << i
    return n, sorted(es)


def run(trials=300, nmax=11, seed=12345):
    rng = random.Random(seed)
    bad1 = bad2 = bad3 = 0
    nflat = 0
    for t in range(trials):
        n = rng.randint(6, nmax)
        n, edges = random_tf_host(n, rng=rng)
        assert is_triangle_free(n, edges)
        cyc = (0, 1, 2, 3, 4)
        # random admissible direction with rational entries
        d = [Fraction(0)] * n
        for w in range(5, n):
            d[w] = Fraction(rng.randint(0, 4))
        tot = sum(d[5:])
        # distribute -tot over the C5 arbitrarily
        parts = [Fraction(rng.randint(-6, 6)) for _ in range(5)]
        parts[4] = -tot - sum(parts[:4])
        for i in range(5):
            d[cyc[i]] = parts[i]
        assert sum(d) == 0
        F, D, low = F_vector(n, edges, cyc, d)
        # (1) closed form matches brute force over all active cuts
        bf = brute_first_order(n, edges, cyc, d)
        if bf != min(F) / 5:
            bad1 += 1
            print('MISMATCH closed form vs brute force', n, edges, d, F, bf)
        # (2) THEOREM G10-1 : sum F_i = -2 * sum_{|A_w|<=1} d_w  <= 0
        if sum(F) != -2 * low or sum(F) > 0:
            bad2 += 1
            print('THEOREM G10-1 FAILS', n, edges, d, F, low)
        # (3) THEOREM G10-2 : if all F_i == 0 the flat face is C5-colourable
        if all(f == 0 for f in F):
            nflat += 1
            S = set(cyc) | {w for w in range(n) if d[w] > 0}
            m, e2 = induced(n, edges, S)
            if not hom_to_c5(m, e2):
                bad3 += 1
                print('THEOREM G10-2 FAILS', n, edges, d, sorted(S))
    print('trials=%d   closed-form mismatches=%d   G10-1 failures=%d   flat directions seen=%d   G10-2 failures=%d'
          % (trials, bad1, bad2, nflat, bad3))
    return bad1 + bad2 + bad3


def exhaustive_flat(trials=4000, nmax=11, seed=777):
    """Search directly for FLAT directions (all F_i = 0) with nonneg outside part,
    then verify the flat face is capped at 1/25 by an EXACT psi evaluation."""
    rng = random.Random(seed)
    found = 0
    viol = 0
    for t in range(trials):
        n = rng.randint(7, nmax)
        n, edges = random_tf_host(n, rng=rng)
        cyc = (0, 1, 2, 3, 4)
        types = c5_diagonal_type(n, edges, cyc)
        diag = {w: A for w, A in types.items() if len(A) == 2}
        if not diag:
            continue
        # choose nonneg weights on diagonal outside vertices; solve the 5 equations for d_i
        dw = {w: Fraction(rng.randint(0, 3)) for w in diag}
        if sum(dw.values()) == 0:
            continue
        D = [Fraction(0)] * 5
        for w, A in diag.items():
            for k in range(5):
                if {k, (k + 2) % 5} == set(A):
                    D[k] += dw[w]
        # solve d_i + d_{i+1} = -(D_i + D_{i-1}) ; the 5-cycle system is invertible
        rhs = [-(D[i] + D[(i - 1) % 5]) for i in range(5)]
        # d_i = (1/2) * sum_k (-1)^k rhs[i+k]  for the odd cycle
        dcyc = []
        for i in range(5):
            s = Fraction(0)
            for k in range(5):
                s += ((-1) ** k) * rhs[(i + k) % 5]
            dcyc.append(s / 2)
        d = [Fraction(0)] * n
        for i in range(5):
            d[cyc[i]] = dcyc[i]
        for w in diag:
            d[w] = dw[w]
        if sum(d) != 0:
            continue
        F, _, _ = F_vector(n, edges, cyc, d)
        if any(f != 0 for f in F):
            continue
        found += 1
        S = set(cyc) | {w for w in range(n) if d[w] > 0}
        m, e2 = induced(n, edges, S)
        if not hom_to_c5(m, e2):
            viol += 1
            print('G10-2 VIOLATION', n, edges, sorted(S))
            continue
        # exact walk along the ray: psi must never exceed 1/25
        ml = all_cut_monoedges(n, edges)
        for num in range(0, 41):
            tt = Fraction(num, 200)
            x = [Fraction(1, 5) if v in set(cyc) else Fraction(0) for v in range(n)]
            x = [x[v] + tt * d[v] for v in range(n)]
            if any(xi < 0 for xi in x):
                break
            s = sum(x)
            if s != 1:
                break
            val = psi_exact(ml, x)
            if val > Fraction(1, 25):
                viol += 1
                print('RAY EXCEEDS 1/25 !!!', n, edges, d, tt, val)
                break
    print('flat directions constructed=%d   violations=%d' % (found, viol))
    return viol


if __name__ == '__main__':
    a = run(trials=int(sys.argv[1]) if len(sys.argv) > 1 else 250)
    b = exhaustive_flat(trials=int(sys.argv[2]) if len(sys.argv) > 2 else 3000)
    print('TOTAL FAILURES:', a + b)
