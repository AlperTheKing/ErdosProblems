"""Exact gate for a row-union Hall transport candidate.

For a fixed long row Q, aggregate each row P of each bad edge g in the same
K-component with demand

    |P cap Q| / |cyc[g]|.

The demand node P may use capacity 1 at any vertex of P, plus a universal
deficit bank.  The max Hall excess is

    max_X demand(X) - |union_{P in X} P|.

The candidate LONG-SURPLUS transport is:

    max_excess <= eta/2 - (|Q|^2-25)/50.

If true, total demand <= N + eta/2 - surplus, hence LONG-SURPLUS.
"""

import argparse
import contextlib
import io
import subprocess
from collections import Counter, defaultdict, deque
from fractions import Fraction as F

with contextlib.redirect_stdout(io.StringIO()):
    from _bdef_construct import Cn, mycielski, union_disjoint
    from _codex_rowcap_non5_half_gate import adj_of, blowup
    from _h import Bconn, GENG, dec
    from _satzmu_conn import kcomponents, struct_for_side
    from _stark1 import gmins
    from _verify_two_lane import build_two_lane
    from _wf_lrsbreak_0 import build_k_lane
    from _wf_lrsbreak_0c import greedy_chords


class Dinic:
    def __init__(self, n):
        self.g = [[] for _ in range(n)]

    def add_edge(self, u, v, c):
        a = [v, c, None]
        b = [u, F(0), a]
        a[2] = b
        self.g[u].append(a)
        self.g[v].append(b)

    def maxflow(self, s, t):
        flow = F(0)
        n = len(self.g)
        while True:
            level = [-1] * n
            level[s] = 0
            q = deque([s])
            while q:
                u = q.popleft()
                for v, c, _rev in self.g[u]:
                    if c > 0 and level[v] < 0:
                        level[v] = level[u] + 1
                        q.append(v)
            if level[t] < 0:
                return flow
            it = [0] * n

            def dfs(u, f):
                if u == t:
                    return f
                while it[u] < len(self.g[u]):
                    e = self.g[u][it[u]]
                    v, c, rev = e
                    if c > 0 and level[u] + 1 == level[v]:
                        ret = dfs(v, min(f, c))
                        if ret > 0:
                            e[1] -= ret
                            rev[1] += ret
                            return ret
                    it[u] += 1
                return F(0)

            while True:
                pushed = dfs(s, F(10**18))
                if pushed == 0:
                    break
                flow += pushed

    def reachable_from(self, s):
        seen = [False] * len(self.g)
        seen[s] = True
        q = deque([s])
        while q:
            u = q.popleft()
            for v, c, _rev in self.g[u]:
                if c > 0 and not seen[v]:
                    seen[v] = True
                    q.append(v)
        return seen


def cycle_blowup_side(parts):
    side = []
    for i, p in enumerate(parts):
        side.extend([i % 2] * p)
    return side


def bridge(block1, block2, u, v):
    n, edges = union_disjoint(block1, block2)
    return n, edges + [(u, block1[0] + v)]


def hall_excess(n, demands, want_witness=False):
    """demands: list of (Fraction mass, tuple/set vertices)."""
    total = sum((d for d, _vs in demands), F(0))
    if not demands:
        return (F(0), []) if want_witness else F(0)
    src = 0
    row0 = 1
    vert0 = row0 + len(demands)
    sink = vert0 + n
    din = Dinic(sink + 1)
    inf = total + n + 1
    for i, (mass, verts) in enumerate(demands):
        rnode = row0 + i
        din.add_edge(src, rnode, mass)
        for v in verts:
            din.add_edge(rnode, vert0 + v, inf)
    for v in range(n):
        din.add_edge(vert0 + v, sink, F(1))
    mincut = din.maxflow(src, sink)
    excess = total - mincut
    if not want_witness:
        return excess
    seen = din.reachable_from(src)
    chosen = [
        i
        for i in range(len(demands))
        if seen[row0 + i]
    ]
    return excess, chosen


def eligible_vertices(pset, b_adj, mode):
    out = set(pset)
    if mode == "bclosed1":
        for v in pset:
            out.update(b_adj[v])
    return tuple(sorted(out))


def check_cut(name, n, edges, side, acc, stop_first=False, eligibility="row"):
    adj = adj_of(n, edges)
    if not Bconn(n, adj, side):
        return
    st = struct_for_side(n, adj, side)
    if st is None:
        return
    M, _ell, _T, _mu, cyc = st
    if not M:
        return
    eta = F(n * n, 25) - len(M)
    b_adj = [set() for _ in range(n)]
    for u, v in edges:
        if side[u] != side[v]:
            b_adj[u].add(v)
            b_adj[v].add(u)
    _comp_map, find = kcomponents(n, cyc)
    by_comp = defaultdict(list)
    for f in M:
        by_comp[find(cyc[f][0][0])].append(f)

    for _comp, fs in by_comp.items():
        all_rows = []
        for g in fs:
            den = F(len(cyc[g]))
            for p in cyc[g]:
                all_rows.append((set(p), den))
        for f in fs:
            for qrow in cyc[f]:
                L = len(qrow)
                if L <= 5:
                    continue
                qset = set(qrow)
                agg = Counter()
                total = F(0)
                for pset, den in all_rows:
                    inter = len(qset & pset)
                    if inter:
                        mass = F(inter, 1) / den
                        agg[eligible_vertices(pset, b_adj, eligibility)] += mass
                        total += mass
                demands = [(mass, verts) for verts, mass in agg.items()]
                excess, witness_idx = hall_excess(n, demands, want_witness=True)
                bank = eta / 2 - F(L * L - 25, 50)
                margin = bank - excess
                acc["rows"] += 1
                if margin < acc["min_margin"][0]:
                    acc["min_margin"] = (
                        margin,
                        name,
                        n,
                        len(M),
                        f,
                        tuple(qrow),
                        total,
                        excess,
                        bank,
                    )
                if excess > acc["max_excess"][0]:
                    acc["max_excess"] = (
                        excess,
                        name,
                        n,
                        len(M),
                        f,
                        tuple(qrow),
                        total,
                        bank,
                    )
                if bank > 0:
                    ratio = excess / bank
                    if ratio > acc["max_bank_ratio"][0]:
                        acc["max_bank_ratio"] = (
                            ratio,
                            name,
                            n,
                            len(M),
                            f,
                            tuple(qrow),
                            excess,
                            bank,
                        )
                if margin < 0:
                    acc["viol"] += 1
                    if acc["first"] is None:
                        acc["first"] = {
                            "name": name,
                            "n": n,
                            "side": "".join(map(str, side)),
                            "m": len(M),
                            "eta": str(eta),
                            "f": f,
                            "row": tuple(qrow),
                            "total_demand": str(total),
                            "hall_excess": str(excess),
                            "bank": str(bank),
                            "margin": str(margin),
                            "witness_demands": [
                                (str(demands[i][0]), tuple(demands[i][1]))
                                for i in witness_idx
                            ],
                        }
                        if stop_first:
                            return


def run_gmin(name, n, edges, acc, max_cuts=None, stop_first=False, eligibility="row"):
    _adj, cuts = gmins(n, edges)
    if max_cuts is not None:
        cuts = cuts[:max_cuts]
    for side in cuts:
        check_cut(name, n, edges, side, acc, stop_first=stop_first, eligibility=eligibility)
        if stop_first and acc["first"]:
            return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-n", type=int, default=7)
    ap.add_argument("--max-n", type=int, default=9)
    ap.add_argument("--two-lane-max", type=int, default=30)
    ap.add_argument("--direct-only", action="store_true")
    ap.add_argument("--skip-census", action="store_true")
    ap.add_argument("--eligibility", choices=["row", "bclosed1"], default="row")
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--stop-first", action="store_true")
    ap.add_argument("--max-cuts", type=int, default=None)
    args = ap.parse_args()

    acc = {
        "rows": 0,
        "viol": 0,
        "first": None,
        "min_margin": (F(10**18),),
        "max_excess": (F(0),),
        "max_bank_ratio": (F(0),),
    }

    for L in range(8, args.two_lane_max + 1, 2):
        n, edges, side, _bad = build_two_lane(L)
        check_cut(f"two-lane-L{L}", n, edges, side, acc, args.stop_first, args.eligibility)
        if args.stop_first and acc["first"]:
            break

    for Ll, k, gap in [(12, 4, 6), (14, 4, 8), (16, 5, 8), (20, 6, 10)]:
        bad = greedy_chords(Ll, k, gap)
        n, edges, side, _ = build_k_lane(Ll, k, bad)
        check_cut(f"klane-L{Ll}k{k}", n, edges, side, acc, args.stop_first, args.eligibility)
        if args.stop_first and acc["first"]:
            break

    for c in (7, 9, 11, 13, 15, 17, 19):
        n, edges = blowup([1] * c)
        check_cut(f"C{c}[1]", n, edges, cycle_blowup_side([1] * c), acc, args.stop_first, args.eligibility)
        if args.stop_first and acc["first"]:
            break

    if not args.direct_only and not (args.stop_first and acc["first"]):
        named = [
            ("Grotzsch", mycielski(5, Cn(5))),
            ("M(C7)", mycielski(7, Cn(7))),
            ("C7|Grotzsch", bridge((7, Cn(7)), mycielski(5, Cn(5)), 0, 0)),
        ]
        for nm, (n, edges) in named:
            max_cuts = args.max_cuts
            if max_cuts is None and args.fast:
                max_cuts = 2
            elif max_cuts is None:
                max_cuts = 3
            run_gmin(nm, n, edges, acc, max_cuts=max_cuts, stop_first=args.stop_first, eligibility=args.eligibility)
            if args.stop_first and acc["first"]:
                break

    if not args.direct_only and not args.skip_census and not (args.stop_first and acc["first"]):
        for nn in range(args.min_n, args.max_n + 1):
            before = acc["viol"]
            for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
                n, edges = dec(g6)
                run_gmin(f"cen{g6}", n, edges, acc, max_cuts=args.max_cuts, stop_first=args.stop_first, eligibility=args.eligibility)
                if args.stop_first and acc["first"]:
                    break
            print(f"census N={nn}: rows={acc['rows']} viol+={acc['viol'] - before}", flush=True)
            if args.stop_first and acc["first"]:
                break

    print("=== ROW-UNION HALL gate ===")
    print("rows:", acc["rows"])
    print("violations:", acc["viol"])
    print("min_margin:", acc["min_margin"])
    print("max_excess:", acc["max_excess"])
    print("max_bank_ratio:", acc["max_bank_ratio"])
    print("first:", acc["first"] or "")
    print("VERDICT:", "ROW-UNION-HALL HOLDS" if acc["viol"] == 0 else "ROW-UNION-HALL FAILS")


if __name__ == "__main__":
    main()
