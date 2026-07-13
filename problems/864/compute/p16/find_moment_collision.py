"""Search profile twins that also match low cross-wrap quotient moments."""

from __future__ import annotations

import argparse
import json
import runpy
from itertools import combinations
from pathlib import Path


HERE = Path(__file__).resolve().parent
AUDIT = runpy.run_path(str(HERE / "residue_phase_audit.py"))
is_sidon = AUDIT["is_sidon"]
label_families = AUDIT["label_families"]
residue_counter = AUDIT["residue_counter"]
cross_collisions = AUDIT["cross_collisions"]
modulus_profile = AUDIT["modulus_profile"]


def frozen(counter: dict[int, int]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(counter.items()))


def cross_wrap_moments(differences: list[int], shifted: list[int], modulus: int, degree: int) -> tuple[int, ...]:
    moments = [0] * (degree + 1)
    for d in differences:
        for c in shifted:
            delta = d - c
            if delta % modulus:
                continue
            quotient = delta // modulus
            power = 1
            for j in range(degree + 1):
                moments[j] += power
                power *= quotient
    return tuple(moments)


def key(z: list[int], gap: int, modulus: int, degree: int) -> tuple[object, ...]:
    differences, shifted = label_families(z, gap)
    return (
        modulus,
        z[-1],
        gap,
        frozen(residue_counter(z, modulus)),
        frozen(residue_counter(differences, modulus)),
        frozen(residue_counter(shifted, modulus)),
        cross_wrap_moments(differences, shifted, modulus, degree),
    )


def search(p: int, max_width: int, max_gap: int, degree: int) -> dict[str, object] | None:
    seen: dict[tuple[object, ...], tuple[bool, list[int]]] = {}
    rulers = 0
    profiles = 0
    for width in range(p - 1, max_width + 1):
        for interior in combinations(range(1, width), p - 2):
            z = [0, *interior, width]
            if not is_sidon(z):
                continue
            rulers += 1
            for gap in range(1, max_gap + 1):
                valid = not cross_collisions(z, gap)
                for modulus in range(p, p * p + 1):
                    profiles += 1
                    signature = key(z, gap, modulus, degree)
                    old = seen.get(signature)
                    if old is not None and old[0] != valid:
                        valid_z = z if valid else old[1]
                        invalid_z = old[1] if valid else z
                        return {
                            "p": p,
                            "width": width,
                            "gap": gap,
                            "m": modulus,
                            "moment_degree": degree,
                            "valid_z": valid_z,
                            "invalid_z": invalid_z,
                            "invalid_cross_collisions": cross_collisions(invalid_z, gap),
                            "moments": signature[-1],
                            "valid_profile": modulus_profile(valid_z, gap, modulus),
                            "rulers_scanned": rulers,
                            "profiles_scanned": profiles,
                        }
                    seen[signature] = (valid, z)
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, default=4)
    parser.add_argument("--max-width", type=int, default=50)
    parser.add_argument("--max-gap", type=int, default=50)
    parser.add_argument("--degree", type=int, default=1)
    args = parser.parse_args()
    print(json.dumps(search(args.p, args.max_width, args.max_gap, args.degree), sort_keys=True))


if __name__ == "__main__":
    main()
