import argparse
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
GENERATOR_PATH = ROOT / "problems/424/compute/generator_b/generate_divisors.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("p424_generator_b", GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def allowed(n: int) -> bool:
    return n >= 2 and n % 3 != 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    generator = load_generator()
    generated_values, _, _ = generator.generate(args.limit)
    generated = bytearray(args.limit + 1)
    for n in generated_values:
        generated[n] = 1
    spf = generator.smallest_prime_factors(args.limit + 1)

    hole = bytearray(args.limit + 1)
    splitless = bytearray(args.limit + 1)
    reducible = bytearray(args.limit + 1)
    hard = bytearray(args.limit + 1)

    for n in range(2, args.limit + 1):
        if not allowed(n) or generated[n]:
            continue
        hole[n] = 1
        has_pair = False
        for a in generator.divisors_from_spf(n + 1, spf):
            b = (n + 1) // a
            if 2 <= a < b and allowed(a) and allowed(b):
                has_pair = True
                break
        if not has_pair:
            splitless[n] = 1
            continue
        reducible[n] = 1
        if n % 2 == 0:
            easy3 = False
            if (n + 1) % 3 == 0:
                parent = (n + 1) // 3
                easy3 = allowed(parent) and parent != 3
            if not easy3:
                hard[n] = 1

    def prefix(bits: bytearray) -> list[int]:
        out = [0] * len(bits)
        total = 0
        for i, bit in enumerate(bits):
            total += bit
            out[i] = total
        return out

    m_prefix = prefix(hole)
    e_prefix = prefix(splitless)
    r_prefix = prefix(reducible)
    k_prefix = prefix(hard)

    t2_parent = bytearray(args.limit + 1)
    u3_parent = bytearray(args.limit + 1)
    for h in range(2, args.limit + 1):
        if not hole[h]:
            continue
        child2 = 2 * h - 1
        if child2 <= args.limit and generated[child2]:
            t2_parent[h] = 1
        child3 = 3 * h - 1
        if h % 2 == 0 or (child3 <= args.limit and generated[child3]):
            u3_parent[h] = 1

    t2_prefix = prefix(t2_parent)
    u3_prefix = prefix(u3_parent)

    max_abs_residual = 0
    max_delta = -10**18
    first_positive_delta = None
    delta_previous = 0
    prime_jump_count = 0
    first_prime_jumps = []

    for x in range(2, args.limit + 1):
        y = (x + 1) // 2
        z = (x + 1) // 3
        delta = r_prefix[x] - m_prefix[y] - m_prefix[z]
        rhs = k_prefix[x] - t2_prefix[y] - u3_prefix[z]
        residual = delta - rhs
        max_abs_residual = max(max_abs_residual, abs(residual))
        if residual != 0:
            raise AssertionError((x, delta, rhs))
        if delta > max_delta:
            max_delta = delta
        if delta > 0 and first_positive_delta is None:
            first_positive_delta = x

        if x >= 11 * 13 - 1 and (x + 1) % 11 == 0:
            p = (x + 1) // 11
            if p > 11 and p % 3 == 2 and spf[p] == p:
                if not hard[x] or delta - delta_previous != 1:
                    raise AssertionError(("prime jump", x, p, hard[x], delta_previous, delta))
                prime_jump_count += 1
                if len(first_prime_jumps) < 12:
                    first_prime_jumps.append({"p": p, "n": x, "delta": delta})
        delta_previous = delta

    payload = {
        "schema_version": 1,
        "limit": args.limit,
        "generated": len(generated_values),
        "holes": m_prefix[-1],
        "splitless": e_prefix[-1],
        "reducible": r_prefix[-1],
        "hard": k_prefix[-1],
        "T2": t2_prefix[-1],
        "U3": u3_prefix[-1],
        "max_abs_identity_residual": max_abs_residual,
        "max_delta": max_delta,
        "first_positive_delta": first_positive_delta,
        "prime_jump_count": prime_jump_count,
        "first_prime_jumps": first_prime_jumps,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
