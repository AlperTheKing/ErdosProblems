"""Worker-3 independent exact R29 all-anchor hub-shore verifier for the R20/R23 four-pattern relation.

The canonical constructor is used only for labelled graph/row incidence.  This
file independently rebuilds the selected tuple, active scope, obligations,
reservations, four source patterns, and all eight three-owner cuts.
"""

from collections import Counter, defaultdict, deque
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
BEST_TUPLE = ROOT / "tmp/fanout/r29_gate/d09/retry2/best_tuple.json"
OWNERS = (0, 1, 2)
REASON_BITS = {
    "sameFirst": 1,
    "commonBad": 2,
    "rowCompanion": 4,
    "outsideAttachment": 8,
}


def norm(x, y):
    return (x, y) if x < y else (y, x)


def file_sha(path):
    return sha256(path.read_bytes()).hexdigest()


def rational_text(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def load_canonical():
    spec = spec_from_file_location("r29_canonical_gate", LEAD)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    data = module.build()
    return module, data


def incidence_sha(data, rows):
    payload = {
        "n": data["n"],
        "blue": sorted(data["blue"]),
        "bad": sorted(data["bad"]),
        "side": data["side"],
        "rows": rows,
        "selector_anchor_rows": [m["anchorRow"] for m in data["selectorMeta"]],
        "selector_start": data["selectorStart"],
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return sha256(raw).hexdigest()


def all_anchor_rows(data):
    rows = list(data["rows"])
    for offset, meta in enumerate(data["selectorMeta"]):
        rows[data["selectorStart"] + offset] = tuple(meta["anchorRow"])
    return tuple(tuple(row) for row in rows)


def row_data(n, rows):
    pair = Counter()
    load = Counter()
    selected = set()
    support = set()
    for row in rows:
        selected.update(row)
        for x in row:
            load[x] += 1
            for y in row:
                pair[x, y] += 1
        support.update(norm(x, y) for x, y in zip(row, row[1:]))
    companions = {
        owner: {x for x in range(n) if pair[owner, x] > 0}
        for owner in OWNERS
    }
    return pair, load, selected, support, companions


def active_scope(data, rows, pair, load, selected, support):
    active_edges = {
        edge for edge in data["blue"]
        if edge not in support and edge[0] in selected and edge[1] in selected
    }
    parent = {v: v for v in selected}

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    def union(x, y):
        x, y = find(x), find(y)
        if x != y:
            parent[max(x, y)] = min(x, y)

    for x, y in active_edges:
        union(x, y)
    active_roots = {
        find(x) for x, y in data["bad"]
        if x in selected and y in selected and find(x) == find(y)
    }
    active_vertices = {v for v in selected if find(v) in active_roots}
    demanded_active = {
        edge for edge in active_edges if find(edge[0]) in active_roots
    }
    degree = Counter()
    for x, y in demanded_active:
        degree[x] += 1
        degree[y] += 1
    collision = {
        v: 2 * sum(max(0, pair[v, y] - 1) for y in range(data["n"]))
        for v in active_vertices
    }
    hit_need = {
        v: max(0, degree[v] - max(0, data["n"] - 5 * load[v]))
        for v in active_vertices
    }
    score = sum(collision.values()) + sum(hit_need.values())
    return active_edges, demanded_active, active_vertices, collision, hit_need, score


def outside_components(data, selected, pair):
    adjacency = [set() for _ in range(data["n"])]
    for x, y in data["blue"]:
        adjacency[x].add(y)
        adjacency[y].add(x)
    component_id = [-1] * data["n"]
    components = []
    attachments = []
    for root in range(data["n"]):
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
            for y in adjacency[x]:
                if y in selected:
                    attachment.add(y)
                elif component_id[y] < 0:
                    component_id[y] = cid
                    todo.append(y)
        components.append(frozenset(vertices))
        attachments.append(frozenset(attachment))
    eligible = {}
    for owner in OWNERS:
        ids = {
            cid for cid, attachment in enumerate(attachments)
            if any(pair[owner, a] > 0 for a in attachment)
        }
        eligible[owner] = {
            x for cid in ids for x in components[cid]
        }
    return component_id, components, attachments, eligible


def signed_loss_oracle(data, component_id, components):
    signed_degree = Counter()
    edge_sign = {}
    for edge in data["blue"]:
        edge_sign[edge] = 1
        signed_degree[edge[0]] += 1
        signed_degree[edge[1]] += 1
    for edge in data["bad"]:
        edge_sign[edge] = -1
        signed_degree[edge[0]] -= 1
        signed_degree[edge[1]] -= 1

    component_loss = []
    for vertices in components:
        internal = sum(
            sign for edge, sign in edge_sign.items()
            if edge[0] in vertices and edge[1] in vertices
        )
        component_loss.append(sum(signed_degree[x] for x in vertices) - 2 * internal)
    cross_sign = Counter()
    for (x, y), sign in edge_sign.items():
        cx, cy = component_id[x], component_id[y]
        if cx >= 0 and cy >= 0 and cx != cy:
            cross_sign[norm(cx, cy)] += sign

    def pair_loss(x, y):
        return signed_degree[x] + signed_degree[y] - 2 * edge_sign.get(norm(x, y), 0)

    def component_union_loss(cx, cy):
        if cx == cy:
            return component_loss[cx]
        return component_loss[cx] + component_loss[cy] - 2 * cross_sign[norm(cx, cy)]

    return pair_loss, component_union_loss


def build_sources(
    data, pair, companions, demanded_active, active_vertices,
    component_id, components, eligible_outside, pair_loss, component_union_loss,
):
    bad_neighbors = defaultdict(set)
    for x, y in data["bad"]:
        bad_neighbors[x].add(y)
        bad_neighbors[y].add(x)

    owner_masks = {}
    reason_masks = {}
    stage_new_cells = Counter()
    stage_new_capacity = Counter()
    stage_owner_arcs = Counter()

    def capacity(cell):
        x, y = cell
        return 1 if norm(x, y) in demanded_active and x in active_vertices else 2

    def add(pattern, owner, cell):
        bit = 1 << owner
        stage_owner_arcs[pattern] += int(not owner_masks.get(cell, 0) & bit)
        if cell not in owner_masks:
            stage_new_cells[pattern] += 1
            stage_new_capacity[pattern] += capacity(cell)
        owner_masks[cell] = owner_masks.get(cell, 0) | bit
        reason_masks[cell] = reason_masks.get(cell, 0) | REASON_BITS[pattern]

    for owner in OWNERS:
        for y in range(data["n"]):
            if y != owner and pair[owner, y] == 0:
                add("sameFirst", owner, (owner, y))

    for owner in OWNERS:
        for x in sorted(bad_neighbors[owner]):
            for y in sorted(bad_neighbors[owner]):
                if x != y and pair[x, y] == 0 and pair_loss(x, y) >= 0:
                    add("commonBad", owner, (x, y))

    for owner in OWNERS:
        candidates = sorted(companions[owner] - {owner})
        for x in candidates:
            for y in candidates:
                if x != y and pair[x, y] == 0 and pair_loss(x, y) >= 0:
                    add("rowCompanion", owner, (x, y))

    outside_loss_histogram = Counter()
    for owner in OWNERS:
        candidates = sorted(eligible_outside[owner])
        for x in candidates:
            for y in candidates:
                if x == y:
                    continue
                loss = component_union_loss(component_id[x], component_id[y])
                if loss >= 0:
                    add("outsideAttachment", owner, (x, y))
                    if owner == OWNERS[0]:
                        outside_loss_histogram[loss] += 1

    capacity_by_mask = Counter()
    cells_by_reason = Counter()
    reservations = []
    for cell, mask in owner_masks.items():
        cap = capacity(cell)
        capacity_by_mask[mask] += cap
        cells_by_reason[reason_masks[cell]] += 1
        if cap == 1:
            reservations.append(cell)
    return {
        "owner_masks": owner_masks,
        "reason_masks": reason_masks,
        "capacity_by_mask": capacity_by_mask,
        "stage_new_cells": stage_new_cells,
        "stage_new_capacity": stage_new_capacity,
        "stage_owner_arcs": stage_owner_arcs,
        "cells_by_reason": cells_by_reason,
        "reservations": sorted(reservations),
        "outside_loss_histogram": outside_loss_histogram,
    }


def cuts_and_flow(demand, capacity_by_mask, stage_capacity, owner_masks):
    cuts = []
    total_demand = sum(demand.values())
    for shore_mask in range(8):
        shore_demand = sum(demand[o] for o in OWNERS if shore_mask & (1 << o))
        reach = sum(cap for mask, cap in capacity_by_mask.items() if mask & shore_mask)
        cut_capacity = total_demand - shore_demand + reach
        cuts.append({
            "shore_mask": shore_mask,
            "shore": [o for o in OWNERS if shore_mask & (1 << o)],
            "demand": shore_demand,
            "neighborhood": reach,
            "deficiency": shore_demand - reach,
            "network_cut_capacity": cut_capacity,
        })
    min_cut = min(cuts, key=lambda item: (item["network_cut_capacity"], item["shore_mask"]))

    # The old 19,925-unit allocation plus 28 concrete outside halves.
    aggregate_flow = {
        "sameFirst_mask1_to_owner0": 5775,
        "sameFirst_mask2_to_owner1": 5775,
        "sameFirst_mask4_to_owner2": 5775,
        "rowCompanion_mask7_to_owner0": 876,
        "rowCompanion_mask7_to_owner1": 876,
        "rowCompanion_mask7_to_owner2": 848,
        "outsideAttachment_mask7_to_owner2": 28,
    }
    outside_cells = sorted(
        cell for cell, mask in owner_masks.items()
        if mask == 7 and cell[0] not in OWNERS and cell[0] >= 732
    )
    repair_sources = [
        {"x": x, "y": y, "half": half, "owner": 2}
        for x, y in outside_cells[:14] for half in (0, 1)
    ]
    received = {
        0: aggregate_flow["sameFirst_mask1_to_owner0"] + aggregate_flow["rowCompanion_mask7_to_owner0"],
        1: aggregate_flow["sameFirst_mask2_to_owner1"] + aggregate_flow["rowCompanion_mask7_to_owner1"],
        2: aggregate_flow["sameFirst_mask4_to_owner2"] + aggregate_flow["rowCompanion_mask7_to_owner2"]
           + aggregate_flow["outsideAttachment_mask7_to_owner2"],
    }
    assert received == demand
    assert stage_capacity["outsideAttachment"] >= 28
    assert len({(x["x"], x["y"], x["half"]) for x in repair_sources}) == 28
    return cuts, min_cut, aggregate_flow, repair_sources


def main():
    module, data = load_canonical()
    rows = all_anchor_rows(data)
    tuple_doc = json.loads(BEST_TUPLE.read_text(encoding="utf-8"))
    tuple_rows = [tuple(item["row"]) for item in tuple_doc["selector_choices"]]
    assert tuple_rows == [tuple(meta["anchorRow"]) for meta in data["selectorMeta"]]
    assert tuple_doc["score"] == 23115
    pair, load, selected, support, companions = row_data(data["n"], rows)
    active_edges, demanded_active, active_vertices, collision, hit_need, score = active_scope(
        data, rows, pair, load, selected, support
    )
    component_id, components, attachments, eligible_outside = outside_components(
        data, selected, pair
    )
    pair_loss, component_union_loss = signed_loss_oracle(data, component_id, components)
    source = build_sources(
        data, pair, companions, demanded_active, active_vertices,
        component_id, components, eligible_outside, pair_loss, component_union_loss,
    )
    demand = {
        owner: collision.get(owner, 0) + hit_need.get(owner, 0)
        for owner in OWNERS
    }
    cuts, min_cut, aggregate_flow, repair_sources = cuts_and_flow(
        demand, source["capacity_by_mask"], source["stage_new_capacity"], source["owner_masks"]
    )

    stage_capacity = source["stage_new_capacity"]
    old_reach = stage_capacity["sameFirst"] + stage_capacity["commonBad"] + stage_capacity["rowCompanion"]
    full_reach = sum(source["capacity_by_mask"].values())
    old_defect = sum(demand.values()) - old_reach
    full_defect = max(cut["deficiency"] for cut in cuts)
    outside_sizes = Counter(map(len, components))

    assertions = {
        "n_2943": data["n"] == 2943,
        "all_anchor_score_23115": score == 23115,
        "hub_demands_6651_each": demand == {0: 6651, 1: 6651, 2: 6651},
        "hub_demand_19953": sum(demand.values()) == 19953,
        "same_first_17325": stage_capacity["sameFirst"] == 17325,
        "common_bad_new_0": stage_capacity["commonBad"] == 0,
        "row_companion_new_2600": stage_capacity["rowCompanion"] == 2600,
        "old_reach_19925_defect_28": old_reach == 19925 and old_defect == 28,
        "outside_676_singletons": len(eligible_outside[0]) == 676
            and all(eligible_outside[o] == eligible_outside[0] for o in OWNERS),
        "outside_loss_always_8": source["outside_loss_histogram"] == Counter({8: 456300}),
        "outside_capacity_912600": stage_capacity["outsideAttachment"] == 912600,
        "four_pattern_reach_932525": full_reach == 932525,
        "four_pattern_hall": full_defect == 0 and min_cut["network_cut_capacity"] == 19953,
        "three_reservations": source["reservations"] == [(0, 55), (1, 2929), (2, 2930)],
    }
    assert all(assertions.values()), assertions

    certificate = {
        "schema": "worker3-r29-all-anchor-four-pattern-v1",
        "arithmetic": "integers and fractions.Fraction only; no floats",
        "input": {
            "lead_path": str(LEAD.relative_to(ROOT)).replace("\\", "/"),
            "lead_sha256": file_sha(LEAD),
            "canonical_payload_sha256": sha256(module.canonical_bytes(data)).hexdigest(),
            "canonical_incidence_sha256": incidence_sha(
                data, tuple(tuple(row) for row in data["rows"])
            ),
            "all_anchor_incidence_sha256": incidence_sha(data, rows),
            "all_anchor_tuple_path": str(BEST_TUPLE.relative_to(ROOT)).replace("\\", "/"),
            "all_anchor_tuple_sha256": file_sha(BEST_TUPLE),
        },
        "tuple": {
            "n": data["n"],
            "blue_edges": len(data["blue"]),
            "bad_edges": len(data["bad"]),
            "rows": len(rows),
            "selector_rows": len(data["selectorMeta"]),
            "selected_vertices": len(selected),
            "active_vertices": len(active_vertices),
            "active_edges": len(active_edges),
            "demanded_active_edges": len(demanded_active),
            "active_scoped_score": score,
        },
        "hub_shore": {
            "owners": list(OWNERS),
            "per_owner": {
                str(o): {
                    "collision": collision[o],
                    "hit_need": hit_need[o],
                    "demand_half_slots": demand[o],
                    "demand_q_at_K1": rational_text(Fraction(demand[o], 2)),
                    "companions_including_owner": len(companions[o]),
                    "eligible_outside_vertices": len(eligible_outside[o]),
                }
                for o in OWNERS
            },
            "demand_half_slots": sum(demand.values()),
            "demand_q_at_K1": rational_text(Fraction(sum(demand.values()), 2)),
        },
        "outside_components": {
            "outside_vertices": data["n"] - len(selected),
            "component_count": len(components),
            "size_histogram": {str(k): v for k, v in sorted(outside_sizes.items())},
            "eligible_component_count_per_owner": {
                str(o): len({component_id[x] for x in eligible_outside[o]}) for o in OWNERS
            },
            "eligible_vertices_per_owner": {
                str(o): len(eligible_outside[o]) for o in OWNERS
            },
            "eligible_ordered_pairs": 676 * 675,
            "switch_loss_histogram": {
                str(k): v for k, v in sorted(source["outside_loss_histogram"].items())
            },
        },
        "reservations": {
            "reserved_ordered_cells": [list(cell) for cell in source["reservations"]],
            "removed_half_slots": len(source["reservations"]),
            "rule": "capacity 1 on a demanded active ordered edge; capacity 2 otherwise",
        },
        "per_pattern_new_reach": {
            name: {
                "new_ordered_cells": source["stage_new_cells"][name],
                "new_owner_cell_arcs": source["stage_owner_arcs"][name],
                "new_half_slots": stage_capacity[name],
                "new_q_capacity_at_K1": rational_text(Fraction(stage_capacity[name], 2)),
            }
            for name in REASON_BITS
        },
        "source_capacity_by_owner_mask": {
            str(mask): capacity for mask, capacity in sorted(source["capacity_by_mask"].items())
        },
        "old_three_pattern": {
            "reach_half_slots": old_reach,
            "demand_minus_reach_half_slots": old_defect,
            "demand_minus_reach_q_at_K1": rational_text(Fraction(old_defect, 2)),
        },
        "four_pattern": {
            "reach_half_slots": full_reach,
            "reach_q_at_K1": rational_text(Fraction(full_reach, 2)),
            "hub_shore_demand_minus_reach_half_slots": sum(demand.values()) - full_reach,
            "hub_shore_demand_minus_reach_q_at_K1":
                rational_text(Fraction(sum(demand.values()) - full_reach, 2)),
            "maximum_deficiency_over_all_shores": full_defect,
        },
        "all_owner_shore_cuts": cuts,
        "minimum_cut": min_cut,
        "aggregate_full_flow": aggregate_flow,
        "explicit_28_half_outside_repair": repair_sources,
        "assertions": assertions,
    }
    output = HERE / "certificate_a.json"
    output.write_text(json.dumps(certificate, sort_keys=True, indent=2) + "\n", encoding="ascii")
    summary = {
        "certificate_sha256": file_sha(output),
        "score": score,
        "demand": sum(demand.values()),
        "old_reach": old_reach,
        "old_defect": old_defect,
        "outside_reach": stage_capacity["outsideAttachment"],
        "four_pattern_reach": full_reach,
        "maximum_deficiency": full_defect,
        "min_cut": min_cut["network_cut_capacity"],
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
