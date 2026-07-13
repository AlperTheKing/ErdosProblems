"""Exact diagnostics for selected fully reflected Problem 864 witnesses."""

from __future__ import annotations

import json
from fractions import Fraction


WITNESSES = [
    (5, 30, [0, 1, 3, 8, 12]),
    (9, 116, [0, 1, 3, 11, 15, 20, 36, 43, 49]),
    (10, 152, [0, 1, 6, 10, 23, 26, 34, 41, 53, 55]),
    (11, 191, [0, 1, 4, 6, 14, 30, 41, 50, 62, 69, 84]),
    (12, 238, [0, 2, 6, 18, 21, 28, 29, 60, 69, 74, 94, 107]),
]


def profile(p: int, theta: int, lower: list[int]) -> dict[str, object]:
    assert len(lower) == p and lower[0] == 0 and lower == sorted(lower)
    width = lower[-1]
    points = sorted(width - x for x in lower)
    gap = theta - 2 * width
    assert gap >= 1

    differences = {points[j] - points[i] for i in range(p) for j in range(i + 1, p)}
    shifted_sums = {gap + points[i] + points[j] for i in range(p) for j in range(i, p)}
    assert len(differences) == p * (p - 1) // 2
    assert len(shifted_sums) == p * (p + 1) // 2
    assert differences.isdisjoint(shifted_sums)
    labels = differences | shifted_sums
    assert len(labels) == p * p and min(labels) >= 1 and max(labels) <= theta

    best_cutoff_slack = None
    best_cutoff = None
    best_width_bound = None
    best_width_data = None
    for r in range(1, p):
        selected = [
            points[i + j] - points[i]
            for j in range(1, r + 1)
            for i in range(p - j)
        ]
        m_r = len(selected)
        t_r = sum(selected)
        upper = r * (r + 1) * width // 2
        assert t_r <= upper
        for cutoff in range(1, theta + 2):
            phi = sum(
                max(0, cutoff - gap - points[i] - points[j])
                for i in range(p)
                for j in range(i, p)
            )
            lower = cutoff * m_r - cutoff * (cutoff - 1) // 2 + phi
            slack = t_r - lower
            assert slack >= 0
            if best_cutoff_slack is None or slack < best_cutoff_slack:
                best_cutoff_slack = slack
                best_cutoff = (r, cutoff, t_r, lower, upper, phi)
            denominator = r * (r + 1) // 2
            width_bound = Fraction(lower, denominator)
            if best_width_bound is None or width_bound > best_width_bound:
                best_width_bound = width_bound
                best_width_data = (r, cutoff, lower, phi)

    holes = sorted(set(range(1, theta + 1)) - labels)
    first_above_tw = next((h for h in holes if h > 2 * width), None)
    return {
        "p": p,
        "theta": theta,
        "theta_over_p2": str(Fraction(theta, p * p)),
        "width": width,
        "width_over_p2": str(Fraction(width, p * p)),
        "gap": gap,
        "label_density": str(Fraction(p * p, theta)),
        "holes": len(holes),
        "first_hole_above_2W": first_above_tw,
        "best_cutoff": {
            "r": best_cutoff[0],
            "cutoff": best_cutoff[1],
            "T_r": best_cutoff[2],
            "lower": best_cutoff[3],
            "upper": best_cutoff[4],
            "phi": best_cutoff[5],
            "slack": best_cutoff_slack,
        },
        "best_width_bound": {
            "value": str(best_width_bound),
            "r": best_width_data[0],
            "cutoff": best_width_data[1],
            "lower": best_width_data[2],
            "phi": best_width_data[3],
        },
    }


def main() -> None:
    for witness in WITNESSES:
        print(json.dumps(profile(*witness), sort_keys=True))


if __name__ == "__main__":
    main()
