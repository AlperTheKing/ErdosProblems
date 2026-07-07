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
    dom = DOM.get(match.group(2))
    if dom is None:
        return None
    return int(match.group(1)), dom


def main() -> None:
    ledger = json.loads(Path("tmp/eq_odl1_rung2_chart_batch_ledger_v44_codex.json").read_text())
    pending = {
        (int(row["chart"]), int(row["dominant"])): row
        for row in ledger["pending_rows_prefix"]
    }
    patterns = {
        "check": "eq_odl1_rung2_source_solution_check_k*_*.json",
        "probe": "probe_k*_*.json",
        "support": "eq_odl1_rung2_support_lp_k*_*.json",
        "basis": "eq_odl1_rung2_basis_probe_k*_*.json",
        "manifest": "eq_odl1_rung2_source_certificate_manifest_k*_*.json",
    }
    counts: dict[tuple[int, int], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for typ, pattern in patterns.items():
        for path in Path("tmp").glob(pattern):
            key = key_from_name(path.name)
            if key in pending:
                counts[key][typ] += 1

    fresh = []
    for key, row in pending.items():
        c = counts[key]
        if not c["check"] and not c["probe"] and not c["support"] and not c["basis"]:
            fresh.append(
                {
                    "chart": row["chart"],
                    "dominant": row["dominant"],
                    "dominant_name": row["dominant_name"],
                    "float_nonzero": row.get("float_nonzero"),
                    "variables": row["variables"],
                    "numeric_order_key": [
                        row.get("float_nonzero") if row.get("float_nonzero") is not None else 10**9,
                        row["variables"],
                        row["chart"],
                        row["dominant"],
                    ],
                }
            )
    fresh.sort(key=lambda r: tuple(r["numeric_order_key"]))
    out = {
        "schema": "fresh_pending_rows_v1",
        "ledger": "tmp/eq_odl1_rung2_chart_batch_ledger_v44_codex.json",
        "fresh_count": len(fresh),
        "fresh": fresh,
    }
    out_path = Path("tmp/fresh_pending_rows_v44_codex.json")
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"fresh_count": len(fresh), "top": fresh[:10]}, sort_keys=True))


if __name__ == "__main__":
    main()
