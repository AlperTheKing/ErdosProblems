"""Q5 exact library: bip, odd-cycle covering LP (tau*), exact rational simplex,
exact min-weight odd cycle via the bipartite double cover.

Everything on an acceptance path uses fractions.Fraction. No floats anywhere.
"""
from fractions import Fraction
import heapq
import itertools


# ---------------------------------------------------------------- graph6 ----
def g6_decode(s):
    """Decode a graph6 string -> (n, adjacency list of frozensets)."""
    s = s.strip()
    data = [ord(c) - 63 for c in s]
    if data[0] < 63:
        n = data[0]
        rest = data[1:]
    else:
        # 63 marker: 6-byte or 12-byte length; only handle the small forms
        raise NotImplementedError("large graph6")
    bits = []
    for d in rest:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    adj = [set() for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i].add(j)
                adj[j].add(i)
            idx += 1
    return n, [frozenset(a) for a in adj]


def edges_of(n, adj):
    return [(i, j) for i in range(n) for j in adj[i] if i < j]


def is_triangle_free(n, adj):
    for i in range(n):
        for j in adj[i]:
            if j > i and (adj[i] & adj[j]):
                return False
    return True


# --------------------------------------------------------------- blow-ups ---
def blowup_C5(n):
    """C5[n]: 5n vertices, parts of size n around a 5-cycle."""
    N = 5 * n
    adj = [set() for _ in range(N)]
    for p in range(5):
        q = (p + 1) % 5
        for a in range(n):
            for b in range(n):
                u, v = p * n + a, q * n + b
                adj[u].add(v)
                adj[v].add(u)
    return N, [frozenset(a) for a in adj]


def blowup(n0, adj0, a):
    """General blow-up H[a]."""
    off, N = [], 0
    for v in range(n0):
        off.append(N)
        N += a[v]
    adj = [set() for _ in range(N)]
    for u in range(n0):
        for v in adj0[u]:
            if u < v:
                for i in range(a[u]):
                    for j in range(a[v]):
                        x, y = off[u] + i, off[v] + j
                        adj[x].add(y)
                        adj[y].add(x)
    return N, [frozenset(x) for x in adj]


# --------------------------------------------------- exact bip (min mono) ---
def bip_exact(n, adj, weights=None):
    """bip(G) = min over cuts S of the weight of monochromatic edges.
    weights: dict (u,v)->Fraction/int, default all 1.  Returns (value, best S mask).
    Exhaustive over 2^(n-1) cuts.  Use only for n <= ~22 in Python."""
    E = edges_of(n, adj)
    if weights is None:
        # unweighted fast path: bitmask popcounts
        amask = [0] * n
        for i in range(n):
            for j in adj[i]:
                amask[i] |= 1 << j
        best, bestS = None, None
        full = (1 << n) - 1
        for mask in range(1 << (n - 1)):
            S = mask << 1                      # vertex 0 forced to side 0
            comp = full ^ S
            tot = 0
            for v in range(n):
                side = S if ((S >> v) & 1) else comp
                tot += (amask[v] & side).bit_count()
            tot >>= 1
            if best is None or tot < best:
                best, bestS = tot, S
        return best, bestS
    best, bestS = None, None
    for mask in range(1 << (n - 1)):
        S = mask << 1
        tot = 0
        for (u, v) in E:
            if ((S >> u) & 1) == ((S >> v) & 1):
                tot += weights[(u, v)]
        if best is None or tot < best:
            best, bestS = tot, S
    return best, bestS


# ------------------------------------- exact min-weight odd cycle (flow) ----
def min_odd_cycle(n, adj, w):
    """Exact minimum-weight odd cycle via shortest v+ -> v- paths in the
    bipartite double cover.  w: dict (u,v)->Fraction >= 0 (unordered key u<v).
    Returns (value, cycle as list of vertices) or (None, None) if bipartite."""
    def wt(u, v):
        return w[(u, v)] if u < v else w[(v, u)]

    best = None
    bestpath = None
    for s in range(n):
        # Dijkstra in the double cover from (s,0) to (s,1)
        INF = None
        dist = {}
        prev = {}
        pq = [(Fraction(0), s, 0, -1, -1)]
        dist[(s, 0)] = Fraction(0)
        seen = set()
        while pq:
            d, u, p, pu, pp = heapq.heappop(pq)
            if (u, p) in seen:
                continue
            seen.add((u, p))
            prev[(u, p)] = (pu, pp)
            if (u, p) == (s, 1):
                break
            if best is not None and d >= best:
                break
            for v in adj[u]:
                nd = d + wt(u, v)
                key = (v, 1 - p)
                if key not in dist or nd < dist[key]:
                    dist[key] = nd
                    heapq.heappush(pq, (nd, v, 1 - p, u, p))
        if (s, 1) in seen:
            d = dist[(s, 1)]
            if best is None or d < best:
                # reconstruct
                path = []
                cur = (s, 1)
                while cur != (-1, -1):
                    path.append(cur[0])
                    cur = prev[cur]
                path.reverse()
                # path[0]=s ... path[-1]=s, odd length walk
                best = d
                bestpath = path
    if best is None:
        return None, None
    cyc = extract_odd_cycle(bestpath)
    return best, cyc


def extract_odd_cycle(walk):
    """walk = closed odd walk v0 ... vk=v0 (k odd). Extract an odd cycle
    (repeated vertices removed by splitting off even loops)."""
    seq = walk[:-1] if walk[0] == walk[-1] else walk[:]
    # split into simple cycles until an odd one remains
    cur = walk[:]           # v0..vk with v0=vk
    while True:
        pos = {}
        found = None
        for i, v in enumerate(cur[:-1]):
            if v in pos:
                found = (pos[v], i)
                break
            pos[v] = i
        if found is None:
            return cur[:-1]
        i, j = found
        inner = cur[i:j + 1]           # closed walk
        outer = cur[:i] + cur[j:]      # closed walk
        if (len(inner) - 1) % 2 == 1:
            cur = inner
        else:
            cur = outer


def enumerate_odd_cycles(n, adj, maxlen=None):
    """All odd cycles (as vertex lists) of a small graph, each once."""
    out = []
    for start in range(n):
        # simple DFS: paths starting at 'start' with all vertices > start except start
        stack = [(start, [start], {start})]
        while stack:
            u, path, used = stack.pop()
            for v in adj[u]:
                if v == start and len(path) >= 3 and len(path) % 2 == 1:
                    if path[1] < path[-1]:      # canonical direction
                        out.append(path[:])
                    continue
                if v <= start or v in used:
                    continue
                if maxlen is not None and len(path) + 1 > maxlen:
                    continue
                stack.append((v, path + [v], used | {v}))
    return out


# --------------------------------------------- exact rational simplex -------
def simplex_max(A, b, c):
    """Exact primal simplex for  max c^T y  s.t.  A y <= b, y >= 0,  with b >= 0.
    A: list of m rows, each a list of n Fractions; b: list of m Fractions >= 0;
    c: list of n Fractions.
    Returns (opt value, y (list of n Fractions), dual z (list of m Fractions)).
    Bland's rule -> guaranteed termination."""
    m = len(A)
    nvar = len(c)
    # tableau: rows 0..m-1 constraints (with slacks), row m = objective
    # columns 0..nvar-1 structural, nvar..nvar+m-1 slacks, last = rhs
    T = [[Fraction(A[i][j]) for j in range(nvar)] +
         [Fraction(1) if k == i else Fraction(0) for k in range(m)] +
         [Fraction(b[i])] for i in range(m)]
    obj = [-Fraction(c[j]) for j in range(nvar)] + [Fraction(0)] * m + [Fraction(0)]
    basis = [nvar + i for i in range(m)]
    total = nvar + m
    it = 0
    while True:
        it += 1
        # Bland: smallest index with negative reduced cost
        e = -1
        for j in range(total):
            if obj[j] < 0:
                e = j
                break
        if e < 0:
            break
        # ratio test, Bland tie-break on smallest basis index
        piv = -1
        bestratio = None
        for i in range(m):
            if T[i][e] > 0:
                r = T[i][total] / T[i][e]
                if bestratio is None or r < bestratio or (r == bestratio and basis[i] < basis[piv]):
                    bestratio, piv = r, i
        if piv < 0:
            raise RuntimeError("unbounded")
        # pivot
        pv = T[piv][e]
        T[piv] = [x / pv for x in T[piv]]
        for i in range(m):
            if i != piv and T[i][e] != 0:
                f = T[i][e]
                Ti, Tp = T[i], T[piv]
                T[i] = [Ti[j] - f * Tp[j] for j in range(total + 1)]
        if obj[e] != 0:
            f = obj[e]
            Tp = T[piv]
            obj = [obj[j] - f * Tp[j] for j in range(total + 1)]
        basis[piv] = e
        if it > 200000:
            raise RuntimeError("iteration limit")
    y = [Fraction(0)] * nvar
    for i in range(m):
        if basis[i] < nvar:
            y[basis[i]] = T[i][total]
    val = obj[total]
    dual = [obj[nvar + i] for i in range(m)]
    return val, y, dual


# -------------------------------- odd-cycle covering LP tau* (row gen) ------
def tau_star(n, adj, w=None, verbose=False):
    """Exact fractional odd-cycle cover / packing value.
       min sum_e w_e z_e  s.t. z(C) >= 1 for every odd cycle C, z >= 0
     = max sum_C y_C      s.t. sum_{C ni e} y_C <= w_e, y >= 0.
    Returns dict with exact Fraction value, cover z, packing y, and the cycles used.
    Row generation with EXACT separation (min-weight odd cycle in the double cover)."""
    E = edges_of(n, adj)
    eidx = {e: i for i, e in enumerate(E)}
    if w is None:
        w = {e: Fraction(1) for e in E}
    w = {e: Fraction(w[e]) for e in E}

    # seed with a few short odd cycles
    cycles = []
    seen = set()

    def add_cycle(cyc):
        key = frozenset((min(cyc[i], cyc[(i + 1) % len(cyc)]),
                         max(cyc[i], cyc[(i + 1) % len(cyc)]))
                        for i in range(len(cyc)))
        if key in seen:
            return False
        seen.add(key)
        cycles.append(sorted(key))
        return True

    z0 = {e: Fraction(0) for e in E}
    v, c = min_odd_cycle(n, adj, z0)
    if v is None:
        return {"value": Fraction(0), "cover": z0, "packing": [], "cycles": [],
                "bipartite": True}
    add_cycle(c)

    rounds = 0
    while True:
        rounds += 1
        # packing LP:  max 1^T y  s.t.  sum_{C ni e} y_C <= w_e
        m = len(E)
        nv = len(cycles)
        A = [[Fraction(0)] * nv for _ in range(m)]
        for k, cy in enumerate(cycles):
            for e in cy:
                A[eidx[e]][k] = Fraction(1)
        b = [w[e] for e in E]
        cobj = [Fraction(1)] * nv
        val, y, z = simplex_max(A, b, cobj)
        zdict = {E[i]: z[i] for i in range(m)}
        mv, mc = min_odd_cycle(n, adj, zdict)
        if verbose:
            print(f"  round {rounds}: |cycles|={nv} LP={val} minodd={mv}")
        if mv >= 1:
            return {"value": val, "cover": zdict,
                    "packing": [(cycles[k], y[k]) for k in range(nv) if y[k] != 0],
                    "cycles": cycles, "rounds": rounds, "bipartite": False}
        if not add_cycle(mc):
            raise RuntimeError("separation returned a known cycle; stalled")


def verify_cover(n, adj, z):
    """Exact check that z >= 0 covers all odd cycles: min odd cycle weight >= 1."""
    for e, val in z.items():
        if val < 0:
            return False, e
    v, c = min_odd_cycle(n, adj, z)
    if v is None:
        return True, None
    return (v >= 1), (v, c)


def verify_packing(n, adj, pack, w):
    """Exact check: y >= 0, every cycle in pack is an odd cycle of G,
    and sum_{C ni e} y_C <= w_e."""
    load = {e: Fraction(0) for e in edges_of(n, adj)}
    tot = Fraction(0)
    for cyc, val in pack:
        if val < 0:
            return False, "negative y"
        if len(cyc) % 2 == 0:
            return False, "even cycle"
        for e in cyc:
            if e not in load:
                return False, f"non-edge {e}"
            load[e] += val
        tot += val
    for e in load:
        if load[e] > w[e]:
            return False, f"capacity violated at {e}"
    return True, tot
