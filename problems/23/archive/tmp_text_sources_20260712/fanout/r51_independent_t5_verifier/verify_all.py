#!/usr/bin/env python3
"""Rebuild, solve, and proof-check every completed n=15/n=16 split."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from pysat.solvers import Solver

from independent_t5_cnf import build_encoding, canonical_json_sha
from semantic_check import check_support


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = REPO / "tmp" / "fanout" / "r42_graph_specific_exclusion"
OUT = HERE / "artifacts"
PAIRS = ((7, 8), (8, 7), (9, 6), (10, 5), (7, 9), (8, 8), (9, 7), (10, 6), (11, 5))
SOLVERS = ("cadical195", "glucose4", "lingeling")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_logged(command: list[str], log: Path) -> tuple[int, str]:
    proc = subprocess.run(
        command,
        cwd=REPO,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    log.write_text(proc.stdout, encoding="utf-8")
    return proc.returncode, proc.stdout


def require_original_claim(artifact: dict, left: int, right: int) -> None:
    required = {
        "schema": "rooted-t5-support-circuit-search-v1",
        "left": left,
        "right": right,
        "requireTwoOwnerProfile": False,
        "requireLiveTransitionProfile": False,
        "requireSharedBadNeighbour": False,
        "ownerRowCount": None,
        "supportMinMultiplicity": 2,
        "requireDeletionSdr": True,
        "requireBadTriangleFree": True,
        "selectedAtomCount": 25,
        "ownerBadDegree": 5,
        "localClassifier": "v",
        "requireActiveScope": True,
        "supportsSolved": 0,
        "supportsWithAtLeast25Atoms": 0,
        "circuitStatuses": {},
        "hit": None,
        "supportTerminalStatus": "INFEASIBLE",
    }
    mismatches = {
        key: {"expected": expected, "actual": artifact.get(key)}
        for key, expected in required.items()
        if artifact.get(key) != expected
    }
    if mismatches:
        raise AssertionError(f"source artifact mismatch: {mismatches}")
    if canonical_json_sha(artifact) != artifact.get("canonicalSha256"):
        raise AssertionError("source artifact canonical SHA mismatch")


def core_clause_count(path: Path) -> int:
    for line in path.read_text(encoding="ascii").splitlines():
        if line.startswith("p cnf "):
            return int(line.split()[3])
    raise AssertionError("core CNF has no header")


def solve_split(left: int, right: int) -> dict:
    n = left + right
    stem = f"n{n}_l{left}_r{right}"
    split = OUT / stem
    split.mkdir(parents=True, exist_ok=True)

    source_path = SOURCE / f"t5_solo_l{left}_r{right}_3000.json"
    artifact = json.loads(source_path.read_text(encoding="utf-8"))
    require_original_claim(artifact, left, right)

    # This is deliberately a relaxation: no connectivity and no symmetry.
    enc = build_encoding(left, right, include_connectivity=False)
    cnf_path = split / "relaxed.cnf"
    enc.cnf.to_file(str(cnf_path))

    solver_status = {}
    for name in SOLVERS:
        with Solver(name=name, bootstrap_with=enc.cnf.clauses) as solver:
            solver_status[name] = "SAT" if solver.solve() else "UNSAT"
    if set(solver_status.values()) != {"UNSAT"}:
        raise AssertionError(f"solver disagreement at {stem}: {solver_status}")

    cadical = HERE / "cadical.exe"
    drat_trim = HERE / "drat-trim.exe"
    lrat_trim = HERE / "lrat-trim.exe"
    for tool in (cadical, drat_trim, lrat_trim):
        if not tool.is_file():
            raise SystemExit(f"missing {tool}; run build_tools.ps1 first")

    drat_path = split / "proof.drat"
    cadical_rc, cadical_out = run_logged(
        [str(cadical), "--no-binary", str(cnf_path), str(drat_path)],
        split / "cadical.log",
    )
    if "s UNSATISFIABLE" not in cadical_out or not drat_path.is_file():
        raise AssertionError(f"CaDiCaL did not produce UNSAT proof at {stem} (rc={cadical_rc})")

    core_path = split / "core.cnf"
    drat_rc, drat_out = run_logged(
        [
            str(drat_trim),
            str(cnf_path),
            str(drat_path),
            "-c",
            str(core_path),
            "-w",
        ],
        split / "drat_check.log",
    )
    if "s VERIFIED" not in drat_out or not core_path.is_file():
        raise AssertionError(f"DRAT verification failed at {stem} (rc={drat_rc})")

    # Generate LRAT directly.  DRAT-trim's LRAT conversion and LRAT-trim
    # disagree on a few RAT-heavy cases; native CaDiCaL LRAT checks cleanly.
    lrat_path = split / "proof.lrat"
    cadical_lrat_rc, cadical_lrat_out = run_logged(
        [str(cadical), "--lrat", "--no-binary", str(cnf_path), str(lrat_path)],
        split / "cadical_lrat.log",
    )
    if "s UNSATISFIABLE" not in cadical_lrat_out or not lrat_path.is_file():
        raise AssertionError(
            f"CaDiCaL did not produce native LRAT at {stem} (rc={cadical_lrat_rc})"
        )

    lrat_rc, lrat_out = run_logged(
        [str(lrat_trim), str(cnf_path), str(lrat_path)],
        split / "lrat_check.log",
    )
    if "s VERIFIED" not in lrat_out:
        raise AssertionError(f"LRAT verification failed at {stem} (rc={lrat_rc})")

    result = {
        "split": stem,
        "left": left,
        "right": right,
        "order": n,
        "sourceArtifact": str(source_path.relative_to(REPO)).replace("\\", "/"),
        "sourceArtifactSha256": sha256(source_path),
        "sourceCanonicalSha256": artifact["canonicalSha256"],
        "sourceArtifactClaim": "INFEASIBLE before any support/circuit certificate",
        "emittedSupportCertificates": artifact["supportsSolved"],
        "emittedCircuitStatuses": artifact["circuitStatuses"],
        "encoding": {
            "variables": enc.pool.top,
            "clauses": len(enc.cnf.clauses),
            "connectivityOmitted": True,
            "labelSymmetryOmitted": True,
        },
        "independentSolverStatuses": solver_status,
        "cadicalReturnCode": cadical_rc,
        "cadicalLratReturnCode": cadical_lrat_rc,
        "dratTrimReturnCode": drat_rc,
        "lratTrimReturnCode": lrat_rc,
        "dratVerified": True,
        "lratVerified": True,
        "coreClauses": core_clause_count(core_path),
        "files": {
            path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in (
                cnf_path,
                drat_path,
                lrat_path,
                core_path,
            )
        },
    }
    result_path = split / "result.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def positive_control() -> dict:
    # Order 17 is the first feasible shore regime in the production sweep.
    enc = build_encoding(9, 8, include_connectivity=True)
    statuses = {}
    edges = None
    for name in SOLVERS:
        with Solver(name=name, bootstrap_with=enc.cnf.clauses) as solver:
            sat = solver.solve()
            statuses[name] = "SAT" if sat else "UNSAT"
            if name == "cadical195" and sat:
                truth = {lit for lit in solver.get_model() if lit > 0}
                edges = [[u, r] for (u, r), var in sorted(enc.edge.items()) if var in truth]
    if set(statuses.values()) != {"SAT"} or edges is None:
        raise AssertionError(f"positive-control disagreement: {statuses}")
    semantics = check_support(9, 8, edges, require_connected=True)
    return {
        "order": 17,
        "left": 9,
        "right": 8,
        "connectivityEncoded": True,
        "statuses": statuses,
        "edges": edges,
        "directSemanticCheck": semantics,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    splits = [solve_split(left, right) for left, right in PAIRS]
    control = positive_control()
    code_files = (
        HERE / "independent_t5_cnf.py",
        HERE / "semantic_check.py",
        HERE / "verify_all.py",
        HERE / "audit_manifest.py",
        HERE / "build_tools.ps1",
        HERE / "lrat_trim_win.c",
    )
    tools = (HERE / "cadical.exe", HERE / "drat-trim.exe", HERE / "lrat-trim.exe")
    manifest = {
        "schema": "independent-rooted-t5-verification-manifest-v1",
        "claimCoverage": {
            "orders": [15, 16],
            "splits": len(splits),
            "allSourceCanonicalHashesMatch": True,
            "allRelaxedCnfsUnsat": True,
            "allDratProofsVerified": True,
            "allLratProofsVerified": True,
            "sourceSupportCertificatesPresent": 0,
            "sourceCircuitCertificatesPresent": 0,
        },
        "logicalStrength": (
            "Each CNF omits connectivity and label symmetry; UNSAT therefore proves a strict "
            "relaxation of the source CP-SAT support model."
        ),
        "splits": splits,
        "positiveControl": control,
        "implementationFiles": {
            str(path.relative_to(HERE)).replace("\\", "/"): sha256(path) for path in code_files
        },
        "toolBinaries": {
            path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)} for path in tools
        },
        "cadicalStaticLibrarySha256": sha256(REPO / "third_party" / "cadical" / "build" / "libcadical.a"),
    }
    raw = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("ascii")
    manifest["canonicalSha256"] = hashlib.sha256(raw).hexdigest()
    path = HERE / "MANIFEST.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest["claimCoverage"], indent=2, sort_keys=True))
    print(f"MANIFEST {manifest['canonicalSha256']}")


if __name__ == "__main__":
    main()
