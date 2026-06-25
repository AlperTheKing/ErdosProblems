#!/usr/bin/env python3
"""D4 SKEPTIC: independent re-derivation of chain (b) soundness.

Goal: attack the per-state inequality  sum_r lam_r g_r(H) >= d_mono(H) - 2/25
which is the HEART of chain (b). I re-implement:
  - beta(H) = e(H) - maxcut(H)  by brute force over 2-colorings (independent of their brute_dmono)
  - d_mono(H) = 2*beta(H)/n^2
  - the deficit functional g_r(H) FROM SCRATCH from the docstring math (NOT calling fx.gr_exact),
    then CROSS-CHECK against fx.gr_exact on the same graphs.
And then I check the convex-combo lower-bound inequality directly on all small triangle-free graphs.
"""
import itertools, pickle
from fractions import Fraction as F
import flag_engine as fe
import flag_sdp as fs
import flag_exact as fx

T = F(2, 25)

def beta_bruteforce(n, A):
    """e(H) - maxcut(H), brute over all 2-colorings. A[i]=neighbor bitmask."""
    edges = []
    for i in range(n):
        for j in range(i+1, n):
            if (A[i] >> j) & 1:
                edges.append((i, j))
    e = len(edges)
    if n == 0:
        return 0
    best_cut = 0
    for mask in range(1 << n):
        cut = 0
        for (i, j) in edges:
            if ((mask >> i) & 1) != ((mask >> j) & 1):
                cut += 1
        if cut > best_cut:
            best_cut = cut
    return e - best_cut  # beta = mono edges in best (max-cut) coloring

def d_mono(n, A):
    """2*beta/n^2 as a Fraction."""
    if n == 0:
        return F(0)
    return F(2 * beta_bruteforce(n, A), n * n)

def my_gr(states, k, Asig, pmap, t):
    """Independent re-implementation of the deficit functional from the docstring.
    g_r(H) = (1/(n)_k) sum_{ordered R inducing sigma} [ (mono density over non-root pairs) - t ].
    mono density = (1/C(m,2)) sum_{u<v in rest, adjacent} q_u q_v + (1-q_u)(1-q_v).
    q_w = pmap[ frozenset(i: w~R[i]) ], default 1/2.
    """
    sigma = (k, Asig)
    out = []
    for (n, A) in states:
        if n < 2:
            out.append(F(0)); continue
        adj = [[bool((A[u] >> v) & 1) for v in range(n)] for u in range(n)]
        nk = 1
        for i in range(k):
            nk *= (n - i)
        m = n - k
        Cm2 = m * (m - 1) // 2
        if Cm2 <= 0 or nk == 0:
            out.append(F(0)); continue
        g = F(0)
        for R in itertools.permutations(range(n), k):
            if not fs._induces_sigma_ordered(A, R, sigma):
                continue
            Rset = set(R)
            rest = [w for w in range(n) if w not in Rset]
            q = {}
            for w in rest:
                alpha = frozenset(i for i in range(k) if adj[w][R[i]])
                q[w] = pmap.get(alpha, F(1, 2))
            cm = F(0)
            for ui in range(len(rest)):
                u = rest[ui]
                for vi in range(ui + 1, len(rest)):
                    v = rest[vi]
                    if adj[u][v]:
                        cm += q[u]*q[v] + (1-q[u])*(1-q[v])
            g += (cm / Cm2 - t)
        out.append(g / nk)
    return out

def load_deficit_pmap(prov, idx):
    pr = prov[idx]
    if pr[0] == "deficit":
        _, k, A, cls, p = pr
        pmap = {cls[i]: F(int(p[i])) for i in range(len(cls))}
        return k, A, pmap
    else:
        _, k, A, pmap = pr
        return k, A, pmap

def main():
    d = pickle.load(open('dual_cert_n9.pkl', 'rb'))
    prov = d['prov']; ndix = d['ndix']
    lam = [F(s) for s in d['lam']]
    # nonzero deficit atoms
    active = [(ndix[c], lam[c]) for c in range(len(ndix)) if lam[c] != 0]
    print("active deficit atoms:", [(i, float(v)) for i, v in active])
    print("sum lam =", sum(lam))

    # CROSS-CHECK my_gr vs fx.gr_exact on small graphs for one active atom
    test_states = []
    for nn in (5, 6, 7):
        test_states += fe.enumerate_graphs(nn, triangle_free=True)
    print("test_states count:", len(test_states))

    i0, _ = active[0]
    k, A, pmap = load_deficit_pmap(prov, i0)
    mine = my_gr(test_states, k, A, pmap, T)
    theirs = fx.gr_exact(test_states, k, A, pmap, T)
    mism = sum(1 for a, b in zip(mine, theirs) if a != b)
    print("CROSS-CHECK my_gr vs fx.gr_exact atom", i0, "mismatches:", mism, "/", len(mine))

    # Build convex combo S(H) = sum lam_r g_r(H), and compare to d_mono(H)-2/25, all exact.
    # Precompute each active atom's g over the test set USING MY implementation.
    combos = [F(0)] * len(test_states)
    for (i, v) in active:
        k, A, pmap = load_deficit_pmap(prov, i)
        g = my_gr(test_states, k, A, pmap, T)
        for s in range(len(test_states)):
            combos[s] += v * g[s]

    # Now the inequality:  S(H) >= d_mono(H) - 2/25  ?
    worst = None
    nviol = 0
    for s, (n, A) in enumerate(test_states):
        dm = d_mono(n, A)
        lhs = combos[s]          # sum lam g
        rhs = dm - T             # d_mono - 2/25
        slack = lhs - rhs        # must be >= 0 for chain (b)
        if slack < 0:
            nviol += 1
            if worst is None or slack < worst[0]:
                worst = (slack, n, A, dm, lhs)
    print("chain(b) inequality  sum_lam g >= d_mono - 2/25 :")
    print("  violations:", nviol, "/", len(test_states))
    if worst:
        print("  WORST slack:", float(worst[0]), "n=", worst[1], "d_mono=", float(worst[3]), "S=", float(worst[4]))
    else:
        print("  min slack >= 0 (no violation)")

    # ALSO independently confirm: max over test_states of FULL cert LHS (lam g + gam m) <= delta?
    # (We only have deficit part with my_gr; the moment part is gate G1. But check deficit-only
    #  upper side too:  is there a state where sum lam g > delta already? That alone would break it
    #  unless moment terms can be negative — but gam>=0 and m_j>=0 means they only ADD, so if
    #  sum lam g(H) > delta for some H, the cert is BROKEN regardless of G1.)
    mn = int(d['maxPhi_num']); md = int(d['maxPhi_den']); delta = F(mn, md)
    over = [(s, combos[s]) for s in range(len(test_states)) if combos[s] > delta]
    print("states with sum_lam_g(H) > delta (deficit part alone):", len(over))
    if over:
        mx = max(over, key=lambda t: t[1])
        n, A = test_states[mx[0]]
        print("  max sum_lam_g =", float(mx[1]), " delta =", float(delta), " n=", n)
        print("  NOTE: moment atoms have gam>=0,m>=0 so they only INCREASE LHS; cannot rescue.")

if __name__ == "__main__":
    main()
