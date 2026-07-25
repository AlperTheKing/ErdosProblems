"""(c) arc cuts are cuts and ARCBOUND >= psi;
(d) int m dmu = W - int g^2 dmu, and m(b) is the value of the cut N(b);
(f) bound_k is a valid upper bound on min_b m(b), including degenerate g.

Everything exact.  Also prints the full profile of the nine round-5 witnesses.
"""
import random
from fractions import Fraction as F
from itertools import combinations
from P4_core import (from_gamma, adjacency, sort_cyclic, W_of, T_of, A_of, g_of, g_at, mono,
                     m_at, m_values, bound_k, arcbound, psi, arcs, far, circdist, TARGET)

random.seed(4)

WITNESSES = [
    ("W1 half-arc killer", 8, [0, 1, 0, 1, 2, 0, 2, 1]),
    ("W1' Gamma_11", 11, [0, 0, 1, 0, 0, 1, 2, 0, 0, 2, 1]),
    ("W1'' Gamma_16", 16, [0, 0, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 2, 0, 1]),
    ("W2 five-atom extremal", 5, [1, 1, 1, 1, 1]),
    ("W3 uniform Gamma_18", 18, [1] * 18),
    ("W4 uniform Gamma_20", 20, [1] * 20),
    ("W5 three-atom near-path", 12, [3, 0, 0, 0, 3, 0, 0, 0, 0, 3, 0, 0]),
    ("W6 seven-atom", 7, [1] * 7),
    ("W7 unequal five-atom", 20, [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1, 3, 0, 0, 0, 0, 0, 1, 3]),
    ("Gamma_40 argmax-g witness", 40, [0] * 1 + [8] + [0] * 5 + [11] + [0] * 8 + [12] + [0] * 4
     + [12] + [0] * 10 + [11] + [0] * 7),
]


def random_measure(m, natoms=None, maxw=6):
    natoms = natoms or random.randint(3, min(9, m))
    idx = random.sample(range(m), natoms)
    w = [0] * m
    for i in idx:
        w[i] = random.randint(1, maxw)
    if sum(w) == 0:
        w[idx[0]] = 1
    return from_gamma(m, w)


def profile(pos, wt, kmax=8):
    pos, wt = sort_cyclic(pos, wt)
    adj = adjacency(pos)
    W = W_of(pos, wt, adj)
    T = T_of(pos, wt, adj)
    A = A_of(pos, wt, adj)
    g = g_of(pos, wt, adj)
    mv = m_values(pos, wt, adj)
    ab = arcbound(pos, wt, adj)
    ps = psi(pos, wt, adj) if len(pos) <= 20 else None
    bks = [bound_k(pos, wt, k, adj) for k in range(kmax + 1)]
    return dict(pos=pos, wt=wt, adj=adj, W=W, T=T, A=A, g=g, m=mv, arcbound=ab, psi=ps, bk=bks)


def main():
    print("=" * 100)
    print("(d) IDENTITY  int m dmu = W - int g^2 dmu    and   m(b) = value of the cut N(b)")
    print("=" * 100)
    bad_id = bad_cut = 0
    tested = 0
    ms = list(range(5, 25))
    for _ in range(400):
        m = random.choice(ms)
        pos, wt = random_measure(m)
        pos, wt = sort_cyclic(pos, wt)
        adj = adjacency(pos)
        W = W_of(pos, wt, adj)
        g = g_of(pos, wt, adj)
        mv = m_values(pos, wt, adj)
        lhs = sum(wt[b] * mv[b] for b in range(len(pos)))
        rhs = W - sum(wt[b] * g[b] ** 2 for b in range(len(pos)))
        tested += 1
        if lhs != rhs:
            bad_id += 1
            print("   IDENTITY FAIL", m, pos, wt, lhs, rhs)
        # m(b) really is the value of the cut S = N(b), computed two independent ways
        for b in range(len(pos)):
            inS = [adj[b][v] for v in range(len(pos))]
            direct = mono(pos, wt, inS, adj)
            viaformula = W - sum(wt[v] * g[v] for v in range(len(pos)) if adj[b][v])
            if direct != mv[b] or direct != viaformula:
                bad_cut += 1
                print("   CUT-VALUE FAIL", m, b, direct, mv[b], viaformula)
        # N(b) must be independent (triangle-freeness)
        for b in range(len(pos)):
            nb = [v for v in range(len(pos)) if adj[b][v]]
            if any(adj[u][v] for u, v in combinations(nb, 2)):
                print("   N(b) NOT INDEPENDENT", m, b)
    print(f"  int m dmu == W - int g^2 dmu      : {tested-bad_id}/{tested} exact")
    print(f"  m(b) == mono(N(b)) (3 ways)       : {'all ok' if bad_cut==0 else str(bad_cut)+' FAILURES'}")

    # ---- the pairing hazard: the arc attached by starting index instead of through N(b)
    print("\n  the pairing hazard (arc taken as [b + ceil(m/3), ...] by INDEX vs the true N(b)):")
    m = 11
    pos, wt = from_gamma(m, [1, 0, 2, 0, 3, 0, 0, 2, 0, 1, 0])
    pos, wt = sort_cyclic(pos, wt)
    adj = adjacency(pos)
    W = W_of(pos, wt, adj)
    g = g_of(pos, wt, adj)
    n = len(pos)
    print(f"    support {pos}  weights {wt}   W={W}")
    for b in range(n):
        true_m = m_at(pos, wt, pos[b], adj)
        # WRONG: pair the b-th atom with the arc that starts at the b-th atom
        wrong_mask = [False] * n
        for t in range((n + 2) // 3):
            wrong_mask[(b + t) % n] = True
        wrong = mono(pos, wt, wrong_mask, adj)
        print(f"    b={b} pos={pos[b]}  m(b)={str(true_m):>10s}={float(true_m):.5f}   "
              f"index-arc value={str(wrong):>10s}={float(wrong):.5f}   "
              f"{'DIFFER' if wrong != true_m else 'same'}")

    # ---------------------------------------------------------------------------
    print("\n" + "=" * 100)
    print("(c)+(f)  ARCBOUND >= psi ;  bound_k >= min_b m(b) >= ARCBOUND ;  all <= 1/25 ?")
    print("=" * 100)
    viol_cp = viol_bk = viol_25 = 0
    tested = 0
    worst_arc = None
    for _ in range(600):
        m = random.choice(ms)
        pos, wt = random_measure(m)
        pos, wt = sort_cyclic(pos, wt)
        if len(pos) > 16:
            continue
        adj = adjacency(pos)
        ab = arcbound(pos, wt, adj)
        ps = psi(pos, wt, adj)
        mn = min(m_values(pos, wt, adj))
        tested += 1
        if ab < ps:
            viol_cp += 1
            print("   ARCBOUND < psi  IMPOSSIBLE", pos, wt, ab, ps)
        for k in range(0, 7):
            bk = bound_k(pos, wt, k, adj)
            if bk is not None and bk < mn:
                viol_bk += 1
                print("   bound_k < min m(b)", k, pos, wt, bk, mn)
        if ab > TARGET:
            viol_25 += 1
            print("   *** ARCBOUND > 1/25 ***", m, pos, wt, ab, float(ab))
        if worst_arc is None or ab > worst_arc[0]:
            worst_arc = (ab, m, pos, wt)
    print(f"  ARCBOUND >= psi                   : {tested-viol_cp}/{tested}")
    print(f"  bound_k >= min_b m(b), k=0..6     : {'no violation' if viol_bk==0 else str(viol_bk)}")
    print(f"  ARCBOUND <= 1/25                  : {tested-viol_25}/{tested}")
    print(f"  largest ARCBOUND seen             : {float(worst_arc[0]):.6f} "
          f"({worst_arc[0]}) on Gamma_{worst_arc[1]} support {worst_arc[2]}")

    # degenerate cases for (f)
    print("\n  (f) degenerate cases:")
    cases = [("isolated atom present", 12, [3, 0, 0, 0, 3, 0, 0, 1, 0, 3, 0, 0]),
             ("all g = 0 (independent set)", 12, [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
             ("single atom", 5, [1, 0, 0, 0, 0]),
             ("empty far graph, two atoms", 9, [1, 0, 0, 2, 0, 0, 0, 0, 0])]
    for nm, m, w in cases:
        pos, wt = from_gamma(m, w)
        pos, wt = sort_cyclic(pos, wt)
        adj = adjacency(pos)
        g = g_of(pos, wt, adj)
        mv = m_values(pos, wt, adj)
        bs = [bound_k(pos, wt, k, adj) for k in range(4)]
        print(f"    {nm:28s} g={[str(t) for t in g]}  m(b)={[str(t) for t in mv]}  "
              f"bound_0..3={[('None' if b is None else str(b)) for b in bs]}  "
              f"ARCBOUND={arcbound(pos,wt,adj)}")

    # ---------------------------------------------------------------------------
    print("\n" + "=" * 100)
    print("FULL PROFILE OF THE ROUND-5 WITNESSES (exact)")
    print("=" * 100)
    hdr = f"{'witness':28s} {'W':>10s} {'T/W':>7s} {'A':>10s} {'b_0':>10s} {'min b_k':>10s} {'min m(b)':>10s} {'ARCB':>10s} {'psi':>10s}"
    print(hdr)
    for nm, m, w in WITNESSES:
        pos, wt = from_gamma(m, w)
        p = profile(pos, wt)
        bks = [b for b in p['bk'] if b is not None]
        tw = float(p['T'] / p['W']) if p['W'] else float('nan')
        print(f"{nm:28s} {float(p['W']):10.6f} {tw:7.4f} {float(p['A']):10.6f} "
              f"{float(p['bk'][0]):10.6f} {float(min(bks)):10.6f} {float(min(p['m'])):10.6f} "
              f"{float(p['arcbound']):10.6f} "
              f"{(('%10.6f' % float(p['psi'])) if p['psi'] is not None else '     n/a ')}"
              f"  {'ARC>1/25!' if p['arcbound'] > TARGET else ''}"
              f"{' minm>1/25!' if min(p['m']) > TARGET else ''}")


if __name__ == '__main__':
    main()
