#!/usr/bin/env python3
"""Exhaust the translation-invariant oriented Cayley templates on Z/18Z.

This is a small structured-family calibration, not a search of all oriented
graphs on 18 vertices and not a proof of SSNC.  Translation invariance forces
the antipodal pairs (difference 9) to be missing.  Minimum outdegree 8 then
forces the connection set to choose exactly one element from each pair
{+k,-k}, 1 <= k <= 8, leaving only 2**8 templates.
"""

from __future__ import annotations

import json


N = 18


def connection_set(mask: int) -> list[int]:
    return sorted(k if (mask >> (k - 1)) & 1 else (-k) % N for k in range(1, 9))


def new_second_offsets(steps: list[int]) -> list[int]:
    direct = set(steps)
    two_step = {(first + second) % N for first in steps for second in steps}
    return sorted(two_step - direct - {0})


def canonical_certificate(steps: list[int]) -> dict[str, object]:
    return {
        "n": N,
        "out_neighbors": [
            sorted((vertex + step) % N for step in steps) for vertex in range(N)
        ],
    }


def main() -> int:
    histogram: dict[int, int] = {}
    best_d2 = N
    best_templates: list[dict[str, object]] = []
    counterexamples: list[dict[str, object]] = []

    for mask in range(1 << 8):
        steps = connection_set(mask)
        n2_offsets = new_second_offsets(steps)
        d2 = len(n2_offsets)
        histogram[d2] = histogram.get(d2, 0) + 1

        template = {
            "mask": mask,
            "new_second_offsets": n2_offsets,
            "steps": steps,
        }
        if d2 < best_d2:
            best_d2 = d2
            best_templates = [template]
        elif d2 == best_d2:
            best_templates.append(template)

        if d2 < 8:
            counterexamples.append(
                {
                    **template,
                    "certificate": canonical_certificate(steps),
                }
            )

    result = {
        "best_d2": best_d2,
        "best_templates": best_templates,
        "counterexample_count": len(counterexamples),
        "counterexamples": counterexamples,
        "d1": 8,
        "d2_histogram": {str(key): histogram[key] for key in sorted(histogram)},
        "family": "translation-invariant oriented Cayley graphs on Z/18Z",
        "status": "HIT" if counterexamples else "NO_HIT_IN_STRUCTURED_FAMILY",
        "templates_checked": 1 << 8,
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
