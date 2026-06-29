"""Switch lab for interval-Hall failures.

This is an exploratory exact tool, not a proof checker.  For a supplied
configuration, it finds interval-Hall failures for unique rows and tests a
few natural switch families:

  * singleton vertices;
  * contiguous intervals on the unique path P_f;
  * path intervals closed under off-path B-components whose spans lie inside.

It reports cut-tight switches (same max-cut size) that strictly lower Gamma.
"""
from __future__ import annotations

from fractions import Fraction as F

from _h import bdist_restr
from _satzmu_conn import struct_for_side
from _codex_upo_conditional_interval_uncross_scan import component_info


def n26_graph():
    n = 26
    edges: list[tuple[int, int]] = []
    for i in range(12):
        edges.append((i, i + 1))
    det = [0, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 12]
    for a, b in zip(det, det[1:]):
        edges.append((min(a, b), max(a, b)))
    edges += [(0, 4), (4, 8), (8, 12), (0, 12)]
    return n, sorted(set(edges))


def adj_from_edges(n: int, edges: list[tuple[int, int]]):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def cut_size(edges, side):
    return sum(1 for a, b in edges if side[a] != side[b])


def gamma_data(n, adj, side):
    total = 0
    bad = []
    for u in range(n):
        for v in adj[u]:
            if v <= u or side[u] != side[v]:
                continue
            d = bdist_restr(adj, side, u, v)
            if d < 0:
                return None
            total += (d + 1) ** 2
            bad.append((u, v, d + 1))
    return total, bad


def interval_failures(n, adj, side, name):
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, _ell, _T, _mu, cyc = st
    S = [F(0)] * n
    for g in M:
        paths = cyc[g]
        k = len(paths)
        seen = {}
        for path in paths:
            for v in path:
                seen[v] = seen.get(v, F(0)) + F(1, k)
        for v, pv in seen.items():
            S[v] += pv

    out = []
    for f in M:
        if len(cyc[f]) != 1:
            continue
        path = cyc[f][0]
        infos = component_info(n, adj, side, path)
        dvec = [S[v] - 1 for v in path]
        for a in range(len(path)):
            for b in range(a, len(path)):
                lhs = sum(dvec[a : b + 1])
                rhs = sum(cap for lo, hi, cap, _vs, _att in infos if not (hi < a or lo > b))
                if lhs > rhs:
                    out.append(
                        {
                            "name": name,
                            "f": f,
                            "path": path,
                            "interval": (a, b),
                            "demand": lhs,
                            "cap": rhs,
                            "dvec": dvec,
                            "components": infos,
                        }
                    )
    return out


def switched(side, verts):
    side2 = list(side)
    for v in verts:
        side2[v] ^= 1
    return side2


def candidate_switches(path, components):
    seen = set()

    def add(label, verts):
        key = tuple(sorted(verts))
        if key and key not in seen:
            seen.add(key)
            yield (label, set(key))

    npath = len(path)
    for v in path:
        yield from add(("singleton", v), {v})

    for a in range(npath):
        for b in range(a, npath):
            base = set(path[a : b + 1])
            yield from add(("path_interval", a, b), base)
            closed = set(base)
            for lo, hi, _cap, vs, _att in components:
                if a <= lo and hi <= b:
                    closed.update(vs)
            yield from add(("closed_interval", a, b), closed)


def analyze(name, n, edges, side, max_report=20):
    adj = adj_from_edges(n, edges)
    base_cut = cut_size(edges, side)
    base_gamma = gamma_data(n, adj, side)
    if base_gamma is None:
        print(name, "invalid base gamma")
        return
    failures = interval_failures(n, adj, side, name)
    print(name, "cut", base_cut, "gamma", base_gamma[0], "interval_failures", len(failures))
    for failure in failures[:max_report]:
        print(
            "FAIL",
            "f",
            failure["f"],
            "P",
            failure["path"],
            "I",
            failure["interval"],
            "demand",
            failure["demand"],
            "cap",
            failure["cap"],
            "dvec",
            [str(x) for x in failure["dvec"]],
        )
        hits = []
        for label, verts in candidate_switches(failure["path"], failure["components"]):
            side2 = switched(side, verts)
            if cut_size(edges, side2) != base_cut:
                continue
            gd = gamma_data(n, adj, side2)
            if gd is None:
                continue
            if gd[0] < base_gamma[0]:
                hits.append((gd[0], label, tuple(sorted(verts)), gd[1]))
        print("  gamma_descent_switches", len(hits))
        for hit in sorted(hits)[:10]:
            print("   ", hit)


if __name__ == "__main__":
    n, edges = n26_graph()
    analyze("N26 parity", n, edges, [v % 2 for v in range(n)])
