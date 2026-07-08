r"""Is GAMMA-MINIMALITY essential for the local condition (L)?  Test (L) on ALL max cuts (not only Gamma-min).
If (L) fails on some non-Gamma-min max cut, Gamma-minimality is the essential lever for the reduction.
Also record the max lambda_c (ell=5 geodesic multiplicity) over Gamma-min cuts to see if the pure-5 bound lambda<=4 is real.
"""
from fractions import Fraction as F
import subprocess
from _claude_residual_hall_gate import residuals
from _claude_shortrow_hall_gate import one_shortest_geodesic_edges
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def max_load_and_lam(n, adj, side):
    cd = residuals(n, adj, side)
    if cd is None:
        return None
    M, ell = cd['M'], cd['ell']
    rows = [e for e in M if 5 <= ell[e] <= 23]
    if any(ell[e] > 23 for e in M):
        return None
    load = {}; lam5 = {}
    for e in rows:
        ed = one_shortest_geodesic_edges(adj, side, e[0], e[1])
        if ed is None:
            return None
        w = F(ell[e] ** 2, ell[e] - 1)
        for c in ed:
            load[c] = load.get(c, F(0)) + w
            if ell[e] == 5:
                lam5[c] = lam5.get(c, 0) + 1
    mx = max(load.values()) if load else F(0)
    mlam5 = max(lam5.values()) if lam5 else 0
    return mx, mlam5


def gamma_of(n, adj, side, cd):
    return sum(cd['ell'][e] ** 2 for e in cd['M'])


def main():
    gmin_fail = 0; nonmin_fail = 0; nonmin_checked = 0; gmin_checked = 0
    max_lam5_gmin = 0; ex_nonmin = None
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            cuts = maxcut_all(n, adj)
            best = gmin(n, adj, cuts)
            if best is None:
                continue
            gmin_side = best[0]
            cdmin = residuals(n, adj, gmin_side)
            if cdmin is None:
                continue
            gmval = gamma_of(n, adj, gmin_side, cdmin)
            # gmin cut
            if Bconn(n, adj, gmin_side):
                r = max_load_and_lam(n, adj, gmin_side)
                if r is not None:
                    gmin_checked += 1
                    if r[0] > 25:
                        gmin_fail += 1
                    max_lam5_gmin = max(max_lam5_gmin, r[1])
            # all OTHER max cuts (non-min Gamma)
            for s in cuts:
                cd = residuals(n, adj, s)
                if cd is None:
                    continue
                if gamma_of(n, adj, s, cd) <= gmval:
                    continue  # this is a (or the) min; skip
                if not Bconn(n, adj, s):
                    continue
                r = max_load_and_lam(n, adj, s)
                if r is None:
                    continue
                nonmin_checked += 1
                if r[0] > 25:
                    nonmin_fail += 1
                    if ex_nonmin is None:
                        ex_nonmin = (nn, g6, str(r[0]), r[1])
        print("  N=%d: gmin_checked %d gmin_fail %d | nonmin_checked %d nonmin_fail %d | max_lam5(gmin) %d"
              % (nn, gmin_checked, gmin_fail, nonmin_checked, nonmin_fail, max_lam5_gmin), flush=True)
    print("=" * 80)
    print("GAMMA-MIN gmin_fail(L) = %d/%d ; NON-min max-cut nonmin_fail(L) = %d/%d ; max ell=5 multiplicity on gmin = %d"
          % (gmin_fail, gmin_checked, nonmin_fail, nonmin_checked, max_lam5_gmin))
    if ex_nonmin:
        print("  non-min (L)-violating max cut: N=%d g6=%s maxLOAD=%s lam5=%d  => Gamma-minimality IS essential for (L)" % ex_nonmin)


if __name__ == '__main__':
    main()
