"""Finite Mordell--Weil lattice search for a rational septuple extension.

All known extension points lie in the coset P+2E(Q).  Fixing one such point
T0, every difference Ti-T0 and 2T0 lies in 2E(Q).  Consequently every point

    T0 + n0*(2T0) + sum_i ni*(Ti-T0)

is again in the extension coset.  The script nevertheless checks the three
square conditions directly before testing compatibility with known cliques.
"""

from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from pathlib import Path

from elliptic_core import CubicCurve, extension_point, extension_roots, rational_sqrt
from verify_tuple import verify_tuple


def q(text: str) -> Fraction:
    return Fraction(text)


def qtext(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def compatible(left: Fraction, right: Fraction) -> bool:
    return rational_sqrt(left * right + 1) is not None


def load_manifest(path: Path) -> dict[str, object]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    box = manifest["coefficient_box"]
    dimension = int(box["dimension"])
    if dimension != len(manifest["directions"]):
        raise ValueError("manifest direction count does not match dimension")
    expected = (int(box["maximum"]) - int(box["minimum"]) + 1) ** dimension
    if expected != int(box["combinations"]):
        raise ValueError("manifest combination count is inconsistent")
    return manifest


def search(manifest: dict[str, object]) -> dict[str, object]:
    triple = tuple(q(value) for value in manifest["triple"])
    extensions = tuple(q(value) for value in manifest["known_extensions"])
    cliques = tuple(
        tuple(q(value) for value in clique)
        for clique in manifest["known_extension_cliques"]
    )
    if len(triple) != 3 or any(len(clique) != 3 for clique in cliques):
        raise ValueError("expected one triple and 3-vertex known cliques")

    curve = CubicCurve.from_diophantine_triple(*triple)
    points = tuple(extension_point(*triple, x) for x in extensions)
    base = points[0]
    neg_base = curve.neg(base)
    directions = (curve.scalar_mul(2, base),) + tuple(
        curve.add(point, neg_base) for point in points[1:]
    )
    if len(directions) != int(manifest["coefficient_box"]["dimension"]):
        raise ValueError("constructed direction count disagrees with manifest")
    if any(direction is None for direction in directions):
        raise ValueError("a declared lattice direction is the identity")

    minimum = int(manifest["coefficient_box"]["minimum"])
    maximum = int(manifest["coefficient_box"]["maximum"])
    coefficient_values = tuple(range(minimum, maximum + 1))
    multiples = tuple(
        {coefficient: curve.scalar_mul(coefficient, direction) for coefficient in coefficient_values}
        for direction in directions
    )

    seen_points: set[object] = set()
    seen_x: set[Fraction] = set()
    forbidden_x = set(triple) | set(extensions)
    infinity_count = 0
    duplicate_point_count = 0
    duplicate_x_count = 0
    forbidden_count = 0
    extension_filter_failures = 0
    candidate_count = 0
    hits: list[dict[str, object]] = []
    near_misses: list[dict[str, object]] = []

    combinations = itertools.product(coefficient_values, repeat=len(directions))
    processed = 0
    for coefficients in combinations:
        processed += 1
        point = base
        for index, coefficient in enumerate(coefficients):
            point = curve.add(point, multiples[index][coefficient])
        if point is None:
            infinity_count += 1
            continue
        if point in seen_points:
            duplicate_point_count += 1
            continue
        seen_points.add(point)
        x = point[0]
        if x in seen_x:
            duplicate_x_count += 1
            continue
        seen_x.add(x)
        if x == 0 or x in forbidden_x:
            forbidden_count += 1
            continue
        roots = extension_roots(*triple, x)
        if roots is None:
            extension_filter_failures += 1
            continue
        candidate_count += 1

        for clique_index, clique in enumerate(cliques):
            passes = tuple(compatible(x, value) for value in clique)
            pass_count = sum(passes)
            if pass_count == 3:
                values = tuple(triple) + tuple(clique) + (x,)
                verification = verify_tuple(values, name=f"seed1-clique-{clique_index}")
                if not verification["valid"]:
                    raise ArithmeticError("targeted clique hit failed independent verifier")
                hits.append(
                    {
                        "coefficients": list(coefficients),
                        "clique_index": clique_index,
                        "x": qtext(x),
                        "point_y": qtext(point[1]),
                        "values": [qtext(value) for value in values],
                        "verification": verification,
                    }
                )
            elif pass_count >= 2:
                near_misses.append(
                    {
                        "pass_count": pass_count,
                        "coefficients": list(coefficients),
                        "clique_index": clique_index,
                        "x": qtext(x),
                        "compatible": [qtext(value) for value, passed in zip(clique, passes) if passed],
                        "missing": [qtext(value) for value, passed in zip(clique, passes) if not passed],
                    }
                )

    near_misses.sort(key=lambda item: int(item["pass_count"]), reverse=True)
    return {
        "status": "HIT" if hits else "NO_HIT",
        "processed_coefficient_vectors": processed,
        "distinct_points": len(seen_points),
        "distinct_x": len(seen_x),
        "infinity_count": infinity_count,
        "duplicate_point_count": duplicate_point_count,
        "duplicate_x_count": duplicate_x_count,
        "forbidden_x_count": forbidden_count,
        "extension_candidate_count": candidate_count,
        "extension_filter_failures": extension_filter_failures,
        "hit_count": len(hits),
        "hits": hits,
        "near_miss_count": len(near_misses),
        "near_misses": near_misses[:100],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    manifest = load_manifest(args.manifest)
    result = search(manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "status",
                    "processed_coefficient_vectors",
                    "distinct_x",
                    "extension_candidate_count",
                    "hit_count",
                    "near_miss_count",
                )
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
