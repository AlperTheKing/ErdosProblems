r"""MULTI-ATOM LONG-SHARED-GEODESIC CONGESTION PROBE v2 (2026-07-08). Decisive test of the reframed gap#1 crux.

FINDING: min achievable MAX cut-edge load L* is maximized at SINGLE-atom odd cycles C_ell (L*=ell^2/(ell-1) -> 25 as
ell -> 23.96); multi-atom blow-ups C5[t] stay at 6.25. IF multi-atom congestion is ALWAYS dominated by the single-atom
envelope, gap#1's spreading-Hall follows from the Lean-proven single-atom lemma (ell^2<=25(ell-1)) alone.

WORST CASE for that: THETA GRAPHS Theta(a,b,c) -- two hubs u,v joined by 3 internally-disjoint paths of lengths a,b,c.
Odd cycles have lengths a+b, a+c, b+c. Choose a odd-ish so exactly TWO of these are odd and SHARE the long path P_a.
The two atoms (bad edges) then have geodesics BOTH forced through P_a's cut edges -- MAXIMAL sharing, FEW parallel
geodesics -> the highest possible multi-atom congestion. N = a+b+c-1 is SMALL (=ell+1 for b=c=2), so long atoms (ell up
to ~21) are reachable with brute-force max cut at N<=24. Triangle-free requires every path length >=2.

For each valid theta: find the Gamma-min MAXIMUM cut (maxcut_all+gmin, brute), verify triangle-free + B-connected,
decompose into K2-components, compute per multi-atom component the min achievable MAX cut-edge load L* (LP).
  * L* > 25  => DECISIVE: switch genuinely required OR (if beta<=N^2/25 still holds) spreading lemma FALSE there.
  * L* <= single-atom envelope ell^2/(ell-1) => multi-atom dominated by single-atom => gap#1 reduces to Lean-proven case.
  * envelope < L* <= 25 => multi-atom is a real extra obligation but bounded (switch/Hall keeps it feasible).
EXACT rational demand. Run from problems/23/writeup.
"""
import numpy as np
from fractions import Fraction as F
from scipy.optimize import linprog
from _claude_residual_hall_gate import residuals, k2_components
from _claude_shortrow_hall_v2_gate import all_shortest_geodesic_cut_edges
from _codex_k2t_switch_probe import adj_from_edges
from _h import maxcut_all, Bconn, gmin


def theta(a, b, c):
    """Theta graph: hubs 0,1 joined by 3 paths of edge-lengths a,b,c. Returns (n, adj, E)."""
    E = []
    nxt = 2
    for L in (a, b, c):
        prev = 0
        for i in range(L - 1):
            E.append((prev, nxt)); prev = nxt; nxt += 1
        E.append((prev, 1))
    return nxt, adj_from_edges(nxt, E), E


def is_triangle_free(n, adj):
    for u in range(n):
        au = set(adj[u])
        for v in adj[u]:
            if v > u and (au & set(adj[v])):
                return False
    return True


def min_max_load(n, adj, side, cd, atoms):
    ell = cd['ell']
    if any(ell[e] > 23 for e in atoms):
        return None, None, None
    Pe = {}
    for e in atoms:
        pe = all_shortest_geodesic_cut_edges(n, adj, side, e[0], e[1])
        if not pe:
            return None, None, None
        Pe[e] = pe
    cut_edges = sorted(set().union(*Pe.values()))
    ci = {c: i for i, c in enumerate(cut_edges)}
    var = [(ei, ci[c]) for ei, e in enumerate(atoms) for c in Pe[e]]
    nq = len(var); NV = nq + 1
    obj = np.zeros(NV); obj[nq] = 1.0
    A_eq = np.zeros((len(atoms), NV)); b_eq = np.zeros(len(atoms))
    for ei, e in enumerate(atoms):
        b_eq[ei] = float(ell[e] ** 2)
        for kk, (a, cc) in enumerate(var):
            if a == ei:
                A_eq[ei, kk] = 1.0
    A_ub = np.zeros((len(cut_edges), NV)); b_ub = np.zeros(len(cut_edges))
    for kk, (a, cc) in enumerate(var):
        A_ub[cc, kk] = 1.0
    for j in range(len(cut_edges)):
        A_ub[j, nq] = -1.0
    res = linprog(c=obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=[(0, None)] * NV, method='highs')
    if not res.success:
        return None, len(cut_edges), None
    return res.x[nq], len(cut_edges), [ell[e] for e in atoms]


def main():
    print("THETA-GRAPH multi-atom congestion probe (2 long odd cycles sharing the long path = worst-case sharing).")
    print("Single-atom envelope L*(C_ell)=ell^2/(ell-1); ell=23 => 529/22 = %.4f." % (529 / 22))
    print("=" * 100)
    best = (0.0, None); over_env = []; over25 = []; tested = 0; thetas = 0
    seen = set()
    for a in range(2, 22):
        for b in range(2, 6):
            for c in range(b, 6):
                n = a + b + c - 1
                if n > 24:
                    continue
                # want two odd cycles sharing P_a: a+b odd and a+c odd => b,c same parity as each other, opposite to a-part
                odds = [(a + b) % 2, (a + c) % 2, (b + c) % 2]
                if sum(1 - o for o in odds) < 2:   # need >=2 odd cycles (o==1 means odd)
                    pass
                key = (a, b, c)
                if key in seen:
                    continue
                seen.add(key)
                nn, adj, E = theta(a, b, c)
                if not is_triangle_free(nn, adj):
                    continue
                thetas += 1
                cuts = maxcut_all(nn, adj)
                bst = gmin(nn, adj, cuts)
                if bst is None:
                    continue
                side = bst[0]
                if not Bconn(nn, adj, side):
                    continue
                cd = residuals(nn, adj, side)
                if cd is None or not cd['ell']:
                    continue
                for X in k2_components(nn, cd):
                    if len(X['atoms']) < 2:
                        continue
                    L, bx, ells = min_max_load(nn, adj, side, cd, X['atoms'])
                    if L is None:
                        continue
                    tested += 1
                    me = max(ells)
                    env = me * me / (me - 1)
                    if L > best[0]:
                        best = (L, dict(theta=(a, b, c), n=nn, atoms=len(X['atoms']), ells=ells, bx=bx, env=round(env, 3)))
                    if L > env + 1e-6:
                        over_env.append(dict(theta=(a, b, c), n=nn, ells=ells, L=round(L, 4), env=round(env, 3), bx=bx))
                    if L > 25 + 1e-6:
                        over25.append(dict(theta=(a, b, c), n=nn, ells=ells, L=round(L, 4), bx=bx))
    print("theta graphs (triangle-free): %d | multi-atom components tested: %d" % (thetas, tested))
    print("MAX multi-atom min-max-load L* = %.6f  at %s" % (best[0], best[1]))
    print("=" * 100)
    if over25:
        print("*** %d multi-atom components with L* > 25 -- DECISIVE (switch-needed OR spreading-lemma falsifier): ***" % len(over25))
        for x in over25[:12]:
            print("   %s" % x)
    elif over_env:
        print("%d multi-atom components EXCEED the single-atom envelope ell^2/(ell-1) but stay <= 25:" % len(over_env))
        for x in over_env[:12]:
            print("   %s" % x)
        print("VERDICT: multi-atom sharing CAN out-congest a single long odd cycle (up to L*=%.4f<=25). The multi-atom" % best[0])
        print("  Hall is a GENUINE extra obligation (not reducible to the single-atom lemma), but stays feasible -- the")
        print("  switch/coarea is what bounds it. => the reframe does NOT collapse to the Lean-proven case; multi-atom is real.")
    else:
        print("VERDICT: NO multi-atom component exceeds the single-atom envelope ell^2/(ell-1) (max L*=%.4f)." % best[0])
        print("  => STRONG evidence multi-atom congestion is DOMINATED by single-atom odd cycles. gap#1 spreading-Hall")
        print("  would then reduce to the Lean-proven single-atom lemma; the switch/coarea would NOT be needed.")


if __name__ == '__main__':
    main()
