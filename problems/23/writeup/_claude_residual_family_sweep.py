r"""FAMILY SWEEP for the graph-computable residual bank (2026-07-08): extends STAGE-3 coverage FAR beyond census
N<=11 + even-chord, to pin EXACTLY where the graph-computable bank (25*sigma + R_full) stops certifying, per the
C_18 anti-artifact lesson. Uses the EXACT residual + component machinery from _claude_residual_hall_gate.py.

Families (all triangle-free, Gamma-min B-connected max cut):
  * Odd cycles C_{2k+1}: single bad edge, ell=2k+1, R_full=0. Predicted: Demand>25*sigma for k>=12 (N>=25) --
    the graph-computable bank FAILS, but beta=1<=N^2/25 (Gamma=N^2 exactly => TIGHT-RESERVE, NON-DEFICIENT cage:
    the door/residual bank is insufficient here, needing the rowDB bank -- NOT a conjecture obstruction).
  * C5[t] balanced blow-ups (the TIGHT extremal, beta=N^2/25 exactly): all ell=5 => Demand=0 (Branch A, trivially fine).
  * Theta graphs Theta(a,b,c) (two hubs joined by 3 internally-disjoint paths, odd lengths): long atoms, multi-geodesic.

For each: report beta<=N^2/25 (conjecture check), Gamma vs N^2 (reserve sign), and whether the graph-computable
bank 25*sigma+R_full covers Demand PER COMPONENT. A FAIL at a NEGATIVE-reserve (Gamma>N^2) cage would be a genuine
obstruction; a FAIL at a tight/positive-reserve cage just marks the graph-computable model's boundary (expected).
Run from problems/23/writeup.
"""
from fractions import Fraction as F
from _claude_residual_hall_gate import residuals, k2_components
from _codex_k2t_switch_probe import adj_from_edges
from _h import maxcut_all, gmin, Bconn


def analyze(name, n, adj, side=None):
    """Report per-component Demand vs 25*sigma+R_full on the Gamma-min B-conn max cut, or on a PROVIDED max cut
    `side` (used for large structured families where maxcut_all is exponential; the provided cut must be a genuine
    maximum cut -- verified by checking no single flip increases the cut and that it is B-connected)."""
    if side is None:
        mc = maxcut_all(n, adj)
        best = gmin(n, adj, mc)
        if best is None:
            return None
        side = best[0]
    else:
        # verify `side` is locally-optimal (a true max cut is a local max under single-vertex flips) and B-connected
        def cutval(s):
            return sum(1 for a in range(n) for b in adj[a] if a < b and s[a] != s[b])
        cv = cutval(side)
        for v in range(n):
            s2 = side[:]; s2[v] = 1 - s2[v]
            if cutval(s2) > cv:
                return dict(name=name, n=n, badcut=True)
    if not Bconn(n, adj, side):
        return None
    cd = residuals(n, adj, side)
    if cd is None:
        return None
    M, ell, T, K2T, R = cd['M'], cd['ell'], cd['T'], cd['K2T'], cd['R']
    edges = [(a, b) for a in range(n) for b in adj[a] if a < b]
    cut_edges = sum(1 for a, b in edges if side[a] != side[b])
    m = len(M)
    sigma = cut_edges - m
    Gamma = sum(ell[e] ** 2 for e in M)
    beta = len(edges) - cut_edges
    comps = k2_components(n, cd)
    worst = None
    for X in comps:
        VX = X['VX']; atomsX = X['atoms']
        R_full = sum(R[u] for u in VX)
        Demand = sum(ell[e] ** 2 - 25 for e in atomsX)
        cover = F(25) * sigma + R_full
        slack = cover - Demand
        if worst is None or slack < worst['slack']:
            worst = dict(Demand=Demand, R_full=R_full, cover=cover, slack=slack,
                         maxell=max(ell[e] for e in atomsX), nV=len(VX), natoms=len(atomsX))
    return dict(name=name, n=n, m=m, sigma=sigma, Gamma=Gamma, N2=n * n, beta=beta, cap=F(n * n, 25),
                reserve=n * n - Gamma, worst=worst)


def show(r):
    if r is None:
        print("   (skipped: no Gamma-min B-conn cage / no bad edge)")
        return
    if r.get('badcut'):
        print("   %-16s N=%-3d  (skipped: provided side is NOT a maximum cut)" % (r['name'], r['n']))
        return
    w = r['worst']
    concl = "conj OK" if r['beta'] <= r['cap'] else "*** CONJECTURE VIOLATED ***"
    bankfail = "" if w['slack'] >= 0 else "  <== graph-bank INSUFFICIENT (deficit %s)" % (-w['slack'])
    reservetag = ("reserve=%d>0" % r['reserve']) if r['reserve'] > 0 else (
        "reserve=0 TIGHT" if r['reserve'] == 0 else "reserve=%d NEGATIVE(deficient)" % r['reserve'])
    print("   %-16s N=%-3d beta=%-4d N^2/25=%-6s [%s] | Gamma=%-5d N^2=%-5d %s | maxell=%d Demand=%s 25sigma+Rfull=%s%s"
          % (r['name'], r['n'], r['beta'], str(r['cap']), concl, r['Gamma'], r['N2'], reservetag,
             w['maxell'], w['Demand'], w['cover'], bankfail))


def odd_cycle(k):
    n = 2 * k + 1
    E = [(i, (i + 1) % n) for i in range(n)]
    return n, adj_from_edges(n, E)


def c5_blowup(t):
    # 5 groups of t vertices; group i fully joined to groups i+1, i-1 (mod 5). Triangle-free (C_5 has no triangle).
    n = 5 * t
    grp = lambda i: list(range(i * t, i * t + t))
    E = []
    for i in range(5):
        for u in grp(i):
            for v in grp((i + 1) % 5):
                E.append((u, v))
    return n, adj_from_edges(n, E)


def theta(a, b, c):
    # two hubs s,t joined by 3 internally-disjoint paths of edge-lengths a,b,c. Triangle-free if each path >=2 edges
    # and no two paths both length... keep lengths >=2 and distinct enough. Vertices: s=0, t=1, then internal.
    s, t = 0, 1
    nxt = 2
    E = []
    for L in (a, b, c):
        prev = s
        for i in range(L - 1):
            E.append((prev, nxt)); prev = nxt; nxt += 1
        E.append((prev, t))
    n = nxt
    return n, adj_from_edges(n, E)


def main():
    print("=" * 100)
    print("FAMILY SWEEP: graph-computable bank 25*sigma+R_full vs Demand, per component (extends STAGE-3 coverage).")
    print("A bank-insufficient FAIL at a NEGATIVE-reserve cage = genuine obstruction; at tight/positive-reserve = model boundary.")
    print("=" * 100)
    print(" ODD CYCLES C_{2k+1} (single long atom, R_full=0; predicted bank-fail at k>=12 / N>=25, all TIGHT reserve):")
    any_neg_reserve_fail = False
    for k in range(2, 21):
        n, adj = odd_cycle(k)
        r = analyze("C_%d" % (2 * k + 1), n, adj, side=[i % 2 for i in range(n)])
        show(r)
        if r and not r.get('badcut') and r['worst']['slack'] < 0 and r['reserve'] < 0:
            any_neg_reserve_fail = True
    print("\n C5[t] BALANCED BLOW-UPS (TIGHT extremal beta=N^2/25; all ell=5 => Demand=0):")
    for t in range(1, 7):
        n, adj = c5_blowup(t)
        side = [0 if (v // t) in (0, 2, 4) else 1 for v in range(n)]
        r = analyze("C5[%d]" % t, n, adj, side=side)
        show(r)
        if r and not r.get('badcut') and r['worst']['slack'] < 0 and r['reserve'] < 0:
            any_neg_reserve_fail = True
    print("\n THETA GRAPHs Theta(a,b,c) (multi-geodesic long atoms):")
    for (a, b, c) in [(2, 4, 4), (2, 4, 6), (4, 4, 6), (2, 6, 6), (4, 6, 8), (6, 6, 8)]:
        n, adj = theta(a, b, c)
        r = analyze("Th(%d,%d,%d)" % (a, b, c), n, adj)
        show(r)
        if r and not r.get('badcut') and r['worst']['slack'] < 0 and r['reserve'] < 0:
            any_neg_reserve_fail = True
    print("=" * 100)
    print("SWEEP VERDICT: %s" % (
        "*** BANK-INSUFFICIENT at a NEGATIVE-RESERVE (deficient) cage -- GENUINE OBSTRUCTION to the graph-bank route ***"
        if any_neg_reserve_fail else
        "NO negative-reserve cage fails the bank. Bank-insufficiency (if any) occurs ONLY at tight/positive-reserve"
        " NON-deficient cages (beta tiny, conjecture holds) -- this is the graph-computable model's boundary (rowDB bank"
        " needed there), NOT a conjecture obstruction. Consistent with the C_18 analysis."))


if __name__ == '__main__':
    main()
