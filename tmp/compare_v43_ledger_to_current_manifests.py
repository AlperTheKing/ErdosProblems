from __future__ import annotations

import json
from pathlib import Path


def manifest_key(path: Path) -> tuple[int, int, str] | None:
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
        return int(data["chart"]), int(data["dominant"]), str(data["band"])
    return None


def main() -> None:
    ledger = json.loads(Path("tmp/eq_odl1_rung2_chart_batch_ledger_v43.json").read_text(encoding="utf-8"))
    ledger_keys = {
        (int(row["chart"]), int(row["dominant"]), str(row["band"]))
        for row in ledger["certified_rows"]
    }
    manifest_paths = [
        *Path("tmp").glob("eq_odl1_rung2_source_certificate_manifest*.json"),
        *Path("tmp").glob("eq_odl1_rung2_repaired_certificate_manifest*.json"),
    ]
    manifest_keys: dict[tuple[int, int, str], list[str]] = {}
    for path in manifest_paths:
        key = manifest_key(path)
        if key is not None:
            manifest_keys.setdefault(key, []).append(str(path))

    payload = {
        "ledger_certified_count": ledger["certified_count"],
        "ledger_unique_keys": len(ledger_keys),
        "current_manifest_unique_keys": len(manifest_keys),
        "in_manifests_not_v43": [
            {"key": key, "paths": sorted(paths)}
            for key, paths in sorted(manifest_keys.items())
            if key not in ledger_keys
        ],
        "in_v43_not_manifests": sorted(key for key in ledger_keys if key not in manifest_keys),
        "duplicate_manifest_keys": [
            {"key": key, "count": len(paths), "paths": sorted(paths)}
            for key, paths in sorted(manifest_keys.items())
            if len(paths) > 1
        ],
    }
    out = Path("tmp/v43_vs_current_manifest_keydiff_codex_v1.json")
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
