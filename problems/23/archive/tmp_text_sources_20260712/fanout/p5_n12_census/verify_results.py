"""Hash, coverage, and cross-artifact verifier for the delivered P5 gate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CANONICAL = (
    "input_audit.json",
    "census_all_n5_n10.json",
    "census_all_n11.json",
    "census_all_n12.json",
    "census_all_n5_n12.json",
    "first_micro_falsifier_replay.json",
    "first_claude_relation_falsifier.json",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    canonical = {}
    for name in CANONICAL:
        payload = json.loads((HERE / name).read_text(encoding="utf-8"))
        claimed = payload.pop("canonicalPayloadSha256")
        actual = canonical_sha(payload)
        assert claimed == actual, name
        canonical[name] = claimed

    for name in ("census_all_n5_n10.json", "census_all_n11.json", "census_all_n12.json"):
        payload = json.loads((HERE / name).read_text(encoding="utf-8"))
        for relative, claimed in payload["sourceSha256"].items():
            assert sha256(ROOT / relative) == claimed, (name, relative)

    aggregate = json.loads((HERE / "census_all_n5_n12.json").read_text(encoding="utf-8"))
    counts = aggregate["total"]["counts"]
    assert counts["availableTuples"] == counts["examinedTuples"] == 40_228_399
    assert counts["testedGraphs"] == counts["representativeGraphs"] == 992_618
    assert counts["positiveDemandTuples"] == 1_649_719
    assert counts["microBeforeP5Failures"] == 63_422
    assert counts["microRepairs"] == 38_310
    assert counts["microFiveFailures"] == 25_112
    assert counts["oneFiveFailures"] == 0
    assert counts["representativeMicroFailures"] == 0
    assert counts["p5NegativeSwitches"] == counts["p5ReservedCandidates"] == 0

    first = aggregate["total"]["first"]["firstMicroFalsifier"]
    assert first == json.loads((HERE / "first_micro_falsifier.json").read_text(encoding="utf-8"))
    assert first["g6"] == "I?`fBO]]?" and first["tupleIndex"] == 43
    assert first["microFive"]["maximumDefect"] == 50
    assert first["oneFive"]["full"]

    replay = json.loads((HERE / "first_micro_falsifier_replay.json").read_text(encoding="utf-8"))
    assert replay["recordSha256"] == first["recordSha256"]
    assert replay["microFive"]["maximumDefect"] == 50
    assert replay["oneFive"]["full"]

    narrow = json.loads((HERE / "first_claude_relation_falsifier.json").read_text(encoding="utf-8"))
    assert narrow["order10Failures"] == 192
    assert narrow["first"]["oneClaudeAfter"]["maximumDefect"] == 6
    assert narrow["first"]["oneFive"]["full"]

    print(json.dumps({
        "verdict": "PASS",
        "canonicalPayloadSha256": canonical,
        "aggregateFileSha256": sha256(HERE / "census_all_n5_n12.json"),
        "firstMicroReplayFileSha256": sha256(HERE / "first_micro_falsifier_replay.json"),
    }, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
