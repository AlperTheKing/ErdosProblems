"""Add raw Singer residues to stored natural-cut records from their certificates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    records: list[dict[str, object]] = []
    for path in args.inputs:
        for line in path.read_text(encoding="ascii").splitlines():
            record = json.loads(line)
            if record.get("family") != "singer":
                continue
            modulus = int(record["modulus"])
            candidate = record.get("best_below_3p2")
            if not isinstance(candidate, dict):
                raise AssertionError("missing natural-cut certificate")
            base = int(candidate["cut_base"])
            points = [int(value) for value in candidate["points"]]
            residues = sorted((value + base) % modulus for value in points)
            if len(residues) != int(record["size"]):
                raise AssertionError("residue reconstruction changed the set size")
            records.append({**record, "residues": residues})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="ascii",
    )
    print(json.dumps({"output": str(args.output), "records": len(records)}, sort_keys=True))


if __name__ == "__main__":
    main()
