"""Aggregate the four disjoint no-common collision census runs."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

from collision_census import COUNT_KEYS, FIRST_KEYS, HIST_KEYS
from fullbank_core import canonical_sha


HERE = Path(__file__).resolve().parent
INPUTS = (
    HERE / "smoke_n5_n8.json",
    HERE / "census_n9_n10.json",
    HERE / "census_n11.json",
    HERE / "census_n12.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_key(record: dict) -> tuple[int, int, int]:
    return record["order"], record["graphOrdinal"], record["tupleIndex"]


def main() -> int:
    counts = Counter()
    hist = {key: Counter() for key in HIST_KEYS}
    first = {key: None for key in FIRST_KEYS}
    status_by_order = {}
    stream_hashes = {}
    input_payload_hashes = {}
    input_file_hashes = {}
    for path in INPUTS:
        payload = json.loads(path.read_text(encoding="ascii"))
        if payload["commonBlue"] or payload["hallDemand"] != "active-scoped collision halves only":
            raise AssertionError(path)
        total = payload["total"]
        counts.update(total["counts"])
        for key in HIST_KEYS:
            hist[key].update(
                {int(value): count for value, count in total["histograms"][key].items()}
            )
        for key in FIRST_KEYS:
            candidate = total["first"][key]
            current = first[key]
            if candidate is not None and (
                current is None or record_key(candidate) < record_key(current)
            ):
                first[key] = candidate
        overlap = set(status_by_order).intersection(payload["statusByOrder"])
        if overlap:
            raise AssertionError((path, overlap))
        status_by_order.update(payload["statusByOrder"])
        stream_hashes.update(payload["graphStreamSha256"])
        input_payload_hashes[path.name] = payload["canonicalPayloadSha256"]
        input_file_hashes[path.name] = sha256(path)

    expected = {
        "testedGraphs": 992_618,
        "examinedTuples": 40_228_399,
        "positiveCollisionTuples": 1_649_719,
        "collisionFailingTuples": 297,
        "defectMinimizerFailingGraphs": 0,
        "allTupleFailingGraphs": 0,
        "someTupleFailingGraphs": 29,
    }
    actual = {key: counts[key] for key in expected}
    if actual != expected:
        raise AssertionError((actual, expected))
    if hist["defectMinimumHistogram"] != Counter({0: 992_618}):
        raise AssertionError(hist["defectMinimumHistogram"])
    if first["firstDefectMinimizerFalsifier"] is not None:
        raise AssertionError("unexpected minimizer falsifier")
    if first["firstAllTupleFalsifier"] is not None:
        raise AssertionError("unexpected all-tuple graph falsifier")

    payload = {
        "schema": "R32_NO_COMMON_COLLISION_CENSUS_AGGREGATE_V1",
        "relation": ["P1_sameFirst", "P3_rowCompanion", "strictP4", "P5"],
        "commonBlue": False,
        "hallDemand": "active-scoped collision halves only",
        "hitNeed": "excluded; recorded separately as bank-funded metadata",
        "integerOnly": True,
        "orders": [5, 12],
        "workersMaximum": 20,
        "counts": {key: counts[key] for key in COUNT_KEYS},
        "histograms": {
            key: {str(value): count for value, count in sorted(hist[key].items())}
            for key in HIST_KEYS
        },
        "first": first,
        "statusByOrder": {
            key: status_by_order[key] for key in sorted(status_by_order, key=int)
        },
        "graphStreamSha256": {
            key: stream_hashes[key] for key in sorted(stream_hashes, key=int)
        },
        "inputCanonicalPayloadSha256": input_payload_hashes,
        "inputFileSha256": input_file_hashes,
        "sha256": {
            "aggregateScript": sha256(Path(__file__)),
            "collisionCore": sha256(HERE / "collision_only_core.py"),
            "censusDriver": sha256(HERE / "collision_census.py"),
            "fullbankCore": sha256(HERE / "fullbank_core.py"),
        },
        "verdict": (
            "NO_COMMON_NOT_ALL_TUPLES; ALL_992618_DEFECT_MINIMA_PASS"
        ),
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    output = HERE / "census_n5_n12_aggregate.json"
    output.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii"
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "graphs": counts["testedGraphs"],
                "tuples": counts["examinedTuples"],
                "tupleFailures": counts["collisionFailingTuples"],
                "minimizerFailures": counts["defectMinimizerFailingGraphs"],
                "allTupleFailingGraphs": counts["allTupleFailingGraphs"],
                "canonicalPayloadSha256": payload["canonicalPayloadSha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

