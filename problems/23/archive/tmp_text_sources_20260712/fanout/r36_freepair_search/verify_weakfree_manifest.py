"""Verify and aggregate the corrected weak-free census artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
FILES = (
    "weakfree_smoke_n5_n8.json",
    "weakfree_n9_n10.json",
    "weakfree_n11.json",
    "weakfree_n12.json",
)
EXPECTED_ELIGIBLE = (100, 6321, 64287, 921910)
EXPECTED_PROBES = {
    "detour": 1027,
    "sigma0": 55,
    "sigma1": 174,
    "sigmaGe2": 8509,
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    payloads = [json.loads((HERE / name).read_text(encoding="ascii")) for name in FILES]
    for payload, expected in zip(payloads, EXPECTED_ELIGIBLE):
        assert payload["schema"] == "R37_WEAK_FREE_DEADEND_GATE_V1"
        assert payload["productionCommonBlueThreshold"] == "sigma >= 2"
        assert payload["counts"]["canonicalZero"] == expected
        assert payload["counts"].get("canonicalPositive", 0) == 0
        assert payload["counts"].get("canonicalDeadEndCandidate", 0) == 0
        assert payload["exactWitness"] is None
        replay = payload["sigma1WitnessReplay"]
        assert (replay["dB"], replay["dM"], replay["sigma"]) == (3, 2, 1)
        assert replay["commonBlueValid"] is False
    probes = {}
    for payload in payloads:
        for kind, count in payload["probeCounts"].items():
            probes[kind] = probes.get(kind, 0) + count
    assert probes == EXPECTED_PROBES
    manifest = {
        "schema": "R37_WEAK_FREE_N_LE_12_MANIFEST_V1",
        "verdict": "ZERO_CANONICAL_DEADEND",
        "productionCommonBlueThreshold": "sigma >= 2",
        "eligibleCanonicalStates": sum(EXPECTED_ELIGIBLE),
        "canonicalPositiveDefectStates": 0,
        "canonicalDeadEndWitness": None,
        "probeCounts": probes,
        "weakFreeProbeCount": probes["sigma0"] + probes["sigma1"],
        "sigma1Witness": payloads[0]["sigma1WitnessReplay"],
        "files": {name: sha(HERE / name) for name in FILES},
    }
    encoded = json.dumps(manifest, sort_keys=True, indent=2) + "\n"
    (HERE / "MANIFEST.json").write_text(encoded, encoding="ascii")
    (HERE / "SHA256SUMS.txt").write_text(
        "".join(f"{sha(HERE / name)}  {name}\n" for name in (*FILES, "MANIFEST.json")),
        encoding="ascii",
    )
    print("REPLAY=PASS")
    print(f"eligible={manifest['eligibleCanonicalStates']} canonical_positive=0 deadends=0")
    print("probes=" + json.dumps(probes, sort_keys=True, separators=(",", ":")))
    print("manifest_sha256=" + sha(HERE / "MANIFEST.json"))


if __name__ == "__main__":
    main()
