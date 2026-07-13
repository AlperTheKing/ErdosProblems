from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
RESULT = LEAD.with_name("lead_result.json")
D03_GRAPH = ROOT / "tmp/fanout/r29_gate/d03/retry2/graph_classes.json"
D09_TUPLE = ROOT / "tmp/fanout/r29_gate/d09/retry2/best_tuple.json"
HAMMING_SOURCE = LEAD.with_name("r29_hamming_gate.py")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


spec = importlib.util.spec_from_file_location("untrusted_lead", LEAD)
lead = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(lead)

data = lead.build()
result_present = RESULT.exists()
claimed = json.loads(RESULT.read_text(encoding="utf-8")) if result_present else None
raw_hash = hashlib.sha256(lead.canonical_bytes(data)).hexdigest()

# Recompute aggregates from the returned incidence data, never from lead_result.json.
blue_by_class = Counter()
for u, v in data["blue"]:
    if {u, v} <= set(range(56)):
        blue_by_class["locked_core"] += 1
    elif u >= 2931 or v >= 2931:
        blue_by_class["seed"] += 1
    elif 2762 <= u <= 2928 and 2762 <= v <= 2928:
        blue_by_class["circuit_internal"] += 1
    else:
        blue_by_class["other"] += 1

baseline = lead.scoped_state(data, data["rows"])
anchor_rows = list(data["rows"])
for i, meta in enumerate(data["selectorMeta"]):
    anchor_rows[data["selectorStart"] + i] = meta["anchorRow"]
anchor_state = lead.scoped_state(data, tuple(anchor_rows))

adj_blue = lead.adjacency(data["n"], data["blue"])
hist = Counter()
for atom in data["atoms"]:
    dist, count = lead.bfs(adj_blue, atom[0])
    assert dist[atom[1]] == 4
    hist[count[atom[1]]] += 1

# Source-coverage audit: locate what is actually established by executable checks.
tree = ast.parse(LEAD.read_text(encoding="utf-8"))
assert_text = [ast.unparse(n.test) for n in ast.walk(tree) if isinstance(n, ast.Assert)]
scoped_calls = [
    ast.unparse(n)
    for n in ast.walk(tree)
    if isinstance(n, ast.Call)
    and isinstance(n.func, ast.Name)
    and n.func.id == "scoped_state"
]

out = {
    "input_hashes": {
        "lead_source": sha256(LEAD),
        "lead_result": sha256(RESULT) if result_present else None,
    },
    "lead_result_present": result_present,
    "canonical_certificate_sha256": raw_hash,
    "canonical_hash_matches_result": raw_hash == claimed["sha256"] if claimed else None,
    "recomputed": {
        "n": data["n"],
        "blue": len(data["blue"]),
        "bad": len(data["bad"]),
        "edges": len(data["graph"]),
        "rows": len(data["rows"]),
        "atoms": len(data["atoms"]),
        "row_histogram": dict(sorted(hist.items())),
        "baseline": {k: baseline[k] for k in ("score", "collisionTotal", "hitNeedTotal")},
        "all_anchor": {k: anchor_state[k] for k in ("score", "collisionTotal", "hitNeedTotal")},
        "all_anchor_delta": anchor_state["score"] - baseline["score"],
        "displayed_class_sum": sum(data["classMax"]),
        "locked_quotient": lead.locked_double_star_maxcut(),
        "coarse_blue_partition": dict(sorted(blue_by_class.items())),
    },
    "source_coverage": {
        "scoped_state_call_count": len(scoped_calls),
        "scoped_state_calls": scoped_calls,
        "has_assert_each_hamming_score_ge_30813": any("30813" in x for x in assert_text),
        "has_assert_global_score_ge_23115": any("score" in x and "23115" in x and ">=" in x for x in assert_text),
        "has_assert_maxcut_upper_bound": any("max" in x.lower() and "7039" in x and "<=" in x for x in assert_text),
    },
}

if D03_GRAPH.exists():
    d03 = json.loads(D03_GRAPH.read_text(encoding="utf-8"))
    d03_edges = {
        tuple(e) for edges in d03["classes"].values() for e in edges
    }
    out["cross_audit_d03_maxcut"] = {
        "graph_file_sha256": sha256(D03_GRAPH),
        "edge_set_equal_to_lead": d03_edges == data["graph"],
        "edge_count": len(d03_edges),
    }
if D09_TUPLE.exists():
    out["cross_audit_d09_global"] = {
        "best_tuple_sha256": sha256(D09_TUPLE),
        "matches_recomputed_all_anchor_score": anchor_state["score"] == 23115,
    }
out["hamming_gate"] = {
    "source_present": HAMMING_SOURCE.exists(),
    "source_sha256": sha256(HAMMING_SOURCE) if HAMMING_SOURCE.exists() else None,
    "result_present": HAMMING_SOURCE.with_name("hamming_result.json").exists(),
}

(HERE / "audit_result.json").write_text(
    json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(out, sort_keys=True))
