"""TASK 2 (step 1) -- the REFINED single-pentagon bound, and its exact verification.

New facts used (all consequences of triangle-freeness, all verified in
R9_thmD_adversarial.py as L3):

  R_j := {v notin C : N(v) cap C = {c_j}}   is INDEPENDENT, and
         N(R_j) cap T  subset  T_j u T_{j+2} u T_{j+3}.
  R_0  := {v notin C : N(v) cap C = empty}.

Cut i  =  the bipartition with sides X_i = {i,i+1,i+3}, Y_i = {i+2,i+4} of the
classes P_m = {c_m} u T_m, with every v in R_j placed OPPOSITE its C-neighbour c_j
(exactly Theorem D's rule) and R_0 placed greedily last.  Then

  monochromatic weight of cut i   <=   F_i :=
        z_i z_{i+1}                                        (inside C u T)
      + r_i tau_{i+2} + r_{i+1} tau_{i+4}
      + r_{i+2} tau_i + r_{i+4} tau_{i+1}                   (R_j -- T ; R_{i+3} pays 0)
      + r_i r_{i+1} + r_i r_{i+3} + r_{i+1} r_{i+3} + r_{i+2} r_{i+4}   (R_j -- R_k)
      + (1/2) r_0 eta                                       (R_0, greedy)

  psi(H,x)  <=  min_i F_i .

This file CHECKS "actual monochromatic weight of cut i <= F_i" exactly, for every
graph/pentagon/weight in the battery.  (A single failure kills the refinement.)
"""
import random
from fractions import Fraction as F
import R9_thmD_lib as L

BAD = []


def refined_data(G, C, a):
    n, adj = G
    T, R, Rj, Rnone = L.classify(G, C)
    if Rj is None:
        return None
    P = [set([C[i]]) | set(T[i]) for i in range(5)]
    z = [sum(a[v] for v in P[i]) for i in range(5)]
    tau = [sum(a[v] for v in T[i]) for i in range(5)]
    r = [sum(a[v] for v in Rj[j]) for j in range(5)]
    r0 = sum(a[v] for v in Rnone)
    q = sum(a)
    eta = q - sum(a[c] for c in C)
    return T, R, Rj, Rnone, P, z, tau, r, r0, eta


def cut_i_actual(G, C, a, i, data):
    """build cut i exactly as prescribed and return its monochromatic weight."""
    n, adj = G
    T, R, Rj, Rnone, P, z, tau, r, r0, eta = data
    side = {}
    for m in range(5):
        s = 0 if (m - i) % 5 in (0, 1, 3) else 1
        for v in P[m]:
            side[v] = s
    for j in range(5):
        for v in Rj[j]:
            side[v] = 1 - side[C[j]]
    for v in Rnone:                       # greedy, last, in index order
        c0 = sum(a[w] * a[v] for w in adj[v] if w in side and side[w] == 0)
        c1 = sum(a[w] * a[v] for w in adj[v] if w in side and side[w] == 1)
        side[v] = 0 if c0 <= c1 else 1
    mono = 0
    for u in range(n):
        for v in adj[u]:
            if u < v and side[u] == side[v]:
                mono += a[u] * a[v]
    return mono


def F_i(i, data):
    T, R, Rj, Rnone, P, z, tau, r, r0, eta = data
    def m5(k):
        return k % 5
    val = z[i] * z[m5(i + 1)]
    val += r[i] * tau[m5(i + 2)] + r[m5(i + 1)] * tau[m5(i + 4)] \
        + r[m5(i + 2)] * tau[i] + r[m5(i + 4)] * tau[m5(i + 1)]
    val += r[i] * r[m5(i + 1)] + r[i] * r[m5(i + 3)] \
        + r[m5(i + 1)] * r[m5(i + 3)] + r[m5(i + 2)] * r[m5(i + 4)]
    return F(2 * val + r0 * eta, 2)          # last term is (1/2) r0 eta


def check_graph(G, tag, weights):
    nbad = 0
    for C in L.induced_C5s(G):
        for a in weights:
            if sum(a) == 0:
                continue
            data = refined_data(G, C, a)
            if data is None:
                BAD.append(('classify', tag, L.to_graph6(G), C, list(a)))
                nbad += 1
                continue
            M = L.psi_int(G, a)
            best = None
            for i in range(5):
                act = cut_i_actual(G, C, a, i, data)
                bound = F_i(i, data)
                if act > bound:
                    BAD.append(('CUT>F', tag, L.to_graph6(G), C, list(a), i, act, bound))
                    nbad += 1
                if M > act:
                    BAD.append(('psi>cut', tag, L.to_graph6(G), C, list(a), i))
                    nbad += 1
                best = bound if best is None else min(best, bound)
            if M > best:
                BAD.append(('psi>minF', tag, L.to_graph6(G), C, list(a), M, best))
                nbad += 1
    return nbad


def rand_weights(n, q, k, seed):
    rnd = random.Random(seed)
    out = []
    for _ in range(k):
        cuts = sorted(rnd.randrange(q + 1) for _ in range(n - 1))
        a = [b - aa for aa, b in zip([0] + cuts, cuts + [q])]
        rnd.shuffle(a)
        out.append(a)
    return out


if __name__ == '__main__':
    import R9_thmD_adversarial as A
    N = L.named_graphs()
    print("=" * 78)
    print("H. REFINED bound  psi <= min_i F_i  : exact check on named graphs")
    print("=" * 78)
    tot = 0
    for name, G in N.items():
        C5s = L.induced_C5s(G)
        if not C5s:
            continue
        W = rand_weights(G[0], 12, 30, seed=hash(name) % 977) + [[1] * G[0]]
        nb = check_graph(G, name, W)
        tot += len(C5s) * len(W) * 5
        print("  %-18s pentagons=%3d weights=%2d : failures %d" % (name, len(C5s), len(W), nb))

    print("=" * 78)
    print("I. REFINED bound on the purpose-built adversaries + random triangle-free")
    print("=" * 78)
    fams = [("R0->T2,T3,T0", A.fam_twins_plus_R([1, 1, 1, 1, 1], [(0, [(2, 0), (3, 0), (0, 0)])])[0]),
            ("R0->T2,T3 heavy", A.fam_twins_plus_R([0, 0, 2, 2, 0], [(0, [(2, 0), (2, 1), (3, 0), (3, 1)])])[0]),
            ("Rempty->all twins", A.fam_twins_plus_R([1, 1, 1, 1, 1], [(None, [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)])])[0]),
            ("3 R on 3 classes", A.fam_twins_plus_R([1, 1, 1, 1, 1], [(0, [(2, 0)]), (1, [(3, 0)]), (2, [(4, 0)])])[0]),
            ("dense twins+2R", A.fam_twins_plus_R([2, 2, 2, 2, 2], [(0, [(2, 0), (3, 1)]), (2, [(4, 0), (0, 1)])])[0])]
    for nm, G in fams:
        assert L.is_triangle_free(G), nm
        W = rand_weights(G[0], 12, 40, seed=hash(nm) % 971) + [[1] * G[0]]
        nb = check_graph(G, nm, W)
        tot += len(L.induced_C5s(G)) * len(W) * 5
        print("  %-20s n=%2d : failures %d" % (nm, G[0], nb))

    ng = 0
    for n in range(7, 12):
        for seed in range(25):
            G = A.rand_trianglefree(n, seed * 977 + n, dens=0.85)
            if not L.induced_C5s(G):
                continue
            W = rand_weights(n, 10, 8, seed=seed) + [[1] * n]
            nb = check_graph(G, 'rand', W)
            ng += 1
            tot += len(L.induced_C5s(G)) * len(W) * 5
    print("  random triangle-free graphs: %d graphs, failures %d" % (ng, len(BAD)))
    print("=" * 78)
    print("cut-level checks performed: %d ; FAILURES: %d" % (tot, len(BAD)))
    for b in BAD[:10]:
        print("  ", b)
