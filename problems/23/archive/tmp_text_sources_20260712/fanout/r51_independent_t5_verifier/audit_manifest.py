#!/usr/bin/env python3
"""Standard-library integrity audit for the independent t=5 manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(payload: dict) -> str:
    body = dict(payload)
    body.pop("canonicalSha256", None)
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    path = HERE / "MANIFEST.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    assert canonical(manifest) == manifest["canonicalSha256"]

    for relative, expected in manifest["implementationFiles"].items():
        assert sha256(HERE / relative) == expected, relative
    for name, metadata in manifest["toolBinaries"].items():
        tool = HERE / name
        assert tool.stat().st_size == metadata["bytes"]
        assert sha256(tool) == metadata["sha256"]

    for split in manifest["splits"]:
        source = REPO / split["sourceArtifact"]
        assert sha256(source) == split["sourceArtifactSha256"]
        source_json = json.loads(source.read_text(encoding="utf-8"))
        assert canonical(source_json) == split["sourceCanonicalSha256"]
        assert source_json["supportTerminalStatus"] == "INFEASIBLE"
        assert source_json["supportsSolved"] == 0
        assert source_json["circuitStatuses"] == {}

        directory = HERE / "artifacts" / split["split"]
        for name, metadata in split["files"].items():
            artifact = directory / name
            assert artifact.stat().st_size == metadata["bytes"], artifact
            assert sha256(artifact) == metadata["sha256"], artifact
        assert "s UNSATISFIABLE" in (directory / "cadical.log").read_text(encoding="utf-8")
        assert "s VERIFIED" in (directory / "drat_check.log").read_text(encoding="utf-8")
        assert "s UNSATISFIABLE" in (directory / "cadical_lrat.log").read_text(encoding="utf-8")
        assert "s VERIFIED" in (directory / "lrat_check.log").read_text(encoding="utf-8")
        assert set(split["independentSolverStatuses"].values()) == {"UNSAT"}

    assert set(manifest["positiveControl"]["statuses"].values()) == {"SAT"}
    assert manifest["positiveControl"]["directSemanticCheck"]["connected"] is True
    print(f"PASS manifest={manifest['canonicalSha256']} splits={len(manifest['splits'])}")


if __name__ == "__main__":
    main()
