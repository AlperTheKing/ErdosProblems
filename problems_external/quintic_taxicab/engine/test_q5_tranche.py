#!/usr/bin/env python3
"""Fast, no-launch contract tests for :mod:`q5_tranche`.

Every filesystem mutation in this suite is redirected to a temporary
directory.  In particular, the production global lock and tranche directory
must remain absent before and after every test.
"""

from __future__ import annotations

import argparse
import ast
import copy
import shutil
import hashlib
import inspect
import json
import os
import sys
import uuid
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock
ENGINE = Path(__file__).resolve().parent
sys.path.insert(0, str(ENGINE))


import q5_tranche as tranche


UTC = timezone.utc
ZERO_SHA = "0" * 64
FROZEN_SOURCE_SHA = "78928e3074a0c50754990fab6d73c72cddd63b9eb79936902326fed38fab766d"
FROZEN_TOOL_SHA = "e4b062dd5273e4510c359f55a39565efc9fa8e0b19ad2818a5228ce87a663a6c"
FROZEN_TABLE_SHA = "c9cb415199bcb60513c8b41b15c866073f806c9dc7116320471fe7c38e3dac0a"
FROZEN_PAYLOAD_SHA = "f3defaf9d3aa173c800e82d8ab62f24048cafc8d6e8fb16b5ce00106a9791cf8"


def iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def clock_lock(t0: datetime) -> dict[str, object]:
    return {
        "schema_version": 1,
        "kind": "Q5_TRANCHE_GLOBAL_LOCK",
        "tranche_id": tranche.TRANCHE_ID,
        "t0": tranche._utc_text(t0),
        "s": tranche._utc_text(t0 + timedelta(seconds=25_200)),
        "launch_readiness_sha256": ZERO_SHA,
        "g": tranche._utc_text(t0 + timedelta(seconds=28_800)),
        "creator_pid": 1,
        "claimed_utc": tranche._utc_text(t0),
        "magic_terminal_summary_sha256": ZERO_SHA,
    }


def timing_state(now: datetime, remaining_ms: int = 300_050) -> dict[str, object]:
    rows = [
        {"lane_id": lane, "elapsed_milliseconds": 10, "weight": 2}
        for lane in range(64)
    ]
    return {
        "accepted_pilots": {
            "A": {"timing_rows": []},
            "B": {"timing_rows": copy.deepcopy(rows)},
            "C": {"timing_rows": copy.deepcopy(rows)},
            "D": {"timing_rows": copy.deepcopy(rows)},
        },
        "s": iso(now + timedelta(milliseconds=remaining_ms)),
        "updated_utc": iso(now),
    }


def candidate_row(h: int, maximum: int) -> dict[str, object]:
    return {
        "H": h,
        "b": 7,
        "balance_pass": True,
        "max_lane_weight": maximum,
        "min_lane_weight": maximum - 1,
        "oeis_gate_pass": True,
        "specialization_count": 100,
    }


class Q5TrancheNoLaunchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertFalse(tranche.LOCK_PATH.exists(), "production tranche lock already exists")
        self.assertFalse(tranche.TRANCHE_DIR.exists(), "production tranche directory already exists")

    def tearDown(self) -> None:
        self.assertFalse(tranche.LOCK_PATH.exists(), "test created production tranche lock")
        self.assertFalse(tranche.TRANCHE_DIR.exists(), "test created production tranche directory")
    def _main_fixture(self, status: str = "FINITE_NO_HIT") -> dict[str, object]:
        now = datetime.now(UTC).replace(microsecond=0)
        if status == "TIMEOUT_INCOMPLETE":
            t0 = now - timedelta(hours=7, minutes=10)
        else:
            t0 = now - timedelta(hours=1)
        lock = clock_lock(t0)
        lock["boot_time_microseconds"] = 1
        lock["monotonic_start_ns"] = 1
        selection_time = (
            tranche._parse_time(lock["s"], "S") - timedelta(minutes=20)
            if status == "TIMEOUT_INCOMPLETE"
            else now - timedelta(minutes=20)
        )
        created = selection_time - timedelta(minutes=1)
        launch_claimed = selection_time + timedelta(minutes=1)
        s = tranche._parse_time(lock["s"], "S")
        if status == "TIMEOUT_INCOMPLETE":
            finished = s + timedelta(seconds=1)
        else:
            finished = launch_claimed + timedelta(minutes=1)
        final_updated = finished

        root = tranche.ENGINE_DIR / f"q5-main-accept-test-{uuid.uuid4().hex}"
        root.mkdir()
        self.addCleanup(shutil.rmtree, root, True)
        manifest_path = root / "main" / "manifest.json"
        lanes_dir = root / "main" / "lanes"
        run_dir = root / "main" / "run"
        report_path = root / "selection_report.json"
        terminal_report_path = root / "main_terminal_report.json"
        manifest_path.parent.mkdir(parents=True)
        authorizations_dir = root / "authorizations"
        authorization_path = authorizations_dir / "MAIN.json"
        readiness_path = root / "Q5_LAUNCH_READY.json"
        public_status_path = root / "public_status_gate.json"
        state_path = root / "state.json"
        lanes_dir.mkdir()
        run_dir.mkdir()

        artifact_records: dict[str, dict[str, object]] = {}
        frozen_artifacts: dict[str, str] = {}
        for role, raw_path in tranche.MANIFEST_ARTIFACT_PATHS.items():
            path = raw_path.resolve()
            digest = tranche._sha256_file(path)
            artifact_records[role] = {
                "path": str(path),
                "size": path.stat().st_size,
                "sha256": digest,
            }
            frozen_artifacts[str(path)] = digest

        payload_digest = "a" * 64
        lanes: list[dict[str, object]] = []
        for lane_id in range(64):
            lane_file = lanes_dir / f"lane_{lane_id:02d}.tsv"
            result_path = run_dir / f"lane_{lane_id:02d}.result.json"
            lanes.append(
                {
                    "lane_id": lane_id,
                    "estimated_weight": 1,
                    "specializations": [
                        {"p": lane_id + 1, "q": 1, "estimated_work": 1}
                    ],
                    "assignment_sha256": ZERO_SHA,
                    "lane_file": {
                        "path": str(lane_file.resolve()),
                        "size": 0,
                        "sha256": ZERO_SHA,
                    },
                    "command": [],
                    "result_path": str(result_path.resolve()),
                }
            )
        payload = {
            "mode": "SELECTED_MAIN",
            "campaign_id": tranche.MAIN_CAMPAIGN_ID,
            "search_mode": "canonical_positive_u_positive_y",
            "worker_kind": "native",
            "bounds": {"P": 48, "Q": 48, "N": 48, "D": 48},
            "deadline": iso(s),
            "manifest_path": str(manifest_path.resolve()),
            "run_dir": str(run_dir.resolve()),
            "created_utc": iso(created),
            "artifacts": artifact_records,
            "lanes": lanes,
        }
        envelope = {"payload": payload, "payload_sha256": payload_digest}
        manifest_path.write_text(
            json.dumps(envelope, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )

        hit: dict[str, object] | None = None
        if status == "VERIFIED_HIT":
            hit = {
                "lane_id": 0,
                "candidate_index": 0,
                "integer_quadruple": ["1", "2", "3", "4"],
                "scalar_report": {},
                "independent_report": {},
                "candidate_observed_utc": iso(launch_claimed + timedelta(seconds=15)),
                "verified_utc": iso(launch_claimed + timedelta(seconds=30)),
            }

        lane_statuses: dict[str, str] = {}
        lanes_state: dict[str, dict[str, object]] = {}
        for lane in lanes:
            lane_id = int(lane["lane_id"])
            if status == "FINITE_NO_HIT":
                result_status = "NO_HIT"
                terminal_status = "NO_HIT"
            elif status == "TIMEOUT_INCOMPLETE":
                result_status = "TIMEOUT_INCOMPLETE"
                terminal_status = "TIMEOUT_INCOMPLETE"
            elif lane_id == 0:
                result_status = "HIT"
                terminal_status = "VERIFIED_HIT"
            else:
                result_status = "NO_HIT"
                terminal_status = "NO_HIT"

            counts = {key: "0" for key in tranche.supervisor_lib.COUNT_KEYS}
            counts["reduced_t_values"] = "1"
            candidates: list[dict[str, object]] = []
            if result_status == "HIT":
                counts["pairs_considered"] = "1"
                counts["admissible_specializations"] = "1"
                counts["bounded_z_squares"] = "1"
                counts["candidate_records"] = "1"
                counts["verified_integer_certificates"] = "1"
                assert hit is not None
                candidates = [{"integer_quadruple": hit["integer_quadruple"]}]
            result = {
                "schema_version": 1,
                "kind": "Q5_TORSOR_LANE_RESULT",
                "campaign_id": tranche.MAIN_CAMPAIGN_ID,
                "manifest_payload_sha256": payload_digest,
                "lane_file_sha256": ZERO_SHA,
                "search_mode": "canonical_positive_u_positive_y",
                "lane_id": lane_id,
                "assignment_sha256": ZERO_SHA,
                "status": result_status,
                "signed_u_symmetry_pruned": True,
                "negative_y_pruned": True,
                "zero_u_pruned": True,
                "emit_torsor_points": False,
                "elapsed_milliseconds": "1",
                "assigned_specializations": 1,
                "completed_specializations": (
                    0 if result_status == "TIMEOUT_INCOMPLETE" else 1
                ),
                "counts": counts,
                "zero_z_rejected_as_nontarget": True,
                "complete": result_status == "NO_HIT",
                "candidates": candidates,
            }
            Path(lane["result_path"]).write_text(
                json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="ascii",
            )
            (run_dir / f"lane_{lane_id:02d}.stdout.txt").write_bytes(b"")
            (run_dir / f"lane_{lane_id:02d}.stderr.txt").write_bytes(b"")
            lane_statuses[str(lane_id)] = terminal_status
            lanes_state[str(lane_id)] = {
                "status": terminal_status,
                "pid": None,
                "assigned_specializations": 1,
            }

        launch_lock = {
            "schema_version": 1,
            "kind": "Q5_TORSOR_LAUNCH_LOCK",
            "campaign_id": tranche.MAIN_CAMPAIGN_ID,
            "manifest_payload_sha256": payload_digest,
            "supervisor_pid": 4242,
            "launch_readiness_sha256": ZERO_SHA,
            "authorization_sha256": ZERO_SHA,
            "authorization_expires_utc": iso(launch_claimed + timedelta(minutes=4)),
            "claimed_utc": iso(launch_claimed),
        }
        (run_dir / "launch.lock").write_text(
            json.dumps(launch_lock, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        summary = {
            "schema_version": 1,
            "kind": "Q5_TORSOR_SUPERVISOR_SUMMARY",
            "campaign_id": tranche.MAIN_CAMPAIGN_ID,
            "manifest_path": str(manifest_path.resolve()),
            "manifest_payload_sha256": payload_digest,
            "status": status,
            "finished_utc": iso(finished),
            "owned_pids": [],
            "spawned_lane_ids": list(range(64)),
            "verified_hit": hit,
            "lane_statuses": lane_statuses,
        }
        final_state = {
            "schema_version": 1,
            "kind": "Q5_TORSOR_SUPERVISOR_STATE",
            "campaign_id": tranche.MAIN_CAMPAIGN_ID,
            "manifest_payload_sha256": payload_digest,
            "status": status,
            "updated_utc": iso(final_updated),
            "supervisor_pid": 4242,
            "owned_pids": [],
            "spawned_lane_ids": list(range(64)),
            "lanes": lanes_state,
            "anomaly": None,
        }
        (run_dir / "supervisor_summary.json").write_text(
            json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        (run_dir / "supervisor_state.json").write_text(
            json.dumps(final_state, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        if hit is not None:
            verified_path = run_dir / "lane_00.candidate_000.verified.json"
            verified_path.write_text(
                json.dumps(hit, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="ascii",
            )

        selection_report = {
            "schema_version": 1,
            "kind": "Q5_TRANCHE_SELECTION_REPORT",
            "tranche_id": tranche.TRANCHE_ID,
            "generated_utc": iso(selection_time),
            "selection_setup_deadline_utc": iso(selection_time + timedelta(minutes=5)),
            "selected_h": 48,
            "selected_main_manifest_path": str(manifest_path.resolve()),
            "selected_main_manifest_sha256": payload_digest,
            "public_status_gate": {"checked_utc": iso(selection_time), "file_sha256": ZERO_SHA},
        }
        report_path.write_text(
            json.dumps(selection_report, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        state = tranche._state_template(lock, "MAIN_FROZEN", selection_time)
        state["accepted_pilots"] = {name: {} for name in tranche.PILOT_ORDER}
        state["selection_report_sha256"] = tranche._sha256_file(report_path)
        state["selected_h"] = 48
        state["selected_main_manifest_sha256"] = payload_digest
        plan = {
            "t0": lock["t0"],
            "s": lock["s"],
            "g": lock["g"],
            "frozen_artifact_hashes": frozen_artifacts,
            "launch_readiness": {
                "path": str(readiness_path.resolve()),
                "file_sha256": ZERO_SHA,
            },
            "authorization_paths": {
                phase: str((authorizations_dir / f"{phase}.json").resolve())
                for phase in (*tranche.PILOT_ORDER, "MAIN")
            },
        }
        state_bytes = tranche._pretty_bytes(state)
        state_path.write_bytes(state_bytes)
        state_sha256 = hashlib.sha256(state_bytes).hexdigest()

        authorizations_dir.mkdir()
        authorization_ticket = {
            "schema_version": 1,
            "kind": "q5-launch-authorization-v1",
            "tranche_id": tranche.TRANCHE_ID,
            "phase": "MAIN",
            "created_utc": iso(launch_claimed - timedelta(minutes=1)),
            "expires_utc": launch_lock["authorization_expires_utc"],
            "state_path": str(state_path.resolve()),
            "state_sha256": state_sha256,
            "manifest_path": str(manifest_path.resolve()),
            "manifest_file_sha256": tranche._sha256_file(manifest_path),
            "manifest_payload_sha256": payload_digest,
            "campaign_id": tranche.MAIN_CAMPAIGN_ID,
            "mode": "SELECTED_MAIN",
            "search_mode": "canonical_positive_u_positive_y",
            "deadline": payload["deadline"],
            "run_dir": str(run_dir.resolve()),
            "readiness_path": str(readiness_path.resolve()),
            "readiness_sha256": ZERO_SHA,
            "public_status_path": str(public_status_path.resolve()),
            "public_status_sha256": ZERO_SHA,
        }
        authorization_bytes = tranche._pretty_bytes(authorization_ticket)
        authorization_path.write_bytes(authorization_bytes)
        launch_lock["authorization_sha256"] = hashlib.sha256(
            authorization_bytes
        ).hexdigest()
        (run_dir / "launch.lock").write_bytes(tranche._pretty_bytes(launch_lock))
        census = {
            "schema_version": 1,
            "kind": "Q5_TRANCHE_PROCESS_CENSUS",
            "captured_utc": iso(now),
            "active_processes": [],
            "artifact_hashes": frozen_artifacts,
            "errors": [],
        }
        return {
            "now": now,
            "lock": lock,
            "plan": plan,
            "state": state,
            "envelope": envelope,
            "manifest_path": manifest_path,
            "lanes_dir": lanes_dir,
            "run_dir": run_dir,
            "selection_report_path": report_path,
            "terminal_report_path": terminal_report_path,
            "selection_report": selection_report,
            "state_path": state_path,
            "state_bytes": state_bytes,
            "state_sha256": state_sha256,
            "authorizations_dir": authorizations_dir,
            "authorization_path": authorization_path,
            "authorization_ticket": authorization_ticket,
            "readiness_path": readiness_path,
            "public_status_path": public_status_path,
            "launch_lock": launch_lock,
            "census": census,
        }

    def _call_accept_main(
        self,
        case: dict[str, object],
        *,
        census: dict[str, object] | None = None,
    ) -> tuple[dict[str, object], dict[str, object]]:
        captured: dict[str, object] = {}
        transition_mock = mock.Mock()
        fail_closed = mock.Mock()
        public_revalidate = mock.Mock()
        authorization_validation = mock.Mock(
            wraps=tranche._validate_authorization_ticket
        )
        chosen_census = copy.deepcopy(
            census if census is not None else case["census"]
        )
        live_census = mock.Mock(return_value=chosen_census)
        case.update(
            transition_mock=transition_mock,
            fail_closed_mock=fail_closed,
            public_revalidate_mock=public_revalidate,
            authorization_validation_mock=authorization_validation,
            live_census_mock=live_census,
        )
        intents_dir = case["state_path"].parent / "intents"

        result: dict[str, object] | None = None
        with mock.patch.object(tranche, "TRANCHE_DIR", case["state_path"].parent), \
                mock.patch.object(tranche, "INTENTS_DIR", intents_dir), \
                mock.patch.object(tranche, "MAIN_MANIFEST_PATH", case["manifest_path"]), \
                mock.patch.object(tranche, "MAIN_LANE_CONFIG_DIR", case["lanes_dir"]), \
                mock.patch.object(tranche, "STATE_PATH", case["state_path"]), \
                mock.patch.object(tranche, "AUTHORIZATIONS_DIR", case["authorizations_dir"]), \
                mock.patch.object(tranche, "READINESS_PATH", case["readiness_path"]), \
                mock.patch.object(tranche, "PUBLIC_STATUS_PATH", case["public_status_path"]), \
                mock.patch.object(tranche, "MAIN_RUN_DIR", case["run_dir"]), \
                mock.patch.object(tranche, "SELECTION_REPORT_PATH", case["selection_report_path"]), \
                mock.patch.object(tranche, "MAIN_TERMINAL_REPORT_PATH", case["terminal_report_path"]), \
                mock.patch.object(
                    tranche, "_load_context",
                    return_value=(
                        copy.deepcopy(case["lock"]),
                        copy.deepcopy(case["plan"]),
                        copy.deepcopy(case["state"]),
                    ),
                ), \
                mock.patch.object(tranche, "_validate_transition_clock"), \
                mock.patch.object(tranche, "_revalidate_accepted_artifacts"), \
                mock.patch.object(
                    tranche.manifest_lib,
                    "audit_manifest",
                    return_value=copy.deepcopy(case["envelope"]),
                ), \
                mock.patch.object(
                    tranche, "_validate_verified_hit",
                    side_effect=lambda value: copy.deepcopy(value),
                ), \
                mock.patch.object(
                    tranche, "_revalidate_public_status_evidence",
                    public_revalidate,
                ), \
                mock.patch.object(
                    tranche, "_validate_authorization_ticket",
                    authorization_validation,
                ), \
                mock.patch.object(tranche, "_now_utc", return_value=case["now"]), \
                mock.patch.object(tranche, "_live_census", live_census):
            try:
                result = tranche.accept_main()
            finally:
                if case["state_path"].is_file():
                    committed = json.loads(
                        case["state_path"].read_text(encoding="ascii")
                    )
                    if committed.get("phase") == "FAIL_CLOSED":
                        fail_closed(committed)
                    elif committed.get("phase") != case["state"].get("phase"):
                        transition_mock(committed)
                        report_bytes = case["terminal_report_path"].read_bytes()
                        updates = {
                            "main_terminal_report_sha256":
                                committed["main_terminal_report_sha256"],
                        }
                        if committed.get("verified_hit") is not None:
                            updates["verified_hit"] = copy.deepcopy(
                                committed["verified_hit"]
                            )
                        captured.update(
                            phase=committed["phase"],
                            now=tranche._parse_time(
                                committed["updated_utc"], "committed state"
                            ),
                            updates=updates,
                            extra_files={
                                case["terminal_report_path"]: report_bytes
                            },
                        )
        assert result is not None
        return result, captured


    def test_plan_pins_global_lock_and_load_context_rejects_drift(self) -> None:
        root = tranche.ENGINE_DIR / f"q5-lock-pin-test-{uuid.uuid4().hex}"
        root.mkdir()
        self.addCleanup(shutil.rmtree, root, True)
        lock_path = root / "q5_tranche.lock"
        plan_path = root / "plan.json"
        state_path = root / "state.json"
        intents_dir = root / "intents"
        intents_dir.mkdir()

        t0 = datetime(2026, 7, 21, 5, 0, 0, tzinfo=UTC)
        lock = clock_lock(t0)
        lock.update(
            frozen_artifact_hashes={},
            boot_time_microseconds=1,
            monotonic_start_ns=1,
        )
        lock_path.write_text(
            json.dumps(lock, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        with mock.patch.object(tranche, "LOCK_PATH", lock_path):
            generated = tranche._plan(
                lock,
                {},
                (
                    {"artifact_hashes": {}},
                    {"artifact_hashes": {}},
                    {"artifact_hashes": {}},
                ),
            )
        self.assertEqual(
            generated["global_lock_sha256"], tranche._sha256_file(lock_path)
        )

        plan = {
            "t0": lock["t0"],
            "s": lock["s"],
            "g": lock["g"],
            "magic_terminal": {"summary_sha256": ZERO_SHA},
            "frozen_artifact_hashes": {},
            "launch_readiness": {
                "path": str(tranche.READINESS_PATH.resolve()),
                "file_sha256": ZERO_SHA,
            },
            "global_lock_sha256": tranche._sha256_file(lock_path),
        }
        plan_path.write_text(
            json.dumps(plan, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        state = tranche._state_template(lock, "READY_A", t0)
        state["plan_sha256"] = tranche._sha256_file(plan_path)
        state_path.write_text(
            json.dumps(state, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        with mock.patch.object(tranche, "LOCK_PATH", lock_path), \
                mock.patch.object(tranche, "PLAN_PATH", plan_path), \
                mock.patch.object(tranche, "STATE_PATH", state_path), \
                mock.patch.object(tranche, "_validate_readiness", return_value={"file_sha256": ZERO_SHA}), \
                mock.patch.object(
                    tranche, "_validate_magic_terminal",
                    return_value={"summary_sha256": ZERO_SHA},
                ) as magic_validator, \
                mock.patch.object(
                    tranche, "_artifact_hashes", return_value={}
                ) as artifact_hashes, \
                mock.patch.object(tranche, "INTENTS_DIR", intents_dir), \
                mock.patch.object(tranche, "_validate_ledger"):
            loaded_lock, loaded_plan, loaded_state = tranche._load_context()
            self.assertEqual(loaded_lock, lock)
            self.assertEqual(loaded_plan, plan)
            self.assertEqual(loaded_state, state)

            magic_validator.return_value = {"summary_sha256": "1" * 64}
            with self.assertRaisesRegex(
                tranche.PermanentFailure, "magic terminal prerequisite differs"
            ):
                tranche._load_context()
            magic_validator.return_value = {"summary_sha256": ZERO_SHA}

            artifact_hashes.return_value = {"unexpected": "2" * 64}
            with self.assertRaisesRegex(
                tranche.PermanentFailure, "frozen runtime artifacts drifted"
            ):
                tranche._load_context()
            artifact_hashes.return_value = {}


            drifted = copy.deepcopy(lock)
            drifted["monotonic_start_ns"] = 2
            lock_path.write_text(
                json.dumps(drifted, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="ascii",
            )
            with self.assertRaisesRegex(
                tranche.PermanentFailure, "global lock differs"
            ):
                tranche._load_context()

    def test_accept_main_finite_no_hit_and_timeout_pin_reports(self) -> None:
        expected_phases = {
            "FINITE_NO_HIT": "MAIN_FINITE_NO_HIT",
            "TIMEOUT_INCOMPLETE": "MAIN_TIMEOUT_INCOMPLETE",
        }
        for status, expected_phase in expected_phases.items():
            with self.subTest(status=status):
                case = self._main_fixture(status)
                result, captured = self._call_accept_main(case)
                self.assertTrue(result["ok"])
                self.assertFalse(result["already_accepted"])
                self.assertEqual(result["phase"], expected_phase)
                self.assertEqual(result["status"], status)
                self.assertEqual(captured["phase"], expected_phase)
                extra_files = captured["extra_files"]
                self.assertEqual(set(extra_files), {case["terminal_report_path"]})
                report_bytes = extra_files[case["terminal_report_path"]]
                report = json.loads(report_bytes.decode("ascii"))
                self.assertEqual(report["status"], status)
                self.assertEqual(report["lane_status_counts"], {status.replace("FINITE_", ""): 64})
                self.assertEqual(len(report["result_sha256"]), 64)
                self.assertEqual(report["spawned_lane_ids"], list(range(64)))
                expected_lane_ids = {str(lane_id) for lane_id in range(64)}
                self.assertEqual(set(report["stdout_sha256"]), expected_lane_ids)
                self.assertEqual(set(report["stderr_sha256"]), expected_lane_ids)
                expected_inventory = {
                    "launch.lock", "supervisor_state.json", "supervisor_summary.json",
                } | {
                    f"lane_{lane_id:02d}.{suffix}"
                    for lane_id in range(64)
                    for suffix in ("result.json", "stdout.txt", "stderr.txt")
                }
                self.assertEqual(set(report["run_inventory"]), expected_inventory)
                self.assertEqual(report["missing_result_lane_ids"], [])
                self.assertEqual(
                    captured["updates"]["main_terminal_report_sha256"],
                    hashlib.sha256(report_bytes).hexdigest(),
                )
                case["fail_closed_mock"].assert_not_called()
                self.assertEqual(case["public_revalidate_mock"].call_count, 2)
                self.assertEqual(
                    case["authorization_validation_mock"].call_count, 2
                )
                self.assertEqual(case["live_census_mock"].call_count, 2)


    def test_accept_main_verified_artifact_is_pinned(self) -> None:
        case = self._main_fixture("VERIFIED_HIT")
        result, captured = self._call_accept_main(case)
        self.assertFalse(result["already_accepted"])
        self.assertEqual(result["phase"], "VERIFIED_HIT")
        report_bytes = captured["extra_files"][case["terminal_report_path"]]
        report = json.loads(report_bytes.decode("ascii"))
        verified_path = case["run_dir"] / "lane_00.candidate_000.verified.json"
        self.assertEqual(report["verified_hit"], case["state"].get("verified_hit") or json.loads(
            verified_path.read_text(encoding="ascii")
        ))
        self.assertEqual(report["verified_artifact_path"], str(verified_path))
        self.assertEqual(
            report["verified_artifact_sha256"], tranche._sha256_file(verified_path)
        )
        binding = captured["updates"]["verified_hit"]
        self.assertEqual(binding["source"], "main")
        self.assertEqual(binding["source_id"], tranche.MAIN_CAMPAIGN_ID)
        self.assertEqual(binding["record"], report["verified_hit"])
        self.assertEqual(
            binding["source_evidence_sha256"],
            hashlib.sha256(report_bytes).hexdigest(),
        )
        self.assertEqual(report["lane_status_counts"], {"NO_HIT": 63, "VERIFIED_HIT": 1})
        case["fail_closed_mock"].assert_not_called()

    def test_accept_main_rejects_missing_malformed_results_and_stderr(self) -> None:
        cases: list[tuple[str, callable]] = [
            (
                "missing_result",
                lambda fixture: (fixture["run_dir"] / "lane_00.result.json").unlink(),
            ),
            (
                "malformed_result",
                lambda fixture: (fixture["run_dir"] / "lane_00.result.json").write_text(
                    "{}\n", encoding="ascii"
                ),
            ),
            (
                "nonempty_stderr",
                lambda fixture: (fixture["run_dir"] / "lane_00.stderr.txt").write_bytes(
                    b"synthetic error\n"
                ),
            ),
        ]
        for name, mutate in cases:
            with self.subTest(name=name):
                case = self._main_fixture("FINITE_NO_HIT")
                mutate(case)
                with self.assertRaises(tranche.PermanentFailure):
                    self._call_accept_main(case)
                case["fail_closed_mock"].assert_called_once()

    def test_accept_main_rejects_missing_stdout_and_unexpected_files(self) -> None:
        cases: list[tuple[str, callable]] = [
            (
                "missing_stdout",
                lambda fixture: (fixture["run_dir"] / "lane_00.stdout.txt").unlink(),
            ),
            (
                "unexpected_extra_file",
                lambda fixture: (fixture["run_dir"] / "unexpected.txt").write_bytes(b""),
            ),
        ]
        for name, mutate in cases:
            with self.subTest(name=name):
                case = self._main_fixture("FINITE_NO_HIT")
                mutate(case)
                with self.assertRaises(tranche.PermanentFailure):
                    self._call_accept_main(case)
                case["fail_closed_mock"].assert_called_once()

    def test_accept_main_rejects_unclean_census_and_preselection_launch(self) -> None:
        case = self._main_fixture("FINITE_NO_HIT")
        bad_census = copy.deepcopy(case["census"])
        bad_census["active_processes"] = [{"pid": 999999}]
        with self.assertRaises(tranche.PermanentFailure):
            self._call_accept_main(case, census=bad_census)
        case["fail_closed_mock"].assert_called_once()

        case = self._main_fixture("FINITE_NO_HIT")
        launch_claimed = tranche._parse_time(
            case["launch_lock"]["claimed_utc"], "launch"
        )
        report = copy.deepcopy(case["selection_report"])
        report["generated_utc"] = iso(launch_claimed + timedelta(seconds=1))
        report["public_status_gate"]["checked_utc"] = iso(
            launch_claimed - timedelta(minutes=1)
        )
        case["selection_report_path"].write_text(
            json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        case["state"]["selection_report_sha256"] = tranche._sha256_file(
            case["selection_report_path"]
        )
        with self.assertRaises(tranche.PermanentFailure):
            self._call_accept_main(case)
        case["fail_closed_mock"].assert_called_once()

    def test_accept_main_is_idempotent_after_terminal_commit(self) -> None:
        case = self._main_fixture("FINITE_NO_HIT")
        first, captured = self._call_accept_main(case)
        report_bytes = captured["extra_files"][case["terminal_report_path"]]
        case["terminal_report_path"].write_bytes(report_bytes)
        case["state"]["phase"] = first["phase"]
        case["state"]["main_terminal_report_sha256"] = hashlib.sha256(
            report_bytes
        ).hexdigest()

        second, second_capture = self._call_accept_main(case)
        self.assertTrue(second["ok"])
        self.assertEqual(second["phase"], "MAIN_FINITE_NO_HIT")
        self.assertTrue(second["already_accepted"])
        self.assertEqual(second["status"], "FINITE_NO_HIT")
        self.assertEqual(second_capture, {})
        case["transition_mock"].assert_not_called()
        case["fail_closed_mock"].assert_not_called()

    def test_terminal_main_audit_replays_public_auth_and_census(self) -> None:
        case = self._main_fixture("FINITE_NO_HIT")
        self._call_accept_main(case)
        terminal_state = json.loads(case["state_path"].read_text(encoding="ascii"))
        terminal_report = json.loads(
            case["terminal_report_path"].read_text(encoding="ascii")
        )
        generated = tranche._parse_time(
            case["selection_report"]["generated_utc"], "selection generated"
        )
        core = {
            "generated_utc": iso(generated),
            "selection_setup_deadline_utc": iso(
                generated + timedelta(minutes=5)
            ),
            "remaining_before_s_milliseconds": 1,
            "setup_guard_milliseconds": 300_000,
            "timing_records": [],
            "rho": {
                "numerator": 1,
                "denominator": 1,
                "source_pilot": "B",
                "source_lane": 0,
            },
            "selected_h": 48,
            "candidates": [],
        }
        selection_report = {
            "schema_version": 1,
            "kind": "Q5_TRANCHE_SELECTION_REPORT",
            "tranche_id": tranche.TRANCHE_ID,
            "t0": terminal_state["t0"],
            "s": terminal_state["s"],
            "g": terminal_state["g"],
            "pilot_evidence": terminal_state["accepted_pilots"],
            "candidate_table": {"rows": []},
            **{key: value for key, value in core.items() if key != "candidates"},
            "selected_main_manifest_path": str(case["manifest_path"].resolve()),
            "selected_main_manifest_sha256":
                terminal_state["selected_main_manifest_sha256"],
            "public_status_gate":
                copy.deepcopy(case["selection_report"]["public_status_gate"]),
        }
        original_load_json = tranche._load_json

        def load_json(path: Path, *args: object, **kwargs: object) -> object:
            if Path(path) == case["selection_report_path"]:
                return copy.deepcopy(selection_report)
            return original_load_json(path, *args, **kwargs)

        public_revalidate = mock.Mock()
        authorization_validation = mock.Mock(
            wraps=tranche._validate_authorization_ticket
        )
        live_census = mock.Mock(return_value=copy.deepcopy(case["census"]))
        main_revalidate = mock.Mock(wraps=tranche._revalidate_main_evidence)
        with mock.patch.object(
                tranche, "_load_context",
                return_value=(
                    copy.deepcopy(case["lock"]),
                    copy.deepcopy(case["plan"]),
                    copy.deepcopy(terminal_state),
                ),
            ), mock.patch.object(
                tranche, "_audit_plan"
            ), mock.patch.object(
                tranche, "MAIN_MANIFEST_PATH", case["manifest_path"]
            ), mock.patch.object(
                tranche, "MAIN_LANE_CONFIG_DIR", case["lanes_dir"]
            ), mock.patch.object(
                tranche, "MAIN_RUN_DIR", case["run_dir"]
            ), mock.patch.object(
                tranche, "STATE_PATH", case["state_path"]
            ), mock.patch.object(
                tranche, "AUTHORIZATIONS_DIR", case["authorizations_dir"]
            ), mock.patch.object(
                tranche, "READINESS_PATH", case["readiness_path"]
            ), mock.patch.object(
                tranche, "PUBLIC_STATUS_PATH", case["public_status_path"]
            ), mock.patch.object(
                tranche, "SELECTION_REPORT_PATH", case["selection_report_path"]
            ), mock.patch.object(
                tranche, "MAIN_TERMINAL_REPORT_PATH",
                case["terminal_report_path"],
            ), mock.patch.object(
                tranche, "_load_json", side_effect=load_json
            ), mock.patch.object(
                tranche, "_ready_selection_anchor", return_value=generated
            ), mock.patch.object(
                tranche, "_selection_core", return_value=core
            ), mock.patch.object(
                tranche.manifest_lib, "audit_manifest",
                return_value=copy.deepcopy(case["envelope"]),
            ), mock.patch.object(
                tranche, "_revalidate_public_status_evidence",
                public_revalidate,
            ), mock.patch.object(
                tranche, "_validate_authorization_ticket",
                authorization_validation,
            ), mock.patch.object(
                tranche, "_live_census", live_census
            ), mock.patch.object(
                tranche, "_now_utc", return_value=case["now"]
            ), mock.patch.object(
                tranche, "_revalidate_main_evidence", main_revalidate
            ):
            audited = tranche.audit_tranche()

        self.assertTrue(audited["ok"])
        self.assertEqual(audited["phase"], "MAIN_FINITE_NO_HIT")
        main_revalidate.assert_called_once()
        self.assertEqual(main_revalidate.call_args.args[0], terminal_report)
        public_revalidate.assert_called_once()
        authorization_validation.assert_called_once()
        live_census.assert_called_once()

    def test_accept_main_rejects_authorization_state_drift(self) -> None:
        for drift_kind in ("semantic", "bytes_only", "ticket_path"):
            with self.subTest(drift_kind=drift_kind):
                case = self._main_fixture("FINITE_NO_HIT")
                if drift_kind == "semantic":
                    drifted_state = copy.deepcopy(case["state"])
                    drifted_state["revision"] += 1
                    case["state_path"].write_bytes(
                        tranche._pretty_bytes(drifted_state)
                    )
                    expected = "authorization state changed before acceptance"
                elif drift_kind == "bytes_only":
                    alternate_bytes = (
                        json.dumps(
                            case["state"],
                            sort_keys=True,
                            separators=(",", ":"),
                        )
                        + "\n"
                    ).encode("ascii")
                    self.assertNotEqual(alternate_bytes, case["state_bytes"])
                    case["state_path"].write_bytes(alternate_bytes)
                    expected = "authorization state pin is malformed"
                else:
                    ticket = copy.deepcopy(case["authorization_ticket"])
                    ticket["state_path"] = str(
                        (case["state_path"].parent / "different-state.json").resolve()
                    )
                    ticket_bytes = tranche._pretty_bytes(ticket)
                    case["authorization_path"].write_bytes(ticket_bytes)
                    case["launch_lock"]["authorization_sha256"] = hashlib.sha256(
                        ticket_bytes
                    ).hexdigest()
                    (case["run_dir"] / "launch.lock").write_bytes(
                        tranche._pretty_bytes(case["launch_lock"])
                    )
                    expected = "authorization state pin is malformed"

                with self.assertRaisesRegex(tranche.PermanentFailure, expected):
                    self._call_accept_main(case)
                case["fail_closed_mock"].assert_called_once()

    def test_import_surface_has_only_fixed_no_launch_commands(self) -> None:
        engine = Path(tranche.__file__).resolve().parent
        self.assertEqual(tranche.ENGINE_DIR, engine)
        self.assertEqual(tranche.LOCK_PATH, engine / "q5_tranche.lock")
        self.assertEqual(tranche.TRANCHE_DIR, engine / "logs" / "q5-eight-hour-tranche-v1")
        self.assertEqual(tranche.PLAN_PATH, tranche.TRANCHE_DIR / "plan.json")
        self.assertEqual(tranche.STATE_PATH, tranche.TRANCHE_DIR / "state.json")
        self.assertEqual(tranche.INTENTS_DIR, tranche.TRANCHE_DIR / "intents")

        parser = tranche._parser()
        subparsers = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ]
        self.assertEqual(len(subparsers), 1)
        self.assertEqual(
            set(subparsers[0].choices),
            {"start", "authorize", "accept-pilot", "preview", "finalize", "accept-main", "audit"},
        )
        expected_parameters = {
            tranche.start_tranche: (),
            tranche.authorize_launch: ("phase",),
            tranche.accept_pilot: ("pilot",),
            tranche.preview_selection: (),
            tranche.finalize_selection: (),
            tranche.accept_main: (),
            tranche.audit_tranche: (),
        }
        for public, parameters in expected_parameters.items():
            self.assertEqual(tuple(inspect.signature(public).parameters), parameters)
        hidden_mutators = (
            "_transition", "_transition_action", "_claim_lock",
            "_claim_lock_action", "_commit_initial", "_commit_initial_action",
            "_fail_closed", "_fail_closed_action", "_install_mutating_routes",
            "_start_tranche_action", "_accept_pilot_action",
            "_finalize_selection_action", "_accept_main_action",
        )
        for name in hidden_mutators:
            with self.subTest(hidden=name):
                self.assertFalse(hasattr(tranche, name))
        with self.assertRaises(TypeError):
            tranche.start_tranche(_claim_lock=lambda *args: {})
        with self.assertRaises(TypeError):
            tranche.accept_pilot("A", _transition=lambda *args: {})
        with self.assertRaises(TypeError):
            tranche.accept_main(_transition=lambda *args: {})


        source = Path(tranche.__file__).read_text(encoding="utf-8")
        self.assertIn("candidate_*.verified.json", source)
        tree = ast.parse(source)
        imported = {
            alias.name.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module.split(".", 1)[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        self.assertNotIn("subprocess", imported)
        forbidden_calls = {"Popen", "run", "call", "check_call", "check_output",
                           "system", "kill", "terminate"}
        called_attributes = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertTrue(forbidden_calls.isdisjoint(called_attributes))

    def test_permanent_lock_and_immutable_eight_hour_clock_in_temp_paths(self) -> None:
        t0 = datetime(2026, 7, 21, 5, 0, 0, 987654, tzinfo=UTC)
        magic = {"summary_sha256": ZERO_SHA}
        frozen_artifacts = {str((tranche.ENGINE_DIR / "scan_torsor_exact.exe").resolve()): ZERO_SHA}
        descriptor, raw_path = tempfile.mkstemp(
            prefix="q5-tranche-lock-test-", dir=tranche.ENGINE_DIR
        )
        os.close(descriptor)
        lock_path = Path(raw_path)
        lock_path.unlink()
        tranche_dir = lock_path.with_name(lock_path.name + "-absent-dir")
        try:
            with mock.patch.object(tranche, "LOCK_PATH", lock_path), \
                    mock.patch.object(tranche, "TRANCHE_DIR", tranche_dir):
                lock = clock_lock(t0.replace(microsecond=0))
                lock.update(
                    frozen_artifact_hashes=frozen_artifacts,
                    boot_time_microseconds=1,
                    monotonic_start_ns=1,
                )
                self.assertEqual(lock["frozen_artifact_hashes"], frozen_artifacts)
                self.assertEqual(tranche._parse_time(lock["t0"], "T0").microsecond, 0)
                self.assertIsInstance(lock["boot_time_microseconds"], int)
                self.assertIsInstance(lock["monotonic_start_ns"], int)
                parsed_t0 = tranche._parse_time(lock["t0"], "T0")
                self.assertEqual(tranche._parse_time(lock["s"], "S") - parsed_t0,
                                 timedelta(seconds=25_200))
                self.assertEqual(tranche._parse_time(lock["g"], "G") - parsed_t0,
                                 timedelta(seconds=28_800))

                state = tranche._state_template(lock, "READY_A", parsed_t0)
                tranche._validate_state_shape(state)
                for field, delta in (("s", 1), ("g", -1)):
                    bad = copy.deepcopy(state)
                    bad[field] = tranche._utc_text(
                        tranche._parse_time(bad[field], field) + timedelta(seconds=delta)
                    )
                    with self.subTest(field=field), self.assertRaises(tranche.PermanentFailure):
                        tranche._validate_state_shape(bad)
        finally:
            if lock_path.exists():
                lock_path.unlink()

    def test_public_start_claims_lock_and_refuses_second_start(self) -> None:
        root = tranche.ENGINE_DIR / f".q5-public-start-{uuid.uuid4().hex}"
        root.mkdir()
        self.addCleanup(shutil.rmtree, root, True)
        lock_path = root / "q5_tranche.lock"
        tranche_dir = root / "tranche"
        plan_path = tranche_dir / "plan.json"
        state_path = tranche_dir / "state.json"
        intents_dir = tranche_dir / "intents"
        authorizations_dir = tranche_dir / "authorizations"
        readiness_path = root / "readiness.json"
        artifact_hashes = {"runtime": ZERO_SHA}
        magic = {
            "outcome": "CONTINUE",
            "status": "TIMEOUT_INCOMPLETE",
            "state_sha256": ZERO_SHA,
            "summary_sha256": ZERO_SHA,
            "inventory_sha256": ZERO_SHA,
            "run_once_sha256": ZERO_SHA,
            "recovery_tree_sha256": ZERO_SHA,
            "verified_hit": None,
            "finished_utc": "2026-07-21T05:00:00Z",
        }

        def census(captured: datetime) -> dict[str, object]:
            return {
                "schema_version": 1,
                "kind": "Q5_TRANCHE_PROCESS_CENSUS",
                "captured_utc": iso(captured),
                "active_processes": [],
                "artifact_hashes": copy.deepcopy(artifact_hashes),
                "errors": [],
            }

        def invoke(start: datetime, monotonic_base: int) -> dict[str, object]:
            snapshots = [
                census(start),
                census(start + timedelta(seconds=10)),
                census(start + timedelta(seconds=11)),
            ]
            with mock.patch.object(
                tranche, "_validate_readiness",
                return_value={"file_sha256": ZERO_SHA},
            ), mock.patch.object(
                tranche, "_validate_magic_terminal",
                return_value=copy.deepcopy(magic),
            ), mock.patch.object(
                tranche, "_live_census", side_effect=snapshots
            ), mock.patch.object(
                tranche, "_now_utc",
                side_effect=[
                    start,
                    start + timedelta(seconds=10),
                    start + timedelta(seconds=11),
                    start + timedelta(seconds=11),
                ],
            ), mock.patch.object(
                tranche.time, "sleep"
            ), mock.patch.object(
                tranche.time,
                "monotonic_ns",
                side_effect=[
                    monotonic_base,
                    monotonic_base + 10_000_000_000,
                    monotonic_base + 10_000_000_001,
                ],
            ), mock.patch.object(
                tranche, "_boot_time_microseconds", return_value=123
            ):
                return tranche.start_tranche()

        start = datetime(2026, 7, 21, 5, 0, 0, tzinfo=UTC)
        with mock.patch.object(tranche, "LOCK_PATH", lock_path), \
                mock.patch.object(tranche, "TRANCHE_DIR", tranche_dir), \
                mock.patch.object(tranche, "PLAN_PATH", plan_path), \
                mock.patch.object(tranche, "STATE_PATH", state_path), \
                mock.patch.object(tranche, "INTENTS_DIR", intents_dir), \
                mock.patch.object(
                    tranche, "AUTHORIZATIONS_DIR", authorizations_dir
                ), \
                mock.patch.object(tranche, "READINESS_PATH", readiness_path):
            first = invoke(start, 100)
            self.assertTrue(first["ok"])
            self.assertEqual(first["phase"], "READY_A")
            self.assertTrue(lock_path.is_file())
            self.assertTrue(state_path.is_file())
            lock = json.loads(lock_path.read_text(encoding="ascii"))
            self.assertEqual(lock["frozen_artifact_hashes"], artifact_hashes)
            parsed_t0 = tranche._parse_time(lock["t0"], "T0")
            self.assertEqual(
                tranche._parse_time(lock["s"], "S") - parsed_t0,
                timedelta(seconds=25_200),
            )
            self.assertEqual(
                tranche._parse_time(lock["g"], "G") - parsed_t0,
                timedelta(seconds=28_800),
            )
            frozen_lock = lock_path.read_bytes()
            frozen_state = state_path.read_bytes()

            with self.assertRaisesRegex(
                tranche.PermanentFailure, "permanent Q5 tranche lock already exists"
            ):
                invoke(start + timedelta(seconds=20), 20_000_000_000)
            self.assertEqual(lock_path.read_bytes(), frozen_lock)
            self.assertEqual(state_path.read_bytes(), frozen_state)

    def test_candidate_table_is_exact_frozen_H48_through_H512(self) -> None:
        self.assertEqual(tranche.CANDIDATE_TABLE_PAYLOAD_SHA256, FROZEN_PAYLOAD_SHA)
        expected = tranche.EXPECTED_FILE_HASHES
        frozen_by_name = {
            "q5_manifest.py": "712c6422281da41a471a29a272aa92c35efc9182759a632bfe1d1987ac3ccf1b",
            "scan_torsor_exact.cpp": "3e96532361aa2768cd36deb093376a9a8ef658cbd5afaca2301ca3ecd461c5c9",
            "scan_torsor_exact.exe": "19997a0ed9658aea134aef94fd14486e0c8196909f39d5b71d0bb6b2a24689b9",
            "verify_certificate.py": "843f13506611d51f1d944b9a63778f9bd793dd06b4693838d4ca1a957b00833a",
            "verify_independent.cpp": "3641129248f507c5f844519f6894fa8aef4c22a4b1d8fe89375d50baa02cf74d",
            "verify_independent.exe": "055206b62c0d07d2f896e15657749346ef3f5e8f6e6262959198109e4d9fb8f0",
            "q5_candidate_table.cpp": FROZEN_SOURCE_SHA,
            "q5_candidate_table.exe": FROZEN_TOOL_SHA,
            "q5_candidate_table.json": FROZEN_TABLE_SHA,
        }
        self.assertEqual(
            {path.name: digest for path, digest in expected.items()},
            frozen_by_name,
        )
        self.assertEqual(expected[tranche.CANDIDATE_TABLE_SOURCE_PATH], FROZEN_SOURCE_SHA)
        for path, digest in expected.items():
            with self.subTest(path=path.name):
                self.assertEqual(tranche._sha256_file(path), digest)
        self.assertEqual(expected[tranche.CANDIDATE_TABLE_TOOL_PATH], FROZEN_TOOL_SHA)
        self.assertEqual(expected[tranche.CANDIDATE_TABLE_PATH], FROZEN_TABLE_SHA)
        self.assertEqual(tranche._sha256_file(tranche.CANDIDATE_TABLE_SOURCE_PATH), FROZEN_SOURCE_SHA)
        self.assertEqual(tranche._sha256_file(tranche.CANDIDATE_TABLE_TOOL_PATH), FROZEN_TOOL_SHA)
        self.assertEqual(tranche._sha256_file(tranche.CANDIDATE_TABLE_PATH), FROZEN_TABLE_SHA)
        plan = {
            "candidate_table": {
                "file_sha256": FROZEN_TABLE_SHA,
                "source_sha256": FROZEN_SOURCE_SHA,
                "tool_sha256": FROZEN_TOOL_SHA,
            }
        }
        rows = tranche._candidate_table(plan)
        self.assertEqual([row["H"] for row in rows], list(range(48, 513)))
        self.assertEqual(rows[0]["max_lane_weight"], 78_585)
        self.assertEqual(rows[16]["H"], 64)
        self.assertEqual(rows[16]["max_lane_weight"], 244_414)
        self.assertEqual(rows[-1]["max_lane_weight"], 981_381_125)

    def test_selector_uses_exact_cross_products_first_tie_and_exact_ceil(self) -> None:
        now = datetime(2026, 7, 21, 6, 0, 0, tzinfo=UTC)
        state = timing_state(now)
        rows = [candidate_row(48, 3), candidate_row(49, 4)]
        with mock.patch.object(tranche, "_radicand_bits", return_value=5), \
                mock.patch.object(tranche, "_candidate_table", return_value=rows):
            result = tranche._selection_core(
                state, {}, now, ready_selection_anchor=now
            )
        self.assertEqual(result["rho"], {
            "numerator": 1,
            "denominator": 5,
            "source_pilot": "B",
            "source_lane": 0,
        })
        self.assertEqual(result["candidates"][0]["predicted_milliseconds"], 45)
        self.assertEqual(result["candidates"][1]["predicted_milliseconds"], 59)
        self.assertTrue(result["candidates"][0]["fits"])
        self.assertFalse(result["candidates"][1]["fits"])
        self.assertEqual(result["selected_h"], 48)

        # Ratios which round to the same binary float still compare exactly:
        # A/(A-1) > (A+1)/A, so lane 1 must win.
        large = 10**18
        exact_state = timing_state(now, remaining_ms=1)
        for pilot in ("B", "C", "D"):
            for row in exact_state["accepted_pilots"][pilot]["timing_rows"]:
                row.update(elapsed_milliseconds=1, weight=large)
        exact_state["accepted_pilots"]["B"]["timing_rows"][0].update(
            elapsed_milliseconds=large + 1, weight=large
        )
        exact_state["accepted_pilots"]["B"]["timing_rows"][1].update(
            elapsed_milliseconds=large, weight=large - 1
        )
        with mock.patch.object(tranche, "_radicand_bits", return_value=1), \
                mock.patch.object(tranche, "_candidate_table", return_value=[candidate_row(48, 3)]):
            exact = tranche._selection_core(
                exact_state, {}, now, ready_selection_anchor=now
            )
        self.assertEqual(exact["rho"]["source_pilot"], "B")
        self.assertEqual(exact["rho"]["source_lane"], 1)

    def test_running_magic_evidence_is_rejected_before_any_lock(self) -> None:
        state = {
            "schema_version": 1,
            "kind": "magic_square_squares_frozen_tranche_recovery_state",
            "run_id": tranche.MAGIC_RUN_ID,
            "source_run_id": tranche.MAGIC_SOURCE_RUN_ID,
            "supervisor_pid": 1,
            "status": "RUNNING",
            "original_started_utc": "2026-07-20T00:00:00Z",
            "original_deadline_utc": "2026-07-21T06:00:00Z",
            "deadline_unix": 0,
            "worker_cap": 64,
            "workers_launched_recovery": 64,
            "workers_running_recovery": 0,
            "retained_completed_lanes": 0,
            "manifest_sha256": tranche.MAGIC_MANIFEST_SHA256,
            "approved_artifact_hashes": copy.deepcopy(tranche.MAGIC_APPROVED_ARTIFACT_HASHES),
            "proof_claim": False,
            "anomaly": None,
            "updated_utc": "2026-07-21T06:00:00Z",
            "lanes": [],
        }
        summary = {
            "schema_version": 1,
            "kind": "magic_square_squares_frozen_tranche_recovery_summary",
            "run_id": tranche.MAGIC_RUN_ID,
            "source_run_id": tranche.MAGIC_SOURCE_RUN_ID,
            "source_portfolio_status": "RUNNING",
            "status": "RUNNING",
            "proof_claim": False,
            "claim_scope": "NONE",
            "original_started_utc": "2026-07-20T00:00:00Z",
            "original_deadline_utc": "2026-07-21T06:00:00Z",
            "finished_utc": None,
            "manifest_sha256": tranche.MAGIC_MANIFEST_SHA256,
            "approved_artifact_hashes": copy.deepcopy(tranche.MAGIC_APPROVED_ARTIFACT_HASHES),
            "workers_requested_original": 64,
            "workers_launched_recovery": 64,
            "retained_completed_lanes": 0,
            "combined_lane_count": 64,
            "stop_reason": None,
            "hit_lane": None,
            "anomaly": None,
            "owned_tree_snapshot_error": None,
            "unverified_stop_lanes": [],
            "dead_root_failures": [],
            "owned_process_survivors": [],
            "source_anomaly_retained_as_provenance": None,
            "nonempty_recovery_stderr_lanes": [],
            "original_artifacts_unchanged": True,
            "changed_original_files": [],
            "lane_status_counts": {"RUNNING": 64},
            "lanes": [],
        }
        evidence = {
            tranche.MAGIC_STATE_PATH: state,
            tranche.MAGIC_SUMMARY_PATH: summary,
            tranche.MAGIC_INVENTORY_PATH: {},
            tranche.MAGIC_RUN_ONCE_PATH: {},
        }

        def fake_load(path: Path, *, missing_ready: bool = False) -> object:
            del missing_ready
            return copy.deepcopy(evidence[path])

        with mock.patch.object(tranche, "_validate_readiness", return_value={"file_sha256": ZERO_SHA}), \
                mock.patch.object(tranche, "_load_json", side_effect=fake_load), \
                mock.patch.object(
                    tranche, "_now_utc",
                    return_value=datetime(2026, 7, 21, 6, 0, 0, tzinfo=UTC),
                ), \
                mock.patch.object(
                    tranche.time, "sleep",
                    side_effect=lambda _: self.fail("sleep reached after RUNNING evidence"),
                ), \
                mock.patch.object(
                    tranche, "_live_census",
                    side_effect=lambda _: self.fail("census reached after RUNNING evidence"),
                ):
            with self.assertRaisesRegex(tranche.TrancheNotReady, "not in an accepted terminal state"):
                tranche.start_tranche()

    def test_orphan_intent_is_permanent_failure(self) -> None:
        t0 = datetime(2026, 7, 21, 5, 0, 0, tzinfo=UTC)
        state = tranche._state_template(clock_lock(t0), "READY_A", t0)
        initial = {
            "schema_version": 1,
            "kind": "Q5_TRANCHE_TRANSITION_INTENT",
            "tranche_id": tranche.TRANCHE_ID,
            "from_revision": None,
            "from_phase": None,
            "to_revision": 0,
            "to_phase": "READY_A",
            "previous_state_sha256": None,
            "next_state_sha256": tranche._canonical_sha(state),
            "extra_files": {},
            "created_utc": tranche._utc_text(t0),
        }
        first = Path("transition_000000.json")
        orphan = Path("transition_000001.json")
        with mock.patch.object(tranche, "_load_json", return_value=initial):
            with mock.patch.object(tranche, "_intent_files", return_value=[first]):
                tranche._validate_ledger(state)
            with mock.patch.object(tranche, "_intent_files", return_value=[first, orphan]):
                with self.assertRaisesRegex(tranche.PermanentFailure, "orphan transition intent"):
                    tranche._validate_ledger(state)

    def test_accept_and_finalize_fail_closed_at_G_or_on_clock_rollback(self) -> None:
        t0 = datetime(2026, 7, 21, 5, 0, 0, tzinfo=UTC)
        lock = clock_lock(t0)
        updated = t0 + timedelta(seconds=100)

        accept_state = tranche._state_template(lock, "READY_A", updated)
        accept_plan: dict[str, object] = {}
        accept_evidence = {
            "finished_utc": iso(updated),
            "verified_hit": None,
            "timing_rows": [],
        }
        accept_times = {
            "at_G": tranche._parse_time(accept_state["g"], "G"),
            "rollback": updated - timedelta(seconds=1),
        }
        for name, now in accept_times.items():
            with self.subTest(command="accept", case=name), \
                    mock.patch.object(
                        tranche, "_load_context",
                        return_value=(copy.deepcopy(lock), accept_plan, copy.deepcopy(accept_state)),
                    ), \
                    mock.patch.object(
                        tranche, "_validate_pilot_evidence",
                        return_value=(copy.deepcopy(accept_evidence), False),
                    ), \
                    mock.patch.object(tranche, "_now_utc", return_value=now), \
                    mock.patch.object(tranche, "_write_xb"), \
                    mock.patch.object(tranche.manifest_lib, "atomic_write_bytes"):
                with self.assertRaises(tranche.PermanentFailure):
                    tranche.accept_pilot("A")

        finalize_state = tranche._state_template(lock, "READY_SELECTION", updated)
        finalize_state["accepted_pilots"] = {name: {} for name in tranche.PILOT_ORDER}
        finalize_core = {
            "selected_h": None,
            "generated_utc": iso(updated),
            "remaining_before_s_milliseconds": 0,
            "setup_guard_milliseconds": 300_000,
            "timing_records": [],
            "rho": {"numerator": 1, "denominator": 1, "source_pilot": "B", "source_lane": 0},
            "candidates": [],
        }
        finalize_times = {
            "at_G": tranche._parse_time(finalize_state["g"], "G"),
            "rollback": updated - timedelta(seconds=1),
        }
        for name, now in finalize_times.items():
            with self.subTest(command="finalize", case=name), \
                    mock.patch.object(
                        tranche, "_load_context",
                        return_value=(copy.deepcopy(lock), {}, copy.deepcopy(finalize_state)),
                    ), \
                    mock.patch.object(tranche, "_current_clean_census", return_value={}), \
                    mock.patch.object(tranche, "_selection_core", return_value=copy.deepcopy(finalize_core)), \
                    mock.patch.object(tranche, "_now_utc", return_value=now), \
                    mock.patch.object(tranche, "_write_xb"), \
                    mock.patch.object(tranche.manifest_lib, "atomic_write_bytes"):
                with self.assertRaises(tranche.PermanentFailure):
                    tranche.finalize_selection()

    def test_main_manifest_rejects_future_creation_and_noncanonical_runtime(self) -> None:
        now = datetime(2026, 7, 21, 6, 0, 0, tzinfo=UTC)
        selected_h = 48
        row = candidate_row(selected_h, 78_585)
        row["min_lane_weight"] = 76_274
        row["specialization_count"] = 1_423
        core = {"generated_utc": iso(now), "selection_setup_deadline_utc": iso(now + timedelta(minutes=5)), "candidates": [row]}
        state = {
            "s": iso(now + timedelta(hours=1)),
            "accepted_pilots": {"D": {"finished_utc": iso(now - timedelta(hours=1))}},
        }

        artifact_paths = {
            "worker": tranche.ENGINE_DIR / "scan_torsor_exact.exe",
            "worker_source": tranche.ENGINE_DIR / "scan_torsor_exact.cpp",
            "scalar_verifier": tranche.ENGINE_DIR / "verify_certificate.py",
            "independent_verifier": tranche.ENGINE_DIR / "verify_independent.exe",
            "manifest_tool": tranche.ENGINE_DIR / "q5_manifest.py",
            "supervisor": tranche.ENGINE_DIR / "q5_supervisor.py",
            "python_interpreter": Path(sys.executable),
        }

        def artifact(path: Path) -> dict[str, object]:
            path = path.resolve()
            return {
                "path": str(path),
                "size": path.stat().st_size,
                "sha256": tranche._sha256_file(path),
            }

        descriptor, raw_path = tempfile.mkstemp(
            prefix="q5-main-manifest-test-", suffix=".json", dir=tranche.ENGINE_DIR
        )
        os.close(descriptor)
        manifest_path = Path(raw_path)
        lanes_dir = manifest_path.with_name(manifest_path.name + "-lanes")
        run_dir = manifest_path.with_name(manifest_path.name + "-absent-run")
        payload = {
            "mode": "SELECTED_MAIN",
            "search_mode": "canonical_positive_u_positive_y",
            "worker_kind": "native",
            "bounds": {"P": 48, "Q": 48, "N": 48, "D": 48},
            "deadline": state["s"],
            "manifest_path": str(manifest_path.resolve()),
            "run_dir": str(run_dir.resolve()),
            "created_utc": iso(now),
            "artifacts": {role: artifact(path) for role, path in artifact_paths.items()},
            "lanes": [
                {
                    "lane_id": lane,
                    "lane_file": {
                        "path": str((lanes_dir / f"lane_{lane:02d}.tsv").resolve()),
                        "size": 0,
                        "sha256": ZERO_SHA,
                    },
                    "result_path": str((run_dir / f"lane_{lane:02d}.result.json").resolve()),
                }
                for lane in range(64)
            ],
            "balance": {
                "max_lane_weight": row["max_lane_weight"],
                "min_lane_weight": row["min_lane_weight"],
                "threshold_pass": True,
            },
            "specialization_count": row["specialization_count"],
            "oeis_redundancy_gate": {"passes": True},
        }
        plan = {
            "frozen_artifact_hashes": {
                record["path"]: record["sha256"]
                for record in payload["artifacts"].values()
            }
        }
        try:
            with mock.patch.object(tranche, "MAIN_MANIFEST_PATH", manifest_path), \
                    mock.patch.object(tranche, "MAIN_LANE_CONFIG_DIR", lanes_dir), \
                    mock.patch.object(tranche, "MAIN_RUN_DIR", run_dir), \
                    mock.patch.object(tranche.manifest_lib, "audit_manifest") as audit:
                audit.return_value = {"payload": copy.deepcopy(payload), "payload_sha256": ZERO_SHA}
                tranche._validate_main_manifest(selected_h, core, state, plan)

                cases: list[tuple[str, dict[str, object]]] = []
                future = copy.deepcopy(payload)
                future["created_utc"] = iso(now + timedelta(minutes=5, seconds=1))
                cases.append(("created_after_setup_window", future))
                python_worker = copy.deepcopy(payload)
                python_worker["worker_kind"] = "python"
                cases.append(("python_worker", python_worker))
                wrong_worker = copy.deepcopy(payload)
                wrong_worker["artifacts"]["worker"] = artifact(tranche.ENGINE_DIR / "q5_manifest.py")
                cases.append(("wrong_worker_path", wrong_worker))
                wrong_hash = copy.deepcopy(payload)
                wrong_hash["artifacts"]["worker"]["sha256"] = ZERO_SHA
                cases.append(("wrong_worker_hash", wrong_hash))
                wrong_lane = copy.deepcopy(payload)
                wrong_lane["lanes"][7]["lane_file"]["path"] = str(
                    manifest_path.with_name("outside-lane-07.tsv").resolve()
                )
                cases.append(("lane_file_outside_fixed_dir", wrong_lane))

                for name, bad in cases:
                    with self.subTest(name=name):
                        audit.return_value = {"payload": bad, "payload_sha256": ZERO_SHA}
                        with self.assertRaises(tranche.TrancheError):
                            tranche._validate_main_manifest(selected_h, core, state, plan)
        finally:
            if manifest_path.exists():
                manifest_path.unlink()

    def test_public_status_schema_hashes_and_five_minute_boundary(self) -> None:
        now = datetime(2026, 7, 21, 6, 0, 0, tzinfo=UTC)

        def gate(checked: datetime) -> dict[str, object]:
            return {
                "schema_version": 1,
                "kind": "Q5_PUBLIC_STATUS_GATE",
                "capture_dir": str(capture_dir.resolve()),
                "checked_utc": iso(checked),
                "problem_open": True,
                "oeis_no_n5_value": True,
                "formal_conjecture_open": True,
                "sources": [
                    {**copy.deepcopy(expected), "content_sha256": ZERO_SHA}
                    for expected in tranche.PUBLIC_SOURCE_EXPECTATIONS
                ],
            }

        root = tranche.ENGINE_DIR / f"q5-public-gate-test-{uuid.uuid4().hex}"
        root.mkdir()
        path = root / "gate.json"
        capture_dir = root / tranche.public_status_lib.CAPTURE_PARENT_NAME / "capture"
        capture_dir.mkdir(parents=True)
        try:

            def write(value: dict[str, object]) -> None:
                path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="ascii")

            def fake_audit(
                _path: Path, *, now: datetime, require_fresh: bool
            ) -> dict[str, object]:
                value = json.loads(path.read_text(encoding="ascii"))
                if set(value) != set(gate(now)):
                    raise tranche.public_status_lib.PublicStatusError("keys differ")
                if any(
                    source.get("content_sha256") != ZERO_SHA
                    for source in value["sources"]
                ):
                    raise tranche.public_status_lib.PublicStatusError("content_sha256")
                checked = tranche._parse_time(value["checked_utc"], "checked")
                if require_fresh and not checked <= now <= checked + timedelta(minutes=5):
                    raise tranche.public_status_lib.PublicStatusError("public gate is not fresh")
                return value

            with mock.patch.object(tranche, "PUBLIC_STATUS_PATH", path), \
                    mock.patch.object(tranche.public_status_lib, "audit_gate", side_effect=fake_audit):
                write(gate(now - timedelta(minutes=5)))
                accepted = tranche._validate_public_status(now)
                self.assertEqual(accepted["file_sha256"], hashlib.sha256(path.read_bytes()).hexdigest())

                write(gate(now - timedelta(minutes=5, seconds=1)))
                with self.assertRaises(tranche.TrancheNotReady):
                    tranche._validate_public_status(now)

                write(gate(now + timedelta(microseconds=1)))
                with self.assertRaises(tranche.TrancheNotReady):
                    tranche._validate_public_status(now)

                malformed = gate(now)
                malformed["unexpected"] = True
                write(malformed)
                with self.assertRaisesRegex(tranche.TrancheError, "keys differ"):
                    tranche._validate_public_status(now)

                malformed = gate(now)
                malformed["sources"][0]["content_sha256"] = "abc"
                write(malformed)
                with self.assertRaisesRegex(tranche.TrancheError, "content_sha256"):
                    tranche._validate_public_status(now)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_relative_token_uses_process_cwd_and_census_freshness(self) -> None:
        engine = tranche.ENGINE_DIR.resolve()
        expected = (engine / "scan_torsor_exact.exe").resolve()
        self.assertEqual(
            tranche._path_token("scan_torsor_exact.exe", str(engine)),
            expected,
        )
        self.assertEqual(
            tranche._path_token(".\\scan_torsor_exact.exe", str(engine)),
            expected,
        )
        self.assertIsNone(tranche._path_token("scan_torsor_exact.exe", None))
        self.assertIsNone(tranche._path_token("--worker", str(engine)))

        now = datetime(2026, 7, 21, 6, 0, 10, tzinfo=UTC)
        hashes = {str(expected): ZERO_SHA}
        plan = {
            "t0": iso(now - timedelta(seconds=10)),
            "frozen_artifact_hashes": hashes,
        }

        def census(captured: datetime, artifact_hashes: dict[str, str] | None = None) -> dict[str, object]:
            return {
                "schema_version": 1,
                "kind": "Q5_TRANCHE_PROCESS_CENSUS",
                "captured_utc": iso(captured),
                "active_processes": [],
                "artifact_hashes": hashes if artifact_hashes is None else artifact_hashes,
                "errors": [],
            }

        current = tranche._current_clean_census(
            plan, lambda: now, lambda: census(now - timedelta(seconds=5))
        )
        self.assertEqual(current["artifact_hashes"], hashes)
        bad_cases = {
            "older_than_five_seconds": census(now - timedelta(seconds=5, microseconds=1)),
            "predates_T0": census(now - timedelta(seconds=11)),
            "future": census(now + timedelta(microseconds=1)),
            "artifact_drift": census(now, {str(expected): "1" * 64}),
        }
        for name, snapshot in bad_cases.items():
            with self.subTest(name=name), self.assertRaises(tranche.TrancheError):
                tranche._current_clean_census(plan, lambda: now, lambda snapshot=snapshot: snapshot)

    def test_ledger_rejects_illegal_phase_edge_and_timestamp_rollback(self) -> None:
        t0 = datetime(2026, 7, 21, 5, 0, 0, tzinfo=UTC)
        state = tranche._state_template(clock_lock(t0), "READY_B", t0 + timedelta(seconds=1))
        state["revision"] = 1
        state["last_intent"] = "transition_000001.json"
        first_path = Path("transition_000000.json")
        second_path = Path("transition_000001.json")
        first = {
            "schema_version": 1,
            "kind": "Q5_TRANCHE_TRANSITION_INTENT",
            "tranche_id": tranche.TRANCHE_ID,
            "from_revision": None,
            "from_phase": None,
            "to_revision": 0,
            "to_phase": "READY_A",
            "previous_state_sha256": None,
            "next_state_sha256": ZERO_SHA,
            "extra_files": {},
            "created_utc": iso(t0),
        }
        second = {
            "schema_version": 1,
            "kind": "Q5_TRANCHE_TRANSITION_INTENT",
            "tranche_id": tranche.TRANCHE_ID,
            "from_revision": 0,
            "from_phase": "READY_A",
            "to_revision": 1,
            "to_phase": "READY_B",
            "previous_state_sha256": ZERO_SHA,
            "next_state_sha256": tranche._canonical_sha(state),
            "extra_files": {},
            "created_utc": iso(t0 + timedelta(seconds=1)),
        }

        def run(candidate_state: dict[str, object], candidate_second: dict[str, object]) -> None:
            records = {first_path: first, second_path: candidate_second}
            with mock.patch.object(tranche, "_intent_files", return_value=[first_path, second_path]), \
                    mock.patch.object(
                        tranche, "_load_json",
                        side_effect=lambda path, **_: copy.deepcopy(records[path]),
                    ):
                tranche._validate_ledger(candidate_state)

        run(state, second)

        illegal_state = copy.deepcopy(state)
        illegal_state["phase"] = "READY_D"
        illegal = copy.deepcopy(second)
        illegal["to_phase"] = "READY_D"
        illegal["next_state_sha256"] = tranche._canonical_sha(illegal_state)
        with self.assertRaisesRegex(tranche.PermanentFailure, "phase edge is illegal"):
            run(illegal_state, illegal)

        rollback_state = copy.deepcopy(state)
        rollback_state["updated_utc"] = iso(t0 - timedelta(seconds=1))
        rollback = copy.deepcopy(second)
        rollback["created_utc"] = rollback_state["updated_utc"]
        rollback["next_state_sha256"] = tranche._canonical_sha(rollback_state)
        with self.assertRaisesRegex(tranche.PermanentFailure, "timestamp rollback"):
            run(rollback_state, rollback)

    def test_accepted_pilot_artifact_hash_drift_is_rejected(self) -> None:
        spec = tranche.PILOT_SPECS["A"]
        manifest_path = spec["manifest_path"].resolve()
        run_dir = spec["run_dir"].resolve()
        summary_path = run_dir / "supervisor_summary.json"
        final_state_path = run_dir / "supervisor_state.json"
        launch_lock_path = run_dir / "launch.lock"
        evidence = {
            "pilot": "A",
            "campaign_id": spec["campaign_id"],
            "manifest_path": str(manifest_path),
            "manifest_file_sha256": ZERO_SHA,
            "summary_path": str(summary_path),
            "summary_sha256": ZERO_SHA,
            "final_state_path": str(final_state_path),
            "final_state_sha256": ZERO_SHA,
            "launch_lock_sha256": ZERO_SHA,
            "manifest_payload_sha256": ZERO_SHA,
            "authorization_state_sha256": ZERO_SHA,
            "result_sha256": {},
            "run_inventory": {},
            "spawned_lane_ids": [],
            "stdout_sha256": {},
            "stderr_sha256": {},
            "verified_artifact_path": None,
            "verified_artifact_sha256": None,
            "finished_utc": "2026-07-21T06:00:00Z",
            "timing_rows": [],
            "verified_hit": None,
        }
        state = {"accepted_pilots": {"A": evidence}}
        plan = {"launch_readiness": {"file_sha256": ZERO_SHA}}

        envelope = {"payload": {"lanes": []}, "payload_sha256": ZERO_SHA}
        def fake_load(path: Path, **_: object) -> tuple[object, str]:
            if Path(path).resolve() == manifest_path:
                return copy.deepcopy(envelope), ZERO_SHA
            digest = "1" * 64 if Path(path).resolve() == summary_path else ZERO_SHA
            return {}, digest

        with mock.patch.object(tranche, "_load_json_with_sha", side_effect=fake_load), \
                mock.patch.object(tranche.manifest_lib, "audit_manifest", return_value=envelope), \
                mock.patch.object(tranche, "_inventory", return_value={}):
            with self.assertRaisesRegex(tranche.PermanentFailure, "terminal JSON hash drift"):
                tranche._revalidate_accepted_artifacts(state, plan)

    def test_launch_readiness_pins_full_suite_and_two_referees(self) -> None:
        now = datetime(2026, 7, 21, 6, 0, 0, tzinfo=UTC)
        artifacts = {
            name: tranche._sha256_file(path)
            for name, path in tranche.READINESS_ARTIFACT_PATHS.items()
        }
        test_files = {
            name: tranche._sha256_file(tranche.ENGINE_DIR / name)
            for name in tranche.READINESS_TEST_FILES
        }
        tests_body = {
            "passed": 1,
            "failed": 0,
            "commands": list(tranche.READINESS_TEST_COMMANDS),
            "test_files": test_files,
        }
        tests = {**tests_body, "suite_sha256": tranche._canonical_sha(tests_body)}
        reviewed = tranche._canonical_sha({"artifacts": artifacts, "tests": tests})
        marker = {
            "schema_version": 1,
            "kind": "q5-launch-readiness",
            "tranche_id": tranche.TRANCHE_ID,
            "created_utc": iso(now),
            "artifacts": artifacts,
            "tests": tests,
            "referee_verdicts": [
                {"referee": "r1", "verdict": "LAUNCH_SAFE", "reviewed_readiness_sha256": reviewed},
                {"referee": "r2", "verdict": "LAUNCH_SAFE", "reviewed_readiness_sha256": reviewed},
            ],
        }
        path = tranche.ENGINE_DIR / f".q5-readiness-test-{uuid.uuid4().hex}.json"
        def write(value: dict[str, object]) -> None:
            path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="ascii")
        try:
            write(marker)
            with mock.patch.object(tranche, "READINESS_PATH", path):
                accepted = tranche._validate_readiness(now=now)
                self.assertEqual(accepted["reviewed_readiness_sha256"], reviewed)
                drifted = copy.deepcopy(marker)
                first = tranche.READINESS_TEST_FILES[0]
                drifted["tests"]["test_files"][first] = ZERO_SHA
                write(drifted)
                with self.assertRaisesRegex(tranche.TrancheError, "test-file drift"):
                    tranche._validate_readiness(now=now)
                duplicate = copy.deepcopy(marker)
                duplicate["referee_verdicts"][1]["referee"] = "r1"
                write(duplicate)
                with self.assertRaisesRegex(tranche.TrancheError, "not distinct"):
                    tranche._validate_readiness(now=now)
        finally:
            path.unlink(missing_ok=True)
    def test_finalize_rejects_selected_H_change_between_two_clocks(self) -> None:
        now = datetime(2026, 7, 21, 6, 0, 0, tzinfo=UTC)
        lock = clock_lock(now - timedelta(hours=1))
        state = tranche._state_template(lock, "READY_SELECTION", now - timedelta(seconds=1))
        state["accepted_pilots"] = {name: {} for name in tranche.PILOT_ORDER}
        first_core = {"selected_h": 48}
        second_core = {"selected_h": 49}
        clock = mock.Mock(side_effect=[now, now + timedelta(seconds=1)])
        with mock.patch.object(tranche, "_load_context", return_value=(lock, {}, state)), \
                mock.patch.object(tranche, "_validate_transition_clock"), \
                mock.patch.object(tranche, "_revalidate_accepted_artifacts"), \
                mock.patch.object(
                    tranche, "_ready_selection_anchor",
                    return_value=tranche._parse_time(state["updated_utc"], "anchor"),
                ), \
                mock.patch.object(tranche, "_current_clean_census"), \
                mock.patch.object(
                    tranche, "_selection_core",
                    side_effect=[first_core, second_core],
                ), \
                mock.patch.object(tranche, "_validate_public_status", return_value={}), \
                mock.patch.object(
                    tranche, "_validate_main_manifest",
                    return_value=({}, ZERO_SHA),
                ), \
                mock.patch.object(tranche, "_sha256_file", return_value=ZERO_SHA), \
                mock.patch.object(tranche, "_now_utc", side_effect=clock), \
                mock.patch.object(tranche, "_write_xb"), \
                mock.patch.object(tranche.manifest_lib, "atomic_write_bytes"):
            with self.assertRaisesRegex(tranche.PermanentFailure, "selected H changed"):
                tranche.finalize_selection()

    def test_magic_terminal_requires_unique_rows_histogram_and_actual_artifacts(self) -> None:
        lane_ids = sorted(tranche._magic_lane_ids())
        summary_lanes = [
            {
                "lane": lane,
                "source_run_id": tranche.MAGIC_SOURCE_RUN_ID,
                "status": "NO_HIT",
                "return_code": 0,
                "single_thread_search": True,
                "source": "retained_original_exact_completion",
                "owned": False,
                "pid": None,
                "stdout": str(
                    (tranche.MAGIC_SOURCE_RUN_DIR / "lanes" / lane / "process.stdout.txt").resolve()
                ),
                "stderr": str(
                    (tranche.MAGIC_SOURCE_RUN_DIR / "lanes" / lane / "process.stderr.txt").resolve()
                ),
            }
            for lane in lane_ids
        ]
        recovered_lane = summary_lanes[-1]["lane"]
        summary_lanes[-1].update(
            source="recovered_interrupted_lane",
            owned=True,
            pid=424242,
            stdout=str(
                (tranche.MAGIC_RUN_DIR / "lanes" / recovered_lane / "recovery.stdout.txt").resolve()
            ),
            stderr=str(
                (tranche.MAGIC_RUN_DIR / "lanes" / recovered_lane / "recovery.stderr.txt").resolve()
            ),
        )
        state_lanes = copy.deepcopy(summary_lanes)
        state = {
            "schema_version": 1,
            "kind": "magic_square_squares_frozen_tranche_recovery_state",
            "run_id": tranche.MAGIC_RUN_ID,
            "source_run_id": tranche.MAGIC_SOURCE_RUN_ID,
            "supervisor_pid": 1,
            "status": "NO_HIT_DECLARED_DOMAINS",
            "original_started_utc": "2026-07-20T00:00:00Z",
            "original_deadline_utc": "2026-07-21T06:00:00Z",
            "deadline_unix": 0,
            "worker_cap": 64,
            "workers_launched_recovery": 1,
            "workers_running_recovery": 0,
            "retained_completed_lanes": 63,
            "manifest_sha256": tranche.MAGIC_MANIFEST_SHA256,
            "approved_artifact_hashes": copy.deepcopy(tranche.MAGIC_APPROVED_ARTIFACT_HASHES),
            "proof_claim": False,
            "anomaly": None,
            "updated_utc": "2026-07-21T06:00:00Z",
            "lanes": state_lanes,
        }
        summary = {
            "schema_version": 1,
            "kind": "magic_square_squares_frozen_tranche_recovery_summary",
            "run_id": tranche.MAGIC_RUN_ID,
            "source_run_id": tranche.MAGIC_SOURCE_RUN_ID,
            "source_portfolio_status": "RUNNING",
            "status": "NO_HIT_DECLARED_DOMAINS",
            "proof_claim": False,
            "claim_scope": "DECLARED_DOMAINS_ONLY",
            "original_started_utc": "2026-07-20T00:00:00Z",
            "original_deadline_utc": "2026-07-21T06:00:00Z",
            "finished_utc": "2026-07-21T06:00:00Z",
            "manifest_sha256": tranche.MAGIC_MANIFEST_SHA256,
            "approved_artifact_hashes": copy.deepcopy(tranche.MAGIC_APPROVED_ARTIFACT_HASHES),
            "workers_requested_original": 64,
            "workers_launched_recovery": 1,
            "retained_completed_lanes": 63,
            "combined_lane_count": 64,
            "stop_reason": "ALL_COMPLETED",
            "hit_lane": None,
            "anomaly": None,
            "owned_tree_snapshot_error": None,
            "unverified_stop_lanes": [],
            "dead_root_failures": [],
            "owned_process_survivors": [],
            "source_anomaly_retained_as_provenance": None,
            "nonempty_recovery_stderr_lanes": [],
            "original_artifacts_unchanged": True,
            "changed_original_files": [],
            "lane_status_counts": {"NO_HIT": 64},
            "lanes": summary_lanes,
        }
        inventory = {
            "source_run_dir": str(tranche.MAGIC_SOURCE_RUN_DIR.resolve()),
            "files": {},
        }
        run_once = {
            "approved_artifact_hashes": copy.deepcopy(tranche.MAGIC_APPROVED_ARTIFACT_HASHES),
            "approved_gaussian_exe_sha256": tranche.MAGIC_APPROVED_ARTIFACT_HASHES["gaussian_center.exe"],
            "created_utc": "2026-07-20T00:00:00Z",
            "creator_pid": 1,
            "manifest_sha256": tranche.MAGIC_MANIFEST_SHA256,
            "original_deadline_unix": 0,
            "original_start_unix": 0,
            "rule": "once",
            "run_dir": str(tranche.MAGIC_RUN_DIR.resolve()),
            "schema_version": 1,
            "source_run_dir": str(tranche.MAGIC_SOURCE_RUN_DIR.resolve()),
            "source_summary_sha256": ZERO_SHA,
        }

        def run(
            candidate_state: dict[str, object],
            candidate_summary: dict[str, object],
            *,
            bad_actual_artifact: str | None = None,
        ) -> dict[str, object]:
            records = {
                tranche.MAGIC_STATE_PATH: candidate_state,
                tranche.MAGIC_SUMMARY_PATH: candidate_summary,
                tranche.MAGIC_INVENTORY_PATH: inventory,
                tranche.MAGIC_RUN_ONCE_PATH: run_once,
            }

            def fake_hash(path: Path) -> str:
                name = Path(path).name
                if name in tranche.MAGIC_APPROVED_ARTIFACT_HASHES:
                    if name == bad_actual_artifact:
                        return ZERO_SHA
                    return tranche.MAGIC_APPROVED_ARTIFACT_HASHES[name]
                return ZERO_SHA

            with mock.patch.object(
                    tranche, "_load_json",
                    side_effect=lambda path, **_: copy.deepcopy(records[path]),
                ), mock.patch.object(tranche, "_sha256_file", side_effect=fake_hash), \
                    mock.patch.object(tranche, "_inventory", return_value={}), \
                    mock.patch.object(tranche, "_scan_magic_raw_candidate_signals"), \
                    mock.patch.object(tranche, "_magic_recovery_tree_sha256", return_value=ZERO_SHA), \
                    mock.patch.object(Path, "rglob", return_value=[]), \
                    mock.patch.object(Path, "is_file", return_value=True), \
                    mock.patch.object(Path, "stat", return_value=mock.Mock(st_size=0)):
                return tranche._validate_magic_terminal()

        valid = run(copy.deepcopy(state), copy.deepcopy(summary))
        self.assertEqual(valid["outcome"], "CONTINUE")
        bad_retained_state = copy.deepcopy(state)
        bad_retained_summary = copy.deepcopy(summary)
        for value in (bad_retained_state, bad_retained_summary):
            value["lanes"][0]["owned"] = True
            value["lanes"][0]["pid"] = 7
        with self.assertRaisesRegex(tranche.TrancheError, "retained"):
            run(bad_retained_state, bad_retained_summary)

        outside_state = copy.deepcopy(state)
        outside_summary = copy.deepcopy(summary)
        outside_path = str((tranche.ENGINE_DIR / "outside.stderr.txt").resolve())
        outside_state["lanes"][0]["stderr"] = outside_path
        outside_summary["lanes"][0]["stderr"] = outside_path
        with self.assertRaisesRegex(tranche.TrancheError, "stderr path is not canonical"):
            run(outside_state, outside_summary)


        duplicate_summary = copy.deepcopy(summary)
        duplicate_summary["lanes"][-1] = copy.deepcopy(duplicate_summary["lanes"][0])
        with self.assertRaisesRegex(tranche.TrancheError, "lane identities"):
            run(copy.deepcopy(state), duplicate_summary)

        timeout_state = copy.deepcopy(state)
        timeout_summary = copy.deepcopy(summary)
        timeout_state["status"] = "TIMEOUT_INCOMPLETE"
        timeout_summary["status"] = "TIMEOUT_INCOMPLETE"
        timeout_summary["stop_reason"] = "ORIGINAL_DEADLINE"
        timeout_state["lanes"][-1]["status"] = "TIMEOUT_INCOMPLETE"
        timeout_state["lanes"][-1]["return_code"] = 3
        timeout_summary["lanes"][-1]["status"] = "TIMEOUT_INCOMPLETE"
        timeout_summary["lanes"][-1]["return_code"] = 3
        with self.assertRaisesRegex(tranche.TrancheError, "lane_status_counts"):
            run(timeout_state, timeout_summary)

        artifact_name = next(iter(tranche.MAGIC_APPROVED_ARTIFACT_HASHES))
        with self.assertRaisesRegex(tranche.TrancheError, "actual magic artifact"):
            run(copy.deepcopy(state), copy.deepcopy(summary), bad_actual_artifact=artifact_name)

    def test_raw_magic_candidate_signal_is_rejected(self) -> None:
        raw_file = mock.MagicMock()
        raw_file.is_file.return_value = True
        raw_file.suffix = ".json"
        raw_file.name = "lane_result.json"
        raw_file.read_text.return_value = json.dumps({"candidate_count": 1})
        root = mock.MagicMock()
        root.rglob.return_value = [raw_file]
        with self.assertRaisesRegex(tranche.TrancheError, "candidate signal"):
            tranche._scan_magic_raw_candidate_signals(root)
    def test_monotonic_boot_binding_rejects_reboot_expiry_and_wall_lag(self) -> None:
        t0 = datetime(2026, 7, 21, 5, 0, 0, tzinfo=UTC)
        boot_us = 1_700_000_000_000_000
        start_ns = 10_000_000_000
        lock = clock_lock(t0)
        lock["boot_time_microseconds"] = boot_us
        lock["monotonic_start_ns"] = start_ns
        state = tranche._state_template(lock, "READY_A", t0)

        with mock.patch("psutil.boot_time", return_value=boot_us / 1_000_000), \
                mock.patch.object(
                    tranche.time, "monotonic_ns",
                    return_value=start_ns + 3_600 * 1_000_000_000,
                ):
            tranche._validate_transition_clock(
                state, t0 + timedelta(hours=1), lock
            )

        with mock.patch("psutil.boot_time", return_value=(boot_us + 1_000_000) / 1_000_000), \
                mock.patch.object(
                    tranche.time, "monotonic_ns",
                    return_value=start_ns + 3_600 * 1_000_000_000,
                ):
            with self.assertRaises(tranche.TrancheError):
                tranche._validate_transition_clock(
                    state, t0 + timedelta(hours=1), lock
                )

        with mock.patch("psutil.boot_time", return_value=boot_us / 1_000_000), \
                mock.patch.object(
                    tranche.time, "monotonic_ns",
                    return_value=start_ns + 28_800 * 1_000_000_000,
                ):
            with self.assertRaises(tranche.TrancheError):
                tranche._validate_transition_clock(
                    state, t0 + timedelta(hours=7), lock
                )

        with mock.patch("psutil.boot_time", return_value=boot_us / 1_000_000), \
                mock.patch.object(
                    tranche.time, "monotonic_ns",
                    return_value=start_ns + 14_400 * 1_000_000_000,
                ):
            with self.assertRaises(tranche.TrancheError):
                tranche._validate_transition_clock(
                    state, t0 + timedelta(hours=3), lock
                )

    def test_verified_artifact_hash_and_exact_set_are_revalidated(self) -> None:
        case = self._main_fixture("VERIFIED_HIT")
        extra_path = case["run_dir"] / "lane_01.candidate_000.verified.json"
        extra_path.write_text("{}\n", encoding="ascii")
        with self.assertRaises(tranche.PermanentFailure):
            self._call_accept_main(case)
        case["fail_closed_mock"].assert_called_once()

        case = self._main_fixture("VERIFIED_HIT")
        verified_path = case["run_dir"] / "lane_00.candidate_000.verified.json"
        verified_path.write_text("{}\n", encoding="ascii")
        with self.assertRaises(tranche.PermanentFailure):
            self._call_accept_main(case)
        case["fail_closed_mock"].assert_called_once()



    def test_verified_hit_candidate_index_must_be_zero(self) -> None:
        record = {
            "integer_quadruple": ["1", "2", "3", "4"],
            "scalar_report": {},
            "independent_report": {},
            "lane_id": 0,
            "candidate_index": 1,
            "candidate_observed_utc": "2026-07-21T06:00:00Z",
            "verified_utc": "2026-07-21T06:00:01Z",
        }
        with self.assertRaisesRegex(
            tranche.TrancheError, "candidate index must be zero"
        ):
            tranche._validate_verified_hit(record)

    def test_verified_hit_state_requires_source_bound_evidence(self) -> None:
        now = datetime(2026, 7, 21, 6, 0, 0, tzinfo=UTC)
        lock = clock_lock(now - timedelta(minutes=1))
        record = {
            "integer_quadruple": ["1", "2", "3", "4"],
            "scalar_report": {},
            "independent_report": {},
            "lane_id": 0,
            "candidate_index": 0,
            "candidate_observed_utc": "2026-07-21T06:00:00Z",
            "verified_utc": "2026-07-21T06:00:01Z",
        }
        evidence = {
            "verified_hit": copy.deepcopy(record),
            "run_inventory": {"supervisor_summary.json": ZERO_SHA},
        }
        pilot_state = tranche._state_template(lock, "VERIFIED_HIT", now)
        pilot_state.update(revision=1, last_intent="transition_000001.json")
        pilot_state["accepted_pilots"] = {"A": evidence}
        pilot_state["verified_hit"] = tranche._pilot_hit_binding("A", evidence)

        with mock.patch.object(
            tranche, "_validate_verified_hit", return_value=record
        ):
            self.assertEqual(
                tranche._validate_state_shape(copy.deepcopy(pilot_state)),
                pilot_state,
            )

            unbound = copy.deepcopy(pilot_state)
            unbound["verified_hit"] = copy.deepcopy(record)
            with self.assertRaisesRegex(
                tranche.TrancheError, "verified-hit binding keys differ"
            ):
                tranche._validate_state_shape(unbound)

            drifted = copy.deepcopy(pilot_state)
            drifted["accepted_pilots"]["A"]["run_inventory"][
                "supervisor_summary.json"
            ] = "1" * 64
            with self.assertRaisesRegex(
                tranche.PermanentFailure, "not bound to accepted evidence"
            ):
                tranche._validate_state_shape(drifted)

            main_state = tranche._state_template(lock, "VERIFIED_HIT", now)
            main_state.update(
                revision=5,
                last_intent="transition_000005.json",
                main_terminal_report_sha256=ZERO_SHA,
            )
            main_report = {"verified_hit": copy.deepcopy(record)}
            main_state["verified_hit"] = tranche._main_hit_binding(
                main_report, ZERO_SHA
            )
            tranche._validate_state_shape(main_state)
            main_state["verified_hit"]["source_evidence_sha256"] = "2" * 64
            with self.assertRaisesRegex(
                tranche.PermanentFailure, "not bound to its terminal report"
            ):
                tranche._validate_state_shape(main_state)

    def test_exact_run_inventory_rejects_reparse_and_symlink_entries(self) -> None:
        base = tranche.ENGINE_DIR / f".q5-inventory-security-{uuid.uuid4().hex}"
        base.mkdir()
        self.addCleanup(shutil.rmtree, base, True)
        with self.subTest(root=base.name):
            run_dir = base / "run"
            run_dir.mkdir()
            for name in (
                "launch.lock",
                "supervisor_state.json",
                "supervisor_summary.json",
                "lane_00.result.json",
                "lane_00.stdout.txt",
                "lane_00.stderr.txt",
            ):
                (run_dir / name).write_bytes(b"")
            result_path = run_dir / "lane_00.result.json"
            baseline, _, _ = tranche._validate_exact_run_inventory(
                run_dir=run_dir,
                spawned_lane_ids={0},
                result_paths={0: result_path},
                verified_artifact_path=None,
                name="security regression",
            )
            self.assertEqual(
                set(baseline),
                {
                    "launch.lock",
                    "supervisor_state.json",
                    "supervisor_summary.json",
                    "lane_00.result.json",
                    "lane_00.stdout.txt",
                    "lane_00.stderr.txt",
                },
            )

            with mock.patch.object(
                tranche,
                "_is_reparse_stat",
                side_effect=[False, False, False, False, True],
            ):
                with self.assertRaisesRegex(
                    tranche.TrancheError, "symlink or reparse point"
                ):
                    tranche._validate_exact_run_inventory(
                        run_dir=run_dir,
                        spawned_lane_ids={0},
                        result_paths={0: result_path},
                        verified_artifact_path=None,
                        name="security regression",
                    )

            stdout_path = run_dir / "lane_00.stdout.txt"
            target_path = base / "outside.txt"
            target_path.write_bytes(b"outside")
            stdout_path.unlink()
            try:
                stdout_path.symlink_to(target_path)
            except (NotImplementedError, OSError):
                pass
            else:
                with self.assertRaisesRegex(
                    tranche.TrancheError, "symlink or reparse point"
                ):
                    tranche._validate_exact_run_inventory(
                        run_dir=run_dir,
                        spawned_lane_ids={0},
                        result_paths={0: result_path},
                        verified_artifact_path=None,
                        name="security regression",
                    )

            magic_tree = base / "magic-tree"
            magic_tree.mkdir()
            magic_evidence = magic_tree / "evidence.json"
            magic_evidence.write_bytes(b"{}\n")
            self.assertEqual(
                tranche._inventory(magic_tree),
                {"evidence.json": tranche._sha256_file(magic_evidence)},
            )
            with mock.patch.object(
                tranche, "_is_reparse_stat", side_effect=[False, True]
            ):
                with self.assertRaisesRegex(
                    tranche.TrancheError, "symlink or reparse point"
                ):
                    tranche._inventory(magic_tree)

    def test_audit_revalidates_magic_terminal_prerequisite(self) -> None:
        t0 = datetime(2026, 7, 21, 5, 0, 0, tzinfo=UTC)
        lock = clock_lock(t0)
        pinned_magic = {
            "outcome": "CONTINUE",
            "summary_sha256": ZERO_SHA,
        }
        plan = {
            "schema_version": 1,
            "kind": "Q5_TRANCHE_PLAN",
            "tranche_id": tranche.TRANCHE_ID,
            "t0": lock["t0"],
            "s": lock["s"],
            "g": lock["g"],
            "magic_terminal": pinned_magic,
            "launch_readiness": {},
            "authorization_paths": {},
            "preflight_censuses": [],
            "frozen_artifact_hashes": {},
            "pilots": {},
            "main": {},
            "candidate_table": {},
            "selection_rule": "",
            "setup_guard_milliseconds": 300_000,
            "global_lock_sha256": ZERO_SHA,
        }
        current_magic = copy.deepcopy(pinned_magic)
        current_magic["summary_sha256"] = "3" * 64
        with mock.patch.object(
            tranche, "_validate_magic_terminal", return_value=current_magic
        ):
            with self.assertRaisesRegex(
                tranche.PermanentFailure, "magic terminal prerequisite differs"
            ):
                tranche._audit_plan(plan, {})

    def test_accept_main_rejects_nonunique_and_parallel_hit_results(self) -> None:
        case = self._main_fixture("VERIFIED_HIT")
        lane_zero_path = case["run_dir"] / "lane_00.result.json"
        lane_zero = json.loads(lane_zero_path.read_text(encoding="ascii"))
        lane_zero["candidates"].append(copy.deepcopy(lane_zero["candidates"][0]))
        lane_zero["counts"]["candidate_records"] = "2"
        lane_zero["counts"]["verified_integer_certificates"] = "2"
        lane_zero["counts"]["bounded_z_squares"] = "2"
        lane_zero_path.write_text(
            json.dumps(lane_zero, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        with self.assertRaises(tranche.PermanentFailure):
            self._call_accept_main(case)
        case["fail_closed_mock"].assert_called_once()

        case = self._main_fixture("VERIFIED_HIT")
        lane_zero = json.loads(
            (case["run_dir"] / "lane_00.result.json").read_text(encoding="ascii")
        )
        lane_one_path = case["run_dir"] / "lane_01.result.json"
        lane_one = json.loads(lane_one_path.read_text(encoding="ascii"))
        lane_one["status"] = "HIT"
        lane_one["complete"] = False
        lane_one["candidates"] = copy.deepcopy(lane_zero["candidates"])
        for key in (
            "pairs_considered", "admissible_specializations",
            "bounded_z_squares", "candidate_records",
            "verified_integer_certificates",
        ):
            lane_one["counts"][key] = "1"
        lane_one_path.write_text(
            json.dumps(lane_one, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        summary_path = case["run_dir"] / "supervisor_summary.json"
        summary = json.loads(summary_path.read_text(encoding="ascii"))
        summary["lane_statuses"]["1"] = "VERIFIED_HIT"
        summary_path.write_text(
            json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        state_path = case["run_dir"] / "supervisor_state.json"
        final_state = json.loads(state_path.read_text(encoding="ascii"))
        final_state["lanes"]["1"]["status"] = "VERIFIED_HIT"
        state_path.write_text(
            json.dumps(final_state, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        with self.assertRaises(tranche.PermanentFailure):
            self._call_accept_main(case)
        case["fail_closed_mock"].assert_called_once()

    def test_accept_main_rejects_stopped_lane_with_stray_result(self) -> None:
        case = self._main_fixture("VERIFIED_HIT")
        summary_path = case["run_dir"] / "supervisor_summary.json"
        summary = json.loads(summary_path.read_text(encoding="ascii"))
        summary["lane_statuses"]["1"] = "STOPPED_AFTER_VERIFIED_HIT"
        summary_path.write_text(
            json.dumps(summary, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        state_path = case["run_dir"] / "supervisor_state.json"
        final_state = json.loads(state_path.read_text(encoding="ascii"))
        final_state["lanes"]["1"]["status"] = "STOPPED_AFTER_VERIFIED_HIT"
        state_path.write_text(
            json.dumps(final_state, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="ascii",
        )
        self.assertTrue((case["run_dir"] / "lane_01.result.json").is_file())
        with self.assertRaises(tranche.PermanentFailure):
            self._call_accept_main(case)
        case["fail_closed_mock"].assert_called_once()

    def test_accept_pilot_rechecks_identical_inventory_before_commit(self) -> None:
        now = datetime(2026, 7, 21, 6, 0, 0, tzinfo=UTC)
        lock = clock_lock(now - timedelta(minutes=1))
        state = tranche._state_template(lock, "READY_A", now)
        first = {
            "run_inventory": {"supervisor_summary.json": "1" * 64},
            "verified_hit": None,
        }
        drifted = copy.deepcopy(first)
        drifted["run_inventory"]["supervisor_summary.json"] = "2" * 64
        validator = mock.Mock(
            side_effect=[(copy.deepcopy(first), False), (drifted, False)]
        )
        with mock.patch.object(
                tranche, "_load_context", return_value=(lock, {}, state)
            ), mock.patch.object(
                tranche, "_validate_transition_clock"
            ), mock.patch.object(
                tranche, "_validate_pilot_evidence", validator
            ), mock.patch.object(
                tranche, "_now_utc", return_value=now
            ), mock.patch.object(
                tranche, "_write_xb"
            ), mock.patch.object(
                tranche.manifest_lib, "atomic_write_bytes"
            ):
            with self.assertRaisesRegex(
                tranche.PermanentFailure, "terminal evidence changed before commit"
            ):
                tranche.accept_pilot("A")
        self.assertEqual(validator.call_count, 2)

    def test_preview_finalize_audit_sequence_uses_ledger_anchor(self) -> None:
        anchor = datetime(2026, 7, 21, 6, 0, 0, tzinfo=UTC)
        ready_state = timing_state(anchor, remaining_ms=600_000)
        ready_state.update(phase="READY_SELECTION")
        terminal_state = copy.deepcopy(ready_state)
        terminal_state.update(
            phase="MAIN_FROZEN",
            updated_utc=iso(anchor + timedelta(minutes=1)),
        )
        intent_path = Path("transition_000004.json")
        intent = {
            "tranche_id": tranche.TRANCHE_ID,
            "to_revision": 4,
            "from_phase": "READY_D",
            "to_phase": "READY_SELECTION",
            "created_utc": iso(anchor),
        }
        rows = [candidate_row(48, 3), candidate_row(49, 4)]
        with mock.patch.object(
                tranche, "_intent_files", return_value=[intent_path]
            ), mock.patch.object(
                tranche, "_load_json", return_value=intent
            ), mock.patch.object(
                tranche, "_radicand_bits", return_value=5
            ), mock.patch.object(
                tranche, "_candidate_table", return_value=rows
            ):
            preview_anchor = tranche._ready_selection_anchor(ready_state)
            preview = tranche._selection_core(
                ready_state, {}, anchor + timedelta(seconds=1),
                ready_selection_anchor=preview_anchor,
            )
            audit_anchor = tranche._ready_selection_anchor(terminal_state)
            audited = tranche._selection_core(
                terminal_state, {}, anchor,
                ready_selection_anchor=audit_anchor,
            )
        self.assertEqual(preview_anchor, anchor)
        self.assertEqual(audit_anchor, anchor)
        self.assertEqual(preview, audited)
        self.assertEqual(preview["generated_utc"], iso(anchor))

    def test_exact_preview_finalize_audit_command_sequence(self) -> None:
        anchor = datetime(2026, 7, 21, 6, 0, 0, tzinfo=UTC)
        lock = clock_lock(anchor - timedelta(minutes=1))
        ready_state = tranche._state_template(lock, "READY_SELECTION", anchor)
        ready_state.update(revision=4, last_intent="transition_000004.json")
        ready_state["accepted_pilots"] = timing_state(anchor)["accepted_pilots"]
        plan = {"candidate_table": {"file_sha256": ZERO_SHA}}
        state_holder = [ready_state]
        intent_path = Path("transition_000004.json")
        intent = {
            "tranche_id": tranche.TRANCHE_ID,
            "to_revision": 4,
            "from_phase": "READY_D",
            "to_phase": "READY_SELECTION",
            "created_utc": iso(anchor),
        }
        row = candidate_row(48, 3)
        row["balance_pass"] = False
        report_path = (
            tranche.ENGINE_DIR
            / f".q5-selection-sequence-{uuid.uuid4().hex}.json"
        )
        self.addCleanup(report_path.unlink, missing_ok=True)
        state_path = report_path.with_suffix(".state.json")
        intents_dir = report_path.with_suffix(".intents")
        self.addCleanup(state_path.unlink, missing_ok=True)
        original_load_json = tranche._load_json

        def load_context() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
            return lock, plan, copy.deepcopy(state_holder[0])

        def load_json(path: Path, *args: object, **kwargs: object) -> object:
            if Path(path) == intent_path:
                return copy.deepcopy(intent)
            return original_load_json(path, *args, **kwargs)

        def atomic_write(path: Path, data: bytes) -> None:
            if Path(path) == state_path:
                state_holder[0] = json.loads(data.decode("ascii"))
            else:
                Path(path).write_bytes(data)

        public_clock = mock.Mock(
            side_effect=[
                anchor + timedelta(seconds=1),
                anchor + timedelta(seconds=2),
                anchor + timedelta(seconds=3),
            ]
        )
        with mock.patch.object(
                tranche, "SELECTION_REPORT_PATH", report_path
            ), mock.patch.object(
                tranche, "STATE_PATH", state_path
            ), mock.patch.object(
                tranche, "INTENTS_DIR", intents_dir
            ), mock.patch.object(
                tranche, "_load_context", side_effect=load_context
            ), mock.patch.object(
                tranche, "_intent_files", return_value=[intent_path]
            ), mock.patch.object(
                tranche, "_load_json", side_effect=load_json
            ), mock.patch.object(
                tranche, "_radicand_bits", return_value=5
            ), mock.patch.object(
                tranche, "_candidate_table", return_value=[row]
            ), mock.patch.object(
                tranche, "_validate_transition_clock"
            ), mock.patch.object(
                tranche, "_revalidate_accepted_artifacts"
            ), mock.patch.object(
                tranche, "_current_clean_census", return_value={}
            ), mock.patch.object(
                tranche, "_audit_plan"
            ), mock.patch.object(
                tranche, "_now_utc", side_effect=public_clock
            ), mock.patch.object(
                tranche, "_write_xb"
            ), mock.patch.object(
                tranche.manifest_lib, "atomic_write_bytes", side_effect=atomic_write
            ):
            preview = tranche.preview_selection()
            finalized = tranche.finalize_selection()
            audited = tranche.audit_tranche()

        self.assertIsNone(preview["selected_h"])
        self.assertEqual(preview["generated_utc"], iso(anchor))
        self.assertEqual(finalized["phase"], "NO_MAIN")
        self.assertTrue(audited["ok"])
        self.assertEqual(audited["phase"], "NO_MAIN")
        report = json.loads(report_path.read_text(encoding="ascii"))
        self.assertEqual(report["generated_utc"], iso(anchor))
        self.assertEqual(
            state_holder[0]["updated_utc"], iso(anchor + timedelta(seconds=3))
        )

if __name__ == "__main__":
    unittest.main(verbosity=2)
