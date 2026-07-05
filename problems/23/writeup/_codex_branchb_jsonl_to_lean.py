#!/usr/bin/env python3
"""Pilot transpiler from accepted Branch-B JSONL to Lean data.

This is intentionally conservative.  It does not try to replace the accepted
Python verifier; it reuses the final JSONL as source of truth, performs exact
Fraction arithmetic for the selected pilot rows, and emits a small Lean data
file shaped for the later generic checker.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any


CASE_NAMES = [
    "TIGHT_ZERO",
    "FREE_PACKET_EXCHANGE",
    "SPARSE_M1_BANKL_BYPASS",
    "MU_NUK",
    "MU_NUK_REPAIRED",
    "DETOUR_RESIDUAL",
]


CASE_TO_LEAN = {
    "TIGHT_ZERO": "BranchBCase.tightZero",
    "FREE_PACKET_EXCHANGE": "BranchBCase.freePacketExchange",
    "SPARSE_M1_BANKL_BYPASS": "BranchBCase.sparseM1BankLBypass",
    "MU_NUK": "BranchBCase.muNuk",
    "MU_NUK_REPAIRED": "BranchBCase.muNukRepaired",
    "DETOUR_RESIDUAL": "BranchBCase.detourResidual",
}


DICT_TO_LEAN = {
    "empty": "DictClass.empty",
    "terminal-prefix-raw-extraction": "DictClass.terminalPrefixRawExtraction",
    "terminal-prefix-lane-addition": "DictClass.terminalPrefixLaneAddition",
    "noncrossing-coB-extraction": "DictClass.noncrossingCoBExtraction",
    "noncrossing-coB-component-addition": "DictClass.noncrossingCoBComponentAddition",
}

CANDIDATE_PRIORITY = ("candidate_v2", "candidate_v1")
CANDIDATE_NAMES = ("none", "candidate_v1", "candidate_v2")

CANDIDATE_TO_LEAN = {
    "none": "GateBCandidate.none",
    "candidate_v1": "GateBCandidate.candidateV1",
    "candidate_v2": "GateBCandidate.candidateV2",
}


def frac(s: Any) -> Fraction:
    if s is None:
        return Fraction(0)
    if isinstance(s, Fraction):
        return s
    if isinstance(s, int):
        return Fraction(s, 1)
    return Fraction(str(s))


def lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b) if a and b else abs(a or b)


def common_den(values: list[Fraction]) -> int:
    d = 1
    for v in values:
        d = lcm(d, v.denominator)
    return d


def nat_from_fraction(value: Fraction, context: str) -> int:
    if value.denominator != 1 or value < 0:
        raise ValueError(f"expected nonnegative integer {context}, got {value}")
    return int(value)


@dataclass(frozen=True)
class ScaledEq:
    terms: tuple[int, ...]
    target: int
    den: int

    @property
    def ok(self) -> bool:
        return sum(self.terms) == self.target


@dataclass(frozen=True)
class ScaledGe:
    lhs: int
    rhs: int
    margin: int
    den: int

    @property
    def ok(self) -> bool:
        return self.lhs + self.margin == self.rhs and self.margin >= 0


def scaled_eq(terms: list[Fraction], target: Fraction) -> ScaledEq:
    d = common_den([*terms, target])
    out = ScaledEq(
        terms=tuple(int(t * d) for t in terms),
        target=int(target * d),
        den=d,
    )
    if not out.ok:
        raise ValueError(f"scaled_eq failed: {out}")
    return out


def scaled_ge(lhs: Fraction, rhs: Fraction) -> ScaledGe:
    d = common_den([lhs, rhs])
    lhs_i = int(lhs * d)
    rhs_i = int(rhs * d)
    out = ScaledGe(lhs=lhs_i, rhs=rhs_i, margin=rhs_i - lhs_i, den=d)
    if not out.ok:
        raise ValueError(f"scaled_ge failed: {out}")
    return out


def row_key(row: dict[str, Any]) -> tuple[Any, ...]:
    rid = row["row_id"]
    return (
        rid["name"],
        tuple(rid["f"]),
        tuple(rid["row"]),
        row.get("side_recomputation", {}).get("side"),
    )


def representative_key(rep: dict[str, Any]) -> tuple[Any, ...]:
    ref = rep["row_ref"]
    return (
        ref["name"],
        tuple(ref["f"]),
        tuple(ref["row"]),
        ref.get("side"),
    )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def select_gate_b_sequence(row: dict[str, Any]) -> tuple[str, dict[str, Any] | None]:
    """Return the preferred Gate-B op-sequence and its JSON candidate key.

    The accepted v1 file only carries ``candidate_v1``.  The v2+dictionary
    format may carry both, and v2 is the binding semantics when present.
    Falling back to v1 keeps the current v1 artifact reproducible.
    """

    gb = row.get("gate_b_dictionary", {}) or {}
    for key in CANDIDATE_PRIORITY:
        seq = (gb.get(key) or {}).get("op_sequence")
        if seq:
            return key, seq
    return "none", None


def select_pilot_rows(
    rows: list[dict[str, Any]], signatures_path: Path | None
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_key = {row_key(r): r for r in rows}
    selected: dict[tuple[Any, ...], dict[str, Any]] = {}
    reasons: dict[tuple[Any, ...], set[str]] = {}

    def add(row: dict[str, Any], reason: str) -> None:
        k = row_key(row)
        selected[k] = row
        reasons.setdefault(k, set()).add(reason)

    seen_cases: set[str] = set()
    for row in rows:
        case = row["case"]["proof_case"]
        if case not in seen_cases:
            add(row, f"first_case:{case}")
            seen_cases.add(case)
        if seen_cases == set(CASE_NAMES):
            break

    surplus_count = 0
    for row in rows:
        _, seq = select_gate_b_sequence(row)
        if not seq:
            continue
        if frac(seq["op_sequence_rho_sum"]) > frac(seq["raw_to_final_rho_a"]):
            add(row, "gate_b_surplus")
            surplus_count += 1

    sig_count = 0
    if signatures_path and signatures_path.exists():
        sigs = json.loads(signatures_path.read_text(encoding="utf-8"))
        for sig in sigs.get("signatures", []):
            k = representative_key(sig["representative"])
            row = by_key.get(k)
            if row is not None:
                add(row, "op_core_signature_representative")
                sig_count += 1

    pilot = list(selected.values())
    pilot.sort(key=lambda r: (r["row_id"]["n"], r["row_id"]["name"], str(r["row_id"]["f"]), str(r["row_id"]["row"])))
    meta = {
        "selected_rows": len(pilot),
        "first_case_rows": len(seen_cases),
        "surplus_rows_seen": surplus_count,
        "signature_representatives_seen": sig_count,
        "selection_reasons": {
            "|".join(map(str, k)): sorted(v) for k, v in reasons.items()
        },
    }
    return pilot, meta


def certify_row(row: dict[str, Any]) -> dict[str, Any]:
    terms = [frac(t.get("contribution", "0")) for t in row.get("terms", [])]
    identity = row["identity"]
    pressure = scaled_eq(terms, frac(identity["target"]))

    params = row["parameters"]
    finite_margin = scaled_ge(frac(params["target"]), frac(params["rho_Q"]))
    reported_margin = frac(row["finite_row_check"]["rho_minus_target"])
    if reported_margin != frac(params["rho_Q"]) - frac(params["target"]):
        raise ValueError("reported finite margin mismatch")

    candidate_version, seq = select_gate_b_sequence(row)
    op_certs = []
    dominance = scaled_ge(Fraction(0), Fraction(0))
    if seq:
        raw_rho = frac(seq["raw_to_final_rho_a"])
        op_sum = frac(seq["op_sequence_rho_sum"])
        dominance = scaled_ge(raw_rho, op_sum)
        for st in seq["op_steps"]:
            q = Fraction(st["eB_XS"] - st["eM_XS"] - st["eB_XO"] + st["eM_XO"])
            if q != frac(st["exchange_q"]):
                raise ValueError("op q mismatch")
            rho = 25 * max(Fraction(0), q)
            if rho != frac(st["rho_a"]):
                raise ValueError("op rho mismatch")
            pieces = st.get("dictionary_decomposition", [])
            piece_sum = sum((frac(p["contribution"]) for p in pieces), Fraction(0))
            if piece_sum != rho:
                raise ValueError("piece sum mismatch")
            op_certs.append(
                {
                    "op_class": st["op_class"],
                    "step_role": st["step_role"],
                    "quad": [st["eB_XS"], st["eM_XS"], st["eB_XO"], st["eM_XO"]],
                    "q": int(q),
                    "rho": int(rho),
                    "piece_count": len(pieces),
                    "piece_contribs": [
                        nat_from_fraction(frac(p["contribution"]), "dictionary contribution")
                        for p in pieces
                    ],
                    "piece_sum": str(piece_sum),
                }
            )

    return {
        "key": row_key(row),
        "case": row["case"]["proof_case"],
        "row_id": row["row_id"],
        "L": int(row["parameters"]["L"]),
        "pressure_eq": pressure,
        "finite_margin": finite_margin,
        "gate_b": {
            "required": bool(seq),
            "candidate_version": candidate_version,
            "dominance": dominance,
            "op_certs": op_certs,
        },
    }


def lean_str(s: str) -> str:
    return json.dumps(s)


def lean_int_list(values: tuple[int, ...] | list[int]) -> str:
    return "[" + ", ".join(str(v) for v in values) + "]"


def emit_scaled_eq(name: str, cert: ScaledEq) -> str:
    return (
        f"{{ terms := {lean_int_list(cert.terms)}, target := {cert.target}, "
        f"den := {cert.den}, proofMode := {lean_str('rfl-or-norm_num')} }}"
    )


def emit_scaled_ge(cert: ScaledGe) -> str:
    return (
        f"{{ lhs := {cert.lhs}, rhs := {cert.rhs}, margin := {cert.margin}, "
        f"den := {cert.den}, proofMode := {lean_str('rfl-or-norm_num')} }}"
    )



def support_lines() -> list[str]:
    lines: list[str] = []
    lines.append("/- Generated Branch-B certificate support definitions. -/")
    lines.append("import Mathlib")
    lines.append("")
    lines.append("namespace Erdos23Delta0")
    lines.append("namespace Cert")
    lines.append("")
    lines.append("inductive BranchBCase where")
    lines.append("  | tightZero")
    lines.append("  | freePacketExchange")
    lines.append("  | sparseM1BankLBypass")
    lines.append("  | muNuk")
    lines.append("  | muNukRepaired")
    lines.append("  | detourResidual")
    lines.append("deriving Repr, DecidableEq")
    lines.append("")
    lines.append("inductive DictClass where")
    lines.append("  | empty")
    lines.append("  | terminalPrefixRawExtraction")
    lines.append("  | terminalPrefixLaneAddition")
    lines.append("  | noncrossingCoBExtraction")
    lines.append("  | noncrossingCoBComponentAddition")
    lines.append("deriving Repr, DecidableEq")
    lines.append("")
    lines.append("inductive GateBCandidate where")
    lines.append("  | none")
    lines.append("  | candidateV1")
    lines.append("  | candidateV2")
    lines.append("deriving Repr, DecidableEq")
    lines.append("")
    lines.append("def GateBCandidate.expectsOps : GateBCandidate -> Bool")
    lines.append("  | GateBCandidate.none => false")
    lines.append("  | GateBCandidate.candidateV1 => true")
    lines.append("  | GateBCandidate.candidateV2 => true")
    lines.append("")
    lines.append("structure ScaledEqCert where")
    lines.append("  terms : List Int")
    lines.append("  target : Int")
    lines.append("  den : Nat")
    lines.append("  proofMode : String")
    lines.append("deriving Repr")
    lines.append("")
    lines.append("structure ScaledGeCert where")
    lines.append("  lhs : Int")
    lines.append("  rhs : Int")
    lines.append("  margin : Nat")
    lines.append("  den : Nat")
    lines.append("  proofMode : String")
    lines.append("deriving Repr")
    lines.append("")
    lines.append("def intListSum : List Int -> Int")
    lines.append("  | [] => 0")
    lines.append("  | x :: xs => x + intListSum xs")
    lines.append("")
    lines.append("def natListSum : List Nat -> Nat")
    lines.append("  | [] => 0")
    lines.append("  | x :: xs => x + natListSum xs")
    lines.append("")
    lines.append("def ScaledEqCert.check (c : ScaledEqCert) : Bool :=")
    lines.append("  (c.den != 0) && (intListSum c.terms == c.target)")
    lines.append("")
    lines.append("def ScaledGeCert.check (c : ScaledGeCert) : Bool :=")
    lines.append("  (c.den != 0) && (c.lhs + Int.ofNat c.margin == c.rhs)")
    lines.append("")
    lines.append("structure OpStepPilot where")
    lines.append("  opClass : DictClass")
    lines.append("  stepRole : String")
    lines.append("  eB_XS : Int")
    lines.append("  eM_XS : Int")
    lines.append("  eB_XO : Int")
    lines.append("  eM_XO : Int")
    lines.append("  q : Int")
    lines.append("  rho : Int")
    lines.append("  pieceCount : Nat")
    lines.append("  pieceContribs : List Nat")
    lines.append("  pieceSum : Nat")
    lines.append("deriving Repr")
    lines.append("")
    lines.append("def OpStepPilot.expectedQ (s : OpStepPilot) : Int :=")
    lines.append("  s.eB_XS - s.eM_XS - s.eB_XO + s.eM_XO")
    lines.append("")
    lines.append("def OpStepPilot.expectedRho (s : OpStepPilot) : Int :=")
    lines.append("  if s.q < 0 then 0 else 25 * s.q")
    lines.append("")
    lines.append("def OpStepPilot.check (s : OpStepPilot) : Bool :=")
    lines.append("  (s.q == OpStepPilot.expectedQ s) &&")
    lines.append("  (s.rho == OpStepPilot.expectedRho s) &&")
    lines.append("  (s.pieceContribs.length == s.pieceCount) &&")
    lines.append("  (natListSum s.pieceContribs == s.pieceSum) &&")
    lines.append("  (s.rho == Int.ofNat s.pieceSum)")
    lines.append("")
    lines.append("def opStepListCheck : List OpStepPilot -> Bool")
    lines.append("  | [] => true")
    lines.append("  | s :: ss => OpStepPilot.check s && opStepListCheck ss")
    lines.append("")
    lines.append("structure RowPilot where")
    lines.append("  name : String")
    lines.append("  n : Nat")
    lines.append("  m : Nat")
    lines.append("  L : Nat")
    lines.append("  caseTag : BranchBCase")
    lines.append("  gateBCandidate : GateBCandidate")
    lines.append("  pressure : ScaledEqCert")
    lines.append("  finiteMargin : ScaledGeCert")
    lines.append("  gateBDominance : ScaledGeCert")
    lines.append("  opSteps : List OpStepPilot")
    lines.append("deriving Repr")
    lines.append("")
    lines.append("def RowPilot.candidateCheck (r : RowPilot) : Bool :=")
    lines.append("  GateBCandidate.expectsOps r.gateBCandidate == !r.opSteps.isEmpty")
    lines.append("")
    lines.append("def RowPilot.check (r : RowPilot) : Bool :=")
    lines.append("  ScaledEqCert.check r.pressure &&")
    lines.append("  ScaledGeCert.check r.finiteMargin &&")
    lines.append("  ScaledGeCert.check r.gateBDominance &&")
    lines.append("  RowPilot.candidateCheck r &&")
    lines.append("  opStepListCheck r.opSteps")
    lines.append("")
    lines.append("def rowPilotListCheck : List RowPilot -> Bool")
    lines.append("  | [] => true")
    lines.append("  | r :: rs => RowPilot.check r && rowPilotListCheck rs")
    lines.append("")
    lines.append("def rowPilotCaseCount (tag : BranchBCase) : List RowPilot -> Nat")
    lines.append("  | [] => 0")
    lines.append("  | r :: rs => (if r.caseTag = tag then 1 else 0) + rowPilotCaseCount tag rs")
    lines.append("")
    lines.append("def rowPilotCandidateCount (tag : GateBCandidate) : List RowPilot -> Nat")
    lines.append("  | [] => 0")
    lines.append("  | r :: rs => (if r.gateBCandidate = tag then 1 else 0) + rowPilotCandidateCount tag rs")
    lines.append("")
    lines.append("def rowPilotGateBRowCount : List RowPilot -> Nat")
    lines.append("  | [] => 0")
    lines.append("  | r :: rs => (if GateBCandidate.expectsOps r.gateBCandidate then 1 else 0) + rowPilotGateBRowCount rs")
    lines.append("")
    lines.append("def branchBCaseCountVector (rows : List RowPilot) : List Nat := [")
    lines.append("  rowPilotCaseCount BranchBCase.tightZero rows,")
    lines.append("  rowPilotCaseCount BranchBCase.freePacketExchange rows,")
    lines.append("  rowPilotCaseCount BranchBCase.sparseM1BankLBypass rows,")
    lines.append("  rowPilotCaseCount BranchBCase.muNuk rows,")
    lines.append("  rowPilotCaseCount BranchBCase.muNukRepaired rows,")
    lines.append("  rowPilotCaseCount BranchBCase.detourResidual rows")
    lines.append("]")
    lines.append("")
    lines.append("def branchBCandidateCountVector (rows : List RowPilot) : List Nat := [")
    lines.append("  rowPilotCandidateCount GateBCandidate.none rows,")
    lines.append("  rowPilotCandidateCount GateBCandidate.candidateV1 rows,")
    lines.append("  rowPilotCandidateCount GateBCandidate.candidateV2 rows")
    lines.append("]")
    lines.append("")
    lines.append("end Cert")
    lines.append("end Erdos23Delta0")
    lines.append("")
    return lines


def emit_support(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(support_lines()), encoding="utf-8")


def emit_lean(
    pilot: list[dict[str, Any]],
    out_path: Path,
    def_name: str = "branchBPilotRows",
    *,
    emit_length_theorem: bool = True,
    self_contained: bool = False,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("/- Generated by _codex_branchb_jsonl_to_lean.py.")
    lines.append("   Branch-B certificate row data; do not edit by hand. -/")
    lines.append("")
    if self_contained:
        lines.extend(support_lines())
    else:
        lines.append("import Erdos23Delta0.Cert.BranchBSupport")
        lines.append("")
    lines.append("namespace Erdos23Delta0")
    lines.append("namespace Cert")
    lines.append("")
    lines.append(f"def {def_name} : List RowPilot := [")
    row_lines = []
    for cert in pilot:
        rid = cert["row_id"]
        op_entries = []
        for op in cert["gate_b"]["op_certs"]:
            cls = DICT_TO_LEAN[op["op_class"]]
            q0, q1, q2, q3 = op["quad"]
            op_entries.append(
                "{ "
                f"opClass := {cls}, stepRole := {lean_str(op['step_role'])}, "
                f"eB_XS := {q0}, eM_XS := {q1}, eB_XO := {q2}, eM_XO := {q3}, "
                f"q := {op['q']}, rho := {op['rho']}, "
                f"pieceCount := {op['piece_count']}, "
                f"pieceContribs := {lean_int_list(op['piece_contribs'])}, "
                f"pieceSum := {sum(op['piece_contribs'])} "
                "}"
            )
        row_lines.append(
            "  { "
            f"name := {lean_str(rid['name'])}, n := {rid['n']}, m := {rid['m']}, L := {cert['L']}, "
            f"caseTag := {CASE_TO_LEAN[cert['case']]}, "
            f"gateBCandidate := {CANDIDATE_TO_LEAN[cert['gate_b']['candidate_version']]}, "
            f"pressure := {emit_scaled_eq('pressure', cert['pressure_eq'])}, "
            f"finiteMargin := {emit_scaled_ge(cert['finite_margin'])}, "
            f"gateBDominance := {emit_scaled_ge(cert['gate_b']['dominance'])}, "
            f"opSteps := [{', '.join(op_entries)}] "
            "}"
        )
    lines.append(",\n".join(row_lines))
    lines.append("]")
    lines.append("")
    if emit_length_theorem:
        lines.append(f"theorem {def_name}_length : {def_name}.length = {len(pilot)} := by")
        lines.append("  rfl")
        lines.append("")
    lines.append("set_option maxRecDepth 20000 in")
    lines.append(f"theorem {def_name}_check : rowPilotListCheck {def_name} = true := by")
    lines.append("  rfl")
    lines.append("")
    lines.append("end Cert")
    lines.append("end Erdos23Delta0")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def module_name_from_path(path: Path) -> str:
    parts = path.with_suffix("").parts
    if "Erdos23Delta0" in parts:
        idx = parts.index("Erdos23Delta0")
        return ".".join(parts[idx:])
    raise ValueError(f"cannot derive module name from {path}")


def count_cases(certs: list[dict[str, Any]]) -> list[int]:
    counter = Counter(c["case"] for c in certs)
    return [counter[name] for name in CASE_NAMES]


def count_candidates(certs: list[dict[str, Any]]) -> list[int]:
    counter = Counter(c["gate_b"]["candidate_version"] for c in certs)
    return [counter[name] for name in CANDIDATE_NAMES]


def count_gate_b_rows(certs: list[dict[str, Any]]) -> int:
    return sum(1 for c in certs if c["gate_b"]["required"])


def emit_index(
    out_path: Path,
    shard_paths: list[str],
    shard_lengths: list[int],
    extra_imports: list[str],
    shard_case_counts: list[list[int]],
    shard_candidate_counts: list[list[int]],
    shard_gate_b_counts: list[int],
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("/- Generated aggregate imports for Branch-B certificate shards. -/")
    lines.append("import Erdos23Delta0.Cert.BranchBSupport")
    for module in extra_imports:
        lines.append(f"import {module}")
    for shard in shard_paths:
        lines.append(f"import {module_name_from_path(Path(shard))}")
    lines.append("")
    lines.append("namespace Erdos23Delta0")
    lines.append("namespace Cert")
    lines.append("")
    names = [Path(p).stem for p in shard_paths]
    def_names = [f"branchBRowsShard{name[-3:]}" for name in names]
    checks = [f"rowPilotListCheck {d}" for d in def_names]
    lens = [f"{d}.length" for d in def_names]
    case_vectors = [f"branchBCaseCountVector {d}" for d in def_names]
    candidate_vectors = [f"branchBCandidateCountVector {d}" for d in def_names]
    gate_b_counts = [f"rowPilotGateBRowCount {d}" for d in def_names]
    lines.append("def branchBShardChecks : List Bool := [")
    lines.append("  " + ",\n  ".join(checks))
    lines.append("]")
    lines.append("")
    lines.append("set_option maxRecDepth 20000 in")
    lines.append("theorem branchBShardChecks_expected :")
    lines.append("    branchBShardChecks = [" + ", ".join(["true"] * len(checks)) + "] := by")
    lines.append("  rfl")
    lines.append("")
    lines.append("def branchBShardLengths : List Nat := [")
    lines.append("  " + ",\n  ".join(lens))
    lines.append("]")
    lines.append("")
    lines.append("def branchBShardCaseCountVectors : List (List Nat) := [")
    lines.append("  " + ",\n  ".join(case_vectors))
    lines.append("]")
    lines.append("")
    lines.append("def branchBShardCandidateCountVectors : List (List Nat) := [")
    lines.append("  " + ",\n  ".join(candidate_vectors))
    lines.append("]")
    lines.append("")
    lines.append("def branchBShardGateBRowCounts : List Nat := [")
    lines.append("  " + ",\n  ".join(gate_b_counts))
    lines.append("]")
    lines.append("")
    lines.append("set_option maxRecDepth 20000 in")
    lines.append("theorem branchBShardLengths_expected :")
    lines.append("    branchBShardLengths = [" + ", ".join(str(x) for x in shard_lengths) + "] := by")
    lines.append("  rfl")
    lines.append("")
    lines.append("set_option maxRecDepth 20000 in")
    lines.append("theorem branchBShardCaseCountVectors_expected :")
    lines.append("    branchBShardCaseCountVectors = [")
    lines.append("      " + ",\n      ".join(lean_int_list(v) for v in shard_case_counts))
    lines.append("    ] := by")
    lines.append("  rfl")
    lines.append("")
    lines.append("set_option maxRecDepth 20000 in")
    lines.append("theorem branchBShardCandidateCountVectors_expected :")
    lines.append("    branchBShardCandidateCountVectors = [")
    lines.append("      " + ",\n      ".join(lean_int_list(v) for v in shard_candidate_counts))
    lines.append("    ] := by")
    lines.append("  rfl")
    lines.append("")
    lines.append("set_option maxRecDepth 20000 in")
    lines.append("theorem branchBShardGateBRowCounts_expected :")
    lines.append("    branchBShardGateBRowCounts = [" + ", ".join(str(x) for x in shard_gate_b_counts) + "] := by")
    lines.append("  rfl")
    lines.append("")
    lines.append("set_option maxRecDepth 20000 in")
    lines.append(f"theorem branchBShardCount : branchBShardChecks.length = {len(checks)} := by")
    lines.append("  rfl")
    lines.append("")
    lines.append("set_option maxRecDepth 20000 in")
    lines.append(f"theorem branchBTotalRows : natListSum branchBShardLengths = {sum(shard_lengths)} := by")
    lines.append("  rfl")
    lines.append("")
    lines.append("end Cert")
    lines.append("end Erdos23Delta0")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tmp/bankl_branchb_gateb_final_v1.jsonl")
    ap.add_argument("--signatures", default="tmp/bankl_completion_op_sequence_core_signatures_v1.json")
    ap.add_argument("--mode", choices=["pilot", "full"], default="pilot")
    ap.add_argument("--manifest", default="tmp/branchb_lean_transpile_pilot_v1_manifest.json")
    ap.add_argument("--lean-out", default="problems/23/lean/Erdos23Delta0/Cert/BranchBData/Pilot.lean")
    ap.add_argument("--out-dir", default="problems/23/lean/Erdos23Delta0/Cert/BranchBData")
    ap.add_argument("--support-out", default="problems/23/lean/Erdos23Delta0/Cert/BranchBSupport.lean")
    ap.add_argument("--index-out", default="problems/23/lean/Erdos23Delta0/Cert/BranchBData.lean")
    ap.add_argument("--extra-index-import", action="append", default=[])
    ap.add_argument("--shard-size", type=int, default=500)
    ap.add_argument("--self-contained", action="store_true", help="emit standalone files with local support defs")
    args = ap.parse_args()

    rows = load_jsonl(Path(args.input))
    emitted: list[str] = []
    if not args.self_contained:
        emit_support(Path(args.support_out))
        emitted.append(args.support_out)
    shard_lengths: list[int] = []
    if args.mode == "pilot":
        pilot_rows, selection_meta = select_pilot_rows(rows, Path(args.signatures))
        certs = [certify_row(r) for r in pilot_rows]
        emit_lean(certs, Path(args.lean_out), "branchBPilotRows", self_contained=args.self_contained)
        emitted.append(args.lean_out)
    else:
        selection_meta = {"mode": "full", "selected_rows": len(rows)}
        certs = [certify_row(r) for r in rows]
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        shard_case_counts: list[list[int]] = []
        shard_candidate_counts: list[list[int]] = []
        shard_gate_b_counts: list[int] = []
        for idx in range(0, len(certs), args.shard_size):
            shard_no = idx // args.shard_size
            chunk = certs[idx : idx + args.shard_size]
            shard_path = out_dir / f"Shard{shard_no:03d}.lean"
            emit_lean(
                chunk,
                shard_path,
                f"branchBRowsShard{shard_no:03d}",
                emit_length_theorem=False,
                self_contained=args.self_contained,
            )
            emitted.append(str(shard_path))
            shard_lengths.append(len(chunk))
            shard_case_counts.append(count_cases(chunk))
            shard_candidate_counts.append(count_candidates(chunk))
            shard_gate_b_counts.append(count_gate_b_rows(chunk))
        shard_paths = emitted if args.self_contained else emitted[1:]
        if not args.self_contained:
            emit_index(
                Path(args.index_out),
                shard_paths,
                shard_lengths,
                args.extra_index_import,
                shard_case_counts,
                shard_candidate_counts,
                shard_gate_b_counts,
            )
            emitted.append(args.index_out)

    case_counts = Counter(c["case"] for c in certs)
    gate_b_candidate_counts = Counter(c["gate_b"]["candidate_version"] for c in certs)
    op_steps = sum(len(c["gate_b"]["op_certs"]) for c in certs)
    manifest = {
        "schema": "branchb_lean_transpile_v1",
        "mode": args.mode,
        "self_contained": args.self_contained,
        "input": args.input,
        "signatures": args.signatures,
        "lean_out": args.lean_out if args.mode == "pilot" else None,
        "out_dir": args.out_dir if args.mode == "full" else None,
        "support_out": None if args.self_contained else args.support_out,
        "index_out": None if args.self_contained else (args.index_out if args.mode == "full" else None),
        "extra_index_imports": args.extra_index_import if args.mode == "full" and not args.self_contained else [],
        "emitted": emitted,
        "selected": selection_meta,
        "counts": {
            "input_rows": len(rows),
            "rows": len(certs),
            "gate_b_rows": sum(1 for c in certs if c["gate_b"]["required"]),
            "op_steps": op_steps,
            "case_counts": dict(case_counts),
            "gate_b_candidate_counts": dict(gate_b_candidate_counts),
        },
        "checks": {
            "all_pressure_eq_scaled": all(c["pressure_eq"].ok for c in certs),
            "all_finite_margins_scaled": all(c["finite_margin"].ok for c in certs),
            "all_gate_b_dominance_scaled": all(c["gate_b"]["dominance"].ok for c in certs),
        },
    }
    Path(args.manifest).write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(
        f"PASS branchb lean {args.mode} emit "
        f"rows={len(certs)} gate_b_rows={manifest['counts']['gate_b_rows']} "
        f"op_steps={op_steps} emitted={len(emitted)}"
    )
if __name__ == "__main__":
    main()








