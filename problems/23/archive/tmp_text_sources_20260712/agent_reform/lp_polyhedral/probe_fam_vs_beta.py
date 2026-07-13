# Adversarial probe: hunt for non-bipartite triangle-free G where the union family
# misses beta (fam > beta), and especially where 25*fam > n^2 (Lemma W' falsifier).
import random
from lib import *

random.seed(0)
worst_gap = []
fails = []
tested = 0

def test(name, n, E):
    global tested
    if not E or not is_triangle_free(n, E) or is_bipartite(n, E):
        return
    tested += 1
    b, _ = beta_exact(n, E)
    fm, S, rkA, rkI, mA, mI = min_uncut_union_family(n, E)
    if fm is None:
        return
    if fm > b:
        worst_gap.append((name, n, len(E), b, fm))
        print(f"GAP fam>beta: {name} n={n} e={len(E)} beta={b} fam={fm}")
    if 25 * fm > n * n:
        fails.append((name, n, len(E), b, fm))
        print(f"*** LEMMA FAIL: {name} n={n} e={len(E)} beta={b} fam={fm} edges={E}")

# 1) bipartite-heavy hybrids: K_{a,b} with a C5 glued at a vertex / by an edge / disjoint
for a in (3, 5, 7):
    for b in (3, 5, 7):
        base = [(i, a + j) for i in range(a) for j in range(b)]
        n0 = a + b
        # disjoint C5
        E = base + [(n0 + i, n0 + (i + 1) % 5) for i in range(5)]
        test(f"K{a},{b}+C5 disjoint", n0 + 5, [(min(u, v), max(u, v)) for u, v in E])
        # C5 sharing one vertex (vertex 0)
        E = base + [(0, n0), (n0, n0 + 1), (n0 + 1, n0 + 2), (n0 + 2, n0 + 3), (0, n0 + 3)]
        test(f"K{a},{b}+C5 shared-v", n0 + 4, [(min(u, v), max(u, v)) for u, v in E])

# 2) random triangle-free with wide density mix
for trial in range(600):
    n = random.randint(6, 15)
    style = trial % 3
    if style == 0:
        nn, E = random_maximal_trianglefree(n, seed=trial)
    elif style == 1:
        m = random.randint(n, min(3 * n, n * n // 4))
        nn, E = random_trianglefree_sparse(n, m, seed=trial)
    else:
        sizes = [random.randint(0, 3) for _ in range(5)]
        if sum(sizes) == 0:
            continue
        nn, E = blowup(*cycle(5), sizes)
        extra = random.randint(0, 2)  # sprinkle deletions
        E = [e for i, e in enumerate(E) if random.random() > 0.1 * extra]
    test(f"rand{trial}", nn, E)

# 3) odd antiholes? no (triangles). Mobius-Kantor + chord etc.
n, E = gen_petersen(8, 3)  # Mobius-Kantor, bipartite -> add a C5 flap to make odd
E2 = list(E) + [(0, 16), (16, 17), (17, 1)]  # path making odd cycle? check tf
test("MK+flap", 18, [(min(u, v), max(u, v)) for u, v in E2])

print(f"probe done: tested={tested}, fam>beta cases={len(worst_gap)}, lemma failures={len(fails)}")
