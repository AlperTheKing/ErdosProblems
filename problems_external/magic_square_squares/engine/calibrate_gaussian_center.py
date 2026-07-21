#!/usr/bin/env python3
"""Compare the compiled Gaussian engine with the independent slow reference."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys


def run_checked(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {command!r}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return completed.stdout


def canonical_lines(output: str) -> list[str]:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in lines:
        json.loads(line)
    return lines


def main() -> int:
    directory = pathlib.Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--engine",
        type=pathlib.Path,
        default=directory / "gaussian_center.exe",
    )
    parser.add_argument(
        "--reference",
        type=pathlib.Path,
        default=directory / "gaussian_center_reference.py",
    )
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=512)
    parser.add_argument("--chunk-size", type=int, default=73)
    arguments = parser.parse_args()

    fast_output = run_checked(
        [
            str(arguments.engine),
            "--inspect",
            "--start",
            str(arguments.start),
            "--end",
            str(arguments.end),
            "--chunk-size",
            str(arguments.chunk_size),
        ]
    )
    reference_output = run_checked(
        [
            sys.executable,
            str(arguments.reference),
            "--start",
            str(arguments.start),
            "--end",
            str(arguments.end),
        ]
    )
    fast_lines = canonical_lines(fast_output)
    reference_lines = canonical_lines(reference_output)
    if fast_lines != reference_lines:
        mismatch = next(
            (
                index
                for index, pair in enumerate(
                    zip(fast_lines, reference_lines, strict=False)
                )
                if len(pair) != 2 or pair[0] != pair[1]
            ),
            min(len(fast_lines), len(reference_lines)),
        )
        fast = fast_lines[mismatch] if mismatch < len(fast_lines) else None
        slow = (
            reference_lines[mismatch]
            if mismatch < len(reference_lines)
            else None
        )
        raise AssertionError(
            f"first mismatch at output index {mismatch}: "
            f"fast={fast!r}, reference={slow!r}"
        )

    canonical = ("\n".join(fast_lines) + "\n").encode("ascii")
    result = {
        "ok": True,
        "start": arguments.start,
        "end": arguments.end,
        "centers": len(fast_lines),
        "sha256": hashlib.sha256(canonical).hexdigest(),
    }
    print(json.dumps(result, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
