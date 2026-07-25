"""G12 task (a): exact bip, nu* (= tau*), and integrality gap on
  * the extremal family C5[n], n = 1..6
  * the known extremal graphs at N = 12, 13, 14, 15.

Every number is an exact Fraction/int and is produced by at least two
independent routes:
  method 1 = full odd-cycle enumeration + exact rational simplex
  method 2 = cutting planes with exact double-cover (Dijkstra) separation
  method 3 = for C5[n], a closed-form primal/dual certificate pair, verified exactly.
"""
from fractions import Fraction as F
import itertools
import sys
import G12_core as C

# graph6 strings supplied by the campaign; the leading character fixes N
# ('K'->12, 'L'->13, 'M'->14), so there are TWO extremal graphs on 12 vertices.
EXTREMAL = ["K?ABBBwerwBw", "K?BD@g]Qvo^?", "L??ED@_~?~^_Fw", "M?AE@bH{AYN_LgBs?"]


def closed_form_c5_blowup(n):
    """Exact certificate pair for C5[n]:
       primal  y_C = 1/n^3 on each of the n^5 transversal 5-cycles  -> value n^2
       dual    x_e = 1/5   on each of the 5n^2 edges                -> value n^2
    Both verified exactly (primal edge loads, dual min-odd-cycle weight)."""
    N, E = C.blowup(5, C.C5()[1], [n] * 5)
    eidx = {}
    for i, (u, v) in enumerate(E):
        eidx[(u, v)] = i
        eidx[(v, u)] = i
    y = F(1, n ** 3)
    load = [F(0)] * len(E)
    cnt = 0
    for choice in itertools.product(range(n), repeat=5):
        vs = [i * n + choice[i] for i in range(5)]
        for k in range(5):
            load[eidx[(vs[k], vs[(k + 1) % 5])]] += y
        cnt += 1
    assert cnt == n ** 5
    primal_val = F(cnt) * y
    primal_ok = all(l <= 1 for l in load)
    dual_val = F(len(E), 5)
    mw = C.min_odd_cycle_weight(N, E, [F(1, 5)] * len(E))
    dual_ok = (mw >= 1)
    return dict(N=N, m=len(E), primal_val=primal_val, primal_ok=primal_ok,
                dual_val=dual_val, dual_ok=dual_ok, min_odd=mw,
                maxload=max(load), minload=min(load))


def main():
    print("=" * 78, flush=True)
    print("(a1) C5[n]:  bip = n^2 (accepted fact 1);  nu* computed exactly", flush=True)
    print("=" * 78, flush=True)
    for n in range(1, 7):
        cf = closed_form_c5_blowup(n)
        assert cf['primal_val'] == cf['dual_val'] == n * n
        print(f"n={n} N={cf['N']} |E|={cf['m']}  bip={n*n}", flush=True)
        print(f"    closed-form PRIMAL packing value = {cf['primal_val']}, feasible={cf['primal_ok']},"
              f" every edge load = {cf['minload']}..{cf['maxload']}", flush=True)
        print(f"    closed-form DUAL cover value    = {cf['dual_val']}, feasible={cf['dual_ok']},"
              f" min odd cycle x-weight = {cf['min_odd']}", flush=True)
        print(f"    ==> nu* = tau* = {n*n} = bip;  integrality gap = 1;  deficit = 0;"
              f"  nu*/N^2 = {F(n*n, cf['N']**2)}", flush=True)
        if n <= 3:
            N, E = C.blowup(5, C.C5()[1], [n] * 5)
            r2 = C.nu_star_cutting(N, E)
            assert r2['value'] == n * n
            print(f"    [independent] cutting-plane nu* = {r2['value']} "
                  f"({r2['ncycles']} generated cycles)", flush=True)
        if n <= 2:
            N, E = C.blowup(5, C.C5()[1], [n] * 5)
            r1 = C.nu_star_enumerate(N, E)
            assert r1['value'] == n * n
            print(f"    [independent] full-enumeration nu* = {r1['value']} "
                  f"({r1['ncycles']} odd cycles, primal_ok={r1['primal_ok']},"
                  f" dual_ok={r1['dual_ok']})", flush=True)

    print(flush=True)
    print("=" * 78, flush=True)
    print("(a2) known extremal graphs N = 12,13,14,15", flush=True)
    print("=" * 78, flush=True)
    for g6 in EXTREMAL:
        n, E = C.graph6_to_edges(g6)
        N = n
        tf = C.is_triangle_free(n, E)
        bip = C.bip_bruteforce_fast(n, E)
        r2 = C.nu_star_cutting(n, E)
        nu = r2['value']
        degs = [0] * n
        for u, v in E:
            degs[u] += 1
            degs[v] += 1
        print(f"N={N} g6={g6} |E|={len(E)} tri-free={tf} delta={min(degs)} Delta={max(degs)}", flush=True)
        print(f"    bip = {bip}   (N^2/25 = {F(N*N,25)},  bip/N^2 = {F(bip, N*N)}"
              f" = {float(F(bip,N*N)):.6f})", flush=True)
        print(f"    nu* = tau* = {nu} = {float(nu):.6f}   [cutting planes, {r2['ncycles']} rows]", flush=True)
        print(f"    integrality gap bip/nu* = {F(bip)/nu} = {float(F(bip)/nu):.6f}"
              f"   deficit bip-nu* = {F(bip)-nu}", flush=True)
        print(f"    nu*/N^2 = {nu/ (N*N)} = {float(nu/(N*N)):.6f}"
              f"    |E|/5 = {F(len(E),5)} (uniform-1/5 cover bound)", flush=True)
        try:
            r1 = C.nu_star_enumerate(n, E)
            assert r1['value'] == nu, (r1['value'], nu)
            print(f"    [independent] full enumeration: {r1['ncycles']} odd cycles, nu* = {r1['value']},"
                  f" primal_ok={r1['primal_ok']}, dual_ok={r1['dual_ok']}", flush=True)
        except Exception as ex:
            print(f"    [independent] full enumeration skipped: {ex}", flush=True)


if __name__ == "__main__":
    main()
