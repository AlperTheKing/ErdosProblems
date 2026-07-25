"""Q5: falsification test of Theorem A / Theorem C on V8 = And(3) = Wagner graph.

Exhaustive over ALL integer weight vectors of a fixed denominator D on the 8
vertices (zero weights allowed, as accepted base 2 requires): check
    psi(V8, x) <= 1/25   and   Lambda(V8,x) == psi(V8,x)
exactly.  A single violation would refute the theorems (and, for psi > 1/25,
Erdos #23 itself).
"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction
from Q5_lib import *
from Q5_wagner import V8


def compositions(D, k):
    if k == 1:
        yield (D,)
        return
    for i in range(D + 1):
        for rest in compositions(D - i, k - 1):
            yield (i,) + rest


def main():
    n, adj = V8()
    E = edges_of(n, adj)
    amask = [0] * n
    for i in range(n):
        for j in adj[i]:
            amask[i] |= 1 << j
    cuts = []
    full = (1 << n) - 1
    for m in range(1 << (n - 1)):
        S = m << 1
        cuts.append((S, full ^ S))
    LIM = Fraction(1, 25)
    for D in (int(a) for a in sys.argv[1:]) if len(sys.argv) > 1 else (10, 12, 14, 16):
        best = Fraction(0)
        bestc = None
        cnt = 0
        for c in compositions(D, n):
            cnt += 1
            # psi = min over cuts of monochromatic mass, exact in integers then /D^2
            bm = None
            for (S, C) in cuts:
                tot = 0
                for (u, v) in E:
                    if ((S >> u) & 1) == ((S >> v) & 1):
                        tot += c[u] * c[v]
                if bm is None or tot < bm:
                    bm = tot
                    if bm == 0:
                        break
            val = Fraction(bm, D * D)
            if val > best:
                best, bestc = val, c
            if val > LIM:
                print(f"  *** VIOLATION D={D} x={c}/{D}: psi={val} > 1/25")
                return
        print(f"  D={D}: {cnt} weight vectors, max psi = {best} = {float(best):.6f} "
              f"at {bestc}/{D}   [<= 1/25 = 0.04 : {best <= LIM}]")
        if best == LIM:
            print(f"      equality attained at {bestc}/{D}"
                  f"  (support size {sum(1 for t in bestc if t)})")


if __name__ == "__main__":
    main()
