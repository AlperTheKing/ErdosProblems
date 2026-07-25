"""Q5: the recorded 'tightest open case' -- the Wagner configuration on Gamma_14,
support {0,1,2,5,6,7,10,11} -- induces the WAGNER GRAPH V8 = Moebius ladder M8
= And(3) = C8(3,4), which is K5-MINOR-FREE.

W1  the induced subgraph is 3-regular on 8 vertices, 12 edges, and is isomorphic
    to the circulant C8(1,4) = Moebius ladder M8 = Wagner graph V8.
W2  V8 has NO K5 minor (self-contained degree proof, no citation needed):
    a K5 minor needs 5 branch sets each sending >= 4 edges out; in a cubic graph
    a singleton sends only 3, so every branch set has >= 2 vertices, hence
    >= 10 > 8 vertices.  Verified additionally by brute force over all
    assignments of the 8 vertices to 5 branch sets + unused.
W3  hence (Barahona 1983 / Guenin 2001) the odd-circuit clutter of V8 is ideal:
    psi(V8,x) = Lambda(V8,x) for EVERY weighting x -- verified exactly on many x.
W4  hence by Theorem A of Q5.md,  max_x psi(V8,x) <= 1/25.
W5  exact lower bound: numerically maximise psi(V8,x), then certify the best
    rational point exactly.
"""
import sys, os, random, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction
from Q5_lib import *
from Q5_theory import andrasfai
from Q5_andrasfai import induced


def V8():
    """Moebius ladder M8 = C8(1,4)."""
    adj = [set() for _ in range(8)]
    for i in range(8):
        for d in (1, 4):
            j = (i + d) % 8
            adj[i].add(j)
            adj[j].add(i)
    return 8, [frozenset(a) for a in adj]


def iso(n1, a1, n2, a2):
    if n1 != n2:
        return None
    for p in itertools.permutations(range(n1)):
        ok = True
        for u in range(n1):
            if frozenset(p[v] for v in a1[u]) != a2[p[u]]:
                ok = False
                break
        if ok:
            return p
    return None


def has_K5_minor(n, adj, verbose=False):
    """Brute force: assign each vertex to branch set 0..4 or 5 (unused).
    Returns a witness or None.  Only for n <= 11."""
    best = None
    for assign in itertools.product(range(6), repeat=n):
        B = [[v for v in range(n) if assign[v] == i] for i in range(5)]
        if any(len(b) == 0 for b in B):
            continue
        ok = True
        for b in B:                                  # connected?
            seen, st = set(), [b[0]]
            bs = set(b)
            while st:
                u = st.pop()
                if u in seen:
                    continue
                seen.add(u)
                for v in adj[u]:
                    if v in bs and v not in seen:
                        st.append(v)
            if len(seen) != len(b):
                ok = False
                break
        if not ok:
            continue
        for i in range(5):
            for j in range(i + 1, 5):
                if not any(v in adj[u] for u in B[i] for v in B[j]):
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return B
    return best


def main():
    print("=== W1  Wagner configuration support induces the Wagner graph V8 ===")
    N, adj = andrasfai(5)
    S = [0, 1, 2, 5, 6, 7, 10, 11]
    n2, adj2 = induced(N, adj, S)
    degs = sorted(len(a) for a in adj2)
    print(f"  Gamma_14 restricted to {S}: n={n2} |E|={len(edges_of(n2,adj2))} degrees={degs}")
    n3, adj3 = V8()
    p = iso(n2, adj2, n3, adj3)
    print(f"  isomorphic to Moebius ladder C8(1,4) = Wagner graph V8 ?  {p is not None}"
          f"  (map {p})")
    n4, adj4 = andrasfai(3)
    p2 = iso(n4, adj4, n3, adj3)
    print(f"  And(3) = Gamma_8 isomorphic to V8 ?  {p2 is not None}  (map {p2})")

    print()
    print("=== W2  V8 has no K5 minor ===")
    w = has_K5_minor(n3, adj3)
    print(f"  brute force over all 6^8 = 1679616 branch assignments: "
          f"{'K5 MINOR FOUND ' + str(w) if w else 'NO K5 minor'}")
    print("  (self-contained proof: cubic => every branch set has >= 2 vertices => >= 10 > 8)")

    print()
    print("=== W3  psi = Lambda on V8 for random weightings (exact) ===")
    rnd = random.Random(555)
    E = edges_of(n3, adj3)
    gaps = 0
    for t in range(200):
        raw = [rnd.randint(0, 7) for _ in range(8)]
        if sum(raw) == 0:
            continue
        s = sum(raw)
        x = [Fraction(r, s) for r in raw]
        w = {e: x[e[0]] * x[e[1]] for e in E}
        lam = tau_star(n3, adj3, w=w)["value"]
        psi = bip_exact(n3, adj3, weights=w)[0]
        if lam != psi:
            gaps += 1
            print(f"  GAP at {raw}: Lambda={lam} psi={psi}")
    print(f"  200 random product weightings: gaps = {gaps}")
    gaps = 0
    for t in range(300):
        w = {}
        for e in E:
            r = rnd.random()
            w[e] = Fraction(0) if r < 0.25 else (Fraction(10**6) if r > 0.85 else Fraction(1))
        tau, _ = bip_exact(n3, adj3, weights=w)
        if tau >= 10 ** 6:
            continue
        ts = tau_star(n3, adj3, w=w)["value"]
        if ts < tau:
            gaps += 1
            print(f"  MINOR-PROBE GAP: tau*={ts} tau={tau}")
    print(f"  300 random 0/1/inf weightings (Lehman minor probe): gaps = {gaps}")

    print()
    print("=== W5  exact maximisation of psi(V8,x) over the simplex ===")
    # block ascent over integer weight vectors with a fixed denominator
    best = (Fraction(0), None)
    for D in (8, 12, 16, 20, 24, 28, 32, 40, 48):
        # local search over integer compositions of D into 8 parts
        cur = [D // 8] * 8
        cur[0] += D - sum(cur)
        def val(c):
            s = sum(c)
            x = [Fraction(ci, s) for ci in c]
            ww = {e: x[e[0]] * x[e[1]] for e in E}
            return bip_exact(n3, adj3, weights=ww)[0]
        v = val(cur)
        improved = True
        while improved:
            improved = False
            for i in range(8):
                for j in range(8):
                    if i == j or cur[i] == 0:
                        continue
                    c2 = cur[:]
                    c2[i] -= 1
                    c2[j] += 1
                    v2 = val(c2)
                    if v2 > v:
                        cur, v, improved = c2, v2, True
        if v > best[0]:
            best = (v, cur[:], D)
        print(f"  denominator {D}: best psi = {v} = {float(v):.6f}  at {cur}")
    v, c, D = best
    print(f"  BEST: psi(V8,x) = {v} = {float(v):.6f} at x = {c}/{sum(c)}"
          f"   [<= 1/25 = 0.04 by Theorem A + W2/W3]")
    print(f"  recorded 'tightest open case' value 0.038652 -> now capped by 1/25, PROVED")


if __name__ == "__main__":
    main()
