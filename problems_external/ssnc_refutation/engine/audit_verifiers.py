#!/usr/bin/env python3
"""Cross-audit the independent scalar and C++ bitset SSNC verifiers."""

from __future__ import annotations

import argparse
from contextlib import nullcontext
import json
import random
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCALAR = HERE / "verify_scalar.py"
BITSET = HERE / "verify_bitset.exe"


def random_graph(rng: random.Random, n: int) -> dict[str, object]:
    rows: list[list[int]] = [[] for _ in range(n)]
    for left in range(n):
        for right in range(left + 1, n):
            relation = rng.randrange(3)
            if relation == 1:
                rows[left].append(right)
            elif relation == 2:
                rows[right].append(left)
    return {"n": n, "out_neighbors": rows}


def invoke(command: list[str], certificate: Path) -> tuple[int, dict[str, object], str]:
    result = subprocess.run(
        [*command, str(certificate)], capture_output=True, text=True, check=False
    )
    if result.stderr:
        raise AssertionError(f"unexpected stderr from {command}: {result.stderr!r}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError(
            f"non-JSON output from {command}: {result.stdout!r}"
        ) from error
    return result.returncode, payload, result.stdout


def normalize(payload: dict[str, object]) -> dict[str, object]:
    # Both programs expose the same mathematical ledger but intentionally use
    # different internal representations and parsers.
    return {
        "status": payload.get("status"),
        "n": payload.get("n"),
        "per_vertex": payload.get("per_vertex"),
        "failing_vertices": payload.get("failing_vertices"),
        "errors": payload.get("errors"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=0x55CC2026)
    parser.add_argument("--max-n", type=int, default=64)
    args = parser.parse_args()
    if args.samples <= 0 or not 1 <= args.max_n <= 512:
        parser.error("samples must be positive and max-n must be in 1..512")
    if not BITSET.exists():
        parser.error(f"missing bitset verifier: {BITSET}")

    rng = random.Random(args.seed)
    temp_root = HERE / "cross_audit_build"
    temp_root.mkdir(exist_ok=True)
    with nullcontext(str(temp_root)) as temp_name:
        certificate = Path(temp_name) / "certificate.json"
        for sample in range(args.samples):
            # Force word-boundary cases regularly; otherwise sample all sizes.
            boundaries = [1, 2, 3, 17, 18, 63, 64]
            n = boundaries[sample % len(boundaries)] if sample < len(boundaries) * 4 else rng.randint(1, args.max_n)
            graph = random_graph(rng, n)
            certificate.write_text(
                json.dumps(graph, separators=(",", ":")), encoding="ascii"
            )
            scalar_code, scalar_payload, scalar_stdout = invoke(
                ["python", str(SCALAR)], certificate
            )
            bitset_code, bitset_payload, bitset_stdout = invoke(
                [str(BITSET)], certificate
            )
            if scalar_code != bitset_code or normalize(scalar_payload) != normalize(bitset_payload):
                failure = Path(temp_name) / f"failure-{sample}.json"
                failure.write_text(json.dumps(graph, indent=2), encoding="ascii")
                raise AssertionError(
                    f"verifier disagreement at sample {sample}, n={n}, file={failure}\n"
                    f"scalar({scalar_code})={scalar_stdout}\n"
                    f"bitset({bitset_code})={bitset_stdout}"
                )

    print(
        json.dumps(
            {
                "status": "CROSS_AUDIT_OK",
                "samples": args.samples,
                "seed": args.seed,
                "max_n": args.max_n,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
