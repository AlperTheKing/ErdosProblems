#!/usr/bin/env python3
"""AGENT fiberhunter -- Script C2: GENERAL capture search at t=5 (all shapes).

Same axiom/profile model as fh_capture_search.py but capture is encoded exactly as
the engine's active-scope gate does it: latent[e] = edge present and unused by every
selected row; one scope atom; two commodity flows from the owner to the scope atom's
endpoints over latent edges.  SAT = active owner (any capture shape: incident at any
odd tail depth, remote branched, anything).  UNSAT per split = no active owner at
that shore split, for ANY triangle-free 25/24 profile circuit and ANY selection --
modulo the post-check axioms (mu>=2, deletion-SDR, connectivity), which are applied
to any SAT model before it counts (nogood loop otherwise).

Window: splits (n1,n2), n1 in 7..14 owner shore, n2 in 6..13, 15 <= n <= 20:
  n <= 20 by the capture rank theorem (captured atom's selected row closes a cycle
  through the first tail edge, independent of the 4 coverage cycles => rank >= 5);
  n1 >= 7, n2 >= 6 by the far-tail-vertex triangle theorems; n >= 15 by R49.
Redundant sound cuts: sum(latent) >= 4 (minimal capture inventory) and
sum(latent) <= 10 (|S_omega| >= 3t-1 = 14, R50 + rederived).
"""

from __future__ import annotations

import json
import sys
import time
from itertools import combinations
from pathlib import Path

from ortools.sat.python import cp_model

OUT = Path(r"E:\Projects\ErdosProblems\tmp\agent_hunt\fiberhunter")


def e(u, v):
    return (u, v) if u < v else (v, u)


def bfs(adj, src, n):
    d = [-1] * n
    d[src] = 0
    q = [src]
    h = 0
    while h < len(q):
        c = q[h]
        h += 1
        for x in adj[c]:
            if d[x] == -1:
                d[x] = d[c] + 1
                q.append(x)
    return d


def four_paths(adj, a, b):
    out = []
    for m1 in adj[a]:
        if m1 == b:
            continue
        for m2 in adj[m1]:
            if m2 in (a, b):
                continue
            for m3 in adj[m2]:
                if m3 in (a, b, m1):
                    continue
                if b in adj[m3]:
                    out.append((a, m1, m2, m3, b))
    return out


def row_edges(r):
    return frozenset(e(r[k], r[k + 1]) for k in range(4))


def max_matching(nl, adjlist):
    mr, ml = {}, {}

    def aug(l, seen):
        for r in adjlist[l]:
            if r in seen:
                continue
            seen.add(r)
            if r not in mr or aug(mr[r], seen):
                mr[r] = l
                ml[l] = r
                return True
        return False

    cnt = 0
    for l in range(nl):
        if aug(l, set()):
            cnt += 1
    return cnt, ml


def solve_split(n1, n2, time_limit, workers, log):
    V1 = list(range(n1))            # v=0, b1..b5=1..5, free 6..
    V2 = list(range(n1, n1 + n2))   # x0, y1..y4, free ...
    v = 0
    Bs = [1, 2, 3, 4, 5]
    x0 = n1
    Ys = [n1 + 1, n1 + 2, n1 + 3, n1 + 4]
    freeV1 = [z for z in V1 if z >= 6]
    freeV2 = [z for z in V2 if z >= n1 + 5]
    n = n1 + n2

    vx0 = e(v, x0)
    forced_present = [vx0] + [e(v, y) for y in Ys]
    forced_absent = ({e(v, g) for g in freeV2} | {e(b, x0) for b in Bs}
                     | {e(b, y) for b in Bs for y in Ys})

    model = cp_model.CpModel()
    edge = {}
    for a in V1:
        for c in V2:
            ed = e(a, c)
            if ed in forced_absent:
                continue
            edge[ed] = model.new_bool_var(f"E{a}_{c}")
    for ed in forced_present:
        model.add(edge[ed] == 1)
    model.add(sum(edge.values()) == 24)

    def edge_ok(a, c):
        return e(a, c) in edge

    pairs = [tuple(sorted(p)) for p in combinations(V1, 2)] + [tuple(sorted(p)) for p in combinations(V2, 2)]
    atom = {}
    for p in pairs:
        if v in p and p[1] not in Bs:
            continue
        atom[p] = model.new_bool_var(f"A{p[0]}_{p[1]}")
    for b in Bs:
        model.add(atom[(v, b)] == 1)
    model.add(sum(atom.values()) == 25)

    for p, av in atom.items():
        a, b = p
        others = V2 if p[0] in V1 else V1
        for m in others:
            if edge_ok(a, m) and edge_ok(b, m):
                model.add(edge[e(a, m)] + edge[e(b, m)] + av <= 2)

    rows = {}
    edge_users = {ed: [] for ed in edge}
    cov_candidates = {y: {} for y in Ys}
    for p, av in atom.items():
        a, b = p
        plist = []
        if p[0] in V1 and p[1] in V1:
            M1s, M2s = V2, V1
        else:
            M1s, M2s = V1, V2
        noninc = v not in p
        for m1 in M1s:
            if not edge_ok(*sorted((a, m1))):
                continue
            if noninc and m1 == v:
                continue
            for m3 in M1s:
                if m3 == m1 or not edge_ok(*sorted((b, m3))):
                    continue
                if noninc and m3 == v:
                    continue
                for m2 in M2s:
                    if m2 in (a, b):
                        continue
                    if noninc and m2 == v:
                        continue
                    if not (edge_ok(*sorted((m2, m1))) and edge_ok(*sorted((m2, m3)))):
                        continue
                    res = frozenset((e(a, m1), e(m1, m2), e(m2, m3), e(m3, b)))
                    if vx0 in res:
                        continue  # vx0 never selected
                    var = model.new_bool_var(f"R{p[0]}_{p[1]}_{m1}_{m2}_{m3}")
                    for ed in res:
                        model.add_implication(var, edge[ed])
                    vs = frozenset((a, m1, m2, m3, b))
                    plist.append((var, vs, res))
                    for ed in res:
                        edge_users[ed].append(var)
                    if noninc and x0 in vs:
                        for y in Ys:
                            if y in vs:
                                cov_candidates[y].setdefault(p, []).append(var)
        if not plist:
            model.add(av == 0)
        else:
            model.add(sum(var for var, _, _ in plist) == av)
        rows[p] = plist

    # sel / latent
    sel = {}
    latent = {}
    for ed, users in edge_users.items():
        s = model.new_bool_var(f"S{ed[0]}_{ed[1]}")
        for uvar in users:
            model.add_implication(uvar, s)
        model.add(s <= sum(users) if users else s == 0)
        sel[ed] = s
        l = model.new_bool_var(f"L{ed[0]}_{ed[1]}")
        model.add(l <= edge[ed])
        model.add(l + s <= 1)
        model.add(l >= edge[ed] - s)
        latent[ed] = l
    for y in Ys:
        model.add(sel[e(v, y)] == 1)
    model.add(sel[vx0] == 0)  # redundant (no rows) but explicit
    model.add(sum(latent.values()) >= 4)
    model.add(sum(latent.values()) <= 10)

    # coverage
    covsel = {}
    for y in Ys:
        terms = []
        for p, rvars in cov_candidates[y].items():
            cv = model.new_bool_var(f"C{y}_{p[0]}_{p[1]}")
            model.add(sum(rvars) >= cv)
            covsel[(y, p)] = cv
            terms.append(cv)
        if not terms:
            model.add(1 == 0)
        else:
            model.add(sum(terms) >= 1)
    for p in {p for (_, p) in covsel}:
        model.add(sum(cv for (y2, p2), cv in covsel.items() if p2 == p) <= 1)

    # bad-triangle-free
    for side in (V1, V2):
        for tvs in combinations(side, 3):
            trip = [atom[q] for q in (e(tvs[0], tvs[1]), e(tvs[0], tvs[2]), e(tvs[1], tvs[2])) if q in atom]
            if len(trip) == 3:
                model.add(sum(trip) <= 2)

    # scope atom + two latent flows from owner
    scope = {}
    for p, av in atom.items():
        sv = model.new_bool_var(f"G{p[0]}_{p[1]}")
        model.add(sv <= av)
        scope[p] = sv
    model.add(sum(scope.values()) == 1)
    for k in (0, 1):
        flow = {}
        for ed in edge:
            a, c = ed
            for (s_, t_) in ((a, c), (c, a)):
                fv = model.new_bool_var(f"F{k}_{s_}_{t_}")
                model.add(fv <= latent[ed])
                flow[(s_, t_)] = fv
        for z in range(n):
            out_ = sum(fv for (s_, _), fv in flow.items() if s_ == z)
            in_ = sum(fv for (_, t_), fv in flow.items() if t_ == z)
            sink = sum(sv for p, sv in scope.items() if p[k] == z)
            model.add(out_ - in_ == (1 if z == v else 0) - sink)

    # symmetry breaking
    def adj_int(z, others):
        return sum(edge[e(z, o)] * (1 << i) for i, o in enumerate(others) if e(z, o) in edge)

    for cls, others in ((Bs, V2), (Ys, V1), (freeV1, V2), (freeV2, V1)):
        for i in range(len(cls) - 1):
            model.add(adj_int(cls[i], others) >= adj_int(cls[i + 1], others))

    for z in freeV1 + freeV2:
        model.add(sum(edge[q] for q in edge if z in q) >= 1)

    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = 7

    attempts = 0
    while True:
        attempts += 1
        t0 = time.time()
        status = solver.solve(model)
        dt = time.time() - t0
        name = solver.status_name(status)
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return {"split": [n1, n2], "status": name, "time": round(dt, 1), "attempts": attempts}, None
        E = sorted(q for q, var in edge.items() if solver.value(var))
        A = sorted(p for p, var in atom.items() if solver.value(var))
        SelRows = {}
        for p in A:
            for var, vs, res in rows[p]:
                if solver.value(var):
                    # reconstruct sequence from res: find path a->b
                    SelRows[p] = reconstruct(p, res)
        fail = post_check(n, n1, E, A, SelRows, v, x0, Bs, Ys)
        if fail is None:
            return ({"split": [n1, n2], "status": "FALSIFIER_VERIFIED", "time": round(dt, 1), "attempts": attempts},
                    {"edges": [list(q) for q in E], "atoms": [list(p) for p in A],
                     "rows": {str(p): list(r) for p, r in SelRows.items()}})
        log(f"    postcheck fail ({fail}); nogood {attempts}")
        model.add(sum(edge[q] for q in E) + sum(atom[p] for p in A) <= 48)
        if attempts >= 60:
            return {"split": [n1, n2], "status": "NOGOOD_CAP", "time": round(dt, 1), "attempts": attempts}, None


def reconstruct(p, res):
    adj = {}
    for a, b in res:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    path = [p[0]]
    prev = None
    while path[-1] != p[1]:
        nxts = [z for z in adj[path[-1]] if z != prev]
        prev = path[-1]
        path.append(nxts[0])
    return tuple(path)


def post_check(n, n1, E, A, SelRows, v, x0, Bs, Ys):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    if len(E) != 24:
        return "edgecount"
    if any(x < 0 for x in bfs(adj, 0, n)):
        return "disconnected"
    shore = ["L" if z < n1 else "R" for z in range(n)]
    dist = [bfs(adj, s, n) for s in range(n)]
    for a, b in A:
        if shore[a] != shore[b] or dist[a][b] != 4:
            return f"atom-dist {(a, b, dist[a][b])}"
    dbs = {p: four_paths(adj, *p) for p in A}
    for p, r in SelRows.items():
        if tuple(r) not in set(map(tuple, dbs[p])):
            return "selected row not in DB"
    fp = {p: frozenset().union(*(row_edges(r) for r in dbs[p])) for p in A}
    eid = {ed: k for k, ed in enumerate(sorted(map(tuple, E)))}
    mu = [0] * 24
    for p in A:
        for ed in fp[p]:
            mu[eid[ed]] += 1
    if min(mu) < 2:
        return "mu<2"
    for out_i in range(25):
        rest = [p for k, p in enumerate(A) if k != out_i]
        cnt, _ = max_matching(len(rest), [[eid[ed] for ed in fp[p]] for p in rest])
        if cnt != 24:
            return f"SDR fail del {out_i}"
    gadj = [set(adj[z]) for z in range(n)]
    for a, b in A:
        gadj[a].add(b)
        gadj[b].add(a)
    for a, b, c in combinations(range(n), 3):
        if b in gadj[a] and c in gadj[a] and c in gadj[b]:
            return "triangle"
    sel_union = set()
    for p, r in SelRows.items():
        sel_union |= row_edges(r)
    latent = set(map(tuple, E)) - sel_union
    if e(v, x0) not in latent:
        return "vx0 selected"
    if sum(1 for p, r in SelRows.items() if v in r) != 5:
        return "r(v)!=5"
    for y in Ys:
        if e(v, y) not in sel_union:
            return "star edge unselected"
    covs = set()
    for y in Ys:
        got = [p for p, r in SelRows.items() if v not in p and x0 in r and y in r and v not in r]
        got = [p for p in got if p not in covs]
        if not got:
            return f"coverage fail y={y}"
        covs.add(got[0])
    comp = {v}
    st = [v]
    ladj = {}
    for a, b in latent:
        ladj.setdefault(a, []).append(b)
        ladj.setdefault(b, []).append(a)
    while st:
        c = st.pop()
        for x in ladj.get(c, []):
            if x not in comp:
                comp.add(x)
                st.append(x)
    if not any(a in comp and b in comp for a, b in A):
        return "no capture"
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    time_limit = float(sys.argv[1]) if len(sys.argv) > 1 else 1200.0
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    only = sys.argv[3] if len(sys.argv) > 3 else None
    splits = []
    for a in range(7, 15):
        for b in range(6, 14):
            if 15 <= a + b <= 20:
                splits.append((a, b))
    splits.sort(key=lambda s: (s[0] + s[1], s[0]))
    if only:
        want = {tuple(map(int, x.split("x"))) for x in only.split(",")}
        splits = [s for s in splits if s in want]

    def log(msg):
        print(msg, flush=True)

    results = []
    falsifier = None
    for n1, n2 in splits:
        log(f"[split {n1}+{n2} order {n1 + n2}] building...")
        res, model_data = solve_split(n1, n2, time_limit, workers, log)
        results.append(res)
        log(f"  -> {res['status']} ({res['time']}s, attempts {res['attempts']})")
        (OUT / "fh_capture_general_results.json").write_text(
            json.dumps({"schema": "fiberhunter-capture-general-v1",
                        "shape": "ALL capture shapes (2-commodity latent flow)",
                        "results": results, "falsifier": falsifier}, indent=1), encoding="utf-8")
        if model_data is not None:
            falsifier = model_data
            (OUT / "fh_FALSIFIER_general.json").write_text(json.dumps(model_data, indent=1), encoding="utf-8")
            log("!!! FALSIFIER FOUND AND VERIFIED — stopping")
            break
    log("done")


if __name__ == "__main__":
    main()
