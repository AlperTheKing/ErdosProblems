from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


def main() -> None:
    rows = []
    bad = []
    for path in Path("tmp").glob("eq_odl1_rung2_source_certificate_manifest_k*_*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - diagnostic script
            bad.append((str(path), repr(exc)))
            continue
        if (
            data.get("exact_ok") is True
            and int(data.get("full_negative_residual_count", -1)) == 0
            and int(data.get("solution_negative_count", -1)) == 0
            and str(data.get("full_min_residual")) == "0"
        ):
            rows.append(
                (
                    int(data["chart"]),
                    int(data["dominant"]),
                    str(path),
                    path.stat().st_mtime,
                )
            )

    by_key: dict[tuple[int, int], list[tuple[str, float]]] = defaultdict(list)
    for chart, dominant, path, mtime in rows:
        by_key[(chart, dominant)].append((path, mtime))

    payload = {
        "exact_source_manifests": len(rows),
        "bad_json": len(bad),
        "unique_keys": len(by_key),
        "dupe_keys": sum(1 for values in by_key.values() if len(values) > 1),
        "sample_dupes": [
            {
                "key": key,
                "count": len(values),
                "latest_paths": sorted(path for path, _ in values)[-3:],
            }
            for key, values in list(by_key.items())
            if len(values) > 1
        ][:10],
    }
    out = Path("tmp/exact_source_manifest_inventory_codex_v1.json")
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
