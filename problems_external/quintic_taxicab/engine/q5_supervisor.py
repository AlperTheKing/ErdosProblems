#!/usr/bin/env python3
"""Fail-closed supervisor for one hash-pinned Q5-TORSOR campaign.

The default operation is audit-only.  Launch requires the exact manifest
payload digest, campaign id, and campaign/search modes on the command line.
Only nonempty lanes are spawned, every child is single-threaded and hidden on
Windows, and at most 64 owned children can exist.  The supervisor terminates
only its own ``Popen`` children.

Lane result and supervisor state files are JSON committed by atomic replace.
A worker candidate is not accepted until the existing exact Python and native
C++ verifiers independently return exit code zero, empty stderr, and a valid
JSON report for the same integer quadruple.
"""

from __future__ import annotations

import argparse
import contextlib
import ctypes
import hashlib
import json
import os
import math
import re
import stat
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping, Sequence

import q5_manifest as manifest_lib


RESULT_KIND = "Q5_TORSOR_LANE_RESULT"
RESULT_STATUSES = {"HIT", "NO_HIT", "TIMEOUT_INCOMPLETE", "FAIL_CLOSED"}
SEMANTIC_EXIT_CODES = {
    "NO_HIT": 0,
    "TIMEOUT_INCOMPLETE": 3,
    "HIT": 10,
}
DECIMAL_RE = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
UNSIGNED_DECIMAL_RE = re.compile(r"0|[1-9][0-9]*\Z")
POSITIVE_DECIMAL_RE = re.compile(r"[1-9][0-9]*\Z")
RATIONAL_RE = re.compile(r"0|(?:-?[1-9][0-9]*)(?:/[1-9][0-9]*)?\Z")
COUNT_KEYS = {
    "reduced_u_values",
    "reduced_t_values",
    "pairs_considered",
    "admissible_specializations",
    "zero_u_tested",
    "radicand_squares",
    "y_signs_tested",
    "nonnegative_z",
    "z_squares",
    "bounded_z_squares",
    "repeated_entry_rejections",
    "candidate_records",
    "verified_integer_certificates",
}
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
ARTIFACT_ROLES = {
    "worker",
    "worker_source",
    "scalar_verifier",
    "independent_verifier",
    "manifest_tool",
    "supervisor",
    "python_interpreter",
}
AGGREGATE_MUTEX_NAME = "Global\\Q5_TORSOR_MACHINE_WORKER_CAP_V1"
ENGINE_DIR = Path(__file__).resolve().parent
TRANCHE_ID = "q5-eight-hour-tranche-v1"
TRANCHE_DIR = ENGINE_DIR / "logs" / TRANCHE_ID
TRANCHE_LOCK_PATH = ENGINE_DIR / "q5_tranche.lock"
TRANCHE_PLAN_PATH = TRANCHE_DIR / "plan.json"
TRANCHE_STATE_PATH = TRANCHE_DIR / "state.json"
SELECTION_REPORT_PATH = TRANCHE_DIR / "selection_report.json"
PUBLIC_STATUS_PATH = TRANCHE_DIR / "public_status_gate.json"
READINESS_PATH = ENGINE_DIR / "Q5_LAUNCH_READY.json"
AUTHORIZATION_DIR = TRANCHE_DIR / "authorizations"
MAGIC_ENGINE_DIR = ENGINE_DIR.parent.parent / "magic_square_squares" / "engine"
PROCESS_ROOTS = (ENGINE_DIR.resolve(), MAGIC_ENGINE_DIR.resolve())
INTERPRETER_NAMES = {
    "python", "python.exe", "python3", "python3.exe",
    "pwsh", "pwsh.exe", "powershell", "powershell.exe",
}
READINESS_ARTIFACTS = {
    "q5_tranche.py",
    "q5_supervisor.py",
    "q5_manifest.py",
    "q5_manifest_transaction.py",
    "q5_public_status.py",
    "run_q5_supervisor_hidden.ps1",
}
READINESS_TEST_FILES = (
    "test_q5_manifest_supervisor.py",
    "test_q5_tranche.py",
    "test_q5_public_status.py",
    "test_q5_manifest_transaction.py",
    "test_q5_candidate_table.py",
    "test_scan_torsor_exact.py",
    "test_reference_enumerator.py",
    "test_verify_certificate.py",
    "test_verify_independent.py",
    "test_pari_quartic_calibration.py",
)
AUTHORIZATION_PHASES = {"A", "B", "C", "D", "MAIN"}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
WAIT_OBJECT_0 = 0x00000000
WAIT_ABANDONED = 0x00000080
WAIT_TIMEOUT = 0x00000102
TRANCHE_LOCK_KEYS = {
    "schema_version", "kind", "tranche_id", "t0", "s", "g",
    "creator_pid", "claimed_utc", "magic_terminal_summary_sha256",
    "frozen_artifact_hashes", "boot_time_microseconds", "monotonic_start_ns",
    "launch_readiness_sha256",
}
TRANCHE_PLAN_KEYS = {
    "schema_version", "kind", "tranche_id", "t0", "s", "g",
    "magic_terminal", "global_lock_sha256", "preflight_censuses",
    "frozen_artifact_hashes", "pilots", "main", "candidate_table",
    "selection_rule", "setup_guard_milliseconds", "launch_readiness",
    "authorization_paths",
}
TRANCHE_STATE_KEYS = {
    "schema_version", "kind", "tranche_id", "revision", "phase",
    "t0", "s", "g", "plan_sha256", "last_intent", "accepted_pilots",
    "selection_report_sha256", "selected_h",
    "selected_main_manifest_sha256", "verified_hit",
    "main_terminal_report_sha256", "persistent_error", "updated_utc",
}


class SupervisorError(RuntimeError):
    """Raised whenever execution cannot be certified under the contract."""


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _path_token(token: str, cwd: str | None) -> Path | None:
    candidate = token.strip().strip('"')
    if not candidate or candidate.startswith("-"):
        return None
    try:
        path = Path(candidate)
        if not path.is_absolute():
            if not cwd:
                return None
            path = Path(cwd) / path
        return path.resolve()
    except OSError:
        return None


def _process_is_relevant(info: Mapping[str, Any]) -> tuple[bool, list[str]]:
    """Classify direct paths plus cwd/module/import-style Q5 invocations."""

    cwd_text = str(info.get("cwd") or "")
    cwd_path: Path | None = None
    if cwd_text:
        try:
            cwd_path = Path(cwd_text).resolve()
        except OSError:
            cwd_path = None
    cmdline = [str(token) for token in (info.get("cmdline") or [])]
    exe_text = str(info.get("exe") or "")
    name = str(info.get("name") or Path(exe_text).name).casefold()
    resolved: list[Path] = []
    for token in [*cmdline, exe_text]:
        path = _path_token(token, cwd_text or None)
        if path is not None:
            resolved.append(path)
    matched = sorted(
        {str(path) for path in resolved if any(_is_within(path, root) for root in PROCESS_ROOTS)}
    )
    cwd_under_root = cwd_path is not None and any(
        _is_within(cwd_path, root) for root in PROCESS_ROOTS
    )
    joined = " ".join(cmdline).casefold().replace("/", "\\")
    module_or_import = any(
        marker in joined
        for marker in (
            "q5_supervisor", "q5_tranche", "q5_manifest",
            "quintic_taxicab", "scan_torsor_exact",
            "magic_square_squares", "recovery_supervisor",
            "tranche_supervisor", "s_lane_search",
        )
    )
    interpreter = name in INTERPRETER_NAMES or Path(exe_text).name.casefold() in INTERPRETER_NAMES
    return bool(matched or module_or_import or (cwd_under_root and interpreter)), matched


def _known_process_chain() -> set[int]:
    try:
        import psutil  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SupervisorError("psutil is required for the live process census") from exc
    result = {os.getpid()}
    try:
        parent = psutil.Process(os.getpid()).parent()
        while parent is not None:
            if parent.pid in result:
                raise SupervisorError("current process ancestor chain contains a cycle")
            result.add(parent.pid)
            parent = parent.parent()
    except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied, OSError) as exc:
        raise SupervisorError(f"cannot identify current process ancestor chain: {exc}") from exc
    return result


def live_relevant_process_census(
    *, exempt_pids: set[int] | None = None
) -> dict[str, Any]:
    """Return every live Q5/magic process not in the explicit caller chain."""

    try:
        import psutil  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SupervisorError("psutil is required for the live process census") from exc
    exempt = _known_process_chain() if exempt_pids is None else set(exempt_pids)
    active: list[dict[str, Any]] = []
    errors: list[str] = []
    for process in psutil.process_iter(
        ["pid", "ppid", "create_time", "name", "exe", "cmdline", "cwd"]
    ):
        try:
            info = process.info
            pid = int(info["pid"])
            if pid in exempt:
                continue
            relevant, matched = _process_is_relevant(info)
            if relevant:
                active.append(
                    {
                        "pid": pid,
                        "ppid": int(info.get("ppid") or 0),
                        "create_time": info.get("create_time"),
                        "name": str(info.get("name") or ""),
                        "exe": str(info.get("exe") or ""),
                        "argv": list(info.get("cmdline") or []),
                        "cwd": str(info.get("cwd") or ""),
                        "matched_paths": matched,
                    }
                )
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except (psutil.AccessDenied, OSError) as exc:
            try:
                name = process.name().casefold()
            except Exception:
                name = ""
            if name in INTERPRETER_NAMES or name in {
                "scan_torsor_exact.exe", "s_lane_search.exe",
                "elliptic_integral_search.exe", "gaussian_center.exe",
            }:
                errors.append(f"pid {process.pid} census denied: {type(exc).__name__}")
    active.sort(key=lambda row: (row["pid"], row["create_time"] or 0))
    return {"active_processes": active, "errors": errors}


def assert_clean_relevant_process_census() -> dict[str, Any]:
    census = live_relevant_process_census()
    if census["errors"] or census["active_processes"]:
        raise SupervisorError(f"relevant live process census is not clean: {census}")
    return census


def assert_no_unowned_relevant_processes(
    active: Mapping[int, subprocess.Popen[Any]],
) -> dict[str, Any]:
    """Reject any relevant process outside this supervisor's owned worker set."""

    owned_pids = {process.pid for process in active.values()}
    if len(owned_pids) != len(active) or len(owned_pids) > manifest_lib.LANE_COUNT:
        raise SupervisorError("owned worker identity/cap is invalid")
    census = live_relevant_process_census(
        exempt_pids=_known_process_chain() | owned_pids
    )
    if census["errors"] or census["active_processes"]:
        raise SupervisorError(
            f"unowned relevant process appeared during Q5 execution: {census}"
        )
    return census


def _boot_time_microseconds() -> int:
    try:
        import psutil  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SupervisorError("psutil is required for the boot identity") from exc
    try:
        return int(psutil.boot_time() * 1_000_000)
    except (OSError, ValueError, OverflowError) as exc:
        raise SupervisorError(f"cannot obtain system boot identity: {exc}") from exc


class DeadlineGuard:
    """Fail-closed wall/monotonic S/local deadline plus immutable hard G."""

    def __init__(
        self, *, deadline: datetime, t0: datetime, monotonic_start_ns: int,
        boot_time_microseconds: int, hard_deadline: datetime | None = None,
        launch_readiness_sha256: str | None = None,
        authorization_sha256: str | None = None,
        authorization_expires_utc: str | None = None,
        wall_clock: Callable[[], datetime] | None = None,
        monotonic_clock: Callable[[], int] | None = None,
        boot_clock: Callable[[], int] | None = None,
    ) -> None:
        self.deadline = deadline.astimezone(timezone.utc)
        self.hard_deadline = (hard_deadline or deadline).astimezone(timezone.utc)
        self.t0 = t0.astimezone(timezone.utc)
        self.monotonic_start_ns = monotonic_start_ns
        self.boot_time_microseconds = boot_time_microseconds
        if launch_readiness_sha256 is not None and (
            not isinstance(launch_readiness_sha256, str)
            or SHA256_RE.fullmatch(launch_readiness_sha256) is None
        ):
            raise SupervisorError("launch readiness SHA-256 is malformed")
        self.launch_readiness_sha256 = launch_readiness_sha256
        if (authorization_sha256 is None) != (authorization_expires_utc is None):
            raise SupervisorError("authorization hash/expiry binding is incomplete")
        if authorization_sha256 is not None:
            _strict_sha(authorization_sha256, "authorization SHA-256")
            authorization_expires = _parse_utc(
                authorization_expires_utc, "authorization expires_utc"
            )
        else:
            authorization_expires = None
        self.authorization_sha256 = authorization_sha256
        self.authorization_expires_utc = authorization_expires_utc
        self.authorization_expires = authorization_expires
        self._wall_clock = wall_clock or (lambda: datetime.now(timezone.utc))
        self._monotonic_clock = monotonic_clock or time.monotonic_ns
        self._boot_clock = boot_clock or _boot_time_microseconds
        def elapsed_ns(target: datetime) -> int:
            delta = target - self.t0
            return ((delta.days * 86400 + delta.seconds) * 1_000_000_000
                    + delta.microseconds * 1_000)
        deadline_ns = elapsed_ns(self.deadline)
        hard_ns = elapsed_ns(self.hard_deadline)
        if deadline_ns <= 0 or hard_ns < deadline_ns:
            raise SupervisorError("deadline/hard deadline does not follow immutable T0")
        self.monotonic_deadline_ns = monotonic_start_ns + deadline_ns
        self.monotonic_hard_deadline_ns = monotonic_start_ns + hard_ns

    def _instant(self) -> tuple[datetime, int]:
        now = self._wall_clock().astimezone(timezone.utc)
        monotonic_now = self._monotonic_clock()
        if self._boot_clock() != self.boot_time_microseconds:
            raise SupervisorError("system boot identity changed after T0")
        if monotonic_now < self.monotonic_start_ns:
            raise SupervisorError("monotonic clock moved before T0")
        elapsed_us = (monotonic_now - self.monotonic_start_ns) // 1_000
        wall_us = int((now - self.t0).total_seconds() * 1_000_000)
        if wall_us + 5_000_000 < elapsed_us:
            raise SupervisorError("wall clock rollback detected against monotonic tranche clock")
        return now, monotonic_now

    def assert_authorization_current(self) -> None:
        if self.authorization_expires is None:
            return
        now, _ = self._instant()
        if now >= self.authorization_expires:
            raise SupervisorError("launch authorization expired before claim/spawn")

    def reached(self) -> bool:
        now, monotonic_now = self._instant()
        return now >= self.deadline or monotonic_now >= self.monotonic_deadline_ns

    def hard_reached(self) -> bool:
        now, monotonic_now = self._instant()
        return now >= self.hard_deadline or monotonic_now >= self.monotonic_hard_deadline_ns


class _LockedPathSet:
    """Hold read handles that deny write/delete replacement on Windows."""

    def __init__(self, paths: Sequence[Path]) -> None:
        self.paths = tuple(sorted({path.resolve() for path in paths}, key=lambda p: str(p).casefold()))
        self._handles: list[Any] = []

    def __enter__(self) -> "_LockedPathSet":
        try:
            if os.name == "nt":
                kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
                kernel32.CreateFileW.argtypes = [
                    ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
                    ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
                ]
                kernel32.CreateFileW.restype = ctypes.c_void_p
                for path in self.paths:
                    handle = kernel32.CreateFileW(
                        str(path), 0x80000000, 0x00000001, None, 3, 0x80, None
                    )
                    if handle in (None, ctypes.c_void_p(-1).value):
                        raise SupervisorError(
                            f"cannot lock runtime artifact {path}: {ctypes.get_last_error()}"
                        )
                    self._handles.append(int(handle))
            else:
                self._handles = [path.open("rb") for path in self.paths]
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        handles, self._handles = self._handles, []
        if os.name == "nt":
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
            kernel32.CloseHandle.restype = ctypes.c_bool
            for handle in reversed(handles):
                kernel32.CloseHandle(handle)
        else:
            for stream in reversed(handles):
                stream.close()


@contextlib.contextmanager
def locked_artifacts(
    artifacts: Mapping[str, Mapping[str, Any]]
) -> Iterator[None]:
    paths = [Path(record["path"]) for record in artifacts.values()]
    with _LockedPathSet(paths):
        validate_all_artifact_identity(artifacts)
        yield
        validate_all_artifact_identity(artifacts)


class _AggregateSupervisorReservation:
    """Machine-wide Windows mutex preventing overlapping Q5 supervisors."""

    def __init__(self) -> None:
        self._handle: int | None = None

    def __enter__(self) -> "_AggregateSupervisorReservation":
        if os.name != "nt":
            raise SupervisorError(
                "aggregate Q5 supervisor reservation requires Windows"
            )
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
        kernel32.CreateMutexW.restype = ctypes.c_void_p
        kernel32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        kernel32.WaitForSingleObject.restype = ctypes.c_uint32
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel32.CloseHandle.restype = ctypes.c_bool

        handle = kernel32.CreateMutexW(None, False, AGGREGATE_MUTEX_NAME)
        if not handle:
            raise SupervisorError(
                f"cannot create aggregate Q5 supervisor mutex: {ctypes.get_last_error()}"
            )
        wait_result = kernel32.WaitForSingleObject(handle, 0)
        if wait_result not in {WAIT_OBJECT_0, WAIT_ABANDONED}:
            kernel32.CloseHandle(handle)
            if wait_result == WAIT_TIMEOUT:
                raise SupervisorError("aggregate Q5 supervisor reservation is held")
            raise SupervisorError(
                f"aggregate Q5 supervisor mutex wait failed: {wait_result:#x}"
            )
        self._handle = int(handle)
        if wait_result == WAIT_ABANDONED:
            try:
                census = live_relevant_process_census()
                if census["errors"] or census["active_processes"]:
                    raise SupervisorError(
                        f"abandoned aggregate mutex has non-clean census: {census}"
                    )
            except BaseException:
                self.__exit__(None, None, None)
                raise
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        handle = self._handle
        self._handle = None
        if handle is None:
            return
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.ReleaseMutex.argtypes = [ctypes.c_void_p]
        kernel32.ReleaseMutex.restype = ctypes.c_bool
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel32.CloseHandle.restype = ctypes.c_bool
        kernel32.ReleaseMutex(handle)
        kernel32.CloseHandle(handle)

    def assert_active(self) -> None:
        """Require this exact reservation to hold the machine-wide mutex."""
        if self._handle is None:
            raise SupervisorError("aggregate Q5 supervisor reservation is not active")


def aggregate_supervisor_reservation() -> _AggregateSupervisorReservation:
    return _AggregateSupervisorReservation()


def validate_semantic_exit(returncode: int, status: str, lane_id: int) -> None:
    """Require the native worker's exact status/exit-code correspondence."""

    expected = SEMANTIC_EXIT_CODES.get(status)
    if expected is None:
        raise SupervisorError(
            f"lane {lane_id} status {status} has no accepted semantic exit"
        )
    if returncode != expected:
        raise SupervisorError(
            f"lane {lane_id} exit/status mismatch: code {returncode}, "
            f"status {status}, expected {expected}"
        )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def _load_json_bytes(path: Path) -> tuple[Any, bytes, str]:
    try:
        data = path.read_bytes()
        value = json.loads(data.decode("ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SupervisorError(f"cannot read strict JSON {path}: {exc}") from exc
    return value, data, hashlib.sha256(data).hexdigest()


def _parse_utc(value: Any, name: str) -> datetime:
    if not isinstance(value, str):
        raise SupervisorError(f"{name} must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SupervisorError(f"{name} is not valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SupervisorError(f"{name} must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _strict_sha(value: Any, name: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise SupervisorError(f"{name} is not a lowercase SHA-256 digest")
    return value


def validate_readiness(
    readiness: Any, *, engine_dir: Path = ENGINE_DIR, now: datetime | None = None
) -> dict[str, Any]:
    marker = dict(_require_keys(
        readiness,
        {
            "schema_version", "kind", "tranche_id", "created_utc",
            "artifacts", "tests", "referee_verdicts",
        },
        "Q5 launch readiness marker",
    ))
    if (
        marker["schema_version"] != 1
        or marker["kind"] != "q5-launch-readiness"
        or marker["tranche_id"] != TRANCHE_ID
    ):
        raise SupervisorError("Q5 launch readiness marker identity mismatch")
    created = _parse_utc(marker["created_utc"], "readiness created_utc")
    observed = datetime.now(timezone.utc) if now is None else now.astimezone(timezone.utc)
    if created > observed:
        raise SupervisorError("Q5 launch readiness marker is future-dated")
    artifacts = marker["artifacts"]
    if not isinstance(artifacts, dict) or set(artifacts) != READINESS_ARTIFACTS:
        raise SupervisorError("Q5 launch readiness artifact set mismatch")
    normalized: dict[str, str] = {}
    for relative_name in sorted(READINESS_ARTIFACTS):
        if Path(relative_name).as_posix() != relative_name or Path(relative_name).is_absolute():
            raise SupervisorError("readiness artifact name is not engine-relative POSIX")
        expected = _strict_sha(artifacts[relative_name], f"readiness artifact {relative_name}")
        artifact_path = (engine_dir / Path(relative_name)).resolve()
        if not artifact_path.is_file() or not _is_within(artifact_path, engine_dir.resolve()):
            raise SupervisorError(f"readiness artifact path is invalid: {relative_name}")
        if _sha256_file(artifact_path) != expected:
            raise SupervisorError(f"readiness artifact hash drift: {relative_name}")
        normalized[relative_name] = expected
    tests = dict(_require_keys(
        marker["tests"],
        {"passed", "failed", "commands", "test_files", "suite_sha256"},
        "readiness tests",
    ))
    passed = _strict_int(tests["passed"], "readiness tests passed", 1)
    failed = _strict_int(tests["failed"], "readiness tests failed", 0)
    suite_sha = _strict_sha(tests["suite_sha256"], "readiness suite_sha256")
    if passed <= 0 or failed != 0:
        raise SupervisorError("readiness tests do not certify a zero-failure suite")
    commands = tests["commands"]
    expected_commands = [
        "python -m unittest -v " + " ".join(
            f"problems_external.quintic_taxicab.engine.{Path(name).stem}"
            for name in READINESS_TEST_FILES
        )
    ]
    if commands != expected_commands:
        raise SupervisorError("readiness test command list mismatch")
    test_files = tests["test_files"]
    if not isinstance(test_files, dict) or set(test_files) != set(READINESS_TEST_FILES):
        raise SupervisorError("readiness test-file set mismatch")
    normalized_test_files: dict[str, str] = {}
    for relative_name in READINESS_TEST_FILES:
        expected = _strict_sha(
            test_files[relative_name], f"readiness test file {relative_name}"
        )
        test_path = (engine_dir / relative_name).resolve()
        if not test_path.is_file() or not _is_within(test_path, engine_dir.resolve()):
            raise SupervisorError(f"readiness test-file path is invalid: {relative_name}")
        if _sha256_file(test_path) != expected:
            raise SupervisorError(f"readiness test-file hash drift: {relative_name}")
        normalized_test_files[relative_name] = expected
    suite_payload = {
        "passed": passed,
        "failed": failed,
        "commands": commands,
        "test_files": normalized_test_files,
    }
    expected_suite_sha = hashlib.sha256(
        manifest_lib.canonical_bytes(suite_payload)
    ).hexdigest()
    if suite_sha != expected_suite_sha:
        raise SupervisorError("readiness suite hash mismatch")
    readiness_review_sha = hashlib.sha256(
        manifest_lib.canonical_bytes({"artifacts": normalized, "tests": tests})
    ).hexdigest()
    verdicts = marker["referee_verdicts"]
    if not isinstance(verdicts, list) or len(verdicts) != 2:
        raise SupervisorError("readiness requires exactly two referee verdicts")
    referee_names: set[str] = set()
    for raw in verdicts:
        verdict = dict(_require_keys(
            raw, {"referee", "verdict", "reviewed_readiness_sha256"},
            "readiness referee verdict",
        ))
        referee = verdict["referee"]
        if not isinstance(referee, str) or not referee.strip():
            raise SupervisorError("readiness referee name must be nonempty")
        referee_names.add(referee)
        if verdict["verdict"] != "LAUNCH_SAFE":
            raise SupervisorError("readiness referee verdict is not LAUNCH_SAFE")
        if verdict["reviewed_readiness_sha256"] != readiness_review_sha:
            raise SupervisorError("readiness referee review hash mismatch")
    if len(referee_names) != 2:
        raise SupervisorError("readiness referees must be distinct")
    return marker


def _validate_tranche_context(
    *, authorization: Any, authorization_sha: str, envelope: Mapping[str, Any], manifest_path: Path,
    state: Any, state_sha: str, plan: Any, plan_sha: str,
    lock: Any, lock_sha: str, readiness: Any, readiness_sha: str,
    selection_report: Any | None, selection_report_sha: str | None,
    public_status: Any | None, public_status_sha: str | None,
    now: datetime | None = None,
) -> DeadlineGuard:
    """Validate a controller ticket against immutable fixed tranche records."""

    auth = dict(_require_keys(
        authorization,
        {
            "schema_version", "kind", "tranche_id", "phase",
            "created_utc", "expires_utc", "state_path", "state_sha256",
            "manifest_path", "manifest_file_sha256",
            "manifest_payload_sha256", "campaign_id", "mode",
            "search_mode", "deadline", "run_dir", "readiness_path",
            "readiness_sha256", "public_status_path",
            "public_status_sha256",
        },
        "Q5 launch authorization",
    ))
    if (
        auth["schema_version"] != 1
        or auth["kind"] != "q5-launch-authorization-v1"
        or auth["tranche_id"] != TRANCHE_ID
        or auth["phase"] not in AUTHORIZATION_PHASES
    ):
        raise SupervisorError("Q5 launch authorization identity mismatch")
    observed = datetime.now(timezone.utc) if now is None else now.astimezone(timezone.utc)
    created = _parse_utc(auth["created_utc"], "authorization created_utc")
    expires = _parse_utc(auth["expires_utc"], "authorization expires_utc")
    if created > observed or expires <= observed or expires <= created:
        raise SupervisorError("Q5 launch authorization is not currently valid")
    if expires - created > timedelta(minutes=5):
        raise SupervisorError("Q5 launch authorization validity exceeds five minutes")

    state_record = dict(state) if isinstance(state, dict) else {}
    plan_record = dict(plan) if isinstance(plan, dict) else {}
    lock_record = dict(lock) if isinstance(lock, dict) else {}
    if set(state_record) != TRANCHE_STATE_KEYS:
        raise SupervisorError("fixed tranche state key set mismatch")
    if set(plan_record) != TRANCHE_PLAN_KEYS:
        raise SupervisorError("fixed tranche plan key set mismatch")
    if set(lock_record) != TRANCHE_LOCK_KEYS:
        raise SupervisorError("fixed tranche lock key set mismatch")
    if any(record.get("schema_version") != 1 for record in (state_record, plan_record, lock_record)):
        raise SupervisorError("fixed tranche schema version mismatch")
    revision = _strict_int(state_record.get("revision"), "state revision", 0)
    if state_record.get("last_intent") != f"transition_{revision:06d}.json":
        raise SupervisorError("fixed tranche state intent pointer mismatch")
    if _parse_utc(state_record.get("updated_utc"), "state updated_utc") > created:
        raise SupervisorError("authorization predates the pinned tranche state")
    if state_record.get("kind") != "Q5_TRANCHE_STATE" or state_record.get("tranche_id") != TRANCHE_ID:
        raise SupervisorError("fixed tranche state identity mismatch")
    if plan_record.get("kind") != "Q5_TRANCHE_PLAN" or plan_record.get("tranche_id") != TRANCHE_ID:
        raise SupervisorError("fixed tranche plan identity mismatch")
    if lock_record.get("kind") != "Q5_TRANCHE_GLOBAL_LOCK" or lock_record.get("tranche_id") != TRANCHE_ID:
        raise SupervisorError("fixed tranche lock identity mismatch")
    if auth["state_path"] != str(TRANCHE_STATE_PATH.resolve()) or auth["state_sha256"] != state_sha:
        raise SupervisorError("authorization state path/hash mismatch")
    if plan_record.get("global_lock_sha256") != lock_sha or state_record.get("plan_sha256") != plan_sha:
        raise SupervisorError("fixed tranche lock/plan/state hash chain mismatch")
    for key in ("t0", "s", "g"):
        if state_record.get(key) != plan_record.get(key) or state_record.get(key) != lock_record.get(key):
            raise SupervisorError(f"immutable tranche {key.upper()} mismatch")

    if lock_record.get("launch_readiness_sha256") != readiness_sha:
        raise SupervisorError("fixed tranche readiness differs from global lock")
    if plan_record.get("launch_readiness") != {
        "path": str(READINESS_PATH.resolve()),
        "file_sha256": readiness_sha,
    }:
        raise SupervisorError("fixed tranche readiness differs across lock/plan")
    expected_authorization_paths = {
        phase_name: str((AUTHORIZATION_DIR / f"{phase_name}.json").resolve())
        for phase_name in sorted(AUTHORIZATION_PHASES)
    }
    if plan_record.get("authorization_paths") != expected_authorization_paths:
        raise SupervisorError("fixed tranche authorization path map mismatch")

    phase = auth["phase"]
    expected_state_phase = "MAIN_FROZEN" if phase == "MAIN" else f"READY_{phase}"
    if state_record.get("phase") != expected_state_phase:
        raise SupervisorError(
            f"authorization phase {phase} does not match state {state_record.get('phase')}"
        )
    fixed_auth_path = (AUTHORIZATION_DIR / f"{phase}.json").resolve()
    if plan_record["authorization_paths"].get(phase) != str(fixed_auth_path):
        raise SupervisorError(f"authorization path is not fixed for phase {phase}")
    payload = envelope["payload"]
    digest = envelope["payload_sha256"]
    resolved_manifest = manifest_path.resolve()
    if auth["manifest_path"] != str(resolved_manifest):
        raise SupervisorError("authorization manifest path mismatch")
    if auth["manifest_payload_sha256"] != digest:
        raise SupervisorError("authorization manifest payload digest mismatch")
    if auth["campaign_id"] != payload["campaign_id"]:
        raise SupervisorError("authorization campaign id mismatch")
    if auth["mode"] != payload["mode"] or auth["search_mode"] != payload["search_mode"]:
        raise SupervisorError("authorization campaign/search mode mismatch")
    if auth["deadline"] != payload["deadline"] or auth["run_dir"] != payload["run_dir"]:
        raise SupervisorError("authorization deadline/run_dir mismatch")
    if auth["readiness_path"] != str(READINESS_PATH.resolve()) or auth["readiness_sha256"] != readiness_sha:
        raise SupervisorError("authorization readiness path/hash mismatch")
    validate_readiness(readiness, now=observed)

    if phase == "MAIN":
        main = plan_record.get("main")
        if not isinstance(main, dict):
            raise SupervisorError("fixed tranche main plan is malformed")
        if (
            auth["manifest_path"] != main.get("manifest_path")
            or auth["campaign_id"] != main.get("campaign_id")
            or auth["run_dir"] != main.get("run_dir")
            or auth["deadline"] != state_record.get("s")
            or auth["deadline"] != main.get("deadline")
        ):
            raise SupervisorError("MAIN authorization differs from fixed main plan")
        if payload["mode"] != "SELECTED_MAIN" or payload["search_mode"] != "canonical_positive_u_positive_y":
            raise SupervisorError("MAIN authorization mode mismatch")
        if state_record.get("selected_main_manifest_sha256") != digest:
            raise SupervisorError("MAIN digest differs from frozen selection")
        if selection_report_sha is None or state_record.get("selection_report_sha256") != selection_report_sha:
            raise SupervisorError("MAIN selection report hash mismatch")
        if not isinstance(selection_report, dict) or selection_report.get("selected_main_manifest_sha256") != digest:
            raise SupervisorError("MAIN selection report payload mismatch")
        if auth["public_status_path"] != str(PUBLIC_STATUS_PATH.resolve()):
            raise SupervisorError("MAIN public-status path mismatch")
        if public_status_sha is None or auth["public_status_sha256"] != public_status_sha:
            raise SupervisorError("MAIN public-status hash mismatch")
        if not isinstance(public_status, dict):
            raise SupervisorError("MAIN public-status record is malformed")
        try:
            import q5_public_status as public_status_lib
            audited_public = public_status_lib.audit_gate(
                PUBLIC_STATUS_PATH, now=observed, require_fresh=True
            )
        except Exception as exc:
            raise SupervisorError(f"MAIN raw public-status audit failed: {exc}") from exc
        if audited_public != public_status:
            raise SupervisorError("MAIN public-status bytes differ from raw-capture audit")
        embedded = selection_report.get("public_status_gate")
        if not isinstance(embedded, dict) or embedded.get("file_sha256") != public_status_sha:
            raise SupervisorError("MAIN selection report public-status pin mismatch")
        if not all(public_status.get(key) is True for key in (
            "problem_open", "oeis_no_n5_value", "formal_conjecture_open"
        )):
            raise SupervisorError("MAIN public-status gate is not open")
        checked = _parse_utc(public_status.get("checked_utc"), "public-status checked_utc")
        if checked > observed or observed - checked > timedelta(minutes=5):
            raise SupervisorError("MAIN public-status gate is stale")
    else:
        if auth["public_status_path"] is not None or auth["public_status_sha256"] is not None:
            raise SupervisorError("pilot authorization must not carry public-status fields")
        pilots = plan_record.get("pilots")
        if not isinstance(pilots, list):
            raise SupervisorError("fixed tranche pilot plan is malformed")
        spec = next((row for row in pilots if isinstance(row, dict) and row.get("name") == phase), None)
        if spec is None:
            raise SupervisorError(f"fixed tranche lacks Pilot {phase}")
        if (
            auth["manifest_path"] != spec.get("manifest_path")
            or auth["campaign_id"] != spec.get("campaign_id")
            or auth["run_dir"] != spec.get("run_dir")
            or auth["search_mode"] != spec.get("search_mode")
            or auth["mode"] != "CALIBRATION_ONLY"
        ):
            raise SupervisorError(f"Pilot {phase} authorization differs from fixed plan")
        pilot_deadline = _parse_utc(auth["deadline"], f"Pilot {phase} deadline")
        manifest_created = _parse_utc(payload.get("created_utc"), "manifest created_utc")
        local_limit = _strict_int(spec.get("limit_seconds"), f"Pilot {phase} limit_seconds", 1)
        if pilot_deadline > manifest_created + timedelta(seconds=local_limit):
            raise SupervisorError(f"Pilot {phase} deadline exceeds its local limit")

    deadline = _parse_utc(auth["deadline"], "authorization deadline")
    t0 = _parse_utc(lock_record.get("t0"), "tranche T0")
    s = _parse_utc(lock_record.get("s"), "tranche S")
    g = _parse_utc(lock_record.get("g"), "tranche G")
    if deadline > s:
        raise SupervisorError("authorization deadline extends beyond S")
    guard = DeadlineGuard(
        deadline=deadline, t0=t0,
        monotonic_start_ns=_strict_int(lock_record.get("monotonic_start_ns"), "lock monotonic_start_ns", 0),
        hard_deadline=g,
        boot_time_microseconds=_strict_int(lock_record.get("boot_time_microseconds"), "lock boot_time_microseconds", 0),
        launch_readiness_sha256=readiness_sha,
        authorization_sha256=authorization_sha,
        authorization_expires_utc=auth["expires_utc"],
    )
    if guard.reached():
        raise SupervisorError("authorization deadline has already been reached")
    return guard


class _LaunchAuthorizationReservation:
    """Lock and validate the fixed controller ticket and its complete hash chain."""

    def __init__(
        self, *, authorization_path: Path, manifest_path: Path,
        envelope: Mapping[str, Any],
    ) -> None:
        self.authorization_path = authorization_path
        self.manifest_path = manifest_path
        self.envelope = envelope
        self._locks: _LockedPathSet | None = None
        self.deadline_guard: DeadlineGuard | None = None
        self.launch_readiness_sha256: str | None = None
        self.authorization_sha256: str | None = None
        self.authorization_expires_utc: str | None = None

    def __enter__(self) -> "_LaunchAuthorizationReservation":
        preliminary, _, preliminary_sha = _load_json_bytes(self.authorization_path)
        phase = preliminary.get("phase") if isinstance(preliminary, dict) else None
        if phase not in AUTHORIZATION_PHASES:
            raise SupervisorError("authorization phase is invalid")
        expected_path = (AUTHORIZATION_DIR / f"{phase}.json").resolve()
        if self.authorization_path.resolve() != expected_path:
            raise SupervisorError(f"authorization path is not fixed for phase {phase}")
        capture_paths: list[Path] = []
        paths = [
            expected_path, self.manifest_path.resolve(), TRANCHE_STATE_PATH.resolve(),
            TRANCHE_PLAN_PATH.resolve(), TRANCHE_LOCK_PATH.resolve(), READINESS_PATH.resolve(),
        ]
        paths.extend((ENGINE_DIR / name).resolve() for name in READINESS_ARTIFACTS)
        paths.extend(
            Path(record["path"]).resolve() for record in self.envelope["payload"]["artifacts"].values()
        )
        if phase == "MAIN":
            paths.extend([SELECTION_REPORT_PATH.resolve(), PUBLIC_STATUS_PATH.resolve()])
            preliminary_gate, _, _ = _load_json_bytes(PUBLIC_STATUS_PATH)
            if not isinstance(preliminary_gate, dict):
                raise SupervisorError("MAIN preliminary public-status gate is malformed")
            capture_root = (TRANCHE_DIR / "public_status_captures").resolve()
            capture_dir_value = preliminary_gate.get("capture_dir")
            sources_value = preliminary_gate.get("sources")
            if not isinstance(capture_dir_value, str) or not isinstance(sources_value, list):
                raise SupervisorError("MAIN preliminary public-status capture schema mismatch")
            capture_dir = Path(capture_dir_value).resolve()
            if not _is_within(capture_dir, capture_root):
                raise SupervisorError("MAIN public-status capture directory escapes fixed root")
            capture_paths = [capture_dir / "capture_index.json"]
            for source in sources_value:
                if not isinstance(source, dict) or not isinstance(source.get("content_path"), str):
                    raise SupervisorError("MAIN preliminary public-status source is malformed")
                capture_path = Path(source["content_path"]).resolve()
                if not _is_within(capture_path, capture_dir):
                    raise SupervisorError("MAIN public-status capture path escapes capture dir")
                capture_paths.append(capture_path)
            paths.extend(capture_paths)
        self._locks = _LockedPathSet(paths)
        self._locks.__enter__()
        try:
            authorization, _, authorization_sha = _load_json_bytes(expected_path)
            if authorization_sha != preliminary_sha:
                raise SupervisorError("authorization bytes changed before lock acquisition")
            if not isinstance(authorization, dict) or authorization.get("phase") != phase:
                raise SupervisorError("locked authorization phase differs from preliminary phase")
            manifest_value, _, manifest_sha = _load_json_bytes(self.manifest_path.resolve())
            if manifest_value != self.envelope:
                raise SupervisorError("locked manifest bytes differ from audited envelope")
            if authorization.get("manifest_file_sha256") != manifest_sha:
                raise SupervisorError("authorization manifest file hash mismatch")
            state, _, state_sha = _load_json_bytes(TRANCHE_STATE_PATH)
            plan, _, plan_sha = _load_json_bytes(TRANCHE_PLAN_PATH)
            lock, _, lock_sha = _load_json_bytes(TRANCHE_LOCK_PATH)
            readiness, _, readiness_sha = _load_json_bytes(READINESS_PATH)
            selection = public = None
            selection_sha = public_sha = None
            if phase == "MAIN":
                selection, _, selection_sha = _load_json_bytes(SELECTION_REPORT_PATH)
                public, _, public_sha = _load_json_bytes(PUBLIC_STATUS_PATH)
                actual_capture_dir = Path(public.get("capture_dir", "")).resolve() if isinstance(public, dict) else None
                actual_sources = public.get("sources") if isinstance(public, dict) else None
                if actual_capture_dir is None or not isinstance(actual_sources, list):
                    raise SupervisorError("locked MAIN public-status capture schema mismatch")
                actual_capture_paths = [actual_capture_dir / "capture_index.json"]
                for source in actual_sources:
                    if not isinstance(source, dict) or not isinstance(source.get("content_path"), str):
                        raise SupervisorError("locked MAIN public-status source is malformed")
                    actual_capture_paths.append(Path(source["content_path"]).resolve())
                if {path.resolve() for path in actual_capture_paths} != {path.resolve() for path in capture_paths}:
                    raise SupervisorError("locked MAIN capture path set differs from preliminary enumeration")
            guard = _validate_tranche_context(
                authorization=authorization, envelope=self.envelope,
                manifest_path=self.manifest_path, state=state, state_sha=state_sha,
                plan=plan, plan_sha=plan_sha, lock=lock, lock_sha=lock_sha,
                authorization_sha=authorization_sha,
                readiness=readiness, readiness_sha=readiness_sha,
                selection_report=selection, selection_report_sha=selection_sha,
                public_status=public, public_status_sha=public_sha,
            )
            self.deadline_guard = guard
            self.launch_readiness_sha256 = guard.launch_readiness_sha256
            self.authorization_sha256 = guard.authorization_sha256
            self.authorization_expires_utc = guard.authorization_expires_utc
            if (
                self.launch_readiness_sha256 is None
                or self.authorization_sha256 is None
                or self.authorization_expires_utc is None
            ):
                raise SupervisorError("authorized launch context is incomplete")
            assert_clean_relevant_process_census()
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def active_guard(
        self, *, envelope: Mapping[str, Any], manifest_path: Path
    ) -> DeadlineGuard:
        """Return the held guard only while the fixed authorization is locked."""
        if (
            self._locks is None
            or self.deadline_guard is None
            or self.envelope is not envelope
            or self.manifest_path.resolve() != manifest_path.resolve()
            or self.launch_readiness_sha256
            != self.deadline_guard.launch_readiness_sha256
            or self.authorization_sha256
            != self.deadline_guard.authorization_sha256
            or self.authorization_expires_utc
            != self.deadline_guard.authorization_expires_utc
        ):
            raise SupervisorError("launch authorization reservation is not active")
        return self.deadline_guard

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        locks, self._locks = self._locks, None
        self.deadline_guard = None
        self.launch_readiness_sha256 = None
        self.authorization_sha256 = None
        self.authorization_expires_utc = None
        if locks is not None:
            locks.__exit__(exc_type, exc, traceback)



def validate_runtime_identity(
    payload: Mapping[str, Any],
    runtime_paths: Mapping[str, Path] | None = None,
) -> None:
    """Bind this process to the three runtime artifacts pinned in the manifest."""

    if runtime_paths is None:
        manifest_file = getattr(manifest_lib, "__file__", None)
        if not isinstance(manifest_file, str):
            raise SupervisorError("imported q5_manifest has no filesystem identity")
        runtime_paths = {
            "supervisor": Path(__file__),
            "manifest_tool": Path(manifest_file),
            "python_interpreter": Path(sys.executable),
        }
    expected_roles = {"supervisor", "manifest_tool", "python_interpreter"}
    if set(runtime_paths) != expected_roles:
        raise SupervisorError("runtime identity role set mismatch")
    artifacts = payload["artifacts"]
    for role in sorted(expected_roles):
        try:
            current = Path(runtime_paths[role]).resolve(strict=True)
        except OSError as exc:
            raise SupervisorError(f"runtime {role} cannot be resolved: {exc}") from exc
        recorded = Path(artifacts[role]["path"]).resolve()
        if current != recorded:
            raise SupervisorError(
                f"runtime {role} path mismatch: {current} != {recorded}"
            )
        try:
            size = current.stat().st_size
            digest = _sha256_file(current)
        except OSError as exc:
            raise SupervisorError(f"runtime {role} cannot be hashed: {exc}") from exc
        if size != artifacts[role]["size"] or digest != artifacts[role]["sha256"]:
            raise SupervisorError(f"runtime {role} hash mismatch")


def _require_keys(value: Mapping[str, Any], expected: set[str], name: str) -> Mapping[str, Any]:
    keys = set(value)
    if keys != expected:
        raise SupervisorError(
            f"{name} keys differ: missing={sorted(expected-keys)}, "
            f"extra={sorted(keys-expected)}"
        )
    return value


def _strict_int(value: Any, name: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SupervisorError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise SupervisorError(f"{name} must be at least {minimum}")
    return value

def validate_all_artifact_identity(
    artifacts: Mapping[str, Mapping[str, Any]],
) -> None:
    """Rehash every manifest artifact immediately before executable use."""

    if not isinstance(artifacts, Mapping) or set(artifacts) != ARTIFACT_ROLES:
        raise SupervisorError("manifest artifact role set mismatch")
    for role in sorted(ARTIFACT_ROLES):
        record = artifacts[role]
        if not isinstance(record, Mapping) or set(record) != {"path", "size", "sha256"}:
            raise SupervisorError(f"artifact {role} record is malformed")
        path_text = record["path"]
        size = record["size"]
        digest = record["sha256"]
        if (
            not isinstance(path_text, str)
            or isinstance(size, bool)
            or not isinstance(size, int)
            or size < 0
            or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        ):
            raise SupervisorError(f"artifact {role} identity is malformed")
        try:
            current = Path(path_text).resolve(strict=True)
            current_size = current.stat().st_size
            current_digest = _sha256_file(current)
        except OSError as exc:
            raise SupervisorError(f"artifact {role} cannot be rehashed: {exc}") from exc
        if str(current) != path_text or current_size != size or current_digest != digest:
            raise SupervisorError(f"artifact {role} identity changed before execution")


def _load_strict_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SupervisorError(f"cannot read strict JSON {path}: {exc}") from exc


def _now_text() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _claim_run_dir(
    run_dir: Path, payload: Mapping[str, Any], payload_digest: str,
    launch_readiness_sha256: str, authorization_sha256: str,
    authorization_expires_utc: str,
) -> Path:
    """Atomically claim a fresh run directory and permanently forbid reuse."""

    readiness_sha = _strict_sha(
        launch_readiness_sha256, "launch lock readiness SHA-256"
    )
    authorization_sha = _strict_sha(
        authorization_sha256, "launch lock authorization SHA-256"
    )
    authorization_expires = _parse_utc(
        authorization_expires_utc, "launch lock authorization expires_utc"
    )
    run_dir.mkdir(parents=True, exist_ok=True)
    lock_path = run_dir / "launch.lock"
    try:
        with lock_path.open("xb") as stream:
            claimed = datetime.now(timezone.utc)
            if claimed >= authorization_expires:
                raise SupervisorError("launch authorization expired at run-dir claim")
            claimed_utc = claimed.isoformat(timespec="microseconds").replace(
                "+00:00", "Z"
            )
            claim = {
                "schema_version": 1,
                "kind": "Q5_TORSOR_LAUNCH_LOCK",
                "campaign_id": payload["campaign_id"],
                "manifest_payload_sha256": payload_digest,
                "launch_readiness_sha256": readiness_sha,
                "authorization_sha256": authorization_sha,
                "authorization_expires_utc": authorization_expires_utc,
                "supervisor_pid": os.getpid(),
                "claimed_utc": claimed_utc,
            }
            stream.write(
                json.dumps(claim, sort_keys=True, separators=(",", ":")).encode("ascii")
                + b"\n"
            )
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise SupervisorError(f"run_dir launch lock already exists: {lock_path}") from exc
    except OSError as exc:
        raise SupervisorError(f"cannot atomically claim run_dir {run_dir}: {exc}") from exc
    try:
        entries = list(run_dir.iterdir())
    except OSError as exc:
        raise SupervisorError(f"cannot inspect run_dir {run_dir}: {exc}") from exc
    if set(entries) != {lock_path}:
        raise SupervisorError(f"run_dir was not fresh when claimed: {run_dir}")
    return lock_path


def _atomic_state(path: Path, value: Any) -> None:
    manifest_lib.atomic_write_json(path, value)


def _owned_pids(active: Mapping[int, subprocess.Popen[Any]]) -> list[int]:
    return sorted(process.pid for process in active.values())


def _terminate_owned(active: Mapping[int, subprocess.Popen[Any]]) -> dict[str, Any]:
    """Terminate owned children and report errors plus every observed survivor."""

    errors: list[str] = []
    for process in active.values():
        if process.poll() is None:
            try:
                process.terminate()
            except OSError as exc:
                errors.append(f"pid {process.pid} terminate failed: {exc}")
    deadline = time.monotonic() + 2.0
    for process in active.values():
        remaining = max(0.0, deadline - time.monotonic())
        if process.poll() is None:
            try:
                process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                pass  # Expected escalation to kill below.
            except OSError as exc:
                errors.append(f"pid {process.pid} pre-kill wait failed: {exc}")
    for process in active.values():
        if process.poll() is None:
            try:
                process.kill()
            except OSError as exc:
                errors.append(f"pid {process.pid} kill failed: {exc}")
    for process in active.values():
        if process.poll() is None:
            try:
                process.wait(timeout=2.0)
            except (subprocess.TimeoutExpired, OSError) as exc:
                errors.append(f"pid {process.pid} final wait failed: {exc}")

    survivors = sorted(
        process.pid for process in active.values() if process.poll() is None
    )
    return {"survivor_pids": survivors, "errors": errors}


def _rational(token: Any, name: str) -> Fraction:
    if not isinstance(token, str) or RATIONAL_RE.fullmatch(token) is None:
        raise SupervisorError(f"{name} is not a canonical rational string")
    try:
        value = Fraction(token)
    except (ValueError, ZeroDivisionError) as exc:
        raise SupervisorError(f"{name} is malformed") from exc
    if str(value) != token:
        raise SupervisorError(f"{name} is not reduced canonical form")
    return value


def _positive_decimal(token: Any, name: str) -> int:
    if not isinstance(token, str) or POSITIVE_DECIMAL_RE.fullmatch(token) is None:
        raise SupervisorError(f"{name} is not a canonical positive decimal string")
    return int(token, 10)


def _validate_candidate(
    candidate: Any,
    *,
    payload: Mapping[str, Any],
    lane: Mapping[str, Any],
) -> tuple[int, int, int, int]:
    if not isinstance(candidate, dict):
        raise SupervisorError("candidate must be an object")
    _require_keys(
        candidate,
        {
            "source_p", "source_q", "source_u_numerator", "source_u_denominator",
            "Y", "Z", "v", "rational_quadruple", "integer_quadruple", "h",
            "exact_verification",
        },
        "candidate",
    )
    p = _strict_int(candidate["source_p"], "candidate source_p", 1)
    q = _strict_int(candidate["source_q"], "candidate source_q", 1)
    if math.gcd(p, q) != 1:
        raise SupervisorError("candidate source p/q is not reduced")
    if (p, q) not in {
        (job["p"], job["q"]) for job in lane["specializations"]
    }:
        raise SupervisorError("candidate source p/q is not assigned to this lane")
    numerator_token = candidate["source_u_numerator"]
    if not isinstance(numerator_token, str) or DECIMAL_RE.fullmatch(numerator_token) is None:
        raise SupervisorError("candidate source_u_numerator is not canonical decimal")
    if numerator_token == "-0":
        raise SupervisorError("candidate source_u_numerator must encode zero as 0")
    n = int(numerator_token, 10)
    d = _strict_int(candidate["source_u_denominator"], "source_u_denominator", 1)
    bounds = payload["bounds"]
    if abs(n) > bounds["N"] or d > bounds["D"] or math.gcd(abs(n), d) != 1:
        raise SupervisorError("candidate u is outside or not reduced in the declared box")
    if abs(n) * q >= p * d:
        raise SupervisorError("candidate does not satisfy |u|<t")
    if payload["search_mode"] == "canonical_positive_u_positive_y" and n <= 0:
        raise SupervisorError("canonical candidate must have positive u")

    t = Fraction(p, q)
    u = Fraction(n, d)
    Y = _rational(candidate["Y"], "candidate Y")
    Z = _rational(candidate["Z"], "candidate Z")
    v = _rational(candidate["v"], "candidate v")
    if payload["search_mode"] == "canonical_positive_u_positive_y" and Y <= 0:
        raise SupervisorError("canonical candidate must have positive Y")
    if v < 0:
        raise SupervisorError("candidate v must be the nonnegative root")
    T = t + 1
    L = t**5 + 10 * t**3 * u**2 + 5 * t * u**4
    if Y**2 != 80 * T**6 + 20 * T * L:
        raise SupervisorError("candidate Y does not satisfy the torsor quartic")
    if Z != (Y - 10 * T**3) / (10 * T):
        raise SupervisorError("candidate Z reconstruction mismatch")
    if Z < 0 or Z >= T**2 or v**2 != Z:
        raise SupervisorError("candidate Z/v square or positivity gate mismatch")
    if payload["search_mode"] == "canonical_positive_u_positive_y" and Z <= 0:
        raise SupervisorError("canonical candidate must have positive Z")

    raw_rational = candidate["rational_quadruple"]
    if not isinstance(raw_rational, list) or len(raw_rational) != 4:
        raise SupervisorError("candidate rational_quadruple must have four entries")
    rational_values = tuple(
        _rational(token, f"candidate rational_quadruple[{index}]")
        for index, token in enumerate(raw_rational)
    )
    expected_rational = (
        (t - u) / 2,
        (t + u) / 2,
        (T - v) / 2,
        (T + v) / 2,
    )
    if rational_values != expected_rational:
        raise SupervisorError("candidate rational quadruple reconstruction mismatch")
    if any(value <= 0 for value in rational_values):
        raise SupervisorError("candidate rational quadruple is not positive")
    if (rational_values[0] ** 5 + rational_values[1] ** 5 !=
            rational_values[2] ** 5 + rational_values[3] ** 5):
        raise SupervisorError("candidate rational fifth-power equality mismatch")

    raw = candidate["integer_quadruple"]
    if not isinstance(raw, list) or len(raw) != 4:
        raise SupervisorError("candidate integer_quadruple must have four entries")
    values: list[int] = []
    for index, token in enumerate(raw):
        values.append(_positive_decimal(token, f"candidate integer_quadruple[{index}]"))
    common_denominator = math.lcm(*(value.denominator for value in rational_values))
    cleared = [
        value.numerator * (common_denominator // value.denominator)
        for value in rational_values
    ]
    common_gcd = 0
    for value in cleared:
        common_gcd = math.gcd(common_gcd, abs(value))
    primitive = tuple(value // common_gcd for value in cleared)
    if tuple(values) != primitive:
        raise SupervisorError("candidate integer quadruple is not the primitive clearing")
    a, b, c, d_value = values
    h = _positive_decimal(candidate["h"], "candidate h")
    if h != (c + d_value) - (a + b) or h % 30 != 0:
        raise SupervisorError("candidate h reconstruction or h mod 30 gate mismatch")
    if a**5 + b**5 != c**5 + d_value**5:
        raise SupervisorError("candidate integer fifth-power equality mismatch")
    if set((a, b)).intersection((c, d_value)):
        raise SupervisorError("candidate integer representations are not cross-disjoint")
    if candidate["exact_verification"] is not True:
        raise SupervisorError("candidate exact_verification must be true")
    return tuple(values)  # type: ignore[return-value]


def _run_verifier(command: Sequence[str], timeout_seconds: float = 60.0) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            list(command),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout_seconds,
            creationflags=CREATE_NO_WINDOW,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SupervisorError(f"verifier execution failed: {exc}") from exc
    if completed.returncode != 0:
        raise SupervisorError(f"verifier returned {completed.returncode}")
    if completed.stderr:
        raise SupervisorError("verifier emitted stderr")
    try:
        report = json.loads(completed.stdout.decode("ascii"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise SupervisorError(f"verifier emitted malformed JSON: {exc}") from exc
    if not isinstance(report, dict) or report.get("valid") is not True:
        raise SupervisorError("verifier did not report valid=true")
    return report


def dual_verify_candidate(
    values: tuple[int, int, int, int],
    artifacts: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Run the two existing independent exact verifiers."""

    decimal = [str(value) for value in values]
    scalar_command = [
        artifacts["python_interpreter"]["path"],
        artifacts["scalar_verifier"]["path"],
        "--quadruple",
        *decimal,
    ]
    native_command = [artifacts["independent_verifier"]["path"], *decimal]
    with locked_artifacts(artifacts):
        scalar = _run_verifier(scalar_command)
        validate_all_artifact_identity(artifacts)
        native = _run_verifier(native_command)
    certificate = scalar.get("certificate")
    if certificate != dict(zip(("a", "b", "c", "d"), values)):
        raise SupervisorError("scalar verifier certificate echo mismatch")
    scalar_sum = scalar.get("left_sum")
    native_sum = native.get("left_sum")
    if not isinstance(scalar_sum, int) or native_sum != str(scalar_sum):
        raise SupervisorError("independent verifier sum mismatch")
    return {
        "integer_quadruple": decimal,
        "scalar_report": scalar,
        "independent_report": native,
    }


def validate_lane_result(
    result: Any,
    *,
    payload: Mapping[str, Any],
    payload_digest: str,
    lane: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate identity, completion counts and status invariants."""

    if not isinstance(result, dict):
        raise SupervisorError("lane result must be an object")
    _require_keys(
        result,
        {
            "schema_version", "kind", "campaign_id", "manifest_payload_sha256",
            "lane_file_sha256", "search_mode", "lane_id", "assignment_sha256",
            "status", "signed_u_symmetry_pruned", "negative_y_pruned",
            "zero_u_pruned", "emit_torsor_points", "elapsed_milliseconds",
            "assigned_specializations", "completed_specializations", "counts",
            "zero_z_rejected_as_nontarget", "complete",
            "candidates",
        },
        "lane result",
    )
    if result["schema_version"] != 1 or result["kind"] != RESULT_KIND:
        raise SupervisorError("lane result schema mismatch")
    comparisons = {
        "campaign_id": payload["campaign_id"],
        "manifest_payload_sha256": payload_digest,
        "lane_file_sha256": lane["lane_file"]["sha256"],
        "search_mode": payload["search_mode"],
        "lane_id": lane["lane_id"],
        "assignment_sha256": lane["assignment_sha256"],
    }
    for key, expected in comparisons.items():
        if result[key] != expected:
            raise SupervisorError(f"lane result {key} mismatch")
    status = result["status"]
    if status not in RESULT_STATUSES:
        raise SupervisorError("lane result status is unrecognized")
    assigned = len(lane["specializations"])
    if _strict_int(result["assigned_specializations"], "assigned_specializations", 0) != assigned:
        raise SupervisorError("assigned_specializations mismatch")
    completed = _strict_int(result["completed_specializations"], "completed_specializations", 0)
    if completed > assigned:
        raise SupervisorError("completed_specializations exceeds assignment")
    if not isinstance(result["counts"], dict):
        raise SupervisorError("counts must be an object")
    if set(result["counts"]) != COUNT_KEYS:
        raise SupervisorError("lane result count-key set mismatch")
    count_values: dict[str, int] = {}
    for key in sorted(COUNT_KEYS):
        value = result["counts"][key]
        if not isinstance(value, str) or UNSIGNED_DECIMAL_RE.fullmatch(value) is None:
            raise SupervisorError(f"count {key} is not a canonical unsigned decimal string")
        count_values[key] = int(value, 10)
    elapsed = result["elapsed_milliseconds"]
    if not isinstance(elapsed, str) or UNSIGNED_DECIMAL_RE.fullmatch(elapsed) is None:
        raise SupervisorError("elapsed_milliseconds is not canonical unsigned decimal")
    canonical = payload["search_mode"] == "canonical_positive_u_positive_y"
    expected_flags = {
        "signed_u_symmetry_pruned": canonical,
        "negative_y_pruned": canonical,
        "zero_u_pruned": canonical,
        "emit_torsor_points": False,
    }
    if result["zero_z_rejected_as_nontarget"] is not True:
        raise SupervisorError("worker must reject Z=0 as a nontarget lift")
    for key, expected in expected_flags.items():
        if result[key] is not expected:
            raise SupervisorError(f"lane result {key} mismatch")
    if canonical and count_values["zero_u_tested"] != 0:
        raise SupervisorError("canonical mode must not test u=0")
    candidates = result["candidates"]
    if count_values["reduced_t_values"] != assigned:
        raise SupervisorError("reduced_t_values differs from assigned specializations")
    if not isinstance(candidates, list):
        raise SupervisorError("candidates must be an array")
    if status == "NO_HIT" and (completed != assigned or candidates):
        raise SupervisorError("NO_HIT requires complete assignment and no candidates")
    expected_complete = status == "NO_HIT" and completed == assigned
    if result["complete"] is not expected_complete:
        raise SupervisorError("lane result complete flag mismatch")
    if status == "HIT" and len(candidates) != 1:
        raise SupervisorError("HIT requires exactly one candidate")
    if status in {"TIMEOUT_INCOMPLETE", "FAIL_CLOSED"} and candidates:
        raise SupervisorError(f"{status} must not carry candidates")
    if count_values["verified_integer_certificates"] != len(candidates):
        raise SupervisorError("verified certificate count differs from candidates")
    if count_values["candidate_records"] < len(candidates):
        raise SupervisorError("candidate_records is below verified candidate count")
    if count_values["bounded_z_squares"] < count_values["candidate_records"]:
        raise SupervisorError("bounded_z_squares is below candidate_records")
    if count_values["admissible_specializations"] > count_values["pairs_considered"]:
        raise SupervisorError("admissible_specializations exceeds pairs_considered")
    return result


def _assert_empty_lane_stderr(run_dir: Path, lane_id: int) -> None:
    stderr_path = run_dir / f"lane_{lane_id:02d}.stderr.txt"
    try:
        if not stderr_path.is_file():
            raise SupervisorError(f"lane {lane_id} stderr file is missing")
        if stderr_path.stat().st_size != 0:
            raise SupervisorError(f"lane {lane_id} emitted stderr")
    except OSError as exc:
        raise SupervisorError(f"cannot inspect lane {lane_id} stderr: {exc}") from exc


def _partition_active_snapshot(
    active: Mapping[int, subprocess.Popen[Any]],
) -> tuple[
    dict[int, tuple[subprocess.Popen[Any], int]],
    dict[int, subprocess.Popen[Any]],
]:
    """Take one deterministic poll snapshot without reclassifying its members."""

    terminal: dict[int, tuple[subprocess.Popen[Any], int]] = {}
    live: dict[int, subprocess.Popen[Any]] = {}
    for lane_id in sorted(active):
        process = active[lane_id]
        returncode = process.poll()
        if returncode is None:
            live[lane_id] = process
        else:
            terminal[lane_id] = (process, returncode)
    return terminal, live


def _validate_terminal_snapshot(
    terminal: Mapping[int, tuple[subprocess.Popen[Any], int]],
    *,
    run_dir: Path,
    payload: Mapping[str, Any],
    payload_digest: str,
    lane_by_id: Mapping[int, Mapping[str, Any]],
) -> dict[int, dict[str, Any]]:
    """Fully validate every process terminal in the same poll snapshot."""

    records: dict[int, dict[str, Any]] = {}
    for lane_id in sorted(terminal):
        _, returncode = terminal[lane_id]
        _assert_empty_lane_stderr(run_dir, lane_id)
        lane = lane_by_id[lane_id]
        result = validate_lane_result(
            _load_strict_json(Path(lane["result_path"])),
            payload=payload,
            payload_digest=payload_digest,
            lane=lane,
        )
        validate_semantic_exit(returncode, result["status"], lane_id)
        records[lane_id] = {"returncode": returncode, "result": result}
    return records


def _stop_snapshot_live(
    snapshot_live: Mapping[int, subprocess.Popen[Any]],
    *,
    run_dir: Path,
    lane_by_id: Mapping[int, Mapping[str, Any]],
) -> tuple[int, ...]:
    """Stop only snapshot-live peers and reject any result written while stopping."""

    stopped_lane_ids = tuple(sorted(snapshot_live))
    stop_report = _terminate_owned(snapshot_live)
    if stop_report["survivor_pids"] or stop_report["errors"]:
        raise SupervisorError(f"owned snapshot-live worker stop failed: {stop_report}")
    for lane_id in stopped_lane_ids:
        process = snapshot_live[lane_id]
        if process.poll() is None:
            raise SupervisorError(f"snapshot-live lane {lane_id} survived stop")
        _assert_empty_lane_stderr(run_dir, lane_id)
        if Path(lane_by_id[lane_id]["result_path"]).exists():
            raise SupervisorError(
                f"snapshot-live lane {lane_id} produced a result while being stopped"
            )
    return stopped_lane_ids


def _exact_lane_artifact_ids(
    run_dir: Path, glob_pattern: str, name_pattern: re.Pattern[str], role: str
) -> set[int]:
    lane_ids: set[int] = set()
    for path in run_dir.glob(glob_pattern):
        match = name_pattern.fullmatch(path.name)
        if match is None:
            raise SupervisorError(f"unexpected {role} artifact name: {path.name}")
        lane_id = int(match.group(1), 10)
        if lane_id in lane_ids:
            raise SupervisorError(f"duplicate {role} artifact for lane {lane_id}")
        lane_ids.add(lane_id)
    return lane_ids


def _validate_terminal_run_dir_inventory(
    *,
    run_dir: Path,
    spawned_lane_ids: set[int],
    terminal_records: Mapping[int, Mapping[str, Any]],
    verification_path: Path | None,
    include_summary: bool,
) -> None:
    """Require the exact flat regular-file inventory for a success report."""

    terminal_lane_ids = set(terminal_records)
    if not terminal_lane_ids <= spawned_lane_ids:
        raise SupervisorError("terminal result producers were not all spawned")
    expected = {"launch.lock", "supervisor_state.json"}
    expected.update(
        f"lane_{lane_id:02d}.{suffix}.txt"
        for lane_id in spawned_lane_ids
        for suffix in ("stdout", "stderr")
    )
    expected.update(
        f"lane_{lane_id:02d}.result.json" for lane_id in terminal_lane_ids
    )
    if verification_path is not None:
        try:
            verification_parent = verification_path.parent.resolve()
            run_dir_resolved = run_dir.resolve()
        except OSError as exc:
            raise SupervisorError(
                f"cannot resolve terminal inventory paths: {exc}"
            ) from exc
        match = re.fullmatch(
            r"lane_([0-9]{2})[.]candidate_000[.]verified[.]json",
            verification_path.name,
        )
        if (
            verification_parent != run_dir_resolved
            or match is None
            or int(match.group(1), 10) not in terminal_lane_ids
        ):
            raise SupervisorError(
                "verified-candidate path is not one terminal producer artifact"
            )
        expected.add(verification_path.name)
    if include_summary:
        expected.add("supervisor_summary.json")

    try:
        entries = list(run_dir.iterdir())
    except OSError as exc:
        raise SupervisorError(
            f"cannot inspect terminal run-dir inventory: {exc}"
        ) from exc
    actual = {entry.name for entry in entries}
    if actual != expected:
        raise SupervisorError(
            "terminal run-dir inventory mismatch: "
            f"missing={sorted(expected - actual)}, unexpected={sorted(actual - expected)}"
        )
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    for entry in entries:
        try:
            metadata = entry.lstat()
        except OSError as exc:
            raise SupervisorError(
                f"cannot inspect terminal artifact {entry.name}: {exc}"
            ) from exc
        attributes = getattr(metadata, "st_file_attributes", 0)
        if (
            entry.is_symlink()
            or not stat.S_ISREG(metadata.st_mode)
            or bool(reparse_flag and attributes & reparse_flag)
        ):
            raise SupervisorError(
                f"terminal artifact is not a regular non-reparse file: {entry.name}"
            )


def _validate_verified_hit_producer_inventory(
    *,
    run_dir: Path,
    payload: Mapping[str, Any],
    payload_digest: str,
    lane_by_id: Mapping[int, Mapping[str, Any]],
    state: Mapping[str, Any],
    spawned_lane_ids: set[int],
    terminal_records: Mapping[int, Mapping[str, Any]],
    stopped_live_lane_ids: set[int],
    winner_lane_id: int,
    verified_hit: Mapping[str, Any],
    verification_path: Path,
) -> None:
    """Assert the sole-winner producer state and its exact lane artifact sets."""

    terminal_lane_ids = set(terminal_records)
    if terminal_lane_ids & stopped_live_lane_ids:
        raise SupervisorError("terminal and stopped-live lane sets overlap")
    if terminal_lane_ids | stopped_live_lane_ids != spawned_lane_ids:
        raise SupervisorError("winner reconciliation does not cover every spawned lane")
    hit_lane_ids = {
        lane_id
        for lane_id, record in terminal_records.items()
        if record["result"]["status"] == "HIT"
    }
    if hit_lane_ids != {winner_lane_id}:
        raise SupervisorError("verified producer must have exactly one HIT result")
    winner_result = terminal_records[winner_lane_id]["result"]
    if len(winner_result["candidates"]) != 1:
        raise SupervisorError("verified producer HIT must have exactly one candidate")
    if set(verified_hit) != {
        "integer_quadruple", "scalar_report", "independent_report", "lane_id",
        "candidate_index", "candidate_observed_utc", "verified_utc",
    }:
        raise SupervisorError("verified-hit record key set mismatch")
    if verified_hit["lane_id"] != winner_lane_id or verified_hit["candidate_index"] != 0:
        raise SupervisorError("verified-hit producer must be candidate index zero")

    for lane_id, record in terminal_records.items():
        expected_status = "HIT" if lane_id == winner_lane_id else "NO_HIT"
        if record["result"]["status"] != expected_status:
            raise SupervisorError(
                f"terminal peer lane {lane_id} has non-preservable status"
            )
        current = validate_lane_result(
            _load_strict_json(Path(lane_by_id[lane_id]["result_path"])),
            payload=payload,
            payload_digest=payload_digest,
            lane=lane_by_id[lane_id],
        )
        validate_semantic_exit(record["returncode"], current["status"], lane_id)
        if current != record["result"]:
            raise SupervisorError(f"terminal lane {lane_id} result changed after validation")

    expected_result_ids = terminal_lane_ids
    actual_result_ids = _exact_lane_artifact_ids(
        run_dir, "lane_*.result.json",
        re.compile(r"lane_([0-9]{2})[.]result[.]json\Z"), "result",
    )
    if actual_result_ids != expected_result_ids:
        raise SupervisorError("lane result artifact set does not match terminal producers")
    expected_stream_ids = spawned_lane_ids
    for suffix in ("stdout", "stderr"):
        actual_stream_ids = _exact_lane_artifact_ids(
            run_dir, f"lane_*.{suffix}.txt",
            re.compile(rf"lane_([0-9]{{2}})[.]{suffix}[.]txt\Z"), suffix,
        )
        if actual_stream_ids != expected_stream_ids:
            raise SupervisorError(f"lane {suffix} artifact set does not match spawned lanes")
    for lane_id in spawned_lane_ids:
        _assert_empty_lane_stderr(run_dir, lane_id)

    verified_paths = {
        path.resolve() for path in run_dir.glob("lane_*.candidate_*.verified.json")
    }
    if verified_paths != {verification_path.resolve()}:
        raise SupervisorError("verified-candidate artifact set is not exactly the sole winner")
    if _load_strict_json(verification_path) != verified_hit:
        raise SupervisorError("verified-candidate artifact differs from producer record")

    lane_states = state["lanes"]
    for lane in payload["lanes"]:
        lane_id = lane["lane_id"]
        status = lane_states[str(lane_id)]["status"]
        if not lane["specializations"]:
            expected = "NO_WORK"
        elif lane_id == winner_lane_id:
            expected = "VERIFIED_HIT"
        elif lane_id in stopped_live_lane_ids:
            expected = "STOPPED_AFTER_VERIFIED_HIT"
        else:
            expected = "NO_HIT"
        if status != expected:
            raise SupervisorError(
                f"lane {lane_id} producer status {status} differs from {expected}"
            )



def _state_template(payload: Mapping[str, Any], digest: str) -> dict[str, Any]:
    lanes = {
        str(lane["lane_id"]): {
            "status": "PENDING" if lane["specializations"] else "NO_WORK",
            "pid": None,
            "assigned_specializations": len(lane["specializations"]),
        }
        for lane in payload["lanes"]
    }
    return {
        "schema_version": 1,
        "kind": "Q5_TORSOR_SUPERVISOR_STATE",
        "campaign_id": payload["campaign_id"],
        "manifest_payload_sha256": digest,
        "status": "STARTING",
        "updated_utc": _now_text(),
        "supervisor_pid": os.getpid(),
        "owned_pids": [],
        "spawned_lane_ids": [],
        "lanes": lanes,
        "anomaly": None,
    }


def run_campaign(
    envelope: Mapping[str, Any], *, manifest_path: Path, poll_seconds: float,
    authorization_path: Path,
) -> dict[str, Any]:
    """Sole search-worker launch boundary with every fixed validation in force."""

    if (
        isinstance(poll_seconds, bool)
        or not isinstance(poll_seconds, (int, float))
        or not math.isfinite(float(poll_seconds))
        or not 0.02 <= float(poll_seconds) <= 5.0
    ):
        raise SupervisorError("poll_seconds must be between 0.02 and 5.0")
    poll_seconds = float(poll_seconds)
    if not isinstance(envelope, Mapping):
        raise SupervisorError("campaign envelope must be a mapping")
    digest = envelope.get("payload_sha256")
    payload = envelope.get("payload")
    campaign_id = payload.get("campaign_id") if isinstance(payload, Mapping) else None
    if not isinstance(digest, str) or not isinstance(campaign_id, str):
        raise SupervisorError("campaign envelope identity is malformed")
    try:
        audited = manifest_lib.audit_manifest(
            manifest_path,
            expected_digest=digest,
            expected_campaign_id=campaign_id,
        )
    except manifest_lib.ManifestError as exc:
        raise SupervisorError(f"campaign manifest audit failed: {exc}") from exc
    if audited != envelope:
        raise SupervisorError("supplied envelope differs from the audited manifest")
    validate_runtime_identity(audited["payload"])
    envelope = audited

    def _run_authorized_campaign(
        launch_session: _LaunchAuthorizationReservation,
        aggregate_reservation: _AggregateSupervisorReservation,
    ) -> dict[str, Any]:
        aggregate_reservation.assert_active()
        deadline_guard = launch_session.active_guard(
            envelope=envelope, manifest_path=manifest_path
        )
        launch_readiness_sha256 = deadline_guard.launch_readiness_sha256
        authorization_sha256 = deadline_guard.authorization_sha256
        authorization_expires_utc = deadline_guard.authorization_expires_utc
        if (
            launch_readiness_sha256 is None
            or authorization_sha256 is None
            or authorization_expires_utc is None
        ):
            raise SupervisorError("authorized launch binding is incomplete")
        payload = envelope["payload"]
        digest = envelope["payload_sha256"]
        validate_all_artifact_identity(payload["artifacts"])
        assert_no_unowned_relevant_processes({})
        if payload["mode"] == "SELECTED_MAIN" and payload["oeis_redundancy_gate"]["passes"] is not True:
            raise SupervisorError("OEIS redundancy gate route-kills this finite box")
        if deadline_guard.reached():
            raise SupervisorError("common deadline has already expired")
        run_dir = Path(payload["run_dir"])
        deadline_guard.assert_authorization_current()
        _claim_run_dir(
            run_dir, payload, digest, launch_readiness_sha256,
            authorization_sha256, authorization_expires_utc,
        )
        state_path = run_dir / "supervisor_state.json"
        summary_path = run_dir / "supervisor_summary.json"
        state = _state_template(payload, digest)
        _atomic_state(state_path, state)

        active: dict[int, subprocess.Popen[Any]] = {}
        lane_by_id = {lane["lane_id"]: lane for lane in payload["lanes"]}
        validating_lane_id: int | None = None
        spawned_lane_ids: set[int] = set()
        terminal_records: dict[int, dict[str, Any]] = {}
        stopped_live_lane_ids: set[int] = set()
        spawn_deadline_reached = False
        timed_out = False
        try:
            for lane in payload["lanes"]:
                lane_id = lane["lane_id"]
                if not lane["specializations"]:
                    continue
                if deadline_guard.reached():
                    spawn_deadline_reached = True
                    break
                if len(active) >= manifest_lib.LANE_COUNT:
                    raise SupervisorError("owned worker cap would exceed 64")
                stdout_path = run_dir / f"lane_{lane_id:02d}.stdout.txt"
                stderr_path = run_dir / f"lane_{lane_id:02d}.stderr.txt"
                environment = os.environ.copy()
                environment.update(payload["thread_environment"])
                environment["Q5_MANIFEST_PAYLOAD_SHA256"] = digest
                environment["Q5_LANE_FILE_SHA256"] = lane["lane_file"]["sha256"]
                environment["Q5_DEADLINE_UTC"] = payload["deadline"]
                try:
                    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
                        validate_all_artifact_identity(payload["artifacts"])
                        if deadline_guard.reached():
                            spawn_deadline_reached = True
                            break
                        deadline_guard.assert_authorization_current()
                        # The mutex serializes cooperative supervisors, but an external
                        # process can race the census.  Census on both sides of Popen;
                        # register first so any post-spawn or stream-close failure owns
                        # and terminates the child through the outer fail-closed handler.
                        assert_no_unowned_relevant_processes(active)
                        process = subprocess.Popen(
                            lane["command"],
                            stdin=subprocess.DEVNULL,
                            stdout=stdout,
                            stderr=stderr,
                            env=environment,
                            shell=False,
                            creationflags=CREATE_NO_WINDOW,
                        )
                        active[lane_id] = process
                        spawned_lane_ids.add(lane_id)
                        state["spawned_lane_ids"] = sorted(spawned_lane_ids)
                        assert_no_unowned_relevant_processes(active)
                except OSError as exc:
                    raise SupervisorError(f"failed to spawn lane {lane_id}: {exc}") from exc
                state["lanes"][str(lane_id)].update(status="RUNNING", pid=process.pid)
                state["owned_pids"] = _owned_pids(active)
                state["updated_utc"] = _now_text()
                _atomic_state(state_path, state)


            if len(active) > manifest_lib.LANE_COUNT:
                raise SupervisorError("owned worker cap exceeded after spawn")
            state["status"] = "RUNNING"
            state["owned_pids"] = _owned_pids(active)
            state["updated_utc"] = _now_text()
            _atomic_state(state_path, state)

            verified_hit: dict[str, Any] | None = None
            verification_path: Path | None = None
            while active or spawn_deadline_reached:
                assert_no_unowned_relevant_processes(active)
                terminal_snapshot, snapshot_live = _partition_active_snapshot(active)
                candidate_observed_utc = _now_text()
                deadline_at_snapshot = deadline_guard.reached()
                for lane_id in snapshot_live:
                    _assert_empty_lane_stderr(run_dir, lane_id)
                if terminal_snapshot:
                    validating_lane_id = min(terminal_snapshot)
                terminal_batch = _validate_terminal_snapshot(
                    terminal_snapshot,
                    run_dir=run_dir,
                    payload=payload,
                    payload_digest=digest,
                    lane_by_id=lane_by_id,
                )
                statuses = {
                    lane_id: record["result"]["status"]
                    for lane_id, record in terminal_batch.items()
                }
                invalid_terminal = {
                    lane_id: status
                    for lane_id, status in statuses.items()
                    if status not in {"NO_HIT", "HIT"}
                }
                if invalid_terminal:
                    raise SupervisorError(
                        "terminal snapshot contains non-final-search status: "
                        f"{invalid_terminal}"
                    )
                hit_lane_ids = sorted(
                    lane_id for lane_id, status in statuses.items() if status == "HIT"
                )
                if len(hit_lane_ids) > 1:
                    raise SupervisorError(
                        f"terminal snapshot contains multiple HIT producers: {hit_lane_ids}"
                    )

                for lane_id, record in terminal_batch.items():
                    del active[lane_id]
                    terminal_records[lane_id] = record
                    state["lanes"][str(lane_id)].update(
                        status=(
                            "EXITED_PENDING_VALIDATION"
                            if record["result"]["status"] == "HIT"
                            else "NO_HIT"
                        ),
                        pid=None,
                    )
                if set(active) != set(snapshot_live):
                    raise SupervisorError(
                        "active process set changed after fixed poll snapshot"
                    )
                state["owned_pids"] = _owned_pids(active)
                if terminal_batch:
                    state["updated_utc"] = _now_text()
                    _atomic_state(state_path, state)

                if hit_lane_ids:
                    winner_lane_id = hit_lane_ids[0]
                    validating_lane_id = winner_lane_id
                    if deadline_at_snapshot or spawn_deadline_reached:
                        raise SupervisorError(
                            "HIT producer was first observed at or after the search deadline"
                        )
                    stopped = _stop_snapshot_live(
                        snapshot_live, run_dir=run_dir, lane_by_id=lane_by_id
                    )
                    stopped_live_lane_ids.update(stopped)
                    for lane_id in stopped:
                        state["lanes"][str(lane_id)].update(
                            status="STOPPED_AFTER_CANDIDATE", pid=None
                        )
                    active.clear()
                    state["owned_pids"] = []
                    state["updated_utc"] = _now_text()
                    _atomic_state(state_path, state)

                    winner_lane = lane_by_id[winner_lane_id]
                    winner_result = terminal_batch[winner_lane_id]["result"]
                    if len(winner_result["candidates"]) != 1:
                        raise SupervisorError(
                            "winner HIT must contain exactly one candidate"
                        )
                    values = _validate_candidate(
                        winner_result["candidates"][0],
                        payload=payload,
                        lane=winner_lane,
                    )
                    verification = dual_verify_candidate(
                        values, payload["artifacts"]
                    )
                    if deadline_guard.hard_reached():
                        raise SupervisorError(
                            "hard deadline G reached during candidate verification"
                        )
                    verification.update(
                        lane_id=winner_lane_id,
                        candidate_index=0,
                        candidate_observed_utc=candidate_observed_utc,
                        verified_utc=_now_text(),
                    )
                    verification_path = run_dir / (
                        f"lane_{winner_lane_id:02d}.candidate_000.verified.json"
                    )
                    if verification_path.exists():
                        raise SupervisorError(
                            "verified-candidate artifact already exists"
                        )
                    _atomic_state(verification_path, verification)
                    verified_hit = verification
                    for lane_id in stopped:
                        state["lanes"][str(lane_id)].update(
                            status="STOPPED_AFTER_VERIFIED_HIT", pid=None
                        )
                    state["lanes"][str(winner_lane_id)].update(
                        status="VERIFIED_HIT", pid=None
                    )
                    _validate_verified_hit_producer_inventory(
                        run_dir=run_dir,
                        payload=payload,
                        payload_digest=digest,
                        lane_by_id=lane_by_id,
                        state=state,
                        spawned_lane_ids=spawned_lane_ids,
                        terminal_records=terminal_records,
                        stopped_live_lane_ids=stopped_live_lane_ids,
                        winner_lane_id=winner_lane_id,
                        verified_hit=verified_hit,
                        verification_path=verification_path,
                    )
                    state["updated_utc"] = _now_text()
                    _atomic_state(state_path, state)
                    validating_lane_id = None
                    break

                validating_lane_id = None
                if spawn_deadline_reached or deadline_at_snapshot:
                    stopped = _stop_snapshot_live(
                        snapshot_live, run_dir=run_dir, lane_by_id=lane_by_id
                    )
                    for lane_id in stopped:
                        state["lanes"][str(lane_id)].update(
                            status="TIMEOUT_INCOMPLETE", pid=None
                        )
                    active.clear()
                    pending_lane_ids = {
                        lane["lane_id"]
                        for lane in payload["lanes"]
                        if lane["specializations"]
                        and state["lanes"][str(lane["lane_id"])]["status"] == "PENDING"
                    }
                    for lane_id in pending_lane_ids:
                        state["lanes"][str(lane_id)].update(
                            status="TIMEOUT_INCOMPLETE", pid=None
                        )
                    incomplete_lane_ids = set(stopped) | pending_lane_ids
                    if not incomplete_lane_ids:
                        raise SupervisorError(
                            "search deadline reached after all lanes were terminal; "
                            "TIMEOUT_INCOMPLETE would have zero incomplete lanes"
                        )
                    timed_out = True
                    state["owned_pids"] = []
                    state["updated_utc"] = _now_text()
                    _atomic_state(state_path, state)
                    break
                if active:
                    if deadline_guard.reached():
                        continue
                    time.sleep(poll_seconds)

            if verified_hit is None and not timed_out and deadline_guard.reached():
                raise SupervisorError(
                    "search deadline reached before a FINITE_NO_HIT terminal summary"
                )
            if verified_hit is not None:
                final_status = "VERIFIED_HIT"
            elif timed_out:
                final_status = "TIMEOUT_INCOMPLETE"
            else:
                final_status = "FINITE_NO_HIT"
            nonempty_statuses = {
                lane["lane_id"]: state["lanes"][str(lane["lane_id"])]["status"]
                for lane in payload["lanes"]
                if lane["specializations"]
            }
            if final_status == "FINITE_NO_HIT" and any(
                status != "NO_HIT" for status in nonempty_statuses.values()
            ):
                raise SupervisorError(
                    "FINITE_NO_HIT requires every nonempty lane to be NO_HIT"
                )
            if final_status == "TIMEOUT_INCOMPLETE":
                if "TIMEOUT_INCOMPLETE" not in nonempty_statuses.values():
                    raise SupervisorError(
                        "TIMEOUT_INCOMPLETE requires at least one incomplete lane"
                    )
                if any(
                    status not in {"NO_HIT", "TIMEOUT_INCOMPLETE"}
                    for status in nonempty_statuses.values()
                ):
                    raise SupervisorError("timeout summary has an invalid lane status")
            if final_status == "FINITE_NO_HIT" and deadline_guard.reached():
                raise SupervisorError("search deadline reached before finite summary write")
            if deadline_guard.hard_reached():
                raise SupervisorError("hard deadline G reached before supervisor summary")
            assert_no_unowned_relevant_processes(active)
            _validate_terminal_run_dir_inventory(
                run_dir=run_dir,
                spawned_lane_ids=spawned_lane_ids,
                terminal_records=terminal_records,
                verification_path=verification_path,
                include_summary=False,
            )
            summary = {
                "schema_version": 1,
                "kind": "Q5_TORSOR_SUPERVISOR_SUMMARY",
                "campaign_id": payload["campaign_id"],
                "manifest_path": str(manifest_path.resolve()),
                "manifest_payload_sha256": digest,
                "status": final_status,
                "finished_utc": _now_text(),
                "owned_pids": [],
                "spawned_lane_ids": sorted(spawned_lane_ids),
                "verified_hit": verified_hit,
                "lane_statuses": {
                    lane_id: lane_state["status"]
                    for lane_id, lane_state in state["lanes"].items()
                },
            }
            _atomic_state(summary_path, summary)
            if deadline_guard.hard_reached():
                raise SupervisorError("hard deadline G reached during terminal summary write")
            if final_status == "FINITE_NO_HIT" and deadline_guard.reached():
                raise SupervisorError(
                    "search deadline reached during finite terminal summary write"
                )
            state["status"] = final_status
            state["owned_pids"] = []
            state["updated_utc"] = _now_text()
            _atomic_state(state_path, state)
            if deadline_guard.hard_reached():
                raise SupervisorError("hard deadline G reached during final state write")
            if final_status == "FINITE_NO_HIT" and deadline_guard.reached():
                raise SupervisorError(
                    "search deadline reached during finite final state write"
                )
            _validate_terminal_run_dir_inventory(
                run_dir=run_dir,
                spawned_lane_ids=spawned_lane_ids,
                terminal_records=terminal_records,
                verification_path=verification_path,
                include_summary=True,
            )
            return summary
        except BaseException as exc:
            stop_report = _terminate_owned(active)
            survivors = stop_report["survivor_pids"]
            if validating_lane_id is not None:
                state["lanes"][str(validating_lane_id)].update(
                    status="VALIDATION_FAILED", pid=None
                )
            for lane_id, process in active.items():
                if process.poll() is None:
                    state["lanes"][str(lane_id)].update(
                        status="STOP_FAILED", pid=process.pid
                    )
                else:
                    state["lanes"][str(lane_id)].update(
                        status="STOPPED_FAIL_CLOSED", pid=None
                    )
            state["status"] = "FAIL_CLOSED"
            for lane_state in state["lanes"].values():
                if lane_state["status"] == "STOPPED_AFTER_CANDIDATE":
                    lane_state.update(status="STOPPED_FAIL_CLOSED", pid=None)
            state["owned_pids"] = survivors
            state["anomaly"] = f"{type(exc).__name__}: {exc}"
            if survivors or stop_report["errors"]:
                state["anomaly"] += f"; owned worker cleanup failed: {stop_report}"
            state["updated_utc"] = _now_text()
            _atomic_state(state_path, state)
            summary = {
                "schema_version": 1,
                "kind": "Q5_TORSOR_SUPERVISOR_SUMMARY",
                "campaign_id": payload["campaign_id"],
                "manifest_path": str(manifest_path.resolve()),
                "manifest_payload_sha256": digest,
                "status": "FAIL_CLOSED",
                "finished_utc": _now_text(),
                "owned_pids": survivors,
                "spawned_lane_ids": sorted(spawned_lane_ids),
                "verified_hit": None,
                "anomaly": state["anomaly"],
                "lane_statuses": {
                    lane_id: lane_state["status"]
                    for lane_id, lane_state in state["lanes"].items()
                },
            }
            _atomic_state(summary_path, summary)
            if isinstance(exc, (KeyboardInterrupt, SystemExit)):
                raise
            raise SupervisorError(str(exc)) from exc



    with aggregate_supervisor_reservation() as aggregate:
        with _LaunchAuthorizationReservation(
            authorization_path=authorization_path,
            manifest_path=manifest_path,
            envelope=envelope,
        ) as session:
            return _run_authorized_campaign(session, aggregate)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--expected-digest", required=True)
    parser.add_argument("--expected-campaign-id", required=True)
    parser.add_argument("--expected-mode", choices=manifest_lib.MODES, required=True)
    parser.add_argument(
        "--expected-search-mode", choices=manifest_lib.SEARCH_MODES, required=True
    )
    parser.add_argument("--launch", action="store_true")
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--poll-ms", type=int, default=200)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if not (20 <= args.poll_ms <= 5000):
            raise SupervisorError("poll-ms must be between 20 and 5000")
        envelope = manifest_lib.audit_manifest(
            args.manifest,
            expected_digest=args.expected_digest,
            expected_campaign_id=args.expected_campaign_id,
        )
        payload = envelope["payload"]
        validate_runtime_identity(payload)
        if payload["mode"] != args.expected_mode:
            raise SupervisorError("campaign mode differs from expected mode")
        if payload["search_mode"] != args.expected_search_mode:
            raise SupervisorError("search mode differs from expected mode")
        if not args.launch:
            report = {
                "ok": True,
                "status": "AUDIT_ONLY",
                "campaign_id": payload["campaign_id"],
                "manifest_payload_sha256": envelope["payload_sha256"],
                "oeis_redundancy_gate": payload["oeis_redundancy_gate"],
            }
        else:
            if args.authorization is None:
                raise SupervisorError("--launch requires fixed --authorization")
            report = run_campaign(
                envelope, manifest_path=args.manifest,
                poll_seconds=args.poll_ms / 1000.0,
                authorization_path=args.authorization,
            )
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
        return 0
    except (manifest_lib.ManifestError, SupervisorError) as exc:
        print(
            json.dumps(
                {"ok": False, "status": "FAIL_CLOSED", "error": str(exc)},
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
