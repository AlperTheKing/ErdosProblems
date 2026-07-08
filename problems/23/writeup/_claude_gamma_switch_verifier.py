r"""Gamma-DECREASING SWITCH verifier (2026-07-08): infrastructure for gap#1's final lemma
NoReducedOverdoorFullSupportMultiShell (option 1 -- a reduced Gamma-min OVER-door full-support shell admits a
zero-slack Gamma-decreasing switch, contradicting Gamma-minimality).

Given a triangle-free graph (adj), a cut (side), and a flip set W, computes EXACTLY (integers/Fraction):
  cut_before, cut_after (# cut edges under side vs side XOR W),
  Gamma_before, Gamma_after (sum_e ell(e)^2 over bad edges of each cut, ell = shortest cut-geodesic length),
  Delta_cut = cut_after - cut_before,  Delta_Gamma = Gamma_after - Gamma_before.
A valid Gamma-decreasing zero-slack switch: Delta_cut >= 0 (stays a max cut -- for a MAX cut before, >=0 means still max)
AND Delta_Gamma < 0. Its existence on an over-door shell CONTRADICTS Gamma-minimality => the over-door shell is not Gamma-min.

Also: brute-force / structured search for such a W on a given over-door full-support shell (single-vertex, edge, and
small subset flips), to empirically confirm option 1 before/independent of GPT-Pro's explicit W. Run from problems/23/writeup.
"""
from fractions import Fraction as F
from itertools import combinations
from _claude_residual_hall_gate import residuals
from _codex_k2t_switch_probe import adj_from_edges
from _h import maxcut_all, gmin, Bconn


def cutval(n, adj, side):
    return sum(1 for a in range(n) for b in adj[a] if a < b and side[a] != side[b])


def gamma_of(n, adj, side):
    """Gamma = sum over bad edges of ell^2 (ell = shortest cut-geodesic length). None if a bad edge has no cut path."""
    cd = residuals(n, adj, side)
    if cd is None:
        return None
    return sum(cd['ell'][e] ** 2 for e in cd['M'])


def flip(side, W):
    s = side[:]
    for v in W:
        s[v] = 1 - s[v]
    return s


def eval_switch(n, adj, side, W):
    s2 = flip(side, W)
    g1 = gamma_of(n, adj, side)
    g2 = gamma_of(n, adj, s2)
    c1 = cutval(n, adj, side)
    c2 = cutval(n, adj, s2)
    return dict(cut_before=c1, cut_after=c2, dcut=c2 - c1,
                gamma_before=g1, gamma_after=g2,
                dgamma=(None if (g1 is None or g2 is None) else g2 - g1))


def search_switch(n, adj, side, max_flip=2):
    """Search for a Gamma-decreasing zero-slack switch (dcut>=0, dgamma<0) with |W|<=max_flip."""
    g1 = gamma_of(n, adj, side)
    if g1 is None:
        return None
    for k in range(1, max_flip + 1):
        for W in combinations(range(n), k):
            r = eval_switch(n, adj, side, W)
            if r['dcut'] >= 0 and r['dgamma'] is not None and r['dgamma'] < 0:
                return dict(W=W, **r)
    return None


def selfcheck():
    """Sanity: on an ODD CYCLE (single-atom, Gamma-min-rigid) there is NO Gamma-decreasing zero-slack switch."""
    n = 9
    E = [(i, (i + 1) % n) for i in range(n)]
    adj = adj_from_edges(n, E)
    side = [i % 2 for i in range(n)]
    g = gamma_of(n, adj, side)
    r = search_switch(n, adj, side, max_flip=2)
    ok = (g == 81) and (r is None)  # C_9: Gamma=81, no improving switch (rigid)
    print("SELFCHECK C_9: Gamma=%s (expect 81), Gamma-decreasing switch found=%s (expect None) -> %s"
          % (g, r, "PASS" if ok else "FAIL"))
    return ok


def main():
    print("=" * 90)
    print("GAMMA-DECREASING SWITCH VERIFIER -- infrastructure for gap#1 final lemma (option 1)")
    print("=" * 90)
    selfcheck()
    print()
    # Demo: figure-8 of two odd cycles sharing a vertex (a small reducible over-ish shell) -- is it Gamma-min?
    def fig8(a, b):
        n = 2 * a + 2 * b + 1
        EA = [(i, i + 1) for i in range(2 * a)] + [(2 * a, 0)]
        off = 2 * a + 1
        EB = [(0, off)] + [(off + i, off + i + 1) for i in range(2 * b - 1)] + [(off + 2 * b - 1, 0)]
        return n, adj_from_edges(n, EA + EB)
    for (a, b) in [(2, 2), (2, 3), (3, 3)]:
        n, adj = fig8(a, b)
        best = gmin(n, adj, maxcut_all(n, adj))
        if best is None:
            print("  fig8(%d,%d): no Gamma-min B-conn cage" % (2 * a + 1, 2 * b + 1)); continue
        side = best[0]
        g = gamma_of(n, adj, side)
        r = search_switch(n, adj, side, max_flip=2)
        print("  fig8(%d,%d) N=%d Gamma-min cut: Gamma=%s, cut=%d, |W|<=2 Gamma-decreasing switch=%s"
              % (2 * a + 1, 2 * b + 1, n, g, cutval(n, adj, side), (r['W'] if r else None)))
    print("\nVerifier ready: call eval_switch(n,adj,side,W) with GPT-Pro's explicit flip set W to check Delta_Gamma<0, Delta_cut>=0.")


if __name__ == '__main__':
    main()
