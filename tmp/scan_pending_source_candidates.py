from __future__ import annotations

import json
import re
from pathlib import Path


DOM = {
    0: "F1",
    1: "F2",
    2: "F3",
    3: "F4",
    4: "F5",
    5: "F6",
    6: "F7",
    7: "B0",
    8: "G1",
    9: "G2",
    10: "G3",
    11: "G4",
    12: "G5",
    13: "G6",
    14: "G7",
}


def main() -> None:
    ledger = json.loads(Path("tmp/eq_odl1_rung2_chart_batch_ledger_v43.json").read_text())
    pending = ledger.get("pending_rows_prefix", [])
    pending_keys = {(int(r["chart"]), int(r["dominant"])) for r in pending}

    source_files = list(Path("tmp").glob("eq_odl1_rung2_source_solution_k*_*.jsonl"))
    check_files = list(Path("tmp").glob("eq_odl1_rung2_source_solution_check_k*_*.json"))
    manifest_files = list(Path("tmp").glob("eq_odl1_rung2_source_certificate_manifest_k*_*.json"))

    def key_of(path: Path) -> tuple[int, int] | None:
        name = path.name
        m = re.search(r"_k(\d+)_([A-Z]\d|B0|G\d)_", name)
        if not m:
            return None
        k = int(m.group(1))
        dom_name = m.group(2)
        for idx, short in DOM.items():
            if short == dom_name:
                return (k, idx)
        return None

    by_key: dict[tuple[int, int], dict[str, list[str]]] = {}
    for category, files in [
        ("source_solution", source_files),
        ("check_summary", check_files),
        ("manifest", manifest_files),
    ]:
        for p in files:
            key = key_of(p)
            if key is None or key not in pending_keys:
                continue
            by_key.setdefault(key, {}).setdefault(category, []).append(str(p))

    rows = []
    for r in pending:
        key = (int(r["chart"]), int(r["dominant"]))
        info = by_key.get(key, {})
        checks = []
        for p in info.get("check_summary", []):
            try:
                d = json.loads(Path(p).read_text())
                checks.append({
                    "path": p,
                    "exact_ok": d.get("exact_ok"),
                    "full_negative_residual_count": d.get("full_negative_residual_count"),
                    "full_min_residual": d.get("full_min_residual"),
                    "solution_negative_count": d.get("solution_negative_count"),
                })
            except Exception as exc:
                checks.append({"path": p, "error": repr(exc)})
        rows.append({
            "chart": key[0],
            "dominant": key[1],
            "dominant_name": r.get("dominant_name"),
            "source_solution_count": len(info.get("source_solution", [])),
            "check_summary_count": len(info.get("check_summary", [])),
            "manifest_count": len(info.get("manifest", [])),
            "source_solutions": sorted(info.get("source_solution", []))[-8:],
            "checks": checks[-8:],
        })

    out = {
        "schema": "pending_source_candidate_scan_v1",
        "ledger": "tmp/eq_odl1_rung2_chart_batch_ledger_v43.json",
        "pending_count": len(pending),
        "pending_with_source_solution": sum(1 for r in rows if r["source_solution_count"]),
        "pending_with_check_summary": sum(1 for r in rows if r["check_summary_count"]),
        "pending_with_manifest": sum(1 for r in rows if r["manifest_count"]),
        "rows": rows,
    }
    out_path = Path("tmp/pending_source_candidate_scan_v1.json")
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "pending_count": out["pending_count"],
        "with_source_solution": out["pending_with_source_solution"],
        "with_check_summary": out["pending_with_check_summary"],
        "with_manifest": out["pending_with_manifest"],
        "out": str(out_path),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
