r"""VERIFY the proof-attack workflow's central reduction (2026-07-08): m*Q <= T^2 for ell=5 atom subsets.

The ell5-expansion-attack workflow (wf_82f1381a-8a5) reduced the open Ell5SupportExpansion (|E_short(S)| >= |S|) LOSSLESSLY
(Cauchy-Schwarz) to the single scalar inequality, for every subset S of ell=5 atoms of a K2-component:
    m * Q <= T^2 ,    where m=|S|,  T = sum_{e in S} |P_e| = sum_c d(c),  Q = sum_c d(c)^2,  d(c)=#{e in S : c in P_e}.
Reason: T^2 = (sum_c d(c))^2 <= |E_short(S)| * Q  (Cauchy-Schwarz), so |E_short(S)| >= T^2/Q; hence m*Q<=T^2 => |E_short(S)|>=m.
The per-atom strengthening L2:  g(e) := sum_{c in P_e} d(c) <= (T/m) |P_e|  sums to m*Q<=T^2 (since sum_e g(e)=Q, sum_e (T/m)|P_e| = T^2/m).
Workflow claims: m*Q<=T^2 holds on all realizable instances with ~2.29x margin (max L2 ratio 7/16); a 14-atom abstract
sunflower gives m*Q>T^2 (so girth+max-cut ESSENTIAL, the inequality is NOT set-theoretically automatic).

This gate EXACT-verifies m*Q<=T^2 and L2 over ell=5 atom subsets of triangle-free Gamma-min MAX-cut components
(census N<=11 + C5[t]): full atom set per component, plus ALL subsets for components with <=12 ell=5 atoms. Reports the
tightest margin T^2/(m*Q) and max L2 ratio g(e)*m/(T*|P_e|). If m*Q<=T^2 holds everywhere => the workflow's reduction
target is VALID and is the clean open lemma. If it FAILS on a real component => the reduction is refuted (falsifier).
EXACT rational. Run from problems/23/writeup.
"""
import subprocess
from fractions import Fraction as F
from itertools import combinations
from _claude_residual_hall_gate import residuals, k2_components
from _claude_shortrow_hall_v2_gate import all_shortest_geodesic_cut_edges, c5_blowup
from _codex_k2t_switch_probe import adj_from_edges
from _h import dec, maxcut_all, Bconn, GENG, gmin


def check_subset(Sedges, Pe):
    """m*Q<=T^2 ? plus max L2 ratio. Returns (ok, ratio_T2_over_mQ:F, maxL2ratio:F, hall_ok)."""
    dc = {}
    for e in Sedges:
        for c in Pe[e]:
            dc[c] = dc.get(c, 0) + 1
    m = len(Sedges)
    T = sum(len(Pe[e]) for e in Sedges)   # = sum_c d(c)
    Q = sum(d * d for d in dc.values())
    Eshort = len(dc)
    ok = m * Q <= T * T
    ratio = F(T * T, m * Q) if m * Q > 0 else F(10 ** 9)
    # per-atom L2 max ratio g(e)*m / (T*|P_e|)
    maxL2 = F(0)
    for e in Sedges:
        g = sum(dc[c] for c in Pe[e])
        r = F(g * m, T * len(Pe[e])) if T * len(Pe[e]) > 0 else F(0)
        if r > maxL2:
            maxL2 = r
    return ok, ratio, maxL2, (Eshort >= m)


def analyze(name, n, adj, side, acc):
    if not Bconn(n, adj, side):
        return
    cd = residuals(n, adj, side)
    if cd is None or not cd['ell']:
        return
    ell = cd['ell']
    for X in k2_components(n, cd):
        five = [e for e in X['atoms'] if ell[e] == 5]
        if len(five) < 1:
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
        subsets = []
        if len(five) <= 12:
            for r in range(1, len(five) + 1):
                subsets.extend(combinations(five, r))
        else:
            subsets = [tuple(five)]  # just the full set for large comps
        for S in subsets:
            okq, ratio, l2, hall = check_subset(list(S), Pe)
            acc['checks'] += 1
            if not hall:
                acc['hall_fail'] += 1
            if not okq:
                acc['mq_fail'] += 1
                if acc['mq_ex'] is None:
                    acc['mq_ex'] = (name, n, [ell[e] for e in S], str(ratio))
            else:
                if ratio < acc['min_ratio'][0]:
                    acc['min_ratio'] = (ratio, name, n, len(S))
            if l2 > acc['max_l2'][0]:
                acc['max_l2'] = (l2, name, n, len(S))


def main():
    print("VERIFY m*Q <= T^2 (workflow's lossless Cauchy-Schwarz reduction of Ell5SupportExpansion).")
    print("=" * 96)
    acc = dict(comps=0, checks=0, mq_fail=0, hall_fail=0,
               min_ratio=(F(10 ** 9), '', 0, 0), max_l2=(F(0), '', 0, 0), mq_ex=None)
    for nn in range(8, 12):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); adj = adj_from_edges(n, E)
            b = gmin(n, adj, maxcut_all(n, adj))
            if b is None:
                continue
            analyze('cen%d' % nn, n, adj, b[0], acc)
        mr = acc['min_ratio']; ml = acc['max_l2']
        print("  census N=%d: comps %d, subset-checks %d | m*Q>T^2 fails %d | Hall fails %d | min T^2/(mQ)=%s ~%.4f | max L2 ratio=%s ~%.4f"
              % (nn, acc['comps'], acc['checks'], acc['mq_fail'], acc['hall_fail'],
                 mr[0], float(mr[0]), ml[0], float(ml[0])), flush=True)
    for t in range(1, 8):
        n, adj, side = c5_blowup(t)
        analyze('C5[%d]' % t, n, adj, side, acc)
    print("=" * 96)
    mr = acc['min_ratio']; ml = acc['max_l2']
    print("TOTAL comps %d, subset-checks %d" % (acc['comps'], acc['checks']))
    print("m*Q <= T^2 FAILURES: %d | Hall (|E_short|>=|S|) FAILURES: %d" % (acc['mq_fail'], acc['hall_fail']))
    print("tightest margin  T^2/(m*Q) = %s ~ %.5f  @ %s N=%d |S|=%d  (>=1 needed)" % (mr[0], float(mr[0]), mr[1], mr[2], mr[3]))
    print("max per-atom L2 ratio g(e)m/(T|P_e|) = %s ~ %.5f  @ %s N=%d |S|=%d  (<=1 needed; workflow claims 7/16)"
          % (ml[0], float(ml[0]), ml[1], ml[2], ml[3]))
    if acc['mq_ex']:
        print("  *** m*Q > T^2 FAILURE (refutes the reduction): %s ***" % (acc['mq_ex'],))
    print("VERDICT: %s" % (
        "m*Q <= T^2 HOLDS on ALL %d subset-checks (tightest margin %.4f >= 1; max L2 ratio %.4f <= 1) -- the workflow's"
        " lossless Cauchy-Schwarz reduction is VALIDATED: Ell5SupportExpansion follows from m*Q<=T^2 (equiv. per-atom L2),"
        " a clean scalar inequality with real slack. This is the sharp open lemma to prove from girth+max-cut."
        % (acc['checks'], float(mr[0]), float(ml[0])) if acc['mq_fail'] == 0 else
        "*** m*Q > T^2 on %d subset-checks -- the reduction is REFUTED on real components; Cauchy-Schwarz is too lossy"
        " there (Hall still holds via the true |E_short|). Report Hall-fail=%d (should be 0). ***"
        % (acc['mq_fail'], acc['hall_fail'])))


if __name__ == '__main__':
    main()
