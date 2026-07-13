import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

p46 = load("p46_threshold", ROOT / "problems/864/compute/p46/carry_statistics.py")
p84 = load("p84_threshold", ROOT / "problems/864/compute/p84/audit_phase_fourier.py")

def threshold_slacks(folds):
    graph = {(a, c) for a, c, _u, _v in folds}
    by_u = {}
    for a, c, u, _v in folds:
        by_u.setdefault(u, []).append((a, c))
    increments = []
    for u, matching in sorted(by_u.items()):
        left = {a for a, _c in matching}
        right = {c for _a, c in matching}
        induced = sum((a, c) in graph for a in left for c in right)
        increments.append((u, 2 * len(matching) - induced))
    prefix = 0
    min_prefix = 0
    for _u, increment in increments:
        prefix += increment
        min_prefix = min(min_prefix, prefix)
    suffix = 0
    min_suffix = 0
    for _u, increment in reversed(increments):
        suffix += increment
        min_suffix = min(min_suffix, suffix)
    return min_prefix, min_suffix, prefix

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-width", type=int, default=30)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    holes = failures = 0
    minima = {"prefix": 0, "suffix": 0, "total": 0}
    witnesses = {}
    for width in range(1, args.max_width + 1):
        for ruler in p46.sidon_rulers(width):
            p = len(ruler)
            baseline = (3 * p * p - p + 2) // 2
            max_gamma = baseline - width - 2
            if max_gamma < 0:
                continue
            forbidden = p46.forbidden_three_minus_one(ruler)
            z = tuple(sorted(width - x for x in ruler))
            for b in (1, 2):
                for gamma in range(max_gamma + 1):
                    if 2 * width + 2 * gamma + b in forbidden:
                        continue
                    holes += 1
                    B = tuple(gamma + x for x in z)
                    h = gamma + width + 1
                    folds = p84.canonical_folds(B, h)
                    prefix, suffix, total = threshold_slacks(folds)
                    row = {"B": B, "p": p, "h": h, "b": b, "C_S": len(folds), "min_prefix_slack": prefix, "min_suffix_slack": suffix, "total_slack": total}
                    for key, value in (("prefix", prefix), ("suffix", suffix), ("total", total)):
                        if value < minima[key]:
                            minima[key] = value
                            witnesses[key] = row
                    if prefix < 0 or suffix < 0 or total < 0:
                        failures += 1
    result = {"max_width": args.max_width, "literal_holes": holes, "failures": failures, "minimum_slacks": minima, "witnesses": witnesses}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
