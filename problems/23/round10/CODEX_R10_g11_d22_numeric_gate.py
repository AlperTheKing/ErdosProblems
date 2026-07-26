"""Independent floating audit for the expanded R10 Gamma_11 D22 warm start.

This script deliberately shares no construction code with
CODEX_R10_g11_d22_sdp.py.  It rebuilds Gamma_11, the 56 cyclic-interval cuts,
all homogeneous monomials, and every coefficient of the Positivstellensatz
identity from the exported Q4-layout pickle.

Passing this audit is numerical steering evidence only.  It is not a proof:
the final acceptance path requires Fraction-valued data and exact PSD checks.
"""

from __future__ import annotations

import pickle
import sys
from fractions import Fraction
from math import factorial
from pathlib import Path

import numpy as np


N = 11
D = 4
DT = 6


def monomials(number_variables: int, degree: int) -> list[tuple[int, ...]]:
    out: list[tuple[int, ...]] = []

    def visit(index: int, remaining: int, prefix: list[int]) -> None:
        if index == number_variables - 1:
            out.append(tuple(prefix + [remaining]))
            return
        for value in range(remaining + 1):
            visit(index + 1, remaining - value, prefix + [value])

    visit(0, degree, [])
    return out


def multinomial(exponent: tuple[int, ...]) -> int:
    result = factorial(sum(exponent))
    for power in exponent:
        result //= factorial(power)
    return result


def edges_gamma_11() -> list[tuple[int, int]]:
    return [
        (u, v)
        for u in range(N)
        for v in range(u + 1, N)
        if 3 * min(v - u, N - (v - u)) > N
    ]


def canonical_mask(side: set[int]) -> int:
    if 0 in side:
        side = set(range(N)) - side
    return sum(1 << (vertex - 1) for vertex in side)


def interval_cuts(edges: list[tuple[int, int]]) -> list[tuple[int, frozenset[int]]]:
    masks = {0}
    for length in range(1, 6):
        for start in range(N):
            masks.add(canonical_mask({(start + offset) % N for offset in range(length)}))
    if len(masks) != 56:
        raise AssertionError(f"independent cut rebuild produced {len(masks)} cuts")
    cuts = []
    for mask in sorted(masks):
        side = {vertex for vertex in range(1, N) if (mask >> (vertex - 1)) & 1}
        mono = frozenset(
            edge_index
            for edge_index, (u, v) in enumerate(edges)
            if (u in side) == (v in side)
        )
        cuts.append((mask, mono))
    return cuts


def main(path: Path) -> None:
    with path.open("rb") as handle:
        certificate = pickle.load(handle)
    if certificate.get("NUMERICAL_ONLY") is not True:
        raise AssertionError("input is not explicitly marked NUMERICAL_ONLY")
    if certificate["n"] != N or certificate["d"] != 2:
        raise AssertionError("wrong graph size or multiplier degree")
    if Fraction(certificate["c"]) != Fraction(25):
        raise AssertionError("wrong fixed c")

    edges = edges_gamma_11()
    cuts = interval_cuts(edges)
    if list(map(tuple, certificate["E"])) != edges:
        raise AssertionError("stored edge set is not Gamma_11")
    if certificate["cuts"] != cuts:
        raise AssertionError("stored cuts are not the 56 cyclic-interval cuts")
    print(f"G1_G2_OK edges={len(edges)} cuts={len(cuts)}")

    multiplier_monomials = monomials(N, D)
    target_monomials = monomials(N, DT)
    target_index = {item: i for i, item in enumerate(target_monomials)}
    nu = certificate["nu"]
    minimum_multiplier = min(float(value) for value in nu.values())
    normalization = np.zeros(len(multiplier_monomials))
    for monomial_index, monomial in enumerate(multiplier_monomials):
        normalization[monomial_index] = sum(
            float(nu.get((cut_index, monomial), 0.0))
            for cut_index in range(len(cuts))
        )
    normalization_rhs = np.array(
        [25 * multinomial(monomial) for monomial in multiplier_monomials],
        dtype=float,
    )
    normalization_residual = float(np.max(np.abs(normalization - normalization_rhs)))
    print(
        f"G3_G4_NUMERIC min_nu={minimum_multiplier:.12e} "
        f"normalization_residual={normalization_residual:.12e}"
    )

    target = np.array([multinomial(alpha) for alpha in target_monomials], dtype=float)
    for (cut_index, monomial), value in nu.items():
        for edge_index in cuts[cut_index][1]:
            u, v = edges[edge_index]
            alpha = list(monomial)
            alpha[u] += 1
            alpha[v] += 1
            target[target_index[tuple(alpha)]] -= float(value)

    gram = np.zeros(len(target_monomials))
    minimum_eigenvalue = float("inf")
    qblocks = certificate["Q"]
    for basis, raw_matrix in qblocks:
        matrix = np.asarray(raw_matrix, dtype=float)
        if matrix.shape != (len(basis), len(basis)):
            raise AssertionError("Gram block shape mismatch")
        symmetry_error = float(np.max(np.abs(matrix - matrix.T)))
        if symmetry_error > 1e-12:
            raise AssertionError(f"nonsymmetric Gram block: {symmetry_error}")
        eigenvalue = (
            float(matrix[0, 0])
            if len(basis) == 1
            else float(np.linalg.eigvalsh(matrix).min())
        )
        minimum_eigenvalue = min(minimum_eigenvalue, eigenvalue)
        for i, left in enumerate(basis):
            for j, right in enumerate(basis):
                alpha = tuple((a + b) // 2 for a, b in zip(left, right))
                gram[target_index[alpha]] += matrix[i, j]
    identity_residual = float(np.max(np.abs(target - gram)))
    print(
        f"G5_G6_NUMERIC blocks={len(qblocks)} "
        f"identity_residual={identity_residual:.12e} "
        f"minimum_eigenvalue={minimum_eigenvalue:.12e}"
    )
    print("NUMERICAL_AUDIT_ONLY: exact rational gate still required")


if __name__ == "__main__":
    default = Path(__file__).with_name("CODEX_R10_g11_d22_numeric.pkl")
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else default)
