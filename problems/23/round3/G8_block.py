"""G8: exact blocking witnesses for FIXED-FAMILY certificate schemes on And(k).

(1) matching bound.  For any cut S and any pair of nonnegative linear forms L,L'
    with L(x)L'(x) >= q_S(x) on the nonnegative orthant:  put x = e_a + e_b for a
    monochromatic edge ab; then (l_a+l_b)(l'_a+l'_b) >= q_S(e_a+e_b) >= 1.  For a
    matching a_1b_1,...,a_nu b_nu inside mono(S), Cauchy-Schwarz gives
        (sum_v l_v)(sum_v l'_v) >= (sum_i sqrt((l_{a_i}+l_{b_i})(l'_{a_i}+l'_{b_i})))^2 >= nu^2.
    So c(S) := min lambda lambda' >= nu(mono(S))^2.
    Evaluating any AM-GM chain  psi <= min_j L_jL'_j <= prod_j (L_jL'_j)^{w_j}  at the
    UNIFORM point x = (1/n,...,1/n) forces  min_j c_j <= n^2/25.

(2) geometric-mean scheme.  Any certificate of the shape
        psi(x) <= min_j q_{S_j}(x) <= prod_j q_{S_j}(x)^{w_j} <= 1/25   (sum w_j = 1)
    forces q_{S_j}(x*) = 1/25 for every j in supp(w) and EVERY maximiser x* of psi
    (otherwise the product at x* exceeds 1/25).  So supp(w) must lie in the
    intersection of the active cut sets over all maximisers.  Here we intersect over
    the induced-C5 uniform points, which are maximisers by accepted fact 3.
"""
import sys, itertools
from fractions import Fraction
from G8_graphs import andrasfai
from G8_monostruct import max_matching


def induced_C5s(n, adj, edges):
    out = []
    for S in itertools.combinations(range(n), 5):
        Sset = set(S)
        sub = [(u, v) for (u, v) in edges if u in Sset and v in Sset]
        if len(sub) != 5:
            continue
        deg = {v: 0 for v in S}
        for (u, v) in sub:
            deg[u] += 1; deg[v] += 1
        if all(d == 2 for d in deg.values()):
            out.append(S)
    return out


if __name__ == "__main__":
    for k in (2, 3, 4, 5):
        n, conn, adj, edges = andrasfai(k)
        C5s = induced_C5s(n, adj, edges)
        print(f"And({k}) n={n}: {len(C5s)} induced C5s")
        # active cut sets at the induced-C5 uniform points
        inter = None
        for C in C5s:
            Cset = set(C)
            act = set()
            for mask in range(1 << (n - 1)):
                side = [0] * n
                for v in range(1, n):
                    side[v] = (mask >> (v - 1)) & 1
                cnt = 0
                for (u, v) in edges:
                    if u in Cset and v in Cset and side[u] == side[v]:
                        cnt += 1
                        if cnt > 1:
                            break
                if cnt == 1:                      # value exactly 1/25 at this point
                    act.add(mask)
            inter = act if inter is None else (inter & act)
        print(f"   |intersection of active cut sets over all induced-C5 maximisers| = {len(inter)}")
        if inter:
            for mask in sorted(inter)[:6]:
                side = [0] * n
                for v in range(1, n):
                    side[v] = (mask >> (v - 1)) & 1
                mono = [(u, v) for (u, v) in edges if side[u] == side[v]]
                print(f"      cut {''.join(map(str,side))}: |mono|={len(mono)} nu={max_matching(mono)}")
            print("   => geometric-mean scheme NOT yet excluded by this test")
        else:
            print("   => ANY fixed-family geometric-mean certificate is BLOCKED:")
            print("      no single cut is simultaneously optimal at all induced-C5 maximisers.")
        # matching bound
        best = None
        for mask in range(1 << (n - 1)):
            side = [0] * n
            for v in range(1, n):
                side[v] = (mask >> (v - 1)) & 1
            mono = [(u, v) for (u, v) in edges if side[u] == side[v]]
            if not mono:
                continue
            nu = max_matching(mono)
            if best is None or nu < best[0]:
                best = (nu, mask, mono)
        nu = best[0]
        print(f"   min over cuts of nu(mono(S)) = {nu}  (= k-1 = {k-1}) ; c(S) >= {nu*nu}"
              f" vs n^2/25 = {Fraction(n*n,25)}"
              f"  => product-of-two-linear-forms AM-GM "
              f"{'POSSIBLE' if Fraction(nu*nu) <= Fraction(n*n,25) else 'BLOCKED'}")
        sys.stdout.flush()
