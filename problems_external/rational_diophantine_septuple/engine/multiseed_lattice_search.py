"""Exact finite elliptic-lattice portfolio over shared catalog triples."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

from catalog_scan import parse_catalog
from elliptic_core import CubicCurve, extension_point, extension_roots, rational_sqrt
from verify_tuple import verify_tuple


def q(value: str) -> Fraction:
    return Fraction(value)


def qtext(value: Fraction) -> str:
    return str(value)


def compatible(left: Fraction, right: Fraction) -> bool:
    return rational_sqrt(left * right + 1) is not None


def build_groups(records: list[dict[str, object]]) -> dict[tuple[Fraction, ...], dict[str, object]]:
    extensions: dict[tuple[Fraction, ...], set[Fraction]] = defaultdict(set)
    cliques: dict[tuple[Fraction, ...], set[tuple[Fraction, ...]]] = defaultdict(set)
    record_ids: dict[tuple[Fraction, ...], set[int]] = defaultdict(set)
    torsion_tags: dict[tuple[Fraction, ...], set[str]] = defaultdict(set)

    for record in records:
        values = tuple(record["values"])  # type: ignore[arg-type]
        index = int(record["index"])
        for positions in itertools.combinations(range(6), 3):
            chosen = set(positions)
            triple = tuple(sorted(values[position] for position in positions))
            remaining = tuple(sorted(values[position] for position in range(6) if position not in chosen))
            extensions[triple].update(remaining)
            cliques[triple].add(remaining)
            record_ids[triple].add(index)
        for tag, triple in record["torsion"]:  # type: ignore[union-attr]
            torsion_tags[triple].add(tag)

    return {
        triple: {
            "extensions": extensions[triple],
            "cliques": cliques[triple],
            "record_ids": record_ids[triple],
            "torsion_tags": torsion_tags[triple],
        }
        for triple in extensions
    }


def select_groups(
    groups: dict[tuple[Fraction, ...], dict[str, object]], manifest: dict[str, object]
) -> list[tuple[tuple[Fraction, ...], dict[str, object]]]:
    selection = manifest["seed_selection"]
    minimum_extensions = int(selection["minimum_distinct_known_extensions"])
    minimum_records = int(selection["minimum_catalog_records"])
    excluded_tags = set(selection["excluded_torsion_tags"])
    excluded_triples = {
        tuple(sorted(q(value) for value in triple))
        for triple in selection.get("excluded_triples_already_searched", [])
    }
    eligible = []
    for triple, group in groups.items():
        if triple in excluded_triples:
            continue
        if len(group["extensions"]) < minimum_extensions:
            continue
        if len(group["record_ids"]) < minimum_records:
            continue
        if set(group["torsion_tags"]) & excluded_tags:
            continue
        eligible.append((triple, group))
    eligible.sort(
        key=lambda item: (
            len(item[1]["extensions"]),
            len(item[1]["record_ids"]),
            item[0],
        ),
        reverse=True,
    )
    return eligible


def search_seed(
    triple: tuple[Fraction, ...],
    group: dict[str, object],
    coefficient_minimum: int,
    coefficient_maximum: int,
) -> dict[str, object]:
    extensions = tuple(sorted(group["extensions"]))
    cliques = tuple(sorted(group["cliques"]))
    curve = CubicCurve.from_diophantine_triple(*triple)
    points = tuple(extension_point(*triple, value) for value in extensions)
    base = points[0]
    neg_base = curve.neg(base)
    directions = (curve.scalar_mul(2, base),) + tuple(
        curve.add(point, neg_base) for point in points[1:]
    )
    if any(direction is None for direction in directions):
        raise ValueError(f"identity direction for seed {triple}")

    coefficient_values = tuple(range(coefficient_minimum, coefficient_maximum + 1))
    multiples = tuple(
        {coefficient: curve.scalar_mul(coefficient, direction) for coefficient in coefficient_values}
        for direction in directions
    )
    seen_points: set[object] = set()
    seen_x: set[Fraction] = set()
    forbidden_x = set(triple) | set(extensions)
    processed = 0
    extension_failures = 0
    candidates = 0
    near_misses: list[dict[str, object]] = []
    hits: list[dict[str, object]] = []

    for coefficients in itertools.product(coefficient_values, repeat=len(directions)):
        processed += 1
        point = base
        for index, coefficient in enumerate(coefficients):
            point = curve.add(point, multiples[index][coefficient])
        if point is None or point in seen_points:
            continue
        seen_points.add(point)
        x = point[0]
        if x in seen_x:
            continue
        seen_x.add(x)
        if x == 0 or x in forbidden_x:
            continue
        if extension_roots(*triple, x) is None:
            extension_failures += 1
            continue
        candidates += 1
        for clique in cliques:
            passes = tuple(compatible(x, value) for value in clique)
            pass_count = sum(passes)
            if pass_count == 3:
                septuple = tuple(triple) + tuple(clique) + (x,)
                verification = verify_tuple(septuple, name="catalog-multiseed-hit")
                if not verification["valid"]:
                    raise ArithmeticError("clique hit failed independent verification")
                hits.append(
                    {
                        "coefficients": list(coefficients),
                        "x": qtext(x),
                        "clique": [qtext(value) for value in clique],
                        "values": [qtext(value) for value in septuple],
                        "verification": verification,
                    }
                )
            elif pass_count >= 2:
                near_misses.append(
                    {
                        "pass_count": pass_count,
                        "coefficients": list(coefficients),
                        "x": qtext(x),
                        "clique": [qtext(value) for value in clique],
                    }
                )

    return {
        "triple": [qtext(value) for value in triple],
        "catalog_records": sorted(group["record_ids"]),
        "known_extension_count": len(extensions),
        "known_clique_count": len(cliques),
        "dimension": len(directions),
        "processed_vectors": processed,
        "distinct_points": len(seen_points),
        "distinct_x": len(seen_x),
        "extension_candidate_count": candidates,
        "extension_filter_failures": extension_failures,
        "hit_count": len(hits),
        "hits": hits,
        "near_miss_count": len(near_misses),
        "near_misses": near_misses[:20],
    }


def search(manifest: dict[str, object], catalog_path: Path) -> dict[str, object]:
    records = parse_catalog(catalog_path)
    expected = int(manifest["input"]["expected_sextuples"])
    if len(records) != expected:
        raise ValueError(f"expected {expected} catalog records, parsed {len(records)}")
    groups = build_groups(records)
    selected = select_groups(groups, manifest)
    lattice = manifest["per_seed_lattice"]
    coefficient_minimum = int(lattice["coefficient_minimum"])
    coefficient_maximum = int(lattice["coefficient_maximum"])

    seed_results: list[dict[str, object]] = []
    hits: list[dict[str, object]] = []
    for triple, group in selected:
        result = search_seed(triple, group, coefficient_minimum, coefficient_maximum)
        seed_results.append(result)
        if result["hits"]:
            hits.extend(result["hits"])
            break

    return {
        "status": "HIT" if hits else "NO_HIT",
        "catalog_sextuples": len(records),
        "selected_seed_count": len(selected),
        "processed_seed_count": len(seed_results),
        "processed_vectors": sum(int(row["processed_vectors"]) for row in seed_results),
        "distinct_x_sum": sum(int(row["distinct_x"]) for row in seed_results),
        "extension_candidate_sum": sum(int(row["extension_candidate_count"]) for row in seed_results),
        "extension_filter_failures": sum(int(row["extension_filter_failures"]) for row in seed_results),
        "hit_count": len(hits),
        "hits": hits,
        "near_miss_count": sum(int(row["near_miss_count"]) for row in seed_results),
        "seed_results": seed_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("catalog", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = search(manifest, args.catalog)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "status",
                    "selected_seed_count",
                    "processed_seed_count",
                    "processed_vectors",
                    "distinct_x_sum",
                    "extension_candidate_sum",
                    "extension_filter_failures",
                    "hit_count",
                    "near_miss_count",
                )
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
