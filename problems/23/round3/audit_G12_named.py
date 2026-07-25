"""AUDIT G12 / step 1: the named graphs of the report, all exact, all independent.

Checks
  * the 4 supplied "extremal" graph6 strings: N, |E|, degrees, triangle-freeness,
    girth, bip (exhaustive cut enumeration), and nu* with an exactly verified
    primal packing + dual cover certificate pair.
  * OK5 and S3(K5) rebuilt from scratch.
  * C5[n] closed-form certificate pair re-derived.
  * Petersen, Clebsch.
"""
from fractions import Fraction as Fr
import audit_G12_core as A

EXTREMAL = ["K?ABBBwerwBw", "K?BD@g]Qvo^?", "L??ED@_~?~^_Fw", "M?AE@bH{AYN_LgBs?"]


def five_cycle_columns(n, E):
    return [es for vs, es in A.simple_cycles(n, E, maxlen=5, only_odd=True)
            if len(vs) == 5]


def hdr(t):
    print("=" * 76)
    print(t)
    print("=" * 76)


def report_graph(name, n, E, full_dual=True):
    m = len(E)
    tf = A.triangle_free(n, E)
    d = A.degrees(n, E)
    b = A.bip(n, E)
    g = A.girth(n, E)
    print(f"{name}: N={n} |E|={m} tri-free={tf} girth={g} "
          f"deg-multiset={sorted(d)}")
    print(f"   bip = {b}   N^2/25 = {Fr(n*n,25)}   bip/N^2 = {Fr(b,n*n)}   |E|/5 = {Fr(m,5)}")
    # --- nu* : lower bound from 5-cycle columns, upper bound from uniform 1/5 ---
    cols = five_cycle_columns(n, E)
    odd = [es for _, es in A.simple_cycles(n, E, only_odd=True)]
    res = A.nu_star_certified(n, E, columns=cols, dual_check_cycles=odd)
    lower = res["lower"]
    unif = [Fr(1, 5)] * m
    unif_ok = A.check_cover(n, E, unif, odd)
    print(f"   #odd cycles = {len(odd)}, #5-cycles = {len(cols)}")
    print(f"   packing over 5-cycles only (exact, feasibility re-checked): {lower}")
    print(f"   uniform x=1/5 is a feasible cover: {unif_ok}  -> tau* <= {Fr(m,5)}")
    if unif_ok and lower == Fr(m, 5):
        print(f"   ==> nu* = tau* = {Fr(m,5)} EXACT (primal=dual)")
        nu = Fr(m, 5)
    else:
        res2 = A.nu_star_certified(n, E)          # full LP over all odd cycles
        nu = res2["value"]
        print(f"   full odd-cycle LP: nu* = {nu} (dual verified on all {len(odd)} odd cycles)")
    print(f"   bip - nu* = {Fr(b) - nu}   gap bip/nu* = {Fr(b)/nu if nu else '-'}")
    return dict(n=n, m=m, bip=b, nu=nu, tf=tf, girth=g)


def main():
    hdr("A. the four supplied 'extremal' graph6 strings")
    res = {}
    for s in EXTREMAL:
        res[s] = report_graph(s, *A.g6(s))
        print()

    hdr("B. OK5 rebuilt from scratch (K5, subdivide 01,23,24,34 into paths of length 3)")
    K5E = [(i, j) for i in range(5) for j in range(i + 1, 5)]
    sub = {(0, 1), (2, 3), (2, 4), (3, 4)}
    E, nxt = [], 5
    for (u, v) in K5E:
        if (u, v) in sub:
            E += [(u, nxt), (nxt, nxt + 1), (nxt + 1, v)]
            nxt += 2
        else:
            E.append((u, v))
    n = nxt
    E = sorted(tuple(sorted(e)) for e in E)
    print("   edges:", E)
    r = report_graph("OK5", n, E)
    # explicit transversal claimed by the report
    mids = [e for e in E if e[0] >= 5 and e[1] >= 5]
    rem = [e for e in E if e not in mids]
    print(f"   claimed transversal (middle edges) {mids}: bipartite remainder = "
          f"{A.is_bipartite(n, rem)}  size {len(mids)}")
    print()

    hdr("C. K5 itself and S3(K5)")
    n5, E5 = 5, K5E
    r5 = A.nu_star_certified(n5, E5)
    print(f"   K5: bip={A.bip(n5,E5)} nu*={r5['value']} (all {r5['n_odd']} odd cycles)")
    E, nxt = [], 5
    for (u, v) in K5E:
        E += [(u, nxt), (nxt, nxt + 1), (nxt + 1, v)]
        nxt += 2
    E = sorted(tuple(sorted(e)) for e in E)
    n = nxt
    print(f"   S3(K5): N={n} |E|={len(E)} tri-free={A.triangle_free(n,E)} girth={A.girth(n,E)}")
    rr = A.nu_star_certified(n, E)
    print(f"   S3(K5): nu* = {rr['value']} over {rr['n_odd']} odd cycles")
    mids = [e for e in E if e[0] >= 5 and e[1] >= 5]
    # transversal = middle edges of the paths replacing 01,23,24,34
    want = []
    order = [(u, v) for (u, v) in K5E]
    for i, (u, v) in enumerate(order):
        if (u, v) in sub:
            want.append((5 + 2 * i, 6 + 2 * i))
    rem = [e for e in E if e not in want]
    print(f"   transversal {want} -> bipartite remainder = {A.is_bipartite(n, rem)}")
    print()

    hdr("D. C5[n] closed-form certificate pair, n = 1..4 (exact)")
    for k in range(1, 5):
        N, E = A.blowup(*C5PAIR, [k] * 5)
        m = len(E)
        assert m == 5 * k * k
        # dual x = 1/5
        odd = [es for _, es in A.simple_cycles(N, E, only_odd=True)] if N <= 10 else None
        ok = A.check_cover(N, E, [Fr(1, 5)] * m, odd) if odd is not None else "skipped(size)"
        # primal: 1/k^3 on each transversal 5-cycle -> load check by counting
        ei = {}
        for i, (u, v) in enumerate(E):
            ei[(u, v)] = i
            ei[(v, u)] = i
        load = [Fr(0)] * m
        cnt = 0
        import itertools
        for ch in itertools.product(range(k), repeat=5):
            vs = [i * k + ch[i] for i in range(5)]
            for t in range(5):
                load[ei[(vs[t], vs[(t + 1) % 5])]] += Fr(1, k ** 3)
            cnt += 1
        print(f"   n={k}: N={N} |E|={m}  #transversal 5-cycles={cnt}={k**5}  "
              f"all edge loads == 1: {all(t == 1 for t in load)}  primal value = "
              f"{Fr(cnt, k**3)}  dual value = {Fr(m,5)}  uniform-cover feasible: {ok}")
    print()

    hdr("E. Petersen and Clebsch")
    P = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 5), (1, 6), (2, 7), (3, 8), (4, 9),
         (5, 7), (7, 9), (9, 6), (6, 8), (8, 5)]
    report_graph("Petersen", 10, P)
    S = [1, 2, 4, 8, 15]
    CE = sorted({tuple(sorted((u, u ^ s))) for u in range(16) for s in S})
    n, E = 16, CE
    d = A.degrees(n, E)
    print(f"   Clebsch: N=16 |E|={len(E)} tri-free={A.triangle_free(n,E)} "
          f"girth={A.girth(n,E)} degs={set(d)}")
    print(f"   Clebsch bip = {A.bip(n,E)} (accepted fact: 8)")
    # M1 and M2 for Clebsch
    a = [set() for _ in range(16)]
    for u, v in E:
        a[u].add(v)
        a[v].add(u)
    M1 = min(sum(1 for (p, q) in E if p not in a[v] and q not in a[v]) for v in range(16))
    best = 0
    for S2 in range(1 << 16):
        vs = [i for i in range(16) if (S2 >> i) & 1]
        ok = all(q not in a[p] for p, q in ((vs[i], vs[j]) for i in range(len(vs))
                                            for j in range(i + 1, len(vs))))
        if ok:
            t = sum(d[i] for i in vs)
            if t > best:
                best = t
    print(f"   Clebsch M1 = {M1}, M2 = {len(E)-best} (report: 15), N^2/25 = {Fr(256,25)}")


C5PAIR = A.C5

if __name__ == "__main__":
    main()
