"""Byte-stable replay verifier for the R41 rotor realization manifest."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "manifest.json"
DRIVER = HERE / "search_rotor_realization.py"


def main() -> int:
    payload = json.loads(MANIFEST.read_text(encoding="ascii"))
    claimed = payload.pop("canonicalPayloadSha256")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    assert hashlib.sha256(canonical).hexdigest() == claimed

    with tempfile.TemporaryDirectory() as tmp:
        replay = Path(tmp) / "manifest.json"
        run = subprocess.run(
            [sys.executable, str(DRIVER), "--output", str(replay)],
            check=True,
            capture_output=True,
            text=True,
        )
        assert replay.read_bytes() == MANIFEST.read_bytes()

    data = json.loads(MANIFEST.read_text(encoding="ascii"))
    assert data["verdict"] == "BOUNDED_ZERO_FAILURE_MANIFEST"
    assert data["structural"]["triangleFree"]
    assert data["structural"]["blueConnected"]
    assert data["structural"]["maxcut"]["isMaximum"]
    assert data["tuplesEnumerated"] == data["tupleCount"] == 144
    assert data["minimumDefect"] == 0
    assert data["supportRetentionLemma"]["failures"] == 0
    assert not any(p["bothInverseActive"] for p in data["saturatedInversePairs"])
    assert data["singletonCutTightPrune"] == {
        "allWeakSingletonCutTightFailures": 0,
        "allWeakStates": 0,
        "cutTightClassAndMultiplicitySaturation": 0,
        "multiplicitySaturatedStates": 32,
        "multiplicitySaturatedWithAttachmentClass": 0,
    }
    print(json.dumps({
        "replay": "PASS",
        "manifestSha256": hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
        "payloadSha256": data["canonicalPayloadSha256"],
        "driverOutput": run.stdout.strip(),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
