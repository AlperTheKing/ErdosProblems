import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


heap_generator = load(
    "p424_heap", ROOT / "problems/424/compute/generator_a/generate_heap.py"
)
divisor_generator = load(
    "p424_divisors", ROOT / "problems/424/compute/generator_b/generate_divisors.py"
)


def verify_witnesses(values, parents):
    value_set = set(values)
    for value in values:
        if value in (2, 3):
            continue
        left, right = parents[value]
        assert left != right
        assert left in value_set and right in value_set
        assert left < value and right < value
        assert left * right - 1 == value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    values_a, parents_a, depths_a = heap_generator.generate(args.limit)
    values_b, parents_b, depths_b = divisor_generator.generate(args.limit)
    assert values_a == values_b
    verify_witnesses(values_a, parents_a)
    verify_witnesses(values_b, parents_b)
    assert all(value % 3 != 1 for value in values_a)
    expected_prefix = [2, 3, 5, 9, 14, 17, 26]
    assert values_a[: len(expected_prefix)] == expected_prefix
    payload = {
        "schema_version": 1,
        "limit": args.limit,
        "count": len(values_a),
        "maximum_depth_a": max(depths_a.values(), default=0),
        "maximum_depth_b": max(depths_b.values(), default=0),
        "exact_match": True,
        "mod3_invariant": True,
        "prefix_verified": expected_prefix,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
