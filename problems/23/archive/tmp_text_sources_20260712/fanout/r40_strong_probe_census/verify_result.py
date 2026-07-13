"""Structural verifier for the completed R40 census payload."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R32 = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
sys.path.insert(0, str(R32))

from collision_only_core import canonical_sha  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "payload", type=Path, nargs="?", default=HERE / "census_n5_n12.json"
    )
    args = parser.parse_args()
    payload = json.loads(args.payload.read_text(encoding="ascii"))
    claimed = payload.pop("canonicalPayloadSha256")
    assert canonical_sha(payload) == claimed
    counts = payload["counts"]
    classes = payload["ownerClassification"]
    assert payload["verdict"] == "PASS"
    assert payload["smallestExactWitness"] is None
    assert payload["integerOnly"] is True
    assert payload["workers"] <= 8
    assert counts.get("failure", 0) == 0
    assert counts["pass"] == counts["eligibleGraphs"]
    assert sum(classes.values()) == counts["activeOwnerChecks"]
    assert payload["minimumDefectHistogram"] == {
        "0": counts["eligibleGraphs"]
    }
    assert payload["allWeakReduction"] == {}
    audit = payload["r41SupportMonotonicityAudit"]
    assert audit["generalIdentityPass"] == audit["genuineDetours"]
    assert audit["r41ActivePrecondition"] == 0
    assert (
        audit["supportDelta=-1"]
        + audit["supportDelta=0"]
        + audit["supportDelta=1"]
        == audit["genuineDetours"]
    )
    print(json.dumps({
        "verdict": "PASS",
        "payloadSha256": claimed,
        "eligibleGraphs": counts["eligibleGraphs"],
        "rowTuples": counts["rowTuples"],
        "activeOwnerChecks": counts["activeOwnerChecks"],
        "genuineDetours": audit["genuineDetours"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
