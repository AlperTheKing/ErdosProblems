"""Fresh-prime replay wrapper for the exact second-face dimension probe."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "CODEX_R10_SECOND_FACE_BLOCK0_DIMENSION_PROBE.py"
FRESH_PRIMES = (1_000_133, 1_000_151, 1_000_159)


def main() -> None:
    spec = importlib.util.spec_from_file_location(
        "codex_r10_face2_dimension_source", SOURCE
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.PRIMES = FRESH_PRIMES
    module.main()


if __name__ == "__main__":
    main()
