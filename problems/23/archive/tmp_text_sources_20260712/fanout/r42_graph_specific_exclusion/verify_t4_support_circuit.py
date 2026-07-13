"""Independent exact verifier for t4_support_circuit_hit.json."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path


HERE = Path(__file__).resolve().parent
PATH = HERE / "t4_support_circuit_hit.json"


def main():
    payload = json.loads(PATH.read_text())
    claimed = payload.pop("canonicalSha256")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    assert sha256(canonical.encode("ascii")).hexdigest() == claimed
    rows = [frozenset(row) for row in payload["rows"]]
    assert len(rows) == 16 and all(len(row) == 4 for row in rows)
    support = set().union(*rows)
    assert support == set(range(15))
    assert len(support) == 15
    degrees = [sum(edge in row for row in rows) for edge in range(15)]
    assert degrees == payload["edgeDegrees"] and min(degrees) >= 2
    vstar = set(payload["edges"]["vStar"])
    mstar = set(payload["edges"]["mStar"])
    tails = set(payload["edges"]["sharedTail"])
    internal = set(payload["edges"]["internal"])
    assert len(vstar) == len(mstar) == len(tails) == 4
    assert len(internal) == 3
    assert len(vstar | mstar | tails | internal) == 15
    fixed = rows[:8]
    assert all(row == frozenset({0, 12, 14, 8 + i})
               for i, row in enumerate(fixed[:4]))
    assert all(row == frozenset({4, 13, 14, 8 + i})
               for i, row in enumerate(fixed[4:]))
    full = (1 << 16) - 1
    worst = -10**9
    witnesses = []
    for mask in range(1, full):
        union = set()
        count = 0
        for i, row in enumerate(rows):
            if (mask >> i) & 1:
                union.update(row)
                count += 1
        defect = count - len(union)
        if defect > worst:
            worst = defect
            witnesses = [mask]
        elif defect == worst:
            witnesses.append(mask)
        assert defect <= 0
    assert worst == payload["worstProperDefect"] == 0
    assert len(rows) - len(support) == payload["fullDefect"] == 1
    result = {
        "verdict": "PASS_ABSTRACT_SUPPORT_CIRCUIT",
        "canonicalSha256": claimed,
        "properSubsetsChecked": full - 1,
        "worstProperDefect": worst,
        "tightProperSubsets": len(witnesses),
        "minEdgeDegree": min(degrees),
        "scope": "abstract support family only; graph/path realization unproved",
    }
    out = HERE / "t4_support_circuit_verification.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
