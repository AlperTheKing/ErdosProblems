"""Exact modular test of the c7=0 low-rank support hypothesis.

No solver is called.  The ten exact block-0 pencil generators are rebuilt
from the sealed affine-dual space.  We compare the stacked row ranks of all
ten generators and of the nine-generator subpencil omitting index 7.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PSD_PATH = HERE / "CODEX_R10_ZERO_NU_BLOCK0_PSD_EXPOSURE.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    helper = load_module("codex_r10_c7_psd_helper", PSD_PATH)
    builder = load_module("codex_r10_c7_base", helper.BASE_PATH)
    row_helpers = load_module("codex_r10_c7_rows", helper.ROW_HELPER_PATH)
    model = builder.build_model()
    blowup = np.load(helper.BLOWUP_PATH, allow_pickle=False)
    space = np.load(helper.SPACE_PATH, allow_pickle=False)
    q_pencil = np.asarray(
        [
            [int(value) for value in row]
            for row in space["block0_q_pencil_decimal"]
        ],
        dtype=np.int64,
    )

    grouped: dict[int, list[list[int]]] = defaultdict(list)
    for encoded in blowup["kernel_rows_json"]:
        block, row = json.loads(str(encoded))
        grouped[int(block)].append([int(value) for value in row])
    orbit = model.gram_orbits[0]
    quotient_dm, denominator, _pivots, free = (
        row_helpers.integer_kernel_parameter(
            grouped[0], len(orbit.basis)
        )
    )
    quotient = np.asarray(
        [
            [int(value) for value in row]
            for row in quotient_dm.to_list()
        ],
        dtype=np.int64,
    )
    if denominator != 24 or quotient.shape != (286, 154):
        raise AssertionError((denominator, quotient.shape, len(free)))

    ids = orbit.entry_ids.astype(np.int64)
    multiplicities = np.bincount(ids.reshape(-1))
    common = int(np.lcm.reduce(multiplicities))
    matrices = []
    for coefficients in q_pencil:
        ambient = (
            coefficients[ids] * (common // multiplicities[ids])
        ).astype(np.int64)
        matrix = quotient.T @ (ambient @ quotient)
        if not np.array_equal(matrix, matrix.T):
            raise AssertionError("nonsymmetric generator")
        matrices.append(matrix)

    primes = (1_000_037, 1_000_039)
    for omitted in (None, 7):
        selected = [
            matrix
            for index, matrix in enumerate(matrices)
            if index != omitted
        ]
        stacked = np.vstack(selected)
        ranks = [
            len(helper.select_rows_mod_prime(stacked, prime)[0])
            for prime in primes
        ]
        print(
            f"omitted={omitted} generators={len(selected)}"
            f" ranks={ranks} kernel_dimensions="
            f"{[154 - rank for rank in ranks]}"
        )

    rank7 = [
        len(helper.select_rows_mod_prime(matrices[7], prime)[0])
        for prime in primes
    ]
    print(f"generator7_ranks={rank7}")


if __name__ == "__main__":
    main()
