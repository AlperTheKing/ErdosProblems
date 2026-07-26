"""Run the exact block0 pencil producer only through the index-7 rank gate."""

from __future__ import annotations

import sys
from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parent
    / "CODEX_R10_ZERO_NU_BLOCK0_PSD_EXPOSURE.py"
)
text = SOURCE.read_text(encoding="utf-8")
old_stack = "stacked = np.vstack(psd_pencil).astype(np.int64)"
new_stack = (
    "stacked = np.vstack([matrix for index, matrix in "
    "enumerate(psd_pencil) if index != 7]).astype(np.int64)"
)
old_gate = """    if ranks != [EXPECTED_COMMON_RANK, EXPECTED_COMMON_RANK]:
        raise AssertionError(f"unexpected common ranks {ranks}")
"""
new_gate = """    print(f"EXACT_PENCIL_EXCEPT7_RANKS={ranks}")
    return
"""
if text.count(old_stack) != 1 or text.count(old_gate) != 1:
    raise AssertionError("pinned source text changed")
text = text.replace(old_stack, new_stack).replace(old_gate, new_gate)
sys.argv = [str(SOURCE), "--output", str(SOURCE.with_suffix(".unused.npz"))]
namespace = {"__name__": "__main__", "__file__": str(SOURCE)}
exec(compile(text, str(SOURCE), "exec"), namespace)
