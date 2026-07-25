"""audit_Q1_falsifier.py -- audit of the R1 claim (Grotzsch kills the neighbourhood-union
cut certificate) and of the surrounding exact values.  Everything exact.

Checks:
 A. decode J?BD@g]Qvo?, confirm n=11, |E|=20, triangle-free, iso to M(C5)
 B. bip = 4 (own subset-DP maxcut), fam over ALL unions = 5, #distinct unions
 C. the blow-up a = (1,1,1,1,1,2,2,2,2,2,2): bip and fam, cross-checked against an
    EXPLICIT 17-vertex blow-up (brute force over all 2^17 cuts) -- this also re-verifies base 1
 D. the "attained ONLY at (0,0,0,0,0,t,t,t,t,t,0)" claim of section 7:
    enumerate ALL induced C5 of the Grotzsch graph and evaluate 25*bip/W^2 on each
    concentration
 E. novelty: does the RECORDED Wagner configuration on Gamma_14 already kill the
    neighbourhood-UNION family?  (if yes, R1 is not a new obstruction)
 F. tightness of the union family on C5[n] and Petersen
"""
from fractions import Fraction
from itertools import combinations
from audit_Q1_core import (g6, edges, trianglefree, bip, fam_union, fam_union_weighted,
                           bip_weighted, induced_c5, blowup_edges, bip_edgelist, eS_table)

G6F = "J?BD@g]Qvo?"
OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)


# ------------------------------------------------------------------ A
say("=== A. identify the falsifier ===")
n, adj = g6(G6F)
E = edges(n, adj)
deg = [bin(adj[i]).count("1") for i in range(n)]
say(f"n={n} |E|={len(E)} triangle-free={trianglefree(n,adj)} degrees={sorted(deg)}")
say(f"degree by index: {deg}")


def mycielski_c5():
    a = [0] * 11
    def add(x, y):
        a[x] |= 1 << y
        a[y] |= 1 << x
    for i in range(5):
        add(i, (i + 1) % 5)             # u_i cycle
    for i in range(5):
        add(5 + i, (i - 1) % 5)
        add(5 + i, (i + 1) % 5)
        add(10, 5 + i)
    return 11, a


def iso(n1, a1, n2, a2):
    from itertools import permutations
    d1 = [bin(a1[i]).count("1") for i in range(n1)]
    d2 = [bin(a2[i]).count("1") for i in range(n2)]
    if sorted(d1) != sorted(d2):
        return None
    order = sorted(range(n1), key=lambda v: (d1[v], -sum(1 for u in range(n1) if a1[v] >> u & 1)))
    mp, used = {}, set()

    def rec(k):
        if k == n1:
            return True
        u = order[k]
        for w in range(n2):
            if w in used or d2[w] != d1[u]:
                continue
            if all(((a1[u] >> x & 1) == (a2[w] >> mp[x] & 1)) for x in order[:k]):
                mp[u] = w
                used.add(w)
                if rec(k + 1):
                    return True
                used.discard(w)
                del mp[u]
        return False
    return dict(mp) if rec(0) else None


n2, adj2 = mycielski_c5()
mp = iso(n, adj, n2, adj2)
say(f"isomorphic to Mycielskian(C5)=Grotzsch: {mp is not None}   map={mp}")
if mp:
    inv = {v: k for k, v in mp.items()}
    say(f"  g6 index of the apex (M(C5) vertex 10) = {inv[10]}")
    say(f"  g6 indices of the C5 (M(C5) 0..4)      = {[inv[i] for i in range(5)]}")
    say(f"  g6 indices of the shadows (M(C5) 5..9) = {[inv[i] for i in range(5,10)]}")

# ------------------------------------------------------------------ B
say("\n=== B. bip and the neighbourhood-union family ===")
b = bip(n, adj)
fv, fI, fU = fam_union(n, adj)
uniq = len({eval("0") if False else u for u in
            [__import__("functools").reduce(lambda x, y: x | y,
                                            [adj[v] for v in range(n) if I >> v & 1], 0)
             for I in range(1 << n)]})
say(f"bip = {b}   (target n^2/25 = {Fraction(n*n,25)} = {Fraction(121,25)})")
say(f"fam over ALL unions of neighbourhoods = {fv}, witness I={bin(fI)}, N(I)={sorted(v for v in range(n) if fU>>v&1)}")
say(f"#distinct union sets = {uniq}")
say(f"25*fam - n^2 = {25*fv - n*n}   (>0 means the certificate exceeds the 1/25 target)")
say(f"exact: truth = {Fraction(b,121)}, certificate = {Fraction(fv,121)}, 1/25 = {Fraction(1,25)}")
say(f"       certificate - 1/25 = {Fraction(fv,121)-Fraction(1,25)};  1/25 - truth = {Fraction(1,25)-Fraction(b,121)}")

# ------------------------------------------------------------------ C
say("\n=== C. the weighted blow-up a=(1,1,1,1,1,2,2,2,2,2,2) ===")
a_report = (1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2)
bw, argS = bip_weighted(n, adj, a_report)
fw, argI = fam_union_weighted(n, adj, a_report)
W = sum(a_report)
say(f"labelling used by Q1.md: indices 0..4 shadows, 5..9 C5, 10 apex  ->  a={a_report}, W={W}")
say(f"bip(H[a]) (min over ALL 2^11 cuts of H, base 1) = {bw}     25*bip = {25*bw} vs W^2 = {W*W}")
say(f"fam(H[a]) over all unions                       = {fw}     25*fam = {25*fw} vs W^2 = {W*W}")
say(f"exact: truth = {Fraction(bw,W*W)}, certificate = {Fraction(fw,W*W)}, 1/25 = {Fraction(1,25)}")
say(f"       overshoot factor certificate/(W^2/25) = {Fraction(25*fw,W*W)}")
# explicit 17-vertex blow-up, independent of base 1
N17, E17 = blowup_edges(n, adj, a_report)
b17 = bip_edgelist(N17, E17)
say(f"EXPLICIT blow-up: N={N17}, |E|={len(E17)}, bip by brute force over all 2^{N17} cuts = {b17}"
    f"   agrees with base-1 value: {b17 == bw}")

# also the OTHER natural labelling (0..4 = C5, 5..9 = shadows) to check for a labelling slip
if mp:
    a_alt = [0] * 11
    for i in range(5):
        a_alt[inv[i]] = 2        # C5 vertices weight 2
    for i in range(5, 10):
        a_alt[inv[i]] = 1        # shadows weight 1
    a_alt[inv[10]] = 2           # apex weight 2
    bw2, _ = bip_weighted(n, adj, a_alt)
    fw2, _ = fam_union_weighted(n, adj, a_alt)
    say(f"structure-based vector a={tuple(a_alt)} (C5=2, shadows=1, apex=2): bip={bw2}, fam={fw2}, W={sum(a_alt)}")

# ------------------------------------------------------------------ D
say("\n=== D. the 'max 25*bip/W^2 = 1 attained ONLY at (0,0,0,0,0,t,t,t,t,t,0)' claim ===")
c5s = induced_c5(n, adj)
say(f"number of induced C5 in the Grotzsch graph = {len(c5s)}")
ones = []
for S in c5s:
    a = [0] * n
    for v in S:
        a[v] = 5
    bb, _ = bip_weighted(n, adj, a)
    Wc = sum(a)
    if 25 * bb == Wc * Wc:
        ones.append((tuple(a), bb, Wc))
say(f"concentrations on an induced C5 with weight 5 each: {len(ones)} of them attain 25*bip/W^2 = 1 exactly")
for t in ones[:6]:
    say(f"   a={t[0]}  bip={t[1]}  W={t[2]}  25*bip/W^2 = {Fraction(25*t[1], t[2]*t[2])}")
say(f"claim 'only at (0,0,0,0,0,5,5,5,5,5,0)' is therefore {'TRUE' if len(ones)==1 else 'FALSE'} "
    f"({len(ones)} distinct maximisers at W=25)")

# ------------------------------------------------------------------ E
say("\n=== E. novelty: does the recorded Wagner witness already kill the UNION family? ===")
# Gamma_14: vertices 0..13 on R/Z, i~j iff circular distance > 1/3
nw = 14
adjw = [0] * nw
for i in range(nw):
    for j in range(i + 1, nw):
        d = min((j - i) % nw, (i - j) % nw)
        if Fraction(d, nw) > Fraction(1, 3):
            adjw[i] |= 1 << j
            adjw[j] |= 1 << i
Ew = edges(nw, adjw)
say(f"Gamma_14: |E|={len(Ew)}, triangle-free={trianglefree(nw,adjw)}, degrees={sorted(bin(adjw[i]).count('1') for i in range(nw))}")
supp = [0, 1, 2, 5, 6, 7, 10, 11]
x = [Fraction(1, 8) if v in supp else Fraction(0) for v in range(nw)]
# true psi at this x
best = None
for S in range(1 << nw):
    val = sum(x[u] * x[v] for (u, v) in Ew if ((S >> u) & 1) == ((S >> v) & 1))
    if best is None or val < best:
        best = val
say(f"true psi at the Wagner point = {best}  (recorded value 1/32 = {Fraction(1,32)}) -> match {best==Fraction(1,32)}")
# single neighbourhood values m(b)
mb = {}
for bvx in range(nw):
    S = adjw[bvx]
    mb[bvx] = sum(x[u] * x[v] for (u, v) in Ew if ((S >> u) & 1) == ((S >> v) & 1))
say(f"m(b) over support points: {[str(mb[v]) for v in supp]}  (recorded 3/64 = {Fraction(3,64)})")
fwag, argw = fam_union_weighted(nw, adjw, x)
say(f"min over ALL neighbourhood-UNION cuts of Gamma_14 at the Wagner point = {fwag}")
say(f"  1/25 = {Fraction(1,25)};  union family exceeds 1/25 : {fwag > Fraction(1,25)}")
say(f"  => the recorded Wagner witness ALREADY kills the union family: {fwag > Fraction(1,25)}")

# ------------------------------------------------------------------ F
say("\n=== F. calibration of the union family on C5[n] and Petersen ===")
n5, adj5 = g6("DUW")
say(f"C5 g6=DUW edges={edges(n5,adj5)} triangle-free={trianglefree(n5,adj5)}")
for t in range(1, 7):
    a = (t,) * 5
    bb, _ = bip_weighted(n5, adj5, a)
    ff, _ = fam_union_weighted(n5, adj5, a)
    say(f"  C5[{t}]: bip={bb}=t^2? {bb==t*t}   fam={ff}   equal={bb==ff}   25*bip/W^2={Fraction(25*bb,(5*t)**2)}")
npg, adjpg = g6("IheA@GUAo")
say(f"Petersen: n={npg} |E|={len(edges(npg,adjpg))} triangle-free={trianglefree(npg,adjpg)} "
    f"bip={bip(npg,adjpg)} fam={fam_union(npg,adjpg)[0]} #inducedC5={len(induced_c5(npg,adjpg))}")

with open("audit_Q1_falsifier.out", "w") as f:
    f.write("\n".join(OUT) + "\n")
