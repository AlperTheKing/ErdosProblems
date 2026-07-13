"""Run every exact P48 construction audit and write one JSON certificate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_algebraic import (
    bose_audit,
    parabola_carry_audit,
    ruzsa_audit,
    welch_audit,
)
from audit_core import (
    costas_composition_audit,
    separated_union_audit,
    tensor_audit,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-union-span", type=int, default=9)
    parser.add_argument("--max-parabola-prime", type=int, default=43)
    parser.add_argument("--max-bose-prime", type=int, default=13)
    parser.add_argument("--max-ruzsa-prime", type=int, default=43)
    parser.add_argument("--max-welch-prime", type=int, default=31)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("problems/864/compute/p48/audit_results.json"),
    )
    args = parser.parse_args()

    result = {
        "conventions": {
            "diagonal_pair_sums": True,
            "repeated_triple_summands": True,
            "arithmetic": "exact integers; decimals are display-only",
        },
        "tensor": tensor_audit(),
        "costas_composition": costas_composition_audit(),
        "separated_unions": separated_union_audit(args.max_union_span),
        "parabola_carries": parabola_carry_audit(args.max_parabola_prime),
        "bose": bose_audit(args.max_bose_prime),
        "ruzsa": ruzsa_audit(args.max_ruzsa_prime),
        "welch": welch_audit(args.max_welch_prime),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="ascii")
    print("PASS: P48 recursive-construction audit")
    print(
        "guarded unions:",
        result["separated_unions"]["difference_disjoint_pairs"],
        "pairs and",
        result["separated_unions"]["joint_lag_inequalities"],
        "lag inequalities",
    )
    print("output:", args.output)


if __name__ == "__main__":
    main()
