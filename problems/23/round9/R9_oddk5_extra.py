"""R9: (a) pin bip(M22) harder, (b) odd-K5 minor status of C5 blow-ups,
(c) the odd-girth-5 gap ceiling 5/2 and the spectral family."""
from fractions import Fraction as F
from R9_oddk5_lib import G, bip, odd_girth, maxcut_local, cut_value, Cn
import R9_oddk5_srg as S
import R9_oddk5_minor as MIN
import sys, time

def blowup(g, t):
    E = []
    for (a, b) in g.E:
        for i in range(t):
            for j in range(t):
                E.append((a * t + i, b * t + j))
    return G(g.n * t, E)

if __name__ == "__main__":
    print("(a) M22: pinning bip between the spectral bound and the best cut found")
    g = S.m22_graph()
    best = 0
    t0 = time.time()
    for seed in range(1, 40):
        c, side = maxcut_local(g, iters=60, seed=seed)
        assert c == cut_value(g, side)
        if c > best:
            best = c
            print(f"    seed {seed}: cut {c}  -> bip <= {g.m - c}   ({time.time()-t0:.0f}s)")
            sys.stdout.flush()
    lb = 193
    print(f"    final: bip(M22) in [{lb}, {g.m-best}]   Lambda = {F(g.m,5)} "
          f"  gap in [{F(lb)/F(g.m,5)}, {F(g.m-best)/F(g.m,5)}]")
    print(f"    psi(uniform) in [{F(lb,77*77)}, {F(g.m-best,77*77)}] vs 1/25 = {F(1,25)}")

    print()
    print("(b) odd-K5 minor status of C5 blow-ups")
    for t in (1, 2, 3):
        g = blowup(Cn(5), t)
        t0 = time.time()
        try:
            f = MIN.has_odd_k5_minor(g)
            print(f"    C5[{t}]: n={g.n} m={g.m} odd-K5 minor = {f}   ({time.time()-t0:.0f}s)")
        except Exception as e:
            print(f"    C5[{t}]: n={g.n} failed: {e}")
        sys.stdout.flush()
