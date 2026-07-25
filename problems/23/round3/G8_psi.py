"""G8: psi(H,x) = min over cuts S of H of sum_{uv monochromatic} x_u x_v, on the simplex.

Exact rational evaluation + numerical global maximisation (multistart SLSQP on the
epigraph form) for Andrasfai graphs.  Numerics only GUIDE; every reported value is
re-derived exactly with Fractions.
"""
import itertools, sys
from fractions import Fraction
import numpy as np
from G8_graphs import andrasfai


def all_cuts(n, edges):
    """Return list of (mask, mono_edge_list). Cuts up to complement: vertex 0 fixed side 0."""
    out = []
    for mask in range(1 << (n - 1)):
        side = [0] * n
        for v in range(1, n):
            side[v] = (mask >> (v - 1)) & 1
        mono = [(u, v) for (u, v) in edges if side[u] == side[v]]
        out.append((mask, mono))
    return out


def psi_exact(cuts, x):
    """x: sequence of Fractions (or ints). Returns min over cuts of mono weight (exact)."""
    best = None
    for _, mono in cuts:
        s = 0
        for (u, v) in mono:
            s += x[u] * x[v]
            if best is not None and s > best:
                break
        if best is None or s < best:
            best = s
    return best


def psi_np(cuts_arr, x):
    """cuts_arr: list of (idx_u array, idx_v array). float."""
    vals = [float(np.dot(x[a], x[b])) for (a, b) in cuts_arr]
    return min(vals)


def build_np(cuts):
    out = []
    for _, mono in cuts:
        if mono:
            a = np.array([e[0] for e in mono], dtype=int)
            b = np.array([e[1] for e in mono], dtype=int)
        else:
            a = np.zeros(0, dtype=int); b = np.zeros(0, dtype=int)
        out.append((a, b))
    return out


def maximise(n, cuts, ntrial=400, seed=0):
    from scipy.optimize import minimize
    ca = build_np(cuts)
    # constraint functions
    def negobj(z):
        return -z[n]
    def negobj_grad(z):
        g = np.zeros(n + 1); g[n] = -1.0; return g
    cons = []
    for (a, b) in ca:
        def f(z, a=a, b=b):
            return float(np.dot(z[a], z[b])) - z[n]
        def fj(z, a=a, b=b):
            g = np.zeros(n + 1)
            np.add.at(g, a, z[b])
            np.add.at(g, b, z[a])
            g[n] = -1.0
            return g
        cons.append({'type': 'ineq', 'fun': f, 'jac': fj})
    cons.append({'type': 'eq', 'fun': lambda z: float(np.sum(z[:n]) - 1.0),
                 'jac': lambda z: np.concatenate([np.ones(n), [0.0]])})
    bnds = [(0.0, 1.0)] * n + [(0.0, 1.0)]
    rng = np.random.default_rng(seed)
    best = (-1.0, None)
    for t in range(ntrial):
        x0 = rng.dirichlet(np.ones(n) * rng.uniform(0.2, 3.0))
        z0 = np.concatenate([x0, [psi_np(ca, x0)]])
        try:
            r = minimize(negobj, z0, jac=negobj_grad, constraints=cons, bounds=bnds,
                         method='SLSQP', options={'maxiter': 400, 'ftol': 1e-14})
        except Exception:
            continue
        x = np.clip(r.x[:n], 0, None)
        s = x.sum()
        if s <= 0:
            continue
        x = x / s
        val = psi_np(ca, x)
        if val > best[0]:
            best = (val, x.copy())
    return best


if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    ntrial = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    n, conn, adj, edges = andrasfai(k)
    cuts = all_cuts(n, edges)
    print(f"And({k}) n={n} |E|={len(edges)} #cuts={len(cuts)}")
    sizes = sorted(set(len(m) for _, m in cuts))
    print("mono-set sizes present:", sizes[:10], " min =", sizes[0])
    mins = [ (mask,m) for mask,m in cuts if len(m)==sizes[0] ]
    print(f"#cuts with minimum mono size {sizes[0]}: {len(mins)}; example mono {mins[0][1]}")

    # exact value at the uniform point
    xu = [Fraction(1, n)] * n
    print("psi(uniform) =", psi_exact(cuts, xu), "  1/25 =", Fraction(1, 25))

    # exact value at an induced C5 point: find an induced C5
    C5 = None
    for S in itertools.combinations(range(n), 5):
        sub = [(u, v) for (u, v) in edges if u in S and v in S]
        if len(sub) != 5:
            continue
        deg = {v: 0 for v in S}
        for (u, v) in sub:
            deg[u] += 1; deg[v] += 1
        if all(d == 2 for d in deg.values()):
            C5 = S; break
    print("induced C5:", C5)
    xc = [Fraction(0)] * n
    for v in C5:
        xc[v] = Fraction(1, 5)
    print("psi(C5-uniform) =", psi_exact(cuts, xc))

    val, x = maximise(n, cuts, ntrial=ntrial)
    print("numeric max psi =", val, " (1/25 = 0.04)")
    print("argmax ~", np.round(x, 6))
