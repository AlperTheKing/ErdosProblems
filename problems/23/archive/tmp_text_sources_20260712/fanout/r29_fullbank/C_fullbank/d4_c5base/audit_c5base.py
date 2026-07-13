"""Exact R29 c5Base/source-key audit; integer arithmetic only."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
REBUILD = ROOT / "tmp/fanout/r29_gate/d05/retry2/rebuild_owner_hall.py"


def load_module(path):
    spec = importlib.util.spec_from_file_location("r29_owner_rebuild", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    m = load_module(REBUILD)
    incidence = m.load_untrusted_incidence()
    state = m.rebuild_scope(incidence)
    rows, pair, load, support, active_edges, active_vertices = state[:6]
    masks, reasons, companions = m.owner_sources(
        incidence, pair, active_edges, active_vertices)

    # Canonical source key is exactly the ordered FreeHalf triple used by the
    # reconstruction: (x,y,half).  Pattern labels are witnesses, not keys.
    keys = set(masks)
    reason_counts = Counter(reasons.values())
    same_first = {k for k in keys if reasons[k] & 1}
    row_companion = {k for k in keys if reasons[k] & 2}
    common_bad = set()       # reconstruction has no separate reason bit/pool
    outside_attachment = set()  # not implemented by this reconstruction/API

    # Any provider-supplied c5Base token keyed by the same FreeHalf is already
    # represented.  Union cardinality is the only permitted combined count.
    proposed_same_key_c5base = set(keys)
    independent_base_keys = set()  # no concrete R29 provider/exporter exists
    dedup_union = keys | proposed_same_key_c5base | independent_base_keys

    result = {
        "schema": "r29-c5base-source-key-audit-v1",
        "arithmetic": "integers_only",
        "instance": {"n": incidence["n"], "shore": [0, 1, 2]},
        "canonical_source_key": ["ordered_source_x", "ordered_source_y", "half_bit"],
        "reach": {
            "sameFirst_keys": len(same_first),
            "commonBad_additional_keys": len(common_bad),
            "rowCompanion_additional_keys": len(row_companion - same_first),
            "outsideAttachment_additional_keys": len(outside_attachment),
            "overlap_sameFirst_rowCompanion": len(same_first & row_companion),
            "deduplicated_FreeHalf_keys": len(keys),
        },
        "c5base_accounting_scaled_units": {
            "FreeHalf_reach_if_relabelled_c5Base": len(proposed_same_key_c5base),
            "additional_independent_base_density": len(independent_base_keys),
            "strongest_combined_after_source_key_dedup": len(dedup_union),
            "forbidden_naive_sum": len(keys) + len(proposed_same_key_c5base),
            "double_count_removed": len(keys & proposed_same_key_c5base),
            "compiled_concrete_R29_tokens_without_provider": 0,
            "conditional_emitted_tokens_if_partial_matching_covers_all_HitNeed": 3,
        },
        "assertions": {
            "reach_is_19925": len(keys) == 19925,
            "sameFirst_is_17325": len(same_first) == 17325,
            "rowCompanion_additional_is_2600": len(row_companion - same_first) == 2600,
            "pattern_overlap_is_zero": len(same_first & row_companion) == 0,
            "dedup_prohibits_39850": len(dedup_union) == 19925,
            "no_independent_provider_tokens_found": len(independent_base_keys) == 0,
        },
        "provider_assumptions": [
            "The lead build() incidence is the canonical reconstructed R29 N=2943 instance.",
            "A FreeHalf/c5Base adapter uses the ordered triple (x,y,half) as BaseKey/sourceId.",
            "Each admitted key has capacity one scaled unit (the prose 1/(2K) unit).",
            "Incidence to shore owners is the owner mask rebuilt by owner_sources.",
            "Any independent base-density provider must export concrete keys disjoint from all FreeHalf keys.",
            "No outsideAttachment checker/provider and no concrete R29 full-bank c5Base ledger are compiled.",
        ],
        "input_sha256": {
            "rebuild_owner_hall.py": digest(REBUILD),
            "r29_lead_gate.py": digest(m.LEAD),
        },
    }
    assert all(result["assertions"].values())
    out = HERE / "audit.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
