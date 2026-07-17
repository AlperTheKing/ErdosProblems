"""Extract exact product-collision witnesses from the smallest C102 channel."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from math import gcd
from pathlib import Path

from C102_truncated_decoder_verify import offsets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    a0, b0, c0 = 2, 1, 1
    k = 2
    q = 2**a0 * 3**b0 * 5**c0
    ds = offsets(a0 * k, b0 * k, c0 * k)[a0 * k, b0 * k, c0 * k]
    hs = sorted(8 * q**k + d + 1 for d in ds)
    residue_counts = {r: sum(h % 3 == r for h in hs) for r in range(3)}
    selected_residue = 2 if residue_counts[2] >= residue_counts[0] else 0
    assert selected_residue == 2
    selected = [h for h in hs if h % 3 == selected_residue]

    products: dict[int, list[tuple[int, int, int, int]]] = defaultdict(list)
    for left_h in selected:
        u = 2 * left_h - 1
        for right_h in selected:
            v = 3 * right_h - 1
            products[u * v].append((u, v, left_h, right_h))

    collisions = []
    for product, witnesses in sorted(products.items()):
        if len(witnesses) == 1:
            continue
        assert len(witnesses) == 2
        (u1, v1, h1, j1), (u2, v2, h2, j2) = witnesses
        g = gcd(u1, u2)
        reduced_left = (u2 // g, u1 // g)
        assert reduced_left[0] * v2 == reduced_left[1] * v1
        collisions.append(
            {
                "product": str(product),
                "witnesses": [
                    {"u": u1, "v": v1, "left_h": h1, "right_h": j1},
                    {"u": u2, "v": v2, "left_h": h2, "right_h": j2},
                ],
                "reduced_u2_over_u1": {
                    "numerator": reduced_left[0],
                    "denominator": reduced_left[1],
                },
                "left_h_difference": h2 - h1,
                "right_h_difference": j2 - j1,
            }
        )

    edge_count = len(selected) ** 2
    colliding_edge_count = sum(len(w) for w in products.values() if len(w) > 1)
    result = {
        "source": "C102_truncated_decoder_verify.offsets",
        "ray": [a0, b0, c0],
        "Q": q,
        "k": k,
        "selected_residue": selected_residue,
        "selected_size": len(selected),
        "edge_count": edge_count,
        "product_support": len(products),
        "collision_products": len(collisions),
        "colliding_edges": colliding_edge_count,
        "collisions": collisions,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
