#!/usr/bin/env python3
"""Replay the official coherence-free selector coverage artifacts."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import official_selector as official
import r35_official_search as r35_search
import run_wave as helpers
import selector_core as core


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
COVERAGE = HERE / "official_coverage.json"
R35_RESULT = HERE / "r35_official_search.json"
OUTPUT = HERE / "official_verification.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_ok(value: dict) -> bool:
    copy = dict(value)
    claimed = copy.pop("canonicalPayloadSha256")
    return core.canonical_sha(copy) == claimed


def source_hashes_ok(value: dict) -> bool:
    return all(file_sha(HERE / name) == expected for name, expected in value["sourceSha256"].items())


def replay_fixture(graph: core.CutGraph, recorded: dict) -> dict:
    row_db = core.complete_row_database(graph)
    replay = official.exhaustive_minimum_collision_tuples(graph, row_db)
    analysis = replay["minimumTuples"][0]["analysis"]
    expected = recorded["evaluatedMinimumTuples"][0]["analysis"]
    decoded_n, decoded_edges = core.graph6_decode(recorded["graph6"])
    checks = {
        "graph6": decoded_n == graph.n and decoded_edges == graph.edges,
        "singletonRowDatabase": replay["tupleCount"] == 1,
        "selectorPass": replay["selectorVerdict"]
        == recorded["selectorVerdict"]
        == "PASS_SOME_MINIMUM_TUPLE",
        "minimumCollisionUnits": replay["minimumCollisionUnits"]
        == recorded["minimumCollisionUnits"],
        "maximumFlow": analysis["flow"]["maximumFlow"]
        == expected["maximumFlow"],
        "demand": analysis["flow"]["totalDemand"]
        == expected["collisionHalfDemand"],
        "defectZero": analysis["flow"]["defect"] == expected["defect"] == 0,
        "allShoreSlackNonnegative": analysis["shoreAudit"]["minimumShore"]["slack"]
        >= 0,
    }
    return {"checks": checks, "allChecksPass": all(checks.values())}


def replay_r35(recorded_coverage: dict) -> dict:
    artifact = load(R35_RESULT)
    r35 = r35_search.load_r35()
    graph = core.CutGraph(
        "R35_N24", r35.N, frozenset(r35.BLUE), frozenset(r35.BAD)
    )
    optimum_replay = r35_search.solve_choice(r35, workers=16)
    choice = tuple(artifact["trials"][0]["choice"])
    rows = tuple(
        r35.ROW_FAMILIES[atom][item] for atom, item in enumerate(choice)
    )
    analysis = official.analyze_tuple(graph, rows)
    checks = {
        "canonicalPayloadSha256": canonical_ok(artifact),
        "sourceSha256": all(
            file_sha(ROOT / name) == expected
            if "/" in name
            else file_sha(HERE / name) == expected
            for name, expected in artifact["sourceSha256"].items()
        ),
        "cpSatOptimal": optimum_replay["status"] == artifact["optimization"]["status"] == "OPTIMAL",
        "minimumCollisionUnits": optimum_replay["collisionUnits"]
        == artifact["optimization"]["minimumCollisionUnits"]
        == 82,
        "recordedChoiceIsMinimum": analysis["collisionUnits"] == 82,
        "recordedChoicePasses": analysis["verdict"] == "PASS",
        "recordedChoiceFlow": analysis["flow"]["maximumFlow"]
        == analysis["flow"]["totalDemand"]
        == 164,
        "coverageReference": recorded_coverage["canonicalHashValid"]
        and recorded_coverage["passingMinimumTupleFound"],
    }
    return {
        "checks": checks,
        "allChecksPass": all(checks.values()),
        "replayedOptimalChoice": list(optimum_replay["choice"]),
        "recordedPassingChoice": list(choice),
    }


def external_p4_replays() -> dict:
    n24_path = HERE / "n24_unscoped_p4_replay.json"
    n89_path = (
        ROOT
        / "tmp"
        / "fanout"
        / "r53_global_softcap_gate"
        / "n89_unscoped_p4_alternate.json"
    )
    if not n24_path.exists() or not n89_path.exists():
        return {"status": "SKIPPED_MISSING", "allChecksPass": False}
    n24 = load(n24_path)
    n89 = load(n89_path)
    diagnostics = n89["namedDiagnostics"]
    checks = {
        "n24LiteralAssignment": n24["defect"] == 0
        and n24["maximumFlow"] == n24["globalDemand"] == 312
        and all(n24["certificateChecks"].values()),
        "n89LiteralAssignment": diagnostics["n89_singleton_row_database"]["defect"]
        == 0
        and diagnostics["n89_singleton_row_database"]["maximumFlow"] == 776,
    }
    return {
        "status": "COMPLETE",
        "checks": checks,
        "allChecksPass": all(checks.values()),
        "n24FileSha256": file_sha(n24_path),
        "n89FileSha256": file_sha(n89_path),
    }


def coverage_shape(coverage: dict) -> dict:
    random_cases = coverage["randomCensusStress"]["cases"]
    blowup_cases = coverage["blowupStress"]["cases"]
    checks = {
        "canonicalPayloadSha256": canonical_ok(coverage),
        "sourceSha256": source_hashes_ok(coverage),
        "counterexampleFlagFalse": coverage["counterexampleFound"] is False,
        "randomCaseCount": len(random_cases) == 91,
        "randomAllPass": all(
            case["selectorVerdict"] == "PASS_SOME_MINIMUM_TUPLE"
            for case in random_cases
        ),
        "blowupCaseCount": len(blowup_cases) == 33,
        "blowupAllPass": all(
            case["selectorVerdict"] == "PASS_SOME_MINIMUM_TUPLE"
            for case in blowup_cases
        ),
        "fixedFailureDistinguished": sum(
            case["fixedTuple"]["verdict"] == "FAIL" for case in blowup_cases
        )
        == 19,
        "allStressRowProductsExhausted": all(
            case["rowProductExhaustive"] for case in random_cases + blowup_cases
        ),
    }
    return {"checks": checks, "allChecksPass": all(checks.values())}


def main() -> int:
    coverage = load(COVERAGE)
    fixture_records = {
        item["fixture"]: item for item in coverage["namedFixtures"]["fixtures"]
    }
    result = {
        "schema": "CDC_WAVE1_OFFICIAL_SELECTOR_REPLAY_V1",
        "N24": replay_fixture(core.n24_fixture(), fixture_records["N24"]),
        "N89": replay_fixture(core.n89_fixture(), fixture_records["N89"]),
        "R35": replay_r35(coverage["r35GlobalOptimization"]),
        "coverage": coverage_shape(coverage),
        "externalP4Replays": external_p4_replays(),
        "verifierSha256": file_sha(Path(__file__)),
    }
    result["allChecksPass"] = all(
        result[key]["allChecksPass"]
        for key in ("N24", "N89", "R35", "coverage", "externalP4Replays")
    )
    result["canonicalPayloadSha256"] = core.canonical_sha(result)
    helpers.write_json(OUTPUT, result)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0 if result["allChecksPass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
