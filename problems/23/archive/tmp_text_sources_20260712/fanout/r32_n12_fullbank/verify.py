"""Independent consistency verifier for the no-common collision artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def load_checked(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="ascii"))
    expected = value.pop("canonicalPayloadSha256", None)
    if expected is not None:
        actual = canonical_sha(value)
        if actual != expected:
            raise AssertionError((path.name, actual, expected))
        value["canonicalPayloadSha256"] = expected
    return value


def main() -> int:
    aggregate_path = HERE / "census_n5_n12_aggregate.json"
    aggregate = load_checked(aggregate_path)
    checks = {}

    checks["aggregateNoCommon"] = aggregate["commonBlue"] is False
    checks["aggregateRelation"] = aggregate["relation"] == [
        "P1_sameFirst",
        "P3_rowCompanion",
        "strictP4",
        "P5",
    ]
    checks["aggregateCollisionOnly"] = (
        aggregate["hallDemand"] == "active-scoped collision halves only"
    )
    counts = aggregate["counts"]
    checks["coverage"] = (
        counts["testedGraphs"] == 992_618
        and counts["examinedTuples"] == 40_228_399
        and counts["positiveCollisionTuples"] == 1_649_719
    )
    checks["tupleFailuresExact"] = counts["collisionFailingTuples"] == 297
    checks["minimizersAllPass"] = (
        counts["defectMinimizerGraphs"] == 992_618
        and counts["defectMinimizerPassingGraphs"] == 992_618
        and counts["defectMinimizerFailingGraphs"] == 0
        and aggregate["histograms"]["defectMinimumHistogram"] == {"0": 992_618}
    )
    checks["noAllTupleGraphFalsifier"] = (
        counts["allTupleFailingGraphs"] == 0
        and aggregate["first"]["firstAllTupleFalsifier"] is None
    )
    checks["allTupleUniversalFalse"] = (
        counts["someTupleFailingGraphs"] == 29
        and aggregate["first"]["firstTupleFalsifier"] is not None
    )

    inputs_ok = True
    for filename, expected_hash in aggregate["inputFileSha256"].items():
        path = HERE / filename
        inputs_ok &= sha256(path) == expected_hash
        payload = load_checked(path)
        inputs_ok &= payload["commonBlue"] is False
        inputs_ok &= payload["total"]["first"][
            "firstDefectMinimizerFalsifier"
        ] is None
    checks["inputFilesPinned"] = inputs_ok

    fixture = load_checked(HERE / "fixture_no_common.json")
    checks["fixture78"] = (
        fixture["checks"]["collisionPaid28"]
        and fixture["checks"]["doorsPaid50"]
        and fixture["checks"]["noCommonNeeded"]
        and fixture["accounting"]["hallDemandIncludesHitNeed"] is False
        and fixture["accounting"]["combinedMatchedDiagnostic"] == 78
    )

    battery = json.loads(
        (HERE / "fixture_battery_result.json").read_text(encoding="ascii")
    )
    checks["batteryNoCommon"] = (
        battery["common_blue"] is False
        and battery["relation"]
        == ["P1_sameFirst", "P3_rowCompanion", "strictP4", "P5"]
    )
    checks["batteryAllPass"] = all(
        item["checked_certificate"]["full"] for item in battery["fixtures"]
    ) and len(battery["fixtures"]) == 9
    owner_ledger_ok = True
    for item in battery["fixtures"]:
        owner_ledger_ok &= item["common_blue"] is False
        owner_ledger_ok &= item["hall_demand"] == "collision only"
        for owner_record in item["owner_records"].values():
            owner_ledger_ok &= owner_record["demand"] == owner_record["collision"]
            owner_ledger_ok &= "P2_commonBad_new" not in owner_record[
                "pattern_additions_raw"
            ]
    checks["batteryOwnerLedgers"] = owner_ledger_ok
    r29 = next(
        item
        for item in battery["fixtures"]
        if item["fixture"] == "2943" and item["scope"] == "active"
    )
    hub = r29["special_2943"]["hub_shores"]
    checks["r29Exact"] = (
        r29["checked_certificate"]["total_demand"] == 23_108
        and r29["checked_certificate"]["max_flow"] == 23_108
        and hub["old"] == {
            "mask": 7,
            "owners": [0, 1, 2],
            "demand": 19_950,
            "reach": 19_925,
            "slack": -25,
        }
        and hub["certificate"] == {
            "mask": 7,
            "owners": [0, 1, 2],
            "demand": 19_950,
            "reach": 19_953,
            "slack": 3,
        }
    )

    replay = load_checked(HERE / "first_tuple_falsifier_n10.json")
    checks["tupleReplay"] = (
        replay["verdict"] == "EXACT_TUPLE_FALSIFIER_BUT_GRAPH_MINIMUM_ZERO"
        and replay["failingTuple"]["analysis"]["collisionDefect"] == 2
        and replay["failingTuple"]["analysis"]["hallWitness"]
        == {"owners": [4, 6, 8], "demand": 32, "reach": 30}
        and replay["defectMinimum"]["defect"] == 0
    )

    if not all(checks.values()):
        raise AssertionError([key for key, value in checks.items() if not value])
    payload = {
        "schema": "R32_NO_COMMON_COLLISION_VERIFICATION_V1",
        "verdict": "PASS",
        "checks": checks,
        "sha256": {
            "aggregate": sha256(aggregate_path),
            "fixture": sha256(HERE / "fixture_no_common.json"),
            "fixtureBattery": sha256(HERE / "fixture_battery_result.json"),
            "tupleReplay": sha256(HERE / "first_tuple_falsifier_n10.json"),
            "verifier": sha256(Path(__file__)),
        },
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    output = HERE / "verification.json"
    output.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii"
    )
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

