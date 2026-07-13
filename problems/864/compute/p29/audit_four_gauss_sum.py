"""Numerical audit for the P29 shifted four-Gauss-sum reduction.

This checks finite instances only.  It is not used as an asymptotic proof.
For prime q it verifies:

* the three-dimensional Fourier identity (21);
* the exact formula when one output frequency is zero;
* maxima for every zero/coincidence pattern among (r,s,t);
* the Gauss-sum formula for Singer coefficients; and
* the projection from all characters of F_(q^3)^* to characters trivial on
  F_q^*.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np


COMPUTE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COMPUTE_DIR / "p12"))

from algebraic_scan import extension_field, singer  # noqa: E402


def collision_label(r: int, s: int, t: int) -> str:
    values = (r, s, t)
    zero_count = sum(x == 0 for x in values)
    multiplicities = sorted(
        Counter(x for x in values if x != 0).values(), reverse=True
    )
    suffix = "+".join(str(x) for x in multiplicities) or "none"
    return f"z{zero_count}_nz{suffix}"


def singer_checks(q: int) -> tuple[int, tuple[int, ...], np.ndarray]:
    v, points, _ = singer(q)
    if v != q * q + q + 1 or len(points) != q + 1:
        raise AssertionError("wrong Singer parameters")
    differences = Counter((x - y) % v for x in points for y in points)
    if differences[0] != q + 1:
        raise AssertionError("wrong zero-difference multiplicity")
    if any(differences[x] != 1 for x in range(1, v)):
        raise AssertionError("not a perfect difference set")
    f = np.zeros(v, dtype=np.float64)
    f[list(points)] = 1.0
    fourier = np.fft.fft(f)
    if abs(fourier[0] - (q + 1)) > 1e-9:
        raise AssertionError("wrong zero Fourier coefficient")
    if np.max(np.abs(np.abs(fourier[1:]) ** 2 - q)) > 1e-8:
        raise AssertionError("Singer flatness failed")
    return v, points, fourier


def formula_21(fourier: np.ndarray, d: int) -> np.ndarray:
    v = len(fourier)
    r, s, t = np.ogrid[:v, :v, :v]
    out = np.zeros((v, v, v), dtype=np.complex128)
    for k in range(v):
        out += (
            fourier[k]
            * fourier[(r - k) % v]
            * fourier[(s - k) % v]
            * fourier[(t - k) % v]
            * np.exp(-2j * np.pi * k * d / v)
        )
    return out / v


def exact_zero_frequency(
    q: int,
    v: int,
    points: tuple[int, ...],
    fourier: np.ndarray,
    d: int,
) -> tuple[np.ndarray, int]:
    reps = [(x, y) for x in points for y in points if (x + y) % v == d]
    if len(reps) > 2:
        raise AssertionError("modular Sidon sum multiplicity exceeded two")
    freq = np.arange(v)
    weighted = np.zeros((v, v), dtype=np.complex128)
    for x, y in reps:
        weighted += np.exp(
            -2j * np.pi * (freq[:, None] * x + freq[None, :] * y) / v
        )
    return q * weighted + fourier[:, None] * fourier[None, :], len(reps)


def fourier_audit(q: int) -> dict[str, object]:
    v, points, fourier = singer_checks(q)
    f = np.zeros(v, dtype=np.float64)
    f[list(points)] = 1.0
    grid = np.arange(v)
    x = grid[:, None, None]
    y = grid[None, :, None]
    z = grid[None, None, :]

    labels = np.empty(v**3, dtype=np.int8)
    label_names = sorted(
        {collision_label(r, s, t) for r in range(v) for s in range(v) for t in range(v)}
    )
    label_to_code = {label: i for i, label in enumerate(label_names)}
    cursor = 0
    for r in range(v):
        for s in range(v):
            for t in range(v):
                labels[cursor] = label_to_code[collision_label(r, s, t)]
                cursor += 1
    indices = {code: np.flatnonzero(labels == code) for code in range(len(label_names))}

    maxima = {
        label: {"absolute_value": -1.0, "witness": None}
        for label in label_names
        if label != "z3_nznone"
    }
    max_formula_error = 0.0
    max_zero_formula_error = 0.0
    max_sum_representations = 0
    check_d = {0, 1, v // 2, v - 1}

    for d in range(v):
        w = (x + y + z - d) % v
        g = f[:, None, None] * f[None, :, None] * f[None, None, :] * f[w]
        transformed = np.fft.fftn(g)

        zero_expected, rep_count = exact_zero_frequency(q, v, points, fourier, d)
        max_sum_representations = max(max_sum_representations, rep_count)
        max_zero_formula_error = max(
            max_zero_formula_error,
            float(np.max(np.abs(transformed[0, :, :] - zero_expected))),
        )

        if d in check_d:
            predicted = formula_21(fourier, d)
            max_formula_error = max(
                max_formula_error, float(np.max(np.abs(transformed - predicted)))
            )

        absolute = np.abs(transformed).ravel()
        for label, code in label_to_code.items():
            if label == "z3_nznone":
                continue
            eligible = indices[code]
            local_pos = int(np.argmax(absolute[eligible]))
            flat_index = int(eligible[local_pos])
            value = float(absolute[flat_index])
            if value > maxima[label]["absolute_value"]:
                r, s, t = np.unravel_index(flat_index, transformed.shape)
                maxima[label] = {
                    "absolute_value": value,
                    "over_q_3_2": value / (q**1.5),
                    "witness": [d, int(r), int(s), int(t)],
                }

    if max_formula_error > 2e-7 or max_zero_formula_error > 2e-7:
        raise AssertionError((max_formula_error, max_zero_formula_error))
    return {
        "q": q,
        "v": v,
        "points": list(points),
        "max_formula_21_error": max_formula_error,
        "max_zero_frequency_formula_error": max_zero_formula_error,
        "max_ordered_sum_representations": max_sum_representations,
        "collision_maxima": maxima,
    }


def field_trace(field, x, q: int):
    return field.add(field.add(x, field.pow(x, q)), field.pow(x, q * q))


def gauss_projection_audit(q: int) -> dict[str, object]:
    field = extension_field(q, 3)
    alpha = field.primitive()
    q3 = q**3
    order = q3 - 1
    v = q * q + q + 1

    powers = []
    value = field.one
    for _ in range(order):
        powers.append(value)
        value = field.mul(value, alpha)
    additive = np.empty(order, dtype=np.complex128)
    for i, value in enumerate(powers):
        trace = field_trace(field, value, q)
        if any(trace[j] != 0 for j in range(1, field.degree)):
            raise AssertionError("trace did not land in the prime field")
        additive[i] = np.exp(2j * np.pi * trace[0] / q)
    gauss = np.fft.fft(additive)
    if abs(gauss[0] + 1) > 1e-8:
        raise AssertionError("trivial Gauss sum is not -1")
    if np.max(np.abs(np.abs(gauss[1:]) ** 2 - q3)) > 2e-7:
        raise AssertionError("nontrivial Gauss magnitudes failed")

    _, points, fourier = singer_checks(q)
    subgroup_indices = np.arange(v) * (q - 1)
    singer_gauss_error = float(
        np.max(np.abs(fourier[1:] - gauss[subgroup_indices[1:]] / q))
    )
    if singer_gauss_error > 2e-7:
        raise AssertionError("Singer/Gauss coefficient formula failed")

    triples = [(1, 1, 1)]
    if v > 3:
        triples.append((1, 1, 2))
    if v > 4:
        triples.append((1, 2, 3))
    max_projection_error = 0.0
    max_katz_normalized_full_sum = 0.0
    samples = []
    all_chars = np.arange(order)
    for r, s, t in triples:
        ar, bs, ct = (r * (q - 1), s * (q - 1), t * (q - 1))
        product = (
            gauss
            * gauss[(ar - all_chars) % order]
            * gauss[(bs - all_chars) % order]
            * gauss[(ct - all_chars) % order]
        )
        restricted_product = product[subgroup_indices]
        for d in sorted({0, 1, v // 2, v - 1}):
            restricted_phase = np.exp(-2j * np.pi * np.arange(v) * d / v)
            restricted = np.sum(restricted_product * restricted_phase)
            full_values = []
            for ell in range(q - 1):
                exponent = d + v * ell
                phase = np.exp(-2j * np.pi * all_chars * exponent / order)
                full_value = np.sum(product * phase)
                full_values.append(full_value)
                max_katz_normalized_full_sum = max(
                    max_katz_normalized_full_sum,
                    float(abs(full_value) / (order * q3**1.5)),
                )
            projected = sum(full_values) / (q - 1)
            error = float(abs(restricted - projected))
            max_projection_error = max(max_projection_error, error)
            samples.append({"rst": [r, s, t], "d": d, "error": error})

    if max_projection_error > 2e-5:
        raise AssertionError("character-subgroup projection failed")
    return {
        "q": q,
        "field_order": q3,
        "multiplicative_order": order,
        "singer_gauss_error": singer_gauss_error,
        "max_projection_error": max_projection_error,
        "max_abs_full_sum_over_order_Q_3_2": max_katz_normalized_full_sum,
        "samples": samples,
        "points": list(points),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", nargs="+", type=int, default=[2, 3, 5, 7])
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("audit_results.json"),
    )
    args = parser.parse_args()
    if any(q not in (2, 3, 5, 7, 11, 13) for q in args.q):
        raise ValueError("this audit currently accepts small prime q only")

    result = {
        "scope": "finite normalization audit, not an asymptotic proof",
        "fourier_audits": [fourier_audit(q) for q in args.q],
        "gauss_projection_audits": [gauss_projection_audit(q) for q in args.q],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
