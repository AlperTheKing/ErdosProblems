"""G10_corpus.py -- build the graph corpora consumed by G10_hunt.exe.

Output format (one graph per line):  name h E u1 v1 u2 v2 ...
"""
import sys, os, subprocess, random
from itertools import combinations
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from G10_core import (cycle, petersen, grotzsch, chvatal, circulant, andrasfai,
                      kneser, mycielski, is_triangle_free, is_maximal_triangle_free,
                      g6_to_edges, adjacency)

HERE = os.path.dirname(os.path.abspath(__file__))
GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"


def emit(fh, name, n, edges):
    es = sorted(set((min(u, v), max(u, v)) for u, v in edges))
    fh.write("%s %d %d %s\n" % (name, n, len(es), " ".join("%d %d" % e for e in es)))


def maximal_completion(n, edges):
    """Greedily add edges keeping triangle-freeness until maximal (only increases psi)."""
    es = set((min(u, v), max(u, v)) for u, v in edges)
    adj = [0] * n
    for u, v in es:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    random.shuffle(pairs)
    changed = True
    while changed:
        changed = False
        for (i, j) in pairs:
            if (i, j) in es:
                continue
            if adj[i] & adj[j]:
                continue
            es.add((i, j))
            adj[i] |= 1 << j
            adj[j] |= 1 << i
            changed = True
    return sorted(es)


# ---------------------------------------------------------------- named family
def named_graphs():
    out = []
    for k in range(2, 12):
        out.append(("C%d" % (2 * k + 1),) + cycle(2 * k + 1))
    out.append(("Petersen",) + petersen())
    out.append(("Grotzsch",) + grotzsch())
    out.append(("Chvatal",) + chvatal())
    out.append(("Mycielski_C7",) + mycielski(*cycle(7)))
    out.append(("Mycielski_P",) + mycielski(*petersen()))
    # Andrasfai
    for k in range(2, 9):
        out.append(("And%d" % k,) + andrasfai(k))
    # Kneser / Borsuk-type
    out.append(("Kneser52",) + kneser(5, 2))     # Petersen
    out.append(("Kneser72",) + kneser(7, 2))     # 21 vertices
    out.append(("Kneser73",) + kneser(7, 3))     # 35 vertices - big
    out.append(("Kneser83",) + kneser(8, 3))
    # triangle-free circulants on n <= 30
    for n in range(5, 31):
        for r in range(1, 5):
            for conn in combinations(range(1, n // 2 + 1), r):
                nn, ee = circulant(n, list(conn))
                if len(ee) == 0:
                    continue
                if is_triangle_free(nn, ee):
                    out.append(("Circ%d_%s" % (n, "-".join(map(str, conn))), nn, ee))
    return out


def cayley_nonabelian(maxord=30):
    """Cayley graphs on dihedral and a few other nonabelian groups of order <= 30."""
    res = []
    for m in range(3, maxord // 2 + 1):
        # dihedral group D_m of order 2m: elements (r,s) r in Z_m, s in {0,1}
        elems = [(r, s) for s in (0, 1) for r in range(m)]
        idx = {g: i for i, g in enumerate(elems)}

        def mul(x, y):
            r1, s1 = x
            r2, s2 = y
            if s1 == 0:
                return ((r1 + r2) % m, s2)
            return ((r1 - r2) % m, 1 - s2)
        # connection sets: unions of an involution class + rotations, closed under inverse
        cands = []
        for r in range(m):
            cands.append([(r, 1)])                      # reflections are involutions
        for r in range(1, m):
            cands.append([(r, 0), ((-r) % m, 0)])
        import itertools
        for k in (1, 2, 3):
            for combo in itertools.combinations(range(len(cands)), k):
                conn = []
                for c in combo:
                    conn.extend(cands[c])
                conn = list(dict.fromkeys(conn))
                if (0, 0) in conn:
                    continue
                n, e = None, None
                es = set()
                for g in elems:
                    for s in conn:
                        hh = mul(g, s)
                        i, j = idx[g], idx[hh]
                        if i != j:
                            es.add((min(i, j), max(i, j)))
                es = sorted(es)
                if not es:
                    continue
                if is_triangle_free(len(elems), es):
                    res.append(("D%d_%d" % (m, len(res)), len(elems), es))
    return res


def maximal_tf_from_geng(n, cap=None):
    """geng -t -c  ->  keep maximal triangle-free."""
    p = subprocess.Popen([GENG, "-tcq", str(n)], stdout=subprocess.PIPE)
    out = []
    for line in p.stdout:
        s = line.decode().strip()
        if not s:
            continue
        nn, ee = g6_to_edges(s)
        if is_maximal_triangle_free(nn, ee):
            out.append((nn, ee))
            if cap and len(out) >= cap:
                p.kill()
                break
    p.wait()
    return out


def random_maximal_tf(n, cnt, seed=0):
    rnd = random.Random(seed)
    res = []
    for t in range(cnt):
        random.seed(rnd.randrange(1 << 30))
        es = maximal_completion(n, [])
        res.append((n, es))
    return res


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'named':
        with open(os.path.join(HERE, 'G10_named.txt'), 'w') as fh:
            seen = set()
            for (nm, n, e) in named_graphs():
                if n > 24:
                    continue
                key = (n, tuple(sorted(set((min(u, v), max(u, v)) for u, v in e))))
                if key in seen:
                    continue
                seen.add(key)
                emit(fh, nm, n, e)
            for (nm, n, e) in cayley_nonabelian(30):
                if n > 24:
                    continue
                key = (n, tuple(sorted(set((min(u, v), max(u, v)) for u, v in e))))
                if key in seen:
                    continue
                seen.add(key)
                emit(fh, nm, n, e)
        print('named written')
    elif mode == 'mtf':
        lo, hi = int(sys.argv[2]), int(sys.argv[3])
        with open(os.path.join(HERE, 'G10_mtf_%d_%d.txt' % (lo, hi)), 'w') as fh:
            for n in range(lo, hi + 1):
                gs = maximal_tf_from_geng(n)
                print('n=%d maximal triangle-free: %d' % (n, len(gs)))
                for i, (nn, ee) in enumerate(gs):
                    emit(fh, 'mtf%d_%d' % (nn, i), nn, ee)
    elif mode == 'randmtf':
        lo, hi, cnt = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        with open(os.path.join(HERE, 'G10_randmtf.txt'), 'w') as fh:
            for n in range(lo, hi + 1):
                for i, (nn, ee) in enumerate(random_maximal_tf(n, cnt, seed=n * 7919)):
                    emit(fh, 'rmtf%d_%d' % (nn, i), nn, ee)
        print('random maximal tf written')
