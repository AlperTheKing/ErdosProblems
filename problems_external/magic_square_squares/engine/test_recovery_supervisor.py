#!/usr/bin/env python3
"""Bounded process and preflight tests for the fail-closed recovery mode."""

from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path
import sys
import threading
import time
import unittest
from unittest import mock
import uuid

import recovery_supervisor as recovery
import tranche_supervisor as base


ENGINE_DIR = Path(__file__).resolve().parent
DUMMY = ENGINE_DIR / "dummy_recovery_worker.py"

def test_run_dir(label: str) -> Path:
    root = ENGINE_DIR / "calibration" / "recovery_selftest"
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{label}-{uuid.uuid4().hex}"
    path.mkdir()
    return path


def retained_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for lane_id in sorted(recovery.RETAINED_LANE_IDS):
        records.append({
            "lane": lane_id,
            "family": lane_id[0],
            "source": "retained_dummy",
            "source_run_id": recovery.ORIGINAL_RUN_ID,
            "owned": False,
            "pid": None,
            "single_thread_search": True,
            "command": [],
            "cwd": str(ENGINE_DIR),
            "stdout": "",
            "stderr": "",
            "engine_summary": "",
            "started_utc": None,
            "finished_utc": None,
            "return_code": 0,
            "status": "NO_HIT",
            "raw_status": "DUMMY_RETAINED",
            "status_detail": {},
        })
    return records


def prefix_checkpoints() -> dict[str, dict[str, object]]:
    values: dict[str, dict[str, object]] = {}
    for lane_id in sorted(recovery.RECOVERED_LANE_IDS):
        if lane_id[0] in "GN":
            values[lane_id] = {
                "range_start": "100",
                "range_end": "199",
                "next_m": "150",
                "processed_centers": "50",
                "status": "RUNNING" if lane_id != "N14" else "FAILED",
            }
    return values


def dummy_specs(
    run_dir: Path,
    *,
    hit_lane: str | None = None,
    regular_delay: float = 0.02,
    hit_delay: float = 0.01,
    forced_nonzero_lane: str | None = None,
    grandchild_lane: str | None = None,
) -> list[base.LaneSpec]:
    specs: list[base.LaneSpec] = []
    for lane_id in sorted(recovery.RECOVERED_LANE_IDS):
        lane_dir = run_dir / "lanes" / lane_id
        summary = lane_dir / "engine" / "summary.json"
        status = "HIT_VERIFIED" if lane_id == hit_lane else "NO_HIT"
        delay = hit_delay if lane_id == hit_lane else regular_delay
        command = [
            sys.executable, str(DUMMY), "--lane", lane_id,
            "--summary", str(summary), "--delay", str(delay),
            "--status", status, "--threads", "1",
        ]
        if lane_id[0] in "GN":
            command.extend([
                "--start", "150", "--deadline-unix",
                str(int(recovery.ORIGINAL_DEADLINE_UNIX)),
            ])
        if lane_id == forced_nonzero_lane:
            command.extend(["--forced-exit-code", "7"])
        if lane_id == grandchild_lane:
            command.extend([
                "--spawn-grandchild-pids", str(run_dir / "descendant_pids.json")
            ])
        specs.append(base.LaneSpec(
            lane_id=lane_id,
            family=lane_id[0],
            command=tuple(command),
            cwd=ENGINE_DIR,
            summary_kind="standard",
            engine_summary=summary,
            stdout_path=lane_dir / "recovery.stdout.txt",
            stderr_path=lane_dir / "recovery.stderr.txt",
        ))
    recovery.validate_recovery_specs(specs)
    return specs


class RecoverySupervisorTests(unittest.TestCase):
    def test_atomic_first_publication_retries_transient_access_denied(self) -> None:
        run_dir = test_run_dir("atomic-first-publication")
        target = run_dir / "state.json"
        real_replace = os.replace
        calls = 0

        def fail_once(source: object, destination: object) -> None:
            nonlocal calls
            calls += 1
            if calls == 1:
                error = PermissionError(13, "synthetic first-publication denial")
                error.winerror = 5
                raise error
            real_replace(source, destination)

        with mock.patch.object(recovery.os, "replace", side_effect=fail_once):
            recovery.atomic_write_json(target, {"sequence": 1})
        self.assertEqual(calls, 2)
        self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"sequence": 1})
        self.assertEqual(list(run_dir.glob(f".{target.name}.*.tmp")), [])

    def test_atomic_persistent_access_denied_exhausts_128_attempts(self) -> None:
        run_dir = test_run_dir("atomic-persistent-denial")
        target = run_dir / "state.json"
        calls = 0

        def always_deny(source: object, destination: object) -> None:
            nonlocal calls
            calls += 1
            error = PermissionError(13, "synthetic persistent denial")
            error.winerror = 5
            raise error

        with (
            mock.patch.object(recovery.os, "replace", side_effect=always_deny),
            mock.patch.object(recovery.time, "sleep", return_value=None),
            self.assertRaises(PermissionError),
        ):
            recovery.atomic_write_json(target, {"sequence": 1})
        self.assertEqual(calls, 128)
        self.assertFalse(target.exists())
        self.assertEqual(list(run_dir.glob(f".{target.name}.*.tmp")), [])
    def test_atomic_replacement_waits_for_fixed_exclusive_lock(self) -> None:
        if os.name != "nt":
            self.skipTest("Win32 sharing semantics test")
        import ctypes

        run_dir = test_run_dir("atomic-fixed-lock")
        target = run_dir / "state.json"
        recovery.atomic_write_json(target, {"sequence": -1})
        create_file = ctypes.windll.kernel32.CreateFileW
        create_file.restype = ctypes.c_void_p
        invalid = ctypes.c_void_p(-1).value
        real_replace = os.replace

        for sequence in range(20):
            acquired = threading.Event()
            locker_errors: list[str] = []

            def lock_once() -> None:
                handle = create_file(
                    str(target), 0x80000000, 0x00000001 | 0x00000002,
                    None, 3, 0x80, None,
                )
                if not handle or handle == invalid:
                    locker_errors.append("CreateFileW failed")
                    acquired.set()
                    return
                acquired.set()
                time.sleep(0.1)
                ctypes.windll.kernel32.CloseHandle(ctypes.c_void_p(handle))

            locker = threading.Thread(target=lock_once, daemon=True)
            locker.start()
            self.assertTrue(acquired.wait(timeout=2.0))
            calls = 0

            def counting_replace(source: object, destination: object) -> None:
                nonlocal calls
                calls += 1
                real_replace(source, destination)

            with mock.patch.object(
                recovery.os, "replace", side_effect=counting_replace
            ):
                recovery.atomic_write_json(target, {"sequence": sequence})
            locker.join(timeout=2.0)
            self.assertFalse(locker.is_alive())
            self.assertEqual(locker_errors, [])
            self.assertGreaterEqual(calls, 2)
        self.assertEqual(
            json.loads(target.read_text(encoding="utf-8")), {"sequence": 19}
        )
        self.assertEqual(list(run_dir.glob(f".{target.name}.*.tmp")), [])

    def test_atomic_publication_with_concurrent_readers(self) -> None:
        run_dir = test_run_dir("atomic-concurrent-readers")
        target = run_dir / "state.json"
        stop = threading.Event()
        errors: list[str] = []
        valid_reads = 0
        valid_reads_lock = threading.Lock()

        def reader() -> None:
            nonlocal valid_reads
            while not stop.is_set():
                try:
                    value = json.loads(target.read_text(encoding="utf-8"))
                    if not isinstance(value, dict) or not isinstance(value.get("sequence"), int):
                        errors.append("reader observed invalid JSON object")
                        return
                    with valid_reads_lock:
                        valid_reads += 1
                except FileNotFoundError:
                    pass
                except PermissionError as error:
                    if (
                        getattr(error, "winerror", None) not in {5, 32, 33}
                        and getattr(error, "errno", None) != 13
                    ):
                        errors.append(repr(error))
                        return
                except BaseException as error:
                    errors.append(repr(error))
                    return
                time.sleep(0.001)

        readers = [threading.Thread(target=reader, daemon=True) for _ in range(4)]
        for thread in readers:
            thread.start()
        try:
            for sequence in range(300):
                recovery.atomic_write_json(target, {"sequence": sequence})
        finally:
            stop.set()
            for thread in readers:
                thread.join(timeout=2.0)
        self.assertEqual(errors, [])
        self.assertGreaterEqual(valid_reads, 2)
        self.assertEqual(
            json.loads(target.read_text(encoding="utf-8")), {"sequence": 299}
        )
        self.assertEqual(list(run_dir.glob(f".{target.name}.*.tmp")), [])
    def test_current_failure_preflight_and_suffix_commands(self) -> None:
        preflight = recovery.validate_original_failure(
            ENGINE_DIR, require_approved_engine=False, require_dead_workers=False
        )
        self.assertEqual(len(preflight.retained_records), 19)
        self.assertEqual(len(preflight.prefix_checkpoints), 32)
        self.assertEqual(preflight.prefix_checkpoints["N14"]["status"], "FAILED")
        run_dir = test_run_dir("specs")
        specs = recovery.recovery_specs(
            ENGINE_DIR, run_dir, remaining_seconds=60.0,
            prefix_checkpoints=preflight.prefix_checkpoints,
        )
        self.assertEqual(len(specs), 45)
        for spec in specs:
            command = list(spec.command)
            if spec.family in {"G", "N"}:
                self.assertNotIn("--resume", command)
                self.assertEqual(
                    command[command.index("--start") + 1],
                    preflight.prefix_checkpoints[spec.lane_id]["next_m"],
                )
                self.assertEqual(
                    command[command.index("--deadline-unix") + 1],
                    str(int(recovery.ORIGINAL_DEADLINE_UNIX)),
                )
            else:
                self.assertEqual(command[command.index("--time-limit-seconds") + 1], "60.000000")

    def test_staging_preserves_failed_n14_prefix_and_original_tree(self) -> None:
        preflight = recovery.validate_original_failure(
            ENGINE_DIR, require_approved_engine=False, require_dead_workers=False
        )
        before = recovery.artifact_inventory(preflight.original_run_dir)
        staged = dataclasses.replace(
            preflight, recovery_run_dir=(
                ENGINE_DIR / "calibration" / "recovery_selftest" /
                f"staged-{uuid.uuid4().hex}"
            )
        )
        run_dir = recovery.reserve_and_stage(staged)
        n14 = json.loads(
            (run_dir / "lanes" / "N14" / "prefix_checkpoint.json").read_text(
                encoding="utf-8"
            )
        )
        provenance = json.loads(
            (run_dir / "lanes" / "N14" / "prefix_provenance.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(n14["status"], "FAILED")
        self.assertTrue(provenance["n14_failed_status_retained_as_provenance"])
        self.assertFalse((run_dir / "lanes" / "N14" / "engine" / "summary.json").exists())
        self.assertEqual(before, recovery.artifact_inventory(preflight.original_run_dir))

    def test_45_dummy_suffixes_merge_with_19_retained_results(self) -> None:
        run_dir = test_run_dir("dummy-all-no-hit")
        code = recovery.run_recovery_specs(
            dummy_specs(run_dir), retained_records(), run_dir, ENGINE_DIR,
            deadline_unix=time.time() + 20.0,
            original_inventory=None, original_run_dir=None,
            prefix_checkpoints=prefix_checkpoints(),
        )
        summary = json.loads(
            (run_dir / "recovery_summary.json").read_text(encoding="utf-8")
        )
        self.assertEqual(code, 0)
        self.assertEqual(summary["status"], "NO_HIT_DECLARED_DOMAINS")
        self.assertEqual(summary["combined_lane_count"], 64)
        self.assertEqual(summary["workers_launched_recovery"], 45)
        self.assertEqual(summary["retained_completed_lanes"], 19)
        self.assertEqual(summary["lane_status_counts"], {"NO_HIT": 64})
        self.assertEqual(summary["nonempty_recovery_stderr_lanes"], [])
        self.assertEqual(summary["source_portfolio_status"], "FAILED")
        n14 = next(row for row in summary["lanes"] if row["lane"] == "N14")
        self.assertEqual(
            n14["status_detail"]["coverage"]["method"],
            "immutable_committed_prefix_plus_explicit_suffix",
        )

    def test_repeated_45_child_lifecycle_has_no_missing_summary_or_survivor(self) -> None:
        for iteration in range(3):
            run_dir = test_run_dir(f"dummy-repeat-{iteration}")
            code = recovery.run_recovery_specs(
                dummy_specs(run_dir, regular_delay=0.0),
                retained_records(), run_dir, ENGINE_DIR,
                deadline_unix=time.time() + 20.0,
                original_inventory=None, original_run_dir=None,
                prefix_checkpoints=prefix_checkpoints(),
            )
            summary = json.loads(
                (run_dir / "recovery_summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(code, 0)
            self.assertEqual(summary["lane_status_counts"], {"NO_HIT": 64})
            self.assertEqual(summary["owned_process_survivors"], [])
            self.assertEqual(summary["unverified_stop_lanes"], [])
            self.assertEqual(summary["dead_root_failures"], [])
            self.assertEqual(list(run_dir.rglob(".*.tmp")), [])
    def test_nonzero_exit_cannot_validate_no_hit_summary(self) -> None:
        run_dir = test_run_dir("dummy-nonzero-no-hit")
        code = recovery.run_recovery_specs(
            dummy_specs(run_dir, forced_nonzero_lane="G01"),
            retained_records(), run_dir, ENGINE_DIR,
            deadline_unix=time.time() + 20.0,
            original_inventory=None, original_run_dir=None,
            prefix_checkpoints=prefix_checkpoints(),
        )
        summary = json.loads(
            (run_dir / "recovery_summary.json").read_text(encoding="utf-8")
        )
        self.assertEqual(code, 3)
        self.assertEqual(summary["status"], "FAILED")
        g01 = next(row for row in summary["lanes"] if row["lane"] == "G01")
        self.assertEqual(g01["status"], "FAILED")
        self.assertIn("return code zero", g01["status_detail"]["error"])

    def test_nonzero_exit_cannot_validate_hit_summary(self) -> None:
        gate_calls = 0

        def accepting_gate(*args: object) -> tuple[bool, dict[str, object]]:
            nonlocal gate_calls
            gate_calls += 1
            return True, {"accepted": True, "dummy": True}

        run_dir = test_run_dir("dummy-nonzero-hit")
        code = recovery.run_recovery_specs(
            dummy_specs(
                run_dir, hit_lane="G01", forced_nonzero_lane="G01"
            ),
            retained_records(), run_dir, ENGINE_DIR,
            deadline_unix=time.time() + 20.0,
            original_inventory=None, original_run_dir=None,
            prefix_checkpoints=prefix_checkpoints(),
            verifier_gate=accepting_gate,
        )
        summary = json.loads(
            (run_dir / "recovery_summary.json").read_text(encoding="utf-8")
        )
        self.assertEqual(code, 3)
        self.assertEqual(summary["status"], "FAILED")
        self.assertEqual(gate_calls, 0)
        g01 = next(row for row in summary["lanes"] if row["lane"] == "G01")
        self.assertEqual(g01["status"], "FAILED")
        self.assertIn("return code zero", g01["status_detail"]["error"])
    def test_deadline_before_spawn_and_existing_run_once_refuse(self) -> None:
        run_dir = test_run_dir("deadline-refusal")
        specs = dummy_specs(run_dir)
        with self.assertRaises(recovery.RecoveryRefused):
            recovery.run_recovery_specs(
                specs, retained_records(), run_dir, ENGINE_DIR,
                deadline_unix=time.time() - 1.0,
                original_inventory=None, original_run_dir=None,
                prefix_checkpoints=prefix_checkpoints(),
            )
        self.assertFalse(any(run_dir.rglob("recovery.stdout.txt")))

        preflight = recovery.validate_original_failure(
            ENGINE_DIR, require_approved_engine=False, require_dead_workers=False
        )
        existing = test_run_dir("existing-run-once")
        staged = dataclasses.replace(preflight, recovery_run_dir=existing)
        with self.assertRaises(recovery.RecoveryRefused):
            recovery.reserve_and_stage(staged)
    def test_dummy_verified_hit_stops_only_owned_recovery_workers(self) -> None:
        def accepting_gate(*args: object) -> tuple[bool, dict[str, object]]:
            return True, {"accepted": True, "dummy": True}

        run_dir = test_run_dir("dummy-hit")
        denied = mock.Mock(returncode=1, stdout=b"", stderr=b"ERROR: Access denied")
        with mock.patch.object(recovery.subprocess, "run", return_value=denied):
            code = recovery.run_recovery_specs(
                dummy_specs(
                    run_dir, hit_lane="G01", regular_delay=5.0,
                    grandchild_lane="G02",
                ),
                retained_records(), run_dir, ENGINE_DIR,
                deadline_unix=time.time() + 20.0,
                original_inventory=None, original_run_dir=None,
                prefix_checkpoints=prefix_checkpoints(),
                verifier_gate=accepting_gate,
            )
        summary = json.loads(
            (run_dir / "recovery_summary.json").read_text(encoding="utf-8")
        )
        self.assertEqual(code, 0)
        self.assertEqual(summary["status"], "HIT_VERIFIED")
        self.assertEqual(summary["hit_lane"], "G01")
        self.assertIn("STOPPED_AFTER_OTHER_HIT", summary["lane_status_counts"])
        self.assertEqual(summary["nonempty_recovery_stderr_lanes"], [])
        descendant_pids = json.loads(
            (run_dir / "descendant_pids.json").read_text(encoding="utf-8")
        )
        import psutil
        for pid in descendant_pids.values():
            self.assertFalse(psutil.pid_exists(int(pid)), f"descendant PID {pid} survived")
        g02 = next(row for row in summary["lanes"] if row["lane"] == "G02")
        stop = g02["status_detail"]["stop_evidence"]
        self.assertTrue(stop["shutdown_verified"])
        self.assertEqual(stop["taskkill_exit"], 1)
        self.assertTrue(
            stop["psutil_fallback"]["root_suspended_before_resnapshot"]
        )

if __name__ == "__main__":
    unittest.main(verbosity=2)
