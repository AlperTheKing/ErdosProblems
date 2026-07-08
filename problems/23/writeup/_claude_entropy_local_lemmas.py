r"""LOCAL sufficient-condition probe for mQ<=T^2 (=> |E_short(S)|>=|S|).

For a fixed atom set S (we test the FULL ell=5 atom set of each K2-component, the natural hard case):
  r_e=|P_e|, T=sum r_e, m=|S|, rbar=T/m, d(c)=#atoms through c,
  g(e)=sum_{c in P_e} d(c) = sum_f |P_e cap P_f|  (total co-incidence of e).
Candidate LOCAL lemmas (each SUFFICIENT for a piece of mQ<=T^2):
  (L1)  d(c) <= |P_e|            for every incidence (e,c)          [pure local]
  (L2)  g(e) <= rbar * r_e       for every atom e   ==> mQ<=T^2     [per-atom, SUFFICIENT]
  (L3)  g(e) <= r_e^2            (weaker, = "avg congestion <= own support"); insufficient alone
We report worst-case violation ratios of L1,L2 over all components; if L2 holds (ratio<=1) with slack,
it is the crisp per-atom target for a girth-based proof.
EXACT rational arithmetic. Run from problems/23/writeup.
"""
import subprocess
from fractions import Fraction
from _claude_residual_hall_gate import residuals, k2_components
from _claude_shortrow_hall_v2_gate import all_shortest_geodesic_cut_edges, c5_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def analyze(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    cd = residuals(n, adj, side)
    if cd is None or not cd['ell']:
        return
    ell = cd['ell']
    for X in k2_components(n, cd):
        five = [e for e in X['atoms'] if ell[e] == 5]
        if len(five) < 2:
            continue
        Pe = {}
        ok = True
        for e in five:
            p = all_shortest_geodesic_cut_edges(n, adj, side, e[0], e[1])
            if not p:
                ok = False; break
            Pe[e] = set(p)
        if not ok:
            continue
        acc['comps'] += 1
        m = len(five)
        dc = {}
        for e in five:
            for c in Pe[e]:
                dc[c] = dc.get(c, 0) + 1
        T = sum(len(Pe[e]) for e in five)
        rbar = Fraction(T, m)
        # L1
        for e in five:
            re = len(Pe[e])
            for c in Pe[e]:
                ratio = Fraction(dc[c], re)
                if ratio > acc['L1max'][0]:
                    acc['L1max'] = (ratio, name, dc[c], re)
        # L2 and L3
        for e in five:
            re = len(Pe[e])
            g = sum(dc[c] for c in Pe[e])
            r2 = Fraction(g, rbar * re)   # want <=1 for L2
            if r2 > acc['L2max'][0]:
                acc['L2max'] = (r2, name, g, re, float(rbar))
            r3 = Fraction(g, re * re)
            if r3 > acc['L3max'][0]:
                acc['L3max'] = (r3, name, g, re)


def main():
    print("LOCAL sufficient-condition probe for mQ<=T^2 (full ell=5 atom set per component).")
    print("=" * 100)
    acc = dict(comps=0, L1max=(Fraction(0), '', 0, 0),
               L2max=(Fraction(0), '', 0, 0, 0.0), L3max=(Fraction(0), '', 0, 0))
    for nn in range(8, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            b = gmin(n, adj, maxcut_all(n, adj))
            if b is None:
                continue
            analyze('cen%d' % nn, n, adj, b[0], acc)
        print("  census N=%d: comps=%d  L1max=%.3f  L2max=%.3f  L3max=%.3f"
              % (nn, acc['comps'], float(acc['L1max'][0]), float(acc['L2max'][0]), float(acc['L3max'][0])), flush=True)
    for t in range(1, 10):
        n, adj, side = c5_blowup(t)
        analyze('C5[%d]' % t, n, adj, side, acc)
    print("  after C5[t<=9]: comps=%d  L1max=%.3f  L2max=%.3f  L3max=%.3f"
          % (acc['comps'], float(acc['L1max'][0]), float(acc['L2max'][0]), float(acc['L3max'][0])), flush=True)
    print("=" * 100)
    print("L1  max d(c)/|P_e| = %s = %.4f  (%s; d=%d, |P_e|=%d)   [L1 holds iff <=1]"
          % (acc['L1max'][0], float(acc['L1max'][0]), acc['L1max'][1], acc['L1max'][2], acc['L1max'][3]))
    print("L2  max g(e)/(rbar*|P_e|) = %s = %.4f  (%s; g=%d, |P_e|=%d, rbar=%.2f)   [L2 holds iff <=1 => mQ<=T^2]"
          % (acc['L2max'][0], float(acc['L2max'][0]), acc['L2max'][1], acc['L2max'][2], acc['L2max'][3], acc['L2max'][4]))
    print("L3  max g(e)/|P_e|^2 = %s = %.4f  (%s)   [not sufficient alone]"
          % (acc['L3max'][0], float(acc['L3max'][0]), acc['L3max'][1]))
    print("VERDICT L1:", "HOLDS" if acc['L1max'][0] <= 1 else "FALSE")
    print("VERDICT L2 (per-atom sufficient for mQ<=T^2):", "HOLDS with slack" if acc['L2max'][0] <= 1 else "FALSE -> L2 not the right target")


if __name__ == '__main__':
    main()
