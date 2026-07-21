#!/usr/bin/env python3
"""Transactionally construct a fixed-path Q5 phase manifest.

This helper prepares files only; it cannot launch a worker or supervisor.  A
phase is built completely in a same-parent staging directory, all embedded
paths are rebound to the fixed canonical destination, the tranche state is
rechecked byte-for-byte, and one directory rename commits the result.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import q5_manifest as manifest_lib


TRANCHE_ID = "q5-eight-hour-tranche-v1"
ENGINE_DIR = Path(__file__).resolve().parent
PHASES = ("A", "B", "C", "D", "MAIN")
PILOT_SPECS: dict[str, dict[str, Any]] = {
    "A": {
        "bounds": {"P": 10, "Q": 10, "N": 10, "D": 10},
        "search_mode": "audit_signed_u_both_y",
        "limit_seconds": 120,
        "expected_state": "READY_A",
    },
    "B": {
        "bounds": {"P": 47, "Q": 47, "N": 47, "D": 47},
        "search_mode": "canonical_positive_u_positive_y",
        "limit_seconds": 120,
        "expected_state": "READY_B",
    },
    "C": {
        "bounds": {"P": 256, "Q": 256, "N": 128, "D": 128},
        "search_mode": "canonical_positive_u_positive_y",
        "limit_seconds": 600,
        "expected_state": "READY_C",
    },
    "D": {
        "bounds": {"P": 512, "Q": 512, "N": 192, "D": 192},
        "search_mode": "canonical_positive_u_positive_y",
        "limit_seconds": 1800,
        "expected_state": "READY_D",
    },
}


class TransactionError(RuntimeError):
    """The fixed-path manifest transaction is not safe to commit."""


Clock = Callable[[], datetime]


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json_bytes(path: Path, name: str) -> tuple[dict[str, Any], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TransactionError(f"cannot load {name} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TransactionError(f"{name} must be a JSON object")
    return value, raw


def _parse_utc(value: Any, name: str) -> datetime:
    if not isinstance(value, str):
        raise TransactionError(f"{name} must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TransactionError(f"{name} is not ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TransactionError(f"{name} lacks a UTC offset")
    return parsed.astimezone(timezone.utc)


def _utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _fixed_paths(engine_dir: Path, phase: str) -> dict[str, Path]:
    tranche = engine_dir.resolve() / "logs" / TRANCHE_ID
    base = tranche / ("main" if phase == "MAIN" else f"pilot_{phase}")
    return {
        "tranche": tranche,
        "state": tranche / "state.json",
        "plan": tranche / "plan.json",
        "base": base,
        "manifest": base / "manifest.json",
        "lanes": base / "lanes",
        "run": base / "run",
    }


def _campaign_id(phase: str) -> str:
    return "q5-tranche-v1-main" if phase == "MAIN" else f"q5-tranche-v1-pilot-{phase}"


def _validate_context(
    *,
    phase: str,
    selected_h: int | None,
    engine_dir: Path,
    now: datetime,
) -> tuple[dict[str, Path], dict[str, Any], bytes, dict[str, Any], dict[str, Any]]:
    if phase not in PHASES:
        raise TransactionError(f"phase must be one of {PHASES}")
    paths = _fixed_paths(engine_dir, phase)
    state, state_bytes = _load_json_bytes(paths["state"], "tranche state")
    plan, plan_bytes = _load_json_bytes(paths["plan"], "tranche plan")
    if (
        state.get("schema_version") != 1
        or state.get("kind") != "Q5_TRANCHE_STATE"
        or state.get("tranche_id") != TRANCHE_ID
    ):
        raise TransactionError("tranche state identity mismatch")
    if (
        plan.get("schema_version") != 1
        or plan.get("kind") != "Q5_TRANCHE_PLAN"
        or plan.get("tranche_id") != TRANCHE_ID
    ):
        raise TransactionError("tranche plan identity mismatch")
    if state.get("persistent_error") is not None:
        raise TransactionError("tranche state carries a persistent error")
    if state.get("plan_sha256") != _sha256(plan_bytes):
        raise TransactionError("tranche plan hash differs from state pin")
    deadline_s = _parse_utc(state.get("s"), "state.s")
    if now.tzinfo is None or now.utcoffset() is None:
        raise TransactionError("clock returned a naive timestamp")
    if now.astimezone(timezone.utc) >= deadline_s:
        raise TransactionError("search deadline S has elapsed")

    campaign = _campaign_id(phase)
    if phase == "MAIN":
        if state.get("phase") != "READY_SELECTION":
            raise TransactionError("MAIN construction requires READY_SELECTION")
        updated = _parse_utc(state.get("updated_utc"), "state.updated_utc")
        if now.astimezone(timezone.utc) > updated + timedelta(seconds=300):
            raise TransactionError("MAIN setup window exceeds 300 seconds from READY_SELECTION")

        if isinstance(selected_h, bool) or not isinstance(selected_h, int):
            raise TransactionError("MAIN construction requires integer --selected-h")
        if selected_h < 48 or selected_h > 512:
            raise TransactionError("selected H is outside the frozen candidate table")
        bounds = {"P": selected_h, "Q": selected_h, "N": selected_h, "D": selected_h}
        spec = {
            "bounds": bounds,
            "search_mode": "canonical_positive_u_positive_y",
            "limit_seconds": None,
            "expected_state": "READY_SELECTION",
        }
        plan_record = plan.get("main")
        expected_record = {
            "campaign_id": campaign,
            "manifest_path": str(paths["manifest"].resolve()),
            "lane_config_dir": str(paths["lanes"].resolve()),
            "run_dir": str(paths["run"].resolve()),
            "deadline": state["s"],
        }
        if not isinstance(plan_record, dict) or any(
            plan_record.get(key) != value for key, value in expected_record.items()
        ):
            raise TransactionError("fixed MAIN paths/deadline differ from tranche plan")
    else:
        if selected_h is not None:
            raise TransactionError("--selected-h is valid only for MAIN")
        spec = dict(PILOT_SPECS[phase])
        if state.get("phase") != spec["expected_state"]:
            raise TransactionError(
                f"Pilot {phase} construction requires {spec['expected_state']}"
            )
        records = plan.get("pilots")
        if not isinstance(records, list):
            raise TransactionError("tranche plan pilots is not an array")
        matches = [record for record in records if isinstance(record, dict) and record.get("name") == phase]
        if len(matches) != 1:
            raise TransactionError(f"tranche plan has no unique Pilot {phase}")
        plan_record = matches[0]
        expected_record = {
            "campaign_id": campaign,
            "bounds": spec["bounds"],
            "search_mode": spec["search_mode"],
            "limit_seconds": spec["limit_seconds"],
            "manifest_path": str(paths["manifest"].resolve()),
            "lane_config_dir": str(paths["lanes"].resolve()),
            "run_dir": str(paths["run"].resolve()),
        }
        if any(plan_record.get(key) != value for key, value in expected_record.items()):
            raise TransactionError(f"Pilot {phase} fixed contract differs from tranche plan")
    return paths, state, state_bytes, plan, spec


def _validate_existing(
    *,
    phase: str,
    paths: Mapping[str, Path],
    spec: Mapping[str, Any],
    state: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        envelope = manifest_lib.audit_manifest(
            paths["manifest"], expected_campaign_id=_campaign_id(phase)
        )
    except manifest_lib.ManifestError as exc:
        raise TransactionError(f"existing fixed manifest is invalid: {exc}") from exc
    payload = envelope["payload"]
    mode = "SELECTED_MAIN" if phase == "MAIN" else "CALIBRATION_ONLY"
    if payload["mode"] != mode or payload["search_mode"] != spec["search_mode"]:
        raise TransactionError("existing fixed manifest mode mismatch")
    if payload["bounds"] != spec["bounds"]:
        raise TransactionError("existing fixed manifest bounds mismatch")
    if (
        payload["manifest_path"] != str(paths["manifest"].resolve())
        or payload["run_dir"] != str(paths["run"].resolve())
    ):
        raise TransactionError("existing fixed manifest path mismatch")
    if phase == "MAIN":
        if payload["deadline"] != state["s"]:
            raise TransactionError("existing MAIN deadline differs from S")
    elif _parse_utc(payload["deadline"], "pilot deadline") > _parse_utc(state["s"], "S"):
        raise TransactionError("existing pilot deadline exceeds S")
    return envelope


def _rebind_paths(value: Any, old_root: str, new_root: str) -> Any:
    if isinstance(value, str):
        return new_root + value[len(old_root) :] if value.startswith(old_root) else value
    if isinstance(value, list):
        return [_rebind_paths(item, old_root, new_root) for item in value]
    if isinstance(value, dict):
        return {key: _rebind_paths(item, old_root, new_root) for key, item in value.items()}
    return value


def build_phase(
    phase: str,
    *,
    selected_h: int | None = None,
    engine_dir: Path = ENGINE_DIR,
    clock: Clock = _now_utc,
) -> dict[str, Any]:
    """Build or idempotently audit one canonical phase manifest."""

    phase = phase.upper()
    now = clock()
    paths, state, state_bytes, _plan, spec = _validate_context(
        phase=phase,
        selected_h=selected_h,
        engine_dir=engine_dir,
        now=now,
    )
    target = paths["base"]
    if target.exists():
        envelope = _validate_existing(
            phase=phase, paths=paths, spec=spec, state=state
        )
        return {
            "ok": True,
            "status": "REUSED",
            "phase": phase,
            "manifest_path": str(paths["manifest"].resolve()),
            "manifest_file_sha256": manifest_lib.sha256_file(paths["manifest"]),
            "manifest_payload_sha256": envelope["payload_sha256"],
        }

    paths["tranche"].mkdir(parents=False, exist_ok=True)
    stale = sorted(paths["tranche"].glob(f".{target.name}.build.*"))
    if stale:
        raise TransactionError(
            "stale manifest staging exists; preserve and inspect it before retry: "
            + ", ".join(str(path) for path in stale)
        )
    staging = paths["tranche"] / f".{target.name}.build.{os.getpid()}.{uuid.uuid4().hex}"
    staging.mkdir(exist_ok=False)
    committed = False
    try:
        deadline_s = _parse_utc(state["s"], "state.s")
        if phase == "MAIN":
            deadline = deadline_s
            mode = "SELECTED_MAIN"
        else:
            deadline = min(
                now.astimezone(timezone.utc) + timedelta(seconds=spec["limit_seconds"]),
                deadline_s,
            )
            mode = "CALIBRATION_ONLY"
        envelope = manifest_lib.build_manifest(
            output=staging / "manifest.json",
            lane_config_dir=staging / "lanes",
            run_dir=staging / "run",
            campaign_id=_campaign_id(phase),
            mode=mode,
            search_mode=spec["search_mode"],
            P=spec["bounds"]["P"],
            Q=spec["bounds"]["Q"],
            N=spec["bounds"]["N"],
            D=spec["bounds"]["D"],
            deadline=_utc_text(deadline),
            worker=engine_dir / "scan_torsor_exact.exe",
            worker_source=engine_dir / "scan_torsor_exact.cpp",
            worker_kind="native",
            scalar_verifier=engine_dir / "verify_certificate.py",
            independent_verifier=engine_dir / "verify_independent.exe",
            supervisor=engine_dir / "q5_supervisor.py",
            python_interpreter=Path(sys.executable),
        )
        payload = copy.deepcopy(envelope["payload"])
        created = _parse_utc(payload["created_utc"], "manifest created_utc")
        if phase != "MAIN":
            exact_deadline = min(created + timedelta(seconds=spec["limit_seconds"]), deadline_s)
            payload["deadline"] = _utc_text(exact_deadline)
        for lane in payload["lanes"]:
            lane_file = staging / "lanes" / f"lane_{lane['lane_id']:02d}.tsv"
            tsv = manifest_lib.lane_tsv_bytes(
                payload["campaign_id"],
                payload["deadline"],
                payload["search_mode"],
                lane,
                payload["bounds"],
                lane["assignment_sha256"],
            )
            manifest_lib.atomic_write_bytes(lane_file, tsv)
            lane["lane_file"]["size"] = len(tsv)
            lane["lane_file"]["sha256"] = manifest_lib.sha256_bytes(tsv)
        old_root = str(staging.resolve())
        new_root = str(target.resolve())
        relocated_payload = _rebind_paths(payload, old_root, new_root)
        if old_root in json.dumps(relocated_payload, ensure_ascii=True):
            raise TransactionError("staging path remains in relocated manifest")
        relocated = {
            "payload_sha256": manifest_lib.sha256_bytes(
                manifest_lib.canonical_bytes(relocated_payload)
            ),
            "payload": relocated_payload,
        }
        manifest_lib.atomic_write_json(staging / "manifest.json", relocated)
        _state_again, state_bytes_again = _load_json_bytes(paths["state"], "tranche state")
        if state_bytes_again != state_bytes:
            raise TransactionError("tranche state changed during manifest construction")
        if phase == "MAIN":
            commit_now = clock()
            if commit_now.tzinfo is None or commit_now.utcoffset() is None:
                raise TransactionError("clock returned a naive timestamp at MAIN commit")
            selection_anchor = _parse_utc(state["updated_utc"], "state.updated_utc")
            if commit_now.astimezone(timezone.utc) > selection_anchor + timedelta(seconds=300):
                raise TransactionError(
                    "MAIN setup window elapsed during manifest construction"
                )

        try:
            os.rename(staging, target)
        except FileExistsError:
            envelope = _validate_existing(
                phase=phase, paths=paths, spec=spec, state=state
            )
            return {
                "ok": True,
                "status": "REUSED_AFTER_RACE",
                "phase": phase,
                "manifest_path": str(paths["manifest"].resolve()),
                "manifest_file_sha256": manifest_lib.sha256_file(paths["manifest"]),
                "manifest_payload_sha256": envelope["payload_sha256"],
            }
        committed = True
        audited = _validate_existing(
            phase=phase, paths=paths, spec=spec, state=state
        )
        return {
            "ok": True,
            "status": "CREATED",
            "phase": phase,
            "manifest_path": str(paths["manifest"].resolve()),
            "manifest_file_sha256": manifest_lib.sha256_file(paths["manifest"]),
            "manifest_payload_sha256": audited["payload_sha256"],
        }
    except manifest_lib.ManifestError as exc:
        raise TransactionError(f"manifest construction failed: {exc}") from exc
    finally:
        if not committed:
            shutil.rmtree(staging, ignore_errors=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build", choices=("build",))
    parser.add_argument("--phase", choices=PHASES, required=True)
    parser.add_argument("--selected-h", type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = build_phase(args.phase, selected_h=args.selected_h)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    except TransactionError as exc:
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
