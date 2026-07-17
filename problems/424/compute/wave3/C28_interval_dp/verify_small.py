"""Independent literal-set checks for packed_tiled_dp."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXE = HERE / "packed_tiled_dp.exe"
WIDTHS = (1, 7, 65, 1000, 65537)


def literal_supports(A: int, B: int, C: int) -> dict[tuple[int, int, int], set[int]]:
    supports: dict[tuple[int, int, int], set[int]] = {(0, 0, 0): {0}}
    for n in range(1, A + B + C + 1):
        for a in range(max(0, n - B - C), min(A, n) + 1):
            for b in range(max(0, n - a - C), min(B, n - a) + 1):
                c = n - a - b
                values: set[int] = set()
                if a:
                    values.update(2 * x for x in supports[(a - 1, b, c)])
                if b:
                    values.update(3 * x + 1 for x in supports[(a, b - 1, c)])
                if c:
                    values.update(5 * x + 3 for x in supports[(a, b, c - 1)])
                supports[(a, b, c)] = values
    return supports


def packed_count(a: int, b: int, c: int, width: int) -> int:
    command = [
        str(EXE),
        "--a",
        str(a),
        "--b",
        str(b),
        "--c",
        str(c),
        "--tile-bits",
        str(width),
        "--threads",
        "1",
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return int(json.loads(completed.stdout)["count"])


def main() -> None:
    if not EXE.exists():
        raise SystemExit(f"missing executable: {EXE}")
    supports = literal_supports(6, 4, 2)
    comparisons = 0
    for state, support in sorted(supports.items()):
        a, b, c = state
        width = WIDTHS[(a * 15 + b * 3 + c) % len(WIDTHS)]
        observed = packed_count(a, b, c, width)
        if observed != len(support):
            raise AssertionError(
                f"state={state} width={width}: packed={observed}, literal={len(support)}"
            )
        comparisons += 1

    terminal = len(supports[(6, 4, 2)])
    width_results = {}
    for width in WIDTHS:
        observed = packed_count(6, 4, 2, width)
        if observed != terminal:
            raise AssertionError(
                f"terminal width={width}: packed={observed}, literal={terminal}"
            )
        width_results[str(width)] = observed
        comparisons += 1

    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(
        json.dumps(
            {
                "literal_states": len(supports),
                "comparisons": comparisons,
                "terminal_count": terminal,
                "terminal_width_results": width_results,
                "status": "ok",
                "script_sha256": source_hash,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
