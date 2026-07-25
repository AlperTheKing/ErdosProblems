"""
G11 second, independently written verifier + explicit construction of the
Brandt-Thomasse VEGA graphs.

Why this file exists
--------------------
Brandt & Thomasse, "Dense triangle-free graphs are four-colorable: a solution
to the Erdos-Simonovits problem", Corollary 4.1:

    "The twin-free, maximal triangle-free, weighted graphs with delta > 1/3
     are the 3-colorable graphs Gamma_i for i >= 1 and the 4-chromatic Vega
     graphs."

Together with the blow-up/psi identity this says: EVERY triangle-free graph G
with delta(G) > n/3 admits a homomorphism into some Gamma_i (= Andrasfai
graph And_i) or into some Vega graph.  The Andrasfai side was already handled
by the campaign; the Vega side is new, so this file builds the Vega graphs
explicitly and evaluates psi exactly at the Brandt-Thomasse regular weight
vector (which is an exact rational LOWER bound on max_x psi).

Construction (Brandt-Thomasse, Section 1, verbatim paraphrase):
  "For some integer i >= 2, start with a graph Gamma_i on vertex set
   {1,...,3i-1} and add an edge xy and an induced 6-cycle (a,v,c,u,b,w) such
   that x is joined to a,b,c and y is joined to u,v,w.  The set of neighbors
   of a,u on the Gamma_i graph is {1,...,i}.  The set of neighbors of b,v on
   the Gamma_i graph is {i+1,...,2i}.  The set of neighbors of c,w on the
   Gamma_i graph is {2i+1,...,3i-1}.  This is the sole Vega graph on 3i+7
   vertices.  We denote it by Upsilon_i."
  Three further Vega graphs: Upsilon_i - {y}, Upsilon_i - {2i},
  Upsilon_i - {y, 2i}.

Weights (Brandt-Thomasse Theorem 3), integer form, all four families.

Everything below is exact integer / Fraction arithmetic.

Run:  python G11_verify_vega.py
"""

from fractions import Fraction
from itertools import combinations


# ---------------------------------------------------------------- graphs

def gamma(i):
    """Gamma_i on labels 1..3i-1 ; j ~ j+i, ..., j+2i-1  (mod 3i-1)."""
    n = 3 * i - 1
    V = list(range(1, n + 1))
    E = set()
    for j in V:
        for s in range(i, 2 * i):
            t = (j + s - 1) % n + 1          # representatives in 1..3i-1
            if t != j:
                E.add(frozenset((j, t)))
    return V, E


def vega_upsilon(i):
    """Upsilon_i, 3i+7 vertices.  Special vertices are strings."""
    V, E = gamma(i)
    V = list(V) + ['x', 'y', 'a', 'b', 'c', 'u', 'v', 'w']
    E = set(E)
    E.add(frozenset(('x', 'y')))
    for e in [('a', 'v'), ('v', 'c'), ('c', 'u'), ('u', 'b'),
              ('b', 'w'), ('w', 'a')]:                       # 6-cycle a v c u b w
        E.add(frozenset(e))
    for t in ('a', 'b', 'c'):
        E.add(frozenset(('x', t)))
    for t in ('u', 'v', 'w'):
        E.add(frozenset(('y', t)))
    A = list(range(1, i + 1))
    B = list(range(i + 1, 2 * i + 1))
    C = list(range(2 * i + 1, 3 * i))
    for j in A:
        E.add(frozenset(('a', j)))
        E.add(frozenset(('u', j)))
    for j in B:
        E.add(frozenset(('b', j)))
        E.add(frozenset(('v', j)))
    for j in C:
        E.add(frozenset(('c', j)))
        E.add(frozenset(('w', j)))
    return V, E


def delete(V, E, kill):
    kill = set(kill)
    V2 = [z for z in V if z not in kill]
    E2 = {e for e in E if not (set(e) & kill)}
    return V2, E2


def vega_family(i):
    """The four Vega graphs derived from Upsilon_i, with BT weights."""
    V, E = vega_upsilon(i)
    out = {}

    # Upsilon_i : weight 1 on x,y,1,2i ; 3i-3 on c,w ; 3i-2 on u,v,a,b ; 3 else
    wt = {}
    for z in V:
        wt[z] = 3
    for z in ('x', 'y', 1, 2 * i):
        wt[z] = 1
    for z in ('c', 'w'):
        wt[z] = 3 * i - 3
    for z in ('u', 'v', 'a', 'b'):
        wt[z] = 3 * i - 2
    out[f'Ups_{i}'] = (V, E, wt, 9 * i - 6, 27 * i - 19)

    # Upsilon_i - {y} : 1 on 1,2i ; 2 on x ; 3i-4 on w ; 3i-3 on u,v,c ;
    #                   3i-2 on a,b ; 3 else
    V1, E1 = delete(V, E, ['y'])
    wt1 = {z: 3 for z in V1}
    for z in (1, 2 * i):
        wt1[z] = 1
    wt1['x'] = 2
    wt1['w'] = 3 * i - 4
    for z in ('u', 'v', 'c'):
        wt1[z] = 3 * i - 3
    for z in ('a', 'b'):
        wt1[z] = 3 * i - 2
    out[f'Ups_{i}-y'] = (V1, E1, wt1, 9 * i - 7, 27 * i - 22)

    # Upsilon_i - {2i} : 1 on x,y ; 2 on 1,i ; 3i-3 on b,v,c,w ; 3i-2 on u,a ;
    #                    3 else
    V2, E2 = delete(V, E, [2 * i])
    wt2 = {z: 3 for z in V2}
    for z in ('x', 'y'):
        wt2[z] = 1
    for z in (1, i):
        wt2[z] = 2
    for z in ('b', 'v', 'c', 'w'):
        wt2[z] = 3 * i - 3
    for z in ('u', 'a'):
        wt2[z] = 3 * i - 2
    out[f'Ups_{i}-2i'] = (V2, E2, wt2, 9 * i - 7, 27 * i - 22)

    # Upsilon_i - {y,2i} : 2 on x,1,i ; 3i-4 on v,w ; 3i-3 on u,b,c ;
    #                      3i-2 on a ; 3 else
    V3, E3 = delete(V, E, ['y', 2 * i])
    wt3 = {z: 3 for z in V3}
    for z in ('x', 1, i):
        wt3[z] = 2
    for z in ('v', 'w'):
        wt3[z] = 3 * i - 4
    for z in ('u', 'b', 'c'):
        wt3[z] = 3 * i - 3
    wt3['a'] = 3 * i - 2
    out[f'Ups_{i}-y-2i'] = (V3, E3, wt3, 9 * i - 8, 27 * i - 25)

    return out


# ------------------------------------------------------------ predicates

def adjacency(V, E):
    adj = {z: set() for z in V}
    for e in E:
        p, q = tuple(e)
        adj[p].add(q)
        adj[q].add(p)
    return adj


def triangle_free(V, E):
    adj = adjacency(V, E)
    for e in E:
        p, q = tuple(e)
        if adj[p] & adj[q]:
            return False
    return True


def maximal_triangle_free(V, E):
    """triangle-free and diameter <= 2 (equivalently every non-edge has a
    common neighbour)."""
    if not triangle_free(V, E):
        return False
    adj = adjacency(V, E)
    for p, q in combinations(V, 2):
        if q in adj[p]:
            continue
        if not (adj[p] & adj[q]):
            return False
    return True


def twin_free(V, E):
    adj = adjacency(V, E)
    for p, q in combinations(V, 2):
        if adj[p] == adj[q]:
            return False
    return True


def chromatic_number(V, E, cap=6):
    adj = adjacency(V, E)
    order = sorted(V, key=lambda z: -len(adj[z]))
    for k in range(1, cap + 1):
        col = {}

        def bt(idx):
            if idx == len(order):
                return True
            z = order[idx]
            used = {col[t] for t in adj[z] if t in col}
            maxc = min(k, (max(col.values()) + 2) if col else 1)
            for cc in range(maxc):
                if cc in used:
                    continue
                col[z] = cc
                if bt(idx + 1):
                    return True
                del col[z]
            return False

        if bt(0):
            return k
    return None


# --------------------------------------------- exact cut minimisation

def min_weighted_monochromatic(V, E, wt):
    """Exact min over all 2-colourings of sum_{monochromatic uv} w_u w_v.
    Brute force over 2^(|V|-1) cuts.  Integer arithmetic."""
    idx = {z: t for t, z in enumerate(V)}
    n = len(V)
    el = [(idx[tuple(e)[0]], idx[tuple(e)[1]],
           wt[tuple(e)[0]] * wt[tuple(e)[1]]) for e in E]
    best = None
    for mask in range(1 << (n - 1)):
        m = mask << 1
        s = 0
        for p, q, ww in el:
            if ((m >> p) & 1) == ((m >> q) & 1):
                s += ww
                if best is not None and s >= best:
                    break
        if best is None or s < best:
            best = s
    return best


def bip_unweighted(V, E):
    return min_weighted_monochromatic(V, E, {z: 1 for z in V})


# ------------------------------------------------------------------ main

def main():
    print("=" * 78)
    print("VEGA GRAPHS (Brandt-Thomasse):  structure checks + exact psi at the")
    print("BT regular weight vector.  psi_BT is a LOWER bound on max_x psi.")
    print("Conjecture threshold: 1/25 = 0.04")
    print("=" * 78)
    rows = []
    for i in range(2, 7):
        fam = vega_family(i)
        for name, (V, E, wt, deg, tot) in fam.items():
            tf = triangle_free(V, E)
            mtf = maximal_triangle_free(V, E)
            tw = twin_free(V, E)
            adj = adjacency(V, E)
            wdeg = {z: sum(wt[t] for t in adj[z]) for z in V}
            regular = (len(set(wdeg.values())) == 1)
            degval = next(iter(set(wdeg.values()))) if regular else None
            totw = sum(wt[z] for z in V)
            ok_deg = (degval == deg)
            ok_tot = (totw == tot)
            n = len(V)
            small = n <= 22
            if small:
                num = min_weighted_monochromatic(V, E, wt)
                psi = Fraction(num, totw * totw)
                bipu = bip_unweighted(V, E)
                bipr = Fraction(bipu, n * n)
            else:
                psi = None
                bipu = None
                bipr = None
            rows.append((name, n, tf, mtf, tw, regular, ok_deg, ok_tot,
                         psi, bipu, bipr))
            s_psi = (f"{psi} = {float(psi):.6f}" if psi is not None else "skipped")
            s_bip = (f"{bipu} ({float(bipr):.6f} n^-2)" if bipu is not None
                     else "skipped")
            print(f"  {name:14s} n={n:3d} triangle-free={tf} maxTF={mtf} "
                  f"twin-free={tw} reg-wt={regular} deg={ok_deg} tot={ok_tot}")
            print(f"                  psi_BT = {s_psi:34s}  bip = {s_bip}")
            assert tf, name
            assert mtf, name
            assert tw, name
            assert regular and ok_deg and ok_tot, (name, degval, deg, totw, tot)
            if psi is not None:
                assert psi <= Fraction(1, 25), ("PSI EXCEEDS 1/25", name, psi)
                assert bipr <= Fraction(1, 25), ("BIP EXCEEDS 1/25", name, bipr)

    print()
    print("  chi(Ups_2 - y - 2i) (should be 4; BT say it is the Grotzsch graph):",
          end=' ')
    V, E, _, _, _ = vega_family(2)['Ups_2-y-2i']
    print(chromatic_number(V, E), " n =", len(V), " |E| =", len(E))
    print("  chi(Ups_2)                       :",
          chromatic_number(*vega_family(2)['Ups_2'][:2]))
    print()
    print("  delta(BT weights) = (9i-6)/(27i-19) > 1/3 exactly:")
    for i in range(2, 8):
        d = Fraction(9 * i - 6, 27 * i - 19)
        print(f"    i={i}: {d} = {float(d):.8f}   > 1/3 ? {d > Fraction(1,3)}"
              f"   (27i-18) - (27i-19) = 1")
    print()
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
