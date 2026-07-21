#!/usr/bin/env python3
"""Recover the interrupted frozen 64-lane tranche without extending it.

This is a recovery of ``tranche64-frozen-manifest-v1`` rather than a second
tranche.  It retains completed E/S results, treats each committed G/N
checkpoint as an immutable prefix and searches only its unsearched suffix,
and restarts only the S lanes that were killed by the N14 atomic-write
failure.  The original run tree is never written.

Production process creation requires the explicit ``--execute-recovery``
flag, an exact semantic match to the recorded N14 failure, an approved
patched Gaussian executable hash, a fresh run-once directory, and time
remaining before the original absolute deadline.  Running with no arguments
is read-only preflight and cannot create a search process.
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
import uuid
from typing import Any, Callable, Iterable, Sequence

import tranche_supervisor as base


SCHEMA_VERSION = 1
ORIGINAL_RUN_ID = "tranche64-frozen-manifest-v1"
RECOVERY_RUN_ID = "tranche64-frozen-manifest-v1-recovery-v1"
ORIGINAL_START_UNIX = 1_784_585_850.0  # 2026-07-20 22:17:30 UTC
ORIGINAL_DEADLINE_UNIX = 1_784_614_650.0  # 2026-07-21 06:17:30 UTC
ORIGINAL_DURATION_SECONDS = 8 * 60 * 60
EXPECTED_MANIFEST_SHA256 = (
    "917F8F14729DF6D52D34796253589B22BE88FDC993E8BBB5898CC5FE59888C21"
)

# Set only after the patched executable passes the independent concurrent
# reader/writer stress test and its hash is approved.  A placeholder is an
# intentional fail-closed launch gate.
APPROVED_GAUSSIAN_EXE_SHA256 = (
    "0FB9884C814C0D790C2E01701D674FEF47B681F9EB16B7DEE58C5E58FBB6ACB8"
)
GAUSSIAN_FINAL_CALIBRATION_APPROVED = True
APPROVED_ATOMIC_STRESS_EXE_SHA256 = (
    "2130D532F234BCC77D702BEB40A99060A8F0B48F5EEBA382A49A556FCDB6E806"
)
APPROVED_S_EXE_SHA256 = (
    "092AE87D563569AE2CB2F7C8E64C70DE4582D4085C5428F4F0D73008D46C3996"
)
APPROVED_SCALAR_SHA256 = (
    "F4CE16B8EA0E8329A4CE96518574FDD6936414E1A72B1A09FA91F0C5404FA382"
)
APPROVED_INDEPENDENT_SHA256 = (
    "DCB3019916CB759DDB4654517BAB67EF5AA8D70775DE0B60C60BB609CF833589"
)

RECOVERED_LANE_IDS = (
    {f"G{number:02d}" for number in range(1, 17)}
    | {f"N{number:02d}" for number in range(1, 17)}
    | {f"S{number:02d}" for number in range(4, 17)}
)
RETAINED_LANE_IDS = (
    {f"E{number:02d}" for number in range(1, 17)}
    | {"S01", "S02", "S03"}
)
ALL_LANE_IDS = {
    f"{family}{number:02d}"
    for family in "GENS"
    for number in range(1, 17)
}

POLL_SECONDS = 0.25
STATE_HEARTBEAT_SECONDS = 10.0


def approved_artifact_hashes() -> dict[str, str]:
    return {
        "recovery_supervisor.py": sha256_file(Path(__file__).resolve()),
        "gaussian_center.exe": APPROVED_GAUSSIAN_EXE_SHA256,
        "s_lane_search.exe": APPROVED_S_EXE_SHA256,
        "verify_scalar.py": APPROVED_SCALAR_SHA256,
        "verify_independent.exe": APPROVED_INDEPENDENT_SHA256,
        "test_gaussian_atomic_stress.exe": APPROVED_ATOMIC_STRESS_EXE_SHA256,
    }

class RecoveryRefused(RuntimeError):
    """Raised before process creation when a fail-closed gate is not met."""


@dataclasses.dataclass(frozen=True)
class Preflight:
    original_run_dir: Path
    recovery_run_dir: Path
    original_summary_sha256: str
    original_inventory: dict[str, str]
    original_summary: dict[str, Any]
    original_lane_rows: dict[str, dict[str, Any]]
    retained_records: tuple[dict[str, Any], ...]
    prefix_checkpoints: dict[str, dict[str, Any]]
    executable_hashes: dict[str, str]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def _windows_replace_is_transient(error: OSError, target: Path, temporary: Path) -> bool:
    winerror = getattr(error, "winerror", None)
    if winerror in {32, 33}:  # sharing or lock violation
        return True
    if winerror != 5:
        return False
    try:
        # Do not stat the destination here. An exclusive Windows reader can
        # make even target.exists()/is_file()/is_symlink() raise WinError 5,
        # which is exactly the transient condition this classifier handles.
        # Invalid destinations exhaust the bounded retry loop and still fail.
        return (
            temporary.parent == target.parent
            and temporary.is_file()
            and not temporary.is_symlink()
        )
    except OSError:
        return False


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(
        f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
    )
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as target:
            json.dump(value, target, sort_keys=True, separators=(",", ":"))
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


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RecoveryRefused(f"cannot read exact JSON artifact {path}: {error}") from error
    if not isinstance(value, dict):
        raise RecoveryRefused(f"JSON artifact is not an object: {path}")
    return value


def artifact_inventory(root: Path) -> dict[str, str]:
    if not root.is_dir():
        raise RecoveryRefused(f"original run directory is missing: {root}")
    inventory: dict[str, str] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        inventory[path.relative_to(root).as_posix()] = sha256_file(path)
    return inventory


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RecoveryRefused(message)


def _expected_n14_error(original_run_dir: Path) -> str:
    target = original_run_dir / "lanes" / "N14" / "engine" / "summary.json"
    return f"atomic replace failed for: {target}"


def _is_squarefree(value: int) -> bool:
    factor = 2
    while factor * factor <= value:
        if value % (factor * factor) == 0:
            return False
        factor += 1
    return True


def _validate_standard_no_hit(lane_id: str, summary: dict[str, Any]) -> None:
    _require(summary.get("status") == "NO_HIT", f"{lane_id} is not exact NO_HIT")
    _require(summary.get("lane") == lane_id, f"{lane_id} engine lane mismatch")
    _require(summary.get("engine") == "elliptic_integral_search",
             f"{lane_id} engine identity mismatch")
    number = int(lane_id[1:])
    _require(summary.get("kappa_min") == (number - 1) * 64 + 1,
             f"{lane_id} kappa_min mismatch")
    _require(summary.get("kappa_max") == number * 64,
             f"{lane_id} kappa_max mismatch")
    _require(summary.get("x_bound") == 1 << 20, f"{lane_id} x bound mismatch")
    _require(summary.get("squarefree_only") is True,
             f"{lane_id} did not record squarefree-only enumeration")
    _require(summary.get("integral_precursors_only") is True,
             f"{lane_id} did not record integral-precursor scope")
    _require(summary.get("chunk_count") == 1 and summary.get("chunk_index") == 0,
             f"{lane_id} chunk coverage mismatch")
    counts = summary.get("counts")
    _require(isinstance(counts, dict), f"{lane_id} counts missing")
    expected_squarefree = sum(
        _is_squarefree(kappa)
        for kappa in range((number - 1) * 64 + 1, number * 64 + 1)
    )
    _require(counts.get("kappas_selected") == expected_squarefree,
             f"{lane_id} squarefree-kappa count mismatch")
    _require(counts.get("kappas_selected") == counts.get("kappas_completed"),
             f"{lane_id} did not complete every selected kappa")
    _require(counts.get("x_tested") == expected_squarefree * (2 * (1 << 20) + 1),
             f"{lane_id} x-box coverage mismatch")
    _require(counts.get("candidates_reconstructed") == 0,
             f"{lane_id} retained a candidate")


def _validate_s_no_hit(lane_id: str, path: Path) -> dict[str, Any]:
    values = base.parse_json_lines(path)
    summaries = [value for value in values if value.get("type") == "summary"]
    _require(len(summaries) == 1, f"{lane_id} does not have one exact S summary")
    summary = summaries[0]
    number = int(lane_id[1:])
    expected_min = 2 if number == 1 else (number - 1) * 128 + 1
    _require(summary.get("status") == "EXHAUSTED", f"{lane_id} is not exhausted")
    _require(summary.get("p_min") == expected_min and summary.get("p_max") == number * 128,
             f"{lane_id} P band mismatch")
    _require(summary.get("threads") == 1, f"{lane_id} was not single-threaded")
    _require(summary.get("candidate_count") == 0
             and summary.get("verified_candidate_count") == 0,
             f"{lane_id} has candidate data and cannot be retained as NO_HIT")
    return summary


def _retained_record(row: dict[str, Any], detail: dict[str, Any]) -> dict[str, Any]:
    return {
        "lane": row["lane"],
        "family": row["family"],
        "source": "retained_original_exact_completion",
        "source_run_id": ORIGINAL_RUN_ID,
        "owned": False,
        "pid": None,
        "single_thread_search": True,
        "command": row.get("command"),
        "cwd": row.get("cwd"),
        "stdout": row.get("stdout"),
        "stderr": row.get("stderr"),
        "engine_summary": row.get("engine_summary"),
        "started_utc": row.get("started_utc"),
        "finished_utc": row.get("finished_utc"),
        "return_code": row.get("return_code"),
        "status": "NO_HIT",
        "raw_status": row.get("raw_status"),
        "status_detail": detail,
    }


def _pid_is_live(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes

        process_query_limited_information = 0x1000
        still_active = 259
        handle = ctypes.windll.kernel32.OpenProcess(
            process_query_limited_information, False, pid
        )
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            if not ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return False
            return code.value == still_active
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def _pid_matches_recorded_command(pid: int, command: Sequence[str]) -> bool:
    """Return true only if a live/reused PID is the recorded owned process."""
    if not _pid_is_live(pid):
        return False
    try:
        import psutil

        current = psutil.Process(pid).cmdline()
    except Exception as error:
        raise RecoveryRefused(
            f"cannot disambiguate live/reused PID {pid}: {type(error).__name__}: {error}"
        ) from error
    normalized_current = [str(item).casefold() for item in current]
    normalized_expected = [str(item).casefold() for item in command]
    return normalized_current == normalized_expected


def _original_supervisor_still_live(pid: int) -> bool:
    if not _pid_is_live(pid):
        return False
    try:
        import psutil

        command = " ".join(psutil.Process(pid).cmdline()).casefold()
    except Exception as error:
        raise RecoveryRefused(
            f"cannot disambiguate original supervisor PID {pid}: "
            f"{type(error).__name__}: {error}"
        ) from error
    return "tranche_supervisor.py" in command and ORIGINAL_RUN_ID.casefold() in command


@dataclasses.dataclass(frozen=True)
class ProcessIdentity:
    lane_id: str
    pid: int
    create_time: float
    command: tuple[str, ...]


def _capture_owned_process_tree(
    lanes: Sequence[base.OwnedLane],
) -> list[ProcessIdentity]:
    """Snapshot each live owned root and every currently owned descendant."""
    import psutil

    identities: list[ProcessIdentity] = []
    seen: set[tuple[int, float]] = set()
    for lane in lanes:
        try:
            root = psutil.Process(lane.process.pid)
            processes = [root, *root.children(recursive=True)]
        except psutil.NoSuchProcess:
            continue
        except Exception as error:
            raise RecoveryRefused(
                f"cannot snapshot owned tree {lane.spec.lane_id}: "
                f"{type(error).__name__}: {error}"
            ) from error
        for process in processes:
            try:
                identity = (process.pid, process.create_time())
                command = tuple(process.cmdline())
            except psutil.NoSuchProcess:
                continue
            except Exception as error:
                raise RecoveryRefused(
                    f"cannot identify owned tree PID {process.pid}: "
                    f"{type(error).__name__}: {error}"
                ) from error
            if identity in seen:
                continue
            seen.add(identity)
            identities.append(ProcessIdentity(
                lane.spec.lane_id, identity[0], identity[1], command
            ))
    return identities


def _process_identity_is_live(identity: ProcessIdentity) -> bool:
    import psutil

    try:
        process = psutil.Process(identity.pid)
        return (
            abs(process.create_time() - identity.create_time) < 1e-6
            and process.is_running()
            and process.status() != psutil.STATUS_ZOMBIE
        )
    except psutil.NoSuchProcess:
        return False
    except Exception:
        # Failure to inspect an owned identity is fail-closed as a survivor.
        return True


def _psutil_fallback_kill(
    lane: base.OwnedLane,
) -> tuple[dict[str, Any], list[ProcessIdentity]]:
    """Freeze, re-snapshot, and kill one exact owned tree bottom-up."""
    import psutil

    evidence: dict[str, Any] = {
        "attempted": True,
        "root_suspended_before_resnapshot": False,
        "tree_stabilized": False,
        "freeze_errors": [],
        "kill_attempts": [],
    }
    identities: list[ProcessIdentity] = []
    root_identity: tuple[int, float] | None = None
    try:
        root = psutil.Process(lane.process.pid)
        root_identity = (root.pid, root.create_time())
        root.suspend()
        evidence["root_suspended_before_resnapshot"] = True

        known: dict[tuple[int, float], ProcessIdentity] = {}
        # Suspending the root prevents it from creating new children. Repeatedly
        # snapshot and suspend descendants until a pass discovers no new live
        # identity; this closes the child-spawn race before any kill is sent.
        for _pass in range(8):
            snapshot = _capture_owned_process_tree([lane])
            new_items = [
                item for item in snapshot
                if (item.pid, item.create_time) not in known
            ]
            for item in new_items:
                known[(item.pid, item.create_time)] = item
                if (item.pid, item.create_time) == root_identity:
                    continue
                try:
                    process = psutil.Process(item.pid)
                    if abs(process.create_time() - item.create_time) >= 1e-6:
                        evidence["freeze_errors"].append({
                            "pid": item.pid,
                            "error": "pid_reused_before_suspend",
                        })
                    else:
                        process.suspend()
                except psutil.NoSuchProcess:
                    pass
                except BaseException as error:
                    evidence["freeze_errors"].append({
                        "pid": item.pid,
                        "error": f"{type(error).__name__}: {error}",
                    })
            if not new_items:
                evidence["tree_stabilized"] = True
                break
        identities = list(known.values())
        evidence["resnapshot"] = [
            {"pid": item.pid, "create_time": item.create_time,
             "command": list(item.command)}
            for item in identities
        ]

        # The root is first in the snapshot. Reverse order sends hard kills to
        # all observed descendants before the suspended root. Each signal is
        # guarded by PID creation time, so a reused PID is never killed.
        for identity in reversed(identities):
            row: dict[str, Any] = {
                "pid": identity.pid,
                "create_time": identity.create_time,
                "signal": "kill",
            }
            try:
                process = psutil.Process(identity.pid)
                if abs(process.create_time() - identity.create_time) >= 1e-6:
                    row["result"] = "pid_reused_not_signalled"
                else:
                    process.kill()
                    row["result"] = "kill_sent"
            except psutil.NoSuchProcess:
                row["result"] = "already_exited"
            except BaseException as error:
                row["result"] = "kill_error"
                row["error"] = f"{type(error).__name__}: {error}"
            evidence["kill_attempts"].append(row)
        evidence["result"] = "signals_attempted"
    except psutil.NoSuchProcess:
        evidence["result"] = "root_exited_before_fallback_resnapshot"
    except BaseException as error:
        evidence["result"] = "fallback_exception"
        evidence["error"] = f"{type(error).__name__}: {error}"
    finally:
        # If the root was frozen but could not be killed, resume it so the
        # ordinary Popen reap/kill fallback can still act on the owned root.
        if evidence["root_suspended_before_resnapshot"]:
            try:
                root = psutil.Process(lane.process.pid)
                if lane.process.poll() is None:
                    root.resume()
                    evidence["root_resumed_for_popen_reap"] = True
            except psutil.NoSuchProcess:
                pass
            except BaseException as error:
                evidence["root_resume_error"] = f"{type(error).__name__}: {error}"
    return evidence, identities


def _stop_owned_recovery_process(
    lane: base.OwnedLane,
) -> tuple[dict[str, Any], list[ProcessIdentity]]:
    if lane.process.poll() is not None:
        return ({
            "action": "already_exited",
            "taskkill_exit": None,
        }, [])
    if os.name == "nt":
        completed = subprocess.run(
            ["taskkill", "/PID", str(lane.process.pid), "/T", "/F"],
            stdin=subprocess.DEVNULL, capture_output=True, check=False,
            creationflags=int(getattr(subprocess, "CREATE_NO_WINDOW", 0)),
        )
        evidence: dict[str, Any] = {
            "action": "taskkill_tree",
            "root_was_live_before_taskkill": True,
            "taskkill_exit": completed.returncode,
            "taskkill_stdout": completed.stdout.decode("utf-8", errors="replace"),
            "taskkill_stderr": completed.stderr.decode("utf-8", errors="replace"),
        }
        supplemental: list[ProcessIdentity] = []
        if completed.returncode != 0:
            fallback, supplemental = _psutil_fallback_kill(lane)
            evidence["psutil_fallback"] = fallback
        return evidence, supplemental
    try:
        os.killpg(lane.process.pid, signal.SIGTERM)
        return ({
            "action": "kill_process_group",
            "taskkill_exit": None,
        }, [])
    except ProcessLookupError:
        return ({
            "action": "already_exited",
            "taskkill_exit": None,
        }, [])

def _wait_for_owned_tree_death(
    identities: Sequence[ProcessIdentity], timeout: float = 5.0,
) -> list[ProcessIdentity]:
    deadline = time.monotonic() + timeout
    while True:
        survivors = [item for item in identities if _process_identity_is_live(item)]
        if not survivors or time.monotonic() >= deadline:
            return survivors
        time.sleep(0.05)


def validate_original_failure(
    engine_dir: Path,
    *,
    require_approved_engine: bool,
    require_dead_workers: bool,
    now: float | None = None,
) -> Preflight:
    """Perform every read-only gate before a recovery directory can exist."""
    engine_dir = engine_dir.resolve()
    original_run_dir = engine_dir / "logs" / ORIGINAL_RUN_ID
    recovery_run_dir = engine_dir / "logs" / RECOVERY_RUN_ID
    summary_path = original_run_dir / "portfolio_summary.json"
    state_path = original_run_dir / "portfolio_state.json"
    lock_path = original_run_dir / "RUN_ONCE.json"
    summary = read_json(summary_path)
    state = read_json(state_path)
    lock = read_json(lock_path)

    _require(lock.get("run_dir") == str(original_run_dir), "original run lock mismatch")
    _require(summary.get("schema_version") == 1, "original summary schema mismatch")
    _require(summary.get("run_id") == ORIGINAL_RUN_ID, "original run ID mismatch")
    _require(summary.get("status") == "FAILED", "original summary is not FAILED")
    _require(summary.get("stop_reason") == "FAILED", "original stop reason mismatch")
    _require(summary.get("anomaly") == "nonempty stderr: N14",
             "original anomaly is not exactly the N14 stderr event")
    _require(summary.get("nonempty_stderr_lanes") == ["N14"],
             "original nonempty-stderr set is not exactly N14")
    _require(summary.get("hit_lane") is None, "original run recorded a hit")
    _require(summary.get("proof_claim") is False, "original summary made a proof claim")
    _require(summary.get("manifest_sha256") == EXPECTED_MANIFEST_SHA256,
             "original manifest hash mismatch")
    _require(summary.get("started_utc") == "2026-07-20T22:17:30.000+00:00",
             "original T0 mismatch")
    _require(summary.get("deadline_utc") == "2026-07-21T06:17:30.000+00:00",
             "original deadline mismatch")
    _require(summary.get("duration_limit_seconds") == ORIGINAL_DURATION_SECONDS,
             "original duration mismatch")
    _require(summary.get("workers_requested") == 64
             and summary.get("workers_launched") == 64,
             "original worker count mismatch")
    _require(summary.get("lane_status_counts") == {"FAILED": 45, "NO_HIT": 19},
             "original final lane-count signature mismatch")
    _require(state.get("status") == "FAILED" and state.get("anomaly") == "nonempty stderr: N14",
             "original final state does not match the N14 failure")
    _require(state.get("workers_launched") == 64 and state.get("workers_running") == 0,
             "original final worker state mismatch")
    _require(state.get("deadline_unix") == ORIGINAL_DEADLINE_UNIX,
             "original state deadline mismatch")
    _require(state.get("manifest_sha256") == EXPECTED_MANIFEST_SHA256,
             "original state manifest hash mismatch")
    _require(state.get("proof_claim") is False, "original state made a proof claim")
    manifest_path = engine_dir.parent / "LANE_MANIFEST.md"
    _require(sha256_file(manifest_path) == EXPECTED_MANIFEST_SHA256,
             "current LANE_MANIFEST.md hash mismatch")
    if require_dead_workers:
        supervisor_pid = state.get("supervisor_pid")
        _require(
            isinstance(supervisor_pid, int)
            and not _original_supervisor_still_live(supervisor_pid),
            f"original supervisor process remains live: PID {supervisor_pid}",
        )

    rows = summary.get("lanes")
    _require(isinstance(rows, list) and len(rows) == 64,
             "original summary does not contain 64 lanes")
    lane_rows = {
        str(row.get("lane")): row for row in rows if isinstance(row, dict)
    }
    _require(set(lane_rows) == ALL_LANE_IDS, "original lane IDs mismatch")

    expected_specs = {
        spec.lane_id: spec
        for spec in base.production_specs(engine_dir, original_run_dir, ORIGINAL_DEADLINE_UNIX)
    }
    for lane_id, row in lane_rows.items():
        _require(row.get("owned") is True, f"{lane_id} was not recorded owned")
        _require(row.get("single_thread_search") is True,
                 f"{lane_id} was not recorded single-threaded")
        _require(row.get("command") == list(expected_specs[lane_id].command),
                 f"{lane_id} command differs from frozen manifest command")
        stderr_path = Path(str(row.get("stderr")))
        _require(stderr_path == expected_specs[lane_id].stderr_path,
                 f"{lane_id} stderr path mismatch")
        size = stderr_path.stat().st_size if stderr_path.is_file() else -1
        _require(size > 0 if lane_id == "N14" else size == 0,
                 f"{lane_id} original stderr signature mismatch")
        if require_dead_workers:
            pid = row.get("pid")
            _require(
                isinstance(pid, int)
                and not _pid_matches_recorded_command(pid, row["command"]),
                f"original owned process remains live: {lane_id} PID {pid}",
            )

    n14_stderr = Path(str(lane_rows["N14"]["stderr"]))
    try:
        n14_stderr_value = json.loads(n14_stderr.read_text(encoding="utf-8").strip())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RecoveryRefused(f"N14 stderr is not its exact JSON failure: {error}") from error
    expected_error = _expected_n14_error(original_run_dir)
    _require(n14_stderr_value == {"status": "FAILED", "error": expected_error},
             "N14 stderr content is not the exact atomic-replace failure")

    retained: list[dict[str, Any]] = []
    for lane_id in sorted(RETAINED_LANE_IDS):
        row = lane_rows[lane_id]
        _require(row.get("status") == "NO_HIT", f"{lane_id} not retained NO_HIT")
        if lane_id.startswith("E"):
            engine_summary = read_json(Path(str(row["engine_summary"])))
            _validate_standard_no_hit(lane_id, engine_summary)
            _require(row.get("raw_status") == "NO_HIT", f"{lane_id} raw status mismatch")
            detail = {"summary": engine_summary}
        else:
            s_summary = _validate_s_no_hit(lane_id, Path(str(row["engine_summary"])))
            _require(row.get("raw_status") == "EXHAUSTED", f"{lane_id} raw status mismatch")
            detail = {"summary": s_summary}
        retained.append(_retained_record(row, detail))

    prefix_checkpoints: dict[str, dict[str, Any]] = {}
    for lane_id in sorted(RECOVERED_LANE_IDS):
        row = lane_rows[lane_id]
        _require(row.get("status") == "FAILED" and row.get("raw_status") == "PORTFOLIO_STOP",
                 f"{lane_id} does not have the expected portfolio-stop record")
        if lane_id.startswith(("G", "N")):
            seed = read_json(Path(str(row["engine_summary"])))
            expected_mode = lane_id[0]
            _require(seed.get("schema") == "gaussian-center-v1"
                     and seed.get("mode") == expected_mode,
                     f"{lane_id} checkpoint identity mismatch")
            _require(seed.get("verified_candidates") == "0"
                     and seed.get("candidate_file") == ""
                     and seed.get("candidate_sha256") == "",
                     f"{lane_id} checkpoint contains candidate state")
            verification = seed.get("verification")
            _require(isinstance(verification, dict)
                     and verification.get("scalar_exit") == -1
                     and verification.get("independent_exit") == -1,
                     f"{lane_id} checkpoint contains unexpected verifier state")
            start = int(expected_specs[lane_id].command[
                list(expected_specs[lane_id].command).index("--start") + 1
            ])
            end = int(expected_specs[lane_id].command[
                list(expected_specs[lane_id].command).index("--end") + 1
            ])
            next_m = int(seed.get("next_m", "-1"))
            _require(int(seed.get("range_start", "-1")) == start
                     and int(seed.get("range_end", "-1")) == end
                     and int(seed.get("chunk_size", "-1")) == 1 << 16,
                     f"{lane_id} checkpoint domain mismatch")
            _require(start <= next_m <= end + 1, f"{lane_id} next_m outside domain")
            processed = int(seed.get("processed_centers", "-1"))
            _require(processed == next_m - start,
                     f"{lane_id} checkpoint counter is not a contiguous prefix")
            if lane_id == "N14":
                _require(seed.get("status") == "FAILED" and seed.get("error") == expected_error,
                         "N14 checkpoint is not the exact atomic-replace failure")
            else:
                _require(seed.get("status") in {"RUNNING", "TIMEOUT_INCOMPLETE"},
                         f"{lane_id} checkpoint is not resumable")
                _require(seed.get("error") == "",
                         f"{lane_id} has a non-N14 checkpoint error")
            prefix_checkpoints[lane_id] = seed

    executable_paths = {
        "gaussian_center.exe": engine_dir / "gaussian_center.exe",
        "s_lane_search.exe": engine_dir / "s_lane_search.exe",
        "verify_scalar.py": engine_dir / "verify_scalar.py",
        "verify_independent.exe": engine_dir / "verify_independent.exe",
    }
    executable_hashes = {name: sha256_file(path) for name, path in executable_paths.items()}
    _require(executable_hashes["s_lane_search.exe"] == APPROVED_S_EXE_SHA256,
             "structural engine hash changed")
    _require(executable_hashes["verify_scalar.py"] == APPROVED_SCALAR_SHA256,
             "scalar verifier hash changed")
    _require(executable_hashes["verify_independent.exe"] == APPROVED_INDEPENDENT_SHA256,
             "independent verifier hash changed")
    if require_approved_engine:
        _require(GAUSSIAN_FINAL_CALIBRATION_APPROVED,
                 "patched Gaussian engine awaits root approval after final calibration")
        _require(executable_hashes["gaussian_center.exe"] == APPROVED_GAUSSIAN_EXE_SHA256,
                 "Gaussian executable is not the approved atomic-retry build")
        stress_path = engine_dir / "test_gaussian_atomic_stress.exe"
        _require(sha256_file(stress_path) == APPROVED_ATOMIC_STRESS_EXE_SHA256,
                 "Gaussian atomic stress executable hash mismatch")
        stress = subprocess.run(
            [str(stress_path)], cwd=str(engine_dir), stdin=subprocess.DEVNULL,
            capture_output=True, creationflags=base.process_creation_flags(), check=False,
        )
        try:
            stress_value = json.loads(stress.stdout.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RecoveryRefused(f"Gaussian atomic stress output malformed: {error}") from error
        _require(stress.returncode == 0 and not stress.stderr
                 and isinstance(stress_value, dict)
                 and stress_value.get("ok") is True
                 and stress_value.get("writes") == 2000
                 and int(stress_value.get("valid_reads", 0)) >= 2
                 and int(stress_value.get("writer_transient_retries", 0)) >= 1
                 and stress_value.get("nontransient_attempts") == 1,
                 "Gaussian concurrent atomic stress gate failed")

    current = time.time() if now is None else now
    if require_approved_engine:
        _require(current < ORIGINAL_DEADLINE_UNIX,
                 "original absolute deadline has passed; zero recovery workers allowed")
        _require(not recovery_run_dir.exists(),
                 f"recovery run-once directory already exists: {recovery_run_dir}")

    return Preflight(
        original_run_dir=original_run_dir,
        recovery_run_dir=recovery_run_dir,
        original_summary_sha256=sha256_file(summary_path),
        original_inventory=artifact_inventory(original_run_dir),
        original_summary=summary,
        original_lane_rows=lane_rows,
        retained_records=tuple(retained),
        prefix_checkpoints=prefix_checkpoints,
        executable_hashes=executable_hashes,
    )


def reserve_and_stage(preflight: Preflight) -> Path:
    """Create the run-once tree and copy immutable prefix evidence only."""
    run_dir = preflight.recovery_run_dir
    run_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        run_dir.mkdir()
    except FileExistsError as error:
        raise RecoveryRefused(f"recovery run-once directory exists: {run_dir}") from error
    atomic_write_json(run_dir / "RUN_ONCE_RECOVERY.json", {
        "schema_version": SCHEMA_VERSION,
        "created_utc": utc_now(),
        "creator_pid": os.getpid(),
        "run_dir": str(run_dir),
        "source_run_dir": str(preflight.original_run_dir),
        "source_summary_sha256": preflight.original_summary_sha256,
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "original_start_unix": ORIGINAL_START_UNIX,
        "original_deadline_unix": ORIGINAL_DEADLINE_UNIX,
        "approved_gaussian_exe_sha256": APPROVED_GAUSSIAN_EXE_SHA256,
        "approved_artifact_hashes": approved_artifact_hashes(),
        "rule": "Run once; recover the original frozen domains without time extension.",
    })
    atomic_write_json(run_dir / "original_artifact_inventory.json", {
        "source_run_dir": str(preflight.original_run_dir),
        "files": preflight.original_inventory,
    })

    for lane_id, seed in preflight.prefix_checkpoints.items():
        source_path = Path(str(preflight.original_lane_rows[lane_id]["engine_summary"]))
        target_path = run_dir / "lanes" / lane_id / "prefix_checkpoint.json"
        atomic_write_json(target_path, seed)
        atomic_write_json(target_path.parent / "prefix_provenance.json", {
            "lane": lane_id,
            "source_path": str(source_path),
            "source_sha256": sha256_file(source_path),
            "source_status": read_json(source_path).get("status"),
            "committed_prefix_start": seed.get("range_start"),
            "committed_prefix_end": str(int(seed["next_m"]) - 1),
            "unsearched_suffix_start": seed.get("next_m"),
            "frozen_range_end": seed.get("range_end"),
            "n14_failed_status_retained_as_provenance": lane_id == "N14",
        })
    return run_dir


def recovery_specs(
    engine_dir: Path,
    run_dir: Path,
    *,
    remaining_seconds: float,
    prefix_checkpoints: dict[str, dict[str, Any]],
) -> list[base.LaneSpec]:
    """Derive the 45 recovery commands from the original frozen commands."""
    _require(remaining_seconds > 0, "no absolute-deadline time remains")
    original_run = engine_dir.resolve() / "logs" / ORIGINAL_RUN_ID
    original = {
        spec.lane_id: spec
        for spec in base.production_specs(engine_dir, original_run, ORIGINAL_DEADLINE_UNIX)
    }
    specs: list[base.LaneSpec] = []
    for lane_id in sorted(RECOVERED_LANE_IDS):
        source = original[lane_id]
        lane_dir = run_dir / "lanes" / lane_id
        command = list(source.command)
        if lane_id.startswith(("G", "N")):
            engine_out = lane_dir / "engine"
            checkpoint = prefix_checkpoints[lane_id]
            suffix_start = str(checkpoint["next_m"])
            _require(int(suffix_start) <= int(checkpoint["range_end"]),
                     f"{lane_id} has no suffix and should not be relaunched")
            command[command.index("--start") + 1] = suffix_start
            command[command.index("--run-dir") + 1] = str(engine_out)
            command[command.index("--deadline-unix") + 1] = str(int(ORIGINAL_DEADLINE_UNIX))
            kind = "standard"
            summary = engine_out / "summary.json"
        else:
            output = lane_dir / "engine.jsonl"
            verification = lane_dir / "verification"
            command[command.index("--output") + 1] = str(output)
            command[command.index("--verification-dir") + 1] = str(verification)
            command[command.index("--time-limit-seconds") + 1] = f"{remaining_seconds:.6f}"
            kind = "s_jsonl"
            summary = output
        specs.append(base.LaneSpec(
            lane_id=lane_id,
            family=lane_id[0],
            command=tuple(command),
            cwd=engine_dir.resolve(),
            summary_kind=kind,
            engine_summary=summary,
            stdout_path=lane_dir / "recovery.stdout.txt",
            stderr_path=lane_dir / "recovery.stderr.txt",
        ))
    validate_recovery_specs(specs)
    return specs


def validate_recovery_specs(specs: Sequence[base.LaneSpec]) -> None:
    ids = {spec.lane_id for spec in specs}
    _require(len(specs) == 45 and ids == RECOVERED_LANE_IDS,
             "recovery must contain exactly the 45 interrupted lanes")
    _require(sum(spec.family == "G" for spec in specs) == 16, "G recovery count mismatch")
    _require(sum(spec.family == "N" for spec in specs) == 16, "N recovery count mismatch")
    _require(sum(spec.family == "S" for spec in specs) == 13, "S recovery count mismatch")
    for spec in specs:
        command = list(spec.command)
        if spec.family in {"G", "N"}:
            _require("--resume" not in command,
                     f"{spec.lane_id} must be a fresh explicit suffix, not a resume")
            deadline = command[command.index("--deadline-unix") + 1]
            _require(deadline == str(int(ORIGINAL_DEADLINE_UNIX)),
                     f"{spec.lane_id} deadline changed")
        else:
            _require(command[command.index("--threads") + 1] == "1",
                     f"{spec.lane_id} is not single-threaded")


def _candidate_payload(spec: base.LaneSpec, detail: dict[str, Any]) -> dict[str, Any]:
    if spec.family == "S":
        candidate = detail.get("candidate")
        if not isinstance(candidate, dict):
            raise RecoveryRefused(f"{spec.lane_id} S hit lacks candidate JSON")
        return candidate
    summary = detail.get("summary")
    if not isinstance(summary, dict):
        raise RecoveryRefused(f"{spec.lane_id} hit lacks summary")
    candidate_path = Path(str(summary.get("candidate_file", "")))
    candidate = read_json(candidate_path)
    expected_name = str(summary.get("candidate_sha256", "")) + ".json"
    _require(candidate_path.name == expected_name,
             f"{spec.lane_id} candidate path/hash key mismatch")
    return candidate


def _flatten_matrix(value: Any) -> list[str]:
    if isinstance(value, list) and len(value) == 3 and all(
        isinstance(row, list) and len(row) == 3 for row in value
    ):
        values = [item for row in value for item in row]
    elif isinstance(value, list) and len(value) == 9:
        values = value
    else:
        raise RecoveryRefused("candidate matrix is not 3 by 3 or flat length nine")
    result: list[str] = []
    for item in values:
        text = str(item)
        _require(text.isdigit(), "candidate matrix contains a non-positive-integer token")
        result.append(text)
    return result


def production_verifier_gate(
    spec: base.LaneSpec,
    detail: dict[str, Any],
    engine_dir: Path,
    gate_dir: Path,
) -> tuple[bool, dict[str, Any]]:
    """Re-run both exact verifiers independently of the emitting engine."""
    candidate = _candidate_payload(spec, detail)
    msq_d = candidate.get("msq_d") or candidate.get("W")
    _require(isinstance(msq_d, dict), f"{spec.lane_id} candidate lacks MSQ-D")
    try:
        m, b, c = (str(msq_d[key]) for key in ("m", "b", "c"))
    except KeyError as error:
        raise RecoveryRefused(f"{spec.lane_id} candidate MSQ-D is incomplete") from error
    for token in (m, b, c):
        _require(token.isdigit(), f"{spec.lane_id} candidate MSQ-D is not integral")
    matrix = _flatten_matrix(candidate.get("matrix"))
    nested_matrix = [
        [int(matrix[3 * row + column]) for column in range(3)]
        for row in range(3)
    ]
    matrix_json = json.dumps(nested_matrix, separators=(",", ":"))
    gate_dir.mkdir(parents=True, exist_ok=True)
    candidate_file = gate_dir / "candidate_values.txt"
    candidate_file.write_text(" ".join(matrix) + "\n", encoding="ascii", newline="\n")

    # The authoritative scalar and independent calls consume the same nine
    # candidate values (JSON matrix vs. flat tokens).  A second scalar call
    # checks the MSQ-D bridge and must expand to those identical nine values.
    scalar_matrix = subprocess.run(
        [sys.executable, str(engine_dir / "verify_scalar.py"), "--matrix", matrix_json],
        cwd=str(engine_dir), stdin=subprocess.DEVNULL, capture_output=True,
        creationflags=base.process_creation_flags(), check=False,
    )
    scalar_msq_d = subprocess.run(
        [sys.executable, str(engine_dir / "verify_scalar.py"), "--msq-d", m, b, c],
        cwd=str(engine_dir), stdin=subprocess.DEVNULL, capture_output=True,
        creationflags=base.process_creation_flags(), check=False,
    )
    independent = subprocess.run(
        [str(engine_dir / "verify_independent.exe"), "--file", str(candidate_file)],
        cwd=str(engine_dir), stdin=subprocess.DEVNULL, capture_output=True,
        creationflags=base.process_creation_flags(), check=False,
    )
    (gate_dir / "scalar_matrix.stdout.json").write_bytes(scalar_matrix.stdout)
    (gate_dir / "scalar_matrix.stderr.txt").write_bytes(scalar_matrix.stderr)
    (gate_dir / "scalar_msq_d.stdout.json").write_bytes(scalar_msq_d.stdout)
    (gate_dir / "scalar_msq_d.stderr.txt").write_bytes(scalar_msq_d.stderr)
    (gate_dir / "independent.stdout.json").write_bytes(independent.stdout)
    (gate_dir / "independent.stderr.txt").write_bytes(independent.stderr)

    def parsed_json(raw: bytes) -> dict[str, Any] | None:
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        return value if isinstance(value, dict) else None

    scalar_matrix_value = parsed_json(scalar_matrix.stdout)
    scalar_msq_d_value = parsed_json(scalar_msq_d.stdout)
    independent_value = parsed_json(independent.stdout)
    msq_d_expands_to_same_matrix = False
    if scalar_msq_d_value is not None and scalar_msq_d_value.get("valid") is True:
        try:
            msq_d_expands_to_same_matrix = (
                _flatten_matrix(scalar_msq_d_value.get("matrix")) == matrix
            )
        except RecoveryRefused:
            msq_d_expands_to_same_matrix = False
    accepted = (
        scalar_matrix.returncode == 0 and scalar_msq_d.returncode == 0
        and independent.returncode == 0
        and not scalar_matrix.stderr and not scalar_msq_d.stderr
        and not independent.stderr
        and scalar_matrix_value is not None
        and scalar_matrix_value.get("valid") is True
        and scalar_msq_d_value is not None
        and scalar_msq_d_value.get("valid") is True
        and independent_value is not None
        and independent_value.get("valid") is True
        and msq_d_expands_to_same_matrix
    )
    evidence = {
        "accepted": accepted,
        "scalar_matrix_exit": scalar_matrix.returncode,
        "scalar_msq_d_exit": scalar_msq_d.returncode,
        "independent_exit": independent.returncode,
        "scalar_matrix_valid_json": (
            scalar_matrix_value is not None and scalar_matrix_value.get("valid") is True
        ),
        "scalar_msq_d_valid_json": (
            scalar_msq_d_value is not None and scalar_msq_d_value.get("valid") is True
        ),
        "independent_valid_json": (
            independent_value is not None and independent_value.get("valid") is True
        ),
        "msq_d_expands_to_same_candidate_matrix": msq_d_expands_to_same_matrix,
        "matrix_token_sha256": hashlib.sha256(
            (" ".join(matrix) + "\n").encode("ascii")
        ).hexdigest().upper(),
        "candidate_file": str(candidate_file),
    }
    atomic_write_json(gate_dir / "gate.json", evidence)
    return accepted, evidence


def _recovered_record(lane: base.OwnedLane) -> dict[str, Any]:
    record = base.lane_record(lane)
    record["source"] = "recovered_interrupted_lane"
    record["source_run_id"] = ORIGINAL_RUN_ID
    return record


def _attach_prefix_coverage(
    lane: base.OwnedLane,
    prefix_checkpoints: dict[str, dict[str, Any]],
) -> None:
    """Record how a G/N suffix combines with its immutable committed prefix."""
    if lane.spec.family not in {"G", "N"}:
        return
    checkpoint = prefix_checkpoints[lane.spec.lane_id]
    detail = dict(lane.status_detail)
    detail["coverage"] = {
        "method": "immutable_committed_prefix_plus_explicit_suffix",
        "frozen_range_start": checkpoint["range_start"],
        "committed_prefix_end": str(int(checkpoint["next_m"]) - 1),
        "suffix_start": checkpoint["next_m"],
        "frozen_range_end": checkpoint["range_end"],
        "prefix_processed_centers": checkpoint["processed_centers"],
        "prefix_status_as_recorded": checkpoint["status"],
        "source_run_id": ORIGINAL_RUN_ID,
    }
    lane.status_detail = detail


def _all_records(
    retained_records: Sequence[dict[str, Any]],
    owned: Sequence[base.OwnedLane],
) -> list[dict[str, Any]]:
    records = [copy.deepcopy(record) for record in retained_records]
    records.extend(_recovered_record(lane) for lane in owned)
    records.sort(key=lambda record: str(record["lane"]))
    _require({str(record["lane"]) for record in records} == ALL_LANE_IDS,
             "combined record is not exactly 64 lanes")
    return records


def _write_state(
    path: Path,
    *,
    status: str,
    retained_records: Sequence[dict[str, Any]],
    owned: Sequence[base.OwnedLane],
    anomaly: str | None,
) -> None:
    records = _all_records(retained_records, owned)
    atomic_write_json(path, {
        "schema_version": SCHEMA_VERSION,
        "kind": "magic_square_squares_frozen_tranche_recovery_state",
        "run_id": RECOVERY_RUN_ID,
        "source_run_id": ORIGINAL_RUN_ID,
        "supervisor_pid": os.getpid(),
        "status": status,
        "original_started_utc": "2026-07-20T22:17:30.000+00:00",
        "original_deadline_utc": "2026-07-21T06:17:30.000+00:00",
        "deadline_unix": ORIGINAL_DEADLINE_UNIX,
        "worker_cap": 64,
        "workers_launched_recovery": len(owned),
        "workers_running_recovery": sum(lane.process.poll() is None for lane in owned),
        "retained_completed_lanes": len(retained_records),
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "approved_artifact_hashes": approved_artifact_hashes(),
        "proof_claim": False,
        "anomaly": anomaly,
        "updated_utc": utc_now(),
        "lanes": records,
    })


VerifierGate = Callable[
    [base.LaneSpec, dict[str, Any], Path, Path],
    tuple[bool, dict[str, Any]],
]


def run_recovery_specs(
    specs: Sequence[base.LaneSpec],
    retained_records: Sequence[dict[str, Any]],
    run_dir: Path,
    engine_dir: Path,
    *,
    deadline_unix: float,
    original_inventory: dict[str, str] | None,
    original_run_dir: Path | None,
    prefix_checkpoints: dict[str, dict[str, Any]],
    verifier_gate: VerifierGate = production_verifier_gate,
) -> int:
    """Run only the interrupted lanes and emit a combined 64-lane summary."""
    validate_recovery_specs(specs)
    _require(len(retained_records) == 19, "exactly 19 completed lanes must be retained")
    _require({str(record["lane"]) for record in retained_records} == RETAINED_LANE_IDS,
             "retained lane set mismatch")
    _require(time.time() < deadline_unix, "deadline passed before worker creation")

    state_path = run_dir / "recovery_state.json"
    summary_path = run_dir / "recovery_summary.json"
    owned: list[base.OwnedLane] = []
    stop_reason: str | None = None
    hit_lane: str | None = None
    anomaly: str | None = None
    owned_tree_identities: list[ProcessIdentity] = []
    owned_process_survivors: list[ProcessIdentity] = []
    stop_evidence: dict[str, dict[str, Any]] = {}
    tree_audit_error: str | None = None
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
            _require(time.time() < deadline_unix,
                     "deadline reached during startup; no additional workers allowed")
            spec.stdout_path.parent.mkdir(parents=True, exist_ok=True)
            stdout = spec.stdout_path.open("xb")
            stderr = spec.stderr_path.open("xb")
            try:
                process = subprocess.Popen(
                    list(spec.command), cwd=str(spec.cwd), env=base_environment,
                    stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                    creationflags=base.process_creation_flags(),
                    start_new_session=(os.name != "nt"),
                )
            finally:
                stdout.close()
                stderr.close()
            owned.append(base.OwnedLane(spec, process, utc_now()))
        _require(len(owned) == 45, "recovery did not launch exactly 45 interrupted lanes")
        _write_state(state_path, status="RUNNING", retained_records=retained_records,
                     owned=owned, anomaly=None)

        last_state = time.monotonic()
        while True:
            if time.time() >= deadline_unix:
                stop_reason = "ORIGINAL_DEADLINE"
                break
            event = False
            for lane in owned:
                if time.time() >= deadline_unix:
                    stop_reason = "ORIGINAL_DEADLINE"
                    break
                if lane.normalized_status != "RUNNING":
                    continue
                if lane.spec.stderr_path.exists() and lane.spec.stderr_path.stat().st_size > 0:
                    anomaly = f"nonempty recovery stderr: {lane.spec.lane_id}"
                    stop_reason = "FAILED"
                    event = True
                    break
                return_code = lane.process.poll()
                normalized, raw, detail = base.normalize_lane_result(lane.spec)
                if return_code is None:
                    if normalized == "HIT_VERIFIED":
                        # A terminal summary is insufficient until the child
                        # itself exits zero; the exit branch performs the
                        # supervisor verifier gate.
                        continue
                    if normalized == "FAILED":
                        lane.normalized_status = normalized
                        lane.raw_status = raw
                        lane.status_detail = detail
                        anomaly = f"failed live recovery result: {lane.spec.lane_id}"
                        stop_reason = "FAILED"
                        event = True
                        break
                    continue

                lane.return_code = return_code
                lane.finished_utc = utc_now()
                if normalized == "RUNNING":
                    normalized = "FAILED"
                    detail = {"summary": detail.get("summary"),
                              "error": "process exited with RUNNING summary"}
                if return_code != 0 and normalized in {"NO_HIT", "HIT_VERIFIED"}:
                    normalized = "FAILED"
                    detail = {
                        "summary": detail.get("summary"),
                        "error": (
                            "terminal result requires return code zero; got "
                            f"{return_code}"
                        ),
                    }
                if normalized == "HIT_VERIFIED":
                    accepted, evidence = verifier_gate(
                        lane.spec, detail, engine_dir,
                        run_dir / "supervisor_verification" / lane.spec.lane_id,
                    )
                    detail = dict(detail)
                    detail["supervisor_verification"] = evidence
                    normalized = "HIT_VERIFIED" if accepted else "FAILED"
                    if not accepted:
                        anomaly = f"supervisor verifier disagreement: {lane.spec.lane_id}"
                lane.normalized_status = normalized
                lane.raw_status = raw
                lane.status_detail = detail
                event = True
                if normalized == "HIT_VERIFIED":
                    hit_lane = lane.spec.lane_id
                    stop_reason = "HIT_VERIFIED"
                    break
                if normalized in {"FAILED", "MISSING_SUMMARY"}:
                    anomaly = anomaly or f"invalid completed recovery result: {lane.spec.lane_id}"
                    stop_reason = "FAILED"
                    break

            if stop_reason is not None:
                break
            if all(lane.normalized_status != "RUNNING" for lane in owned):
                stop_reason = "ALL_COMPLETED"
                break
            if time.time() >= deadline_unix:
                stop_reason = "ORIGINAL_DEADLINE"
                break
            if event or time.monotonic() - last_state >= STATE_HEARTBEAT_SECONDS:
                _write_state(state_path, status="RUNNING",
                             retained_records=retained_records, owned=owned,
                             anomaly=anomaly)
                last_state = time.monotonic()
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        stop_reason = "INTERRUPTED"
        anomaly = "recovery supervisor interrupted"
    except BaseException as error:
        stop_reason = "FAILED"
        anomaly = f"recovery supervisor exception: {type(error).__name__}: {error}"
        (run_dir / "recovery_exception.txt").write_text(
            traceback.format_exc(), encoding="utf-8", newline="\n"
        )
    finally:
        try:
            owned_tree_identities = _capture_owned_process_tree(owned)
        except BaseException as error:
            tree_audit_error = f"{type(error).__name__}: {error}"
            anomaly = f"owned process tree snapshot failed: {tree_audit_error}"
            stop_reason = "FAILED"
            owned_tree_identities = []
        for lane in owned:
            try:
                evidence, supplemental = _stop_owned_recovery_process(lane)
                stop_evidence[lane.spec.lane_id] = evidence
                known = {
                    (item.pid, item.create_time) for item in owned_tree_identities
                }
                owned_tree_identities.extend(
                    item for item in supplemental
                    if (item.pid, item.create_time) not in known
                )
            except BaseException as error:
                stop_evidence[lane.spec.lane_id] = {
                    "action": "stop_exception",
                    "error": f"{type(error).__name__}: {error}",
                }
                anomaly = f"owned process stop failed: {lane.spec.lane_id}"
                stop_reason = "FAILED"
        base.reap_owned(owned)
        dead_root_failures = [
            lane.spec.lane_id for lane in owned if lane.process.poll() is None
        ]
        owned_process_survivors = _wait_for_owned_tree_death(owned_tree_identities)
        for lane in owned:
            lane_survivors = [
                item for item in owned_process_survivors
                if item.lane_id == lane.spec.lane_id
            ]
            root_live = lane.process.poll() is None
            evidence = stop_evidence[lane.spec.lane_id]
            taskkill_failed = (
                evidence.get("action") == "taskkill_tree"
                and evidence.get("taskkill_exit") != 0
            )
            fallback = evidence.get("psutil_fallback")
            fallback_ready = (
                not taskkill_failed
                or (
                    isinstance(fallback, dict)
                    and (
                        (
                            fallback.get("root_suspended_before_resnapshot") is True
                            and fallback.get("tree_stabilized") is True
                            and fallback.get("freeze_errors") == []
                        )
                        or (
                            fallback.get("result")
                            == "root_exited_before_fallback_resnapshot"
                            and not root_live
                            and not lane_survivors
                        )
                    )
                )
            )
            verified = (
                tree_audit_error is None
                and not root_live
                and not lane_survivors
                and fallback_ready
            )
            evidence["independent_identity_check"] = {
                "root_popen_reaped": not root_live,
                "captured_identity_survivors": [
                    {"pid": item.pid, "create_time": item.create_time}
                    for item in lane_survivors
                ],
            }
            evidence["shutdown_verified"] = verified
        unverified_stops = [
            lane_id for lane_id, evidence in stop_evidence.items()
            if evidence.get("shutdown_verified") is not True
        ]
        if unverified_stops or dead_root_failures or owned_process_survivors:
            anomaly = "owned process tree shutdown was not independently verified"
            stop_reason = "FAILED"
        for lane in owned:
            if lane.return_code is None:
                lane.return_code = lane.process.poll()
            if lane.finished_utc is None:
                lane.finished_utc = utc_now()
            detail = dict(lane.status_detail)
            detail["stop_evidence"] = stop_evidence.get(lane.spec.lane_id, {})
            lane_survivors = [
                item for item in owned_process_survivors
                if item.lane_id == lane.spec.lane_id
            ]
            if lane_survivors:
                detail["owned_process_survivors"] = [
                    {"pid": item.pid, "create_time": item.create_time,
                     "command": list(item.command)}
                    for item in lane_survivors
                ]
            lane.status_detail = detail
            if lane.normalized_status == "RUNNING":
                if stop_reason == "ORIGINAL_DEADLINE":
                    lane.normalized_status = "TIMEOUT_INCOMPLETE"
                    lane.raw_status = "STOPPED_AT_ORIGINAL_DEADLINE"
                elif stop_reason == "HIT_VERIFIED":
                    lane.normalized_status = "STOPPED_AFTER_OTHER_HIT"
                    lane.raw_status = "RECOVERY_PORTFOLIO_STOP"
                elif stop_reason == "INTERRUPTED":
                    lane.normalized_status = "INTERRUPTED"
                    lane.raw_status = "RECOVERY_PORTFOLIO_STOP"
                else:
                    lane.normalized_status = "STOPPED_AFTER_RECOVERY_FAILURE"
                    lane.raw_status = "RECOVERY_PORTFOLIO_STOP"

    for lane in owned:
        _attach_prefix_coverage(lane, prefix_checkpoints)

    records = _all_records(retained_records, owned)
    statuses = [str(record["status"]) for record in records]
    if stop_reason == "HIT_VERIFIED":
        overall, exit_code = "HIT_VERIFIED", 0
    elif stop_reason == "ALL_COMPLETED" and all(status == "NO_HIT" for status in statuses):
        overall, exit_code = "NO_HIT_DECLARED_DOMAINS", 0
    elif stop_reason == "ORIGINAL_DEADLINE" or "TIMEOUT_INCOMPLETE" in statuses:
        overall, exit_code = "TIMEOUT_INCOMPLETE", 4
    elif stop_reason == "INTERRUPTED":
        overall, exit_code = "INTERRUPTED", 130
    else:
        overall, exit_code = "FAILED", 3

    original_unchanged: bool | None = None
    changed_original_files: list[str] = []
    if original_inventory is not None and original_run_dir is not None:
        current_inventory = artifact_inventory(original_run_dir)
        keys = set(original_inventory) | set(current_inventory)
        changed_original_files = sorted(
            key for key in keys
            if original_inventory.get(key) != current_inventory.get(key)
        )
        original_unchanged = not changed_original_files
        if not original_unchanged:
            overall, exit_code = "FAILED", 3
            anomaly = "original artifact tree changed during recovery"

    nonempty_recovery_stderr = [
        lane.spec.lane_id for lane in owned
        if lane.spec.stderr_path.exists() and lane.spec.stderr_path.stat().st_size > 0
    ]
    summary = {
        "schema_version": SCHEMA_VERSION,
        "kind": "magic_square_squares_frozen_tranche_recovery_summary",
        "run_id": RECOVERY_RUN_ID,
        "source_run_id": ORIGINAL_RUN_ID,
        "source_portfolio_status": "FAILED",
        "status": overall,
        "proof_claim": False,
        "claim_scope": (
            "A no-hit or timeout concerns only the original 64 finite domains in "
            "LANE_MANIFEST.md; it is not an impossibility proof."
        ),
        "original_started_utc": "2026-07-20T22:17:30.000+00:00",
        "original_deadline_utc": "2026-07-21T06:17:30.000+00:00",
        "finished_utc": utc_now(),
        "manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "approved_artifact_hashes": approved_artifact_hashes(),
        "workers_requested_original": 64,
        "workers_launched_recovery": len(owned),
        "retained_completed_lanes": len(retained_records),
        "combined_lane_count": len(records),
        "stop_reason": stop_reason,
        "hit_lane": hit_lane,
        "anomaly": anomaly,
        "owned_tree_snapshot_error": tree_audit_error,
        "unverified_stop_lanes": unverified_stops,
        "dead_root_failures": dead_root_failures,
        "owned_process_survivors": [
            {"lane": item.lane_id, "pid": item.pid,
             "create_time": item.create_time, "command": list(item.command)}
            for item in owned_process_survivors
        ],
        "source_anomaly_retained_as_provenance": "nonempty stderr: N14",
        "nonempty_recovery_stderr_lanes": nonempty_recovery_stderr,
        "original_artifacts_unchanged": original_unchanged,
        "changed_original_files": changed_original_files,
        "lane_status_counts": {
            status: statuses.count(status) for status in sorted(set(statuses))
        },
        "lanes": records,
    }
    atomic_write_json(summary_path, summary)
    _write_state(state_path, status=overall, retained_records=retained_records,
                 owned=owned, anomaly=anomaly)
    return exit_code


def execute_production_recovery(engine_dir: Path) -> int:
    preflight = validate_original_failure(
        engine_dir, require_approved_engine=True, require_dead_workers=True
    )
    # Recheck time after all hash and artifact reads, immediately before the
    # irreversible run-once reservation.
    remaining = ORIGINAL_DEADLINE_UNIX - time.time()
    _require(remaining > 0, "original absolute deadline passed after preflight")
    run_dir = reserve_and_stage(preflight)
    specs = recovery_specs(
        engine_dir, run_dir, remaining_seconds=remaining,
        prefix_checkpoints=preflight.prefix_checkpoints,
    )
    return run_recovery_specs(
        specs, preflight.retained_records, run_dir, engine_dir.resolve(),
        deadline_unix=ORIGINAL_DEADLINE_UNIX,
        original_inventory=preflight.original_inventory,
        original_run_dir=preflight.original_run_dir,
        prefix_checkpoints=preflight.prefix_checkpoints,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute-recovery", action="store_true",
        help="create the run-once recovery and launch only the 45 interrupted lanes",
    )
    args = parser.parse_args(argv)
    engine_dir = Path(__file__).resolve().parent
    try:
        if args.execute_recovery:
            return execute_production_recovery(engine_dir)
        preflight = validate_original_failure(
            engine_dir, require_approved_engine=False, require_dead_workers=False
        )
        current_gaussian = preflight.executable_hashes["gaussian_center.exe"]
        approved = (
            APPROVED_GAUSSIAN_EXE_SHA256 != "PENDING_PATCHED_GAUSSIAN_APPROVAL"
            and current_gaussian == APPROVED_GAUSSIAN_EXE_SHA256
        )
        print(json.dumps({
            "status": "PREFLIGHT_ONLY",
            "processes_launched": 0,
            "exact_failure_match": True,
            "retained_completed_lanes": len(preflight.retained_records),
            "recovery_lanes": len(RECOVERED_LANE_IDS),
            "original_deadline_unix": ORIGINAL_DEADLINE_UNIX,
            "seconds_remaining": max(0.0, ORIGINAL_DEADLINE_UNIX - time.time()),
            "gaussian_exe_sha256": current_gaussian,
            "approved_gaussian_hash": APPROVED_GAUSSIAN_EXE_SHA256,
            "launch_authorized_by_hash": approved,
        }, sort_keys=True))
        return 0
    except RecoveryRefused as error:
        print(json.dumps({
            "status": "RECOVERY_REFUSED",
            "processes_launched": 0,
            "error": str(error),
        }, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
