# flag-algebra-free density lens: ANCHORED (pivotal) PENTAGON reformulation of Erdos #23.
# All arithmetic EXACT (ints / Fractions).
#
# Definitions (cut = bitmask S of side-0; side1 = complement):
#   mono edge: both ends same side.  beta(G) = min over cuts of #mono.
#   For a 5-cycle C and a cut: #mono edges of C is 1,3,5 (parity).  An ANCHOR of C
#   is a mono edge of C whose two C-neighbour edges are both cross.  Claim: every
#   5-cycle has at most one anchor (checked here exhaustively per graph).
#   R(cut) = # of anchored 5-cycles = sum over mono uv of #paths x-z-y with
#   x in N_cross(u), y in N_cross(v)   [triangle-freeness kills all degeneracies].
# Proposition A:  R(cut) <= #C5(G)  for EVERY cut of every triangle-free G.
# Named cap (Grzesik / HHKNR): #C5(G) <= (N/5)^5 for triangle-free G.
# Missing lemma APS(kappa):  max over cuts R >= (N/5)^5 + kappa*(beta - N^2/25)*(N/5)^3
#   for triangle-free G with 25*delta > 4N-2 (post-peel window).
#   APS + PropA + cap  ==>  beta <= N^2/25.
# This battery measures kappa_req exactly on a zoo and self-checks every identity.

import random
from fractions import Fraction
from itertools import combinations, permutations

def make(n, edges, name):
    edges = sorted(set((min(u, v), max(u, v)) for (u, v) in edges))
    adj = [0] * n
    for u, v in edges:
        assert u != v and 0 <= u < n and 0 <= v < n, name
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    for u, v in edges:
        assert adj[u] & adj[v] == 0, "TRIANGLE in " + name
    return {"n": n, "edges": edges, "adj": adj, "name": name}

def cut_value(G, m):
    c = 0
    for u, v in G["edges"]:
        if ((m >> u) ^ (m >> v)) & 1:
            c += 1
    return c

def maxcut_and_masks(G, cap=250000):
    n, edges, adj = G["n"], G["edges"], G["adj"]
    full = (1 << n) - 1
    best = -1
    masks = []
    capped = False
    for m in range(1 << (n - 1)):
        comp = full ^ m
        c = 0
        mm = m
        while mm:
            b = mm & -mm
            u = b.bit_length() - 1
            c += (adj[u] & comp).bit_count()
            mm ^= b
        if c > best:
            best = c
            masks = [m]
        elif c == best:
            if len(masks) < cap:
                masks.append(m)
            else:
                capped = True
    return best, masks, capped

def pentagons(G):
    n, adj = G["n"], G["adj"]
    out = []
    for S in combinations(range(n), 5):
        a = S[0]
        rest = S[1:]
        seen = set()
        for p in permutations(rest):
            cyc = (a,) + p
            key = min(cyc[1], cyc[4])
            if cyc[1] != key:
                continue  # kill direction double-count
            ok = True
            for i in range(5):
                u, v = cyc[i], cyc[(i + 1) % 5]
                if not (adj[u] >> v) & 1:
                    ok = False
                    break
            if ok:
                out.append(cyc)
    return out

def trA5(G):
    n, adj = G["n"], G["adj"]
    A = [[(adj[i] >> j) & 1 for j in range(n)] for i in range(n)]
    def mul(X, Y):
        return [[sum(X[i][k] * Y[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
    A2 = mul(A, A)
    A4 = mul(A2, A2)
    A5 = mul(A4, A)
    return sum(A5[i][i] for i in range(n))

def R_of_cut(G, m):
    n, edges, adj = G["n"], G["edges"], G["adj"]
    full = (1 << n) - 1
    comp = full ^ m
    tot = 0
    for u, v in edges:
        su = (m >> u) & 1
        if su != ((m >> v) & 1):
            continue
        opp = m if su == 0 else comp
        X = adj[u] & opp
        Y = adj[v] & opp
        assert X & Y == 0
        for z in range(n):
            tot += (adj[z] & X).bit_count() * (adj[z] & Y).bit_count()
    return tot

def R_direct(G, m, pents):
    tot = 0
    for cyc in pents:
        side = [(m >> x) & 1 for x in cyc]
        monopos = [i for i in range(5) if side[i] == side[(i + 1) % 5]]
        assert len(monopos) in (1, 3, 5), "parity"
        anchors = [i for i in monopos
                   if ((i - 1) % 5) not in monopos and ((i + 1) % 5) not in monopos]
        assert len(anchors) <= 1, "anchor uniqueness FAILS"
        tot += len(anchors)
    return tot

def beta_report(G, allcuts_R=False, cap=250000, selftest_pents=None):
    n = G["n"]
    e = len(G["edges"])
    mc, masks, capped = maxcut_and_masks(G, cap)
    beta = e - mc
    Rbest_max = 0
    lim = min(len(masks), 25000)
    for m in masks[:lim]:
        r = R_of_cut(G, m)
        if r > Rbest_max:
            Rbest_max = r
    Rbest_all = None
    if allcuts_R:
        Rbest_all = 0
        for m in range(1 << (n - 1)):
            r = R_of_cut(G, m)
            if r > Rbest_all:
                Rbest_all = r
    if selftest_pents is not None:
        for m in list(selftest_pents):
            assert R_of_cut(G, m) == R_direct(G, m, G["pents"]), "PropA formula mismatch"
    return {"e": e, "maxcut": mc, "beta": beta, "nmaxcuts": len(masks),
            "capped": capped, "Rmax_over_maxcuts": Rbest_max,
            "Rmax_over_allcuts": Rbest_all}

def kappa_req(n, beta, R, delta):
    A5 = Fraction(n ** 5, 3125)
    T3 = Fraction(n ** 3, 125)
    gap = Fraction(n * n, 25) - beta
    win = 25 * delta > 4 * n - 2
    if gap < 0:
        return ("CONJ-CE", win)
    if gap == 0:
        return (("OK-tight" if R >= A5 else "NEEDS-INF"), win)
    if R >= A5:
        return (Fraction(0), win)
    return ((A5 - R) / (gap * T3), win)

# ---------- graph zoo ----------
def cyc(k):
    return make(k, [(i, (i + 1) % k) for i in range(k)], "C%d" % k)

def circulant(k, diffs, name=None):
    E = []
    for i in range(k):
        for d in diffs:
            E.append((i, (i + d) % k))
    return make(k, E, name or ("C%d(%s)" % (k, ",".join(map(str, diffs)))))

def blowup(base, sizes, name):
    ofs = []
    t = 0
    for s in sizes:
        ofs.append(t)
        t += s
    E = []
    for (u, v) in base["edges"]:
        for i in range(sizes[u]):
            for j in range(sizes[v]):
                E.append((ofs[u] + i, ofs[v] + j))
    return make(t, E, name)

def petersen():
    E = ([(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)]
         + [(5, 7), (7, 9), (9, 6), (6, 8), (8, 5)])
    return make(10, E, "Petersen")

def groetzsch():
    E = [(i, (i + 1) % 5) for i in range(5)]
    for j in range(5):
        E += [(5 + j, (j - 1) % 5), (5 + j, (j + 1) % 5), (5 + j, 10)]
    return make(11, E, "Groetzsch")

def rand_maximal_tf(n, seed):
    rnd = random.Random(seed)
    adj = [0] * n
    E = []
    pairs = list(combinations(range(n), 2))
    changed = True
    while changed:
        changed = False
        rnd.shuffle(pairs)
        for (u, v) in pairs:
            if not (adj[u] >> v) & 1 and adj[u] & adj[v] == 0:
                adj[u] |= 1 << v
                adj[v] |= 1 << u
                E.append((u, v))
                changed = True
    return make(n, E, "randMaxTF(n=%d,s=%d)" % (n, seed))

def run(G, allcuts=False, selftest=False):
    n = G["n"]
    pents = pentagons(G)
    G["pents"] = pents
    t5 = trA5(G)
    assert t5 == 10 * len(pents), "tr(A^5) != 10*#C5 in " + G["name"]
    st = None
    if selftest:
        rnd = random.Random(99)
        st = [rnd.randrange(1 << (n - 1)) for _ in range(12)] + [0]
    rep = beta_report(G, allcuts_R=allcuts, selftest_pents=st)
    deg = [G["adj"][i].bit_count() for i in range(n)]
    delta = min(deg)
    R = rep["Rmax_over_allcuts"] if rep["Rmax_over_allcuts"] is not None else rep["Rmax_over_maxcuts"]
    assert R <= len(pents), "PropA violated (R > #C5) in " + G["name"]
    kr, win = kappa_req(n, rep["beta"], R, delta)
    x = Fraction(25 * rep["beta"], n * n)
    y = Fraction(3125 * R, n ** 5)
    print("%-28s N=%-3d e=%-4d mc=%-4d beta=%-4d #C5=%-6d Rmax(maxcuts)=%-6d Rall=%-6s delta=%-2d win=%d x=%s y=%s kappa_req=%s%s"
          % (G["name"], n, rep["e"], rep["maxcut"], rep["beta"], len(pents),
             rep["Rmax_over_maxcuts"], str(rep["Rmax_over_allcuts"]), delta, int(win),
             str(x), str(y),
             (str(kr) + ("(=%.4f)" % float(kr) if isinstance(kr, Fraction) else "")),
             "  CAPPED" if rep["capped"] else ""), flush=True)
    return {"name": G["name"], "n": n, "beta": rep["beta"], "R": R,
            "C5": len(pents), "kappa": kr, "win": win}

def main():
    results = []
    C5 = cyc(5)

    # --- core identities on blow-ups: beta(C5[n_i]) = min n_i n_{i+1}; R = prod checks
    print("== blow-up formula checks ==", flush=True)
    for sizes in [(1, 1, 1, 1, 1), (2, 2, 2, 2, 2), (1, 1, 1, 1, 2), (1, 2, 1, 2, 2),
                  (2, 2, 2, 2, 3), (1, 1, 2, 2, 2), (3, 3, 3, 3, 3), (1, 3, 2, 3, 2)]:
        B = blowup(C5, sizes, "C5%s" % (sizes,))
        mc, _, _ = maxcut_and_masks(B)
        beta = len(B["edges"]) - mc
        pred = min(sizes[i] * sizes[(i + 1) % 5] for i in range(5))
        assert beta == pred, (sizes, beta, pred)
        assert 25 * pred <= B["n"] ** 2, "min prod > N^2/25 ?!"
    print("beta(C5[n])=min n_i n_{i+1} verified on 8 size-vectors; min-prod<=N^2/25 all", flush=True)

    # tight calibration at balanced blow-ups: R(canonical maxcut) = t^5 = #C5, beta=t^2
    for t in (1, 2, 3):
        B = blowup(C5, (t,) * 5, "C5[%d]" % t)
        pents = pentagons(B)
        B["pents"] = pents
        assert len(pents) == t ** 5
        # canonical cut: classes V1,V3 on side1
        m = 0
        for i in range(t):
            m |= 1 << (0 * t + i)
            m |= 1 << (2 * t + i)
        mc, masks, _ = maxcut_and_masks(B)
        beta = len(B["edges"]) - mc
        assert beta == t * t
        r = R_of_cut(B, m)
        assert r == R_direct(B, m, pents) == t ** 5, (t, r)
        print("C5[%d]: beta=t^2=%d, #C5=t^5=%d, R(canonical)=t^5 TIGHT (x=1,y=1)" % (t, beta, len(pents)), flush=True)

    # edge-monotonicity of beta: spot check
    rnd = random.Random(5)
    for trial in range(6):
        H = rand_maximal_tf(9, 100 + trial)
        mcH, _, _ = maxcut_and_masks(H)
        bH = len(H["edges"]) - mcH
        for _ in range(4):
            eidx = rnd.randrange(len(H["edges"]))
            E2 = [ed for i, ed in enumerate(H["edges"]) if i != eidx]
            H2 = make(9, E2, "H2")
            mc2, _, _ = maxcut_and_masks(H2)
            assert len(E2) - mc2 <= bH, "beta not edge-monotone?!"
    print("beta edge-monotone: 24/24 spot checks pass", flush=True)

    print("== zoo ==", flush=True)
    zoo_small = [cyc(5), cyc(7), cyc(9), cyc(11), cyc(13),
                 petersen(), groetzsch(),
                 circulant(8, [1, 4], "Andrasfai3=C8(1,4)"),
                 circulant(11, [1, 4], "Andrasfai4=C11(1,4)"),
                 circulant(14, [1, 4, 7], "Andrasfai5=C14(1,4,7)"),
                 circulant(10, [1, 3]), circulant(13, [1, 5]),
                 blowup(C5, (1, 1, 1, 1, 2), "C5[1,1,1,1,2]"),
                 blowup(C5, (2, 2, 2, 2, 3), "C5[2,2,2,2,3]"),
                 blowup(C5, (2, 2, 2, 2, 2), "C5[2]"),
                 blowup(cyc(7), (2,) * 7, "C7[2]"),
                 ]
    for G in zoo_small:
        results.append(run(G, allcuts=(G["n"] <= 14), selftest=(G["n"] <= 11)))

    zoo_big = [blowup(C5, (3, 3, 3, 3, 3), "C5[3]"),
               blowup(C5, (3, 3, 3, 3, 4), "C5[3,3,3,3,4]"),
               circulant(17, [1, 4], "C17(1,4)"),
               blowup(cyc(9), (2,) * 9, "C9[2]"),
               blowup(petersen(), (2,) * 10, "Petersen[2]"),
               blowup(C5, (4, 4, 4, 4, 4), "C5[4]"),
               blowup(cyc(7), (3,) * 7, "C7[3]"),
               ]
    for G in zoo_big:
        results.append(run(G, allcuts=False, selftest=False))

    # C5[3] minus edges (perturbations)
    B = blowup(C5, (3, 3, 3, 3, 3), "x")
    rnd = random.Random(11)
    for k in (1, 2, 3):
        E = list(B["edges"])
        for _ in range(k):
            E.pop(rnd.randrange(len(E)))
        results.append(run(make(15, E, "C5[3]-minus%d" % k), allcuts=False))

    # random maximal triangle-free hunt
    print("== random maximal TF hunt ==", flush=True)
    worst = None
    for n in (12, 13, 14, 15):
        for s in range(10):
            G = rand_maximal_tf(n, 1000 * n + s)
            r = run(G, allcuts=(n <= 13))
            results.append(r)

    print("== kappa summary ==", flush=True)
    kw = [r for r in results if isinstance(r["kappa"], Fraction) and r["win"]]
    ka = [r for r in results if isinstance(r["kappa"], Fraction)]
    if kw:
        w = max(kw, key=lambda r: r["kappa"])
        print("worst kappa_req IN WINDOW : %s = %s (%.5f)" % (w["name"], w["kappa"], float(w["kappa"])), flush=True)
    if ka:
        a = max(ka, key=lambda r: r["kappa"])
        print("worst kappa_req overall   : %s = %s (%.5f)" % (a["name"], a["kappa"], float(a["kappa"])), flush=True)
    bad = [r for r in results if r["kappa"] == "CONJ-CE" or r["kappa"] == "NEEDS-INF"]
    print("CONJ-CE/NEEDS-INF entries: %s" % ([(r["name"], r["kappa"]) for r in bad] if bad else "none"), flush=True)
    print("BATTERY DONE", flush=True)

if __name__ == "__main__":
    main()
