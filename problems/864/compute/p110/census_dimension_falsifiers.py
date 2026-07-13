import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "problems/864/compute/p86"))
import dense_loose_search as p86


def row_for(base):
    B = base.values
    h = B[-1] + 1
    folds, _sums = p86.fold_edges(B, h)
    triangles, _witnesses = p86.loose_triangle_data(folds, 0)
    p = len(B)
    dimension = len(folds) + 4 * p
    encoded = ",".join(map(str, B)).encode("ascii")
    return {
        "B": B,
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "sources": base.sources,
        "p": p,
        "h": h,
        "C_S": len(folds),
        "T_F": triangles,
        "weighted_ambient_dimension": dimension,
        "dimension_excess": triangles - dimension,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    bases, manifests = p86.load_archives()
    failures = []
    maximum_triangles = 0
    for base in bases:
        row = row_for(base)
        maximum_triangles = max(maximum_triangles, row["T_F"])
        if row["dimension_excess"] > 0:
            failures.append(row)
    smallest = min(failures, key=lambda row: (row["p"], row["h"], row["B"]))
    strongest = max(
        failures,
        key=lambda row: (row["dimension_excess"], row["T_F"], -row["p"]),
    )
    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "archive_manifests": manifests,
        "endpoint_systems": len(bases),
        "dimension_failures": len(failures),
        "maximum_T_F": maximum_triangles,
        "failures": sorted(failures, key=lambda row: (row["p"], row["h"], row["B"])),
        "smallest_failure": smallest,
        "strongest_failure": strongest,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
