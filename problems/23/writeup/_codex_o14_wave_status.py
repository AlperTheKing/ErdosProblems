#!/usr/bin/env python3
"""Summarize the active/finished Claude O14 wave without running Lean.

The Claude re-gate script streams only aggregate shard counts while the wave is
in progress.  When a phase finishes, the JSON summary contains concrete failure
objects.  This helper is intentionally read-only: it reports the latest console
line, phase counters, and groups any persisted failures by a short error
signature so the next rerun can target the real failure class.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def short_signature(err: str) -> str:
    """Extract a stable-ish first Lean error line from a captured stderr tail."""
    lines = [line.strip() for line in err.splitlines() if line.strip()]
    for line in lines:
        if "error:" in line.lower():
            return line[:240]
    return (lines[0] if lines else "<no error text>")[:240]


def phase_counts(summary: dict) -> dict[str, object]:
    phases = summary.get("phases", {})
    out: dict[str, object] = {}
    for name, value in phases.items():
        if isinstance(value, dict):
            out[name] = {
                key: value.get(key)
                for key in ("ok", "skip", "sec", "files", "hits")
                if key in value
            }
            if "fail" in value:
                fail = value.get("fail") or []
                out[name]["fail_count"] = len(fail)
        else:
            out[name] = value
    return out


def persisted_failures(summary: dict) -> list[tuple[str, dict]]:
    failures: list[tuple[str, dict]] = []
    for phase, value in (summary.get("phases") or {}).items():
        if not isinstance(value, dict):
            continue
        for item in value.get("fail") or []:
            if isinstance(item, dict):
                failures.append((phase, item))
    return failures


def console_tail(console: Path, n: int) -> list[str]:
    if not console.exists():
        return []
    lines = console.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-n:]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("tmp/claude_o14_wave_regate_summary.json"),
    )
    parser.add_argument(
        "--console",
        type=Path,
        default=Path("tmp/claude_o14_wave_regate_console.txt"),
    )
    parser.add_argument("--tail", type=int, default=20)
    args = parser.parse_args()

    if not args.summary.exists():
        print(json.dumps({"error": "summary_missing", "summary": str(args.summary)}, indent=2))
        return 1

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    failures = persisted_failures(summary)
    sig_counts: Counter[str] = Counter()
    modules_by_sig: dict[str, list[str]] = defaultdict(list)
    for phase, item in failures:
        sig = short_signature(str(item.get("err", "")))
        sig_counts[f"{phase}: {sig}"] += 1
        module = str(item.get("module", "<unknown>"))
        if len(modules_by_sig[f"{phase}: {sig}"]) < 10:
            modules_by_sig[f"{phase}: {sig}"].append(module)

    console_lines = console_tail(args.console, args.tail)
    latest_progress = None
    progress_re = re.compile(r"^\[(?P<phase>[^\]]+)\]\s+(?P<done>\d+)/(?:\d+).*fail=(?P<fail>\d+)")
    for line in reversed(console_lines):
        if progress_re.search(line):
            latest_progress = line
            break

    report = {
        "summary": str(args.summary),
        "started": summary.get("started"),
        "finished": summary.get("finished"),
        "all_ok": summary.get("all_ok"),
        "phases": phase_counts(summary),
        "persisted_failure_count": len(failures),
        "failure_signatures": [
            {
                "signature": sig,
                "count": count,
                "sample_modules": modules_by_sig[sig],
            }
            for sig, count in sig_counts.most_common()
        ],
        "latest_progress": latest_progress,
        "console_tail": console_lines,
    }
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
