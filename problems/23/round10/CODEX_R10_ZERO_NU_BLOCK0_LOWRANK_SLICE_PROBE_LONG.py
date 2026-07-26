"""Extend the pinned alpha[7]=0 alternating probe from 100 to 1000 steps."""

from __future__ import annotations

from pathlib import Path


SOURCE = (
    Path(__file__).resolve().parent
    / "CODEX_R10_ZERO_NU_BLOCK0_LOWRANK_SLICE_PROBE.py"
)
text = SOURCE.read_text(encoding="utf-8")
old = "for iteration in range(100):"
new = "for iteration in range(1000):"
if text.count(old) != 1:
    raise AssertionError("pinned short probe changed")
namespace = {"__name__": "__main__", "__file__": str(SOURCE)}
exec(compile(text.replace(old, new), str(SOURCE), "exec"), namespace)
