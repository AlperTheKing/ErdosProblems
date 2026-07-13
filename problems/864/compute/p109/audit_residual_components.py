#!/usr/bin/env python3
"""Exact audit of residual-interval component excess for Problem 864."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p46 = load("p46_p109", ROOT / "problems/864/compute/p46/carry_statistics.py")
p93 = load("p93_p109", ROOT / "problems/864/compute/p93/audit_triangle_components.py")
p88 = load("p88_p109", ROOT / "problems/864/compute/p88/verify_c84_order_counterexample.py")


def residual_components(values: tuple[int, ...], h: int, b: int) -> dict[str, object]:
    folds, triangles = p93.fold_triangle_system(values, h)
    differences = {right - left for left in values for right in values if left < right}
    intervals = [(h - b - v, h - b - u) for _a, _c, u, v in folds]
    order = sorted(range(len(folds)), key=lambda i: (intervals[i][0], intervals[i][1], i))

    component_of: dict[int, int] = {}
    components: list[dict[str, object]] = []
    current_right: int | None = None
    current_id = -1
    for fold_id in order:
        left, right = intervals[fold_id]
        assert left <= right
        if current_right is None or left > current_right:
            current_id += 1
            current_right = right
            components.append({"left": left, "right": right, "folds": [], "triangles": 0, "V_b": 0})
        else:
            current_right = max(current_right, right)
            components[current_id]["right"] = current_right
        component_of[fold_id] = current_id
        components[current_id]["folds"].append(fold_id)
        a, c, _u, _v = folds[fold_id]
        components[current_id]["V_b"] += int(a + c + b in differences)

    cross_component_triangles = []
    for triangle in triangles:
        ids = {component_of[i] for i in triangle}
        if len(ids) != 1:
            cross_component_triangles.append({
                "fold_ids": triangle,
                "component_ids": sorted(ids),
                "folds": [folds[i] for i in triangle],
                "intervals": [intervals[i] for i in triangle],
            })
            continue
        components[ids.pop()]["triangles"] += 1

    worst = None
    for component_id, component in enumerate(components):
        fold_count = len(component["folds"])
        triangle_count = int(component["triangles"])
        collision_count = int(component["V_b"])
        residual = triangle_count - fold_count - collision_count
        record = {
            "component": component_id,
            "left": component["left"],
            "right": component["right"],
            "folds": fold_count,
            "triangles": triangle_count,
            "V_b": collision_count,
            "residual": residual,
        }
        if worst is None or (residual, triangle_count, -fold_count) > (
            worst["residual"], worst["triangles"], -worst["folds"]
        ):
            worst = record
    return {
        "C_S": len(folds),
        "T_F": len(triangles),
        "V_b": sum(a + c + b in differences for a, c, _u, _v in folds),
        "component_count": len(components),
        "cross_component_triangle_count": len(cross_component_triangles),
        "first_cross_component_triangle": cross_component_triangles[0] if cross_component_triangles else None,
        "worst": worst,
    }


def scan_width(max_width: int) -> dict[str, object]:
    rows = triangle_rows = failures = 0
    maximum_residual = 0
    first_failure = None
    for width in range(1, max_width + 1):
        for ruler in p46.sidon_rulers(width):
            p = len(ruler)
            baseline = (3 * p * p - p + 2) // 2
            max_gamma = baseline - width - 2
            if max_gamma < 0:
                continue
            forbidden = p46.forbidden_three_minus_one(ruler)
            reflected = tuple(sorted(width - x for x in ruler))
            for gamma in range(max_gamma + 1):
                values = tuple(gamma + x for x in reflected)
                h = gamma + width + 1
                for b in (1, 2):
                    if 2 * width + 2 * gamma + b in forbidden:
                        continue
                    rows += 1
                    result = residual_components(values, h, b)
                    triangle_rows += result["T_F"] > 0
                    residual = result["worst"]["residual"] if result["worst"] else 0
                    maximum_residual = max(maximum_residual, residual)
                    if result["cross_component_triangle_count"] or residual > 0:
                        failures += 1
                        if first_failure is None:
                            first_failure = {
                                "B": values,
                                "h": h,
                                "b": b,
                                "delta": baseline - h,
                                **result,
                            }
    return {
        "rows": rows,
        "triangle_rows": triangle_rows,
        "failures": failures,
        "maximum_residual": maximum_residual,
        "first_failure": first_failure,
    }


def scan_p88() -> dict[str, object]:
    rows = failures = 0
    maximum_residual = 0
    first_failure = None
    for gamma in range(2085):
        values = tuple(x + gamma for x in p88.B)
        h = p88.H + gamma
        for b in (1, 2):
            rows += 1
            result = residual_components(values, h, b)
            residual = result["worst"]["residual"] if result["worst"] else 0
            maximum_residual = max(maximum_residual, residual)
            if result["cross_component_triangle_count"] or residual > 0:
                failures += 1
                if first_failure is None:
                    first_failure = {"gamma": gamma, "h": h, "b": b, **result}
    return {
        "rows": rows,
        "failures": failures,
        "maximum_residual": maximum_residual,
        "first_failure": first_failure,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "candidate": "T_F(component) <= C_S(component) + V_b(component) for canonical residual-interval overlap components",
        "positive_defect_literal_holes": scan_width(args.max_width),
        "P88_positive_defect_translations": scan_p88(),
    }
    rendered = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="ascii")
    print(rendered)


if __name__ == "__main__":
    main()
