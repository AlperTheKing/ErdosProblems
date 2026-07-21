"""Search the complete compatibility graph of a finite EC lattice box.

The parent lattice manifest determines an exact finite set of points in the
extension coset P+2E(Q).  Unlike ``lattice_extend_search.py``, this program
does not require a new point to extend one of the catalogued sextuples.  It
forms every pair among all generated extension x-coordinates and the known
extensions, retains exactly the pairs for which x*z+1 is a rational square,
and searches that graph for a 4-clique.

Small-prime quadratic-residue tests are rejection-only filters.  A pair is
discarded only after a prime with invertible denominators proves it cannot be
a rational square.  Every surviving pair is checked with exact Fraction and
integer-square-root arithmetic.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path

from elliptic_core import CubicCurve, extension_point, extension_roots, rational_sqrt
from lattice_extend_search import load_manifest
from verify_tuple import verify_tuple


def q(text: str) -> Fraction:
    return Fraction(text)


def qtext(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def fraction_mod(value: Fraction, prime: int) -> int | None:
    """Map a rational to F_p, or return None when its denominator vanishes."""

    denominator = value.denominator % prime
    if denominator == 0:
        return None
    return (value.numerator % prime) * pow(denominator, -1, prime) % prime


def quadratic_residues(prime: int) -> frozenset[int]:
    return frozenset((value * value) % prime for value in range(prime))


def modular_square_possible(
    left_residues: tuple[int | None, ...],
    right_residues: tuple[int | None, ...],
    primes: tuple[int, ...],
    residue_sets: tuple[frozenset[int], ...],
) -> tuple[bool, int | None, int]:
    """Return whether modular tests permit a square and the rejecting prime.

    The third return value counts usable prime tests.  A missing residue skips
    that prime, which preserves soundness when a denominator is divisible by p.
    """

    usable = 0
    for index, prime in enumerate(primes):
        left = left_residues[index]
        right = right_residues[index]
        if left is None or right is None:
            continue
        usable += 1
        if (left * right + 1) % prime not in residue_sets[index]:
            return False, prime, usable
    return True, None, usable


def find_four_clique(adjacency: list[set[int]]) -> tuple[list[int] | None, int]:
    """Return the lexicographically first 4-clique and the triangle count."""

    triangle_count = 0
    for left in range(len(adjacency)):
        for right in sorted(vertex for vertex in adjacency[left] if vertex > left):
            common = {
                vertex
                for vertex in adjacency[left].intersection(adjacency[right])
                if vertex > right
            }
            triangle_count += len(common)
            for third in sorted(common):
                fourths = [
                    vertex
                    for vertex in common.intersection(adjacency[third])
                    if vertex > third
                ]
                if fourths:
                    return [left, right, third, min(fourths)], triangle_count
    return None, triangle_count


def generate_extension_vertices(parent: dict[str, object]) -> tuple[list[Fraction], dict[str, int]]:
    triple = tuple(q(value) for value in parent["triple"])
    extensions = tuple(q(value) for value in parent["known_extensions"])
    curve = CubicCurve.from_diophantine_triple(*triple)
    points = tuple(extension_point(*triple, x) for x in extensions)
    base = points[0]
    neg_base = curve.neg(base)
    directions = (curve.scalar_mul(2, base),) + tuple(
        curve.add(point, neg_base) for point in points[1:]
    )
    if len(directions) != int(parent["coefficient_box"]["dimension"]):
        raise ValueError("constructed direction count disagrees with parent manifest")
    if any(direction is None for direction in directions):
        raise ValueError("a declared lattice direction is the identity")

    minimum = int(parent["coefficient_box"]["minimum"])
    maximum = int(parent["coefficient_box"]["maximum"])
    coefficient_values = tuple(range(minimum, maximum + 1))
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
    infinity_count = 0
    extension_filter_failures = 0
    for coefficients in itertools.product(coefficient_values, repeat=len(directions)):
        processed += 1
        point = base
        for index, coefficient in enumerate(coefficients):
            point = curve.add(point, multiples[index][coefficient])
        if point is None:
            infinity_count += 1
            continue
        if point in seen_points:
            continue
        seen_points.add(point)
        x = point[0]
        if x in forbidden_x or x in generated_x:
            continue
        if extension_roots(*triple, x) is None:
            extension_filter_failures += 1
            continue
        generated_x.add(x)

    vertices = sorted(generated_x.union(extensions))
    stats = {
        "processed_coefficient_vectors": processed,
        "distinct_points": len(seen_points),
        "generated_extension_candidates": len(generated_x),
        "known_extensions": len(extensions),
        "vertex_count": len(vertices),
        "infinity_count": infinity_count,
        "extension_filter_failures": extension_filter_failures,
    }
    return vertices, stats


def search(parent_path: Path, run_manifest: dict[str, object]) -> dict[str, object]:
    expected_hash = str(run_manifest["parent_manifest_sha256"]).upper()
    actual_hash = sha256(parent_path)
    if actual_hash != expected_hash:
        raise ValueError(f"parent manifest SHA-256 mismatch: {actual_hash}")
    parent = load_manifest(parent_path)
    vertices, generation = generate_extension_vertices(parent)

    expected_vertices = int(run_manifest["expected_vertex_count"])
    expected_candidates = int(run_manifest["expected_generated_extension_candidates"])
    if len(vertices) != expected_vertices:
        raise ValueError(f"vertex count {len(vertices)} != declared {expected_vertices}")
    if generation["generated_extension_candidates"] != expected_candidates:
        raise ValueError("generated extension candidate count disagrees with manifest")

    primes = tuple(int(value) for value in run_manifest["quadratic_residue_primes"])
    residue_sets = tuple(quadratic_residues(prime) for prime in primes)
    modular_values = tuple(
        tuple(fraction_mod(value, prime) for prime in primes) for value in vertices
    )

    adjacency = [set() for _ in vertices]
    modular_rejects = {str(prime): 0 for prime in primes}
    modular_usable_tests = 0
    exact_square_tests = 0
    pair_count = 0
    for left_index, left in enumerate(vertices):
        left_mod = modular_values[left_index]
        for right_index in range(left_index + 1, len(vertices)):
            pair_count += 1
            possible, rejecting_prime, usable = modular_square_possible(
                left_mod,
                modular_values[right_index],
                primes,
                residue_sets,
            )
            modular_usable_tests += usable
            if not possible:
                modular_rejects[str(rejecting_prime)] += 1
                continue
            exact_square_tests += 1
            if rational_sqrt(left * vertices[right_index] + 1) is not None:
                adjacency[left_index].add(right_index)
                adjacency[right_index].add(left_index)

    declared_pairs = int(run_manifest["expected_pair_count"])
    if pair_count != declared_pairs:
        raise ValueError(f"pair count {pair_count} != declared {declared_pairs}")

    clique, triangle_count = find_four_clique(adjacency)
    edge_count = sum(len(neighbors) for neighbors in adjacency) // 2
    hit: dict[str, object] | None = None
    if clique is not None:
        triple = tuple(q(value) for value in parent["triple"])
        extension_values = tuple(vertices[index] for index in clique)
        values = triple + extension_values
        verification = verify_tuple(values, name="seed1-full-4-clique")
        if not verification["valid"]:
            raise ArithmeticError("4-clique failed exact tuple verification")
        hit = {
            "indices": clique,
            "extensions": [qtext(value) for value in extension_values],
            "values": [qtext(value) for value in values],
            "verification": verification,
        }

    max_clique_lower_bound = 4 if clique else (3 if triangle_count else (2 if edge_count else 1))
    return {
        "status": "HIT" if hit else "NO_HIT",
        "parent_manifest_sha256": actual_hash,
        **generation,
        "pair_count": pair_count,
        "quadratic_residue_primes": list(primes),
        "modular_usable_tests": modular_usable_tests,
        "modular_rejects": modular_rejects,
        "exact_square_tests": exact_square_tests,
        "edge_count": edge_count,
        "triangle_count_until_first_hit_or_exhaustion": triangle_count,
        "max_clique_lower_bound": max_clique_lower_bound,
        "hit_count": 1 if hit else 0,
        "hit": hit,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("parent_manifest", type=Path)
    parser.add_argument("run_manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    run_manifest = json.loads(args.run_manifest.read_text(encoding="utf-8"))
    result = search(args.parent_manifest, run_manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "status",
                    "vertex_count",
                    "pair_count",
                    "exact_square_tests",
                    "edge_count",
                    "hit_count",
                )
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
