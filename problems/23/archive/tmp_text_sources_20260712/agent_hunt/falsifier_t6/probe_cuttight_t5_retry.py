#!/usr/bin/env python3
"""Retry the UNKNOWN t=5 cut-tight-star cells with a 600s budget each,
to pin the exact t=5 pinch window (feasibility threshold order)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from probe_cuttight_star_feasibility import probe


def main():
    out = {}
    for l, r in [(10, 9), (10, 10), (11, 10)]:
        out[f"t5:{l}+{r}"] = probe(l, r, 5, time_limit=600.0, workers=8)
        print(f"t5:{l}+{r}: {out[f't5:{l}+{r}']}", flush=True)
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
