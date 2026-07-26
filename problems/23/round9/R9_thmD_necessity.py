"""(a) Is triangle-freeness genuinely used in Theorem D?  -> explicit counterexamples
    to the INEQUALITY once a triangle is allowed (the statement is read literally:
    T_i = {v : N(v) cap C = {c_{i-1},c_{i+1}}},  R = everything else outside C).
(b) Verification of the DEFICIENCY refinement
        cut_i  <=  yhat_i yhat_{i+1} - D_i + BAD_i
    on complete blow-ups with attached W-vertices (this is the inequality that
    quantifies 'a bad W-W edge forces its endpoints to have deficient B-neighbourhoods').
"""
import itertools, random
from fractions import Fraction as Fr
import R9_thmD_lib as L
import R9_thmD_thmE as E

BAD = []


def literal_TR(G, C):
    n, adj = G
    Cs = set(C)
    T = [[] for _ in range(5)]
    R = []
    for v in range(n):
        if v in Cs:
            continue
        nb = adj[v] & Cs
        for i in range(5):
            if nb == {C[(i - 1) % 5], C[(i + 1) % 5]}:
                T[i].append(v)
                break
        else:
            R.append(v)
    return T, R


def thmD_holds(G, C, a):
    T, R = literal_TR(G, C)
    q = sum(a)
    r = sum(a[v] for v in R)
    e = q - sum(a[c] for c in C)
    return 25 * L.psi_int(G, a) <= (q - r) ** 2 + 25 * r * e


def comps(n, q):
    if n == 1:
        yield (q,); return
    for f in range(q + 1):
        for rest in comps(n - 1, q - f):
            yield (f,) + rest


if __name__ == '__main__':
    print("=" * 78)
    print("W. IS TRIANGLE-FREENESS NECESSARY?  (Theorem D read literally, triangles allowed)")
    print("=" * 78)
    base = [(i, (i + 1) % 5) for i in range(5)]
    fams = {
        "C5 + v ~ c0,c1 (one triangle)": L.mkgraph(6, base + [(5, 0), (5, 1)]),
        "C5 + v ~ c0,c1,c2": L.mkgraph(6, base + [(5, 0), (5, 1), (5, 2)]),
        "C5 + v ~ all of C": L.mkgraph(6, base + [(5, i) for i in range(5)]),
        "C5 + K3 attached": L.mkgraph(8, base + [(5, 0), (6, 0), (5, 6), (7, 5), (7, 6)]),
        "C5 + 2 vtx on edge c0c1": L.mkgraph(7, base + [(5, 0), (5, 1), (6, 0), (6, 1)]),
    }
    for nm, G in fams.items():
        C = (0, 1, 2, 3, 4)
        tri = not L.is_triangle_free(G)
        found = None
        for a in comps(G[0], 10):
            if sum(a) == 0:
                continue
            if not thmD_holds(G, C, a):
                found = a
                break
        if found:
            T, R = literal_TR(G, C)
            q = sum(found); r = sum(found[v] for v in R)
            e = q - sum(found[c] for c in C)
            print("  %-30s triangles=%s  COUNTEREXAMPLE a=%s : 25M=%d > %d=(q-r)^2+25re"
                  % (nm, tri, list(found), 25 * L.psi_int(G, found),
                     (q - r) ** 2 + 25 * r * e))
            print("      graph6 = %s   x = %s   (psi = %s, bound = %s)"
                  % (L.to_graph6(G), [str(Fr(t, q)) for t in found],
                     Fr(L.psi_int(G, found), q * q),
                     Fr((q - r) ** 2 + 25 * r * e, 25 * q * q)))
        else:
            print("  %-30s triangles=%s  no counterexample at q=10" % (nm, tri))

    print("=" * 78)
    print("X. DEFICIENCY refinement   cut_i <= yhat_i yhat_{i+1} - D_i + BAD_i")
    print("=" * 78)
    rnd = random.Random(77)
    tot = fails = 0
    for trial in range(500):
        sizes = [rnd.randint(1, 3) for _ in range(5)]
        nW = rnd.randint(1, 3)
        wspec = []
        for _ in range(nW):
            m = rnd.randrange(5)
            pv = [i for i in range(sizes[(m - 1) % 5]) if rnd.random() < .6]
            nx = [i for i in range(sizes[(m + 1) % 5]) if rnd.random() < .6]
            wspec.append((m, pv, nx))
        ww = [(k, l) for k in range(nW) for l in range(k + 1, nW) if rnd.random() < .5]
        G, cls, wv = E.build(sizes, wspec, ww)
        if not L.is_triangle_free(G) or G[0] > 12:
            continue
        adm = E.structure_E1(G, cls)
        assign = {}
        ok = True
        for (v, m) in wv:
            if not adm.get(v):
                ok = False; break
            assign[v] = m if m in adm[v] else adm[v][0]
        if not ok:
            continue
        n, adj = G
        inB = {v: m for m in range(5) for v in cls[m]}
        badsets = E.badsets(G, cls, assign)
        for a in [[rnd.randint(0, 6) for _ in range(G[0])] for _ in range(20)]:
            if sum(a) == 0:
                continue
            y = [sum(a[v] for v in cls[m]) for m in range(5)]
            yh = list(y)
            for v, m in assign.items():
                yh[m] += a[v]
            # deficiencies
            alpha = {}; beta = {}
            for v, m in assign.items():
                alpha[v] = y[(m - 1) % 5] - sum(a[w] for w in adj[v] if w in inB
                                                and inB[w] == (m - 1) % 5)
                beta[v] = y[(m + 1) % 5] - sum(a[w] for w in adj[v] if w in inB
                                               and inB[w] == (m + 1) % 5)
                if alpha[v] < 0 or beta[v] < 0:
                    BAD.append(('neg-deficiency', L.to_graph6(G), v)); fails += 1
            for i in range(5):
                D = sum(a[v] * beta[v] for v in assign if assign[v] == i) \
                    + sum(a[v] * alpha[v] for v in assign if assign[v] == (i + 1) % 5)
                B_i = sum(a[u] * a[v] for (u, v) in badsets[i])
                lhs = E.cut_weight(G, cls, assign, a, i)
                rhs = yh[i] * yh[(i + 1) % 5] - D + B_i
                tot += 1
                if lhs > rhs:
                    BAD.append(('deficiency', L.to_graph6(G), list(a), i, lhs, rhs))
                    fails += 1
            # triangle-freeness forces deficiency on every bad edge (checked here)
            for (u, v) in badsets[0]:
                mu, mv = assign[u], assign[v]
                if mu == mv:
                    if beta[u] + beta[v] < y[(mu + 1) % 5] or alpha[u] + alpha[v] < y[(mu - 1) % 5]:
                        BAD.append(('tf-deficiency-d0', L.to_graph6(G), u, v)); fails += 1
                elif (mu - mv) % 5 == 2:
                    if alpha[u] + beta[v] < y[(mu - 1) % 5]:
                        BAD.append(('tf-deficiency-d2', L.to_graph6(G), u, v)); fails += 1
    print("   %d cut-level deficiency checks, %d failures" % (tot, fails))
    for b in BAD[:8]:
        print("   ", b)
