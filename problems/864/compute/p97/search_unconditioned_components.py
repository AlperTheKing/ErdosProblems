#!/usr/bin/env python3
"""Search endpoint-normalized Sidon fold systems without the literal hole."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


p46 = load("p46_p97", ROOT / "problems/864/compute/p46/carry_statistics.py")
p84 = load("p84_p97", ROOT / "problems/864/compute/p84/audit_phase_fourier.py")
p96 = load("p96_p97", ROOT / "problems/864/compute/p96/search_component_bound.py")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=30)
    args = parser.parse_args()
    rows = failures = 0
    best = None
    for width in range(1, args.max_width + 1):
        for ruler in p46.sidon_rulers(width):
            p = len(ruler)
            baseline = (3 * p * p - p + 2) // 2
            max_gamma = baseline - width - 2
            if max_gamma < 0:
                continue
            z = tuple(sorted(width - x for x in ruler))
            for gamma in range(max_gamma + 1):
                rows += 1
                B = tuple(gamma + x for x in z)
                h = gamma + width + 1
                folds = p84.canonical_folds(B, h)
                triangles, excess = p96.component_data(folds)
                if excess > 0:
                    failures += 1
                key = (excess, triangles, len(folds))
                if best is None or key > best[0]:
                    best = (key, {
                        "B": B, "p": p, "h": h, "delta": baseline - h,
                        "C_S": len(folds), "T_F": triangles,
                        "maximum_component_excess": excess,
                    })
    print(json.dumps({
        "max_width": args.max_width, "rows": rows, "failures": failures,
        "best": best[1] if best else None,
    }, indent=2))


if __name__ == "__main__":
    main()
