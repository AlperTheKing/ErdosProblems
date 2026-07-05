#!/usr/bin/env python3
"""Audit current EQ CERT-2 artifacts without promoting float evidence.

This script is intentionally conservative.  It records the exact falsifier
search state and classifies LP/row-generation artifacts by their own exact
acceptance fields.  A numerical LP success is reported as an oracle attempt,
not as a certificate, unless the artifact also contains the exact rational
residual gate used by the producer script.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
from pathlib import Path
from typing import Any


ACCEPTED_FALSIFIER_SCHEMAS = {
    "eq_cert2_chart_falsifier_bound4_aggregate_v1",
    "eq_cert2_add3b_chart_falsifier_v2",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a JSON object")
    return data


def is_zero_string(value: Any) -> bool:
    if value is None:
        return False
    return str(value).strip() == "0"


def audit_falsifier(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
    }
    if not path.exists():
        info.update({"ok": False, "reason": "missing"})
        return info

    try:
        data = load_json(path)
    except Exception as exc:  # pragma: no cover - diagnostic path
        info.update({"ok": False, "reason": f"json_error: {exc}"})
        return info

    schema = data.get("schema")
    charts = data.get("charts") or []
    chart_hits = [c.get("hit") for c in charts if isinstance(c, dict)]
    total_checked = 0
    total_feasible = 0
    best_zero_count = 0
    for c in charts:
        if not isinstance(c, dict):
            continue
        exhaustive = c.get("exhaustive") or {}
        random_part = c.get("random") or {}
        total_checked += int(exhaustive.get("checked") or 0)
        total_checked += int(random_part.get("checked") or 0)
        total_feasible += int(exhaustive.get("feasible") or 0)
        total_feasible += int(random_part.get("feasible") or 0)
        best = exhaustive.get("best") or c.get("best") or {}
        if is_zero_string(best.get("P_EQ")):
            best_zero_count += 1

    top_hit_clean = data.get("hit") is None
    chart_hits_clean = all(hit is None for hit in chart_hits)
    schema_ok = schema in ACCEPTED_FALSIFIER_SCHEMAS
    ok = bool(schema_ok and top_hit_clean and chart_hits_clean)
    info.update(
        {
            "schema": schema,
            "sha256": sha256_file(path),
            "ok": ok,
            "schema_ok": schema_ok,
            "top_hit_clean": top_hit_clean,
            "chart_hits_clean": chart_hits_clean,
            "chart_count": len(charts),
            "best_zero_chart_count": best_zero_count,
            "total_checked": total_checked,
            "total_feasible": total_feasible,
        }
    )
    if not ok:
        info["reason"] = "schema_or_hit_failure"
    return info


def last_history_event(data: dict[str, Any]) -> dict[str, Any] | None:
    history = data.get("history")
    if isinstance(history, list) and history:
        last = history[-1]
        if isinstance(last, dict):
            return {
                k: last.get(k)
                for k in (
                    "iteration",
                    "oracle",
                    "rows",
                    "columns",
                    "lp_status",
                    "lp_message",
                    "success",
                    "violated",
                    "worst_residual",
                    "float_nonzero",
                )
                if k in last
            }
    return None


def classify_candidate(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
    }
    if not path.exists():
        out.update({"classification": "missing", "exact_certificate": False})
        return out

    try:
        data = load_json(path)
    except Exception as exc:  # pragma: no cover - diagnostic path
        out.update(
            {
                "classification": "json_error",
                "exact_certificate": False,
                "error": str(exc),
            }
        )
        return out

    schema = data.get("schema")
    out.update({"schema": schema, "sha256": sha256_file(path)})

    if schema == "eq_cert2_chart_rowgen_v1":
        exact = data.get("exact") or {}
        final = data.get("final")
        exact_ok = bool(final == "EXACT_OK" and exact.get("ok") is True)
        out.update(
            {
                "classification": "exact_rowgen" if exact_ok else "rowgen_no_exact_cert",
                "exact_certificate": exact_ok,
                "chart": data.get("chart"),
                "final": final,
                "exact_ok": bool(exact.get("ok")) if exact else False,
                "history_len": len(data.get("history") or []),
                "last_history_event": last_history_event(data),
            }
        )
        if exact:
            out["exact_gate"] = {
                "max_denominator": exact.get("max_denominator"),
                "residual_min_coeff": exact.get("residual_min_coeff"),
                "seed_residual": exact.get("seed_residual"),
            }
        return out

    if schema == "eq_cert2_chart_bernstein_lp_v1":
        exact_ok = bool(data.get("exact_ok") is True)
        out.update(
            {
                "classification": "exact_lp" if exact_ok else "lp_no_exact_cert",
                "exact_certificate": exact_ok,
                "chart": data.get("chart"),
                "success": bool(data.get("success")),
                "exact_ok": exact_ok,
                "lp_status": data.get("lp_status"),
                "lp_message": data.get("lp_message"),
                "float_nonzero": data.get("float_nonzero"),
            }
        )
        if exact_ok:
            out["exact_gate"] = {
                "max_denominator": data.get("max_denominator"),
                "residual_min_coeff": data.get("residual_min_coeff"),
                "seed_residual": data.get("seed_residual"),
            }
        else:
            check = data.get("last_exact_check") or {}
            if check:
                out["last_exact_check"] = {
                    "residual_min_coeff": check.get("residual_min_coeff"),
                    "seed_residual": check.get("seed_residual"),
                    "negative_terms_count": len(check.get("negative_terms") or []),
                }
        return out

    out.update(
        {
            "classification": "unrecognized_schema",
            "exact_certificate": False,
        }
    )
    return out


def expand_candidates(values: list[str], patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    seen: set[str] = set()
    for value in values:
        p = Path(value)
        key = str(p)
        if key not in seen:
            paths.append(p)
            seen.add(key)
    for pattern in patterns:
        for match in sorted(glob.glob(pattern)):
            p = Path(match)
            key = str(p)
            if key not in seen:
                paths.append(p)
                seen.add(key)
    return paths


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--falsifier",
        default="tmp/eq_cert2_chart_falsifier_bound4_all_v2.json",
    )
    ap.add_argument("--candidate", action="append", default=[])
    ap.add_argument("--candidate-glob", action="append", default=[])
    ap.add_argument("--summary", default="tmp/eq_cert2_artifact_audit_v1.json")
    args = ap.parse_args()

    falsifier = audit_falsifier(Path(args.falsifier))
    candidates = [classify_candidate(p) for p in expand_candidates(args.candidate, args.candidate_glob)]
    exact_candidates = [c for c in candidates if c.get("exact_certificate") is True]
    numeric_oracle_attempts = [
        c
        for c in candidates
        if c.get("schema")
        in {
            "eq_cert2_chart_rowgen_v1",
            "eq_cert2_chart_bernstein_lp_v1",
        }
        and c.get("exact_certificate") is not True
    ]

    if not falsifier.get("ok"):
        status = "FAIL_FALSIFIER_AUDIT"
    elif exact_candidates:
        status = "PASS_EXACT_CERTS_PRESENT"
    else:
        status = "OPEN_NO_EXACT_CERT"

    out = {
        "schema": "eq_cert2_artifact_audit_v1",
        "acceptance_policy": "exact rational gates only; float LP success is non-certifying",
        "status": status,
        "falsifier": falsifier,
        "candidate_count": len(candidates),
        "exact_certificate_count": len(exact_candidates),
        "numeric_oracle_attempt_count": len(numeric_oracle_attempts),
        "candidates": candidates,
    }
    Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(status, args.summary)


if __name__ == "__main__":
    main()
