"""TASK 1 (part 2) -- verify every STEP of the Theorem D proof, and attack it with
purpose-built adversarial graphs + random triangle-free graphs.

Proof steps checked, exactly, on every (graph, pentagon) pair encountered:
 L1  |N(v) cap C| <= 1 for v in R                    [triangle-freeness]
 L2  every edge of H[C u T] joins CONSECUTIVE classes P_i={c_i} u T_i
 L3  R_j (unique C-neighbour c_j) is independent, and has NO neighbour in
     T_{j-1} u T_{j+1}                                [triangle-freeness]
 L4  the bipartition built in the proof has monochromatic weight <= the bound
     (this is the step that would break if the proof were wrong)
"""
import random, itertools
from fractions import Fraction as F
import R9_thmD_lib as L

BAD = []


def proof_steps(G, C, verbose=False):
    """returns (ok, info); checks L1,L2,L3 structurally (weight-free)."""
    n, adj = G
    Cs = set(C)
    T, R, Rj, Rnone = L.classify(G, C)
    if Rj is None:
        BAD.append(('L1', L.to_graph6(G), C))
        return False, None
    # L2 : edges of H[C u T] only between consecutive classes
    P = [set([C[i]]) | set(T[i]) for i in range(5)]
    where = {}
    for i in range(5):
        for v in P[i]:
            where[v] = i
    for u in where:
        for v in adj[u]:
            if v in where:
                d = (where[u] - where[v]) % 5
                if d not in (1, 4):
                    BAD.append(('L2', L.to_graph6(G), C, u, v, where[u], where[v]))
                    return False, None
    # L3
    for j in range(5):
        for u in Rj[j]:
            for v in Rj[j]:
                if v in adj[u]:
                    BAD.append(('L3-indep', L.to_graph6(G), C, u, v))
                    return False, None
            for m in ((j - 1) % 5, (j + 1) % 5):
                if adj[u] & set(T[m]):
                    BAD.append(('L3-nbr', L.to_graph6(G), C, u, j, m))
                    return False, None
    return True, (T, R, Rj, Rnone, P)


def proof_cut_weight(G, C, a, info):
    """Build the exact bipartition of the proof and return its monochromatic weight
    (integer, in units of 1/q^2), minimised over the 5 choices of the pair (a,a+1)
    exactly as the proof prescribes (choose the minimiser of y_a y_{a+1})."""
    n, adj = G
    T, R, Rj, Rnone, P = info
    y = [sum(a[v] for v in P[i]) for i in range(5)]
    best = min(range(5), key=lambda i: y[i] * y[(i + 1) % 5])
    side = {}
    for i in range(5):
        s = 0 if (i - best) % 5 in (0, 1, 3) else 1
        for v in P[i]:
            side[v] = s
    for j in range(5):
        cj_side = side[C[j]]
        for v in Rj[j]:
            side[v] = 1 - cj_side                     # opposite its C-neighbour
    for v in Rnone:
        side[v] = 0                                    # arbitrary, as the proof says
    mono = 0
    for u in range(n):
        for v in adj[u]:
            if u < v and side[u] == side[v]:
                mono += a[u] * a[v]
    return mono, y, best


def full_check(G, name, weights, tag):
    """run L1-L3 once per pentagon, then L4 + Theorem D for every weight vector."""
    C5s = L.induced_C5s(G)
    nviol = 0
    for C in C5s:
        ok, info = proof_steps(G, C)
        if not ok:
            return -1
        T, R, Rj, Rnone, P = info
        for a in weights:
            q = sum(a)
            if q == 0:
                continue
            r = sum(a[v] for v in R)
            e = q - sum(a[c] for c in C)
            M = L.psi_int(G, a)
            mono, y, best = proof_cut_weight(G, C, a, info)
            # L4a : the proof's cut is a legal bipartition, so psi <= its weight
            if M > mono:
                BAD.append(('L4a', tag, L.to_graph6(G), C, list(a), M, mono))
                nviol += 1
            # L4b : the proof's cut weight is <= the claimed bound
            if 25 * mono > (q - r) ** 2 + 25 * r * e:
                BAD.append(('L4b', tag, L.to_graph6(G), C, list(a), mono))
                nviol += 1
            # Theorem D itself
            if 25 * M > (q - r) ** 2 + 25 * r * e:
                BAD.append(('THMD', tag, L.to_graph6(G), C, list(a), M))
                nviol += 1
    return nviol


def rand_weights(n, q, k, seed):
    rnd = random.Random(seed)
    out = []
    for _ in range(k):
        cuts = sorted(rnd.randrange(q + 1) for _ in range(n - 1))
        a = [b - aa for aa, b in zip([0] + cuts, cuts + [q])]
        rnd.shuffle(a)
        out.append(a)
    return out


# ------------------------------------------------------ adversarial families -
def fam_twins_plus_R(t_sizes, r_spec):
    """C5 (0..4) + t_sizes[i] full twins of class i + R-vertices.
    r_spec: list of (c_index or None, set of (class, index) twins to attach)."""
    e = [(i, (i + 1) % 5) for i in range(5)]
    nxt = 5
    twins = [[] for _ in range(5)]
    for i in range(5):
        for _ in range(t_sizes[i]):
            v = nxt; nxt += 1
            twins[i].append(v)
            e.append((v, (i - 1) % 5))
            e.append((v, (i + 1) % 5))
    for cj, att in r_spec:
        v = nxt; nxt += 1
        if cj is not None:
            e.append((v, cj))
        for (cl, idx) in att:
            if idx < len(twins[cl]):
                e.append((v, twins[cl][idx]))
    return L.mkgraph(nxt, e), twins


def rand_trianglefree(n, seed, dens=1.0):
    rnd = random.Random(seed)
    adj = [set() for _ in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    rnd.shuffle(pairs)
    for (i, j) in pairs:
        if rnd.random() > dens:
            continue
        if adj[i] & adj[j]:
            continue
        adj[i].add(j); adj[j].add(i)
    return L.mkgraph(n, [(i, j) for i in range(n) for j in adj[i] if i < j])


if __name__ == '__main__':
    N = L.named_graphs()
    print("=" * 78)
    print("E. PROOF-STEP verification L1-L4 on the named graphs")
    print("=" * 78)
    tot = 0
    for name, G in N.items():
        C5s = L.induced_C5s(G)
        if not C5s:
            continue
        W = rand_weights(G[0], 12, 40, seed=hash(name) % 997)
        W += [[1] * G[0]]
        if 12 % 5 == 0:
            pass
        v = full_check(G, name, W, name)
        tot += len(C5s) * len(W)
        print("  %-18s pentagons=%3d weights=%d  L1-L4 violations: %s"
              % (name, len(C5s), len(W), v))

    print("=" * 78)
    print("F. PURPOSE-BUILT adversaries: twins + R-vertices wired to be maximally costly")
    print("=" * 78)
    fams = []
    # R vertex on c_0 attached to every twin it is allowed to touch (T_2, T_3, T_0)
    fams.append(("R0 -> T2,T3,T0 (max legal)", fam_twins_plus_R(
        [1, 1, 1, 1, 1], [(0, [(2, 0), (3, 0), (0, 0)])])))
    fams.append(("R0 -> T2,T3 heavy", fam_twins_plus_R(
        [0, 0, 2, 2, 0], [(0, [(2, 0), (2, 1), (3, 0), (3, 1)])])))
    fams.append(("two R on c_0", fam_twins_plus_R(
        [0, 0, 2, 2, 0], [(0, [(2, 0), (3, 0)]), (0, [(2, 1), (3, 1)])])))
    fams.append(("R_empty -> many twins", fam_twins_plus_R(
        [1, 1, 1, 1, 1], [(None, [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)])])))
    fams.append(("R_empty -> T0,T1 only", fam_twins_plus_R(
        [2, 2, 0, 0, 0], [(None, [(0, 0), (0, 1), (1, 0), (1, 1)])])))
    fams.append(("R on c0 and R on c1 adjacent-ish", fam_twins_plus_R(
        [1, 1, 1, 1, 1], [(0, [(2, 0)]), (1, [(3, 0)]), (2, [(4, 0)])])))
    fams.append(("dense twins 2 each + 2 R", fam_twins_plus_R(
        [2, 2, 2, 2, 2], [(0, [(2, 0), (3, 1)]), (2, [(4, 0), (0, 1)])])))
    fams.append(("twins only, no R (rho=0)", fam_twins_plus_R(
        [3, 1, 2, 0, 2], [])))
    for nm, (G, tw) in fams:
        if not L.is_triangle_free(G):
            print("  %-34s SKIP (not triangle-free by construction)" % nm)
            continue
        W = rand_weights(G[0], 12, 60, seed=hash(nm) % 991) + [[1] * G[0]]
        v = full_check(G, nm, W, nm)
        print("  %-34s n=%2d pent=%3d  L1-L4+ThmD violations: %s"
              % (nm, G[0], len(L.induced_C5s(G)), v))

    print("=" * 78)
    print("G. RANDOM triangle-free graphs (n=7..12), all pentagons, random + all-ones weights")
    print("=" * 78)
    ngraph = nc5 = ninst = 0
    for n in range(7, 13):
        for seed in range(40):
            G = rand_trianglefree(n, seed * 131 + n, dens=0.9)
            C5s = L.induced_C5s(G)
            if not C5s:
                continue
            W = rand_weights(n, 10, 12, seed=seed) + [[1] * n]
            v = full_check(G, 'rand', W, 'rand n=%d s=%d' % (n, seed))
            ngraph += 1; nc5 += len(C5s); ninst += len(C5s) * len(W)
        print("  n=%2d cumulative: graphs=%d pentagons=%d instances=%d violations=%d"
              % (n, ngraph, nc5, ninst, len(BAD)))

    print("=" * 78)
    print("TOTAL L1-L4 / Theorem D violations found: %d" % len(BAD))
    for b in BAD[:15]:
        print("   ", b)
