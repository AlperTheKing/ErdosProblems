import argparse
import hashlib
import json
from pathlib import Path


ENERGY_FIELDS = (
    "K",
    "source_k",
    "source_pairs",
    "N",
    "distinct_products",
    "E",
    "E_over_N",
    "within_collision_pairs",
    "cross_collision_pairs",
    "max_r",
    "matrix",
    "multiplicity_histogram",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    left = json.loads(args.left.read_text())
    right = json.loads(args.right.read_text())
    assert left["ray"] == right["ray"]
    assert left["base_Q"] == right["base_Q"]
    assert left["tie_policy"] == right["tie_policy"]
    assert left["blocks"] == right["blocks"]
    for field in ENERGY_FIELDS:
        assert left["energy"][field] == right["energy"][field], field
    output = {
        "schema": "C32-partition-equivalence-v1",
        "left": {
            "path": str(args.left),
            "sha256": digest(args.left),
            "bucket_shift": left["energy"]["bucket_shift"],
        },
        "right": {
            "path": str(args.right),
            "sha256": digest(args.right),
            "bucket_shift": right["energy"]["bucket_shift"],
        },
        "checked_energy_fields": list(ENERGY_FIELDS),
        "status": "PASS",
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print("PASS: independent bucket partitions have identical exact energy data")


if __name__ == "__main__":
    main()
