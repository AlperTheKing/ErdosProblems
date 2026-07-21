#!/usr/bin/env python3
"""Deterministic no-search worker used only by tranche harness tests."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time
import uuid


def atomic_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as target:
        json.dump(value, target, sort_keys=True)
        target.write("\n")
        target.flush()
        os.fsync(target.fileno())
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--delay", type=float, required=True)
    parser.add_argument("--threads", choices=("1",), default="1")
    parser.add_argument(
        "--status", choices=("NO_HIT", "HIT_VERIFIED", "FAILED"), required=True
    )
    args = parser.parse_args()
    time.sleep(args.delay)
    value: dict[str, object] = {
        "engine": "dummy_lane_worker",
        "lane": args.lane,
        "status": args.status,
    }
    if args.status == "HIT_VERIFIED":
        value["verification"] = {"scalar_exit": 0, "independent_exit": 0}
    atomic_json(args.summary, value)
    return 3 if args.status == "FAILED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
