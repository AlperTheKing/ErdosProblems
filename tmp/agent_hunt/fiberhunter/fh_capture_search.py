#!/usr/bin/env python3
"""AGENT fiberhunter -- Script C: rooted CAPTURE search at t=5 (the SC-failing window).

Question: does ANY triangle-free 25/24 profile circuit admit a profile-consistent
selection whose owner is ACTIVE (captures a bad edge through the latent tail)?
This is the exact negation of the live lemma t5_triangleFree_localProfile_is_scopeVacuous,
restricted to incident capture at I-path length 3 (the minimal shape; every incident
capture contains one; remote capture needs >=5 latent edges -- separate variant).

ROOTING (all THEOREMS, derived + exact-checked this session):
  - capture => cycle rank >= 5 => n <= 24-5+1 = 20  (captured atom's own selected row
    closes a cycle through the first tail edge, independent of the 4 coverage cycles);
  - owner shore >= 7 under capture (w = first tail vertex is far-V1: w not in
    N_B(v) by triangle with vx0, w != v), other shore >= 6 (u far-V2: u not in N_M(v)
    by triangle with vb);
  - order >= 15 (R49 order-14 closure);
  - WLOG captured bad neighbour = b1 (b-symmetry).

MODEL (per shore split (n1,n2)): labeled V1 = {v, b1..b5, w} + free f's,
V2 = {x0, y1..y4, u} + free g's.
  support edge vars; forced present: v-x0, v-y_i, x0-w, w-u, u-b1;
  forced absent: v-u, v-free (d_M(v)=5 exact), b_j-x0, b_j-y_i (triangle theorems);
  sum edges = 24;
  atom vars over same-shore pairs, sum = 25, {v,b_j} forced, no other {v,.};
  atom => no common neighbour (distance exactly 4 with the row var below);
  one selected-row var per atom (4-path triples), row => its 4 edges present;
  rows NEVER use the 4 rooted-latent edges (v-x0, x0-w, w-u, u-b1) -- capture edges
  stay latent => owner's latent component contains v,x0,w,u,b1 => atom {v,b1}
  captured BY CONSTRUCTION;
  r_omega(v) = 5 exactly: no nonincident row contains v (triples filtered);
  star: each v-y_i used by >= 1 selected row;
  coverage: for each y_i one DISTINCT nonincident atom whose selected row contains
  x0 and y_i (v-free by construction);
  bad-triangle-free: atom triple sum <= 2 on same-shore triples.

POST-CHECK on any SAT model (exact python): connectivity, complete-DB recompute,
distance-4, mu(e)>=2, deletion-SDR 25x24, realized profile, capture component.
Failures become nogoods and the model is re-solved (loop cap).  A fully verified
SAT = FALSIFIER of the live lemma (would be reported, not celebrated).

Exact integer arithmetic; CP-SAT is used as an exhaustive finite search engine
(UNSAT verdicts are decision procedure outputs on a finite model, reported per split).
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
    V1 = list(range(n1))            # v=0, b1..b5=1..5, w=6, free 7..
    V2 = list(range(n1, n1 + n2))   # x0, y1..y4, u, free ...
    v, W = 0, 6
    Bs = [1, 2, 3, 4, 5]
    x0 = n1
    Ys = [n1 + 1, n1 + 2, n1 + 3, n1 + 4]
    U = n1 + 5
    freeV1 = [z for z in V1 if z >= 7]
    freeV2 = [z for z in V2 if z >= n1 + 6]
    n = n1 + n2

    forced_present = [e(v, x0)] + [e(v, y) for y in Ys] + [e(W, x0), e(W, U), e(Bs[0], U)]
    latent_forced = {e(v, x0), e(W, x0), e(W, U), e(Bs[0], U)}
    forced_absent = {e(v, U)} | {e(v, g) for g in freeV2} | {e(b, x0) for b in Bs} | {e(b, y) for b in Bs for y in Ys}

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

    # atoms
    pairs = [tuple(sorted(p)) for p in combinations(V1, 2)] + [tuple(sorted(p)) for p in combinations(V2, 2)]
    atom = {}
    for p in pairs:
        if v in p and p[1] not in Bs:
            continue  # d_B(v)=5 exactly
        atom[p] = model.new_bool_var(f"A{p[0]}_{p[1]}")
    for b in Bs:
        model.add(atom[(v, b)] == 1)
    model.add(sum(atom.values()) == 25)

    # distance-4: no common neighbour
    for p, av in atom.items():
        a, b = p
        others = V2 if p[0] in V1 else V1
        for m in others:
            if edge_ok(a, m) and edge_ok(b, m):
                model.add(edge[e(a, m)] + edge[e(b, m)] + av <= 2)

    # rows
    rows = {}          # p -> list[(triple, var, vertexset, edgeset)]
    star_users = {e(v, y): [] for y in Ys}
    cov_candidates = {y: {} for y in Ys}   # y -> p -> [rowvars]
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
                    if res & latent_forced:
                        continue
                    var = model.new_bool_var(f"R{p[0]}_{p[1]}_{m1}_{m2}_{m3}")
                    for ed in res:
                        model.add_implication(var, edge[ed])
                    vs = frozenset((a, m1, m2, m3, b))
                    plist.append(((m1, m2, m3), var, vs, res))
                    for ed in res & set(star_users):
                        star_users[ed].append(var)
                    if noninc and x0 in vs:
                        for y in Ys:
                            if y in vs:
                                cov_candidates[y].setdefault(p, []).append(var)
        if not plist:
            model.add(av == 0)
        else:
            model.add(sum(var for _, var, _, _ in plist) == av)
        rows[p] = plist

    # star edges selected
    for ed, users in star_users.items():
        model.add(sum(users) >= 1)

    # coverage: one distinct nonincident atom per y
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
    allp = {p for (_, p) in covsel}
    for p in allp:
        model.add(sum(cv for (y2, p2), cv in covsel.items() if p2 == p) <= 1)

    # bad-triangle-free
    for side in (V1, V2):
        for tvs in combinations(side, 3):
            trip = [atom[q] for q in (e(tvs[0], tvs[1]), e(tvs[0], tvs[2]), e(tvs[1], tvs[2])) if q in atom]
            if len(trip) == 3:
                model.add(sum(trip) <= 2)

    # symmetry breaking: adjacency-int lex on interchangeable classes
    def adj_int(z, others):
        return sum(edge[e(z, o)] * (1 << i) for i, o in enumerate(others) if e(z, o) in edge)

    for cls, others in ((Bs[1:], V2), (Ys, V1), (freeV1, V2), (freeV2, V1)):
        for i in range(len(cls) - 1):
            model.add(adj_int(cls[i], others) >= adj_int(cls[i + 1], others))

    # free vertices: usage implied by edges (isolated = unused, fine); require order = n:
    # every free vertex must be used (smaller orders covered by smaller splits)
    for z in freeV1:
        model.add(sum(edge[q] for q in edge if z in q) >= 1)
    for z in freeV2:
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

        # extract candidate
        E = sorted(q for q, var in edge.items() if solver.value(var))
        A = sorted(p for p, var in atom.items() if solver.value(var))
        SelRows = {}
        for p in A:
            for t, var, vs, res in rows[p]:
                if solver.value(var):
                    SelRows[p] = (p[0],) + t + (p[1],)
        fail = post_check(n, n1, E, A, SelRows, v, x0, W, U, Bs, Ys, log)
        if fail is None:
            return {"split": [n1, n2], "status": "FALSIFIER_VERIFIED", "time": round(dt, 1),
                    "attempts": attempts}, {"edges": [list(q) for q in E], "atoms": [list(p) for p in A],
                                            "rows": {str(p): list(r) for p, r in SelRows.items()}}
        log(f"    postcheck fail ({fail}); adding nogood {attempts}")
        model.add(sum(edge[q] for q in E) + sum(atom[p] for p in A) <= 48)
        if attempts >= 60:
            return {"split": [n1, n2], "status": "NOGOOD_CAP", "time": round(dt, 1), "attempts": attempts}, None


def post_check(n, n1, E, A, SelRows, v, x0, W, U, Bs, Ys, log):
    adj = [set() for _ in range(n)]
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    if len(E) != 24:
        return "edgecount"
    d0 = bfs(adj, 0, n)
    if any(x < 0 for x in d0):
        return "disconnected"
    shore = ["L" if z < n1 else "R" for z in range(n)]
    dist = [bfs(adj, s, n) for s in range(n)]
    for a, b in A:
        if shore[a] != shore[b] or dist[a][b] != 4:
            return f"atom-dist {(a, b, dist[a][b])}"
    dbs = {p: four_paths(adj, *p) for p in A}
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
    # triangles blue+bad
    gadj = [set(adj[z]) for z in range(n)]
    for a, b in A:
        gadj[a].add(b)
        gadj[b].add(a)
    for a, b, c in combinations(range(n), 3):
        if b in gadj[a] and c in gadj[a] and c in gadj[b]:
            return "triangle"
    # realized profile + capture
    sel_union = set()
    for p, r in SelRows.items():
        if tuple(r) not in set(map(tuple, dbs[p])):
            return "selected row not in DB"
        sel_union |= row_edges(r)
    latent = set(map(tuple, E)) - sel_union
    need_latent = {e(v, x0), e(W, x0), e(W, U), e(Bs[0], U)}
    if not need_latent <= latent:
        return "rooted latent edges not latent"
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
    time_limit = float(sys.argv[1]) if len(sys.argv) > 1 else 600.0
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 16
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
        (OUT / "fh_capture_results.json").write_text(
            json.dumps({"schema": "fiberhunter-capture-search-v1",
                        "shape": "incident capture, I-path length 3 (minimal); rooted latent {vx0,x0w,wu,ub1}",
                        "results": results, "falsifier": falsifier}, indent=1), encoding="utf-8")
        if model_data is not None:
            falsifier = model_data
            (OUT / "fh_FALSIFIER.json").write_text(json.dumps(model_data, indent=1), encoding="utf-8")
            log("!!! FALSIFIER FOUND AND VERIFIED — stopping")
            break
    log("done")


if __name__ == "__main__":
    main()
