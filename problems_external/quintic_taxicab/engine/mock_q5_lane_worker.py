#!/usr/bin/env python3
"""Tiny contract worker used only by supervisor calibration tests.

Campaign-id suffixes select synthetic behavior: ``-stderr-at-exit`` emits stderr,
``-digest-mismatch`` corrupts the echoed manifest digest, ``-invalid-hit``
emits a rejected candidate and exits with the native HIT code 10,
``-semantic-timeout`` emits TIMEOUT_INCOMPLETE and exits with the native code
3, ``-unexpected-exit`` returns 7 after a valid NO_HIT result, and
``-exit-status-mismatch`` returns 10 after a valid NO_HIT result. ``-sleep``
waits past a short test deadline. All other campaigns return a complete finite
NO_HIT without doing mathematical search.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

import q5_manifest as manifest_lib


class MockError(ValueError):
    pass


def parse_lane(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if b"\r" in data or not data.endswith(b"\n") or data.startswith(b"\xef\xbb\xbf"):
        raise MockError("lane file is not strict LF ASCII")
    expected_hash = os.environ.get("Q5_LANE_FILE_SHA256", "")
    if manifest_lib.sha256_bytes(data) != expected_hash:
        raise MockError("lane file SHA mismatch")
    lines = data.decode("ascii").splitlines()
    if len(lines) < 13 or lines[0] != "Q5_TORSOR_LANE_V1":
        raise MockError("lane file schema mismatch")
    keys = [
        "campaign_id", "deadline", "search_mode", "lane_id", "lane_count",
        "P", "Q", "N", "D", "assignment_sha256", "count",
    ]
    metadata: dict[str, str] = {}
    for line, expected_key in zip(lines[1:12], keys):
        parts = line.split("\t")
        if len(parts) != 2 or parts[0] != expected_key:
            raise MockError(f"expected TSV metadata {expected_key}")
        metadata[expected_key] = parts[1]
    if lines[12] != "p\tq\testimated_work":
        raise MockError("lane row header mismatch")
    rows: list[dict[str, int]] = []
    for line in lines[13:]:
        parts = line.split("\t")
        if len(parts) != 3:
            raise MockError("malformed lane row")
        rows.append(
            {"p": int(parts[0]), "q": int(parts[1]), "estimated_work": int(parts[2])}
        )
    if int(metadata["count"]) != len(rows):
        raise MockError("lane count mismatch")
    if manifest_lib.assignment_digest(rows) != metadata["assignment_sha256"]:
        raise MockError("assignment digest mismatch")
    if int(metadata["lane_count"]) != 64:
        raise MockError("lane_count must be 64")
    if metadata["deadline"] != os.environ.get("Q5_DEADLINE_UTC"):
        raise MockError("deadline environment mismatch")
    if datetime.now(timezone.utc) >= manifest_lib.parse_deadline(metadata["deadline"]):
        raise MockError("deadline expired")
    return {"metadata": metadata, "rows": rows}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--lane-file", type=Path, required=True)
    result.add_argument("--lane-id", type=int, required=True)
    result.add_argument("--threads", type=int, required=True)
    result.add_argument("--result", type=Path, required=True)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.threads != 1:
        print("mock requires one thread", file=sys.stderr)
        return 2
    try:
        lane = parse_lane(args.lane_file)
        metadata = lane["metadata"]
        if args.lane_id != int(metadata["lane_id"]):
            raise MockError("lane id CLI mismatch")
        campaign = metadata["campaign_id"]
        if campaign.endswith("-sleep"):
            time.sleep(60)
        digest = os.environ.get("Q5_MANIFEST_PAYLOAD_SHA256", "")
        if campaign.endswith("-digest-mismatch"):
            digest = "0" * 64
        if campaign.endswith("-invalid-hit"):
            status = "HIT"
        elif campaign.endswith("-semantic-timeout"):
            status = "TIMEOUT_INCOMPLETE"
        else:
            status = "NO_HIT"
        candidates = (
            [{
                "source_p": 1,
                "source_q": 1,
                "source_u_numerator": "0",
                "source_u_denominator": 1,
                "Y": "0",
                "Z": "0",
                "v": "0",
                "rational_quadruple": ["1/2", "1/2", "1", "1"],
                "integer_quadruple": ["1", "1", "2", "2"],
                "h": "2",
                "exact_verification": True,
            }]
            if status == "HIT"
            else []
        )
        hit_count = "1" if status == "HIT" else "0"
        counts = {key: "0" for key in (
            "reduced_t_values", "reduced_u_values", "pairs_considered", "admissible_specializations",
            "zero_u_tested", "radicand_squares", "y_signs_tested", "nonnegative_z",
            "z_squares", "bounded_z_squares", "repeated_entry_rejections",
            "candidate_records", "verified_integer_certificates",
        )}
        counts["reduced_t_values"] = str(len(lane["rows"]))
        for key in ("pairs_considered", "admissible_specializations", "bounded_z_squares", "candidate_records", "verified_integer_certificates"):
            counts[key] = hit_count
        report = {
            "lane_file_sha256": os.environ.get("Q5_LANE_FILE_SHA256", ""),
            "schema_version": 1,
            "kind": "Q5_TORSOR_LANE_RESULT",
            "campaign_id": campaign,
            "signed_u_symmetry_pruned": False,
            "negative_y_pruned": False,
            "zero_u_pruned": False,
            "emit_torsor_points": False,
            "elapsed_milliseconds": "0",
            "manifest_payload_sha256": digest,
            "search_mode": metadata["search_mode"],
            "lane_id": args.lane_id,
            "zero_z_rejected_as_nontarget": True,
            "complete": status == "NO_HIT",
            "assignment_sha256": metadata["assignment_sha256"],
            "status": status,
            "assigned_specializations": len(lane["rows"]),
            "completed_specializations": (
                len(lane["rows"])
                if status != "TIMEOUT_INCOMPLETE"
                else max(0, len(lane["rows"]) - 1)
            ),
            "counts": counts,
            "candidates": candidates,
        }
        manifest_lib.atomic_write_json(args.result, report)
        if campaign.endswith("-stderr") or campaign.endswith("-stderr-at-exit"):
            print("synthetic stderr", file=sys.stderr, flush=True)
        if campaign.endswith("-unexpected-exit"):
            return 7
        if campaign.endswith("-exit-status-mismatch"):
            return 10
        if status == "HIT":
            return 10
        if status == "TIMEOUT_INCOMPLETE":
            return 3
        return 0
    except (OSError, UnicodeError, ValueError, manifest_lib.ManifestError) as exc:
        print(f"mock FAIL_CLOSED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
