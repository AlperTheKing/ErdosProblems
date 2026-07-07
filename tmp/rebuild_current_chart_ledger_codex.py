from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import sys

sys.path.append("problems/23/writeup")
import _codex_eq_odl1_rung2_batch_ledger as ledger


PREFERRED_SUBSTRINGS = (
    "codex_384prime",
    "codex_v1",
    "quick_codex",
    "patch",
    "repair",
)


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


def score(path: Path) -> tuple[int, float, str]:
    name = path.name
    preference = sum(1 for marker in PREFERRED_SUBSTRINGS if marker in name)
    return preference, path.stat().st_mtime, str(path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--pending-prefix", type=int, default=108)
    args = ap.parse_args()

    candidates = [
        *Path("tmp").glob("eq_odl1_rung2_source_certificate_manifest*.json"),
        *Path("tmp").glob("eq_odl1_rung2_repaired_certificate_manifest*.json"),
    ]
    by_key: dict[tuple[int, int, str], Path] = {}
    for path in candidates:
        key = manifest_key(path)
        if key is None:
            continue
        prev = by_key.get(key)
        if prev is None or score(path) > score(prev):
            by_key[key] = path

    ns = SimpleNamespace(
        numeric_map=Path("tmp/eq_odl1_rung2_support_numeric_map_full_sum_t60_w16_v1.json"),
        manifest=sorted(by_key.values(), key=str),
        pending_prefix=args.pending_prefix,
    )
    out = ledger.run(ns)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "out": str(args.out),
                "certified_count": out["certified_count"],
                "pending_count": out["pending_count"],
                "feasible_near_row_count": out["feasible_near_row_count"],
                "first_pending": out["pending_rows_prefix"][0]
                if out["pending_rows_prefix"]
                else None,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
