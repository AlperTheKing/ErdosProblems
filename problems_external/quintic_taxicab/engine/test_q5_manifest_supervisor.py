from __future__ import annotations

import ast
import contextlib
import json
import os
import shutil
import subprocess
import sys
import time
import unittest
import uuid
from unittest import mock
from datetime import datetime, timedelta, timezone
from pathlib import Path

ENGINE = Path(__file__).resolve().parent
sys.path.insert(0, str(ENGINE))
import q5_manifest as manifest_lib
import q5_supervisor as supervisor_lib
import reference_enumerator as reference_lib
MANIFEST_TOOL = ENGINE / "q5_manifest.py"
SUPERVISOR = ENGINE / "q5_supervisor.py"
MOCK = ENGINE / "mock_q5_lane_worker.py"
SCALAR = ENGINE / "verify_certificate.py"
INDEPENDENT = ENGINE / "verify_independent.exe"
NATIVE_SCANNER = ENGINE / "scan_torsor_exact.exe"
NATIVE_SCANNER_SOURCE = ENGINE / "scan_torsor_exact.cpp"
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class Q5HarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = ENGINE / f"q5_harness_{uuid.uuid4().hex}"
        self.temporary.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary, ignore_errors=True)

    def build(
        self,
        campaign_id: str = "mock-nohit",
        *,
        deadline_delta: timedelta = timedelta(minutes=5),
        worker: Path = MOCK,
        mode: str = "CALIBRATION_ONLY",
        search_mode: str = "audit_signed_u_both_y",
        D: int = 500,
        P: int = 1,
        Q: int = 1,
        workspace: Path | None = None,
    ) -> tuple[dict, Path, Path]:
        base = self.temporary if workspace is None else workspace
        if workspace is not None:
            base.mkdir()
        manifest_path = base / "manifest.json"
        run_dir = base / "run"
        deadline = datetime.now(timezone.utc) + deadline_delta
        envelope = manifest_lib.build_manifest(
            output=manifest_path,
            lane_config_dir=base / "lanes",
            run_dir=run_dir,
            campaign_id=campaign_id,
            mode=mode,
            search_mode=search_mode,
            P=P,
            Q=Q,
            N=0,
            D=D,
            deadline=manifest_lib.utc_text(deadline),
            worker=worker,
            worker_source=worker,
            worker_kind="python",
            scalar_verifier=SCALAR,
            independent_verifier=INDEPENDENT,
            supervisor=SUPERVISOR,
            python_interpreter=Path(sys.executable),
        )
        return envelope, manifest_path, run_dir

    @staticmethod
    def mock_launch_binding(envelope: dict) -> dict[str, str]:
        return {
            "launch_readiness_sha256": "0" * 64,
            "authorization_sha256": "1" * 64,
            "authorization_expires_utc": envelope["payload"]["deadline"],
        }
    def run_campaign_test(
        self,
        envelope: dict,
        *,
        manifest_path: Path,
        poll_seconds: float,
        deadline_guard: object | None = None,
        census_side_effect: object | None = None,
    ) -> dict:
        """Exercise only the public launch boundary with environmental fakes."""

        binding = self.mock_launch_binding(envelope)
        guard = deadline_guard
        if guard is None:
            now = datetime.now(timezone.utc)
            guard = supervisor_lib.DeadlineGuard(
                deadline=manifest_lib.parse_deadline(envelope["payload"]["deadline"]),
                t0=now,
                monotonic_start_ns=time.monotonic_ns(),
                boot_time_microseconds=supervisor_lib._boot_time_microseconds(),
            )

        class AuthorizedGuard:
            launch_readiness_sha256 = binding["launch_readiness_sha256"]
            authorization_sha256 = binding["authorization_sha256"]
            authorization_expires_utc = binding["authorization_expires_utc"]

            def reached(self) -> bool:
                return guard.reached()

            def hard_reached(self) -> bool:
                return guard.hard_reached()

            def assert_authorization_current(self) -> None:
                if isinstance(guard, supervisor_lib.DeadlineGuard):
                    return None
                guard.assert_authorization_current()

        authorized_guard = AuthorizedGuard()

        class TestLaunchSession:
            def active_guard(
                self, *, envelope: object, manifest_path: Path
            ) -> AuthorizedGuard:
                return authorized_guard

        class TestAggregateReservation:
            def assert_active(self) -> None:
                return None

        census_patch = mock.patch.object(
            supervisor_lib,
            "assert_no_unowned_relevant_processes",
            side_effect=census_side_effect,
        ) if census_side_effect is not None else mock.patch.object(
            supervisor_lib,
            "assert_no_unowned_relevant_processes",
            return_value={"active_processes": [], "errors": []},
        )
        with (
            mock.patch.object(
                supervisor_lib,
                "aggregate_supervisor_reservation",
                return_value=contextlib.nullcontext(TestAggregateReservation()),
            ),
            mock.patch.object(
                supervisor_lib,
                "_LaunchAuthorizationReservation",
                return_value=contextlib.nullcontext(TestLaunchSession()),
            ),
            census_patch,
        ):
            return supervisor_lib.run_campaign(
                envelope,
                manifest_path=manifest_path,
                poll_seconds=poll_seconds,
                authorization_path=self.temporary / "test-authorization.json",
            )


    @staticmethod
    def synthetic_lane_result(
        envelope: dict, lane_id: int, status: str
    ) -> dict:
        payload = envelope["payload"]
        lane = payload["lanes"][lane_id]
        assigned = len(lane["specializations"])
        candidates = [{}] if status == "HIT" else []
        hit_count = "1" if status == "HIT" else "0"
        counts = {key: "0" for key in supervisor_lib.COUNT_KEYS}
        counts["reduced_t_values"] = str(assigned)
        for key in (
            "pairs_considered", "admissible_specializations",
            "bounded_z_squares", "candidate_records",
            "verified_integer_certificates",
        ):
            counts[key] = hit_count
        canonical = (
            payload["search_mode"] == "canonical_positive_u_positive_y"
        )
        return {
            "schema_version": 1,
            "kind": supervisor_lib.RESULT_KIND,
            "campaign_id": payload["campaign_id"],
            "manifest_payload_sha256": envelope["payload_sha256"],
            "lane_file_sha256": lane["lane_file"]["sha256"],
            "search_mode": payload["search_mode"],
            "lane_id": lane_id,
            "assignment_sha256": lane["assignment_sha256"],
            "status": status,
            "signed_u_symmetry_pruned": canonical,
            "negative_y_pruned": canonical,
            "zero_u_pruned": canonical,
            "emit_torsor_points": False,
            "elapsed_milliseconds": "0",
            "assigned_specializations": assigned,
            "completed_specializations": assigned,
            "counts": counts,
            "zero_z_rejected_as_nontarget": True,
            "complete": status == "NO_HIT",
            "candidates": candidates,
        }

    class TerminalProcess:
        def __init__(self, pid: int, returncode: int) -> None:
            self.pid = pid
            self.returncode = returncode

        def poll(self) -> int:
            return self.returncode

    class StoppableProcess:
        def __init__(
            self, pid: int, *, on_terminate: object | None = None
        ) -> None:
            self.pid = pid
            self.returncode: int | None = None
            self.on_terminate = on_terminate

        def poll(self) -> int | None:
            return self.returncode

        def terminate(self) -> None:
            callback = self.on_terminate
            if callable(callback):
                callback()
            self.returncode = -15

        def wait(self, timeout: float) -> int:
            if self.returncode is None:
                raise subprocess.TimeoutExpired("synthetic", timeout)
            return self.returncode

        def kill(self) -> None:
            self.returncode = -9

    def supervisor_command(self, envelope: dict, manifest: Path, launch: bool = True) -> list[str]:
        command = [
            sys.executable,
            str(SUPERVISOR),
            "--manifest",
            str(manifest),
            "--expected-digest",
            envelope["payload_sha256"],
            "--expected-campaign-id",
            envelope["payload"]["campaign_id"],
            "--expected-mode",
            "CALIBRATION_ONLY",
            "--expected-search-mode",
            "audit_signed_u_both_y",
            "--poll-ms",
            "20",
        ]
        if launch:
            command.append("--launch")
        return command

    def run_supervisor(self, envelope: dict, manifest: Path, launch: bool = True) -> subprocess.CompletedProcess[str]:
        command = self.supervisor_command(envelope, manifest, launch)
        if not launch:
            return subprocess.run(
                command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, timeout=20,
                creationflags=CREATE_NO_WINDOW,
            )
        try:
            audited = manifest_lib.audit_manifest(
                manifest, expected_digest=envelope["payload_sha256"],
                expected_campaign_id=envelope["payload"]["campaign_id"],
            )
            supervisor_lib.validate_runtime_identity(audited["payload"])
            mock_t0 = datetime.now(timezone.utc)
            mock_deadline = manifest_lib.parse_deadline(
                audited["payload"]["deadline"]
            )
            mock_guard = supervisor_lib.DeadlineGuard(
                deadline=mock_deadline, hard_deadline=mock_deadline + timedelta(minutes=5),
                t0=mock_t0, monotonic_start_ns=time.monotonic_ns(),
                boot_time_microseconds=supervisor_lib._boot_time_microseconds(),
            )
            report = self.run_campaign_test(
                audited, manifest_path=manifest, poll_seconds=0.02,
                deadline_guard=mock_guard,
            )
            return subprocess.CompletedProcess(
                command, 0, json.dumps(report, sort_keys=True), ""
            )
        except (manifest_lib.ManifestError, supervisor_lib.SupervisorError) as exc:
            report = {"ok": False, "status": "FAIL_CLOSED", "error": str(exc)}
            return subprocess.CompletedProcess(
                command, 2, json.dumps(report, sort_keys=True), ""
            )

    def run_lane_direct(
        self, envelope: dict, lane_id: int = 0
    ) -> subprocess.CompletedProcess[str]:
        payload = envelope["payload"]
        lane = payload["lanes"][lane_id]
        environment = os.environ.copy()
        environment.update(payload["thread_environment"])
        environment["Q5_MANIFEST_PAYLOAD_SHA256"] = envelope["payload_sha256"]
        environment["Q5_LANE_FILE_SHA256"] = lane["lane_file"]["sha256"]
        environment["Q5_DEADLINE_UTC"] = payload["deadline"]
        return subprocess.run(
            lane["command"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            env=environment,
            shell=False,
            creationflags=CREATE_NO_WINDOW,
        )

    def test_exact_coverage_and_deterministic_balance(self) -> None:
        lanes = manifest_lib.balanced_assignments(
            20, 20, 10, 10, "canonical_positive_u_positive_y"
        )
        pairs = [
            (item["p"], item["q"])
            for lane in lanes
            for item in lane["specializations"]
        ]
        expected = list(manifest_lib.reduced_pairs(20, 20))
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertEqual(set(pairs), set(expected))
        self.assertTrue(manifest_lib.balance_record(lanes)["threshold_pass"])

    def test_mode_specific_work_estimate(self) -> None:
        canonical = manifest_lib.estimated_work(
            1, 1, 2, 2, "canonical_positive_u_positive_y"
        )
        audit = manifest_lib.estimated_work(1, 1, 2, 2, "audit_signed_u_both_y")
        self.assertEqual(canonical, 5)
        self.assertEqual(audit, 14)

    def test_zero_admissible_jobs_have_balanced_full_loop_baseline(self) -> None:
        lanes = manifest_lib.balanced_assignments(
            1, 128, 10, 1, "canonical_positive_u_positive_y"
        )
        jobs = [job for lane in lanes for job in lane["specializations"]]
        self.assertEqual(len(jobs), 128)
        self.assertTrue(all(job["estimated_work"] == 10 for job in jobs))
        self.assertEqual({lane["estimated_weight"] for lane in lanes}, {20})
        balance = manifest_lib.balance_record(lanes)
        self.assertTrue(balance["threshold_applicable"])
        self.assertTrue(balance["threshold_pass"])
        self.assertEqual(balance["max_min_ratio"], "1.000000000000")

    def test_exact_oeis_gate_uses_squared_integer_inequality(self) -> None:
        killed = manifest_lib.oeis_redundancy_gate(1, 1, 400)
        passed = manifest_lib.oeis_redundancy_gate(1, 1, 500)
        self.assertFalse(killed["passes"])
        self.assertEqual(killed["status"], "ROUTE_KILL_REDUNDANT_BOX")
        self.assertTrue(passed["passes"])
        self.assertEqual(passed["source_class"], "EXTERNAL_STATUS_GATE_NOT_A_SEARCH_CERTIFICATE")

    def test_manifest_round_trip_and_strict_tsv(self) -> None:
        envelope, manifest, _ = self.build()
        audited = manifest_lib.audit_manifest(
            manifest,
            expected_digest=envelope["payload_sha256"],
            expected_campaign_id="mock-nohit",
        )
        self.assertEqual(audited, envelope)
        lane = envelope["payload"]["lanes"][0]
        data = Path(lane["lane_file"]["path"]).read_bytes()
        self.assertNotIn(b"\r", data)
        self.assertIn(b"deadline\t", data)
        self.assertIn(b"search_mode\taudit_signed_u_both_y\n", data)
        self.assertIn(b"lane_count\t64\n", data)
        self.assertEqual(manifest_lib.sha256_bytes(data), lane["lane_file"]["sha256"])

    def test_selected_main_requires_canonical_mode(self) -> None:
        with self.assertRaisesRegex(manifest_lib.ManifestError, "SELECTED_MAIN requires"):
            self.build(mode="SELECTED_MAIN")

    def test_selected_main_rejects_source_covered_box(self) -> None:
        with self.assertRaisesRegex(manifest_lib.ManifestError, "source-based OEIS"):
            self.build(
                mode="SELECTED_MAIN",
                search_mode="canonical_positive_u_positive_y",
                D=1,
            )

    def test_calibration_manifest_may_record_failing_source_gate(self) -> None:
        envelope, manifest, _ = self.build(D=1)
        self.assertFalse(envelope["payload"]["oeis_redundancy_gate"]["passes"])
        self.assertEqual(manifest_lib.audit_manifest(manifest), envelope)

    def test_auditor_rejects_overlap_or_omission_even_with_new_payload_digest(self) -> None:
        envelope, manifest, _ = self.build()
        payload = envelope["payload"]
        payload["lanes"][0]["specializations"] = []
        envelope["payload_sha256"] = manifest_lib.sha256_bytes(
            manifest_lib.canonical_bytes(payload)
        )
        manifest_lib.atomic_write_json(manifest, envelope)
        with self.assertRaisesRegex(manifest_lib.ManifestError, "assignment differs"):
            manifest_lib.audit_manifest(manifest)

    def test_auditor_rejects_lane_file_hash_drift(self) -> None:
        envelope, manifest, _ = self.build()
        lane_path = Path(envelope["payload"]["lanes"][0]["lane_file"]["path"])
        lane_path.write_bytes(lane_path.read_bytes() + b"x\n")
        with self.assertRaisesRegex(manifest_lib.ManifestError, "TSV hash/content drift"):
            manifest_lib.audit_manifest(manifest)

    def test_auditor_rejects_artifact_hash_drift(self) -> None:
        worker_copy = self.temporary / "mock_copy.py"
        shutil.copy2(MOCK, worker_copy)
        envelope, manifest, _ = self.build(worker=worker_copy)
        worker_copy.write_bytes(worker_copy.read_bytes() + b"# drift\n")
        with self.assertRaisesRegex(manifest_lib.ManifestError, "artifact hash drift"):
            manifest_lib.audit_manifest(manifest)

    def test_supervisor_audit_only_spawns_nothing(self) -> None:
        envelope, manifest, run_dir = self.build()
        completed = self.run_supervisor(envelope, manifest, launch=False)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "AUDIT_ONLY")
        self.assertFalse(run_dir.exists())

    def test_supervisor_mock_nohit(self) -> None:
        envelope, manifest, run_dir = self.build()
        completed = self.run_supervisor(envelope, manifest)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(completed.stderr, "")
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(summary["status"], "FINITE_NO_HIT")
        self.assertEqual(summary["owned_pids"], [])
        self.assertEqual(summary["lane_statuses"]["0"], "NO_HIT")
        self.assertEqual(sum(value == "NO_WORK" for value in summary["lane_statuses"].values()), 63)

    def test_mock_hit_exit10_matches_native_semantic_contract(self) -> None:
        envelope, _, _ = self.build("mock-invalid-hit")
        completed = self.run_lane_direct(envelope)
        self.assertEqual(completed.returncode, 10, completed.stderr)
        self.assertEqual(completed.stderr, "")
        lane = envelope["payload"]["lanes"][0]
        result = supervisor_lib.validate_lane_result(
            json.loads(Path(lane["result_path"]).read_text()),
            payload=envelope["payload"],
            payload_digest=envelope["payload_sha256"],
            lane=lane,
        )
        self.assertEqual(result["status"], "HIT")
        supervisor_lib.validate_semantic_exit(completed.returncode, "HIT", 0)

    def test_early_verified_hit_relabels_stopped_live_peers(self) -> None:
        worker = self.temporary / "early_hit_worker.py"
        worker.write_text(
            "from __future__ import annotations\n"
            "import sys, time\n"
            f"sys.path.insert(0, {str(ENGINE)!r})\n"
            "lane_id = int(sys.argv[sys.argv.index('--lane-id') + 1])\n"
            "if lane_id != 0:\n"
            "    time.sleep(60)\n"
            "from mock_q5_lane_worker import main\n"
            "raise SystemExit(main())\n",
            encoding="ascii",
        )
        envelope, manifest, run_dir = self.build(
            "early-verified-hit-invalid-hit", worker=worker, P=2, Q=2, D=1
        )
        verification = {
            "integer_quadruple": ["1", "2", "3", "4"],
            "scalar_report": {"valid": True},
            "independent_report": {"valid": True},
        }
        observed_live_peer_counts: list[int] = []
        terminate_owned = supervisor_lib._terminate_owned

        def observe_then_terminate(active: dict) -> dict:
            observed_live_peer_counts.append(
                sum(process.poll() is None for process in active.values())
            )
            return terminate_owned(active)

        with (
            mock.patch.object(
                supervisor_lib, "_validate_candidate", return_value=(1, 2, 3, 4)
            ),
            mock.patch.object(
                supervisor_lib, "dual_verify_candidate", return_value=verification
            ),
            mock.patch.object(
                supervisor_lib, "_terminate_owned", side_effect=observe_then_terminate
            ),
        ):
            completed = self.run_supervisor(envelope, manifest)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertGreaterEqual(max(observed_live_peer_counts), 2)
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(summary["status"], "VERIFIED_HIT")
        self.assertEqual(summary["lane_statuses"]["0"], "VERIFIED_HIT")
        self.assertEqual(summary["lane_statuses"]["1"], "STOPPED_AFTER_VERIFIED_HIT")
        self.assertEqual(summary["lane_statuses"]["2"], "STOPPED_AFTER_VERIFIED_HIT")
        self.assertNotIn("STOPPED_AFTER_CANDIDATE", summary["lane_statuses"].values())

    def test_hit_result_requires_exactly_one_candidate(self) -> None:
        envelope, _, _ = self.build("two-candidate-contract")
        lane = envelope["payload"]["lanes"][0]
        result = self.synthetic_lane_result(envelope, 0, "HIT")
        result["candidates"] = [{}, {}]
        for key in (
            "bounded_z_squares", "candidate_records",
            "verified_integer_certificates",
        ):
            result["counts"][key] = "2"
        with self.assertRaisesRegex(
            supervisor_lib.SupervisorError, "HIT requires exactly one candidate"
        ):
            supervisor_lib.validate_lane_result(
                result,
                payload=envelope["payload"],
                payload_digest=envelope["payload_sha256"],
                lane=lane,
            )

    def test_concurrent_lower_and_higher_nohit_peers_are_preserved(self) -> None:
        envelope, manifest, run_dir = self.build(
            "terminal-batch-sole-hit", P=2, Q=2, D=1
        )
        statuses = {0: "NO_HIT", 1: "HIT", 2: "NO_HIT"}

        def spawn(command: list[str], **_: object) -> object:
            lane_id = int(command[command.index("--lane-id") + 1])
            result_path = Path(command[command.index("--result") + 1])
            manifest_lib.atomic_write_json(
                result_path,
                self.synthetic_lane_result(envelope, lane_id, statuses[lane_id]),
            )
            return self.TerminalProcess(
                70000 + lane_id, 10 if statuses[lane_id] == "HIT" else 0
            )

        verification = {
            "integer_quadruple": ["1", "2", "3", "4"],
            "scalar_report": {"valid": True},
            "independent_report": {"valid": True},
        }
        with (
            mock.patch.object(supervisor_lib.subprocess, "Popen", side_effect=spawn),
            mock.patch.object(
                supervisor_lib, "_validate_candidate", return_value=(1, 2, 3, 4)
            ),
            mock.patch.object(
                supervisor_lib, "dual_verify_candidate", return_value=verification
            ),
        ):
            summary = self.run_campaign_test(
                envelope,
                manifest_path=manifest,
                poll_seconds=0.02,
            )
        self.assertEqual(summary["status"], "VERIFIED_HIT")
        self.assertEqual(summary["lane_statuses"]["0"], "NO_HIT")
        self.assertEqual(summary["lane_statuses"]["1"], "VERIFIED_HIT")
        self.assertEqual(summary["lane_statuses"]["2"], "NO_HIT")
        self.assertEqual(summary["verified_hit"]["candidate_index"], 0)
        self.assertEqual(
            sorted(path.name for path in run_dir.glob("lane_*.result.json")),
            [
                "lane_00.result.json",
                "lane_01.result.json",
                "lane_02.result.json",
            ],
        )

    def test_concurrent_second_hit_fails_closed_before_verification(self) -> None:
        envelope, manifest, run_dir = self.build(
            "terminal-batch-double-hit", P=2, Q=2, D=1
        )
        statuses = {0: "HIT", 1: "HIT", 2: "NO_HIT"}

        def spawn(command: list[str], **_: object) -> object:
            lane_id = int(command[command.index("--lane-id") + 1])
            result_path = Path(command[command.index("--result") + 1])
            manifest_lib.atomic_write_json(
                result_path,
                self.synthetic_lane_result(envelope, lane_id, statuses[lane_id]),
            )
            return self.TerminalProcess(
                71000 + lane_id, 10 if statuses[lane_id] == "HIT" else 0
            )

        with (
            mock.patch.object(supervisor_lib.subprocess, "Popen", side_effect=spawn),
            mock.patch.object(
                supervisor_lib, "dual_verify_candidate"
            ) as dual_verify,
            self.assertRaisesRegex(
                supervisor_lib.SupervisorError, "multiple HIT producers"
            ),
        ):
            self.run_campaign_test(
                envelope,
                manifest_path=manifest,
                poll_seconds=0.02,
            )
        dual_verify.assert_not_called()
        summary = json.loads(
            (run_dir / "supervisor_summary.json").read_text(encoding="ascii")
        )
        self.assertEqual(summary["status"], "FAIL_CLOSED")

    def test_stopped_snapshot_live_peer_stray_result_fails_closed(self) -> None:
        envelope, manifest, run_dir = self.build(
            "stopped-peer-stray-result", P=2, Q=2, D=1
        )

        def spawn(command: list[str], **_: object) -> object:
            lane_id = int(command[command.index("--lane-id") + 1])
            result_path = Path(command[command.index("--result") + 1])
            if lane_id == 0:
                manifest_lib.atomic_write_json(
                    result_path,
                    self.synthetic_lane_result(envelope, lane_id, "HIT"),
                )
                return self.TerminalProcess(72000, 10)

            def write_stray() -> None:
                manifest_lib.atomic_write_json(
                    result_path,
                    self.synthetic_lane_result(envelope, lane_id, "NO_HIT"),
                )

            return self.StoppableProcess(
                72000 + lane_id, on_terminate=write_stray
            )

        with (
            mock.patch.object(supervisor_lib.subprocess, "Popen", side_effect=spawn),
            mock.patch.object(
                supervisor_lib, "dual_verify_candidate"
            ) as dual_verify,
            self.assertRaisesRegex(
                supervisor_lib.SupervisorError, "produced a result while being stopped"
            ),
        ):
            self.run_campaign_test(
                envelope,
                manifest_path=manifest,
                poll_seconds=0.02,
            )
        dual_verify.assert_not_called()
        summary = json.loads(
            (run_dir / "supervisor_summary.json").read_text(encoding="ascii")
        )
        self.assertEqual(summary["status"], "FAIL_CLOSED")

    def test_deadline_boundary_drains_terminal_nohit_before_stopping_live(self) -> None:
        envelope, manifest, _ = self.build(
            "deadline-terminal-drain", P=2, Q=2, D=1
        )

        def spawn(command: list[str], **_: object) -> object:
            lane_id = int(command[command.index("--lane-id") + 1])
            if lane_id == 0:
                result_path = Path(command[command.index("--result") + 1])
                manifest_lib.atomic_write_json(
                    result_path,
                    self.synthetic_lane_result(envelope, lane_id, "NO_HIT"),
                )
                return self.TerminalProcess(73000, 0)
            return self.StoppableProcess(73000 + lane_id)

        class BoundaryGuard:
            def __init__(self) -> None:
                self.calls = 0

            def reached(self) -> bool:
                self.calls += 1
                return self.calls >= 8

            def hard_reached(self) -> bool:
                return False

            def assert_authorization_current(self) -> None:
                return None

        with mock.patch.object(
            supervisor_lib.subprocess, "Popen", side_effect=spawn
        ):
            summary = self.run_campaign_test(
                envelope,
                manifest_path=manifest,
                poll_seconds=0.02,
                deadline_guard=BoundaryGuard(),
            )
        self.assertEqual(summary["status"], "TIMEOUT_INCOMPLETE")
        self.assertEqual(summary["lane_statuses"]["0"], "NO_HIT")
        self.assertEqual(summary["lane_statuses"]["1"], "TIMEOUT_INCOMPLETE")
        self.assertEqual(summary["lane_statuses"]["2"], "TIMEOUT_INCOMPLETE")

    def test_all_nohit_crossing_s_before_summary_is_fail_closed(self) -> None:
        envelope, manifest, run_dir = self.build("finite-summary-crosses-s")

        def spawn(command: list[str], **_: object) -> object:
            lane_id = int(command[command.index("--lane-id") + 1])
            result_path = Path(command[command.index("--result") + 1])
            manifest_lib.atomic_write_json(
                result_path,
                self.synthetic_lane_result(envelope, lane_id, "NO_HIT"),
            )
            return self.TerminalProcess(74000 + lane_id, 0)

        class SummaryBoundaryGuard:
            def __init__(self) -> None:
                self.calls = 0

            def reached(self) -> bool:
                self.calls += 1
                return self.calls >= 6

            def hard_reached(self) -> bool:
                return False

            def assert_authorization_current(self) -> None:
                return None

        with (
            mock.patch.object(supervisor_lib.subprocess, "Popen", side_effect=spawn),
            self.assertRaisesRegex(
                supervisor_lib.SupervisorError,
                "deadline reached before finite summary write",
            ),
        ):
            self.run_campaign_test(
                envelope,
                manifest_path=manifest,
                poll_seconds=0.02,
                deadline_guard=SummaryBoundaryGuard(),
            )
        summary = json.loads(
            (run_dir / "supervisor_summary.json").read_text(encoding="ascii")
        )
        self.assertEqual(summary["status"], "FAIL_CLOSED")
        self.assertNotIn(
            "TIMEOUT_INCOMPLETE", summary["lane_statuses"].values()
        )

    def test_manifest_created_utc_preserves_same_second_microseconds(self) -> None:
        first = datetime(2026, 7, 21, 8, 0, 0, 123456, tzinfo=timezone.utc)
        second = first.replace(microsecond=123457)
        self.assertEqual(manifest_lib.utc_text(first), manifest_lib.utc_text(second))
        self.assertLess(
            manifest_lib.utc_text_precise(first),
            manifest_lib.utc_text_precise(second),
        )
        fixed_now = datetime.now(timezone.utc).replace(microsecond=654321)

        class FixedDateTime(datetime):
            @classmethod
            def now(cls, tz: timezone | None = None) -> datetime:
                if tz is None:
                    return fixed_now.replace(tzinfo=None)
                return fixed_now.astimezone(tz)

        with mock.patch.object(manifest_lib, "datetime", FixedDateTime):
            envelope, _, _ = self.build("precise-created-utc")
        self.assertEqual(
            envelope["payload"]["created_utc"],
            manifest_lib.utc_text_precise(fixed_now),
        )
        self.assertNotIn(".", envelope["payload"]["deadline"])

    def test_mock_timeout_exit3_matches_native_semantic_contract(self) -> None:
        envelope, _, _ = self.build("mock-semantic-timeout")
        completed = self.run_lane_direct(envelope)
        self.assertEqual(completed.returncode, 3, completed.stderr)
        self.assertEqual(completed.stderr, "")
        lane = envelope["payload"]["lanes"][0]
        result = supervisor_lib.validate_lane_result(
            json.loads(Path(lane["result_path"]).read_text()),
            payload=envelope["payload"],
            payload_digest=envelope["payload_sha256"],
            lane=lane,
        )
        self.assertEqual(result["status"], "TIMEOUT_INCOMPLETE")
        supervisor_lib.validate_semantic_exit(
            completed.returncode, "TIMEOUT_INCOMPLETE", 0
        )

    def test_supervisor_rejects_unexpected_worker_exit_after_result_validation(self) -> None:
        envelope, manifest, run_dir = self.build("mock-unexpected-exit")
        completed = self.run_supervisor(envelope, manifest)
        self.assertEqual(completed.returncode, 2)
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(summary["status"], "FAIL_CLOSED")
        self.assertIn(
            "exit/status mismatch: code 7, status NO_HIT, expected 0",
            summary["anomaly"],
        )

    def test_supervisor_rejects_inconsistent_exit_and_result_status(self) -> None:
        envelope, manifest, run_dir = self.build("mock-exit-status-mismatch")
        completed = self.run_supervisor(envelope, manifest)
        self.assertEqual(completed.returncode, 2)
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(summary["status"], "FAIL_CLOSED")
        self.assertIn(
            "exit/status mismatch: code 10, status NO_HIT, expected 0",
            summary["anomaly"],
        )

    def test_runtime_identity_rejects_substituted_supervisor_path(self) -> None:
        envelope, manifest, _ = self.build("mock-runtime-substitution")
        supervisor_lib.validate_runtime_identity(envelope["payload"])
        runtime_paths = {
            "supervisor": SUPERVISOR,
            "manifest_tool": Path(manifest_lib.__file__),
            "python_interpreter": Path(sys.executable),
        }
        for role in sorted(runtime_paths):
            with self.subTest(role=role):
                substituted = dict(runtime_paths)
                substituted[role] = MOCK
                with self.assertRaisesRegex(
                    supervisor_lib.SupervisorError, f"runtime {role} path mismatch"
                ):
                    supervisor_lib.validate_runtime_identity(
                        envelope["payload"], substituted
                    )
        drifted_payload = json.loads(json.dumps(envelope["payload"]))
        drifted_payload["artifacts"]["supervisor"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(
            supervisor_lib.SupervisorError, "runtime supervisor hash mismatch"
        ):
            supervisor_lib.validate_runtime_identity(drifted_payload)
        substitute = self.temporary / "substituted_supervisor.py"
        shutil.copy2(SUPERVISOR, substitute)
        command = self.supervisor_command(envelope, manifest, launch=False)
        command[1] = str(substitute)
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ENGINE)
        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            env=environment,
            creationflags=CREATE_NO_WINDOW,
        )
        self.assertEqual(completed.returncode, 2, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertIn("runtime supervisor path mismatch", report["error"])

    def test_wrapper_requires_authorization_parameter(self) -> None:
        envelope, manifest, run_dir = self.build("mock-wrapper-python-mismatch")
        unpinned_python = shutil.which("pwsh")
        self.assertIsNotNone(unpinned_python)
        command = [
            "pwsh", "-NoProfile", "-File",
            str(ENGINE / "run_q5_supervisor_hidden.ps1"),
            "-Python", str(unpinned_python),
            "-Manifest", str(manifest),
            "-ExpectedDigest", envelope["payload_sha256"],
            "-CampaignId", envelope["payload"]["campaign_id"],
            "-Mode", "CALIBRATION_ONLY",
            "-SearchMode", "audit_signed_u_both_y",
            "-Launch",
        ]
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            creationflags=CREATE_NO_WINDOW,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Authorization", completed.stderr)
        self.assertFalse(run_dir.exists())

    def test_cli_launch_requires_fixed_authorization(self) -> None:
        envelope, manifest, run_dir = self.build("mock-authorization-required")
        completed = subprocess.run(
            self.supervisor_command(envelope, manifest),
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, timeout=20,
            creationflags=CREATE_NO_WINDOW,
        )
        self.assertEqual(completed.returncode, 2, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertIn("--launch requires fixed --authorization", report["error"])
        self.assertFalse(run_dir.exists())

    def test_public_launch_boundary_rejects_missing_authorization_before_claim(self) -> None:
        envelope, manifest, run_dir = self.build("mock-public-boundary")
        with mock.patch.object(supervisor_lib.subprocess, "Popen") as popen:
            with self.assertRaisesRegex(
                supervisor_lib.SupervisorError, "cannot read strict JSON"
            ):
                supervisor_lib.run_campaign(
                    envelope, manifest_path=manifest, poll_seconds=0.02,
                    authorization_path=self.temporary / "missing-authorization.json",
                )
            popen.assert_not_called()
        self.assertFalse(run_dir.exists())

    def test_launch_lock_claim_is_exclusive_and_controller_compatible(self) -> None:
        envelope, _, _ = self.build("mock-direct-lock")
        lock_dir = self.temporary / "direct_lock_run"
        binding = self.mock_launch_binding(envelope)
        lock_path = supervisor_lib._claim_run_dir(
            lock_dir, envelope["payload"], envelope["payload_sha256"],
            binding["launch_readiness_sha256"], binding["authorization_sha256"],
            binding["authorization_expires_utc"],
        )
        original = lock_path.read_bytes()
        record = json.loads(original)
        self.assertEqual(set(record), {
            "schema_version", "kind", "campaign_id",
            "manifest_payload_sha256", "launch_readiness_sha256",
            "authorization_sha256", "authorization_expires_utc",
            "supervisor_pid", "claimed_utc",
        })
        import q5_tranche as tranche_lib
        accepted = tranche_lib._validate_launch_lock_value(
            record, envelope["payload"], envelope["payload_sha256"],
            name="supervisor regression launch lock",
            expected_readiness_sha256=binding["launch_readiness_sha256"],
        )
        self.assertEqual(
            accepted["authorization_sha256"], binding["authorization_sha256"]
        )
        expired_dir = self.temporary / "expired_direct_lock_run"
        expired_utc = manifest_lib.utc_text(
            datetime.now(timezone.utc) - timedelta(seconds=1)
        )
        with self.assertRaisesRegex(
            supervisor_lib.SupervisorError, "expired at run-dir claim"
        ):
            supervisor_lib._claim_run_dir(
                expired_dir, envelope["payload"], envelope["payload_sha256"],
                binding["launch_readiness_sha256"], binding["authorization_sha256"],
                expired_utc,
            )
        expired_lock = expired_dir / "launch.lock"
        self.assertTrue(expired_lock.is_file())
        self.assertEqual(expired_lock.read_bytes(), b"")
        with self.assertRaisesRegex(
            supervisor_lib.SupervisorError, "launch lock already exists"
        ):
            supervisor_lib._claim_run_dir(
                lock_dir, envelope["payload"], envelope["payload_sha256"],
                binding["launch_readiness_sha256"], binding["authorization_sha256"],
                binding["authorization_expires_utc"],
            )
        self.assertEqual(lock_path.read_bytes(), original)
        self.assertEqual(list(lock_dir.iterdir()), [lock_path])

    def test_lock_and_fast_completion_timestamps_are_monotone(self) -> None:
        envelope, _, _ = self.build("mock-fast-timestamp")
        lock_dir = self.temporary / "fast_timestamp_run"
        binding = self.mock_launch_binding(envelope)
        fixed_now = datetime.now(timezone.utc).replace(microsecond=900000)

        class FixedDateTime(datetime):
            @classmethod
            def now(cls, tz: timezone | None = None) -> datetime:
                if tz is None:
                    return fixed_now.replace(tzinfo=None)
                return fixed_now.astimezone(tz)

        with mock.patch.object(supervisor_lib, "datetime", FixedDateTime):
            lock_path = supervisor_lib._claim_run_dir(
                lock_dir, envelope["payload"], envelope["payload_sha256"],
                binding["launch_readiness_sha256"], binding["authorization_sha256"],
                binding["authorization_expires_utc"],
            )
            finished_utc = supervisor_lib._now_text()

        claim = json.loads(lock_path.read_text(encoding="ascii"))
        claimed = supervisor_lib._parse_utc(claim["claimed_utc"], "claimed_utc")
        finished = supervisor_lib._parse_utc(finished_utc, "finished_utc")
        self.assertEqual(claimed.microsecond, 900000)
        self.assertEqual(finished.microsecond, 900000)
        self.assertGreaterEqual(finished, claimed)

    def test_terminate_owned_reports_simulated_survivor(self) -> None:
        class StubbornProcess:
            pid = 424242

            def poll(self) -> None:
                return None

            def terminate(self) -> None:
                raise OSError("synthetic terminate failure")

            def wait(self, timeout: float) -> None:
                raise subprocess.TimeoutExpired("synthetic", timeout)

            def kill(self) -> None:
                raise OSError("synthetic kill failure")

        report = supervisor_lib._terminate_owned({0: StubbornProcess()})
        self.assertEqual(report["survivor_pids"], [424242])
        self.assertTrue(report["errors"])
        self.assertTrue(any("final wait failed" in item for item in report["errors"]))

    def test_stderr_written_at_exit_is_always_fail_closed(self) -> None:
        for index in range(8):
            with self.subTest(index=index):
                envelope, manifest, run_dir = self.build(
                    f"mock-{index}-stderr-at-exit",
                    workspace=self.temporary / f"stderr_at_exit_{index}",
                )
                completed = self.run_supervisor(envelope, manifest)
                self.assertEqual(completed.returncode, 2)
                summary = json.loads(
                    (run_dir / "supervisor_summary.json").read_text()
                )
                self.assertIn("emitted stderr", summary["anomaly"])
                self.assertGreater(
                    (run_dir / "lane_00.stderr.txt").stat().st_size, 0
                )

    def test_native_scanner_cross_contract_audit_box(self) -> None:
        manifest = self.temporary / "native_manifest.json"
        run_dir = self.temporary / "native_run"
        envelope = manifest_lib.build_manifest(
            output=manifest,
            lane_config_dir=self.temporary / "native_lanes",
            run_dir=run_dir,
            campaign_id="native-cross-contract",
            mode="CALIBRATION_ONLY",
            search_mode="audit_signed_u_both_y",
            P=2,
            Q=2,
            N=2,
            D=2,
            deadline=manifest_lib.utc_text(
                datetime.now(timezone.utc) + timedelta(minutes=5)
            ),
            worker=NATIVE_SCANNER,
            worker_source=NATIVE_SCANNER_SOURCE,
            worker_kind="native",
            scalar_verifier=SCALAR,
            independent_verifier=INDEPENDENT,
            supervisor=SUPERVISOR,
            python_interpreter=Path(sys.executable),
        )
        completed = self.run_supervisor(envelope, manifest)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(summary["status"], "FINITE_NO_HIT")

        aggregate = {key: 0 for key in supervisor_lib.COUNT_KEYS}
        reference = reference_lib.enumerate_box(reference_lib.BoxBounds(2, 2, 2, 2))
        per_lane_u_counts: list[int] = []
        for lane in envelope["payload"]["lanes"]:
            if not lane["specializations"]:
                continue
            result = json.loads(Path(lane["result_path"]).read_text())
            supervisor_lib.validate_lane_result(
                result,
                payload=envelope["payload"],
                payload_digest=envelope["payload_sha256"],
                lane=lane,
            )
            for key, value in result["counts"].items():
                if key == "reduced_u_values":
                    per_lane_u_counts.append(int(value))
                else:
                    aggregate[key] += int(value)
        self.assertTrue(per_lane_u_counts)
        self.assertTrue(all(value == reference["counts"]["reduced_u_values"] for value in per_lane_u_counts))
        common_keys = set(reference["counts"]).intersection(aggregate) - {"reduced_u_values"}
        for key in common_keys:
            self.assertEqual(aggregate[key], reference["counts"][key], key)
        self.assertEqual(aggregate["repeated_entry_rejections"], 0)
        self.assertEqual(aggregate["reduced_t_values"], 3)

    def test_supervisor_fails_closed_on_worker_stderr(self) -> None:
        envelope, manifest, run_dir = self.build("mock-stderr")
        completed = self.run_supervisor(envelope, manifest)
        self.assertEqual(completed.returncode, 2)
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(summary["status"], "FAIL_CLOSED")
        self.assertEqual(summary["owned_pids"], [])
        self.assertGreater((run_dir / "lane_00.stderr.txt").stat().st_size, 0)

    def test_supervisor_fails_closed_on_result_digest_mismatch(self) -> None:
        envelope, manifest, run_dir = self.build("mock-digest-mismatch")
        completed = self.run_supervisor(envelope, manifest)
        self.assertEqual(completed.returncode, 2)
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(summary["status"], "FAIL_CLOSED")
        self.assertIn("manifest_payload_sha256 mismatch", summary["anomaly"])
        self.assertEqual(summary["owned_pids"], [])

    def test_supervisor_fails_closed_on_invalid_candidate_provenance(self) -> None:
        envelope, manifest, run_dir = self.build("mock-invalid-hit")
        completed = self.run_supervisor(envelope, manifest)
        self.assertEqual(completed.returncode, 2)
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(summary["status"], "FAIL_CLOSED")
        self.assertIn("candidate Y does not satisfy", summary["anomaly"])
        self.assertNotIn("exit/status mismatch", summary["anomaly"])
        state = json.loads((run_dir / "supervisor_state.json").read_text())
        self.assertEqual(state["lanes"]["0"]["status"], "VALIDATION_FAILED")
        self.assertIsNone(state["lanes"]["0"]["pid"])
        self.assertEqual(summary["lane_statuses"]["0"], "VALIDATION_FAILED")

    def test_dual_verifier_gate_rejects_unequal_quadruple(self) -> None:
        envelope, _, _ = self.build()
        with self.assertRaisesRegex(supervisor_lib.SupervisorError, "verifier returned 1"):
            supervisor_lib.dual_verify_candidate(
                (1, 2, 3, 4), envelope["payload"]["artifacts"]
            )

    def test_supervisor_stops_owned_worker_at_common_deadline(self) -> None:
        envelope, manifest, run_dir = self.build(
            "mock-sleep", deadline_delta=timedelta(seconds=2.5)
        )
        completed = self.run_supervisor(envelope, manifest)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(summary["status"], "TIMEOUT_INCOMPLETE")
        self.assertEqual(summary["owned_pids"], [])
        self.assertEqual(summary["lane_statuses"]["0"], "TIMEOUT_INCOMPLETE")

    def test_hidden_wrapper_requires_explicit_launch(self) -> None:
        command = [
            "pwsh",
            "-NoProfile",
            "-File",
            str(ENGINE / "run_q5_supervisor_hidden.ps1"),
            "-Python",
            sys.executable,
            "-Authorization",
            str(self.temporary / "missing-authorization.json"),
            "-Manifest",
            str(self.temporary / "missing.json"),
            "-ExpectedDigest",
            "0" * 64,
            "-CampaignId",
            "mock",
            "-Mode",
            "CALIBRATION_ONLY",
            "-SearchMode",
            "audit_signed_u_both_y",
        ]
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            creationflags=CREATE_NO_WINDOW,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("pass -Launch", completed.stderr)



    def test_relevance_census_catches_module_and_import_invocations(self) -> None:
        outside = r"C:\not-the-q5-workspace"
        cases = [
            {
                "cwd": outside,
                "cmdline": [sys.executable, "-m", "q5_supervisor"],
                "exe": sys.executable,
                "name": Path(sys.executable).name,
            },
            {
                "cwd": outside,
                "cmdline": [sys.executable, "-c", "import q5_tranche"],
                "exe": sys.executable,
                "name": Path(sys.executable).name,
            },
            {
                "cwd": str(ENGINE),
                "cmdline": [sys.executable, "-c", "print(1)"],
                "exe": sys.executable,
                "name": Path(sys.executable).name,
            },
        ]
        for case in cases:
            with self.subTest(cmdline=case["cmdline"], cwd=case["cwd"]):
                relevant, _ = supervisor_lib._process_is_relevant(case)
                self.assertTrue(relevant)

    def test_dual_clock_guard_detects_rollback_and_separates_hard_g(self) -> None:
        t0 = datetime(2026, 7, 21, tzinfo=timezone.utc)
        rollback = supervisor_lib.DeadlineGuard(
            deadline=t0 + timedelta(seconds=20),
            hard_deadline=t0 + timedelta(seconds=30),
            t0=t0,
            monotonic_start_ns=1_000,
            boot_time_microseconds=77,
            wall_clock=lambda: t0 + timedelta(seconds=1),
            monotonic_clock=lambda: 1_000 + 10_000_000_000,
            boot_clock=lambda: 77,
        )
        with self.assertRaisesRegex(
            supervisor_lib.SupervisorError, "wall clock rollback"
        ):
            rollback.reached()

        wall = [t0 + timedelta(seconds=2)]
        monotonic = [1_000 + 2_000_000_000]
        guard = supervisor_lib.DeadlineGuard(
            deadline=t0 + timedelta(seconds=2),
            hard_deadline=t0 + timedelta(seconds=5),
            t0=t0,
            monotonic_start_ns=1_000,
            boot_time_microseconds=77,
            wall_clock=lambda: wall[0],
            monotonic_clock=lambda: monotonic[0],
            boot_clock=lambda: 77,
        )
        self.assertTrue(guard.reached())
        self.assertFalse(guard.hard_reached())
        wall[0] = t0 + timedelta(seconds=5)
        monotonic[0] = 1_000 + 5_000_000_000
        self.assertTrue(guard.hard_reached())

    def test_readiness_marker_binds_exact_artifact_bytes(self) -> None:
        readiness_engine = self.temporary / "readiness_engine"
        readiness_engine.mkdir()
        artifact_hashes = {}
        for name in supervisor_lib.READINESS_ARTIFACTS:
            path = readiness_engine / name
            path.write_bytes(("artifact:" + name).encode("ascii"))
            artifact_hashes[name] = manifest_lib.sha256_file(path)
        test_file_hashes = {}
        for name in supervisor_lib.READINESS_TEST_FILES:
            path = readiness_engine / name
            path.write_bytes(("test:" + name).encode("ascii"))
            test_file_hashes[name] = manifest_lib.sha256_file(path)
        commands = [
            "python -m unittest -v " + " ".join(
                f"problems_external.quintic_taxicab.engine.{Path(name).stem}"
                for name in supervisor_lib.READINESS_TEST_FILES
            )
        ]
        suite_payload = {
            "passed": 1, "failed": 0, "commands": commands,
            "test_files": test_file_hashes,
        }
        tests = dict(suite_payload)
        tests["suite_sha256"] = manifest_lib.sha256_bytes(
            manifest_lib.canonical_bytes(suite_payload)
        )
        reviewed_sha = manifest_lib.sha256_bytes(
            manifest_lib.canonical_bytes({"artifacts": artifact_hashes, "tests": tests})
        )
        now = datetime.now(timezone.utc)
        marker = {
            "schema_version": 1,
            "kind": "q5-launch-readiness",
            "tranche_id": supervisor_lib.TRANCHE_ID,
            "created_utc": manifest_lib.utc_text(now),
            "artifacts": artifact_hashes,
            "tests": tests,
            "referee_verdicts": [
                {"referee": "r1", "verdict": "LAUNCH_SAFE", "reviewed_readiness_sha256": reviewed_sha},
                {"referee": "r2", "verdict": "LAUNCH_SAFE", "reviewed_readiness_sha256": reviewed_sha},
            ],
        }
        self.assertEqual(
            supervisor_lib.validate_readiness(
                marker, engine_dir=readiness_engine, now=now
            ),
            marker,
        )
        (readiness_engine / "q5_supervisor.py").write_bytes(b"drift")
        with self.assertRaisesRegex(supervisor_lib.SupervisorError, "hash drift"):
            supervisor_lib.validate_readiness(
                marker, engine_dir=readiness_engine, now=now
            )

    def test_aggregate_reservation_is_machine_wide_and_reusable(self) -> None:
        self.assertEqual(
            supervisor_lib.AGGREGATE_MUTEX_NAME,
            r"Global\Q5_TORSOR_MACHINE_WORKER_CAP_V1",
        )
        code = (
            f"import sys,time\nsys.path.insert(0,{str(ENGINE)!r})\n"
            "import q5_supervisor as s\n"
            "with s.aggregate_supervisor_reservation():\n"
            " print('HELD',flush=True)\n time.sleep(2)\n"
        )
        holder = subprocess.Popen(
            [sys.executable, "-c", code], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, creationflags=CREATE_NO_WINDOW,
        )
        self.assertEqual(holder.stdout.readline().strip(), "HELD")
        with self.assertRaisesRegex(
            supervisor_lib.SupervisorError, "reservation is held"
        ):
            with supervisor_lib.aggregate_supervisor_reservation():
                self.fail("second machine-wide reservation unexpectedly succeeded")
        stdout, stderr = holder.communicate(timeout=10)
        self.assertEqual(holder.returncode, 0, stdout + stderr)
        with supervisor_lib.aggregate_supervisor_reservation():
            pass

    def test_deadline_between_claim_and_spawn_creates_no_process(self) -> None:
        envelope, manifest, run_dir = self.build("deadline-no-spawn")

        class Guard:
            calls = 0

            def assert_authorization_current(self) -> None:
                return None

            def reached(self) -> bool:
                self.calls += 1
                return self.calls >= 2

            def hard_reached(self) -> bool:
                return False

        with mock.patch.object(supervisor_lib.subprocess, "Popen") as popen:
            summary = self.run_campaign_test(
                envelope, manifest_path=manifest, poll_seconds=0.02,
                deadline_guard=Guard(),
            )
            popen.assert_not_called()
        self.assertEqual(summary["status"], "TIMEOUT_INCOMPLETE")
        self.assertTrue(run_dir.is_dir())

    def test_authorization_expiry_between_claim_and_spawn_blocks_process(self) -> None:
        envelope, manifest, run_dir = self.build("authorization-expiry-boundary")

        class Guard:
            checks = 0

            def reached(self) -> bool:
                return False

            def hard_reached(self) -> bool:
                return False

            def assert_authorization_current(self) -> None:
                self.checks += 1
                if self.checks >= 2:
                    raise supervisor_lib.SupervisorError(
                        "launch authorization expired before claim/spawn"
                    )

        with mock.patch.object(supervisor_lib.subprocess, "Popen") as popen:
            with self.assertRaisesRegex(
                supervisor_lib.SupervisorError, "authorization expired"
            ):
                self.run_campaign_test(
                    envelope, manifest_path=manifest, poll_seconds=0.02,
                    deadline_guard=Guard(),
                )
            popen.assert_not_called()
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(summary["status"], "FAIL_CLOSED")

    def test_terminal_write_crossing_hard_g_is_fail_closed(self) -> None:
        envelope, manifest, run_dir = self.build("hard-g-terminalization")

        class Guard:
            hard_checks = 0

            def reached(self) -> bool:
                return False

            def hard_reached(self) -> bool:
                self.hard_checks += 1
                return self.hard_checks >= 2

            def assert_authorization_current(self) -> None:
                return None

        with self.assertRaisesRegex(
            supervisor_lib.SupervisorError, "terminal summary write"
        ):
            self.run_campaign_test(
                envelope, manifest_path=manifest, poll_seconds=0.02,
                deadline_guard=Guard(),
            )
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        state = json.loads((run_dir / "supervisor_state.json").read_text())
        self.assertEqual(summary["status"], "FAIL_CLOSED")
        self.assertEqual(state["status"], "FAIL_CLOSED")

    def test_worker_artifact_mutation_is_rejected_before_spawn(self) -> None:
        worker = self.temporary / "mutable_worker.py"
        shutil.copy2(MOCK, worker)
        envelope, manifest, run_dir = self.build(
            "artifact-worker-mutation", worker=worker
        )
        manifest_lib.audit_manifest(manifest)
        worker.write_bytes(worker.read_bytes() + b"# mutation\n")
        with mock.patch.object(supervisor_lib.subprocess, "Popen") as popen:
            with self.assertRaisesRegex(
                supervisor_lib.SupervisorError,
                "campaign manifest audit failed: artifact hash drift: worker",
            ):
                self.run_campaign_test(
                    envelope, manifest_path=manifest, poll_seconds=0.02,
                    )
            popen.assert_not_called()
        self.assertFalse(run_dir.exists())

    def test_public_campaign_is_only_native_worker_spawn_boundary(self) -> None:
        self.assertFalse(hasattr(supervisor_lib, "_run_campaign_authorized"))
        self.assertFalse(hasattr(supervisor_lib, "_run_campaign_test_only"))
        tree = ast.parse(SUPERVISOR.read_text(encoding="utf-8"))
        parents = {
            child: parent
            for parent in ast.walk(tree)
            for child in ast.iter_child_nodes(parent)
        }
        popen_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
            and node.func.attr == "Popen"
        ]
        self.assertEqual(len(popen_calls), 1)

        function_path = []
        current = popen_calls[0]
        while current in parents:
            current = parents[current]
            if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_path.append(current.name)
        self.assertEqual(
            tuple(reversed(function_path)),
            ("run_campaign", "_run_authorized_campaign"),
        )

        module_functions = {
            node.name: node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        lexical_owners = {
            name
            for name, function in module_functions.items()
            if popen_calls[0] in set(ast.walk(function))
        }
        self.assertEqual(lexical_owners, {"run_campaign"})
        call_graph = {
            name: {
                node.func.id
                for node in ast.walk(function)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in module_functions
            }
            for name, function in module_functions.items()
        }
        reachable = {"run_campaign"}
        changed = True
        while changed:
            changed = False
            for caller, callees in call_graph.items():
                if caller not in reachable and callees & reachable:
                    reachable.add(caller)
                    changed = True
        self.assertEqual(reachable, {"run_campaign", "main"})
        self.assertFalse(
            any(
                isinstance(node, ast.ImportFrom)
                and node.module == "subprocess"
                and any(alias.name == "Popen" for alias in node.names)
                for node in ast.walk(tree)
            )
        )
        self.assertFalse(
            any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "Popen"
                for node in ast.walk(tree)
            )
        )

    def test_public_poll_seconds_range_is_fail_closed(self) -> None:
        envelope, manifest, run_dir = self.build("public-poll-range")
        for value in (
            0.0, 0.019999, 5.000001, float("nan"), float("inf"), True, "0.02",
        ):
            with self.subTest(value=value):
                with (
                    mock.patch.object(
                        supervisor_lib, "aggregate_supervisor_reservation"
                    ) as reservation,
                    mock.patch.object(supervisor_lib.subprocess, "Popen") as popen,
                    self.assertRaisesRegex(
                        supervisor_lib.SupervisorError,
                        "poll_seconds must be between 0.02 and 5.0",
                    ),
                ):
                    supervisor_lib.run_campaign(
                        envelope,
                        manifest_path=manifest,
                        poll_seconds=value,
                        authorization_path=self.temporary / "unused.json",
                    )
                reservation.assert_not_called()
                popen.assert_not_called()
        self.assertFalse(run_dir.exists())

    def test_post_spawn_census_failure_terminates_registered_worker(self) -> None:
        envelope, manifest, run_dir = self.build(
            "post-spawn-census-cleanup", D=1
        )
        worker = self.StoppableProcess(81000)
        observed: list[dict[int, object]] = []

        def census(active: dict[int, object]) -> dict[str, object]:
            observed.append(dict(active))
            if active:
                raise supervisor_lib.SupervisorError(
                    "synthetic post-spawn census failure"
                )
            return {"active_processes": [], "errors": []}

        with (
            mock.patch.object(
                supervisor_lib.subprocess, "Popen", return_value=worker
            ) as popen,
            self.assertRaisesRegex(
                supervisor_lib.SupervisorError,
                "synthetic post-spawn census failure",
            ),
        ):
            self.run_campaign_test(
                envelope,
                manifest_path=manifest,
                poll_seconds=0.02,
                census_side_effect=census,
            )
        popen.assert_called_once()
        self.assertTrue(any(snapshot == {0: worker} for snapshot in observed))
        self.assertEqual(worker.poll(), -15)
        state = json.loads((run_dir / "supervisor_state.json").read_text())
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(state["status"], "FAIL_CLOSED")
        self.assertEqual(state["spawned_lane_ids"], [0])
        self.assertEqual(state["owned_pids"], [])
        self.assertEqual(state["lanes"]["0"]["status"], "STOPPED_FAIL_CLOSED")
        self.assertEqual(summary["status"], "FAIL_CLOSED")
        self.assertEqual(summary["owned_pids"], [])

    def test_stream_context_exit_failure_terminates_registered_worker(self) -> None:
        envelope, manifest, run_dir = self.build(
            "stream-exit-cleanup", D=1
        )
        worker = self.StoppableProcess(82000)
        real_open = Path.open

        class FailingExit:
            def __init__(self, stream: object) -> None:
                self.stream = stream

            def __enter__(self) -> object:
                return self.stream

            def __exit__(
                self, exc_type: object, exc: object, traceback: object
            ) -> None:
                self.stream.close()
                raise OSError("synthetic stream-context exit")

        def open_with_failing_stderr(
            path: Path, *args: object, **kwargs: object
        ) -> object:
            stream = real_open(path, *args, **kwargs)
            if path.name == "lane_00.stderr.txt":
                return FailingExit(stream)
            return stream

        with (
            mock.patch.object(
                supervisor_lib.subprocess, "Popen", return_value=worker
            ) as popen,
            mock.patch.object(Path, "open", new=open_with_failing_stderr),
            self.assertRaisesRegex(
                supervisor_lib.SupervisorError,
                "synthetic stream-context exit",
            ),
        ):
            self.run_campaign_test(
                envelope, manifest_path=manifest, poll_seconds=0.02
            )
        popen.assert_called_once()
        self.assertEqual(worker.poll(), -15)
        state = json.loads((run_dir / "supervisor_state.json").read_text())
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(state["spawned_lane_ids"], [0])
        self.assertEqual(state["lanes"]["0"]["status"], "STOPPED_FAIL_CLOSED")
        self.assertEqual(summary["status"], "FAIL_CLOSED")
        self.assertEqual(summary["owned_pids"], [])

    def test_terminal_inventory_rejects_unexpected_entry(self) -> None:
        envelope, manifest, run_dir = self.build(
            "terminal-extra-artifact", D=1
        )

        def spawn(command: list[str], **_: object) -> object:
            lane_id = int(command[command.index("--lane-id") + 1])
            result_path = Path(command[command.index("--result") + 1])
            manifest_lib.atomic_write_json(
                result_path,
                self.synthetic_lane_result(envelope, lane_id, "NO_HIT"),
            )
            (run_dir / "unexpected.tmp").write_bytes(b"unexpected")
            return self.TerminalProcess(83000, 0)

        with (
            mock.patch.object(
                supervisor_lib.subprocess, "Popen", side_effect=spawn
            ),
            self.assertRaisesRegex(
                supervisor_lib.SupervisorError,
                "terminal run-dir inventory mismatch",
            ),
        ):
            self.run_campaign_test(
                envelope, manifest_path=manifest, poll_seconds=0.02
            )
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(summary["status"], "FAIL_CLOSED")
        self.assertIn("unexpected.tmp", summary["anomaly"])

    def test_terminal_inventory_rejects_nonregular_expected_entry(self) -> None:
        envelope, manifest, run_dir = self.build(
            "terminal-nonregular-artifact", D=1
        )
        process = self.TerminalProcess(84000, 0)

        def spawn(command: list[str], **_: object) -> object:
            lane_id = int(command[command.index("--lane-id") + 1])
            result_path = Path(command[command.index("--result") + 1])
            manifest_lib.atomic_write_json(
                result_path,
                self.synthetic_lane_result(envelope, lane_id, "NO_HIT"),
            )
            return process

        active_checks = 0

        def census(active: dict[int, object]) -> dict[str, object]:
            nonlocal active_checks
            if active:
                active_checks += 1
                if active_checks == 2:
                    stdout_path = run_dir / "lane_00.stdout.txt"
                    stdout_path.unlink()
                    stdout_path.mkdir()
            return {"active_processes": [], "errors": []}

        with (
            mock.patch.object(
                supervisor_lib.subprocess, "Popen", side_effect=spawn
            ),
            self.assertRaisesRegex(
                supervisor_lib.SupervisorError,
                "not a regular non-reparse file",
            ),
        ):
            self.run_campaign_test(
                envelope,
                manifest_path=manifest,
                poll_seconds=0.02,
                census_side_effect=census,
            )
        self.assertEqual(active_checks, 2)
        summary = json.loads((run_dir / "supervisor_summary.json").read_text())
        self.assertEqual(summary["status"], "FAIL_CLOSED")


    def test_verifier_artifact_mutation_between_verifiers_is_rejected(self) -> None:
        envelope, _, _ = self.build("artifact-verifier-mutation")
        artifacts = json.loads(json.dumps(envelope["payload"]["artifacts"]))
        native = self.temporary / "mutable_verify_independent.exe"
        shutil.copy2(INDEPENDENT, native)
        artifacts["independent_verifier"] = manifest_lib.artifact_record(native)
        values = (1, 2, 3, 4)
        scalar_report = {
            "valid": True,
            "certificate": dict(zip(("a", "b", "c", "d"), values)),
            "left_sum": values[0] ** 5 + values[1] ** 5,
        }

        def scalar_then_mutate(command: list[str]) -> dict:
            native.write_bytes(native.read_bytes() + b"mutation")
            return scalar_report

        with mock.patch.object(
            supervisor_lib, "_run_verifier", side_effect=scalar_then_mutate
        ) as verifier:
            with self.assertRaises(PermissionError):
                supervisor_lib.dual_verify_candidate(values, artifacts)
        self.assertEqual(verifier.call_count, 1)
if __name__ == "__main__":
    unittest.main()
