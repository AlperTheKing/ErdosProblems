#!/usr/bin/env python3
"""Independent recursive audit of the C109 global fixed-root scans."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import C109_fixed_root_search as exact


def require(condition: bool, message: object) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def audit_record(row: dict[str, object], root: int) -> dict[str, object]:
    h = int(row["h"])
    expected_d = int(row["d"])
    factors = tuple(
        (int(p), int(exponent)) for p, exponent in row["h_plus_1_factorization"]
    )
    require(exact.factor_tuple(h + 1) == factors, ("factorization", h))
    candidate = exact.classify_candidate(h + 1, factors, root)
    require(candidate.hard, ("not-hard", h))
    require(candidate.fixed_root_witness, ("not-witnessed", h, root))
    require(len(candidate.pairs) == expected_d, ("pair-count", h, len(candidate.pairs)))
    endpoints = sorted(
        {
            endpoint
            for pair in candidate.pairs
            for endpoint in pair
            if not exact.generated(endpoint) and exact.seed_root(endpoint) == root
        }
    )
    require(endpoints == row["witness_endpoints"], ("endpoints", h, endpoints))
    require(
        all(not (exact.generated(a) and exact.generated(b)) for a, b in candidate.pairs),
        ("unblocked-pair", h),
    )
    return {"root": root, "h": h, "d": expected_d, "witness_endpoints": endpoints}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records-1e8", type=Path, required=True)
    parser.add_argument("--records-4e9", type=Path, required=True)
    parser.add_argument("--bin-1e8", type=Path, required=True)
    parser.add_argument("--bin-4e9", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    records_1e8 = json.loads(args.records_1e8.read_text(encoding="ascii"))
    records_4e9 = json.loads(args.records_4e9.read_text(encoding="ascii"))
    bin_1e8 = json.loads(args.bin_1e8.read_text(encoding="ascii"))
    bin_4e9 = json.loads(args.bin_4e9.read_text(encoding="ascii"))

    require(records_1e8["limit"] == 100_000_000, "record 1e8 limit")
    require(records_4e9["limit"] == 4_000_000_000, "record 4e9 limit")
    require(records_1e8["hard_count"] == 3_368_726, "record 1e8 hard count")
    require(records_4e9["hard_count"] == 106_360_959, "record 4e9 hard count")
    require(bin_1e8["hard_count_scanned"] == 3_368_726, "bin 1e8 hard count")
    require(bin_4e9["hard_count_scanned"] == 106_360_959, "bin 4e9 hard count")
    require(bin_1e8["classification_digest"] == "94633c57cc653c6e", "C104 digest")
    require(bin_4e9["classification_digest"] == "08eb5810482ec820", "C105 digest")
    for result in (bin_1e8, bin_4e9):
        require(result["first_failure_source_h"] is None, "unexpected C104-BIN failure")
        require(result["failures_at_first_source"] == [], "unexpected failure rows")

    require(not exact.generated(107), "107 generated")
    require(not exact.generated(213), "213 generated")
    require(not exact.generated(425), "425 generated")
    require(exact.generated(849), "849 missing")
    require(not exact.generated(123), "123 generated")
    require(not exact.generated(245), "245 generated")
    require(exact.generated(489), "489 missing")

    audited = []
    expected_maxima = {54: 16, 62: 16}
    expected_first_16 = {54: 1_559_219_514, 62: 298_274_514}
    for root_row in records_4e9["roots"]:
        root = int(root_row["root"])
        require(root_row["maximum_d"] == expected_maxima[root], ("maximum", root))
        d16 = [row for row in root_row["records"] if row["d"] == 16]
        require(len(d16) == 1 and d16[0]["h"] == expected_first_16[root], ("first-16", root))
        audited.extend(audit_record(row, root) for row in root_row["records"])

    for short_root, long_root in zip(records_1e8["roots"], records_4e9["roots"], strict=True):
        prefix = long_root["records"][: len(short_root["records"])]
        require(short_root["records"] == prefix, ("record-prefix", short_root["root"]))

    payload = {
        "schema": "C109-fixed-root-independent-audit-v1",
        "exact_recursive_records_audited": len(audited),
        "audited_records": audited,
        "chain_checks": {
            "root_54_missing_then_generated": [107, 213, 425, 849],
            "root_62_missing_then_generated": [123, 245, 489],
        },
        "global_cross_checks": {
            "C104_1e8_classification_digest_match": True,
            "C105_4e9_classification_digest_match": True,
            "C105_4e9_hard_count_match": True,
            "C104_BIN_no_failure_through_4e9": True,
        },
        "input_sha256": {
            args.records_1e8.name: sha256(args.records_1e8),
            args.records_4e9.name: sha256(args.records_4e9),
            args.bin_1e8.name: sha256(args.bin_1e8),
            args.bin_4e9.name: sha256(args.bin_4e9),
        },
        "oracle_cache": {
            "generated": exact.generated.cache_info()._asdict(),
            "factorizations": exact.factor_tuple.cache_info()._asdict(),
        },
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(
        f"audited={len(audited)} root54_max=16 root62_max=16 "
        "C104_BIN_failure_through_4e9=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
