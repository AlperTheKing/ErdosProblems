"""Smoke tests for the INDEPENDENT audit library (own decoder / own bip / own tau*)."""
from fractions import Fraction as F
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round7")
from audit_Q5_lib import (g6, g6_encode, E_of, tri_free, induced, bip, psi, emass,
                          all_cycles, tau_star_exact, C5n, circulant, andrasfai, V8,
                          petersen, grotzsch, Kn, subdiv3, NAMED_G6)

ok = True


def chk(name, got, want):
    global ok
    good = (got == want)
    ok &= good
    print(f"  {'OK ' if good else 'FAIL'} {name}: got {got} want {want}")


print("== graph6 round trip ==")
for nm, s in NAMED_G6.items():
    n, A = g6(s)
    chk(f"{nm} reencode", g6_encode(n, A), s)
    print(f"      {nm}: N={n} |E|={len(E_of(n,A))} trianglefree={tri_free(n,A)}")

print("== bip smoke ==")
n, A = C5n(1)
chk("bip(C5)", bip(n, A)[0], 1)
chk("bip(K5)", bip(*Kn(5))[0], 4)
chk("bip(K4)", bip(*Kn(4))[0], 2)
chk("bip(Petersen)", bip(*petersen())[0], 3)
chk("bip(C5[2])", bip(*C5n(2))[0], 4)
chk("bip(C5[3])", bip(*C5n(3))[0], 9)
n, A = C5n(1)
chk("bip(C5) bipartite-check on C4", bip(*circulant(4, [1]))[0], 0)

print("== odd cycle enumeration ==")
n, A = Kn(5)
cyc = all_cycles(n, A, only_odd=True)
chk("K5 odd cycles (10 tri + 12 C5)", len(cyc), 22)
chk("K5 all cycles", len(all_cycles(n, A, only_odd=False)), 37)

print("== tau* smoke ==")
v, z, y, C = tau_star_exact(*Kn(5))
chk("tau*(K5)", v, F(10, 3))
v, z, y, C = tau_star_exact(*C5n(1))
chk("tau*(C5)", v, F(1))
v, z, y, C = tau_star_exact(*petersen())
chk("tau*(Petersen)", v, F(3))

print("\nSMOKE", "PASS" if ok else "FAIL")
