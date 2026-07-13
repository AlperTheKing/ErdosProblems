# Blue-ball transport (discharging) check for Erdos #23 (beta <= N^2/25, triangle-free).
# FORM: fix an optimal cut (A,B). m(v)=mono-degree. Charge m(v)/2 per vertex, sum = beta.
# CLAIM (radius-r Hall/transport): charge can be redistributed so that every vertex holds
# <= N/25, moving charge only within blue(=cut-edge)-distance <= r.
# Feasibility <=> integer maxflow == 50*beta with supply 25*m(v), per-vertex cap 2N (all x50 scaled).
# Exact integer arithmetic throughout.
import sys, random, itertools
from collections import deque
import numpy as np

# ---------------- exact max-cut enumeration (vertex N-1 pinned to side 0) ----------------
def maxcut_enumerate(N, edges, cap_cuts=200):
    assert N <= 26
    total = 1 << (N - 1)
    chunk = 1 << 20
    best = -1
    # pass 1: find max
    for start in range(0, total, chunk):
        end = min(start + chunk, total)
        masks = np.arange(start, end, dtype=np.int64)
        cut = np.zeros(end - start, dtype=np.int64)
        for (i, j) in edges:
            bi = (masks >> i) & 1 if i < N - 1 else 0
            bj = (masks >> j) & 1 if j < N - 1 else 0
            cut += (bi ^ bj)
        m = int(cut.max())
        if m > best:
            best = m
    # pass 2: collect masks achieving best
    out = []
    for start in range(0, total, chunk):
        end = min(start + chunk, total)
        masks = np.arange(start, end, dtype=np.int64)
        cut = np.zeros(end - start, dtype=np.int64)
        for (i, j) in edges:
            bi = (masks >> i) & 1 if i < N - 1 else 0
            bj = (masks >> j) & 1 if j < N - 1 else 0
            cut += (bi ^ bj)
        w = np.nonzero(cut == best)[0]
        for x in w[: max(0, cap_cuts - len(out))]:
            out.append(int(masks[x]))
        if len(out) >= cap_cuts:
            break
    return best, out

def side_of(mask, N):
    return [ (mask >> v) & 1 if v < N - 1 else 0 for v in range(N) ]

# ---------------- Dinic (integers) ----------------
class Dinic:
    def __init__(self, n):
        self.n = n
        self.g = [[] for _ in range(n)]
    def add(self, u, v, cap):
        self.g[u].append([v, cap, len(self.g[v])])
        self.g[v].append([u, 0, len(self.g[u]) - 1])
    def bfs(self, s, t):
        self.level = [-1] * self.n
        self.level[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for e in self.g[u]:
                if e[1] > 0 and self.level[e[0]] < 0:
                    self.level[e[0]] = self.level[u] + 1
                    q.append(e[0])
        return self.level[t] >= 0
    def dfs(self, u, t, f):
        if u == t:
            return f
        while self.it[u] < len(self.g[u]):
            e = self.g[u][self.it[u]]
            v = e[0]
            if e[1] > 0 and self.level[v] == self.level[u] + 1:
                d = self.dfs(v, t, min(f, e[1]))
                if d > 0:
                    e[1] -= d
                    self.g[v][e[2]][1] += d
                    return d
            self.it[u] += 1
        return 0
    def maxflow(self, s, t):
        fl = 0
        while self.bfs(s, t):
            self.it = [0] * self.n
            while True:
                f = self.dfs(s, t, 10 ** 18)
                if f == 0:
                    break
                fl += f
        return fl
    def reachable(self, s):
        seen = [False] * self.n
        seen[s] = True
        q = deque([s])
        while q:
            u = q.popleft()
            for e in self.g[u]:
                if e[1] > 0 and not seen[e[0]]:
                    seen[e[0]] = True
                    q.append(e[0])
        return seen

# ---------------- Hall / transport check for one cut ----------------
def transport_check(N, adj, side, r):
    # mono degree
    m = [sum(1 for w in adj[v] if side[w] == side[v]) for v in range(N)]
    beta2 = sum(m)                       # = 2*beta
    supply = [25 * mv for mv in m]       # total = 50*beta
    cap = 2 * N                          # = 50*(N/25)
    # blue adjacency
    badj = [[w for w in adj[v] if side[w] != side[v]] for v in range(N)]
    # balls radius r
    balls = []
    for v in range(N):
        dist = {v: 0}
        q = deque([v])
        while q:
            u = q.popleft()
            if dist[u] == r:
                continue
            for w in badj[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    q.append(w)
        balls.append(sorted(dist.keys()))
    # flow net: 0 src, 1..N supply, N+1..2N recv, 2N+1 sink
    D = Dinic(2 * N + 2)
    src, sink = 0, 2 * N + 1
    for v in range(N):
        if supply[v] > 0:
            D.add(src, 1 + v, supply[v])
        D.add(N + 1 + v, sink, cap)
    for v in range(N):
        if supply[v] > 0:
            for w in balls[v]:
                D.add(1 + v, N + 1 + w, 10 ** 18)
    need = 25 * beta2
    fl = D.maxflow(src, sink)
    if fl == need:
        return True, None
    # extract violating S from min cut
    seen = D.reachable(src)
    S = [v for v in range(N) if supply[v] > 0 and seen[1 + v]]
    B = set()
    for v in S:
        B.update(balls[v])
    lhs = sum(m[v] for v in S)           # sum_S m(v)
    rhs_sets = len(B)
    # violation iff 25*lhs > 2N*|B|
    return False, (S, sorted(B), lhs, rhs_sets, need - fl)

# ---------------- graph zoo ----------------
def build_adj(N, edges):
    adj = [set() for _ in range(N)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    for a, b in edges:
        assert not (adj[a] & adj[b]), "triangle found"
    return [sorted(s) for s in adj]

def petersen():
    E = []
    for i in range(5):
        E.append((i, (i + 1) % 5))
        E.append((i, i + 5))
        E.append((i + 5, 5 + (i + 2) % 5))
    return 10, E

def grotzsch():
    E = []
    for i in range(5):
        E.append((i, (i + 1) % 5))
        E.append((5 + i, (i + 1) % 5))
        E.append((5 + i, (i - 1) % 5))
        E.append((5 + i, 10))
    return 11, E

def chvatal():
    E = [(0,1),(0,4),(0,6),(0,9),(1,2),(1,5),(1,7),(2,3),(2,6),(2,8),
         (3,4),(3,7),(3,9),(4,5),(4,8),(5,10),(5,11),(6,10),(6,11),
         (7,8),(7,11),(8,10),(9,10),(9,11)]
    return 12, E

def clebsch():
    verts = list(range(16))
    E = []
    for x in range(16):
        for y in range(x + 1, 16):
            w = bin(x ^ y).count("1")
            if w == 1 or w == 4:
                E.append((x, y))
    return 16, E

def mcgee():
    lcf = [12, 7, -7]
    E = set()
    for i in range(24):
        E.add(frozenset((i, (i + 1) % 24)))
        E.add(frozenset((i, (i + lcf[i % 3]) % 24)))
    return 24, [tuple(sorted(e)) for e in E]

def gp(n, k):
    E = []
    for i in range(n):
        E.append((i, (i + 1) % n))
        E.append((i, n + i))
        E.append((n + i, n + (i + k) % n))
    return 2 * n, list(set(tuple(sorted(e)) for e in E))

def blowup(base_edges, weights):
    # classes sized weights[i]
    offs = [0]
    for w in weights:
        offs.append(offs[-1] + w)
    N = offs[-1]
    E = []
    for (a, b) in base_edges:
        for x in range(offs[a], offs[a + 1]):
            for y in range(offs[b], offs[b + 1]):
                E.append((min(x, y), max(x, y)))
    return N, E

C5 = [(i, (i + 1) % 5) for i in range(5)]
C7 = [(i, (i + 1) % 7) for i in range(7)]

def rand_maximal_tf(N, seed):
    rng = random.Random(seed)
    pairs = [(i, j) for i in range(N) for j in range(i + 1, N)]
    rng.shuffle(pairs)
    adj = [set() for _ in range(N)]
    E = []
    for (i, j) in pairs:
        if not (adj[i] & adj[j]):
            adj[i].add(j); adj[j].add(i); E.append((i, j))
    return N, E

def rand_sparse_tf(N, target_e, seed):
    rng = random.Random(seed)
    adj = [set() for _ in range(N)]
    E = []
    tries = 0
    while len(E) < target_e and tries < 50 * target_e:
        tries += 1
        i, j = rng.randrange(N), rng.randrange(N)
        if i == j or j in adj[i]:
            continue
        if adj[i] & adj[j]:
            continue
        adj[i].add(j); adj[j].add(i); E.append((min(i, j), max(i, j)))
    return N, E

# ---------------- runner ----------------
def run_graph(name, N, edges, radii=(1, 2, 3), cap_cuts=200, verbose_fail=True):
    adj = build_adj(N, edges)
    e = len(edges)
    mc, masks = maxcut_enumerate(N, edges, cap_cuts=cap_cuts)
    beta = e - mc
    conj_ok = 25 * beta <= N * N
    line = f"{name}: N={N} e={e} maxcut={mc} beta={beta} 25beta={25*beta} N^2={N*N} conj={'OK' if conj_ok else 'VIOLATED'} cuts={len(masks)}{'+' if len(masks)==cap_cuts else ''}"
    print(line)
    results = {}
    for r in radii:
        feas = 0
        first_fail = None
        for mask in masks:
            side = side_of(mask, N)
            ok, cert = transport_check(N, adj, side, r)
            if ok:
                feas += 1
            elif first_fail is None:
                first_fail = (mask, cert)
        verdict = "ALL" if feas == len(masks) else ("SOME(%d/%d)" % (feas, len(masks)) if feas > 0 else "NONE")
        results[r] = (verdict, first_fail)
        msg = f"  r={r}: {verdict}"
        if first_fail and (verbose_fail or verdict == "NONE"):
            mask, (S, B, lhs, nb, defect) = first_fail
            msg += f" | viol S(|{len(S)}|) sum_m={lhs} ball={nb} need 25*{lhs}<={2*N}*{nb} i.e. {25*lhs}<={2*N*nb} defect50x={defect}"
        print(msg)
    sys.stdout.flush()
    return results

def stage_named():
    run_graph("petersen", *petersen())
    run_graph("grotzsch", *grotzsch())
    run_graph("chvatal", *chvatal())
    run_graph("clebsch", *clebsch())
    n, E = gp(7, 2)
    try:
        run_graph("GP(7,2)", n, E)
    except AssertionError:
        print("GP(7,2): has triangle, skipped")
    run_graph("GP(9,2)", *gp(9, 2))
    run_graph("C5", 5, C5)
    run_graph("C7", 7, [(i, (i + 1) % 7) for i in range(7)])

def stage_blowups():
    for w in [(1,1,1,1,1),(2,2,2,2,2),(3,3,3,3,3),(4,4,4,4,4)]:
        run_graph(f"C5blow{w}", *blowup(C5, list(w)))
    for w in [(1,1,1,1,2),(1,1,1,2,2),(1,1,2,2,2),(1,2,2,3,3),(2,2,3,3,3),
              (1,1,2,3,3),(1,3,1,3,1),(2,3,2,3,2),(1,1,1,3,3),(4,4,1,4,4),
              (1,4,4,1,4),(2,2,2,5,5),(1,1,4,4,4),(5,5,1,1,1),(3,4,3,4,3)]:
        run_graph(f"C5blow{w}", *blowup(C5, list(w)))
    run_graph("C7blow2", *blowup(C7, [2]*7))
    run_graph("petersen_blow2", *blowup(petersen()[1], [2]*10))

def stage_mcgee():
    run_graph("mcgee24", *mcgee(), cap_cuts=60)

def stage_blow5():
    run_graph("C5blow(5,5,5,5,5)", *blowup(C5, [5]*5), cap_cuts=12)

def stage_random():
    bad = 0
    for N in (10, 12, 14, 16):
        for seed in range(60):
            n, E = rand_maximal_tf(N, 1000 * N + seed)
            res = run_quiet(f"maxTF_N{N}_s{seed}", n, E)
            bad += res
    for N in (18, 20):
        for seed in range(15):
            n, E = rand_maximal_tf(N, 1000 * N + seed)
            res = run_quiet(f"maxTF_N{N}_s{seed}", n, E)
            bad += res
    for N in (12, 14, 16, 18):
        for seed in range(40):
            n, E = rand_sparse_tf(N, (N * N) // 5, 7000 * N + seed)
            res = run_quiet(f"spTF_N{N}_s{seed}", n, E)
            bad += res
    print(f"RANDOM BATTERY DONE bad_r2_graphs={bad}")

def run_quiet(name, N, edges, cap_cuts=120):
    # returns 1 if radius-2 transport fails on ALL optimal cuts or SOME cut (report both), else 0
    adj = build_adj(N, edges)
    e = len(edges)
    mc, masks = maxcut_enumerate(N, edges, cap_cuts=cap_cuts)
    beta = e - mc
    if beta == 0:
        return 0
    feas = 0
    fail_cert = None
    for mask in masks:
        side = side_of(mask, N)
        ok, cert = transport_check(N, adj, side, 2)
        if ok:
            feas += 1
        elif fail_cert is None:
            fail_cert = (mask, cert)
    if feas < len(masks):
        verdict = "SOME" if feas > 0 else "NONE"
        mask, (S, B, lhs, nb, defect) = fail_cert
        print(f"  !! {name}: N={N} e={e} beta={beta} r=2 {verdict}({feas}/{len(masks)}) viol |S|={len(S)} sum_m={lhs} |B2|={nb} check {25*lhs}<={2*N*nb} mask={mask}")
        sys.stdout.flush()
        return 1 if feas == 0 else 0
    return 0

if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "named"
    dict(named=stage_named, blowups=stage_blowups, mcgee=stage_mcgee,
         blow5=stage_blow5, random=stage_random)[stage]()
