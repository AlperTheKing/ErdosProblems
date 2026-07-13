# adversarial hunt for the APS frontier: maximize slope (1-y)/(1-x) over triangle-free
# graphs, where x = 25*beta/N^2, y = 3125*Rbest/N^5, Rbest = max over max cuts of the
# anchored-pentagon count.  EXACT arithmetic (Fractions) for all recorded values.
import random, json
from fractions import Fraction
from itertools import combinations

def tf_ok(adj, u, v):
    return adj[u] & adj[v] == 0 and not (adj[u] >> v) & 1

def maxcut_masks(n, adj, cap=20000):
    full = (1 << n) - 1
    best = -1
    masks = []
    for m in range(1 << (n - 1)):
        comp = full ^ m
        c = 0
        mm = m
        while mm:
            b = mm & -mm
            c += (adj[b.bit_length() - 1] & comp).bit_count()
            mm ^= b
        if c > best:
            best = c
            masks = [m]
        elif c == best and len(masks) < cap:
            masks.append(m)
    return best, masks

def R_of_cut(n, edges, adj, m):
    full = (1 << n) - 1
    comp = full ^ m
    tot = 0
    for u, v in edges:
        su = (m >> u) & 1
        if su != ((m >> v) & 1):
            continue
        opp = m if su == 0 else comp
        X = adj[u] & opp
        Y = adj[v] & opp
        for z in range(n):
            tot += (adj[z] & X).bit_count() * (adj[z] & Y).bit_count()
    return tot

def eval_graph(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    mc, masks = maxcut_masks(n, adj)
    beta = len(edges) - mc
    R = 0
    for m in masks[:4000]:
        r = R_of_cut(n, edges, adj, m)
        if r > R:
            R = r
    x = Fraction(25 * beta, n * n)
    y = Fraction(3125 * R, n ** 5)
    slope = None
    if x < 1 and beta > 0:
        slope = (1 - y) / (1 - x)
    return beta, R, x, y, slope

def circulant_edges(n, D):
    E = set()
    for i in range(n):
        for d in D:
            E.add((min(i, (i + d) % n), max(i, (i + d) % n)))
    return sorted(E)

def circ_tf(n, D):
    S = set()
    for d in D:
        S.add(d % n)
        S.add((-d) % n)
    for a in S:
        for b in S:
            if (a + b) % n in S:
                return False
    return True

def scan_circulants():
    print("== circulant scan ==", flush=True)
    tops = []
    for n in range(10, 19):
        cap_d = 3 if n <= 17 else 2
        cands = []
        for k in range(2, cap_d + 1):
            for D in combinations(range(1, n // 2 + 1), k):
                if circ_tf(n, D):
                    cands.append(D)
        for D in cands:
            E = circulant_edges(n, D)
            beta, R, x, y, slope = eval_graph(n, E)
            if beta > 0 and slope is not None and slope > Fraction(5, 2):
                tops.append((float(slope), n, D, beta, R, str(x), str(y)))
                print("  C%d%s beta=%d R=%d x=%s y=%s slope=%.4f" % (n, D, beta, R, x, y, float(slope)), flush=True)
    tops.sort(reverse=True)
    return tops

def hill_climb(n, seed, steps=1500):
    rnd = random.Random(seed)
    # start from a random maximal TF graph
    adj = [0] * n
    edges = set()
    pairs = list(combinations(range(n), 2))
    rnd.shuffle(pairs)
    for (u, v) in pairs:
        if tf_ok(adj, u, v):
            adj[u] |= 1 << v
            adj[v] |= 1 << u
            edges.add((u, v))
    cur = eval_graph(n, sorted(edges))
    cur_slope = cur[4] if cur[4] is not None else Fraction(0)
    best = (cur_slope, sorted(edges), cur)
    for step in range(steps):
        # random move: toggle one edge (keep TF), occasionally two
        moves = 1 if rnd.random() < 0.7 else 2
        newE = set(edges)
        newadj = adj[:]
        ok = True
        for _ in range(moves):
            if newE and rnd.random() < 0.5:
                e = rnd.choice(sorted(newE))
                newE.discard(e)
                newadj[e[0]] &= ~(1 << e[1])
                newadj[e[1]] &= ~(1 << e[0])
            else:
                u, v = rnd.sample(range(n), 2)
                u, v = min(u, v), max(u, v)
                if tf_ok(newadj, u, v):
                    newadj[u] |= 1 << v
                    newadj[v] |= 1 << u
                    newE.add((u, v))
                else:
                    ok = False
                    break
        if not ok or not newE:
            continue
        beta, R, x, y, slope = eval_graph(n, sorted(newE))
        if beta == 0 or slope is None:
            continue
        if x >= 1:
            if y < 1:
                print("  !!! x>=1 with y<1: CE to nonlinear form? beta=%d R=%d x=%s y=%s" % (beta, R, x, y), flush=True)
            continue
        # simulated-annealing-ish acceptance on slope
        if slope >= cur_slope or rnd.random() < 0.02:
            edges, adj, cur_slope = newE, newadj, slope
            if slope > best[0]:
                best = (slope, sorted(edges), (beta, R, x, y, slope))
    return best

def main():
    tops = scan_circulants()
    print("top circulant slopes:", [(t[0], "C%d%s" % (t[1], t[2])) for t in tops[:8]], flush=True)

    print("== hill climb (slope maximization) ==", flush=True)
    overall = None
    for n in (12, 13, 14):
        for s in range(4):
            b = hill_climb(n, 7000 + 13 * n + s, steps=1200)
            beta, R, x, y, slope = b[2]
            print("n=%d seed%d: slope=%.4f beta=%d R=%d x=%s y=%s e=%d" % (n, s, float(b[0]), beta, R, x, y, len(b[1])), flush=True)
            if overall is None or b[0] > overall[0]:
                overall = (b[0], n, b[1], b[2])
    print("HILL BEST slope=%.5f n=%d beta=%d R=%d x=%s y=%s" % (float(overall[0]), overall[1], overall[3][0], overall[3][1], overall[3][2], overall[3][3]), flush=True)
    with open("hunt_best.json", "w") as f:
        json.dump({"slope": str(overall[0]), "n": overall[1], "edges": overall[2],
                   "beta": overall[3][0], "R": overall[3][1],
                   "x": str(overall[3][2]), "y": str(overall[3][3])}, f)
    print("HUNT DONE", flush=True)

if __name__ == "__main__":
    main()
