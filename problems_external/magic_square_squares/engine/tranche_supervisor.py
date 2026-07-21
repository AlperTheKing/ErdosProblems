#!/usr/bin/env python3
"""Run the frozen 64-lane tranche under one absolute deadline.

The production entry point deliberately has no duration override.  It either
passes every preflight check and starts exactly 64 single-threaded search
engines, or starts none.  A bounded no-hit result is never labelled UNSAT.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback
import uuid
from typing import Any, Iterable, Sequence


SCHEMA_VERSION = 1
PRODUCTION_SECONDS = 8 * 60 * 60
EXPECTED_MANIFEST_SHA256 = (
    "917F8F14729DF6D52D34796253589B22BE88FDC993E8BBB5898CC5FE59888C21"
)
EXPECTED_FAMILIES = {"G": 16, "E": 16, "N": 16, "S": 16}
POLL_SECONDS = 0.25
STATE_HEARTBEAT_SECONDS = 10.0


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(
        f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
    )
    with temporary.open("w", encoding="utf-8", newline="\n") as target:
        json.dump(value, target, sort_keys=True, separators=(",", ":"))
        target.write("\n")
        target.flush()
        os.fsync(target.fileno())
    os.replace(temporary, path)


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return value if isinstance(value, dict) else None


@dataclasses.dataclass(frozen=True)
class LaneSpec:
    lane_id: str
    family: str
    command: tuple[str, ...]
    cwd: Path
    summary_kind: str
    engine_summary: Path
    stdout_path: Path
    stderr_path: Path


@dataclasses.dataclass
class OwnedLane:
    spec: LaneSpec
    process: subprocess.Popen[bytes]
    started_utc: str
    finished_utc: str | None = None
    return_code: int | None = None
    normalized_status: str = "RUNNING"
    raw_status: str | None = None
    status_detail: dict[str, Any] = dataclasses.field(default_factory=dict)


def lane_record(lane: OwnedLane) -> dict[str, Any]:
    return {
        "lane": lane.spec.lane_id,
        "family": lane.spec.family,
        "pid": lane.process.pid,
        "owned": True,
        "single_thread_search": True,
        "command": list(lane.spec.command),
        "cwd": str(lane.spec.cwd),
        "stdout": str(lane.spec.stdout_path),
        "stderr": str(lane.spec.stderr_path),
        "engine_summary": str(lane.spec.engine_summary),
        "started_utc": lane.started_utc,
        "finished_utc": lane.finished_utc,
        "return_code": lane.return_code,
        "status": lane.normalized_status,
        "raw_status": lane.raw_status,
        "status_detail": lane.status_detail,
    }


def production_specs(
    engine_dir: Path, run_dir: Path, deadline_unix: float
) -> list[LaneSpec]:
    """Build exactly the frozen 16 G + 16 E + 16 N + 16 S commands."""
    engine_dir = engine_dir.resolve()
    run_dir = run_dir.resolve()
    python = Path(sys.executable).resolve()
    scalar = (engine_dir / "verify_scalar.py").resolve()
    independent = (engine_dir / "verify_independent.exe").resolve()
    gaussian = (engine_dir / "gaussian_center.exe").resolve()
    elliptic = (engine_dir / "elliptic_integral_search.exe").resolve()
    structural = (engine_dir / "s_lane_search.exe").resolve()

    required = [python, scalar, independent, gaussian, elliptic, structural]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("missing required production file(s): " + "; ".join(missing))

    specs: list[LaneSpec] = []
    center_base = 5_000_000_000_000
    center_step = 1 << 24
    gaussian_chunk_size = 1 << 16

    def common_paths(lane_id: str) -> tuple[Path, Path, Path]:
        lane_dir = run_dir / "lanes" / lane_id
        return (
            lane_dir,
            lane_dir / "process.stdout.txt",
            lane_dir / "process.stderr.txt",
        )

    for number in range(1, 17):
        lane_id = f"G{number:02d}"
        lane_dir, stdout, stderr = common_paths(lane_id)
        start = center_base if number == 1 else center_base + (number - 1) * center_step + 1
        end = center_base + number * center_step
        engine_out = lane_dir / "engine"
        command = (
            str(gaussian), "--mode", "G", "--start", str(start), "--end", str(end),
            "--chunk-size", str(gaussian_chunk_size), "--run-dir", str(engine_out),
            "--scalar-verifier", str(scalar), "--independent-verifier", str(independent),
            "--python", str(python), "--deadline-unix", str(int(deadline_unix)),
        )
        specs.append(LaneSpec(lane_id, "G", command, engine_dir, "standard",
                              engine_out / "summary.json", stdout, stderr))

    for number in range(1, 17):
        lane_id = f"E{number:02d}"
        lane_dir, stdout, stderr = common_paths(lane_id)
        engine_out = lane_dir / "engine"
        command = (
            str(elliptic), "--lane", lane_id, "--x-bound", str(1 << 20),
            "--chunk-count", "1", "--chunk-index", "0",
            "--max-seconds", str(PRODUCTION_SECONDS), "--out-dir", str(engine_out),
            "--python", str(python), "--scalar-verifier", str(scalar),
            "--independent-verifier", str(independent),
        )
        specs.append(LaneSpec(lane_id, "E", command, engine_dir, "standard",
                              engine_out / "summary.json", stdout, stderr))

    for number in range(1, 17):
        lane_id = f"N{number:02d}"
        lane_dir, stdout, stderr = common_paths(lane_id)
        global_number = 16 + number
        start = center_base + (global_number - 1) * center_step + 1
        end = center_base + global_number * center_step
        engine_out = lane_dir / "engine"
        command = (
            str(gaussian), "--mode", "N", "--start", str(start), "--end", str(end),
            "--chunk-size", str(gaussian_chunk_size), "--run-dir", str(engine_out),
            "--scalar-verifier", str(scalar), "--independent-verifier", str(independent),
            "--python", str(python), "--deadline-unix", str(int(deadline_unix)),
        )
        specs.append(LaneSpec(lane_id, "N", command, engine_dir, "standard",
                              engine_out / "summary.json", stdout, stderr))

    for number in range(1, 17):
        lane_id = f"S{number:02d}"
        lane_dir, stdout, stderr = common_paths(lane_id)
        p_min = 2 if number == 1 else (number - 1) * 128 + 1
        p_max = number * 128
        output = lane_dir / "engine.jsonl"
        verification_dir = lane_dir / "verification"
        command = (
            str(structural), "--p-min", str(p_min), "--p-max", str(p_max),
            "--threads", "1", "--time-limit-seconds", str(PRODUCTION_SECONDS),
            "--output", str(output), "--scalar", str(scalar),
            "--independent", str(independent), "--python", str(python),
            "--verification-dir", str(verification_dir),
        )
        specs.append(LaneSpec(lane_id, "S", command, engine_dir, "s_jsonl",
                              output, stdout, stderr))

    validate_specs(specs)
    return specs


def validate_specs(specs: Sequence[LaneSpec]) -> None:
    if len(specs) != 64:
        raise RuntimeError(f"expected exactly 64 lanes, got {len(specs)}")
    ids = [spec.lane_id for spec in specs]
    if len(set(ids)) != 64:
        raise RuntimeError("lane IDs are not unique")
    counts = {family: sum(spec.family == family for spec in specs)
              for family in EXPECTED_FAMILIES}
    if counts != EXPECTED_FAMILIES:
        raise RuntimeError(f"incorrect family counts: {counts}")
    for family, count in EXPECTED_FAMILIES.items():
        expected = {f"{family}{number:02d}" for number in range(1, count + 1)}
        actual = {spec.lane_id for spec in specs if spec.family == family}
        if actual != expected:
            raise RuntimeError(f"incorrect {family} lane IDs")
    for spec in specs:
        command = list(spec.command)
        if spec.family == "S":
            position = command.index("--threads")
            if command[position + 1] != "1":
                raise RuntimeError(f"{spec.lane_id} is not single-threaded")


def parse_json_lines(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (FileNotFoundError, OSError, UnicodeDecodeError):
        return []
    values: list[dict[str, Any]] = []
    for line in lines:
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            values.append(value)
    return values


def normalize_lane_result(spec: LaneSpec) -> tuple[str, str | None, dict[str, Any]]:
    if spec.summary_kind == "s_jsonl":
        values = parse_json_lines(spec.engine_summary)
        summaries = [value for value in values if value.get("type") == "summary"]
        if not summaries:
            return "MISSING_SUMMARY", None, {}
        summary = summaries[-1]
        raw = str(summary.get("status", ""))
        candidates = [value for value in values if value.get("type") == "candidate"]
        dual = [
            value for value in candidates
            if value.get("verified") is True
            and value.get("scalar_verifier", {}).get("accepted") is True
            and value.get("scalar_verifier", {}).get("exit_code") == 0
            and value.get("independent_verifier", {}).get("accepted") is True
            and value.get("independent_verifier", {}).get("exit_code") == 0
        ]
        if raw == "SAT" and summary.get("verified_candidate_count", 0) >= 1 and dual:
            return "HIT_VERIFIED", raw, {"summary": summary, "candidate": dual[0]}
        if raw == "EXHAUSTED":
            return "NO_HIT", raw, {"summary": summary}
        if raw == "TIMEOUT_INCOMPLETE":
            return "TIMEOUT_INCOMPLETE", raw, {"summary": summary}
        if raw in {"VERIFIER_FAILURE", "FAILED", "FAILED_VERIFICATION"}:
            return "FAILED", raw, {"summary": summary}
        return "FAILED", raw, {"summary": summary, "error": "unrecognized S result"}

    summary = read_json(spec.engine_summary)
    if summary is None:
        return "MISSING_SUMMARY", None, {}
    raw = str(summary.get("status", ""))
    if raw == "HIT_VERIFIED":
        verification = summary.get("verification", {})
        if (isinstance(verification, dict)
                and verification.get("scalar_exit") == 0
                and verification.get("independent_exit") == 0):
            return "HIT_VERIFIED", raw, {"summary": summary}
        return "FAILED", raw, {
            "summary": summary,
            "error": "HIT_VERIFIED lacked two zero verifier exits",
        }
    if raw == "CANDIDATE_VERIFIED":
        # The Gaussian engine writes candidate artifacts only after both exact
        # verifier exits are zero.  Require the retained verifier evidence too.
        verification = summary.get("verification", {})
        if (isinstance(verification, dict)
                and verification.get("scalar_exit") == 0
                and verification.get("independent_exit") == 0):
            return "HIT_VERIFIED", raw, {"summary": summary}
        return "FAILED", raw, {
            "summary": summary,
            "error": "CANDIDATE_VERIFIED lacked two zero verifier exits",
        }
    if raw in {"NO_HIT", "G_FAIL", "N_FAIL"}:
        return "NO_HIT", raw, {"summary": summary}
    if raw == "TIMEOUT_INCOMPLETE":
        return "TIMEOUT_INCOMPLETE", raw, {"summary": summary}
    if raw in {"FAILED", "FAILED_VERIFICATION", "VERIFIER_FAILURE"}:
        return "FAILED", raw, {"summary": summary}
    if raw == "RUNNING":
        return "RUNNING", raw, {"summary": summary}
    return "FAILED", raw, {"summary": summary, "error": "unrecognized result"}


def process_creation_flags() -> int:
    if os.name != "nt":
        return 0
    return int(getattr(subprocess, "CREATE_NO_WINDOW", 0)) | int(
        getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    )


def stop_owned_process(lane: OwnedLane) -> None:
    if lane.process.poll() is not None:
        return
    if os.name == "nt":
        # /T is intentionally restricted to the exact still-live PID retained
        # in this Popen object; it also stops a transient verifier descendant.
        subprocess.run(
            ["taskkill", "/PID", str(lane.process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            creationflags=int(getattr(subprocess, "CREATE_NO_WINDOW", 0)),
        )
    else:
        try:
            os.killpg(lane.process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return


def reap_owned(lanes: Iterable[OwnedLane], timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    for lane in lanes:
        remaining = max(0.0, deadline - time.monotonic())
        try:
            lane.process.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            if lane.process.poll() is None:
                lane.process.kill()
                lane.process.wait(timeout=2.0)


def write_state(
    path: Path,
    *,
    run_id: str,
    started_utc: str,
    deadline_utc: str,
    deadline_unix: float,
    status: str,
    lanes: Sequence[OwnedLane],
    anomaly: str | None = None,
) -> None:
    atomic_write_json(path, {
        "schema_version": SCHEMA_VERSION,
        "kind": "magic_square_squares_frozen_tranche_state",
        "run_id": run_id,
        "supervisor_pid": os.getpid(),
        "status": status,
        "started_utc": started_utc,
        "deadline_utc": deadline_utc,
        "deadline_unix": deadline_unix,
        "worker_cap": 64,
        "workers_launched": len(lanes),
        "workers_running": sum(lane.process.poll() is None for lane in lanes),
        "family_counts": {
            family: sum(lane.spec.family == family for lane in lanes)
            for family in EXPECTED_FAMILIES
        },
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "proof_claim": False,
        "anomaly": anomaly,
        "updated_utc": utc_now(),
        "lanes": [lane_record(lane) for lane in lanes],
    })


def run_specs(
    specs: Sequence[LaneSpec],
    run_dir: Path,
    duration_seconds: float,
    *,
    manifest_sha256: str,
    start_unix_override: float | None = None,
) -> int:
    validate_specs(specs)
    if len(specs) > 64:
        raise RuntimeError("aggregate worker cap exceeded")

    run_id = run_dir.name
    start_unix = time.time() if start_unix_override is None else start_unix_override
    started_utc = dt.datetime.fromtimestamp(
        start_unix, tz=dt.timezone.utc
    ).isoformat(timespec="milliseconds")
    deadline_unix = start_unix + duration_seconds
    deadline_utc = dt.datetime.fromtimestamp(
        deadline_unix, tz=dt.timezone.utc
    ).isoformat(timespec="milliseconds")
    state_path = run_dir / "portfolio_state.json"
    summary_path = run_dir / "portfolio_summary.json"
    owned: list[OwnedLane] = []
    stopping_reason: str | None = None
    hit_lane: str | None = None
    anomaly: str | None = None

    base_environment = os.environ.copy()
    base_environment.update({
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "VECLIB_MAXIMUM_THREADS": "1",
    })

    try:
        for spec in specs:
            spec.stdout_path.parent.mkdir(parents=True, exist_ok=True)
            stdout = spec.stdout_path.open("wb")
            stderr = spec.stderr_path.open("wb")
            try:
                process = subprocess.Popen(
                    list(spec.command),
                    cwd=str(spec.cwd),
                    env=base_environment,
                    stdin=subprocess.DEVNULL,
                    stdout=stdout,
                    stderr=stderr,
                    creationflags=process_creation_flags(),
                    start_new_session=(os.name != "nt"),
                )
            finally:
                stdout.close()
                stderr.close()
            owned.append(OwnedLane(spec, process, utc_now()))

        if len(owned) != 64:
            raise RuntimeError(f"startup launched {len(owned)} rather than 64 workers")
        write_state(
            state_path, run_id=run_id, started_utc=started_utc,
            deadline_utc=deadline_utc, deadline_unix=deadline_unix,
            status="RUNNING", lanes=owned,
        )

        last_state = time.monotonic()
        while True:
            now = time.time()
            event = False
            for lane in owned:
                if lane.normalized_status != "RUNNING":
                    continue
                if lane.spec.stderr_path.exists() and lane.spec.stderr_path.stat().st_size > 0:
                    anomaly = f"nonempty stderr: {lane.spec.lane_id}"
                    stopping_reason = "FAILED"
                    event = True
                    break
                return_code = lane.process.poll()
                if return_code is None:
                    normalized, raw, detail = normalize_lane_result(lane.spec)
                    if normalized == "HIT_VERIFIED":
                        lane.normalized_status = normalized
                        lane.raw_status = raw
                        lane.status_detail = detail
                        hit_lane = lane.spec.lane_id
                        stopping_reason = "HIT_VERIFIED"
                        event = True
                        break
                    if normalized == "FAILED":
                        lane.normalized_status = normalized
                        lane.raw_status = raw
                        lane.status_detail = detail
                        anomaly = f"failed live result: {lane.spec.lane_id}"
                        stopping_reason = "FAILED"
                        event = True
                        break
                    continue

                lane.return_code = return_code
                lane.finished_utc = utc_now()
                normalized, raw, detail = normalize_lane_result(lane.spec)
                if normalized == "RUNNING":
                    normalized = "FAILED"
                    detail = {
                        "summary": detail.get("summary"),
                        "error": "process exited while engine summary remained RUNNING",
                    }
                lane.normalized_status = normalized
                lane.raw_status = raw
                lane.status_detail = detail
                event = True
                if normalized == "HIT_VERIFIED":
                    hit_lane = lane.spec.lane_id
                    stopping_reason = "HIT_VERIFIED"
                    break
                if normalized in {"FAILED", "MISSING_SUMMARY"}:
                    anomaly = f"invalid completed result: {lane.spec.lane_id}"
                    stopping_reason = "FAILED"
                    break

            if stopping_reason is not None:
                break
            if all(lane.normalized_status != "RUNNING" for lane in owned):
                stopping_reason = "ALL_COMPLETED"
                break
            if now >= deadline_unix:
                stopping_reason = "DEADLINE"
                break
            if event or time.monotonic() - last_state >= STATE_HEARTBEAT_SECONDS:
                write_state(
                    state_path, run_id=run_id, started_utc=started_utc,
                    deadline_utc=deadline_utc, deadline_unix=deadline_unix,
                    status="RUNNING", lanes=owned, anomaly=anomaly,
                )
                last_state = time.monotonic()
            time.sleep(POLL_SECONDS)

    except KeyboardInterrupt:
        stopping_reason = "INTERRUPTED"
        anomaly = "supervisor interrupted"
    except BaseException as error:
        stopping_reason = "FAILED"
        anomaly = f"supervisor exception: {type(error).__name__}: {error}"
        (run_dir / "supervisor_exception.txt").write_text(
            traceback.format_exc(), encoding="utf-8", newline="\n"
        )
    finally:
        for lane in owned:
            stop_owned_process(lane)
        reap_owned(owned)
        for lane in owned:
            if lane.return_code is None:
                lane.return_code = lane.process.poll()
            if lane.finished_utc is None:
                lane.finished_utc = utc_now()
            if lane.normalized_status == "RUNNING":
                if stopping_reason == "DEADLINE":
                    lane.normalized_status = "TIMEOUT_INCOMPLETE"
                    lane.raw_status = "STOPPED_AT_COMMON_DEADLINE"
                elif stopping_reason == "HIT_VERIFIED":
                    lane.normalized_status = "STOPPED_AFTER_OTHER_HIT"
                    lane.raw_status = "PORTFOLIO_STOP"
                elif stopping_reason == "INTERRUPTED":
                    lane.normalized_status = "INTERRUPTED"
                    lane.raw_status = "PORTFOLIO_STOP"
                else:
                    lane.normalized_status = "FAILED"
                    lane.raw_status = "PORTFOLIO_STOP"

    if stopping_reason == "HIT_VERIFIED":
        overall = "HIT_VERIFIED"
        exit_code = 0
    elif stopping_reason == "ALL_COMPLETED" and all(
        lane.normalized_status == "NO_HIT" for lane in owned
    ):
        overall = "NO_HIT_DECLARED_DOMAINS"
        exit_code = 0
    elif stopping_reason == "DEADLINE" or any(
        lane.normalized_status == "TIMEOUT_INCOMPLETE" for lane in owned
    ):
        overall = "TIMEOUT_INCOMPLETE"
        exit_code = 4
    elif stopping_reason == "INTERRUPTED":
        overall = "INTERRUPTED"
        exit_code = 130
    else:
        overall = "FAILED"
        exit_code = 3

    finished_utc = utc_now()
    summary = {
        "schema_version": SCHEMA_VERSION,
        "kind": "magic_square_squares_frozen_tranche_summary",
        "run_id": run_id,
        "status": overall,
        "proof_claim": False,
        "claim_scope": (
            "A no-hit or timeout concerns only the 64 finite domains in "
            "LANE_MANIFEST.md; it is not an impossibility proof."
        ),
        "started_utc": started_utc,
        "deadline_utc": deadline_utc,
        "finished_utc": finished_utc,
        "duration_limit_seconds": duration_seconds,
        "manifest_sha256": manifest_sha256,
        "workers_requested": 64,
        "workers_launched": len(owned),
        "family_counts": {
            family: sum(lane.spec.family == family for lane in owned)
            for family in EXPECTED_FAMILIES
        },
        "stop_reason": stopping_reason,
        "hit_lane": hit_lane,
        "anomaly": anomaly,
        "nonempty_stderr_lanes": [
            lane.spec.lane_id for lane in owned
            if lane.spec.stderr_path.exists() and lane.spec.stderr_path.stat().st_size > 0
        ],
        "lane_status_counts": {
            status: sum(lane.normalized_status == status for lane in owned)
            for status in sorted({lane.normalized_status for lane in owned})
        },
        "lanes": [lane_record(lane) for lane in owned],
    }
    atomic_write_json(summary_path, summary)
    write_state(
        state_path, run_id=run_id, started_utc=started_utc,
        deadline_utc=deadline_utc, deadline_unix=deadline_unix,
        status=overall, lanes=owned, anomaly=anomaly,
    )
    return exit_code


def reserve_run_dir(path: Path) -> Path:
    absolute = path.resolve()
    absolute.parent.mkdir(parents=True, exist_ok=True)
    try:
        absolute.mkdir()
    except FileExistsError as error:
        raise RuntimeError(f"run directory already exists; refusing rerun: {absolute}") from error
    lock = absolute / "RUN_ONCE.json"
    atomic_write_json(lock, {
        "schema_version": SCHEMA_VERSION,
        "created_utc": utc_now(),
        "creator_pid": os.getpid(),
        "run_dir": str(absolute),
        "rule": "This canonical directory is never resumed or overwritten.",
    })
    return absolute


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="validate the frozen production inputs without creating a run directory",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    engine_dir = Path(__file__).resolve().parent
    manifest = engine_dir.parent / "LANE_MANIFEST.md"
    if args.preflight_only:
        try:
            if args.run_dir.resolve().exists():
                raise RuntimeError(
                    f"canonical run directory already exists: {args.run_dir.resolve()}"
                )
            manifest_sha256 = sha256_file(manifest)
            if manifest_sha256 != EXPECTED_MANIFEST_SHA256:
                raise RuntimeError(
                    "frozen manifest hash mismatch: " + manifest_sha256
                )
            deadline_unix = float(int(time.time())) + PRODUCTION_SECONDS
            specs = production_specs(engine_dir, args.run_dir, deadline_unix)
            print(json.dumps({
                "status": "PREFLIGHT_OK",
                "proof_claim": False,
                "run_dir": str(args.run_dir.resolve()),
                "manifest_sha256": manifest_sha256,
                "workers": len(specs),
                "family_counts": {
                    family: sum(spec.family == family for spec in specs)
                    for family in EXPECTED_FAMILIES
                },
            }, sort_keys=True, separators=(",", ":")))
            return 0
        except BaseException as error:
            print(json.dumps({
                "status": "FAILED_PREFLIGHT",
                "proof_claim": False,
                "error": f"{type(error).__name__}: {error}",
            }, sort_keys=True, separators=(",", ":")), file=sys.stderr)
            return 2

    run_dir = reserve_run_dir(args.run_dir)
    try:
        manifest_sha256 = sha256_file(manifest)
        if manifest_sha256 != EXPECTED_MANIFEST_SHA256:
            raise RuntimeError(
                "frozen manifest hash mismatch: " + manifest_sha256
            )
        start_unix = float(int(time.time()))
        deadline_unix = start_unix + PRODUCTION_SECONDS
        specs = production_specs(engine_dir, run_dir, deadline_unix)
    except BaseException as error:
        summary = {
            "schema_version": SCHEMA_VERSION,
            "kind": "magic_square_squares_frozen_tranche_summary",
            "run_id": run_dir.name,
            "status": "FAILED_PREFLIGHT",
            "proof_claim": False,
            "workers_requested": 64,
            "workers_launched": 0,
            "error": f"{type(error).__name__}: {error}",
            "finished_utc": utc_now(),
        }
        atomic_write_json(run_dir / "portfolio_summary.json", summary)
        return 2
    return run_specs(
        specs, run_dir, PRODUCTION_SECONDS,
        manifest_sha256=manifest_sha256,
        start_unix_override=start_unix,
    )


if __name__ == "__main__":
    raise SystemExit(main())
