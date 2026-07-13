#!/usr/bin/env python3
"""Exact necessary-condition gate for the R55 soft-cap rotor pattern.

This gate reuses the corrected global R53 soft-cap implementation.  It is a
finite falsifier search on two supplied state spaces, not a universal theorem.
All arithmetic is integer arithmetic and every flow is an integral max flow.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from concurrent.futures import ProcessPoolExecutor
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
from itertools import combinations
import json
import os
from pathlib import Path
import sys
from typing import Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOFTCAP_DIR = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate"
R35_PATH = ROOT / "tmp" / "fanout" / "r35_24_trade" / "evaluate_trade.py"
ROTOR_PATH = ROOT / "problems" / "23" / "writeup" / "_claude_r39_8vtx_rotor_gate.py"
for path in (SOFTCAP_DIR,):
    sys.path.insert(0, str(path))

import global_softcap as soft  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_bytes(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")


def load_module(name: str, path: Path, *, quiet: bool = False):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    if quiet:
        with redirect_stdout(io.StringIO()):
            spec.loader.exec_module(module)
    else:
        spec.loader.exec_module(module)
    return module


R35 = load_module("r56_r35_fixture", R35_PATH)


def r35_rows(choice: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(R35.ROW_FAMILIES[index][row_index])
        for index, row_index in enumerate(choice)
    )


R35_CTX = soft.make_graph_context(R35.N, R35.BLUE, R35.BAD)
R35_RADICES = tuple(R35.RADICES)


def rotor_fixture():
    module = load_module("r56_rotor_fixture", ROTOR_PATH, quiet=True)
    blue = [tuple(sorted(edge)) for edge in module.blue]
    bad = [tuple(sorted(edge)) for edge in module.bad]
    ctx = soft.make_graph_context(8, blue, bad)
    families = (
        tuple(tuple(row) for row in module.fam_ab),
        tuple(tuple(row) for row in module.fam_pq),
    )
    label_by_choice = {}
    for label, rows in module.states.items():
        choice = tuple(families[index].index(tuple(row)) for index, row in enumerate(rows))
        label_by_choice[choice] = label
    choices = tuple(sorted(label_by_choice))
    assert len(choices) == 4
    return ctx, families, choices, label_by_choice


def neighborhood(center: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    """Exact Hamming-at-most-two neighborhood used by r35_exchange_gate.py."""
    states = {tuple(center)}
    for index, radix in enumerate(R35_RADICES):
        for replacement in range(radix):
            if replacement != center[index]:
                state = list(center)
                state[index] = replacement
                states.add(tuple(state))
    for left, right in combinations(range(len(center)), 2):
        for left_replacement in range(R35_RADICES[left]):
            if left_replacement == center[left]:
                continue
            for right_replacement in range(R35_RADICES[right]):
                if right_replacement == center[right]:
                    continue
                state = list(center)
                state[left] = left_replacement
                state[right] = right_replacement
                states.add(tuple(state))
    return tuple(sorted(states))


def merge_relation(target: dict[int, int], source: dict[int, int]) -> None:
    for base, mask in source.items():
        target[base] = target.get(base, 0) | mask


def build_full_model(ctx, rows):
    """Build all six relations and one exact grouped maximum flow."""
    state = soft.reconstruct_state(ctx, rows)
    owners, demand = soft.global_demands(state)
    nonfree_active = [
        (x, y)
        for x, y in sorted(state.active_edges)
        if state.pair[x][y] != 0 or state.pair[y][x] != 0
    ]
    if nonfree_active:
        raise AssertionError(("active edge lacks four FreeHalf keys", nonfree_active))
    relation: dict[int, int] = {}
    family_sizes = {}
    for family in soft.FAMILY_ORDER:
        addition, _audit = soft.FAMILY_BUILDERS[family](ctx, state, owners)
        family_sizes[family] = {
            "orderedBases": len(addition),
            "ownerBaseArcs": sum(mask.bit_count() for mask in addition.values()),
        }
        merge_relation(relation, addition)
    flow, assigned = soft.solve_grouped_flow(
        ctx.n,
        owners,
        demand,
        relation,
        state.active_edges,
        extract_assignment=True,
    )
    return state, owners, demand, relation, family_sizes, flow, assigned


def validate_assignment(ctx, state, owners, demand, relation, flow, assigned):
    owner_index = {owner: index for index, owner in enumerate(owners)}
    used = Counter()
    active_load = Counter()
    records = []
    for owner in owners:
        keys = sorted(assigned[owner])
        if len(keys) > demand[owner_index[owner]]:
            raise AssertionError((owner, len(keys), demand[owner_index[owner]]))
        bit = 1 << owner_index[owner]
        for x, y, half in keys:
            if x == y or half not in (0, 1) or state.pair[x][y] != 0:
                raise AssertionError(("not a literal FreeHalf", owner, x, y, half))
            if not relation.get(ctx.n * x + y, 0) & bit:
                raise AssertionError(("ineligible assignment", owner, x, y, half))
            key = (x, y, half)
            used[key] += 1
            edge = soft.norm_edge(x, y)
            if edge in state.active_edges:
                active_load[edge] += 1
            records.append([owner, x, y, half])
    if len(records) != flow["maximumFlow"]:
        raise AssertionError((len(records), flow["maximumFlow"]))
    if any(value != 1 for value in used.values()):
        raise AssertionError("literal key capacity exceeded")
    if any(value > 2 for value in active_load.values()):
        raise AssertionError("active edge aggregate capacity exceeded")
    return records


def state_metric(ctx, rows):
    state, owners, demand, relation, family_sizes, flow, assigned = build_full_model(ctx, rows)
    total_demand = sum(demand)
    if total_demand % 2:
        raise AssertionError(("odd CollisionHalf demand", total_demand))
    assignments = validate_assignment(
        ctx, state, owners, demand, relation, flow, assigned
    )
    return {
        "collisionUnits": total_demand // 2,
        "groupedDefect": flow["defect"],
        "globalCollisionHalfDemand": total_demand,
        "maximumFlow": flow["maximumFlow"],
        "activeEdges": [list(edge) for edge in sorted(state.active_edges)],
        "familySizes": family_sizes,
        "unionOrderedBases": len(relation),
        "assignments": assignments,
    }


def metric_worker(task):
    fixture, choice = task
    choice = tuple(choice)
    if fixture != "r35":
        raise ValueError(fixture)
    return choice, state_metric(R35_CTX, r35_rows(choice))


def same_slot_change(old_row, new_row):
    if old_row[0] != new_row[0] or old_row[-1] != new_row[-1]:
        return None
    different = [index for index, pair in enumerate(zip(old_row, new_row)) if pair[0] != pair[1]]
    if len(different) != 1 or different[0] not in range(1, len(old_row) - 1):
        return None
    slot = different[0]
    return slot, old_row[slot], new_row[slot]


def pair_count(rows, x: int, y: int) -> int:
    return sum(x in row and y in row for row in rows)


def lower_bound_circulation(node_count: int, edge_specs):
    """Exact feasible-circulation solver with integral lower bounds."""
    network = soft.Dinic()
    for _ in range(node_count + 2):
        network.node()
    super_source = node_count
    super_sink = node_count + 1
    balance = [0] * node_count
    records = []
    for source, target, lower, upper, label in edge_specs:
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
    value = network.max_flow(super_source, super_sink)
    if value != required:
        return False, None
    flows = [(label, lower + (arc.initial - arc.cap)) for arc, lower, label in records]
    return True, flows


def forced_keys_optimal(ctx, rows, u: int, w: int, optimum: int):
    """Require both literal keys (u,w,0/1) in a flow of fixed value optimum."""
    state, owners, demand, relation, _family_sizes, flow, _assigned = build_full_model(ctx, rows)
    if flow["maximumFlow"] != optimum:
        raise AssertionError((flow["maximumFlow"], optimum))
    base = ctx.n * u + w
    mask = relation.get(base, 0)
    if u == w or state.pair[u][w] != 0 or mask == 0 or optimum < 2:
        return {"feasible": False, "forcedOwners": [], "reason": "not-two-eligible-free-keys"}

    # Pool network equivalent to solve_grouped_flow, except ordered bases are
    # kept separate so a lower bound of two means the two literal keys of this
    # precise orientation are both used.
    source = 0
    sink = 1
    next_node = 2
    owner_nodes = {}
    for owner in owners:
        owner_nodes[owner] = next_node
        next_node += 1
    active_group = {}
    for edge in sorted(state.active_edges):
        active_group[edge] = next_node
        next_node += 1
    pool_nodes = {}
    for ordered_base in sorted(relation):
        pool_nodes[ordered_base] = next_node
        next_node += 1

    infinity = max(1, sum(demand))
    specs = []
    for owner, amount in zip(owners, demand):
        specs.append((source, owner_nodes[owner], 0, amount, ("source-owner", owner)))
    for ordered_base, owner_mask in sorted(relation.items()):
        x, y = divmod(ordered_base, ctx.n)
        pool = pool_nodes[ordered_base]
        bits = owner_mask
        while bits:
            bit = bits & -bits
            owner_index = bit.bit_length() - 1
            owner = owners[owner_index]
            specs.append((owner_nodes[owner], pool, 0, infinity, ("owner-pool", owner, ordered_base)))
            bits ^= bit
        active = soft.norm_edge(x, y)
        target = active_group[active] if active in active_group else sink
        lower = 2 if ordered_base == base else 0
        specs.append((pool, target, lower, 2, ("pool-out", ordered_base)))
    for edge, group in sorted(active_group.items()):
        specs.append((group, sink, 0, 2, ("active-cap", edge[0], edge[1])))
    # Fix the total s-t flow to the previously computed grouped optimum.
    specs.append((sink, source, optimum, optimum, ("fixed-optimum", optimum)))
    feasible, flows = lower_bound_circulation(next_node, specs)
    if not feasible:
        return {"feasible": False, "forcedOwners": [], "reason": "lower-bound-circulation-infeasible"}
    forced_owners = []
    for label, amount in flows:
        if label[0] == "owner-pool" and label[2] == base:
            forced_owners.extend([label[1]] * amount)
    if len(forced_owners) != 2:
        raise AssertionError((u, w, forced_owners))
    return {
        "feasible": True,
        "forcedOwners": sorted(forced_owners),
        "reason": "exact-lower-bound-circulation",
    }


def forced_worker(task):
    fixture, choice, pairs, optimum = task
    choice = tuple(choice)
    if fixture != "r35":
        raise ValueError(fixture)
    rows = r35_rows(choice)
    return choice, {
        f"{u},{w}": forced_keys_optimal(R35_CTX, rows, u, w, optimum)
        for u, w in pairs
    }


def strongly_connected_components(nodes, adjacency):
    """Deterministic Kosaraju decomposition."""
    nodes = tuple(sorted(nodes))
    allowed = set(nodes)
    seen = set()
    order = []
    for root in nodes:
        if root in seen:
            continue
        stack = [(root, 0)]
        seen.add(root)
        while stack:
            vertex, cursor = stack[-1]
            neighbors = sorted(x for x in adjacency.get(vertex, ()) if x in allowed)
            if cursor < len(neighbors):
                nxt = neighbors[cursor]
                stack[-1] = (vertex, cursor + 1)
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append((nxt, 0))
            else:
                stack.pop()
                order.append(vertex)
    reverse = defaultdict(set)
    for source in nodes:
        for target in adjacency.get(source, ()):
            if target in allowed:
                reverse[target].add(source)
    components = []
    assigned = set()
    for root in reversed(order):
        if root in assigned:
            continue
        component = []
        queue = [root]
        assigned.add(root)
        for vertex in queue:
            component.append(vertex)
            for nxt in sorted(reverse.get(vertex, ())):
                if nxt not in assigned:
                    assigned.add(nxt)
                    queue.append(nxt)
        components.append(tuple(sorted(component)))
    return tuple(sorted(components, key=lambda item: item[0]))


def classify_scope(name, indices, metrics, transitions):
    indices = tuple(sorted(indices))
    allowed = set(indices)
    adjacency = defaultdict(set)
    for transition in transitions:
        if transition[0] in allowed and transition[1] in allowed and transition[7]:
            adjacency[transition[0]].add(transition[1])
    components = strongly_connected_components(indices, adjacency)
    c_min = min(metrics[index]["collisionUnits"] for index in indices)
    c_min_indices = [index for index in indices if metrics[index]["collisionUnits"] == c_min]
    c_min_has_d0 = any(metrics[index]["groupedDefect"] == 0 for index in c_min_indices)
    scope_has_d0 = any(metrics[index]["groupedDefect"] == 0 for index in indices)
    defect_histogram = Counter(
        metrics[index]["groupedDefect"] for index in indices
    )
    component_records = []
    flags = []
    for component in components:
        members = set(component)
        sink = not any(
            target in allowed and target not in members
            for source in component
            for target in adjacency.get(source, ())
        )
        cycle = len(component) > 1 or any(source in adjacency.get(source, ()) for source in component)
        values = sorted({
            (metrics[index]["collisionUnits"], metrics[index]["groupedDefect"])
            for index in component
        })
        record = {
            "members": list(component),
            "size": len(component),
            "sinkInTestedSaturatedGraph": sink,
            "hasDirectedCycle": cycle,
            "values": [list(value) for value in values],
        }
        component_records.append(record)
        condition = (
            sink
            and cycle
            and values == [(c_min, 1)]
            and not c_min_has_d0
        )
        if condition:
            flags.append(record)
    return {
        "name": name,
        "stateCount": len(indices),
        "collisionMinimum": c_min,
        "collisionMinimumStateCount": len(c_min_indices),
        "collisionMinimumFaceHasD0": c_min_has_d0,
        "scopeHasD0": scope_has_d0,
        "defectHistogram": {
            str(key): value for key, value in sorted(defect_histogram.items())
        },
        "defectOneStateCount": defect_histogram[1],
        "saturatedSccCount": len(components),
        "candidateRotorFlags": flags,
        "components": component_records,
    }


def build_transitions(fixture, choices, families, metrics, ctx, workers):
    index_by_choice = {choice: index for index, choice in enumerate(choices)}
    radices = tuple(len(family) for family in families)
    neutral = []
    raw_directed = 0
    neutral_directed = 0
    free_directed = 0
    forced_requests = defaultdict(set)
    for source_index, choice in enumerate(choices):
        for atom, radix in enumerate(radices):
            for replacement in range(radix):
                if replacement == choice[atom]:
                    continue
                target_choice = choice[:atom] + (replacement,) + choice[atom + 1 :]
                target_index = index_by_choice.get(target_choice)
                if target_index is None:
                    continue
                change = same_slot_change(families[atom][choice[atom]], families[atom][replacement])
                if change is None:
                    continue
                raw_directed += 1
                if (
                    metrics[source_index]["collisionUnits"] != metrics[target_index]["collisionUnits"]
                    or metrics[source_index]["groupedDefect"] != metrics[target_index]["groupedDefect"]
                ):
                    continue
                neutral_directed += 1
                slot, u, w = change
                rows = (
                    r35_rows(choice)
                    if fixture == "r35"
                    else tuple(families[i][value] for i, value in enumerate(choice))
                )
                free = u != w and pair_count(rows, u, w) == 0
                if free:
                    free_directed += 1
                    forced_requests[choice].add((u, w))
                neutral.append([source_index, target_index, atom, slot, u, w, free, False, []])

    forced_results = {}
    tasks = []
    for choice, pairs in sorted(forced_requests.items()):
        source_index = index_by_choice[choice]
        tasks.append((fixture, choice, tuple(sorted(pairs)), metrics[source_index]["maximumFlow"]))
    if fixture == "r35" and tasks:
        if workers == 1:
            outputs = map(forced_worker, tasks)
        else:
            executor = ProcessPoolExecutor(max_workers=workers)
            outputs = executor.map(forced_worker, tasks, chunksize=4)
        try:
            for choice, result in outputs:
                forced_results[choice] = result
        finally:
            if workers != 1:
                executor.shutdown()
    elif fixture == "rotor":
        for _fixture, choice, pairs, optimum in tasks:
            rows = tuple(families[i][value] for i, value in enumerate(choice))
            forced_results[choice] = {
                f"{u},{w}": forced_keys_optimal(ctx, rows, u, w, optimum)
                for u, w in pairs
            }

    saturated = 0
    for transition in neutral:
        source_index, _target, _atom, _slot, u, w, free, _sat, _owners = transition
        if not free:
            continue
        choice = choices[source_index]
        witness = forced_results[choice][f"{u},{w}"]
        transition[7] = witness["feasible"]
        transition[8] = witness["forcedOwners"]
        saturated += int(witness["feasible"])
    return {
        "rawSameSlotDirected": raw_directed,
        "neutralPreservingCDDirected": neutral_directed,
        "neutralFreeDirected": free_directed,
        "saturatedDirected": saturated,
        "records": neutral,
    }


def state_record(choice, metric, label=None):
    record = {"choice": list(choice), **metric}
    if label is not None:
        record["label"] = label
    return record


def build_payload(workers: int):
    rotor_ctx, rotor_families, rotor_choices, rotor_labels = rotor_fixture()
    rotor_metrics = [
        state_metric(
            rotor_ctx,
            tuple(rotor_families[index][value] for index, value in enumerate(choice)),
        )
        for choice in rotor_choices
    ]
    rotor_transitions = build_transitions(
        "rotor", rotor_choices, rotor_families, rotor_metrics, rotor_ctx, workers
    )
    rotor_scope = classify_scope(
        "complete-four-state-rotor",
        range(len(rotor_choices)),
        rotor_metrics,
        rotor_transitions["records"],
    )

    displayed = tuple(R35.DISPLAYED)
    one_row_minimum = displayed[:9] + (0,) + displayed[10:]
    displayed_scope_choices = set(neighborhood(displayed))
    minimum_scope_choices = set(neighborhood(one_row_minimum))
    union_choices = tuple(sorted(displayed_scope_choices | minimum_scope_choices))
    tasks = [("r35", choice) for choice in union_choices]
    if workers == 1:
        outputs = map(metric_worker, tasks)
    else:
        executor = ProcessPoolExecutor(max_workers=workers)
        outputs = executor.map(metric_worker, tasks, chunksize=8)
    metric_by_choice = {}
    try:
        for choice, metric in outputs:
            metric_by_choice[choice] = metric
    finally:
        if workers != 1:
            executor.shutdown()
    r35_metrics = [metric_by_choice[choice] for choice in union_choices]
    r35_families = tuple(tuple(tuple(row) for row in family) for family in R35.ROW_FAMILIES)
    r35_transitions = build_transitions(
        "r35", union_choices, r35_families, r35_metrics, R35_CTX, workers
    )
    union_index = {choice: index for index, choice in enumerate(union_choices)}
    displayed_indices = sorted(union_index[choice] for choice in displayed_scope_choices)
    minimum_indices = sorted(union_index[choice] for choice in minimum_scope_choices)
    scopes = [
        classify_scope(
            "displayed-center-hamming-le-two",
            displayed_indices,
            r35_metrics,
            r35_transitions["records"],
        ),
        classify_scope(
            "one-row-minimum-center-hamming-le-two",
            minimum_indices,
            r35_metrics,
            r35_transitions["records"],
        ),
        classify_scope(
            "union-of-both-hamming-le-two-neighborhoods",
            range(len(union_choices)),
            r35_metrics,
            r35_transitions["records"],
        ),
    ]
    for scope, indices in zip(scopes[:2], (displayed_indices, minimum_indices)):
        scope["stateIndices"] = indices

    payload = {
        "schema": "R56_GLOBAL_SOFTCAP_SATURATED_ROTOR_NECESSARY_SUPERSET_V1",
        "status": "FINITE_NECESSARY_CONDITION_SUPERSET_GATE_NOT_A_UNIVERSAL_THEOREM",
        "arithmetic": "Python integers; exact integral max flow and lower-bound circulation",
        "model": {
            "source": "global R53 soft-cap model",
            "families": list(soft.FAMILY_ORDER),
            "collisionUnits": "globalCollisionHalfDemand / 2",
            "groupedDefect": "full six-family demand minus exact grouped maximum flow",
            "defectParityAudit": (
                "all tested defects are even: each owner demand, direct ordered-base "
                "pool, and active-edge group has even capacity in this executable model"
            ),
            "forcedKeyTest": (
                "lower-bound circulation fixes total flow at the exact optimum and imposes "
                "lower bound 2 on the ordered-base pool (u,w), forcing literal keys 0 and 1"
            ),
            "sinkMeaning": "sink only in the saturated transition graph induced by the finite tested scope",
            "flagCondition": (
                "C is scope minimum; D=1; sink SCC has a directed saturated cycle; "
                "the C-minimum face contains no D=0 state"
            ),
        },
        "inputs": {
            "globalSoftcap": {"path": str(SOFTCAP_DIR / "global_softcap.py"), "sha256": sha256(SOFTCAP_DIR / "global_softcap.py")},
            "rotor": {"path": str(ROTOR_PATH), "sha256": sha256(ROTOR_PATH)},
            "r35": {"path": str(R35_PATH), "sha256": sha256(R35_PATH)},
        },
        "workers": workers,
        "fixtures": {
            "rotor8": {
                "order": 8,
                "stateCount": len(rotor_choices),
                "states": [state_record(choice, metric, rotor_labels[choice]) for choice, metric in zip(rotor_choices, rotor_metrics)],
                "transitions": rotor_transitions,
                "scopes": [rotor_scope],
            },
            "r35n24": {
                "order": 24,
                "rowFamilySizes": list(R35_RADICES),
                "displayedCenter": list(displayed),
                "oneRowMinimumCenter": list(one_row_minimum),
                "displayedNeighborhoodCount": len(displayed_scope_choices),
                "oneRowMinimumNeighborhoodCount": len(minimum_scope_choices),
                "intersectionCount": len(displayed_scope_choices & minimum_scope_choices),
                "unionStateCount": len(union_choices),
                "states": [state_record(choice, metric) for choice, metric in zip(union_choices, r35_metrics)],
                "transitions": r35_transitions,
                "scopes": scopes,
            },
        },
    }
    flags = []
    for fixture_name, fixture in payload["fixtures"].items():
        for scope in fixture["scopes"]:
            for flag in scope["candidateRotorFlags"]:
                flags.append({"fixture": fixture_name, "scope": scope["name"], **flag})
    payload["exactCounts"] = {
        "totalUniqueStates": len(rotor_choices) + len(union_choices),
        "totalAssignments": sum(
            len(state["assignments"])
            for fixture in payload["fixtures"].values()
            for state in fixture["states"]
        ),
        "totalNeutralTransitions": sum(
            fixture["transitions"]["neutralPreservingCDDirected"]
            for fixture in payload["fixtures"].values()
        ),
        "totalSaturatedTransitions": sum(
            fixture["transitions"]["saturatedDirected"]
            for fixture in payload["fixtures"].values()
        ),
        "candidateRotorFlags": len(flags),
        "defectOneStates": sum(
            state["groupedDefect"] == 1
            for fixture in payload["fixtures"].values()
            for state in fixture["states"]
        ),
    }
    payload["candidateRotorFlags"] = flags
    payload["verdict"] = (
        "CANDIDATE_NECESSARY_PATTERN_FOUND" if flags else "NO_CANDIDATE_IN_TESTED_FINITE_SCOPES"
    )
    return payload


def report_text(payload, results_sha: str, gate_sha: str, verify_sha: str) -> str:
    rotor = payload["fixtures"]["rotor8"]
    r35 = payload["fixtures"]["r35n24"]
    lines = [
        "# R56 global-softcap saturated rotor necessary-condition gate",
        "",
        "## Scope and verdict",
        "",
        "This is a finite **necessary-condition superset gate**, not a universal theorem.",
        "Sinkhood is computed only inside each finite tested saturated-transition graph;",
        "therefore boundary truncation can create false-positive sinks but cannot justify a",
        "general rotor-exclusion claim.",
        "",
        f"Exact verdict: `{payload['verdict']}`.",
        "",
        "## Exact model",
        "",
        "- `C` is one half of global CollisionHalf demand.",
        "- `D` is the defect after explicitly unioning all six R53 families.",
        "- Every state carries one explicit exact integral maximum-flow assignment.",
        "- A forced-key test fixes total flow at the true optimum and gives lower bound 2",
        "  to the exact ordered `(u,w)` pool, so both literal keys `(u,w,0/1)` are used.",
        "- Neutral transitions change one row at one internal slot and preserve `(C,D)`.",
        "- Saturated transitions additionally have `pairCount(u,w)=0` and pass that forced-key test.",
        "",
        "The exact D=1 population is zero. In this executable R53 relation every",
        "owner demand is even, every ordered-base pool contributes two literal halves,",
        "and every active-edge group has capacity two, so all tested grouped defects",
        "are even. Thus the requested D=1 filter is vacuous on these scopes; this gate",
        "does not by itself exclude an R55 unit-core whose local deficiency is one.",
        "",
        "## Exact counts",
        "",
        f"- Rotor states: {rotor['stateCount']}",
        f"- R35 displayed Hamming<=2 states: {r35['displayedNeighborhoodCount']}",
        f"- R35 one-row-minimum Hamming<=2 states: {r35['oneRowMinimumNeighborhoodCount']}",
        f"- R35 neighborhood intersection: {r35['intersectionCount']}",
        f"- R35 unique union states: {r35['unionStateCount']}",
        f"- Total explicit assigned flow units: {payload['exactCounts']['totalAssignments']}",
        f"- Total neutral directed transitions: {payload['exactCounts']['totalNeutralTransitions']}",
        f"- Total saturated directed transitions: {payload['exactCounts']['totalSaturatedTransitions']}",
        f"- Candidate rotor flags: {payload['exactCounts']['candidateRotorFlags']}",
        f"- Unique states with D=1: {payload['exactCounts']['defectOneStates']}",
        "",
        "### Per-fixture transition counts",
        "",
        "| Fixture | Raw same-slot | Neutral `(C,D)` | Free | Saturated |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, fixture in payload["fixtures"].items():
        transitions = fixture["transitions"]
        lines.append(
            f"| {name} | {transitions['rawSameSlotDirected']} | "
            f"{transitions['neutralPreservingCDDirected']} | "
            f"{transitions['neutralFreeDirected']} | {transitions['saturatedDirected']} |"
        )
    lines.extend([
        "",
        "### Scope classification",
        "",
        "| Fixture / scope | States | C min | C-min states | C-min has D=0 | Flags |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for name, fixture in payload["fixtures"].items():
        for scope in fixture["scopes"]:
            lines.append(
                f"| {name} / {scope['name']} | {scope['stateCount']} | "
                f"{scope['collisionMinimum']} | {scope['collisionMinimumStateCount']} | "
                f"{str(scope['collisionMinimumFaceHasD0']).lower()} | "
                f"{len(scope['candidateRotorFlags'])} |"
            )
    lines.extend([
        "",
        "## Replay",
        "",
        "From `E:\\Projects\\ErdosProblems`:",
        "",
        "```powershell",
        "python tmp/fanout/r56_soft_rotor_gate/gate.py --workers 32 --output tmp/fanout/r56_soft_rotor_gate/results.json",
        "python tmp/fanout/r56_soft_rotor_gate/verify.py --workers 32 --input tmp/fanout/r56_soft_rotor_gate/results.json",
        "```",
        "",
        "## SHA-256",
        "",
        "```text",
        f"gate.py       {gate_sha}",
        f"verify.py     {verify_sha}",
        f"results.json  {results_sha}",
        f"global_softcap.py {payload['inputs']['globalSoftcap']['sha256']}",
        f"rotor input   {payload['inputs']['rotor']['sha256']}",
        f"R35 input     {payload['inputs']['r35']['sha256']}",
        "```",
        "",
    ])
    return "\n".join(lines)


def write_support_files(payload, output: Path) -> None:
    output.write_bytes(canonical_bytes(payload))
    results_sha = sha256(output)
    gate_sha = sha256(HERE / "gate.py")
    verify_sha = sha256(HERE / "verify.py")
    replay = (
        "# Replay\n\n"
        "From `E:\\Projects\\ErdosProblems`:\n\n"
        "```powershell\n"
        "python tmp/fanout/r56_soft_rotor_gate/gate.py --workers 32 --output tmp/fanout/r56_soft_rotor_gate/results.json\n"
        "python tmp/fanout/r56_soft_rotor_gate/verify.py --workers 32 --input tmp/fanout/r56_soft_rotor_gate/results.json\n"
        "```\n"
    )
    (HERE / "REPLAY.md").write_text(replay, encoding="ascii", newline="\n")
    report = report_text(payload, results_sha, gate_sha, verify_sha)
    (HERE / "REPORT.md").write_text(report, encoding="ascii", newline="\n")
    manifest_files = ["gate.py", "verify.py", output.name, "REPORT.md", "REPLAY.md"]
    manifest = "".join(f"{sha256(HERE / name)}  {name}\n" for name in manifest_files)
    (HERE / "MANIFEST.sha256").write_text(manifest, encoding="ascii", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=min(32, os.cpu_count() or 1))
    parser.add_argument("--output", type=Path, default=HERE / "results.json")
    args = parser.parse_args()
    if not 1 <= args.workers <= 32:
        parser.error("workers must be in 1..32")
    output = args.output.resolve()
    if output.parent != HERE.resolve():
        parser.error("output must stay inside tmp/fanout/r56_soft_rotor_gate")
    payload = build_payload(args.workers)
    write_support_files(payload, output)
    print(json.dumps({
        "verdict": payload["verdict"],
        "exactCounts": payload["exactCounts"],
        "resultsSha256": sha256(output),
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
