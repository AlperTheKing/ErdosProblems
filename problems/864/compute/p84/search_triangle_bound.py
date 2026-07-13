import argparse
import importlib.util
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
P46_PATH = ROOT / "problems/864/compute/p46/carry_statistics.py"
P84_PATH = ROOT / "problems/864/compute/p84/audit_phase_fourier.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def triangle_count(folds):
    ac = {(a, c) for a, c, _, _ in folds}
    au = {}
    cu = {}
    for a, c, u, _ in folds:
        au.setdefault(a, set()).add(u)
        cu.setdefault(c, set()).add(u)
    trace = sum(len(au.get(a, set()) & cu.get(c, set())) for a, c in ac)
    return trace - len(folds)


def witness(width, ruler, gamma, b, folds, triangles):
    z = tuple(sorted(width - x for x in ruler))
    B = tuple(gamma + x for x in z)
    return {
        "p": len(B),
        "width": width,
        "gamma": gamma,
        "h": gamma + width + 1,
        "b": b,
        "B": B,
        "C_S": len(folds),
        "T_F": triangles,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    p46 = load_module("p46", P46_PATH)
    p84 = load_module("p84", P84_PATH)
    rulers = candidates = holes = failures = nonzero = 0
    max_difference = None
    max_ratio = None
    max_triangles = None

    for width in range(1, args.max_width + 1):
        for ruler in p46.sidon_rulers(width):
            rulers += 1
            p = len(ruler)
            baseline = (3 * p * p - p + 2) // 2
            max_gamma = baseline - width - 2
            if max_gamma < 0:
                continue
            forbidden = p46.forbidden_three_minus_one(ruler)
            z = tuple(sorted(width - x for x in ruler))
            for b in (1, 2):
                for gamma in range(max_gamma + 1):
                    candidates += 1
                    if 2 * width + 2 * gamma + b in forbidden:
                        continue
                    holes += 1
                    B = tuple(gamma + x for x in z)
                    h = gamma + width + 1
                    folds = p84.canonical_folds(B, h)
                    triangles = triangle_count(folds)
                    if triangles:
                        nonzero += 1
                    difference = triangles - len(folds)
                    row = witness(width, ruler, gamma, b, folds, triangles)
                    if difference > 0:
                        failures += 1
                    if max_difference is None or difference > max_difference[0]:
                        max_difference = (difference, row)
                    ratio = Fraction(triangles, len(folds)) if folds else Fraction(0)
                    if max_ratio is None or ratio > max_ratio[0]:
                        max_ratio = (ratio, row)
                    if max_triangles is None or triangles > max_triangles[0]:
                        max_triangles = (triangles, row)

    result = {
        "max_width": args.max_width,
        "sidon_rulers": rulers,
        "positive_defect_candidates": candidates,
        "admissible_holes": holes,
        "nonzero_triangle_rows": nonzero,
        "T_F_gt_C_S_failures": failures,
        "max_T_F_minus_C_S": {
            "value": max_difference[0],
            "witness": max_difference[1],
        },
        "max_T_F_over_C_S": {
            "numerator": max_ratio[0].numerator,
            "denominator": max_ratio[0].denominator,
            "witness": max_ratio[1],
        },
        "max_T_F": {
            "value": max_triangles[0],
            "witness": max_triangles[1],
        },
    }
    rendered = json.dumps(result, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
