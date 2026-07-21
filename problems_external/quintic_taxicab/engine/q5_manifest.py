#!/usr/bin/env python3
"""Build and audit hash-pinned 64-lane Q5-TORSOR manifests.

This module performs orchestration only.  It does not search for rational
points.  Every positive reduced ``t=p/q`` in the declared ``P`` by ``Q``
rectangle is assigned exactly once.  Lane configuration is emitted as strict
ASCII TSV so the native worker does not need an ad-hoc JSON parser.

The manifest is an envelope whose ``payload_sha256`` is SHA-256 of the exact
ASCII bytes produced by::

    json.dumps(payload, sort_keys=True, separators=(",", ":"),
               ensure_ascii=True, allow_nan=False).encode("ascii")

An assignment digest uses the same encoding on the ordered
``specializations`` array only.  Lane TSV hashes are over their raw bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import math
import os
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_VERSION = 1
KIND = "Q5_TORSOR_LANE_MANIFEST"
LANE_COUNT = 64
MAX_DURATION = timedelta(hours=8)
MODES = ("CALIBRATION_ONLY", "SELECTED_MAIN")
SEARCH_MODES = (
    "canonical_positive_u_positive_y",
    "audit_signed_u_both_y",
)
PRUNING_CONTRACTS = {
    "canonical_positive_u_positive_y": {
        "u_domain": "reduced n/d with n>0",
        "Y_domain": "positive root only",
        "Z_domain": "0<Z<T^2 with nonnegative v",
        "zero_lift_basis": (
            "Darmon-Merel Main Theorem 1 excludes nontrivial primitive "
            "x^5+y^5=2z^5 lifts; source: Winding quotient and some variants "
            "of Fermat's Last Theorem"
        ),
    },
    "audit_signed_u_both_y": {
        "u_domain": "reduced signed n/d including unique zero 0/1",
        "Y_domain": "both signs",
        "Z_domain": "0<=Z<T^2 with nonnegative v",
        "zero_lift_basis": "no pruning in audit mode",
    },
}
CAMPAIGN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
DECIMAL_RE = re.compile(r"0|[1-9][0-9]*\Z")
BALANCE_NUMERATOR = 5
BALANCE_DENOMINATOR = 4
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "PARI_MT_ENGINE": "single",
}


class ManifestError(ValueError):
    """Raised when a manifest or build request violates the frozen contract."""


def canonical_bytes(value: Any) -> bytes:
    """Return the sole byte representation used for manifest digests."""

    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        return text.encode("ascii")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise ManifestError(f"value is not canonical-JSON encodable: {exc}") from exc


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
    except OSError as exc:
        raise ManifestError(f"cannot hash artifact {path}: {exc}") from exc
    return digest.hexdigest()


def _strict_int(value: Any, name: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ManifestError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ManifestError(f"{name} must be at least {minimum}")
    return value


def _resolved_file(path: str | Path, name: str) -> Path:
    resolved = Path(path).expanduser().resolve()
    if not resolved.is_file():
        raise ManifestError(f"{name} is not a file: {resolved}")
    return resolved


def _resolved_dir(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def parse_deadline(value: str) -> datetime:
    """Parse a timezone-aware ISO-8601 timestamp."""

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ManifestError(f"invalid deadline {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ManifestError("deadline must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def utc_text_precise(value: datetime) -> str:
    """Format provenance timestamps without collapsing same-second events."""

    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )

def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Commit one file with a same-directory replace."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise ManifestError(f"atomic write failed for {path}: {exc}") from exc


def atomic_write_json(path: Path, value: Any, pretty: bool = True) -> None:
    if pretty:
        data = (
            json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
            + "\n"
        ).encode("ascii")
    else:
        data = canonical_bytes(value) + b"\n"
    atomic_write_bytes(path, data)


def artifact_record(path: Path) -> dict[str, Any]:
    path = _resolved_file(path, "artifact")
    return {
        "path": str(path),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def reduced_pairs(P: int, Q: int) -> Iterable[tuple[int, int]]:
    """Yield the declared reduced rectangle in stable p,q order."""

    for p in range(1, P + 1):
        for q in range(1, Q + 1):
            if math.gcd(p, q) == 1:
                yield p, q


def estimated_work(p: int, q: int, N: int, D: int, search_mode: str) -> int:
    """Count full numerator-loop work plus an admissible-trial surcharge."""

    limits = (min(N, (p * d - 1) // q) for d in range(1, D + 1))
    if search_mode == "canonical_positive_u_positive_y":
        full_loop = D * N
        admissible = sum(limits)
        return full_loop + admissible
    if search_mode == "audit_signed_u_both_y":
        full_loop = D * (2 * N + 1)
        admissible = sum(1 + 2 * limit for limit in limits)
        return full_loop + admissible
    raise ManifestError("unrecognized search_mode")


def balanced_assignments(
    P: int, Q: int, N: int, D: int, search_mode: str
) -> list[dict[str, Any]]:
    """Assign jobs by deterministic longest-processing-time-first scheduling."""

    jobs = [
        {"p": p, "q": q, "estimated_work": estimated_work(p, q, N, D, search_mode)}
        for p, q in reduced_pairs(P, Q)
    ]
    jobs.sort(key=lambda item: (-item["estimated_work"], item["p"], item["q"]))
    heap: list[tuple[int, int]] = [(0, lane_id) for lane_id in range(LANE_COUNT)]
    heapq.heapify(heap)
    lanes: list[list[dict[str, int]]] = [[] for _ in range(LANE_COUNT)]
    weights = [0] * LANE_COUNT
    for job in jobs:
        weight, lane_id = heapq.heappop(heap)
        lanes[lane_id].append(job)
        weight += job["estimated_work"]
        weights[lane_id] = weight
        heapq.heappush(heap, (weight, lane_id))
    return [
        {
            "lane_id": lane_id,
            "estimated_weight": weights[lane_id],
            "specializations": lanes[lane_id],
        }
        for lane_id in range(LANE_COUNT)
    ]


def balance_record(lanes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    weights = [_strict_int(lane["estimated_weight"], "estimated_weight", 0) for lane in lanes]
    minimum = min(weights)
    maximum = max(weights)
    applicable = minimum > 0
    ratio = None if not applicable else f"{maximum / minimum:.12f}"
    passes = not applicable or (
        maximum * BALANCE_DENOMINATOR <= minimum * BALANCE_NUMERATOR
    )
    return {
        "min_lane_weight": minimum,
        "max_lane_weight": maximum,
        "max_min_ratio": ratio,
        "ratio_threshold": f"{BALANCE_NUMERATOR / BALANCE_DENOMINATOR:.2f}",
        "threshold_applicable": applicable,
        "threshold_pass": passes,
    }


def oeis_redundancy_gate(P: int, Q: int, D: int) -> dict[str, Any]:
    """Return the exact squared form of the A046881 lower-bound gate.

    With ``B = 2*sqrt(10)*Q*D^2*(P+Q)^(3/2)``, squaring gives
    ``B^2 = K = 40*Q^2*D^4*(P+Q)^3``.  Therefore
    ``2*B^5 > 10^33`` is exactly equivalent to
    ``4*K^5 > 10^66``; no floating-point approximation is used.
    """

    B_squared = 40 * Q**2 * D**4 * (P + Q) ** 3
    left_squared = 4 * B_squared**5
    threshold_squared = 10**66
    passes = left_squared > threshold_squared
    return {
        "source": "OEIS A046881; modified 2026-07-19; recorded lower bound >10^33",
        "source_class": "EXTERNAL_STATUS_GATE_NOT_A_SEARCH_CERTIFICATE",
        "verification_status": "SOURCE_BASED_UNVERIFIED_ON_PAGE",
        "formal_conjectures_snapshot_prefix": "main@b8b5208",
        "bound_formula": "B=2*sqrt(10)*Q*D^2*(P+Q)^(3/2)",
        "exact_pass_inequality": "4*(B_squared)^5>10^66",
        "inputs": {"P": P, "Q": Q, "D": D},
        "B_squared": str(B_squared),
        "twice_B_fifth_squared": str(left_squared),
        "known_lower_bound_squared": str(threshold_squared),
        "status": "PASS" if passes else "ROUTE_KILL_REDUNDANT_BOX",
        "passes": passes,
    }


def assignment_digest(specializations: Sequence[Mapping[str, Any]]) -> str:
    return sha256_bytes(canonical_bytes(list(specializations)))


def lane_tsv_bytes(
    campaign_id: str,
    deadline: str,
    search_mode: str,
    lane: Mapping[str, Any],
    bounds: Mapping[str, int],
    digest: str,
) -> bytes:
    specializations = lane["specializations"]
    lines = [
        "Q5_TORSOR_LANE_V1",
        f"campaign_id\t{campaign_id}",
        f"deadline\t{deadline}",
        f"search_mode\t{search_mode}",
        f"lane_id\t{lane['lane_id']}",
        f"lane_count\t{LANE_COUNT}",
        f"P\t{bounds['P']}",
        f"Q\t{bounds['Q']}",
        f"N\t{bounds['N']}",
        f"D\t{bounds['D']}",
        f"assignment_sha256\t{digest}",
        f"count\t{len(specializations)}",
        "p\tq\testimated_work",
    ]
    lines.extend(
        f"{job['p']}\t{job['q']}\t{job['estimated_work']}"
        for job in specializations
    )
    return ("\n".join(lines) + "\n").encode("ascii")


def _worker_command(
    worker_kind: str,
    artifacts: Mapping[str, Mapping[str, Any]],
    lane_file: Path,
    lane_id: int,
    result_path: Path,
) -> list[str]:
    if worker_kind == "native":
        prefix = [artifacts["worker"]["path"]]
    elif worker_kind == "python":
        prefix = [artifacts["python_interpreter"]["path"], artifacts["worker"]["path"]]
    else:
        raise ManifestError("worker_kind must be native or python")
    return prefix + [
        "--lane-file",
        str(lane_file),
        "--lane-id",
        str(lane_id),
        "--threads",
        "1",
        "--result",
        str(result_path),
    ]


def build_manifest(
    *,
    output: Path,
    lane_config_dir: Path,
    run_dir: Path,
    campaign_id: str,
    mode: str,
    search_mode: str,
    P: int,
    Q: int,
    N: int,
    D: int,
    deadline: str,
    worker: Path,
    worker_source: Path,
    worker_kind: str,
    scalar_verifier: Path,
    independent_verifier: Path,
    supervisor: Path,
    python_interpreter: Path,
) -> dict[str, Any]:
    """Create lane TSVs followed by an atomic manifest commit."""

    if CAMPAIGN_RE.fullmatch(campaign_id) is None:
        raise ManifestError("campaign_id must match [A-Za-z0-9][A-Za-z0-9_.-]{0,127}")
    if mode not in MODES:
        raise ManifestError(f"mode must be one of {MODES}")
    if search_mode not in SEARCH_MODES:
        raise ManifestError(f"search_mode must be one of {SEARCH_MODES}")
    if mode == "SELECTED_MAIN" and search_mode != "canonical_positive_u_positive_y":
        raise ManifestError(
            "SELECTED_MAIN requires canonical_positive_u_positive_y"
        )
    P = _strict_int(P, "P", 1)
    Q = _strict_int(Q, "Q", 1)
    N = _strict_int(N, "N", 0)
    D = _strict_int(D, "D", 1)
    output = output.resolve()
    lane_config_dir = lane_config_dir.resolve()
    run_dir = run_dir.resolve()
    deadline_value = parse_deadline(deadline)
    created = datetime.now(timezone.utc)
    if deadline_value <= created:
        raise ManifestError("deadline must be in the future")
    if deadline_value - created > MAX_DURATION:
        raise ManifestError("deadline may be at most eight hours after manifest creation")

    artifacts: dict[str, dict[str, Any]] = {
        "worker": artifact_record(worker),
        "worker_source": artifact_record(worker_source),
        "scalar_verifier": artifact_record(scalar_verifier),
        "independent_verifier": artifact_record(independent_verifier),
        "manifest_tool": artifact_record(Path(__file__)),
        "supervisor": artifact_record(supervisor),
        "python_interpreter": artifact_record(python_interpreter),
    }
    bounds = {"P": P, "Q": Q, "N": N, "D": D}
    lanes = balanced_assignments(P, Q, N, D, search_mode)
    balance = balance_record(lanes)
    redundancy_gate = oeis_redundancy_gate(P, Q, D)
    if balance["threshold_applicable"] and not balance["threshold_pass"]:
        raise ManifestError(
            "LPT assignment exceeds the 1.25 max/min balance threshold; "
            "do not launch this rectangle"
        )
    if mode == "SELECTED_MAIN" and not redundancy_gate["passes"]:
        raise ManifestError(
            "SELECTED_MAIN box is route-killed by the source-based OEIS "
            "redundancy gate"
        )

    lane_files: list[tuple[Path, bytes]] = []
    lane_records: list[dict[str, Any]] = []
    for lane in lanes:
        lane_id = lane["lane_id"]
        digest = assignment_digest(lane["specializations"])
        lane_file = (lane_config_dir / f"lane_{lane_id:02d}.tsv").resolve()
        result_path = (run_dir / f"lane_{lane_id:02d}.result.json").resolve()
        tsv = lane_tsv_bytes(
            campaign_id, utc_text(deadline_value), search_mode, lane, bounds, digest
        )
        lane_files.append((lane_file, tsv))
        lane_records.append(
            {
                **lane,
                "assignment_sha256": digest,
                "lane_file": {
                    "path": str(lane_file),
                    "size": len(tsv),
                    "sha256": sha256_bytes(tsv),
                },
                "command": _worker_command(
                    worker_kind, artifacts, lane_file, lane_id, result_path
                ),
                "result_path": str(result_path),
            }
        )

    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": KIND,
        "mode": mode,
        "campaign_id": campaign_id,
        "search_mode": search_mode,
        "created_utc": utc_text_precise(created),
        "deadline": utc_text(deadline_value),
        "max_runtime_seconds": int(MAX_DURATION.total_seconds()),
        "bounds": bounds,
        "lane_count": LANE_COUNT,
        "specialization_count": sum(len(lane["specializations"]) for lane in lanes),
        "assignment_rule": "LPT(full_u_loop_plus_admissible_trials_then_p_then_q,min_weight_then_lane_id)",
        "pruning_contract": PRUNING_CONTRACTS[search_mode],
        "work_estimate": (
            "D*N + sum_d=1..D min(N,floor((p*d-1)/q))"
            if search_mode == "canonical_positive_u_positive_y"
            else "D*(2*N+1) + sum_d=1..D(1+2*min(N,floor((p*d-1)/q)))"
        ),
        "balance": balance,
        "oeis_redundancy_gate": redundancy_gate,
        "worker_kind": worker_kind,
        "run_dir": str(run_dir),
        "manifest_path": str(output),
        "thread_environment": THREAD_ENVIRONMENT,
        "artifacts": artifacts,
        "lanes": lane_records,
    }
    envelope = {
        "payload_sha256": sha256_bytes(canonical_bytes(payload)),
        "payload": payload,
    }

    if output.exists():
        raise ManifestError(f"refusing to overwrite existing manifest {output}")
    for lane_file, _ in lane_files:
        if lane_file.exists():
            raise ManifestError(f"refusing to overwrite existing lane file {lane_file}")
    for lane_file, data in lane_files:
        atomic_write_bytes(lane_file, data)
    atomic_write_json(output, envelope)
    return envelope


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read strict manifest {path}: {exc}") from exc


def _require_keys(value: Mapping[str, Any], expected: set[str], name: str) -> None:
    keys = set(value)
    if keys != expected:
        raise ManifestError(
            f"{name} keys differ: missing={sorted(expected-keys)}, extra={sorted(keys-expected)}"
        )


def _audit_artifact(record: Any, role: str) -> Path:
    if not isinstance(record, dict):
        raise ManifestError(f"artifact {role} must be an object")
    _require_keys(record, {"path", "size", "sha256"}, f"artifact {role}")
    path_text = record["path"]
    if not isinstance(path_text, str):
        raise ManifestError(f"artifact {role} path must be a string")
    path = _resolved_file(path_text, f"artifact {role}")
    if str(path) != path_text:
        raise ManifestError(f"artifact {role} path is not canonical absolute")
    size = _strict_int(record["size"], f"artifact {role} size", 0)
    digest = record["sha256"]
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        raise ManifestError(f"artifact {role} sha256 is malformed")
    if path.stat().st_size != size or sha256_file(path) != digest:
        raise ManifestError(f"artifact hash drift: {role}")
    return path


def audit_manifest(
    path: Path,
    *,
    expected_digest: str | None = None,
    expected_campaign_id: str | None = None,
) -> dict[str, Any]:
    """Audit canonical digest, artifacts, coverage, balance, TSVs and commands."""

    path = path.resolve()
    envelope = _load_json(path)
    if not isinstance(envelope, dict):
        raise ManifestError("manifest envelope must be an object")
    _require_keys(envelope, {"payload_sha256", "payload"}, "manifest envelope")
    digest = envelope["payload_sha256"]
    payload = envelope["payload"]
    if not isinstance(digest, str) or SHA256_RE.fullmatch(digest) is None:
        raise ManifestError("payload_sha256 is malformed")
    if not isinstance(payload, dict):
        raise ManifestError("payload must be an object")
    recomputed = sha256_bytes(canonical_bytes(payload))
    if recomputed != digest:
        raise ManifestError("manifest payload digest mismatch")
    if expected_digest is not None and digest != expected_digest:
        raise ManifestError("manifest digest differs from the expected launch digest")

    required_payload_keys = {
        "schema_version", "kind", "mode", "campaign_id", "created_utc",
        "search_mode",
        "deadline", "max_runtime_seconds", "bounds", "lane_count",
        "specialization_count", "assignment_rule", "work_estimate", "balance",
        "oeis_redundancy_gate", "pruning_contract",
        "worker_kind", "run_dir", "manifest_path", "thread_environment",
        "artifacts", "lanes",
    }
    _require_keys(payload, required_payload_keys, "payload")
    if payload["schema_version"] != SCHEMA_VERSION or payload["kind"] != KIND:
        raise ManifestError("schema version or kind mismatch")
    if payload["mode"] not in MODES:
        raise ManifestError("unrecognized manifest mode")
    search_mode = payload["search_mode"]
    if search_mode not in SEARCH_MODES:
        raise ManifestError("unrecognized search_mode")
    if payload["mode"] == "SELECTED_MAIN" and search_mode != "canonical_positive_u_positive_y":
        raise ManifestError("SELECTED_MAIN requires canonical_positive_u_positive_y")
    campaign_id = payload["campaign_id"]
    if not isinstance(campaign_id, str) or CAMPAIGN_RE.fullmatch(campaign_id) is None:
        raise ManifestError("campaign_id is malformed")
    if expected_campaign_id is not None and campaign_id != expected_campaign_id:
        raise ManifestError("campaign_id differs from expected launch campaign")
    if payload["manifest_path"] != str(path):
        raise ManifestError("manifest was moved from its hash-pinned path")
    run_dir = _resolved_dir(payload["run_dir"])
    if str(run_dir) != payload["run_dir"]:
        raise ManifestError("run_dir is not canonical absolute")
    created = parse_deadline(payload["created_utc"])
    deadline = parse_deadline(payload["deadline"])
    if deadline <= created or deadline - created > MAX_DURATION:
        raise ManifestError("declared campaign duration is invalid")
    if payload["max_runtime_seconds"] != int(MAX_DURATION.total_seconds()):
        raise ManifestError("max_runtime_seconds must be 28800")

    bounds = payload["bounds"]
    if not isinstance(bounds, dict):
        raise ManifestError("bounds must be an object")
    _require_keys(bounds, {"P", "Q", "N", "D"}, "bounds")
    P = _strict_int(bounds["P"], "P", 1)
    Q = _strict_int(bounds["Q"], "Q", 1)
    N = _strict_int(bounds["N"], "N", 0)
    if payload["pruning_contract"] != PRUNING_CONTRACTS[search_mode]:
        raise ManifestError("search-mode pruning contract drift")
    D = _strict_int(bounds["D"], "D", 1)
    if payload["lane_count"] != LANE_COUNT:
        raise ManifestError("lane_count must be exactly 64")
    if payload["assignment_rule"] != "LPT(full_u_loop_plus_admissible_trials_then_p_then_q,min_weight_then_lane_id)":
        raise ManifestError("assignment rule drift")
    expected_formula = (
        "D*N + sum_d=1..D min(N,floor((p*d-1)/q))"
        if search_mode == "canonical_positive_u_positive_y"
        else "D*(2*N+1) + sum_d=1..D(1+2*min(N,floor((p*d-1)/q)))"
    )
    if payload["work_estimate"] != expected_formula:
        raise ManifestError("work estimate drift")
    if payload["thread_environment"] != THREAD_ENVIRONMENT:
        raise ManifestError("single-thread environment drift")
    worker_kind = payload["worker_kind"]
    if worker_kind not in ("native", "python"):
        raise ManifestError("worker_kind must be native or python")

    artifacts = payload["artifacts"]
    if not isinstance(artifacts, dict):
        raise ManifestError("artifacts must be an object")
    expected_roles = {
        "worker", "worker_source", "scalar_verifier", "independent_verifier",
        "manifest_tool", "supervisor", "python_interpreter",
    }
    _require_keys(artifacts, expected_roles, "artifacts")
    for role in sorted(expected_roles):
        _audit_artifact(artifacts[role], role)

    expected_lanes = balanced_assignments(P, Q, N, D, search_mode)
    expected_balance = balance_record(expected_lanes)
    if payload["balance"] != expected_balance:
        raise ManifestError("balance record mismatch")
    if expected_balance["threshold_applicable"] and not expected_balance["threshold_pass"]:
        raise ManifestError("max/min estimated lane weight exceeds 1.25")
    expected_gate = oeis_redundancy_gate(P, Q, D)
    if payload["oeis_redundancy_gate"] != expected_gate:
        raise ManifestError("OEIS redundancy gate record mismatch")
    if payload["mode"] == "SELECTED_MAIN" and not expected_gate["passes"]:
        raise ManifestError("SELECTED_MAIN box fails the source-based OEIS redundancy gate")
    lanes = payload["lanes"]
    if not isinstance(lanes, list) or len(lanes) != LANE_COUNT:
        raise ManifestError("lanes must contain exactly 64 records")

    seen: set[tuple[int, int]] = set()
    for lane_id, (lane, expected_lane) in enumerate(zip(lanes, expected_lanes)):
        if not isinstance(lane, dict):
            raise ManifestError(f"lane {lane_id} must be an object")
        _require_keys(
            lane,
            {
                "lane_id", "estimated_weight", "specializations",
                "assignment_sha256", "lane_file", "command", "result_path",
            },
            f"lane {lane_id}",
        )
        if lane["lane_id"] != lane_id:
            raise ManifestError("lane IDs must be exactly 0 through 63")
        if lane["estimated_weight"] != expected_lane["estimated_weight"]:
            raise ManifestError(f"lane {lane_id} estimated weight mismatch")
        specializations = lane["specializations"]
        if specializations != expected_lane["specializations"]:
            raise ManifestError(f"lane {lane_id} assignment differs from deterministic LPT")
        for job in specializations:
            pair = (job["p"], job["q"])
            if pair in seen:
                raise ManifestError(f"duplicate specialization {pair}")
            seen.add(pair)
        assignment_sha = assignment_digest(specializations)
        if lane["assignment_sha256"] != assignment_sha:
            raise ManifestError(f"lane {lane_id} assignment digest mismatch")

        lane_file_record = lane["lane_file"]
        if not isinstance(lane_file_record, dict):
            raise ManifestError(f"lane {lane_id} file record must be an object")
        _require_keys(lane_file_record, {"path", "size", "sha256"}, f"lane {lane_id} file")
        lane_file = _resolved_file(lane_file_record["path"], f"lane {lane_id} file")
        expected_tsv = lane_tsv_bytes(
            campaign_id, payload["deadline"], search_mode, lane, bounds, assignment_sha
        )
        actual_tsv = lane_file.read_bytes()
        if (
            str(lane_file) != lane_file_record["path"]
            or len(actual_tsv) != lane_file_record["size"]
            or sha256_bytes(actual_tsv) != lane_file_record["sha256"]
            or actual_tsv != expected_tsv
        ):
            raise ManifestError(f"lane {lane_id} TSV hash/content drift")

        expected_result_path = (run_dir / f"lane_{lane_id:02d}.result.json").resolve()
        if lane["result_path"] != str(expected_result_path):
            raise ManifestError(f"lane {lane_id} result path mismatch")
        expected_command = _worker_command(
            worker_kind, artifacts, lane_file, lane_id, expected_result_path
        )
        if lane["command"] != expected_command:
            raise ManifestError(f"lane {lane_id} single-thread command drift")

    expected_pairs = set(reduced_pairs(P, Q))
    if seen != expected_pairs:
        missing = sorted(expected_pairs - seen)[:10]
        extra = sorted(seen - expected_pairs)[:10]
        raise ManifestError(f"coverage mismatch: missing={missing}, extra={extra}")
    if payload["specialization_count"] != len(expected_pairs):
        raise ManifestError("specialization_count mismatch")
    return envelope


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--lane-config-dir", type=Path, required=True)
    build.add_argument("--run-dir", type=Path, required=True)
    build.add_argument("--campaign-id", required=True)
    build.add_argument("--mode", choices=MODES, required=True)
    for name in ("P", "Q", "N", "D"):
        build.add_argument(f"--{name}", type=int, required=True)
    build.add_argument("--search-mode", choices=SEARCH_MODES, required=True)
    build.add_argument("--deadline", required=True)
    build.add_argument("--worker", type=Path, required=True)
    build.add_argument("--worker-source", type=Path, required=True)
    build.add_argument("--worker-kind", choices=("native", "python"), required=True)
    build.add_argument("--scalar-verifier", type=Path, required=True)
    build.add_argument("--independent-verifier", type=Path, required=True)
    build.add_argument(
        "--supervisor", type=Path, default=Path(__file__).with_name("q5_supervisor.py")
    )
    build.add_argument("--python-interpreter", type=Path, default=Path(sys.executable))

    audit = subparsers.add_parser("audit")
    audit.add_argument("--manifest", type=Path, required=True)
    audit.add_argument("--expected-digest")
    audit.add_argument("--expected-campaign-id")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.action == "build":
            envelope = build_manifest(
                output=args.output,
                lane_config_dir=args.lane_config_dir,
                run_dir=args.run_dir,
                campaign_id=args.campaign_id,
                mode=args.mode,
                P=args.P,
                Q=args.Q,
                search_mode=args.search_mode,
                N=args.N,
                D=args.D,
                deadline=args.deadline,
                worker=args.worker,
                worker_source=args.worker_source,
                worker_kind=args.worker_kind,
                scalar_verifier=args.scalar_verifier,
                independent_verifier=args.independent_verifier,
                supervisor=args.supervisor,
                python_interpreter=args.python_interpreter,
            )
        else:
            envelope = audit_manifest(
                args.manifest,
                expected_digest=args.expected_digest,
                expected_campaign_id=args.expected_campaign_id,
            )
        print(
            json.dumps(
                {
                    "ok": True,
                    "campaign_id": envelope["payload"]["campaign_id"],
                    "payload_sha256": envelope["payload_sha256"],
                    "specialization_count": envelope["payload"]["specialization_count"],
                    "balance": envelope["payload"]["balance"],
                },
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    except ManifestError as exc:
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
