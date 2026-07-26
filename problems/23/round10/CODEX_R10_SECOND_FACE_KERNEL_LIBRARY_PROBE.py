"""Match exact derivative rows against numerical quotient-kernel subspaces.

The candidate library contains:

* support-preserving first derivatives of the weighted Gram evaluation rows;
* one-sided boundary evaluation rows when one parity coordinate enters.

Every row is exact integer data derived from the sealed equality rays through
q=20 and all D22 images.  The SCS point is used only to rank candidates by a
normalized matrix-vector residual.  Modular ranks are exact.

No solver is called and no file is written.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "CODEX_R10_g11_d22_sdp.py"
EQUALITY_SOURCE_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY.py"
BLOWUP_PATH = HERE / "CODEX_R10_BLOWUP_FACE_data.npz"
EQUALITY_PATH = HERE / "CODEX_R10_c5_FACE_EQUALITY_data.npz"
SCS_PATH = HERE / "CODEX_R10_g11_d22_reduced_sdp_scs_numeric.npz"
PRIME = 1_000_003


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def primitive(row):
    values = [int(value) for value in row]
    divisor = 0
    for value in values:
        divisor = math.gcd(divisor, abs(value))
    if divisor:
        values = [value // divisor for value in values]
    first = next((value for value in values if value), 0)
    if first < 0:
        values = [-value for value in values]
    return tuple(values)


class ModularSpan:
    def __init__(self, width: int):
        self.width = width
        self.rows: dict[int, dict[int, int]] = {}

    def add(self, source) -> bool:
        row = {
            index: int(value) % PRIME
            for index, value in enumerate(source)
            if int(value) % PRIME
        }
        while row:
            pivot = min(row)
            base = self.rows.get(pivot)
            if base is None:
                inverse = pow(row[pivot], PRIME - 2, PRIME)
                self.rows[pivot] = {
                    index: value * inverse % PRIME
                    for index, value in row.items()
                    if value * inverse % PRIME
                }
                return True
            factor = row[pivot]
            for index, value in base.items():
                updated = (row.get(index, 0) - factor * value) % PRIME
                if updated:
                    row[index] = updated
                else:
                    row.pop(index, None)
        return False

    @property
    def rank(self):
        return len(self.rows)


def value_row(basis, parity, point):
    if any(parity[index] and point[index] == 0 for index in range(11)):
        return None
    row = []
    for exponent in basis:
        value = 1
        for index in range(11):
            power = (exponent[index] - parity[index]) // 2
            value *= point[index] ** power
        row.append(value)
    return tuple(row)


def derivative_row(basis, parity, point, direction):
    if any(parity[index] and point[index] == 0 for index in range(11)):
        return None
    output = []
    for exponent in basis:
        quotient = tuple(
            (exponent[index] - parity[index]) // 2
            for index in range(11)
        )
        constant = 1
        linear = 0
        for power, value, delta in zip(quotient, point, direction):
            factor0 = value**power
            factor1 = (
                power * value ** (power - 1) * delta if power else 0
            )
            linear = linear * factor0 + constant * factor1
            constant *= factor0
        output.append(linear)
    if not any(output):
        return None
    return tuple(output)


def main() -> None:
    builder = load_module("codex_r10_kernel_library_builder", BASE_PATH)
    equality_core = load_module(
        "codex_r10_kernel_library_equality", EQUALITY_SOURCE_PATH
    )
    model = builder.build_model()
    blowup = np.load(BLOWUP_PATH, allow_pickle=False)
    equality = np.load(EQUALITY_PATH, allow_pickle=False)
    scs = np.load(SCS_PATH, allow_pickle=False)

    existing = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        existing[int(block)].append(tuple(map(int, row)))

    points = set()
    for representative in equality["equality_representatives"]:
        if int(np.sum(representative)) > 20:
            continue
        point = tuple(map(int, representative))
        for element in builder.GROUP:
            points.add(equality_core.vector_image(point, element))

    candidates = [set() for _ in model.gram_orbits]
    labels = [dict() for _ in model.gram_orbits]
    for point in sorted(points):
        support = [index for index, value in enumerate(point) if value]
        outside = [index for index, value in enumerate(point) if not value]
        reference = support[-1]
        for block, orbit in enumerate(model.gram_orbits):
            for moving in support[:-1]:
                direction = [0] * 11
                direction[moving] = 1
                direction[reference] = -1
                row = derivative_row(
                    orbit.basis, orbit.parity_rep, point, direction
                )
                if row is not None:
                    row = primitive(row)
                    candidates[block].add(row)
                    labels[block].setdefault(
                        row, ("interior", point, tuple(direction))
                    )
            parity_missing = [
                index
                for index, value in enumerate(orbit.parity_rep)
                if value and point[index] == 0
            ]
            if len(parity_missing) == 1:
                entering = parity_missing[0]
                row = value_row(
                    orbit.basis, orbit.parity_rep, point
                )
                # value_row rejects the missing parity coordinate; remove
                # the common x_enter factor before evaluating.
                modified_parity = list(orbit.parity_rep)
                modified_parity[entering] = 0
                row = []
                for exponent in orbit.basis:
                    value = 1
                    for index in range(11):
                        power = (
                            exponent[index] - orbit.parity_rep[index]
                        ) // 2
                        value *= point[index] ** power
                    row.append(value)
                if any(row):
                    row = primitive(row)
                    candidates[block].add(row)
                    labels[block].setdefault(
                        row, ("boundary", point, entering)
                    )

    q = scs["q_full"].astype(float)
    offsets = blowup["gram_offsets"].astype(np.int64)
    dimensions = blowup["gram_qdims"].astype(np.int64)
    thresholds = (1e-12, 1e-10, 1e-8, 1e-6, 1e-4)
    for block, orbit in enumerate(model.gram_orbits):
        if not candidates[block]:
            continue
        q0 = int(offsets[block])
        local = q[q0 : q0 + int(dimensions[block])]
        matrix = local[orbit.entry_ids]
        matrix_norm = max(1.0, float(np.linalg.norm(matrix, 2)))
        scored = []
        for row in candidates[block]:
            vector = np.asarray(row, dtype=float)
            residual = float(
                np.linalg.norm(matrix @ vector)
                / (matrix_norm * np.linalg.norm(vector))
            )
            scored.append((residual, row))
        scored.sort(key=lambda item: item[0])

        base_span = ModularSpan(len(orbit.basis))
        for row in existing.get(block, []):
            if not base_span.add(row):
                raise AssertionError("dependent sealed kernel row")
        old_rank = base_span.rank
        counts = []
        ranks = []
        for threshold in thresholds:
            span = ModularSpan(len(orbit.basis))
            for row in existing.get(block, []):
                span.add(row)
            count = 0
            for residual, row in scored:
                if residual > threshold:
                    break
                count += 1
                span.add(row)
            counts.append(count)
            ranks.append(span.rank - old_rank)
        print(
            f"BLOCK {block} order={len(orbit.basis)}"
            f" old_kernel={old_rank} candidates={len(scored)}"
            f" best={scored[0][0]:.12e}"
            f" counts={counts} added_ranks={ranks}"
        )
        for residual, row in scored[:3]:
            print(
                f"ROW block={block} residual={residual:.12e}"
                f" label={labels[block][row]} row={row}"
            )


if __name__ == "__main__":
    main()
