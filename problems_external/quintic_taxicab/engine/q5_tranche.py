#!/usr/bin/env python3
"""Fail-closed, no-launch controller for the post-primary Q5 tranche.

The controller has seven commands: ``start``, ``authorize``, ``accept-pilot``,
``accept-main``, ``preview``, ``finalize`` and ``audit``.  It never creates a subprocess and it
never mutates a process.  The existing manifest builder and supervisor remain
the only programs which may prepare or execute a campaign.

All paths are fixed.  ``start`` takes a permanent engine-global lock, records
one immutable eight-hour clock, and refuses to continue unless the preceding
magic-square campaign has a strict terminal certificate and two clean psutil
censuses at least ten seconds apart.  Every state replacement is preceded by
a write-once transition intent; an intent not matched by the current state is
an unrecoverable fail-closed condition.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import stat
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import q5_manifest as manifest_lib
import q5_public_status as public_status_lib
import q5_supervisor as supervisor_lib


SCHEMA_VERSION = 1
TRANCHE_ID = "q5-eight-hour-tranche-v1"
ENGINE_DIR = Path(__file__).resolve().parent
TRANCHE_DIR = ENGINE_DIR / "logs" / TRANCHE_ID
LOCK_PATH = ENGINE_DIR / "q5_tranche.lock"
PLAN_PATH = TRANCHE_DIR / "plan.json"
STATE_PATH = TRANCHE_DIR / "state.json"
INTENTS_DIR = TRANCHE_DIR / "intents"
SELECTION_REPORT_PATH = TRANCHE_DIR / "selection_report.json"
MAIN_TERMINAL_REPORT_PATH = TRANCHE_DIR / "main_terminal_report.json"
PUBLIC_STATUS_PATH = TRANCHE_DIR / "public_status_gate.json"
READINESS_PATH = ENGINE_DIR / "Q5_LAUNCH_READY.json"
STATUS_COLLECTOR_PATH = ENGINE_DIR / "q5_public_status.py"
MANIFEST_TRANSACTION_PATH = ENGINE_DIR / "q5_manifest_transaction.py"
AUTHORIZATIONS_DIR = TRANCHE_DIR / "authorizations"

MAGIC_ENGINE_DIR = ENGINE_DIR.parent.parent / "magic_square_squares" / "engine"
MAGIC_SOURCE_RUN_DIR = (
    MAGIC_ENGINE_DIR / "logs" / "tranche64-frozen-manifest-v1"
)
MAGIC_RUN_DIR = (
    MAGIC_ENGINE_DIR / "logs" / "tranche64-frozen-manifest-v1-recovery-v1"
)
MAGIC_STATE_PATH = MAGIC_RUN_DIR / "recovery_state.json"
MAGIC_SUMMARY_PATH = MAGIC_RUN_DIR / "recovery_summary.json"
MAGIC_INVENTORY_PATH = MAGIC_RUN_DIR / "original_artifact_inventory.json"
MAGIC_RUN_ONCE_PATH = MAGIC_RUN_DIR / "RUN_ONCE_RECOVERY.json"
APPROACH_REGISTRY_PATH = ENGINE_DIR.parent / "APPROACH_REGISTRY.md"

CANDIDATE_TABLE_PATH = ENGINE_DIR / "q5_candidate_table.json"
CANDIDATE_TABLE_SOURCE_PATH = ENGINE_DIR / "q5_candidate_table.cpp"
CANDIDATE_TABLE_TOOL_PATH = ENGINE_DIR / "q5_candidate_table.exe"
CANDIDATE_TABLE_PAYLOAD_SHA256 = (
    "f3defaf9d3aa173c800e82d8ab62f24048cafc8d6e8fb16b5ce00106a9791cf8"
)

MAGIC_RUN_ID = "tranche64-frozen-manifest-v1-recovery-v1"
MAGIC_SOURCE_RUN_ID = "tranche64-frozen-manifest-v1"
MAGIC_MANIFEST_SHA256 = (
    "917f8f14729df6d52d34796253589b22be88fdc993e8bbb5898cc5fe59888c21"
)
MAGIC_APPROVED_ARTIFACT_HASHES = {
    "gaussian_center.exe": "0fb9884c814c0d790c2e01701d674fef47b681f9eb16b7dee58c5e58fbb6acb8",
    "recovery_supervisor.py": "163bead12e982944b54228fb04774ff80d6f5a203666043752c38db87a570158",
    "s_lane_search.exe": "092ae87d563569ae2cb2f7c8e64c70de4582d4085c5428f4f0d73008d46c3996",
    "test_gaussian_atomic_stress.exe": "2130d532f234bcc77d702beb40a99060a8f0b48f5eeba382a49a556fcdb6e806",
    "verify_independent.exe": "dcb3019916cb759ddb4654517bab67ef5aa8d70775de0b60c60bb609cf833589",
    "verify_scalar.py": "f4ce16b8ea0e8329a4ce96518574fdd6936414e1a72b1a09fa91f0c5404fa382",
}

EXPECTED_FILE_HASHES: dict[Path, str] = {
    ENGINE_DIR / "q5_manifest.py": "712c6422281da41a471a29a272aa92c35efc9182759a632bfe1d1987ac3ccf1b",
    ENGINE_DIR / "scan_torsor_exact.cpp": "3e96532361aa2768cd36deb093376a9a8ef658cbd5afaca2301ca3ecd461c5c9",
    ENGINE_DIR / "scan_torsor_exact.exe": "19997a0ed9658aea134aef94fd14486e0c8196909f39d5b71d0bb6b2a24689b9",
    ENGINE_DIR / "verify_certificate.py": "843f13506611d51f1d944b9a63778f9bd793dd06b4693838d4ca1a957b00833a",
    ENGINE_DIR / "verify_independent.cpp": "3641129248f507c5f844519f6894fa8aef4c22a4b1d8fe89375d50baa02cf74d",
    ENGINE_DIR / "verify_independent.exe": "055206b62c0d07d2f896e15657749346ef3f5e8f6e6262959198109e4d9fb8f0",
    CANDIDATE_TABLE_SOURCE_PATH: "78928e3074a0c50754990fab6d73c72cddd63b9eb79936902326fed38fab766d",
    CANDIDATE_TABLE_TOOL_PATH: "e4b062dd5273e4510c359f55a39565efc9fa8e0b19ad2818a5228ce87a663a6c",
    CANDIDATE_TABLE_PATH: "c9cb415199bcb60513c8b41b15c866073f806c9dc7116320471fe7c38e3dac0a",
}

MANIFEST_ARTIFACT_PATHS: dict[str, Path] = {
    "worker": ENGINE_DIR / "scan_torsor_exact.exe",
    "worker_source": ENGINE_DIR / "scan_torsor_exact.cpp",
    "scalar_verifier": ENGINE_DIR / "verify_certificate.py",
    "independent_verifier": ENGINE_DIR / "verify_independent.exe",
    "manifest_tool": ENGINE_DIR / "q5_manifest.py",
    "supervisor": ENGINE_DIR / "q5_supervisor.py",
    "python_interpreter": Path(sys.executable).resolve(),
}

# These additional artifacts are not asserted against historical digests, but
# their hashes must be identical in both pre-lock snapshots, the post-lock
# snapshot, and every later state transition.
STABILITY_ONLY_PATHS = {
    Path(__file__).resolve(),
    Path(sys.executable).resolve(),
    ENGINE_DIR / "q5_supervisor.py",
    MANIFEST_TRANSACTION_PATH,
    STATUS_COLLECTOR_PATH,
    ENGINE_DIR / "run_q5_supervisor_hidden.ps1",
    MAGIC_ENGINE_DIR / "recovery_supervisor.py",
    MAGIC_ENGINE_DIR / "tranche_supervisor.py",
    APPROACH_REGISTRY_PATH,
    MAGIC_ENGINE_DIR / "elliptic_integral_search.exe",
    MAGIC_ENGINE_DIR / "gaussian_center.exe",
    MAGIC_ENGINE_DIR / "s_lane_search.exe",
}

PROCESS_ROOTS = (MAGIC_ENGINE_DIR.resolve(), ENGINE_DIR.resolve())
PROCESS_SUFFIXES = {".exe", ".py", ".ps1"}
PROCESS_EXEMPT_PATHS = {Path(__file__).resolve()}

READINESS_ARTIFACT_PATHS = {
    "q5_tranche.py": Path(__file__).resolve(),
    "q5_supervisor.py": ENGINE_DIR / "q5_supervisor.py",
    "q5_manifest.py": ENGINE_DIR / "q5_manifest.py",
    "q5_manifest_transaction.py": MANIFEST_TRANSACTION_PATH,
    "q5_public_status.py": STATUS_COLLECTOR_PATH,
    "run_q5_supervisor_hidden.ps1": ENGINE_DIR / "run_q5_supervisor_hidden.ps1",
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
READINESS_TEST_COMMANDS = (
    "python -m unittest -v " + " ".join(
        f"problems_external.quintic_taxicab.engine.{Path(name).stem}"
        for name in READINESS_TEST_FILES
    ),
)

SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
PHASES = {
    "READY_A", "READY_B", "READY_C", "READY_D", "READY_SELECTION",
    "MAIN_FROZEN", "MAIN_FINITE_NO_HIT", "MAIN_TIMEOUT_INCOMPLETE", "NO_MAIN", "VERIFIED_HIT", "FAIL_CLOSED",
}
TERMINAL_PHASES = {"MAIN_FINITE_NO_HIT", "MAIN_TIMEOUT_INCOMPLETE", "NO_MAIN", "VERIFIED_HIT", "FAIL_CLOSED"}

PILOT_ORDER = ("A", "B", "C", "D")
PILOT_SPECS: dict[str, dict[str, Any]] = {
    "A": {
        "bounds": {"P": 10, "Q": 10, "N": 10, "D": 10},
        "search_mode": "audit_signed_u_both_y",
        "limit_seconds": 120,
        "expected_no_work": 1,
    },
    "B": {
        "bounds": {"P": 47, "Q": 47, "N": 47, "D": 47},
        "search_mode": "canonical_positive_u_positive_y",
        "limit_seconds": 120,
        "expected_no_work": 0,
    },
    "C": {
        "bounds": {"P": 256, "Q": 256, "N": 128, "D": 128},
        "search_mode": "canonical_positive_u_positive_y",
        "limit_seconds": 600,
        "expected_no_work": 0,
    },
    "D": {
        "bounds": {"P": 512, "Q": 512, "N": 192, "D": 192},
        "search_mode": "canonical_positive_u_positive_y",
        "limit_seconds": 1800,
        "expected_no_work": 0,
    },
}
for _pilot_name, _pilot_spec in PILOT_SPECS.items():
    _base = TRANCHE_DIR / f"pilot_{_pilot_name}"
    _pilot_spec.update(
        campaign_id=f"q5-tranche-v1-pilot-{_pilot_name}",
        base_dir=_base,
        manifest_path=_base / "manifest.json",
        lane_config_dir=_base / "lanes",
        run_dir=_base / "run",
    )

MAIN_BASE_DIR = TRANCHE_DIR / "main"
MAIN_MANIFEST_PATH = MAIN_BASE_DIR / "manifest.json"
MAIN_LANE_CONFIG_DIR = MAIN_BASE_DIR / "lanes"
MAIN_RUN_DIR = MAIN_BASE_DIR / "run"
MAIN_CAMPAIGN_ID = "q5-tranche-v1-main"

PUBLIC_SOURCE_EXPECTATIONS = (
    {
        "role": "asiryan_arxiv",
        "url": "https://arxiv.org/abs/2512.11072",
        "observed_status": "OPEN",
    },
    {
        "role": "oeis_a046881",
        "url": "https://oeis.org/A046881",
        "observed_status": "NO_N5_VALUE",
    },
    {
        "role": "formal_conjectures_taxicab",
        "url": (
            "https://github.com/google-deepmind/formal-conjectures/blob/"
            "b8b5208aa5d01f5f91c49ca516bf09cae8d93693/"
            "FormalConjectures/Wikipedia/Taxicab.lean"
        ),
        "observed_status": "RESEARCH_OPEN_ANSWER_SORRY",
    },
)


class TrancheError(RuntimeError):
    """A tranche contract was violated."""


class TrancheNotReady(TrancheError):
    """A required terminal artifact has not been committed yet."""


class PermanentFailure(TrancheError):
    """The permanent lock or intent ledger makes continuation impossible."""


Clock = Callable[[], datetime]
Sleeper = Callable[[float], None]
CensusHook = Callable[[], Mapping[str, Any]]


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def _boot_time_microseconds() -> int:
    try:
        import psutil  # type: ignore[import-not-found]
    except ImportError as exc:
        raise TrancheError("psutil is required for the tranche boot identity") from exc
    try:
        return int(psutil.boot_time() * 1_000_000)
    except (OSError, ValueError, OverflowError) as exc:
        raise TrancheError(f"cannot obtain the system boot identity: {exc}") from exc



def _aware_utc(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise TrancheError(f"{name} must be a timezone-aware datetime")
    return value.astimezone(timezone.utc)


def _utc_text(value: datetime) -> str:
    return _aware_utc(value, "timestamp").isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _parse_time(value: Any, name: str) -> datetime:
    if not isinstance(value, str):
        raise TrancheError(f"{name} must be an ISO-8601 string")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TrancheError(f"{name} is not valid ISO-8601") from exc
    return _aware_utc(result, name)


def _strict_int(value: Any, name: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TrancheError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise TrancheError(f"{name} must be at least {minimum}")
    return value


def _require_keys(value: Any, expected: set[str], name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise TrancheError(f"{name} must be an object")
    if set(value) != expected:
        raise TrancheError(
            f"{name} keys differ: missing={sorted(expected-set(value))}, "
            f"extra={sorted(set(value)-expected)}"
        )
    return value


def _load_json_with_sha(
    path: Path, *, missing_ready: bool = False
) -> tuple[Any, str]:
    try:
        data = path.read_bytes()
        value = json.loads(data.decode("ascii"))
    except FileNotFoundError as exc:
        if missing_ready:
            raise TrancheNotReady(f"required artifact is not present: {path}") from exc
        raise TrancheError(f"required artifact is not present: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TrancheError(f"cannot read strict JSON {path}: {exc}") from exc
    return value, hashlib.sha256(data).hexdigest()


def _load_json(path: Path, *, missing_ready: bool = False) -> Any:
    return _load_json_with_sha(path, missing_ready=missing_ready)[0]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise TrancheError(f"cannot hash {path}: {exc}") from exc
    return digest.hexdigest()


def _canonical_sha(value: Any) -> str:
    return manifest_lib.sha256_bytes(manifest_lib.canonical_bytes(value))


def _pretty_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise TrancheError(f"value cannot be encoded as strict JSON: {exc}") from exc


def _validate_readiness(
    *, expected_sha256: str | None = None, now: datetime | None = None
) -> dict[str, Any]:
    """Validate the external, independently reviewed launch root."""

    raw, file_sha256 = _load_json_with_sha(READINESS_PATH, missing_ready=True)
    value = dict(_require_keys(
        raw,
        {
            "schema_version", "kind", "tranche_id", "created_utc",
            "artifacts", "tests", "referee_verdicts",
        },
        "launch readiness",
    ))
    if (
        value["schema_version"] != 1
        or value["kind"] != "q5-launch-readiness"
        or value["tranche_id"] != TRANCHE_ID
    ):
        raise TrancheError("launch readiness identity mismatch")
    created = _parse_time(value["created_utc"], "launch readiness created_utc")
    observed = _aware_utc(now or _now_utc(), "readiness clock")
    if created > observed:
        raise TrancheError("launch readiness was created in the future")
    if expected_sha256 is not None and file_sha256 != expected_sha256:
        raise PermanentFailure("launch readiness differs from its tranche pin")

    artifacts = value["artifacts"]
    if not isinstance(artifacts, dict) or set(artifacts) != set(READINESS_ARTIFACT_PATHS):
        raise TrancheError("launch readiness artifact role set mismatch")
    normalized_artifacts: dict[str, str] = {}
    for name, expected_path in READINESS_ARTIFACT_PATHS.items():
        digest = artifacts[name]
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            raise TrancheError(f"launch readiness artifact hash is malformed: {name}")
        path = expected_path.resolve()
        if not path.is_file() or _sha256_file(path) != digest:
            raise TrancheError(f"launch readiness artifact drift: {name}")
        normalized_artifacts[name] = digest

    tests = dict(_require_keys(
        value["tests"],
        {"passed", "failed", "commands", "test_files", "suite_sha256"},
        "launch readiness tests",
    ))
    passed = _strict_int(tests["passed"], "launch readiness passed tests", 1)
    failed = _strict_int(tests["failed"], "launch readiness failed tests", 0)
    if failed != 0:
        raise TrancheError("launch readiness records failed tests")
    commands = tests["commands"]
    if commands != list(READINESS_TEST_COMMANDS):
        raise TrancheError("launch readiness test commands differ from the fixed suite")
    test_files = tests["test_files"]
    if not isinstance(test_files, dict) or set(test_files) != set(READINESS_TEST_FILES):
        raise TrancheError("launch readiness test-file set mismatch")
    normalized_test_files: dict[str, str] = {}
    for name in READINESS_TEST_FILES:
        digest = test_files[name]
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            raise TrancheError(f"launch readiness test-file hash is malformed: {name}")
        path = (ENGINE_DIR / name).resolve()
        if not path.is_file() or _sha256_file(path) != digest:
            raise TrancheError(f"launch readiness test-file drift: {name}")
        normalized_test_files[name] = digest
    normalized_tests = {
        "passed": passed,
        "failed": failed,
        "commands": list(commands),
        "test_files": normalized_test_files,
    }
    suite_sha256 = tests["suite_sha256"]
    if suite_sha256 != _canonical_sha(normalized_tests):
        raise TrancheError("launch readiness test-suite hash mismatch")
    normalized_tests["suite_sha256"] = suite_sha256

    reviewed_readiness_sha256 = _canonical_sha({
        "artifacts": normalized_artifacts,
        "tests": normalized_tests,
    })
    verdicts = value["referee_verdicts"]
    if not isinstance(verdicts, list) or len(verdicts) != 2:
        raise TrancheError("launch readiness requires exactly two referee verdicts")
    normalized_verdicts: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw_verdict in verdicts:
        verdict = dict(_require_keys(
            raw_verdict,
            {"referee", "verdict", "reviewed_readiness_sha256"},
            "launch readiness referee verdict",
        ))
        referee = verdict["referee"]
        if not isinstance(referee, str) or not referee.strip() or referee in seen:
            raise TrancheError("launch readiness referee identities are not distinct")
        if verdict["verdict"] != "LAUNCH_SAFE":
            raise TrancheError(f"launch readiness referee {referee} did not return LAUNCH_SAFE")
        if verdict["reviewed_readiness_sha256"] != reviewed_readiness_sha256:
            raise TrancheError(f"launch readiness referee {referee} reviewed another readiness set")
        seen.add(referee)
        normalized_verdicts.append(verdict)

    return {
        **value,
        "artifacts": normalized_artifacts,
        "tests": normalized_tests,
        "referee_verdicts": normalized_verdicts,
        "reviewed_readiness_sha256": reviewed_readiness_sha256,
        "file_sha256": file_sha256,
    }
def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except (OSError, ValueError):
        return False


def _artifact_hashes() -> dict[str, str]:
    paths = set(EXPECTED_FILE_HASHES) | STABILITY_ONLY_PATHS
    result: dict[str, str] = {}
    for raw_path in sorted(paths, key=lambda item: str(item).casefold()):
        path = raw_path.resolve()
        if not path.is_file():
            raise TrancheError(f"frozen artifact is missing: {path}")
        digest = _sha256_file(path)
        expected = EXPECTED_FILE_HASHES.get(raw_path)
        if expected is not None and digest != expected:
            raise TrancheError(f"frozen artifact hash drift: {path}")
        result[str(path)] = digest
    return result


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


def _live_census(clock: Clock = _now_utc) -> dict[str, Any]:
    """Capture relevant live processes and all frozen artifact hashes."""

    try:
        import psutil  # type: ignore[import-not-found]
    except ImportError as exc:
        raise TrancheError("psutil is required for the live process census") from exc

    active: list[dict[str, Any]] = []
    errors: list[str] = []
    own_pid = os.getpid()
    exempt_pids = {own_pid}
    try:
        exempt_pids.update(parent.pid for parent in psutil.Process(own_pid).parents())
    except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
        # The controller itself remains exempt.  Failure to identify its
        # ancestors must not exempt any other process.
        pass
    interpreter_names = {"python.exe", "python3.exe", "python", "pwsh.exe", "powershell.exe"}
    for process in psutil.process_iter(
        ["pid", "ppid", "create_time", "name", "exe", "cmdline", "cwd"]
    ):
        matched: list[str] = []
        try:
            info = process.info
            pid = int(info["pid"])
            if pid in exempt_pids:
                continue
            raw_tokens = list(info.get("cmdline") or [])
            if info.get("exe"):
                raw_tokens.append(str(info["exe"]))
            paths = [
                path for token in raw_tokens
                if (path := _path_token(str(token), info.get("cwd"))) is not None
            ]
            matched = sorted(
                {
                    str(path)
                    for path in paths
                    if path not in PROCESS_EXEMPT_PATHS
                    and path.suffix.casefold() in PROCESS_SUFFIXES
                    and any(_is_within(path, root) for root in PROCESS_ROOTS)
                }
            )
            cwd_path: Path | None = None
            try:
                if info.get("cwd"):
                    cwd_path = Path(str(info["cwd"])).resolve()
            except OSError:
                cwd_path = None
            argv_text = " ".join(str(token) for token in info.get("cmdline") or []).casefold()
            executable_name = Path(str(info.get("exe") or info.get("name") or "")).name.casefold()
            cwd_relevant = (
                cwd_path is not None
                and any(_is_within(cwd_path, root) for root in PROCESS_ROOTS)
            )
            module_or_import_form = any(
                marker in argv_text
                for marker in (
                    "q5_supervisor", "q5_tranche", "q5_manifest",
                    "q5_public_status", "scan_torsor_exact",
                    "quintic_taxicab", "magic_square_squares",
                )
            )
            if (cwd_relevant and executable_name in interpreter_names) or module_or_import_form:
                evidence_path = cwd_path or Path(str(info.get("exe") or "")).resolve()
                matched = sorted(set(matched) | {str(evidence_path)})
            if matched:
                parent_chain: list[dict[str, Any]] = []
                parent = process.parent()
                seen_parents: set[tuple[int, float]] = set()
                while parent is not None:
                    with parent.oneshot():
                        parent_identity = {
                            "pid": parent.pid,
                            "create_time": parent.create_time(),
                            "exe": parent.exe(),
                            "argv": parent.cmdline(),
                            "cwd": parent.cwd(),
                        }
                    key = (parent_identity["pid"], parent_identity["create_time"])
                    if key in seen_parents:
                        raise TrancheError("process parent chain contains a cycle")
                    seen_parents.add(key)
                    parent_chain.append(parent_identity)
                    parent = parent.parent()
                active.append(
                    {
                        "pid": pid,
                        "create_time": info.get("create_time"),
                        "exe": str(info.get("exe") or ""),
                        "argv": list(info.get("cmdline") or []),
                        "cwd": str(info.get("cwd") or ""),
                        "parent_chain": parent_chain,
                        "matched_paths": matched,
                    }
                )
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except (psutil.AccessDenied, OSError) as exc:
            name = ""
            try:
                name = process.name()
            except Exception:
                pass
            if matched or name.casefold() in {
                "elliptic_integral_search.exe", "gaussian_center.exe",
                "s_lane_search.exe", "scan_torsor_exact.exe",
                "python.exe", "python3.exe", "python",
                "pwsh.exe", "powershell.exe",
            }:
                errors.append(f"pid {process.pid} census denied: {type(exc).__name__}")
    active.sort(key=lambda row: (row["pid"], row["create_time"] or 0))
    return {
        "schema_version": 1,
        "kind": "Q5_TRANCHE_PROCESS_CENSUS",
        "captured_utc": _utc_text(clock()),
        "active_processes": active,
        "artifact_hashes": _artifact_hashes(),
        "errors": errors,
    }


def _validate_census(snapshot: Mapping[str, Any], name: str) -> dict[str, Any]:
    value = _require_keys(
        snapshot,
        {"schema_version", "kind", "captured_utc", "active_processes", "artifact_hashes", "errors"},
        name,
    )
    if value["schema_version"] != 1 or value["kind"] != "Q5_TRANCHE_PROCESS_CENSUS":
        raise TrancheError(f"{name} schema mismatch")
    _parse_time(value["captured_utc"], f"{name}.captured_utc")
    if not isinstance(value["active_processes"], list) or value["active_processes"]:
        raise TrancheError(f"{name} found a live magic/Q5 process")
    if not isinstance(value["errors"], list) or value["errors"]:
        raise TrancheError(f"{name} was not complete: {value['errors']}")
    hashes = value["artifact_hashes"]
    if not isinstance(hashes, dict) or not hashes:
        raise TrancheError(f"{name} artifact hashes are missing")
    for path, digest in hashes.items():
        if not isinstance(path, str) or not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            raise TrancheError(f"{name} has a malformed artifact hash")
    return dict(value)


def _current_clean_census(plan: Mapping[str, Any], clock: Clock, hook: CensusHook | None) -> dict[str, Any]:
    raw = hook() if hook is not None else _live_census(clock)
    current = _validate_census(raw, "current census")
    captured = _parse_time(current["captured_utc"], "current census time")
    observed = _aware_utc(clock(), "clock")
    if (
        captured < _parse_time(plan["t0"], "T0")
        or captured > observed
        or observed - captured > timedelta(seconds=5)
    ):
        raise TrancheError("current census is stale or predates T0")
    if current["artifact_hashes"] != plan["frozen_artifact_hashes"]:
        raise TrancheError("frozen artifact hashes drifted after T0")
    return current


def _magic_lane_ids() -> set[str]:
    return {f"{family}{index:02d}" for family in "EGNS" for index in range(1, 17)}


def _has_candidate_signal(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {
                "candidate_count", "verified_candidate_count",
                "candidates_reconstructed", "candidate_records",
                "verified_integer_certificates",
            }:
                if isinstance(item, bool) or not isinstance(item, (int, str)):
                    return True
                try:
                    if int(item) != 0:
                        return True
                except ValueError:
                    return True
            if key == "candidates" and isinstance(item, list) and item:
                return True
            if _has_candidate_signal(item):
                return True
    elif isinstance(value, list):
        return any(_has_candidate_signal(item) for item in value)
    return False

def _inventory(root: Path) -> dict[str, str]:
    """Hash a recursive tree only after rejecting link-type substitutions."""

    root = _plain_directory(root, "inventory root")
    result: dict[str, str] = {}
    pending = [root]
    try:
        while pending:
            directory = pending.pop()
            entries = sorted(
                directory.iterdir(),
                key=lambda path: path.name.casefold(),
                reverse=True,
            )
            for path in entries:
                metadata = path.lstat()
                relative = path.relative_to(root).as_posix()
                if path.is_symlink() or _is_reparse_stat(metadata):
                    raise TrancheError(
                        f"inventory contains a symlink or reparse point: {relative}"
                    )
                if stat.S_ISDIR(metadata.st_mode):
                    pending.append(path)
                elif stat.S_ISREG(metadata.st_mode):
                    result[relative] = _sha256_file(path)
                else:
                    raise TrancheError(
                        f"inventory contains a non-regular entry: {relative}"
                    )
    except TrancheError:
        raise
    except OSError as exc:
        raise TrancheError(f"cannot enumerate inventory: {exc}") from exc
    return dict(sorted(result.items()))


def _is_reparse_stat(value: os.stat_result) -> bool:
    """Return whether an lstat result is a Windows reparse point."""

    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(value, "st_file_attributes", 0) & reparse_flag)


def _plain_directory(path: Path, name: str) -> Path:
    """Resolve a directory only after rejecting links and reparse points."""

    raw = path.absolute()
    try:
        metadata = raw.lstat()
    except OSError as exc:
        raise TrancheError(f"{name} cannot be inspected: {exc}") from exc
    if raw.is_symlink() or _is_reparse_stat(metadata):
        raise TrancheError(f"{name} is a symlink or reparse point")
    if not stat.S_ISDIR(metadata.st_mode):
        raise TrancheError(f"{name} is not a directory")
    return raw.resolve()


def _validate_spawned_lane_ids(
    *,
    summary: Mapping[str, Any],
    final_state: Mapping[str, Any],
    payload: Mapping[str, Any],
    lane_statuses: Mapping[str, Any],
    name: str,
) -> set[int]:
    """Validate the supervisor's exact spawned-lane provenance."""

    raw_summary = summary.get("spawned_lane_ids")
    raw_state = final_state.get("spawned_lane_ids")
    if (
        not isinstance(raw_summary, list)
        or raw_state != raw_summary
        or any(
            isinstance(lane_id, bool)
            or not isinstance(lane_id, int)
            or not (0 <= lane_id < manifest_lib.LANE_COUNT)
            for lane_id in raw_summary
        )
        or raw_summary != sorted(set(raw_summary))
    ):
        raise TrancheError(f"{name} spawned-lane provenance is malformed")
    spawned = set(raw_summary)
    assigned = {
        lane["lane_id"] for lane in payload["lanes"] if lane["specializations"]
    }
    mandatory_spawned = {
        int(lane_id)
        for lane_id, status in lane_statuses.items()
        if status in {
            "NO_HIT", "VERIFIED_HIT", "STOPPED_AFTER_VERIFIED_HIT"
        }
    }
    if not spawned.issubset(assigned) or not mandatory_spawned.issubset(spawned):
        raise TrancheError(f"{name} spawned-lane set contradicts terminal statuses")
    for lane in payload["lanes"]:
        lane_id = lane["lane_id"]
        if lane_id not in spawned and lane_statuses[str(lane_id)] not in {
            "NO_WORK", "TIMEOUT_INCOMPLETE"
        }:
            raise TrancheError(f"{name} unspawned lane has a terminal producer status")
    return spawned


def _validate_exact_run_inventory(
    *,
    run_dir: Path,
    spawned_lane_ids: set[int],
    result_paths: Mapping[int, Path],
    verified_artifact_path: Path | None,
    name: str,
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Require the complete run directory to equal its derived file whitelist."""

    root = _plain_directory(run_dir, f"{name} run directory")
    expected = {
        "launch.lock", "supervisor_state.json", "supervisor_summary.json"
    }
    for lane_id in spawned_lane_ids:
        expected.add(f"lane_{lane_id:02d}.stdout.txt")
        expected.add(f"lane_{lane_id:02d}.stderr.txt")
    for lane_id, raw_path in result_paths.items():
        path = raw_path.resolve()
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError as exc:
            raise TrancheError(f"{name} result path escapes the run directory") from exc
        if relative != f"lane_{lane_id:02d}.result.json":
            raise TrancheError(f"{name} result path is not canonical")
        expected.add(relative)
    if verified_artifact_path is not None:
        try:
            relative = verified_artifact_path.resolve().relative_to(root).as_posix()
        except ValueError as exc:
            raise TrancheError(f"{name} verified path escapes the run directory") from exc
        expected.add(relative)
    inventory: dict[str, str] = {}
    try:
        entries = sorted(root.iterdir(), key=lambda path: path.name)
        for path in entries:
            metadata = path.lstat()
            if path.is_symlink() or _is_reparse_stat(metadata):
                raise TrancheError(
                    f"{name} run inventory contains a symlink or reparse point: "
                    f"{path.name}"
                )
            if stat.S_ISDIR(metadata.st_mode):
                raise TrancheError(
                    f"{name} run directory contains unexpected subdirectories"
                )
            if not stat.S_ISREG(metadata.st_mode):
                raise TrancheError(
                    f"{name} run inventory contains a non-regular entry: {path.name}"
                )
            inventory[path.name] = _sha256_file(path)
    except TrancheError:
        raise
    except OSError as exc:
        raise TrancheError(f"{name} run directory cannot be enumerated: {exc}") from exc
    if set(inventory) != expected:
        raise TrancheError(
            f"{name} run inventory differs: "
            f"missing={sorted(expected-set(inventory))}, "
            f"extra={sorted(set(inventory)-expected)}"
        )
    stdout_sha256: dict[str, str] = {}
    stderr_sha256: dict[str, str] = {}
    for lane_id in sorted(spawned_lane_ids):
        lane_key = str(lane_id)
        stdout_name = f"lane_{lane_id:02d}.stdout.txt"
        stderr_name = f"lane_{lane_id:02d}.stderr.txt"
        stderr_path = root / stderr_name
        if stderr_path.stat().st_size != 0:
            raise TrancheError(f"{name} lane {lane_id} stderr is nonempty")
        stdout_sha256[lane_key] = inventory[stdout_name]
        stderr_sha256[lane_key] = inventory[stderr_name]
    return inventory, stdout_sha256, stderr_sha256


def _scan_magic_raw_candidate_signals(root: Path) -> None:
    for path in sorted(root.rglob("*"), key=lambda item: str(item).casefold()):
        if not path.is_file() or not (
            path.suffix.casefold() in {".json", ".jsonl"}
            or path.name.casefold().endswith(".stdout.txt")
        ):
            continue
        try:
            text = path.read_text(encoding="ascii")
            if not text.strip():
                continue
            if path.suffix.casefold() == ".jsonl":
                records = [json.loads(line) for line in text.splitlines() if line.strip()]
            else:
                records = [json.loads(text)]
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise TrancheError(f"cannot parse raw magic evidence {path}: {exc}") from exc
        if any(_has_candidate_signal(record) for record in records):
            raise TrancheError(f"raw magic evidence contains a candidate signal: {path}")


def _magic_recovery_tree_sha256() -> str:
    return _canonical_sha(_inventory(MAGIC_RUN_DIR))

def _validate_magic_verified_hit(row: Mapping[str, Any]) -> dict[str, Any]:
    """Revalidate the recovery supervisor's exact, source-bound hit gate."""

    lane = row.get("lane")
    if (
        not isinstance(lane, str)
        or lane not in _magic_lane_ids()
        or row.get("status") != "HIT_VERIFIED"
        or row.get("source") != "recovered_interrupted_lane"
    ):
        raise TrancheError("magic verified-hit lane provenance is malformed")
    detail = row.get("status_detail")
    if not isinstance(detail, dict):
        raise TrancheError("magic verified-hit lane lacks status detail")
    gate = dict(_require_keys(
        detail.get("supervisor_verification"),
        {
            "accepted", "scalar_matrix_exit", "scalar_msq_d_exit",
            "independent_exit", "scalar_matrix_valid_json",
            "scalar_msq_d_valid_json", "independent_valid_json",
            "msq_d_expands_to_same_candidate_matrix", "matrix_token_sha256",
            "candidate_file",
        },
        "magic supervisor verification gate",
    ))
    if (
        gate["accepted"] is not True
        or gate["scalar_matrix_exit"] != 0
        or gate["scalar_msq_d_exit"] != 0
        or gate["independent_exit"] != 0
        or gate["scalar_matrix_valid_json"] is not True
        or gate["scalar_msq_d_valid_json"] is not True
        or gate["independent_valid_json"] is not True
        or gate["msq_d_expands_to_same_candidate_matrix"] is not True
    ):
        raise TrancheError("magic supervisor verification gate did not fully pass")

    gate_dir = (
        MAGIC_RUN_DIR.resolve() / "supervisor_verification" / lane
    )
    candidate_path = gate_dir / "candidate_values.txt"
    gate_path = gate_dir / "gate.json"
    if gate["candidate_file"] != str(candidate_path):
        raise TrancheError("magic verified-hit candidate path is not canonical")
    for path, name in (
        (candidate_path, "magic candidate"),
        (gate_path, "magic verification gate"),
    ):
        try:
            metadata = path.lstat()
        except OSError as exc:
            raise TrancheError(f"{name} cannot be inspected: {exc}") from exc
        if (
            path.is_symlink()
            or _is_reparse_stat(metadata)
            or not stat.S_ISREG(metadata.st_mode)
        ):
            raise TrancheError(f"{name} is not a plain regular file")

    gate_value, gate_sha256 = _load_json_with_sha(gate_path)
    if gate_value != gate:
        raise TrancheError("magic verification gate artifact differs from the lane")
    try:
        candidate_bytes = candidate_path.read_bytes()
        candidate_text = candidate_bytes.decode("ascii")
    except (OSError, UnicodeError) as exc:
        raise TrancheError(f"cannot read magic candidate values: {exc}") from exc
    tokens = candidate_text.removesuffix("\n").split(" ")
    if (
        not candidate_text.endswith("\n")
        or candidate_text.count("\n") != 1
        or len(tokens) != 9
        or any(re.fullmatch(r"[1-9][0-9]*", token) is None for token in tokens)
    ):
        raise TrancheError("magic candidate values artifact is malformed")
    values = [int(token) for token in tokens]
    roots = [math.isqrt(value) for value in values]
    lines = (
        values[0:3], values[3:6], values[6:9],
        values[0:9:3], values[1:9:3], values[2:9:3],
        (values[0], values[4], values[8]),
        (values[2], values[4], values[6]),
    )
    if (
        len(set(values)) != 9
        or any(root * root != value for root, value in zip(roots, values))
        or len({sum(line) for line in lines}) != 1
    ):
        raise TrancheError("magic candidate fails direct exact arithmetic")
    candidate_sha256 = hashlib.sha256(candidate_bytes).hexdigest()
    matrix_token_sha256 = gate["matrix_token_sha256"]
    if (
        not isinstance(matrix_token_sha256, str)
        or matrix_token_sha256.casefold() != candidate_sha256
    ):
        raise TrancheError("magic candidate hash differs from the verification gate")

    gate_inventory = _inventory(gate_dir)
    expected_gate_files = {
        "candidate_values.txt", "gate.json",
        "scalar_matrix.stdout.json", "scalar_matrix.stderr.txt",
        "scalar_msq_d.stdout.json", "scalar_msq_d.stderr.txt",
        "independent.stdout.json", "independent.stderr.txt",
    }
    if set(gate_inventory) != expected_gate_files:
        raise TrancheError("magic verification gate inventory is not exact")
    for name in (
        "scalar_matrix.stderr.txt", "scalar_msq_d.stderr.txt",
        "independent.stderr.txt",
    ):
        if (gate_dir / name).stat().st_size != 0:
            raise TrancheError("magic verification gate contains verifier stderr")
    scalar_matrix = _load_json(gate_dir / "scalar_matrix.stdout.json")
    scalar_msq_d = _load_json(gate_dir / "scalar_msq_d.stdout.json")
    independent = _load_json(gate_dir / "independent.stdout.json")
    matrix = [values[0:3], values[3:6], values[6:9]]
    if (
        not isinstance(scalar_matrix, dict)
        or scalar_matrix.get("valid") is not True
        or scalar_matrix.get("matrix") != matrix
        or not isinstance(scalar_msq_d, dict)
        or scalar_msq_d.get("valid") is not True
        or scalar_msq_d.get("matrix") != matrix
        or not isinstance(independent, dict)
        or independent.get("valid") is not True
    ):
        raise TrancheError("magic verifier output artifacts do not validate the candidate")
    return {
        "lane": lane,
        "lane_record_sha256": _canonical_sha(row),
        "gate_path": str(gate_path),
        "gate_sha256": gate_sha256,
        "candidate_path": str(candidate_path),
        "candidate_sha256": candidate_sha256,
        "gate_inventory": gate_inventory,
    }



def _validate_magic_terminal() -> dict[str, Any]:
    """Validate the exact terminal recovery artifacts without trusting PIDs."""

    state = _load_json(MAGIC_STATE_PATH, missing_ready=True)
    summary = _load_json(MAGIC_SUMMARY_PATH, missing_ready=True)
    inventory = _load_json(MAGIC_INVENTORY_PATH)
    run_once = _load_json(MAGIC_RUN_ONCE_PATH)

    state_keys = {
        "schema_version", "kind", "run_id", "source_run_id", "supervisor_pid",
        "status", "original_started_utc", "original_deadline_utc", "deadline_unix",
        "worker_cap", "workers_launched_recovery", "workers_running_recovery",
        "retained_completed_lanes", "manifest_sha256", "approved_artifact_hashes",
        "proof_claim", "anomaly", "updated_utc", "lanes",
    }
    summary_keys = {
        "schema_version", "kind", "run_id", "source_run_id", "source_portfolio_status",
        "status", "proof_claim", "claim_scope", "original_started_utc",
        "original_deadline_utc", "finished_utc", "manifest_sha256",
        "approved_artifact_hashes", "workers_requested_original",
        "workers_launched_recovery", "retained_completed_lanes", "combined_lane_count",
        "stop_reason", "hit_lane", "anomaly", "owned_tree_snapshot_error",
        "unverified_stop_lanes", "dead_root_failures", "owned_process_survivors",
        "source_anomaly_retained_as_provenance", "nonempty_recovery_stderr_lanes",
        "original_artifacts_unchanged", "changed_original_files", "lane_status_counts",
        "lanes",
    }
    state = _require_keys(state, state_keys, "magic recovery state")
    summary = _require_keys(summary, summary_keys, "magic recovery summary")
    if state["schema_version"] != 1 or state["kind"] != "magic_square_squares_frozen_tranche_recovery_state":
        raise TrancheError("magic recovery state schema mismatch")
    if summary["schema_version"] != 1 or summary["kind"] != "magic_square_squares_frozen_tranche_recovery_summary":
        raise TrancheError("magic recovery summary schema mismatch")
    for value, name in ((state, "state"), (summary, "summary")):
        if value["run_id"] != MAGIC_RUN_ID or value["source_run_id"] != MAGIC_SOURCE_RUN_ID:
            raise TrancheError(f"magic {name} run identity mismatch")
        if str(value["manifest_sha256"]).casefold() != MAGIC_MANIFEST_SHA256:
            raise TrancheError(f"magic {name} manifest hash mismatch")
        approved = value["approved_artifact_hashes"]
        if not isinstance(approved, dict) or {
            str(key): str(digest).casefold() for key, digest in approved.items()
        } != MAGIC_APPROVED_ARTIFACT_HASHES:
            raise TrancheError(f"magic {name} approved artifact hashes mismatch")
        if value["proof_claim"] is not False:
            raise TrancheError(f"magic {name} contains an invalid proof claim")
    for name, expected_digest in MAGIC_APPROVED_ARTIFACT_HASHES.items():
        path = (MAGIC_ENGINE_DIR / name).resolve()
        if not path.is_file() or _sha256_file(path) != expected_digest:
            raise TrancheError(
                f"actual magic artifact differs from approved hash: {name}"
            )

    if state["status"] != summary["status"]:
        raise TrancheError("magic terminal state/summary status mismatch")
    if state["workers_running_recovery"] != 0 or state["worker_cap"] != 64:
        raise TrancheNotReady("magic recovery still owns running workers")
    if state["anomaly"] is not None or summary["anomaly"] is not None:
        raise TrancheError("magic terminal artifacts contain an anomaly")
    if summary["owned_tree_snapshot_error"] is not None:
        raise TrancheError("magic owned-tree snapshot was not clean")
    for key in (
        "unverified_stop_lanes", "dead_root_failures", "owned_process_survivors",
        "nonempty_recovery_stderr_lanes", "changed_original_files",
    ):
        if not isinstance(summary[key], list) or summary[key]:
            raise TrancheError(f"magic terminal list {key} is not empty")
    if summary["original_artifacts_unchanged"] is not True:
        raise TrancheError("magic original artifact tree was not certified unchanged")
    if summary["workers_requested_original"] != 64 or summary["combined_lane_count"] != 64:
        raise TrancheError("magic terminal summary is not a 64-lane certificate")

    status = summary["status"]
    statuses = summary["lane_status_counts"]
    if not isinstance(statuses, dict):
        raise TrancheError("magic lane_status_counts must be an object")
    if status == "NO_HIT_DECLARED_DOMAINS":
        if summary["stop_reason"] != "ALL_COMPLETED" or statuses != {"NO_HIT": 64}:
            raise TrancheError("magic NO_HIT terminal contract mismatch")
        outcome = "CONTINUE"
    elif status == "TIMEOUT_INCOMPLETE":
        if summary["stop_reason"] != "ORIGINAL_DEADLINE":
            raise TrancheError("magic timeout did not occur at the original deadline")
        if not statuses or not set(statuses).issubset({"NO_HIT", "TIMEOUT_INCOMPLETE"}):
            raise TrancheError("magic timeout lane statuses are not admissible")
        if sum(_strict_int(count, f"magic status count {key}", 0) for key, count in statuses.items()) != 64:
            raise TrancheError("magic timeout lane status count is not 64")
        outcome = "CONTINUE"
    elif status == "HIT_VERIFIED":
        if (
            summary["stop_reason"] != "HIT_VERIFIED"
            or summary["hit_lane"] not in _magic_lane_ids()
            or statuses.get("HIT_VERIFIED") != 1
            or not set(statuses).issubset(
                {"NO_HIT", "HIT_VERIFIED", "STOPPED_AFTER_OTHER_HIT"}
            )
            or sum(
                _strict_int(count, f"magic status count {key}", 0)
                for key, count in statuses.items()
            ) != 64
        ):
            raise TrancheError("magic verified-hit terminal contract mismatch")
        outcome = "VERIFIED_HIT"
    else:
        raise TrancheNotReady(f"magic campaign is not in an accepted terminal state: {status}")

    expected_ids = _magic_lane_ids()
    summary_lanes = summary["lanes"]
    state_lanes = state["lanes"]
    if not isinstance(summary_lanes, list) or not isinstance(state_lanes, list):
        raise TrancheError("magic lane records must be arrays")
    if len(summary_lanes) != 64 or any(not isinstance(row, dict) for row in summary_lanes):
        raise TrancheError("magic summary must contain exactly 64 object rows")
    if len(state_lanes) != 64 or any(not isinstance(row, dict) for row in state_lanes):
        raise TrancheError("magic state must contain exactly 64 object rows")
    if {row.get("lane") for row in summary_lanes} != expected_ids:
        raise TrancheError("magic summary lane identities are not exact")
    if {row.get("lane") for row in state_lanes} != expected_ids:
        raise TrancheError("magic state lane identities are not exact")
    state_by_lane = {row["lane"]: row for row in state_lanes}
    for row in summary_lanes:
        if not isinstance(row, dict) or row.get("source_run_id") != MAGIC_SOURCE_RUN_ID:
            raise TrancheError("magic lane provenance mismatch")
        lane_id = row["lane"]
        state_row = state_by_lane[lane_id]
        if state_row != row:
            raise TrancheError(f"magic lane {lane_id} state/summary row mismatch")
        source = row.get("source")
        if source == "recovered_interrupted_lane":
            pid = row.get("pid")
            if (
                row.get("owned") is not True
                or isinstance(pid, bool)
                or not isinstance(pid, int)
                or pid <= 0
            ):
                raise TrancheError(
                    f"magic recovered lane {lane_id} ownership provenance is malformed"
                )
        elif source == "retained_original_exact_completion":
            if row.get("owned") is not False or row.get("pid") is not None:
                raise TrancheError(
                    f"magic retained lane {lane_id} ownership provenance is malformed"
                )
        else:
            raise TrancheError(f"magic lane {lane_id} source is not canonical")
        if outcome == "CONTINUE" and _has_candidate_signal(row):
            raise TrancheError(f"magic lane {lane_id} contains a candidate signal")
        lane_status = row.get("status")
        if state_row.get("status") != lane_status:
            raise TrancheError(f"magic lane {lane_id} state/summary mismatch")
        if lane_status == "NO_HIT" and row.get("return_code") != 0:
            raise TrancheError(f"magic lane {lane_id} NO_HIT lacks exit zero")
        if row.get("single_thread_search") is not True:
            raise TrancheError(f"magic lane {lane_id} was not single-threaded")
        expected_root = (
            MAGIC_RUN_DIR.resolve()
            if source == "recovered_interrupted_lane"
            else MAGIC_SOURCE_RUN_DIR.resolve()
        )
        for field in ("stdout", "stderr"):
            raw_path = row.get(field)
            if not isinstance(raw_path, str):
                raise TrancheError(f"magic lane {lane_id} {field} path is malformed")
            evidence_path = Path(raw_path).resolve()
            if not _is_within(evidence_path, expected_root) or not evidence_path.is_file():
                raise TrancheError(f"magic lane {lane_id} {field} path is not canonical")
            if field == "stderr" and evidence_path.stat().st_size != 0:
                raise TrancheError(f"magic lane {lane_id} emitted stderr")
    observed_histogram = {
        lane_status: sum(row.get("status") == lane_status for row in summary_lanes)
        for lane_status in sorted({row.get("status") for row in summary_lanes})
    }
    if observed_histogram != statuses:
        raise TrancheError("magic lane_status_counts differs from the 64 raw rows")
    verified_hit: dict[str, Any] | None = None
    if outcome == "CONTINUE":
        _scan_magic_raw_candidate_signals(MAGIC_RUN_DIR)
        _scan_magic_raw_candidate_signals(MAGIC_SOURCE_RUN_DIR)
    else:
        hit_rows = [
            row for row in summary_lanes if row.get("status") == "HIT_VERIFIED"
        ]
        if len(hit_rows) != 1 or hit_rows[0].get("lane") != summary["hit_lane"]:
            raise TrancheError("magic hit lane differs from the 64 raw rows")
        verified_hit = _validate_magic_verified_hit(hit_rows[0])
    recovery_tree_sha256 = _magic_recovery_tree_sha256()

    for stderr_path in MAGIC_RUN_DIR.rglob("*recovery.stderr.txt"):
        if stderr_path.stat().st_size != 0:
            raise TrancheError(f"nonempty recovery stderr found directly: {stderr_path}")

    inventory = _require_keys(inventory, {"source_run_dir", "files"}, "magic inventory")
    if inventory["source_run_dir"] != str(MAGIC_SOURCE_RUN_DIR.resolve()):
        raise TrancheError("magic inventory source path mismatch")
    frozen_files = inventory["files"]
    if not isinstance(frozen_files, dict):
        raise TrancheError("magic frozen source inventory is malformed")
    normalized_files: dict[str, str] = {}
    for relative_path, digest in frozen_files.items():
        if (
            not isinstance(relative_path, str)
            or not isinstance(digest, str)
            or SHA256_RE.fullmatch(digest.casefold()) is None
        ):
            raise TrancheError("magic frozen source inventory entry is malformed")
        normalized_files[relative_path] = digest.casefold()
    if normalized_files != _inventory(MAGIC_SOURCE_RUN_DIR):
        raise TrancheError("magic source inventory differs from the frozen inventory")

    run_once = _require_keys(
        run_once,
        {
            "approved_artifact_hashes", "approved_gaussian_exe_sha256", "created_utc",
            "creator_pid", "manifest_sha256", "original_deadline_unix",
            "original_start_unix", "rule", "run_dir", "schema_version",
            "source_run_dir", "source_summary_sha256",
        },
        "magic run-once record",
    )
    if run_once["schema_version"] != 1 or run_once["run_dir"] != str(MAGIC_RUN_DIR.resolve()):
        raise TrancheError("magic run-once identity mismatch")
    if str(run_once["manifest_sha256"]).casefold() != MAGIC_MANIFEST_SHA256:
        raise TrancheError("magic run-once manifest hash mismatch")

    return {
        "outcome": outcome,
        "status": status,
        "state_sha256": _sha256_file(MAGIC_STATE_PATH),
        "summary_sha256": _sha256_file(MAGIC_SUMMARY_PATH),
        "inventory_sha256": _sha256_file(MAGIC_INVENTORY_PATH),
        "run_once_sha256": _sha256_file(MAGIC_RUN_ONCE_PATH),
        "recovery_tree_sha256": recovery_tree_sha256,
        "verified_hit": verified_hit,
        "finished_utc": summary["finished_utc"],
    }


def _claim_lock_action(
    t0: datetime, magic: Mapping[str, Any], artifact_hashes: Mapping[str, str],
    readiness_sha256: str,
) -> dict[str, Any]:
    if LOCK_PATH.exists():
        raise PermanentFailure(f"permanent Q5 tranche lock already exists: {LOCK_PATH}")
    if TRANCHE_DIR.exists():
        raise PermanentFailure(f"fixed tranche directory already exists without a new lock: {TRANCHE_DIR}")
    t0 = t0.replace(microsecond=0)
    monotonic_start_ns = time.monotonic_ns()
    boot_time_microseconds = _boot_time_microseconds()
    lock = {
        "schema_version": 1,
        "kind": "Q5_TRANCHE_GLOBAL_LOCK",
        "tranche_id": TRANCHE_ID,
        "t0": _utc_text(t0),
        "s": _utc_text(t0 + timedelta(seconds=25200)),
        "g": _utc_text(t0 + timedelta(seconds=28800)),
        "creator_pid": os.getpid(),
        "claimed_utc": _utc_text(t0),
        "boot_time_microseconds": boot_time_microseconds,
        "monotonic_start_ns": monotonic_start_ns,
        "magic_terminal_summary_sha256": magic["summary_sha256"],
        "launch_readiness_sha256": readiness_sha256,
        "frozen_artifact_hashes": dict(artifact_hashes),
    }
    try:
        with LOCK_PATH.open("xb") as stream:
            stream.write(manifest_lib.canonical_bytes(lock) + b"\n")
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise PermanentFailure("permanent Q5 tranche lock was won by another process") from exc
    except OSError as exc:
        raise PermanentFailure(f"cannot create permanent Q5 tranche lock: {exc}") from exc
    return lock


def _state_template(lock: Mapping[str, Any], phase: str, now: datetime) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "Q5_TRANCHE_STATE",
        "tranche_id": TRANCHE_ID,
        "revision": 0,
        "phase": phase,
        "t0": lock["t0"],
        "s": lock["s"],
        "g": lock["g"],
        "plan_sha256": None,
        "last_intent": "transition_000000.json",
        "accepted_pilots": {},
        "selection_report_sha256": None,
        "selected_h": None,
        "selected_main_manifest_sha256": None,
        "verified_hit": None,
        "main_terminal_report_sha256": None,
        "persistent_error": None,
        "updated_utc": _utc_text(now),
    }


STATE_KEYS = {
    "schema_version", "kind", "tranche_id", "revision", "phase", "t0", "s", "g",
    "plan_sha256", "last_intent", "accepted_pilots", "selection_report_sha256",
    "selected_h", "selected_main_manifest_sha256", "verified_hit", "main_terminal_report_sha256",
    "persistent_error", "updated_utc",
}

VERIFIED_HIT_BINDING_KEYS = {
    "schema_version", "kind", "source", "source_id",
    "source_evidence_sha256", "record",
}


def _verified_hit_binding(
    source: str,
    source_id: str,
    source_evidence_sha256: str,
    record: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "Q5_TRANCHE_VERIFIED_HIT_BINDING",
        "source": source,
        "source_id": source_id,
        "source_evidence_sha256": source_evidence_sha256,
        "record": copy.deepcopy(dict(record)),
    }


def _pilot_hit_binding(
    pilot: str, evidence: Mapping[str, Any]
) -> dict[str, Any]:
    record = evidence.get("verified_hit")
    if not isinstance(record, dict):
        raise PermanentFailure(f"pilot {pilot} lacks verified-hit evidence")
    return _verified_hit_binding(
        "pilot", pilot, _canonical_sha(evidence), record
    )


def _main_hit_binding(
    evidence: Mapping[str, Any], report_sha256: str
) -> dict[str, Any]:
    record = evidence.get("verified_hit")
    if not isinstance(record, dict):
        raise PermanentFailure("main report lacks verified-hit evidence")
    return _verified_hit_binding(
        "main", MAIN_CAMPAIGN_ID, report_sha256, record
    )


def _magic_hit_binding(magic: Mapping[str, Any]) -> dict[str, Any]:
    record = magic.get("verified_hit")
    if not isinstance(record, dict):
        raise PermanentFailure("magic terminal record lacks verified-hit evidence")
    return _verified_hit_binding(
        "magic", MAGIC_RUN_ID, _canonical_sha(magic), record
    )


def _validate_verified_hit_binding(state: Mapping[str, Any]) -> None:
    raw = state["verified_hit"]
    if state["phase"] != "VERIFIED_HIT":
        if raw is not None:
            raise PermanentFailure("non-VERIFIED_HIT phase carries verified-hit evidence")
        return
    binding = dict(_require_keys(
        raw, VERIFIED_HIT_BINDING_KEYS, "state verified-hit binding"
    ))
    if (
        binding["schema_version"] != 1
        or binding["kind"] != "Q5_TRANCHE_VERIFIED_HIT_BINDING"
        or binding["source"] not in {"pilot", "main", "magic"}
        or not isinstance(binding["source_id"], str)
        or not isinstance(binding["source_evidence_sha256"], str)
        or SHA256_RE.fullmatch(binding["source_evidence_sha256"]) is None
        or not isinstance(binding["record"], dict)
    ):
        raise PermanentFailure("state verified-hit binding is malformed")
    source = binding["source"]
    if source == "pilot":
        pilot = binding["source_id"]
        evidence = state["accepted_pilots"].get(pilot)
        if (
            pilot not in PILOT_ORDER
            or not isinstance(evidence, dict)
            or state["main_terminal_report_sha256"] is not None
            or binding != _pilot_hit_binding(pilot, evidence)
        ):
            raise PermanentFailure("state pilot hit is not bound to accepted evidence")
        try:
            _validate_verified_hit(binding["record"])
        except TrancheError as exc:
            raise PermanentFailure("state pilot hit record is invalid") from exc
    elif source == "main":
        if (
            binding["source_id"] != MAIN_CAMPAIGN_ID
            or binding["source_evidence_sha256"]
            != state["main_terminal_report_sha256"]
        ):
            raise PermanentFailure("state main hit is not bound to its terminal report")
        try:
            _validate_verified_hit(binding["record"])
        except TrancheError as exc:
            raise PermanentFailure("state main hit record is invalid") from exc
    else:
        if (
            binding["source_id"] != MAGIC_RUN_ID
            or state["revision"] != 0
            or state["accepted_pilots"]
            or state["main_terminal_report_sha256"] is not None
        ):
            raise PermanentFailure("state magic hit is not source-bound")
        try:
            current_magic = _validate_magic_terminal()
        except TrancheError as exc:
            raise PermanentFailure(
                "state magic hit source evidence no longer validates"
            ) from exc
        if (
            current_magic.get("outcome") != "VERIFIED_HIT"
            or binding != _magic_hit_binding(current_magic)
        ):
            raise PermanentFailure(
                "state magic hit differs from live terminal evidence"
            )



def _validate_state_shape(raw: Any) -> dict[str, Any]:
    state = dict(_require_keys(raw, STATE_KEYS, "tranche state"))
    if state["schema_version"] != 1 or state["kind"] != "Q5_TRANCHE_STATE":
        raise PermanentFailure("tranche state schema mismatch")
    if state["tranche_id"] != TRANCHE_ID or state["phase"] not in PHASES:
        raise PermanentFailure("tranche state identity or phase mismatch")
    revision = _strict_int(state["revision"], "state revision", 0)
    if state["last_intent"] != f"transition_{revision:06d}.json":
        raise PermanentFailure("tranche state last-intent pointer mismatch")
    t0 = _parse_time(state["t0"], "state.t0")
    s = _parse_time(state["s"], "state.s")
    g = _parse_time(state["g"], "state.g")
    if t0.microsecond or s != t0 + timedelta(seconds=25200) or g != t0 + timedelta(seconds=28800):
        raise PermanentFailure("T0/S/G immutable clock contract mismatch")
    if not isinstance(state["accepted_pilots"], dict):
        raise PermanentFailure("accepted_pilots must be an object")
    report_sha256 = state["main_terminal_report_sha256"]
    if report_sha256 is not None and (
        not isinstance(report_sha256, str) or SHA256_RE.fullmatch(report_sha256) is None
    ):
        raise PermanentFailure("main terminal report hash is malformed")
    requires_main_report = state["phase"] in {"MAIN_FINITE_NO_HIT", "MAIN_TIMEOUT_INCOMPLETE"}
    if requires_main_report and report_sha256 is None:
        raise PermanentFailure("main terminal phase lacks its report pin")
    if report_sha256 is not None and state["phase"] not in {
        "MAIN_FINITE_NO_HIT", "MAIN_TIMEOUT_INCOMPLETE", "VERIFIED_HIT",
    }:
        raise PermanentFailure("non-main-terminal phase carries a main report pin")
    _validate_verified_hit_binding(state)
    return state


def _write_xb(path: Path, data: bytes) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as exc:
        raise PermanentFailure(f"write-once artifact already exists: {path}") from exc
    except OSError as exc:
        raise PermanentFailure(f"cannot create write-once artifact {path}: {exc}") from exc


def _commit_initial_action(plan: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    plan_bytes = _pretty_bytes(plan)
    state["plan_sha256"] = hashlib.sha256(plan_bytes).hexdigest()
    _validate_state_shape(state)
    state_bytes = _pretty_bytes(state)
    TRANCHE_DIR.mkdir(parents=False, exist_ok=False)
    INTENTS_DIR.mkdir(parents=False, exist_ok=False)
    intent = {
        "schema_version": 1,
        "kind": "Q5_TRANCHE_TRANSITION_INTENT",
        "tranche_id": TRANCHE_ID,
        "from_revision": None,
        "from_phase": None,
        "to_revision": 0,
        "to_phase": state["phase"],
        "previous_state_sha256": None,
        "next_state_sha256": _canonical_sha(state),
        "extra_files": {str(PLAN_PATH): hashlib.sha256(plan_bytes).hexdigest()},
        "created_utc": state["updated_utc"],
    }
    _write_xb(INTENTS_DIR / state["last_intent"], manifest_lib.canonical_bytes(intent) + b"\n")
    manifest_lib.atomic_write_bytes(PLAN_PATH, plan_bytes)
    manifest_lib.atomic_write_bytes(STATE_PATH, state_bytes)
    return state


def _intent_files() -> list[Path]:
    if not INTENTS_DIR.is_dir():
        raise PermanentFailure("transition intent directory is missing")
    files = sorted(INTENTS_DIR.glob("transition_*.json"), key=lambda path: path.name)
    extras = [path for path in INTENTS_DIR.iterdir() if path not in files]
    if extras:
        raise PermanentFailure("transition intent directory contains an unexpected file")
    return files


def _validate_ledger(state: Mapping[str, Any]) -> None:
    revision = state["revision"]
    files = _intent_files()
    expected_names = [f"transition_{index:06d}.json" for index in range(revision + 1)]
    if [path.name for path in files] != expected_names:
        raise PermanentFailure("missing, extra, or orphan transition intent detected")
    previous_sha: str | None = None
    previous_phase: str | None = None
    legal_edges = {
        None: {"READY_A", "VERIFIED_HIT", "FAIL_CLOSED"},
        "READY_A": {"READY_B", "VERIFIED_HIT", "FAIL_CLOSED"},
        "READY_B": {"READY_C", "VERIFIED_HIT", "FAIL_CLOSED"},
        "READY_C": {"READY_D", "VERIFIED_HIT", "FAIL_CLOSED"},
        "READY_D": {"READY_SELECTION", "VERIFIED_HIT", "FAIL_CLOSED"},
        "READY_SELECTION": {"MAIN_FROZEN", "NO_MAIN", "FAIL_CLOSED"},
        "MAIN_FROZEN": {"MAIN_FINITE_NO_HIT", "MAIN_TIMEOUT_INCOMPLETE", "VERIFIED_HIT", "FAIL_CLOSED"},
    }
    previous_time: datetime | None = None
    for index, path in enumerate(files):
        intent = _load_json(path)
        intent = _require_keys(
            intent,
            {
                "schema_version", "kind", "tranche_id", "from_revision", "from_phase",
                "to_revision", "to_phase", "previous_state_sha256", "next_state_sha256",
                "extra_files", "created_utc",
            },
            f"intent {index}",
        )
        if intent["schema_version"] != 1 or intent["kind"] != "Q5_TRANCHE_TRANSITION_INTENT":
            raise PermanentFailure(f"intent {index} schema mismatch")
        if intent["tranche_id"] != TRANCHE_ID or intent["to_revision"] != index:
            raise PermanentFailure(f"intent {index} identity mismatch")
        created = _parse_time(intent["created_utc"], f"intent {index} time")
        if previous_time is not None and created < previous_time:
            raise PermanentFailure(f"intent {index} timestamp rollback")
        allowed = legal_edges.get(previous_phase, set())
        if intent["to_phase"] not in allowed:
            raise PermanentFailure(f"intent {index} phase edge is illegal")
        previous_time = created
        if index == 0:
            if any(intent[key] is not None for key in ("from_revision", "from_phase", "previous_state_sha256")):
                raise PermanentFailure("initial intent has a predecessor")
        else:
            if intent["from_revision"] != index - 1 or intent["from_phase"] != previous_phase:
                raise PermanentFailure(f"intent {index} predecessor mismatch")
            if intent["previous_state_sha256"] != previous_sha:
                raise PermanentFailure(f"intent {index} previous-state hash mismatch")
        extras = intent["extra_files"]
        if not isinstance(extras, dict):
            raise PermanentFailure(f"intent {index} extra_files is not an object")
        for raw_extra_path, expected_digest in extras.items():
            if (
                not isinstance(raw_extra_path, str)
                or not isinstance(expected_digest, str)
                or SHA256_RE.fullmatch(expected_digest) is None
            ):
                raise PermanentFailure(f"intent {index} extra-file record is malformed")
            extra_path = Path(raw_extra_path).resolve()
            if not _is_within(extra_path, TRANCHE_DIR.resolve()):
                raise PermanentFailure(f"intent {index} extra file is outside tranche")
            if _sha256_file(Path(raw_extra_path)) != expected_digest:
                raise PermanentFailure(f"intent {index} extra-file hash mismatch")
        next_sha = intent["next_state_sha256"]
        if not isinstance(next_sha, str) or SHA256_RE.fullmatch(next_sha) is None:
            raise PermanentFailure(f"intent {index} next-state hash malformed")
        previous_sha = next_sha
        previous_phase = intent["to_phase"]
    if previous_sha != _canonical_sha(state) or previous_phase != state["phase"]:
        raise PermanentFailure("latest intent is orphaned from the committed state")
    if previous_time != _parse_time(state["updated_utc"], "state updated_utc"):
        raise PermanentFailure("latest intent timestamp differs from state")


def _load_context() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if not LOCK_PATH.is_file():
        raise TrancheNotReady("Q5 tranche has not been started")
    lock, lock_file_sha256 = _load_json_with_sha(LOCK_PATH)
    lock = dict(_require_keys(
        lock,
        {
            "schema_version", "kind", "tranche_id", "t0", "s", "g", "creator_pid",
            "launch_readiness_sha256",
            "claimed_utc", "magic_terminal_summary_sha256",
            "frozen_artifact_hashes", "boot_time_microseconds",
            "monotonic_start_ns",
        },
        "global lock",
    ))
    if lock["schema_version"] != 1 or lock["kind"] != "Q5_TRANCHE_GLOBAL_LOCK" or lock["tranche_id"] != TRANCHE_ID:
        raise PermanentFailure("global lock identity mismatch")
    state = _validate_state_shape(_load_json(STATE_PATH))
    _strict_int(lock["boot_time_microseconds"], "global lock boot identity", 0)
    _strict_int(lock["monotonic_start_ns"], "global lock monotonic start", 0)
    plan = _load_json(PLAN_PATH)
    if not isinstance(plan, dict):
        raise PermanentFailure("tranche plan must be an object")
    if plan.get("global_lock_sha256") != lock_file_sha256:
        raise PermanentFailure("global lock differs from the plan integrity pin")
    magic_terminal = plan.get("magic_terminal")
    if (
        not isinstance(magic_terminal, dict)
        or magic_terminal.get("summary_sha256")
        != lock["magic_terminal_summary_sha256"]
    ):
        raise PermanentFailure("magic terminal prerequisite differs across lock/plan")
    try:
        current_magic = _validate_magic_terminal()
    except TrancheError as exc:
        raise PermanentFailure("magic terminal prerequisite no longer validates") from exc
    if current_magic != magic_terminal:
        raise PermanentFailure("magic terminal prerequisite differs from its T0 pin")
    if _sha256_file(PLAN_PATH) != state["plan_sha256"]:
        raise PermanentFailure("plan hash differs from the state pin")
    readiness_record = plan.get("launch_readiness")
    if (
        readiness_record != {
            "path": str(READINESS_PATH.resolve()),
            "file_sha256": lock["launch_readiness_sha256"],
        }
    ):
        raise PermanentFailure("launch readiness differs across lock/plan")
    _validate_readiness(expected_sha256=lock["launch_readiness_sha256"])
    for key in ("t0", "s", "g"):
        if state[key] != lock[key] or plan.get(key) != lock[key]:
            raise PermanentFailure(f"immutable {key.upper()} differs across lock/plan/state")
    if lock["frozen_artifact_hashes"] != plan.get("frozen_artifact_hashes"):
        raise PermanentFailure("frozen artifact hashes differ across lock/plan")
    if _artifact_hashes() != plan["frozen_artifact_hashes"]:
        raise PermanentFailure("frozen runtime artifacts drifted after T0")
    _validate_ledger(state)
    return lock, plan, state


def _transition_action(
    state: dict[str, Any],
    *,
    phase: str,
    now: datetime,
    updates: Mapping[str, Any] | None = None,
    extra_files: Mapping[Path, bytes] | None = None,
) -> dict[str, Any]:
    if state["phase"] in TERMINAL_PHASES:
        raise PermanentFailure(f"terminal tranche phase cannot transition: {state['phase']}")
    if phase not in PHASES:
        raise TrancheError(f"unrecognized target phase {phase}")
    new_state = copy.deepcopy(state)
    new_state["revision"] += 1
    new_state["phase"] = phase
    new_state["last_intent"] = f"transition_{new_state['revision']:06d}.json"
    new_state["updated_utc"] = _utc_text(now)
    if updates:
        for key, value in updates.items():
            if key in {"t0", "s", "g", "revision", "last_intent"}:
                raise TrancheError(f"transition cannot modify immutable field {key}")
            if key not in STATE_KEYS:
                raise TrancheError(f"transition update field is not in the state schema: {key}")
            new_state[key] = value
    _validate_state_shape(new_state)
    extras = dict(extra_files or {})
    for path in extras:
        if path.exists():
            raise PermanentFailure(f"transition extra file already exists: {path}")
    intent = {
        "schema_version": 1,
        "kind": "Q5_TRANCHE_TRANSITION_INTENT",
        "tranche_id": TRANCHE_ID,
        "from_revision": state["revision"],
        "from_phase": state["phase"],
        "to_revision": new_state["revision"],
        "to_phase": phase,
        "previous_state_sha256": _canonical_sha(state),
        "next_state_sha256": _canonical_sha(new_state),
        "extra_files": {
            str(path): hashlib.sha256(data).hexdigest() for path, data in extras.items()
        },
        "created_utc": _utc_text(now),
    }
    _write_xb(INTENTS_DIR / new_state["last_intent"], manifest_lib.canonical_bytes(intent) + b"\n")
    for path, data in extras.items():
        manifest_lib.atomic_write_bytes(path, data)
    manifest_lib.atomic_write_bytes(STATE_PATH, _pretty_bytes(new_state))
    return new_state


def _fail_closed_action(
    commit: Callable[..., dict[str, Any]],
    state: dict[str, Any],
    error: BaseException,
    now: datetime,
) -> dict[str, Any]:
    if state["phase"] == "FAIL_CLOSED":
        return state
    transition_time = max(
        now, _parse_time(state["updated_utc"], "state updated_utc")
    )
    return commit(
        state,
        phase="FAIL_CLOSED",
        now=transition_time,
        updates={"persistent_error": f"{type(error).__name__}: {error}"},
    )


def _validate_transition_clock(
    state: Mapping[str, Any],
    now: datetime,
    lock: Mapping[str, Any] | None = None,
) -> None:
    updated = _parse_time(state["updated_utc"], "state updated_utc")
    if now < updated:
        raise TrancheError("clock rollback detected")
    if now >= _parse_time(state["g"], "G"):
        raise TrancheError("tranche hard deadline G has been reached")
    if lock is None:
        return
    boot_now = _boot_time_microseconds()
    boot_start = _strict_int(
        lock.get("boot_time_microseconds"), "global lock boot identity", 0
    )
    if boot_now != boot_start:
        raise TrancheError("system boot identity changed after T0")
    monotonic_start = _strict_int(
        lock.get("monotonic_start_ns"), "global lock monotonic start", 0
    )
    monotonic_now = time.monotonic_ns()
    if monotonic_now < monotonic_start:
        raise TrancheError("monotonic clock moved before the tranche start")
    monotonic_elapsed_ns = monotonic_now - monotonic_start
    if monotonic_elapsed_ns >= 28_800_000_000_000:
        raise TrancheError("tranche hard deadline G has elapsed monotonically")
    t0 = _parse_time(state["t0"], "T0")
    wall_delta = now - t0
    wall_elapsed_us = (
        wall_delta.days * 86_400_000_000
        + wall_delta.seconds * 1_000_000
        + wall_delta.microseconds
    )
    monotonic_elapsed_us = monotonic_elapsed_ns // 1_000
    if wall_elapsed_us + 5_000_000 < monotonic_elapsed_us:
        raise TrancheError("wall clock lags the monotonic tranche clock")



def _plan(lock: Mapping[str, Any], magic: Mapping[str, Any], snapshots: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    pilot_records = []
    for name in PILOT_ORDER:
        spec = PILOT_SPECS[name]
        pilot_records.append(
            {
                "name": name,
                "campaign_id": spec["campaign_id"],
                "bounds": spec["bounds"],
                "search_mode": spec["search_mode"],
                "limit_seconds": spec["limit_seconds"],
                "expected_no_work": spec["expected_no_work"],
                "manifest_path": str(spec["manifest_path"].resolve()),
                "lane_config_dir": str(spec["lane_config_dir"].resolve()),
                "run_dir": str(spec["run_dir"].resolve()),
            }
        )
    return {
        "schema_version": 1,
        "kind": "Q5_TRANCHE_PLAN",
        "tranche_id": TRANCHE_ID,
        "t0": lock["t0"],
        "s": lock["s"],
        "g": lock["g"],
        "magic_terminal": dict(magic),
        "global_lock_sha256": _sha256_file(LOCK_PATH),
        "preflight_censuses": [dict(snapshot) for snapshot in snapshots],
        "frozen_artifact_hashes": snapshots[-1]["artifact_hashes"],
        "launch_readiness": {
            "path": str(READINESS_PATH.resolve()),
            "file_sha256": lock["launch_readiness_sha256"],
        },
        "authorization_paths": {
            phase: str((AUTHORIZATIONS_DIR / f"{phase}.json").resolve())
            for phase in (*PILOT_ORDER, "MAIN")
        },
        "pilots": pilot_records,
        "main": {
            "campaign_id": MAIN_CAMPAIGN_ID,
            "manifest_path": str(MAIN_MANIFEST_PATH.resolve()),
            "lane_config_dir": str(MAIN_LANE_CONFIG_DIR.resolve()),
            "run_dir": str(MAIN_RUN_DIR.resolve()),
            "deadline": lock["s"],
        },
        "candidate_table": {
            "path": str(CANDIDATE_TABLE_PATH.resolve()),
            "file_sha256": _sha256_file(CANDIDATE_TABLE_PATH),
            "payload_sha256": CANDIDATE_TABLE_PAYLOAD_SHA256,
            "source_path": str(CANDIDATE_TABLE_SOURCE_PATH.resolve()),
            "source_sha256": _sha256_file(CANDIDATE_TABLE_SOURCE_PATH),
            "tool_path": str(CANDIDATE_TABLE_TOOL_PATH.resolve()),
            "tool_sha256": _sha256_file(CANDIDATE_TABLE_TOOL_PATH),
        },
        "selection_rule": (
            "rho=max_first_BCD_lane(e/(w*b^2));"
            "Tpred=ceil(3*rho*W_H*b_H^2/2);largest_H_with_Tpred+300000<=floor((S-now)*1000)"
        ),
        "setup_guard_milliseconds": 300000,
    }


def _start_tranche_action(
    claim_lock: Callable[..., dict[str, Any]],
    commit_initial: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    """Claim the tranche using only live clocks, sleeps, and process evidence."""

    clock = _now_utc
    census_hook: CensusHook | None = None
    monotonic_start_ns = time.monotonic_ns()
    readiness_before = _validate_readiness(now=_aware_utc(clock(), "readiness clock"))
    magic_before = _validate_magic_terminal()
    first = _validate_census(
        census_hook() if census_hook is not None else _live_census(clock), "preflight census 1"
    )
    time.sleep(10.0)
    if time.monotonic_ns() - monotonic_start_ns < 10_000_000_000:
        raise TrancheNotReady(
            "clean preflight censuses lack a ten-second monotonic interval")
    second = _validate_census(
        census_hook() if census_hook is not None else _live_census(clock), "preflight census 2"
    )
    first_time = _parse_time(first["captured_utc"], "preflight census 1 time")
    second_time = _parse_time(second["captured_utc"], "preflight census 2 time")
    now = _aware_utc(clock(), "clock")
    if second_time - first_time < timedelta(seconds=10):
        raise TrancheNotReady("clean preflight censuses are less than ten seconds apart")
    if second_time < first_time or now < second_time or now - second_time > timedelta(seconds=5):
        raise TrancheNotReady("newest clean preflight census is not current")
    if first["artifact_hashes"] != second["artifact_hashes"]:
        raise TrancheError("frozen artifact hashes changed between clean preflight censuses")

    lock = claim_lock(
        now.replace(microsecond=0), magic_before, second["artifact_hashes"],
        readiness_before["file_sha256"],
    )
    try:
        post = _validate_census(
            census_hook() if census_hook is not None else _live_census(clock), "post-lock census"
        )
        post_time = _parse_time(post["captured_utc"], "post-lock census time")
        post_now = _aware_utc(clock(), "clock")
        if (
            post_time < _parse_time(lock["claimed_utc"], "lock claim time")
            or post_time > post_now
            or post_now - post_time > timedelta(seconds=5)
        ):
            raise TrancheError("post-lock census is stale or predates the lock")
        readiness_after = _validate_readiness(
            expected_sha256=lock["launch_readiness_sha256"], now=post_now
        )
        if readiness_after["file_sha256"] != readiness_before["file_sha256"]:
            raise TrancheError("launch readiness drifted after the permanent lock")
        magic_after = _validate_magic_terminal()
        if post["artifact_hashes"] != second["artifact_hashes"]:
            raise TrancheError("frozen artifact hashes changed after the permanent lock")
        if magic_after != magic_before:
            raise TrancheError("magic terminal artifacts drifted after the permanent lock")
        phase = "VERIFIED_HIT" if magic_after["outcome"] == "VERIFIED_HIT" else "READY_A"
        plan = _plan(lock, magic_after, (first, second, post))
        initial = _state_template(lock, phase, _aware_utc(clock(), "clock"))
        if phase == "VERIFIED_HIT":
            initial["verified_hit"] = _magic_hit_binding(magic_after)
        state = commit_initial(plan, initial)
        return {"ok": True, "phase": state["phase"], "state": state, "plan_path": str(PLAN_PATH)}
    except BaseException as exc:
        # The global xb lock is already permanent.  Commit a durable failure
        # state when possible; otherwise the lock-without-state itself remains
        # unrecoverable evidence.
        try:
            if not TRANCHE_DIR.exists():
                fallback_snapshot = second
                plan = _plan(lock, magic_before, (first, second, fallback_snapshot))
                failed = _state_template(lock, "FAIL_CLOSED", _aware_utc(clock(), "clock"))
                failed["persistent_error"] = f"{type(exc).__name__}: {exc}"
                commit_initial(plan, failed)
        except BaseException:
            pass
        raise PermanentFailure(f"post-lock start failed permanently: {exc}") from exc


def _pilot_previous_finished(state: Mapping[str, Any], pilot: str) -> datetime:
    index = PILOT_ORDER.index(pilot)
    if index == 0:
        return _parse_time(state["t0"], "T0")
    previous = state["accepted_pilots"].get(PILOT_ORDER[index - 1])
    if not isinstance(previous, dict):
        raise TrancheError("previous pilot evidence is not accepted")
    return _parse_time(previous["finished_utc"], "previous pilot finish")


def _validate_launch_lock(path: Path, payload: Mapping[str, Any], digest: str) -> dict[str, Any]:
    lock = _load_json(path, missing_ready=True)
    lock = dict(_require_keys(
        lock,
        {"schema_version", "kind", "campaign_id", "manifest_payload_sha256", "launch_readiness_sha256", "authorization_sha256", "authorization_expires_utc", "supervisor_pid", "claimed_utc"},
        "pilot launch lock",
    ))
    if lock["schema_version"] != 1 or lock["kind"] != "Q5_TORSOR_LAUNCH_LOCK":
        raise TrancheError("pilot launch lock schema mismatch")
    if lock["campaign_id"] != payload["campaign_id"] or lock["manifest_payload_sha256"] != digest:
        raise TrancheError("pilot launch lock identity mismatch")
    _strict_int(lock["supervisor_pid"], "pilot supervisor pid", 1)
    if not isinstance(lock["launch_readiness_sha256"], str) or SHA256_RE.fullmatch(lock["launch_readiness_sha256"]) is None:
        raise TrancheError("pilot launch readiness hash is malformed")
    authorization_sha256 = lock["authorization_sha256"]
    if not isinstance(authorization_sha256, str) or SHA256_RE.fullmatch(authorization_sha256) is None:
        raise TrancheError("pilot launch authorization hash is malformed")
    claimed = _parse_time(lock["claimed_utc"], "pilot launch claimed_utc")
    expires = _parse_time(lock["authorization_expires_utc"], "pilot authorization expiry")
    if claimed >= expires:
        raise TrancheError("pilot launch was claimed at/after authorization expiry")
    return lock



def _validate_launch_lock_value(
    raw: Any, payload: Mapping[str, Any], digest: str, *, name: str,
    expected_readiness_sha256: str | None = None,
) -> dict[str, Any]:
    lock = dict(_require_keys(
        raw,
        {"schema_version", "kind", "campaign_id", "manifest_payload_sha256", "launch_readiness_sha256", "authorization_sha256", "authorization_expires_utc", "supervisor_pid", "claimed_utc"},
        name,
    ))
    if lock["schema_version"] != 1 or lock["kind"] != "Q5_TORSOR_LAUNCH_LOCK":
        raise TrancheError(f"{name} schema mismatch")
    if lock["campaign_id"] != payload["campaign_id"] or lock["manifest_payload_sha256"] != digest:
        raise TrancheError(f"{name} identity mismatch")
    readiness_sha256 = lock["launch_readiness_sha256"]
    if not isinstance(readiness_sha256, str) or SHA256_RE.fullmatch(readiness_sha256) is None:
        raise TrancheError(f"{name} launch readiness hash is malformed")
    if expected_readiness_sha256 is not None and readiness_sha256 != expected_readiness_sha256:
        raise TrancheError(f"{name} launch readiness pin mismatch")
    authorization_sha256 = lock["authorization_sha256"]
    if not isinstance(authorization_sha256, str) or SHA256_RE.fullmatch(authorization_sha256) is None:
        raise TrancheError(f"{name} authorization hash is malformed")
    _strict_int(lock["supervisor_pid"], f"{name} supervisor pid", 1)
    claimed = _parse_time(lock["claimed_utc"], f"{name} claimed_utc")
    expires = _parse_time(lock["authorization_expires_utc"], f"{name} authorization expiry")
    if claimed >= expires:
        raise TrancheError(f"{name} was claimed at/after authorization expiry")
    return lock


AUTHORIZATION_TICKET_KEYS = {
    "schema_version", "kind", "tranche_id", "phase", "created_utc", "expires_utc",
    "state_path", "state_sha256", "manifest_path", "manifest_file_sha256",
    "manifest_payload_sha256", "campaign_id", "mode", "search_mode", "deadline",
    "run_dir", "readiness_path", "readiness_sha256", "public_status_path",
    "public_status_sha256",
}


def _validate_authorization_ticket(
    *,
    phase: str,
    lock: Mapping[str, Any],
    payload: Mapping[str, Any],
    payload_digest: str,
    manifest_path: Path,
    manifest_file_sha256: str,
    run_dir: Path,
    plan: Mapping[str, Any],
    launch_claimed: datetime,
    expected_public_status_sha256: str | None,
    expected_state_sha256: str,
) -> dict[str, Any]:
    authorization_path = _authorization_path(phase)
    if plan.get("authorization_paths", {}).get(phase) != str(authorization_path):
        raise TrancheError(f"{phase} authorization path differs from the plan")
    raw, authorization_sha256 = _load_json_with_sha(
        authorization_path, missing_ready=True
    )
    ticket = dict(_require_keys(
        raw, AUTHORIZATION_TICKET_KEYS, f"{phase} launch authorization"
    ))
    if authorization_sha256 != lock["authorization_sha256"]:
        raise TrancheError(f"{phase} launch authorization hash mismatch")
    if (
        ticket["schema_version"] != 1
        or ticket["kind"] != "q5-launch-authorization-v1"
        or ticket["tranche_id"] != TRANCHE_ID
        or ticket["phase"] != phase
    ):
        raise TrancheError(f"{phase} launch authorization identity mismatch")
    state_sha256 = ticket["state_sha256"]
    if (
        ticket["state_path"] != str(STATE_PATH.resolve())
        or not isinstance(state_sha256, str)
        or SHA256_RE.fullmatch(state_sha256) is None
        or state_sha256 != expected_state_sha256
    ):
        raise TrancheError(f"{phase} launch authorization state pin is malformed")
    readiness_sha256 = plan["launch_readiness"]["file_sha256"]
    if (
        ticket["readiness_path"] != str(READINESS_PATH.resolve())
        or ticket["readiness_sha256"] != readiness_sha256
        or lock["launch_readiness_sha256"] != readiness_sha256
    ):
        raise TrancheError(f"{phase} launch authorization readiness pin mismatch")
    if (
        ticket["manifest_path"] != str(manifest_path)
        or ticket["manifest_file_sha256"] != manifest_file_sha256
        or ticket["manifest_payload_sha256"] != payload_digest
        or ticket["campaign_id"] != payload["campaign_id"]
        or ticket["mode"] != payload["mode"]
        or ticket["search_mode"] != payload["search_mode"]
        or ticket["deadline"] != payload["deadline"]
        or ticket["run_dir"] != str(run_dir)
    ):
        raise TrancheError(f"{phase} launch authorization manifest contract mismatch")
    created = _parse_time(ticket["created_utc"], f"{phase} authorization created_utc")
    expires = _parse_time(ticket["expires_utc"], f"{phase} authorization expires_utc")
    if (
        ticket["expires_utc"] != lock["authorization_expires_utc"]
        or not created <= launch_claimed < expires
        or expires - created > timedelta(minutes=5)
        or expires > manifest_lib.parse_deadline(payload["deadline"])
    ):
        raise TrancheError(f"{phase} launch authorization chronology mismatch")
    if phase == "MAIN":
        if (
            ticket["public_status_path"] != str(PUBLIC_STATUS_PATH.resolve())
            or ticket["public_status_sha256"] != expected_public_status_sha256
            or expected_public_status_sha256 is None
        ):
            raise TrancheError("MAIN launch authorization public-status pin mismatch")
    elif (
        ticket["public_status_path"] is not None
        or ticket["public_status_sha256"] is not None
        or expected_public_status_sha256 is not None
    ):
        raise TrancheError(f"{phase} pilot authorization carries public-status data")
    return ticket
def _inventory_digest(inventory: Mapping[str, str], root: Path, path: Path, expected: str, name: str) -> None:
    try:
        relative = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise TrancheError(f"{name} is outside its run directory") from exc
    if inventory.get(relative) != expected:
        raise TrancheError(f"{name} differs from the pinned run inventory")

def _validate_verified_chronology(
    *,
    launch_claimed: datetime,
    candidate_observed: datetime,
    verified_time: datetime,
    finished: datetime,
    candidate_deadline: datetime,
    name: str,
) -> None:
    if not (
        launch_claimed <= candidate_observed < candidate_deadline
        and candidate_observed <= verified_time <= finished
    ):
        raise TrancheError(f"{name} candidate/verification chronology is invalid")


def _validate_terminal_lane_state(
    *,
    payload: Mapping[str, Any],
    lanes_state: Mapping[str, Any],
    lane_statuses: Mapping[str, Any],
    name: str,
) -> None:
    expected_ids = {str(index) for index in range(64)}
    if not isinstance(lanes_state, dict) or set(lanes_state) != expected_ids:
        raise TrancheError(f"{name} final lane state identities mismatch")
    if not isinstance(lane_statuses, dict) or set(lane_statuses) != expected_ids:
        raise TrancheError(f"{name} summary lane identities mismatch")
    lanes_by_id = {str(lane["lane_id"]): lane for lane in payload["lanes"]}
    if set(lanes_by_id) != expected_ids:
        raise TrancheError(f"{name} manifest lane identities mismatch")
    for lane_id, raw_lane_state in lanes_state.items():
        lane_state = _require_keys(
            raw_lane_state,
            {"status", "pid", "assigned_specializations"},
            f"{name} lane {lane_id}",
        )
        assigned = len(lanes_by_id[lane_id]["specializations"])
        if (
            lane_state["pid"] is not None
            or lane_state["status"] != lane_statuses[lane_id]
            or lane_state["assigned_specializations"] != assigned
        ):
            raise TrancheError(f"{name} lane {lane_id} terminal mismatch")
        if assigned == 0 and lane_statuses[lane_id] != "NO_WORK":
            raise TrancheError(f"{name} unassigned lane {lane_id} is not NO_WORK")


def _validate_result_lane_binding(
    *,
    lane_id: int,
    lane_status: str,
    result_status: str,
    name: str,
) -> None:
    expected = {
        "NO_HIT": "NO_HIT",
        "HIT": "VERIFIED_HIT",
        "TIMEOUT_INCOMPLETE": "TIMEOUT_INCOMPLETE",
    }.get(result_status)
    if expected is None or lane_status != expected:
        raise TrancheError(
            f"{name} lane {lane_id} result/status binding mismatch"
        )

def _validate_verified_hit(record: Any) -> dict[str, Any]:
    hit = dict(_require_keys(
        record,
        {
            "integer_quadruple", "scalar_report", "independent_report", "lane_id",
            "candidate_index", "candidate_observed_utc", "verified_utc",
        },
        "verified hit",
    ))
    lane_id = _strict_int(hit["lane_id"], "verified hit lane", 0)
    if lane_id >= 64:
        raise TrancheError("verified hit lane is outside 0..63")
    candidate_index = _strict_int(
        hit["candidate_index"], "verified hit candidate index", 0
    )
    if candidate_index != 0:
        raise TrancheError("verified hit candidate index must be zero")
    observed = _parse_time(hit["candidate_observed_utc"], "candidate observed time")
    verified_time = _parse_time(hit["verified_utc"], "verified hit time")
    if observed > verified_time:
        raise TrancheError("verified hit predates its candidate observation")
    raw = hit["integer_quadruple"]
    if not isinstance(raw, list) or len(raw) != 4 or any(
        not isinstance(token, str) or re.fullmatch(r"[1-9][0-9]*", token) is None
        for token in raw
    ):
        raise TrancheError("verified integer quadruple is malformed")
    a, b, c, d = (int(token) for token in raw)
    left_terms = [a**5, b**5]
    right_terms = [c**5, d**5]
    left_sum = sum(left_terms)
    right_sum = sum(right_terms)
    if left_sum != right_sum or set((a, b)).intersection((c, d)):
        raise TrancheError("verified hit fails direct exact arithmetic")

    scalar = _require_keys(
        hit["scalar_report"],
        {
            "schema_version", "verifier", "valid", "checks", "errors",
            "certificate", "left_terms", "right_terms", "left_sum",
            "right_sum", "difference", "cross_collisions", "primitive_gcd",
        },
        "scalar verifier report",
    )
    expected_scalar = {
        "schema_version": 1,
        "verifier": "quintic_taxicab_exact_python",
        "valid": True,
        "checks": {
            "positive_integers": True,
            "fifth_power_equality": True,
            "cross_disjoint": True,
        },
        "errors": [],
        "certificate": {"a": a, "b": b, "c": c, "d": d},
        "left_terms": left_terms,
        "right_terms": right_terms,
        "left_sum": left_sum,
        "right_sum": right_sum,
        "difference": 0,
        "cross_collisions": [],
        "primitive_gcd": math.gcd(a, b, c, d),
    }
    if scalar != expected_scalar or scalar["primitive_gcd"] != 1:
        raise TrancheError("scalar verifier report does not exactly verify the primitive hit")

    native = _require_keys(
        hit["independent_report"],
        {"valid", "code", "checks", "primitive", "common_gcd", "left_sum", "right_sum"},
        "independent verifier report",
    )
    expected_native = {
        "valid": True,
        "code": "VERIFIED",
        "checks": {"positive": True, "fifth_power_equal": True, "cross_disjoint": True},
        "primitive": True,
        "common_gcd": "1",
        "left_sum": str(left_sum),
        "right_sum": str(right_sum),
    }
    if native != expected_native:
        raise TrancheError("independent verifier report does not exactly verify the primitive hit")
    return hit



def _validate_q5_manifest_contract(
    payload: Mapping[str, Any],
    plan: Mapping[str, Any],
    lane_config_dir: Path,
) -> None:
    if payload["worker_kind"] != "native":
        raise TrancheError("Q5 campaign must use the native worker")
    expected_paths = MANIFEST_ARTIFACT_PATHS
    artifacts = payload["artifacts"]
    if set(artifacts) != set(expected_paths):
        raise TrancheError("Q5 artifact role set mismatch")
    frozen = plan["frozen_artifact_hashes"]
    for role, raw_path in expected_paths.items():
        path = raw_path.resolve()
        record = artifacts[role]
        if record["path"] != str(path):
            raise TrancheError(f"Q5 artifact path mismatch: {role}")
        if record["sha256"] != frozen.get(str(path)):
            raise TrancheError(f"Q5 artifact hash differs from the T0 pin: {role}")
    expected_dir = lane_config_dir.resolve()
    for expected_lane, lane in enumerate(payload["lanes"]):
        expected_path = expected_dir / f"lane_{expected_lane:02d}.tsv"
        if Path(lane["lane_file"]["path"]).resolve() != expected_path:
            raise TrancheError(
                f"lane {expected_lane} file is outside the fixed lane directory"
            )
def _validate_pilot_evidence(
    pilot: str,
    state: Mapping[str, Any],
    plan: Mapping[str, Any],
    clock: Clock,
    census_hook: CensusHook | None,
) -> tuple[dict[str, Any], bool]:
    spec = PILOT_SPECS[pilot]
    acceptance_now = _aware_utc(clock(), "pilot acceptance clock")
    manifest_path = spec["manifest_path"].resolve()
    manifest_before, manifest_file_sha256 = _load_json_with_sha(manifest_path, missing_ready=True)
    try:
        envelope = manifest_lib.audit_manifest(
            manifest_path,
            expected_campaign_id=spec["campaign_id"],
        )
    except FileNotFoundError as exc:
        raise TrancheNotReady(f"pilot {pilot} manifest is not present") from exc
    except manifest_lib.ManifestError as exc:
        if not manifest_path.exists():
            raise TrancheNotReady(f"pilot {pilot} manifest is not present") from exc
        raise TrancheError(f"pilot {pilot} manifest audit failed: {exc}") from exc
    manifest_after, manifest_file_sha256_after = _load_json_with_sha(manifest_path)
    if (
        manifest_before != envelope
        or manifest_after != envelope
        or manifest_file_sha256_after != manifest_file_sha256
    ):
        raise TrancheError(f"pilot {pilot} manifest changed during audit")
    payload = envelope["payload"]
    digest = envelope["payload_sha256"]
    if payload["mode"] != "CALIBRATION_ONLY":
        raise TrancheError(f"pilot {pilot} is not CALIBRATION_ONLY")
    if payload["search_mode"] != spec["search_mode"] or payload["bounds"] != spec["bounds"]:
        raise TrancheError(f"pilot {pilot} frozen search contract mismatch")
    if payload["manifest_path"] != str(manifest_path) or payload["run_dir"] != str(spec["run_dir"].resolve()):
        raise TrancheError(f"pilot {pilot} fixed path mismatch")
    _validate_q5_manifest_contract(payload, plan, spec["lane_config_dir"])
    created = manifest_lib.parse_deadline(payload["created_utc"])
    deadline = manifest_lib.parse_deadline(payload["deadline"])
    s = _parse_time(state["s"], "S")
    previous_finished = _pilot_previous_finished(state, pilot)
    if created < previous_finished:
        raise TrancheError(f"pilot {pilot} was created before the previous stage finished")
    if deadline > min(created + timedelta(seconds=spec["limit_seconds"]), s):
        raise TrancheError(f"pilot {pilot} deadline exceeds its local/S limit")

    run_dir = spec["run_dir"].resolve()
    summary_path = run_dir / "supervisor_summary.json"
    final_state_path = run_dir / "supervisor_state.json"
    summary, summary_sha256 = _load_json_with_sha(summary_path, missing_ready=True)
    final_state, final_state_sha256 = _load_json_with_sha(
        final_state_path, missing_ready=True
    )
    summary = dict(_require_keys(
        summary,
        {
            "schema_version", "kind", "campaign_id", "manifest_path",
            "manifest_payload_sha256", "status", "finished_utc", "owned_pids",
            "spawned_lane_ids", "verified_hit", "lane_statuses",
        },
        f"pilot {pilot} summary",
    ))
    final_state = dict(_require_keys(
        final_state,
        {
            "schema_version", "kind", "campaign_id", "manifest_payload_sha256",
            "status", "updated_utc", "supervisor_pid", "owned_pids",
            "spawned_lane_ids", "lanes", "anomaly",
        },
        f"pilot {pilot} final state",
    ))
    if summary["schema_version"] != 1 or summary["kind"] != "Q5_TORSOR_SUPERVISOR_SUMMARY":
        raise TrancheError(f"pilot {pilot} summary schema mismatch")
    if final_state["schema_version"] != 1 or final_state["kind"] != "Q5_TORSOR_SUPERVISOR_STATE":
        raise TrancheError(f"pilot {pilot} state schema mismatch")
    for value, name in ((summary, "summary"), (final_state, "state")):
        if value["campaign_id"] != spec["campaign_id"] or value["manifest_payload_sha256"] != digest:
            raise TrancheError(f"pilot {pilot} {name} identity mismatch")
        if value["owned_pids"] != []:
            raise TrancheError(f"pilot {pilot} {name} retains owned PIDs")
    if summary["manifest_path"] != str(manifest_path):
        raise TrancheError(f"pilot {pilot} summary manifest path mismatch")
    if final_state["anomaly"] is not None:
        raise TrancheError(f"pilot {pilot} state contains an anomaly")
    if final_state["status"] != summary["status"]:
        raise TrancheError(f"pilot {pilot} state/summary status mismatch")
    finished = _parse_time(summary["finished_utc"], f"pilot {pilot} finish")
    final_updated = _parse_time(final_state["updated_utc"], f"pilot {pilot} state update")

    launch_lock_path = run_dir / "launch.lock"
    launch_lock_raw, launch_lock_sha256 = _load_json_with_sha(
        launch_lock_path, missing_ready=True
    )
    launch_lock = _validate_launch_lock_value(
        launch_lock_raw, payload, digest, name=f"pilot {pilot} launch lock",
        expected_readiness_sha256=plan["launch_readiness"]["file_sha256"],
    )
    if launch_lock["supervisor_pid"] != final_state["supervisor_pid"]:
        raise TrancheError(f"pilot {pilot} supervisor PID identity mismatch")
    launch_claimed = _parse_time(launch_lock["claimed_utc"], f"pilot {pilot} launch claim")
    authorization_state, authorization_state_sha256 = _load_json_with_sha(STATE_PATH)
    if authorization_state != state:
        raise TrancheError(f"pilot {pilot} authorization state changed before acceptance")
    authorization_ticket = _validate_authorization_ticket(
        phase=pilot,
        lock=launch_lock,
        payload=payload,
        payload_digest=digest,
        manifest_path=manifest_path,
        manifest_file_sha256=manifest_file_sha256,
        run_dir=run_dir,
        plan=plan,
        launch_claimed=launch_claimed,
        expected_public_status_sha256=None,
        expected_state_sha256=authorization_state_sha256,
    )
    if not (
        previous_finished <= created <= launch_claimed
        <= finished <= final_updated <= acceptance_now
    ):
        raise TrancheError(f"pilot {pilot} chronology is not monotone")
    if final_updated > _parse_time(state["g"], "G"):
        raise TrancheError(f"pilot {pilot} final state was updated after G")


    lanes_state = final_state["lanes"]
    lane_statuses = summary["lane_statuses"]
    _validate_terminal_lane_state(
        payload=payload, lanes_state=lanes_state, lane_statuses=lane_statuses,
        name=f"pilot {pilot}",
    )
    spawned_lane_ids = _validate_spawned_lane_ids(
        summary=summary, final_state=final_state, payload=payload,
        lane_statuses=lane_statuses, name=f"pilot {pilot}",
    )

    hit: dict[str, Any] | None = None
    verified_artifact_path: Path | None = None
    verified_artifact_sha256: str | None = None
    verified = summary["status"] == "VERIFIED_HIT"
    if not verified and finished >= min(deadline, s):
        raise TrancheError(f"pilot {pilot} FINITE_NO_HIT was observed at/after its deadline/S")
    if verified:
        if (
            list(lane_statuses.values()).count("VERIFIED_HIT") != 1
            or not set(lane_statuses.values()).issubset(
                {"NO_HIT", "NO_WORK", "VERIFIED_HIT", "STOPPED_AFTER_VERIFIED_HIT"}
            )
        ):
            raise TrancheError(
                f"pilot {pilot} verified lane statuses are inadmissible")
        hit = _validate_verified_hit(summary["verified_hit"])
        if lane_statuses.get(str(hit["lane_id"])) != "VERIFIED_HIT":
            raise TrancheError(f"pilot {pilot} verified-hit lane status mismatch")
        verified_time = _parse_time(hit["verified_utc"], f"pilot {pilot} verified time")
        candidate_observed = _parse_time(
            hit["candidate_observed_utc"], f"pilot {pilot} candidate observation"
        )
        _validate_verified_chronology(
            launch_claimed=launch_claimed,
            candidate_observed=candidate_observed,
            verified_time=verified_time,
            finished=finished,
            candidate_deadline=min(deadline, s),
            name=f"pilot {pilot}",
        )
        verified_artifact_path = run_dir / (
            f"lane_{hit['lane_id']:02d}.candidate_{hit['candidate_index']:03d}.verified.json"
        )
        verified_paths = sorted(run_dir.glob("lane_*.candidate_*.verified.json"))
        if verified_paths != [verified_artifact_path]:
            raise TrancheError(f"pilot {pilot} verified-artifact set mismatch")
        verified_value, verified_artifact_sha256 = _load_json_with_sha(
            verified_artifact_path, missing_ready=True
        )
        if verified_value != hit:
            raise TrancheError(f"pilot {pilot} verified artifact differs from the summary")
    else:
        if summary["status"] not in {"FINITE_NO_HIT", "RUNNING", "STARTING"}:
            raise TrancheError(f"pilot {pilot} terminal status is fail-closed: {summary['status']}")
        if summary["status"] != "FINITE_NO_HIT":
            raise TrancheNotReady(f"pilot {pilot} has not reached FINITE_NO_HIT")
        if summary["verified_hit"] is not None:
            raise TrancheError(f"pilot {pilot} NO_HIT summary carries a verified hit")
        expected_no_work = spec["expected_no_work"]
        counts = {
            key: list(lane_statuses.values()).count(key)
            for key in set(lane_statuses.values())
        }
        expected_counts = {"NO_HIT": 64 - expected_no_work}
        if expected_no_work:
            expected_counts["NO_WORK"] = expected_no_work
        if counts != expected_counts:
            raise TrancheError(f"pilot {pilot} exact terminal lane counts mismatch: {counts}")
        if list(run_dir.glob("lane_*.candidate_*.verified.json")):
            raise TrancheError(
                f"pilot {pilot} FINITE_NO_HIT carries a verified-candidate artifact")

    result_hashes: dict[str, str] = {}
    timing_rows: list[dict[str, Any]] = []
    validated_hit_lanes = 0
    for lane in payload["lanes"]:
        lane_id = lane["lane_id"]
        nonempty = bool(lane["specializations"])
        result_path = Path(lane["result_path"])
        stderr_path = run_dir / f"lane_{lane_id:02d}.stderr.txt"
        if not nonempty:
            if lane_statuses[str(lane_id)] != "NO_WORK" or result_path.exists():
                raise TrancheError(
                    f"pilot {pilot} unassigned lane {lane_id} has terminal artifacts"
                )
            continue
        if nonempty and not stderr_path.is_file():
            raise TrancheError(f"pilot {pilot} lane {lane_id} stderr artifact is missing")
        if stderr_path.exists() and stderr_path.stat().st_size != 0:
            raise TrancheError(f"pilot {pilot} lane {lane_id} emitted stderr")
        if not result_path.exists():
            if verified and lane_statuses[str(lane_id)] == "STOPPED_AFTER_VERIFIED_HIT":
                continue
            if nonempty:
                raise TrancheError(f"pilot {pilot} lane {lane_id} result is missing")
            continue
        result_value, result_sha256 = _load_json_with_sha(result_path)
        result = supervisor_lib.validate_lane_result(
            result_value, payload=payload, payload_digest=digest, lane=lane
        )
        result_hashes[str(lane_id)] = result_sha256
        result_status = result["status"]
        _validate_result_lane_binding(
            lane_id=lane_id,
            lane_status=lane_statuses[str(lane_id)],
            result_status=result_status,
            name=f"pilot {pilot}",
        )
        if verified and result_status == "HIT":
            if lane_id != summary["verified_hit"]["lane_id"]:
                raise TrancheError(f"pilot {pilot} HIT result lane mismatch")
            candidates = result["candidates"]
            if (
                len(candidates) != 1
                or candidates[0].get("integer_quadruple")
                != summary["verified_hit"]["integer_quadruple"]
            ):
                raise TrancheError(
                    f"pilot {pilot} HIT result must contain exactly the verified candidate"
                )
            validated_hit_lanes += 1
        elif result_status != "NO_HIT":
            raise TrancheError(f"pilot {pilot} lane {lane_id} result is not terminal evidence")
        elapsed = int(result["elapsed_milliseconds"], 10)
        if pilot in {"B", "C", "D"} and elapsed <= 0:
            raise TrancheError(f"pilot {pilot} lane {lane_id} elapsed time is not positive")
        timing_rows.append(
            {"lane_id": lane_id, "elapsed_milliseconds": elapsed, "weight": lane["estimated_weight"]}
        )
    if verified and validated_hit_lanes != 1:
        raise TrancheError(
            f"pilot {pilot} must contain exactly one validated HIT result"
        )
    actual_result_paths = {
        path.resolve() for path in run_dir.glob("lane_*.result.json")
    }
    expected_result_paths = {
        Path(lane["result_path"]).resolve()
        for lane in payload["lanes"]
        if str(lane["lane_id"]) in result_hashes
    }
    if actual_result_paths != expected_result_paths:
        raise TrancheError(f"pilot {pilot} result artifact set mismatch")
    for stderr_path in run_dir.glob("*.stderr.txt"):
        if stderr_path.stat().st_size != 0:
            raise TrancheError(f"pilot {pilot} has nonempty stderr: {stderr_path}")
    result_paths = {
        lane["lane_id"]: Path(lane["result_path"])
        for lane in payload["lanes"]
        if str(lane["lane_id"]) in result_hashes
    }
    run_inventory, stdout_sha256, stderr_sha256 = _validate_exact_run_inventory(
        run_dir=run_dir,
        spawned_lane_ids=spawned_lane_ids,
        result_paths=result_paths,
        verified_artifact_path=verified_artifact_path,
        name=f"pilot {pilot}",
    )
    for artifact_path, artifact_sha256, artifact_name in (
        (summary_path, summary_sha256, f"pilot {pilot} summary"),
        (final_state_path, final_state_sha256, f"pilot {pilot} final state"),
        (launch_lock_path, launch_lock_sha256, f"pilot {pilot} launch lock"),
    ):
        _inventory_digest(run_inventory, run_dir, artifact_path, artifact_sha256, artifact_name)
    for lane in payload["lanes"]:
        lane_key = str(lane["lane_id"])
        if lane_key in result_hashes:
            _inventory_digest(
                run_inventory, run_dir, Path(lane["result_path"]),
                result_hashes[lane_key], f"pilot {pilot} lane {lane_key} result",
            )
    if verified_artifact_path is not None and verified_artifact_sha256 is not None:
        _inventory_digest(
            run_inventory, run_dir, verified_artifact_path,
            verified_artifact_sha256, f"pilot {pilot} verified artifact",
        )
    _current_clean_census(plan, clock, census_hook)

    evidence = {
        "pilot": pilot,
        "campaign_id": spec["campaign_id"],
        "manifest_path": str(manifest_path),
        "manifest_payload_sha256": digest,
        "manifest_file_sha256": manifest_file_sha256,
        "summary_path": str(summary_path),
        "summary_sha256": summary_sha256,
        "final_state_path": str(final_state_path),
        "final_state_sha256": final_state_sha256,
        "launch_lock_sha256": launch_lock_sha256,
        "run_inventory": run_inventory,
        "authorization_state_sha256": authorization_ticket["state_sha256"],
        "result_sha256": result_hashes,
        "spawned_lane_ids": sorted(spawned_lane_ids),
        "stdout_sha256": stdout_sha256,
        "stderr_sha256": stderr_sha256,
        "verified_artifact_path": str(verified_artifact_path) if verified_artifact_path else None,
        "verified_artifact_sha256": verified_artifact_sha256,
        "finished_utc": summary["finished_utc"],
        "timing_rows": timing_rows,
        "verified_hit": summary["verified_hit"],
    }
    return evidence, verified


def _accept_pilot_action(
    commit: Callable[..., dict[str, Any]],
    fail_closed: Callable[..., dict[str, Any]],
    pilot: str,
) -> dict[str, Any]:
    clock = _now_utc
    census_hook: CensusHook | None = None
    lock, plan, state = _load_context()
    expected_phase = f"READY_{pilot}"
    if state["phase"] != expected_phase:
        raise PermanentFailure(f"pilot {pilot} cannot be accepted from phase {state['phase']}")
    now = _aware_utc(clock(), "clock")
    try:
        _validate_transition_clock(state, now, lock)
        evidence, verified = _validate_pilot_evidence(
            pilot, state, plan, clock, census_hook
        )
        commit_now = _aware_utc(clock(), "pilot commit clock")
        _validate_transition_clock(state, commit_now, lock)
        committed_evidence, committed_verified = _validate_pilot_evidence(
            pilot, state, plan, clock, census_hook
        )
        if committed_evidence != evidence or committed_verified is not verified:
            raise TrancheError(
                f"pilot {pilot} terminal evidence changed before commit"
            )
    except TrancheNotReady:
        raise
    except BaseException as exc:
        fail_closed(state, exc, now)
        raise PermanentFailure(f"pilot {pilot} validation failed permanently: {exc}") from exc
    accepted = copy.deepcopy(state["accepted_pilots"])
    accepted[pilot] = evidence
    if verified:
        next_phase = "VERIFIED_HIT"
        updates = {"accepted_pilots": accepted, "verified_hit": _pilot_hit_binding(pilot, evidence)}
    else:
        index = PILOT_ORDER.index(pilot)
        next_phase = "READY_SELECTION" if index == len(PILOT_ORDER) - 1 else f"READY_{PILOT_ORDER[index + 1]}"
        updates = {"accepted_pilots": accepted}
    new_state = commit(state, phase=next_phase, now=commit_now, updates=updates)
    return {"ok": True, "phase": new_state["phase"], "accepted_pilot": pilot}


def _revalidate_accepted_artifacts_legacy(state: Mapping[str, Any]) -> None:
    for pilot in PILOT_ORDER:
        evidence = state["accepted_pilots"].get(pilot)
        if evidence is None:
            continue
        if not isinstance(evidence, dict):
            raise PermanentFailure(f"accepted pilot {pilot} evidence is malformed")
        spec = PILOT_SPECS[pilot]
        manifest_path = spec["manifest_path"].resolve()
        summary_path = spec["run_dir"].resolve() / "supervisor_summary.json"
        final_state_path = spec["run_dir"].resolve() / "supervisor_state.json"
        launch_lock_path = spec["run_dir"].resolve() / "launch.lock"
        fixed = {
            "manifest_path": (manifest_path, "manifest_file_sha256"),
            "summary_path": (summary_path, "summary_sha256"),
            "final_state_path": (final_state_path, "final_state_sha256"),
        }
        for path_field, (path, hash_field) in fixed.items():
            if evidence.get(path_field) != str(path):
                raise PermanentFailure(f"accepted pilot {pilot} {path_field} drift")
            if _sha256_file(path) != evidence.get(hash_field):
                raise PermanentFailure(f"accepted pilot {pilot} {hash_field} drift")
        if _sha256_file(launch_lock_path) != evidence.get("launch_lock_sha256"):
            raise PermanentFailure(f"accepted pilot {pilot} launch-lock drift")
        try:
            envelope = manifest_lib.audit_manifest(
                manifest_path,
                expected_digest=evidence.get("manifest_payload_sha256"),
                expected_campaign_id=spec["campaign_id"],
            )
        except manifest_lib.ManifestError as exc:
            raise PermanentFailure(f"accepted pilot {pilot} manifest drift: {exc}") from exc
        verified_hit = evidence.get("verified_hit")
        verified_paths = sorted(spec["run_dir"].resolve().glob("lane_*.candidate_*.verified.json"))
        if verified_hit is None:
            if evidence.get("verified_artifact_path") is not None or evidence.get("verified_artifact_sha256") is not None:
                raise PermanentFailure(f"accepted pilot {pilot} carries a stray verified-artifact pin")
            if verified_paths:
                raise PermanentFailure(f"accepted pilot {pilot} acquired a verified artifact")
        else:
            hit = _validate_verified_hit(verified_hit)
            expected_verified_path = spec["run_dir"].resolve() / (
                f"lane_{hit['lane_id']:02d}.candidate_{hit['candidate_index']:03d}.verified.json"
            )
            if evidence.get("verified_artifact_path") != str(expected_verified_path):
                raise PermanentFailure(f"accepted pilot {pilot} verified-artifact path drift")
            if verified_paths != [expected_verified_path]:
                raise PermanentFailure(f"accepted pilot {pilot} verified-artifact set drift")
            if _load_json(expected_verified_path) != hit:
                raise PermanentFailure(f"accepted pilot {pilot} verified-artifact content drift")
            if _sha256_file(expected_verified_path) != evidence.get("verified_artifact_sha256"):
                raise PermanentFailure(f"accepted pilot {pilot} verified-artifact hash drift")
        result_hashes = evidence.get("result_sha256")
        if not isinstance(result_hashes, dict):
            raise PermanentFailure(f"accepted pilot {pilot} result hashes are malformed")
        payload_result_ids = {
            str(lane["lane_id"])
            for lane in envelope["payload"]["lanes"]
            if lane["specializations"]
        }
        if verified_hit is None:
            expected_result_ids = payload_result_ids
        else:
            expected_result_ids = {
                str(lane["lane_id"])
                for lane in envelope["payload"]["lanes"]
                if lane["specializations"] and Path(lane["result_path"]).is_file()
            }
            if str(verified_hit["lane_id"]) not in expected_result_ids:
                raise PermanentFailure(f"accepted pilot {pilot} lost its HIT lane result")
        if set(result_hashes) != expected_result_ids:
            raise PermanentFailure(f"accepted pilot {pilot} result set drift")
        for lane in envelope["payload"]["lanes"]:
            lane_id = str(lane["lane_id"])
            if lane_id in expected_result_ids:
                if _sha256_file(Path(lane["result_path"])) != result_hashes[lane_id]:
                    raise PermanentFailure(
                        f"accepted pilot {pilot} lane {lane_id} result drift"
                    )



PILOT_EVIDENCE_KEYS = {
    "pilot", "campaign_id", "manifest_path", "manifest_payload_sha256",
    "manifest_file_sha256", "summary_path", "summary_sha256",
    "final_state_path", "final_state_sha256", "launch_lock_sha256",
    "run_inventory", "authorization_state_sha256", "result_sha256",
    "spawned_lane_ids", "stdout_sha256", "stderr_sha256",
    "verified_artifact_path",
    "verified_artifact_sha256", "finished_utc", "timing_rows", "verified_hit",
}


def _revalidate_accepted_artifacts(
    state: Mapping[str, Any], plan: Mapping[str, Any]
) -> None:
    for pilot in PILOT_ORDER:
        raw_evidence = state["accepted_pilots"].get(pilot)
        if raw_evidence is None:
            continue
        evidence = dict(_require_keys(raw_evidence, PILOT_EVIDENCE_KEYS, f"accepted pilot {pilot}"))
        spec = PILOT_SPECS[pilot]
        run_dir = spec["run_dir"].resolve()
        manifest_path = spec["manifest_path"].resolve()
        if evidence["pilot"] != pilot or evidence["campaign_id"] != spec["campaign_id"]:
            raise PermanentFailure(f"accepted pilot {pilot} identity drift")
        if evidence["manifest_path"] != str(manifest_path):
            raise PermanentFailure(f"accepted pilot {pilot} manifest path drift")

        manifest_value, manifest_sha256 = _load_json_with_sha(manifest_path)
        if manifest_sha256 != evidence["manifest_file_sha256"]:
            raise PermanentFailure(f"accepted pilot {pilot} manifest hash drift")
        try:
            envelope = manifest_lib.audit_manifest(
                manifest_path, expected_digest=evidence["manifest_payload_sha256"],
                expected_campaign_id=spec["campaign_id"],
            )
        except manifest_lib.ManifestError as exc:
            raise PermanentFailure(f"accepted pilot {pilot} manifest drift: {exc}") from exc
        manifest_after, manifest_sha256_after = _load_json_with_sha(manifest_path)
        if (
            manifest_value != envelope or manifest_after != envelope
            or manifest_sha256_after != manifest_sha256
        ):
            raise PermanentFailure(f"accepted pilot {pilot} manifest changed during audit")
        payload = envelope["payload"]

        pinned_inventory = evidence["run_inventory"]
        if (
            not isinstance(pinned_inventory, dict)
            or any(
                not isinstance(name, str) or not isinstance(digest, str)
                or SHA256_RE.fullmatch(digest) is None
                for name, digest in pinned_inventory.items()
            )
            or _inventory(run_dir) != pinned_inventory
        ):
            raise PermanentFailure(f"accepted pilot {pilot} run inventory drift")

        summary_path = run_dir / "supervisor_summary.json"
        final_state_path = run_dir / "supervisor_state.json"
        launch_lock_path = run_dir / "launch.lock"
        summary, summary_sha256 = _load_json_with_sha(summary_path)
        final_state, final_state_sha256 = _load_json_with_sha(final_state_path)
        launch_raw, launch_sha256 = _load_json_with_sha(launch_lock_path)
        if (
            evidence["summary_path"] != str(summary_path)
            or evidence["summary_sha256"] != summary_sha256
            or evidence["final_state_path"] != str(final_state_path)
            or evidence["final_state_sha256"] != final_state_sha256
            or evidence["launch_lock_sha256"] != launch_sha256
        ):
            raise PermanentFailure(f"accepted pilot {pilot} terminal JSON hash drift")
        launch = _validate_launch_lock_value(
            launch_raw, payload, envelope["payload_sha256"],
            name=f"accepted pilot {pilot} launch lock",
            expected_readiness_sha256=plan["launch_readiness"]["file_sha256"],
        )
        _validate_authorization_ticket(
            phase=pilot,
            lock=launch,
            payload=payload,
            payload_digest=envelope["payload_sha256"],
            manifest_path=manifest_path,
            manifest_file_sha256=evidence["manifest_file_sha256"],
            run_dir=run_dir,
            plan=plan,
            launch_claimed=_parse_time(launch["claimed_utc"], "launch claim"),
            expected_public_status_sha256=None,
            expected_state_sha256=evidence["authorization_state_sha256"],
        )
        if (
            summary.get("campaign_id") != spec["campaign_id"]
            or summary.get("manifest_payload_sha256") != envelope["payload_sha256"]
            or summary.get("finished_utc") != evidence["finished_utc"]
            or summary.get("verified_hit") != evidence["verified_hit"]
            or final_state.get("campaign_id") != spec["campaign_id"]
            or final_state.get("manifest_payload_sha256") != envelope["payload_sha256"]
            or final_state.get("status") != summary.get("status")
            or final_state.get("anomaly") is not None
            or summary.get("owned_pids") != []
            or final_state.get("owned_pids") != []
            or launch["supervisor_pid"] != final_state.get("supervisor_pid")
        ):
            raise PermanentFailure(f"accepted pilot {pilot} terminal semantics drift")

        lanes_state = final_state.get("lanes")
        lane_statuses = summary.get("lane_statuses")
        _validate_terminal_lane_state(
            payload=payload, lanes_state=lanes_state,
            lane_statuses=lane_statuses, name=f"accepted pilot {pilot}",
        )
        try:
            spawned_lane_ids = _validate_spawned_lane_ids(
                summary=summary, final_state=final_state, payload=payload,
                lane_statuses=lane_statuses, name=f"accepted pilot {pilot}",
            )
        except TrancheError as exc:
            raise PermanentFailure(
                f"accepted pilot {pilot} spawned-lane provenance drift"
            ) from exc
        if evidence["spawned_lane_ids"] != sorted(spawned_lane_ids):
            raise PermanentFailure(
                f"accepted pilot {pilot} spawned-lane pin drift"
            )
        assigned_lanes = {
            str(lane["lane_id"]): lane
            for lane in payload["lanes"] if lane["specializations"]
        }
        assigned_ids = set(assigned_lanes)
        no_work = 64 - len(assigned_ids)
        status = summary.get("status")
        verified_hit_record = summary.get("verified_hit")
        if status == "FINITE_NO_HIT":
            expected_counts = {"NO_HIT": len(assigned_ids)}
            if no_work:
                expected_counts["NO_WORK"] = no_work
            actual_counts = {
                value: list(lane_statuses.values()).count(value)
                for value in set(lane_statuses.values())
            }
            if actual_counts != expected_counts or verified_hit_record is not None:
                raise PermanentFailure(
                    f"accepted pilot {pilot} finite lane contract drift")
            expected_result_ids = assigned_ids
        elif status == "VERIFIED_HIT":
            if (
                verified_hit_record is None
                or list(lane_statuses.values()).count("VERIFIED_HIT") != 1
                or not set(lane_statuses.values()).issubset(
                    {"NO_HIT", "NO_WORK", "VERIFIED_HIT",
                     "STOPPED_AFTER_VERIFIED_HIT"}
                )
            ):
                raise PermanentFailure(
                    f"accepted pilot {pilot} verified lane contract drift")
            hit_lane = str(_validate_verified_hit(verified_hit_record)["lane_id"])
            if lane_statuses[hit_lane] != "VERIFIED_HIT":
                raise PermanentFailure(
                    f"accepted pilot {pilot} verified lane identity drift")
            expected_result_ids = assigned_ids - {
                lane_id for lane_id in assigned_ids
                if lane_statuses[lane_id] == "STOPPED_AFTER_VERIFIED_HIT"
            }
        else:
            raise PermanentFailure(
                f"accepted pilot {pilot} terminal status drift")

        result_hashes = evidence["result_sha256"]
        if (
            not isinstance(result_hashes, dict)
            or set(result_hashes) != expected_result_ids
            or any(
                not isinstance(value, str)
                or SHA256_RE.fullmatch(value) is None
                for value in result_hashes.values()
            )
        ):
            raise PermanentFailure(
                f"accepted pilot {pilot} result hashes are malformed")
        expected_timing: list[dict[str, Any]] = []
        validated_hit_lanes = 0
        for lane in payload["lanes"]:
            lane_key = str(lane["lane_id"])
            result_path = Path(lane["result_path"])
            if lane_key not in assigned_ids:
                if result_path.exists():
                    raise PermanentFailure(
                        f"accepted pilot {pilot} NO_WORK lane acquired a result")
                continue
            if lane_key not in result_hashes:
                continue
            result_value, result_sha256 = _load_json_with_sha(result_path)
            if result_sha256 != result_hashes[lane_key]:
                raise PermanentFailure(
                    f"accepted pilot {pilot} lane {lane_key} result drift")
            result = supervisor_lib.validate_lane_result(
                result_value, payload=payload,
                payload_digest=envelope["payload_sha256"], lane=lane,
            )
            _validate_result_lane_binding(
                lane_id=lane["lane_id"], lane_status=lane_statuses[lane_key],
                result_status=result["status"], name=f"accepted pilot {pilot}",
            )
            if result["status"] == "HIT":
                if (
                    status != "VERIFIED_HIT"
                    or lane["lane_id"] != verified_hit_record["lane_id"]
                ):
                    raise PermanentFailure(
                        f"accepted pilot {pilot} HIT lane drift")
                candidates = result["candidates"]
                if (
                    len(candidates) != 1
                    or candidates[0].get("integer_quadruple")
                    != verified_hit_record["integer_quadruple"]
                ):
                    raise PermanentFailure(
                        f"accepted pilot {pilot} HIT candidate set drift"
                    )
                validated_hit_lanes += 1
            elif status == "VERIFIED_HIT" and result["status"] != "NO_HIT":
                raise PermanentFailure(f"accepted pilot {pilot} verified peer result drift")
            expected_timing.append({
                "lane_id": lane["lane_id"],
                "elapsed_milliseconds": int(result["elapsed_milliseconds"], 10),
                "weight": lane["estimated_weight"],
            })
        if status == "VERIFIED_HIT" and validated_hit_lanes != 1:
            raise PermanentFailure(
                f"accepted pilot {pilot} verified HIT result count drift")
        actual_results = {
            path.resolve() for path in run_dir.glob("lane_*.result.json")
        }
        expected_results = {
            Path(assigned_lanes[lane_id]["result_path"]).resolve()
            for lane_id in expected_result_ids
        }
        if actual_results != expected_results:
            raise PermanentFailure(
                f"accepted pilot {pilot} result artifact set drift")
        if expected_timing != evidence["timing_rows"]:
            raise PermanentFailure(f"accepted pilot {pilot} timing rows drift")
        if any(
            path.stat().st_size != 0 for path in run_dir.glob("*.stderr.txt")
        ):
            raise PermanentFailure(
                f"accepted pilot {pilot} stderr became nonempty")


        verified_hit = evidence["verified_hit"]
        verified_paths = sorted(run_dir.glob("lane_*.candidate_*.verified.json"))
        if verified_hit is None:
            if (
                evidence["verified_artifact_path"] is not None
                or evidence["verified_artifact_sha256"] is not None
                or verified_paths
            ):
                raise PermanentFailure(f"accepted pilot {pilot} acquired a verified artifact")
        else:
            hit = _validate_verified_hit(verified_hit)
            expected_path = run_dir / (
                f"lane_{hit['lane_id']:02d}.candidate_{hit['candidate_index']:03d}.verified.json"
            )
            verified_value, verified_sha256 = _load_json_with_sha(expected_path)
            if (
                verified_paths != [expected_path]
                or evidence["verified_artifact_path"] != str(expected_path)
                or evidence["verified_artifact_sha256"] != verified_sha256
                or verified_value != hit
            ):
                raise PermanentFailure(f"accepted pilot {pilot} verified artifact drift")
        verified_path_for_inventory = (
            Path(evidence["verified_artifact_path"])
            if isinstance(evidence["verified_artifact_path"], str)
            else None
        )
        result_paths_for_inventory = {
            int(lane_id): Path(assigned_lanes[lane_id]["result_path"])
            for lane_id in expected_result_ids
        }
        try:
            current_inventory, stdout_sha256, stderr_sha256 = (
                _validate_exact_run_inventory(
                    run_dir=run_dir,
                    spawned_lane_ids=spawned_lane_ids,
                    result_paths=result_paths_for_inventory,
                    verified_artifact_path=verified_path_for_inventory,
                    name=f"accepted pilot {pilot}",
                )
            )
        except TrancheError as exc:
            raise PermanentFailure(
                f"accepted pilot {pilot} exact run inventory drift"
            ) from exc
        if (
            current_inventory != pinned_inventory
            or stdout_sha256 != evidence["stdout_sha256"]
            or stderr_sha256 != evidence["stderr_sha256"]
        ):
            raise PermanentFailure(
                f"accepted pilot {pilot} stream/inventory pins drift"
            )

def _radicand_bits(bounds: Mapping[str, int]) -> int:
    p, q, n, d = (bounds[key] for key in ("P", "Q", "N", "D"))
    value = (
        80 * (p + q) ** 6 * d**4
        + 20 * (p + q) * (
            p**5 * d**4
            + 10 * p**3 * n**2 * q**2 * d**2
            + 5 * p * n**4 * q**4
        )
    )
    if value <= 0:
        raise TrancheError("pilot radicand bound is not positive")
    return value.bit_length()


def _candidate_table(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    table = _load_json(CANDIDATE_TABLE_PATH)
    table = _require_keys(table, {"schema_version", "kind", "rows"}, "candidate table")
    if table["schema_version"] != 1 or table["kind"] != "Q5_TORSOR_CANDIDATE_TABLE":
        raise TrancheError("candidate table schema mismatch")
    if _canonical_sha(table) != CANDIDATE_TABLE_PAYLOAD_SHA256:
        raise TrancheError("candidate table payload hash mismatch")
    record = plan["candidate_table"]
    if (
        _sha256_file(CANDIDATE_TABLE_PATH) != record["file_sha256"]
        or _sha256_file(CANDIDATE_TABLE_SOURCE_PATH) != record["source_sha256"]
        or _sha256_file(CANDIDATE_TABLE_TOOL_PATH) != record["tool_sha256"]
    ):
        raise TrancheError("candidate table artifact drift after T0")
    rows = table["rows"]
    if not isinstance(rows, list) or len(rows) != 465:
        raise TrancheError("candidate table must contain H=48..512 exactly")
    result: list[dict[str, Any]] = []
    expected_keys = {
        "H", "b", "balance_pass", "max_lane_weight", "min_lane_weight",
        "oeis_gate_pass", "specialization_count",
    }
    for expected_h, raw in zip(range(48, 513), rows):
        row = dict(_require_keys(raw, expected_keys, f"candidate row H={expected_h}"))
        if row["H"] != expected_h or row["b"] != (5760 * expected_h**10).bit_length():
            raise TrancheError(f"candidate row H={expected_h} identity/bit length mismatch")
        for key in ("max_lane_weight", "min_lane_weight", "specialization_count"):
            _strict_int(row[key], f"candidate H={expected_h} {key}", 1)
        if not isinstance(row["balance_pass"], bool) or not isinstance(row["oeis_gate_pass"], bool):
            raise TrancheError(f"candidate row H={expected_h} gate type mismatch")
        result.append(row)
    return result


def _remaining_milliseconds(s: datetime, now: datetime) -> int:
    delta = s - now
    return delta.days * 86_400_000 + delta.seconds * 1000 + delta.microseconds // 1000


def _ready_selection_anchor(state: Mapping[str, Any]) -> datetime:
    matches: list[datetime] = []
    for path in _intent_files():
        raw = _load_json(path)
        if not isinstance(raw, dict):
            raise PermanentFailure("transition intent is not an object")
        if raw.get("to_phase") != "READY_SELECTION":
            continue
        if (
            raw.get("tranche_id") != TRANCHE_ID
            or raw.get("to_revision") != 4
            or raw.get("from_phase") != "READY_D"
        ):
            raise PermanentFailure("READY_SELECTION intent identity mismatch")
        matches.append(
            _parse_time(raw.get("created_utc"), "READY_SELECTION intent time")
        )
    if len(matches) != 1:
        raise PermanentFailure("ledger must contain exactly one READY_SELECTION anchor")
    anchor = matches[0]
    updated = _parse_time(state["updated_utc"], "state updated_utc")
    if anchor > updated or (state["phase"] == "READY_SELECTION" and anchor != updated):
        raise PermanentFailure("READY_SELECTION anchor/state chronology mismatch")
    return anchor


def _selection_core(
    state: Mapping[str, Any], plan: Mapping[str, Any], now: datetime,
    *, ready_selection_anchor: datetime,
) -> dict[str, Any]:
    if set(state["accepted_pilots"]) != set(PILOT_ORDER):
        raise TrancheError("all four pilots must be accepted before selection")
    anchor = _aware_utc(ready_selection_anchor, "READY_SELECTION anchor")
    setup_deadline = anchor + timedelta(seconds=300)
    if now > setup_deadline:
        raise TrancheError("selection setup window of 300 seconds has elapsed")
    timing: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None
    for pilot in ("B", "C", "D"):
        evidence = state["accepted_pilots"][pilot]
        rows = evidence.get("timing_rows")
        if not isinstance(rows, list) or len(rows) != 64:
            raise TrancheError(f"pilot {pilot} must provide 64 timing rows")
        bits = _radicand_bits(PILOT_SPECS[pilot]["bounds"])
        for expected_lane, row in enumerate(rows):
            row = _require_keys(row, {"lane_id", "elapsed_milliseconds", "weight"}, f"pilot {pilot} timing")
            if row["lane_id"] != expected_lane:
                raise TrancheError(f"pilot {pilot} timing lane order mismatch")
            elapsed = _strict_int(row["elapsed_milliseconds"], "elapsed milliseconds", 1)
            weight = _strict_int(row["weight"], "lane weight", 1)
            denominator = weight * bits**2
            record = {
                "pilot": pilot,
                "lane_id": expected_lane,
                "elapsed_milliseconds": elapsed,
                "weight": weight,
                "b": bits,
                "ratio_numerator": elapsed,
                "ratio_denominator": denominator,
            }
            timing.append(record)
            if best is None or elapsed * best["ratio_denominator"] > best["ratio_numerator"] * denominator:
                best = record
    assert best is not None
    rho_gcd = math.gcd(best["ratio_numerator"], best["ratio_denominator"])
    rho_numerator = best["ratio_numerator"] // rho_gcd
    rho_denominator = best["ratio_denominator"] // rho_gcd
    remaining = _remaining_milliseconds(_parse_time(state["s"], "S"), anchor)
    candidates: list[dict[str, Any]] = []
    selected_h: int | None = None
    for row in _candidate_table(plan):
        numerator = 3 * rho_numerator * row["max_lane_weight"] * row["b"] ** 2
        denominator = 2 * rho_denominator
        predicted = (numerator + denominator - 1) // denominator
        eligible = row["balance_pass"] and row["oeis_gate_pass"]
        fits = eligible and predicted + 300_000 <= remaining
        candidate = dict(row)
        candidate.update(predicted_milliseconds=predicted, eligible=eligible, fits=fits)
        candidates.append(candidate)
        if fits:
            selected_h = row["H"]
    return {
        "generated_utc": _utc_text(anchor),
        "selection_setup_deadline_utc": _utc_text(setup_deadline),
        "remaining_before_s_milliseconds": remaining,
        "setup_guard_milliseconds": 300000,
        "timing_records": timing,
        "rho": {
            "numerator": rho_numerator,
            "denominator": rho_denominator,
            "source_pilot": best["pilot"],
            "source_lane": best["lane_id"],
        },
        "candidates": candidates,
        "selected_h": selected_h,
    }


def preview_selection() -> dict[str, Any]:
    clock = _now_utc
    lock, plan, state = _load_context()
    if state["phase"] != "READY_SELECTION":
        raise TrancheNotReady(f"selection preview requires READY_SELECTION, got {state['phase']}")
    now = _aware_utc(clock(), "clock")
    _validate_transition_clock(state, now, lock)
    _revalidate_accepted_artifacts(state, plan)
    ready_anchor = _ready_selection_anchor(state)
    core = _selection_core(
        state, plan, now, ready_selection_anchor=ready_anchor
    )
    return {"ok": True, "phase": state["phase"], **core}


def _validate_public_status_legacy(now: datetime) -> dict[str, Any]:
    try:
        gate_bytes = PUBLIC_STATUS_PATH.read_bytes()
    except FileNotFoundError as exc:
        raise TrancheNotReady(
            f"required artifact is not present: {PUBLIC_STATUS_PATH}"
        ) from exc
    except OSError as exc:
        raise TrancheError(f"cannot read public status gate: {exc}") from exc
    gate_digest = hashlib.sha256(gate_bytes).hexdigest()
    try:
        gate = json.loads(gate_bytes.decode("ascii"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise TrancheError(f"cannot parse public status gate: {exc}") from exc
    gate = dict(_require_keys(
        gate,
        {
            "schema_version", "kind", "checked_utc", "problem_open",
            "oeis_no_n5_value", "formal_conjecture_open", "sources",
        },
        "public status gate",
    ))
    if gate["schema_version"] != 1 or gate["kind"] != "Q5_PUBLIC_STATUS_GATE":
        raise TrancheError("public status gate schema mismatch")
    if gate["problem_open"] is not True or gate["oeis_no_n5_value"] is not True or gate["formal_conjecture_open"] is not True:
        raise TrancheError("public status gate does not certify the target open")
    checked = _parse_time(gate["checked_utc"], "public status checked_utc")
    if checked > now or now - checked > timedelta(minutes=5):
        raise TrancheNotReady("public status gate is not within five minutes of finalize")
    sources = gate["sources"]
    if not isinstance(sources, list) or len(sources) != len(PUBLIC_SOURCE_EXPECTATIONS):
        raise TrancheError("public status source array mismatch")
    normalized: list[dict[str, Any]] = []
    for expected, raw in zip(PUBLIC_SOURCE_EXPECTATIONS, sources):
        source = dict(_require_keys(raw, {"role", "url", "observed_status", "content_sha256"}, "public source"))
        for key in ("role", "url", "observed_status"):
            if source[key] != expected[key]:
                raise TrancheError(f"public status source {expected['role']} {key} mismatch")
        digest = source["content_sha256"]
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            raise TrancheError("public status content_sha256 is malformed")
        normalized.append(source)
    gate["sources"] = normalized
    gate["file_sha256"] = gate_digest
    return gate



def _audit_public_status(now: datetime, *, require_fresh: bool) -> dict[str, Any]:
    gate_before, gate_sha256 = _load_json_with_sha(PUBLIC_STATUS_PATH, missing_ready=True)
    if not isinstance(gate_before, dict):
        raise TrancheError("public status gate must be an object")
    capture_dir_raw = gate_before.get("capture_dir")
    if not isinstance(capture_dir_raw, str):
        raise TrancheError("public status gate capture_dir is malformed")
    capture_dir = Path(capture_dir_raw).resolve()
    capture_parent = (PUBLIC_STATUS_PATH.parent / public_status_lib.CAPTURE_PARENT_NAME).resolve()
    try:
        capture_dir.relative_to(capture_parent)
    except ValueError as exc:
        raise TrancheError("public status capture_dir is outside the fixed capture parent") from exc
    inventory_before = _inventory(capture_dir)
    try:
        audited = public_status_lib.audit_gate(
            PUBLIC_STATUS_PATH, now=now, require_fresh=require_fresh
        )
    except public_status_lib.PublicStatusError as exc:
        if "not fresh" in str(exc):
            raise TrancheNotReady(str(exc)) from exc
        raise TrancheError(f"public status audit failed: {exc}") from exc
    inventory_after = _inventory(capture_dir)
    gate_after, gate_sha256_after = _load_json_with_sha(PUBLIC_STATUS_PATH)
    if (
        gate_before != audited
        or gate_after != gate_before
        or gate_sha256_after != gate_sha256
        or inventory_after != inventory_before
    ):
        raise TrancheError("public status gate or capture inventory changed during audit")
    return {
        **audited,
        "file_sha256": gate_sha256,
        "capture_inventory": inventory_before,
    }


def _validate_public_status(now: datetime) -> dict[str, Any]:
    return _audit_public_status(_aware_utc(now, "public status clock"), require_fresh=True)


def _revalidate_public_status_evidence(evidence: Any) -> None:
    expected_keys = set(public_status_lib.GATE_KEYS) | {"file_sha256", "capture_inventory"}
    evidence = dict(_require_keys(evidence, expected_keys, "pinned public status gate"))
    current = _audit_public_status(
        _parse_time(evidence["checked_utc"], "pinned public status checked_utc"),
        require_fresh=False,
    )
    if current != evidence:
        raise PermanentFailure("pinned public status gate or capture inventory drifted")

def _validate_main_manifest(
    selected_h: int,
    core: Mapping[str, Any],
    state: Mapping[str, Any],
    plan: Mapping[str, Any],
) -> tuple[dict[str, Any], str]:
    if not MAIN_MANIFEST_PATH.is_file():
        raise TrancheNotReady(f"selected main manifest is not present: {MAIN_MANIFEST_PATH}")
    try:
        envelope = manifest_lib.audit_manifest(
            MAIN_MANIFEST_PATH.resolve(), expected_campaign_id=MAIN_CAMPAIGN_ID
        )
    except manifest_lib.ManifestError as exc:
        raise TrancheError(f"selected main manifest audit failed: {exc}") from exc
    payload = envelope["payload"]
    _validate_q5_manifest_contract(payload, plan, MAIN_LANE_CONFIG_DIR)
    if payload["mode"] != "SELECTED_MAIN" or payload["search_mode"] != "canonical_positive_u_positive_y":
        raise TrancheError("selected main manifest mode mismatch")
    if payload["bounds"] != {"P": selected_h, "Q": selected_h, "N": selected_h, "D": selected_h}:
        raise TrancheError("selected main manifest is not the selected symmetric box")
    if payload["deadline"] != state["s"]:
        raise TrancheError("selected main manifest deadline is not exactly S")
    if payload["manifest_path"] != str(MAIN_MANIFEST_PATH.resolve()) or payload["run_dir"] != str(MAIN_RUN_DIR.resolve()):
        raise TrancheError("selected main manifest fixed path mismatch")
    if MAIN_RUN_DIR.exists():
        raise TrancheError("selected main run directory already exists before finalize")
    d_finished = _parse_time(state["accepted_pilots"]["D"]["finished_utc"], "Pilot D finish")
    created = manifest_lib.parse_deadline(payload["created_utc"])
    if created <= d_finished:
        raise TrancheError("selected main manifest was not created after Pilot D")
    if created > _parse_time(core["selection_setup_deadline_utc"], "selection setup deadline"):
        raise TrancheError("selected main manifest was created after the setup window")
    row = next(item for item in core["candidates"] if item["H"] == selected_h)
    balance = payload["balance"]
    if (
        balance["max_lane_weight"] != row["max_lane_weight"]
        or balance["min_lane_weight"] != row["min_lane_weight"]
        or balance["threshold_pass"] is not row["balance_pass"]
        or payload["specialization_count"] != row["specialization_count"]
        or payload["oeis_redundancy_gate"]["passes"] is not row["oeis_gate_pass"]
    ):
        raise TrancheError("selected main manifest differs from its frozen candidate row")
    return envelope, envelope["payload_sha256"]


def _finalize_selection_action(
    commit: Callable[..., dict[str, Any]],
    fail_closed: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    clock = _now_utc
    census_hook: CensusHook | None = None
    lock, plan, state = _load_context()
    if state["phase"] != "READY_SELECTION":
        raise PermanentFailure(f"finalize requires READY_SELECTION, got {state['phase']}")
    now = _aware_utc(clock(), "clock")
    try:
        _validate_transition_clock(state, now, lock)
        _revalidate_accepted_artifacts(state, plan)
        _current_clean_census(plan, clock, census_hook)
        ready_anchor = _ready_selection_anchor(state)
        core = _selection_core(
            state, plan, now, ready_selection_anchor=ready_anchor
        )
        selected_h = core["selected_h"]
        selected_digest: str | None = None
        public_gate: dict[str, Any] | None = None
        main_file_sha256: str | None = None
        if selected_h is not None:
            public_gate = _validate_public_status(now)
            _, selected_digest = _validate_main_manifest(selected_h, core, state, plan)
            main_file_sha256 = _sha256_file(MAIN_MANIFEST_PATH)
        _revalidate_accepted_artifacts(state, plan)
        _current_clean_census(plan, clock, census_hook)
        commit_now = _aware_utc(clock(), "finalize commit clock")
        _validate_transition_clock(state, commit_now, lock)
        if _ready_selection_anchor(state) != ready_anchor:
            raise TrancheError("READY_SELECTION anchor changed before commit")
        committed_core = _selection_core(
            state, plan, commit_now,
            ready_selection_anchor=ready_anchor,
        )
        if committed_core["selected_h"] != selected_h:
            raise TrancheError("selected H changed before the atomic commit")
        core = committed_core
        if selected_h is not None:
            public_gate = _validate_public_status(commit_now)
            if main_file_sha256 != _sha256_file(MAIN_MANIFEST_PATH):
                raise TrancheError("selected main manifest changed before commit")
        now = commit_now
        report = {
            "schema_version": 1,
            "kind": "Q5_TRANCHE_SELECTION_REPORT",
            "tranche_id": TRANCHE_ID,
            "t0": state["t0"],
            "s": state["s"],
            "g": state["g"],
            "pilot_evidence": state["accepted_pilots"],
            "candidate_table": {
                **plan["candidate_table"],
                "rows": core["candidates"],
            },
            "generated_utc": core["generated_utc"],
            "selection_setup_deadline_utc": core["selection_setup_deadline_utc"],
            "remaining_before_s_milliseconds": core["remaining_before_s_milliseconds"],
            "setup_guard_milliseconds": core["setup_guard_milliseconds"],
            "timing_records": core["timing_records"],
            "rho": core["rho"],
            "selected_h": selected_h,
            "selected_main_manifest_path": str(MAIN_MANIFEST_PATH.resolve()),
            "selected_main_manifest_sha256": selected_digest,
            "public_status_gate": public_gate,
        }
        report_bytes = _pretty_bytes(report)
        report_sha = hashlib.sha256(report_bytes).hexdigest()
        phase = "MAIN_FROZEN" if selected_h is not None else "NO_MAIN"
        new_state = commit(
            state,
            phase=phase,
            now=now,
            updates={
                "selection_report_sha256": report_sha,
                "selected_h": selected_h,
                "selected_main_manifest_sha256": selected_digest,
            },
            extra_files={SELECTION_REPORT_PATH: report_bytes},
        )
        return {
            "ok": True,
            "phase": new_state["phase"],
            "selected_h": selected_h,
            "selected_main_manifest_sha256": selected_digest,
            "selection_report_path": str(SELECTION_REPORT_PATH),
        }
    except TrancheNotReady:
        raise
    except BaseException as exc:
        fail_closed(state, exc, now)
        raise PermanentFailure(f"selection finalize failed permanently: {exc}") from exc





def _authorization_path(phase: str) -> Path:
    if phase not in {*PILOT_ORDER, "MAIN"}:
        raise TrancheError(f"unknown launch authorization phase: {phase}")
    return (AUTHORIZATIONS_DIR / f"{phase}.json").resolve()


def authorize_launch(phase: str) -> dict[str, Any]:
    clock = _now_utc
    census_hook: CensusHook | None = None
    """Create one phase-specific launch ticket; never launch a process."""

    if phase not in {*PILOT_ORDER, "MAIN"}:
        raise TrancheError(f"unknown launch authorization phase: {phase}")
    lock, plan, state = _load_context()
    expected_state_phase = "MAIN_FROZEN" if phase == "MAIN" else f"READY_{phase}"
    if state["phase"] != expected_state_phase:
        raise PermanentFailure(
            f"launch phase {phase} requires {expected_state_phase}, got {state['phase']}"
        )
    now = _aware_utc(clock(), "launch authorization clock")
    _validate_transition_clock(state, now, lock)
    _revalidate_accepted_artifacts(state, plan)
    _current_clean_census(plan, clock, census_hook)
    readiness = _validate_readiness(
        expected_sha256=lock["launch_readiness_sha256"], now=now
    )

    state_value, state_sha256 = _load_json_with_sha(STATE_PATH)
    if state_value != state:
        raise PermanentFailure("state changed while launch authorization was prepared")

    public_status_path: str | None = None
    public_status_sha256: str | None = None
    public_expiry: datetime | None = None
    if phase == "MAIN":
        selection_report = _load_selection_report_pinned(state)
        setup_deadline = _parse_time(
            selection_report.get("selection_setup_deadline_utc"),
            "selection setup deadline",
        )
        if now > setup_deadline:
            raise TrancheNotReady("main launch authorization missed the selection setup window")
        envelope, manifest_file_sha256 = _audit_main_manifest_stable(state, plan)
        payload = envelope["payload"]
        if envelope["payload_sha256"] != state["selected_main_manifest_sha256"]:
            raise PermanentFailure("main manifest differs from the selected digest")
        manifest_path = MAIN_MANIFEST_PATH.resolve()
        run_dir = MAIN_RUN_DIR.resolve()
        status = _validate_public_status(now)
        public_status_path = str(PUBLIC_STATUS_PATH.resolve())
        public_status_sha256 = status["file_sha256"]
        public_expiry = _parse_time(status["expires_utc"], "public status expiry")
    else:
        spec = PILOT_SPECS[phase]
        manifest_path = spec["manifest_path"].resolve()
        try:
            envelope = manifest_lib.audit_manifest(
                manifest_path, expected_campaign_id=spec["campaign_id"]
            )
        except FileNotFoundError as exc:
            raise TrancheNotReady(f"pilot {phase} manifest is not present") from exc
        except manifest_lib.ManifestError as exc:
            raise TrancheError(f"pilot {phase} manifest audit failed: {exc}") from exc
        manifest_file_sha256 = _sha256_file(manifest_path)
        payload = envelope["payload"]
        run_dir = spec["run_dir"].resolve()
        if (
            payload["mode"] != "CALIBRATION_ONLY"
            or payload["search_mode"] != spec["search_mode"]
            or payload["bounds"] != spec["bounds"]
            or payload["campaign_id"] != spec["campaign_id"]
            or payload["manifest_path"] != str(manifest_path)
            or payload["run_dir"] != str(run_dir)
        ):
            raise TrancheError(f"pilot {phase} manifest contract mismatch")
        _validate_q5_manifest_contract(payload, plan, spec["lane_config_dir"])
        created = manifest_lib.parse_deadline(payload["created_utc"])
        expected_deadline = min(
            created + timedelta(seconds=spec["limit_seconds"]),
            _parse_time(state["s"], "S"),
        )
        pilot_deadline = manifest_lib.parse_deadline(payload["deadline"])
        if not (created < pilot_deadline <= expected_deadline):
            raise TrancheError(f"pilot {phase} deadline exceeds its local/S cap")

    deadline = manifest_lib.parse_deadline(payload["deadline"])
    if now >= deadline:
        raise TrancheNotReady(f"launch phase {phase} deadline has been reached")
    if run_dir.exists() or (run_dir / "launch.lock").exists():
        raise PermanentFailure(f"launch phase {phase} run directory or launch lock already exists")
    expected_ticket_path = _authorization_path(phase)
    if plan.get("authorization_paths", {}).get(phase) != str(expected_ticket_path):
        raise PermanentFailure("authorization path differs from the frozen plan")
    if expected_ticket_path.exists():
        raise PermanentFailure(f"launch authorization already exists: {expected_ticket_path}")

    expiry = min(now + timedelta(minutes=5), deadline)
    if public_expiry is not None:
        expiry = min(expiry, public_expiry)
    if expiry <= now:
        raise TrancheNotReady("launch authorization would already be expired")
    ticket = {
        "schema_version": 1,
        "kind": "q5-launch-authorization-v1",
        "tranche_id": TRANCHE_ID,
        "phase": phase,
        "created_utc": _utc_text(now),
        "expires_utc": _utc_text(expiry),
        "state_path": str(STATE_PATH.resolve()),
        "state_sha256": state_sha256,
        "manifest_path": str(manifest_path),
        "manifest_file_sha256": manifest_file_sha256,
        "manifest_payload_sha256": envelope["payload_sha256"],
        "campaign_id": payload["campaign_id"],
        "mode": payload["mode"],
        "search_mode": payload["search_mode"],
        "deadline": payload["deadline"],
        "run_dir": str(run_dir),
        "readiness_path": str(READINESS_PATH.resolve()),
        "readiness_sha256": readiness["file_sha256"],
        "public_status_path": public_status_path,
        "public_status_sha256": public_status_sha256,
    }
    encoded = _pretty_bytes(ticket)
    _write_xb(expected_ticket_path, encoded)
    return {
        "ok": True,
        "phase": phase,
        "authorization_path": str(expected_ticket_path),
        "authorization_sha256": hashlib.sha256(encoded).hexdigest(),
        "expires_utc": ticket["expires_utc"],
    }

MAIN_REPORT_KEYS = {
    "schema_version", "kind", "tranche_id", "status", "accepted_utc",
    "manifest_path", "manifest_payload_sha256", "manifest_file_sha256",
    "summary_path", "summary_sha256", "final_state_path", "final_state_sha256",
    "launch_lock_path", "launch_lock_sha256", "selection_report_sha256",
    "authorization_state_sha256",
    "result_sha256", "stdout_sha256", "stderr_sha256",
    "spawned_lane_ids", "finished_utc", "lane_status_counts",
    "run_inventory",
    "missing_result_lane_ids", "verified_hit", "verified_artifact_path",
    "verified_artifact_sha256",
}


def _audit_main_manifest_stable(
    state: Mapping[str, Any], plan: Mapping[str, Any]
) -> tuple[dict[str, Any], str]:
    before, before_sha = _load_json_with_sha(MAIN_MANIFEST_PATH, missing_ready=True)
    try:
        envelope = manifest_lib.audit_manifest(
            MAIN_MANIFEST_PATH.resolve(),
            expected_digest=state["selected_main_manifest_sha256"],
            expected_campaign_id=MAIN_CAMPAIGN_ID,
        )
    except manifest_lib.ManifestError as exc:
        raise TrancheError(f"main manifest audit failed: {exc}") from exc
    after, after_sha = _load_json_with_sha(MAIN_MANIFEST_PATH)
    if before != envelope or after != envelope or before_sha != after_sha:
        raise TrancheError("main manifest changed during its stable audit")
    payload = envelope["payload"]
    _validate_q5_manifest_contract(payload, plan, MAIN_LANE_CONFIG_DIR)
    selected_h = _strict_int(state["selected_h"], "selected H", 48)
    if payload["mode"] != "SELECTED_MAIN" or payload["search_mode"] != "canonical_positive_u_positive_y":
        raise TrancheError("main manifest mode mismatch")
    if payload["bounds"] != {"P": selected_h, "Q": selected_h, "N": selected_h, "D": selected_h}:
        raise TrancheError("main manifest bounds differ from selected H")
    if payload["deadline"] != state["s"]:
        raise TrancheError("main manifest deadline is not exactly S")
    if payload["manifest_path"] != str(MAIN_MANIFEST_PATH.resolve()):
        raise TrancheError("main manifest fixed path mismatch")
    if payload["run_dir"] != str(MAIN_RUN_DIR.resolve()):
        raise TrancheError("main run fixed path mismatch")
    return envelope, before_sha


def _load_selection_report_pinned(state: Mapping[str, Any]) -> dict[str, Any]:
    report, digest = _load_json_with_sha(SELECTION_REPORT_PATH)
    if digest != state["selection_report_sha256"]:
        raise PermanentFailure("selection report differs from the state pin")
    if not isinstance(report, dict) or report.get("selected_h") != state["selected_h"]:
        raise PermanentFailure("selection report selected H mismatch")
    if report.get("selected_main_manifest_sha256") != state["selected_main_manifest_sha256"]:
        raise PermanentFailure("selection report main digest mismatch")
    return report


def _validate_main_evidence(
    state: Mapping[str, Any],
    plan: Mapping[str, Any],
    clock: Clock,
    census_hook: CensusHook | None,
) -> dict[str, Any]:
    acceptance_now = _aware_utc(clock(), "main acceptance clock")
    envelope, manifest_file_sha256 = _audit_main_manifest_stable(state, plan)
    payload = envelope["payload"]
    digest = envelope["payload_sha256"]
    run_dir = MAIN_RUN_DIR.resolve()
    summary_path = run_dir / "supervisor_summary.json"
    final_state_path = run_dir / "supervisor_state.json"
    launch_lock_path = run_dir / "launch.lock"
    summary, summary_sha256 = _load_json_with_sha(summary_path, missing_ready=True)
    final_state, final_state_sha256 = _load_json_with_sha(
        final_state_path, missing_ready=True
    )
    summary = dict(_require_keys(
        summary,
        {
            "schema_version", "kind", "campaign_id", "manifest_path",
            "manifest_payload_sha256", "status", "finished_utc", "owned_pids",
            "spawned_lane_ids", "verified_hit", "lane_statuses",
        },
        "main summary",
    ))
    final_state = dict(_require_keys(
        final_state,
        {
            "schema_version", "kind", "campaign_id", "manifest_payload_sha256",
            "status", "updated_utc", "supervisor_pid", "owned_pids",
            "spawned_lane_ids", "lanes", "anomaly",
        },
        "main final state",
    ))
    if summary["schema_version"] != 1 or summary["kind"] != "Q5_TORSOR_SUPERVISOR_SUMMARY":
        raise TrancheError("main summary schema mismatch")
    if final_state["schema_version"] != 1 or final_state["kind"] != "Q5_TORSOR_SUPERVISOR_STATE":
        raise TrancheError("main state schema mismatch")
    for value, name in ((summary, "summary"), (final_state, "state")):
        if value["campaign_id"] != MAIN_CAMPAIGN_ID or value["manifest_payload_sha256"] != digest:
            raise TrancheError(f"main {name} identity mismatch")
        if value["owned_pids"] != []:
            raise TrancheError(f"main {name} retains owned PIDs")
    if summary["manifest_path"] != str(MAIN_MANIFEST_PATH.resolve()):
        raise TrancheError("main summary manifest path mismatch")
    if final_state["anomaly"] is not None:
        raise TrancheError("main final state contains an anomaly")
    if final_state["status"] != summary["status"]:
        raise TrancheError("main state/summary status mismatch")

    status = summary["status"]
    if status in {"STARTING", "RUNNING"}:
        raise TrancheNotReady("main campaign has not reached a terminal status")
    if status not in {"FINITE_NO_HIT", "TIMEOUT_INCOMPLETE", "VERIFIED_HIT"}:
        raise TrancheError(f"main terminal status is fail-closed: {status}")
    launch_lock_raw, launch_lock_sha256 = _load_json_with_sha(
        launch_lock_path, missing_ready=True
    )
    launch_lock = _validate_launch_lock_value(
        launch_lock_raw, payload, digest, name="main launch lock",
        expected_readiness_sha256=plan["launch_readiness"]["file_sha256"],
    )
    if launch_lock["supervisor_pid"] != final_state["supervisor_pid"]:
        raise TrancheError("main supervisor PID identity mismatch")
    created = manifest_lib.parse_deadline(payload["created_utc"])
    launch_claimed = _parse_time(launch_lock["claimed_utc"], "main launch claim")
    finished = _parse_time(summary["finished_utc"], "main finish")
    final_updated = _parse_time(final_state["updated_utc"], "main final state update")
    s = _parse_time(state["s"], "S")
    g = _parse_time(state["g"], "G")
    if not (created <= launch_claimed <= finished <= final_updated <= acceptance_now):
        raise TrancheError("main chronology is not monotone")
    if final_updated > g or launch_claimed >= s:
        raise TrancheError("main launch/finalization is outside S/G")
    if status == "TIMEOUT_INCOMPLETE" and finished < s:
        raise TrancheError("main timeout was recorded before S")
    if status == "FINITE_NO_HIT" and finished >= s:
        raise TrancheError("main FINITE_NO_HIT was observed at/after S")

    selection_report = _load_selection_report_pinned(state)
    generated = _parse_time(
        selection_report.get("generated_utc"), "selection report generated_utc"
    )
    if generated >= launch_claimed:
        raise TrancheError("main launch claim does not follow the frozen selection")
    public_gate = selection_report.get("public_status_gate")
    if not isinstance(public_gate, dict):
        raise TrancheError("main selection report lacks a public status gate")
    checked = _parse_time(public_gate.get("checked_utc"), "public status checked_utc")
    _revalidate_public_status_evidence(public_gate)
    if not (checked <= launch_claimed <= checked + timedelta(minutes=5)):
        raise TrancheError("main launch was outside the five-minute public-status window")
    authorization_state, authorization_state_sha256 = _load_json_with_sha(
        STATE_PATH
    )
    if authorization_state != state:
        raise TrancheError("main authorization state changed before acceptance")
    authorization_ticket = _validate_authorization_ticket(
        phase="MAIN",
        lock=launch_lock,
        payload=payload,
        payload_digest=digest,
        manifest_path=MAIN_MANIFEST_PATH.resolve(),
        manifest_file_sha256=manifest_file_sha256,
        run_dir=run_dir,
        plan=plan,
        launch_claimed=launch_claimed,
        expected_public_status_sha256=public_gate["file_sha256"],
        expected_state_sha256=authorization_state_sha256,
    )


    lanes_state = final_state["lanes"]
    lane_statuses = summary["lane_statuses"]
    _validate_terminal_lane_state(
        payload=payload, lanes_state=lanes_state, lane_statuses=lane_statuses,
        name="main",
    )
    spawned_lane_ids = _validate_spawned_lane_ids(
        summary=summary, final_state=final_state, payload=payload,
        lane_statuses=lane_statuses, name="main",
    )

    counts = {
        key: list(lane_statuses.values()).count(key)
        for key in sorted(set(lane_statuses.values()))
    }
    no_work = sum(not bool(lane["specializations"]) for lane in payload["lanes"])
    if status == "FINITE_NO_HIT":
        expected_counts = {"NO_HIT": 64 - no_work}
        if no_work:
            expected_counts["NO_WORK"] = no_work
        if counts != expected_counts or summary["verified_hit"] is not None:
            raise TrancheError("main finite NO_HIT lane contract mismatch")
    elif status == "TIMEOUT_INCOMPLETE":
        if summary["verified_hit"] is not None or counts.get("TIMEOUT_INCOMPLETE", 0) < 1:
            raise TrancheError("main timeout carries a hit or no incomplete lane")
        if not set(counts).issubset({"NO_HIT", "NO_WORK", "TIMEOUT_INCOMPLETE"}):
            raise TrancheError("main timeout lane status is inadmissible")
    else:
        hit = _validate_verified_hit(summary["verified_hit"])
        if counts.get("VERIFIED_HIT") != 1:
            raise TrancheError("main verified summary lacks exactly one hit lane")
        if lane_statuses[str(hit["lane_id"])] != "VERIFIED_HIT":
            raise TrancheError("main verified-hit lane status mismatch")
        if not set(counts).issubset(
            {"NO_HIT", "NO_WORK", "VERIFIED_HIT", "STOPPED_AFTER_VERIFIED_HIT"}
        ):
            raise TrancheError("main verified-hit lane statuses are inadmissible")
        candidate_observed = _parse_time(hit["candidate_observed_utc"], "main candidate observation")
        verified_time = _parse_time(hit["verified_utc"], "main verified time")
        _validate_verified_chronology(
            launch_claimed=launch_claimed,
            candidate_observed=candidate_observed,
            verified_time=verified_time,
            finished=finished,
            candidate_deadline=s,
            name="main",
        )

    result_sha256: dict[str, str] = {}
    stderr_sha256: dict[str, str] = {}
    stdout_sha256: dict[str, str] = {}
    missing_result_lane_ids: list[int] = []
    validated_hit_lanes = 0
    for lane in payload["lanes"]:
        lane_id = lane["lane_id"]
        lane_key = str(lane_id)
        assigned = bool(lane["specializations"])
        result_path = Path(lane["result_path"])
        stderr_path = run_dir / f"lane_{lane_id:02d}.stderr.txt"
        if not assigned:
            if result_path.exists():
                raise TrancheError(f"main NO_WORK lane {lane_id} has a result")
            continue
        if lane_id not in spawned_lane_ids:
            if (
                status != "TIMEOUT_INCOMPLETE"
                or lane_statuses[lane_key] != "TIMEOUT_INCOMPLETE"
                or result_path.exists()
            ):
                raise TrancheError(
                    f"main unspawned lane {lane_id} has inadmissible evidence"
                )
            missing_result_lane_ids.append(lane_id)
            continue
        if not stderr_path.is_file() or stderr_path.stat().st_size != 0:
            raise TrancheError(f"main lane {lane_id} stderr is missing or nonempty")
        stderr_sha256[lane_key] = _sha256_file(stderr_path)
        if not result_path.is_file():
            missing_status_ok = (
                status == "TIMEOUT_INCOMPLETE"
                and lane_statuses[lane_key] == "TIMEOUT_INCOMPLETE"
            ) or (
                status == "VERIFIED_HIT"
                and lane_statuses[lane_key] == "STOPPED_AFTER_VERIFIED_HIT"
            )
            if not missing_status_ok:
                raise TrancheError(
                    f"main lane {lane_id} result is missing unexpectedly")
            missing_result_lane_ids.append(lane_id)
            continue
        result_value, result_digest = _load_json_with_sha(result_path)
        result = supervisor_lib.validate_lane_result(
            result_value, payload=payload, payload_digest=digest, lane=lane
        )
        result_sha256[lane_key] = result_digest
        result_status = result["status"]
        _validate_result_lane_binding(
            lane_id=lane_id,
            lane_status=lane_statuses[lane_key],
            result_status=result_status,
            name="main",
        )
        if status == "FINITE_NO_HIT" and result_status != "NO_HIT":
            raise TrancheError(f"main finite lane {lane_id} result is not NO_HIT")
        if status == "TIMEOUT_INCOMPLETE" and result_status not in {"NO_HIT", "TIMEOUT_INCOMPLETE"}:
            raise TrancheError(f"main timeout lane {lane_id} result is inadmissible")
        if status == "VERIFIED_HIT":
            if result_status == "HIT":
                if lane_id != summary["verified_hit"]["lane_id"]:
                    raise TrancheError("main HIT result lane differs from the verified summary")
                candidates = result["candidates"]
                if (
                    len(candidates) != 1
                    or candidates[0].get("integer_quadruple")
                    != summary["verified_hit"]["integer_quadruple"]
                ):
                    raise TrancheError(
                        "main HIT result must contain exactly the verified candidate"
                    )
                validated_hit_lanes += 1
            elif result_status != "NO_HIT":
                raise TrancheError(f"main verified run lane {lane_id} result is inadmissible")

    actual_result_paths = {path.resolve() for path in run_dir.glob("lane_*.result.json")}
    pinned_result_paths = {
        Path(lane["result_path"]).resolve()
        for lane in payload["lanes"]
        if str(lane["lane_id"]) in result_sha256
    }
    if actual_result_paths != pinned_result_paths:
        raise TrancheError("main result artifact set differs from the manifest lanes")
    verified_paths = sorted(run_dir.glob("lane_*.candidate_*.verified.json"))
    verified_artifact_path: Path | None = None
    verified_artifact_sha256: str | None = None
    if status == "VERIFIED_HIT":
        hit = summary["verified_hit"]
        if validated_hit_lanes != 1:
            raise TrancheError("main must contain exactly one validated HIT result")
        verified_artifact_path = run_dir / (
            f"lane_{hit['lane_id']:02d}.candidate_{hit['candidate_index']:03d}.verified.json"
        )
        if verified_paths != [verified_artifact_path]:
            raise TrancheError("main verified-artifact set mismatch")
        verified_value, verified_artifact_sha256 = _load_json_with_sha(
            verified_artifact_path, missing_ready=True
        )
        if verified_value != hit:
            raise TrancheError("main verified artifact differs from the summary")
    elif verified_paths:
        raise TrancheError("main non-hit terminal state carries a verified artifact")
    for stderr_path in run_dir.glob("*.stderr.txt"):
        if stderr_path.stat().st_size != 0:
            raise TrancheError(f"main has nonempty stderr: {stderr_path}")
    result_paths_for_inventory = {
        lane["lane_id"]: Path(lane["result_path"])
        for lane in payload["lanes"]
        if str(lane["lane_id"]) in result_sha256
    }
    run_inventory, stdout_sha256, exact_stderr_sha256 = (
        _validate_exact_run_inventory(
            run_dir=run_dir,
            spawned_lane_ids=spawned_lane_ids,
            result_paths=result_paths_for_inventory,
            verified_artifact_path=verified_artifact_path,
            name="main",
        )
    )
    if exact_stderr_sha256 != stderr_sha256:
        raise TrancheError("main stderr hashes differ from the exact inventory")
    for artifact_path, artifact_sha256, artifact_name in (
        (summary_path, summary_sha256, "main summary"),
        (final_state_path, final_state_sha256, "main final state"),
        (launch_lock_path, launch_lock_sha256, "main launch lock"),
    ):
        _inventory_digest(run_inventory, run_dir, artifact_path, artifact_sha256, artifact_name)
    for lane in payload["lanes"]:
        lane_key = str(lane["lane_id"])
        if lane_key in result_sha256:
            _inventory_digest(run_inventory, run_dir, Path(lane["result_path"]), result_sha256[lane_key], f"main lane {lane_key} result")
        if lane_key in stderr_sha256:
            _inventory_digest(run_inventory, run_dir, run_dir / f"lane_{lane['lane_id']:02d}.stderr.txt", stderr_sha256[lane_key], f"main lane {lane_key} stderr")
    if verified_artifact_path is not None and verified_artifact_sha256 is not None:
        _inventory_digest(run_inventory, run_dir, verified_artifact_path, verified_artifact_sha256, "main verified artifact")
    _current_clean_census(plan, clock, census_hook)

    return {
        "schema_version": 1,
        "kind": "Q5_TRANCHE_MAIN_TERMINAL_REPORT",
        "tranche_id": TRANCHE_ID,
        "status": status,
        "accepted_utc": _utc_text(acceptance_now),
        "manifest_path": str(MAIN_MANIFEST_PATH.resolve()),
        "manifest_payload_sha256": digest,
        "manifest_file_sha256": manifest_file_sha256,
        "summary_path": str(summary_path),
        "summary_sha256": summary_sha256,
        "final_state_path": str(final_state_path),
        "final_state_sha256": final_state_sha256,
        "launch_lock_path": str(launch_lock_path),
        "launch_lock_sha256": launch_lock_sha256,
        "run_inventory": run_inventory,
        "selection_report_sha256": state["selection_report_sha256"],
        "authorization_state_sha256": authorization_ticket["state_sha256"],
        "result_sha256": result_sha256,
        "spawned_lane_ids": sorted(spawned_lane_ids),
        "stdout_sha256": stdout_sha256,
        "stderr_sha256": stderr_sha256,
        "finished_utc": summary["finished_utc"],
        "lane_status_counts": counts,
        "missing_result_lane_ids": missing_result_lane_ids,
        "verified_hit": summary["verified_hit"],
        "verified_artifact_path": str(verified_artifact_path) if verified_artifact_path else None,
        "verified_artifact_sha256": verified_artifact_sha256,
    }


def _revalidate_main_evidence(
    evidence: Mapping[str, Any], state: Mapping[str, Any], plan: Mapping[str, Any]
) -> None:
    evidence = _require_keys(evidence, MAIN_REPORT_KEYS, "main terminal report")
    if evidence["schema_version"] != 1 or evidence["kind"] != "Q5_TRANCHE_MAIN_TERMINAL_REPORT":
        raise PermanentFailure("main terminal report schema mismatch")
    if evidence["tranche_id"] != TRANCHE_ID:
        raise PermanentFailure("main terminal report identity mismatch")
    _parse_time(evidence["accepted_utc"], "main report accepted_utc")
    _parse_time(evidence["finished_utc"], "main report finished_utc")
    status = evidence["status"]
    if status not in {"FINITE_NO_HIT", "TIMEOUT_INCOMPLETE", "VERIFIED_HIT"}:
        raise PermanentFailure("main terminal report status is malformed")
    counts = evidence["lane_status_counts"]
    if (
        not isinstance(counts, dict)
        or not counts
        or any(not isinstance(key, str) for key in counts)
        or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in counts.values()
        )
        or sum(counts.values()) != 64
    ):
        raise PermanentFailure("main terminal report lane counts are malformed")
    missing = evidence["missing_result_lane_ids"]
    if (
        not isinstance(missing, list)
        or any(
            isinstance(lane_id, bool)
            or not isinstance(lane_id, int)
            or not (0 <= lane_id < 64)
            for lane_id in missing
        )
        or len(set(missing)) != len(missing)
    ):
        raise PermanentFailure("main terminal report missing-result lanes are malformed")

    pinned_inventory = evidence["run_inventory"]
    if (
        not isinstance(pinned_inventory, dict)
        or any(
            not isinstance(name, str) or not isinstance(digest, str)
            or SHA256_RE.fullmatch(digest) is None
            for name, digest in pinned_inventory.items()
        )
        or _inventory(MAIN_RUN_DIR.resolve()) != pinned_inventory
    ):
        raise PermanentFailure("main run inventory drift")
    envelope, manifest_file_sha256 = _audit_main_manifest_stable(state, plan)
    payload = envelope["payload"]
    if evidence["manifest_path"] != str(MAIN_MANIFEST_PATH.resolve()):
        raise PermanentFailure("main report manifest path drift")
    if evidence["manifest_payload_sha256"] != envelope["payload_sha256"]:
        raise PermanentFailure("main report manifest payload drift")
    if evidence["manifest_file_sha256"] != manifest_file_sha256:
        raise PermanentFailure("main report manifest file drift")
    fixed = {
        "summary_path": (MAIN_RUN_DIR.resolve() / "supervisor_summary.json", "summary_sha256"),
        "final_state_path": (MAIN_RUN_DIR.resolve() / "supervisor_state.json", "final_state_sha256"),
        "launch_lock_path": (MAIN_RUN_DIR.resolve() / "launch.lock", "launch_lock_sha256"),
    }
    for path_field, (path, hash_field) in fixed.items():
        digest = evidence[hash_field]
        if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
            raise PermanentFailure(f"main report {hash_field} is malformed")
        if evidence[path_field] != str(path) or _sha256_file(path) != digest:
            raise PermanentFailure(f"main report {path_field}/{hash_field} drift")
    final_state_value, semantic_state_sha256 = _load_json_with_sha(
        MAIN_RUN_DIR.resolve() / "supervisor_state.json"
    )
    launch_value, semantic_launch_sha256 = _load_json_with_sha(
        MAIN_RUN_DIR.resolve() / "launch.lock"
    )
    if (
        semantic_state_sha256 != evidence["final_state_sha256"]
        or semantic_launch_sha256 != evidence["launch_lock_sha256"]
    ):
        raise PermanentFailure("main state/launch bytes drifted before semantic revalidation")
    launch_value = _validate_launch_lock_value(
        launch_value, payload, envelope["payload_sha256"], name="pinned main launch lock",
        expected_readiness_sha256=plan["launch_readiness"]["file_sha256"],
    )
    if (
        final_state_value.get("status") != status
        or final_state_value.get("anomaly") is not None
        or final_state_value.get("owned_pids") != []
        or launch_value["supervisor_pid"] != final_state_value.get("supervisor_pid")
    ):
        raise PermanentFailure("main state/launch semantics drifted")
    if evidence["selection_report_sha256"] != state["selection_report_sha256"]:
        raise PermanentFailure("main report/state selection pin mismatch")
    if _sha256_file(SELECTION_REPORT_PATH) != evidence["selection_report_sha256"]:
        raise PermanentFailure("main report selection pin drift")
    selection_report = _load_selection_report_pinned(state)
    public_gate = selection_report.get("public_status_gate")
    if not isinstance(public_gate, dict):
        raise PermanentFailure("main selection lost its public-status evidence")
    try:
        _revalidate_public_status_evidence(public_gate)
        _validate_authorization_ticket(
            phase="MAIN",
            lock=launch_value,
            payload=payload,
            payload_digest=envelope["payload_sha256"],
            manifest_path=MAIN_MANIFEST_PATH.resolve(),
            manifest_file_sha256=evidence["manifest_file_sha256"],
            run_dir=MAIN_RUN_DIR.resolve(),
            plan=plan,
            launch_claimed=_parse_time(
                launch_value["claimed_utc"], "pinned main launch claim"
            ),
            expected_public_status_sha256=public_gate["file_sha256"],
            expected_state_sha256=evidence["authorization_state_sha256"],
        )
    except TrancheError as exc:
        raise PermanentFailure(
            "main public-status/authorization evidence drift"
        ) from exc


    summary, semantic_summary_sha256 = _load_json_with_sha(
        MAIN_RUN_DIR.resolve() / "supervisor_summary.json"
    )
    if semantic_summary_sha256 != evidence["summary_sha256"]:
        raise PermanentFailure("main summary bytes drifted before semantic revalidation")
    lane_statuses = summary.get("lane_statuses")
    expected_ids = {str(index) for index in range(64)}
    if not isinstance(lane_statuses, dict) or set(lane_statuses) != expected_ids:
        raise PermanentFailure("main report summary lane identities drifted")
    summary_counts = {
        key: list(lane_statuses.values()).count(key)
        for key in sorted(set(lane_statuses.values()))
    }
    if (
        summary.get("status") != status
        or summary.get("finished_utc") != evidence["finished_utc"]
        or summary.get("verified_hit") != evidence["verified_hit"]
        or summary_counts != counts
    ):
        raise PermanentFailure("main report differs semantically from its summary")

    try:
        _validate_terminal_lane_state(
            payload=payload, lanes_state=final_state_value.get("lanes"),
            lane_statuses=lane_statuses, name="revalidated main",
        )
    except TrancheError as exc:
        raise PermanentFailure("main terminal lane state drift") from exc
    try:
        spawned_lane_ids = _validate_spawned_lane_ids(
            summary=summary, final_state=final_state_value, payload=payload,
            lane_statuses=lane_statuses, name="revalidated main",
        )
    except TrancheError as exc:
        raise PermanentFailure("main spawned-lane provenance drift") from exc
    if evidence["spawned_lane_ids"] != sorted(spawned_lane_ids):
        raise PermanentFailure("main spawned-lane pin drift")

    assigned_lanes = {
        str(lane["lane_id"]): lane for lane in payload["lanes"] if lane["specializations"]
    }
    assigned_ids = set(assigned_lanes)
    no_work = 64 - len(assigned_ids)
    if counts.get("NO_WORK", 0) != no_work:
        raise PermanentFailure("main report NO_WORK count differs from the manifest")
    if status == "FINITE_NO_HIT":
        expected_counts = {"NO_HIT": len(assigned_ids)}
        if no_work:
            expected_counts["NO_WORK"] = no_work
        if counts != expected_counts or missing or evidence["verified_hit"] is not None:
            raise PermanentFailure("main finite report lane contract mismatch")
    elif status == "TIMEOUT_INCOMPLETE":
        if (
            counts.get("TIMEOUT_INCOMPLETE", 0) < 1
            or evidence["verified_hit"] is not None
            or not set(counts).issubset({"NO_HIT", "NO_WORK", "TIMEOUT_INCOMPLETE"})
        ):
            raise PermanentFailure("main timeout report lane contract mismatch")
    else:
        if (
            counts.get("VERIFIED_HIT", 0) != 1
            or evidence["verified_hit"] is None
            or not set(counts).issubset(
                {
                    "NO_HIT", "NO_WORK", "VERIFIED_HIT",
                    "STOPPED_AFTER_VERIFIED_HIT",
                }
            )
        ):
            raise PermanentFailure("main verified report lane contract mismatch")

    result_hashes = evidence["result_sha256"]
    stdout_hashes = evidence["stdout_sha256"]
    stderr_hashes = evidence["stderr_sha256"]
    for hashes, field in (
        (result_hashes, "result_sha256"),
        (stdout_hashes, "stdout_sha256"),
        (stderr_hashes, "stderr_sha256"),
    ):
        if not isinstance(hashes, dict):
            raise PermanentFailure(f"main report {field} is malformed")
        for lane_id, digest in hashes.items():
            if (
                not isinstance(lane_id, str)
                or lane_id not in expected_ids
                or not isinstance(digest, str)
                or SHA256_RE.fullmatch(digest) is None
            ):
                raise PermanentFailure(f"main report {field} entry is malformed")
    result_ids = set(result_hashes)
    stdout_ids = set(stdout_hashes)
    stderr_ids = set(stderr_hashes)
    spawned_ids = {str(lane_id) for lane_id in spawned_lane_ids}
    missing_ids = {str(lane_id) for lane_id in missing}
    if (
        not missing_ids.issubset(assigned_ids)
        or stdout_ids != spawned_ids
        or stderr_ids != spawned_ids
        or result_ids != assigned_ids - missing_ids
        or not result_ids.issubset(spawned_ids)
    ):
        raise PermanentFailure("main report lane artifact sets are incomplete")
    verified_hit_record: dict[str, Any] | None = None
    if status == "VERIFIED_HIT":
        verified_hit_record = _validate_verified_hit(evidence["verified_hit"])
    validated_hit_lanes = 0
    for lane_id in result_ids:
        result_path = Path(assigned_lanes[lane_id]["result_path"]).resolve()
        result_value, result_digest = _load_json_with_sha(result_path)
        if result_digest != result_hashes[lane_id]:
            raise PermanentFailure(f"main result lane {lane_id} drift")
        result = supervisor_lib.validate_lane_result(
            result_value, payload=payload, payload_digest=envelope["payload_sha256"],
            lane=assigned_lanes[lane_id],
        )
        try:
            _validate_result_lane_binding(
                lane_id=int(lane_id),
                lane_status=lane_statuses[lane_id],
                result_status=result["status"],
                name="revalidated main",
            )
        except TrancheError as exc:
            raise PermanentFailure("main result/lane binding drift") from exc
        if status == "FINITE_NO_HIT":
            if result["status"] != "NO_HIT":
                raise PermanentFailure("main finite result status drift")
        elif status == "TIMEOUT_INCOMPLETE":
            if result["status"] not in {"NO_HIT", "TIMEOUT_INCOMPLETE"}:
                raise PermanentFailure("main timeout result status drift")
        else:
            if result["status"] == "HIT":
                if (
                    verified_hit_record is None
                    or int(lane_id) != verified_hit_record["lane_id"]
                ):
                    raise PermanentFailure("main HIT result lane drift")
                candidates = result["candidates"]
                if (
                    len(candidates) != 1
                    or candidates[0].get("integer_quadruple")
                    != verified_hit_record["integer_quadruple"]
                ):
                    raise PermanentFailure("main HIT candidate set drift")
                validated_hit_lanes += 1
            elif result["status"] != "NO_HIT":
                raise PermanentFailure("main verified peer result drift")
    if status == "VERIFIED_HIT" and validated_hit_lanes != 1:
        raise PermanentFailure("main verified HIT result count drift")

    run_dir = MAIN_RUN_DIR.resolve()
    for lane_id in stdout_ids:
        stdout_path = run_dir / f"lane_{int(lane_id):02d}.stdout.txt"
        if _sha256_file(stdout_path) != stdout_hashes[lane_id]:
            raise PermanentFailure(f"main stdout lane {lane_id} drift")
    for lane_id in stderr_ids:
        stderr_path = run_dir / f"lane_{int(lane_id):02d}.stderr.txt"
        if stderr_path.stat().st_size != 0 or _sha256_file(stderr_path) != stderr_hashes[lane_id]:
            raise PermanentFailure(f"main stderr lane {lane_id} drift")
    expected_results = {
        Path(assigned_lanes[lane_id]["result_path"]).resolve() for lane_id in result_ids
    }
    actual_results = {path.resolve() for path in run_dir.glob("lane_*.result.json")}
    if actual_results != expected_results:
        raise PermanentFailure("main result artifact set drift")
    expected_stderr = {
        run_dir / f"lane_{int(lane_id):02d}.stderr.txt" for lane_id in stderr_ids
    }
    actual_stderr = {path.resolve() for path in run_dir.glob("lane_*.stderr.txt")}
    if actual_stderr != expected_stderr:
        raise PermanentFailure("main stderr artifact set drift")
    if any(path.stat().st_size != 0 for path in run_dir.glob("*.stderr.txt")):
        raise PermanentFailure("main stderr content became nonempty")
    for lane_id in missing_ids:
        if status == "TIMEOUT_INCOMPLETE":
            expected_missing_status = "TIMEOUT_INCOMPLETE"
        elif status == "VERIFIED_HIT":
            expected_missing_status = "STOPPED_AFTER_VERIFIED_HIT"
        else:
            expected_missing_status = None
        if lane_statuses[lane_id] != expected_missing_status:
            raise PermanentFailure("main missing result has an inadmissible lane status")

    verified_paths = {
        path.resolve() for path in run_dir.glob("lane_*.candidate_*.verified.json")
    }
    verified_hit = evidence["verified_hit"]
    if verified_hit is None:
        if evidence["verified_artifact_path"] is not None or evidence["verified_artifact_sha256"] is not None:
            raise PermanentFailure("main report has a stray verified-artifact pin")
        if verified_paths:
            raise PermanentFailure("main non-hit report has a verified artifact")
    else:
        hit = _validate_verified_hit(verified_hit)
        expected_path = run_dir / (
            f"lane_{hit['lane_id']:02d}.candidate_{hit['candidate_index']:03d}.verified.json"
        )
        if evidence["verified_artifact_path"] != str(expected_path):
            raise PermanentFailure("main verified-artifact path drift")
        if verified_paths != {expected_path}:
            raise PermanentFailure("main verified-artifact set drift")
        verified_digest = evidence["verified_artifact_sha256"]
        verified_value, actual_verified_digest = _load_json_with_sha(expected_path)
        if (
            not isinstance(verified_digest, str)
            or SHA256_RE.fullmatch(verified_digest) is None
            or verified_value != hit
            or actual_verified_digest != verified_digest
        ):
            raise PermanentFailure("main verified-artifact content/hash drift")
    verified_path_for_inventory = (
        Path(evidence["verified_artifact_path"])
        if isinstance(evidence["verified_artifact_path"], str)
        else None
    )
    result_paths_for_inventory = {
        int(lane_id): Path(assigned_lanes[lane_id]["result_path"])
        for lane_id in result_ids
    }
    try:
        current_inventory, exact_stdout_sha256, exact_stderr_sha256 = (
            _validate_exact_run_inventory(
                run_dir=run_dir,
                spawned_lane_ids=spawned_lane_ids,
                result_paths=result_paths_for_inventory,
                verified_artifact_path=verified_path_for_inventory,
                name="revalidated main",
            )
        )
    except TrancheError as exc:
        raise PermanentFailure("main exact run inventory drift") from exc
    if (
        current_inventory != pinned_inventory
        or exact_stdout_sha256 != stdout_hashes
        or exact_stderr_sha256 != stderr_hashes
    ):
        raise PermanentFailure("main stream/inventory pins drift")
    try:
        _current_clean_census(plan, _now_utc, None)
    except TrancheError as exc:
        raise PermanentFailure("main live clean census revalidation failed") from exc


def _accept_main_action(
    commit: Callable[..., dict[str, Any]],
    fail_closed: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    clock = _now_utc
    census_hook: CensusHook | None = None
    lock, plan, state = _load_context()
    already_terminal = {
        "MAIN_FINITE_NO_HIT", "MAIN_TIMEOUT_INCOMPLETE", "VERIFIED_HIT"
    }
    if (
        state["phase"] in already_terminal
        and state["main_terminal_report_sha256"] is not None
    ):
        evidence, report_sha256 = _load_json_with_sha(MAIN_TERMINAL_REPORT_PATH)
        if report_sha256 != state["main_terminal_report_sha256"]:
            raise PermanentFailure("accepted main report differs from the state pin")
        expected_phase = {
            "FINITE_NO_HIT": "MAIN_FINITE_NO_HIT",
            "TIMEOUT_INCOMPLETE": "MAIN_TIMEOUT_INCOMPLETE",
            "VERIFIED_HIT": "VERIFIED_HIT",
        }.get(evidence.get("status"))
        if expected_phase != state["phase"]:
            raise PermanentFailure("accepted main report status/phase mismatch")
        _revalidate_accepted_artifacts(state, plan)
        _revalidate_main_evidence(evidence, state, plan)
        if state["phase"] == "VERIFIED_HIT" and state["verified_hit"] != _main_hit_binding(evidence, report_sha256):
            raise PermanentFailure("accepted main hit differs from the state")
        return {
            "ok": True,
            "already_accepted": True,
            "phase": state["phase"],
            "status": evidence["status"],
            "main_terminal_report_path": str(MAIN_TERMINAL_REPORT_PATH),
            "main_terminal_report_sha256": report_sha256,
        }
    if state["phase"] != "MAIN_FROZEN":
        raise PermanentFailure(f"main cannot be accepted from phase {state['phase']}")
    now = _aware_utc(clock(), "clock")
    try:
        _validate_transition_clock(state, now, lock)
        _revalidate_accepted_artifacts(state, plan)
        evidence = _validate_main_evidence(state, plan, clock, census_hook)

        commit_now = _aware_utc(clock(), "main commit clock")
        _validate_transition_clock(state, commit_now, lock)
        _revalidate_accepted_artifacts(state, plan)
        _revalidate_main_evidence(evidence, state, plan)
        report_bytes = _pretty_bytes(evidence)
        report_sha256 = hashlib.sha256(report_bytes).hexdigest()
        phase = {
            "FINITE_NO_HIT": "MAIN_FINITE_NO_HIT",
            "TIMEOUT_INCOMPLETE": "MAIN_TIMEOUT_INCOMPLETE",
            "VERIFIED_HIT": "VERIFIED_HIT",
        }[evidence["status"]]
        updates: dict[str, Any] = {"main_terminal_report_sha256": report_sha256}
        if phase == "VERIFIED_HIT":
            updates["verified_hit"] = _main_hit_binding(evidence, report_sha256)
        new_state = commit(
            state, phase=phase, now=commit_now, updates=updates,
            extra_files={MAIN_TERMINAL_REPORT_PATH: report_bytes},
        )
        return {
            "ok": True,
            "already_accepted": False,
            "phase": new_state["phase"],
            "status": evidence["status"],
            "main_terminal_report_path": str(MAIN_TERMINAL_REPORT_PATH),
            "main_terminal_report_sha256": report_sha256,
        }
    except TrancheNotReady:
        raise
    except BaseException as exc:
        fail_closed(state, exc, now)
        raise PermanentFailure(f"main validation failed permanently: {exc}") from exc

def _install_mutating_routes() -> tuple[
    Callable[[], dict[str, Any]],
    Callable[[str], dict[str, Any]],
    Callable[[], dict[str, Any]],
    Callable[[], dict[str, Any]],
]:
    """Close every high-level state writer over a non-exported capability."""

    claim_lock_action = _claim_lock_action
    commit_initial_action = _commit_initial_action
    transition_action = _transition_action
    fail_closed_action = _fail_closed_action
    start_action = _start_tranche_action
    pilot_action = _accept_pilot_action
    finalize_action = _finalize_selection_action
    main_action = _accept_main_action

    legal_edges = {
        "READY_A": {"READY_B", "VERIFIED_HIT", "FAIL_CLOSED"},
        "READY_B": {"READY_C", "VERIFIED_HIT", "FAIL_CLOSED"},
        "READY_C": {"READY_D", "VERIFIED_HIT", "FAIL_CLOSED"},
        "READY_D": {"READY_SELECTION", "VERIFIED_HIT", "FAIL_CLOSED"},
        "READY_SELECTION": {"MAIN_FROZEN", "NO_MAIN", "FAIL_CLOSED"},
        "MAIN_FROZEN": {
            "MAIN_FINITE_NO_HIT", "MAIN_TIMEOUT_INCOMPLETE",
            "VERIFIED_HIT", "FAIL_CLOSED",
        },
    }

    def claim_lock(
        t0: datetime,
        magic: Mapping[str, Any],
        artifact_hashes: Mapping[str, str],
        readiness_sha256: str,
    ) -> dict[str, Any]:
        return claim_lock_action(
            t0, magic, artifact_hashes, readiness_sha256
        )

    def commit_initial(
        plan: dict[str, Any], state: dict[str, Any]
    ) -> dict[str, Any]:
        if (
            state.get("revision") != 0
            or state.get("phase") not in {"READY_A", "VERIFIED_HIT", "FAIL_CLOSED"}
        ):
            raise PermanentFailure("initial tranche state is not a legal root")
        return commit_initial_action(plan, state)

    def commit(
        state: dict[str, Any],
        *,
        phase: str,
        now: datetime,
        updates: Mapping[str, Any] | None = None,
        extra_files: Mapping[Path, bytes] | None = None,
    ) -> dict[str, Any]:
        _validate_state_shape(state)
        if phase not in legal_edges.get(state["phase"], set()):
            raise PermanentFailure(
                f"illegal tranche phase edge {state['phase']} -> {phase}"
            )
        return transition_action(
            state, phase=phase, now=now, updates=updates,
            extra_files=extra_files,
        )

    def fail_closed(
        state: dict[str, Any], error: BaseException, now: datetime
    ) -> dict[str, Any]:
        return fail_closed_action(commit, state, error, now)

    def start_tranche() -> dict[str, Any]:
        return start_action(claim_lock, commit_initial)

    def accept_pilot(pilot: str) -> dict[str, Any]:
        if pilot not in PILOT_ORDER:
            raise TrancheError(f"unknown pilot: {pilot}")
        return pilot_action(commit, fail_closed, pilot)

    def finalize_selection() -> dict[str, Any]:
        return finalize_action(commit, fail_closed)

    def accept_main() -> dict[str, Any]:
        return main_action(commit, fail_closed)

    return start_tranche, accept_pilot, finalize_selection, accept_main


start_tranche, accept_pilot, finalize_selection, accept_main = (
    _install_mutating_routes()
)
del (
    _install_mutating_routes,
    _claim_lock_action,
    _commit_initial_action,
    _transition_action,
    _fail_closed_action,
    _start_tranche_action,
    _accept_pilot_action,
    _finalize_selection_action,
    _accept_main_action,
)



def _audit_plan(plan: Mapping[str, Any], state: Mapping[str, Any]) -> None:
    expected_keys = {
        "schema_version", "kind", "tranche_id", "t0", "s", "g", "magic_terminal",
        "launch_readiness", "authorization_paths",
        "preflight_censuses", "frozen_artifact_hashes", "pilots", "main",
        "candidate_table", "selection_rule", "setup_guard_milliseconds", "global_lock_sha256",
    }
    _require_keys(plan, expected_keys, "tranche plan")
    if plan["schema_version"] != 1 or plan["kind"] != "Q5_TRANCHE_PLAN" or plan["tranche_id"] != TRANCHE_ID:
        raise PermanentFailure("tranche plan identity mismatch")
    try:
        current_magic = _validate_magic_terminal()
    except TrancheError as exc:
        raise PermanentFailure("magic terminal prerequisite no longer validates") from exc
    if current_magic != plan["magic_terminal"]:
        raise PermanentFailure("magic terminal prerequisite differs from its T0 pin")
    expected_authorizations = {
        phase: str(_authorization_path(phase)) for phase in (*PILOT_ORDER, "MAIN")
    }
    if plan["authorization_paths"] != expected_authorizations:
        raise PermanentFailure("tranche authorization paths drift")
    if plan["launch_readiness"] != {
        "path": str(READINESS_PATH.resolve()), "file_sha256": _sha256_file(READINESS_PATH)
    }:
        raise PermanentFailure("tranche launch readiness drift")
    if plan["setup_guard_milliseconds"] != 300000:
        raise PermanentFailure("tranche setup guard drift")
    _candidate_table(plan)
    accepted_names = list(state["accepted_pilots"])
    if accepted_names != list(PILOT_ORDER[: len(accepted_names)]):
        raise PermanentFailure("accepted pilot sequence is not an A/B/C/D prefix")
    _revalidate_accepted_artifacts(state, plan)


def audit_tranche() -> dict[str, Any]:
    lock, plan, state = _load_context()
    _audit_plan(plan, state)
    phase = state["phase"]
    _validate_verified_hit_binding(state)
    expected_count = {
        "READY_A": 0, "READY_B": 1, "READY_C": 2, "READY_D": 3,
        "READY_SELECTION": 4, "MAIN_FROZEN": 4, "MAIN_FINITE_NO_HIT": 4,
        "MAIN_TIMEOUT_INCOMPLETE": 4, "NO_MAIN": 4,
    }.get(phase)
    if phase == "VERIFIED_HIT":
        binding = state["verified_hit"]
        if binding["source"] == "magic":
            expected_count = 0
        elif binding["source"] == "pilot":
            expected_count = PILOT_ORDER.index(binding["source_id"]) + 1
        else:
            expected_count = 4
    if expected_count is not None and len(state["accepted_pilots"]) != expected_count:
        raise PermanentFailure("state phase and accepted-pilot count disagree")
    has_main_terminal_report = state["main_terminal_report_sha256"] is not None
    if phase == "VERIFIED_HIT" and not has_main_terminal_report:
        binding = state["verified_hit"]
        if binding["source"] == "magic":
            expected_binding = _magic_hit_binding(plan["magic_terminal"])
        elif binding["source"] == "pilot":
            pilot = binding["source_id"]
            expected_binding = _pilot_hit_binding(
                pilot, state["accepted_pilots"][pilot]
            )
        else:
            raise PermanentFailure("main hit lacks its terminal report pin")
        if binding != expected_binding:
            raise PermanentFailure("verified-hit state differs from source evidence")
    selection_phases = {
        "MAIN_FROZEN", "MAIN_FINITE_NO_HIT", "MAIN_TIMEOUT_INCOMPLETE", "NO_MAIN"
    }
    if phase == "VERIFIED_HIT" and has_main_terminal_report:
        selection_phases.add("VERIFIED_HIT")
    if phase in selection_phases:
        report = _load_json(SELECTION_REPORT_PATH)
        if _sha256_file(SELECTION_REPORT_PATH) != state["selection_report_sha256"]:
            raise PermanentFailure("selection report differs from the state pin")
        report = _require_keys(
            report,
            {
                "schema_version", "kind", "tranche_id", "t0", "s", "g",
                "pilot_evidence", "candidate_table", "generated_utc",
                "selection_setup_deadline_utc",
                "remaining_before_s_milliseconds", "setup_guard_milliseconds",
                "timing_records", "rho", "selected_h", "selected_main_manifest_path",
                "selected_main_manifest_sha256", "public_status_gate",
            },
            "selection report",
        )
        if report["schema_version"] != 1 or report["kind"] != "Q5_TRANCHE_SELECTION_REPORT":
            raise PermanentFailure("selection report schema mismatch")
        if report["pilot_evidence"] != state["accepted_pilots"]:
            raise PermanentFailure("selection report pilot evidence mismatch")
        generated = _parse_time(report["generated_utc"], "selection report generated_utc")
        ready_anchor = _ready_selection_anchor(state)
        if generated != ready_anchor:
            raise PermanentFailure(
                "selection report does not use the original READY_SELECTION anchor"
            )
        recomputed = _selection_core(
            state, plan, generated, ready_selection_anchor=ready_anchor
        )
        for key in (
            "generated_utc", "selection_setup_deadline_utc", "remaining_before_s_milliseconds", "setup_guard_milliseconds",
            "timing_records", "rho", "selected_h",
        ):
            if report[key] != recomputed[key]:
                raise PermanentFailure(f"selection report {key} mismatch")
        if report["candidate_table"].get("rows") != recomputed["candidates"]:
            raise PermanentFailure("selection report candidate rows mismatch")
        if report["selected_h"] != state["selected_h"] or report["selected_main_manifest_sha256"] != state["selected_main_manifest_sha256"]:
            raise PermanentFailure("selection report/state selection mismatch")
        if phase != "NO_MAIN":
            if state["selected_h"] is None or state["selected_main_manifest_sha256"] is None:
                raise PermanentFailure("MAIN_FROZEN lacks a selected manifest")
            try:
                envelope = manifest_lib.audit_manifest(
                    MAIN_MANIFEST_PATH.resolve(),
                    expected_digest=state["selected_main_manifest_sha256"],
                    expected_campaign_id=MAIN_CAMPAIGN_ID,
                )
            except manifest_lib.ManifestError as exc:
                raise PermanentFailure(f"frozen main manifest audit failed: {exc}") from exc
            if envelope["payload"]["deadline"] != state["s"]:
                raise PermanentFailure("frozen main deadline drift")
        elif any(
            value is not None for value in (state["selected_h"], state["selected_main_manifest_sha256"])
        ):
            raise PermanentFailure("NO_MAIN carries a selected manifest")
    main_terminal_phases = {"MAIN_FINITE_NO_HIT", "MAIN_TIMEOUT_INCOMPLETE"}
    if phase == "VERIFIED_HIT" and has_main_terminal_report:
        main_terminal_phases.add("VERIFIED_HIT")
    if phase in main_terminal_phases:
        report, report_sha256 = _load_json_with_sha(MAIN_TERMINAL_REPORT_PATH)
        if report_sha256 != state["main_terminal_report_sha256"]:
            raise PermanentFailure("main terminal report differs from the state pin")
        _revalidate_main_evidence(report, state, plan)
        expected_phase = {
            "FINITE_NO_HIT": "MAIN_FINITE_NO_HIT",
            "TIMEOUT_INCOMPLETE": "MAIN_TIMEOUT_INCOMPLETE",
            "VERIFIED_HIT": "VERIFIED_HIT",
        }.get(report["status"])
        if expected_phase != phase:
            raise PermanentFailure("main terminal report status/phase mismatch")
        if phase == "VERIFIED_HIT" and state["verified_hit"] != _main_hit_binding(report, report_sha256):
            raise PermanentFailure("main verified hit differs from the state")
    elif has_main_terminal_report:
        raise PermanentFailure("non-main-terminal phase carries a main report")
    if phase in {"MAIN_FINITE_NO_HIT", "MAIN_TIMEOUT_INCOMPLETE"} and not has_main_terminal_report:
        raise PermanentFailure("main terminal phase lacks its report")
    if phase == "FAIL_CLOSED" and not isinstance(state["persistent_error"], str):
        raise PermanentFailure("FAIL_CLOSED lacks its persistent error")
    return {
        "ok": phase != "FAIL_CLOSED",
        "phase": phase,
        "revision": state["revision"],
        "t0": lock["t0"],
        "s": lock["s"],
        "g": lock["g"],
        "accepted_pilots": list(state["accepted_pilots"]),
        "selected_h": state["selected_h"],
        "selected_main_manifest_sha256": state["selected_main_manifest_sha256"],
        "main_terminal_report_sha256": state["main_terminal_report_sha256"],
        "persistent_error": state["persistent_error"],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("start")
    authorize = commands.add_parser("authorize")
    authorize.add_argument("phase", choices=(*PILOT_ORDER, "MAIN"))
    accept = commands.add_parser("accept-pilot")
    accept.add_argument("pilot", choices=PILOT_ORDER)
    commands.add_parser("preview")
    commands.add_parser("accept-main")
    commands.add_parser("finalize")
    commands.add_parser("audit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "start":
            report = start_tranche()
        elif args.command == "accept-pilot":
            report = accept_pilot(args.pilot)
        elif args.command == "authorize":
            report = authorize_launch(args.phase)
        elif args.command == "accept-main":
            report = accept_main()
        elif args.command == "preview":
            report = preview_selection()
        elif args.command == "finalize":
            report = finalize_selection()
        else:
            report = audit_tranche()
        print(json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        return 0 if report.get("ok", False) else 2
    except TrancheNotReady as exc:
        print(json.dumps({"ok": False, "status": "NOT_READY", "error": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 3
    except (TrancheError, manifest_lib.ManifestError, supervisor_lib.SupervisorError) as exc:
        print(json.dumps({"ok": False, "status": "FAIL_CLOSED", "error": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
