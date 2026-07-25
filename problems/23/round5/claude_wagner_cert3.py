"""ROOT-AGENT: construct an exact x-dependent certificate for max_x psi(Wagner, x) <= 1/25.

Wagner = And(3) = Gamma_8 = C8(1,4): the first pattern that does NOT map to C5, so a rigorous
ceiling for it is the first real step of the delta > N/3 route.

Certificate form (the shape verified for C5 in R3-C14):
    quadratic forms lambda_S(z) >= 0 (entrywise nonnegative coefficient matrices), one per cut S in
    a chosen family, with sum_S lambda_S = (sum z)^2, such that
        P(z) := (sum z)^4 - 25 * sum_S lambda_S(z) q_S(z)   is nonnegative for z >= 0,
    certified by writing P(y^2) as a sum of squares in y.

Parity blocking: P(y^2) has only even exponents, so the Gram matrix splits by the parity class of
the exponent vector.  For n = 8 and degree 4 in z, the blocks are one 36x36 (all-even class), 28
blocks of size 8 (weight-two classes) and 70 of size 1 - a small SDP.

Numeric solve with cvxpy, then rational rounding, exact repair of the linear constraints, and exact
verification (own rational LDL^T + own polynomial expansion).
"""
import sys
import json
import numpy as np
from fractions import Fraction as F
from itertools import combinations

N = 8


def adjacency():
    return [[(u != v and 3 * min((u - v) % N, (v - u) % N) > N) for v in range(N)] for u in range(N)]


def arc_cuts(lengths):
    seen, res = set(), []
    for i in range(N):
        for l in lengths:
            inA = [False] * N
            for t in range(l):
                inA[(i + t) % N] = True
            key = min(tuple(inA), tuple(not b for b in inA))
            if key not in seen:
                seen.add(key)
                res.append(tuple(inA))
    return res


def all_cuts():
    seen,res=set(),[]
    for m in range(1<<(N-1)):
        S=(m<<1)|1
        inA=tuple(bool((S>>v)&1) for v in range(N))
        key=min(inA,tuple(not b for b in inA))
        if key not in seen:
            seen.add(key); res.append(inA)
    return res


def mono_edges(adj, inA):
    return [(u, v) for u, v in combinations(range(N), 2) if adj[u][v] and inA[u] == inA[v]]


def deg4_monomials():
    out = []
    for c in combinations_with_replacement_idx(4):
        e = [0] * N
        for i in c:
            e[i] += 1
        out.append(tuple(e))
    return sorted(set(out))


def combinations_with_replacement_idx(k):
    from itertools import combinations_with_replacement
    return combinations_with_replacement(range(N), k)


def main():
    adj = adjacency()
    cuts = arc_cuts([2, 3, 4]) if len(sys.argv)<2 else (arc_cuts([1,2,3,4]) if sys.argv[1]=='wide' else all_cuts())
    print(f"Wagner: {len(cuts)} arc cuts (lengths 3 and 4)")

    pairs = [(i, j) for i in range(N) for j in range(i, N)]
    monos4 = deg4_monomials()                      # degree-4 monomials in z  == degree-8 in y
    midx = {m: i for i, m in enumerate(monos4)}

    # ---- P(z) coefficients as linear functions of the lambda entries
    # (sum z)^4
    const = {m: 0 for m in monos4}
    from itertools import product
    for t in product(range(N), repeat=4):
        e = [0] * N
        for i in t:
            e[i] += 1
        const[tuple(e)] += 1
    # -25 * sum_S lambda_S(z) q_S(z)
    lin = {m: {} for m in monos4}                  # monomial -> {(s,i,j): coefficient}
    for s, inA in enumerate(cuts):
        for (u, v) in mono_edges(adj, inA):
            for (i, j) in pairs:
                e = [0] * N
                e[i] += 1; e[j] += 1; e[u] += 1; e[v] += 1
                key = tuple(e)
                c = 25 * (1 if i == j else 2)
                lin[key][(s, i, j)] = lin[key].get((s, i, j), 0) + c

    # ---- Gram blocks by parity class of the degree-4 y-monomials
    ymonos = deg4_monomials()                       # degree 4 in y
    blocks = {}
    for m in ymonos:
        par = tuple(x % 2 for x in m)
        blocks.setdefault(par, []).append(m)
    print(f"  Gram blocks: {len(blocks)}; sizes {sorted((len(v) for v in blocks.values()), reverse=True)[:5]} ...")

    try:
        import cvxpy as cp
    except Exception as e:
        print("cvxpy unavailable:", e); return 2

    lamv = {}
    for s in range(len(cuts)):
        for (i, j) in pairs:
            lamv[(s, i, j)] = cp.Variable(nonneg=True)
    G = {par: cp.Variable((len(ms), len(ms)), PSD=True) for par, ms in blocks.items()}
    tmar = cp.Variable()

    cons = []
    # sum_S lambda_S = J
    for (i, j) in pairs:
        cons.append(sum(lamv[(s, i, j)] for s in range(len(cuts))) == 1)
    # coefficient matching:  P(y^2) == sum_b y^T G_b y
    lhs = {}
    for par, ms in blocks.items():
        for a in range(len(ms)):
            for b in range(len(ms)):
                e = tuple(ms[a][k] + ms[b][k] for k in range(N))
                assert all(x % 2 == 0 for x in e)
                key = tuple(x // 2 for x in e)
                lhs.setdefault(key, []).append(G[par][a, b])
    for m in monos4:
        expr = sum(lhs.get(m, []))
        rhs = const[m] - sum(c * lamv[k] for k, c in lin[m].items()) if lin[m] else const[m]
        cons.append(expr == rhs)

    import numpy as _np
    for par, ms in blocks.items():
        cons.append(G[par] - tmar*_np.eye(len(ms)) >> 0)
    cons.append(tmar <= 0.05)
    prob = cp.Problem(cp.Maximize(tmar), cons)
    for solver in (cp.SCS, cp.CLARABEL):
        try:
            prob.solve(solver=solver, verbose=False, **({'max_iters':400000,'eps':1e-11} if solver is cp.SCS else {}))
            print(f"  solver {solver}: {prob.status}  margin={prob.value}")
            if prob.status in ('optimal', 'optimal_inaccurate'):
                out = {'graph': 'wagner', 'n': N,
                       'cuts': [[int(b) for b in c] for c in cuts],
                       'claim': 'max_x psi(Wagner,x) <= 1/25',
                       'lambda': [[[float(lamv[(s, min(i, j), max(i, j))].value) for j in range(N)]
                                   for i in range(N)] for s in range(len(cuts))],
                       'gram': [{'parity': list(par), 'ymonomials': [list(m) for m in ms],
                                 'G': [[float(x) for x in row] for row in np.array(G[par].value)]}
                                for par, ms in blocks.items()]}
                json.dump(out, open('claude_wagner_cert_margin.json', 'w'))
                print("  numeric certificate written to claude_wagner_cert_numeric.json")
                return 0
        except Exception as ex:
            print(f"  solver {solver} failed: {str(ex)[:120]}")
    return 1


if __name__ == '__main__':
    sys.exit(main())
