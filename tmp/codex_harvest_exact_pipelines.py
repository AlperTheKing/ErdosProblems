from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def tag_from_pipeline(path: Path) -> str:
    prefix = "eq_odl1_rung2_pipeline_"
    name = path.name
    if not name.startswith(prefix) or not name.endswith(".json"):
        raise ValueError(path)
    return name[len(prefix):-5]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="eq_odl1_rung2_pipeline_*_claude_cpp.json")
    ap.add_argument("--ledger-out", type=Path, required=True)
    ap.add_argument("--pending-prefix", type=int, default=108)
    args = ap.parse_args()

    made = []
    skipped = []
    for pipe in sorted(Path("tmp").glob(args.glob)):
        try:
            data = json.loads(pipe.read_text(encoding="utf-8"))
        except Exception as exc:
            skipped.append({"pipeline": str(pipe), "reason": f"read_error:{exc}"})
            continue
        if data.get("exact_ok") is not True:
            skipped.append({
                "pipeline": str(pipe),
                "reason": "not_exact_ok",
                "exact_ok": data.get("exact_ok"),
                "neg_res": data.get("check_summary", {}).get("full_negative_residual_count"),
                "neg_sol": data.get("check_summary", {}).get("solution_negative_count"),
            })
            continue
        tag = tag_from_pipeline(pipe)
        out = Path("tmp") / f"eq_odl1_rung2_source_certificate_manifest_{tag}.json"
        if out.exists():
            skipped.append({"pipeline": str(pipe), "reason": "manifest_exists", "manifest": str(out)})
            continue
        proc = subprocess.run(
            [
                sys.executable,
                "tmp/codex_manifest_from_pipeline.py",
                "--pipeline",
                str(pipe),
                "--out",
                str(out),
            ],
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            skipped.append({"pipeline": str(pipe), "reason": "manifest_failed", "stderr": proc.stderr[-1000:]})
            continue
        made.append(json.loads(proc.stdout))

    proc = subprocess.run(
        [
            sys.executable,
            "tmp/rebuild_current_chart_ledger_codex.py",
            "--out",
            str(args.ledger_out),
            "--pending-prefix",
            str(args.pending_prefix),
        ],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-2000:])
    ledger = json.loads(proc.stdout)
    print(json.dumps({"made": made, "skipped": skipped, "ledger": ledger}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
