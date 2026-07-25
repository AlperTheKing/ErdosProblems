"""Q5: is the odd-cycle clutter IDEAL on the Andrasfai family?

If yes (no odd-K5 minor), then by Guenin + Theorem A of Q5.md,
    max_x psi(And(k), x) = max_x Lambda(And(k), x) <= 1/25
which would close the Andrasfai half of the delta > N/3 reduction (base 8).

We test psi vs Lambda EXACTLY at
  - uniform x,
  - the recorded Wagner configuration on Gamma_14 = And(5), support {0,1,2,5,6,7,10,11},
  - many random rational product weights x_u x_v,
  - many random {0,1,inf} weights (Lehman minor probe -> idealness for all weights).
A single gap kills the route on that graph and (by Guenin) exhibits an odd-K5 minor.
"""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction
from Q5_lib import *
from Q5_theory import andrasfai

BIG = Fraction(10 ** 6)


def induced(n, adj, S):
    S = sorted(S)
    idx = {v: i for i, v in enumerate(S)}
    a = [set() for _ in S]
    for v in S:
        for u in adj[v]:
            if u in idx:
                a[idx[v]].add(idx[u])
    return len(S), [frozenset(x) for x in a]


def compare(n, adj, w, tag):
    lam = tau_star(n, adj, w=w)["value"]
    psi = bip_exact(n, adj, weights=w)[0]
    if lam != psi:
        print(f"    GAP {tag}: Lambda={lam} < psi={psi}  gap={psi-lam}")
    return lam, psi


def main():
    print("=== Andrasfai family: psi vs Lambda (exact) ===")
    for k in (2, 3, 4, 5, 6):
        N, adj = andrasfai(k)
        E = edges_of(N, adj)
        assert is_triangle_free(N, adj)
        x = [Fraction(1, N)] * N
        w = {e: x[e[0]] * x[e[1]] for e in E}
        lam, psi = compare(N, adj, w, f"And({k}) uniform")
        print(f"  And({k}): N={N} |E|={len(E)} deg={len(adj[0])}"
              f"  uniform: Lambda={lam}={float(lam):.6f}  psi={psi}={float(psi):.6f}"
              f"  ({'EQUAL' if lam == psi else 'GAP'})   1/25={0.04}")

    print()
    print("=== Wagner configuration on Gamma_14 = And(5), support {0,1,2,5,6,7,10,11} ===")
    N, adj = andrasfai(5)
    S = [0, 1, 2, 5, 6, 7, 10, 11]
    n2, adj2 = induced(N, adj, S)
    E2 = edges_of(n2, adj2)
    print(f"  induced subgraph: n={n2} |E|={len(E2)} tri-free={is_triangle_free(n2,adj2)}"
          f" edges={E2}")
    x = [Fraction(1, 8)] * 8
    w = {e: x[e[0]] * x[e[1]] for e in E2}
    lam, psi = compare(n2, adj2, w, "Wagner")
    print(f"  Wagner uniform-on-support: Lambda={lam} ({float(lam):.6f})"
          f"  psi={psi} ({float(psi):.6f})  recorded value 1/32={1/32:.6f}"
          f"  ({'EQUAL' if lam == psi else 'GAP'})")
    # also inside the full Gamma_14 (locality claim: must give the same Lambda)
    xf = [Fraction(0)] * N
    for v in S:
        xf[v] = Fraction(1, 8)
    wf = {e: xf[e[0]] * xf[e[1]] for e in edges_of(N, adj)}
    lam2 = tau_star(N, adj, w=wf)["value"]
    psi2 = bip_exact(N, adj, weights=wf)[0]
    print(f"  same weights inside the full Gamma_14: Lambda={lam2} psi={psi2}"
          f"  [locality Lambda(H,x)=Lambda(H[supp],x): {'OK' if lam2 == lam else 'FAILS'}]")

    print()
    print("=== random product weights ===")
    rnd = random.Random(20260725)
    for k in (3, 4, 5):
        N, adj = andrasfai(k)
        E = edges_of(N, adj)
        gaps = 0
        best = Fraction(0)
        T = 60 if k < 5 else 30
        for t in range(T):
            raw = [rnd.randint(0, 5) for _ in range(N)]
            if sum(raw) == 0:
                continue
            s = sum(raw)
            x = [Fraction(r, s) for r in raw]
            w = {e: x[e[0]] * x[e[1]] for e in E}
            lam, psi = compare(N, adj, w, f"And({k}) x={raw}")
            if lam != psi:
                gaps += 1
            if psi > best:
                best = psi
            assert lam <= Fraction(1, 25)
        print(f"  And({k}): {T} random product weights, gaps={gaps}, max psi seen={best}"
              f" ({float(best):.6f})")

    print()
    print("=== {0,1,inf} minor probe (Lehman: idealness for all w >= 0) ===")
    for k in (3, 4, 5):
        N, adj = andrasfai(k)
        E = edges_of(N, adj)
        gaps = 0
        T = 200 if k < 5 else 80
        for t in range(T):
            w = {}
            for e in E:
                r = rnd.random()
                w[e] = Fraction(0) if r < 0.25 else (BIG if r > 0.85 else Fraction(1))
            tau, _ = bip_exact(N, adj, weights=w)
            if tau >= BIG:
                continue
            ts = tau_star(N, adj, w=w)["value"]
            if ts < tau:
                gaps += 1
                print(f"    GAP And({k}) minor probe: tau*={ts} < tau={tau}")
                print(f"      w = { {str(a): str(b) for a, b in w.items()} }")
                if gaps >= 2:
                    break
        print(f"  And({k}): {T} random 0/1/inf weightings, gaps={gaps}")


if __name__ == "__main__":
    main()
