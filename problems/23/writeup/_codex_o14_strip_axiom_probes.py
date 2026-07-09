#!/usr/bin/env python3
"""Report or remove generated O14 `#print axioms` probe lines.

Generated proof payloads sometimes keep local audit probes after a successful
build.  They are not part of the proof object and must be absent from final
artifacts.  This helper is read-only by default; pass `--write` to strip only
whole lines whose first token is `#print axioms`.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TARGET = ROOT / "problems/23/lean/Erdos23Delta0/O14/Generated"
PROBE_RE = re.compile(r"^\s*#print\s+axioms\b")


def scan_file(path: Path, write: bool) -> tuple[int, bool]:
    hits = 0
    if not write:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                hits += int(bool(PROBE_RE.match(line)))
        return hits, False

    kept: list[str] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if PROBE_RE.match(line):
                hits += 1
            else:
                kept.append(line)
    if not hits:
        return 0, False
    if write:
        path.write_text("".join(kept), encoding="utf-8", newline="")
    return hits, write


def candidate_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    try:
        proc = subprocess.run(
            ["rg", "-l", r"^\s*#print\s+axioms\b", str(target), "-g", "*.lean"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        return sorted(target.rglob("*.lean"))
    if proc.returncode == 0:
        return [Path(line) for line in proc.stdout.splitlines() if line.strip()]
    if proc.returncode == 1:
        return []
    return sorted(target.rglob("*.lean"))


def rg_counts(target: Path) -> list[tuple[Path, int]] | None:
    if target.is_file():
        hits, _ = scan_file(target, write=False)
        return [(target, hits)] if hits else []
    try:
        proc = subprocess.run(
            ["rg", "--count-matches", r"^\s*#print\s+axioms\b", str(target), "-g", "*.lean"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode == 1:
        return []
    if proc.returncode != 0:
        return None
    out: list[tuple[Path, int]] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        path_text, count_text = line.rsplit(":", 1)
        out.append((Path(path_text), int(count_text)))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    parser.add_argument("--max-report", type=int, default=50)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    target = args.target
    if not args.write:
        counts = rg_counts(target)
        if counts is not None:
            total_hits = sum(count for _, count in counts)
            for path, hits in counts[: args.max_report]:
                print(f"{path.relative_to(ROOT)}:{hits}")
            print(
                f"reported: files={len(counts)} hit_files={len(counts)} probe_lines={total_hits} "
                f"reported_files={min(len(counts), args.max_report)} "
                f"hidden_files={max(0, len(counts) - args.max_report)} touched=0"
            )
            return 1 if total_hits else 0

    files = candidate_files(target)
    total_hits = 0
    hit_files = 0
    touched = 0
    reported = 0
    for path in files:
        hits, did_write = scan_file(path, args.write)
        if hits:
            hit_files += 1
            total_hits += hits
            touched += int(did_write)
            if reported < args.max_report:
                print(f"{path.relative_to(ROOT)}:{hits}")
                reported += 1

    mode = "stripped" if args.write else "reported"
    hidden_files = max(0, hit_files - reported)
    print(
        f"{mode}: files={len(files)} hit_files={hit_files} probe_lines={total_hits} "
        f"reported_files={reported} hidden_files={hidden_files} touched={touched}"
    )
    return 1 if total_hits and not args.write else 0


if __name__ == "__main__":
    raise SystemExit(main())
