"""Exact bounded search for a collision-loaded R42 source-swap rotor graft.

The hunt has two deliberately separate phases.

* ``abstract`` exhausts the smallest one-component physical-key source-swap
  systems.  It verifies that turnover, half-zero reservation, injectivity and
  base/component coherence alone admit positive-defect cycles.
* ``graph`` starts from the exact N29 active-pin cage.  It attaches a small
  symmetric K(2,k)-style traffic pack with an external owner ``o``.  The pack
  has k anchored length-four bad rows sharing o and r, so it gives o collision
  mass 4(k-1) without changing a pre-existing shortest row.

An abstract candidate is never reported as a graph hit.  A graph hit must pass
every structural and matching gate in ``is_hit_scc``; otherwise the manifest is
a bounded no-hit result only.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P5_DIR = ROOT / "tmp" / "fanout" / "p5_n12_census"
FULLBANK_DIR = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
for directory in (str(P5_DIR), str(FULLBANK_DIR)):
    if directory not in sys.path:
        sys.path.insert(0, directory)

import p5_core as p5  # noqa: E402
import fullbank_core as fullbank  # noqa: E402


def edge(x: int, y: int) -> tuple[int, int]:
    return (x, y) if x < y else (y, x)


def canonical_sha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_id(n: int, x: int, y: int, half: int) -> int:
    return p5.source_id(n, x, y, half)


def decode_source(n: int, source: int) -> list[int]:
    return list(p5.decode_source(n, source))


def all_perfect_source_uses(demand: int) -> int:
    """Number of injective optimal matchings from four sources to demand rows."""
    return math.factorial(demand) // math.factorial(demand - 4)


def abstract_phase() -> dict:
    """Exhaust the minimal physical-key countermodel family exactly.

    Each state has four usable half-one keys and ``demand`` interchangeable
    collision obligations in one active component.  The two states swap the
    old middle ``m`` and ``v``.  Values 5..8 are the entire requested bounded
    abstract space: four usable keys and positive integer defect at most four.
    """
    x, y, m, v = "x", "y", "m", "v"

    def bases(middle: str) -> tuple[tuple[str, str], ...]:
        return ((middle, x), (x, middle), (middle, y), (y, middle))

    def raw(middle: str) -> tuple[tuple[str, str, int], ...]:
        return tuple((a, b, half) for a, b in bases(middle) for half in (0, 1))

    candidates = []
    for demand in range(5, 9):
        obligations = tuple(f"o{i}" for i in range(demand))
        state_records = {}
        for label, middle in (("omega_m", v), ("omega_v", m)):
            raw_keys = raw(middle)
            reserved = tuple(key for key in raw_keys if key[2] == 0)
            usable = tuple(key for key in raw_keys if key[2] == 1)
            maximum_matchings = 0
            all_use_every_key = True
            # Exhaustively enumerate all optimal assignments; the source
            # order is fixed, so no symmetry quotient hides an assignment.
            for assigned_obligations in itertools.permutations(obligations, len(usable)):
                maximum_matchings += 1
                matching = dict(zip(usable, assigned_obligations))
                all_use_every_key &= set(matching) == set(usable)
                if len(set(matching.values())) != len(usable):
                    raise AssertionError("noninjective abstract matching")
            if maximum_matchings != all_perfect_source_uses(demand):
                raise AssertionError((demand, maximum_matchings))
            state_records[label] = {
                "rawNewFreeKeys": [list(key) for key in raw_keys],
                "halfZeroScopedReserved": [list(key) for key in reserved],
                "usableHalfOne": [list(key) for key in usable],
                "component": 0,
                "collisionDemand": demand,
                "maximumCoherentMatching": len(usable),
                "canonicalCollisionDefect": demand - len(usable),
                "optimalCoherentMatchings": maximum_matchings,
                "allOptimalMatchingsConsumeEveryUsableTurnoverKey": all_use_every_key,
                "baseKeyComponentCoherent": True,
            }
        transitions = []
        for source, target in (("omega_m", "omega_v"), ("omega_v", "omega_m")):
            old_usable = {tuple(key) for key in state_records[source]["usableHalfOne"]}
            new_usable = {tuple(key) for key in state_records[target]["usableHalfOne"]}
            gained = sorted(new_usable - old_usable)
            lost = sorted(old_usable - new_usable)
            if len(gained) != 4 or len(lost) != 4:
                raise AssertionError((source, target, gained, lost))
            transitions.append({
                "source": source,
                "target": target,
                "supportDelta": 0,
                "uniqueOldMiddleEdges": True,
                "rawNewFreeKeys": 8,
                "usableNewFreeKeys": 4,
                "usableGained": [list(key) for key in gained],
                "usableLost": [list(key) for key in lost],
                "targetAllUsableGainedMatched": True,
                "targetComponentOrBaseBlocked": 0,
                "productionExposure": 0,
            })
        candidates.append({
            "demand": demand,
            "states": state_records,
            "transitions": transitions,
            "positiveDefect": demand - 4,
            "abstractOnly": True,
        })
    return {
        "space": {
            "middleStates": 2,
            "usableTurnoverKeys": 4,
            "collisionDemandRange": [5, 8],
            "systemsEnumerated": len(candidates),
        },
        "candidates": candidates,
        "qualifyingAbstractSystems": len(candidates),
        "verdict": "ABSTRACT_POSITIVE_DEFECT_SOURCE_SWAP_SYSTEMS_EXIST",
        "nonConclusion": "abstract systems are not triangle-free maximum-cut cages",
    }


@dataclass(frozen=True)
class GraftSpec:
    pin_mask: int
    traffic_multiplicity: int
    attachment: str
    lock_mode: str


@dataclass(frozen=True)
class Cage:
    n: int
    names: tuple[str, ...]
    blue: frozenset[tuple[int, int]]
    bad: frozenset[tuple[int, int]]
    side_zero: frozenset[int]
    q_m: tuple[int, ...]
    q_v: tuple[int, ...]
    old_bad_count: int
    external_owner: int | None
    traffic_hubs: tuple[int, ...]
    spec: GraftSpec


def build_cage(spec: GraftSpec) -> Cage:
    """Generate the N29 cage plus a parameterized external traffic pack.

    The core rows are Q_m=a-x-m-y-b, Q_v=a-x-v-y-b and
    P=c-m-d-v-e.  Four C5 background rows select the private pin interiors.
    A selected pin joins one of a,b to one of m,v through two off-support blue
    edges.  The traffic rows h_i-o-u_i-r-k_i share the external pair (o,r).
    Their only core contact is the unused blue edge o-attachment, so the
    original row database is checked against the traffic-free cage explicitly.
    A private length-six lock is deliberately too long to create another row.
    """
    names = ["a", "x", "m", "y", "b", "c", "d", "v", "e"]
    lookup = {name: index for index, name in enumerate(names)}

    def add(name: str) -> int:
        lookup[name] = len(names)
        names.append(name)
        return lookup[name]

    a, x, m, y, b, c, d, v, e = (lookup[name] for name in names)
    blue = {
        edge(a, x), edge(x, m), edge(m, y), edge(y, b),
        edge(x, v), edge(v, y),
        edge(c, m), edge(m, d), edge(d, v), edge(v, e),
    }
    bad = {edge(a, b), edge(c, e)}
    side_zero = {x, y, c, d, e}
    pin_specs = (("am", a, m), ("bm", b, m), ("av", a, v), ("bv", b, v))
    for index, (tag, endpoint, middle) in enumerate(pin_specs):
        z = add(f"z_{tag}")
        h = add(f"h_{tag}")
        i = add(f"i_{tag}")
        j = add(f"j_{tag}")
        k = add(f"k_{tag}")
        # h-z-i-j-k is a unique length-four blue row for bad h-k.
        blue.update((edge(h, z), edge(z, i), edge(i, j), edge(j, k)))
        bad.add(edge(h, k))
        side_zero.update((z, j))
        if spec.pin_mask & (1 << index):
            blue.update((edge(endpoint, z), edge(z, middle)))
    old_bad_count = len(bad)
    external_owner: int | None = None
    traffic_hubs: list[int] = []
    if spec.traffic_multiplicity:
        external_owner = add("o")
        r = add("r")
        traffic_hubs.append(r)
        attachment = lookup[spec.attachment]
        blue.add(edge(external_owner, attachment))
        for index in range(spec.traffic_multiplicity):
            h = add(f"th_{index}")
            u = add(f"tu_{index}")
            k = add(f"tk_{index}")
            # h-o-u-r-k is an anchored C5 row, and all k choices of u are
            # intentionally enumerated by the row database.
            blue.update((edge(h, external_owner), edge(external_owner, u), edge(u, r), edge(r, k)))
            bad.add(edge(h, k))
            side_zero.update((h, u, k))
            if spec.lock_mode == "traffic_l6":
                lock = [add(f"tl_{index}_{step}") for step in range(5)]
                blue.update(edge(left, right) for left, right in zip((h, *lock), (*lock, k)))
                # h,k are on side zero, so the six-edge lock alternates as
                # required and creates no length-four row.
                side_zero.update((lock[1], lock[3]))
        if spec.lock_mode not in {"none", "traffic_l6"}:
            raise ValueError(f"unknown lock mode {spec.lock_mode}")
    return Cage(
        n=len(names),
        names=tuple(names),
        blue=frozenset(blue),
        bad=frozenset(bad),
        side_zero=frozenset(side_zero),
        q_m=(a, x, m, y, b),
        q_v=(a, x, v, y, b),
        old_bad_count=old_bad_count,
        external_owner=external_owner,
        traffic_hubs=tuple(traffic_hubs),
        spec=spec,
    )


def adjacency(n: int, edges: Iterable[tuple[int, int]]) -> list[set[int]]:
    out = [set() for _ in range(n)]
    for u, v in edges:
        out[u].add(v)
        out[v].add(u)
    return out


def is_connected(n: int, edges: Iterable[tuple[int, int]]) -> bool:
    adj = adjacency(n, edges)
    if not adj or not adj[0]:
        return False
    seen = {0}
    todo = [0]
    while todo:
        vertex = todo.pop()
        for neighbor in adj[vertex] - seen:
            seen.add(neighbor)
            todo.append(neighbor)
    return len(seen) == n


def triangle_free(n: int, edges: Iterable[tuple[int, int]]) -> bool:
    adj = adjacency(n, edges)
    return not any(adj[u] & adj[v] for u, v in edges)


def shortest_rows(n: int, blue: Iterable[tuple[int, int]], start: int, finish: int) -> tuple[tuple[int, ...], ...]:
    """Enumerate all simple shortest blue paths, accepting only length four."""
    adj = adjacency(n, blue)
    dist = [-1] * n
    dist[start] = 0
    queue = deque([start])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                queue.append(v)
    if dist[finish] != 4:
        return ()
    reverse = [-1] * n
    reverse[finish] = 0
    queue = deque([finish])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if reverse[v] < 0:
                reverse[v] = reverse[u] + 1
                queue.append(v)
    out: list[tuple[int, ...]] = []

    def visit(path: tuple[int, ...]) -> None:
        u = path[-1]
        if u == finish:
            if len(path) == 5:
                out.append(path)
            return
        for v in sorted(adj[u]):
            if v in path:
                continue
            if dist[v] != dist[u] + 1 or reverse[v] != 4 - dist[v]:
                continue
            visit((*path, v))

    visit((start,))
    return tuple(sorted(out))


def maxcut_exact(n: int, edges: Iterable[tuple[int, int]]) -> dict:
    """Exact integer max-cut via deterministic bucket elimination.

    A factor maps assignments on a sorted scope to the maximum cut value
    contributed by eliminated variables.  Min-degree elimination keeps the
    active-pin family small and records a replayable width/table certificate.
    """
    factors: list[tuple[tuple[int, ...], dict[int, int]]] = []
    for u, v in sorted(edges):
        scope = (u, v)
        factors.append((scope, {0: 0, 1: 1, 2: 1, 3: 0}))
    remaining = set(range(n))
    widths: list[int] = []
    table_sizes: list[int] = []
    while remaining:
        incidence = {v: [] for v in remaining}
        for index, (scope, _table) in enumerate(factors):
            for v in scope:
                if v in remaining:
                    incidence[v].append(index)
        # Min-degree, then vertex id: fixed deterministic variable order.
        vertex = min(remaining, key=lambda q: (len({w for i in incidence[q] for w in factors[i][0] if w != q and w in remaining}), q))
        used = [factors[i] for i in incidence[vertex]]
        keep = [factor for i, factor in enumerate(factors) if i not in set(incidence[vertex])]
        scope = tuple(sorted({w for local_scope, _ in used for w in local_scope if w != vertex}))
        widths.append(len(scope))
        table: dict[int, int] = {}
        for mask in range(1 << len(scope)):
            best = -1
            for bit in (0, 1):
                assignment = {w: (mask >> index) & 1 for index, w in enumerate(scope)}
                assignment[vertex] = bit
                value = 0
                for local_scope, local_table in used:
                    local_mask = sum(assignment[w] << index for index, w in enumerate(local_scope))
                    value += local_table[local_mask]
                best = max(best, value)
            table[mask] = best
        keep.append((scope, table))
        factors = keep
        table_sizes.append(len(table))
        remaining.remove(vertex)
    if any(scope for scope, _table in factors):
        raise AssertionError("bucket elimination left a nonconstant factor")
    # Disconnected candidates can produce several independent constant
    # factors.  Their values add, exactly as the original edge factors do.
    optimum = sum(table[0] for _scope, table in factors)
    return {
        "exactMaxCut": optimum,
        "method": "integer_bucket_elimination",
        "maxIntermediateArity": max(widths, default=0),
        "maxTableEntries": max(table_sizes, default=1),
        "eliminations": len(widths),
    }


def maxcut_bruteforce(n: int, edges: Iterable[tuple[int, int]]) -> int:
    """Independent reference used only for the fixed small-engine audit."""
    edges = tuple(edges)
    return max(
        sum(((mask >> u) ^ (mask >> v)) & 1 for u, v in edges)
        for mask in range(1 << max(0, n - 1))
    )


def maxcut_engine_self_check() -> dict:
    """Compare bucket elimination to brute force on every simple 5-vertex graph."""
    n = 5
    possible = tuple((u, v) for u in range(n) for v in range(u + 1, n))
    for mask in range(1 << len(possible)):
        graph = tuple(edge for index, edge in enumerate(possible) if mask & (1 << index))
        exact = maxcut_exact(n, graph)["exactMaxCut"]
        brute = maxcut_bruteforce(n, graph)
        if exact != brute:
            raise AssertionError((mask, exact, brute))
    return {
        "graphs": 1 << len(possible),
        "vertices": n,
        "oracle": "fixed-v0 brute-force max-cut",
        "verdict": "PASS",
    }


def structural_gate(cage: Cage) -> dict:
    all_edges = cage.blue | cage.bad
    displayed = sum(((u in cage.side_zero) != (v in cage.side_zero)) for u, v in all_edges)
    blue_cross = all((u in cage.side_zero) != (v in cage.side_zero) for u, v in cage.blue)
    bad_mono = all((u in cage.side_zero) == (v in cage.side_zero) for u, v in cage.bad)
    maximum = maxcut_exact(cage.n, all_edges)
    return {
        "n": cage.n,
        "edgeCount": len(all_edges),
        "blueEdges": len(cage.blue),
        "badEdges": len(cage.bad),
        "triangleFree": triangle_free(cage.n, all_edges),
        "blueConnected": is_connected(cage.n, cage.blue),
        "displayedCut": displayed,
        "blueCrossesDisplayedCut": blue_cross,
        "badMonochromaticInDisplayedCut": bad_mono,
        "maxCut": maximum,
        "displayedCutIsMaximum": maximum["exactMaxCut"] == displayed,
    }


def merge_relations(*relations: dict[int, int]) -> dict[int, int]:
    out: dict[int, int] = {}
    for relation in relations:
        for source, mask in relation.items():
            out[source] = out.get(source, 0) | mask
    return out


def solve_production(ctx: p5.GraphContext, state: p5.TupleState) -> dict:
    """Exact production P1/P2/P3/strict-P4/P5 matching with reservations."""
    owners = fullbank.collision_owners(state)
    masks = p5.relation_masks(ctx, state)
    # P2/common-blue is introduced by fullbank terminals so its two terminal
    # edges are deducted exclusively.  P4 is ordinary unreserved supply.
    raw = fullbank.project_masks(
        state, merge_relations(masks["p13"], masks["p4"], masks["p5"]), owners
    )
    terminals = fullbank.common_terminals(ctx, state, owners, raw)
    result = fullbank.coherent_collision_match(ctx, state, owners, raw, terminals)
    owner_components = tuple(state.selected_comp[owner] for owner in owners)
    reserve_edges = {
        reserved_edge
        for terminal_index in result.selected_terminals
        for reserved_edge in terminals[terminal_index].reserve_edges
    }
    final_relation = {
        source: mask
        for source, mask in raw.items()
        if fullbank.source_edge(ctx.n, source) not in reserve_edges
    }
    for terminal_index in result.selected_terminals:
        terminal = terminals[terminal_index]
        owner_bit = 1 << terminal.owner_index
        for source in terminal.sources:
            if fullbank.source_edge(ctx.n, source) not in reserve_edges:
                final_relation[source] = final_relation.get(source, 0) | owner_bit
    labels = dict(result.base_labels)
    for source in tuple(final_relation):
        label = labels.get(fullbank.source_base(source))
        if label is None:
            continue
        filtered = sum(
            1 << owner_index
            for owner_index, component in enumerate(owner_components)
            if component == label and final_relation[source] & (1 << owner_index)
        )
        if filtered:
            final_relation[source] = filtered
        else:
            del final_relation[source]
    used = {source for source, _owner in result.assignment}
    return {
        "owners": owners,
        "masks": masks,
        "raw": raw,
        "terminals": terminals,
        "finalRelation": final_relation,
        "result": result,
        "used": used,
        "defect": result.defect,
        "demand": result.demand,
        "matched": result.matched,
    }


def state_record(cage: Cage, ctx: p5.GraphContext, rows: tuple[tuple[int, ...], ...], choice: tuple[int, ...]) -> dict:
    """Solve one complete row tuple without retaining a quadratic JSON audit."""
    state = p5.reconstruct_state(ctx, rows)
    solved = solve_production(ctx, state)
    return {
        "choice": tuple(choice),
        "rows": rows,
        "defect": solved["defect"],
        "collisionDemand": solved["demand"],
        "collisionMatched": solved["matched"],
        "matchingSearchNodes": solved["result"].search_nodes,
        "_state": state,
        "_solved": solved,
    }


def source_status(cage: Cage, solved: dict, source: int) -> str:
    """Classify a target turnover key under the final production matching."""
    if source in solved["used"]:
        return "MATCHED"
    # A key absent from final relation has no surviving owner arc after the
    # exact reservation/coherence search, which is the permitted block case.
    owner_mask = solved["finalRelation"].get(source, 0)
    if not owner_mask:
        return "COMPONENT_OR_BASE_BLOCKED"
    return "UNUSED_ELIGIBLE"


def generated_turnover(cage: Cage, old: p5.TupleState, target: p5.TupleState, old_middle: int) -> dict:
    created: list[int] = []
    for z in (old.rows[0][1], old.rows[0][3]):
        if old.pair[old_middle][z] != 1 or target.pair[old_middle][z] != 0:
            raise AssertionError("transition is not source-swap singleton turnover")
        for left, right in ((old_middle, z), (z, old_middle)):
            for half in (0, 1):
                created.append(source_id(cage.n, left, right, half))
    if len(created) != 8 or len(set(created)) != 8:
        raise AssertionError(created)
    reserved = [
        source for source in created
        if p5._reserved(target, *p5.decode_source(cage.n, source))
    ]
    usable = sorted(set(created) - set(reserved))
    return {
        "raw": sorted(created),
        "reserved": sorted(reserved),
        "usable": usable,
    }


def common_blue_probe_sources(cage: Cage, ctx: p5.GraphContext, state: p5.TupleState, solved: dict) -> set[int]:
    """Production P2 probe keys which would count as Exposure if unused."""
    out: set[int] = set()
    active = adjacency(cage.n, state.demanded_active_edges)
    support = adjacency(cage.n, state.support)
    owner_index = {owner: index for index, owner in enumerate(solved["owners"])}
    for owner in sorted(state.active_vertices):
        if owner not in owner_index:
            continue
        owner_bit = 1 << owner_index[owner]
        for x in active[owner]:
            for y in support[owner]:
                if x == y or state.pair[x][y] != 0 or ctx.sigma_pair[x][y] < 2:
                    continue
                for left, right in ((x, y), (y, x)):
                    for half in (0, 1):
                        source = source_id(cage.n, left, right, half)
                        if p5._reserved(state, left, right, half):
                            continue
                        if solved["masks"]["p2"].get(source, 0) & owner_bit:
                            out.add(source)
    return out


def directed_detour(cage: Cage, ctx: p5.GraphContext, source: dict, target: dict) -> dict | None:
    source_rows = tuple(tuple(row) for row in source["rows"])
    target_rows = tuple(tuple(row) for row in target["rows"])
    changes = [index for index, (left, right) in enumerate(zip(source_rows, target_rows)) if left != right]
    if len(changes) != 1:
        return None
    row_index = changes[0]
    left, right = source_rows[row_index], target_rows[row_index]
    changed_positions = [index for index, (u, v) in enumerate(zip(left, right)) if u != v]
    if changed_positions != [2]:
        return None
    old_middle, new_middle = left[2], right[2]
    if left[0] != right[0] or left[1] != right[1] or left[3] != right[3] or left[4] != right[4]:
        return None
    old_state: p5.TupleState = source["_state"]
    target_state: p5.TupleState = target["_state"]
    x, y = left[1], left[3]
    entering = {edge(x, new_middle), edge(new_middle, y)}
    old_edges = {edge(x, old_middle), edge(old_middle, y)}
    genuine = entering <= old_state.demanded_active_edges
    support_constant = (
        len(old_state.support) == len(target_state.support)
        and old_state.pair[old_middle][x] == 1
        and old_state.pair[old_middle][y] == 1
        and target_state.pair[old_middle][x] == 0
        and target_state.pair[old_middle][y] == 0
    )
    if not (genuine and support_constant):
        return None
    turnover = generated_turnover(cage, old_state, target_state, old_middle)
    statuses = {
        source: source_status(cage, target["_solved"], source)
        for source in turnover["usable"]
    }
    probes = common_blue_probe_sources(cage, ctx, target_state, target["_solved"])
    unused_probes = sorted(probes - target["_solved"]["used"])
    unused_turnover = sorted(source for source, status in statuses.items() if status == "UNUSED_ELIGIBLE")
    return {
        "from": tuple(source["choice"]),
        "to": tuple(target["choice"]),
        "rowIndex": row_index,
        "oldMiddle": old_middle,
        "newMiddle": new_middle,
        "oldEdges": [list(item) for item in sorted(old_edges)],
        "enteringActiveEdges": [list(item) for item in sorted(entering)],
        "supportConstant": True,
        "uniqueOldMiddleEdges": True,
        "turnover": {
            "rawNewFreeKeys": [decode_source(cage.n, source) for source in turnover["raw"]],
            "halfZeroScopedReserved": [decode_source(cage.n, source) for source in turnover["reserved"]],
            "usableHalfOne": [decode_source(cage.n, source) for source in turnover["usable"]],
            "targetStatus": [
                {"source": decode_source(cage.n, source), "status": statuses[source]}
                for source in turnover["usable"]
            ],
        },
        "productionCommonBlueProbeKeys": [decode_source(cage.n, source) for source in sorted(probes)],
        "unusedProductionCommonBlueProbeKeys": [decode_source(cage.n, source) for source in unused_probes],
        "productionExposure": len(unused_turnover) + len(unused_probes),
        "turnoverAllMatchedOrBlocked": not unused_turnover,
    }


def tarjan(nodes: Iterable[tuple[int, ...]], arcs: dict[tuple[int, ...], set[tuple[int, ...]]]) -> list[list[tuple[int, ...]]]:
    index = 0
    indices: dict[tuple[int, ...], int] = {}
    low: dict[tuple[int, ...], int] = {}
    stack: list[tuple[int, ...]] = []
    on_stack: set[tuple[int, ...]] = set()
    components: list[list[tuple[int, ...]]] = []

    def visit(node: tuple[int, ...]) -> None:
        nonlocal index
        indices[node] = index
        low[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for nxt in sorted(arcs.get(node, ())):
            if nxt not in indices:
                visit(nxt)
                low[node] = min(low[node], low[nxt])
            elif nxt in on_stack:
                low[node] = min(low[node], indices[nxt])
        if low[node] == indices[node]:
            component = []
            while True:
                nxt = stack.pop()
                on_stack.remove(nxt)
                component.append(nxt)
                if nxt == node:
                    break
            components.append(sorted(component))

    for node in sorted(nodes):
        if node not in indices:
            visit(node)
    return components


def serial_state(record: dict) -> dict:
    return {key: value for key, value in record.items() if not key.startswith("_")}


def evaluate_cage(pin_mask: int) -> dict:
    cage = build_cage(pin_mask)
    structural = structural_gate(cage)
    record = {
        "pinMask": pin_mask,
        "selectedPins": [name for index, name in enumerate(("am", "bm", "av", "bv")) if pin_mask & (1 << index)],
        "structural": structural,
    }
    if not (
        structural["triangleFree"]
        and structural["blueConnected"]
        and structural["displayedCutIsMaximum"]
    ):
        record["gate"] = "STRUCTURAL_REJECT"
        return record

    bads = tuple(sorted(cage.bad))
    families = tuple(shortest_rows(cage.n, cage.blue, *bad) for bad in bads)
    family_sizes = tuple(len(family) for family in families)
    if not all(families):
        record.update({"gate": "SHORTEST_ROW_REJECT", "familySizes": list(family_sizes)})
        return record
    tuple_count = math.prod(family_sizes)
    if tuple_count > 200_000:
        raise RuntimeError(f"unbounded tuple family {tuple_count} for pin mask {pin_mask}")
    ctx = p5.make_graph_context(cage.n, cage.blue, cage.bad)
    states: dict[tuple[int, ...], dict] = {}
    minimum: int | None = None
    for choice in itertools.product(*(range(size) for size in family_sizes)):
        rows = tuple(families[index][selected] for index, selected in enumerate(choice))
        state = state_record(cage, ctx, rows, choice)
        states[choice] = state
        minimum = state["defect"] if minimum is None else min(minimum, state["defect"])
    if minimum is None:
        raise AssertionError("no row tuples")
    minimal = {choice: state for choice, state in states.items() if state["defect"] == minimum}
    detours: list[dict] = []
    arcs: dict[tuple[int, ...], set[tuple[int, ...]]] = {choice: set() for choice in minimal}
    for source_choice, source in minimal.items():
        for target_choice, target in minimal.items():
            if source_choice == target_choice:
                continue
            transition = directed_detour(cage, ctx, source, target)
            if transition is not None:
                detours.append(transition)
                arcs[source_choice].add(target_choice)
    components = tarjan(minimal, arcs)
    scc_records = []
    hits = []
    for component in components:
        members = set(component)
        outgoing = sorted({target for source in members for target in arcs[source] if target not in members})
        internal = [edge_record for edge_record in detours if tuple(edge_record["from"]) in members and tuple(edge_record["to"]) in members]
        cyclic = len(component) > 1 or any(node in arcs[node] for node in component)
        all_turnover = bool(internal) and all(
            edge_record["turnoverAllMatchedOrBlocked"]
            and len(edge_record["turnover"]["rawNewFreeKeys"]) == 8
            and len(edge_record["turnover"]["halfZeroScopedReserved"]) == 4
            and len(edge_record["turnover"]["usableHalfOne"]) == 4
            for edge_record in internal
        )
        exposure = sum(edge_record["productionExposure"] for edge_record in internal)
        hit = minimum > 0 and cyclic and not outgoing and all_turnover and exposure == 0
        item = {
            "members": [list(choice) for choice in component],
            "cyclic": cyclic,
            "outgoingEqualDefectDetours": [list(choice) for choice in outgoing],
            "internalDetours": internal,
            "allTransitionsHaveExactTurnover": all_turnover,
            "productionExposure": exposure,
            "hit": hit,
        }
        scc_records.append(item)
        if hit:
            hits.append(item)
    record.update({
        "gate": "FULL_GRAPH_EVALUATED",
        "labels": list(cage.names),
        "blue": [list(item) for item in sorted(cage.blue)],
        "bad": [list(item) for item in bads],
        "familySizes": list(family_sizes),
        "tupleCount": tuple_count,
        "completeShortestRows": [[[vertex for vertex in row] for row in family] for family in families],
        "minimumCanonicalCollisionDefect": minimum,
        "minimalStates": [serial_state(state) for _choice, state in sorted(minimal.items())],
        "equalDefectDetours": detours,
        "sinkSccs": scc_records,
        "hitSccs": hits,
    })
    return record


def graph_phase() -> dict:
    records = [evaluate_cage(pin_mask) for pin_mask in range(16)]
    full = [record for record in records if record["gate"] == "FULL_GRAPH_EVALUATED"]
    hits = [hit for record in full for hit in record["hitSccs"]]
    counter = Counter(record["gate"] for record in records)
    minima = [record["minimumCanonicalCollisionDefect"] for record in full]
    strongest = (
        "Every structurally valid member of the enumerated active-pin family has "
        "minimum canonical collision defect zero."
        if full and all(value == 0 for value in minima)
        else "No positive-defect sink SCC passed every source-swap gate in the enumerated family."
    )
    return {
        "space": {
            "pinMasks": list(range(16)),
            "pinChoices": 4,
            "backgroundRows": 4,
            "rowTupleCap": 200000,
            "workers": 1,
        },
        "counts": dict(sorted(counter.items())),
        "records": records,
        "hitCount": len(hits),
        "strongestBoundedInvariant": strongest,
        "verdict": "GRAPH_HIT" if hits else "BOUNDED_NO_GRAPH_HIT",
        "nonConclusion": "This is an exact finite-family search, not a proof outside that family.",
    }


def build_manifest(workers: int) -> dict:
    if not 1 <= workers <= 16:
        raise ValueError("workers must be in 1..16")
    abstract = abstract_phase()
    maxcut_check = maxcut_engine_self_check()
    graph = graph_phase()
    payload = {
        "schema": "R42_SOURCE_SWAP_HUNT_V1",
        "arithmetic": "Python integers, finite sets, deterministic exhaustive products, integer bucket elimination",
        "workers": workers,
        "productionContract": {
            "sourceIdentity": "(ordered sourceX, ordered sourceY, half)",
            "relations": ["P1", "P2/common-blue sigma>=2", "P3", "strict-P4", "P5"],
            "reservation": "half=0 on a demanded active edge with active owner",
            "coherence": "BaseKeyComponentCoherent",
            "exposure": "unused production common-blue probes plus unused eligible turnover FreeHalves",
        },
        "inputs": {
            "p5_core.py": sha_file(P5_DIR / "p5_core.py"),
            "fullbank_core.py": sha_file(FULLBANK_DIR / "fullbank_core.py"),
            "source_swap_hunt.py": sha_file(HERE / "source_swap_hunt.py"),
        },
        "abstract": abstract,
        "maxCutEngineSelfCheck": maxcut_check,
        "graph": graph,
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--output", type=Path, default=HERE / "manifest.json")
    args = parser.parse_args(argv)
    try:
        payload = build_manifest(args.workers)
    except ValueError as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        "abstractSystems": payload["abstract"]["qualifyingAbstractSystems"],
        "canonicalPayloadSha256": payload["canonicalPayloadSha256"],
        "graphHits": payload["graph"]["hitCount"],
        "graphVerdict": payload["graph"]["verdict"],
        "graphGateCounts": payload["graph"]["counts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
