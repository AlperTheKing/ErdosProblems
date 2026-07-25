"""Strict provenance/order wrapper for ``hilbert_hurwitz_audit_v2``.

Version 3 is superseded: it rebound its imported validator before saving the
original.  This version saves the callable first and is the canonical wrapper.
"""

from __future__ import annotations

from fractions import Fraction
import sys

import hilbert_hurwitz_audit_v2 as base


original_validator = base.validated_coefficients


def partition(value):
    if isinstance(value, str):
        values = [part for part in value.split(",") if part.strip()]
    elif isinstance(value, (list, tuple)):
        values = value
    else:
        return None
    try:
        answer = tuple(int(item) for item in values)
    except (TypeError, ValueError):
        return None
    if any(item < 0 for item in answer):
        return None
    if any(answer[i] < answer[i + 1] for i in range(len(answer) - 1)):
        return None
    return answer


def strict_validator(record: dict, stats: dict[str, int]):
    for key in ("triple_rejected", "strict_sample_rejected", "hstar_rejected",
                "explicit_unheldout_rejected", "independent_provenance_records"):
        stats.setdefault(key, 0)
    lam, mu, nu = (partition(record.get(key)) for key in ("lam", "mu", "nu"))
    if lam is None or mu is None or nu is None or sum(lam) + sum(mu) != sum(nu):
        stats["triple_rejected"] += 1
        return None
    if record.get("heldout") is False:
        stats["explicit_unheldout_rejected"] += 1
        return None
    coefficients = original_validator(record, stats)
    if coefficients is None:
        return None
    dimension = next((record[key] for key in ("d", "degree", "dim")
                      if isinstance(record.get(key), int)), len(coefficients) - 1)
    if dimension != len(coefficients) - 1:
        stats["degree_rejected"] += 1
        return None
    hstar = record.get("hstar")
    if isinstance(hstar, list):
        try:
            hstar_values = [int(value) for value in hstar]
        except (TypeError, ValueError):
            stats["hstar_rejected"] += 1
            return None
        if len(hstar_values) < dimension + 1 or any(hstar_values[dimension + 1:]):
            stats["hstar_rejected"] += 1
            return None
    samples = record.get("samples")
    if isinstance(samples, list):
        try:
            expected_values = [Fraction(value) for value in samples]
        except (TypeError, ValueError, ZeroDivisionError):
            stats["strict_sample_rejected"] += 1
            return None
        for n, expected in enumerate(expected_values):
            actual = sum(value * n**power
                         for power, value in enumerate(coefficients))
            if actual != expected:
                stats["strict_sample_rejected"] += 1
                return None
    independent = (
        record.get("agree") is True
        or (isinstance(record.get("engineA"), list)
            and isinstance(record.get("engineB"), list)
            and record["engineA"] == record["engineB"])
        or record.get("engineB_confirmed") is True
        or record.get("two_engine_verified") is True
    )
    if independent:
        stats["independent_provenance_records"] += 1
    return coefficients


base.validated_coefficients = strict_validator


if __name__ == "__main__":
    raise SystemExit(base.main(sys.argv[1]))
