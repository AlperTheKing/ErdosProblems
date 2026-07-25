"""R8: second-order behaviour on the flat (twin-splitting) cone, and Theorem A.

S1. On the flat cone the support graph is always a SUBGRAPH of a complete C5 blow-up
    (triangle-freeness forces it).  psi stays exactly 1/25 iff that subgraph is the
    COMPLETE blow-up; otherwise psi drops at second order at the exact rate
        max_i  Miss_i(d),   Miss_i(d) = sum over non-adjacent twin pairs (v,w),
                                        v a twin of class i, w a twin of class i+1, of d_v d_w.
S2. THEOREM A (local exactness ball).  H triangle-free, C an induced C5,
        T = {v notin C : N(v) cap C = {c_{i-1},c_{i+1}} for some i}   ("full twins"),
        R = V \ (C u T),  rho = x(R),  eta = x(V \ C).
    Then    psi(H,x) <= (1-rho)^2/25 + rho*eta.
    Corollary: psi <= 1/25 whenever 25*eta <= 2 - rho; in particular whenever eta <= 1/13,
    and unconditionally (any eta) when rho = 0.
"""
import sys, os, random, itertools
from fractions import Fraction as F
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from R8_stability_core import (Graph, C, blowup_C5, petersen, grotzsch, wagner, circle_graph,
                               K, psi_exact, cut_mono_masks, from_g6)

random.seed(4242)
OK = True


def report(tag, ok, extra=""):
    global OK
    OK = OK and ok
    print(f"[{'PASS' if ok else 'FAIL'}] {tag} {extra}")


# ------------------------------------------------------------------ S1
def build_twin_graph(missing_pairs):
    """C5 on 0..4 (cycle 0-1-2-3-4-0); v=5 is a full twin of 0 (adj 1,4);
       w=6 is a full twin of 1 (adj 0,2).  missing_pairs: set of twin-twin pairs to OMIT."""
    E = [(i, (i + 1) % 5) for i in range(5)]
    E += [(5, 1), (5, 4)]          # v twin of class 0
    E += [(6, 0), (6, 2)]          # w twin of class 1
    if (5, 6) not in missing_pairs:
        E.append((5, 6))
    return Graph(7, E, name="C5+twin0+twin1" + ("(missing vw)" if (5, 6) in missing_pairs else ""))


def S1():
    Hfull = build_twin_graph(set())
    Hmiss = build_twin_graph({(5, 6)})
    assert Hfull.is_triangle_free() and Hmiss.is_triangle_free()
    cf, cm = cut_mono_masks(Hfull), cut_mono_masks(Hmiss)
    ok_full = ok_miss = True
    rows = []
    for tnum in range(0, 6):
        for snum in range(0, 6):
            t, s = F(tnum, 30), F(snum, 30)
            x = [F(1, 5) - t, F(1, 5) - s, F(1, 5), F(1, 5), F(1, 5), t, s]
            vf, _ = psi_exact(Hfull, x, cf)
            vm, _ = psi_exact(Hmiss, x, cm)
            if vf != F(1, 25):
                ok_full = False
            if vm != F(1, 25) - t * s:
                ok_miss = False
            if tnum <= 2 and snum <= 2:
                rows.append((t, s, vf, vm, F(1, 25) - t * s))
    report("S1a complete twin structure => psi identically 1/25 on the flat cone", ok_full)
    report("S1b one missing twin-twin edge => psi = 1/25 - t*s EXACTLY (second-order drop)", ok_miss)
    print("     (t, s, psi_complete, psi_missing, 1/25 - t*s)")
    for r in rows[:9]:
        print("      ", r)

    # graph6 codes so the exact C++ grid engine can take the global maxima
    print(f"     g6(complete twin graph) = {Hfull.g6()}   g6(missing vw) = {Hmiss.g6()}")
    open("R8_twin7.g6", "w").write(Hfull.g6() + "\n" + Hmiss.g6() + "\n")


# ------------------------------------------------------------------ S2  (Theorem A)
def classify_C5(g, cyc):
    """Return (T_by_class, R) for the induced C5 `cyc`."""
    Cset = set(cyc)
    T = {i: [] for i in range(5)}
    R = []
    for v in range(g.n):
        if v in Cset:
            continue
        nb = set(u for u in cyc if (g.adj[v] >> u) & 1)
        assert len(nb) <= 2, "triangle-free + induced C5 forces <=2 neighbours in C"
        placed = False
        for m in range(5):
            if nb == {cyc[(m - 1) % 5], cyc[(m + 1) % 5]}:
                T[m].append(v)
                placed = True
                break
        if not placed:
            assert len(nb) <= 1
            R.append(v)
    return T, R


def thmA_bound(g, cyc, x):
    T, R = classify_C5(g, cyc)
    rho = sum(x[v] for v in R)
    eta = sum(x[v] for v in range(g.n) if v not in set(cyc))
    return (1 - rho) ** 2 / 25 + rho * eta, rho, eta


def S2():
    graphs = [C(5), blowup_C5([2, 2, 2, 2, 2]), blowup_C5([3, 1, 2, 2, 1]), blowup_C5([3, 3, 3, 3, 2]),
              petersen(), grotzsch(), wagner(), circle_graph(11), C(7), K(3, 3),
              build_twin_graph(set()), build_twin_graph({(5, 6)})]
    ok = True
    ok_cor = True
    tight = []
    for g in graphs:
        if g.n > 11:
            continue
        cycs = g.induced_C5s()
        if not cycs:
            continue
        cuts = cut_mono_masks(g)
        for cyc in cycs[:3]:
            for trial in range(400):
                # random weightings, biased towards concentrating on C
                x = [F(0)] * g.n
                mode = trial % 4
                for v in range(g.n):
                    if v in set(cyc):
                        x[v] = F(random.randint(4, 12), 1)
                    else:
                        x[v] = F(random.randint(0, [1, 2, 5, 12][mode]), 1)
                s = sum(x)
                if s == 0:
                    continue
                x = [xi / s for xi in x]
                val, _ = psi_exact(g, x, cuts)
                bnd, rho, eta = thmA_bound(g, cyc, x)
                if val > bnd:
                    ok = False
                    print("   ThmA VIOLATED", g.name, cyc, x, val, bnd)
                if 25 * eta <= 2 - rho:
                    if val > F(1, 25):
                        ok_cor = False
                        print("   ThmA corollary VIOLATED", g.name, cyc, x, val)
                    if val == F(1, 25):
                        tight.append((g.name, float(eta), float(rho)))
    report("S2a Theorem A: psi <= (1-rho)^2/25 + rho*eta", ok)
    report("S2b Corollary: 25*eta <= 2-rho  =>  psi <= 1/25", ok_cor)
    print(f"     tight instances (psi = 1/25) inside the certified region: {len(tight)}")
    if tight:
        mx = max(tight, key=lambda t: t[1])
        print(f"     largest certified eta with equality: {mx}")


# ------------------------------------------------------------------ S3: kill of naive
# quantitative monotonicity: C5[2] sits at psi = 1/25 EXACTLY yet is L1-distance 1 from
# every C5-concentration.
def S3():
    g = blowup_C5([2, 2, 2, 2, 2])
    cuts = cut_mono_masks(g)
    x = [F(1, 10)] * 10
    val, _ = psi_exact(g, x, cuts)
    best = None
    for cyc in g.induced_C5s():
        y = [F(0)] * 10
        for v in cyc:
            y[v] = F(1, 5)
        dist = sum(abs(x[i] - y[i]) for i in range(10))
        if best is None or dist < best:
            best = dist
    # also: distance to ANY C5-concentration in ANY triangle-free supergraph is >= this
    report("S3  C5[2] uniform: psi = 1/25 exactly", val == F(1, 25), f"psi={val}")
    print(f"     L1 distance from uniform-C5[2] to the nearest C5-concentration = {best} = {float(best)}")
    print("     => 'psi >= 1/25 - eps  implies  L1-dist to a C5-concentration <= f(eps)' is FALSE "
          "already at eps = 0 (f(0) would have to be >= 1, i.e. the maximum possible up to 8/5).")
    for N in (10, 20, 40, 100):
        print(f"     on C5[{N//5}] (N={N}) the distance is {F(2) - F(10, N)} = "
              f"{float(F(2) - F(10, N))}   -> 2 = the diameter of the simplex in L1.")


if __name__ == "__main__":
    S1(); S2(); S3()
    print("\nALL PASS" if OK else "\nSOME CHECK FAILED")
