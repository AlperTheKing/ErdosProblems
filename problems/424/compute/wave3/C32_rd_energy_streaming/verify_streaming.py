import argparse
import hashlib
import json
from pathlib import Path


FIELDS = (
    "N",
    "distinct_products",
    "E",
    "within_collision_pairs",
    "cross_collision_pairs",
    "max_r",
    "matrix",
    "multiplicity_histogram",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("c26", type=Path)
    parser.add_argument("streams", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    c26 = json.loads(args.c26.read_text())
    reference = {row["K"]: row for row in c26["energies"] if row["status"] == "computed"}
    checks = []
    for path in args.streams:
        data = json.loads(path.read_text())
        energy = data["energy"]
        k = energy["K"]
        ref = reference[k]
        assert data["ray"] == c26["ray"]
        assert data["base_Q"] == c26["base_Q"]
        assert data["tie_policy"] == c26["tie_policy"]
        for block, ref_block in zip(data["blocks"], c26["blocks"]):
            for field in (
                "k",
                "counts",
                "M",
                "W",
                "D",
                "offset_fnv1a64_le",
                "H_G0",
                "H_G2",
                "selected_color",
                "U_size",
                "V_size",
            ):
                assert block[field] == ref_block[field], (path, field)
        assert energy["source_k"] == ref["source_k"]
        assert energy["source_pairs"] == ref["block_pairs"]
        for field in FIELDS:
            assert energy[field] == ref[field], (path, field, energy[field], ref[field])
        assert energy["E_over_N"] == ref["E_over_N"]
        checks.append({"K": k, "path": str(path), "sha256": sha256(path)})

    args.output.write_text(
        json.dumps(
            {
                "schema": "C32-streaming-verification-v1",
                "reference": str(args.c26),
                "reference_sha256": sha256(args.c26),
                "checks": checks,
                "status": "PASS",
            },
            indent=2,
        )
        + "\n"
    )
    print(f"PASS: {len(checks)} streaming energies match C26 exactly")


if __name__ == "__main__":
    main()
