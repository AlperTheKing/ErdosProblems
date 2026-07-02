"""Consolidated exact reduction of the y=1, x=q, s2 endpoint.

This is an organizational closure gate for one endpoint blocker in the x=q
branch.  It does not prove the full x=q endpoint coverage theorem.  It proves
that the endpoint blocker s2=0 has no independent capacity obstruction left:
any minimum on y=1, x=q, s2=0 reduces to one of the already tracked endpoint
blockers

    u=1,  s1=0,  or  s3=0.

The proof chain is exact and consists of:

1. strict v-monotonicity at fixed core variables on x=q,s2;
2. infeasibility of capacity blockers s4=0 and s5=0 on x=q,s2;
3. s6=0 descends to s3=0;
4. s7=0 descends to s3=0 or b=1;
5. that b=1 boundary descends to s3=0.

Each component is checked by a separate exact script; this gate runs them in a
single place so later endpoint-coverage work can cite one artifact.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
COMPONENTS = [
    "_codex_sib_s7_y1_xq_s2_monotone_v.py",
    "_codex_sib_s7_y1_xq_s2_impossible_caps.py",
    "_codex_sib_s7_y1_xq_s2_pair_structure.py",
    "_codex_sib_s7_y1_xq_s2_s6_descent.py",
    "_codex_sib_s7_y1_xq_s2_s7_descent.py",
    "_codex_sib_s7_y1_xq_s2_s7_b1_descent.py",
]


def run_component(script: str) -> None:
    path = HERE / script
    assert path.exists(), path
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert hasattr(module, "main"), script
    module.main()


def main() -> None:
    for script in COMPONENTS:
        run_component(script)
    print("PASS y=1 x=q,s2 endpoint reduces to u1, s1, or s3 blockers")


if __name__ == "__main__":
    main()
