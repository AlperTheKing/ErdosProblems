#!/usr/bin/env python3
"""Complete the t=6 cut-tight order-20 row: probe 11+9, 12+8, 13+7 (600s)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from probe_cuttight_star_feasibility import probe


def main():
    out = {}
    for l, r in [(11, 9), (12, 8), (13, 7)]:
        out[f"t6:{l}+{r}"] = probe(l, r, 6, time_limit=600.0, workers=8)
        print(f"t6:{l}+{r}: {out[f't6:{l}+{r}']}", flush=True)
    Path(sys.argv[1]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
