r"""Threshold-cut / random-cut TV inequality probe (the 'random cut' entropy idea), EXACT. 2026-07-08.

DERIVED FACT (integrate the max-cut vertex inequality |dM(U)|<=|dB(U)| over threshold cuts U={phi<=theta}):
   for ANY phi: V->R,   sum_{bad (u,v)} |phi(u)-phi(v)|  <=  sum_{blue (x,y)} |phi(x)-phi(y)|.      (TV)
This is a genuine first-moment consequence of maximum cut (no deficiency needed). Tests:
 (1) TV holds exactly for random integer phi on census + C5[t] (structural sanity).
 (2) TIGHTNESS at C5[t] under the C5-coloring phi (=part index on the pentagon): is TV an equality? (extremal-tight)
 (3) DISTANCE-SOURCE double count: sum_w TV with phi_w=d_B(w,.):
        LHS = sum_bad sum_w |d_B(w,u)-d_B(w,v)|      RHS = sum_w sum_blue |d_B(w,x)-d_B(w,y)|
     compare LHS to Gamma=sum ell^2 and RHS to N*|B| and N^2 -- is the resulting bound tight at C5[t] or loose?
     (i.e. does the 2nd-moment-over-sources escape circularity, or is it loose like all spreading args?)
Run from problems/23/writeup: python _claude_tv_randomcut_probe.py
"""
from fractions import Fraction as F
from collections import deque
import random, subprocess
from _h import Bconn, dec, maxcut_all, gmin, GENG, blow
from _codex_k2t_switch_probe import adj_from_edges


def blue_dist_all(n, adj, side, s):
    d = {s: 0}; q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if side[u] != side[v] and v not in d:
                d[v] = d[u] + 1; q.append(v)
    return d


def edges_by_type(n, adj, side):
    bad = []; blue = []
    for a in range(n):
        for b in adj[a]:
            if a < b:
                (bad if side[a] == side[b] else blue).append((a, b))
    return bad, blue


def tv_check(n, adj, side, phi):
    bad, blue = edges_by_type(n, adj, side)
    lhs = sum(abs(phi[a] - phi[b]) for a, b in bad)
    rhs = sum(abs(phi[a] - phi[b]) for a, b in blue)
    return lhs, rhs


def distance_source_doublecount(n, adj, side):
    bad, blue = edges_by_type(n, adj, side)
    D = [blue_dist_all(n, adj, side, w) for w in range(n)]
    # only count sources that reach both endpoints (Bconn => all reach)
    lhs = 0; rhs = 0
    for w in range(n):
        dw = D[w]
        for a, b in bad:
            if a in dw and b in dw:
                lhs += abs(dw[a] - dw[b])
        for a, b in blue:
            if a in dw and b in dw:
                rhs += abs(dw[a] - dw[b])
    return lhs, rhs, len(blue), len(bad)


def main():
    print("Threshold-cut TV inequality + distance-source double count (EXACT)")
    print("=" * 100)
    # (1)+(3) census sanity + double count
    random.seed(1)
    tv_fail = 0; ntest = 0
    print("\nC5[t] extremal:")
    for t in range(1, 6):
        nn, E = blow(t); adj = adj_from_edges(nn, E)
        best = gmin(nn, adj, maxcut_all(nn, adj))
        if best is None:
            continue
        side, G, M, ell = best
        # (2) C5-coloring phi = part index (0..4) on pentagon -> use pentagon metric via +-1 steps.
        # part(v)=v//t ; pentagon coordinate: use phi=part index (linear 0..4). TV under this phi:
        part = [v // t for v in range(nn)]
        lhs, rhs = tv_check(nn, adj, side, part)
        # random phi checks
        rf = 0
        for _ in range(200):
            phi = [random.randint(0, 50) for _ in range(nn)]
            l, r = tv_check(nn, adj, side, phi)
            ntest += 1
            if l > r:
                rf += 1; tv_fail += 1
        dl, dr, nblue, nbad = distance_source_doublecount(nn, adj, side)
        Gamma = G
        print("  C5[%d] N=%2d Gamma=%4d N^2=%4d | part-phi TV: %d<=%d slack=%d %s | randfail=%d/200"
              % (t, nn, Gamma, nn * nn, lhs, rhs, rhs - lhs, "TIGHT" if lhs == rhs else "", rf))
        print("        dist-source: LHS(bad)=%d  RHS(blue)=%d  N*|B|=%d  Gamma=%d  N^2=%d | LHS/Gamma=%s RHS/(N|B|)=%s"
              % (dl, dr, nn * nblue, Gamma, nn * nn,
                 str(F(dl, Gamma)) if Gamma else '-', str(F(dr, nn * nblue)) if nblue else '-'))
    # census random-phi TV sanity
    print("\nCensus N<=9 random-phi TV sanity (should NEVER fail; TV is a theorem):")
    cfail = 0; cn = 0
    for nn in range(5, 10):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            best = gmin(n, adj, maxcut_all(n, adj))
            if best is None:
                continue
            side = best[0]
            if not Bconn(n, adj, side):
                continue
            cn += 1
            for _ in range(20):
                phi = [random.randint(0, 30) for _ in range(n)]
                l, r = tv_check(n, adj, side, phi)
                if l > r:
                    cfail += 1
        print("   census N=%d: cages=%d TV-fails=%d" % (nn, cn, cfail), flush=True)
    print("\nSUMMARY: TV inequality random-phi failures: C5[t]=%d/%d  census=%d (expect 0 -- it is a theorem from max-cut)"
          % (tv_fail, ntest, cfail))
    print("distance-source double count: LHS/Gamma and RHS/(N|B|) ratios above reveal tightness/looseness at C5[t].")


if __name__ == '__main__':
    main()
