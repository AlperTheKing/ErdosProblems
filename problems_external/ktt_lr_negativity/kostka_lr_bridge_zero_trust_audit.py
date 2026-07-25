#!/usr/bin/env python3
"""Zero-trust audit for the dilation-compatible skew-Kostka-to-LR bridge.

This file deliberately does not import code from vendor/kostka or from any
existing tableau implementation.  Its skew-tableau counter is a small
Young-lattice dynamic program written for this audit.  LR values are obtained
from the separately implemented C++ Knutson--Tao hive counter.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import subprocess
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
HIVE = HERE / "engine" / "lr_hive.exe"
KOSTKA = HERE / "vendor" / "kostka" / "target" / "release" / "kostka.exe"


def trim(parts):
    parts = tuple(int(x) for x in parts)
    while parts and parts[-1] == 0:
        parts = parts[:-1]
    return parts


def scale(parts, n):
    return trim(n * x for x in parts)


def is_partition(parts):
    return all(x > 0 for x in parts) and all(a >= b for a, b in zip(parts, parts[1:]))


def partitions(n, max_part=None, max_len=None):
    if n == 0:
        yield ()
        return
    if max_part is None or max_part > n:
        max_part = n
    if max_len is not None and max_len == 0:
        return
    for first in range(max_part, 0, -1):
        next_len = None if max_len is None else max_len - 1
        for tail in partitions(n - first, first, next_len):
            yield (first,) + tail


def compositions(n, max_len):
    if n == 0:
        yield ()
        return
    for length in range(1, min(max_len, n) + 1):
        for cuts in itertools.combinations(range(1, n), length - 1):
            points = (0,) + cuts + (n,)
            yield tuple(points[i + 1] - points[i] for i in range(length))


def contains(outer, inner):
    return all((inner[i] if i < len(inner) else 0) <= outer[i] for i in range(len(outer)))


def extensions_by_horizontal_strip(alpha, outer, strip_size):
    """Enumerate gamma with alpha <= gamma <= outer and gamma/alpha horizontal."""
    length = len(outer)
    upper = []
    for row in range(length):
        ceiling = outer[row] if row == 0 else min(outer[row], alpha[row - 1])
        upper.append(ceiling - alpha[row])
    if strip_size < 0 or strip_size > sum(upper):
        return

    inc = [0] * length

    def rec(row, remaining):
        if row == length:
            if remaining == 0:
                yield tuple(alpha[i] + inc[i] for i in range(length))
            return
        future_capacity = sum(upper[row + 1 :])
        lo = max(0, remaining - future_capacity)
        hi = min(upper[row], remaining)
        for value in range(lo, hi + 1):
            inc[row] = value
            yield from rec(row + 1, remaining - value)

    yield from rec(0, strip_size)


def independent_skew_kostka(outer, inner, weight):
    """Count SSYT through horizontal-strip chains, independently of vendor code."""
    outer = trim(outer)
    inner = trim(inner)
    weight = tuple(x for x in weight if x)
    if not outer or not contains(outer, inner):
        return int(not outer and not inner and not weight)
    if sum(outer) - sum(inner) != sum(weight):
        return 0
    length = len(outer)
    start = inner + (0,) * (length - len(inner))
    states = {start: 1}
    for strip_size in weight:
        nxt = {}
        for alpha, multiplicity in states.items():
            for gamma in extensions_by_horizontal_strip(alpha, outer, strip_size):
                nxt[gamma] = nxt.get(gamma, 0) + multiplicity
        states = nxt
        if not states:
            return 0
    return states.get(outer, 0)


def bridge_partitions(outer, inner, weight):
    inner = trim(inner)
    weight = tuple(x for x in weight if x)
    W = sum(weight)
    tails = [sum(weight[j:]) for j in range(len(weight))] + [0]
    R = trim(tuple(W + x for x in inner) + tuple(tails[:-1]))
    S = trim((W,) * len(inner) + tuple(tails[1:]))
    return R, S


def assert_bridge_geometry(outer, inner, weight):
    R, S = bridge_partitions(outer, inner, weight)
    assert not R or is_partition(R)
    assert not S or is_partition(S)
    assert contains(R, S)
    assert sum(R) == sum(outer) + sum(S)

    padded_S = S + (0,) * (len(R) - len(S))
    actual = {(r + 1, c) for r in range(len(R)) for c in range(padded_S[r] + 1, R[r] + 1)}
    W = sum(weight)
    tails = [sum(weight[j:]) for j in range(len(weight))] + [0]
    expected = set()
    for r, width in enumerate(inner):
        expected.update((r + 1, W + c) for c in range(1, width + 1))
    for j, width in enumerate(weight):
        expected.update((len(inner) + j + 1, c) for c in range(tails[j + 1] + 1, tails[j] + 1))
    assert actual == expected

    # Every displayed factor uses its own rows and columns.
    components = []
    if inner:
        components.append({(r + 1, W + c) for r, width in enumerate(inner) for c in range(1, width + 1)})
    for j, _ in enumerate(weight):
        components.append({(len(inner) + j + 1, c) for c in range(tails[j + 1] + 1, tails[j] + 1)})
    for i, left in enumerate(components):
        left_rows = {r for r, _ in left}
        left_cols = {c for _, c in left}
        for right in components[i + 1 :]:
            assert left_rows.isdisjoint({r for r, _ in right})
            assert left_cols.isdisjoint({c for _, c in right})
    return R, S


def csv(parts):
    return ",".join(str(x) for x in parts) if parts else "0"


def run_hive_batch(requests):
    lines = [f"{csv(lam)};{csv(mu)};{csv(nu)};1000000000000000000" for lam, mu, nu in requests]
    with tempfile.TemporaryDirectory(prefix="ktt_bridge_audit_") as tmp:
        batch = Path(tmp) / "bridge.batch"
        batch.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
        env = os.environ.copy()
        env.setdefault("LR_HIVE_NODE_CAP", "200000000")
        proc = subprocess.run(
            [str(HIVE), "--batch", str(batch)],
            text=True,
            capture_output=True,
            check=True,
            env=env,
        )
    values = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    assert len(values) == len(requests), (len(values), len(requests), proc.stderr)
    assert all(re.fullmatch(r"[0-9]+", x) for x in values), Counter(values)
    return [int(x) for x in values]


def run_vendor_skew(outer, inner, weight):
    cmd = [
        str(KOSTKA),
        "skew",
        "--lambda",
        csv(outer),
        "--mu",
        csv(inner),
        "--weight",
        csv(weight),
        "--format",
        "json",
    ]
    data = json.loads(subprocess.run(cmd, text=True, capture_output=True, check=True).stdout)
    return int(data["value"])


def parse_display_polynomial(text):
    if text == "0":
        return [Fraction(0)]
    coeffs = {}
    for term in text.split(" + "):
        if "n^" in term:
            prefix, exponent = term.split("n^")
            degree = int(exponent)
        elif term.endswith("n"):
            prefix, degree = term[:-1], 1
        else:
            prefix, degree = term, 0
        if degree and prefix == "":
            coefficient = Fraction(1)
        else:
            prefix = prefix.strip()
            if prefix.startswith("(") and prefix.endswith(")"):
                prefix = prefix[1:-1]
            coefficient = Fraction(prefix)
        coeffs[degree] = coefficient
    degree = max(coeffs)
    return [coeffs.get(i, Fraction(0)) for i in range(degree + 1)]


def eval_poly(coeffs, n):
    value = Fraction(0)
    for coefficient in reversed(coeffs):
        value = value * n + coefficient
    return value


def trim_poly(coeffs):
    coeffs = list(coeffs)
    while len(coeffs) > 1 and coeffs[-1] == 0:
        coeffs.pop()
    return coeffs


def interpolate_from_consecutive_values(values):
    """Newton-forward interpolation, returned in the ordinary monomial basis."""
    differences = list(map(Fraction, values))
    deltas = []
    while differences:
        deltas.append(differences[0])
        differences = [b - a for a, b in zip(differences, differences[1:])]

    result = [Fraction(0)]
    binomial = [Fraction(1)]
    for j, delta in enumerate(deltas):
        if len(result) < len(binomial):
            result += [Fraction(0)] * (len(binomial) - len(result))
        for i, coefficient in enumerate(binomial):
            result[i] += delta * coefficient
        # C(n,j+1) = C(n,j) * (n-j)/(j+1).
        multiplied = [Fraction(0)] * (len(binomial) + 1)
        for i, coefficient in enumerate(binomial):
            multiplied[i] -= coefficient * j
            multiplied[i + 1] += coefficient
        binomial = [x / (j + 1) for x in multiplied]
    return trim_poly(result)


def run_vendor_degree(outer, inner, weight):
    cmd = [str(KOSTKA), "degree", "--lambda", csv(outer), "--mu", csv(inner), "--weight", csv(weight)]
    output = subprocess.run(cmd, text=True, capture_output=True, check=True).stdout.strip()
    match = re.fullmatch(r"degree: ([0-9]+)", output)
    assert match, output
    return int(match.group(1))


def run_vendor_ehrhart(outer, inner, weight, show_values, positive_only):
    cmd = [
        str(KOSTKA),
        "ehrhart",
        "--lambda",
        csv(outer),
        "--mu",
        csv(inner),
        "--weight",
        csv(weight),
        "--show-values",
        str(show_values),
        "--format",
        "json",
    ]
    if positive_only:
        cmd.append("--no-reciprocity")
    return json.loads(subprocess.run(cmd, text=True, capture_output=True, check=True).stdout)


def deterministic_cases():
    candidates = []
    for size in range(3, 9):
        for outer in partitions(size, max_len=4):
            for inner_size in range(1, size):
                for inner in partitions(inner_size, max_len=len(outer)):
                    if not contains(outer, inner):
                        continue
                    W = size - inner_size
                    for weight in compositions(W, 4):
                        if len(inner) + len(weight) > 6:
                            continue
                        value = independent_skew_kostka(outer, inner, weight)
                        if value:
                            key = f"{csv(outer)}/{csv(inner)}|{csv(weight)}"
                            digest = hashlib.sha256(key.encode("ascii")).hexdigest()
                            candidates.append((digest, value, outer, inner, weight))
    nontrivial = sorted((x for x in candidates if x[1] > 1), key=lambda x: x[0])[:96]
    singleton = sorted((x for x in candidates if x[1] == 1), key=lambda x: x[0])[:32]
    chosen = sorted(nontrivial + singleton, key=lambda x: x[0])
    assert len(chosen) == 128
    result = [(outer, inner, weight, value) for _, value, outer, inner, weight in chosen]
    # The README's stale Ehrhart example is also replayed through the LR bridge.
    fixed = ((4, 3, 2, 1), (2, 1), (2, 2, 2, 1))
    result.append((*fixed, independent_skew_kostka(*fixed)))
    return result


def main():
    assert HIVE.is_file(), HIVE
    assert KOSTKA.is_file(), KOSTKA
    cases = deterministic_cases()

    requests = []
    expected = []
    metadata = []
    for outer, inner, weight, base_value in cases:
        R, S = assert_bridge_geometry(outer, inner, weight)
        assert base_value == independent_skew_kostka(outer, inner, weight)
        for n in range(0, 4):
            nR_direct, nS_direct = bridge_partitions(scale(outer, n), scale(inner, n), scale(weight, n))
            assert nR_direct == scale(R, n)
            assert nS_direct == scale(S, n)
        for n in range(1, 4):
            n_outer, n_inner, n_weight = scale(outer, n), scale(inner, n), scale(weight, n)
            count = independent_skew_kostka(n_outer, n_inner, n_weight)
            nR, nS = scale(R, n), scale(S, n)
            requests.append((n_outer, nS, nR))
            expected.append(count)
            metadata.append((outer, inner, weight, R, S, n, count))

    hive_values = run_hive_batch(requests)
    assert hive_values == expected

    vendor_values = []
    for outer, inner, weight, _, _, n, _ in metadata:
        vendor_values.append(run_vendor_skew(scale(outer, n), scale(inner, n), scale(weight, n)))
    assert vendor_values == expected

    records = [
        {
            "lambda": list(outer),
            "beta": list(inner),
            "weight": list(weight),
            "R": list(R),
            "S": list(S),
            "n": n,
            "count": count,
        }
        for outer, inner, weight, R, S, n, count in metadata
    ]
    records_sha = hashlib.sha256(
        json.dumps(records, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()

    # Degree/Ehrhart audit.  The fixed case is the stale README example.
    fixed = ((4, 3, 2, 1), (2, 1), (2, 2, 2, 1))
    poly_pool = [(outer, inner, weight) for outer, inner, weight, _ in cases]
    poly_pool.sort(key=lambda x: hashlib.sha256(repr(x).encode("ascii")).hexdigest())
    poly_cases = [fixed] + [x for x in poly_pool if x != fixed][:63]
    poly_records = []
    for outer, inner, weight in poly_cases:
        # There are (k-1)*L intermediate coordinates and at least k-1 row-sum equations.
        upper_degree = max(0, (len(weight) - 1) * (len(outer) - 1))
        values = [1]
        for n in range(1, upper_degree + 3):
            values.append(independent_skew_kostka(scale(outer, n), scale(inner, n), scale(weight, n)))
        independent_coeffs = interpolate_from_consecutive_values(values[: upper_degree + 1])
        independent_degree = len(independent_coeffs) - 1
        assert all(eval_poly(independent_coeffs, n) == values[n] for n in range(upper_degree + 3))

        reported_degree = run_vendor_degree(outer, inner, weight)
        adaptive = run_vendor_ehrhart(outer, inner, weight, upper_degree + 2, False)
        positive = run_vendor_ehrhart(outer, inner, weight, upper_degree + 2, True)
        adaptive_coeffs = trim_poly(parse_display_polynomial(adaptive["polynomial"]))
        positive_coeffs = trim_poly(parse_display_polynomial(positive["polynomial"]))
        assert adaptive_coeffs == positive_coeffs == independent_coeffs
        assert adaptive_coeffs[0] == 1
        assert reported_degree == adaptive["degree"] == positive["degree"] == independent_degree
        assert [int(x) for x in adaptive["values"]] == values[1:]
        assert [int(x) for x in positive["values"]] == values[1:]
        poly_records.append(
            {
                "lambda": list(outer),
                "beta": list(inner),
                "weight": list(weight),
                "degree_upper_bound": upper_degree,
                "degree": independent_degree,
                "polynomial": adaptive["polynomial"],
                "held_out_n": [upper_degree + 1, upper_degree + 2],
                "held_out_values": [values[upper_degree + 1], values[upper_degree + 2]],
            }
        )

    poly_sha = hashlib.sha256(
        json.dumps(poly_records, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    stale = poly_records[0]
    assert stale["degree"] == 8
    assert stale["polynomial"] == (
        "(1/45)n^8 + (85/336)n^7 + (19/15)n^6 + (89/24)n^5 + "
        "(211/30)n^4 + (431/48)n^3 + (691/90)n^2 + (341/84)n + 1"
    )

    summary = {
        "status": "PASS",
        "base_instances": len(cases),
        "nonpartition_weight_instances": sum(tuple(sorted(w, reverse=True)) != w for _, _, w, _ in cases),
        "bridge_dilations": [1, 2, 3],
        "bridge_evaluations": len(records),
        "tableau_hive_mismatches": 0,
        "tableau_vendor_mismatches": 0,
        "max_bridge_rank": max(len(R) for _, _, _, R, _, _, _ in metadata),
        "max_count": max(expected),
        "bridge_records_sha256": records_sha,
        "ehrhart_instances": len(poly_records),
        "ehrhart_degree_mismatches": 0,
        "ehrhart_polynomial_mismatches": 0,
        "ehrhart_p0_failures": 0,
        "ehrhart_held_out_checks": 2 * len(poly_records),
        "ehrhart_held_out_failures": 0,
        "ehrhart_records_sha256": poly_sha,
        "stale_readme_current": stale,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
