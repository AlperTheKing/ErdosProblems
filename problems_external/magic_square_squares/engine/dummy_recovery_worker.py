#!/usr/bin/env python3
"""Bounded deterministic worker used only by recovery-supervisor tests."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid


def _windows_replace_is_transient(error: OSError, target: Path, temporary: Path) -> bool:
    winerror = getattr(error, "winerror", None)
    if winerror in {32, 33}:  # sharing or lock violation
        return True
    if winerror != 5:
        return False
    try:
        return (
            temporary.parent == target.parent
            and temporary.is_file()
            and not temporary.is_symlink()
        )
    except OSError:
        return False


def atomic_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as target:
            json.dump(value, target, sort_keys=True)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        maximum_attempts = 128 if os.name == "nt" else 1
        for attempt in range(1, maximum_attempts + 1):
            try:
                os.replace(temporary, path)
                return
            except OSError as error:
                transient = os.name == "nt" and _windows_replace_is_transient(error, path, temporary)
                if not transient or attempt == maximum_attempts:
                    raise
                # Jitter avoids phase-lock with a reader repeatedly releasing
                # and reacquiring a non-delete-sharing Windows handle.
                delay = 0.0005 + ((uuid.uuid4().int & 0x1FFF) / 1_000_000.0)
                time.sleep(min(0.008, delay))
        raise AssertionError("atomic replace retry loop fell through")
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--delay", type=float, required=True)
    parser.add_argument("--status", choices=("NO_HIT", "HIT_VERIFIED", "FAILED"), required=True)
    parser.add_argument("--threads", choices=("1",), default="1")
    parser.add_argument("--deadline-unix")
    parser.add_argument("--start")
    parser.add_argument("--forced-exit-code", type=int)
    parser.add_argument("--spawn-grandchild-pids", type=Path)
    args = parser.parse_args()
    if args.spawn_grandchild_pids is not None:
        args.spawn_grandchild_pids.parent.mkdir(parents=True, exist_ok=True)
        child_code = (
            "import json,os,pathlib,subprocess,sys,time;"
            "grandchild=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)']);"
            "path=pathlib.Path(sys.argv[1]);"
            "path.write_text(json.dumps({'child':os.getpid(),'grandchild':grandchild.pid}),encoding='utf-8');"
            "time.sleep(60)"
        )
        subprocess.Popen([
            sys.executable, "-c", child_code, str(args.spawn_grandchild_pids)
        ])
    time.sleep(args.delay)
    value: dict[str, object] = {
        "engine": "dummy_recovery_worker",
        "lane": args.lane,
        "status": args.status,
    }
    if args.status == "HIT_VERIFIED":
        value["verification"] = {"scalar_exit": 0, "independent_exit": 0}
    atomic_json(args.summary, value)
    if args.forced_exit_code is not None:
        return args.forced_exit_code
    return 3 if args.status == "FAILED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
