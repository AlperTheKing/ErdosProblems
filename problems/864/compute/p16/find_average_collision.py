"""Find valid/invalid Sidon rulers with matching modulus-average moments."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations


def labels(z: list[int], gap: int) -> tuple[list[int], list[int]]:
    p = len(z)
    d = [z[j] - z[i] for i in range(p) for j in range(i + 1, p)]
    c = [gap + z[i] + z[j] for i in range(p) for j in range(i, p)]
    return d, c


def is_sidon(z: list[int]) -> bool:
    sums = [z[i] + z[j] for i in range(len(z)) for j in range(i, len(z))]
    return len(sums) == len(set(sums))


def cross_count(d: list[int], c: list[int], modulus: int) -> int:
    dh = Counter(x % modulus for x in d)
    ch = Counter(x % modulus for x in c)
    return sum(dh[r] * ch[r] for r in dh)


def search(p: int, max_width: int, max_gap: int, degree: int, subcritical: bool) -> dict[str, object] | None:
    seen: dict[tuple[int, ...], tuple[bool, list[int]]] = {}
    rulers = 0
    profiles = 0
    for width in range(p - 1, max_width + 1):
        for interior in combinations(range(1, width), p - 2):
            z = [0, *interior, width]
            if not is_sidon(z):
                continue
            rulers += 1
            for gap in range(1, max_gap + 1):
                if subcritical and gap + 2 * width >= 3 * p * p:
                    continue
                d, c = labels(z, gap)
                valid = set(d).isdisjoint(c)
                moments = [0] * (degree + 1)
                vector = []
                for modulus in range(p, p * p + 1):
                    value = cross_count(d, c, modulus)
                    vector.append(value)
                    for j in range(degree + 1):
                        moments[j] += modulus**j * value
                profiles += 1
                key = (width, gap, *moments)
                old = seen.get(key)
                if old is not None and old[0] != valid:
                    good = z if valid else old[1]
                    bad = old[1] if valid else z
                    gd, gc = labels(good, gap)
                    bd, bc = labels(bad, gap)
                    return {
                        "p": p,
                        "width": width,
                        "gap": gap,
                        "length": gap + 2 * width,
                        "degree": degree,
                        "moments": moments,
                        "valid_z": good,
                        "invalid_z": bad,
                        "invalid_intersection": sorted(set(bd).intersection(bc)),
                        "valid_vector": [cross_count(gd, gc, m) for m in range(p, p * p + 1)],
                        "invalid_vector": [cross_count(bd, bc, m) for m in range(p, p * p + 1)],
                        "rulers_scanned": rulers,
                        "profiles_scanned": profiles,
                    }
                seen[key] = (valid, z)
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, default=5)
    parser.add_argument("--max-width", type=int, default=35)
    parser.add_argument("--max-gap", type=int, default=20)
    parser.add_argument("--degree", type=int, default=2)
    parser.add_argument("--subcritical", action="store_true")
    args = parser.parse_args()
    print(json.dumps(search(args.p, args.max_width, args.max_gap, args.degree, args.subcritical), sort_keys=True))


if __name__ == "__main__":
    main()
