"""Independent semantic comparison for the R44 live-rotor graft replay."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ORIGINAL = ROOT / "tmp/fanout/r44_dense_source_swap_graft/manifest.json"
REPLAY = ROOT / "tmp/fanout/r42_graph_specific_exclusion/r44_replay_workers8.json"
RESULT = ROOT / "tmp/fanout/r42_graph_specific_exclusion/r44_replay_verification.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def canonical_sha(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_embedded_sha(payload: dict) -> str:
    claimed = payload["canonicalPayloadSha256"]
    unhashed = copy.deepcopy(payload)
    del unhashed["canonicalPayloadSha256"]
    actual = canonical_sha(unhashed)
    assert actual == claimed, (claimed, actual)
    return actual


def semantic_payload(payload: dict) -> dict:
    normalized = copy.deepcopy(payload)
    del normalized["canonicalPayloadSha256"]
    del normalized["workers"]
    del normalized["graph"]["space"]["workers"]
    return normalized


def main() -> None:
    original = json.loads(ORIGINAL.read_text(encoding="ascii"))
    replay = json.loads(REPLAY.read_text(encoding="ascii"))
    original_canonical = check_embedded_sha(original)
    replay_canonical = check_embedded_sha(replay)

    original_semantic = semantic_payload(original)
    replay_semantic = semantic_payload(replay)
    assert original_semantic == replay_semantic
    semantic = canonical_sha(original_semantic)

    graph = replay["graph"]
    assert graph["hitCount"] == 0
    assert graph["verdict"] == "BOUNDED_NO_GRAPH_HIT"
    assert graph["counts"] == {
        "ACTIVE_PIN_REJECT": 112,
        "FULL_GRAPH_EVALUATED": 8,
        "STRUCTURAL_REJECT": 8,
    }
    full = [r for r in graph["records"] if r["gate"] == "FULL_GRAPH_EVALUATED"]
    assert len(full) == 8
    assert all(r["minimumCanonicalCollisionDefect"] == 0 for r in full)
    assert all(not r["hitSccs"] for r in full)

    result = {
        "schema": "R44_REPLAY_VERIFICATION_V1",
        "originalFileSha256": file_sha(ORIGINAL),
        "replayFileSha256": file_sha(REPLAY),
        "originalCanonicalPayloadSha256": original_canonical,
        "replayCanonicalPayloadSha256": replay_canonical,
        "normalizedSemanticSha256": semantic,
        "normalizedPayloadsEqual": True,
        "workerMetadataOnlyDifference": True,
        "graphGateCounts": graph["counts"],
        "fullGraphEvaluated": len(full),
        "minimumDefects": [r["minimumCanonicalCollisionDefect"] for r in full],
        "graphHits": graph["hitCount"],
    }
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
