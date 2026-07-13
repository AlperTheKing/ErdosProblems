"""Find a valid/invalid pair with the same exact single-modulus profile."""

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


def frozen_counter(counter: dict[int, int]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(counter.items()))


def profile_key(z: list[int], gap: int, modulus: int) -> tuple[object, ...]:
    differences, shifted_sums = label_families(z, gap)
    return (
        modulus,
        z[-1],
        gap,
        frozen_counter(residue_counter(z, modulus)),
        frozen_counter(residue_counter(differences, modulus)),
        frozen_counter(residue_counter(shifted_sums, modulus)),
    )


def search(p: int, max_width: int, max_gap: int) -> dict[str, object] | None:
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
                    key = profile_key(z, gap, modulus)
                    old = seen.get(key)
                    if old is not None and old[0] != valid:
                        valid_z = z if valid else old[1]
                        invalid_z = old[1] if valid else z
                        # The profile key already proves equality of the three
                        # residue histograms.  The valid profile also records
                        # the induced aggregate collision counts.  The invalid
                        # twin differs only in how those collisions split into
                        # zero-wrap and nonzero-wrap layers.
                        vp = modulus_profile(valid_z, gap, modulus)
                        return {
                            "p": p,
                            "width": width,
                            "gap": gap,
                            "m": modulus,
                            "valid_z": valid_z,
                            "invalid_z": invalid_z,
                            "invalid_cross_collisions": cross_collisions(invalid_z, gap),
                            "profile": vp,
                            "rulers_scanned": rulers,
                            "profiles_scanned": profiles,
                        }
                    seen[key] = (valid, z)
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, default=4)
    parser.add_argument("--max-width", type=int, default=40)
    parser.add_argument("--max-gap", type=int, default=40)
    args = parser.parse_args()
    print(json.dumps(search(args.p, args.max_width, args.max_gap), sort_keys=True))


if __name__ == "__main__":
    main()
