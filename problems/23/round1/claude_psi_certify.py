"""RIGOROUS upper bound on  max over the simplex of  psi(H,x) = min over cuts S of
   sum_{uv monochromatic under S} x_u x_v,   by exact interval branch-and-bound.

This is the concrete open task recorded in section 3g of CLAUDE_GATE_RESULTS.md: hill-climbing
gives only LOWER bounds, and both natural fixed-multiplier certificates were shown there to be too
weak (uniform over all cuts -> 1/8; the five C5 rotation cuts -> 1/20, failing even on C5).

Method, entirely in exact rational arithmetic.
  * A region is a box [lo_i, hi_i] intersected with the simplex; it is discarded when the box
    cannot meet the simplex, i.e. when sum(lo) > 1 or sum(hi) < 1.
  * For ANY single cut S,  psi(x) <= q_S(x) = sum_{uv mono} x_u x_v <= sum_{uv mono} hi_u hi_v
    on the box. So  min over a set of cuts of that box-bound  is a valid upper bound for psi on
    the whole region. If it is <= the target, the region is certified and pruned.
  * Otherwise split the widest coordinate at its midpoint and recurse.
Termination with a full prune is a PROOF that max_x psi(H,x) <= target.

Usage: python claude_psi_certify.py <pattern> [target_num] [target_den] [max_nodes]
"""

import sys
from fractions import Fraction
from itertools import combinations


def cycle(n):
    return n, [(i, (i + 1) % n) for i in range(n)]


def petersen():
    outer = [(i, (i + 1) % 5) for i in range(5)]
    spokes = [(i, 5 + i) for i in range(5)]
    inner = [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
    return 10, outer + spokes + inner


def circulant(n, conn):
    E = set()
    for v in range(n):
        for d in conn:
            w = (v + d) % n
            E.add((min(v, w), max(v, w)))
    return n, sorted(E)


def grotzsch():
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E.append((5 + i, (i + 1) % 5))
        E.append((5 + i, (i - 1) % 5))
        E.append((10, 5 + i))
    return 11, [(min(a, b), max(a, b)) for a, b in E]


PATTERNS = {
    "C5": cycle(5),
    "C7": cycle(7),
    "C9": cycle(9),
    "petersen": petersen(),
    "wagner": circulant(8, [1, 4]),
    "c11_13": circulant(11, [1, 3]),
    "c13_15": circulant(13, [1, 5]),
    "grotzsch": grotzsch(),
}


def mono_lists(n, edges):
    """for each cut (vertex 0 fixed on one side), the list of monochromatic edges"""
    out = []
    for mask in range(1 << (n - 1)):
        S = (mask << 1) | 1
        out.append([(u, v) for (u, v) in edges
                    if ((S >> u) & 1) == ((S >> v) & 1)])
    return out


def certify(n, edges, target, max_nodes=400000):
    cuts = mono_lists(n, edges)
    # order cuts by their value at the uniform point, best (smallest) first: good cuts get tried first
    unif = Fraction(1, n)
    cuts.sort(key=lambda ml: len(ml))
    ZERO, ONE = Fraction(0), Fraction(1)

    stack = [([ZERO] * n, [ONE] * n)]
    nodes = 0
    max_lower_seen = ZERO
    while stack:
        lo, hi = stack.pop()
        nodes += 1
        if nodes > max_nodes:
            return None, nodes, max_lower_seen
        if sum(lo) > ONE or sum(hi) < ONE:
            continue                                    # box misses the simplex
        # upper bound: best (smallest) single-cut box bound
        best_ub = None
        for ml in cuts:
            ub = ZERO
            for (u, v) in ml:
                ub += hi[u] * hi[v]
                if best_ub is not None and ub > best_ub:
                    break
            if best_ub is None or ub < best_ub:
                best_ub = ub
                if best_ub <= target:
                    break
        if best_ub is not None and best_ub <= target:
            continue                                    # region certified
        # not certified: split the widest coordinate
        widths = [hi[i] - lo[i] for i in range(n)]
        w = max(widths)
        if w == 0:
            # a single point that we could not certify: evaluate it exactly
            s = sum(lo)
            if s == 0:
                continue
            x = [c / s for c in lo]
            val = min(sum(x[u] * x[v] for (u, v) in ml) for ml in cuts)
            if val > max_lower_seen:
                max_lower_seen = val
            if val > target:
                return False, nodes, val               # genuine violation of the target
            continue
        i = widths.index(w)
        mid = (lo[i] + hi[i]) / 2
        a_hi = list(hi); a_hi[i] = mid
        b_lo = list(lo); b_lo[i] = mid
        stack.append((list(lo), a_hi))
        stack.append((b_lo, list(hi)))
    return True, nodes, max_lower_seen


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "petersen"
    tn = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    td = int(sys.argv[3]) if len(sys.argv) > 3 else 25
    cap = int(sys.argv[4]) if len(sys.argv) > 4 else 400000
    n, E = PATTERNS[name]
    target = Fraction(tn, td)
    print(f"pattern={name}  n={n}  |E|={len(E)}  cuts={1 << (n - 1)}  target={target} = {float(target):.6f}")
    res, nodes, extra = certify(n, E, target, cap)
    if res is True:
        print(f"CERTIFIED: max_x psi <= {target}   (branch-and-bound closed, {nodes} nodes, exact rationals)")
    elif res is False:
        print(f"REFUTED: found a simplex point with psi = {extra} = {float(extra):.6f} > {target}")
    else:
        print(f"INCONCLUSIVE: node cap {cap} reached ({nodes} nodes); best lower bound seen {float(extra):.6f}")
