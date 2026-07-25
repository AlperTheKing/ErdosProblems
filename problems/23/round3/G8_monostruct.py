"""G8: structure of the monochromatic edge sets of all cuts of And(k), and the
exact obstruction to the AM-GM (product-of-two-linear-forms) certificate.

For a cut S let mono(S) be its monochromatic edge set and define
  c(S) = min { (sum_v l_v)(sum_v l'_v) : l,l' >= 0,  l_u l'_v + l_v l'_u >= 1
               for every uv in mono(S) }.
Then q_S(x) <= L(x) L'(x) with L = sum l_v x_v, L' = sum l'_v x_v, and
c(S) is the cheapest such product bound.

LEMMA (proved in the report): c(S) >= nu(mono(S))^2, where nu = maximum matching,
by Cauchy-Schwarz.  Also c(S) = m for a star with m edges.

NECESSARY CONDITION for an AM-GM certificate of  max psi <= 1/25  on an n-vertex
graph: evaluating the chain at x = uniform gives
      n^{-2} prod_j (lambda_j lambda'_j)^{w_j} <= 1/25,
so some cut must satisfy c(S) <= n^2/25.
"""
import sys, itertools
from fractions import Fraction
from G8_graphs import andrasfai


def max_matching(edges):
    """max matching of a small graph, brute force over edge subsets (greedy + BB)."""
    best = 0
    m = len(edges)
    def rec(i, used, cur):
        nonlocal best
        if cur + (m - i) <= best:
            return
        if i == m:
            best = max(best, cur)
            return
        u, v = edges[i]
        if u not in used and v not in used:
            rec(i + 1, used | {u, v}, cur + 1)
        rec(i + 1, used, cur)
    rec(0, frozenset(), 0)
    return best


def is_star(edges):
    if not edges:
        return None
    vs = set()
    for e in edges:
        vs |= set(e)
    for c in vs:
        if all(c in e for e in edges):
            return c
    return None


def c_of_cut(edges):
    """exact c(S) for the shapes that actually occur: star -> #edges; else use nu^2
    as a certified LOWER bound and a numeric GP for the value."""
    if not edges:
        return Fraction(0), 'empty'
    ctr = is_star(edges)
    if ctr is not None:
        return Fraction(len(edges)), f'star(center={ctr},m={len(edges)})'
    nu = max_matching(edges)
    return Fraction(nu * nu), f'nu={nu} (lower bound nu^2)'


if __name__ == "__main__":
    for k in (2, 3, 4, 5):
        n, conn, adj, edges = andrasfai(k)
        target = Fraction(n * n, 25)
        best = None
        histo = {}
        stars = []
        for mask in range(1 << (n - 1)):
            side = [0] * n
            for v in range(1, n):
                side[v] = (mask >> (v - 1)) & 1
            mono = [(u, v) for (u, v) in edges if side[u] == side[v]]
            if not mono:
                continue
            nu = max_matching(mono)
            ctr = is_star(mono)
            key = (len(mono), nu, ctr is not None)
            histo[key] = histo.get(key, 0) + 1
            lb = Fraction(len(mono)) if ctr is not None else Fraction(nu * nu)
            if best is None or lb < best[0]:
                best = (lb, mask, mono, nu, ctr)
            if ctr is not None:
                stars.append((len(mono), mask, mono, ctr))
        print(f"And({k}) n={n}: n^2/25 = {target} = {float(target):.4f}")
        print(f"   cheapest cut lower bound c(S) >= {best[0]} = {float(best[0]):.4f}"
              f"   mono={best[2]}  nu={best[3]} star_center={best[4]}")
        stars.sort()
        print(f"   #cuts whose mono set is a STAR: {len(stars)}"
              + (f"; smallest star has {stars[0][0]} edges: {stars[0][2]}" if stars else ""))
        verdict = ("AM-GM product certificate POSSIBLE (necessary condition met)"
                   if best[0] <= target else
                   "AM-GM product certificate IMPOSSIBLE: every cut has c(S) > n^2/25")
        print("   =>", verdict)
        sizes = sorted(set(kk[0] for kk in histo))
        print("   |mono| sizes:", sizes[:8], "...")
        for s in sizes[:3]:
            sub = {kk: vv for kk, vv in histo.items() if kk[0] == s}
            print(f"      |mono|={s}: " + ", ".join(f"nu={kk[1]},star={kk[2]}: {vv} cuts"
                                                    for kk, vv in sorted(sub.items())))
        sys.stdout.flush()
