"""Exact gate for GPT-Pro's cycle-neighbor CAGE absorption atom.

For a fixed bad edge f, left atoms are (g,P,Q,x) where P is a shortest
f-row, Q is a shortest g-row, and x lies in both rows.  The atom has mass
1/(|cyc[f]| |cyc[g]|) and may be routed only to the union of the two
closed-cycle neighbor sets of x in P+f and Q+g.  Each vertex has capacity 1.

The atom would imply ROWSUM-O for f if the fractional Hall condition holds:

    for every Y subset V,
      mass({atoms with neighbor_set subset Y}) <= |Y|.

This script enumerates all Y exactly for small instances.  A failure is a
direct falsifier to the proposed atom, not to ROWSUM-O.
"""

from __future__ import annotations

import argparse
from collections import deque
import subprocess
from fractions import Fraction as F

from _h import GENG, Bconn, dec, loads
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _codex_cage import blowup_edges


def c5_nonuniform_info(k):
    """Gamma-min side for C5[k+1,k,k+1,k,k+1].

    Parts 0,1,3 are on one side and 2,4 on the other.  The only bad
    class is 0-1, and every shortest B-row from part 0 to part 1 has the
    form 0-4-3-2-1.
    """
    sizes = [k + 1, k, k + 1, k, k + 1]
    offsets = [0]
    for s in sizes[:-1]:
        offsets.append(offsets[-1] + s)

    def part_vertices(i):
        return list(range(offsets[i], offsets[i] + sizes[i]))

    n = sum(sizes)
    E = []
    Bset = set()
    for i in range(5):
        for a in part_vertices(i):
            for b in part_vertices((i + 1) % 5):
                e = (min(a, b), max(a, b))
                E.append(e)
                if i != 0:
                    Bset.add(e)
    M = []
    ell = {}
    cyc = {}
    for a in part_vertices(0):
        for b in part_vertices(1):
            f = (min(a, b), max(a, b))
            M.append(f)
            ell[f] = 5
            rows = []
            for v4 in part_vertices(4):
                for v3 in part_vertices(3):
                    for v2 in part_vertices(2):
                        rows.append([a, v4, v3, v2, b])
            cyc[f] = rows
    return {
        "n": n,
        "M": M,
        "ell": ell,
        "cyc": cyc,
        "check_M": M[:1],
        "E": E,
        "Bset": Bset,
    }


def closed_neighbors(path, idx):
    """Two neighbors of path[idx] on the closed odd cycle path + bad edge."""
    L = len(path)
    if idx == 0:
        return {path[1], path[-1]}
    if idx == L - 1:
        return {path[-2], path[0]}
    return {path[idx - 1], path[idx + 1]}


def graph_adj(info):
    if "E" in info:
        adj = [set() for _ in range(info["n"])]
        for a, b in info["E"]:
            adj[a].add(b)
            adj[b].add(a)
        return adj
    if "adj" in info:
        return [set(s) for s in info["adj"]]
    raise KeyError("info needs E or adj for graph-neighborhood port modes")


def graph_ball(adj, x, radius):
    seen = {x}
    q = deque([(x, 0)])
    while q:
        u, d = q.popleft()
        if d == radius:
            continue
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append((v, d + 1))
    return seen


def two_gate_b_moat_vertices(n, Bset, base, iterative=False):
    adjB = [set() for _ in range(n)]
    for a, b in Bset:
        adjB[a].add(b)
        adjB[b].add(a)
    out = set(base)
    while True:
        changed = False
        seen = set()
        for s in range(n):
            if s in out or s in seen:
                continue
            comp = []
            attach = set()
            stack = [s]
            seen.add(s)
            while stack:
                u = stack.pop()
                comp.append(u)
                for w in adjB[u]:
                    if w in out:
                        attach.add(w)
                    elif w not in seen:
                        seen.add(w)
                        stack.append(w)
            if len(attach) >= 2:
                out.update(comp)
                changed = True
        if not iterative or not changed:
            return out


def atom_mask(P, i, Q, j, port_mode, ball_masks=None, info=None):
    if port_mode == "neighbors":
        verts = closed_neighbors(P, i) | closed_neighbors(Q, j)
    elif port_mode == "neighbors-center":
        verts = closed_neighbors(P, i) | closed_neighbors(Q, j) | {P[i]}
    elif port_mode.startswith("ball"):
        verts = ball_masks[P[i]]
    elif port_mode == "p-row":
        verts = set(P)
    elif port_mode == "q-row":
        verts = set(Q)
    elif port_mode == "row-union":
        verts = set(P) | set(Q)
    elif port_mode == "row-union-bimoat":
        verts = two_gate_b_moat_vertices(
            info["n"], info["Bset"], set(P) | set(Q), iterative=False
        )
    elif port_mode == "row-union-biclosure":
        verts = two_gate_b_moat_vertices(
            info["n"], info["Bset"], set(P) | set(Q), iterative=True
        )
    else:
        raise ValueError(f"unknown port_mode {port_mode!r}")
    mask = 0
    for v in verts:
        mask |= 1 << v
    return mask


def atom_neighbor_masks(n, info, f, port_mode="neighbors"):
    paths_f = info["cyc"][f]
    nf = len(paths_f)
    out = []
    ball_masks = None
    if port_mode.startswith("ball"):
        radius = int(port_mode[4:])
        adj = graph_adj(info)
        ball_masks = [graph_ball(adj, x, radius) for x in range(n)]
    for g in info["M"]:
        paths_g = info["cyc"][g]
        ng = len(paths_g)
        mass = F(1, nf * ng)
        for P in paths_f:
            posP = {v: i for i, v in enumerate(P)}
            for Q in paths_g:
                for j, x in enumerate(Q):
                    i = posP.get(x)
                    if i is None:
                        continue
                    mask = atom_mask(P, i, Q, j, port_mode, ball_masks, info)
                    out.append((mask, mass, (g, tuple(P), tuple(Q), x)))
    return out


def atom_neighbor_demands(n, info, f, port_mode="neighbors"):
    paths_f = info["cyc"][f]
    nf = len(paths_f)
    demand = {}
    count = 0
    total = F(0)
    ball_masks = None
    if port_mode.startswith("ball"):
        radius = int(port_mode[4:])
        adj = graph_adj(info)
        ball_masks = [graph_ball(adj, x, radius) for x in range(n)]
    for g in info["M"]:
        paths_g = info["cyc"][g]
        ng = len(paths_g)
        mass = F(1, nf * ng)
        for P in paths_f:
            posP = {v: i for i, v in enumerate(P)}
            for Q in paths_g:
                for j, x in enumerate(Q):
                    i = posP.get(x)
                    if i is None:
                        continue
                    mask = atom_mask(P, i, Q, j, port_mode, ball_masks, info)
                    demand[mask] = demand.get(mask, F(0)) + mass
                    total += mass
                    count += 1
    return demand, total, count


def enum_hall_failure(n, atoms):
    # demand[mask] = total mass of atoms with exactly this neighbor mask.
    demand = [F(0) for _ in range(1 << n)]
    for mask, mass, _meta in atoms:
        demand[mask] += mass

    # subset zeta transform: submass[Y] = sum_{mask subset Y} demand[mask].
    submass = demand[:]
    for bit in range(n):
        step = 1 << bit
        for mask in range(1 << n):
            if mask & step:
                submass[mask] += submass[mask ^ step]

    worst = None
    for Y in range(1 << n):
        lhs = submass[Y]
        rhs = Y.bit_count()
        viol = lhs - rhs
        if worst is None or viol > worst[0]:
            worst = (viol, Y, lhs, rhs)
    if worst and worst[0] > 0:
        return worst
    return None


def flow_hall_failure(n, atoms):
    """Exact Fraction max-flow on compressed neighbor masks."""
    demand_by_mask = {}
    total = F(0)
    for mask, mass, _meta in atoms:
        demand_by_mask[mask] = demand_by_mask.get(mask, F(0)) + mass
        total += mass
    masks = list(demand_by_mask)
    source = 0
    mask0 = 1
    vert0 = mask0 + len(masks)
    sink = vert0 + n
    Nnodes = sink + 1
    graph = [[] for _ in range(Nnodes)]

    def add(u, v, c):
        graph[u].append([v, c, len(graph[v])])
        graph[v].append([u, F(0), len(graph[u]) - 1])

    inf = total
    for mi, mask in enumerate(masks):
        node = mask0 + mi
        add(source, node, demand_by_mask[mask])
        for v in range(n):
            if (mask >> v) & 1:
                add(node, vert0 + v, inf)
    for v in range(n):
        add(vert0 + v, sink, F(1))

    flow = F(0)
    while True:
        level = [-1] * Nnodes
        q = [source]
        level[source] = 0
        for u in q:
            for v, c, _rev in graph[u]:
                if c > 0 and level[v] < 0:
                    level[v] = level[u] + 1
                    q.append(v)
        if level[sink] < 0:
            break
        it = [0] * Nnodes

        def dfs(u, f):
            if u == sink:
                return f
            i = it[u]
            while i < len(graph[u]):
                it[u] = i
                v, c, rev = graph[u][i]
                if c > 0 and level[u] + 1 == level[v]:
                    ret = dfs(v, min(f, c))
                    if ret > 0:
                        graph[u][i][1] -= ret
                        graph[v][rev][1] += ret
                        return ret
                i += 1
                it[u] = i
            return F(0)

        while True:
            pushed = dfs(source, inf)
            if pushed == 0:
                break
            flow += pushed
    if flow < total:
        # Extract the source side of the residual min-cut.  Infinite
        # mask->vertex arcs force every source-side atom mask to be contained
        # in the source-side vertex set Y, so Y is a concrete Hall witness.
        seen = [False] * Nnodes
        stack = [source]
        seen[source] = True
        while stack:
            u = stack.pop()
            for v, c, _rev in graph[u]:
                if c > 0 and not seen[v]:
                    seen[v] = True
                    stack.append(v)

        Y = 0
        for v in range(n):
            if seen[vert0 + v]:
                Y |= 1 << v
        lhs = sum(mass for mask, mass in demand_by_mask.items() if (mask & ~Y) == 0)
        rhs = Y.bit_count()
        return (lhs - rhs, Y, lhs, rhs)
    return None


def flow_hall_failure_demands(n, demand_by_mask, total):
    masks = list(demand_by_mask)
    source = 0
    mask0 = 1
    vert0 = mask0 + len(masks)
    sink = vert0 + n
    Nnodes = sink + 1
    graph = [[] for _ in range(Nnodes)]

    def add(u, v, c):
        graph[u].append([v, c, len(graph[v])])
        graph[v].append([u, F(0), len(graph[u]) - 1])

    inf = total
    for mi, mask in enumerate(masks):
        node = mask0 + mi
        add(source, node, demand_by_mask[mask])
        for v in range(n):
            if (mask >> v) & 1:
                add(node, vert0 + v, inf)
    for v in range(n):
        add(vert0 + v, sink, F(1))

    flow = F(0)
    while True:
        level = [-1] * Nnodes
        q = [source]
        level[source] = 0
        for u in q:
            for v, c, _rev in graph[u]:
                if c > 0 and level[v] < 0:
                    level[v] = level[u] + 1
                    q.append(v)
        if level[sink] < 0:
            break
        it = [0] * Nnodes

        def dfs(u, f):
            if u == sink:
                return f
            i = it[u]
            while i < len(graph[u]):
                it[u] = i
                v, c, rev = graph[u][i]
                if c > 0 and level[u] + 1 == level[v]:
                    ret = dfs(v, min(f, c))
                    if ret > 0:
                        graph[u][i][1] -= ret
                        graph[v][rev][1] += ret
                        return ret
                i += 1
                it[u] = i
            return F(0)

        while True:
            pushed = dfs(source, inf)
            if pushed == 0:
                break
            flow += pushed
    if flow < total:
        seen = [False] * Nnodes
        stack = [source]
        seen[source] = True
        while stack:
            u = stack.pop()
            for v, c, _rev in graph[u]:
                if c > 0 and not seen[v]:
                    seen[v] = True
                    stack.append(v)

        Y = 0
        for v in range(n):
            if seen[vert0 + v]:
                Y |= 1 << v
        lhs = sum(mass for mask, mass in demand_by_mask.items() if (mask & ~Y) == 0)
        rhs = Y.bit_count()
        return (lhs - rhs, Y, lhs, rhs)
    return None


def hall_failure(n, atoms, method):
    if method == "enum" or (method == "auto" and n <= 16):
        return enum_hall_failure(n, atoms)
    return flow_hall_failure(n, atoms)


def rowsum_for_f(info, f):
    n = info["n"]
    pfs = {}
    S = [F(0) for _ in range(n)]
    for g in info["M"]:
        paths = info["cyc"][g]
        den = len(paths)
        cnt = {}
        for P in paths:
            for v in P:
                cnt[v] = cnt.get(v, 0) + 1
        pf = {v: F(c, den) for v, c in cnt.items()}
        pfs[g] = pf
        for v, x in pf.items():
            S[v] += x
    return sum(x * S[v] for v, x in pfs[f].items())


def check_info(label, info, method="auto", port_mode="neighbors"):
    n = info["n"]
    checked = 0
    for f in info.get("check_M", info["M"]):
        if method == "flow":
            demands, total, atom_count = atom_neighbor_demands(
                n, info, f, port_mode=port_mode
            )
            fail = flow_hall_failure_demands(n, demands, total)
            atoms_len = atom_count
        else:
            atoms = atom_neighbor_masks(n, info, f, port_mode=port_mode)
            fail = hall_failure(n, atoms, method)
            atoms_len = len(atoms)
        checked += 1
        if fail is not None:
            viol, Y, lhs, rhs = fail
            members = [v for v in range(n) if (Y >> v) & 1]
            return {
                "fail": True,
                "label": label,
                "port_mode": port_mode,
                "n": n,
                "f": f,
                "atoms": atoms_len,
                "rowsum": rowsum_for_f(info, f),
                "viol": viol,
                "Y": members,
                "lhs": lhs,
                "rhs": rhs,
                "checked": checked,
            }
    return {
        "label": label,
        "port_mode": port_mode,
        "n": n,
        "checked": checked,
        "fail": None,
    }


def check_graph_gmins(g6, method="auto", port_mode="neighbors"):
    n, edges = dec(g6)
    adj, cuts = gmins(n, edges)
    checked_cuts = 0
    for ci, side_s in enumerate(cuts):
        side = [int(c) for c in side_s]
        if not Bconn(n, adj, side):
            continue
        st = struct_for_side(n, adj, side)
        if st is None:
            continue
        M, ell, T, mu, cyc = st
        if not M:
            continue
        checked_cuts += 1
        E = [(u, v) for u in range(n) for v in adj[u] if u < v]
        Bset = {e for e in E if side[e[0]] != side[e[1]]}
        info = {
            "n": n,
            "M": M,
            "ell": ell,
            "T": T,
            "cyc": cyc,
            "E": E,
            "Bset": Bset,
        }
        res = check_info(
            f"{g6}:cut{ci}", info, method=method, port_mode=port_mode
        )
        if res.get("fail") is not None:
            return res
    return {"g6": g6, "checked_cuts": checked_cuts, "fail": None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g6", default=None)
    ap.add_argument("--blow", type=int, default=1)
    ap.add_argument("--c5-nonuniform", type=int, default=0)
    ap.add_argument("--census-n", type=int, default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--all-gmins", action="store_true")
    ap.add_argument("--method", choices=["auto", "enum", "flow"], default="auto")
    ap.add_argument(
        "--ports",
        choices=[
            "neighbors",
            "neighbors-center",
            "ball2",
            "ball3",
            "p-row",
            "q-row",
            "row-union",
            "row-union-bimoat",
            "row-union-biclosure",
        ],
        default="neighbors",
        help="Atom sink set to exact-gate.",
    )
    args = ap.parse_args()

    if args.c5_nonuniform:
        info = c5_nonuniform_info(args.c5_nonuniform)
        res = check_info(
            f"C5[{args.c5_nonuniform + 1},{args.c5_nonuniform},"
            f"{args.c5_nonuniform + 1},{args.c5_nonuniform},"
            f"{args.c5_nonuniform + 1}]",
            info,
            method=args.method,
            port_mode=args.ports,
        )
        print(res)
        raise SystemExit(1 if res.get("fail") is not None else 0)

    if args.g6:
        if args.all_gmins:
            if args.blow != 1:
                raise SystemExit("--all-gmins with --blow is not supported")
            res = check_graph_gmins(args.g6, method=args.method, port_mode=args.ports)
            print(res)
            raise SystemExit(1 if res and res.get("fail") is not None else 0)
        n, edges = dec(args.g6) if args.blow == 1 else blowup_edges(args.g6, args.blow)
        info = loads(n, edges)
        if info is None:
            raise SystemExit("loads returned None")
        info["E"] = edges
        res = check_info(
            f"{args.g6}[{args.blow}]", info, method=args.method, port_mode=args.ports
        )
        print(res)
        raise SystemExit(1 if res.get("fail") is not None else 0)

    if args.census_n:
        seen = 0
        checked_cuts = 0
        for g6 in subprocess.run([GENG, "-tc", str(args.census_n)], capture_output=True, text=True).stdout.split():
            seen += 1
            if args.limit and seen > args.limit:
                break
            if args.all_gmins:
                res = check_graph_gmins(
                    g6, method=args.method, port_mode=args.ports
                )
                checked_cuts += 0 if res is None else res.get("checked_cuts", 0)
                if res and res.get("fail") is not None:
                    print("FAIL", res)
                    raise SystemExit(1)
                continue
            n, edges = dec(g6)
            info = loads(n, edges)
            if info is None:
                continue
            info["E"] = edges
            res = check_info(g6, info, method=args.method, port_mode=args.ports)
            if res.get("fail") is not None:
                print("FAIL", res)
                raise SystemExit(1)
        suffix = f" checked_cuts={checked_cuts}" if args.all_gmins else ""
        print(f"PASS census_n={args.census_n} seen={seen}{suffix}")


if __name__ == "__main__":
    main()
