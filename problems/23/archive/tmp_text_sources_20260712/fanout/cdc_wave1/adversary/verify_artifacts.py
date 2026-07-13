#!/usr/bin/env python3
"""Replay and cross-check the CDC wave-1 adversary artifacts."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import run_wave
import selector_core as core


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="ascii"))


def canonical_ok(value: dict) -> bool:
    copy = dict(value)
    claimed = copy.pop("canonicalPayloadSha256")
    return core.canonical_sha(copy) == claimed


def source_hashes_ok(value: dict) -> bool:
    return all(
        sha256((HERE / name).read_bytes()).hexdigest() == expected
        for name, expected in value["sourceSha256"].items()
    )


def fixture_replay(name: str, graph: core.CutGraph) -> dict:
    artifact = load(name)
    row_db = core.complete_row_database(graph)
    replay = core.exhaustive_minimum_collision_tuples(graph, row_db)
    recorded = artifact["rowSelection"]
    replay_minimum = replay["minimumTuples"][0]["analysis"]
    recorded_minimum = recorded["minimumTuples"][0]["analysis"]
    g6 = artifact["graph"]["graph6"]
    decoded_n, decoded_edges = core.graph6_decode(g6)
    checks = {
        "canonicalPayloadSha256": canonical_ok(artifact),
        "sourceSha256": source_hashes_ok(artifact),
        "graph6ExactRoundTrip": decoded_n == graph.n and decoded_edges == graph.edges,
        "singletonCompleteRowDatabase": all(len(rows) == 1 for _edge, rows in row_db),
        "selectorVerdict": replay["selectorVerdict"]
        == recorded["selectorVerdict"]
        == "FAIL_ALL_MINIMUM_TUPLES",
        "minimumCollisionUnits": replay["minimumCollisionUnits"]
        == recorded["minimumCollisionUnits"],
        "maximumFlow": replay_minimum["flow"]["maximumFlow"]
        == recorded_minimum["flow"]["maximumFlow"],
        "defect": replay_minimum["flow"]["defect"]
        == recorded_minimum["flow"]["defect"],
        "minimumShore": replay_minimum["shoreAudit"]["minimumShore"]
        == recorded_minimum["shoreAudit"]["minimumShore"],
    }
    return {
        "checks": checks,
        "allChecksPass": all(checks.values()),
        "defect": replay_minimum["flow"]["defect"],
        "shoreOwners": replay_minimum["shoreAudit"]["minimumShore"]["owners"],
        "shoreDemand": replay_minimum["shoreAudit"]["minimumShore"]["demand"],
        "shoreCapacity": replay_minimum["shoreAudit"]["minimumShore"]["capacity"],
    }


def r53_crosscheck() -> dict:
    base = ROOT / "tmp" / "fanout" / "r53_global_softcap_gate"
    strict_path = base / "counterexample_n89.json"
    alternate_path = base / "n89_unscoped_p4_alternate.json"
    if not strict_path.exists() or not alternate_path.exists():
        return {"status": "SKIPPED_MISSING"}
    strict = json.loads(strict_path.read_text(encoding="ascii"))
    alternate = json.loads(alternate_path.read_text(encoding="ascii"))
    diagnostics = alternate["namedDiagnostics"]
    checks = {
        "strictP4N89": {
            "defect": strict["primal"]["defect"] == 2,
            "maximumFlow": strict["primal"]["maximumFlow"] == 774,
            "shore": strict["dual"]["shoreOwners"] == [0, 1, 2],
            "shoreDemand": strict["dual"]["shoreDemand"] == 528,
            "shoreCapacity": strict["dual"]["shoreCapacity"] == 526,
        },
        "unscopedP4Alternate": {
            "n24DefectZero": diagnostics["n24_r1_fixed_rows"]["defect"] == 0,
            "n89DefectZero": diagnostics["n89_singleton_row_database"]["defect"] == 0,
        },
    }
    return {
        "status": "COMPLETE",
        "strictSourceFileSha256": sha256(strict_path.read_bytes()).hexdigest(),
        "alternateSourceFileSha256": sha256(alternate_path.read_bytes()).hexdigest(),
        "checks": checks,
        "allChecksPass": all(
            value for group in checks.values() for value in group.values()
        ),
    }


def main() -> int:
    coverage = load("coverage_report.json")
    result = {
        "schema": "CDC_WAVE1_SELECTOR_ADVERSARY_REPLAY_V1",
        "counterexampleN24": fixture_replay(
            "counterexample_n24.json", core.n24_fixture()
        ),
        "counterexampleN89": fixture_replay(
            "counterexample_n89.json", core.n89_fixture()
        ),
        "coverageChecks": {
            "canonicalPayloadSha256": canonical_ok(coverage),
            "sourceSha256": source_hashes_ok(coverage),
            "randomSampleComplete": coverage["randomCensusStress"]["status"]
            == "COMPLETE",
            "blowupStressComplete": coverage["blowupStress"]["status"]
            == "COMPLETE",
        },
        "r53IndependentCrosscheck": r53_crosscheck(),
        "verifierSha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    result["allChecksPass"] = (
        result["counterexampleN24"]["allChecksPass"]
        and result["counterexampleN89"]["allChecksPass"]
        and all(result["coverageChecks"].values())
        and result["r53IndependentCrosscheck"].get("allChecksPass", False)
    )
    result["canonicalPayloadSha256"] = core.canonical_sha(result)
    run_wave.write_json(HERE / "verification.json", result)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["allChecksPass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
