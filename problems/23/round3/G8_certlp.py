"""G8: AM-GM cut certificates for max_x psi(H,x) <= 1/25.

CERTIFICATE SCHEME (new; NOT a fixed averaging certificate -- the averaging is
GEOMETRIC, so the 1/20 obstruction for arithmetic averaging on C5 does not apply).

An ATOM is a triple (S, A, B) where S is a cut of H, A and B are disjoint vertex
sets, and every monochromatic edge of S has one end in A and the other in B.
Then                q_S(x) = sum_{mono uv} x_u x_v  <=  x(A) * x(B).
Given atoms j = 1..m and weights w_j >= 0 with sum_j w_j = 1,

  psi(x) <= min_j q_{S_j}(x) <= min_j x(A_j) x(B_j)
         <= prod_j ( x(A_j) x(B_j) )^{w_j}            (min <= weighted geom mean)
          = ( prod_j x(A_j)^{w_j} ) ( prod_j x(B_j)^{w_j} )
         <= ( sum_j w_j x(A_j) ) ( sum_j w_j x(B_j) )  (weighted AM-GM, twice).

So if the weights satisfy the LINEAR system
        sum_j w_j [v in A_j] = 1/5   for every vertex v,
        sum_j w_j [v in B_j] = 1/5   for every vertex v,
        sum_j w_j = 1,   w >= 0,
then both averaged forms equal (1/5) * sum_v x_v = 1/5 on the simplex and
        psi(x) <= 1/25   for EVERY x in the simplex.       (*)

On C5 the 5 single-edge cuts with A={i}, B={i+1}, w=1/5 give exactly (*): the
scheme reproduces the sharp C5 bound, so it is not lossy at the extremal object.

This script searches for such a certificate by exact rational LP.
"""
import sys, itertools
from fractions import Fraction
import numpy as np
from G8_graphs import andrasfai


def cuts_and_atoms(n, edges, max_mono=None, max_atoms_per_cut=None):
    atoms = []          # (mask, frozenset A, frozenset B)
    for mask in range(1 << (n - 1)):
        side = [0] * n
        for v in range(1, n):
            side[v] = (mask >> (v - 1)) & 1
        mono = [(u, v) for (u, v) in edges if side[u] == side[v]]
        if not mono:
            continue                      # cannot happen for non-bipartite H
        if max_mono is not None and len(mono) > max_mono:
            continue
        # components / bipartiteness of the mono graph
        adjm = {}
        verts = set()
        for (u, v) in mono:
            adjm.setdefault(u, []).append(v)
            adjm.setdefault(v, []).append(u)
            verts.add(u); verts.add(v)
        colour = {}
        comps = []
        ok = True
        for s in sorted(verts):
            if s in colour:
                continue
            comp = [s]; colour[s] = 0; stack = [s]
            while stack:
                a = stack.pop()
                for b in adjm[a]:
                    if b not in colour:
                        colour[b] = 1 - colour[a]; comp.append(b); stack.append(b)
                    elif colour[b] == colour[a]:
                        ok = False
            comps.append(comp)
        if not ok:
            continue                      # mono graph has an odd cycle: no A x B cover
        free = [v for v in range(n) if v not in verts]
        r = len(comps)
        cnt = 0
        for signs in itertools.product([0, 1], repeat=r):
            A0, B0 = set(), set()
            for ci, comp in enumerate(comps):
                for v in comp:
                    if (colour[v] ^ signs[ci]) == 0:
                        A0.add(v)
                    else:
                        B0.add(v)
            for extra in itertools.product([0, 1, 2], repeat=len(free)):
                A = set(A0); B = set(B0)
                for v, e in zip(free, extra):
                    if e == 1:
                        A.add(v)
                    elif e == 2:
                        B.add(v)
                atoms.append((mask, frozenset(A), frozenset(B)))
                cnt += 1
                if max_atoms_per_cut and cnt >= max_atoms_per_cut:
                    break
            if max_atoms_per_cut and cnt >= max_atoms_per_cut:
                break
    # dedupe
    return sorted(set(atoms), key=lambda t: (len(t[1]) + len(t[2]), t[0]))


def solve_lp(n, atoms):
    from scipy.optimize import linprog
    m = len(atoms)
    Aeq = np.zeros((2 * n + 1, m))
    beq = np.zeros(2 * n + 1)
    for j, (mask, A, B) in enumerate(atoms):
        for v in A:
            Aeq[v, j] = 1.0
        for v in B:
            Aeq[n + v, j] = 1.0
        Aeq[2 * n, j] = 1.0
    beq[:n] = 0.2
    beq[n:2 * n] = 0.2
    beq[2 * n] = 1.0
    # minimise total atom size -> prefers small, sparse certificates
    c = np.array([len(A) + len(B) for (_, A, B) in atoms], dtype=float)
    r = linprog(c, A_eq=Aeq, b_eq=beq, bounds=[(0, None)] * m, method='highs')
    return r


def exact_verify(n, edges, atoms, idx, w):
    """w: list of Fractions for atoms[idx]. Verify the certificate exactly."""
    assert sum(w) == 1, ("sum w", sum(w))
    a_acc = [Fraction(0)] * n
    b_acc = [Fraction(0)] * n
    for j, wt in zip(idx, w):
        mask, A, B = atoms[j]
        assert wt > 0
        assert not (A & B), "A,B not disjoint"
        side = [0] * n
        for v in range(1, n):
            side[v] = (mask >> (v - 1)) & 1
        mono = [(u, v) for (u, v) in edges if side[u] == side[v]]
        for (u, v) in mono:
            assert (u in A and v in B) or (v in A and u in B), \
                f"mono edge {(u,v)} not covered by A x B for atom {j}"
        for v in A:
            a_acc[v] += wt
        for v in B:
            b_acc[v] += wt
    assert all(t == Fraction(1, 5) for t in a_acc), ("A marginals", a_acc)
    assert all(t == Fraction(1, 5) for t in b_acc), ("B marginals", b_acc)
    return True


def rationalise_and_solve(n, atoms, support):
    """Exact rational solve of the equality system restricted to `support`."""
    import sympy as sp
    m = len(support)
    rows = []
    rhs = []
    for v in range(n):
        rows.append([1 if v in atoms[j][1] else 0 for j in support]); rhs.append(sp.Rational(1, 5))
    for v in range(n):
        rows.append([1 if v in atoms[j][2] else 0 for j in support]); rhs.append(sp.Rational(1, 5))
    rows.append([1] * m); rhs.append(sp.Integer(1))
    M = sp.Matrix(rows)
    b = sp.Matrix(rhs)
    sol, params = M.gauss_jordan_solve(M.copy() * 0 + M, b) if False else (None, None)
    # use lstsq-free exact approach: solve M w = b via nullspace parametrisation
    aug = M.row_join(b)
    rref, piv = aug.rref()
    # build a particular solution with free vars = 0
    w = [sp.Integer(0)] * m
    for i, p in enumerate(piv):
        if p == m:
            return None            # inconsistent
        w[p] = rref[i, m]
    if any(wi < 0 for wi in w):
        return None
    return [Fraction(int(sp.nsimplify(wi).p), int(sp.nsimplify(wi).q)) for wi in w]


if __name__ == "__main__":
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    max_mono = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    n, conn, adj, edges = andrasfai(k)
    print(f"And({k}) n={n} |E|={len(edges)}")
    atoms = cuts_and_atoms(n, edges, max_mono=max_mono)
    print(f"atoms (cut, A, B) with |mono|<={max_mono}: {len(atoms)}")
    r = solve_lp(n, atoms)
    print("LP status:", r.status, r.message)
    if r.status != 0:
        print("NO CERTIFICATE with this atom set")
        sys.exit(0)
    supp = [j for j in range(len(atoms)) if r.x[j] > 1e-9]
    print(f"LP feasible; support size {len(supp)}")
    for j in supp:
        mask, A, B = atoms[j]
        print(f"   w={r.x[j]:.6f}  cut mask={mask:0{n}b}  A={sorted(A)}  B={sorted(B)}")
    wq = rationalise_and_solve(n, atoms, supp)
    if wq is None:
        print("exact rational solve on the LP support failed; retry with a different support")
    else:
        print("exact rational weights:", [str(x) for x in wq])
        exact_verify(n, edges, atoms, supp, wq)
        print("EXACT CERTIFICATE VERIFIED:  max_x psi(And(%d),x) <= 1/25" % k)
