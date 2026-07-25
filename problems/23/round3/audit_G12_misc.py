"""AUDIT G12: the remaining claims -- P6 (T-join / double cover), R2 mechanism
numbers (M1,M2,M3 on Petersen / Clebsch / Andrasfai / the N=14 extremal graph),
the band algebra, and the P3 covering chain on named graphs.  All exact.
"""
from fractions import Fraction as Fr
import random
import sympy as sp
import audit_G12_core as A


# ---------------------------------------------------------------- mechanisms
def mechs(n, E):
    m = len(E)
    d = A.degrees(n, E)
    a = [set() for _ in range(n)]
    for u, v in E:
        a[u].add(v)
        a[v].add(u)
    M1 = min(sum(1 for (p, q) in E if p not in a[v] and q not in a[v]) for v in range(n))
    if n <= 20:
        best = 0
        for S in range(1 << n):
            vs = [i for i in range(n) if (S >> i) & 1]
            if all(q not in a[p] for i, p in enumerate(vs) for q in vs[i + 1:]):
                best = max(best, sum(d[i] for i in vs))
        M2 = m - best
    else:
        M2 = None
    # BFS layer parity cut
    M3 = None
    for s in range(n):
        lay = {s: 0}
        fr = [s]
        while fr:
            nf = []
            for u in fr:
                for w in a[u]:
                    if w not in lay:
                        lay[w] = lay[u] + 1
                        nf.append(w)
            fr = nf
        if len(lay) < n:
            continue
        mono = sum(1 for u, v in E if lay[u] == lay[v])
        M3 = mono if M3 is None else min(M3, mono)
    M4 = Fr(m) - Fr(sum(x * x for x in d), n)
    M5 = Fr((n - max(d)) ** 2, 4)
    return M1, M2, M3, M4, M5


def andrasfai(k):
    n = 3 * k - 1
    E = sorted({(i, j) for i in range(n) for j in range(n)
                if i < j and ((j - i) % 3 == 1)})
    return n, E


# ---------------------------------------------------------------- P6 checks
def cut_space_basis(n, E):
    """delta({v}) for v = 0..n-2 spans Cut(G)."""
    m = len(E)
    B = []
    for v in range(n - 1):
        x = 0
        for i, (p, q) in enumerate(E):
            if p == v or q == v:
                x |= 1 << i
        B.append(x)
    return B


def coset_min(n, E):
    """min |F| over F in 1 + Cut(G), by enumerating the cut space from a basis."""
    m = len(E)
    B = cut_space_basis(n, E)
    ones = (1 << m) - 1
    best = m
    for S in range(1 << len(B)):
        x = 0
        t = S
        while t:
            b = t & -t
            x ^= B[b.bit_length() - 1]
            t ^= b
        w = bin(ones ^ x).count("1")
        best = min(best, w)
    return best


def cycle_space_basis(n, E):
    """Fundamental cycles of a spanning forest, as edge bitmasks."""
    par = {}
    a = [[] for _ in range(n)]
    for i, (u, v) in enumerate(E):
        a[u].append((v, i))
        a[v].append((u, i))
    seen = [False] * n
    tree = set()
    pe = [-1] * n
    pv = [-1] * n
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        q = [s]
        while q:
            x = q.pop()
            for y, i in a[x]:
                if not seen[y]:
                    seen[y] = True
                    pe[y] = i
                    pv[y] = x
                    tree.add(i)
                    q.append(y)
    out = []
    for i, (u, v) in enumerate(E):
        if i in tree:
            continue
        pu, qv = [], []
        x = u
        while x != -1:
            pu.append(x)
            x = pv[x]
        x = v
        while x != -1:
            qv.append(x)
            x = pv[x]
        Su, Sv = set(pu), set(qv)
        lca = next(z for z in pu if z in Sv)
        mask = 1 << i
        x = u
        while x != lca:
            mask ^= 1 << pe[x]
            x = pv[x]
        x = v
        while x != lca:
            mask ^= 1 << pe[x]
            x = pv[x]
        out.append(mask)
    return out


def double_cover_ok(n, E, Fset, trials_seed=None):
    """G-F bipartite  <=>  in (GxK2) - both lifts of F, (v,0) and (v,1) are
    in different components for every v."""
    rem = [e for i, e in enumerate(E) if i not in Fset]
    lhs = A.is_bipartite(n, rem)
    # double cover on 2n nodes: (v,p) ~ (u,1-p) for uv in rem
    par = list(range(2 * n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    for u, v in rem:
        for p in (0, 1):
            ru, rv = find(2 * u + p), find(2 * v + 1 - p)
            if ru != rv:
                par[ru] = rv
    rhs = all(find(2 * v) != find(2 * v + 1) for v in range(n))
    return lhs == rhs, lhs, rhs


def main():
    print("=" * 76)
    print("1. band algebra, exact (sympy)")
    print("=" * 76)
    x = sp.symbols('x')
    r = sp.solve(sp.Eq(x - 4 * x**2, sp.Rational(1, 25)), x)
    print(f"   roots of x - 4x^2 = 1/25 : {r}   (1/20 and 1/5: {sorted(r) == [sp.Rational(1,20), sp.Rational(1,5)]})")
    print(f"   max of x-4x^2 = {sp.Rational(1,16)} at x = {sp.Rational(1,8)}: "
          f"{sp.simplify((x-4*x**2).subs(x, sp.Rational(1,8))) == sp.Rational(1,16)}")
    print(f"   at x = 1/5 the bound is exactly {sp.simplify((x-4*x**2).subs(x, sp.Rational(1,5)))}")
    print()

    print("=" * 76)
    print("2. mechanisms M1..M5 on the named graphs (exact)")
    print("=" * 76)
    named = {}
    named["C5"] = A.C5
    named["C5[2]"] = A.blowup(*A.C5, [2] * 5)
    named["C5[3]"] = A.blowup(*A.C5, [3] * 5)
    named["Petersen"] = (10, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 5), (1, 6),
                              (2, 7), (3, 8), (4, 9), (5, 7), (7, 9), (9, 6), (6, 8), (8, 5)])
    S = [1, 2, 4, 8, 15]
    named["Clebsch"] = (16, sorted({tuple(sorted((u, u ^ s))) for u in range(16) for s in S}))
    for k in (3, 4, 5, 6):
        named[f"And({k})"] = andrasfai(k)
    named["extremal N=14"] = A.g6("M?AE@bH{AYN_LgBs?")
    named["extremal N=12a"] = A.g6("K?ABBBwerwBw")
    for nm, (n, E) in named.items():
        assert A.triangle_free(n, E), nm
        M1, M2, M3, M4, M5 = mechs(n, E)
        tgt = Fr(n * n, 25)
        b = A.bip(n, E) if n <= 20 else None
        print(f"{nm}: N={n} |E|={len(E)} bip={b} N^2/25={tgt}={float(tgt):.4f}")
        print(f"    M1={M1} {'BREAKS' if M1 > tgt else 'ok'}   M2={M2} "
              f"{'BREAKS' if M2 is not None and M2 > tgt else 'ok'}   M3={M3} "
              f"{'BREAKS' if M3 is not None and M3 > tgt else 'ok'}")
        print(f"    M4={M4}={float(M4):.4f} {'BREAKS' if M4 > tgt else 'ok'}   "
              f"M5={M5} {'BREAKS' if M5 > tgt else 'ok'}   "
              f"M2/N^2={Fr(M2, n*n) if M2 is not None else '-'}")
        if b is not None:
            assert b <= M1 and (M2 is None or b <= M2) and b <= M4 and b <= M5, nm
    print("   (bip <= M1,M2,M4,M5 verified on every row)")
    print()

    print("=" * 76)
    print("3. P6 statement 1 (coset of the cut space) and statement 2 (double cover)")
    print("=" * 76)
    rnd = random.Random(20260725)
    for nm in ["C5", "C5[2]", "Petersen", "extremal N=12a"]:
        n, E = named[nm]
        cm = coset_min(n, E)
        b = A.bip(n, E)
        cyc = cycle_space_basis(n, E)
        # parity characterisation of the coset, tested on the optimal F
        ok2 = True
        for _ in range(200):
            Fset = {i for i in range(len(E)) if rnd.random() < 0.35}
            good, l, r2 = double_cover_ok(n, E, Fset)
            ok2 &= good
        print(f"{nm}: bip={b}  min weight of coset 1+Cut(G) = {cm}  equal={b == cm}"
              f"   double-cover equivalence on 200 random F: {ok2}"
              f"   (cycle-space dim {len(cyc)} = |E|-n+1 = {len(E)-n+1})")
    print()

    print("=" * 76)
    print("4. Higman-Sims / Clebsch arithmetic for the M2 ceiling")
    print("=" * 76)
    print(f"   Clebsch  srg(16,5,0,2): m=40, alpha=5  -> M2 = 40-5*5 = {40-25}, "
          f"M2/N^2 = {Fr(15,256)} = {float(Fr(15,256)):.6f}")
    print(f"   Higman-Sims srg(100,22,0,6): m=1100, alpha=22 -> M2 = 1100-22*22 = {1100-484}, "
          f"M2/N^2 = {Fr(616,10000)} = {float(Fr(616,10000)):.6f}  (literature alpha, not recomputed)")
    print(f"   N^2/16 for N=100 is {Fr(10000,16)} = 625 > 616")
    print(f"   C8 (2-regular, N=8=4*2): M1 = 8-2*2 = 4 = N^2/16 = {Fr(64,16)} EXACT")
    print(f"   any d-regular triangle-free graph on N=4d vertices: M1 = 2d^2-d^2 = d^2 = N^2/16")


if __name__ == "__main__":
    main()
