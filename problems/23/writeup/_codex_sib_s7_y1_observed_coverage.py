"""Observed active-set coverage gate for the SIB S7 y=1 branch.

This script intentionally is NOT a proof certificate.  It reruns the deterministic
basin-scan classifier in `_tmp_y1_active_coverage.py` and requires that every
observed cluster is assigned to an already exact-checked family.

Use: regression guard and coordination artifact.  Remaining proof obligation:
turn this observed inventory into a finite exact FJ/Sturm coverage certificate.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    here = Path(__file__).resolve().parent
    script = here / "_tmp_y1_active_coverage.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=here.parents[2],
        text=True,
        capture_output=True,
        check=True,
    )
    print(proc.stdout, end="")
    assert "PASS active-set coverage scan: all observed clusters classified" in proc.stdout
    print("PASS observed y=1 active-set coverage gate (not a proof certificate)")


if __name__ == "__main__":
    main()
