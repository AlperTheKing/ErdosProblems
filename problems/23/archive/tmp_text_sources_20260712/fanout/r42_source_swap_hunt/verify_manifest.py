"""Independent deterministic replay check for the R42 source-swap hunt."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

import source_swap_hunt as hunt


HERE = Path(__file__).resolve().parent


def main() -> int:
    manifest_path = HERE / "manifest.json"
    recorded = json.loads(manifest_path.read_text(encoding="ascii"))
    for line in (HERE / "SHA256SUMS.txt").read_text(encoding="ascii").splitlines():
        digest, filename = line.split(maxsplit=1)
        actual = hashlib.sha256((HERE / filename).read_bytes()).hexdigest().upper()
        if actual != digest:
            raise AssertionError((filename, digest, actual))
    with tempfile.TemporaryDirectory() as directory:
        replay_path = Path(directory) / "manifest.json"
        if hunt.main(["--workers", str(recorded["workers"]), "--output", str(replay_path)]) != 0:
            raise AssertionError("replay command failed")
        replayed = json.loads(replay_path.read_text(encoding="ascii"))
    if recorded != replayed:
        raise AssertionError("replay manifest differs")
    if recorded["canonicalPayloadSha256"] != hunt.canonical_sha({
        key: value for key, value in recorded.items() if key != "canonicalPayloadSha256"
    }):
        raise AssertionError("canonical payload hash mismatch")
    graph = recorded["graph"]
    if graph["hitCount"]:
        for record in graph["records"]:
            for scc in record.get("hitSccs", []):
                if not scc["hit"]:
                    raise AssertionError("listed hit is not a hit")
    print(json.dumps({
        "canonicalPayloadSha256": recorded["canonicalPayloadSha256"],
        "graphHits": graph["hitCount"],
        "verdict": graph["verdict"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
