"""ROOT-AGENT probe (Claude, round 3): Lasserre / moment relaxation at LEVEL 3 for

        max over the simplex of  psi(H,x) = min over cuts S of q_S(x),   q_S(x) = sum_{uv mono} x_u x_v.

Round 2 recorded: level 1 gives 0.0552786 and level 2 gives 0.053170 on C5, whose true value is
0.04 exactly.  A relaxation is useful only if it can certify <= 1/25 on C5 itself, so level 3 is the
next thing to test before the whole moment/SOS family is declared dead.

Formulation (standard).  Feasibility at threshold t:  does there exist a probability measure mu on
{x >= 0, sum x = 1} with q_S(x) >= t for every cut S?  Relaxation at level d: moment vector y over
monomials of degree <= 2d with
    M_d(y) >= 0                                        (moment matrix)
    L_{q_S - t}(y) >= 0  for every cut S               (localizing, order d-1)
    L_{x_i}(y) >= 0      for every i                   (localizing, order d-1)
    y_alpha = sum_i y_{alpha + e_i}   for |alpha| <= 2d-1     (the identity sum x = 1)
    y_0 = 1.
If infeasible, then max_x psi(H,x) < t  is CERTIFIED (upper bound).  Bisection on t.

Exactness note: this is a numerical SDP, so it can only ever point the way; any accepted claim would
need an exactly verified rational dual.  Its purpose here is to decide whether the moment route is
worth exact work at all.
"""
import sys
import itertools
import numpy as np

try:
    import cvxpy as cp
except Exception as e:                                    # pragma: no cover
    print("cvxpy unavailable:", e)
    sys.exit(2)


def monomials(n, deg):
    out = []
    for d in range(deg + 1):
        for c in itertools.combinations_with_replacement(range(n), d):
            a = [0] * n
            for i in c:
                a[i] += 1
            out.append(tuple(a))
    return out


def graph(name):
    if name == 'C5':
        return 5, [(i, (i + 1) % 5) for i in range(5)]
    if name == 'C7':
        return 7, [(i, (i + 1) % 7) for i in range(7)]
    if name == 'wagner':
        return 8, sorted({(min(v, w), max(v, w)) for v in range(8)
                          for w in ((v + 1) % 8, (v + 4) % 8)})
    raise SystemExit("unknown graph")


def cuts(n, E):
    out = []
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        out.append([(u, v) for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1)])
    return out


def relax_feasible(n, E, level, t, solver_verbose=False):
    B = monomials(n, level)                     # moment matrix basis, degree <= level
    Bl = monomials(n, level - 1)                # localizing basis
    allmon = sorted({tuple(np.add(a, b)) for a in B for b in B} |
                    {tuple(np.add(np.add(a, b), e)) for a in Bl for b in Bl
                     for e in monomials(n, 2)})
    idx = {a: i for i, a in enumerate(allmon)}
    y = cp.Variable(len(allmon))

    cons = [y[idx[tuple([0] * n)]] == 1]

    # moment matrix
    M = cp.bmat([[y[idx[tuple(np.add(a, b))]] for b in B] for a in B])
    cons.append(M >> 0)

    # localizing for each cut:  q_S - t >= 0
    for mono in cuts(n, E):
        rows = []
        for a in Bl:
            row = []
            for b in Bl:
                ab = tuple(np.add(a, b))
                expr = -t * y[idx[ab]]
                for (u, v) in mono:
                    e = [0] * n; e[u] += 1; e[v] += 1
                    expr = expr + y[idx[tuple(np.add(ab, e))]]
                row.append(expr)
            rows.append(row)
        cons.append(cp.bmat(rows) >> 0)

    # localizing for x_i >= 0
    for i in range(n):
        rows = []
        for a in Bl:
            row = []
            for b in Bl:
                e = [0] * n; e[i] = 1
                row.append(y[idx[tuple(np.add(np.add(a, b), e))]])
            rows.append(row)
        cons.append(cp.bmat(rows) >> 0)

    # sum x = 1 propagated to moments
    for a in monomials(n, 2 * level - 1):
        expr = 0
        for i in range(n):
            e = [0] * n; e[i] = 1
            expr = expr + y[idx[tuple(np.add(a, e))]]
        cons.append(expr == y[idx[a]])

    prob = cp.Problem(cp.Minimize(0), cons)
    try:
        prob.solve(solver=cp.SCS, verbose=solver_verbose, max_iters=40000, eps=1e-8)
    except Exception as ex:
        print("   solver error:", ex)
        return None
    return prob.status


if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'C5'
    level = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    n, E = graph(name)
    print(f"{name}: n={n} |E|={len(E)} cuts={1 << (n - 1)} level={level} "
          f"moment basis={len(monomials(n, level))} localizing basis={len(monomials(n, level - 1))}")
    lo, hi = 0.04, 0.09          # lo = the truth on C5, hi = a value we know is not certifiable
    # first: is the relaxation infeasible just above the truth?
    for t in (0.0401, 0.042, 0.045, 0.048, 0.052, 0.0533, 0.056):
        st = relax_feasible(n, E, level, t)
        print(f"   t = {t:.4f}  ->  {st}")
        if st is not None and 'infeasible' in str(st):
            print(f"   CERTIFIED: max_x psi < {t} at level {level}")
            break
