"""Exact PHT test on the two reconstructible archived R29 abstractions."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SELECTORS = 676
FAMILY_SIZE = 680
NONBASELINE = 679
BASE_SCORE = 30_811
ARCHIVED_DEFECT = 28


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pair(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def main() -> int:
    # Omega_abs is the full 680^676 product.  Coordinate value zero is the
    # archived baseline row and values 1..679 are nonbaseline rows.
    omega_size = FAMILY_SIZE ** SELECTORS
    changed_total = SELECTORS * NONBASELINE * FAMILY_SIZE ** (SELECTORS - 1)

    # Both abstractions match baseline 30811 and every archived Hamming-one
    # value 30813.  A is additive.  B agrees with A except at all-changed
    # tuples, where its score is zero.
    sum_a = BASE_SCORE * omega_size + 2 * changed_total
    all_changed = NONBASELINE ** SELECTORS
    sum_b = sum_a - (BASE_SCORE + 2 * SELECTORS) * all_changed
    threshold = omega_size * (BASE_SCORE - ARCHIVED_DEFECT)
    residual_a = threshold - sum_a
    residual_b = threshold - sum_b
    assert residual_a < 0 < residual_b

    sources = [
        ROOT / "problems" / "23" / "writeup" / "WALL_ATTACK_R29_GPTPRO56.md",
        ROOT / "tmp" / "fanout" / "r29_gate" / "d08" / "audit.py",
        ROOT / "tmp" / "fanout" / "r29_gate" / "d08" / "certificate.json",
        ROOT / "tmp" / "fanout" / "r29_gate" / "d09" / "audit.py",
        ROOT / "tmp" / "fanout" / "r29_gate" / "d05" / "min_cut_certificate.json",
    ]
    payload = {
        "format": "pht-r29-archived-abstractions-v1",
        "scope": "aggregate abstractions only; no 2943-vertex graph constructed",
        "arithmetic": "Python integers and Fraction",
        "omega": {
            "definition": "Omega_abs={0,...,679}^{676}",
            "cardinality": omega_size,
            "cardinalityExpression": "680^676",
            "baseline": [0] * SELECTORS,
        },
        "shore": {
            "owners": ["r", "cL", "cR"],
            "archivedDefect": ARCHIVED_DEFECT,
            "status": "conditional on archived aggregate min-cut cardinalities",
        },
        "models": {
            "A": {
                "score": "30811+2*k for k changed coordinates",
                "scoreSum": sum_a,
                "phtThreshold": threshold,
                "residual": residual_a,
                "normalizedResidual": pair(Fraction(residual_a, omega_size)),
                "phtHolds": False,
            },
            "B": {
                "score": "A except score=0 when all 676 coordinates are changed",
                "scoreSum": sum_b,
                "allChangedMultiplicity": all_changed,
                "phtThreshold": threshold,
                "residual": residual_b,
                "normalizedResidual": pair(Fraction(residual_b, omega_size)),
                "phtHolds": True,
            },
        },
        "conclusion": (
            "the archived R29 abstractions admit opposite PHT verdicts; an "
            "instance-level verdict requires the missing authenticated graph/row data"
        ),
        "sourceSha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
            for path in sources
        },
        "scriptSha256": sha256(Path(__file__)),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["resultSha256"] = hashlib.sha256(encoded).hexdigest()
    output = HERE / "r29_abstractions_result.json"
    output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "output": str(output),
        "modelAResidualSign": -1,
        "modelBResidualSign": 1,
        "resultSha256": payload["resultSha256"],
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
