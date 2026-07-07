from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def line_count(path: Path) -> int:
    with path.open("rb") as handle:
        return sum(1 for _ in handle)


def rel(path: str | Path) -> str:
    p = Path(path)
    try:
        return str(p.relative_to(Path.cwd()))
    except ValueError:
        return str(p)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    pipe = json.loads(args.pipeline.read_text(encoding="utf-8"))
    artifacts = pipe["artifacts"]
    check = pipe["check_summary"]
    tag = pipe["tag"]
    modular = Path(f"tmp/eq_odl1_rung2_modular_{tag}.json")

    manifest = {
        "schema": "eq_odl1_rung2_source_certificate_manifest_v1",
        "certificate_kind": "source",
        "chart": pipe["chart"],
        "dominant": pipe["dominant"],
        "band": pipe["band"],
        "support": pipe["support"],
        "exact_ok": pipe["exact_ok"],
        "core": rel(artifacts["core"]),
        "modular_summary": rel(modular),
        "modular_summary_sha256": sha256(modular),
        "solution_jsonl": rel(artifacts["source_solution"]),
        "solution_jsonl_sha256": sha256(Path(artifacts["source_solution"])),
        "solution_jsonl_records": line_count(Path(artifacts["source_solution"])),
        "check_summary": rel(artifacts["check"]),
        "check_summary_sha256": sha256(Path(artifacts["check"])),
        "columns_checked": check["columns"],
        "nonzero_source_columns": check["nonzero_source_columns"],
        "solution_negative_count": check["solution_negative_count"],
        "full_min_residual": check["full_min_residual"],
        "full_negative_residual_count": check["full_negative_residual_count"],
        "full_zero_residual_count": check["full_zero_residual_count"],
        "target_beta_json": check.get("target_beta_json"),
        "target_beta_json_sha256": None,
        "target_beta_mode": check.get("target_beta_mode"),
        "target_beta_nonzero_count": check.get("target_beta_nonzero_count"),
        "repair": None,
        "native_solver": "tmp/codex_mod_prime_solve.exe",
        "native_wrapper": "tmp/codex_modular_solve_cpp_parallel.py",
        "verification_command": (
            "python -B problems/23/writeup/_codex_eq_odl1_rung2_source_solution_check.py "
            f"--chart {pipe['chart']} --dominant {pipe['dominant']} "
            f"--band {pipe['band']} --support {pipe['support']} "
            f"--solution {rel(artifacts['source_solution'])} --summary {rel(artifacts['check'])}"
        ),
    }

    args.out.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {
                "manifest": str(args.out),
                "sha256": sha256(args.out),
                "exact_ok": manifest["exact_ok"],
                "records": manifest["solution_jsonl_records"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
