"""ROOT-AGENT probe (Claude, round 3): Lasserre relaxation of max_x psi(H,x) in EPIGRAPH form.

Instead of bisecting a feasibility problem (numerically fragile: Round 2 and my first level-3 run
both hit inaccurate/failed statuses), lift the epigraph variable into the polynomial problem:

        maximise  t   subject to   q_S(x) - t >= 0 for every cut S,  x >= 0,  sum x = 1,  0 <= t <= 1/4.

The objective is now LINEAR, so the level-d moment relaxation is a single SDP whose optimal value is
an upper bound on max_x psi(H,x), decreasing in d.  Truth on C5 is exactly 1/25 = 0.04; Round 2
recorded 0.0552786 at level 1 and 0.053170 at level 2 for the bisection form.

Usage: claude_lasserre_epi.py <graph> <level>
"""
import sys
import itertools
import numpy as np
import cvxpy as cp


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
        return 8, sorted({(min(v, w), max(v, w)) for v in range(8) for w in ((v + 1) % 8, (v + 4) % 8)})
    if name == 'petersen':
        return 10, sorted({(min(a, b), max(a, b)) for a, b in
                           [(i, (i + 1) % 5) for i in range(5)] + [(i, 5 + i) for i in range(5)] +
                           [(5 + i, 5 + (i + 2) % 5) for i in range(5)]})
    raise SystemExit('unknown graph ' + name)


def cutlist(n, E):
    return [[(u, v) for (u, v) in E if ((((m << 1) | 1) >> u) & 1) == ((((m << 1) | 1) >> v) & 1)]
            for m in range(1 << (n - 1))]


def solve(name, level):
    n, E = graph(name)
    cuts = cutlist(n, E)
    N = n + 1                      # variables: x_0..x_{n-1} and t (index n)
    B = monomials(N, level)
    Bl = monomials(N, level - 1)
    print(f"{name}: n={n} |E|={len(E)} cuts={len(cuts)} level={level} "
          f"moment basis {len(B)} localizing basis {len(Bl)}")

    need = set()
    for a in B:
        for b in B:
            need.add(tuple(np.add(a, b)))
    shifts = [tuple([0] * N)]
    for i in range(N):
        e = [0] * N; e[i] = 1
        shifts.append(tuple(e))
    for (u, v) in [(u, v) for (u, v) in E]:
        e = [0] * N; e[u] += 1; e[v] += 1
        shifts.append(tuple(e))
    for a in Bl:
        for b in Bl:
            ab = tuple(np.add(a, b))
            for s in shifts:
                need.add(tuple(np.add(ab, s)))
    for a in monomials(N, 2 * level - 1):
        need.add(a)
        for i in range(n):
            e = [0] * N; e[i] = 1
            need.add(tuple(np.add(a, e)))
    allmon = sorted(need)
    idx = {a: i for i, a in enumerate(allmon)}
    y = cp.Variable(len(allmon))
    ZERO = tuple([0] * N)
    cons = [y[idx[ZERO]] == 1]

    cons.append(cp.bmat([[y[idx[tuple(np.add(a, b))]] for b in B] for a in B]) >> 0)

    def loc(coeffs):
        """localizing matrix for the polynomial sum coeff * x^shift"""
        rows = []
        for a in Bl:
            row = []
            for b in Bl:
                ab = tuple(np.add(a, b))
                expr = 0
                for (co, sh) in coeffs:
                    expr = expr + co * y[idx[tuple(np.add(ab, sh))]]
                row.append(expr)
            rows.append(row)
        return cp.bmat(rows)

    et = [0] * N; et[n] = 1; et = tuple(et)
    for mono in cuts:
        co = [(-1.0, et)]
        for (u, v) in mono:
            e = [0] * N; e[u] += 1; e[v] += 1
            co.append((1.0, tuple(e)))
        cons.append(loc(co) >> 0)
    for i in range(n):
        e = [0] * N; e[i] = 1
        cons.append(loc([(1.0, tuple(e))]) >> 0)
    cons.append(loc([(1.0, et)]) >> 0)                      # t >= 0
    cons.append(loc([(0.25, ZERO), (-1.0, et)]) >> 0)       # t <= 1/4

    for a in monomials(N, 2 * level - 1):
        expr = 0
        for i in range(n):
            e = [0] * N; e[i] = 1
            expr = expr + y[idx[tuple(np.add(a, e))]]
        cons.append(expr == y[idx[a]])

    prob = cp.Problem(cp.Maximize(y[idx[et]]), cons)
    for solver in (cp.SCS, cp.CLARABEL):
        try:
            prob.solve(solver=solver, verbose=False,
                       **({'max_iters': 200000, 'eps': 1e-9} if solver is cp.SCS else {}))
            print(f"   solver {solver}: status {prob.status}  value {prob.value}")
            if prob.value is not None and prob.status in ('optimal', 'optimal_inaccurate'):
                print(f"   >>> level-{level} upper bound on max_x psi({name}) = {prob.value:.8f}"
                      f"   (truth on C5 = 0.04000000)")
        except Exception as ex:
            print(f"   solver {solver} failed: {ex}")


if __name__ == '__main__':
    solve(sys.argv[1] if len(sys.argv) > 1 else 'C5',
          int(sys.argv[2]) if len(sys.argv) > 2 else 2)
