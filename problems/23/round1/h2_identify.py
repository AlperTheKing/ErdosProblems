"""H2 (i): identify the known exact extremal graphs as weighted blow-ups of named bases.

Strategy: reduce each extremal graph by twin classes (false twins = same neighbourhood);
the quotient is the base and the class sizes are the weights.  Then test the quotient for
isomorphism against a catalogue of named triangle-free graphs.
"""
import itertools
from h2_lib import *
from h2_decode import twin_classes, quotient, indep_number, odd_girth, hom_to_C5
from h2_blowup_theory import bip_blowup

EXTREMAL = {
 12: ["K?ABBBwerwBw", "K?BD@g]Qvo^?"],
 13: ["L??ED@_~?~^_Fw", "L??EDB_~?~^_Fw", "L??EFB_~FwB{Fw", "L??FFB_~?~^_Fw",
      "L?`DAboU`w@{hS", "L?`DAboUdIF_Bo", "L?`DE`gl@YJODg"],
 14: ["M?AE@bH{AYN_LgBs?"],
}


def canon(n, adj):
    """Cheap canonical form: brute-force over permutations is too slow for n>8, so
    use a refinement + backtracking isomorphism test instead."""
    return (n, tuple(sorted(bin(a).count("1") for a in adj)), num_edges(n, adj))


def iso(n1, adj1, n2, adj2):
    """Exact isomorphism test by degree-refined backtracking (small n only)."""
    if n1 != n2:
        return None
    if sorted(bin(a).count("1") for a in adj1) != sorted(bin(a).count("1") for a in adj2):
        return None
    n = n1
    deg1 = [bin(a).count("1") for a in adj1]
    deg2 = [bin(a).count("1") for a in adj2]
    perm = [-1] * n
    used = [False] * n

    def rec(k):
        if k == n:
            return True
        # order vertices of g1 by descending degree for pruning
        v = order[k]
        for u in range(n):
            if used[u] or deg2[u] != deg1[v]:
                continue
            ok = True
            for j in range(k):
                w = order[j]
                if (((adj1[v] >> w) & 1) != ((adj2[u] >> perm[w]) & 1)):
                    ok = False
                    break
            if ok:
                perm[v] = u
                used[u] = True
                if rec(k + 1):
                    return True
                used[u] = False
                perm[v] = -1
        return False

    order = sorted(range(n), key=lambda v: -deg1[v])
    return perm[:] if rec(0) else None


# ---- named catalogue of small triangle-free graphs ----
def grotzsch():
    # Mycielskian of C5: u_0..u_4 cycle, w_0..w_4 shadows (w_i ~ u_{i-1}, u_{i+1}),
    # apex z ~ all w_i.
    E = [(i, (i + 1) % 5) for i in range(5)]
    for i in range(5):
        E += [(5 + i, (i - 1) % 5), (5 + i, (i + 1) % 5), (5 + i, 10)]
    return 11, E


def mycielski_of(n, edges):
    E = list(edges)
    for (u, v) in edges:
        E += [(u, n + v), (v, n + u)]
    for i in range(n):
        E.append((n + i, 2 * n))
    return 2 * n + 1, E


NAMED = []
NAMED.append(("C5", 5, C5_EDGES))
NAMED.append(("Grotzsch=M(C5)", *grotzsch()))
NAMED.append(("Petersen", 10, PETERSEN_EDGES))
NAMED.append(("C13(1,5)", *circulant(13, [1, 5])))
NAMED.append(("Andrasfai(3)=Wagner", *circulant(8, [1, 4])))
NAMED.append(("Andrasfai(4)=C11(1,4)", *circulant(11, [1, 4])))
NAMED.append(("M(C7)", *mycielski_of(7, C7_EDGES)))
NAMED.append(("Chvatal", 12, [(0,1),(0,4),(0,6),(0,9),(1,2),(1,5),(1,7),(2,3),(2,6),(2,8),
                              (3,4),(3,7),(3,9),(4,5),(4,8),(5,10),(5,11),(6,10),(6,11),
                              (7,8),(7,11),(8,10),(9,10),(9,11)]))


def sub_iso_named(bn, bedges):
    badj = edges_to_adj(bn, bedges)
    for name, n, e in NAMED:
        if n != bn:
            continue
        if iso(bn, badj, n, edges_to_adj(n, e)) is not None:
            return name
    return None


def spanning_super_named(bn, bedges):
    """Is the quotient a SPANNING SUBGRAPH of a named graph on the same order?"""
    badj = edges_to_adj(bn, bedges)
    out = []
    for name, n, e in NAMED:
        if n != bn:
            continue
        nadj = edges_to_adj(n, e)
        # try all permutations only for small n
        if n <= 9:
            for p in itertools.permutations(range(n)):
                ok = all(((nadj[p[i]] >> p[j]) & 1) for i in range(n) for j in range(i + 1, n)
                         if (badj[i] >> j) & 1)
                if ok:
                    out.append(name)
                    break
    return out


if __name__ == "__main__":
    print("### twin-quotient (base) of each exact extremal graph\n")
    for N in sorted(EXTREMAL):
        for g in EXTREMAL[N]:
            n, adj = g6_decode(g)
            cls = twin_classes(n, adj)
            K, qe, sizes = quotient(n, adj, cls)
            m = num_edges(n, adj)
            b = bip_blowup(K, qe, sizes)
            name = sub_iso_named(K, qe)
            print(f"{g}  N={N} m={m} bip={b}")
            print(f"   base order h={K}  |E(base)|={len(qe)}  weights={sizes}"
                  f"  base={name or 'unnamed'}")
            print(f"   base g6 = {g6_encode(K, edges_to_adj(K, qe))}")
    print()
    print("### Grotzsch (M(C5)) blow-up: the mechanism that beats every C5 blow-up")
    gn, ge = grotzsch()
    gadj = edges_to_adj(gn, ge)
    print("   Grotzsch g6 =", g6_encode(gn, gadj), " triangle-free:", is_triangle_free(gn, gadj))
    for c in range(1, 5):
        w = [1] * 10 + [c]
        N = sum(w)
        print(f"   weights (1^5,1^5,{c}) -> N={N}, bip={bip_blowup(gn, ge, w)}, "
              f"N^2/25={N*N/25:.2f}")
