from collections import Counter, deque
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
BEST = ROOT / "tmp/fanout/r29_gate/d09/retry2/best_tuple.json"
CUT = ROOT / "tmp/fanout/r29_gate/d03/retry2/attaining_cut_bits.txt"
MAXCERT = ROOT / "tmp/fanout/r29_gate/d03/retry2/certificate.json"
FOURCERT = HERE.parent / "certificate.json"
FOURVERIFY = HERE.parent / "verify_fourpattern.py"
CERTVERIFY = HERE.parent / "verify_certificate.py"

def digest(p): return sha256(p.read_bytes()).hexdigest()
def load_module(path, name):
    s = spec_from_file_location(name, path); m = module_from_spec(s); s.loader.exec_module(m); return m

lead = load_module(LEAD, "r29_worker1_lead")
four = load_module(FOURVERIFY, "r29_worker1_four")
data = lead.build()
best = json.loads(BEST.read_text(encoding="ascii"))
cert = json.loads(FOURCERT.read_text(encoding="ascii"))
maxcert = json.loads(MAXCERT.read_text(encoding="ascii"))

rows = list(data["rows"])
for i, meta in enumerate(data["selectorMeta"]):
    rows[data["selectorStart"] + i] = tuple(meta["anchorRow"])
rows = tuple(rows)
assert [list(rows[data["selectorStart"] + x["selector"]]) for x in best["selector_choices"]] == [x["row"] for x in best["selector_choices"]]

pair, load, selected, support, companions = four.row_data(data["n"], rows)
active_edges, demanded, active_vertices, collision, hit_need, score = four.active_scope(data, rows, pair, load, selected, support)
cid, outside, attachments, eligible = four.outside_components(data, selected, pair)

# Connected components of the selected active-edge graph, including isolated selected vertices.
adj = {v: set() for v in selected}
for x, y in active_edges: adj[x].add(y); adj[y].add(x)
seen = set(); selected_components = []
for root in sorted(selected):
    if root in seen: continue
    q = deque([root]); seen.add(root); vs = []
    while q:
        x = q.popleft(); vs.append(x)
        for y in sorted(adj[x]):
            if y not in seen: seen.add(y); q.append(y)
    selected_components.append(vs)

bits = CUT.read_text(encoding="ascii").strip()
assert len(bits) == data["n"] and set(bits) <= {"0", "1"}
cut_edges = sum(bits[x] != bits[y] for x, y in data["blue"])
assert cut_edges == maxcert["maxcut"] == 7039

input_paths = [LEAD, BEST, CUT, MAXCERT, FOURCERT, FOURVERIFY, CERTVERIFY]
fixture = {
    "schema": "r29-n2943-all-anchor-canonical-fixture-v1",
    "arithmetic": "integers only; no floats",
    "inputs": [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": digest(p)} for p in input_paths],
    "constructor": {
        "call": "tmp/fanout/r29_gate/lead/r29_lead_gate.py:build()",
        "canonical_payload_sha256": lead.canonical_bytes(data).hex() and sha256(lead.canonical_bytes(data)).hexdigest(),
        "n": data["n"], "blue_edges": len(data["blue"]), "bad_edges": len(data["bad"]),
        "row_count": len(data["rows"]), "selector_start": data["selectorStart"], "selector_stop": data["selectorStop"],
    },
    "all_anchor_tuple": {
        "rows": [list(r) for r in rows],
        "selector_anchors": [{"selector": i, "row_index": data["selectorStart"]+i, "anchor_row": list(m["anchorRow"]), "atom": list(data["atoms"][data["selectorStart"]+i])} for i,m in enumerate(data["selectorMeta"])],
        "selected_vertices": sorted(selected), "selected_vertex_count": len(selected), "score": score,
    },
    "max_cut": {"value": cut_edges, "bits": bits, "shore_1": [i for i,b in enumerate(bits) if b == "1"], "class_upper_bounds": maxcert["class_upper_bounds"]},
    "scope": {
        "active_edges": [list(e) for e in sorted(active_edges)], "active_edge_count": len(active_edges),
        "demanded_active_edges": [list(e) for e in sorted(demanded)], "demanded_active_edge_count": len(demanded),
        "active_vertices": sorted(active_vertices), "active_vertex_count": len(active_vertices),
        "selected_active_edge_components": selected_components,
        "active_components": [vs for vs in selected_components if set(vs) & active_vertices],
        "outside_components": [{"vertices": sorted(vs), "attachments": sorted(attachments[i])} for i,vs in enumerate(outside)],
        "outside_component_size_histogram": dict(sorted(Counter(map(len,outside)).items())),
    },
    "scoped_demands": cert["hub_shore"],
    "reservations": cert["reservations"],
    "hub_shore": {"owners": cert["hub_shore"]["owners"], "demand_half_slots": cert["hub_shore"]["demand_half_slots"], "four_pattern_reach_half_slots": cert["four_pattern"]["reach_half_slots"], "old_three_pattern_reach_half_slots": cert["old_three_pattern"]["reach_half_slots"]},
}
(HERE / "fixture.json").write_text(json.dumps(fixture, sort_keys=True, separators=(",", ":")), encoding="ascii")

summary = {
    "fixture_sha256": digest(HERE / "fixture.json"), "n": data["n"], "blue_edges": len(data["blue"]), "bad_edges": len(data["bad"]),
    "rows": len(rows), "rigid_rows": data["selectorStart"] + (len(rows)-data["selectorStop"]), "selector_rows": data["selectorStop"]-data["selectorStart"],
    "selected_vertices": len(selected), "maxcut": cut_edges, "active_edges": len(active_edges), "demanded_active_edges": len(demanded),
    "active_vertices": len(active_vertices), "selected_components": len(selected_components), "active_components": sum(bool(set(vs) & active_vertices) for vs in selected_components), "outside_components": len(outside),
    "outside_vertices": sum(map(len,outside)), "hub_demand_half_slots": cert["hub_shore"]["demand_half_slots"],
    "reservations": len(cert["reservations"]["reserved_ordered_cells"]), "four_pattern_reach_half_slots": cert["four_pattern"]["reach_half_slots"],
}
(HERE / "audit_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n", encoding="ascii")
print(json.dumps(summary, sort_keys=True))
