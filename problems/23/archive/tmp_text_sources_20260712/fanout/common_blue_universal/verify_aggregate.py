"""Strict aggregate verifier for the CommonBlue universal exact fanout."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANE_RE = re.compile(r"lane\d\d_[a-z0-9_]+$")
SHA_RE = re.compile(r"^([0-9a-fA-F]{64})\s+[* ]?(.+?)\s*$")
EXPECTED_LANES = (
    "lane01_n6_n10", "lane02_n11", "lane03_n12",
    "lane04_fixtures_small", "lane05_fixtures_mid",
    "lane06_fixtures_large", "lane07_base_obstructions",
    "lane08_adversarial_cage", "lane09_referee",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reject_floats(value, where: str = "$") -> None:
    if isinstance(value, float):
        raise AssertionError(f"floating value at {where}: {value!r}")
    if isinstance(value, dict):
        for key, item in value.items():
            reject_floats(item, f"{where}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            reject_floats(item, f"{where}[{index}]")


def verify_manifest(lane: Path) -> dict:
    manifest = lane / "MANIFEST.sha256"
    if not manifest.is_file():
        raise AssertionError(f"missing {manifest.relative_to(HERE)}")
    checked = []
    for line_no, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        match = SHA_RE.fullmatch(line)
        if match is None:
            raise AssertionError(f"malformed {manifest.name}:{line_no}")
        expected, relative = match.groups()
        target = (lane / relative).resolve()
        target.relative_to(lane.resolve())
        if target == manifest.resolve():
            raise AssertionError("manifest must not hash itself")
        if not target.is_file():
            raise AssertionError(f"missing manifest target {target}")
        actual = sha256(target)
        if actual.lower() != expected.lower():
            raise AssertionError(f"SHA mismatch for {target}: {actual} != {expected}")
        checked.append({"path": target.relative_to(lane).as_posix(), "sha256": actual})
    if not checked:
        raise AssertionError(f"empty {manifest}")
    return {"sha256": sha256(manifest), "checked": checked}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-incomplete", action="store_true")
    parser.add_argument("--output", type=Path, default=HERE / "aggregate.json")
    args = parser.parse_args()

    lanes = [HERE / name for name in EXPECTED_LANES]
    assert all(path.is_dir() and LANE_RE.fullmatch(path.name) for path in lanes)
    aggregate = {"schema": "COMMON_BLUE_MICRO_UNIVERSAL_AGGREGATE_V2", "lanes": [], "errors": []}
    for lane in lanes:
        try:
            report = lane / "REPORT.md"
            result_path = lane / "result.json"
            final = lane / "final.md"
            for required in (report, result_path, final):
                if not required.is_file():
                    raise AssertionError(f"missing {required.relative_to(HERE)}")
            result = json.loads(result_path.read_text(encoding="utf-8"))
            reject_floats(result)
            manifest = verify_manifest(lane)
            aggregate["lanes"].append({
                "lane": lane.name,
                "resultSha256": sha256(result_path),
                "reportSha256": sha256(report),
                "finalSha256": sha256(final),
                "manifest": manifest,
                "result": result,
            })
        except Exception as exc:
            aggregate["errors"].append({"lane": lane.name, "error": str(exc)})
    aggregate["complete"] = len(aggregate["lanes"]) == 9 and not aggregate["errors"]
    if aggregate["errors"] and not args.allow_incomplete:
        print(json.dumps(aggregate, sort_keys=True, separators=(",", ":")))
        raise SystemExit(1)
    args.output.write_text(json.dumps(aggregate, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "complete": aggregate["complete"],
        "verifiedLanes": len(aggregate["lanes"]),
        "errors": aggregate["errors"],
        "aggregateSha256": sha256(args.output),
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
