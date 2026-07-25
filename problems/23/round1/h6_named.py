"""H6: emit graph6 for named triangle-free graphs whose ASYMPTOTIC edge density
2m/N^2 lies inside the Balogh-Clemen-Lidicky open band (0.2486, 0.3197) -- the only
density window in which a counterexample to the Erdos n^2/25 conjecture can live.

Density is 2m/N^2 (the limit of |E|/C(n,2) along the blow-up family), because by the
blow-up identity a counterexample's whole blow-up family must stay in the band.
"""
import itertools

def to_g6(n, E):
    S = set(tuple(sorted(e)) for e in E)
    bits = [1 if (i, j) in S else 0 for j in range(1, n) for i in range(j)]
    while len(bits) % 6:
        bits.append(0)
    out = chr(n + 63)
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        out += chr(v + 63)
    return out

def has_triangle(n, E):
    adj = [0] * n
    for a, b in E:
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    return any(adj[a] & adj[b] for a, b in E)

G = {}

# C5
G["C5"] = (5, [(i, (i + 1) % 5) for i in range(5)])

# Petersen (Kneser K(5,2))
V = list(itertools.combinations(range(5), 2))
idx = {v: i for i, v in enumerate(V)}
G["Petersen"] = (10, [(idx[a], idx[b]) for a, b in itertools.combinations(V, 2)
                      if not set(a) & set(b)])

# Wagner / Moebius ladder M8 (sharpness example for Haggkvist's 3n/8 theorem)
G["WagnerV8"] = (8, [(i, (i + 1) % 8) for i in range(8)] + [(i, i + 4) for i in range(4)])

# Moebius ladders M_{2k} = C_{2k} + diagonals (triangle-free for 2k >= 6)
for k in (5, 6, 7, 8, 9, 10):
    n = 2 * k
    G[f"Moebius_M{n}"] = (n, [(i, (i + 1) % n) for i in range(n)] + [(i, i + k) for i in range(k)])

# Groetzsch = Mycielskian of C5
def mycielski(n, E):
    # vertices 0..n-1 original, n..2n-1 copies, 2n apex
    EE = list(E)
    for a, b in E:
        EE.append((a, n + b))
        EE.append((b, n + a))
    for i in range(n):
        EE.append((n + i, 2 * n))
    return 2 * n + 1, EE

G["Groetzsch"] = mycielski(*G["C5"])
G["Myc_Petersen"] = mycielski(*G["Petersen"])

# Clebsch graph = folded 5-cube: GF(2)^4, x~y iff x^y in {1,2,4,8,15}
CL = [(x, y) for x in range(16) for y in range(x + 1, 16) if (x ^ y) in (1, 2, 4, 8, 15)]
G["Clebsch16"] = (16, CL)

# triangle-free circulants (Ramsey-type)
def circ(n, S):
    E = set()
    for i in range(n):
        for s in S:
            j = (i + s) % n
            E.add(tuple(sorted((i, j))))
    return n, sorted(E)

G["C13(1,5)"] = circ(13, [1, 5])          # the (3,5) Ramsey graph
G["C16(1,2,7)"] = circ(16, [1, 2, 7])
G["C17(1,2,4,8)"] = circ(17, [1, 2, 4, 8])
G["C14(1,4,6)"] = circ(14, [1, 4, 6])
G["C18(1,4,7)"] = circ(18, [1, 4, 7])
G["C19(1,7,8)"] = circ(19, [1, 7, 8])
G["C20(1,4,7,9)"] = circ(20, [1, 4, 7, 9])
G["C11(1,3)"] = circ(11, [1, 3])
G["C12(1,5)"] = circ(12, [1, 5])
G["C15(1,4)"] = circ(15, [1, 4])
G["C16(1,7)"] = circ(16, [1, 7])
G["C20(1,4,9)"] = circ(20, [1, 4, 9])

LO, HI = 0.2486, 0.3197
print("# name  n  m  2m/n^2  in_BCL_band?  graph6")
keep = []
for name, (n, E) in G.items():
    E = sorted(set(tuple(sorted(e)) for e in E))
    if has_triangle(n, E):
        print(f"# {name}: HAS TRIANGLE - skipped")
        continue
    d = 2 * len(E) / n ** 2
    band = LO < d < HI
    g6 = to_g6(n, E)
    print(f"{name:16s} n={n:3d} m={len(E):4d} d={d:.4f} {'IN-BAND' if band else '       '}  {g6}")
    keep.append(g6)

with open("h6_named.g6", "w") as f:
    f.write("\n".join(keep) + "\n")
print(f"# wrote {len(keep)} graph6 lines to h6_named.g6")
