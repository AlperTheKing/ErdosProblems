"""Q1_checks.py -- all remaining exact checks for the Q1 report.

 1. identify the n=11 falsifier as the Grotzsch graph (Mycielskian of C5) by explicit isomorphism
 2. exact weighted statement of the falsifier (uniform x = 1/11)
 3. widen the cut family: unions of neighbourhoods over ARBITRARY index sets, and
    complements/Boolean combinations of at most 2 neighbourhoods -- does anything reach 4?
 4. bip is additive over disjoint unions (ingredient of the counting dichotomy)
 5. blow-up identity bip(H[a]) = min over cuts of H, checked over ALL 2^{|V(H[a])|} cuts
 6. pentagon-counting obstruction: C7 has bip = 1 and zero 5-cycles
 7. labelled count of C5-blow-ups (the 'lower bound from C5 blow-ups' of route (b))
"""
from fractions import Fraction
from itertools import product, combinations
from math import comb, factorial
from Q1_verify import g6_decode, edges, is_triangle_free, mono_count, bip_bruteforce, independent_sets

G6_FALSIFIER = "J?BD@g]Qvo?"


def mycielski_c5():
    """Grotzsch graph: u_0..u_4 = C5, v_0..v_4 shadows (v_i ~ u_{i-1}, u_{i+1}), w ~ all v_i"""
    n = 11
    adj = [set() for _ in range(n)]

    def add(a, b):
        adj[a].add(b)
        adj[b].add(a)
    for i in range(5):
        add(i, (i + 1) % 5)                 # u_i on the C5
    for i in range(5):
        add(5 + i, (i - 1) % 5)             # v_i ~ u_{i-1}
        add(5 + i, (i + 1) % 5)             # v_i ~ u_{i+1}
        add(10, 5 + i)                      # w ~ v_i
    return n, adj


def iso(n1, a1, n2, a2):
    """brute-force isomorphism search using degree partition (n <= 11 here)"""
    if n1 != n2:
        return None
    from itertools import permutations
    d1 = [len(a1[i]) for i in range(n1)]
    d2 = [len(a2[i]) for i in range(n2)]
    if sorted(d1) != sorted(d2):
        return None
    # group vertices of g2 by degree, permute within classes
    classes = {}
    for v in range(n2):
        classes.setdefault(d2[v], []).append(v)
    order = sorted(range(n1), key=lambda v: d1[v])
    pools = {d: classes[d] for d in classes}
    mapping = {}
    used = set()

    def rec(k):
        if k == len(order):
            return True
        u = order[k]
        for w in pools[d1[u]]:
            if w in used:
                continue
            ok = True
            for uu in order[:k]:
                if (uu in a1[u]) != (mapping[uu] in a2[w]):
                    ok = False
                    break
            if ok:
                mapping[u] = w
                used.add(w)
                if rec(k + 1):
                    return True
                used.discard(w)
                del mapping[u]
        return False
    return dict(mapping) if rec(0) else None


def fam_union_all(n, adj, index_sets):
    """min over the given index sets I of mono( union of N(v), v in I ), exact integers"""
    E = edges(n, adj)
    best = (len(E), None)
    for I in index_sets:
        NI = set()
        for v in I:
            NI |= adj[v]
        m = mono_count(E, NI)
        if m < best[0]:
            best = (m, tuple(sorted(I)))
    return best


def all_subsets(n):
    for mask in range(1 << n):
        yield [i for i in range(n) if mask >> i & 1]


def bip_of_edge_list(n, E):
    best = len(E)
    for mask in range(1 << n):
        A = {i for i in range(n) if mask >> i & 1}
        m = sum(1 for (u, v) in E if (u in A) == (v in A))
        best = min(best, m)
    return best


def disjoint_union(n1, E1, n2, E2):
    return n1 + n2, E1 + [(u + n1, v + n1) for (u, v) in E2]


def blowup(n, adj, a):
    """H[a] as (N, edge list)"""
    off = [0] * (n + 1)
    for i in range(n):
        off[i + 1] = off[i] + a[i]
    N = off[n]
    E = []
    for i in range(n):
        for j in adj[i]:
            if i < j:
                for p in range(off[i], off[i + 1]):
                    for q in range(off[j], off[j + 1]):
                        E.append((p, q))
    return N, E


def psi_min_over_cuts_of_H(n, adj, a):
    """min over cuts S of H of sum_{uv mono} a_u a_v -- the blow-up identity's right side"""
    E = edges(n, adj)
    best = None
    for mask in range(1 << n):
        tot = 0
        for (u, v) in E:
            if ((mask >> u) & 1) == ((mask >> v) & 1):
                tot += a[u] * a[v]
        if best is None or tot < best:
            best = tot
    return best


def main():
    print("### 1. identify the falsifier")
    n, adj = g6_decode(G6_FALSIFIER)
    n2, adj2 = mycielski_c5()
    mp = iso(n, adj, n2, adj2)
    print(f"  g6={G6_FALSIFIER}: n={n}, |E|={len(edges(n,adj))}, triangle-free={is_triangle_free(n,adj)}")
    print(f"  isomorphic to Mycielskian(C5) = Grotzsch graph ?  {mp is not None}   mapping={mp}")

    print("\n### 2. exact weighted statement (uniform x = 1/11)")
    b = bip_bruteforce(n, adj)
    fam, I, NI = None, None, None
    E = edges(n, adj)
    best = (len(E), None, None)
    for J in independent_sets(n, adj):
        S = set()
        for v in J:
            S |= adj[v]
        m = mono_count(E, S)
        if m < best[0]:
            best = (m, J, frozenset(S))
    fam, I, NI = best
    x = Fraction(1, 11)
    print(f"  bip = {b},  psi_true = {b}*x^2 = {Fraction(b,121)} = {float(Fraction(b,121)):.6f}   (1/25 = {float(Fraction(1,25)):.6f})")
    print(f"  fam = {fam},  certificate value = {Fraction(fam,121)} = {float(Fraction(fam,121)):.6f}")
    print(f"  EXCESS over 1/25 : {Fraction(fam,121) - Fraction(1,25)} = {float(Fraction(fam,121)-Fraction(1,25)):.8f}  > 0")
    print(f"  slack of truth   : {Fraction(1,25) - Fraction(b,121)} = {float(Fraction(1,25)-Fraction(b,121)):.8f}  > 0")

    print("\n### 3. widen the family")
    v1 = fam_union_all(n, adj, [[v] for v in range(n)])
    v2 = fam_union_all(n, adj, [list(c) for c in combinations(range(n), 2)])
    v3 = fam_union_all(n, adj, [list(c) for c in combinations(range(n), 3)])
    vall = fam_union_all(n, adj, all_subsets(n))
    print(f"  min mono over single neighbourhoods N(v)          : {v1}")
    print(f"  min mono over N(u) u N(v)                          : {v2}")
    print(f"  min mono over N(u) u N(v) u N(w)                   : {v3}")
    print(f"  min mono over ALL unions of neighbourhoods         : {vall}")
    # complements of unions are the same cuts (mono is complement-invariant)
    # symmetric differences of two neighbourhoods:
    Es = edges(n, adj)
    bestsd = (len(Es), None)
    for u, v in combinations(range(n), 2):
        S = adj[u] ^ adj[v]
        m = mono_count(Es, S)
        if m < bestsd[0]:
            bestsd = (m, (u, v))
    print(f"  min mono over N(u) sym-diff N(v)                   : {bestsd}")
    print(f"  true bip                                           : {b}   (target n^2/25 = {Fraction(121,25)})")

    print("\n### 4. bip additive over disjoint unions (spot check)")
    import random
    random.seed(1)
    ok = True
    tests = [("DUW", "DUW"), ("DUW", "C~"), ("F?bBo", "DUW")]
    for s1, s2 in tests:
        na, aa = g6_decode(s1)
        nb, ab = g6_decode(s2)
        E1 = edges(na, aa)
        E2 = edges(nb, ab)
        NN, EE = disjoint_union(na, E1, nb, E2)
        lhs = bip_of_edge_list(NN, EE)
        rhs = bip_of_edge_list(na, E1) + bip_of_edge_list(nb, E2)
        print(f"  bip({s1} + {s2}) = {lhs}   bip({s1})+bip({s2}) = {rhs}   equal={lhs==rhs}")
        ok &= (lhs == rhs)
    print(f"  all additive: {ok}")

    print("\n### 5. blow-up identity over ALL cuts of the blow-up")
    for (g6, a) in [("DUW", (1, 1, 1, 1, 1)), ("DUW", (2, 2, 2, 2, 2)), ("DUW", (3, 1, 2, 1, 2)),
                    ("DUW", (2, 1, 2, 2, 1)), ("ECpo", (2, 1, 2, 1, 1, 2))]:
        nh, ah = g6_decode(g6)
        NN, EE = blowup(nh, ah, a)
        lhs = bip_of_edge_list(NN, EE)
        rhs = psi_min_over_cuts_of_H(nh, ah, a)
        print(f"  H={g6} a={a}: bip(H[a]) over all 2^{NN} cuts = {lhs}; min over cuts of H = {rhs}; equal={lhs==rhs}")

    print("\n### 6. pentagon-counting obstruction: C7")
    c7 = "F?bBo"  # placeholder; build C7 explicitly instead
    nC, aC = 7, [set() for _ in range(7)]
    for i in range(7):
        aC[i].add((i + 1) % 7)
        aC[(i + 1) % 7].add(i)
    EC = edges(nC, aC)
    bC = bip_of_edge_list(nC, EC)
    # count 5-cycles directly
    c5 = 0
    for S in combinations(range(7), 5):
        sub = {v: aC[v] & set(S) for v in S}
        if all(len(sub[v]) == 2 for v in S):
            # connected check
            start = S[0]
            seen = {start}
            stack = [start]
            while stack:
                z = stack.pop()
                for w in sub[z]:
                    if w not in seen:
                        seen.add(w)
                        stack.append(w)
            if len(seen) == 5:
                c5 += 1
    print(f"  C7: bip = {bC}, number of 5-cycles = {c5}")
    print(f"  => any inequality of the form F(bip) <= const * (#C5) with F(t)>0 for t>0 is FALSE at C7")

    print("\n### 7. labelled C5-blow-up count (route (b) lower bound)")
    for N in [25, 50, 100]:
        k = N // 5
        cnt = factorial(N) // (factorial(k) ** 5) // 10
        print(f"  N={N}: #labelled C5[N/5] = N!/((N/5)!^5 * 10) = {cnt}  ~ 2^{cnt.bit_length()-1}"
              f"   (vs 2^(N^2/4) = 2^{N*N//4})")


if __name__ == "__main__":
    main()
