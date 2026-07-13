#!/usr/bin/env python3
"""Independent artifact and certificate consistency checks."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="ascii"))


def check_self_hash(value: dict, *, ignored=()) -> bool:
    copy = dict(value)
    expected = copy.pop("canonicalPayloadSha256")
    for key in ignored:
        copy.pop(key, None)
    return canonical_sha(copy) == expected


def main() -> int:
    checks = {}
    named_path = HERE / "named_results.json"
    named = load(named_path)
    checks["namedCanonicalHash"] = check_self_hash(named)
    checks["sixRelationFamilies"] = set(named["relationProvenance"]) == {
        "P1_sameFirst",
        "P2_commonBad",
        "P3_rowCompanion",
        "P4_outsideAttachment",
        "P5_quiescentAttachment",
        "commonBlue",
    }
    checks["allRelationDataReconstructed"] = all(
        item["data"] == "reconstructed"
        for item in named["relationProvenance"].values()
    )

    expected_defects = {
        "n12_common_blue_choice_0_4_7_9": 0,
        "n12_common_blue_graph_minimum": 0,
        "n24_r1_fixed_rows": 0,
        "n167_fixed_rows": 0,
        "n175_fixed_rows": 0,
        "n311_fixed_rows": 0,
        "n89_singleton_row_database": 0,
        "n24_r35_displayed": 24,
        "n24_r35_old_one_row_trade": 6,
        "n24_r35_hamming_le_one_minimum": 6,
        "n2943_all_anchor": 0,
        "n3892_lex_rows": 0,
        "n78_rotor_state_0": 0,
        "n78_rotor_state_1": 0,
        "n78_rotor_state_2": 0,
        "n78_rotor_state_3": 0,
    }
    fixtures = {item["name"]: item for item in named["fixtures"]}
    checks["fixtureSet"] = set(fixtures) == set(expected_defects)
    checks["fixtureDefects"] = all(
        fixtures[name]["minimumDefect"] == defect
        for name, defect in expected_defects.items()
    )
    checks["fixtureCanonicalHashes"] = all(
        check_self_hash(item) for item in fixtures.values()
    )
    checks["fixedFailureDuals"] = all(
        item["stages"][-1]["minCutShoreDefect"] == item["minimumDefect"]
        for item in fixtures.values()
        if item["minimumDefect"] > 0
    )
    checks["failuresListComplete"] = {
        item["name"] for item in named["failures"]
    } == {
        name for name, defect in expected_defects.items() if defect > 0
    }

    n89 = fixtures["n89_singleton_row_database"]
    n89_stage = n89["stages"][-1]
    checks["n89CorrectedProductionPass"] = (
        n89["metadata"]["rowDatabaseSingleton"]
        and n89["state"]["globalCollisionHalfDemand"] == 776
        and n89["maximumFlow"] == 776
        and n89["minimumDefect"] == 0
        and n89_stage["defect"] == 0
        and n89_stage["afterAdding"] == "P4_outsideAttachment"
        and n89["notEnumeratedFamilies"] == ["P5_quiescentAttachment"]
    )
    counterexample = load(HERE / "counterexample_n89.json")
    checks["n89StrictP4ArchivedCounterexample"] = (
        counterexample["schema"] == "R53_GLOBAL_FREEHALF_N89_COUNTEREXAMPLE_V1"
        and counterexample["primal"]["globalCollisionHalfDemand"] == 776
        and counterexample["primal"]["maximumFlow"] == 774
        and counterexample["primal"]["defect"] == 2
        and counterexample["dual"]["shoreOwners"] == [0, 1, 2]
        and counterexample["dual"]["shoreDemand"] == 528
        and counterexample["dual"]["shoreCapacity"] == 526
        and counterexample["dataAvailability"]["allSixFamiliesReconstructed"]
        and not counterexample["dataAvailability"]["missingRelationData"]
        and counterexample["sourceSha256"][
            "tmp/fanout/r53_global_softcap_gate/global_softcap.py"
        ]
        == "b4e1b379f53a1297f95ec30eb38b796f3906949a1b6f462a07ae627667fe9652"
    )
    r35 = fixtures["n24_r35_displayed"]
    r35_stage = r35["stages"][-1]
    checks["r35DisplayedDual"] = (
        r35["state"]["globalCollisionHalfDemand"] == 312
        and r35["maximumFlow"] == 288
        and r35["minCutSourceOwners"] == [6, 8]
        and r35_stage["minCutSourceOwnerDemand"] == 144
        and r35_stage["minCutShoreDirectCapacity"] == 116
        and r35_stage["minCutShoreActiveCapacity"] == 4
    )

    n12_path = HERE / "n12_common_blue_all_tuples.json"
    n12 = load(n12_path)
    checks["n12ExhaustiveCanonicalHash"] = check_self_hash(n12)
    checks["n12NestedHashAndFile"] = (
        check_self_hash(named["n12AllTuples"], ignored=("fileSha256",))
        and named["n12AllTuples"]["fileSha256"] == sha256(n12_path)
    )
    checks["n12ExhaustiveCounts"] = (
        n12["tuples"] == 2400
        and n12["minimumDefect"] == 0
        and n12["failureCount"] == 0
        and sum(n12["defectHistogram"].values()) == 2400
        and len(n12["failures"]) == 0
        and all(
            item["shoreDemand"] - item["shoreCapacity"] == item["defect"]
            for item in n12["failures"]
        )
    )

    r35_path = HERE / "r35_n24_hamming_le_one.json"
    r35_local = load(r35_path)
    checks["r35LocalCanonicalHash"] = check_self_hash(r35_local)
    checks["r35NestedHashAndFile"] = (
        check_self_hash(
            named["r35N24HammingLeOne"], ignored=("fileSha256",)
        )
        and named["r35N24HammingLeOne"]["fileSha256"] == sha256(r35_path)
    )
    checks["r35LocalCoverage"] = (
        r35_local["statesExhausted"] == 214
        and r35_local["minimumDefect"] == 6
        and len(r35_local["failures"]) == 214
        and sum(r35_local["defectHistogram"].values()) == 214
    )

    alternate = load(HERE / "n89_unscoped_p4_alternate.json")
    alternate_sources = [
        tuple(record["source"]) for record in alternate["assignments"]
    ]
    alternate_diagnostics = alternate["namedDiagnostics"]
    checks["unscopedP4IndependentReplay"] = (
        check_self_hash(alternate)
        and alternate["status"] == "CORRECTED_MODEL_INDEPENDENT_REPLAY_PASS"
        and alternate["globalDemand"] == 776
        and alternate["maximumFlow"] == 776
        and alternate["defect"] == 0
        and all(alternate["checks"].values())
        and len(alternate_sources) == len(set(alternate_sources)) == 776
        and alternate_diagnostics["n12_common_blue_choice_0_4_7_9"][
            "defect"
        ]
        == 0
        and alternate_diagnostics["n24_r1_fixed_rows"]["defect"] == 0
        and alternate_diagnostics["n89_singleton_row_database"]["defect"] == 0
        and alternate_diagnostics["n24_r35_displayed"]["defect"] == 24
        and alternate_diagnostics["n24_r35_old_one_row_trade"]["defect"]
        == 6
        and alternate_diagnostics["n24_r35_hamming_le_one"][
            "minimumDefect"
        ]
        == 6
    )

    census_expectations = {
        "census_n5_n10.json": 6421,
        "census_n11.json": 64287,
        "census_n12.json": 921910,
    }
    census_total = 0
    for filename, expected_tested in census_expectations.items():
        value = load(HERE / filename)
        key = filename.removesuffix(".json")
        checks[f"{key}CanonicalHash"] = check_self_hash(value)
        tested = sum(
            counts.get("tested", 0)
            for counts in value["coverage"]["countsByOrder"].values()
        )
        census_total += tested
        checks[f"{key}Coverage"] = (
            value["coverage"]["completeForSelectedOrders"]
            and value["failedGraphCount"] == 0
            and tested == expected_tested
            and not value["failures"]
        )
    checks["censusN5ToN12Total"] = census_total == 992618

    exactness_violations = []
    for path in sorted(HERE.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="ascii"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(
                node.value, (float, complex)
            ):
                exactness_violations.append((path.name, node.lineno, "literal"))
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "float"
            ):
                exactness_violations.append((path.name, node.lineno, "float"))
            elif isinstance(node, (ast.Name, ast.Attribute)) and getattr(
                node, "id", getattr(node, "attr", "")
            ) == "native_decide":
                exactness_violations.append(
                    (path.name, node.lineno, "native_decide")
                )
    core_tree = ast.parse(
        (HERE / "global_softcap.py").read_text(encoding="ascii")
    )
    core_true_divisions = [
        node.lineno
        for node in ast.walk(core_tree)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
    ]
    checks["integerOnlySource"] = not exactness_violations
    checks["noTrueDivisionInFlowCore"] = not core_true_divisions

    certificate_checks = {}
    for item in fixtures.values():
        artifact = item.get("certificate") or item.get("partialFlowArtifact")
        if artifact is None:
            continue
        path = ROOT / artifact["path"]
        value = load(path)
        assignments = value["assignments"]
        sources = [tuple(record["source"]) for record in assignments]
        obligations = [tuple(record["obligation"]) for record in assignments]
        generic = {
            "canonicalHash": check_self_hash(value),
            "fileHash": sha256(path) == artifact["fileSha256"],
            "uniqueSources": len(sources) == len(set(sources)),
            "uniqueObligations": len(obligations) == len(set(obligations)),
            "eligibleFamilyOnEveryArc": all(
                record["families"] for record in assignments
            ),
            "activeLoadsAtMostTwo": all(
                amount <= 2 for amount in value["activeEdgeLoads"].values()
            ),
        }
        if "certificate" in item:
            generic["allChecksTrue"] = all(value["checks"].values())
            generic["assignmentCardinality"] = (
                len(assignments) == item["state"]["globalCollisionHalfDemand"]
            )
        else:
            generic["properPartialFlow"] = (
                len(assignments) == item["maximumFlow"]
                and not value["checks"]["allGlobalDemandAssigned"]
            )
        certificate_checks[item["name"]] = generic
    checks["literalAssignmentArtifacts"] = all(
        all(values.values()) for values in certificate_checks.values()
    )

    artifact_paths = sorted(
        path
        for path in HERE.rglob("*")
        if path.is_file()
        and path.suffix in {".py", ".json", ".md", ".ps1"}
        and path.name not in {"verification.json"}
    )
    artifact_hashes = {
        str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
        for path in artifact_paths
    }
    payload = {
        "schema": "R53_GLOBAL_SOFTCAP_VERIFICATION_V1",
        "checks": checks,
        "certificateChecks": certificate_checks,
        "artifactSha256": artifact_hashes,
        "allChecksPass": all(checks.values()),
    }
    if not payload["allChecksPass"]:
        raise AssertionError(
            [name for name, passed in checks.items() if not passed]
        )
    payload["canonicalPayloadSha256"] = canonical_sha(payload)
    verification_path = HERE / "verification.json"
    verification_path.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="ascii"
    )

    manifest_paths = sorted(
        path
        for path in HERE.rglob("*")
        if path.is_file()
        and path.suffix in {".py", ".json", ".md", ".ps1"}
        and path.name != "MANIFEST.sha256"
    )
    manifest = "".join(
        f"{sha256(path)}  {str(path.relative_to(HERE)).replace('\\', '/')}\n"
        for path in manifest_paths
    )
    (HERE / "MANIFEST.sha256").write_text(manifest, encoding="ascii")
    print(
        json.dumps(
            {
                "allChecksPass": True,
                "canonicalPayloadSha256": payload["canonicalPayloadSha256"],
                "artifactCount": len(manifest_paths),
                "censusSystems": census_total,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
