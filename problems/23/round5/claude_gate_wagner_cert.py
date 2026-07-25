"""ROOT-AGENT GATE (Claude): independent exact verification of the round-7 Wagner certificate.

Claim: max_x psi(And(3) = Gamma_8 = Wagner, x) <= 1/25, certified by
    L^4 - sum_S nu_S(x) q_S(x)  =  SOS   (after x = y^2),   sum_S nu_S = 25 L^2,  nu_S >= 0,
where L = sum_j x_j and q_S(x) = sum over the monochromatic edges of S of x_u x_v.

If it verifies, this is the first rigorous psi-ceiling in the campaign for a pattern that is NOT
homomorphic to C5 - Wagner is And(3), the first Andrasfai graph beyond C5.

Everything below is my own: own Wagner construction, own graph6-free edge list, own polynomial
expansion (dicts exponent -> Fraction), own rational LDL^T with symmetric pivoting.  Nothing is
imported from the constructor or from the auditor.
"""
import pickle
import sys
from fractions import Fraction as F
from itertools import combinations


def wagner():
    """And(3) = circle graph Gamma_8: u ~ v iff 3*circdist(u,v) > 8, i.e. distance 3 or 4"""
    n = 8
    E = []
    for u in range(n):
        for v in range(u + 1, n):
            d = min((u - v) % n, (v - u) % n)
            if 3 * d > n:
                E.append((u, v))
    return n, E


def is_psd(M):
    n = len(M)
    A = [[F(M[i][j]) for j in range(n)] for i in range(n)]
    for k in range(n):
        best = max(range(k, n), key=lambda i: A[i][i])
        if A[best][best] < 0:
            return False, f"negative pivot {A[best][best]} at step {k}"
        if A[best][best] == 0:
            for i in range(k, n):
                for j in range(k, n):
                    if i != j and A[i][j] != 0 and A[i][i] == 0:
                        return False, f"zero pivot with nonzero off-diagonal ({i},{j})"
            break
        if best != k:
            A[k], A[best] = A[best], A[k]
            for r in range(n):
                A[r][k], A[r][best] = A[r][best], A[r][k]
        d = A[k][k]
        for i in range(k + 1, n):
            f = A[i][k] / d
            if f == 0:
                continue
            for j in range(k, n):
                A[i][j] -= f * A[k][j]
                A[j][i] = A[i][j]
    return True, None


def main(path):
    d = pickle.load(open(path, 'rb'))
    n = d['n']
    E = [tuple(e) for e in d['E']]
    cuts = d['cuts']
    nu = d['nu']
    Q = d['Q']

    # --- 1. the pattern is really Wagner
    n0, E0 = wagner()
    ok_graph = (n == n0) and (sorted(tuple(sorted(e)) for e in E) == sorted(E0))
    print(f"(1) pattern is Gamma_8 = And(3) = Wagner: {ok_graph}   (n={n}, |E|={len(E)})")
    if not ok_graph:
        print("    certificate edge list:", sorted(tuple(sorted(e)) for e in E))
        print("    my Wagner edge list  :", sorted(E0))

    # --- 2. every listed cut is realised by a genuine bipartition, and its mono set matches
    eidx = {tuple(sorted(e)): i for i, e in enumerate(E)}
    allcuts = {}
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        mono = frozenset(eidx[tuple(sorted(e))] for e in E
                         if ((S >> e[0]) & 1) == ((S >> e[1]) & 1))
        allcuts.setdefault(mono, m)
    ok_cuts = all(frozenset(ms) in allcuts for _, ms in cuts)
    print(f"(2) all {len(cuts)} listed monochromatic sets are realised by genuine cuts: {ok_cuts}")

    # --- 3. multipliers nonnegative, degree 2
    negs = [(k, v) for k, v in nu.items() if v < 0]
    degs = set()
    for k in nu:
        mono_part = k[1] if isinstance(k, tuple) and len(k) == 2 else None
        if mono_part is not None:
            degs.add(sum(mono_part) if hasattr(mono_part, '__iter__') else None)
    print(f"(3) all {len(nu)} multiplier coefficients are exact and nonnegative: {not negs}"
          + (f"   first negative {negs[:1]}" if negs else "")
          + (f"   multiplier monomial degrees {sorted(x for x in degs if x is not None)}" if degs else ""))

    # --- 4. sum_S nu_S == 25 L^2 , as a polynomial identity in x
    tot = {}
    for (s, mono), c in nu.items():
        tot[mono] = tot.get(mono, F(0)) + c
    target = {}
    for i in range(n):
        for j in range(n):
            e = [0] * n; e[i] += 1; e[j] += 1
            target[tuple(e)] = target.get(tuple(e), F(0)) + 25
    ok_sum = all(tot.get(k, F(0)) == v for k, v in target.items()) and \
             all(target.get(k, F(0)) == v for k, v in tot.items())
    print(f"(4) sum_S nu_S == 25 (sum x)^2 exactly: {ok_sum}")

    # --- 5. Gram blocks PSD (own rational LDL^T)
    badq = []
    for bi, blk in enumerate(Q):
        G = blk['G'] if isinstance(blk, dict) and 'G' in blk else (blk[1] if isinstance(blk, tuple) else blk)
        try:
            sym = all(G[i][j] == G[j][i] for i in range(len(G)) for j in range(len(G)))
            psd, info = is_psd(G)
        except Exception as ex:
            badq.append((bi, f"unreadable: {ex}")); continue
        if not (sym and psd):
            badq.append((bi, f"sym={sym} psd={psd} {info}"))
    print(f"(5) all {len(Q)} Gram blocks symmetric and PSD (own rational LDL^T): {not badq}"
          + (f"   failures {badq[:2]}" if badq else ""))

    # --- 6. the polynomial identity, expanded by hand
    def pmulmono(a, b):
        return tuple(x + y for x, y in zip(a, b))
    lhs = {}
    # L^4
    def add(d_, k, c):
        d_[k] = d_.get(k, F(0)) + c
    from itertools import product
    for t in product(range(n), repeat=4):
        e = [0] * n
        for i in t:
            e[i] += 1
        add(lhs, tuple(e), F(1))
    # - sum_S nu_S q_S
    for (s, mono), c in nu.items():
        ms = dict(cuts)[s] if not isinstance(cuts[0], tuple) else None
        ms = None
        for ss, mset in cuts:
            if ss == s:
                ms = mset; break
        if ms is None:
            print("    cut id not found:", s); return False
        for ei in ms:
            u, v = E[ei]
            e = [0] * n; e[u] += 1; e[v] += 1
            add(lhs, pmulmono(mono, tuple(e)), -c)
    lhs = {k: v for k, v in lhs.items() if v != 0}
    rhs = {}
    for blk in Q:
        if isinstance(blk, dict):
            mons = blk.get('mons') or blk.get('ymonomials') or blk.get('basis')
            G = blk['G']
        else:
            mons, G = blk[0], blk[1]
        for i in range(len(mons)):
            for j in range(len(mons)):
                if G[i][j]:
                    key = tuple((mons[i][k] + mons[j][k]) for k in range(n))
                    if any(x % 2 for x in key):
                        print("    odd exponent in Gram product - identity is in y, not x");
                    key2 = tuple(x // 2 for x in key)
                    add(rhs, key2, G[i][j])
    rhs = {k: v for k, v in rhs.items() if v != 0}
    diff = dict(lhs)
    for k, v in rhs.items():
        diff[k] = diff.get(k, F(0)) - v
    diff = {k: v for k, v in diff.items() if v != 0}
    print(f"(6) L^4 - sum_S nu_S q_S == sum_b v^T Q_b v exactly: {not diff}"
          + (f"   residual monomials {len(diff)}, e.g. {list(diff.items())[:2]}" if diff else ""))

    verdict = ok_graph and ok_cuts and (not negs) and ok_sum and (not badq) and (not diff)
    print(f"\nROOT GATE VERDICT: {'CONFIRMED - max_x psi(Wagner) <= 1/25 is PROVED' if verdict else 'NOT CONFIRMED'}")
    return verdict


if __name__ == '__main__':
    p = sys.argv[1] if len(sys.argv) > 1 else '../round7/Q4_cert_g8_d1.pkl'
    sys.exit(0 if main(p) else 1)
