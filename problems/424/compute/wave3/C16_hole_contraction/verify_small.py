import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
GENERATOR_PATH = ROOT / "problems/424/compute/generator_b/generate_divisors.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("p424_generator_b", GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def is_allowed(value):
    return value >= 2 and value % 3 != 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.limit < 100_000:
        raise ValueError("limit must be at least 100000")

    generator = load_generator()
    generated_values, _, _ = generator.generate(args.limit)
    generated = set(generated_values)
    spf = generator.smallest_prime_factors(args.limit + 1)

    def admissible_pairs(n):
        pairs = []
        for left in generator.divisors_from_spf(n + 1, spf):
            right = (n + 1) // left
            if 2 <= left < right and is_allowed(left) and is_allowed(right):
                pairs.append((left, right))
        return sorted(pairs)

    missing_prefix = [0] * (args.limit + 1)
    splitless = 0
    reducible = 0
    odd = 0
    seed3_even = 0
    hard = 0
    healed = 0
    forced_hard_fiber_11 = 0
    first_injective_failure = None
    first_hard = None
    snapshot_32 = None

    for n in range(2, args.limit + 1):
        missing_prefix[n] = missing_prefix[n - 1]
        missing = is_allowed(n) and n not in generated
        if missing:
            missing_prefix[n] += 1

        pairs = admissible_pairs(n) if missing else []
        if missing and not pairs:
            splitless += 1
        elif missing:
            reducible += 1
            if n % 2:
                parent = (n + 1) // 2
                assert is_allowed(parent) and parent not in generated
                odd += 1
            else:
                parent = (n + 1) // 3
                if (n + 1) % 3 == 0 and is_allowed(parent) and parent != 3:
                    assert parent not in generated
                    seed3_even += 1
                else:
                    hard += 1
                    if first_hard is None:
                        first_hard = n
                    if (n + 1) % 11 == 0:
                        prime = (n + 1) // 11
                        if (
                            prime >= 5
                            and prime != 11
                            and spf[prime] == prime
                            and prime in generated
                        ):
                            assert len(pairs) == 1
                            assert set(pairs[0]) == {11, prime}
                            forced_hard_fiber_11 += 1

        if n % 2 and n in generated:
            parent = (n + 1) // 2
            if is_allowed(parent) and parent not in generated:
                healed += 1

        half = (n + 1) // 2
        third = (n + 1) // 3
        assert missing_prefix[half] == odd + healed
        assert hard <= healed
        assert reducible <= missing_prefix[half] + missing_prefix[third]
        if reducible > missing_prefix[half] and first_injective_failure is None:
            first_injective_failure = n
        if n == 32:
            snapshot_32 = (missing_prefix[n], splitless, reducible)

    assert first_injective_failure == 32
    assert first_hard == 54
    assert admissible_pairs(54) == [(5, 11)]
    assert 5 in generated and 11 not in generated
    assert 21 not in generated and 41 in generated
    assert 27 in generated and 54 not in generated
    assert snapshot_32 == (13, 7, 6)

    if args.limit == 100_000:
        assert missing_prefix[args.limit] == 26_823
        assert splitless == 11_928
        assert reducible == 14_895
        assert (odd, seed3_even, hard) == (7_741, 2_046, 5_108)
        assert forced_hard_fiber_11 == 350

    payload = {
        "schema_version": 1,
        "algorithm": "independent Python divisor recursion via generator_b",
        "limit": args.limit,
        "missing": missing_prefix[args.limit],
        "splitless": splitless,
        "reducible": reducible,
        "odd_seed2": odd,
        "even_seed3": seed3_even,
        "hard": hard,
        "healed": healed,
        "forced_hard_fiber_11": forced_hard_fiber_11,
        "first_injective_failure": first_injective_failure,
        "first_hard": first_hard,
        "all_cutoff_seed_partition": True,
        "all_cutoff_two_scale": True,
        "local_falsifier": {
            "n": 54,
            "unique_admissible_pair": [5, 11],
            "missing_endpoint": 11,
            "endpoint_seed2_child": 21,
            "endpoint_child_is_missing": True,
            "direct_half": 27,
            "direct_half_is_generated": True,
        },
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
