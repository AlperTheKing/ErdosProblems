#!/usr/bin/env python3
"""Verify an even-starter certificate and its developed perfect 1-factorisation.

The implementation deliberately uses only the Python standard library.  It
checks the complete factorisation and every pair of factors directly; the
cyclic-symmetry calculation is an additional diagnostic, not a shortcut used
by the main verification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable


Edge = tuple[int, int]
Factor = frozenset[Edge]


class VerificationError(ValueError):
    """Raised when a certificate or one of its derived objects is invalid."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def canonical_edge(u: int, v: int) -> Edge:
    require(u != v, f"loop edge ({u}, {v})")
    return (u, v) if u < v else (v, u)


@dataclass(frozen=True)
class Certificate:
    path: Path
    raw_sha256: str
    name: str
    modulus: int
    order: int
    pairs: tuple[Edge, ...]
    declared_omitted: tuple[int, ...] | None


@dataclass(frozen=True)
class VerificationResult:
    certificate: Certificate
    omitted: tuple[int, int]
    factors: tuple[Factor, ...]
    full_pair_checks: int
    full_cycle_histogram: Counter[int]
    translation_checks: int
    orbit_sizes: Counter[int]
    representative_checks: int
    representative_cycle_histogram: Counter[int]


def _strict_int(value: Any, location: str) -> int:
    require(type(value) is int, f"{location} must be an integer")
    return value


def load_certificate(path: Path) -> Certificate:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise VerificationError(f"cannot read {path}: {exc}") from exc

    try:
        document = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"invalid JSON in {path}: {exc}") from exc

    require(isinstance(document, dict), "certificate root must be an object")
    modulus = _strict_int(document.get("modulus"), "modulus")
    order = _strict_int(document.get("order", modulus + 2), "order")
    require(order == modulus + 2, "order must equal modulus + 2")
    name = document.get("name", path.stem)
    require(isinstance(name, str) and name, "name must be a nonempty string")

    raw_pairs = document.get("pairs")
    require(isinstance(raw_pairs, list), "pairs must be an array")
    pairs: list[Edge] = []
    for index, raw_pair in enumerate(raw_pairs):
        require(
            isinstance(raw_pair, list) and len(raw_pair) == 2,
            f"pairs[{index}] must be a two-element array",
        )
        x = _strict_int(raw_pair[0], f"pairs[{index}][0]")
        y = _strict_int(raw_pair[1], f"pairs[{index}][1]")
        pairs.append((x, y))

    raw_omitted = document.get("omitted")
    declared_omitted: tuple[int, ...] | None = None
    if raw_omitted is not None:
        require(isinstance(raw_omitted, list), "omitted must be an array")
        declared_omitted = tuple(
            _strict_int(value, f"omitted[{index}]")
            for index, value in enumerate(raw_omitted)
        )

    return Certificate(
        path=path,
        raw_sha256=hashlib.sha256(raw).hexdigest(),
        name=name,
        modulus=modulus,
        order=order,
        pairs=tuple(pairs),
        declared_omitted=declared_omitted,
    )


def verify_even_starter(certificate: Certificate) -> tuple[int, int]:
    modulus = certificate.modulus
    require(modulus >= 4 and modulus % 2 == 0, "modulus must be even and at least 4")
    expected_pairs = modulus // 2 - 1
    require(
        len(certificate.pairs) == expected_pairs,
        f"expected {expected_pairs} pairs, found {len(certificate.pairs)}",
    )

    endpoint_owner: dict[int, int] = {}
    differences: Counter[int] = Counter()
    for index, (x, y) in enumerate(certificate.pairs):
        require(0 <= x < modulus, f"pairs[{index}][0]={x} is outside Z/{modulus}Z")
        require(0 <= y < modulus, f"pairs[{index}][1]={y} is outside Z/{modulus}Z")
        require(x != y, f"pairs[{index}] has equal endpoints")
        for endpoint in (x, y):
            require(
                endpoint not in endpoint_owner,
                f"endpoint {endpoint} occurs in pairs {endpoint_owner.get(endpoint)} and {index}",
            )
            endpoint_owner[endpoint] = index
        differences[(x - y) % modulus] += 1
        differences[(y - x) % modulus] += 1

    omitted = tuple(sorted(set(range(modulus)) - set(endpoint_owner)))
    require(len(omitted) == 2, f"expected two omitted residues, found {omitted}")
    if certificate.declared_omitted is not None:
        require(
            tuple(sorted(certificate.declared_omitted)) == omitted,
            f"declared omitted residues {certificate.declared_omitted} do not match {omitted}",
        )

    expected_differences = Counter(
        {difference: 1 for difference in range(1, modulus) if difference != modulus // 2}
    )
    if differences != expected_differences:
        missing = sorted((expected_differences - differences).elements())
        extra = sorted((differences - expected_differences).elements())
        raise VerificationError(
            f"signed differences are not Z/{modulus}Z \\ {{0,{modulus // 2}}}; "
            f"missing={missing}, extra={extra}"
        )
    return (omitted[0], omitted[1])


def develop_factors(certificate: Certificate, omitted: tuple[int, int]) -> tuple[Factor, ...]:
    modulus = certificate.modulus
    infinity_0 = modulus
    infinity_1 = modulus + 1
    omitted_0, omitted_1 = omitted
    factors: list[Factor] = []

    for shift in range(modulus):
        edges = {
            canonical_edge((x + shift) % modulus, (y + shift) % modulus)
            for x, y in certificate.pairs
        }
        edges.add(canonical_edge(infinity_0, (omitted_0 + shift) % modulus))
        edges.add(canonical_edge(infinity_1, (omitted_1 + shift) % modulus))
        factors.append(frozenset(edges))

    special_edges = {canonical_edge(infinity_0, infinity_1)}
    special_edges.update(
        canonical_edge(x, x + modulus // 2) for x in range(modulus // 2)
    )
    factors.append(frozenset(special_edges))
    return tuple(factors)


def verify_factorisation(certificate: Certificate, factors: tuple[Factor, ...]) -> None:
    order = certificate.order
    require(len(factors) == order - 1, f"expected {order - 1} factors, found {len(factors)}")
    expected_factor_size = order // 2
    owners: defaultdict[Edge, list[int]] = defaultdict(list)

    for factor_index, factor in enumerate(factors):
        require(
            len(factor) == expected_factor_size,
            f"factor {factor_index} has {len(factor)} edges, expected {expected_factor_size}",
        )
        degrees = [0] * order
        for u, v in factor:
            require(0 <= u < order and 0 <= v < order, f"factor {factor_index} has invalid edge {(u, v)}")
            degrees[u] += 1
            degrees[v] += 1
            owners[(u, v)].append(factor_index)
        require(
            all(degree == 1 for degree in degrees),
            f"factor {factor_index} is not a perfect matching; degrees={degrees}",
        )

    expected_edges = {
        (u, v) for u in range(order) for v in range(u + 1, order)
    }
    actual_edges = set(owners)
    missing = sorted(expected_edges - actual_edges)
    extra = sorted(actual_edges - expected_edges)
    repeated = sorted((edge, indices) for edge, indices in owners.items() if len(indices) != 1)
    require(not missing, f"edge partition is missing {len(missing)} edges; first={missing[:5]}")
    require(not extra, f"edge partition has invalid edges; first={extra[:5]}")
    require(not repeated, f"edge partition repeats {len(repeated)} edges; first={repeated[:5]}")


def hamilton_cycle_length(first: Factor, second: Factor, order: int) -> int:
    require(first.isdisjoint(second), "two factors share an edge")
    adjacency: list[list[int]] = [[] for _ in range(order)]
    for u, v in first | second:
        adjacency[u].append(v)
        adjacency[v].append(u)
    require(
        all(len(neighbours) == 2 for neighbours in adjacency),
        "factor union is not spanning 2-regular",
    )

    start = 0
    previous = -1
    current = start
    visited = {start}
    while True:
        neighbours = adjacency[current]
        following = neighbours[0] if neighbours[0] != previous else neighbours[1]
        previous, current = current, following
        if current == start:
            break
        require(current not in visited, "factor union repeats a vertex before closing")
        visited.add(current)
    return len(visited)


def verify_all_factor_pairs(
    certificate: Certificate, factors: tuple[Factor, ...]
) -> tuple[int, Counter[int]]:
    histogram: Counter[int] = Counter()
    checks = 0
    for first_index, second_index in combinations(range(len(factors)), 2):
        length = hamilton_cycle_length(
            factors[first_index], factors[second_index], certificate.order
        )
        histogram[length] += 1
        checks += 1
        require(
            length == certificate.order,
            f"factors {first_index} and {second_index} form a {length}-cycle, "
            f"not a Hamilton cycle of length {certificate.order}",
        )
    expected_checks = len(factors) * (len(factors) - 1) // 2
    require(checks == expected_checks, "not all unordered factor pairs were checked")
    return checks, histogram


def translate_factor(factor: Factor, shift: int, modulus: int) -> Factor:
    def translate_vertex(vertex: int) -> int:
        return (vertex + shift) % modulus if vertex < modulus else vertex

    return frozenset(
        canonical_edge(translate_vertex(u), translate_vertex(v)) for u, v in factor
    )


def factor_pair_orbits(modulus: int) -> tuple[frozenset[tuple[int, int]], ...]:
    special = modulus
    unseen = set(combinations(range(modulus + 1), 2))
    orbits: list[frozenset[tuple[int, int]]] = []

    def translate_index(index: int, shift: int) -> int:
        return (index + shift) % modulus if index != special else special

    while unseen:
        seed = min(unseen)
        orbit = frozenset(
            tuple(sorted((translate_index(seed[0], shift), translate_index(seed[1], shift))))
            for shift in range(modulus)
        )
        require(orbit <= unseen | (set(combinations(range(modulus + 1), 2)) - unseen), "invalid orbit")
        unseen.difference_update(orbit)
        orbits.append(orbit)
    return tuple(orbits)


def verify_cyclic_symmetry(
    certificate: Certificate, factors: tuple[Factor, ...]
) -> tuple[int, Counter[int], int, Counter[int]]:
    modulus = certificate.modulus
    special = modulus
    translation_checks = 0
    for shift in range(modulus):
        for factor_index in range(modulus):
            require(
                translate_factor(factors[factor_index], shift, modulus)
                == factors[(factor_index + shift) % modulus],
                f"translation {shift} does not send M_{factor_index} to the expected factor",
            )
            translation_checks += 1
        require(
            translate_factor(factors[special], shift, modulus) == factors[special],
            f"translation {shift} does not fix the special factor",
        )
        translation_checks += 1

    orbits = factor_pair_orbits(modulus)
    expected_orbits = modulus // 2 + 1
    require(
        len(orbits) == expected_orbits,
        f"expected {expected_orbits} factor-pair orbits, found {len(orbits)}",
    )
    orbit_sizes = Counter(len(orbit) for orbit in orbits)
    require(
        sum(size * count for size, count in orbit_sizes.items())
        == len(factors) * (len(factors) - 1) // 2,
        "factor-pair orbits do not partition all pairs",
    )

    representatives = [(special, 0)] + [(0, difference) for difference in range(1, modulus // 2 + 1)]
    representative_histogram: Counter[int] = Counter()
    for first_index, second_index in representatives:
        length = hamilton_cycle_length(
            factors[first_index], factors[second_index], certificate.order
        )
        representative_histogram[length] += 1
        require(
            length == certificate.order,
            f"symmetry representative {(first_index, second_index)} is not Hamiltonian",
        )
    require(len(representatives) == len(orbits), "representative count does not match orbit count")
    return translation_checks, orbit_sizes, len(representatives), representative_histogram


def verify(certificate: Certificate) -> VerificationResult:
    omitted = verify_even_starter(certificate)
    factors = develop_factors(certificate, omitted)
    verify_factorisation(certificate, factors)
    full_pair_checks, full_histogram = verify_all_factor_pairs(certificate, factors)
    translation_checks, orbit_sizes, representative_checks, representative_histogram = (
        verify_cyclic_symmetry(certificate, factors)
    )
    return VerificationResult(
        certificate=certificate,
        omitted=omitted,
        factors=factors,
        full_pair_checks=full_pair_checks,
        full_cycle_histogram=full_histogram,
        translation_checks=translation_checks,
        orbit_sizes=orbit_sizes,
        representative_checks=representative_checks,
        representative_cycle_histogram=representative_histogram,
    )


def counter_as_json(counter: Counter[int]) -> str:
    return json.dumps({str(key): counter[key] for key in sorted(counter)}, separators=(",", ":"))


def print_result(result: VerificationResult) -> None:
    certificate = result.certificate
    order = certificate.order
    expected_edges = order * (order - 1) // 2
    signed_difference_count = certificate.modulus - 2
    print(f"certificate={certificate.path}")
    print(f"certificate_sha256={certificate.raw_sha256}")
    print(f"name={certificate.name}")
    print(f"modulus={certificate.modulus} order={order}")
    print(
        "even_starter=PASS "
        f"pairs={len(certificate.pairs)} omitted={list(result.omitted)} "
        f"signed_differences={signed_difference_count}/{signed_difference_count}"
    )
    print(
        "edge_partition=PASS "
        f"factors={len(result.factors)} edges={expected_edges}/{expected_edges}"
    )
    print(
        "all_factor_pairs=PASS "
        f"checks={result.full_pair_checks} "
        f"cycle_length_histogram={counter_as_json(result.full_cycle_histogram)}"
    )
    print(
        "cyclic_symmetry=PASS "
        f"factor_image_checks={result.translation_checks} "
        f"pair_orbits={sum(result.orbit_sizes.values())} "
        f"orbit_size_histogram={counter_as_json(result.orbit_sizes)}"
    )
    print(
        "symmetry_representatives=PASS "
        f"checks={result.representative_checks} "
        "representatives=special-vs-M0,M0-vs-Md[1..modulus/2] "
        f"cycle_length_histogram={counter_as_json(result.representative_cycle_histogram)}"
    )
    print(f"VERIFIED: perfect 1-factorisation of K_{order}")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path, help="JSON even-starter certificate")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        certificate = load_certificate(args.certificate)
        result = verify(certificate)
    except VerificationError as exc:
        print(f"VERIFICATION FAILED: {exc}", file=sys.stderr)
        return 1
    print_result(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
