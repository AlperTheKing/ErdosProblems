"""H2 (iii): emit a catalogue of named triangle-free bases in graph6.

Families: odd cycles, Andrasfai graphs, Petersen/Kneser K(5,2), Wagner V8,
Mobius-Kantor GP(8,3), Grotzsch, Chvatal, Clebsch (folded 5-cube), Ramsey
(3,k)-graphs, Mycielskians and generalised Mycielskians, Cayley graphs on
Z_5 x Z_m, Kneser K(2k+1,k), and circulants with small independence number.
"""
import sys, itertools
from h2_lib import *

CAT = []


def add(name, n, edges):
    edges = sorted({(min(a, b), max(a, b)) for a, b in edges if a != b})
    adj = edges_to_adj(n, edges)
    if not is_triangle_free(n, adj):
        return
    CAT.append((name, n, edges, g6_encode(n, adj)))


# --- cycles ---
for k in (5, 7, 9, 11, 13):
    add(f"C{k}", k, [(i, (i + 1) % k) for i in range(k)])

# --- Andrasfai graphs And(k) on 3k-1 vertices, S = {i : i = 1 mod 3} ---
for k in range(2, 8):
    n = 3 * k - 1
    S = [d % n for d in range(1, n) if d % 3 == 1]
    S = sorted({min(d, n - d) for d in S})
    n2, e = circulant(n, S)
    add(f"Andrasfai({k})_n{n}", n2, e)

# --- Petersen / Kneser ---
add("Petersen=K(5,2)", 10, PETERSEN_EDGES)


def kneser(m, k):
    V = list(itertools.combinations(range(m), k))
    idx = {v: i for i, v in enumerate(V)}
    E = [(idx[a], idx[b]) for a in V for b in V if a < b and not set(a) & set(b)]
    return len(V), E


for (m, k) in [(5, 2), (7, 3), (9, 4)]:
    n, e = kneser(m, k)
    if n <= 24:
        add(f"Kneser({m},{k})", n, e)

# --- Wagner V8 / Mobius-Kantor ---
n, e = wagner(); add("Wagner_V8", n, e)
n, e = mobius_kantor(); add("MobiusKantor_GP(8,3)", n, e)

# --- generalized Petersen GP(n,k) triangle-free ---
for nn in range(5, 12):
    for kk in range(1, nn // 2 + 1):
        e = [(i, (i + 1) % nn) for i in range(nn)]
        e += [(i, nn + i) for i in range(nn)]
        e += [(nn + i, nn + (i + kk) % nn) for i in range(nn)]
        if 2 * nn <= 22:
            add(f"GP({nn},{kk})", 2 * nn, e)

# --- Mycielskian ---
def mycielski(n, edges):
    # vertices 0..n-1 original, n..2n-1 shadows, 2n apex
    E = list(edges)
    for (u, v) in edges:
        E.append((u, n + v))
        E.append((v, n + u))
    for i in range(n):
        E.append((n + i, 2 * n))
    return 2 * n + 1, E


n, e = 5, C5_EDGES
n1, e1 = mycielski(n, e); add("Grotzsch=M(C5)_n11", n1, e1)
n2, e2 = mycielski(n1, e1)
if n2 <= 24:
    add(f"M(M(C5))_n{n2}", n2, e2)
n, e = 7, C7_EDGES
n1, e1 = mycielski(n, e); add("M(C7)_n15", n1, e1)
n1, e1 = mycielski(9, [(i, (i + 1) % 9) for i in range(9)]); add("M(C9)_n19", n1, e1)


# --- generalised Mycielskian mu_r(C5): r levels + apex ---
def gen_mycielski(n, edges, r):
    # levels 0..r-1 copies, apex
    V = r * n
    E = []
    for (u, v) in edges:
        E.append((u, v))
    for lev in range(r - 1):
        for (u, v) in edges:
            E.append((lev * n + u, (lev + 1) * n + v))
            E.append((lev * n + v, (lev + 1) * n + u))
    apex = V
    for i in range(n):
        E.append(((r - 1) * n + i, apex))
    return V + 1, E


for r in (2, 3, 4):
    nn, ee = gen_mycielski(5, C5_EDGES, r)
    if nn <= 22:
        add(f"genMyc_C5_r{r}_n{nn}", nn, ee)

# --- Chvatal graph (12 vertices, 4-regular, triangle-free, chi=4) ---
CHVATAL = [(0,1),(0,4),(0,6),(0,9),(1,2),(1,5),(1,7),(2,3),(2,6),(2,8),(3,4),(3,7),
           (3,9),(4,5),(4,8),(5,10),(5,11),(6,10),(6,11),(7,8),(7,11),(8,10),(9,10),(9,11)]
add("Chvatal_n12", 12, CHVATAL)

# --- Clebsch graph = folded 5-cube: V=GF(2)^4, join u~v iff u+v in {e1..e4, 1111} ---
def clebsch():
    diffs = [1, 2, 4, 8, 15]
    E = [(u, u ^ d) for u in range(16) for d in diffs]
    return 16, E


n, e = clebsch(); add("Clebsch_n16", n, e)

# --- Ramsey (3,k) critical circulants ---
add("C13(1,5)_R35", *circulant(13, [1, 5]))
for n, S in [(16, [1, 2, 4, 8]), (17, [1, 2, 4, 8]), (18, [1, 5, 8]),
             (21, [1, 2, 5, 8, 10]), (22, [1, 5, 8, 11]), (20, [1, 4, 6, 9])]:
    nn, ee = circulant(n, S)
    add(f"C{n}{tuple(S)}", nn, ee)

# --- all triangle-free circulants on n = 16..22 with small independence number
for n in range(15, 23):
    for r in range(1, 5):
        for S in itertools.combinations(range(1, n // 2 + 1), r):
            nn, ee = circulant(n, list(S))
            adj = edges_to_adj(nn, ee)
            if is_triangle_free(nn, adj):
                add(f"C{n}{S}", nn, ee)

# --- Cayley graphs on Z5 x Zm with connection set {(+-1,s)} u {(0,t)} ---
# triangle-free iff T cap (S-S) empty and Cayley(Zm,T) triangle-free
for m in range(2, 5):
    for Ssz in range(1, m + 1):
        for S in itertools.combinations(range(m), Ssz):
            SS = {(a - b) % m for a in S for b in S}
            for Tsz in range(0, 3):
                for T in itertools.combinations(range(1, m), Tsz):
                    Tsym = {t % m for t in T} | {(-t) % m for t in T}
                    if Tsym & SS:
                        continue
                    n = 5 * m
                    if n > 22:
                        continue
                    E = []
                    for a in range(5):
                        for b in range(m):
                            v = a * m + b
                            for s in S:
                                E.append((v, ((a + 1) % 5) * m + (b + s) % m))
                            for t in Tsym:
                                E.append((v, a * m + (b + t) % m))
                    add(f"Cay(Z5xZ{m},S={S},T={tuple(sorted(Tsym))})", n, E)

if __name__ == "__main__":
    out = open("h2_named.g6", "w")
    seen = set()
    for name, n, e, g6 in CAT:
        if g6 in seen:
            continue
        seen.add(g6)
        out.write(g6 + "\n")
        print(f"{g6}\t{name}\tn={n}\tm={len(e)}")
    out.close()
    print(f"# {len(seen)} distinct triangle-free bases written to h2_named.g6", file=sys.stderr)
