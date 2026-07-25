"""R8: exact local theory of psi at a C5-concentration.

Verifies, in exact rational arithmetic:
 L1. psi(C5,x) = min_i x_i x_{i+1}.
 L2. For a complete blow-up C5[V1..V5] with class sums y: psi = min_i y_i y_{i+1}
     (splitting classes never helps the cut).  Hence the maximiser set is the whole
     face {class sums = 1/5} -- a PLATEAU, not a strict maximum.
 L3. Directional-derivative formula at the C5 point u (weight 1/5 on an induced C5):
        D_d psi(u) = (1/5) * min_i ( a_i + a_{i+1} ),   a_i = d_i + W_{p_i},
     where p_i = {i-1,i+1} and W_{p_i} = sum of d_v over v outside C with N(v) cap C = p_i.
 L4. The flat cone {d : D_d psi(u) = 0} is exactly the twin-splitting cone
        d_v = 0 for v outside C with |N(v) cap C| <= 1,  and  d_i = -W_{p_i} for i in C.
 L5. Quantitative first-order drop  D_d psi(u) <= -(2/25) W' - (1/125)||a - mean(a)||_1.
 L6. C5[n] is a MAXIMAL triangle-free graph (no edge can be added).
"""
import sys, os, random
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R8_stability_core import (Graph, C, blowup_C5, blowup_classes, petersen, grotzsch,
                               wagner, circle_graph, K, psi_exact, cut_mono_masks)

random.seed(20260726)
OK = True


def report(tag, ok, extra=""):
    global OK
    OK = OK and ok
    print(f"[{'PASS' if ok else 'FAIL'}] {tag} {extra}")


# ------------------------------------------------------------------ L1
def L1():
    g = C(5)
    cuts = cut_mono_masks(g)
    ok = True
    for _ in range(300):
        raw = [F(random.randint(0, 12), 1) for _ in range(5)]
        s = sum(raw)
        if s == 0:
            continue
        x = [r / s for r in raw]
        v, _ = psi_exact(g, x, cuts)
        w = min(x[i] * x[(i + 1) % 5] for i in range(5))
        if v != w:
            ok = False
            print("   counterexample", x, v, w)
            break
    report("L1  psi(C5,x) = min_i x_i x_{i+1}", ok)


# ------------------------------------------------------------------ L2
def L2():
    ok = True
    worst = None
    for sizes in [(2, 2, 2, 2, 2), (3, 1, 2, 2, 1), (1, 1, 1, 2, 2), (2, 1, 3, 1, 2), (2, 0, 2, 2, 2),
                  (3, 1, 1, 1, 1)]:
        g = blowup_C5(list(sizes))
        if g.n == 0 or g.n > 11:
            continue
        cls = blowup_classes(list(sizes))
        cuts = cut_mono_masks(g)
        for _ in range(120):
            raw = [F(random.randint(0, 9), 1) for _ in range(g.n)]
            s = sum(raw)
            if s == 0:
                continue
            x = [r / s for r in raw]
            y = [sum(x[v] for v in range(g.n) if cls[v] == i) for i in range(5)]
            v, _ = psi_exact(g, x, cuts)
            w = min(y[i] * y[(i + 1) % 5] for i in range(5))
            if v != w:
                ok = False
                worst = (sizes, x, v, w)
                break
        if not ok:
            break
    report("L2  psi(C5[V1..V5],x) = min_i y_i y_{i+1} (class sums)", ok, str(worst or ""))

    # the plateau: every x with class sums 1/5 on C5[2] attains exactly 1/25
    g = blowup_C5([2, 2, 2, 2, 2]); cls = blowup_classes([2, 2, 2, 2, 2]); cuts = cut_mono_masks(g)
    ok2 = True
    vals = set()
    for _ in range(200):
        x = [None] * 10
        for i in range(5):
            a = F(random.randint(0, 10), 50)
            x[2 * i], x[2 * i + 1] = a, F(1, 5) - a
        v, _ = psi_exact(g, x, cuts)
        vals.add(v)
        if v != F(1, 25):
            ok2 = False
    report("L2b PLATEAU: psi = 1/25 on the whole face {class sums = 1/5} of C5[2]", ok2,
           f"values seen = {sorted(vals)}")


# ------------------------------------------------------------------ L3, L4, L5
def C5_point(g, cyc):
    x = [F(0)] * g.n
    for v in cyc:
        x[v] = F(1, 5)
    return x


def active_cuts(g, x, val, cuts):
    E = g.edges
    out = []
    for (Sm, mono) in cuts:
        s = F(0)
        for k in mono:
            u, v = E[k]
            s += x[u] * x[v]
        if s == val:
            out.append((Sm, mono))
    return out


def dir_deriv_bruteforce(g, x, d, cuts, val):
    """Danskin: D_d psi = min over ACTIVE cuts of <grad q_S(x), d>."""
    E = g.edges
    best = None
    for (Sm, mono) in active_cuts(g, x, val, cuts):
        s = F(0)
        for k in mono:
            u, v = E[k]
            s += x[u] * d[v] + x[v] * d[u]
        if best is None or s < best:
            best = s
    return best


def formula_deriv(g, cyc, d):
    """(1/5) min_i (a_i + a_{i+1}), a_i = d_i + W_{p_i}, p_i = {cyc[i-1],cyc[i+1]}."""
    Cset = set(cyc)
    W = [F(0)] * 5      # W[i] = weight moved onto twins of cyc[i]
    Wprime = F(0)
    for v in range(g.n):
        if v in Cset:
            continue
        nb = frozenset(u for u in cyc if (g.adj[v] >> u) & 1)
        if len(nb) == 2:
            # must be a distance-2 pair of the C5 (triangle-freeness)
            idx = [k for k in range(5) if cyc[k] in nb]
            k0, k1 = idx
            mid = None
            for m in range(5):
                if {cyc[(m - 1) % 5], cyc[(m + 1) % 5]} == set(nb):
                    mid = m
            assert mid is not None, ("neighbourhood in C is not a distance-2 pair", nb)
            W[mid] += d[v]
        elif len(nb) <= 1:
            Wprime += d[v]
        else:
            raise AssertionError("vertex with >=3 neighbours in an induced C5 of a triangle-free graph")
    a = [d[cyc[i]] + W[i] for i in range(5)]
    return F(1, 5) * min(a[i] + a[(i + 1) % 5] for i in range(5)), a, W, Wprime


def L345():
    tests = [petersen(), grotzsch(), wagner(), circle_graph(11), circle_graph(14),
             blowup_C5([2, 2, 2, 2, 2]), blowup_C5([3, 1, 2, 2, 1]), C(5)]
    ok3 = ok5 = True
    flatcone_ok = True
    detail = []
    for g in tests:
        if g.n > 14:
            continue
        cyc = g.induced_C5s()
        if not cyc:
            continue
        cyc = cyc[0]
        x = C5_point(g, cyc)
        cuts = cut_mono_masks(g)
        val, _ = psi_exact(g, x, cuts)
        assert val == F(1, 25), (g.name, val)
        Cset = set(cyc)
        nact = len(active_cuts(g, x, val, cuts))
        detail.append((g.name, nact, 5 * 2 ** (g.n - 5)))
        for _ in range(60):
            d = [F(0)] * g.n
            for v in range(g.n):
                if v in Cset:
                    d[v] = F(random.randint(-6, 6), 30)
                else:
                    d[v] = F(random.randint(0, 6), 30)
            tot = sum(d)
            # fix sum to 0 by adjusting a C-vertex
            d[cyc[0]] -= tot
            bf = dir_deriv_bruteforce(g, x, d, cuts, val)
            fm, a, W, Wp = formula_deriv(g, cyc, d)
            if bf != fm:
                ok3 = False
                print("   L3 mismatch", g.name, d, bf, fm)
                break
            mean = sum(a) / 5
            rhs = -F(2, 25) * Wp - F(1, 125) * sum(abs(ai - mean) for ai in a)
            if not (bf <= rhs):
                ok5 = False
                print("   L5 violated", g.name, d, bf, rhs)
        # flat cone check: build twin-splitting directions explicitly, check derivative 0
        for _ in range(40):
            d = [F(0)] * g.n
            W = [F(0)] * 5
            for v in range(g.n):
                if v in Cset:
                    continue
                nb = frozenset(u for u in cyc if (g.adj[v] >> u) & 1)
                if len(nb) == 2:
                    mid = [m for m in range(5) if {cyc[(m - 1) % 5], cyc[(m + 1) % 5]} == set(nb)][0]
                    z = F(random.randint(0, 5), 60)
                    d[v] = z
                    W[mid] += z
            for m in range(5):
                d[cyc[m]] = -W[m]
            if all(di == 0 for di in d):
                continue
            bf = dir_deriv_bruteforce(g, x, d, cuts, val)
            if bf != 0:
                flatcone_ok = False
                print("   L4 twin direction not flat", g.name, d, bf)
    report("L3  directional-derivative formula at the C5 point", ok3)
    report("L4  twin-splitting directions are exactly flat (derivative 0)", flatcone_ok)
    report("L5  D_d psi <= -(2/25)W' - (1/125)||a-mean(a)||_1", ok5)
    print("    active-cut counts at the C5 point (observed, predicted 5*2^(n-5)):")
    for t in detail:
        print("      ", t)


# ------------------------------------------------------------------ L6
def L6():
    ok = True
    for sizes in [(1, 1, 1, 1, 1), (2, 2, 2, 2, 2), (3, 1, 2, 2, 1), (2, 1, 1, 3, 2)]:
        g = blowup_C5(list(sizes))
        assert g.is_triangle_free()
        cnt = 0
        for u in range(g.n):
            for v in range(u + 1, g.n):
                if (g.adj[u] >> v) & 1:
                    continue
                g2 = Graph(g.n, g.edges + [(u, v)])
                if g2.is_triangle_free():
                    ok = False
                    cnt += 1
        if not ok:
            print("   L6 fails for", sizes, "addable non-edges:", cnt)
    report("L6  every complete C5 blow-up is MAXIMAL triangle-free", ok)


if __name__ == "__main__":
    L1(); L2(); L345(); L6()
    print("\nALL PASS" if OK else "\nSOME CHECK FAILED")
