#!/usr/bin/env python3
"""Audit corrected residual-interval matching on unrestricted exact rows."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p46 = load("p46_residual_audit", ROOT / "problems/864/compute/p46/carry_statistics.py")
p93 = load("p93_residual_audit", ROOT / "problems/864/compute/p93/audit_triangle_components.py")
p97 = load("p97_residual_audit", ROOT / "problems/864/compute/p97/audit_phase_interval_matching_w30.py")
p88 = load("p88_residual_audit", ROOT / "problems/864/compute/p88/verify_c84_order_counterexample.py")


def row_ok(values, h, b):
    folds, triangles = p93.fold_triangle_system(values, h)
    if not triangles:
        return True, len(folds), 0, 0
    differences = {right - left for left in values for right in values if left < right}
    shared = [(a, c, u) for a, c, u, _v in folds]
    for base, au, cu in triangles:
        a, c, _r, _s = folds[base]
        u = folds[au][2]
        assert folds[cu][2] == u
        shared.append((a, c, u))
    intervals = []
    for a, c, u in shared:
        tau, lam = u - a - c - b, h - b - u
        intervals.append((min(tau, lam), max(tau, lam)))
    slots = []
    bad = 0
    for a, c, u, v in folds:
        slots.extend((h - b - v, h - b - u))
        if a + c + b in differences:
            slots.append(h - b - v)
            bad += 1
    return p97.greedy_match(intervals, slots) == len(intervals), len(folds), len(triangles), bad


def width_scan():
    rows = triangle_rows = failures = 0
    first = None
    for width in range(1, 31):
        for ruler in p46.sidon_rulers(width):
            z = tuple(sorted(width - x for x in ruler))
            for gamma in range(width):
                values = tuple(gamma + x for x in z)
                h = gamma + width + 1
                for b in (1, 2):
                    rows += 1
                    ok, folds, triangles, bad = row_ok(values, h, b)
                    triangle_rows += triangles > 0
                    if not ok:
                        failures += 1
                        first = first or {"B": values, "h": h, "b": b, "C_S": folds, "T_F": triangles, "V_b": bad}
    return {"rows": rows, "triangle_rows": triangle_rows, "matching_failures": failures, "first_failure": first}


def p88_scan():
    rows = failures = 0
    first = None
    for gamma in range(2085):
        values = tuple(x + gamma for x in p88.B)
        h = p88.H + gamma
        for b in (1, 2):
            rows += 1
            ok, folds, triangles, bad = row_ok(values, h, b)
            if not ok:
                failures += 1
                first = first or {"gamma": gamma, "b": b, "C_S": folds, "T_F": triangles, "V_b": bad}
    return {"rows": rows, "matching_failures": failures, "first_failure": first}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {"width_30_unrestricted": width_scan(), "P88_positive_defect_translations": p88_scan()}
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
