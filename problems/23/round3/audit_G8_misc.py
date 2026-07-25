"""AUDIT of G8 sections 4 (arc cuts), 6.1 (C5 certificate), 8 (rotation kernel).

(A) rotation-averaging kernel on Gamma:
    K(d) = 1-2d for 1/3 < d <= 1/2 (d = circular distance), 0 otherwise;
    B(mu) = sum_{u<v} K(d(u,v)) x_u x_v  is the arithmetic average, over a uniform
    random half-circle arc cut, of the monochromatic weight.
    The report claims max over the simplex = 1/20.  Tested exactly.

(B) arc-cut optimality on K_{p/k}: min over cyclic-interval cuts vs min over ALL cuts,
    exact Fractions, own random weightings (different seed / generator).

(C) the C5 sharp certificate of section 6.1, verified exactly by hand.
"""
import sys, random
from fractions import Fraction
import numpy as np


# ---------------------------------------------------------------- (A) kernel
def kernel(d):
    """d = circular distance in [0,1/2]; exact Fraction in, Fraction out."""
    if d > Fraction(1, 3) and d <= Fraction(1, 2):
        return 1 - 2 * d
    return Fraction(0)


def B_of_config(pos, mass):
    """pos: Fractions in [0,1); mass: Fractions summing to 1."""
    tot = Fraction(0)
    k = len(pos)
    for i in range(k):
        for j in range(i + 1, k):
            d = (pos[i] - pos[j]) % 1
            d = min(d, 1 - d)
            tot += kernel(d) * mass[i] * mass[j]
    return tot


def mc_check_kernel(pos, mass, nsteps=200000):
    """independent Monte-Carlo/quadrature check that B = E_theta[mono weight]."""
    pos = [float(p) for p in pos]
    mass = [float(m) for m in mass]
    k = len(pos)
    adj = [[False] * k for _ in range(k)]
    for i in range(k):
        for j in range(k):
            if i == j:
                continue
            d = abs(pos[i] - pos[j]) % 1.0
            d = min(d, 1 - d)
            adj[i][j] = d > 1.0 / 3
    tot = 0.0
    for t in range(nsteps):
        th = (t + 0.5) / nsteps
        inA = [((p - th) % 1.0) < 0.5 for p in pos]
        s = 0.0
        for i in range(k):
            for j in range(i + 1, k):
                if adj[i][j] and inA[i] == inA[j]:
                    s += mass[i] * mass[j]
        tot += s
    return tot / nsteps


# ---------------------------------------------------------------- (B) arc cuts
def kpk(k):
    p = 3 * k - 1
    E = [(i, j) for i in range(p) for j in range(i + 1, p)
         if k <= (j - i) % p <= p - k]
    return p, E


def min_all_cuts(p, E, x):
    best = None
    for mask in range(1 << (p - 1)):
        side = [0] + [(mask >> (v - 1)) & 1 for v in range(1, p)]
        s = sum(x[u] * x[v] for (u, v) in E if side[u] == side[v])
        if best is None or s < best:
            best = s
    return best


def min_arc_cuts(p, E, x):
    best = None
    for i in range(p):
        for m in range(1, p):
            side = [0] * p
            for t in range(m):
                side[(i + t) % p] = 1
            s = sum(x[u] * x[v] for (u, v) in E if side[u] == side[v])
            if best is None or s < best:
                best = s
    return best


if __name__ == "__main__":
    print("=== (A) rotation-averaging kernel on Gamma ===")
    # the report's claimed maximiser: 2 atoms at distance 2/5, mass 1/2
    pos = [Fraction(0), Fraction(2, 5)]
    mass = [Fraction(1, 2), Fraction(1, 2)]
    v = B_of_config(pos, mass)
    print(f"  report's point: 2 atoms at d=2/5, mass 1/2   B = {v} = {float(v):.6f}"
          f"   (mc {mc_check_kernel(pos,mass):.6f})")
    # uniform C5 measure
    pos5 = [Fraction(i, 5) for i in range(5)]
    m5 = [Fraction(1, 5)] * 5
    v5 = B_of_config(pos5, m5)
    print(f"  uniform C5 measure:                          B = {v5} = {float(v5):.6f}"
          f"   (mc {mc_check_kernel(pos5,m5):.6f})")
    # FALSIFIER: two atoms just past distance 1/3
    for dd in [Fraction(17, 50), Fraction(34, 100), Fraction(101, 300), Fraction(1001, 3000)]:
        pos2 = [Fraction(0), dd]
        vv = B_of_config(pos2, mass)
        print(f"  2 atoms at d={dd} ({float(dd):.5f}), mass 1/2:  B = {vv} = {float(vv):.8f}"
              f"   {'EXCEEDS 1/20' if vv > Fraction(1,20) else ''}")
    print(f"  1/20 = {float(Fraction(1,20)):.6f}   1/12 = {1/12:.6f}   1/25 = 0.04")
    # exhaustive over 5-point equally spaced support (where 1/20 does come from)
    best = Fraction(0)
    for w0 in range(0, 21):
        for w1 in range(0, 21 - w0):
            for w2 in range(0, 21 - w0 - w1):
                for w3 in range(0, 21 - w0 - w1 - w2):
                    w4 = 20 - w0 - w1 - w2 - w3
                    mm = [Fraction(t, 20) for t in (w0, w1, w2, w3, w4)]
                    b = B_of_config(pos5, mm)
                    if b > best:
                        best = b
    print(f"  max of B over measures supported on the 5 pentagon points (grid 1/20): "
          f"{best} = {float(best):.6f}   (= 1/20 = {Fraction(1,20)})")
    print()

    print("=== (B) arc-cut optimality, exact Fractions, own trials ===")
    rng = random.Random(20260725)
    for k in (2, 3, 4, 5):
        p, E = kpk(k)
        trials = 120 if p <= 11 else 30
        bad = 0
        for t in range(trials):
            w = [rng.randint(0, 9) for _ in range(p)]
            if sum(w) == 0:
                continue
            tot = sum(w)
            x = [Fraction(wi, tot) for wi in w]
            a = min_all_cuts(p, E, x)
            b = min_arc_cuts(p, E, x)
            if a != b:
                bad += 1
                if bad <= 2:
                    print(f"   K_{{{p}/{k}}} ARC GAP  x={[str(t) for t in x]} all={a} arc={b}")
        print(f"   K_{{{p}/{k}}}: {trials} exact rational trials, arc-cut failures = {bad}")
        sys.stdout.flush()
    print()

    print("=== (C) the C5 certificate of section 6.1, exact ===")
    C5E = [(i, (i + 1) % 5) for i in range(5)]
    atoms = []
    for i in range(5):
        A = {i}
        Bs = {(i + 1) % 5}
        # the cut whose unique mono edge is (i,i+1)
        found = None
        for mask in range(1 << 4):
            side = [0] + [(mask >> (v - 1)) & 1 for v in range(1, 5)]
            mono = [tuple(sorted(e)) for e in C5E if side[e[0]] == side[e[1]]]
            if sorted(mono) == [tuple(sorted((i, (i + 1) % 5)))]:
                found = (side, mono)
                break
        atoms.append((A, Bs, found))
        assert found is not None, i
    accA = [Fraction(0)] * 5
    accB = [Fraction(0)] * 5
    w = Fraction(1, 5)
    for (A, Bs, found) in atoms:
        side, mono = found
        for (u, v) in mono:
            assert (u in A and v in Bs) or (v in A and u in Bs), (u, v, A, Bs)
        for v in A:
            accA[v] += w
        for v in Bs:
            accB[v] += w
    print(f"   A-marginals {accA}  B-marginals {accB}  sum w = {5*w}")
    print(f"   valid sharp certificate: {all(t==Fraction(1,5) for t in accA+accB) and 5*w==1}")
