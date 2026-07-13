"""Corrected production neutralExposure gate.

The production source union is P1/P2/P3/P4/P5 plus corrected common-blue.
Common-blue is accepted only through TerminalData.Valid, whose numerical
condition is sigma({x,y}) >= 2.  Sigma 0/1 probes are recorded as weak and do
not contribute to exposure.

All currently available canonical states have a checked defect-zero coherent
matching in the P1/P3/P4/P5 subset.  Since defect is a natural number, these
states are defect-minimal for the larger production relation.  Consequently
the positive-defect matching-state graph, its equal-defect detours, and sink
SCCs have empty domains.  The manifest records this logical short circuit
explicitly instead of claiming to enumerate irrelevant perfect matchings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R32 = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
JOIN = ROOT / "tmp" / "fanout" / "r32_join5886"
R36 = ROOT / "tmp" / "fanout" / "r36_freepair_search"
R36_PROOF = ROOT / "tmp" / "fanout" / "r36_freepair_proof"
R41_ROTOR = ROOT / "tmp" / "fanout" / "r41_rotor_realization"

CENSUS_FILES = (
    "weakfree_smoke_n5_n8.json",
    "weakfree_n9_n10.json",
    "weakfree_n11.json",
    "weakfree_n12.json",
)
FIXTURE_NAMES = ("89", "2943", "3892", "join-5886")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


def source_contract() -> dict:
    return {
        "families": ["P1", "P2", "P3", "P4", "P5", "common-blue"],
        "ordinaryCheckedSubset": ["P1", "P3", "strict-P4", "P5"],
        "commonBluePredicate": (
            "blue(owner,x) and blue(owner,y) and pairCount(x,y)=0 and "
            "dM({x,y})+2<=dB({x,y})"
        ),
        "terminalDataThreshold": "sigma({x,y})=dB({x,y})-dM({x,y}) >= 2",
        "weakSigma01CountsAsExposure": False,
        "physicalSourceIdentity": "(ordered sourceX, ordered sourceY, half)",
        "coherence": "both halves of one ordered-pair base use one active component",
        "commonBlueReservation": "exclusive terminal edges; reserved-edge FreeHalves deducted",
    }


def monotone_support_contract() -> dict:
    """Exact support potential for a genuine two-edge detour.

    In an induced shortest row, a blue pair occurring in a row is consecutive.
    Thus pairCount(m,x)=1 is equivalent to the selected support edge mx having
    a unique selected-row occurrence, and likewise for my.
    """
    rotor_path = R41_ROTOR / "manifest.json"
    rotor = read_json(rotor_path)
    retention = rotor["supportRetentionLemma"]
    if retention["failures"] != 0:
        raise AssertionError(retention)
    return {
        "detour": "Q=(a,...,x,m,y,...,b) -> Q'=(a,...,x,v,y,...,b)",
        "genuinePremise": "xv and vy are active, hence absent from old selectedSupport",
        "supportDelta": (
            "+2 - 1[pairCount(m,x)=1] - 1[pairCount(m,y)=1]"
        ),
        "nondecreasing": True,
        "equalityIff": "pairCount(m,x)=pairCount(m,y)=1",
        "strictGrowthOtherwise": True,
        "cycleConsequence": (
            "every edge of a directed neutral cycle has constant support and is fully unsaturated"
        ),
        "newFreeConsequence": (
            "each cycle transition creates both orientations and both halves on the old-middle endpoints"
        ),
        "r38MultiplicitySaturatedRotorPossible": False,
        "remainingCandidate": "source-swap rotor consuming every created eligible key",
        "boundedRealCageAudit": {
            "checkedSaturatedTransitions": retention["checkedTransitions"],
            "supportRetentionFailures": retention["failures"],
            "inverseActivePairs": sum(
                bool(pair["bothInverseActive"])
                for pair in rotor["saturatedInversePairs"]
            ),
            "input": str(rotor_path.relative_to(ROOT)).replace("\\", "/"),
            "inputSha256": sha256_file(rotor_path),
        },
    }


def zero_record(name: str, evidence: dict, *, tuple_label: str) -> dict:
    """A defect-zero state makes the positive-defect exposure domain empty."""
    return {
        "name": name,
        "tupleScope": tuple_label,
        "defect": 0,
        "minimumDefect": 0,
        "defectMinimalTuples": 1,
        "optimalCoherentMatchings": {
            "enumerationStatus": "POSITIVE_DEFECT_DOMAIN_EMPTY",
            "reason": "one checked total coherent matching proves natural-valued defect minimum zero",
        },
        "equalDefectDetours": 0,
        "neutralStateVertices": 0,
        "neutralStateEdges": 0,
        "sinkSccs": [],
        "minimumExposure": 0,
        "exposureConvention": "minimum over the empty positive-defect sink-SCC domain",
        "defectPositiveExposureZero": False,
        "fullReplayCertificate": None,
        "evidence": evidence,
    }


def load_fixture_records() -> tuple[list[dict], dict]:
    battery_path = R32 / "fixture_battery_result.json"
    battery = read_json(battery_path)
    raw_source = battery["fixtures"] if "fixtures" in battery else battery
    if isinstance(raw_source, list):
        source = {}
        for entry in raw_source:
            source.setdefault(str(entry["fixture"]), entry)
    else:
        source = raw_source["fixtures"] if "fixtures" in raw_source else raw_source

    records = []
    for name in ("89", "2943", "3892"):
        item = source[name]
        cert = item.get("checked_certificate", item)
        demand = cert.get("total_demand", cert.get("collisionDemand"))
        matched = cert.get("max_flow", cert.get("collisionMatched"))
        if not cert.get("full", demand == matched) or demand != matched:
            raise AssertionError((name, demand, matched))
        records.append(zero_record(name, {
            "kind": "exact P1/P3/strict-P4/P5 subset certificate",
            "collisionDemand": demand,
            "collisionMatched": matched,
            "ownerShoresChecked": cert["owner_shores_checked"],
            "shoreTableSha256": cert["shore_table_sha256"],
            "input": str(battery_path.relative_to(ROOT)).replace("\\", "/"),
            "inputSha256": sha256_file(battery_path),
        }, tuple_label="available checked canonical fixture state"))

    join_path = JOIN / "result.json"
    join = read_json(join_path)
    repair = join["coherenceConstrainedRepair"]
    flows = repair["exactFlowPerComponent"]
    demand = repair["perComponentDemand"]
    if flows != [demand, demand]:
        raise AssertionError((flows, demand))
    records.append(zero_record("join-5886", {
        "kind": "exact component-coherent P1/P3/P5 subset assignment",
        "perComponentDemand": demand,
        "exactFlowPerComponent": flows,
        "combinedAssignments": repair["combinedAssignments"],
        "fullKeyInjective": repair["fullKeyInjective"],
        "baseKeyComponentCoherent": repair["baseKeyComponentCoherent"],
        "assignmentSha256": repair["assignmentSHA256"],
        "input": str(join_path.relative_to(ROOT)).replace("\\", "/"),
        "inputSha256": sha256_file(join_path),
    }, tuple_label="available all-anchor joined canonical state"))
    if tuple(r["name"] for r in records) != FIXTURE_NAMES:
        raise AssertionError([r["name"] for r in records])
    return records, {
        "fixtureBattery": sha256_file(battery_path),
        "joinResult": sha256_file(join_path),
        "joinAssignment": sha256_file(JOIN / "coherent_assignment.json"),
    }


def load_census_records() -> tuple[list[dict], dict]:
    expected_manifest = read_json(R36 / "MANIFEST.json")["files"]
    records = []
    hashes = {}
    total = 0
    probes = {"sigma0": 0, "sigma1": 0, "sigmaGe2": 0, "detour": 0}
    for name in CENSUS_FILES:
        path = R36 / name
        digest = sha256_file(path)
        if expected_manifest[name] != digest:
            raise AssertionError((name, expected_manifest[name], digest))
        payload = read_json(path)
        if payload["verdict"] != "ZERO_CANONICAL_DEADEND":
            raise AssertionError((name, payload["verdict"]))
        positive = payload["counts"].get("canonicalPositive", 0)
        dead = payload["counts"].get("canonicalDeadEndCandidate", 0)
        if positive or dead:
            raise AssertionError((name, positive, dead))
        states = payload["counts"].get("canonicalZero", 0)
        total += states
        for key in probes:
            probes[key] += payload.get("probeCounts", {}).get(key, 0)
        records.append({
            "file": name,
            "orders": payload["orders"],
            "availableCanonicalStates": states,
            "minimumDefect": 0,
            "defectMinimalTuples": states,
            "positiveDefectStates": 0,
            "optimalCoherentMatchingExpansion": "vacuous for positive-defect domain",
            "equalDefectDetours": 0,
            "sinkSccs": 0,
            "minimumExposure": 0,
            "sha256": digest,
        })
        hashes[name] = digest
    if total != 992_618:
        raise AssertionError(total)
    if probes != {"sigma0": 55, "sigma1": 174, "sigmaGe2": 8509, "detour": 1027}:
        raise AssertionError(probes)
    return records, {
        "availableCanonicalStates": total,
        "positiveDefectStates": 0,
        "minimumExposure": 0,
        "probeCounts": probes,
        "weakSigma01Excluded": probes["sigma0"] + probes["sigma1"],
        "files": hashes,
    }


def sigma_gap_replay() -> dict:
    path = R36_PROOF / "REPORT.md"
    verifier = R36_PROOF / "verify_counterexample.py"
    return {
        "order": 20,
        "dB": 3,
        "dM": 2,
        "sigma": 1,
        "countsAsExposure": False,
        "reportSha256": sha256_file(path),
        "verifierSha256": sha256_file(verifier),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output", type=Path, default=HERE / "manifest.json")
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("workers must be in 1..8")

    fixtures, fixture_hashes = load_fixture_records()
    census, census_summary = load_census_records()
    payload = {
        "schema": "R41_CORRECTED_PRODUCTION_NEUTRAL_EXPOSURE_GATE_V1",
        "arithmetic": "Python integers, finite sets, and SHA-256 only",
        "workers": args.workers,
        "sourceContract": source_contract(),
        "monotoneSupportDichotomy": monotone_support_contract(),
        "enumerationRule": {
            "tuple": "all available canonical states; defect zero certifies global minimum immediately",
            "matching": "expand all optimal coherent matchings only when minimum defect is positive",
            "detour": "enumerate one-row equal-defect detours only on the positive-minimum state graph",
            "scc": "Tarjan sink SCCs of the resulting occurrence graph",
            "exposure": (
                "unused production probe sources plus unused target-eligible NewFree escape sources; "
                "weak sigma 0/1 probes excluded"
            ),
            "replay": "emit full replay certificate for every defect>0, Exposure=0 sink SCC",
        },
        "fixtures": fixtures,
        "census": census,
        "censusSummary": census_summary,
        "sigmaGapControl": sigma_gap_replay(),
        "defectPositiveExposureZeroCertificates": [],
        "verdict": "NO_POSITIVE_DEFECT_EXPOSURE_ZERO_STATE_IN_AVAILABLE_CANONICAL_INPUTS",
        "inputs": fixture_hashes,
    }
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        "verdict": payload["verdict"],
        "fixtures": {r["name"]: [r["defect"], r["minimumExposure"]] for r in fixtures},
        "canonicalStates": census_summary["availableCanonicalStates"],
        "weakSigma01Excluded": census_summary["weakSigma01Excluded"],
        "sha256": payload["canonicalPayloadSha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
