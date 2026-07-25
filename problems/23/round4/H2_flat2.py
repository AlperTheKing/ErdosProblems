"""H2_flat2.py -- inspect the 2-dimensional flat spaces at m=21, 39 and test the
second-order WSQ / ARC criteria on them exactly."""
import sys, itertools
from fractions import Fraction
from H2_core import edges, total_W, arcbound_fast
from H2_flat import flat_space


def show(m):
    d = flat_space(m)
    E, W0, S0, AB0, opt = d['E'], d['W0'], d['S0'], d['AB0'], d['opt']
    B = d['basis']
    print(f"--- m={m}  W0={W0} S0={S0} AB0={AB0} #opt={len(opt)} dim V={len(B)}")
    # integralise the basis
    Bi = []
    for v in B:
        den = 1
        for x in v:
            den = den * x.denominator // __import__('math').gcd(den, x.denominator)
        Bi.append([int(x * den) for x in v])
    for v in Bi:
        print("   basis:", v)
    # explore the 2-plane over integer coefficients
    best = None
    R = 6
    for c in itertools.product(range(-R, R + 1), repeat=len(Bi)):
        if all(x == 0 for x in c):
            continue
        h = [sum(c[i] * Bi[i][j] for i in range(len(Bi))) for j in range(m)]
        g = 0
        for x in h:
            g = __import__('math').gcd(g, abs(x))
        if g > 1:
            continue
        Wh = total_W(h, E)
        mm = min(sum(h[i] * h[j] for (i, j) in E if a[i] == a[j]) for a in opt)
        # WSQ second-order slack:  S0^2*mono - 2*W0*W(h) > 0  for all optimal arcs
        wsq = S0 * S0 * mm - 2 * W0 * Wh
        arc = mm            # ARC criterion: mono(A*,h) > 0 for all optimal arcs
        if best is None or wsq > best[0]:
            best = (wsq, arc, tuple(h), mm, Wh)
        if wsq > 0:
            print(f"   *** WSQ 2nd-ORDER VIOLATION h={h} min_mono={mm} W(h)={Wh}")
    print(f"   best over the plane: WSQ-slack={best[0]} (need >0), min_mono={best[3]},"
          f" W(h)={best[4]}\n     h={best[2]}")
    return d, Bi


if __name__ == "__main__":
    for m in ([int(x) for x in sys.argv[1:]] or [21, 39]):
        show(m)
