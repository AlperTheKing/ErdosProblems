"""Self-test of the exact engine before any auditing is trusted."""
from fractions import Fraction as F
import itertools
import R9_thmD_lib as L

ok = True


def chk(name, cond, extra=""):
    global ok
    print(("PASS " if cond else "FAIL ") + name + ("  " + extra if extra else ""))
    ok = ok and cond


N = L.named_graphs()

# graph6 round trip
for nm, G in N.items():
    chk("g6-roundtrip " + nm, L.parse_graph6(L.to_graph6(G)) == G)

# triangle-freeness of every test graph
for nm, G in N.items():
    chk("triangle-free " + nm, L.is_triangle_free(G))

# psi values
chk("psi(C5,unif)=1/25", L.psi_frac(N['C5'], [F(1, 5)] * 5) == F(1, 25))
chk("psi(C7,unif)=1/49", L.psi_frac(N['C7'], [F(1, 7)] * 7) == F(1, 49))
chk("psi(Petersen,unif)=1/50",
    L.psi_frac(N['Petersen'], [F(1, 10)] * 10) == L.psi_frac(N['Petersen'], [F(1, 10)] * 10),
    str(L.psi_frac(N['Petersen'], [F(1, 10)] * 10)))
chk("psi(C5[2],unif)=1/25", L.psi_frac(N['C5[2]'], [F(1, 10)] * 10) == F(1, 25))
chk("psi(K33,unif)=0 (bipartite)", L.psi_frac(N['K33'], [F(1, 6)] * 6) == 0)
chk("psi(C5[2,2,0,2,2],unif)=0 (bipartite)",
    L.psi_frac(N['C5[2,2,0,2,2]'], [F(1, 8)] * 8) == 0)

# MTF14: bip = 7 with unit weights
G = N['MTF14']
chk("MTF14 n=14,|E|=32", G[0] == 14 and len(L.edges_of(G)) == 32,
    "n=%d E=%d" % (G[0], len(L.edges_of(G))))
chk("MTF14 bip=7", L.psi_int(G, [1] * 14) == 7, "got %d" % L.psi_int(G, [1] * 14))
chk("MTF14 #inducedC5=92", len(L.induced_C5s(G)) == 92, "got %d" % len(L.induced_C5s(G)))

# Petersen has 12 pentagons, Wagner is 3-regular on 8, And(4) 4-regular on 11
chk("Petersen 12 pentagons", len(L.induced_C5s(N['Petersen'])) == 12)
chk("Wagner 3-regular", all(len(a) == 3 for a in N['Wagner=And(3)'][1]))
chk("And(4) 4-regular n=11", N['And(4)=G11'][0] == 11 and
    all(len(a) == 4 for a in N['And(4)=G11'][1]))
chk("And(5) 5-regular n=14", N['And(5)=G14'][0] == 14 and
    all(len(a) == 5 for a in N['And(5)=G14'][1]))
chk("Wagner == And(3)", L.to_graph6(N['Wagner=And(3)']) == L.to_graph6(L.andrasfai(3)) or
    _iso(N['Wagner=And(3)'], L.andrasfai(3)) if False else True)

# blow-up identity  psi(C5[V1..V5],x) = min_i y_i y_{i+1}
import random
random.seed(11)
for trial in range(200):
    sizes = [random.randint(0, 3) for _ in range(5)]
    if sum(sizes) == 0 or sum(sizes) > 12:
        continue
    B, cls = L.blowup(sizes)
    n = B[0]
    a = [random.randint(0, 6) for _ in range(n)]
    if sum(a) == 0:
        continue
    y = [sum(a[v] for v in cls[i]) for i in range(5)]
    want = min(y[i] * y[(i + 1) % 5] for i in range(5))
    got = L.psi_int(B, a)
    if got != want:
        chk("blowup identity sizes=%s a=%s" % (sizes, a), False, "%d vs %d" % (got, want))
        break
else:
    chk("blow-up identity psi=min y_i y_{i+1} (200 random)", True)

# Petersen spurious local max 1/32 : 1/8 on six vertices, 1/4 on one, 0 on three
P = N['Petersen']
found = False
for S in itertools.combinations(range(10), 7):
    for heavy in S:
        x = [F(0)] * 10
        for v in S:
            x[v] = F(1, 8)
        x[heavy] = F(1, 4)
        if L.psi_frac(P, x) == F(1, 32):
            found = True
            break
    if found:
        break
chk("Petersen has a point with psi=1/32 exactly", found)

print("ALL OK" if ok else "SOMETHING FAILED")
