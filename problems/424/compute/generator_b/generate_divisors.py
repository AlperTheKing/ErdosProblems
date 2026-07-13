import argparse
import hashlib
import json
from pathlib import Path


def smallest_prime_factors(limit):
    spf = list(range(limit + 1))
    if limit >= 1:
        spf[1] = 1
    bound = int(limit**0.5)
    for prime in range(2, bound + 1):
        if spf[prime] != prime:
            continue
        start = prime * prime
        for multiple in range(start, limit + 1, prime):
            if spf[multiple] == multiple:
                spf[multiple] = prime
    return spf


def divisors_from_spf(value, spf):
    factors = []
    current = value
    while current > 1:
        prime = spf[current]
        exponent = 0
        while current % prime == 0:
            current //= prime
            exponent += 1
        factors.append((prime, exponent))
    divisors = [1]
    for prime, exponent in factors:
        base = list(divisors)
        power = 1
        for _ in range(exponent):
            power *= prime
            divisors.extend(divisor * power for divisor in base)
    return divisors


def generate(limit):
    if limit < 1:
        return [], {}, {}
    spf = smallest_prime_factors(limit + 1)
    reached = bytearray(limit + 1)
    parent = {}
    depth = {}
    if limit >= 2:
        reached[2] = 1
        depth[2] = 0
    if limit >= 3:
        reached[3] = 1
        depth[3] = 0

    for value in range(4, limit + 1):
        product = value + 1
        for left in divisors_from_spf(product, spf):
            if left < 2:
                continue
            right = product // left
            if left >= right:
                continue
            if reached[left] and reached[right]:
                reached[value] = 1
                parent[value] = (left, right)
                depth[value] = 1 + max(depth[left], depth[right])
                break
    values = [value for value in range(1, limit + 1) if reached[value]]
    return values, parent, depth


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    values, parent, depth = generate(args.limit)
    payload = {
        "schema_version": 1,
        "algorithm": "exact ascending divisor recursion",
        "limit": args.limit,
        "count": len(values),
        "maximum": values[-1] if values else None,
        "sha256": hashlib.sha256(
            (",".join(map(str, values)) + "\n").encode("ascii")
        ).hexdigest(),
        "values": values,
        "parents": {str(value): pair for value, pair in parent.items()},
        "depths": {str(value): depth[value] for value in values},
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="ascii")
    print(json.dumps({key: value for key, value in payload.items() if key not in {"values", "parents", "depths"}}, indent=2))


if __name__ == "__main__":
    main()

