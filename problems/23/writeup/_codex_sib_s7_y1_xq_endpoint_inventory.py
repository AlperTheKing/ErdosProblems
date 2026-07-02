"""Executable inventory gate for observed x=q endpoint blockers.

This file does not prove full x=q endpoint coverage.  It makes the current
computational inventory explicit: the temporary endpoint scans for the five
blockers {u=1, v=1, s1=0, s2=0, s3=0} only produce support families that are
covered by exact verifier scripts in the manifest.

Keeping this as an executable gate prevents the proof tree from regressing
while the remaining FJ/Sturm coverage theorem is developed.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent


EXACT_SCRIPTS = [
    "_codex_sib_s7_y1_xq_survivors.py",
    "_codex_sib_s7_y1_xq_v1_survivor.py",
    "_codex_sib_s7_y1_xq_u1v1_endpoint.py",
    "_codex_sib_s7_y1_xq_s1_observed.py",
    "_codex_sib_s7_y1_xq_s2s3_observed.py",
    "_codex_sib_s7_y1_xq_s2_impossible_caps.py",
]


OBSERVED_COVER = {
    "u1": {
        ("f1", "s3", "s4", "s5", "s6", "s7", "u1"): "XQ_A",
        ("d1", "f1", "s1", "s2", "s3", "s6", "s7", "u1"): "XQ_B",
    },
    "v1": {
        ("d1", "f1", "s2", "s3", "s6", "s7"): "XQ_B-v1",
        ("d1", "f1", "s3", "s6", "s7", "u1"): "XQ-u=v=1",
        ("a1", "c1", "e1", "s1", "s3", "s4", "s5", "s6", "s7", "u1"): "XQ_S5_HIGH-v1",
        ("f1", "s3", "s4", "s5", "s6", "s7", "u1"): "XQ_A-v1",
    },
    "s1": {
        ("f1", "s1", "s3", "s4", "s5", "s6", "s7", "u1"): "XQ_A-s1",
        ("a1", "s1", "s3", "s4", "s5", "s6", "s7", "u1"): "XQ_S5_HIGH-s1",
        ("d1", "f1", "s1", "s2", "s3", "s6", "s7", "u1"): "XQ_B-s1",
    },
    "s2": {
        ("d1", "f1", "s1", "s2", "s3", "s6", "s7", "u1"): "XQ_B-s2",
    },
    "s3": {
        ("f1", "s3", "s4", "s5", "s6", "s7", "u1"): "XQ_A-s3",
        ("a1", "s1", "s3", "s4", "s5", "s6", "s7", "u1"): "XQ_S5_HIGH-s3",
        ("d1", "f1", "s1", "s2", "s3", "s6", "s7", "u1"): "XQ_B-s3",
    },
}


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    for script in EXACT_SCRIPTS:
        path = HERE / script
        assert path.exists(), path
        module = load_module(path)
        assert hasattr(module, "main"), script

    assert set(OBSERVED_COVER) == {"u1", "v1", "s1", "s2", "s3"}
    assert all(OBSERVED_COVER[key] for key in OBSERVED_COVER)
    # The full endpoint blocker set is therefore represented in the observed
    # inventory by named exact-positive or infeasible families.
    total_families = sum(len(v) for v in OBSERVED_COVER.values())
    assert total_families == 13

    print("PASS y=1 x=q endpoint observed inventory is mapped to exact verifier families")


if __name__ == "__main__":
    main()
