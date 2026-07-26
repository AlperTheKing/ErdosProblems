"""TASK 2 (step 5) -- WHICH graphs does Theorem E settle unconditionally, and what is
the exact residual region?

!!! RETRACTED CRITERION -- READ THIS FIRST !!!
`e_covered` below implements the criterion "BAD_i = 0 for SOME i", which I first believed
implied psi <= 1/25 for every x.  IT DOES NOT (see R9_thmD.md section 5.2): BAD_{i0}=0 only
gives psi <= y_{i0} y_{i0+1}, and the AM-GM bound 1/25 is available only at the MINIMISING i.
Witness: y = (1/6,1/4,1/6,1/4,1/6) has min over any four cuts = 1/24 > 1/25.
The census printed by this file is therefore NOT a list of settled graphs.  The file is kept
only because `blowups_from_C5`, `admissible` and `hom_exists` are the search primitives reused
by R9_thmD_maxbound.py and R9_thmD_thmE2.py.  The CORRECT unconditional criterion is
BAD_i = 0 for ALL i, i.e. a homomorphism H -> C5.

A triangle-free H is "E-COVERED" if it has a complete induced C5-blow-up B, an
assignment m(.) of the outside vertices W to classes (legal by E1), and a cut i,
with BAD_i = 0.  Then  psi(H,x) <= 1/25  for EVERY x -- the conjecture is proved
outright for that graph, at every weighting.

BAD_i = 0 is a graph-homomorphism condition: the W-W edges must map into
   ALLOW_i = {distance-1 pairs} u {the distance-2 pair centred at i}
                                u {the distance-2 pair centred at i+1}
(no W-W edge inside a class, no distance-2 W-W edge centred elsewhere).
"""
import sys, itertools
from fractions import Fraction as Fr
import R9_thmD_lib as L


def allowed_pairs(i):
    P = set()
    for m in range(5):
        P.add(frozenset({m, (m + 1) % 5}))          # distance 1: always fine
    P.add(frozenset({(i - 1) % 5, (i + 1) % 5}))    # distance 2 centred at i
    P.add(frozenset({i, (i + 2) % 5}))              # distance 2 centred at i+1
    return P


ALLOW = [allowed_pairs(i) for i in range(5)]


def admissible(G, cls):
    """E1: for each v outside B, the classes m with N(v) cap B subset V_{m-1} u V_{m+1}."""
    n, adj = G
    inB = {v: m for m in range(5) for v in cls[m]}
    out = {}
    for v in range(n):
        if v in inB:
            continue
        nb = {inB[w] for w in adj[v] if w in inB}
        out[v] = [m for m in range(5) if nb <= {(m - 1) % 5, (m + 1) % 5}]
    return out


def hom_exists(G, cls, adm, i):
    """backtracking: is there an assignment W -> Z5 (within adm) with BAD_i = 0?"""
    n, adj = G
    inB = {v: m for m in range(5) for v in cls[m]}
    W = [v for v in range(n) if v not in inB]
    if any(not adm[v] for v in W):
        return None
    W.sort(key=lambda v: len(adm[v]))
    A = ALLOW[i]
    asg = {}

    def bt(k):
        if k == len(W):
            return True
        v = W[k]
        for m in adm[v]:
            ok = True
            for u in adj[v]:
                if u in asg:
                    if frozenset({m, asg[u]}) not in A:
                        ok = False
                        break
            if ok:
                asg[v] = m
                if bt(k + 1):
                    return True
                del asg[v]
        return False
    return dict(asg) if bt(0) else None


def blowups_from_C5(G, C, maxsub=4096):
    """all complete induced C5-blow-ups whose class m contains c_m:
    V_m = {c_m} u S_m with S_m subset T_m and complete bipartite between consecutive S."""
    n, adj = G
    T, R, Rj, Rnone = L.classify(G, C)
    if Rj is None:
        return
    yield [[c] for c in C]                       # the plain pentagon
    tot = 1
    for k in range(5):
        tot *= (1 << len(T[k]))
    if tot > maxsub or tot == 1:
        return
    for choice in itertools.product(*[list(itertools.chain.from_iterable(
            itertools.combinations(T[m], r) for r in range(len(T[m]) + 1))) for m in range(5)]):
        if all(len(s) == 0 for s in choice):
            continue
        ok = True
        for m in range(5):
            for u in choice[m]:
                for w in choice[(m + 1) % 5]:
                    if w not in adj[u]:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                break
        if ok:
            yield [[C[m]] + list(choice[m]) for m in range(5)]


def e_covered(G, deep=True):
    """returns (covered?, witness) where witness = (classes, cut i, assignment)."""
    for C in L.induced_C5s(G):
        for cls in (blowups_from_C5(G, C) if deep else [[[c] for c in C]]):
            adm = admissible(G, cls)
            for i in range(5):
                a = hom_exists(G, cls, adm, i)
                if a is not None:
                    return True, (cls, i, a)
    return False, None


def read_g6(path, limit=None):
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(L.parse_graph6(line))
            if limit and len(out) >= limit:
                break
    return out


if __name__ == '__main__':
    print("=" * 78)
    print("N. E-COVERAGE of the named graphs  (covered => psi <= 1/25 proved for ALL x)")
    print("=" * 78)
    N = L.named_graphs()
    N['And(6)=G17'] = L.andrasfai(6)
    N['And(7)=G20'] = L.andrasfai(7)
    N['C5[2,1,1,1,1]'] = L.blowup([2, 1, 1, 1, 1])[0]
    for name, G in N.items():
        if not L.induced_C5s(G):
            print("  %-18s n=%2d : no induced C5 (odd girth >= 7) -- OUT OF SCOPE" % (name, G[0]))
            continue
        cov, wit = e_covered(G)
        extra = ""
        if cov:
            cls, i, a = wit
            extra = "cut %d, classes %s" % (i, [sorted(c) for c in cls])
        print("  %-18s n=%2d : %s  %s" % (name, G[0], "COVERED" if cov else "not covered", extra))

    print("=" * 78)
    print("O. E-COVERAGE census over catalogues of triangle-free graphs")
    print("=" * 78)
    import os
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    cats = [('connected tf n=7', 'round8/R8_tf7.g6', None),
            ('connected tf n=8', 'round8/R8_tf8.g6', None),
            ('connected tf n=9', 'round7/audit_tf9.g6', None),
            ('connected tf n=10', 'round7/tf10.g6', None),
            ('maximal tf n=11', 'round7/mtf11.g6', None),
            ('maximal tf n=12', 'round7/mtf12.g6', None),
            ('maximal tf n=13', 'round7/mtf13.g6', None),
            ('maximal tf n=14', 'round7/mtf14.g6', None)]
    for label, rel, lim in cats:
        p = os.path.join(base, rel)
        if not os.path.exists(p):
            print("  %-20s : file missing (%s)" % (label, rel))
            continue
        gs = read_g6(p, lim)
        withc5 = cov = 0
        notcov = []
        for G in gs:
            if not L.is_triangle_free(G):
                continue
            if not L.induced_C5s(G):
                continue
            withc5 += 1
            c, w = e_covered(G)
            if c:
                cov += 1
            elif len(notcov) < 4:
                notcov.append(L.to_graph6(G))
        print("  %-20s : %5d graphs, %5d with an induced C5, %5d E-COVERED (%.1f%%)"
              % (label, len(gs), withc5, cov, 100.0 * cov / max(withc5, 1)))
        if notcov:
            print("       first uncovered: %s" % ", ".join(notcov))
