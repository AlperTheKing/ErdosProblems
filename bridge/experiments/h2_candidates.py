import itertools
from h2_redteam import report, is_triangle_free, min5drop, beta_sub

def edgeset(edges):
    return sorted(set(tuple(sorted(e)) for e in edges))

# ---------- candidate constructions on 15 vertices ----------

def gp(m, k):
    # Generalized Petersen GP(m,k): outer 0..m-1 cycle, inner m..2m-1 with step k, spokes.
    n = 2*m
    E = []
    for i in range(m):
        E.append((i, (i+1)%m))            # outer cycle
        E.append((i, m+i))                # spoke
        E.append((m+i, m+(i+k)%m))        # inner
    return n, edgeset(E)

def cayley_z15(conn):
    n = 15
    E = []
    for v in range(15):
        for s in conn:
            E.append((v, (v+s)%15))
    return n, edgeset(E)

def c5_blowup_minus_matching(t):
    # C5[t] minus a perfect matching between consecutive parts (one matching per edge-class)
    n = 5*t
    E = []
    for i in range(5):
        j = (i+1)%5
        for a in range(t):
            for b in range(t):
                if a==b:  # remove the "diagonal" matching
                    continue
                E.append((i*t+a, j*t+b))
    return n, edgeset(E)

def two_c5_glued(t):
    # two C5 blow-ups sharing... build C5[2]=10 vtx + a C5 on remaining 5, glue by identifying
    # Actually: C5[3] is 15; instead take C5[2] (10v) disjoint-ish + C5 (5v) connected sparsely.
    # We'll do: C5[2] on 0..9, plus C5 on 10..14, plus a perfect matching 0-10,2-11,4-12,6-13,8-14
    E = []
    t=2
    for i in range(5):
        j=(i+1)%5
        for a in range(t):
            for b in range(t):
                E.append((i*t+a, j*t+b))
    # outer C5 on 10..14
    for i in range(5):
        E.append((10+i, 10+(i+1)%5))
    # connect: vertex 2i (first in part i) to 10+i
    for i in range(5):
        E.append((2*i, 10+i))
    return 15, edgeset(E)

def kneser_petersen_plus():
    # Petersen (10v) + C5 (5v) joined as a 5-blowup-ish? Just test Petersen + disjoint C5.
    E = []
    # Petersen: outer 0-4 cycle, inner 5-9 pentagram, spokes
    for i in range(5):
        E.append((i,(i+1)%5))
        E.append((i,5+i))
        E.append((5+i,5+(i+2)%5))
    # C5 on 10..14
    for i in range(5):
        E.append((10+i,10+(i+1)%5))
    return 15, edgeset(E)

def mobius_kantor_frag():
    # Mobius-Kantor is GP(8,3) (16v) - too big. Use GP(7,2)+isolated? GP(7,2)=14v + 1 isolated.
    n,E = gp(7,2)  # 14 vertices
    # add vertex 14 connected to make 15; attach to a few to spread beta
    E = list(E)
    E.append((14,0)); E.append((14,3)); E.append((14,5))
    return 15, edgeset(E)

def c15_cycle_plus_chords():
    # 15-cycle (bipartite-ish? odd so beta from chords). Add chords step 4 (odd-girth preserving)
    E = []
    for i in range(15):
        E.append((i,(i+1)%15))
    for i in range(15):
        E.append((i,(i+4)%15))
    return 15, edgeset(E)

def c5_blowup_322():
    # unbalanced C5 blow-up parts sizes 3,3,3,3,3 is balanced; try 3,3,3,3,3 minus partial
    # do parts 3,3,3,3,3 but make it a "twisted" blowup: connect i to i+1 AND i+2 mod 5 partially
    pass

def wagner_like():
    # Mobius-Kantor fragment: GP(8,3) has 16 v. Take subgraph on 15.
    m,k=8,3
    E=[]
    for i in range(m):
        E.append((i,(i+1)%m))
        E.append((i,m+i))
        E.append((m+i,m+(i+k)%m))
    E = [e for e in E if 15 not in e]  # drop vertex 15
    return 15, edgeset(E)

def cayley_z15_124():
    return cayley_z15([1,2,4])  # may have triangles, check

def cayley_z15_1_4():
    return cayley_z15([1,4])

def cayley_z15_2_3():
    return cayley_z15([2,3])

def cayley_z15_1_6():
    return cayley_z15([1,6])

def cayley_z15_4_6():
    return cayley_z15([4,6])

def cayley_z15_1_2_7():
    return cayley_z15([1,2,7])

def random_c5_transversal_blocked():
    # C5[3] but rewire so no induced C5 transversal removal helps: add edges WITHIN the
    # natural transversal structure to forbid the cheap removal. Take C5[3] and add a
    # "second layer" of C5's offset.
    t=3
    E=[]
    for i in range(5):
        j=(i+1)%5
        for a in range(t):
            for b in range(t):
                E.append((i*t+a,j*t+b))
    return 15, edgeset(E)  # placeholder = C5[3]

CANDS = [
    ("GP(7,2)+v14",) + mobius_kantor_frag(),
    ("Petersen+C5", ) + kneser_petersen_plus(),
    ("C5[3]-matching",) + c5_blowup_minus_matching(3),
    ("two_C5_glued",) + two_c5_glued(2),
    ("C15+chord4",) + c15_cycle_plus_chords(),
    ("MobiusKantor_frag(GP83-v15)",) + wagner_like(),
    ("Cayley_Z15[1,4]",) + cayley_z15_1_4(),
    ("Cayley_Z15[2,3]",) + cayley_z15_2_3(),
    ("Cayley_Z15[1,6]",) + cayley_z15_1_6(),
    ("Cayley_Z15[4,6]",) + cayley_z15_4_6(),
    ("Cayley_Z15[1,2,7]",) + cayley_z15_1_2_7(),
    ("Cayley_Z15[1,4,6]",) + cayley_z15([1,4,6]),
    ("Cayley_Z15[2,3,7]",) + cayley_z15([2,3,7]),
]

if __name__ == "__main__":
    results = []
    for name, n, E in CANDS:
        r = report(name, n, E)
        if r is not None:
            results.append((name, n, E, r))
    print("\n=== BREAKERS ===")
    for name,n,E,r in results:
        if r[3]:
            print(name, "beta=",r[0],"min5drop=",r[1])
