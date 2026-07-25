"""Q5 extra checks:
  C1  3-subdivision lemma on more graphs (bip and tau* invariant).
  C2  Theorem A stress test: Lambda(H,x) <= 1/25 on random triangle-free H
      (geng) with random rational x, exact.
  C3  quantitative form of Theorem B:  psi = 1/25 + eta  =>  Lambda <= 1/25 - eta/3
      and psi - Lambda >= 4 eta / 3.  (verified as an inequality chain on samples)
"""
import sys, os, random, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction
from Q5_lib import *
from Q5_theory import subdivide3
from Q5_g6 import g6_encode

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"
BIPEXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Q5_bip.exe")


def C1():
    print("=== C1  3-subdivision preserves bip and tau* ===")
    # only graphs whose 3-subdivision has N <= 26 (exhaustive cut enumeration)
    tests = [("C5", blowup_C5(1)), ("K4", (4, [frozenset(set(range(4)) - {i}) for i in range(4)])),
             ("K33", g6_decode("Ec_o")),
             ("K5", (5, [frozenset(set(range(5)) - {i}) for i in range(5)]))]
    for name, (n, adj) in tests:
        b0, _ = bip_exact(n, adj)
        t0 = tau_star(n, adj)["value"]
        n2, adj2 = subdivide3(n, adj)
        t2 = tau_star(n2, adj2)["value"]
        g6 = g6_encode(n2, adj2)
        out = subprocess.run([BIPEXE, g6], capture_output=True, text=True).stdout.strip()
        b2 = int(out.split("bip=")[1].split()[0])
        print(f"  {name}: bip {b0}->{b2}  tau* {t0}->{t2}  N {n}->{n2}"
              f"  tri-free(sub)={is_triangle_free(n2,adj2)}  [{'OK' if b0==b2 and t0==t2 else 'FAIL'}]")
        assert b0 == b2 and t0 == t2


def C2(nvert=9, samples=3, xtrials=4, seed=3):
    print(f"=== C2  Theorem A stress test on triangle-free graphs, N={nvert} ===")
    rnd = random.Random(seed)
    out = subprocess.run([GENG, "-q", "-t", "-c", str(nvert)], capture_output=True, text=True)
    gs = [g for g in out.stdout.split() if g]
    print(f"  geng produced {len(gs)} connected triangle-free graphs on {nvert} vertices")
    picks = rnd.sample(gs, min(samples, len(gs)))
    worst = Fraction(0)
    worstinfo = None
    for g6 in picks:
        n, adj = g6_decode(g6)
        assert is_triangle_free(n, adj)
        E = edges_of(n, adj)
        for t in range(xtrials):
            raw = [rnd.randint(0, 6) for _ in range(n)]
            if sum(raw) == 0:
                continue
            s = sum(raw)
            x = [Fraction(r, s) for r in raw]
            w = {e: x[e[0]] * x[e[1]] for e in E}
            lam = tau_star(n, adj, w=w)["value"]
            psi = bip_exact(n, adj, weights=w)[0]
            e = sum(w.values())
            assert lam <= psi, (g6, raw, "Lambda > psi")
            assert lam <= e / 5, (g6, raw, "Lambda > e/5")
            assert psi <= e - 4 * e * e, (g6, raw, "psi > e-4e^2")
            assert lam <= Fraction(1, 25), (g6, raw, "Lambda > 1/25 -- COUNTEREXAMPLE")
            if lam > worst:
                worst, worstinfo = lam, (g6, raw, s, psi, e)
    print(f"  all checks passed; max Lambda seen = {worst} ({float(worst):.6f}) <= 1/25 = 0.04")
    print(f"  attained at {worstinfo}")


def C3():
    print("=== C3  quantitative Theorem B (symbolic check of the two algebraic steps) ===")
    # step 1: eta > 0, psi = 1/25 + eta <= e - 4e^2  =>  1/5 - e >= 5 eta/3
    # since (3/5)s - 4s^2 >= eta with s = 1/5 - e implies s >= 5 eta / 3.
    from fractions import Fraction as F
    ok = True
    for num in range(1, 40):
        eta = F(num, 1000)
        # smallest s>0 with (3/5)s - 4 s^2 = eta ; check s >= 5 eta/3 numerically-exactly
        # solve 4s^2 - (3/5)s + eta = 0 -> s = (3/5 -/+ sqrt(9/25 - 16 eta))/8
        disc = F(9, 25) - 16 * eta
        if disc < 0:
            continue
        # s_small is the smaller root; verify (5 eta/3) <= s_small by checking the
        # quadratic is still positive-or-zero at 5eta/3, i.e. 4t^2-(3/5)t+eta >= 0 at t=5eta/3
        t = 5 * eta / 3
        val = 4 * t * t - F(3, 5) * t + eta
        if val < 0:
            ok = False
            print(f"  FAIL at eta={eta}: 4t^2-(3/5)t+eta = {val} < 0")
    print(f"  step 1 (1/5 - e >= 5*eta/3) holds on the sampled grid: {ok}")
    print("  step 2: Lambda <= e/5 <= (1/5 - 5eta/3)/5 = 1/25 - eta/3, so psi - Lambda >= 4eta/3")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "C1"):
        C1()
    if which in ("all", "C2"):
        C2()
    if which in ("all", "C3"):
        C3()
