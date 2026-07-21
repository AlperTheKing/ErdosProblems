#!/usr/bin/env python3
"""Exact N2 sweep of all connected triangle/square-free graphs, n=8..14."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "exhaustive_n2_n8_9.py"
SPEC = importlib.util.spec_from_file_location("n2base", BASE_PATH)
BASE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BASE)

OUT = HERE / "exhaustive_n2_n8_14_results.json"


def main() -> None:
    t0 = time.time()
    result = {"test": "WOWII144_Candidate_N2_exhaustive_n8_14",
              "generator": "nauty geng 2.8.9 -c -t -f",
              "per_n": {}, "failures": []}
    for n in range(8, 15):
        proc = subprocess.run(
            [str(BASE.GENG), "-c", "-t", "-f", "-q", str(n)],
            capture_output=True, text=True, check=True)
        lines = proc.stdout.split()
        counts = {"connected_triangle_square_free": len(lines),
                  "girth_lt_5": 0, "nonresidual": 0,
                  "residual": 0, "failures": 0}
        for line in lines:
            rec = BASE.check(line)
            tag = rec[0]
            if tag == "skip":
                counts["girth_lt_5"] += 1
            elif tag == "nonresidual":
                counts["nonresidual"] += 1
            else:
                counts["residual"] += 1
                if tag == "fail":
                    counts["failures"] += 1
                    result["failures"].append(rec[1:])
        result["per_n"][str(n)] = counts
        print(n, counts, flush=True)
    result["elapsed_sec"] = round(time.time() - t0, 2)
    encoded = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    OUT.write_bytes(encoded)
    digest = hashlib.sha256(encoded).hexdigest().upper()
    OUT.with_suffix(".json.sha256").write_text(digest + "  " + OUT.name + "\n")
    print("wrote", OUT)
    print("sha256", digest)


if __name__ == "__main__":
    main()
