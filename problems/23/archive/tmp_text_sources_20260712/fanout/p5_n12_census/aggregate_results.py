"""Merge disjoint exact order censuses without re-running graph enumeration."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
INPUTS = (
    HERE / "census_all_n5_n10.json",
    HERE / "census_all_n11.json",
    HERE / "census_all_n12.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def record_key(record: dict) -> tuple[int, int, int]:
    return record["order"], record["graphOrdinal"], record["tupleIndex"]


def empty_from(sample: dict) -> dict:
    return {
        "counts": {key: 0 for key in sample["counts"]},
        "histograms": {key: {} for key in sample["histograms"]},
        "first": {key: None for key in sample["first"]},
    }


def merge_bucket(target: dict, source: dict) -> None:
    for key, value in source["counts"].items():
        target["counts"][key] += value
    for name, source_hist in source["histograms"].items():
        target_hist = target["histograms"][name]
        for key, value in source_hist.items():
            target_hist[key] = target_hist.get(key, 0) + value
    for name, candidate in source["first"].items():
        current = target["first"][name]
        if candidate is not None and (
            current is None or record_key(candidate) < record_key(current)
        ):
            target["first"][name] = candidate


def main() -> int:
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in INPUTS]
    for payload in payloads:
        assert payload["schema"] == "P5_N_LE_12_CENSUS_V1"
        assert payload["mode"] == "all" and payload["bandSelection"] == "all"
        counts = payload["total"]["counts"]
        assert counts["examinedTuples"] == counts["availableTuples"]
        assert counts["p5NegativeSwitches"] == 0
        assert counts["p5ReservedCandidates"] == 0

    source_hashes = payloads[0]["sourceSha256"]
    assert all(payload["sourceSha256"] == source_hashes for payload in payloads)
    order_sets = [set(payload["coverage"]["statusByOrder"]) for payload in payloads]
    assert not (order_sets[0] & order_sets[1] or order_sets[0] & order_sets[2] or order_sets[1] & order_sets[2])
    assert set().union(*order_sets) == {str(n) for n in range(5, 13)}

    total = empty_from(payloads[0]["total"])
    bands = {name: empty_from(payloads[0]["bands"][name]) for name in ("light", "medium", "heavy")}
    generated = {}
    streams = {}
    status = {}
    for payload in payloads:
        merge_bucket(total, payload["total"])
        for name in bands:
            merge_bucket(bands[name], payload["bands"][name])
        generated.update(payload["coverage"]["generatedByOrder"])
        streams.update(payload["coverage"]["graphStreamSha256ByOrder"])
        status.update(payload["coverage"]["statusByOrder"])

    counts = total["counts"]
    assert counts["examinedTuples"] == 40_228_399
    assert counts["microBeforeP5Failures"] == (
        counts["microRepairs"] + counts["microFiveFailures"]
    )
    assert counts["oneBeforeP5Failures"] == 0
    assert counts["oneFiveFailures"] == 0
    assert counts["representativeMicroFailures"] == 0
    assert counts["representativeZeroDemand"] == counts["representativeGraphs"]

    result = {
        "schema": "P5_N_LE_12_AGGREGATE_V1",
        "arithmetic": "Python integers only",
        "workersMaximum": max(payload["workers"] for payload in payloads),
        "mode": "all tuples plus exact global-minimum representative per graph",
        "representativeRule": payloads[0]["representativeRule"],
        "relation": payloads[0]["relation"],
        "coverage": {
            "orders": [5, 6, 7, 8, 9, 10, 11, 12],
            "generatedByOrder": dict(sorted(generated.items(), key=lambda item: int(item[0]))),
            "graphStreamSha256ByOrder": dict(sorted(streams.items(), key=lambda item: int(item[0]))),
            "statusByOrder": dict(sorted(status.items(), key=lambda item: int(item[0]))),
            "n12ExpectedValidated": payloads[-1]["coverage"]["n12ExpectedValidated"],
            "inputCanonicalPayloadSha256": {
                path.name: payload["canonicalPayloadSha256"]
                for path, payload in zip(INPUTS, payloads)
            },
            "inputFileSha256": {path.name: sha256(path) for path in INPUTS},
        },
        "bands": bands,
        "total": total,
        "sourceSha256": source_hashes,
        "aggregateScriptSha256": sha256(Path(__file__)),
    }
    result["canonicalPayloadSha256"] = canonical_sha(result)
    output = HERE / "census_all_n5_n12.json"
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "canonicalPayloadSha256": result["canonicalPayloadSha256"],
        "counts": counts,
        "firstMicroFalsifier": total["first"]["firstMicroFalsifier"],
        "firstOneFalsifier": total["first"]["firstOneFalsifier"],
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
