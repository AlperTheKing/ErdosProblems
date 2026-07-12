#!/usr/bin/env python3
"""verify_5 core: fully independent re-implementation of the t=5 circuit axioms,
classifier, profile-consistency, capture decision (solver-free factored procedure),
and per-edge latent feasibility. No code shared with fiberhunter or the engine.

Written by the adversarial verifier agent. Pure Python except where a runner
explicitly cross-checks with CP-SAT (separate module).
"""

from __future__ import annotations

import hashlib
import itertools
import json


def norm(u, v):
    return (u, v) if u < v else (v, u)


def canonical_sha(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------- graph basics
def graph6_decode(s):
    """Own graph6 decoder (n < 63 only)."""
    data = [ord(c) - 63 for c in s.strip()]
    assert all(0 <= x < 64 for x in data), "bad graph6 char"
    n = data[0]
    assert n < 63
    bits = []
    for value in data[1:]:
        bits.extend(((value >> (5 - i)) & 1) for i in range(6))
    need = n * (n - 1) // 2
    assert len(bits) >= need
    edges = []
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                edges.append((i, j))
            k += 1
    return n, edges


def build_adj(n, edges):
    adj = {v: set() for v in range(n)}
    for u, v in edges:
        assert u != v
        assert v not in adj[u], "duplicate edge"
        adj[u].add(v)
        adj[v].add(u)
    return adj


def bfs_dist(adj, src):
    dist = {src: 0}
    frontier = [src]
    while frontier:
        nxt = []
        for u in frontier:
            for w in adj[u]:
                if w not in dist:
                    dist[w] = dist[u] + 1
                    nxt.append(w)
        frontier = nxt
    return dist


def is_connected(adj, n):
    return len(bfs_dist(adj, 0)) == n


def triangle_count(n, edges):
    adj = {v: set() for v in range(n)}
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    t = 0
    for u, v in edges:
        t += len(adj[u] & adj[v])
    return t // 3


# ---------------------------------------------------------------- rows / atoms
def all_rows(adj, u, v):
    """All simple paths with exactly 5 vertices from u to v (length-4 paths)."""
    out = []

    def dfs(path):
        if len(path) == 5:
            if path[-1] == v:
                out.append(tuple(path))
            return
        last = path[-1]
        for w in sorted(adj[last]):
            if w in path:
                continue
            if len(path) == 4 and w != v:
                continue
            dfs(path + [w])

    dfs([u])
    return sorted(out)


def available_atoms(n, edges, left_n):
    """Same-shore pairs at support distance exactly 4, with complete row DBs."""
    adj = build_adj(n, edges)
    shores = [("L", range(left_n)), ("R", range(left_n, n))]
    atoms = []
    for shore, vertices in shores:
        vs = list(vertices)
        for i, u in enumerate(vs):
            du = bfs_dist(adj, u)
            for v in vs[i + 1 :]:
                if du.get(v) != 4:
                    continue
                rows = all_rows(adj, u, v)
                assert rows, f"distance-4 pair {u},{v} with no length-4 path"
                footprint = sorted(
                    {norm(r[k], r[k + 1]) for r in rows for k in range(4)}
                )
                atoms.append(
                    {"shore": shore, "u": u, "v": v, "rows": rows, "footprint": footprint}
                )
    return atoms


# ---------------------------------------------------------------- matching
def max_matching(left_items, adjacency):
    """Kuhn's augmenting-path max bipartite matching.
    adjacency: dict left_item -> iterable of right items. Returns (size, match_r)."""
    match_r = {}

    def try_augment(u, visited):
        for w in adjacency.get(u, ()):
            if w in visited:
                continue
            visited.add(w)
            if w not in match_r or try_augment(match_r[w], visited):
                match_r[w] = u
                return True
        return False

    size = 0
    for u in left_items:
        if try_augment(u, set()):
            size += 1
    return size, match_r


def deletion_sdr_sizes(chosen_atoms, support_edges):
    sizes = []
    edge_set = list(map(tuple, support_edges))
    for excluded in range(len(chosen_atoms)):
        lefts = [i for i in range(len(chosen_atoms)) if i != excluded]
        adjacency = {
            i: [e for e in chosen_atoms[i]["footprint"] if tuple(e) in set(edge_set)]
            for i in lefts
        }
        size, _ = max_matching(lefts, adjacency)
        sizes.append(size)
    return sizes


# ---------------------------------------------------------------- classifier
def first_step(row, owner):
    if row[0] == owner:
        return row[1]
    if row[-1] == owner:
        return row[-2]
    raise AssertionError("owner not an endpoint of incident row")


def classifier_vector(chosen_atoms, adj, owner, active):
    neighbours = sorted(adj[owner])
    assert active in neighbours
    support = [y for y in neighbours if y != active]
    incident = [
        i for i, a in enumerate(chosen_atoms) if owner in (a["u"], a["v"])
    ]
    nonincident = [i for i in range(len(chosen_atoms)) if i not in incident]
    forced = [
        i
        for i in range(len(chosen_atoms))
        if all(owner in row for row in chosen_atoms[i]["rows"])
    ]
    e_forced = len(set(forced) - set(incident))

    empty_steps = 0
    step_adj = {}
    for i in incident:
        steps = {first_step(r, owner) for r in chosen_atoms[i]["rows"]} & set(support)
        if not steps:
            empty_steps += 1
        step_adj[i] = sorted(steps)
    step_rank, _ = max_matching(incident, step_adj)

    cov_adj = {}
    for y in support:
        atoms_for_y = [
            i
            for i in nonincident
            if any(
                owner not in row and active in row and y in row
                for row in chosen_atoms[i]["rows"]
            )
        ]
        cov_adj[y] = atoms_for_y
    cov_rank, _ = max_matching(support, cov_adj)
    return {
        "eForced": e_forced,
        "iStep": empty_steps,
        "dStep": 4 - step_rank,
        "dCoverage": 4 - cov_rank,
        "incident": incident,
        "support": support,
    }


# ------------------------------------------------- profile-consistency checker
def verify_selection(chosen_atoms, adj, owner, active, selection, n):
    """Pure-Python check that `selection` (list: one row per atom, aligned with
    chosen_atoms) is profile-consistent in the engine-gate sense.
    Returns dict with latent set, owner component, captured atoms."""
    assert len(selection) == len(chosen_atoms)
    vx0 = norm(owner, active)
    support_edges = sorted(
        {norm(u, w) for u in adj for w in adj[u]}
    )
    used = set()
    owner_rows = 0
    for i, row in enumerate(selection):
        row = tuple(row)
        assert row in set(chosen_atoms[i]["rows"]), f"row not in DB of atom {i}"
        for k in range(4):
            used.add(norm(row[k], row[k + 1]))
        if owner in row:
            owner_rows += 1
    assert owner_rows == 5, f"owner rows {owner_rows} != 5"
    assert vx0 not in used, "active edge selected"
    star = [y for y in sorted(adj[owner]) if y != active]
    for y in star:
        assert norm(owner, y) in used, f"star edge {owner}-{y} unselected"
        assert any(
            active in sel and y in sel for sel in map(tuple, selection)
        ), f"pair {active},{y} uncovered"
    assert any(active in tuple(sel) for sel in selection), "x0 in no selected row"
    latent = sorted(set(support_edges) - used)
    # owner component over latent edges
    ladj = {v: set() for v in range(n)}
    for u, w in latent:
        ladj[u].add(w)
        ladj[w].add(u)
    comp = set(bfs_dist(ladj, owner))
    captured = [
        i
        for i, a in enumerate(chosen_atoms)
        if a["u"] in comp and a["v"] in comp
    ]
    return {
        "latent": latent,
        "selectedCount": len(used),
        "ownerComponent": sorted(comp),
        "capturedAtoms": captured,
    }


# ------------------------------------------------- factored (solver-free) CSP
def allowed_rows(atom, owner, forbidden_edges, incident):
    """Rows of `atom` usable in a profile-consistent selection avoiding
    forbidden_edges (edge set, must include vx0)."""
    rows = []
    for row in atom["rows"]:
        edges = {norm(row[k], row[k + 1]) for k in range(4)}
        if edges & forbidden_edges:
            continue
        if not incident and owner in row:
            continue
        rows.append(row)
    return rows


def factored_feasible(chosen_atoms, adj, owner, active, extra_latent):
    """Decide: exists a profile-consistent selection whose unused-edge set
    contains extra_latent (vx0 implicitly always unused).
    Solver-free: per-atom row filtering + two Hall matchings."""
    vx0 = norm(owner, active)
    forbidden = set(map(tuple, extra_latent)) | {vx0}
    star = [y for y in sorted(adj[owner]) if y != active]
    incident_ids = [
        i for i, a in enumerate(chosen_atoms) if owner in (a["u"], a["v"])
    ]
    nonincident_ids = [i for i in range(len(chosen_atoms)) if i not in incident_ids]
    assert len(incident_ids) == 5
    allowed = {}
    for i, atom in enumerate(chosen_atoms):
        rows = allowed_rows(atom, owner, forbidden, i in incident_ids)
        if not rows:
            return False, None
        allowed[i] = rows
    # (b) star matching: y -> incident atom with allowed row whose first edge is owner-y
    star_adj = {}
    for y in star:
        star_adj[y] = [
            i
            for i in incident_ids
            if any(first_step(r, owner) == y for r in allowed[i])
        ]
    b_size, b_match = max_matching(star, star_adj)
    if b_size != 4:
        return False, None
    # (c) coverage matching: y -> nonincident atom with allowed row containing active,y
    cov_adj = {}
    for y in star:
        cov_adj[y] = [
            i
            for i in nonincident_ids
            if any(active in r and y in r for r in allowed[i])
        ]
    c_size, c_match = max_matching(star, cov_adj)
    if c_size != 4:
        return False, None
    # construct an explicit witness selection
    # max_matching returns match_r[right_item] = left_item, i.e. b_match[atom]=y
    sel = {}
    for i in incident_ids:
        if i in b_match:
            y = b_match[i]
            sel[i] = next(r for r in allowed[i] if first_step(r, owner) == y)
        else:
            sel[i] = allowed[i][0]
    for i in nonincident_ids:
        if i in c_match:
            y = c_match[i]
            sel[i] = next(r for r in allowed[i] if active in r and y in r)
        else:
            sel[i] = allowed[i][0]
    selection = [sel[i] for i in range(len(chosen_atoms))]
    return True, selection


# ------------------------------------------------------- capture enumeration
def simple_paths(adj, src, dst, avoid, max_len):
    """All simple paths src->dst in adj avoiding vertex set `avoid`."""
    out = []

    def dfs(path):
        last = path[-1]
        if last == dst:
            out.append(list(path))
            return
        if len(path) - 1 >= max_len:
            return
        for w in sorted(adj[last]):
            if w in path or w in avoid:
                continue
            dfs(path + [w])

    if src == dst:
        return [[src]]
    dfs([src])
    return out


def path_edges(path):
    return {norm(path[k], path[k + 1]) for k in range(len(path) - 1)}


def per_edge_latent_feasible(chosen_atoms, adj, owner, active):
    """For every support edge e: is there a profile-consistent selection with e
    unused? Exact via factored_feasible({e}). vx0 is feasible by construction."""
    support_edges = sorted({norm(u, w) for u in adj for w in adj[u]})
    result = {}
    for e in support_edges:
        ok, _ = factored_feasible(chosen_atoms, adj, owner, active, {e})
        result[e] = ok
    return result


def capture_decision(chosen_atoms, adj, owner, active, n, max_path_len=23):
    """Exact solver-free capture decision.
    capture <=> exists chosen atom + union U of simple x0-paths (avoiding owner)
    to its non-owner endpoints with factored_feasible(U).
    Sound+complete pruning: any edge of a feasible U is individually
    latent-feasible (monotonicity), so paths are enumerated inside the
    individually-feasible edge subgraph only.
    Returns (bool, list_of_witnesses, feasible_edge_map)."""
    feas = per_edge_latent_feasible(chosen_atoms, adj, owner, active)
    vx0 = norm(owner, active)
    sub_adj = {v: set() for v in range(n)}
    for (u, w), ok in feas.items():
        if ok and (u, w) != vx0:
            sub_adj[u].add(w)
            sub_adj[w].add(u)
    witnesses = []
    # all simple paths from x0 to every vertex inside feasible subgraph, avoiding owner
    targets = sorted({a["u"] for a in chosen_atoms} | {a["v"] for a in chosen_atoms})
    paths_to = {}
    for t in targets:
        if t == owner:
            continue
        paths_to[t] = simple_paths(sub_adj, active, t, {owner}, max_path_len)
    for idx, atom in enumerate(chosen_atoms):
        ends = [e for e in (atom["u"], atom["v"]) if e != owner]
        if len(ends) == 2:
            u, v = ends
            combos = (
                (pu, pv)
                for pu in paths_to.get(u, [])
                for pv in paths_to.get(v, [])
            )
        else:
            combos = ((p, None) for p in paths_to.get(ends[0], []))
        seen_unions = set()
        for pu, pv in combos:
            U = path_edges(pu) | (path_edges(pv) if pv else set())
            key = frozenset(U)
            if key in seen_unions:
                continue
            seen_unions.add(key)
            ok, selection = factored_feasible(chosen_atoms, adj, owner, active, U)
            if ok:
                witnesses.append(
                    {
                        "atomIndex": idx,
                        "badEdge": [atom["u"], atom["v"]],
                        "unionEdges": sorted(map(list, U)),
                        "selection": [list(r) for r in selection],
                    }
                )
    return bool(witnesses), witnesses, feas


# --------------------------------------------------------------- misc checks
def supersaturation(chosen_atoms, support_edges, kmax=3):
    """min over k-subsets E' of (#atoms touching E') - (k+1), for k=1..kmax."""
    foots = [set(map(tuple, a["footprint"])) for a in chosen_atoms]
    edges = list(map(tuple, support_edges))
    slacks = {}
    for k in range(1, kmax + 1):
        best = None
        for combo in itertools.combinations(edges, k):
            cs = set(combo)
            touch = sum(1 for f in foots if f & cs)
            slack = touch - (k + 1)
            if best is None or slack < best:
                best = slack
        slacks[k] = best
    return slacks


def min_cut_sigma(n, blue_edges, bad_edges):
    """min over all vertex 2-colorings (v0 fixed outside) of blue_cross - bad_cross."""
    best = None
    best_mask = None
    for mask in range(1 << (n - 1)):
        def inside(v):
            return False if v == 0 else bool(mask & (1 << (v - 1)))

        sigma = sum(inside(u) != inside(v) for u, v in blue_edges) - sum(
            inside(u) != inside(v) for u, v in bad_edges
        )
        if best is None or sigma < best:
            best = sigma
            best_mask = mask
    switch = [v for v in range(n) if v and best_mask & (1 << (v - 1))]
    return best, switch
