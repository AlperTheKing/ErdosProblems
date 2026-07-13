"""Replay the doubled-R29 Pattern-5 ownership falsifier as external evidence."""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
SOURCE = (
    ROOT
    / "tmp/fanout/common_blue_universal/pattern5_static_token"
    / "doubled_cage_falsifier.py"
)
EXPECTED_SOURCE_SHA256 = (
    "0b73b97e75a2440e28833883da9f650bfd36223bdb9211f84a70e343d5cd1237"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    assert sha256(SOURCE) == EXPECTED_SOURCE_SHA256
    spec = importlib.util.spec_from_file_location("r32_doubled_cage", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Keep all generated evidence in this owned lane.
    module.HERE = HERE
    with contextlib.redirect_stdout(io.StringIO()):
        module.main()

    output = HERE / "doubled_cage_result.json"
    result = json.loads(output.read_text())
    assert result["arithmetic"] == "integer-only"
    assert result["graph"]["n"] == 5886
    assert result["graph"]["triangleFree"] is True
    assert result["graph"]["maxCutUpper"] == result["graph"]["attainingCut"]
    assert result["pattern5"]["eligibleDestinationRoots"] == [0, 2943]
    assert result["verdict"] == "RELATION_BASE_COMPONENT_UNIQUE_FALSIFIED"
    print(
        json.dumps(
            {
                "resultSHA256": sha256(output),
                "sourceSHA256": sha256(SOURCE),
                "verdict": result["verdict"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
