"""TASK 2 (step 4) -- THEOREM E : the local ball around a C5 BLOW-UP.

THEOREM E.  Let H be triangle-free and let B = (V_0,...,V_4) be a COMPLETE INDUCED
C5-blow-up in H: the V_m are disjoint, each V_m is independent, there is no edge
between V_m and V_{m+2}, and EVERY pair (u,w) in V_m x V_{m+1} is an edge.
(Classes may have any size, including 0 and 1.)  Put W = V(H) \\ (V_0 u...u V_4).

 (E1) [structure]  every v in W has  N(v) cap B  contained in V_{m-1} u V_{m+1}
      for at least one m in Z_5.       [triangle-freeness + completeness]
 (E2) Fix any such assignment m(.), put W_m = {v : m(v)=m}, sigma_m = x(W_m),
      yhat_m = x(V_m) + sigma_m  (so sum yhat = 1).  For i in Z_5 let
        BAD_i = weight of the W-W edges uv with m(u)=m(v),
              + weight of the W-W edges uv with |m(u)-m(v)| = 2 whose "centre"
                (the class between them) is NOT i and NOT i+1.
      Then    psi(H,x)  <=  min_i ( yhat_i yhat_{i+1} + BAD_i )  <=  1/25 + min_i BAD_i.
 (E3) Hence if some i has BAD_i = 0 -- in particular if every W-W edge joins
      classes at C5-distance 1, and in particular if W is independent --
      then psi(H,x) <= 1/25 for EVERY x, with no constraint on x(W).

E3 strictly contains Theorem D(a) (rho = 0), which is the case V_m = {c_m}, W = T.
"""
import random, itertools
from fractions import Fraction as Fr
import R9_thmD_lib as L

FAIL = []


def build(sizes, wspec, wwedges):
    """complete C5 blow-up with class sizes `sizes`, plus W-vertices.
    wspec[k] = (m, nbrs_prev, nbrs_next) : the k-th W vertex is assigned class m and
      is joined to the listed indices of V_{m-1} and V_{m+1}.
    wwedges = list of (k,l) pairs of W-vertices to join."""
    cls, nxt, e = [], 0, []
    for s in sizes:
        cls.append(list(range(nxt, nxt + s)))
        nxt += s
    for m in range(5):
        for u in cls[m]:
            for w in cls[(m + 1) % 5]:
                e.append((u, w))
    wv = []
    for (m, pv, nx) in wspec:
        v = nxt; nxt += 1
        wv.append((v, m))
        for idx in pv:
            if idx < len(cls[(m - 1) % 5]):
                e.append((v, cls[(m - 1) % 5][idx]))
        for idx in nx:
            if idx < len(cls[(m + 1) % 5]):
                e.append((v, cls[(m + 1) % 5][idx]))
    for (k, l) in wwedges:
        e.append((wv[k][0], wv[l][0]))
    e = sorted({(min(a, b), max(a, b)) for a, b in e})
    return L.mkgraph(nxt, e), cls, wv


def structure_E1(G, cls):
    """check (E1) for every W-vertex and return the set of admissible classes."""
    n, adj = G
    inB = {v: m for m in range(5) for v in cls[m]}
    out = {}
    for v in range(n):
        if v in inB:
            continue
        nb = {inB[w] for w in adj[v] if w in inB}
        adm = [m for m in range(5)
               if nb <= {(m - 1) % 5, (m + 1) % 5}]
        out[v] = adm
        if not adm:
            FAIL.append(('E1', L.to_graph6(G), v, sorted(nb)))
    return out


def badsets(G, cls, assign):
    """BAD_i for i in Z_5, given an assignment v -> class."""
    n, adj = G
    inB = {v: m for m in range(5) for v in cls[m]}
    W = [v for v in range(n) if v not in inB]
    bad = [[] for _ in range(5)]
    for u in W:
        for v in adj[u]:
            if v in inB or v <= u:
                continue
            du, dv = assign[u], assign[v]
            d = (du - dv) % 5
            if d == 0:
                for i in range(5):
                    bad[i].append((u, v))
            elif d in (2, 3):
                centre = (du + dv) * 3 % 5 if False else None
                # centre = the class strictly between them on the 5-cycle
                centre = (dv + 1) % 5 if (du - dv) % 5 == 2 else (du + 1) % 5
                for i in range(5):
                    if centre != i and centre != (i + 1) % 5:
                        bad[i].append((u, v))
    return bad


def cut_weight(G, cls, assign, a, i):
    """the cut of E2: class m on side 0 iff (m-i) mod 5 in {0,1,3}; W with its class."""
    n, adj = G
    side = {}
    for m in range(5):
        s = 0 if (m - i) % 5 in (0, 1, 3) else 1
        for v in cls[m]:
            side[v] = s
    for v, m in assign.items():
        side[v] = 0 if (m - i) % 5 in (0, 1, 3) else 1
    mono = 0
    for u in range(n):
        for v in adj[u]:
            if u < v and side[u] == side[v]:
                mono += a[u] * a[v]
    return mono


def check_E(G, cls, assign, weights, tag):
    n, adj = G
    inB = {v: m for m in range(5) for v in cls[m]}
    bad = badsets(G, cls, assign)
    nb = 0
    for a in weights:
        q = sum(a)
        if q == 0:
            continue
        yhat = [0] * 5
        for v in range(n):
            m = inB[v] if v in inB else assign[v]
            yhat[m] += a[v]
        M = L.psi_int(G, a)
        best = None
        for i in range(5):
            B_i = sum(a[u] * a[v] for (u, v) in bad[i])
            bnd = yhat[i] * yhat[(i + 1) % 5] + B_i
            cw = cut_weight(G, cls, assign, a, i)
            if cw > bnd:
                FAIL.append(('E2-cut', tag, L.to_graph6(G), list(a), i, cw, bnd)); nb += 1
            best = bnd if best is None else min(best, bnd)
        if M > best:
            FAIL.append(('E2', tag, L.to_graph6(G), list(a), M, best)); nb += 1
        if min(sum(a[u] * a[v] for (u, v) in bad[i]) for i in range(5)) == 0:
            if 25 * M > q * q:                    # (E3) : psi <= 1/25 unconditionally
                FAIL.append(('E3', tag, L.to_graph6(G), list(a), M, q)); nb += 1
    return nb


def rand_weights(n, q, k, seed):
    rnd = random.Random(seed)
    out = []
    for _ in range(k):
        cuts = sorted(rnd.randrange(q + 1) for _ in range(n - 1))
        a = [b - aa for aa, b in zip([0] + cuts, cuts + [q])]
        rnd.shuffle(a)
        out.append(a)
    return out


def all_weights(n, q):
    def comp(n, q):
        if n == 1:
            yield (q,); return
        for f in range(q + 1):
            for r in comp(n - 1, q - f):
                yield (f,) + r
    return list(comp(n, q))


if __name__ == '__main__':
    rnd = random.Random(2026)
    print("=" * 78)
    print("L. THEOREM E: random complete blow-ups + W-vertices (partial twins).")
    print("   'BAD=0' instances test the UNCONDITIONAL claim psi <= 1/25 (E3).")
    print("=" * 78)
    nE3 = nE3w = ntot = 0
    for trial in range(400):
        sizes = [rnd.randint(1, 2) for _ in range(5)]
        if rnd.random() < .25:
            sizes[rnd.randrange(5)] = rnd.choice([0, 3])
        nW = rnd.randint(1, 3)
        wspec = []
        for _ in range(nW):
            m = rnd.randrange(5)
            pv = [i for i in range(sizes[(m - 1) % 5]) if rnd.random() < .6]
            nx = [i for i in range(sizes[(m + 1) % 5]) if rnd.random() < .6]
            wspec.append((m, pv, nx))
        # W-W edges: distance-1 only (BAD = 0) most of the time, else anything
        ww = []
        for k in range(nW):
            for l in range(k + 1, nW):
                dk = (wspec[k][0] - wspec[l][0]) % 5
                want1 = dk in (1, 4)
                if (want1 and rnd.random() < .6) or (not want1 and rnd.random() < .25):
                    ww.append((k, l))
        G, cls, wv = build(sizes, wspec, ww)
        if not L.is_triangle_free(G):
            continue
        if sum(sizes) == 0 or G[0] > 12:
            continue
        adm = structure_E1(G, cls)
        assign = {}
        okassign = True
        for (v, m) in wv:
            if not adm.get(v):
                okassign = False; break
            assign[v] = m if m in adm[v] else adm[v][0]
        if not okassign:
            continue
        W = rand_weights(G[0], 10, 25, seed=trial) + [[1] * G[0]]
        if G[0] <= 8:
            W += all_weights(G[0], 8)
        nb = check_E(G, cls, assign, W, 'rand%d' % trial)
        ntot += 1
        bad = badsets(G, cls, assign)
        if min(len(bad[i]) for i in range(5)) == 0:
            nE3 += 1
            nE3w += len(W)
    print("  %d blow-up+W graphs tested; %d of them have BAD_i = 0 for some i" % (ntot, nE3))
    print("  (E3) unconditional psi <= 1/25 tested on %d exact weight vectors" % nE3w)
    print("  failures so far: %d" % len(FAIL))

    print("=" * 78)
    print("M. THEOREM E on the named graphs, using every complete induced blow-up found")
    print("   (singleton classes = every induced C5 -- so E3 subsumes Theorem D(a))")
    print("=" * 78)
    N = L.named_graphs()
    import R9_thmD_adversarial as A
    for name in ['C5', 'C5[2]', 'C5[3,1,2,2,1]', 'Petersen', 'Wagner=And(3)',
                 'Grotzsch', 'And(4)=G11', 'MTF14']:
        G = N[name]
        n, adjacency = G
        cnt = cov = 0
        for C in L.induced_C5s(G):
            cls = [[c] for c in C]
            adm = structure_E1(G, cls)
            # choose an assignment minimising the number of BAD edges (greedy over all)
            Wv = [v for v in range(n) if v not in set(C)]
            if any(not adm[v] for v in Wv):
                continue
            bestassign, bestbad = None, None
            for combo in itertools.product(*[adm[v] for v in Wv]):
                assign = dict(zip(Wv, combo))
                b = badsets(G, cls, assign)
                mb = min(len(b[i]) for i in range(5))
                if bestbad is None or mb < bestbad:
                    bestbad, bestassign = mb, assign
                if bestbad == 0:
                    break
            cnt += 1
            if bestbad == 0:
                cov += 1
                W = rand_weights(n, 10, 20, seed=cnt) + [[1] * n]
                check_E(G, cls, bestassign, W, name)
        print("  %-16s pentagons=%3d ; with an assignment making some BAD_i = 0 : %d"
              % (name, cnt, cov))

    print("=" * 78)
    print("THEOREM E failures: %d" % len(FAIL))
    for f in FAIL[:10]:
        print("   ", f)
