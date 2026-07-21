#!/usr/bin/env python3
"""Focused exact and fail-closed tests for the native Q5 torsor scanner."""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import subprocess
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from reference_enumerator import BoxBounds, enumerate_box


HERE = Path(__file__).resolve().parent
WORKER = HERE / "scan_torsor_exact.exe"
AUDIT_MODE = "audit_signed_u_both_y"
CANONICAL_MODE = "canonical_positive_u_positive_y"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def future_deadline() -> str:
    return (
        (datetime.now(timezone.utc) + timedelta(hours=1))
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def estimated_work(p: int, q: int, N: int, D: int, mode: str) -> int:
    maxima = [min(N, (p * d - 1) // q) for d in range(1, D + 1)]
    if mode == CANONICAL_MODE:
        return D * N + sum(maxima)
    return D * (2 * N + 1) + sum(1 + 2 * value for value in maxima)


def lane_bytes(
    *,
    specializations: list[tuple[int, int]],
    P: int,
    Q: int,
    N: int,
    D: int,
    mode: str = AUDIT_MODE,
    lane_id: int = 0,
    campaign_id: str = "q5-scanner-test",
    deadline: str | None = None,
) -> tuple[bytes, str]:
    deadline = deadline or future_deadline()
    jobs = [
        {
            "p": p,
            "q": q,
            "estimated_work": estimated_work(p, q, N, D, mode),
        }
        for p, q in specializations
    ]
    assignment_sha = hashlib.sha256(canonical_bytes(jobs)).hexdigest()
    lines = [
        "Q5_TORSOR_LANE_V1",
        f"campaign_id\t{campaign_id}",
        f"deadline\t{deadline}",
        f"search_mode\t{mode}",
        f"lane_id\t{lane_id}",
        "lane_count\t64",
        f"P\t{P}",
        f"Q\t{Q}",
        f"N\t{N}",
        f"D\t{D}",
        f"assignment_sha256\t{assignment_sha}",
        f"count\t{len(jobs)}",
        "p\tq\testimated_work",
    ]
    lines.extend(f"{job['p']}\t{job['q']}\t{job['estimated_work']}" for job in jobs)
    return ("\n".join(lines) + "\n").encode("ascii"), deadline


def all_reduced(P: int, Q: int) -> list[tuple[int, int]]:
    return [
        (p, q)
        for q in range(1, Q + 1)
        for p in range(1, P + 1)
        if math.gcd(p, q) == 1
    ]

class WorkspaceTemporaryDirectory:
    def __enter__(self) -> str:
        self.path = HERE / f"q5_native_scan_test_{uuid.uuid4().hex}"
        self.path.mkdir()
        return str(self.path)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object,
    ) -> None:
        shutil.rmtree(self.path)


def run_worker(
    data: bytes,
    deadline: str,
    *,
    lane_id: int = 0,
    emit_points: bool = False,
    threads: int = 1,
    mutate_environment: Callable[[dict[str, str]], None] | None = None,
) -> tuple[subprocess.CompletedProcess[str], dict[str, Any] | None]:
    with WorkspaceTemporaryDirectory() as temporary:
        root = Path(temporary).resolve()
        lane_path = root / "lane.tsv"
        result_path = root / "result.json"
        lane_path.write_bytes(data)
        environment = os.environ.copy()
        environment.update(
            {
                "Q5_MANIFEST_PAYLOAD_SHA256": hashlib.sha256(b"payload").hexdigest(),
                "Q5_LANE_FILE_SHA256": hashlib.sha256(data).hexdigest(),
                "Q5_DEADLINE_UTC": deadline,
            }
        )
        if mutate_environment is not None:
            mutate_environment(environment)
        command = [
            str(WORKER),
            "--lane-file",
            str(lane_path),
            "--lane-id",
            str(lane_id),
            "--threads",
            str(threads),
            "--result",
            str(result_path),
        ]
        if emit_points:
            command.append("--emit-torsor-points")
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            env=environment,
            timeout=30,
        )
        result = (
            json.loads(result_path.read_text(encoding="utf-8"))
            if result_path.is_file()
            else None
        )
        return completed, result


class NativeExactScannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not WORKER.is_file():
            raise RuntimeError(f"compile the strict native scanner first: {WORKER}")

    def test_tiny_audit_box_matches_fraction_reference(self) -> None:
        data, deadline = lane_bytes(
            specializations=[(1, 1)], P=1, Q=1, N=1, D=1
        )
        completed, result = run_worker(data, deadline)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stderr, "")
        assert result is not None
        expected = enumerate_box(BoxBounds(1, 1, 1, 1))["counts"]
        for key, value in expected.items():
            self.assertEqual(int(result["counts"][key]), value, key)
        self.assertEqual(result["status"], "NO_HIT")
        self.assertTrue(result["complete"])
        self.assertFalse(result["signed_u_symmetry_pruned"])
        self.assertFalse(result["negative_y_pruned"])
        self.assertFalse(result["zero_u_pruned"])
        self.assertFalse(result["emit_torsor_points"])

    def test_full_ten_box_counters_match_fraction_reference(self) -> None:
        data, deadline = lane_bytes(
            specializations=all_reduced(10, 10), P=10, Q=10, N=10, D=10
        )
        completed, result = run_worker(data, deadline)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        assert result is not None
        expected = enumerate_box(BoxBounds(10, 10, 10, 10))["counts"]
        for key, value in expected.items():
            self.assertEqual(int(result["counts"][key]), value, key)
        self.assertEqual(result["completed_specializations"], len(all_reduced(10, 10)))
        self.assertEqual(result["candidates"], [])

    def test_p1_q3_fixture_matches_pari_and_fraction_values(self) -> None:
        data, deadline = lane_bytes(
            specializations=[(1, 3)], P=1, Q=3, N=10, D=10
        )
        completed, result = run_worker(data, deadline, emit_points=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        assert result is not None
        point = next(
            item
            for item in result["torsor_points"]
            if item["u"] == "1/5" and item["Y_prime_abs"] == "2864/5"
        )
        self.assertEqual(len(point["branches"]), 2)
        self.assertEqual(point["branches"][0]["Z"], "-14/75")
        self.assertEqual(point["branches"][1]["Z"], "-758/225")
        self.assertEqual(result["candidates"], [])

    def test_p181_q15_fixture_rejects_positive_nonsquare_z(self) -> None:
        data, deadline = lane_bytes(
            specializations=[(181, 15)], P=181, Q=15, N=100, D=15
        )
        completed, result = run_worker(data, deadline, emit_points=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        assert result is not None
        point = next(
            item
            for item in result["torsor_points"]
            if item["u"] == "86/15" and item["Y_prime_abs"] == "84913220"
        )
        plus = next(branch for branch in point["branches"] if branch["sign"] == 1)
        self.assertEqual(plus["Z"], "68699/3150")
        self.assertTrue(plus["z_nonnegative"])
        self.assertFalse(plus["z_rational_square"])
        self.assertEqual(result["candidates"], [])

    def test_canonical_mode_prunes_only_registered_symmetries(self) -> None:
        data, deadline = lane_bytes(
            specializations=[(181, 15)],
            P=181,
            Q=15,
            N=100,
            D=15,
            mode=CANONICAL_MODE,
        )
        completed, result = run_worker(data, deadline, emit_points=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        assert result is not None
        self.assertTrue(result["signed_u_symmetry_pruned"])
        self.assertTrue(result["negative_y_pruned"])
        self.assertTrue(result["zero_u_pruned"])
        point = next(item for item in result["torsor_points"] if item["u"] == "86/15")
        self.assertEqual(len(point["branches"]), 1)
        self.assertEqual(point["branches"][0]["Z"], "68699/3150")

    def test_lane_file_digest_mismatch_fails_closed(self) -> None:
        data, deadline = lane_bytes(
            specializations=[(1, 1)], P=1, Q=1, N=1, D=1
        )
        completed, result = run_worker(
            data,
            deadline,
            mutate_environment=lambda env: env.__setitem__(
                "Q5_LANE_FILE_SHA256", "0" * 64
            ),
        )
        self.assertEqual(completed.returncode, 2)
        assert result is not None
        self.assertEqual(result["status"], "FAIL_CLOSED")
        self.assertIn("SHA-256 mismatch", result["error"])

    def test_assignment_digest_drift_fails_closed(self) -> None:
        data, deadline = lane_bytes(
            specializations=[(1, 1)], P=1, Q=1, N=1, D=1
        )
        marker = b"assignment_sha256\t"
        digest_start = data.index(marker) + len(marker)
        tampered = data[:digest_start] + b"0" * 64 + data[digest_start + 64 :]
        completed, result = run_worker(tampered, deadline)
        self.assertEqual(completed.returncode, 2)
        assert result is not None
        self.assertEqual(result["status"], "FAIL_CLOSED")
        self.assertIn("assignment SHA-256 mismatch", result["error"])

    def test_crlf_and_extra_field_fail_closed(self) -> None:
        data, deadline = lane_bytes(
            specializations=[(1, 1)], P=1, Q=1, N=1, D=1
        )
        for malformed in (data.replace(b"\n", b"\r\n"), data + b"extra\tfield\n"):
            with self.subTest(malformed=malformed[-20:]):
                completed, result = run_worker(malformed, deadline)
                self.assertEqual(completed.returncode, 2)
                assert result is not None
                self.assertEqual(result["status"], "FAIL_CLOSED")

    def test_lane_mismatch_and_expired_deadline_fail_closed(self) -> None:
        data, deadline = lane_bytes(
            specializations=[(1, 1)], P=1, Q=1, N=1, D=1
        )
        completed, result = run_worker(data, deadline, lane_id=1)
        self.assertEqual(completed.returncode, 2)
        assert result is not None
        self.assertEqual(result["status"], "FAIL_CLOSED")

        expired = "2000-01-01T00:00:00Z"
        expired_data, _ = lane_bytes(
            specializations=[(1, 1)], P=1, Q=1, N=1, D=1, deadline=expired
        )
        completed, result = run_worker(expired_data, expired)
        self.assertEqual(completed.returncode, 2)
        assert result is not None
        self.assertIn("expired", result["error"])


    def test_malformed_missing_duplicate_and_nul_tsv_fail_closed(self) -> None:
        data, deadline = lane_bytes(
            specializations=[(1, 1)], P=1, Q=1, N=1, D=1
        )
        malformed_cases = (
            data.replace(b"P\t1\n", b"P\t01\n"),
            data.replace(b"Q\t1\n", b"P\t1\n"),
            data.replace(b"D\t1\n", b""),
            data.replace(b"\n", b"\0\n", 1),
        )
        for malformed in malformed_cases:
            with self.subTest(malformed=malformed[-20:]):
                completed, result = run_worker(malformed, deadline)
                self.assertEqual(completed.returncode, 2)
                assert result is not None
                self.assertEqual(result["status"], "FAIL_CLOSED")

    def test_missing_environment_and_threads_fail_closed(self) -> None:
        data, deadline = lane_bytes(
            specializations=[(1, 1)], P=1, Q=1, N=1, D=1
        )
        def drop_payload(environment: dict[str, str]) -> None:
            environment.pop("Q5_MANIFEST_PAYLOAD_SHA256")
        completed, result = run_worker(
            data, deadline, mutate_environment=drop_payload
        )
        self.assertEqual(completed.returncode, 2)
        assert result is not None
        self.assertEqual(result["status"], "FAIL_CLOSED")

        completed, result = run_worker(data, deadline, threads=2)
        self.assertEqual(completed.returncode, 2)
        self.assertIsNone(result)
        self.assertIn("--threads", completed.stderr)

if __name__ == "__main__":
    unittest.main(verbosity=2)
