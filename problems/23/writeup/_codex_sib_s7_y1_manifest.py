"""Run the current exact SIB S7 y=1 proof-tree artifacts.

This is a manifest, not a closure certificate.  It executes the exact scripts
that are currently part of the y=1 branch and prints the remaining proof-tree
obligations.  Keeping the inventory executable prevents us from repeatedly
chasing already-closed survivor families.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


SCRIPTS = [
    "_codex_sib_s7_y1_sixface.py",
    "_codex_sib_s7_y1_s123_face.py",
    "_codex_sib_s7_y1_u1_face.py",
    "_codex_sib_s7_y1_s4_fiber.py",
    "_codex_sib_s7_y1_capacity_fibers.py",
    "_codex_sib_s7_y1_x1_capacity_closed.py",
    "_codex_sib_s7_y1_s2s3_capacity_vfibers.py",
    "_codex_sib_s7_y1_u1_capacity_vfibers.py",
    "_codex_sib_s7_y1_low_active_set.py",
    "_codex_sib_s7_y1_xq_quadratic_split.py",
    "_codex_sib_s7_y1_xq_survivors.py",
    "_codex_sib_s7_y1_xq_v1_survivor.py",
    "_codex_sib_s7_y1_xq_u1v1_endpoint.py",
    "_codex_sib_s7_y1_xq_s1_observed.py",
    "_codex_sib_s7_y1_xq_s2s3_observed.py",
    "_codex_sib_s7_y1_xq_s2_impossible_caps.py",
    "_codex_sib_s7_y1_xq_endpoint_inventory.py",
    "_codex_sib_s7_y1_u1_s4_critical_to_seventight.py",
    "_codex_sib_s7_y1_u1_s6s7_survivor.py",
    "_codex_sib_s7_y1_u1_s1_s6_endpoint.py",
    "_codex_sib_s7_y1_u1_v1_alltight_endpoint.py",
    "_codex_sib_s7_y1_s2_survivors.py",
    "_codex_sib_s7_y1_s3_survivor.py",
    "_codex_sib_s7_y1_u1_high_boundary.py",
    "_codex_sib_s7_y1_more_high_boundaries.py",
    "_codex_sib_s7_y1_support_reductions.py",
    "_codex_sib_s7_y1_fj_support_inventory.py",
    "_codex_sib_s7_y1_support_neighborhoods.py",
    "_codex_sib_s7_y1_support_neighbor_reductions.py",
    "_codex_sib_s7_y1_alltight_drop_faces.py",
    "_codex_sib_s7_y1_highA_drop_faces.py",
    "_codex_sib_s7_y1_u1_s7_high_drop_faces.py",
    "_codex_sib_s7_y1_xqA_easy_drop_faces.py",
    "_codex_sib_s7_y1_xq_s5_high_easy_drops.py",
    "_codex_sib_s7_y1_xq_s5_high_drop_a1.py",
    "_codex_sib_s7_y1_xq_s5_high_drop_s3.py",
    "_codex_sib_s7_y1_xq_s5_high_drop_s1.py",
    "_codex_sib_s7_y1_xq_s5_high_drop_u1.py",
    "_codex_sib_s7_y1_xqB_drop_faces.py",
    "_codex_sib_s7_y1_xqA_drop_s3.py",
    "_codex_sib_s7_y1_xqA_drop_f1.py",
    "_codex_sib_s7_y1_xqA_drop_u1.py",
]


OPEN_OBLIGATIONS = [
    "Full y=1 capacity critical-leaf exclusion beyond observed survivor families.",
    "Full x=q endpoint coverage theorem beyond the observed exact-positive/infeasible inventory.",
    "A proof that the restricted active-set survivor inventory covers every y=1 capacity branch.",
    "The other refined endpoint faces outside y=1 after S7 y=1 is closed.",
]


def main() -> None:
    for script in SCRIPTS:
        path = ROOT / script
        if not path.exists():
            raise FileNotFoundError(path)
        print(f"RUN-MANIFEST {script}", flush=True)
        proc = subprocess.run(
            [sys.executable, str(path)],
            cwd=ROOT.parents[2],
            check=True,
            text=True,
            capture_output=True,
            timeout=60,
        )
        lines = [line for line in proc.stdout.splitlines() if line.strip()]
        if not lines or not lines[-1].startswith("PASS"):
            raise AssertionError(f"{script} did not end in PASS output: {proc.stdout!r}")
        print(f"PASS-MANIFEST {script}: {lines[-1]}")

    print("OPEN:")
    for item in OPEN_OBLIGATIONS:
        print(f"- {item}")


if __name__ == "__main__":
    main()


