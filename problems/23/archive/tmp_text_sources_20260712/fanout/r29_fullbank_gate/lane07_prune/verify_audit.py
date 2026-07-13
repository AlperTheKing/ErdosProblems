"""Independent consistency verifier for lane07 prune audit outputs."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


audit = json.loads((HERE / "audit.json").read_text(encoding="utf-8"))
hall_path = ROOT / "tmp/fanout/r29_gate/d05/retry2/cut_certificate.json"
hall = json.loads(hall_path.read_text(encoding="utf-8"))

assert audit["status"] == "UNDEFINED"
assert all(audit["assertions"].values())
assert audit["hub_shore"]["demand"] == 19953
assert audit["hub_shore"]["implemented_base_freehalf_sources"] == 19925
assert audit["hub_shore"]["auxiliary_defect"] == 28
assert audit["hub_shore"]["demand_by_owner"] == {"0": 6651, "1": 6651, "2": 6651}
assert hall["maximum_deficiency_cut"] == {
    "demand": 19953, "gap": 28, "neighborhood": 19925,
    "shore": [0, 1, 2], "shore_mask": 7,
}
prune = audit["prune_operational_audit"]
assert prune["implemented_graph_derived_prune_source_records"] == 0
assert prune["prune_sources_reachable_from_hub_shore"] == 0
assert prune["overlap_with_existing_base_sources"] == 0
assert prune["new_distinct_sources_after_overlap_removal"] == 0
assert prune["incremental_exact_capacity_units"] == 0
assert prune["defect_after_all_enumerable_implemented_prune_sources"] == 28
assert prune["injectivity_is_vacuous"] and prune["no_double_spend_is_vacuous"]
assert audit["provider_boundary"]["concrete_provider_symbol_matches"]["matches"] == []

for relative, record in audit["source_manifest"].items():
    assert sha(ROOT / relative) == record["sha256"]
assert sha(hall_path) == audit["input_hashes"]["hall_cut_certificate"]

result = {
    "status": "PASS",
    "meaning": "audit.json is internally consistent and source hashes still match; the audited absorption verdict remains UNDEFINED",
    "checks": 18 + len(audit["source_manifest"]),
    "audit_sha256": sha(HERE / "audit.json"),
    "hall_certificate_sha256": sha(hall_path),
}
(HERE / "verification.json").write_text(
    json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(result, sort_keys=True))
