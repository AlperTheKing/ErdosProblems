"""Independent arithmetic and witness audit for certificate.json."""

from collections import Counter, deque
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CERT_PATH = HERE / "certificate.json"
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load_graph():
    spec = spec_from_file_location("r29_input_for_audit", LEAD)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build()


def direct_loss(vertices, blue, bad):
    return (
        sum((x in vertices) != (y in vertices) for x, y in blue)
        - sum((x in vertices) != (y in vertices) for x, y in bad)
    )


def main():
    cert = json.loads(CERT_PATH.read_text(encoding="ascii"))
    assert cert["arithmetic"] == "integers and fractions.Fraction only; no floats"
    assert cert["input"]["lead_sha256"] == digest(LEAD)
    tuple_path = ROOT / cert["input"]["all_anchor_tuple_path"]
    assert cert["input"]["all_anchor_tuple_sha256"] == digest(tuple_path)

    demand = {
        int(owner): record["demand_half_slots"]
        for owner, record in cert["hub_shore"]["per_owner"].items()
    }
    assert demand == {0: 6651, 1: 6651, 2: 6651}
    patterns = cert["per_pattern_new_reach"]
    assert [patterns[name]["new_half_slots"] for name in (
        "sameFirst", "commonBad", "rowCompanion", "outsideAttachment"
    )] == [17325, 0, 2600, 0]
    assert Fraction(patterns["sameFirst"]["new_q_capacity_at_K1"]) == Fraction(17325, 2)
    assert Fraction(patterns["outsideAttachment"]["new_q_capacity_at_K1"]) == 0

    histogram = {
        int(mask): capacity
        for mask, capacity in cert["source_capacity_by_owner_mask"].items()
    }
    assert histogram == {1: 5775, 2: 5775, 4: 5775, 7: 2600}
    assert sum(histogram.values()) == 19925

    expected_cuts = []
    total_demand = sum(demand.values())
    for shore_mask in range(8):
        shore_demand = sum(demand[o] for o in range(3) if shore_mask & (1 << o))
        reach = sum(cap for mask, cap in histogram.items() if mask & shore_mask)
        expected_cuts.append((
            shore_mask, shore_demand, reach, shore_demand - reach,
            total_demand - shore_demand + reach,
        ))
    actual_cuts = [(
        row["shore_mask"], row["demand"], row["neighborhood"], row["deficiency"],
        row["network_cut_capacity"],
    ) for row in cert["all_owner_shore_cuts"]]
    assert actual_cuts == expected_cuts
    assert min(row[4] for row in expected_cuts) == 19925
    assert max(row[3] for row in expected_cuts) == 28
    assert cert["minimum_cut"]["shore_mask"] == 7

    flow = cert["aggregate_maximum_flow"]
    received = {
        0: flow["sameFirst_mask1_to_owner0"] + flow["rowCompanion_mask7_to_owner0"],
        1: flow["sameFirst_mask2_to_owner1"] + flow["rowCompanion_mask7_to_owner1"],
        2: flow["sameFirst_mask4_to_owner2"] + flow["rowCompanion_mask7_to_owner2"],
    }
    assert received == {0: 6651, 1: 6651, 2: 6623}
    assert sum(flow.values()) == 19925
    assert (
        flow["rowCompanion_mask7_to_owner0"]
        + flow["rowCompanion_mask7_to_owner1"]
        + flow["rowCompanion_mask7_to_owner2"]
    ) == 2600

    data = load_graph()
    rows = list(data["rows"])
    for offset, meta in enumerate(data["selectorMeta"]):
        rows[data["selectorStart"] + offset] = tuple(meta["anchorRow"])
    selected = {x for row in rows for x in row}
    pair = Counter((x, y) for row in rows for x in row for y in row)
    blue_adj = [set() for _ in range(data["n"])]
    for x, y in data["blue"]:
        blue_adj[x].add(y)
        blue_adj[y].add(x)

    support = {
        tuple(sorted((x, y)))
        for row in rows for x, y in zip(row, row[1:])
    }
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
            for y in blue_adj[x]:
                if y in selected:
                    attachment.add(y)
                elif component_id[y] < 0:
                    component_id[y] = cid
                    todo.append(y)
        components.append(vertices)
        attachments.append(attachment)

    for owner in range(3):
        loose = {
            cid for cid, attachment in enumerate(attachments)
            if any(pair[owner, a] > 0 for a in attachment)
        }
        strict = {
            cid for cid, attachment in enumerate(attachments)
            if any(pair[owner, a] > 0 and find(a) == find(owner) for a in attachment)
        }
        assert len(loose) == 676
        assert sum(len(components[cid]) for cid in loose) == 676
        assert strict == set()

    summary = {
        "certificate_sha256": digest(CERT_PATH),
        "cuts_checked": len(expected_cuts),
        "full_flow": sum(flow.values()),
        "minimum_cut": min(row[4] for row in expected_cuts),
        "maximum_deficiency": max(row[3] for row in expected_cuts),
        "strict_outside_eligible_vertices": 0,
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
