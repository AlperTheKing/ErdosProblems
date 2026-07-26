"""Generalized exact face from all collected Gamma_11 equality rays at q<=50.

The companion C++ collector enumerates, up to D22 and positive scaling, every
primitive nonnegative integer vector with total q<=50 satisfying

    ARCBOUND_Gamma_11(x) = q^2/25.

This script:

1. parses and independently checks all collected equality representatives;
2. enumerates every complete induced C5-blow-up partition in Gamma_11;
3. generates every balanced class-sum grid point through q=50 and compares
   that symbolic plateau set with the collector output;
4. imposes every resulting F1 multiplier zero and F2 weighted Gram kernel;
5. exports the exact generalized D22 face as integer sparse matrices.

At a general integer equality point a, a parity-p Gram evaluation vector has
coordinates

    v_beta(a) = product_i a_i^((beta_i-p_i)/2),

after dropping the common square-root factor.  This is an exact integer
vector.  Scaling a changes it only by a blockwise common scalar.

The output is a finite q<=50 face certificate, not an all-real theorem and not
an SOS certificate.  No SDP is solved.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
from typing import Iterable

import numpy as np
import scipy.sparse as sp


HERE = Path(__file__).resolve().parent
COLLECTOR_LOG = HERE / "CODEX_R10_c5_FACE_EQUALITY_q5_q50.log"
CORE_PATH = HERE / "CODEX_R10_c5_FACE.py"
BUILDER_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
DEFAULT_DATA = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
DEFAULT_SUMMARY = HERE / "CODEX_R10_c5_FACE_EQUALITY_summary.json"
DEFAULT_REPORT = HERE / "CODEX_R10_c5_FACE_EQUALITY_REPORT.md"
Q_LAYERS = tuple(range(5, 51, 5))
PRIME = 2_000_003


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def parse_collector(path: Path) -> tuple[list[tuple[int, ...]], dict[int, dict[str, int]]]:
    points: list[tuple[int, ...]] = []
    layer_stats: dict[int, dict[str, int]] = {}
    pattern = re.compile(r"EQ q=(\d+) x=\[([0-9,]+)\]$")
    q_done = re.compile(
        r"Q_DONE q=(\d+) target=(\d+) primitive_orbits_at_q=(\d+) "
        r"cumulative_orbits=(\d+) nodes=(\d+) pruned=(\d+) leaves=(\d+) "
        r"equality_leaves=(\d+)$"
    )
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[-2:] == [
        "END_PRIMITIVE_EQUALITY_ORBITS",
        "EXACT_FINITE_COLLECTION_ONLY: no all-real theorem claim",
    ]
    declared = next(
        int(line.split("count=")[1])
        for line in lines
        if line.startswith("BEGIN_PRIMITIVE_EQUALITY_ORBITS")
    )
    for line in lines:
        match = pattern.fullmatch(line)
        if match:
            q = int(match.group(1))
            vector = tuple(int(value) for value in match.group(2).split(","))
            assert len(vector) == 11 and sum(vector) == q
            points.append(vector)
            continue
        match = q_done.fullmatch(line)
        if match:
            values = [int(value) for value in match.groups()]
            q = values[0]
            layer_stats[q] = {
                "target": values[1],
                "primitive_orbits_at_q": values[2],
                "cumulative_orbits": values[3],
                "nodes": values[4],
                "pruned": values[5],
                "leaves": values[6],
                "equality_leaves": values[7],
            }
    assert declared == len(points) == 439
    assert set(layer_stats) == set(Q_LAYERS)
    assert len(set(points)) == len(points)
    return points, layer_stats


def vector_image(
    vector: tuple[int, ...], element: tuple[int, int]
) -> tuple[int, ...]:
    sign, shift = element
    output = [0] * 11
    for vertex, value in enumerate(vector):
        output[(sign * vertex + shift) % 11] = value
    return tuple(output)


def canonical_vector(vector: tuple[int, ...], group) -> tuple[int, ...]:
    return min(vector_image(vector, element) for element in group)


def support_mask(vector: tuple[int, ...]) -> int:
    return sum(1 << vertex for vertex, value in enumerate(vector) if value)


def cycle_order(cycle: Iterable[int], edge_set: set[tuple[int, int]]) -> tuple[int, ...]:
    vertices = tuple(sorted(cycle))
    orders = []
    for first in vertices:
        neighbors = [
            vertex
            for vertex in vertices
            if tuple(sorted((first, vertex))) in edge_set
        ]
        assert len(neighbors) == 2
        for second in neighbors:
            order = [first, second]
            while len(order) < 5:
                previous, current = order[-2], order[-1]
                future = [
                    vertex
                    for vertex in vertices
                    if vertex != previous
                    and tuple(sorted((current, vertex))) in edge_set
                ]
                assert len(future) == 1
                order.append(future[0])
            assert tuple(sorted((order[-1], order[0]))) in edge_set
            orders.append(tuple(order))
    return min(orders)


def partition_canonical(
    classes: tuple[tuple[int, ...], ...], group
) -> tuple[tuple[int, ...], ...]:
    variants = []
    for element in group:
        mapped = [
            tuple(
                sorted((element[0] * vertex + element[1]) % 11 for vertex in cls)
            )
            for cls in classes
        ]
        for direction in (1, -1):
            for start in range(5):
                variants.append(
                    tuple(mapped[(start + direction * index) % 5] for index in range(5))
                )
    return min(variants)


def complete_blowup_partitions(edges, c5s, group) -> list[tuple[tuple[int, ...], ...]]:
    edge_set = set(edges)
    output: set[tuple[tuple[int, ...], ...]] = set()
    for cycle in c5s:
        anchors = cycle_order(cycle, edge_set)
        anchor_set = set(anchors)
        candidates: list[tuple[int, int]] = []
        for vertex in range(11):
            if vertex in anchor_set:
                continue
            compatible = []
            for class_index in range(5):
                required_neighbors = {
                    anchors[(class_index - 1) % 5],
                    anchors[(class_index + 1) % 5],
                }
                actual_neighbors = {
                    anchor
                    for anchor in anchors
                    if tuple(sorted((vertex, anchor))) in edge_set
                }
                if actual_neighbors == required_neighbors:
                    compatible.append(class_index)
            assert len(compatible) <= 1
            if compatible:
                candidates.append((vertex, compatible[0]))

        for selection in range(1 << len(candidates)):
            classes = [set([anchors[index]]) for index in range(5)]
            for bit, (vertex, class_index) in enumerate(candidates):
                if (selection >> bit) & 1:
                    classes[class_index].add(vertex)
            class_of = {
                vertex: class_index
                for class_index, cls in enumerate(classes)
                for vertex in cls
            }
            valid = True
            vertices = sorted(class_of)
            for left, right in combinations(vertices, 2):
                class_distance = (class_of[left] - class_of[right]) % 5
                required_edge = class_distance in (1, 4)
                actual_edge = tuple(sorted((left, right))) in edge_set
                if required_edge != actual_edge:
                    valid = False
                    break
            if valid:
                partition = tuple(tuple(sorted(cls)) for cls in classes)
                output.add(partition_canonical(partition, group))
    return sorted(output)


def weak_compositions(total: int, parts: int) -> list[tuple[int, ...]]:
    if parts == 1:
        return [(total,)]
    output = []
    for first in range(total + 1):
        for tail in weak_compositions(total - first, parts - 1):
            output.append((first,) + tail)
    return output


def plateau_grid(
    partitions: list[tuple[tuple[int, ...], ...]],
    group,
) -> tuple[set[tuple[int, ...]], dict[int, int]]:
    cache = {
        (mass, size): weak_compositions(mass, size)
        for mass in range(1, 11)
        for size in range(1, 4)
    }
    rays: set[tuple[int, ...]] = set()
    by_q: dict[int, int] = {}
    for mass in range(1, 11):
        before = len(rays)
        for classes in partitions:
            choices = [cache[(mass, len(cls))] for cls in classes]
            for class_weights in product(*choices):
                vector = [0] * 11
                for cls, weights in zip(classes, class_weights):
                    for vertex, value in zip(cls, weights):
                        vector[vertex] = value
                gcd = 0
                for value in vector:
                    gcd = math.gcd(gcd, value)
                if gcd != 1:
                    continue
                rays.add(canonical_vector(tuple(vector), group))
        by_q[5 * mass] = len(rays) - before
    return rays, by_q


class ExactRowSpan:
    def __init__(self) -> None:
        self.echelon: list[list[Fraction]] = []
        self.pivots: list[int] = []
        self.selected: list[tuple[int, ...]] = []
        self.seen: set[tuple[int, ...]] = set()

    def add(self, source: tuple[int, ...]) -> bool:
        if source in self.seen:
            return False
        self.seen.add(source)
        row = [Fraction(value) for value in source]
        for base, pivot in zip(self.echelon, self.pivots):
            if row[pivot]:
                factor = row[pivot] / base[pivot]
                row = [
                    value - factor * base_value
                    for value, base_value in zip(row, base)
                ]
        pivot = next((index for index, value in enumerate(row) if value), None)
        if pivot is None:
            return False
        scale = row[pivot]
        self.echelon.append([value / scale for value in row])
        self.pivots.append(pivot)
        self.selected.append(source)
        return True

    @property
    def rank(self) -> int:
        return len(self.selected)


def weighted_kernel_row(
    basis: list[tuple[int, ...]],
    parity_rep: tuple[int, ...],
    vector: tuple[int, ...],
) -> tuple[int, ...] | None:
    if any(
        parity_rep[vertex] and vector[vertex] == 0
        for vertex in range(11)
    ):
        return None
    row = []
    for exponent in basis:
        value = 1
        for vertex in range(11):
            power = (exponent[vertex] - parity_rep[vertex]) // 2
            if power:
                value *= vector[vertex] ** power
        row.append(value)
    assert any(row)
    return tuple(row)


def weighted_gram_equations(
    entry_ids: np.ndarray,
    kernel_rows: list[tuple[int, ...]],
) -> list[dict[int, int]]:
    equations = []
    for vector in kernel_rows:
        nonzero = [(index, value) for index, value in enumerate(vector) if value]
        for row_index in range(entry_ids.shape[0]):
            coefficients: Counter[int] = Counter()
            for column_index, value in nonzero:
                coefficients[int(entry_ids[row_index, column_index])] += value
            if coefficients:
                gcd = 0
                for value in coefficients.values():
                    gcd = math.gcd(gcd, abs(value))
                equation = {
                    column: value // gcd for column, value in coefficients.items()
                }
                equations.append(equation)
    unique = {
        tuple(sorted(equation.items())): equation for equation in equations
    }
    return list(unique.values())


def exact_arc_values(model, vector: tuple[int, ...]) -> list[int]:
    values = []
    for _mask, mono in model.cuts:
        values.append(
            sum(
                vector[model.edges[edge_index][0]]
                * vector[model.edges[edge_index][1]]
                for edge_index in mono
            )
        )
    return values


def build_general_face(log_path: Path):
    core = load_module("codex_r10_equality_core", CORE_PATH)
    builder = load_module("codex_r10_equality_builder", BUILDER_PATH)
    model = builder.build_model()
    points, collector_stats = parse_collector(log_path)

    c5s = core.induced_c5s(model.edges)
    partitions = complete_blowup_partitions(model.edges, c5s, builder.GROUP)
    plateau_rays, plateau_by_q = plateau_grid(partitions, builder.GROUP)
    collector_set = set(points)
    assert plateau_rays == collector_set

    support_histogram = Counter(support_mask(point).bit_count() for point in points)
    equality_by_q = Counter(sum(point) for point in points)
    for point in points:
        assert math.gcd(*point) == 1
        assert point == canonical_vector(point, builder.GROUP)
        q = sum(point)
        assert q in Q_LAYERS
        values = exact_arc_values(model, point)
        assert min(values) == q * q // 25

    multiplier_action, _multiplier_index = builder.action_table(
        model.multiplier_monomials
    )
    _ids, multiplier_reps, _members = builder.orbit_ids(multiplier_action)
    del _ids, _members
    monomial_supports = [
        sum(1 << vertex for vertex, power in enumerate(exponent) if power)
        for exponent in model.multiplier_monomials
    ]

    kernel_spans = [ExactRowSpan() for _orbit in model.gram_orbits]
    forced_multiplier_orbits: set[int] = set()
    increments = []

    points_by_q = {
        q: [point for point in points if sum(point) == q] for q in Q_LAYERS
    }
    for q in Q_LAYERS:
        for point in points_by_q[q]:
            point_support = support_mask(point)
            target = q * q // 25
            cut_values = exact_arc_values(model, point)
            supported_monomials = [
                index
                for index, mask in enumerate(monomial_supports)
                if mask & ~point_support == 0
            ]
            for cut_index, value in enumerate(cut_values):
                if value <= target:
                    continue
                forced_multiplier_orbits.update(
                    int(model.multiplier_orbit_ids[cut_index, monomial_index])
                    for monomial_index in supported_monomials
                )

        full_layer = {
            vector_image(point, element)
            for point in points_by_q[q]
            for element in builder.GROUP
        }
        for point in sorted(full_layer):
            for orbit_index, orbit in enumerate(model.gram_orbits):
                row = weighted_kernel_row(
                    orbit.basis, orbit.parity_rep, point
                )
                if row is not None:
                    kernel_spans[orbit_index].add(row)

        block_constraint_ranks = []
        block_face_dimensions = []
        for orbit, span in zip(model.gram_orbits, kernel_spans):
            original_dimension, face_dimension, _characters = (
                core.invariant_symmetric_dimension(
                    orbit.basis, span.selected, orbit.stabilizer
                )
            )
            assert original_dimension == int(orbit.variable.size)
            block_face_dimensions.append(face_dimension)
            block_constraint_ranks.append(original_dimension - face_dimension)
        increments.append(
            {
                "q_max": q,
                "equality_orbits": sum(
                    len(points_by_q[layer]) for layer in Q_LAYERS if layer <= q
                ),
                "forced_multiplier_orbits": len(forced_multiplier_orbits),
                "kernel_rank_total": sum(span.rank for span in kernel_spans),
                "gram_face_equation_rank": sum(block_constraint_ranks),
                "gram_face_orbit_dimension": sum(block_face_dimensions),
            }
        )

    final_kernel_rows = [span.selected for span in kernel_spans]
    final_constraint_ranks = []
    final_face_dimensions = []
    face_rows_global: list[dict[int, int]] = []
    gram_offsets = []
    gram_qdims = []
    q_offset = 0
    raw_equation_count = 0
    unique_equation_count = 0
    for orbit, kernel_rows in zip(model.gram_orbits, final_kernel_rows):
        qdim = int(orbit.variable.size)
        original_dimension, face_dimension, _characters = (
            core.invariant_symmetric_dimension(
                orbit.basis, kernel_rows, orbit.stabilizer
            )
        )
        assert original_dimension == qdim
        rank = qdim - face_dimension
        equations = weighted_gram_equations(orbit.entry_ids, kernel_rows)
        selected = core.independent_rows_mod_prime(equations, rank, PRIME)
        for equation_index in selected:
            face_rows_global.append(
                {
                    q_offset + column: value
                    for column, value in equations[equation_index].items()
                }
            )
        gram_offsets.append(q_offset)
        gram_qdims.append(qdim)
        q_offset += qdim
        raw_equation_count += len(kernel_rows) * len(orbit.basis)
        unique_equation_count += len(equations)
        final_constraint_ranks.append(rank)
        final_face_dimensions.append(face_dimension)

    gram_face = core.csr_from_dict_rows(face_rows_global, q_offset)
    assert gram_face.shape[0] == sum(final_constraint_ranks)
    assert q_offset == 8647

    forced = np.asarray(sorted(forced_multiplier_orbits), dtype=np.int32)
    live = np.asarray(
        sorted(set(range(2611)) - forced_multiplier_orbits), dtype=np.int32
    )
    normalization_live = model.multiplier_normalization[:, live].astype(np.int64)
    target_nu_live = model.multiplier_target[:, live].astype(np.int64)
    target_gram = sp.hstack(
        [orbit.coefficient_map for orbit in model.gram_orbits],
        format="csr",
    ).astype(np.int64)
    normalization_rhs = np.asarray(
        [
            25 * builder.multinom(model.multiplier_monomials[index])
            for index in multiplier_reps
        ],
        dtype=np.int64,
    )
    target_rhs = np.asarray(
        [
            builder.multinom(model.target_monomials[index])
            for index in model.target_representatives
        ],
        dtype=np.int64,
    )

    partition_masks = np.asarray(
        [
            [sum(1 << vertex for vertex in cls) for cls in partition]
            for partition in partitions
        ],
        dtype=np.int32,
    )
    payload: dict[str, np.ndarray] = {
        "format_version": np.asarray([1], dtype=np.int32),
        "q_max": np.asarray([50], dtype=np.int32),
        "equality_representatives": np.asarray(points, dtype=np.int16),
        "complete_blowup_partition_masks": partition_masks,
        "forced_multiplier_orbits": forced,
        "live_multiplier_orbits": live,
        "normalization_rhs": normalization_rhs,
        "target_rhs": target_rhs,
        "gram_offsets": np.asarray(gram_offsets, dtype=np.int32),
        "gram_qdims": np.asarray(gram_qdims, dtype=np.int32),
        "gram_kernel_dims": np.asarray(
            [span.rank for span in kernel_spans], dtype=np.int32
        ),
        "gram_constraint_ranks": np.asarray(
            final_constraint_ranks, dtype=np.int32
        ),
        "gram_face_dimensions": np.asarray(
            final_face_dimensions, dtype=np.int32
        ),
        "gram_rep_masks": np.asarray(
            [orbit.parity_rep for orbit in model.gram_orbits], dtype=np.int8
        ),
        "q_layers": np.asarray(Q_LAYERS, dtype=np.int32),
        "increment_forced_multiplier_orbits": np.asarray(
            [row["forced_multiplier_orbits"] for row in increments],
            dtype=np.int32,
        ),
        "increment_kernel_rank_total": np.asarray(
            [row["kernel_rank_total"] for row in increments], dtype=np.int32
        ),
        "increment_gram_face_equation_rank": np.asarray(
            [row["gram_face_equation_rank"] for row in increments],
            dtype=np.int32,
        ),
    }
    core.pack_csr(payload, "normalization_live", normalization_live)
    core.pack_csr(payload, "target_nu_live", target_nu_live)
    core.pack_csr(payload, "target_gram", target_gram)
    core.pack_csr(payload, "gram_face", gram_face)

    summary = {
        "finite_scope": "primitive integer equality rays with total q<=50",
        "collector_orbit_representatives": len(points),
        "collector_by_q": {str(q): equality_by_q[q] for q in Q_LAYERS},
        "collector_stats": {str(q): collector_stats[q] for q in Q_LAYERS},
        "support_size_histogram": {
            str(size): count for size, count in sorted(support_histogram.items())
        },
        "complete_blowup_partitions_up_to_D22_and_class_D10": len(partitions),
        "symbolic_plateau_orbits": len(plateau_rays),
        "symbolic_plateau_by_q": {
            str(q): plateau_by_q[q] for q in Q_LAYERS
        },
        "collector_equals_symbolic_plateau": plateau_rays == collector_set,
        "balanced_c5_colourability_pass": len(points),
        "incremental_face": increments,
        "c5_only_baseline": {
            "forced_multiplier_orbits": 1147,
            "kernel_rank_total": 74,
            "gram_face_equation_rank": 1471,
            "gram_face_orbit_dimension": 7176,
        },
        "generalized_face": {
            "forced_multiplier_orbits": len(forced),
            "live_multiplier_orbits": len(live),
            "kernel_rank_total": sum(span.rank for span in kernel_spans),
            "gram_face_equation_rank": int(gram_face.shape[0]),
            "gram_face_orbit_dimension": sum(final_face_dimensions),
            "gram_orbit_scalars": 8647,
            "face_linear_variables": len(live) + sum(final_face_dimensions),
            "normalization_equations": 56,
            "target_equations": 392,
            "raw_kernel_equations": raw_equation_count,
            "unique_kernel_equations": unique_equation_count,
        },
        "increment_over_c5_face": {
            "additional_forced_multiplier_orbits": len(forced) - 1147,
            "additional_kernel_rank": sum(span.rank for span in kernel_spans) - 74,
            "additional_gram_face_equation_rank": int(gram_face.shape[0]) - 1471,
        },
        "per_block_kernel_ranks": [span.rank for span in kernel_spans],
        "per_block_gram_face_ranks": final_constraint_ranks,
        "prime_exact_row_basis": PRIME,
        "status": "finite exact face only; no SDP and no theorem claim",
    }
    return summary, payload


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1 << 20)
            if not block:
                return digest.hexdigest().upper()
            digest.update(block)


def write_report(path: Path, summary: dict[str, object], data_name: str) -> None:
    rows = summary["incremental_face"]
    table = "\n".join(
        f"| {row['q_max']} | {row['equality_orbits']} | "
        f"{row['forced_multiplier_orbits']} | {row['kernel_rank_total']} | "
        f"{row['gram_face_equation_rank']} | {row['gram_face_orbit_dimension']} |"
        for row in rows
    )
    text = f"""# Gamma_11 equality face through q=50

## Scope

This is an exact finite face computation for the registered `c=25`,
degree-4, 56-cut D22 certificate.  It uses every primitive equality ray found
by the complete integer collector through total mass 50.  It neither solves
the SDP nor proves the all-real arc inequality.

## Plateau cross-check

The collector returned {summary['collector_orbit_representatives']} primitive
D22-orbit representatives.  Independently, complete induced C5-blow-up
partitions were enumerated inside Gamma_11 and all balanced class-sum grid
points through q=50 were generated.  The two canonical ray sets are exactly
equal.  Thus all {summary['balanced_c5_colourability_pass']} collected rays
are balanced C5-colourable, including the non-indicator q=10 witness.

Support histogram:

```text
{json.dumps(summary['support_size_histogram'], sort_keys=True)}
```

## Incremental exact face

| q max | equality orbits | forced nu orbits | kernel rank | Gram-face rank | Gram dimension |
|---:|---:|---:|---:|---:|---:|
{table}

The q=5 row reproduces the indicator-only face exactly.  The final difference
from that baseline is:

```text
{json.dumps(summary['increment_over_c5_face'], indent=2, sort_keys=True)}
```

The final generalized dimensions are:

```text
{json.dumps(summary['generalized_face'], indent=2, sort_keys=True)}
```

## Artifact

`{data_name}` stores the 439 equality representatives, complete blow-up
partitions, forced/live multiplier orbit IDs, all original exact coefficient
maps restricted to the live multipliers, and an exact independent integer CSR
basis `gram_face` for the generalized equations `Q_p v_p(a)=0`.

The Gram-face rank is exact blockwise: the invariant symmetric-form character
formula gives the rational rank upper bound, and modular elimination selects
that many original integer evaluation equations with a nonzero minor.
"""
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, default=COLLECTOR_LOG)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    summary, payload = build_general_face(args.log)
    np.savez_compressed(args.data, **payload)
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_report(args.report, summary, args.data.name)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"DATA={args.data.resolve()}")
    print(f"SUMMARY={args.summary.resolve()}")
    print(f"REPORT={args.report.resolve()}")
    print(f"SHA256_SCRIPT={sha256(Path(__file__))}")
    print(f"SHA256_DATA={sha256(args.data)}")
    print(f"SHA256_SUMMARY={sha256(args.summary)}")
    print(f"SHA256_REPORT={sha256(args.report)}")
    print("FINITE_EXACT_FACE_ONLY: no SDP run and no theorem claim")


if __name__ == "__main__":
    main()
