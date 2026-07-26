"""Does the master inequality settle a given graph for EVERY x?

maxbound(H) = max over x of  MB(H,x),
MB(H,x)     = min over (admissible 5-partition P, cut i) of ( y_i y_{i+1} + BAD_i ).

MB(H,x) >= psi(H,x) always.  H is settled by the master inequality iff maxbound <= 1/25.
Adversarial hill-climbing on the exact integer grid, seeded from every C5-concentration,
every blow-up weighting, and random points.
"""
import itertools, random, sys
from fractions import Fraction as Fr
import R9_thmD_lib as L
import R9_thmD_coverage as CV
from R9_thmD_thmE2 import part_bound


def partitions_of(G):
    """all admissible 5-partitions coming from a complete induced C5-blow-up."""
    n, adj = G
    out = []
    seen = set()
    for C in L.induced_C5s(G):
        for cls in CV.blowups_from_C5(G, C):
            adm = CV.admissible(G, cls)
            inB = {v: m for m in range(5) for v in cls[m]}
            W = [v for v in range(n) if v not in inB]
            if any(not adm[v] for v in W):
                continue
            for combo in itertools.product(*[adm[v] for v in W]):
                cls_of = dict(inB)
                cls_of.update(dict(zip(W, combo)))
                key = tuple(cls_of[v] for v in range(n))
                if key not in seen:
                    seen.add(key)
                    out.append(cls_of)
    return out


def MB(G, a, parts):
    best = None
    for P in parts:
        b, per, y = part_bound(G, a, P)
        if best is None or b < best:
            best = b
    return best


def maximise(G, name, q, starts=60, seed=0):
    n = G[0]
    parts = partitions_of(G)
    if not parts:
        print("  %-14s : no admissible partition" % name)
        return
    rnd = random.Random(seed)
    inits = []
    for C in L.induced_C5s(G):                      # mandatory C5-concentrations
        a = [0] * n
        for c in C:
            a[c] = q // 5
        a[C[0]] += q - sum(a)
        inits.append(a)
    for P in parts:                                  # every blow-up weighting
        a = [0] * n
        for m in range(5):
            vs = [v for v in range(n) if P[v] == m]
            if vs:
                a[vs[0]] = q // 5
        a[0] += q - sum(a)
        if min(a) >= 0:
            inits.append(a)
    for _ in range(starts):
        cuts = sorted(rnd.randrange(q + 1) for _ in range(n - 1))
        a = [b - aa for aa, b in zip([0] + cuts, cuts + [q])]
        rnd.shuffle(a)
        inits.append(a)
    best = None
    for a0 in inits:
        a = list(a0)
        cur = MB(G, a, parts)
        improved = True
        while improved:
            improved = False
            for u in range(n):
                if a[u] == 0:
                    continue
                for v in range(n):
                    if u == v:
                        continue
                    a[u] -= 1; a[v] += 1
                    val = MB(G, a, parts)
                    if val > cur:
                        cur = val; improved = True
                    else:
                        a[u] += 1; a[v] -= 1
        if best is None or cur > best[0]:
            best = (cur, list(a))
    val, a = best
    psi = L.psi_int(G, a)
    print("  %-14s q=%3d parts=%4d : maxbound = %s = %.6f  %s   at a=%s (psi=%s)"
          % (name, q, len(parts), Fr(val, q * q), float(Fr(val, q * q)),
             "<= 1/25  SETTLED" if 25 * val <= q * q else "> 1/25  NOT settled",
             a, Fr(psi, q * q)))
    return Fr(val, q * q), a


if __name__ == '__main__':
    N = L.named_graphs()
    print("=" * 78)
    print("V. Can the master inequality settle these graphs for EVERY x?")
    print("=" * 78)
    # first: the hand-built adversarial point for Wagner
    G = N['Wagner=And(3)']
    parts = partitions_of(G)
    a = [33, 12, 0, 0, 12, 0, 21, 21]
    q = sum(a)
    print("  hand-built Wagner point a=%s (q=%d): MB = %s = %.5f, psi = %s"
          % (a, q, Fr(MB(G, a, parts), q * q), float(Fr(MB(G, a, parts), q * q)),
             Fr(L.psi_int(G, a), q * q)))
    print()
    for name, q in [('Wagner=And(3)', 30), ('Wagner=And(3)', 45), ('C5', 25),
                    ('C5[2]', 20), ('And(4)=G11', 20), ('Petersen', 20),
                    ('Grotzsch', 15), ('C5[2,2,1,1,1]', 20)]:
        maximise(N[name], name, q, starts=40, seed=3)
