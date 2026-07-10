#!/usr/bin/env python3
"""Build and gate the temporary O14 packed-integer pilots.

All Lean commands are plain `lake env lean` invocations with an exact toolchain
selected through the environment.  The accepted base cache is never modified:
needed dependency oleans are hard-linked into an isolated cache under the pilot
directory, and missing chart support/MS modules are rebuilt there.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable


THIS = Path(__file__).resolve()
ROOT = THIS.parents[3]
FORMAL = ROOT / "formal-conjectures"
LEAN_SRC = ROOT / "problems/23/lean"
PAYLOAD_DIR = LEAN_SRC / "Erdos23Delta0/O14/Generated/ChartPayloads"
KERNEL_SOURCE = LEAN_SRC / "Erdos23Delta0/O14/SparseConePackedInt.lean"
DEFAULT_OUT = ROOT / "tmp/o14_packed_int_pilot"
DEFAULT_BASE_CACHE = ROOT / "tmp/claude_lean_o_base_v1"
TOOLCHAIN = "leanprover/lean4:v4.27.0"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
FORBIDDEN_RE = re.compile(
    rb"\bsorry\b|\badmit\b|\bnative_decide\b|Lean\.ofReduceBool|\bunsafe\b"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_slots(raw: str) -> list[int]:
    slots = sorted({int(part.strip()) for part in raw.split(",") if part.strip()})
    require(slots, "at least one slot is required")
    return slots


def module_name(path: Path, source_root: Path) -> str:
    return ".".join(path.relative_to(source_root).with_suffix("").parts)


def olean_path(cache: Path, module: str) -> Path:
    return cache / Path(*module.split(".")).with_suffix(".olean")


def chart_dependencies(slot: int) -> tuple[Path, list[Path]]:
    prefix = f"Chart{slot:03d}Cone"
    support = PAYLOAD_DIR / f"{prefix}Support.lean"
    shards: list[tuple[int, Path]] = []
    pattern = re.compile(rf"{prefix}MS(\d+)\.lean")
    for path in PAYLOAD_DIR.glob(f"{prefix}MS*.lean"):
        match = pattern.fullmatch(path.name)
        if match:
            shards.append((int(match.group(1)), path))
    shards.sort()
    require(support.exists(), f"missing support source for slot {slot}")
    require(shards, f"missing MS sources for slot {slot}")
    require(
        [index for index, _path in shards] == list(range(len(shards))),
        f"non-contiguous MS sources for slot {slot}",
    )
    return support, [path for _index, path in shards]


def selected_base_olean(relative: Path, slots: set[int]) -> bool:
    text = str(relative).replace("/", "\\")
    chart_root = "Erdos23Delta0\\O14\\Generated\\ChartPayloads\\"
    compact_root = "Erdos23Delta0\\O14\\CompactPilot\\"
    if text.startswith(compact_root):
        return False
    if not text.startswith(chart_root):
        return True
    name = relative.name
    for slot in slots:
        prefix = f"Chart{slot:03d}Cone"
        if name == f"{prefix}Support.olean" or re.fullmatch(
            rf"{prefix}MS\d+\.olean", name
        ):
            return True
    return False


def same_file(left: Path, right: Path) -> bool:
    try:
        return os.path.samefile(left, right)
    except (FileNotFoundError, OSError):
        return False


def prepare_cache_view(
    base_cache: Path, cache: Path, slots: list[int]
) -> dict[str, Any]:
    base_cache = base_cache.resolve()
    cache = cache.resolve()
    require(base_cache.is_dir(), f"base cache missing: {base_cache}")
    require(cache == (DEFAULT_OUT / "olean").resolve() or ROOT in cache.parents,
            "cache must remain inside the workspace")
    linked = 0
    reused = 0
    logical_bytes = 0
    for source in base_cache.rglob("*.olean"):
        relative = source.relative_to(base_cache)
        if not selected_base_olean(relative, set(slots)):
            continue
        destination = cache / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            if same_file(source, destination):
                reused += 1
                logical_bytes += destination.stat().st_size
            continue
        os.link(source, destination)
        linked += 1
        logical_bytes += source.stat().st_size
    return {
        "base_cache": str(base_cache.relative_to(ROOT)),
        "linked_files": linked,
        "reused_links": reused,
        "logical_bytes": logical_bytes,
        "physical_copy_bytes": 0,
    }


def run_lean(
    path: Path,
    source_root: Path,
    cache: Path,
    log_dir: Path,
    timeout: int,
    phase: str,
) -> dict[str, Any]:
    module = module_name(path, source_root)
    output = olean_path(cache, module)
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "lake",
        "env",
        "lean",
        f"--root={source_root}",
        f"--o={output}",
        str(path),
    ]
    env = os.environ.copy()
    env["ELAN_TOOLCHAIN"] = TOOLCHAIN
    env["LEAN_PATH"] = str(cache)
    started = time.time()
    timed_out = False
    try:
        process = subprocess.run(
            command,
            cwd=FORMAL,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        rc = process.returncode
        stdout = process.stdout
        stderr = process.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        rc = -999
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", "replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", "replace")
    combined = stdout + stderr
    ok = rc == 0 and not timed_out and "error:" not in combined.lower()
    log_path = log_dir / f"{module.replace('.', '_')}.txt"
    if combined:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(combined, encoding="utf-8")
    return {
        "phase": phase,
        "module": module,
        "source": str(path.relative_to(ROOT)),
        "source_sha256": sha256_file(path),
        "output": str(output.relative_to(ROOT)),
        "command": command,
        "command_text": subprocess.list2cmdline(command),
        "cwd": str(FORMAL.relative_to(ROOT)),
        "rc": rc,
        "ok": ok,
        "timed_out": timed_out,
        "seconds": round(time.time() - started, 3),
        "source_bytes": path.stat().st_size,
        "olean_bytes": output.stat().st_size if output.exists() else None,
        "olean_sha256": sha256_file(output) if output.exists() else None,
        "log": str(log_path.relative_to(ROOT)) if combined else None,
        "output_tail": "" if ok else combined[-3000:],
    }


def output_is_fresh(path: Path, source_root: Path, cache: Path) -> bool:
    output = olean_path(cache, module_name(path, source_root))
    if not output.exists():
        return False
    if output.stat().st_mtime_ns >= path.stat().st_mtime_ns:
        return True
    prior_path = cache.parent / "build_summary.json"
    if not prior_path.exists():
        return False
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    source_sha = sha256_file(path)
    output_sha = sha256_file(output)
    module = module_name(path, source_root)
    return any(
        event.get("ok") is True
        and event.get("module") == module
        and event.get("source_sha256") == source_sha
        and event.get("olean_sha256") == output_sha
        for event in prior.get("events", [])
    )


def cached_event(
    path: Path,
    source_root: Path,
    cache: Path,
    phase: str,
    reuse_kind: str = "accepted-cache",
) -> dict[str, Any]:
    module = module_name(path, source_root)
    output = olean_path(cache, module)
    require(output.exists(), f"cached output missing: {output}")
    return {
        "phase": phase,
        "module": module,
        "source": str(path.relative_to(ROOT)),
        "source_sha256": sha256_file(path),
        "output": str(output.relative_to(ROOT)),
        "command": None,
        "command_text": None,
        "cwd": None,
        "rc": 0,
        "ok": True,
        "timed_out": False,
        "seconds": 0.0,
        "source_bytes": path.stat().st_size,
        "olean_bytes": output.stat().st_size,
        "olean_sha256": sha256_file(output),
        "log": None,
        "output_tail": "",
        "reuse_kind": reuse_kind,
    }


def run_many(
    paths: Iterable[Path],
    source_root: Path,
    cache: Path,
    log_dir: Path,
    timeout: int,
    phase: str,
    workers: int,
) -> list[dict[str, Any]]:
    ordered = sorted(set(paths))
    if not ordered:
        return []
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                run_lean, path, source_root, cache, log_dir, timeout, phase
            ): path
            for path in ordered
        }
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda event: event["module"])
    return results


def scan_forbidden(paths: Iterable[Path]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for path in sorted(set(paths)):
        data = path.read_bytes()
        for match in FORBIDDEN_RE.finditer(data):
            hits.append({
                "path": str(path.relative_to(ROOT)),
                "token": match.group(0).decode("ascii", "replace"),
                "offset": match.start(),
            })
    return hits


def parse_axioms(text: str) -> list[dict[str, Any]]:
    pattern = re.compile(
        r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", re.MULTILINE
    )
    records: list[dict[str, Any]] = []
    for declaration, body in pattern.findall(text):
        axioms = sorted(part.strip() for part in body.split(",") if part.strip())
        records.append({"declaration": declaration, "axioms": axioms})
    return records


def sum_bytes(paths: Iterable[Path]) -> int:
    return sum(path.stat().st_size for path in set(paths) if path.exists())


def build_metrics(
    slots: list[int],
    emit_summary: dict[str, Any],
    cache: Path,
    source_root: Path,
    kernel_output: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_slot = {int(chart["slot"]): chart for chart in emit_summary["charts"]}
    metrics: list[dict[str, Any]] = []
    for slot in slots:
        chart = by_slot[slot]
        chart_dir = (
            source_root / "Erdos23Delta0/O14/PackedIntPilot" / f"Chart{slot:03d}"
        )
        pilot_sources = sorted(chart_dir.glob("*.lean"))
        payload_sources = [path for path in pilot_sources if path.name != "Probe.lean"]
        support, ms_sources = chart_dependencies(slot)
        dependency_sources = [support, *ms_sources]
        pilot_oleans = [
            olean_path(cache, module_name(path, source_root)) for path in payload_sources
        ]
        probe_olean = olean_path(
            cache, module_name(chart_dir / "Probe.lean", source_root)
        )
        dependency_oleans = [
            olean_path(cache, module_name(path, LEAN_SRC))
            for path in dependency_sources
        ]
        complete = all(path.exists() for path in [*pilot_oleans, *dependency_oleans])
        actual_all_in = (
            sum_bytes([kernel_output, *pilot_oleans, *dependency_oleans])
            if complete
            else None
        )
        threshold = (275 if slot == 0 else 500) * 1024 * 1024
        metrics.append({
            "slot": slot,
            "active_rows": chart["active_rows"],
            "term_occurrences": chart["term_occurrences"],
            "pilot_source_bytes": sum_bytes(payload_sources),
            "dependency_source_bytes": sum_bytes(dependency_sources),
            "kernel_source_bytes": KERNEL_SOURCE.stat().st_size,
            "all_in_source_bytes": sum_bytes(
                [KERNEL_SOURCE, *payload_sources, *dependency_sources]
            ),
            "pilot_olean_bytes": sum_bytes(pilot_oleans),
            "probe_olean_bytes": probe_olean.stat().st_size if probe_olean.exists() else None,
            "dependency_olean_bytes": sum_bytes(dependency_oleans),
            "kernel_olean_bytes": kernel_output.stat().st_size
            if kernel_output.exists() else None,
            "actual_all_in_olean_bytes": actual_all_in,
            "size_threshold_bytes": threshold,
            "size_pass": actual_all_in is not None and actual_all_in <= threshold,
            "complete": complete,
        })

    projection: dict[str, Any] = {
        "method": "Chart000 component source-byte ratios, integer arithmetic rounded up",
        "base_slot": 0,
        "charts": [],
    }
    base = next((metric for metric in metrics if metric["slot"] == 0), None)
    if base and base["complete"] and base["pilot_source_bytes"]:
        for metric in metrics:
            pilot_projected = (
                base["pilot_olean_bytes"] * metric["pilot_source_bytes"]
                + base["pilot_source_bytes"] - 1
            ) // base["pilot_source_bytes"]
            if metric["dependency_olean_bytes"]:
                dependency_projected = metric["dependency_olean_bytes"]
            elif base["dependency_source_bytes"]:
                dependency_projected = (
                    base["dependency_olean_bytes"] * metric["dependency_source_bytes"]
                    + base["dependency_source_bytes"] - 1
                ) // base["dependency_source_bytes"]
            else:
                dependency_projected = 0
            projected = base["kernel_olean_bytes"] + pilot_projected + dependency_projected
            projection["charts"].append({
                "slot": metric["slot"],
                "projected_all_in_olean_bytes": projected,
                "actual_all_in_olean_bytes": metric["actual_all_in_olean_bytes"],
            })
    return metrics, projection


def project_all_charts(
    emit_summary: dict[str, Any], cache: Path, source_root: Path, kernel_output: Path
) -> dict[str, Any]:
    base_dir = source_root / "Erdos23Delta0/O14/PackedIntPilot/Chart000"
    base_rows = sorted(base_dir.glob("Rows*.lean"))
    pairs = []
    for source in base_rows:
        output = olean_path(cache, module_name(source, source_root))
        if output.exists():
            pairs.append((source.stat().st_size, output.stat().st_size))
    require(len(pairs) == len(base_rows) and pairs, "Chart000 row model is incomplete")

    count = len(pairs)
    sum_x = sum(x for x, _y in pairs)
    sum_y = sum(y for _x, y in pairs)
    sum_xx = sum(x * x for x, _y in pairs)
    sum_xy = sum(x * y for x, y in pairs)
    slope_denom = count * sum_xx - sum_x * sum_x
    slope_numer = count * sum_xy - sum_x * sum_y
    require(slope_denom > 0, "degenerate Chart000 row-size model")
    prediction_denom = count * slope_denom

    def ceil_div(numerator: int, denominator: int) -> int:
        return (numerator + denominator - 1) // denominator

    def project_row(source_bytes: int) -> int:
        numerator = (
            slope_numer * (count * source_bytes - sum_x)
            + sum_y * slope_denom
        )
        return max(1, ceil_div(max(0, numerator), prediction_denom))

    base_support, base_ms = chart_dependencies(0)
    base_dep_sources = [base_support, *base_ms]
    base_dep_oleans = [
        olean_path(cache, module_name(path, LEAN_SRC)) for path in base_dep_sources
    ]
    base_dep_source_bytes = sum_bytes(base_dep_sources)
    base_dep_olean_bytes = sum_bytes(base_dep_oleans)
    base_weight_source = base_dir / "Weights.lean"
    base_weight_olean = olean_path(cache, module_name(base_weight_source, source_root))
    base_cone_source = base_dir / "Cone.lean"
    base_cone_olean = olean_path(cache, module_name(base_cone_source, source_root))

    charts = []
    for chart in emit_summary["charts"]:
        slot = int(chart["slot"])
        chart_dir = (
            source_root / "Erdos23Delta0/O14/PackedIntPilot" / f"Chart{slot:03d}"
        )
        row_sources = sorted(chart_dir.glob("Rows*.lean"))
        row_projected = sum(project_row(path.stat().st_size) for path in row_sources)
        row_outputs = [
            olean_path(cache, module_name(path, source_root)) for path in row_sources
        ]
        weight_source = chart_dir / "Weights.lean"
        weight_output = olean_path(cache, module_name(weight_source, source_root))
        if weight_output.exists():
            weight_projected = weight_output.stat().st_size
        else:
            weight_projected = ceil_div(
                base_weight_olean.stat().st_size * weight_source.stat().st_size,
                base_weight_source.stat().st_size,
            )
        cone_source = chart_dir / "Cone.lean"
        cone_output = olean_path(cache, module_name(cone_source, source_root))
        if cone_output.exists():
            cone_projected = cone_output.stat().st_size
        else:
            cone_projected = ceil_div(
                base_cone_olean.stat().st_size * cone_source.stat().st_size,
                base_cone_source.stat().st_size,
            )
        support, ms_sources = chart_dependencies(slot)
        dep_sources = [support, *ms_sources]
        dep_outputs = [
            olean_path(cache, module_name(path, LEAN_SRC)) for path in dep_sources
        ]
        if all(path.exists() for path in dep_outputs):
            dependency_projected = sum_bytes(dep_outputs)
        else:
            dependency_projected = ceil_div(
                base_dep_olean_bytes * sum_bytes(dep_sources), base_dep_source_bytes
            )
        projected = (
            kernel_output.stat().st_size
            + weight_projected
            + row_projected
            + cone_projected
            + dependency_projected
        )
        threshold = (275 if slot == 0 else 500) * 1024 * 1024
        charts.append({
            "slot": slot,
            "weight_olean_bytes": weight_projected,
            "row_olean_bytes": row_projected,
            "cone_olean_bytes": cone_projected,
            "dependency_olean_bytes": dependency_projected,
            "kernel_olean_bytes": kernel_output.stat().st_size,
            "projected_all_in_olean_bytes": projected,
            "threshold_bytes": threshold,
            "projected_size_pass": projected <= threshold,
            "sample_row_shards_built": sum(path.exists() for path in row_outputs),
            "sample_row_olean_bytes": sum_bytes(row_outputs),
        })
    return {
        "method": "integer least-squares fit over all 131 Chart000 row source/olean pairs",
        "rounding": "each row and component is rounded upward to whole bytes",
        "row_model": {
            "samples": count,
            "slope_numerator": slope_numer,
            "slope_denominator": slope_denom,
            "sum_source_bytes": sum_x,
            "sum_olean_bytes": sum_y,
        },
        "charts": charts,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--base-cache", type=Path, default=DEFAULT_BASE_CACHE)
    parser.add_argument("--slots", default="0,66,107")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--rebuild-deps", action="store_true")
    parser.add_argument("--force-pilot", action="store_true")
    args = parser.parse_args()

    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    base_cache = (
        args.base_cache if args.base_cache.is_absolute() else ROOT / args.base_cache
    )
    source_root = out_dir / "src"
    cache = out_dir / "olean"
    log_dir = out_dir / "logs"
    emit_path = out_dir / "emit_summary.json"
    summary_path = out_dir / "build_summary.json"
    slots = parse_slots(args.slots)
    require(1 <= args.workers <= 16, "workers must be in [1, 16]")
    require(args.timeout > 0, "timeout must be positive")
    require(emit_path.exists(), "run the packed-integer emitter first")
    emit_summary = json.loads(emit_path.read_text(encoding="utf-8"))
    require(emit_summary.get("accepted_v108") is True, "emitter did not accept v108")
    emitted_slots = {int(chart["slot"]) for chart in emit_summary["charts"]}
    require(set(slots) <= emitted_slots, "requested slot was not emitted")

    cache.mkdir(parents=True, exist_ok=True)
    cache_view = prepare_cache_view(base_cache, cache, slots)
    events: list[dict[str, Any]] = []

    kernel_event = run_lean(
        KERNEL_SOURCE, LEAN_SRC, cache, log_dir, args.timeout, "kernel"
    )
    events.append(kernel_event)
    if not kernel_event["ok"]:
        raise RuntimeError(f"kernel build failed: {kernel_event['output_tail']}")
    kernel_output = olean_path(cache, module_name(KERNEL_SOURCE, LEAN_SRC))

    support_todo: list[Path] = []
    ms_todo: list[Path] = []
    for slot in slots:
        support, ms_sources = chart_dependencies(slot)
        support_output = olean_path(cache, module_name(support, LEAN_SRC))
        if args.rebuild_deps or not support_output.exists():
            support_todo.append(support)
        else:
            events.append(cached_event(support, LEAN_SRC, cache, "support-cache"))
        for path in ms_sources:
            output = olean_path(cache, module_name(path, LEAN_SRC))
            if args.rebuild_deps or not output.exists():
                ms_todo.append(path)
            else:
                events.append(cached_event(path, LEAN_SRC, cache, "ms-cache"))

    support_events = run_many(
        support_todo, LEAN_SRC, cache, log_dir, args.timeout, "support", args.workers
    )
    events.extend(support_events)
    support_ok = all(event["ok"] for event in support_events)
    if support_ok:
        ms_events = run_many(
            ms_todo, LEAN_SRC, cache, log_dir, args.timeout, "ms", args.workers
        )
        events.extend(ms_events)

    chart_dirs = {
        slot: source_root / "Erdos23Delta0/O14/PackedIntPilot" / f"Chart{slot:03d}"
        for slot in slots
    }
    weight_paths = [chart_dirs[slot] / "Weights.lean" for slot in slots]
    weight_todo: list[Path] = []
    weight_events: list[dict[str, Any]] = []
    for path in weight_paths:
        if not args.force_pilot and output_is_fresh(path, source_root, cache):
            weight_events.append(cached_event(
                path, source_root, cache, "weights-cache", "pilot-resume"
            ))
        else:
            weight_todo.append(path)
    weight_events.extend(run_many(
        weight_todo,
        source_root, cache, log_dir, args.timeout, "weights", args.workers,
    ))
    events.extend(weight_events)
    good_weights = {
        int(re.search(r"Chart(\d+)\.Weights$", event["module"]).group(1))
        for event in weight_events if event["ok"]
    }
    row_paths = [
        path
        for slot in slots if slot in good_weights
        for path in chart_dirs[slot].glob("Rows*.lean")
    ]
    row_todo: list[Path] = []
    row_events: list[dict[str, Any]] = []
    for path in row_paths:
        if not args.force_pilot and output_is_fresh(path, source_root, cache):
            row_events.append(cached_event(
                path, source_root, cache, "rows-cache", "pilot-resume"
            ))
        else:
            row_todo.append(path)
    row_events.extend(run_many(
        row_todo,
        source_root, cache, log_dir, args.timeout, "rows", args.workers
    ))
    events.extend(row_events)

    successful_modules = {event["module"] for event in events if event["ok"]}
    cone_events: list[dict[str, Any]] = []
    for slot in slots:
        row_modules = {
            module_name(path, source_root) for path in chart_dirs[slot].glob("Rows*.lean")
        }
        support, ms_sources = chart_dependencies(slot)
        dep_modules = {module_name(support, LEAN_SRC)} | {
            module_name(path, LEAN_SRC) for path in ms_sources
        }
        if row_modules | dep_modules <= successful_modules:
            cone_events.append(run_lean(
                chart_dirs[slot] / "Cone.lean", source_root, cache, log_dir,
                args.timeout, "cone",
            ))
    events.extend(cone_events)

    probe_events = run_many(
        [
            chart_dirs[int(re.search(r"Chart(\d+)\.Cone$", event["module"]).group(1))]
            / "Probe.lean"
            for event in cone_events if event["ok"]
        ],
        source_root, cache, log_dir, args.timeout, "probe", args.workers,
    )
    events.extend(probe_events)

    relevant_lean = [KERNEL_SOURCE]
    for slot in slots:
        relevant_lean.extend(chart_dirs[slot].glob("*.lean"))
        support, ms_sources = chart_dependencies(slot)
        relevant_lean.extend([support, *ms_sources])
    forbidden_hits = scan_forbidden(relevant_lean)

    axiom_records: list[dict[str, Any]] = []
    for event in probe_events:
        if event["log"]:
            text = (ROOT / event["log"]).read_text(encoding="utf-8")
            for record in parse_axioms(text):
                record["module"] = event["module"]
                axiom_records.append(record)
    axiom_subset_ok = bool(axiom_records) and all(
        set(record["axioms"]) <= ALLOWED_AXIOMS for record in axiom_records
    )
    final_axioms = [
        record for record in axiom_records
        if record["declaration"].endswith("coreODLGoal_of_packedInt")
    ]
    final_axioms_ok = len(final_axioms) == len(probe_events) and all(
        set(record["axioms"]) == ALLOWED_AXIOMS for record in final_axioms
    )

    metrics, projection = build_metrics(
        slots, emit_summary, cache, source_root, kernel_output
    )
    projection = project_all_charts(
        emit_summary, cache, source_root, kernel_output
    )
    build_ok = all(event["ok"] for event in events if event["phase"] != "ms-cache")
    complete_slots = {metric["slot"] for metric in metrics if metric["complete"]}
    size_ok = set(slots) <= complete_slots and all(
        metric["size_pass"] for metric in metrics if metric["slot"] in slots
    )
    gate = {
        "accepted_v108": emit_summary.get("accepted_v108") is True,
        "reconstruction": all(
            chart["weight_reconstruction_equal"]
            and chart["target_reconstruction_equal"]
            and chart["term_reconstruction_equal"]
            and chart["residual_reconstruction_equal"]
            for chart in emit_summary["charts"] if int(chart["slot"]) in slots
        ),
        "plain_lake_env_lean": all(
            event["command"] is None or event["command"][:3] == ["lake", "env", "lean"]
            for event in events
        ),
        "builds": build_ok and len(probe_events) == len(slots),
        "forbidden_tokens": len(forbidden_hits) == 0,
        "allowed_axioms": axiom_subset_ok and final_axioms_ok,
        "size": size_ok,
    }
    gate["pilot_passes"] = all(gate.values())

    summary = {
        "schema": "o14_packed_int_pilot_build_v1",
        "toolchain": TOOLCHAIN,
        "workers": args.workers,
        "timeout_seconds_per_module": args.timeout,
        "cache_view": cache_view,
        "emit_summary": str(emit_path.relative_to(ROOT)),
        "emit_summary_sha256": sha256_file(emit_path),
        "kernel_source_sha256": sha256_file(KERNEL_SOURCE),
        "events": events,
        "event_counts": {
            "total": len(events),
            "ok": sum(event["ok"] for event in events),
            "failed": sum(not event["ok"] for event in events),
            "commands_run": sum(event["command"] is not None for event in events),
        },
        "forbidden_hits": forbidden_hits,
        "axiom_records": axiom_records,
        "allowed_axioms": sorted(ALLOWED_AXIOMS),
        "metrics": metrics,
        "projection": projection,
        "gate": gate,
    }
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "summary": str(summary_path.relative_to(ROOT)),
        "events": summary["event_counts"],
        "metrics": [
            {
                "slot": metric["slot"],
                "all_in_olean_bytes": metric["actual_all_in_olean_bytes"],
                "size_pass": metric["size_pass"],
            }
            for metric in metrics
        ],
        "gate": gate,
    }, sort_keys=True))
    return 0 if gate["pilot_passes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
