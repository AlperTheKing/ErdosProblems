#!/usr/bin/env python3
"""Process-level tests for the 64-worker supervisor using dummy workers."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import uuid
import unittest

import tranche_supervisor as supervisor


ENGINE_DIR = Path(__file__).resolve().parent
DUMMY = ENGINE_DIR / "dummy_lane_worker.py"


def dummy_specs(
    run_dir: Path,
    *,
    hit_lane: str | None = None,
    regular_delay: float = 0.10,
    hit_delay: float = 0.03,
) -> list[supervisor.LaneSpec]:
    specs: list[supervisor.LaneSpec] = []
    for family in "GENS":
        for number in range(1, 17):
            lane_id = f"{family}{number:02d}"
            lane_dir = run_dir / "lanes" / lane_id
            summary = lane_dir / "engine" / "summary.json"
            status = "HIT_VERIFIED" if lane_id == hit_lane else "NO_HIT"
            delay = hit_delay if lane_id == hit_lane else regular_delay
            command = (
                sys.executable, str(DUMMY), "--lane", lane_id,
                "--summary", str(summary), "--delay", str(delay),
                "--status", status,
                "--threads", "1",
            )
            specs.append(supervisor.LaneSpec(
                lane_id=lane_id,
                family=family,
                command=command,
                cwd=ENGINE_DIR,
                summary_kind="standard",
                engine_summary=summary,
                stdout_path=lane_dir / "process.stdout.txt",
                stderr_path=lane_dir / "process.stderr.txt",
            ))
    supervisor.validate_specs(specs)
    return specs


class TrancheSupervisorProcessTests(unittest.TestCase):
    def run_case(
        self,
        *,
        hit_lane: str | None,
        regular_delay: float,
        duration: float,
    ) -> tuple[int, dict[str, object], dict[str, object]]:
        test_root = ENGINE_DIR / "calibration" / "harness_selftest"
        test_root.mkdir(parents=True, exist_ok=True)
        run_dir = test_root / ("run-" + uuid.uuid4().hex)
        run_dir.mkdir()
        specs = dummy_specs(
            run_dir,
            hit_lane=hit_lane,
            regular_delay=regular_delay,
        )
        code = supervisor.run_specs(
            specs,
            run_dir,
            duration,
            manifest_sha256="DUMMY",
        )
        summary = json.loads(
            (run_dir / "portfolio_summary.json").read_text(encoding="utf-8")
        )
        state = json.loads(
            (run_dir / "portfolio_state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(summary["workers_launched"], 64)
        self.assertEqual(summary["family_counts"], {"E": 16, "G": 16, "N": 16, "S": 16})
        self.assertEqual(state["workers_running"], 0)
        self.assertEqual(summary["nonempty_stderr_lanes"], [])
        for lane in summary["lanes"]:
            self.assertIsNotNone(lane["return_code"])
        return code, summary, state

    def test_all_64_dummy_lanes_exhaust(self) -> None:
        code, summary, state = self.run_case(
            hit_lane=None,
            regular_delay=0.03,
            duration=5.0,
        )
        self.assertEqual(code, 0)
        self.assertEqual(summary["status"], "NO_HIT_DECLARED_DOMAINS")
        self.assertFalse(summary["proof_claim"])
        self.assertEqual(state["status"], "NO_HIT_DECLARED_DOMAINS")

    def test_verified_dummy_hit_stops_owned_workers(self) -> None:
        code, summary, state = self.run_case(
            hit_lane="E01",
            regular_delay=5.0,
            duration=10.0,
        )
        self.assertEqual(code, 0)
        self.assertEqual(summary["status"], "HIT_VERIFIED")
        self.assertEqual(summary["hit_lane"], "E01")
        self.assertEqual(state["workers_running"], 0)
        self.assertIn("STOPPED_AFTER_OTHER_HIT", summary["lane_status_counts"])

    def test_common_deadline_is_incomplete_not_no_hit(self) -> None:
        code, summary, state = self.run_case(
            hit_lane=None,
            regular_delay=5.0,
            duration=0.25,
        )
        self.assertEqual(code, 4)
        self.assertEqual(summary["status"], "TIMEOUT_INCOMPLETE")
        self.assertFalse(summary["proof_claim"])
        self.assertIn("not an impossibility proof", summary["claim_scope"])
        self.assertEqual(state["workers_running"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
