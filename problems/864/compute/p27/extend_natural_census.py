"""Generate larger natural Singer sets and run the P27 all-cut census."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
P12 = HERE.parent / "p12"
sys.path.insert(0, str(P12))
sys.path.insert(0, str(HERE))

from algebraic_scan import singer  # noqa: E402
from census_natural_cuts import audit_record  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=int, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    results = []
    for q in args.parameters:
        modulus, residues, metadata = singer(q)
        record = {
            "family": "singer",
            "parameter": q,
            "modulus": modulus,
            "residues": residues,
            "metadata": metadata,
        }
        result = audit_record(args.output, record)
        results.append(result)
        print(json.dumps(result, sort_keys=True))

    summary = {
        "parameters": args.parameters,
        "records": len(results),
        "cuts": sum(int(row["cuts"]) for row in results),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps({"records": results, "summary": summary}, indent=2, sort_keys=True)
        + "\n",
        encoding="ascii",
    )
    print(json.dumps({"summary": summary}, sort_keys=True))


if __name__ == "__main__":
    main()
