from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


DOM = {
    "F1": 0,
    "F2": 1,
    "F3": 2,
    "F4": 3,
    "F5": 4,
    "F6": 5,
    "F7": 6,
    "B0": 7,
    "G1": 8,
    "G2": 9,
    "G3": 10,
    "G4": 11,
    "G5": 12,
    "G6": 13,
    "G7": 14,
}


def key_from_name(name: str) -> tuple[int, int] | None:
    match = re.search(r"_k(\d+)_([A-Z]\d|B0|G\d)_", name)
    if not match:
        return None
    chart = int(match.group(1))
    dominant_name = match.group(2)
    dominant = DOM.get(dominant_name)
    if dominant is None:
        return None
    return chart, dominant


def exact_check(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    return (
        data.get("exact_ok") is True
        and int(data.get("full_negative_residual_count", -1)) == 0
        and int(data.get("solution_negative_count", -1)) == 0
        and str(data.get("full_min_residual")) == "0"
    )


def exact_manifest(path: Path) -> tuple[int, int] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if (
        data.get("exact_ok") is True
        and int(data.get("full_negative_residual_count", -1)) == 0
        and int(data.get("solution_negative_count", -1)) == 0
        and str(data.get("full_min_residual")) == "0"
    ):
        return int(data["chart"]), int(data["dominant"])
    return None


def main() -> None:
    manifest_keys = {
        key
        for path in Path("tmp").glob("eq_odl1_rung2_*certificate_manifest*.json")
        if (key := exact_manifest(path)) is not None
    }
    checks_by_key: dict[tuple[int, int], list[str]] = defaultdict(list)
    for path in Path("tmp").glob("eq_odl1_rung2_source_solution_check_k*_*.json"):
        key = key_from_name(path.name)
        if key is None:
            continue
        try:
            ok = exact_check(path)
        except Exception:
            continue
        if ok:
            checks_by_key[key].append(str(path))

    missing = {
        key: sorted(paths)
        for key, paths in checks_by_key.items()
        if key not in manifest_keys
    }
    payload = {
        "exact_manifest_keys": len(manifest_keys),
        "exact_check_keys": len(checks_by_key),
        "exact_check_keys_without_manifest": len(missing),
        "missing": [
            {"key": key, "checks": paths[-5:]}
            for key, paths in sorted(missing.items())
        ],
    }
    out = Path("tmp/exact_source_checks_without_manifest_codex_v1.json")
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
