import argparse
import importlib.util
import json
import math
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p124 = load(
    "p124_dependency",
    ROOT / "problems/864/compute/p124/audit_six_sign_chambers.py",
)


def exact_first_dependency(rows):
    pivots = []
    for index, source in enumerate(rows):
        row = {column: Fraction(value) for column, value in source.items() if value}
        combination = {index: Fraction(1)}
        for pivot, pivot_row, pivot_combination in pivots:
            value = row.get(pivot, 0)
            if not value:
                continue
            for column, coefficient in pivot_row.items():
                new_value = row.get(column, 0) - value * coefficient
                if new_value:
                    row[column] = new_value
                else:
                    row.pop(column, None)
            for old_index, coefficient in pivot_combination.items():
                new_value = combination.get(old_index, 0) - value * coefficient
                if new_value:
                    combination[old_index] = new_value
                else:
                    combination.pop(old_index, None)
        if not row:
            return len(pivots), combination
        pivot = max(row)
        value = row[pivot]
        pivots.append(
            (
                pivot,
                {column: coefficient / value for column, coefficient in row.items()},
                {
                    old_index: coefficient / value
                    for old_index, coefficient in combination.items()
                },
            )
        )
    return len(pivots), None


def primitive_integer_combination(combination):
    denominator = 1
    for coefficient in combination.values():
        denominator = math.lcm(denominator, coefficient.denominator)
    integers = {
        index: int(coefficient * denominator)
        for index, coefficient in combination.items()
    }
    divisor = 0
    for coefficient in integers.values():
        divisor = math.gcd(divisor, abs(coefficient))
    return {index: coefficient // divisor for index, coefficient in integers.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="ascii"))
    witness = payload["domains"]["p86_translations"]["first_failure"]
    B = tuple(witness["B"])
    h = witness["h"]
    signs = tuple(witness["signs"])
    folds, triangles, rows = p124.weighted.relation_rows(B, h, 1)
    C = len(folds)
    p = len(B)
    indices = [
        index
        for index, triangle in enumerate(triangles)
        if p124.chamber_key(folds, triangle) == signs
    ]
    chamber_rows = [
        {
            column: value
            for column, value in rows[index].items()
            if column < C + 2 * p
        }
        for index in indices
    ]
    rank_before_dependency, rational = exact_first_dependency(chamber_rows)
    if rational is None:
        raise AssertionError("the stored modular failure has no rational dependency")
    coefficients = primitive_integer_combination(rational)

    exact_sum = {}
    for local_index, coefficient in coefficients.items():
        for column, value in chamber_rows[local_index].items():
            new_value = exact_sum.get(column, 0) + coefficient * value
            if new_value:
                exact_sum[column] = new_value
            else:
                exact_sum.pop(column, None)
    if exact_sum:
        raise AssertionError("reported integer combination is not zero")

    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers and Fraction Gaussian elimination",
        "p": p,
        "h": h,
        "C_S": C,
        "T_F": len(triangles),
        "signs": signs,
        "chamber_rows": len(indices),
        "rank_before_first_dependency": rank_before_dependency,
        "dependency_terms": len(coefficients),
        "maximum_absolute_coefficient": max(map(abs, coefficients.values())),
        "coefficients_by_local_row": coefficients,
        "triangle_fold_ids": {
            local_index: triangles[indices[local_index]]
            for local_index in coefficients
        },
        "exact_zero_verified": True,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
