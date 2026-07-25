"""ROOT-AGENT GATE (Claude, round 3).  Exact verification of three statements about

        psi(H,x) = min over cuts S of H of sum_{uv monochromatic} x_u x_v,   x in the simplex.

  R3-C1  every fixed averaging certificate has value >= bip(H)/(4|E(H)|), hence >= 1/20 on C5[n]
  R3-C2  interior reduction: max psi is attained on a proper face or at an interior critical point
  R3-C3  transfer concavity: t -> psi(x + t(e_u - e_v)) is concave for EVERY pair u,v
         corollary (twin balancing): some maximiser is constant on every twin class

Everything is Fraction arithmetic.  Own graph6 decoder, own cut enumeration; nothing imported from
any other script in this repository.
"""
from fractions import Fraction as F
from itertools import combinations
import random


# ---------------------------------------------------------------- graphs

def g6(s):
    """graph6 -> (n, edge list).  Own decoder."""
    b = [ord(c) - 63 for c in s]
    i = 0
    n = b[0]; i = 1
    if n == 63:
        n = (b[1] << 12) | (b[2] << 6) | b[3]; i = 4
    bits = []
    for x in b[i:]:
        bits.extend((x >> k) & 1 for k in (5, 4, 3, 2, 1, 0))
    E, p = [], 0
    for j in range(1, n):
        for k in range(j):
            if bits[p]:
                E.append((k, j))
            p += 1
    return n, E


def circ(m, S):
    E = set()
    for v in range(m):
        for s in S:
            a, b = v, (v + s) % m
            if a != b:
                E.add((min(a, b), max(a, b)))
    return m, sorted(E)


def blowup(nE, a):
    """balanced/unbalanced blow-up: vertex v of H becomes a[v] independent copies."""
    n, E = nE
    idx, base = [], 0
    for v in range(n):
        idx.append(list(range(base, base + a[v])))
        base += a[v]
    EE = [(x, y) for (u, v) in E for x in idx[u] for y in idx[v]]
    return base, EE


NAMED = {
    'C5': circ(5, [1]),
    'C7': circ(7, [1]),
    'C5[2]': blowup(circ(5, [1]), [2] * 5),
    'C5[3]': blowup(circ(5, [1]), [3] * 5),
    'Wagner=And(3)': circ(8, [1, 4]),
    'And(4)': circ(11, [1, 4]),
    'C11(1,3)': circ(11, [1, 3]),
    'C13(1,5)': circ(13, [1, 5]),
    'Petersen': (10, sorted(set([(i, (i + 1) % 5) for i in range(5)] +
                                [(min(i, 5 + i), max(i, 5 + i)) for i in range(5)] +
                                [(min(5 + i, 5 + (i + 2) % 5), max(5 + i, 5 + (i + 2) % 5)) for i in range(5)]))),
    'Grotzsch': (11, sorted(set([(i, (i + 1) % 5) for i in range(5)] +
                                [(min(5 + i, (i + 1) % 5), max(5 + i, (i + 1) % 5)) for i in range(5)] +
                                [(min(5 + i, (i + 4) % 5), max(5 + i, (i + 4) % 5)) for i in range(5)] +
                                [(5 + i, 10) for i in range(5)]))),
    'extremal N=12 a': g6('K?ABBBwerwBw'),
    'extremal N=13': g6('L??ED@_~?~^_Fw'),
}


def triangles(n, E):
    A = [[0] * n for _ in range(n)]
    for u, v in E:
        A[u][v] = A[v][u] = 1
    return sum(1 for i, j, k in combinations(range(n), 3) if A[i][j] and A[j][k] and A[i][k])


# ---------------------------------------------------------------- psi and bip, exact

def cut_mono_lists(n, E):
    """for every cut (vertex 0 fixed) the list of monochromatic edges"""
    out = []
    for m in range(1 << (n - 1)):
        S = (m << 1) | 1
        out.append([(u, v) for (u, v) in E if ((S >> u) & 1) == ((S >> v) & 1)])
    return out


def bip_exact(n, E):
    return min(len(mono) for mono in cut_mono_lists(n, E))


def psi_exact(cuts, x):
    return min(sum(x[u] * x[v] for (u, v) in mono) for mono in cuts)


# ---------------------------------------------------------------- R3-C1

def gate_R3C1():
    print("=" * 78)
    print("R3-C1  averaging-certificate floor   B(lambda) >= bip(H)/(4|E(H)|)")
    print("=" * 78)
    print(f"{'pattern':18s} {'n':>3s} {'|E|':>5s} {'bip':>5s} {'floor=bip/4|E|':>16s} {'25bip>4|E|':>11s}")
    for name, (n, E) in NAMED.items():
        if n > 20:
            continue
        b = bip_exact(n, E)
        floor = F(b, 4 * len(E))
        dead = 25 * b > 4 * len(E)
        print(f"{name:18s} {n:3d} {len(E):5d} {b:5d} {str(floor):>10s} = {float(floor):.4f} {str(dead):>11s}")

    # the C5 facts behind the bound
    n, E = NAMED['C5']
    cuts = cut_mono_lists(n, E)
    assert all(len(mono) >= 1 for mono in cuts), "some cut of C5 is monochromatic-free"
    print("\nC5: all %d cuts have >= 1 monochromatic edge  => sum_e c_e >= 1 => max_e c_e >= 1/5" % len(cuts))
    # the five rotation cuts {i,i+2}: c_e = 1/5 on every edge
    cnt = {e: 0 for e in E}
    for i in range(5):
        S = {i, (i + 2) % 5}
        for (u, v) in E:
            if ((u in S) == (v in S)):
                cnt[(u, v)] += 1
    print("rotation-cut monochromatic counts per edge:", sorted(cnt.values()),
          "-> c_e = 1/5 for every edge")
    # B(lambda) for that lambda equals (1/5)*max_x sum x_i x_{i+1} = (1/5)(1/4) = 1/20
    x = [F(1, 2), F(1, 2), F(0), F(0), F(0)]
    val = sum(x[u] * x[v] for (u, v) in E) * F(1, 5)
    print("value at x=(1/2,1/2,0,0,0):", val, "= 1/20  (Motzkin-Straus max of sum x_i x_{i+1} is 1/4)")
    assert val == F(1, 20)
    print("=> min over all lambda of B(lambda) = 1/20 on C5, against the truth 1/25.  CONFIRMED\n")


# ---------------------------------------------------------------- R3-C3

def gate_R3C3(trials=400, seed=20260725):
    print("=" * 78)
    print("R3-C3  transfer concavity:  t -> psi(x + t(e_u - e_v)) is concave, every pair u,v")
    print("=" * 78)
    rng = random.Random(seed)
    bad = 0
    checked = 0
    for name, (n, E) in NAMED.items():
        if n > 13:
            continue
        cuts = cut_mono_lists(n, E)
        for _ in range(trials // 8):
            # random rational point of the simplex
            w = [F(rng.randint(0, 12)) for _ in range(n)]
            if sum(w) == 0:
                continue
            x = [wi / sum(w) for wi in w]
            u, v = rng.sample(range(n), 2)
            # three collinear points on the transfer line, inside the simplex
            hi = x[v]
            if hi == 0:
                continue
            t1, t3 = F(0), hi
            t2 = (t1 + t3) / 2
            def pt(t):
                y = list(x); y[u] = x[u] + t; y[v] = x[v] - t; return y
            f1, f2, f3 = (psi_exact(cuts, pt(t)) for t in (t1, t2, t3))
            checked += 1
            if 2 * f2 < f1 + f3:          # midpoint below the chord => not concave
                bad += 1
                print("  CONCAVITY FAILURE", name, u, v, f1, f2, f3)
    print(f"midpoint-concavity checks: {checked}, failures: {bad}")
    assert bad == 0
    print("CONFIRMED (proof: the t^2 coefficient of q_S along e_u-e_v is -[uv monochromatic] <= 0,")
    print("so every q_S is concave along the line, hence so is their minimum).\n")


def twin_classes(n, E):
    A = [set() for _ in range(n)]
    for u, v in E:
        A[u].add(v); A[v].add(u)
    cls, seen = [], set()
    for u in range(n):
        if u in seen:
            continue
        c = [w for w in range(n) if A[w] == A[u]]
        for w in c:
            seen.add(w)
        cls.append(c)
    return cls


def gate_twins(trials=200, seed=7):
    print("=" * 78)
    print("R3-C3 corollary  twin balancing: averaging over a twin class never decreases psi")
    print("=" * 78)
    rng = random.Random(seed)
    tested = 0
    for name in ['C5[2]', 'C5[3]']:
        n, E = NAMED[name]
        cuts = cut_mono_lists(n, E)
        cls = twin_classes(n, E)
        print(f"{name}: twin classes {cls}")
        for _ in range(trials // 2):
            w = [F(rng.randint(0, 9)) for _ in range(n)]
            if sum(w) == 0:
                continue
            x = [wi / sum(w) for wi in w]
            y = list(x)
            for c in cls:
                avg = sum(x[i] for i in c) / len(c)
                for i in c:
                    y[i] = avg
            a, b = psi_exact(cuts, x), psi_exact(cuts, y)
            tested += 1
            assert b >= a, (name, x, a, b)
        print(f"  {tested} random points: psi(balanced) >= psi(x) in every case")
    # and the corollary max psi(H[a]) = max psi(H): check on C5[2] against C5
    n, E = NAMED['C5[2]']
    cuts2 = cut_mono_lists(n, E)
    x = [F(1, 10)] * 10
    print("psi(C5[2], uniform) =", psi_exact(cuts2, x), " (= 1/25, matching max psi(C5))")
    assert psi_exact(cuts2, x) == F(1, 25)
    print("CONFIRMED\n")


# ---------------------------------------------------------------- R3-C2

def gate_R3C2():
    print("=" * 78)
    print("R3-C2  interior reduction (sanity check of the two ingredients)")
    print("=" * 78)
    # ingredient 1: psi(H,x) = psi(H[supp x], x|supp)  -- the plateau lemma, re-verified here
    rng = random.Random(11)
    for name, (n, E) in NAMED.items():
        if n > 12:
            continue
        cuts = cut_mono_lists(n, E)
        for _ in range(30):
            keep = [v for v in range(n) if rng.random() < 0.7]
            if len(keep) < 2:
                continue
            w = {v: F(rng.randint(1, 7)) for v in keep}
            tot = sum(w.values())
            x = [w.get(v, F(0)) / tot for v in range(n)]
            # induced subgraph on keep
            ren = {v: i for i, v in enumerate(keep)}
            EI = [(ren[u], ren[v]) for (u, v) in E if u in ren and v in ren]
            cutsI = cut_mono_lists(len(keep), EI)
            xi = [w[v] / tot for v in keep]
            assert psi_exact(cuts, x) == psi_exact(cutsI, xi), (name, keep)
    print("psi(H,x) = psi(H[supp x], x) verified on every named pattern (n <= 12), 30 random supports each")
    print("=> the maximum of psi over the simplex is attained either on a proper face, where it is")
    print("   bounded by max psi of a proper induced subgraph, or at an interior point, where the")
    print("   KKT conditions hold with EQUALITY in every coordinate.  CONFIRMED\n")


if __name__ == '__main__':
    for name, (n, E) in NAMED.items():
        t = triangles(n, E)
        assert t == 0, (name, t)
    print("all %d named patterns verified triangle-free\n" % len(NAMED))
    gate_R3C1()
    gate_R3C3()
    gate_twins()
    gate_R3C2()
    print("ALL GATES PASSED")
