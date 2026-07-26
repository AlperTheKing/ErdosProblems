"""Self-test of the R9 library against values that are known independently."""
from fractions import Fraction as F
from R9_oddk5_lib import *

ok = True
def chk(name, got, want):
    global ok
    good = (got == want)
    ok &= good
    print(("PASS " if good else "FAIL ") + name, "got", got, "want", want)

# --- C5
c5 = Cn(5)
chk("bip(C5)", bip(c5), 1)
r = Lambda(c5); verify_Lambda(c5, r)
chk("Lambda(C5)", r['value'], F(1))
x = [F(1, 5)] * 5
chk("psi(C5,unif)", psi(c5, x), F(1, 25))
chk("LambdaX(C5,unif)", LambdaX(c5, x)['value'], F(1, 25))
chk("oddgirth(C5)", odd_girth(c5), 5)

# --- K4, K5, K6, K7 : bip = C(n,2)-floor(n^2/4), Lambda = m/3
for n in (4, 5, 6, 7):
    g = Kn(n)
    want_bip = n * (n - 1) // 2 - (n * n) // 4
    chk(f"bip(K{n})", bip(g), want_bip)
    r = Lambda(g); verify_Lambda(g, r)
    chk(f"Lambda(K{n})", r['value'], F(n * (n - 1), 6))

# --- Petersen  (weakly bipartite: no odd-K5 minor  =>  bip = Lambda)
pet_edges = [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] + \
            [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
pet = G(10, pet_edges)
chk("Petersen n,m,tf", (pet.n, pet.m, pet.triangle_free()), (10, 15, True))
chk("bip(Petersen)", bip(pet), 3)
r = Lambda(pet); verify_Lambda(pet, r)
chk("Lambda(Petersen)", r['value'], F(3))
chk("oddgirth(Petersen)", odd_girth(pet), 5)

# --- Wagner / Moebius-Kantor V8 = C8(1,4) = And(3)
v8 = G(8, [(i, (i + 1) % 8) for i in range(8)] + [(i, i + 4) for i in range(4)])
chk("V8 tf", v8.triangle_free(), True)
chk("bip(V8)", bip(v8), 2)
r = Lambda(v8); verify_Lambda(v8, r)
chk("Lambda(V8)", r['value'], F(2))
chk("psi(V8,unif)=1/32", psi(v8, [F(1, 8)] * 8), F(1, 32))

# --- twice-subdivided K5: the round's reference object, psi=4/625, Lambda=2/375
s5, paths = subdivide(Kn(5), 2)
chk("subK5 (n,m,tf,oddgirth)", (s5.n, s5.m, s5.triangle_free(), odd_girth(s5)), (25, 30, True, 9))
chk("bip(subK5)", bip(s5), 4)
r = Lambda(s5); verify_Lambda(s5, r)
chk("Lambda(subK5)", r['value'], F(10, 3))
xu = [F(1, 25)] * 25
chk("psi(subK5,unif)", F(4, 625), F(bip(s5), 625))
chk("Lambda(subK5,unif)", r['value'] / 625, F(2, 375))

print("\nALL PASS" if ok else "\nSOME FAILED")
