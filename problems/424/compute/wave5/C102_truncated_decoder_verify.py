"""Independent small replay for the C102 growing-block decoder census."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path


def offsets(a_max: int, b_max: int, c_max: int) -> dict[tuple[int, int, int], set[int]]:
    states: dict[tuple[int, int, int], set[int]] = {(0, 0, 0): {0}}
    for total in range(1, a_max + b_max + c_max + 1):
        for a in range(a_max + 1):
            for b in range(b_max + 1):
                c = total - a - b
                if not 0 <= c <= c_max:
                    continue
                values: set[int] = set()
                if a:
                    values.update(2 * d for d in states[a - 1, b, c])
                if b:
                    values.update(3 * d + 1 for d in states[a, b - 1, c])
                if c:
                    values.update(5 * d + 3 for d in states[a, b, c - 1])
                states[a, b, c] = values
    return states


def ratio(numerator: int, denominator: int) -> dict[str, str | float]:
    return {
        "numerator": str(numerator),
        "denominator": str(denominator),
        "decimal": numerator / denominator,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    a0, b0, c0 = 2, 1, 1
    q = 2**a0 * 3**b0 * 5**c0
    states = offsets(2 * a0, 2 * b0, 2 * c0)
    layers: dict[int, tuple[list[int], list[int], int, int]] = {}
    layer_rows = []
    for k in (1, 2):
        ds = states[a0 * k, b0 * k, c0 * k]
        hs = sorted(8 * q**k + d + 1 for d in ds)
        counts = Counter(h % 3 for h in hs)
        assert counts[1] == 0
        selected_residue = 2 if counts[2] >= counts[0] else 0
        selected = [h for h in hs if h % 3 == selected_residue]
        assert 2 * len(selected) >= len(ds)
        assert all(h > 5 for h in selected)
        us = [2 * h - 1 if selected_residue == 2 else 4 * h - 3 for h in selected]
        vs = [3 * h - 1 for h in selected]
        assert all(u % 3 == 0 for u in us)
        assert all(v % 3 == 2 for v in vs)
        assert set(us).isdisjoint(vs)
        layers[k] = (us, vs, len(ds), selected_residue)
        layer_rows.append(
            {
                "k": k,
                "D": len(ds),
                "selected_residue": selected_residue,
                "selected_size": len(selected),
            }
        )

    audits = []
    for K in (2, 3):
        first_i = (K + 2) // 3
        last_i = 2 * K // 3
        products = Counter(
            u * v
            for i in range(first_i, last_i + 1)
            for u, v in itertools.product(layers[i][0], layers[K - i][1])
        )
        edges = sum(products.values())
        light = []
        for cutoff in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 4096):
            multiplicities = [r for r in products.values() if r <= cutoff]
            edge_mass = sum(multiplicities)
            light.append(
                {
                    "L": cutoff,
                    "support": len(multiplicities),
                    "edge_mass": edge_mass,
                    "edge_fraction": ratio(edge_mass, edges),
                }
            )
        energy = sum(r * r for r in products.values())
        histogram = Counter(products.values())
        audits.append(
            {
                "K": K,
                "i_range": [first_i, last_i],
                "Q_pow_K": q**K,
                "edges": edges,
                "support": len(products),
                "max_multiplicity": max(products.values()),
                "energy": str(energy),
                "edges_over_Q_pow_K": ratio(edges, q**K),
                "support_over_Q_pow_K": ratio(len(products), q**K),
                "energy_over_edges": ratio(energy, edges),
                "multiplicity_histogram": {
                    str(multiplicity): histogram[multiplicity]
                    for multiplicity in sorted(histogram)
                },
                "light_decoder": light,
            }
        )

    result = {
        "ray": "ray_2_1_1",
        "letter_counts": [a0, b0, c0],
        "Q": q,
        "layers": layer_rows,
        "product_audits": audits,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
