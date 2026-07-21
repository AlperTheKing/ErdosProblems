"""Check the captured eclib/mwrank proof gate for the ACE curve."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


CURVE = "[0,2568913,0,1535181310080,59427518261760000]"
A2 = 2_568_913
A4 = 1_535_181_310_080
A6 = 59_427_518_261_760_000


def main(run_dir_arg: str) -> int:
    run_dir = Path(run_dir_arg)
    stdout = (run_dir / "mwrank_stdout.txt").read_text(encoding="utf-8")
    stderr = (run_dir / "mwrank_stderr.txt").read_text(encoding="utf-8")
    result = json.loads((run_dir / "run_result.json").read_text(encoding="utf-8-sig"))
    combined = stdout + "\n" + stderr

    required = {
        "curve": f"Curve {CURVE}",
        "rank": "Rank = 4",
        "automatic_saturation": "Saturating (with bound = -1)...done:",
        "saturation_result": "points were already saturated.",
        "unconditional_basis": (
            "The rank and full Mordell-Weil basis have been determined "
            "unconditionally."
        ),
    }
    missing = [name for name, marker in required.items() if marker not in combined]
    forbidden_patterns = [
        r"saturation possibly incomplete",
        r"Failed to saturate",
        r"p-saturation failed",
        r"Failed to compute rank",
        r"NOT on curve",
        r"timeout",
    ]
    forbidden = [
        pattern
        for pattern in forbidden_patterns
        if re.search(pattern, combined, flags=re.IGNORECASE)
    ]

    point_pattern = re.compile(
        r"Generator\s+(\d+)\s+is\s+\[(-?\d+):(-?\d+):(-?\d+)\]"
    )
    matches = point_pattern.findall(combined)
    generators = []
    point_checks = []
    for label, x_text, y_text, z_text in matches:
        x, y, z = int(x_text), int(y_text), int(z_text)
        on_curve = (
            y * y * z
            == x**3 + A2 * x * x * z + A4 * x * z * z + A6 * z**3
        )
        generators.append([x, y, z])
        point_checks.append({"label": int(label), "on_curve": on_curve})

    generator_gate = (
        [item["label"] for item in point_checks] == [1, 2, 3, 4]
        and all(item["on_curve"] for item in point_checks)
    )
    process_gate = result.get("completed") is True and result.get("exit_code") == 0
    valid = not missing and not forbidden and generator_gate and process_gate
    report = {
        "valid": valid,
        "process_gate": process_gate,
        "missing_markers": missing,
        "forbidden_markers": forbidden,
        "generator_gate": generator_gate,
        "generators": generators,
        "point_checks": point_checks,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: check_mwrank_certificate.py RUN_DIR")
    raise SystemExit(main(sys.argv[1]))
