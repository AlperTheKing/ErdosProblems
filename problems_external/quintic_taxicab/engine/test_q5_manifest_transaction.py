from __future__ import annotations

import hashlib
import json
import shutil
import sys
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


ENGINE = Path(__file__).resolve().parent
sys.path.insert(0, str(ENGINE))
import q5_manifest as manifest_lib
import q5_manifest_transaction as transaction_lib


class ManifestTransactionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ENGINE / f"q5-manifest-transaction-test-{uuid.uuid4().hex}"
        self.engine.mkdir()
        for name in (
            "scan_torsor_exact.exe",
            "scan_torsor_exact.cpp",
            "verify_certificate.py",
            "verify_independent.exe",
            "q5_supervisor.py",
        ):
            (self.engine / name).write_bytes((name + "\n").encode("ascii"))
        self.now = datetime.now(timezone.utc).replace(microsecond=0)
        self.tranche = self.engine / "logs" / transaction_lib.TRANCHE_ID
        self.tranche.mkdir(parents=True)
        self.write_context("READY_A")

    def tearDown(self) -> None:
        shutil.rmtree(self.engine, ignore_errors=True)

    def _phase_paths(self, phase: str) -> tuple[Path, Path, Path]:
        base = self.tranche / ("main" if phase == "MAIN" else f"pilot_{phase}")
        return base / "manifest.json", base / "lanes", base / "run"

    def write_context(
        self,
        phase: str,
        *,
        updated: datetime | None = None,
        s: datetime | None = None,
    ) -> None:
        deadline = self.now + timedelta(hours=1) if s is None else s
        pilots = []
        for name, spec in transaction_lib.PILOT_SPECS.items():
            manifest, lanes, run = self._phase_paths(name)
            pilots.append(
                {
                    "name": name,
                    "campaign_id": f"q5-tranche-v1-pilot-{name}",
                    "bounds": spec["bounds"],
                    "search_mode": spec["search_mode"],
                    "limit_seconds": spec["limit_seconds"],
                    "expected_no_work": 1 if name == "A" else 0,
                    "manifest_path": str(manifest.resolve()),
                    "lane_config_dir": str(lanes.resolve()),
                    "run_dir": str(run.resolve()),
                }
            )
        main_manifest, main_lanes, main_run = self._phase_paths("MAIN")
        plan = {
            "schema_version": 1,
            "kind": "Q5_TRANCHE_PLAN",
            "tranche_id": transaction_lib.TRANCHE_ID,
            "pilots": pilots,
            "main": {
                "campaign_id": "q5-tranche-v1-main",
                "manifest_path": str(main_manifest.resolve()),
                "lane_config_dir": str(main_lanes.resolve()),
                "run_dir": str(main_run.resolve()),
                "deadline": transaction_lib._utc_text(deadline),
            },
        }
        plan_bytes = (json.dumps(plan, indent=2, sort_keys=True) + "\n").encode("ascii")
        (self.tranche / "plan.json").write_bytes(plan_bytes)
        state = {
            "schema_version": 1,
            "kind": "Q5_TRANCHE_STATE",
            "tranche_id": transaction_lib.TRANCHE_ID,
            "phase": phase,
            "s": transaction_lib._utc_text(deadline),
            "updated_utc": transaction_lib._utc_text(updated or self.now),
            "persistent_error": None,
            "plan_sha256": hashlib.sha256(plan_bytes).hexdigest(),
        }
        (self.tranche / "state.json").write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="ascii"
        )

    def build(self, phase: str = "A", selected_h: int | None = None) -> dict:
        return transaction_lib.build_phase(
            phase,
            selected_h=selected_h,
            engine_dir=self.engine,
            clock=lambda: self.now,
        )

    def test_pilot_atomic_commit_audits_and_is_idempotent(self) -> None:
        result = self.build()
        self.assertEqual(result["status"], "CREATED")
        manifest, lanes, _run = self._phase_paths("A")
        envelope = manifest_lib.audit_manifest(
            manifest, expected_campaign_id="q5-tranche-v1-pilot-A"
        )
        self.assertEqual(result["manifest_payload_sha256"], envelope["payload_sha256"])
        created = manifest_lib.parse_deadline(envelope["payload"]["created_utc"])
        deadline = manifest_lib.parse_deadline(envelope["payload"]["deadline"])
        # Native workers require second-precision deadlines.  The producer keeps
        # microseconds in created_utc and rounds the 120-second ceiling down, so
        # the executable deadline never exceeds the declared local limit.
        duration = deadline - created
        self.assertGreater(duration, timedelta(seconds=119))
        self.assertLessEqual(duration, timedelta(seconds=120))
        self.assertEqual(deadline.microsecond, 0)

        self.assertEqual(len(list(lanes.glob("lane_*.tsv"))), 64)
        for path in manifest.parent.rglob("*"):
            if path.is_file():
                self.assertNotIn(b".pilot_A.build.", path.read_bytes())
        self.assertEqual(list(self.tranche.glob(".pilot_A.build.*")), [])

        repeated = self.build()
        self.assertEqual(repeated["status"], "REUSED")
        self.assertEqual(repeated["manifest_file_sha256"], result["manifest_file_sha256"])

    def test_builder_failure_and_keyboard_interrupt_leave_no_fixed_path(self) -> None:
        with mock.patch.object(
            transaction_lib.manifest_lib,
            "build_manifest",
            side_effect=manifest_lib.ManifestError("fixture failure"),
        ):
            with self.assertRaisesRegex(transaction_lib.TransactionError, "fixture failure"):
                self.build()
        self.assertFalse((self.tranche / "pilot_A").exists())
        self.assertEqual(list(self.tranche.glob(".pilot_A.build.*")), [])

        with mock.patch.object(
            transaction_lib.manifest_lib, "build_manifest", side_effect=KeyboardInterrupt
        ):
            with self.assertRaises(KeyboardInterrupt):
                self.build()
        self.assertFalse((self.tranche / "pilot_A").exists())
        self.assertEqual(list(self.tranche.glob(".pilot_A.build.*")), [])

    def test_state_change_during_build_blocks_commit(self) -> None:
        original = manifest_lib.build_manifest

        def mutate_state(**kwargs):
            envelope = original(**kwargs)
            state_path = self.tranche / "state.json"
            state = json.loads(state_path.read_text(encoding="ascii"))
            state["fixture_drift"] = True
            state_path.write_text(json.dumps(state), encoding="ascii")
            return envelope

        with mock.patch.object(transaction_lib.manifest_lib, "build_manifest", mutate_state):
            with self.assertRaisesRegex(transaction_lib.TransactionError, "state changed"):
                self.build()
        self.assertFalse((self.tranche / "pilot_A").exists())
        self.assertEqual(list(self.tranche.glob(".pilot_A.build.*")), [])

    def test_stale_staging_is_preserved_and_blocks_retry(self) -> None:
        stale = self.tranche / ".pilot_A.build.stale"
        stale.mkdir()
        (stale / "evidence.txt").write_text("partial", encoding="ascii")
        with self.assertRaisesRegex(transaction_lib.TransactionError, "stale manifest staging"):
            self.build()
        self.assertEqual((stale / "evidence.txt").read_text(encoding="ascii"), "partial")
        self.assertFalse((self.tranche / "pilot_A").exists())

    def test_wrong_phase_and_invalid_existing_target_fail_closed(self) -> None:
        self.write_context("READY_B")
        with self.assertRaisesRegex(transaction_lib.TransactionError, "requires READY_A"):
            self.build()

        self.write_context("READY_A")
        base = self.tranche / "pilot_A"
        base.mkdir()
        (base / "manifest.json").write_text("{}", encoding="ascii")
        with self.assertRaisesRegex(transaction_lib.TransactionError, "existing fixed manifest"):
            self.build()

    def test_main_fixed_paths_deadline_and_setup_window(self) -> None:
        self.write_context("READY_SELECTION")
        result = self.build("MAIN", selected_h=48)
        self.assertEqual(result["status"], "CREATED")
        manifest, _lanes, run = self._phase_paths("MAIN")
        envelope = manifest_lib.audit_manifest(
            manifest, expected_campaign_id="q5-tranche-v1-main"
        )
        self.assertEqual(envelope["payload"]["bounds"], {"P": 48, "Q": 48, "N": 48, "D": 48})
        self.assertEqual(envelope["payload"]["deadline"], transaction_lib._utc_text(self.now + timedelta(hours=1)))
        self.assertEqual(envelope["payload"]["run_dir"], str(run.resolve()))

    def test_main_rejects_bad_h_and_expired_setup_window(self) -> None:
        self.write_context("READY_SELECTION")
        with self.assertRaisesRegex(transaction_lib.TransactionError, "outside the frozen"):
            self.build("MAIN", selected_h=47)
        self.write_context("READY_SELECTION", updated=self.now - timedelta(seconds=301))
        with self.assertRaisesRegex(transaction_lib.TransactionError, "setup window"):
            self.build("MAIN", selected_h=48)

    def test_main_crossing_setup_window_does_not_commit(self) -> None:
        self.write_context("READY_SELECTION")
        instants = iter((self.now, self.now + timedelta(seconds=301)))
        with self.assertRaisesRegex(
            transaction_lib.TransactionError, "elapsed during manifest construction"
        ):
            transaction_lib.build_phase(
                "MAIN",
                selected_h=48,
                engine_dir=self.engine,
                clock=lambda: next(instants),
            )
        main = self.tranche / "main"
        self.assertFalse(main.exists())
        self.assertEqual(list(self.tranche.glob(".main.build.*")), [])



if __name__ == "__main__":
    unittest.main()
