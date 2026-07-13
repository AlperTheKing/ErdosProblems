#!/usr/bin/env python3
"""Exact P65 fold audit over every translation of the P20 ruler corpus."""

from __future__ import annotations

import importlib.util
import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "problems/864/compute/p20/results/samples.jsonl"
P45 = ROOT / "problems/864/compute/p45/audit_signed_carry_identity.py"
P57 = ROOT / "problems/864/compute/p57/scan_fold_repair_translations.py"
P65 = ROOT / "problems/864/compute/p65/search_hole_restricted_folds.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    p45 = load(P45, "p45_for_p65")
    p57 = load(P57, "p57_for_p65")
    p65 = load(P65, "p65_exact_audit")
    rulers: dict[tuple[int, ...], dict[str, object]] = {}
    with SOURCE.open(encoding="utf-8") as stream:
        for line in stream:
            source = json.loads(line)
            parameters = p45.reflected_parameters(source)
            if parameters is None:
                continue
            values, _, _ = parameters
            data = p57.ruler_data(tuple(values))
            rulers.setdefault(tuple(data["Z"]), data)

    started = time.perf_counter()
    total = 0
    failures = []
    rows = []
    by_p: dict[int, dict[str, object]] = {}
    for z, data in rulers.items():
        p = int(data["p"])
        width = int(data["width"])
        baseline = (3 * p * p - p + 2) // 2
        max_gamma = baseline - width - 2
        if max_gamma < 0:
            continue
        sum_bits = int(data["sum_bits"])
        difference_bits = int(data["difference_bits"])
        best = None
        admissible = 0
        for gamma in range(max_gamma + 1):
            h = gamma + width + 1
            c_s = (sum_bits & (sum_bits >> h)).bit_count()
            for b in (1, 2):
                gap = 2 * gamma + b
                if difference_bits & (sum_bits << gap):
                    continue
                total += 1
                admissible += 1
                row = {
                    "p": p, "width": width, "gamma": gamma,
                    "h": h, "b": b, "delta": baseline - h,
                    "C_S": c_s, "bound": 2 * p - 3,
                    "excess": c_s - (2 * p - 3), "Z": list(z),
                }
                rank = (row["excess"], c_s, -h, -b)
                if best is None or rank > best[0]:
                    best = (rank, row)
                prior = by_p.get(p)
                if prior is None or rank > (
                    prior["excess"], prior["C_S"], -prior["h"], -prior["b"]
                ):
                    by_p[p] = row
                if row["excess"] > 0:
                    exact = p65.fold_rows(z, gamma, b)
                    if not exact["hole"] or exact["delta"] <= 0:
                        raise AssertionError((row, exact))
                    failures.append(exact)
        rows.append({
            "p": p, "width": width, "admissible_translations": admissible,
            "best": None if best is None else best[1],
        })

    top = sorted(
        (r["best"] for r in rows if r["best"] is not None),
        key=lambda r: (r["excess"], r["C_S"], -r["p"], -r["h"]),
        reverse=True,
    )[:20]
    output = {
        "schema_version": 1, "arithmetic": "exact integers",
        "domain": "all positive-defect translations of 133 distinct P20 rulers",
        "source_rulers": len(rulers), "admissible_translations": total,
        "failure_count": len(failures), "failures": failures,
        "top_twenty": top,
        "best_by_p": {str(p): by_p[p] for p in sorted(by_p)},
        "reports": rows, "elapsed_seconds": time.perf_counter() - started,
    }
    out = ROOT / "problems/864/compute/p65/p20_hole_fold_audit.json"
    out.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps({
        "source_rulers": len(rulers), "admissible_translations": total,
        "failure_count": len(failures), "best": top[0],
        "elapsed_seconds": output["elapsed_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
