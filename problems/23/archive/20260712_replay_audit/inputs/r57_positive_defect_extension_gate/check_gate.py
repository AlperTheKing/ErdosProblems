#!/usr/bin/env python3
"""Exact finite R57-counterexample to R55-rotor extension gate.

The checker has four deliberately explicit scopes.

1. Rebuild the literal 16-vertex graph and its same-atom fork.
2. Exhaust every simple bad-atom extension on the fixed blue graph that keeps
   the inherited cut maximum.
3. Exhaust every extension on the same vertices with one additional legal
   blue edge, and every extension by one additional private blue leaf.
4. Run a non-simple duplicate-atom control to exercise the distinction between
   global grouped defect and R55's local residual unit core.

Every graph, cut, row, flow, lower-bound circulation, and residual-closure
calculation is integral.  The grouped network is the corrected global R53
six-family implementation used by the production-facing R55 trace.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys
from typing import Iterable, Iterator

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
SOFTCAP_DIR = HERE.parent / "r53_global_softcap_gate"
sys.path.insert(0, str(SOFTCAP_DIR))

import global_softcap as soft  # noqa: E402


Edge = tuple[int, int]
Row = tuple[int, ...]
Choice = tuple[int, ...]
Obligation = tuple[int, int, int, int]
SourceKey = tuple[int, int, int]

CORE_NAMES = ("s", "t", "a1", "a2", "a3", "b1", "b2", "b3")
CORE = {name: index for index, name in enumerate(CORE_NAMES)}
LEAF = {name: index + 8 for index, name in enumerate(CORE_NAMES)}
BASE_NAMES = CORE_NAMES + tuple(name + "'" for name in CORE_NAMES)

LEFT_ROW: Row = tuple(CORE[name] for name in ("s", "a1", "a2", "a3", "t"))
RIGHT_ROW: Row = tuple(CORE[name] for name in ("s", "b1", "b2", "b3", "t"))
FORK_LEFT = CORE["a1"]
FORK_RIGHT = CORE["b1"]


def norm_edge(left: int, right: int) -> Edge:
    return (left, right) if left < right else (right, left)


BASE_BLUE = frozenset(
    {norm_edge(left, right)
     for row in (LEFT_ROW, RIGHT_ROW)
     for left, right in zip(row, row[1:])}
    | {norm_edge(CORE[name], LEAF[name]) for name in CORE_NAMES}
)
BASE_BAD = norm_edge(CORE["s"], CORE["t"])
BASE_SHORE = frozenset(
    {CORE[name] for name in ("s", "t", "a2", "b2")}
    | {LEAF[name]
       for name in CORE_NAMES
       if name not in {"s", "t", "a2", "b2"}}
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def edge_label(edge: Edge, names: tuple[str, ...]) -> list[str]:
    return [names[edge[0]], names[edge[1]]]


def adjacency(n: int, edges: Iterable[Edge]) -> tuple[frozenset[int], ...]:
    out = [set() for _ in range(n)]
    for left, right in edges:
        out[left].add(right)
        out[right].add(left)
    return tuple(frozenset(items) for items in out)


def connected(n: int, edges: Iterable[Edge]) -> bool:
    adj = adjacency(n, edges)
    seen = {0}
    queue = deque([0])
    while queue:
        vertex = queue.popleft()
        for neighbor in adj[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return len(seen) == n


def triangle_free(n: int, edges: Iterable[Edge]) -> bool:
    edge_set = frozenset(edges)
    adj = adjacency(n, edge_set)
    return all(not (adj[left] & adj[right]) for left, right in edge_set)


def distances(n: int, edges: Iterable[Edge], source: int) -> tuple[int, ...]:
    adj = adjacency(n, edges)
    distance = [-1] * n
    distance[source] = 0
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for neighbor in adj[vertex]:
            if distance[neighbor] < 0:
                distance[neighbor] = distance[vertex] + 1
                queue.append(neighbor)
    return tuple(distance)


def shortest_rows(n: int, blue: Iterable[Edge], source: int, target: int) -> tuple[Row, ...]:
    edge_set = frozenset(blue)
    adj = adjacency(n, edge_set)
    from_source = distances(n, edge_set, source)
    from_target = distances(n, edge_set, target)
    length = from_source[target]
    if length < 0:
        return ()
    output: list[Row] = []

    def visit(path: list[int]) -> None:
        vertex = path[-1]
        if vertex == target:
            output.append(tuple(path))
            return
        for neighbor in sorted(adj[vertex]):
            if neighbor in path:
                continue
            if from_source[neighbor] != from_source[vertex] + 1:
                continue
            if from_source[neighbor] + from_target[neighbor] != length:
                continue
            path.append(neighbor)
            visit(path)
            path.pop()

    visit([source])
    return tuple(output)


def canonical_cut(mask: int, n: int) -> int:
    return mask ^ ((1 << n) - 1) if mask & 1 else mask


def displayed_mask(shore: Iterable[int], n: int) -> int:
    return canonical_cut(sum(1 << vertex for vertex in shore), n)


def normalized_masks(n: int) -> np.ndarray:
    # Vertex zero is fixed to shore zero, quotienting global complementation.
    return np.arange(1 << (n - 1), dtype=np.uint64) << np.uint64(1)


def cut_values(masks: np.ndarray, edges: Iterable[Edge]) -> np.ndarray:
    values = np.zeros(len(masks), dtype=np.int16)
    for left, right in edges:
        values += (((masks >> np.uint64(left)) ^ (masks >> np.uint64(right))) & 1).astype(np.int16)
    return values


def crosses(edge: Edge, mask: int) -> bool:
    return bool(((mask >> edge[0]) ^ (mask >> edge[1])) & 1)


def gamma_for_cut(n: int, edges: frozenset[Edge], mask: int) -> int | None:
    blue = frozenset(edge for edge in edges if crosses(edge, mask))
    if not connected(n, blue):
        return None
    return sum(
        (distances(n, blue, left)[right] + 1) ** 2
        for left, right in edges - blue
    )


def graph_cut_summary(n: int, edges: frozenset[Edge], shore: frozenset[int]) -> dict:
    masks = normalized_masks(n)
    values = cut_values(masks, edges)
    maximum = int(values.max())
    maximum_indices = np.flatnonzero(values == maximum)
    gammas = [
        value
        for value in (
            gamma_for_cut(n, edges, int(masks[index]))
            for index in maximum_indices
        )
        if value is not None
    ]
    shown_mask = displayed_mask(shore, n)
    shown_value = sum(crosses(edge, shown_mask) for edge in edges)
    shown_gamma = gamma_for_cut(n, edges, shown_mask)
    return {
        "normalizedCuts": len(masks),
        "maximum": maximum,
        "maximumCutOrbits": len(maximum_indices),
        "connectedMaximumCutOrbits": len(gammas),
        "displayedValue": shown_value,
        "minimumConnectedMaximumGamma": min(gammas) if gammas else None,
        "displayedGamma": shown_gamma,
        "displayedIsMaximum": shown_value == maximum,
        "displayedIsGammaMinimal": bool(gammas) and shown_gamma == min(gammas),
    }


def bitset(values: np.ndarray) -> int:
    packed = np.packbits(values.astype(bool), bitorder="little")
    return int.from_bytes(packed.tobytes(), "little")


def candidate_bad_edges(
    n: int,
    blue: frozenset[Edge],
    existing_bad: frozenset[Edge],
    shore: frozenset[int],
) -> tuple[Edge, ...]:
    all_distances = tuple(distances(n, blue, vertex) for vertex in range(n))
    return tuple(
        edge
        for edge in combinations(range(n), 2)
        if edge not in blue
        and edge not in existing_bad
        and ((edge[0] in shore) == (edge[1] in shore))
        and all_distances[edge[0]][edge[1]] == 4
    )


@dataclass(frozen=True)
class BadSubsetGate:
    candidates: tuple[Edge, ...]
    rows: dict[Edge, tuple[Row, ...]]
    raw_counts: dict[int, int]
    valid: dict[int, tuple[tuple[int, ...], ...]]


def gate_bad_subsets(
    n: int,
    blue: frozenset[Edge],
    mandatory_bad: frozenset[Edge],
    shore: frozenset[int],
    max_size: int,
) -> BadSubsetGate:
    """Exhaust bad subsets up to size three with exact all-cut constraints."""
    if max_size not in (1, 2, 3):
        raise ValueError(max_size)
    candidates = candidate_bad_edges(n, blue, mandatory_bad, shore)
    rows = {edge: shortest_rows(n, blue, *edge) for edge in candidates}
    if any(not family or len(family[0]) != 5 for family in rows.values()):
        raise AssertionError("candidate is not a checked length-four row atom")

    masks = normalized_masks(n)
    base_values = cut_values(masks, blue | mandatory_bad)
    slack = len(blue) - base_values
    if int(slack.min()) < 0:
        raise AssertionError("displayed cut is not maximum before atom extension")
    slack_bits = {value: bitset(slack == value) for value in range(max_size)}
    crossing_bits = [
        bitset(((masks >> np.uint64(left)) ^ (masks >> np.uint64(right))) & 1)
        for left, right in candidates
    ]

    raw_counts = {
        size: sum(1 for _ in combinations(range(len(candidates)), size))
        for size in range(1, max_size + 1)
    }
    valid: dict[int, list[tuple[int, ...]]] = {
        size: [] for size in range(1, max_size + 1)
    }

    allowed = [
        index
        for index, crossings in enumerate(crossing_bits)
        if not (crossings & slack_bits[0])
        and triangle_free(n, blue | mandatory_bad | {candidates[index]})
    ]
    valid[1] = [(index,) for index in allowed]
    if max_size == 1:
        return BadSubsetGate(candidates, rows, raw_counts, {1: tuple(valid[1])})

    valid_pairs: set[tuple[int, int]] = set()
    for left, right in combinations(allowed, 2):
        if crossing_bits[left] & crossing_bits[right] & slack_bits[1]:
            continue
        if not triangle_free(
            n, blue | mandatory_bad | {candidates[left], candidates[right]}
        ):
            continue
        valid_pairs.add((left, right))
    valid[2] = sorted(valid_pairs)
    if max_size == 2:
        return BadSubsetGate(
            candidates,
            rows,
            raw_counts,
            {size: tuple(items) for size, items in valid.items()},
        )

    for first, second, third in combinations(allowed, 3):
        if (
            (first, second) not in valid_pairs
            or (first, third) not in valid_pairs
            or (second, third) not in valid_pairs
        ):
            continue
        if (
            crossing_bits[first]
            & crossing_bits[second]
            & crossing_bits[third]
            & slack_bits[2]
        ):
            continue
        chosen = {candidates[first], candidates[second], candidates[third]}
        if triangle_free(n, blue | mandatory_bad | chosen):
            valid[3].append((first, second, third))
    return BadSubsetGate(
        candidates,
        rows,
        raw_counts,
        {size: tuple(items) for size, items in valid.items()},
    )


def merge_relation(target: dict[int, int], source: dict[int, int]) -> None:
    for base, owners in source.items():
        target[base] = target.get(base, 0) | owners


@dataclass
class ExactModel:
    ctx: object
    rows: tuple[Row, ...]
    state: object
    owners: tuple[int, ...]
    demand: tuple[int, ...]
    relation: dict[int, int]
    maximum_flow: int
    defect: int
    collision_units: int


def exact_model(ctx, rows: Iterable[Row]) -> ExactModel:
    normalized = tuple(rows)
    state = soft.reconstruct_state(ctx, normalized)
    owners, demand = soft.global_demands(state)
    relation: dict[int, int] = {}
    for family in soft.FAMILY_ORDER:
        addition, _audit = soft.FAMILY_BUILDERS[family](ctx, state, owners)
        merge_relation(relation, addition)
    flow, _assigned = soft.solve_grouped_flow(
        ctx.n,
        owners,
        demand,
        relation,
        state.active_edges,
        extract_assignment=False,
    )
    total_demand = sum(demand)
    if total_demand % 2:
        raise AssertionError("CollisionHalf demand must be even")
    if flow["maximumFlow"] + flow["defect"] != total_demand:
        raise AssertionError("maximum-flow accounting mismatch")
    return ExactModel(
        ctx=ctx,
        rows=normalized,
        state=state,
        owners=owners,
        demand=demand,
        relation=relation,
        maximum_flow=flow["maximumFlow"],
        defect=flow["defect"],
        collision_units=total_demand // 2,
    )


def pair_count(rows: Iterable[Row], left: int, right: int) -> int:
    return sum(left in row and right in row for row in rows)


def lower_bound_circulation(node_count: int, specs):
    network = soft.Dinic()
    for _ in range(node_count + 2):
        network.node()
    super_source = node_count
    super_sink = node_count + 1
    balance = [0] * node_count
    records = []
    for source, target, lower, upper, label in specs:
        if not 0 <= lower <= upper:
            raise AssertionError((source, target, lower, upper, label))
        arc = network.add_edge(source, target, upper - lower)
        balance[source] -= lower
        balance[target] += lower
        records.append((arc, lower, label))
    required = 0
    for vertex, amount in enumerate(balance):
        if amount > 0:
            network.add_edge(super_source, vertex, amount)
            required += amount
        elif amount < 0:
            network.add_edge(vertex, super_sink, -amount)
    if network.max_flow(super_source, super_sink) != required:
        return None
    return [
        (label, lower + (arc.initial - arc.cap))
        for arc, lower, label in records
    ]


def forced_divergence_feasible(model: ExactModel) -> bool:
    """Can an exact optimum use both direct (a1,b1) physical halves?"""
    n = model.ctx.n
    base = n * FORK_LEFT + FORK_RIGHT
    owner_mask = model.relation.get(base, 0)
    if (
        pair_count(model.rows, FORK_LEFT, FORK_RIGHT) != 0
        or not owner_mask
        or model.maximum_flow < 2
    ):
        return False

    source = 0
    sink = 1
    next_node = 2
    owner_nodes = {}
    for owner in model.owners:
        owner_nodes[owner] = next_node
        next_node += 1
    active_nodes = {}
    for edge in sorted(model.state.active_edges):
        active_nodes[edge] = next_node
        next_node += 1
    pool_nodes = {}
    for ordered_base in sorted(model.relation):
        pool_nodes[ordered_base] = next_node
        next_node += 1

    infinity = max(1, sum(model.demand))
    specs = []
    for owner, amount in zip(model.owners, model.demand):
        specs.append((source, owner_nodes[owner], 0, amount, ("source-owner", owner)))
    for ordered_base, mask in sorted(model.relation.items()):
        left, right = divmod(ordered_base, n)
        pool = pool_nodes[ordered_base]
        bits = mask
        while bits:
            bit = bits & -bits
            owner = model.owners[bit.bit_length() - 1]
            specs.append(
                (owner_nodes[owner], pool, 0, infinity, ("owner-pool", owner, ordered_base))
            )
            bits ^= bit
        edge = norm_edge(left, right)
        target = active_nodes[edge] if edge in active_nodes else sink
        lower = 2 if ordered_base == base else 0
        specs.append((pool, target, lower, 2, ("pool-out", ordered_base)))
    for edge, group in sorted(active_nodes.items()):
        specs.append((group, sink, 0, 2, ("active-cap", edge)))
    specs.append(
        (sink, source, model.maximum_flow, model.maximum_flow, ("fixed-optimum",))
    )
    return lower_bound_circulation(next_node, specs) is not None


def iter_family_states(families: tuple[tuple[Row, ...], ...]) -> Iterator[tuple[Choice, tuple[Row, ...]]]:
    for choice in product(*(range(len(family)) for family in families)):
        yield choice, tuple(families[index][value] for index, value in enumerate(choice))


def summarize_system(ctx, families: tuple[tuple[Row, ...], ...]) -> dict:
    records = [
        (choice, model)
        for choice, rows in iter_family_states(families)
        for model in (exact_model(ctx, rows),)
    ]
    collision_minimum = min(model.collision_units for _choice, model in records)
    defect_minimum = min(
        model.defect
        for _choice, model in records
        if model.collision_units == collision_minimum
    )
    face = [
        (choice, model)
        for choice, model in records
        if (model.collision_units, model.defect)
        == (collision_minimum, defect_minimum)
    ]
    free_face = [
        (choice, model)
        for choice, model in face
        if pair_count(model.rows, FORK_LEFT, FORK_RIGHT) == 0
    ]
    saturated = [
        choice
        for choice, model in free_face
        if forced_divergence_feasible(model)
    ]
    histogram = Counter(
        (model.collision_units, model.defect) for _choice, model in records
    )
    return {
        "rowTuples": len(records),
        "collisionMinimum": collision_minimum,
        "defectMinimumOnCollisionFace": defect_minimum,
        "lexFaceStates": len(face),
        "firstDivergenceFreeLexStates": len(free_face),
        "bothHalvesSaturableLexStates": len(saturated),
        "positivePayloadLexStates": len(face) if defect_minimum > 0 else 0,
        "rotorCandidateLexStates": len(saturated) if defect_minimum > 0 else 0,
        "metricHistogram": {
            f"{collision},{defect}": count
            for (collision, defect), count in sorted(histogram.items())
        },
    }


def aggregate_system_summaries(records: Iterable[dict]) -> dict:
    records = tuple(records)
    histogram = Counter()
    digest = hashlib.sha256()
    for record in records:
        summary = record["summary"]
        histogram[
            (summary["collisionMinimum"], summary["defectMinimumOnCollisionFace"])
        ] += 1
        digest.update(canonical_bytes(record))
    return {
        "systems": len(records),
        "rowTuples": sum(record["summary"]["rowTuples"] for record in records),
        "lexMetricHistogram": {
            f"{collision},{defect}": count
            for (collision, defect), count in sorted(histogram.items())
        },
        "systemsWithPositiveLexDefect": sum(
            record["summary"]["defectMinimumOnCollisionFace"] > 0
            for record in records
        ),
        "systemsWithSaturableLexFork": sum(
            record["summary"]["bothHalvesSaturableLexStates"] > 0
            for record in records
        ),
        "rotorCandidateLexStates": sum(
            record["summary"]["rotorCandidateLexStates"] for record in records
        ),
        "canonicalRecordSha256": digest.hexdigest().upper(),
    }


def explicit_forced_flow(model: ExactModel) -> dict | None:
    """Return one obligation-level optimum forced to use both divergence keys."""
    n = model.ctx.n
    obligations = tuple(
        obligation
        for owner in model.owners
        for obligation in soft.collision_obligations(model.state, owner)
    )
    keys = tuple(
        (ordered_base // n, ordered_base % n, half)
        for ordered_base in sorted(model.relation)
        for half in (0, 1)
    )
    owner_index = {owner: index for index, owner in enumerate(model.owners)}
    active_edges = frozenset(model.state.active_edges)

    source = 0
    sink = 1
    next_node = 2
    obligation_node = {}
    for obligation in obligations:
        obligation_node[obligation] = next_node
        next_node += 1
    key_node = {}
    for key in keys:
        key_node[key] = next_node
        next_node += 1
    group_node = {}
    for edge in sorted(active_edges):
        group_node[edge] = next_node
        next_node += 1

    forced = {
        (FORK_LEFT, FORK_RIGHT, 0),
        (FORK_LEFT, FORK_RIGHT, 1),
    }
    specs = []
    for obligation in obligations:
        specs.append((source, obligation_node[obligation], 0, 1, ("source-obligation", obligation)))
        bit = 1 << owner_index[obligation[0]]
        for key in keys:
            ordered_base = n * key[0] + key[1]
            if model.relation.get(ordered_base, 0) & bit:
                specs.append(
                    (
                        obligation_node[obligation],
                        key_node[key],
                        0,
                        1,
                        ("obligation-key", obligation, key),
                    )
                )
    for key in keys:
        edge = norm_edge(key[0], key[1])
        target = group_node[edge] if edge in active_edges else sink
        lower = int(key in forced)
        specs.append((key_node[key], target, lower, 1, ("key-out", key)))
    for edge, node in sorted(group_node.items()):
        specs.append((node, sink, 0, 2, ("group-out", edge)))
    specs.append(
        (sink, source, model.maximum_flow, model.maximum_flow, ("fixed-optimum",))
    )
    flows = lower_bound_circulation(next_node, specs)
    if flows is None:
        return None

    assignment = {
        label[1]: label[2]
        for label, amount in flows
        if label[0] == "obligation-key" and amount == 1
    }
    if len(assignment) != model.maximum_flow:
        raise AssertionError("explicit assignment has wrong cardinality")
    if len(set(assignment.values())) != len(assignment):
        raise AssertionError("literal key reused")
    active_load = Counter(
        norm_edge(*key[:2])
        for key in assignment.values()
        if norm_edge(*key[:2]) in active_edges
    )
    if any(load > 2 for load in active_load.values()):
        raise AssertionError("active-edge group capacity exceeded")
    if not forced <= set(assignment.values()):
        raise AssertionError("forced keys absent")
    return {
        "obligations": obligations,
        "keys": keys,
        "assignment": assignment,
        "activeEdges": active_edges,
    }


def unit_core_certificate(model: ExactModel) -> dict | None:
    explicit = explicit_forced_flow(model)
    if explicit is None:
        return None
    obligations: tuple[Obligation, ...] = explicit["obligations"]
    keys: tuple[SourceKey, ...] = explicit["keys"]
    assignment: dict[Obligation, SourceKey] = explicit["assignment"]
    active_edges: frozenset[Edge] = explicit["activeEdges"]
    matched_by_key = {key: obligation for obligation, key in assignment.items()}
    unmatched = tuple(sorted(set(obligations) - set(assignment)))
    if not unmatched:
        raise AssertionError("positive core requested from defect-zero flow")
    root = unmatched[0]
    owner_index = {owner: index for index, owner in enumerate(model.owners)}
    n = model.ctx.n

    # Typed residual nodes: ('o', obligation), ('k', key), ('g', edge), ('t', None).
    residual: dict[tuple, set[tuple]] = {}

    def arc(source_node: tuple, target_node: tuple) -> None:
        residual.setdefault(source_node, set()).add(target_node)

    for obligation in obligations:
        owner_bit = 1 << owner_index[obligation[0]]
        for key in keys:
            ordered_base = n * key[0] + key[1]
            if not (model.relation.get(ordered_base, 0) & owner_bit):
                continue
            if assignment.get(obligation) == key:
                arc(("k", key), ("o", obligation))
            else:
                arc(("o", obligation), ("k", key))
    for key in keys:
        edge = norm_edge(*key[:2])
        target = ("g", edge) if edge in active_edges else ("t", None)
        if key in matched_by_key:
            arc(target, ("k", key))
        else:
            arc(("k", key), target)
    for edge in active_edges:
        load = sum(norm_edge(*key[:2]) == edge for key in assignment.values())
        if load < 2:
            arc(("g", edge), ("t", None))
        if load:
            arc(("t", None), ("g", edge))

    start = ("o", root)
    reached = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in residual.get(node, ()):
            if neighbor not in reached:
                reached.add(neighbor)
                queue.append(neighbor)
    if ("t", None) in reached:
        raise AssertionError("maximum flow has an augmenting residual path")

    reached_obligations = {value for kind, value in reached if kind == "o"}
    reached_keys = {value for kind, value in reached if kind == "k"}
    direct_capacity = sum(
        norm_edge(*key[:2]) not in active_edges for key in reached_keys
    )
    active_counts = Counter(
        norm_edge(*key[:2])
        for key in reached_keys
        if norm_edge(*key[:2]) in active_edges
    )
    grouped_capacity = direct_capacity + sum(
        min(2, count) for count in active_counts.values()
    )
    forced_keys = (
        (FORK_LEFT, FORK_RIGHT, 0),
        (FORK_LEFT, FORK_RIGHT, 1),
    )
    successors = tuple(matched_by_key[key] for key in forced_keys)
    residual_closed = all(
        neighbor in reached
        for node in reached
        for neighbor in residual.get(node, ())
    )
    if not residual_closed:
        raise AssertionError("residual BFS result is not successor-closed")
    return {
        "globalDefect": model.defect,
        "leastUnmatchedRoot": list(root),
        "obligationCount": len(reached_obligations),
        "rawReachedSourceKeys": len(reached_keys),
        "directReachedCapacity": direct_capacity,
        "activeReachedGroupCounts": {
            f"{edge[0]},{edge[1]}": count
            for edge, count in sorted(active_counts.items())
        },
        "sourceCapacity": grouped_capacity,
        "positiveUnitDefect": len(reached_obligations) == grouped_capacity + 1,
        "forkKeysReached": all(key in reached_keys for key in forced_keys),
        "bothHalvesMatched": True,
        "successorObligations": [list(obligation) for obligation in successors],
        "successorsInUnitCore": all(
            obligation in reached_obligations for obligation in successors
        ),
        "successorSinkClosed": residual_closed,
        "noSimultaneous": True,
        "residualSinkUnreachable": True,
    }


def base_graph_payload() -> dict:
    n = 16
    edges = BASE_BLUE | {BASE_BAD}
    if not triangle_free(n, edges) or not connected(n, BASE_BLUE):
        raise AssertionError("base graph structural check failed")
    rows = shortest_rows(n, BASE_BLUE, CORE["s"], CORE["t"])
    if set(rows) != {LEFT_ROW, RIGHT_ROW}:
        raise AssertionError(rows)
    cut = graph_cut_summary(n, edges, BASE_SHORE)
    if not cut["displayedIsMaximum"] or not cut["displayedIsGammaMinimal"]:
        raise AssertionError(cut)
    ctx = soft.make_graph_context(n, BASE_BLUE, {BASE_BAD})
    bare = summarize_system(ctx, ((LEFT_ROW, RIGHT_ROW),))
    if bare["collisionMinimum"] != 0 or bare["defectMinimumOnCollisionFace"] != 0:
        raise AssertionError(bare)
    return {
        "vertices": n,
        "blueEdges": len(BASE_BLUE),
        "badEdges": 1,
        "triangleFree": True,
        "blueConnected": True,
        "cut": cut,
        "shortestSTDistance": 4,
        "completeShortestRows": [[BASE_NAMES[v] for v in row] for row in rows],
        "fork": {
            "firstDivergencePosition": 1,
            "commonPredecessor": "s",
            "leftVertex": "a1",
            "rightVertex": "b1",
            "alignedInternalSharingMask": [0, 0, 0],
        },
        "bareSoftcap": bare,
        "bareFirstFailedRotorField": "positiveUnitDefect (no obligations and no unmatched root)",
    }


def fixed_blue_extension_payload() -> dict:
    n = 16
    gate = gate_bad_subsets(
        n, BASE_BLUE, frozenset({BASE_BAD}), BASE_SHORE, max_size=2
    )
    singleton_records = []
    for (index,) in gate.valid[1]:
        edge = gate.candidates[index]
        bad = frozenset({BASE_BAD, edge})
        ctx = soft.make_graph_context(n, BASE_BLUE, bad)
        summary = summarize_system(ctx, ((LEFT_ROW, RIGHT_ROW), gate.rows[edge]))
        cut = graph_cut_summary(n, BASE_BLUE | bad, BASE_SHORE)
        singleton_records.append(
            {
                "addedBad": edge_label(edge, BASE_NAMES),
                "completeRows": len(gate.rows[edge]),
                "cut": {
                    "maximumCutOrbits": cut["maximumCutOrbits"],
                    "minimumConnectedMaximumGamma": cut["minimumConnectedMaximumGamma"],
                    "displayedGamma": cut["displayedGamma"],
                    "displayedIsGammaMinimal": cut["displayedIsGammaMinimal"],
                },
                "summary": summary,
            }
        )
    aggregate = aggregate_system_summaries(singleton_records)
    if len(gate.valid[1]) != 27 or gate.valid[2]:
        raise AssertionError((len(gate.valid[1]), len(gate.valid[2])))
    if aggregate["systemsWithPositiveLexDefect"]:
        raise AssertionError("unexpected fixed-blue positive extension")
    return {
        "universe": (
            "all additional simple bad edges on the fixed 16-vertex blue graph "
            "whose endpoints share the displayed shore and have blue distance four"
        ),
        "candidateBadAtoms": len(gate.candidates),
        "rawSingletons": gate.raw_counts[1],
        "maximumCutTriangleFreeSingletons": len(gate.valid[1]),
        "rawPairs": gate.raw_counts[2],
        "maximumCutTriangleFreePairs": len(gate.valid[2]),
        "largerSubsetsExcluded": (
            "yes: every pair already violates maximum-cut optimality, and adding "
            "same-shore bad edges cannot repair that violating cut"
        ),
        "aggregate": aggregate,
        "allSingletonsGammaMinimal": all(
            record["cut"]["displayedIsGammaMinimal"] for record in singleton_records
        ),
        "records": singleton_records,
        "verdict": "NO_POSITIVE_UNIT_DEFECT_ROTOR_ON_FIXED_BLUE_GRAPH",
    }


def legal_one_blue_edges() -> tuple[Edge, ...]:
    output = []
    for edge in combinations(range(16), 2):
        if edge in BASE_BLUE or edge == BASE_BAD:
            continue
        if (edge[0] in BASE_SHORE) == (edge[1] in BASE_SHORE):
            continue
        blue = BASE_BLUE | {edge}
        full = blue | {BASE_BAD}
        if not triangle_free(16, full):
            continue
        if distances(16, blue, CORE["s"])[CORE["t"]] != 4:
            continue
        values = cut_values(normalized_masks(16), full)
        if int(values.max()) != len(blue):
            continue
        output.append(edge)
    return tuple(output)


def one_blue_extension_payload() -> dict:
    additions = legal_one_blue_edges()
    all_records = {1: [], 2: []}
    raw_counts = Counter()
    valid_counts = Counter()
    triple_valid = 0
    for blue_edge in additions:
        blue = BASE_BLUE | {blue_edge}
        fork_family = shortest_rows(16, blue, CORE["s"], CORE["t"])
        if LEFT_ROW not in fork_family or RIGHT_ROW not in fork_family:
            raise AssertionError("blue extension destroyed the literal fork rows")
        gate = gate_bad_subsets(
            16, blue, frozenset({BASE_BAD}), BASE_SHORE, max_size=3
        )
        for size, count in gate.raw_counts.items():
            raw_counts[size] += count
            valid_counts[size] += len(gate.valid[size])
        triple_valid += len(gate.valid[3])
        for size in (1, 2):
            for indices in gate.valid[size]:
                selected = tuple(gate.candidates[index] for index in indices)
                bad = frozenset({BASE_BAD, *selected})
                ctx = soft.make_graph_context(16, blue, bad)
                families = (fork_family,) + tuple(
                    gate.rows[edge] for edge in selected
                )
                all_records[size].append(
                    {
                        "addedBlue": edge_label(blue_edge, BASE_NAMES),
                        "completeForkRows": len(fork_family),
                        "addedBad": [edge_label(edge, BASE_NAMES) for edge in selected],
                        "summary": summarize_system(ctx, families),
                    }
                )
    if len(additions) != 42 or triple_valid:
        raise AssertionError((len(additions), triple_valid))
    aggregate = {
        str(size): aggregate_system_summaries(all_records[size])
        for size in (1, 2)
    }
    if any(item["systemsWithPositiveLexDefect"] for item in aggregate.values()):
        raise AssertionError("unexpected one-blue positive extension")
    return {
        "universe": (
            "one additional cross-shore blue edge on the same 16 vertices, "
            "preserving triangle-freeness and blue distance d(s,t)=4, followed "
            "by every maximum-cut-compatible distance-four bad-atom subset"
        ),
        "legalBlueAdditions": len(additions),
        "rawBadSubsets": {str(key): value for key, value in sorted(raw_counts.items())},
        "maximumCutTriangleFreeBadSubsets": {
            str(key): value for key, value in sorted(valid_counts.items())
        },
        "largerSubsetsExcluded": (
            "yes: no valid triple exists, and a violating triple remains violating "
            "after more same-shore bad edges are added"
        ),
        "aggregateByAddedBadAtoms": aggregate,
        "verdict": "NO_POSITIVE_UNIT_DEFECT_ROTOR_WITH_ONE_ADDED_BLUE_EDGE",
    }


def one_private_leaf_extension_payload() -> dict:
    records = {1: [], 2: []}
    raw_counts = Counter()
    valid_counts = Counter()
    triple_valid = 0
    for attachment in range(16):
        n = 17
        new_vertex = 16
        blue = BASE_BLUE | {norm_edge(attachment, new_vertex)}
        shore = set(BASE_SHORE)
        if attachment not in shore:
            shore.add(new_vertex)
        shore = frozenset(shore)
        names = BASE_NAMES + (f"new@{BASE_NAMES[attachment]}",)
        fork_family = shortest_rows(n, blue, CORE["s"], CORE["t"])
        if LEFT_ROW not in fork_family or RIGHT_ROW not in fork_family:
            raise AssertionError("private leaf destroyed the literal fork rows")
        gate = gate_bad_subsets(
            n, blue, frozenset({BASE_BAD}), shore, max_size=3
        )
        for size, count in gate.raw_counts.items():
            raw_counts[size] += count
            valid_counts[size] += len(gate.valid[size])
        triple_valid += len(gate.valid[3])
        for size in (1, 2):
            for indices in gate.valid[size]:
                selected = tuple(gate.candidates[index] for index in indices)
                ctx = soft.make_graph_context(n, blue, {BASE_BAD, *selected})
                families = (fork_family,) + tuple(
                    gate.rows[edge] for edge in selected
                )
                records[size].append(
                    {
                        "attachment": BASE_NAMES[attachment],
                        "completeForkRows": len(fork_family),
                        "addedBad": [edge_label(edge, names) for edge in selected],
                        "summary": summarize_system(ctx, families),
                    }
                )
    if triple_valid:
        raise AssertionError(triple_valid)
    aggregate = {
        str(size): aggregate_system_summaries(records[size]) for size in (1, 2)
    }
    if any(item["systemsWithPositiveLexDefect"] for item in aggregate.values()):
        raise AssertionError("unexpected one-leaf positive extension")
    return {
        "universe": (
            "one new degree-one blue vertex attached to any base vertex, placed "
            "opposite its parent, followed by every maximum-cut-compatible "
            "distance-four bad-atom subset"
        ),
        "attachments": 16,
        "rawBadSubsets": {str(key): value for key, value in sorted(raw_counts.items())},
        "maximumCutTriangleFreeBadSubsets": {
            str(key): value for key, value in sorted(valid_counts.items())
        },
        "largerSubsetsExcluded": "yes: no valid triple exists",
        "aggregateByAddedBadAtoms": aggregate,
        "verdict": "NO_POSITIVE_UNIT_DEFECT_ROTOR_WITH_ONE_PRIVATE_LEAF",
    }


def duplicate_atom_control_payload() -> dict:
    ctx = soft.make_graph_context(16, BASE_BLUE, {BASE_BAD})
    records = []
    first_positive = None
    for copies in range(1, 9):
        families = tuple((LEFT_ROW, RIGHT_ROW) for _ in range(copies))
        summary = summarize_system(ctx, families)
        records.append({"copies": copies, "summary": summary})
        if first_positive is None:
            for choice, rows in iter_family_states(families):
                model = exact_model(ctx, rows)
                if model.defect <= 0:
                    continue
                if pair_count(rows, FORK_LEFT, FORK_RIGHT) != 0:
                    continue
                if not forced_divergence_feasible(model):
                    continue
                core = unit_core_certificate(model)
                if core is not None:
                    first_positive = {
                        "copies": copies,
                        "choice": list(choice),
                        "collisionUnits": model.collision_units,
                        "globalDefect": model.defect,
                        "isLexMinimum": (
                            model.collision_units == summary["collisionMinimum"]
                            and model.defect == summary["defectMinimumOnCollisionFace"]
                        ),
                        "unitCore": core,
                    }
                    break
    if any(record["summary"]["defectMinimumOnCollisionFace"] for record in records):
        raise AssertionError("duplicate control unexpectedly has positive lex defect")
    return {
        "status": "RELAXED_CONTROL_NOT_A_SIMPLE_GRAPH_EXTENSION",
        "meaning": (
            "repeat the same s-t BadEdgeData row family; this supplies collision "
            "multiplicity but violates the simple one-atom-per-bad-edge interpretation"
        ),
        "records": records,
        "firstPositiveNonLexState": first_positive,
        "verdict": "SATURATION_AND_LOCAL_UNIT_CORE_DO_NOT_REPAIR_LEX_DEFECT_ZERO",
    }


def report_text(payload: dict, result_sha: str) -> str:
    graph = payload["baseGraph"]
    fixed = payload["fixedBlueExtensions"]
    blue = payload["oneBlueEdgeExtensions"]
    leaf = payload["onePrivateLeafExtensions"]
    duplicate = payload["duplicateAtomControl"]
    control = duplicate["firstPositiveNonLexState"]
    control_line = "No positive control state was found."
    if control is not None:
        core = control["unitCore"]
        control_line = (
            f"The first positive non-lex control occurs at {control['copies']} duplicate atoms "
            f"with global defect {control['globalDefect']}; its least-root residual core has "
            f"|O_K|={core['obligationCount']} and cap(S_K)={core['sourceCapacity']}."
        )
    return f"""# R57 positive-defect extension gate

## Verdict

The literal 16-vertex same-atom fork is **not** an R55 positive-unit-defect
saturated exclusive-fork rotor.  Either selected `s-t` row has no collision
obligations, hence exact grouped defect zero, no unmatched root, and no local
unit core.

No realization exists in any exhaustively tested minimal extension class:

- fixed blue graph, every compatible simple bad atom: {fixed['candidateBadAtoms']} candidates;
  {fixed['maximumCutTriangleFreeSingletons']} singleton systems survive and all have lex defect zero;
  no pair preserves maximum-cut optimality;
- one legal blue edge on the same vertices: {blue['legalBlueAdditions']} blue additions,
  {blue['maximumCutTriangleFreeBadSubsets']['1']} one-atom and
  {blue['maximumCutTriangleFreeBadSubsets']['2']} two-atom systems survive, all lex defect zero;
  no three-atom system survives;
- one new private blue leaf: {leaf['attachments']} attachments,
  {leaf['maximumCutTriangleFreeBadSubsets']['1']} one-atom and
  {leaf['maximumCutTriangleFreeBadSubsets']['2']} two-atom systems survive, all lex defect zero;
  no three-atom system survives.

Thus a realization, if one exists, needs a genuinely larger protection gadget:
at least two non-pendant blue-edge edits or a more general multi-edge vertex
extension.  This is a finite lower bound in the stated extension universe, not
a universal proof of `noPositiveDefectSaturatedExclusiveForkRotor`.

## Exact checks

The base graph replay exhausts {graph['cut']['normalizedCuts']} cuts modulo
complementation.  Its maximum is {graph['cut']['maximum']}, displayed Gamma is
{graph['cut']['displayedGamma']}, and the complete shortest `s-t` row family has
{len(graph['completeShortestRows'])} rows.  All corrected global soft-cap flows
use the six R53 relation families, literal key capacity one, and active-edge
group capacity two.

R55 local unit defect is checked separately from global defect: start at the
least unmatched obligation of an exact optimal integral flow, traverse the
full obligation/key/group residual network, and verify
`obligationCount = sourceCapacity + 1`, where active four-key blocks contribute
at most two.  {control_line}  It is not lex-minimal, so it is not an R55 state.

TICK-117 leaves the successor and sink bodies checker-defined.  This gate makes
that instantiation explicit: successors are the two matched obligations reached
by reversing the saturated divergence keys; the sink is their full residual
BFS closure; noSimultaneous means one selected row per bad atom.

All arithmetic is integer arithmetic.  No floating point, randomized search,
or tolerance is used.  Integrality of this finite grouped network gives the
same optimum as its rational relaxation.

## Replay

From `E:\\Projects\\ErdosProblems`:

```powershell
python -B tmp/fanout/r57_positive_defect_extension_gate/check_gate.py
```

The command rewrites `result.json` and `REPORT.md` deterministically and prints
their SHA-256 digests.

## Digests

```text
check_gate.py       {payload['inputs']['checkGateSha256']}
global_softcap.py   {payload['inputs']['globalSoftcapSha256']}
result.json         {result_sha}
```
"""


def build_payload() -> dict:
    if tuple(soft.FAMILY_ORDER) != (
        "P1_sameFirst",
        "P2_commonBad",
        "P3_rowCompanion",
        "P4_outsideAttachment",
        "P5_quiescentAttachment",
        "commonBlue",
    ):
        raise AssertionError("R53 family interface drift")
    return {
        "schema": "R57_POSITIVE_DEFECT_EXTENSION_GATE_V1",
        "status": "PASS",
        "verdict": "NO_ROTOR_IN_EXHAUSTED_MINIMAL_EXTENSION_CLASSES",
        "arithmetic": {
            "kind": "exact integers",
            "rationalOptimum": "equal by integral finite grouped network",
            "floatingPoint": False,
            "randomized": False,
        },
        "inputs": {
            "checkGate": str((HERE / "check_gate.py").relative_to(ROOT)),
            "checkGateSha256": sha256(HERE / "check_gate.py"),
            "globalSoftcap": str(
                (SOFTCAP_DIR / "global_softcap.py").relative_to(ROOT)
            ),
            "globalSoftcapSha256": sha256(SOFTCAP_DIR / "global_softcap.py"),
            "counterexampleWriteup": str(
                (
                    ROOT
                    / "problems"
                    / "23"
                    / "writeup"
                    / "WALL_ATTACK_R57_CURRENT_INTERFACE_COUNTEREXAMPLE.md"
                ).relative_to(ROOT)
            ),
        },
        "model": {
            "demand": "every global CollisionHalf",
            "relations": list(soft.FAMILY_ORDER),
            "literalKeyCapacity": 1,
            "activeUndirectedEdgeGroupCapacity": 2,
            "forkDivergenceOrderedBase": ["a1", "b1"],
            "positiveUnitDefect": (
                "least-unmatched-root residual closure has "
                "obligationCount = grouped sourceCapacity + 1"
            ),
            "auditOrder": "lexicographic (owner, other, copy, half)",
            "successorCheck": (
                "the two forced divergence keys map by reverse flow to distinct "
                "matched obligations inside the same residual core"
            ),
            "sinkCheck": "full residual BFS closure under every successor arc",
            "noSimultaneous": "one selected row per bad atom; the fork rows are distinct",
        },
        "baseGraph": base_graph_payload(),
        "fixedBlueExtensions": fixed_blue_extension_payload(),
        "oneBlueEdgeExtensions": one_blue_extension_payload(),
        "onePrivateLeafExtensions": one_private_leaf_extension_payload(),
        "duplicateAtomControl": duplicate_atom_control_payload(),
        "scopeBoundary": (
            "not searched: extensions with two or more non-pendant blue-edge "
            "edits, or new vertices of blue degree at least two"
        ),
    }


def main() -> int:
    payload = build_payload()
    result_path = HERE / "result.json"
    result_path.write_bytes(json.dumps(payload, indent=2, sort_keys=True).encode("ascii") + b"\n")
    result_sha = sha256(result_path)
    report_path = HERE / "REPORT.md"
    report_path.write_text(report_text(payload, result_sha), encoding="ascii")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "verdict": payload["verdict"],
                "resultSha256": result_sha,
                "reportSha256": sha256(report_path),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
