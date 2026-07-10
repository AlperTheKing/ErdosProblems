#!/usr/bin/env python3
"""Emit direct common-denominator integer residual proofs for Chart000."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

THIS = Path(__file__).resolve()
sys.path.insert(0, str(THIS.parent))

import _codex_eq_odl1_rung2_scipy_core_probe as probe


def read_solution(path: Path) -> list[tuple[int, Fraction]]:
    records: list[tuple[int, Fraction]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rec = json.loads(line)
            records.append((
                int(rec["source_col"]),
                Fraction(int(rec["num"]), int(rec["den"])),
            ))
    records.sort()
    return records


def intlean(value: int) -> str:
    return f"({value} : Int)"


def multinomial(total: int, exponents: tuple[int, ...]) -> int:
    out = math.factorial(total)
    for exponent in exponents:
        out //= math.factorial(exponent)
    return out


def powslean(exponents: tuple[int, ...]) -> str:
    entries = ", ".join(
        f"({index}, {exponent})"
        for index, exponent in enumerate(exponents)
        if exponent
    )
    return f"[{entries}]"


def scale_row(
    target: Fraction,
    terms: list[tuple[int, Fraction]],
    weight_denom: int,
    scaled_weights: list[int],
) -> tuple[int, int, list[tuple[int, int]], int]:
    scale = target.denominator
    for _weight_id, coeff in terms:
        scale = math.lcm(scale, coeff.denominator)
    target_q = target * weight_denom * scale
    if target_q.denominator != 1:
        raise AssertionError("target did not integer-scale")
    scaled_terms: list[tuple[int, int]] = []
    total = 0
    for weight_id, coeff in terms:
        coeff_q = coeff * scale
        if coeff_q.denominator != 1:
            raise AssertionError("coefficient did not integer-scale")
        coeff_int = coeff_q.numerator
        scaled_terms.append((weight_id, coeff_int))
        total += scaled_weights[weight_id] * coeff_int
    residual = target_q.numerator - total
    if residual < 0:
        raise AssertionError("negative residual")
    return scale, target_q.numerator, scaled_terms, residual


def row_lean(scale: int, target: int, terms: list[tuple[int, int]]) -> str:
    term_text = ", ".join(
        f"{{ weightId := {weight_id}, coeff := {intlean(coeff)} }}"
        for weight_id, coeff in terms
    )
    return (
        f"{{ scalePred := {scale - 1}, target := {intlean(target)}, "
        f"terms := [{term_text}] }}"
    )


def emit_weight_fun(
    path: Path,
    weight_denom: int,
    scaled_weights: list[int],
) -> dict[str, int | str]:
    equations = [
        f"  | {weight_id} => {value}"
        for weight_id, value in enumerate(scaled_weights)
    ]
    equations.append("  | _ => 0")
    facts = [
        f"@[simp] theorem weight_{weight_id:04d} : weight {weight_id} = {value} := rfl"
        for weight_id, value in enumerate(scaled_weights)
    ]
    text = "\n".join([
        "import Erdos23Delta0.O14.SparseConeScaledFun",
        "",
        "namespace Erdos23Delta0",
        "namespace O14",
        "namespace CompactPilot",
        "namespace Chart000ScaledWeightFun",
        "",
        "set_option maxHeartbeats 0",
        "set_option maxRecDepth 2000000",
        "",
        f"def weightDenom : Nat := {weight_denom}",
        "",
        "def weight : Nat -> Nat",
        *equations,
        "",
        *facts,
        "",
        "theorem weightDenom_pos : 0 < weightDenom := by norm_num [weightDenom]",
        "",
        "end Chart000ScaledWeightFun",
        "end CompactPilot",
        "end O14",
        "end Erdos23Delta0",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return {"out": str(path), "bytes": path.stat().st_size}


def emit_shard(
    path: Path,
    namespace: str,
    selected: list[tuple[int, int]],
    prepared,
    terms_by_row: dict[int, list[tuple[int, Fraction]]],
    weight_denom: int,
    scaled_weights: list[int],
) -> dict[str, int | str]:
    lines = [
        "import Erdos23Delta0.O14.CompactPilot.Chart000ScaledWeightFun",
        "",
        "namespace Erdos23Delta0",
        "namespace O14",
        "namespace CompactPilot",
        f"namespace {namespace}",
        "",
        "open SparseConeScaledNat",
        "open SparseConeScaledFun",
        "open Chart000ScaledWeightFun",
        "open PolyCert",
        "",
        "set_option maxHeartbeats 0",
        "set_option maxRecDepth 2000000",
        "",
    ]
    occurrences = 0
    base_terms: list[str] = []
    base_nonneg_names: list[str] = []
    for global_index, beta_row in selected:
        scale, target, terms, _residual = scale_row(
            prepared.p_beta[beta_row],
            terms_by_row[beta_row],
            weight_denom,
            scaled_weights,
        )
        lines.extend([
            f"def row{global_index:04d} : Row :=",
            f"  {row_lean(scale, target, terms)}",
            "",
        ])
        expression = " + ".join(
            f"{intlean(scaled_weights[weight_id])} * {intlean(coeff)}"
            for weight_id, coeff in terms
        ) or intlean(0)
        lines.extend([
            f"theorem residual{global_index:04d}_nonneg :",
            f"    0 <= {intlean(target)} - ({expression}) := by",
            "  norm_num",
            "",
            f"theorem row{global_index:04d}_rational_nonneg :",
            f"    0 <= SparseConeScaledFun.residualRat weightDenom weight row{global_index:04d} := by",
            f"  apply SparseConeScaledFun.residualRat_nonneg_of_scaled weightDenom_pos",
            f"  simpa [row{global_index:04d}, SparseConeScaledFun.scaledResidual,",
            f"    SparseConeScaledFun.scaledWeightedSum] using",
            f"    residual{global_index:04d}_nonneg",
            "",
        ])
        beta = prepared.betas[beta_row]
        bernstein_factor = multinomial(sum(beta), beta)
        coeff_expr = (
            f"({bernstein_factor} : Rat) * "
            f"SparseConeScaledFun.residualRat weightDenom weight row{global_index:04d}"
        )
        base_terms.append(
            f"{{ coeff := {coeff_expr}, pows := {powslean(beta)} }}"
        )
        base_nonneg_names.append(f"row{global_index:04d}_rational_nonneg")
        occurrences += len(terms)
    base_text = ",\n  ".join(base_terms)
    nonneg_text = ", ".join(base_nonneg_names)
    lines.extend([
        "def baseTerms : NF := [",
        f"  {base_text}",
        "]",
        "",
        "theorem hbaseTerms : NF.allCoeffNonneg baseTerms = true := by",
        f"  simp [NF.allCoeffNonneg, baseTerms, {nonneg_text}]",
        "",
    ])
    lines.extend([
        f"end {namespace}",
        "end CompactPilot",
        "end O14",
        "end Erdos23Delta0",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return {
        "out": str(path),
        "rows": len(selected),
        "term_occurrences": occurrences,
        "bytes": path.stat().st_size,
    }


def emit_aggregator(path: Path, shard_count: int, ms_count: int = 45) -> dict[str, int | str]:
    direct_imports = [
        f"import Erdos23Delta0.O14.CompactPilot.Chart000ScaledDirect{shard:03d}"
        for shard in range(shard_count)
    ]
    ms_imports = [
        "import Erdos23Delta0.O14.Generated.ChartPayloads."
        f"Chart000ConeMS{shard:03d}"
        for shard in range(ms_count)
    ]
    direct_names = [f"Chart000ScaledDirect{shard:03d}" for shard in range(shard_count)]
    ms_names = [f"Generated.ChartPayloads.Chart000Cone.MS{shard:03d}" for shard in range(ms_count)]
    text = "\n".join([
        "import Erdos23Delta0.O14.Generated.ChartPayloads.Chart000ConeSupport",
        *direct_imports,
        *ms_imports,
        "",
        "namespace Erdos23Delta0",
        "namespace O14",
        "namespace CompactPilot",
        "namespace Chart000CompactCone",
        "",
        "open PolyCert",
        "open ODLFull",
        "open ConeEvalBridge",
        "",
        "set_option maxHeartbeats 0",
        "set_option maxRecDepth 2000000",
        "",
        "def baseShards : List NF := [",
        "  " + ",\n  ".join(f"{name}.baseTerms" for name in direct_names),
        "]",
        "",
        "theorem hbaseShards : baseShards.all NF.allCoeffNonneg = true := by",
        "  simp [baseShards, " + ", ".join(f"{name}.hbaseTerms" for name in direct_names) + "]",
        "",
        "def base : NF := baseShards.flatten",
        "",
        "theorem hbase : NF.allCoeffNonneg base = true := by",
        "  exact Generated.ChartPayloads.Chart000Cone.Support."
        "nf_allCoeffNonneg_flatten_true baseShards hbaseShards",
        "",
        "def multShards : List (List NF) := [",
        "  " + ",\n  ".join(f"{name}.mults" for name in ms_names),
        "]",
        "",
        "def slackShards : List (List NF) := [",
        "  " + ",\n  ".join(f"{name}.slacks" for name in ms_names),
        "]",
        "",
        "def mults : List NF := multShards.flatten",
        "def slacks : List NF := slackShards.flatten",
        "",
        "theorem hmultShards :",
        "    multShards.all (fun xs => xs.all NF.allCoeffNonneg) = true := by",
        "  simp [multShards, " + ", ".join(f"{name}.hmults" for name in ms_names) + "]",
        "",
        "theorem hmults : mults.all NF.allCoeffNonneg = true := by",
        "  exact Generated.ChartPayloads.Chart000Cone.Support."
        "all_nf_allCoeffNonneg_flatten_true multShards hmultShards",
        "",
        "theorem coreODLGoal_of_compactCone",
        "    {G : CertGraph.GraphData} {c : CertGraph.CutData}",
        "    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}",
        "    (core : ODLCoreData G c rows Q)",
        "    (target : NF) (env : Var -> Rat)",
        "    (hvars : forall v, 0 <= env v)",
        "    (hslacks : ∀ s ∈ slacks, 0 <= NF.eval env s)",
        "    (hidEval :",
        "      NF.eval env target = NF.eval env (comboNF base mults slacks))",
        "    (htarget : NF.eval env target = coreDefect core) :",
        "    CoreODLGoal G c rows Q core := by",
        "  exact coreODLGoal_of_coneEval core target base mults slacks env",
        "    hvars hbase hmults hslacks hidEval htarget",
        "",
        "end Chart000CompactCone",
        "end CompactPilot",
        "end O14",
        "end Erdos23Delta0",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return {"out": str(path), "bytes": path.stat().st_size}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, default=Path("tmp/codex_o14_v108_ledger_inventory.json"))
    parser.add_argument("--slot", type=int, default=0)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--chunk-size", type=int, default=64)
    parser.add_argument("--count", type=int)
    args = parser.parse_args()

    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    chart = next(rec for rec in inventory["rows"] if int(rec["slot"]) == args.slot)
    manifest = json.loads(Path(chart["manifest"]).read_text(encoding="utf-8"))
    prepared, columns, _matrix, _rhs = probe.build_lp(
        int(chart["chart"]), int(chart["dominant"]), chart["band"], manifest["support"]
    )
    solution = read_solution(Path(chart["solution_path"]))
    weight_index = {source_col: index for index, (source_col, _q) in enumerate(solution)}
    weight_denom = math.lcm(*(weight.denominator for _source_col, weight in solution))
    scaled_weights = [(weight * weight_denom).numerator for _source_col, weight in solution]

    terms_by_row: dict[int, list[tuple[int, Fraction]]] = defaultdict(list)
    active = {index for index, q in enumerate(prepared.p_beta) if q}
    for source_col, _weight in solution:
        for beta_row, coeff in columns[source_col].terms:
            terms_by_row[beta_row].append((weight_index[source_col], coeff))
            active.add(beta_row)
    ranked = sorted(active, key=lambda row: (-len(terms_by_row[row]), row))
    indexed = list(enumerate(ranked))
    if args.count is not None:
        indexed = indexed[:args.count]

    records = [emit_weight_fun(
        args.out_dir / "Chart000ScaledWeightFun.lean",
        weight_denom,
        scaled_weights,
    )]
    for shard, start in enumerate(range(0, len(indexed), args.chunk_size)):
        records.append(emit_shard(
            args.out_dir / f"Chart000ScaledDirect{shard:03d}.lean",
            f"Chart000ScaledDirect{shard:03d}",
            indexed[start : start + args.chunk_size],
            prepared,
            terms_by_row,
            weight_denom,
            scaled_weights,
        ))
    records.append(emit_aggregator(
        args.out_dir / "Chart000CompactCone.lean",
        (len(indexed) + args.chunk_size - 1) // args.chunk_size,
    ))
    print(json.dumps({
        "files": len(records),
        "rows": len(indexed),
        "term_occurrences": sum(int(rec.get("term_occurrences", 0)) for rec in records),
        "bytes": sum(int(rec["bytes"]) for rec in records),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
