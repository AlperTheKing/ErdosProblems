"""audit_P3_equality.py -- audit of P3.md (c)'s equality-census claim:

  "on Grotzsch at q = 10 there are 15 Aut-orbits of weightings with psi exactly 1/25, of supports
   up to 7 vertices (they are exactly the weightings whose support maps onto C5 with each fibre
   carrying mass q/5 -- C5-quotient weightings, the blow-up extremals)"

Independent: my own construction, my own exhaustive weighting enumeration, my own max-cut, and an
explicit test of the C5-quotient property (partition of the support into 5 non-empty classes, each
of mass q/5, whose quotient is a 5-cycle and which is a graph homomorphism onto it).
"""
from fractions import Fraction as F
from itertools import combinations, product
from audit_P3_core import vega_family, bip_exact

fam = {nm: (adj, order, w) for (nm, adj, order, w) in vega_family(2)}


def compositions(n, q):
    if n == 1:
        yield (q,)
        return
    for t in range(q + 1):
        for rest in compositions(n - 1, q - t):
            yield (t,) + rest


def is_c5_quotient(order, adj, a, q):
    """support partitions into 5 classes of mass q/5 forming a C5, with all edges between
       cyclically consecutive classes only (i.e. a homomorphism onto C5 that is edge-surjective
       in the blow-up sense)."""
    sup = [t for t in order if a[t] > 0]
    if len(sup) < 5 or q % 5:
        return False
    target = q // 5
    # brute force over assignments of support vertices to 5 classes (up to rotation: fix sup[0]->0)
    for assign in product(range(5), repeat=len(sup) - 1):
        cls = (0,) + assign
        mass = [0] * 5
        for k, t in enumerate(sup):
            mass[cls[k]] += a[t]
        if any(mm != target for mm in mass):
            continue
        ok = True
        for p, r in combinations(range(len(sup)), 2):
            e = sup[r] in adj[sup[p]]
            d = (cls[p] - cls[r]) % 5
            consec = d in (1, 4)
            if e and not consec:
                ok = False
                break
            if (not e) and consec:
                ok = False           # blow-up of C5 requires ALL cross pairs to be edges
                break
        if ok:
            return True
    return False


for gname in ('Ups_2-y-2i', 'Ups_2'):
    adj, order, _ = fam[gname]
    n = len(order)
    for q in (10,):
        eq = []
        tot = 0
        thr = q * q
        for vec in compositions(n, q):
            tot += 1
            a = dict(zip(order, vec))
            bp = bip_exact(order, adj, a)
            if 25 * bp == thr:
                eq.append(vec)
            elif 25 * bp > thr:
                print('*** ERDOS 23 VIOLATION on %s q=%d a=%s bip=%d' % (gname, q, vec, bp))
        # orbit count under Aut: use canonical form via all automorphisms read from P3_input.txt
        auts = []
        cur = None
        with open('P3_input.txt') as f:
            lines = f.read().split('\n')
        for k, line in enumerate(lines):
            if line.startswith('NAME ' + gname + ' '):
                cur = k
                break
        j = cur
        while j < len(lines) and not lines[j].startswith('AUT '):
            j += 1
        na = int(lines[j].split()[1])
        for t in range(na):
            auts.append([int(z) for z in lines[j + 1 + t].split()])
        seen = set()
        for vec in eq:
            best = min(tuple(vec[p[t]] for t in range(n)) for p in auts)
            seen.add(best)
        nsup = sorted({sum(1 for z in v if z > 0) for v in eq})
        nc5 = sum(1 for v in eq if is_c5_quotient(order, adj, dict(zip(order, v)), q))
        print('%-11s n=%2d q=%2d | weightings=%d | psi==1/25 exactly: %d (%d Aut-orbits) | '
              'support sizes %s | C5-quotient: %d of %d'
              % (gname, n, q, tot, len(eq), len(seen), nsup, nc5, len(eq)))
        if nc5 != len(eq):
            print('   *** NOT ALL equality weightings are C5-quotients -- P3.md (c) claim is FALSE ***')
            shown = 0
            for v in eq:
                if not is_c5_quotient(order, adj, dict(zip(order, v)), q):
                    print('   counterexample a =', v, ' order =', order)
                    shown += 1
                    if shown >= 5:
                        break
