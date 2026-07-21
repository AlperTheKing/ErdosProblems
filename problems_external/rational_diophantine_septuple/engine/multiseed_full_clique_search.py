"""Complete compatibility-graph search for the declared multiseed boxes."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

from catalog_scan import parse_catalog
from elliptic_core import CubicCurve, extension_point, extension_roots, rational_sqrt
from lattice_full_clique_search import (
    find_four_clique,
    fraction_mod,
    modular_square_possible,
    quadratic_residues,
    qtext,
)
from multiseed_lattice_search import build_groups, select_groups
from verify_tuple import verify_tuple


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def generate_vertices(
    triple: tuple[Fraction, ...],
    group: dict[str, object],
    coefficient_minimum: int,
    coefficient_maximum: int,
) -> tuple[list[Fraction], dict[str, int]]:
    extensions = tuple(sorted(group["extensions"]))
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
        {
            coefficient: curve.scalar_mul(coefficient, direction)
            for coefficient in coefficient_values
        }
        for direction in directions
    )
    seen_points: set[object] = set()
    generated_x: set[Fraction] = set()
    forbidden_x = set(triple) | set(extensions) | {Fraction(0)}
    processed = 0
    extension_failures = 0
    for coefficients in itertools.product(coefficient_values, repeat=len(directions)):
        processed += 1
        point = base
        for index, coefficient in enumerate(coefficients):
            point = curve.add(point, multiples[index][coefficient])
        if point is None or point in seen_points:
            continue
        seen_points.add(point)
        x = point[0]
        if x in forbidden_x or x in generated_x:
            continue
        if extension_roots(*triple, x) is None:
            extension_failures += 1
            continue
        generated_x.add(x)

    vertices = sorted(generated_x.union(extensions))
    return vertices, {
        "dimension": len(directions),
        "processed_vectors": processed,
        "distinct_points": len(seen_points),
        "generated_extension_candidates": len(generated_x),
        "known_extensions": len(extensions),
        "vertex_count": len(vertices),
        "extension_filter_failures": extension_failures,
    }


def graph_seed(
    triple: tuple[Fraction, ...],
    vertices: list[Fraction],
    primes: tuple[int, ...],
    residue_sets: tuple[frozenset[int], ...],
) -> dict[str, object]:
    modular_values = tuple(
        tuple(fraction_mod(value, prime) for prime in primes) for value in vertices
    )
    adjacency = [set() for _ in vertices]
    exact_tests = 0
    pair_count = 0
    modular_tests = 0
    modular_rejects = {str(prime): 0 for prime in primes}
    for left_index, left in enumerate(vertices):
        for right_index in range(left_index + 1, len(vertices)):
            pair_count += 1
            possible, rejecting_prime, usable = modular_square_possible(
                modular_values[left_index],
                modular_values[right_index],
                primes,
                residue_sets,
            )
            modular_tests += usable
            if not possible:
                modular_rejects[str(rejecting_prime)] += 1
                continue
            exact_tests += 1
            if rational_sqrt(left * vertices[right_index] + 1) is not None:
                adjacency[left_index].add(right_index)
                adjacency[right_index].add(left_index)

    clique, triangle_count = find_four_clique(adjacency)
    edge_count = sum(len(neighbors) for neighbors in adjacency) // 2
    hit: dict[str, object] | None = None
    if clique is not None:
        extensions = tuple(vertices[index] for index in clique)
        values = tuple(triple) + extensions
        if len(values) != 7:
            raise ArithmeticError("a graph hit did not construct seven values")
        verification = verify_tuple(values, name="catalog-multiseed-full-clique")
        if not verification["valid"]:
            raise ArithmeticError("a graph 4-clique failed exact tuple verification")
        hit = {
            "indices": clique,
            "extensions": [qtext(value) for value in extensions],
            "values": [qtext(value) for value in values],
            "verification": verification,
        }

    return {
        "pair_count": pair_count,
        "modular_usable_tests": modular_tests,
        "modular_rejects": modular_rejects,
        "exact_square_tests": exact_tests,
        "edge_count": edge_count,
        "triangle_count_until_first_hit_or_exhaustion": triangle_count,
        "max_clique_size": 4 if hit else (3 if triangle_count else (2 if edge_count else 1)),
        "hit_count": 1 if hit else 0,
        "hit": hit,
    }


def search(
    parent_manifest_path: Path,
    run_manifest: dict[str, object],
    catalog_path: Path,
) -> dict[str, object]:
    parent_hash = sha256(parent_manifest_path)
    if parent_hash != str(run_manifest["parent_manifest_sha256"]).upper():
        raise ValueError("parent manifest SHA-256 mismatch")
    if sha256(catalog_path) != str(run_manifest["catalog_sha256"]).upper():
        raise ValueError("catalog SHA-256 mismatch")

    parent = json.loads(parent_manifest_path.read_text(encoding="utf-8"))
    records = parse_catalog(catalog_path)
    groups = build_groups(records)
    selected = select_groups(groups, parent)
    expected_seeds = int(run_manifest["expected_seed_count"])
    if len(selected) != expected_seeds:
        raise ValueError(f"selected {len(selected)} seeds, expected {expected_seeds}")

    lattice = parent["per_seed_lattice"]
    coefficient_minimum = int(lattice["coefficient_minimum"])
    coefficient_maximum = int(lattice["coefficient_maximum"])
    primes = tuple(int(value) for value in run_manifest["quadratic_residue_primes"])
    residue_sets = tuple(quadratic_residues(prime) for prime in primes)

    seed_results: list[dict[str, object]] = []
    hits: list[dict[str, object]] = []
    for triple, group in selected:
        vertices, generation = generate_vertices(
            triple, group, coefficient_minimum, coefficient_maximum
        )
        graph = graph_seed(triple, vertices, primes, residue_sets)
        row: dict[str, object] = {
            "triple": [qtext(value) for value in triple],
            "catalog_records": sorted(group["record_ids"]),
            **generation,
            **graph,
        }
        seed_results.append(row)
        if graph["hit"] is not None:
            hits.append({"triple": row["triple"], **graph["hit"]})
            break

    totals = {
        "processed_vectors": sum(int(row["processed_vectors"]) for row in seed_results),
        "generated_extension_candidates": sum(
            int(row["generated_extension_candidates"]) for row in seed_results
        ),
        "vertex_count": sum(int(row["vertex_count"]) for row in seed_results),
        "pair_count": sum(int(row["pair_count"]) for row in seed_results),
        "exact_square_tests": sum(int(row["exact_square_tests"]) for row in seed_results),
        "edge_count": sum(int(row["edge_count"]) for row in seed_results),
        "extension_filter_failures": sum(
            int(row["extension_filter_failures"]) for row in seed_results
        ),
    }
    if not hits:
        expected = run_manifest["expected_no_hit_totals"]
        for key in ("processed_vectors", "generated_extension_candidates", "vertex_count", "pair_count"):
            if totals[key] != int(expected[key]):
                raise ValueError(f"aggregate {key}={totals[key]} != declared {expected[key]}")

    return {
        "status": "HIT" if hits else "NO_HIT",
        "parent_manifest_sha256": parent_hash,
        "catalog_sha256": sha256(catalog_path),
        "selected_seed_count": len(selected),
        "processed_seed_count": len(seed_results),
        **totals,
        "hit_count": len(hits),
        "hits": hits,
        "seed_results": seed_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("parent_manifest", type=Path)
    parser.add_argument("run_manifest", type=Path)
    parser.add_argument("catalog", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    run_manifest = json.loads(args.run_manifest.read_text(encoding="utf-8"))
    result = search(args.parent_manifest, run_manifest, args.catalog)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "status",
                    "processed_seed_count",
                    "processed_vectors",
                    "vertex_count",
                    "pair_count",
                    "edge_count",
                    "hit_count",
                )
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
