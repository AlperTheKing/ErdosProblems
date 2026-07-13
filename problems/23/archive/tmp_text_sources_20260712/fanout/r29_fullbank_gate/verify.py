"""Exact R29 all-anchor transfer/FullBank audit.

This gate separates two questions that must not be conflated:

1. the operational four-pattern transfer relation used by the R19--R23 exact
   Python gates; and
2. the compiled Lean FullBank interfaces, whose generic capacity fields still
   need a real graph-derived provider.

All arithmetic is integral or ``fractions.Fraction``.  No floating-point
calculation is used.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from collections import Counter, deque
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAD = ROOT / "tmp" / "fanout" / "r29_gate" / "lead" / "r29_lead_gate.py"
BEST_TUPLE = ROOT / "tmp" / "fanout" / "r29_gate" / "d09" / "retry2" / "best_tuple.json"
SCOPED_HALL_CERT = ROOT / "tmp" / "fanout" / "r29_gate" / "d05" / "retry2" / "cut_certificate.json"
MAXCUT_CLASSES = ROOT / "tmp" / "fanout" / "r29_gate" / "d03" / "retry2" / "graph_classes.json"
MAXCUT_CERT = ROOT / "tmp" / "fanout" / "r29_gate" / "d03" / "retry2" / "certificate.json"
OWNERS = (0, 1, 2)


def edge(u: int, v: int) -> tuple[int, int]:
    assert u != v
    return (u, v) if u < v else (v, u)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_constructor():
    spec = importlib.util.spec_from_file_location("r29_constructor", LEAD)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bfs_dist_count(n: int, edges: set[tuple[int, int]], source: int):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    dist = [-1] * n
    count = [0] * n
    dist[source] = 0
    count[source] = 1
    todo = deque([source])
    while todo:
        u = todo.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                count[v] = count[u]
                todo.append(v)
            elif dist[v] == dist[u] + 1:
                count[v] += count[u]
    return dist, count


def connected(n: int, edges: set[tuple[int, int]]) -> bool:
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = {0}
    todo = deque([0])
    while todo:
        u = todo.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return len(seen) == n


def triangle_free(n: int, graph: set[tuple[int, int]]) -> bool:
    adj = [set() for _ in range(n)]
    for u, v in graph:
        adj[u].add(v)
        adj[v].add(u)
    return all(not (adj[u] & adj[v]) for u, v in graph)


class DSU:
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}

    def find(self, v):
        while self.parent[v] != v:
            self.parent[v] = self.parent[self.parent[v]]
            v = self.parent[v]
        return v

    def union(self, u, v):
        u, v = self.find(u), self.find(v)
        if u != v:
            self.parent[max(u, v)] = min(u, v)


def all_anchor_rows(data: dict) -> tuple[tuple[int, ...], ...]:
    rows = list(data["rows"])
    for j, meta in enumerate(data["selectorMeta"]):
        rows[data["selectorStart"] + j] = tuple(meta["anchorRow"])
    return tuple(rows)


def rebuild_scope(data: dict, rows: tuple[tuple[int, ...], ...]) -> dict:
    n = data["n"]
    pair = Counter()
    row_count = Counter()
    selected = set()
    support = set()
    for row in rows:
        assert len(row) == len(set(row))
        selected.update(row)
        for x in row:
            row_count[x] += 1
            for y in row:
                pair[x, y] += 1
        support.update(edge(u, v) for u, v in zip(row, row[1:]))

    active_edges = {
        e for e in data["blue"]
        if e not in support and e[0] in selected and e[1] in selected
    }
    dsu = DSU(selected)
    for u, v in active_edges:
        dsu.union(u, v)
    active_roots = {
        dsu.find(u) for u, v in data["bad"]
        if u in selected and v in selected and dsu.find(u) == dsu.find(v)
    }
    active_vertices = {v for v in selected if dsu.find(v) in active_roots}
    component_root = {v: dsu.find(v) for v in selected}
    demanded_active = {e for e in active_edges if e[0] in active_vertices}
    active_degree = Counter()
    for u, v in demanded_active:
        active_degree[u] += 1
        active_degree[v] += 1
    collision = {
        v: 2 * sum(max(0, pair[v, y] - 1) for y in range(n))
        for v in active_vertices
    }
    hit_need = {
        v: max(0, active_degree[v] - max(0, n - 5 * row_count[v]))
        for v in active_vertices
    }
    return {
        "pair": pair,
        "row_count": row_count,
        "selected": selected,
        "support": support,
        "active_edges": active_edges,
        "active_vertices": active_vertices,
        "component_root": component_root,
        "demanded_active": demanded_active,
        "collision": collision,
        "hit_need": hit_need,
    }


def outside_components(data: dict, selected: set[int]):
    n = data["n"]
    adj = [set() for _ in range(n)]
    for u, v in data["blue"]:
        adj[u].add(v)
        adj[v].add(u)
    component_id = [-1] * n
    components: list[set[int]] = []
    attachments: list[set[int]] = []
    for root in range(n):
        if root in selected or component_id[root] >= 0:
            continue
        cid = len(components)
        component_id[root] = cid
        vertices = set()
        attachment = set()
        todo = deque([root])
        while todo:
            x = todo.popleft()
            vertices.add(x)
            for y in adj[x]:
                if y in selected:
                    attachment.add(y)
                elif component_id[y] < 0:
                    component_id[y] = cid
                    todo.append(y)
        components.append(vertices)
        attachments.append(attachment)
    return component_id, components, attachments


def weighted_singleton_requirement(data: dict, state: dict) -> dict:
    """Exact FullBank half-singleton load on the hub active component.

    This is a demand-side LP quantity only.  It does not construct any Door,
    vertexSlack, c5Base, or prune capacity.
    """
    root = state["component_root"][OWNERS[0]]
    core = {
        v for v in state["active_vertices"]
        if state["component_root"][v] == root
    }
    assert set(OWNERS) <= core and len(core) == 19
    # In the singleton LP, F is the selected support internal to the chosen
    # component.  Thus O = B \ F still contains selected support edges that
    # leave the component.
    internal_support = {
        e for e in state["support"] if e[0] in core and e[1] in core
    }
    off_support = data["blue"] - internal_support
    internal = {
        e for e in off_support if e[0] in core and e[1] in core
    }
    boundary = {
        e for e in off_support if (e[0] in core) ^ (e[1] in core)
    }
    total = Fraction(len(internal), 1) + Fraction(len(boundary), 2)
    assert len(internal) == 18
    assert len(boundary) == 1441
    assert total == Fraction(1477, 2)
    return {
        "hubComponentVertices": len(core),
        "internalSelectedSupportEdges": len(internal_support),
        "internalOffSupportBlueEdges": len(internal),
        "boundaryOffSupportBlueEdges": len(boundary),
        "requiredLoad": {
            "numerator": total.numerator,
            "denominator": total.denominator,
        },
        "status": "GRAPH_DERIVED_REQUIREMENT_ONLY",
        "warning": "NOT_AVAILABLE_CAPACITY_AND_NOT_COMPARABLE_TO_INTEGRAL_DEFECT_28_WITHOUT_THE_MISSING_ADAPTER",
    }


def staged_sources(data: dict, state: dict):
    n = data["n"]
    pair = state["pair"]
    active_edges = state["active_edges"]
    active_vertices = state["active_vertices"]

    signed_degree = Counter()
    sign = {}
    bad_neighbors = {v: set() for v in range(n)}
    blue_neighbors = {v: set() for v in range(n)}
    for e in data["blue"]:
        sign[e] = 1
        signed_degree[e[0]] += 1
        signed_degree[e[1]] += 1
        blue_neighbors[e[0]].add(e[1])
        blue_neighbors[e[1]].add(e[0])
    for e in data["bad"]:
        sign[e] = -1
        signed_degree[e[0]] -= 1
        signed_degree[e[1]] -= 1
        bad_neighbors[e[0]].add(e[1])
        bad_neighbors[e[1]].add(e[0])

    def pair_loss(x: int, y: int) -> int:
        return signed_degree[x] + signed_degree[y] - 2 * sign.get(edge(x, y), 0)

    stages: dict[str, dict[tuple[int, int, int], int]] = {
        "sameFirst": {},
        "commonBad": {},
        "rowCompanion": {},
        "commonBlueC5Terminal": {},
        "outsideAttachmentScoped": {},
        "outsideAttachmentLegacyUnscoped": {},
    }

    def add(stage: str, key: tuple[int, int, int], owner: int):
        stages[stage][key] = stages[stage].get(key, 0) | (1 << owner)

    # The first three classes exactly follow the operational R20/R23 gates.
    for owner in OWNERS:
        for y in range(n):
            if y == owner or pair[owner, y] != 0:
                continue
            for half in (0, 1):
                reserved = (
                    half == 0
                    and edge(owner, y) in active_edges
                    and owner in active_vertices
                )
                if not reserved:
                    add("sameFirst", (owner, y, half), owner)

        for x in bad_neighbors[owner]:
            for y in bad_neighbors[owner]:
                if x == y or pair[x, y] != 0 or pair_loss(x, y) < 0:
                    continue
                for half in (0, 1):
                    reserved = (
                        half == 0
                        and edge(x, y) in active_edges
                        and x in active_vertices
                    )
                    if not reserved:
                        add("commonBad", (x, y, half), owner)

        companions = [
            x for x in range(n) if x != owner and pair[owner, x] > 0
        ]
        for x in companions:
            for y in companions:
                if x == y or pair[x, y] != 0 or pair_loss(x, y) < 0:
                    continue
                for half in (0, 1):
                    reserved = (
                        half == 0
                        and edge(x, y) in active_edges
                        and x in active_vertices
                    )
                    if not reserved:
                        add("rowCompanion", (x, y, half), owner)

        # Literal compiled CheckedC5BaseTransfer.Valid predicate: both source
        # vertices are blue neighbours of the owner, and reserving those two
        # owner edges leaves nonnegative adjusted switch surplus.
        for x in blue_neighbors[owner]:
            for y in blue_neighbors[owner]:
                if x == y or pair[x, y] != 0 or pair_loss(x, y) < 2:
                    continue
                for half in (0, 1):
                    reserved = (
                        half == 0
                        and edge(x, y) in active_edges
                        and x in active_vertices
                    )
                    if not reserved:
                        add("commonBlueC5Terminal", (x, y, half), owner)

    component_id, components, attachments = outside_components(
        data, state["selected"]
    )
    eligible_by_owner = {}
    eligible_component_by_owner = {}
    eligible_unscoped_by_owner = {}
    eligible_unscoped_component_by_owner = {}
    for owner in OWNERS:
        eligible_unscoped_components = [
            cid for cid, att in enumerate(attachments)
            if any(pair[owner, a] > 0 for a in att)
        ]
        eligible_components = [
            cid for cid, att in enumerate(attachments)
            if any(
                pair[owner, a] > 0
                and state["component_root"][a] == state["component_root"][owner]
                for a in att
            )
        ]
        eligible = set().union(
            *(components[cid] for cid in eligible_components)
        ) if eligible_components else set()
        eligible_unscoped = set().union(
            *(components[cid] for cid in eligible_unscoped_components)
        ) if eligible_unscoped_components else set()
        eligible_by_owner[owner] = eligible
        eligible_component_by_owner[owner] = eligible_components
        eligible_unscoped_by_owner[owner] = eligible_unscoped
        eligible_unscoped_component_by_owner[owner] = eligible_unscoped_components

        def add_outside(stage: str, outside: set[int]):
            loss_cache = {}
            for x in sorted(outside):
                for y in sorted(outside):
                    if x == y:
                        continue
                    cid_pair = (component_id[x], component_id[y])
                    if cid_pair not in loss_cache:
                        left = components[cid_pair[0]]
                        right = components[cid_pair[1]]
                        if len(left) == len(right) == 1:
                            # Exact singleton-union boundary identity.
                            loss_cache[cid_pair] = pair_loss(x, y)
                        else:
                            union = left | right
                            # Exact fallback for non-singleton outside components.
                            loss_cache[cid_pair] = (
                                sum((u in union) != (v in union) for u, v in data["blue"])
                                - sum((u in union) != (v in union) for u, v in data["bad"])
                            )
                    assert loss_cache[cid_pair] >= 0
                    # Outside vertices occur in no selected row, so the ordered
                    # pair is Free and neither half is reserved.
                    assert pair[x, y] == 0
                    add(stage, (x, y, 0), owner)
                    add(stage, (x, y, 1), owner)

        add_outside("outsideAttachmentScoped", eligible)
        add_outside("outsideAttachmentLegacyUnscoped", eligible_unscoped)

    return {
        "stages": stages,
        "signed_degree": signed_degree,
        "pair_loss": pair_loss,
        "component_id": component_id,
        "components": components,
        "attachments": attachments,
        "eligible_by_owner": eligible_by_owner,
        "eligible_component_by_owner": eligible_component_by_owner,
        "eligible_unscoped_by_owner": eligible_unscoped_by_owner,
        "eligible_unscoped_component_by_owner": eligible_unscoped_component_by_owner,
    }


def aggregate_masks(stage_maps):
    masks = {}
    for stage_map in stage_maps:
        for key, owner_mask in stage_map.items():
            masks[key] = masks.get(key, 0) | owner_mask
    return masks


def hall_cuts(demand_by_owner: dict[int, int], masks):
    hist = Counter(masks.values())
    cuts = []
    for shore_mask in range(8):
        demand = sum(
            demand_by_owner[o] for o in OWNERS if shore_mask & (1 << o)
        )
        reach = sum(
            count for owner_mask, count in hist.items()
            if owner_mask & shore_mask
        )
        cuts.append({
            "shoreMask": shore_mask,
            "shore": [o for o in OWNERS if shore_mask & (1 << o)],
            "demand": demand,
            "reach": reach,
            "defect": demand - reach,
        })
    return hist, cuts


def max_flow_by_masks(demand_by_owner: dict[int, int], hist: Counter) -> int:
    # Tiny integral Dinic network: source -> 3 owners -> owner masks -> sink.
    source, sink = 0, 1
    owner_base = 2
    masks = sorted(k for k in hist if k)
    mask_base = owner_base + len(OWNERS)
    graph = [[] for _ in range(mask_base + len(masks))]

    def add(u, v, cap):
        graph[u].append([v, cap, len(graph[v])])
        graph[v].append([u, 0, len(graph[u]) - 1])

    total = sum(demand_by_owner.values())
    for i, owner in enumerate(OWNERS):
        add(source, owner_base + i, demand_by_owner[owner])
    for j, mask in enumerate(masks):
        node = mask_base + j
        for i, owner in enumerate(OWNERS):
            if mask & (1 << owner):
                add(owner_base + i, node, total + 1)
        add(node, sink, hist[mask])

    flow = 0
    while True:
        level = [-1] * len(graph)
        level[source] = 0
        todo = deque([source])
        while todo:
            u = todo.popleft()
            for v, cap, _ in graph[u]:
                if cap > 0 and level[v] < 0:
                    level[v] = level[u] + 1
                    todo.append(v)
        if level[sink] < 0:
            return flow
        cursor = [0] * len(graph)

        def send(u, amount):
            if u == sink:
                return amount
            while cursor[u] < len(graph[u]):
                item = graph[u][cursor[u]]
                v, cap, rev = item
                if cap > 0 and level[v] == level[u] + 1:
                    pushed = send(v, min(amount, cap))
                    if pushed:
                        item[1] -= pushed
                        graph[v][rev][1] += pushed
                        return pushed
                cursor[u] += 1
            return 0

        while True:
            pushed = send(source, total + 1)
            if not pushed:
                break
            flow += pushed


def audit_compiled_surface() -> dict:
    # These strings are load-bearing: they distinguish generic interfaces from
    # a real extractor and are checked against the production source on replay.
    paths = {
        "interface": ROOT / "problems/23/lean/Erdos23Delta0/Ell5FullBankInterface.lean",
        "portSinks": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/FullBankPortSinks.lean",
        "globalPackage": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/FullBankToLengthSurplusCharge.lean",
        "endpointReserve": ROOT / "problems/23/lean/Erdos23Delta0/EndpointReserveHall.lean",
        "collisionAssignment": ROOT / "problems/23/lean/Erdos23Delta0/CollisionTokenAssignment.lean",
        "typedSources": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/TypedFullBankSources.lean",
        "compiledAuxRelation": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/MinimumDemandCollisionHall.lean",
        "checkedC5Terminal": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/CheckedC5BaseTransfer.lean",
        "checkedRowTerminal": ROOT / "problems/23/lean/Erdos23Delta0/Gamma/CheckedRowCompanionBaseTransfer.lean",
    }
    interface = paths["interface"].read_text(encoding="utf-8")
    port_sinks = paths["portSinks"].read_text(encoding="utf-8")
    package = paths["globalPackage"].read_text(encoding="utf-8")
    endpoint_reserve = paths["endpointReserve"].read_text(encoding="utf-8")
    collision_assignment = paths["collisionAssignment"].read_text(encoding="utf-8")
    typed_sources = paths["typedSources"].read_text(encoding="utf-8")
    aux_relation = paths["compiledAuxRelation"].read_text(encoding="utf-8")
    checked_c5 = paths["checkedC5Terminal"].read_text(encoding="utf-8")
    checked_row = paths["checkedRowTerminal"].read_text(encoding="utf-8")
    lean_root = ROOT / "problems/23/lean/Erdos23Delta0"
    missing_terms = {}
    for term in ("CheckedTransferMatching", "outsideAttachment"):
        proc = subprocess.run(
            ["rg", "-l", term, str(lean_root)],
            check=False, capture_output=True, text=True,
        )
        assert proc.returncode in (0, 1)
        missing_terms[term] = [line for line in proc.stdout.splitlines() if line]
    assertions = {
        "interface_declares_remaining_open_existence":
            "The remaining open theorem `Ell5FullBankRelaxedCover_exists`" in interface,
        "port_sinks_explicitly_lack_incidence":
            "legal edge-to-token incidence is still absent from this package" in port_sinks,
        "global_package_capacity_fields_are_data":
            "doorCapQ : ℚ" in package
            and "vertexSlackCapQ : ℚ" in package
            and "c5BaseCapQ : ℚ" in package
            and "pruneCapQ : ℚ" in package,
        "endpoint_reserve_does_not_construct_reserve":
            "The module does not construct the reserve" in endpoint_reserve,
        "collision_assignment_requires_provider":
            "It does not assert that a provider exists" in collision_assignment,
        "typed_sources_lack_sink_adapter":
            "no such adapter is assumed here" in typed_sources,
        "compiled_aux_relation_has_only_two_patterns":
            "SameOwner d s ∨ RowCompanion G c d s" in aux_relation,
        "checked_c5_terminal_is_literal_common_blue":
            "blueb G c T.sourceX T.owner = true" in checked_c5
            and "blueb G c T.sourceY T.owner = true" in checked_c5
            and "dM G c T.switch + 2 <= dB G c T.switch" in checked_c5,
        "checked_c5_global_matching_is_separate":
            "Permanently-Free source ownership and global matching are" in checked_c5
            and "separate layers" in checked_c5,
        "checked_row_global_matching_is_separate":
            "The source slot and global matching layers remain separate" in checked_row,
        "checked_transfer_matching_not_compiled":
            not missing_terms["CheckedTransferMatching"],
        "outside_attachment_not_compiled":
            not missing_terms["outsideAttachment"],
    }
    assert all(assertions.values())
    return {
        "status": "UNDEFINED_WITHOUT_REAL_GRAPH_DERIVED_PROVIDER",
        "assertions": assertions,
        "capacityClasses": {
            "door": "GENERIC_OWN_DOOR_CHECKER_EXISTS_BUT_NO_R29_EXTRACTOR",
            "vertexSlack": "GENERIC_CONSTRUCTOR_REQUIRES_EXPLICIT_SLACK_AND_LEGALITY",
            "c5Base": "LITERAL_COMMON_BLUE_TERMINAL_CHECKER_EXISTS_BUT_SOURCE_OWNERSHIP_GLOBAL_MATCHING_AND_SINK_ADAPTER_ARE_ABSENT",
            "prune": "TYPED_KEY_EXISTS_BUT_REAL_PRUNE_SLOT_TRANSPORT_PROVIDER_ABSENT",
        },
        "sourceSha256": {name: sha256(path) for name, path in paths.items()},
    }


def audit_maxcut_decomposition(module, data: dict) -> dict:
    """Executable proof of the five additive class upper bounds."""
    obj = json.loads(MAXCUT_CLASSES.read_text(encoding="utf-8"))
    classes = {
        name: {edge(*e) for e in edges}
        for name, edges in obj["classes"].items()
    }
    names = sorted(classes)
    for i, name in enumerate(names):
        for other in names[i + 1:]:
            assert classes[name].isdisjoint(classes[other])
    assert set().union(*classes.values()) == data["graph"]

    # Traffic class: exact 16*27^2 quotient enumeration from the constructor.
    traffic_max, traffic_achievers = module.locked_double_star_maxcut()
    assert traffic_max == 4110 and traffic_achievers > 0

    # Selector class: 676 edge-disjoint C5 cycles, so every cut misses one
    # edge per cycle and cuts at most 3380-676 = 2704 edges.
    selector_cycles = []
    for meta in data["selectorMeta"]:
        row = (
            meta["q"], meta["xF"], meta["yF"],
            meta["xD"], meta["yD"], meta["q"]
        )
        selector_cycles.append({edge(u, v) for u, v in zip(row, row[1:])})
    assert all(len(cycle) == 5 for cycle in selector_cycles)
    selector_union = set()
    for cycle in selector_cycles:
        assert selector_union.isdisjoint(cycle)
        selector_union.update(cycle)
    assert selector_union == classes["selectors"]

    # Three edge-disjoint seed C5 cycles.
    seed_cycles = []
    for atom, row in zip(data["atoms"][-3:], data["rows"][-3:]):
        cycle = {edge(u, v) for u, v in zip(row, row[1:])}
        cycle.add(atom)
        seed_cycles.append(cycle)
    seed_union = set()
    for cycle in seed_cycles:
        assert len(cycle) == 5 and seed_union.isdisjoint(cycle)
        seed_union.update(cycle)
    assert seed_union == classes["seeds"]

    # Circuit class: 39 unrestricted support/active edges plus 28
    # edge-disjoint 7-cycles (one atom and its private length-6 gadget).
    circuit_offset = 2762
    local_atoms = sorted(
        {edge(i, (i + 4) % 26) for i in range(26)}
        | {edge(26, 3), edge(26, 23)}
    )
    circuit_cycles = []
    next_vertex = circuit_offset + 27
    for a, b in local_atoms:
        atom = edge(circuit_offset + a, circuit_offset + b)
        internal = list(range(next_vertex, next_vertex + 5))
        next_vertex += 5
        path = [circuit_offset + a] + internal + [circuit_offset + b]
        cycle = {atom} | {edge(u, v) for u, v in zip(path, path[1:])}
        circuit_cycles.append(cycle)
    assert next_vertex == 2929
    circuit_cycle_union = set()
    for cycle in circuit_cycles:
        assert len(cycle) == 7 and circuit_cycle_union.isdisjoint(cycle)
        circuit_cycle_union.update(cycle)
    circuit_free = classes["circuit"] - circuit_cycle_union
    assert len(circuit_free) == 39
    assert circuit_cycle_union | circuit_free == classes["circuit"]
    assert len(classes["cable"]) == 6

    upper = {
        "traffic": traffic_max,
        "selectors": len(classes["selectors"]) - len(selector_cycles),
        "seeds": len(classes["seeds"]) - len(seed_cycles),
        "circuit": len(circuit_free) + 6 * len(circuit_cycles),
        "cable": len(classes["cable"]),
    }
    assert upper == {
        "traffic": 4110, "selectors": 2704, "seeds": 12,
        "circuit": 207, "cable": 6,
    }
    assert sum(upper.values()) == 7039
    attained = {
        name: sum(data["side"][u] != data["side"][v] for u, v in edges)
        for name, edges in classes.items()
    }
    assert attained == upper
    return {
        "classEdgeCounts": {name: len(edges) for name, edges in classes.items()},
        "classUpperBounds": upper,
        "attainingClassCounts": attained,
        "trafficQuotientCases": 16 * 27 * 27,
        "selectorEdgeDisjointC5s": len(selector_cycles),
        "seedEdgeDisjointC5s": len(seed_cycles),
        "circuitFreeEdges": len(circuit_free),
        "circuitEdgeDisjointC7s": len(circuit_cycles),
        "maxCut": sum(upper.values()),
        "sourceSha256": {
            "graphClasses": sha256(MAXCUT_CLASSES),
            "certificate": sha256(MAXCUT_CERT),
        },
    }


def main():
    module = load_constructor()
    data = module.build()
    rows = all_anchor_rows(data)
    advertised_tuple = json.loads(BEST_TUPLE.read_text(encoding="utf-8"))
    assert advertised_tuple["score"] == 23115
    assert len(advertised_tuple["selector_choices"]) == 676
    for choice in advertised_tuple["selector_choices"]:
        selector = choice["selector"]
        assert tuple(choice["row"]) == rows[data["selectorStart"] + selector]
    state = rebuild_scope(data, rows)

    # Structural gates.
    assert data["n"] == 2943
    assert len(data["blue"]) == 7039
    assert len(data["bad"]) == 1383
    assert len(data["graph"]) == 8422
    assert data["blue"].isdisjoint(data["bad"])
    assert triangle_free(data["n"], data["graph"])
    assert connected(data["n"], data["blue"])
    assert all(data["side"][u] != data["side"][v] for u, v in data["blue"])
    assert all(data["side"][u] == data["side"][v] for u, v in data["bad"])
    assert len(rows) == len(data["atoms"]) == 1383
    assert all(len(row) == len(set(row)) == 5 for row in rows)
    assert all(
        edge(row[0], row[-1]) == atom
        and all(edge(u, v) in data["blue"] for u, v in zip(row, row[1:]))
        for atom, row in zip(data["atoms"], rows)
    )

    row_hist = Counter()
    gamma = 0
    for atom in data["atoms"]:
        dist, count = bfs_dist_count(data["n"], data["blue"], atom[0])
        assert dist[atom[1]] == 4
        row_hist[count[atom[1]]] += 1
        gamma += 25
    assert row_hist == Counter({1: 707, 680: 676})
    assert gamma == 34575
    assert sum(data["classMax"]) == len(data["blue"]) == 7039
    maxcut_audit = audit_maxcut_decomposition(module, data)

    demand_by_owner = {
        owner: state["collision"].get(owner, 0)
        + state["hit_need"].get(owner, 0)
        for owner in OWNERS
    }
    assert demand_by_owner == {0: 6651, 1: 6651, 2: 6651}
    assert sum(demand_by_owner.values()) == 19953

    source_data = staged_sources(data, state)
    stages = source_data["stages"]
    stage_order = [
        "sameFirst", "commonBad", "rowCompanion",
        "commonBlueC5Terminal", "outsideAttachmentScoped"
    ]
    cumulative = []
    prior_keys = set()
    maps = []
    for stage in stage_order:
        maps.append(stages[stage])
        masks = aggregate_masks(maps)
        hist, cuts = hall_cuts(demand_by_owner, masks)
        keys = set(masks)
        flow = max_flow_by_masks(demand_by_owner, hist)
        cumulative.append({
            "stage": stage,
            "rawKeys": len(stages[stage]),
            "incrementalUniqueKeys": len(keys - prior_keys),
            "cumulativeUniqueKeys": len(keys),
            "maskHistogram": {str(k): v for k, v in sorted(hist.items())},
            "fullShoreDemand": 19953,
            "fullShoreReach": len(keys),
            "fullShoreDefect": 19953 - len(keys),
            "maxFlow": flow,
            "allHallCutsPass": all(cut["defect"] <= 0 for cut in cuts),
            "cuts": cuts,
        })
        prior_keys = keys

    assert [x["incrementalUniqueKeys"] for x in cumulative] == [17325, 0, 2600, 216, 0]
    assert [x["cumulativeUniqueKeys"] for x in cumulative] == [17325, 17325, 19925, 20141, 20141]
    assert [x["maxFlow"] for x in cumulative] == [17325, 17325, 19925, 19953, 19953]
    assert cumulative[2]["fullShoreDefect"] == 28
    assert cumulative[3]["fullShoreDefect"] == -188
    assert cumulative[3]["allHallCutsPass"]
    assert cumulative[4]["allHallCutsPass"]

    legacy_maps = [
        stages["sameFirst"], stages["commonBad"], stages["rowCompanion"],
        stages["commonBlueC5Terminal"],
        stages["outsideAttachmentLegacyUnscoped"],
    ]
    legacy_masks = aggregate_masks(legacy_maps)
    legacy_hist, legacy_cuts = hall_cuts(demand_by_owner, legacy_masks)
    legacy_unscoped_stage = {
        "stage": "outsideAttachmentLegacyUnscoped",
        "incrementalUniqueKeys": len(
            set(legacy_masks)
            - set(aggregate_masks(legacy_maps[:-1]))
        ),
        "cumulativeUniqueKeys": len(legacy_masks),
        "maskHistogram": {str(k): v for k, v in sorted(legacy_hist.items())},
        "fullShoreDemand": 19953,
        "fullShoreReach": len(legacy_masks),
        "fullShoreDefect": 19953 - len(legacy_masks),
        "maxFlow": max_flow_by_masks(demand_by_owner, legacy_hist),
        "allHallCutsPass": all(cut["defect"] <= 0 for cut in legacy_cuts),
        "cuts": legacy_cuts,
    }
    assert legacy_unscoped_stage["incrementalUniqueKeys"] == 912600
    assert legacy_unscoped_stage["cumulativeUniqueKeys"] == 932741
    assert legacy_unscoped_stage["maxFlow"] == 19953
    assert legacy_unscoped_stage["allHallCutsPass"]

    components = source_data["components"]
    attachments = source_data["attachments"]
    eligible = source_data["eligible_by_owner"]
    eligible_unscoped = source_data["eligible_unscoped_by_owner"]
    assert len(state["selected"]) == 2127
    assert len(components) == 704
    assert Counter(map(len, components)) == Counter({1: 676, 5: 28})
    assert all(len(eligible[o]) == 0 for o in OWNERS)
    assert all(len(eligible_unscoped[o]) == 676 for o in OWNERS)
    assert eligible_unscoped[0] == eligible_unscoped[1] == eligible_unscoped[2]
    assert all(source_data["signed_degree"][x] == 4 for x in eligible_unscoped[0])
    pair_losses = {
        source_data["pair_loss"](x, y)
        for x in eligible_unscoped[0] for y in eligible_unscoped[0] if x != y
    }
    assert pair_losses == {8}
    assert len(stages["outsideAttachmentScoped"]) == 0
    assert len(stages["outsideAttachmentLegacyUnscoped"]) == 676 * 675 * 2

    # Extend the independently certified auxiliary flow by 28 literal
    # common-blue terminal half-slots.  The published flow fills owners 0 and
    # 1 and leaves exactly 28 units at owner 2.
    old_cert = json.loads(SCOPED_HALL_CERT.read_text(encoding="utf-8"))
    old_flow = old_cert["flow_certificate_by_source_mask_to_owner"]
    received = Counter()
    used_by_mask = Counter()
    for label, amount in old_flow.items():
        mask, owner = map(int, label.split("->"))
        assert mask & (1 << owner)
        used_by_mask[mask] += amount
        received[owner] += amount
    pre_common_blue_masks = aggregate_masks([
        stages["sameFirst"], stages["commonBad"], stages["rowCompanion"]
    ])
    pre_common_blue_hist = Counter(pre_common_blue_masks.values())
    assert all(used_by_mask[mask] <= pre_common_blue_hist[mask] for mask in used_by_mask)
    assert received == Counter({0: 6651, 1: 6651, 2: 6623})
    common_blue_incremental = {
        key: mask for key, mask in stages["commonBlueC5Terminal"].items()
        if key not in pre_common_blue_masks
    }
    assert len(common_blue_incremental) == 216
    repair_keys = [
        key for key in sorted(common_blue_incremental)
        if common_blue_incremental[key] & (1 << 2)
    ][:28]
    assert len(repair_keys) == len(set(repair_keys)) == 28
    assert all(
        common_blue_incremental[key] & (1 << 2)
        for key in repair_keys
    )
    received[2] += len(repair_keys)
    assert received == Counter(demand_by_owner)
    common_blue_repair_witnesses = []
    for x, y, half in repair_keys:
        common_blue_repair_witnesses.append({
            "source": [x, y, half],
            "owner": 2,
            "blueToOwnerX": edge(x, 2) in data["blue"],
            "blueToOwnerY": edge(y, 2) in data["blue"],
            "pairCount": state["pair"][x, y],
            "switchLoss": source_data["pair_loss"](x, y),
            "adjustedSurplus": source_data["pair_loss"](x, y) - 2,
        })
    assert all(
        w["blueToOwnerX"] and w["blueToOwnerY"]
        and w["pairCount"] == 0
        and w["adjustedSurplus"] >= 0
        for w in common_blue_repair_witnesses
    )

    # Compact witness to the old R23 Python-gate omission: these sources pass
    # its unscoped attachment test but have no cooccurring attachment in the
    # owner's active component.
    outside_unscoped_examples = []
    for x, y, half in sorted(stages["outsideAttachmentLegacyUnscoped"])[:2]:
        cx = source_data["component_id"][x]
        outside_unscoped_examples.append({
            "source": [x, y, half],
            "attachmentsX": sorted(source_data["attachments"][cx]),
            "unscopedCooccurringAttachmentsX": {
                str(o): [
                    a for a in sorted(source_data["attachments"][cx])
                    if state["pair"][o, a] > 0
                ] for o in OWNERS
            },
            "componentScopedCooccurringAttachmentsX": {
                str(o): [
                    a for a in sorted(source_data["attachments"][cx])
                    if state["pair"][o, a] > 0
                    and state["component_root"][a] == state["component_root"][o]
                ] for o in OWNERS
            },
        })
    assert all(
        all(w["unscopedCooccurringAttachmentsX"][str(o)] for o in OWNERS)
        and all(not w["componentScopedCooccurringAttachmentsX"][str(o)] for o in OWNERS)
        for w in outside_unscoped_examples
    )

    compiled = audit_compiled_surface()
    weighted_requirement = weighted_singleton_requirement(data, state)
    payload = {
        "schema": "R29_FULLBANK_GATE_V1",
        "verdict": {
            "componentScopedFourPatternTransfer": "FAIL_DEFECT_28",
            "compiledCommonBlueTerminalRelation": "PASS_ABSORBS_28_AT_CONDITIONAL_OWNER_HALL_LEVEL",
            "componentScopedR23OutsideAttachment": "BLOCKED_ZERO_ELIGIBLE_SOURCES",
            "legacyUnscopedR23PythonGate": "PASS_ABSORBS_28_BUT_OMITS_COMPONENT_EQUALITY",
            "decisiveFullBankFalsifier": False,
            "decisiveStatusReason": "COMMON_BLUE_TERMINALS_CLOSE_THE_FINITE_OWNER_HALL_DEFECT_BUT_PRODUCTION_SOURCE_OWNERSHIP_GLOBAL_MATCHING_AND_PORT_TO_TOKEN_ADAPTER_ARE_UNDEFINED",
            "compiledEndToEndFullBankInstantiation": compiled["status"],
        },
        "graph": {
            "n": data["n"],
            "edges": len(data["graph"]),
            "blue": len(data["blue"]),
            "bad": len(data["bad"]),
            "maxCut": sum(data["classMax"]),
            "maxCutAudit": maxcut_audit,
            "gamma": gamma,
            "rowHistogram": {str(k): v for k, v in sorted(row_hist.items())},
        },
        "allAnchor": {
            "selectedVertices": len(state["selected"]),
            "activeVertices": len(state["active_vertices"]),
            "activeEdges": len(state["active_edges"]),
            "demandedActiveEdges": len(state["demanded_active"]),
            "owners": {
                str(o): {
                    "collision": state["collision"].get(o, 0),
                    "hitNeed": state["hit_need"].get(o, 0),
                    "demand": demand_by_owner[o],
                } for o in OWNERS
            },
            "hubShoreDemand": sum(demand_by_owner.values()),
        },
        "outsideAttachment": {
            "outsideVertices": data["n"] - len(state["selected"]),
            "componentCount": len(components),
            "componentSizeHistogram": {
                str(k): v for k, v in sorted(Counter(map(len, components)).items())
            },
            "componentScopedEligibleVerticesPerHub": {
                str(o): len(eligible[o]) for o in OWNERS
            },
            "legacyUnscopedEligibleVerticesPerHub": {
                str(o): len(eligible_unscoped[o]) for o in OWNERS
            },
            "eligibleSingletonSignedDegree": 4,
            "everyOrderedPairSwitchLoss": 8,
            "componentScopedOrderedCells": 0,
            "componentScopedHalfSlots": 0,
            "legacyUnscopedOrderedCells": 676 * 675,
            "legacyUnscopedHalfSlots": 676 * 675 * 2,
            "legacyUnscopedExamples": outside_unscoped_examples,
        },
        "commonBlueC5Terminal": {
            "rawKeys": len(stages["commonBlueC5Terminal"]),
            "incrementalUniqueKeysAfterAuxiliaryRelation": len(common_blue_incremental),
            "fullShoreReachBefore": cumulative[2]["fullShoreReach"],
            "fullShoreReachAfter": cumulative[3]["fullShoreReach"],
            "fullShoreDefectBefore": cumulative[2]["fullShoreDefect"],
            "fullShoreDefectAfter": cumulative[3]["fullShoreDefect"],
            "exactRepairOwner": 2,
            "exactRepairHalfSlots": [list(key) for key in repair_keys],
            "exactRepairWitnesses": common_blue_repair_witnesses,
            "productionCaveat": "TERMINAL_VALIDITY_IS_COMPILED; SOURCE_OWNERSHIP_GLOBAL_MATCHING_AND_FULLBANK_SINK_ADAPTER_ARE_SEPARATE_AND_UNINSTANTIATED",
        },
        "weightedFullBankAudit": weighted_requirement,
        "stages": cumulative,
        "legacyUnscopedDiagnosticStage": legacy_unscoped_stage,
        "compiledSurfaceAudit": compiled,
        "inputSha256": {
            "constructor": sha256(LEAD),
            "advertisedAllAnchorTupleFile": sha256(BEST_TUPLE),
            "auxiliaryScopedHallCertificate": sha256(SCOPED_HALL_CERT),
            "canonicalPayload": hashlib.sha256(module.canonical_bytes(data)).hexdigest(),
            "allAnchorTuple": hashlib.sha256(
                json.dumps(rows, separators=(",", ":")).encode()
            ).hexdigest(),
        },
    }
    out = HERE / "RESULT.json"
    out.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
