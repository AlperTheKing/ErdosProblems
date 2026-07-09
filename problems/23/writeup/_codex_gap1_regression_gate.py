#!/usr/bin/env python3
"""One-command Gap#1 regression gate.

This wrapper keeps the three mandatory test articles from the lens handoff in
one place:

* the 24-vertex double-star refutes bare support expansion;
* the 11-vertex escaping atom refutes direct no-escaping-at-max-cut;
* C5[t] blow-ups are the tight all-geodesics guardrail;
* the relaxed-cover positive anchors remain exact-verified.

It is not a proof artifact.  It is a fast exact regression guard before
trusting a new banked full-closure lemma.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WRITEUP = ROOT / "problems" / "23" / "writeup"
OUT = ROOT / "tmp" / "codex_gap1_regression_gate.json"


@dataclass(frozen=True)
class Gate:
    name: str
    script: str
    markers: tuple[str, ...]


GATES = (
    Gate(
        name="bare_sse_24_vertex_refuter",
        script="_claude_v3_refute24_doublestar_realized.py",
        markers=(
            "triangle-free: True",
            "HALL at intended: |S| = 9  |E_short(S)| = 8  VIOLATION",
            "intended is a max cut: True",
            "Gamma-min over max cuts = 225",
        ),
    ),
    Gate(
        name="escaping_atom_at_true_max_cut",
        script="_claude_verify_maxcut_escaping.py",
        markers=(
            "VERDICT: tri-free=True all-ell5=True cut-is-MAX=True doorB=True doorM=True h-escaping=True",
            "NoEscapingAtomAtMaxCut is FALSE",
        ),
    ),
    Gate(
        name="c5_3_all_geodesics_tightness",
        script="_claude_c5_3_diag.py",
        markers=(
            "canonical sum-form FAILS",
            "all-geodesic sum-form holds",
            "MAX-FLOW all-geodesics feasible=True",
            "VERDICT: workflow claim (canonical fails, all-geodesics feasible, tight 225) is CONFIRMED",
        ),
    ),
    Gate(
        name="c5_t_vertex_hall_tightness",
        script="_claude_c5t_structure_dump.py",
        markers=(
            "C5[2]  N=10  |M|=4  Gamma=100  N^2=100",
            "VH S=all: 25*4 = 100  vs  N*|V_all| = 10*10 = 100  => slack 0",
            "C5[3]  N=15  |M|=9  Gamma=225  N^2=225",
            "VH S=all: 25*9 = 225  vs  N*|V_all| = 15*15 = 225  => slack 0",
        ),
    ),
    Gate(
        name="rcc_positive_anchors",
        script="_claude_rcc_anchors_gate.py",
        markers=(
            "C5[3]: |S|=9 |F|=36 cover-ok=True external=0",
            "C_25: Door+Base==Demand: 575+25==600 True (TIGHT)",
            "CP11: |S|=3 |F|=12 cover-ok=True external=0",
            "VERDICT: ALL THREE ANCHOR CERTS EXACT-VERIFIED (GPT-Pro Task 1 sound)",
        ),
    ),
)


def run_gate(gate: Gate) -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, str(WRITEUP / gate.script)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    missing = [marker for marker in gate.markers if marker not in output]
    return {
        "name": gate.name,
        "script": str(WRITEUP / gate.script),
        "returncode": proc.returncode,
        "ok": proc.returncode == 0 and not missing,
        "missing_markers": missing,
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
    }


def main() -> int:
    results = [run_gate(gate) for gate in GATES]
    payload = {
        "schema": "codex_gap1_regression_gate_v1",
        "all_ok": all(result["ok"] for result in results),
        "results": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
