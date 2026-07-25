"""Sound partial symmetry breaking for graph search in CP-SAT.

Fix the pair order  (0,1),(0,2),...,(0,n-1),(1,2),...,(n-2,n-1)  and let A(G) be the
0/1 vector of that graph in that order.  The lexicographically largest A over all
relabellings satisfies  A >=_lex A^pi  for EVERY permutation pi.  Hence imposing that
inequality for any chosen SET of permutations keeps at least one representative of
every isomorphism class: the constraints are sound symmetry breaking, never lose a
solution up to isomorphism.

sym1 : the n-1 adjacent transpositions, encoded as a single linear inequality between
       the binary numbers formed by rows i and i+1 with columns i,i+1 deleted
       (Codish-Miller-Prosser-Stuckey).
sym2 : ALL C(n,2) transpositions, encoded with an explicit lexicographic chain.
       Every auxiliary variable is functionally determined by the edge variables, so
       the encoding is safe under `enumerate_all_solutions`.
"""

from itertools import combinations


def pair_order(n):
    return list(combinations(range(n), 2))


def add_sym1(model, x, idx, n):
    for i in range(n - 1):
        cols = [k for k in range(n) if k != i and k != i + 1]
        L = len(cols)
        terms = []
        for p, k in enumerate(cols):
            c = 1 << (L - 1 - p)
            terms.append(c * x[idx[(min(i, k), max(i, k))]])
            terms.append(-c * x[idx[(min(i + 1, k), max(i + 1, k))]])
        model.Add(sum(terms) >= 0)


def _lex_geq(model, a, b):
    """post a >=_lex b for equal-length lists of BoolVars, with determined aux vars."""
    L = len(a)
    if L == 0:
        return
    # e[p] == "a and b agree on positions 0..p-1"
    e = [None] * (L + 1)
    for p in range(L):
        if p == 0:
            # e[0] is the constant true: constraint is  a0 >= b0
            model.AddBoolOr([a[0], b[0].Not()])
        else:
            model.AddBoolOr([e[p].Not(), a[p], b[p].Not()])
        if p == L - 1:
            break
        ep1 = model.NewBoolVar("")
        if p == 0:
            #  e1 <=> (a0 <=> b0)
            model.AddBoolOr([ep1.Not(), a[0].Not(), b[0]])
            model.AddBoolOr([ep1.Not(), a[0], b[0].Not()])
            model.AddBoolOr([ep1, a[0], b[0]])
            model.AddBoolOr([ep1, a[0].Not(), b[0].Not()])
        else:
            model.AddImplication(ep1, e[p])
            model.AddBoolOr([ep1.Not(), a[p].Not(), b[p]])
            model.AddBoolOr([ep1.Not(), a[p], b[p].Not()])
            model.AddBoolOr([ep1, e[p].Not(), a[p], b[p]])
            model.AddBoolOr([ep1, e[p].Not(), a[p].Not(), b[p].Not()])
        e[p + 1] = ep1


def add_sym2(model, x, idx, n, transpositions=None):
    """A >=_lex A^tau for every transposition tau (or a given subset)."""
    pairs = pair_order(n)
    if transpositions is None:
        transpositions = list(combinations(range(n), 2))
    for (i, j) in transpositions:
        def tau(v):
            return j if v == i else (i if v == j else v)
        a, b = [], []
        for (u, v) in pairs:
            uu, vv = tau(u), tau(v)
            if uu > vv:
                uu, vv = vv, uu
            if (uu, vv) == (u, v):
                continue
            a.append(x[idx[(u, v)]])
            b.append(x[idx[(uu, vv)]])
        _lex_geq(model, a, b)
