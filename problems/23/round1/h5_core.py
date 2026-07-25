"""H5 core: exact maxcut certification for triangle-free graphs at large tight orders.

Everything here is integer arithmetic.  Three independent maxcut routes:
  * exhaustive  (N <= 26 only, used to cross-check the solvers)
  * CP-SAT "xor" model            : s_v in {0,1}, c_uv <= s_u+s_v, c_uv <= 2-s_u-s_v, max sum c
  * CP-SAT "metric" model         : y_uv in {0,1} = [u,v separated] with all triangle
                                    constraints y_ab+y_bc+y_ca <= 2 and y_ab <= y_bc+y_ca (x3).
                                    Much stronger LP relaxation -> proves optimality far faster.
The metric model needs the returned y to be an actual cut; the triangle constraints make
{y=0} an equivalence relation with <=2 classes, so it always is.  We nevertheless RE-DERIVE
the vertex 2-colouring from y and RE-COUNT the crossing edges directly, so the reported
maxcut value is never taken on the solver's word.
"""

from itertools import combinations
from ortools.sat.python import cp_model


# ---------------------------------------------------------------- graph utils
def adj_from_edges(n, edges):
    adj = [0] * n
    for u, v in edges:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def edges_from_adj(n, adj):
    return [(u, v) for u in range(n) for v in range(u + 1, n) if (adj[u] >> v) & 1]


def is_triangle_free(n, adj):
    for u in range(n):
        au = adj[u]
        v = u + 1
        while v < n:
            if (au >> v) & 1:
                if au & adj[v] & ~((1 << (v + 1)) - 1):
                    return False
            v += 1
    return True


def triangle_witness(n, adj):
    for a, b, c in combinations(range(n), 3):
        if (adj[a] >> b) & 1 and (adj[a] >> c) & 1 and (adj[b] >> c) & 1:
            return (a, b, c)
    return None


def g6(n, adj):
    """graph6 encoding, with the 4-byte header for 63 <= n <= 258."""
    if n <= 62:
        out = chr(n + 63)
    else:
        assert n <= 258, "only n <= 258 implemented"
        out = "~" + "".join(chr(((n >> s) & 63) + 63) for s in (12, 6, 0))
    cur = nb = 0
    for j in range(1, n):
        for i in range(j):
            cur = (cur << 1) | ((adj[i] >> j) & 1)
            nb += 1
            if nb == 6:
                out += chr(cur + 63)
                cur = nb = 0
    if nb:
        out += chr((cur << (6 - nb)) + 63)
    return out


def from_g6(s):
    if s[0] == "~":
        n = ((ord(s[1]) - 63) << 12) | ((ord(s[2]) - 63) << 6) | (ord(s[3]) - 63)
        s = s[3:]
    else:
        n = ord(s[0]) - 63
        assert 0 <= n <= 62
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        bits.extend((v >> k) & 1 for k in range(5, -1, -1))
    adj = [0] * n
    p = 0
    for j in range(1, n):
        for i in range(j):
            if bits[p]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            p += 1
    return n, adj


# ------------------------------------------------------------- cut evaluation
def cut_value(n, adj, side):
    """Count crossing edges of the 2-colouring `side` (list of 0/1) by direct enumeration."""
    c = 0
    for u in range(n):
        for v in range(u + 1, n):
            if (adj[u] >> v) & 1 and side[u] != side[v]:
                c += 1
    return c


def maxcut_exhaustive(n, adj):
    deg = [bin(a).count("1") for a in adj]
    S, cut = 1, deg[0]
    best, best_S = cut, S
    for k in range(1, 1 << (n - 1)):
        v = (k & -k).bit_length()
        a = bin(adj[v] & S).count("1")
        if S >> v & 1:
            cut += 2 * a - deg[v]
            S &= ~(1 << v)
        else:
            cut += deg[v] - 2 * a
            S |= 1 << v
        if cut > best:
            best, best_S = cut, S
    return best, [(best_S >> i) & 1 for i in range(n)]


# ------------------------------------------------------------- heuristic (LB)
def maxcut_heuristic(n, adj, restarts=200, rng=None):
    """Local search; returns (best_value, best_side).  LOWER bound on maxcut only."""
    import random
    rng = rng or random.Random(0)
    best, best_side = -1, None
    for _ in range(restarts):
        side = [rng.getrandbits(1) for _ in range(n)]
        # gain[v] = increase in cut if v flips
        improved = True
        while improved:
            improved = False
            order = list(range(n))
            rng.shuffle(order)
            for v in order:
                same = 0
                diff = 0
                av = adj[v]
                for u in range(n):
                    if (av >> u) & 1:
                        if side[u] == side[v]:
                            same += 1
                        else:
                            diff += 1
                if same > diff:
                    side[v] ^= 1
                    improved = True
        val = cut_value(n, adj, side)
        if val > best:
            best, best_side = val, side[:]
    return best, best_side


# --------------------------------------------------------------- CP-SAT exact
def maxcut_cpsat_xor(n, adj, workers=32, max_time=None, log=False, hint_side=None, lb=None):
    edges = edges_from_adj(n, adj)
    m = cp_model.CpModel()
    s = [m.NewBoolVar(f"s{v}") for v in range(n)]
    m.Add(s[0] == 0)
    c = []
    for (u, v) in edges:
        cv = m.NewBoolVar("")
        m.Add(cv <= s[u] + s[v])
        m.Add(cv <= 2 - s[u] - s[v])
        c.append(cv)
    m.Maximize(sum(c))
    if lb is not None:
        m.Add(sum(c) >= lb)
    if hint_side is not None:
        for v in range(n):
            m.AddHint(s[v], hint_side[v] ^ hint_side[0])
    sol = cp_model.CpSolver()
    sol.parameters.num_search_workers = workers
    sol.parameters.log_search_progress = log
    if max_time:
        sol.parameters.max_time_in_seconds = max_time
    st = sol.Solve(m)
    name = sol.StatusName(st)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        side = [sol.Value(s[v]) for v in range(n)]
        return name, cut_value(n, adj, side), side, int(sol.BestObjectiveBound())
    return name, None, None, None


def maxcut_cpsat_metric(n, adj, workers=32, max_time=None, log=False,
                        hint_side=None, lb=None):
    """Metric-polytope integer model.  Returns (status, verified_cut, side, dual_bound)."""
    edges = edges_from_adj(n, adj)
    m = cp_model.CpModel()
    y = {}
    for u in range(n):
        for v in range(u + 1, n):
            y[(u, v)] = m.NewBoolVar(f"y{u}_{v}")

    def Y(a, b):
        return y[(a, b)] if a < b else y[(b, a)]

    for a, b, cc in combinations(range(n), 3):
        ab, bc, ac = Y(a, b), Y(b, cc), Y(a, cc)
        m.Add(ab + bc + ac <= 2)
        m.Add(ab <= bc + ac)
        m.Add(bc <= ab + ac)
        m.Add(ac <= ab + bc)
    m.Maximize(sum(Y(u, v) for (u, v) in edges))
    if lb is not None:
        m.Add(sum(Y(u, v) for (u, v) in edges) >= lb)
    if hint_side is not None:
        for u in range(n):
            for v in range(u + 1, n):
                m.AddHint(y[(u, v)], 1 if hint_side[u] != hint_side[v] else 0)
    sol = cp_model.CpSolver()
    sol.parameters.num_search_workers = workers
    sol.parameters.log_search_progress = log
    if max_time:
        sol.parameters.max_time_in_seconds = max_time
    st = sol.Solve(m)
    name = sol.StatusName(st)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        # rebuild the 2-colouring from y (y=0 is an equivalence with <=2 classes)
        side = [None] * n
        side[0] = 0
        for v in range(1, n):
            side[v] = sol.Value(Y(0, v))
        # consistency audit of the recovered colouring against y
        for u in range(n):
            for v in range(u + 1, n):
                assert sol.Value(y[(u, v)]) == (1 if side[u] != side[v] else 0), \
                    "metric solution is not a cut -- model bug"
        return name, cut_value(n, adj, side), side, int(sol.BestObjectiveBound())
    return name, None, None, None


# ------------------------------------------------------------------ top level
def certify(n, adj, label="", workers=32, max_time=600, model="metric",
            heur_restarts=300, verbose=True):
    """Full exact pipeline for one graph.  Returns dict with the audited numbers."""
    assert len(adj) == n
    tri = triangle_witness(n, adj)
    E = edges_from_adj(n, adj)
    mE = len(E)
    hv, hs = maxcut_heuristic(n, adj, restarts=heur_restarts)
    fn = maxcut_cpsat_metric if model == "metric" else maxcut_cpsat_xor
    st, mc, side, bound = fn(n, adj, workers=workers, max_time=max_time,
                             hint_side=hs, lb=hv)
    res = {
        "label": label, "n": n, "m": mE, "triangle_free": tri is None,
        "triangle_witness": tri, "status": st, "maxcut": mc,
        "dual_bound": bound, "heuristic_cut": hv,
        "bip": (mE - mc) if mc is not None else None,
        "g6": g6(n, adj) if n <= 62 else None,
        "model": model,
    }
    if mc is not None:
        res["ratio"] = (mE - mc) / (n * n)
        res["25bip_vs_N2"] = (25 * (mE - mc), n * n)
        res["violates"] = 25 * (mE - mc) > n * n
        res["proved_optimal"] = (st == "OPTIMAL")
        # bip lower bound valid even if only FEASIBLE: bip >= m - dual_bound
        res["bip_certified_lower"] = mE - bound if bound is not None else None
    if verbose:
        print(f"[{label}] N={n} m={mE} tri-free={tri is None} status={st} "
              f"maxcut={mc} (dual {bound}) bip={res['bip']} "
              f"ratio={res.get('ratio')}", flush=True)
    return res
