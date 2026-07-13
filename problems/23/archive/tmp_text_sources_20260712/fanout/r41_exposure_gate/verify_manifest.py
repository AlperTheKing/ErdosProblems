"""Independent structural verifier for the R41 exposure manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def canonical_sha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    path = HERE / "manifest.json"
    payload = json.loads(path.read_text(encoding="ascii"))
    expected = payload.pop("canonicalPayloadSha256")
    assert canonical_sha(payload) == expected
    assert payload["workers"] <= 8
    assert payload["sourceContract"]["terminalDataThreshold"].endswith(">= 2")
    assert payload["sourceContract"]["weakSigma01CountsAsExposure"] is False
    support = payload["monotoneSupportDichotomy"]
    assert support["nondecreasing"] and support["strictGrowthOtherwise"]
    assert support["r38MultiplicitySaturatedRotorPossible"] is False
    assert support["boundedRealCageAudit"]["supportRetentionFailures"] == 0
    assert support["boundedRealCageAudit"]["inverseActivePairs"] == 0
    assert [r["name"] for r in payload["fixtures"]] == ["89", "2943", "3892", "join-5886"]
    assert all(r["defect"] == 0 and r["minimumExposure"] == 0 for r in payload["fixtures"])
    assert payload["censusSummary"]["availableCanonicalStates"] == 992618
    assert payload["censusSummary"]["positiveDefectStates"] == 0
    assert payload["censusSummary"]["weakSigma01Excluded"] == 229
    assert payload["sigmaGapControl"]["sigma"] == 1
    assert payload["sigmaGapControl"]["countsAsExposure"] is False
    assert payload["defectPositiveExposureZeroCertificates"] == []
    print(f"PASS manifest sha={expected} fixtures=4 canonicalStates=992618 exposureZeroHits=0")


if __name__ == "__main__":
    main()
