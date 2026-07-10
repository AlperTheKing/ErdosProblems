#!/usr/bin/env python3
"""Emit denominator-cleared packed-integer O14 pilots.

The accepted v108 artifacts are read-only inputs.  Before any Lean source is
emitted, this script verifies the canonical inventory and ledger hashes, every
selected manifest/solution/check-summary hash, and a complete exact-Fraction
replay of the source matrix.  Sparse matrix entries are then serialized once
as balanced Lean `TermTree` values and checked one row at a time by ordinary
`decide`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


THIS = Path(__file__).resolve()
ROOT = THIS.parents[3]
LEAN_SRC = ROOT / "problems/23/lean"
PAYLOAD_DIR = LEAN_SRC / "Erdos23Delta0/O14/Generated/ChartPayloads"
sys.path.insert(0, str(THIS.parent))

import _codex_eq_odl1_rung2_scipy_core_probe as probe
import _codex_eq_odl1_rung2_source_solution_check as exact_check


CANONICAL_INVENTORY_SHA256 = (
    "98320beafead44485dd861bd441ea2052e361a52f0b5460e7e111a79a60819d6"
)
CANONICAL_LEDGER_SHA256 = (
    "981d353f88c8148dec975df75cbedcc4975505f2adf2345e6a6a9329fd3bd1af"
)
DEFAULT_SLOTS = (0, 66, 107)
MANIFEST_SCHEMA = "eq_odl1_rung2_source_certificate_manifest_v1"
CHECK_SCHEMA = "eq_odl1_rung2_source_solution_check_v1"
INVENTORY_SCHEMA = "codex_o14_v108_ledger_inventory_v1"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_input(path: Path | str) -> Path:
    value = Path(path)
    return value if value.is_absolute() else ROOT / value


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def write_text(path: Path, text: str) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def parse_slots(raw: str) -> list[int]:
    slots = sorted({int(part.strip()) for part in raw.split(",") if part.strip()})
    require(slots, "at least one slot is required")
    require(all(0 <= slot < 108 for slot in slots), "slot outside [0, 107]")
    return slots


def read_solution(path: Path) -> tuple[dict[int, Fraction], int]:
    values: dict[int, Fraction] = {}
    records = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            record = json.loads(line)
            require(isinstance(record, dict), f"bad solution row {line_number}")
            source_col = int(record["source_col"])
            value = Fraction(int(record["num"]), int(record["den"]))
            values[source_col] = values.get(source_col, Fraction(0)) + value
            records += 1
    values = {source_col: value for source_col, value in values.items() if value}
    return values, records


def multinomial(total: int, exponents: tuple[int, ...]) -> int:
    result = math.factorial(total)
    for exponent in exponents:
        result //= math.factorial(exponent)
    return result


def int_lean(value: int) -> str:
    return f"({value} : Int)"


def pows_lean(exponents: tuple[int, ...]) -> str:
    entries = ", ".join(
        f"({index}, {exponent})"
        for index, exponent in enumerate(exponents)
        if exponent
    )
    return f"[{entries}]"


def tree_lean(terms: list[tuple[int, int]]) -> str:
    if not terms:
        return "TermTree.empty"
    if len(terms) == 1:
        weight_id, coeff = terms[0]
        return (
            "(TermTree.leaf { weightId := "
            f"{weight_id}, coeff := {int_lean(coeff)} }})"
        )
    middle = len(terms) // 2
    return (
        "(TermTree.node "
        + tree_lean(terms[:middle])
        + " "
        + tree_lean(terms[middle:])
        + ")"
    )

def weight_tree_lean(values: list[int]) -> str:
    if not values:
        return "WeightTree.empty"
    if len(values) == 1:
        return f"(WeightTree.leaf {values[0]})"
    middle = len(values) // 2
    return (
        f"(WeightTree.node {middle} "
        + weight_tree_lean(values[:middle]) + " "
        + weight_tree_lean(values[middle:]) + ")"
    )


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def target_beta_for_manifest(manifest: dict[str, Any], prepared: Any) -> list[Fraction]:
    raw_path = manifest.get("target_beta_json")
    if not raw_path:
        return list(prepared.p_beta)
    target_path = resolve_input(raw_path)
    pinned = manifest.get("target_beta_json_sha256")
    require(pinned, "custom target is missing target_beta_json_sha256")
    require(sha256_file(target_path) == str(pinned).lower(), "custom target hash mismatch")
    return exact_check.read_target_beta(target_path, len(prepared.p_beta))


def discover_ms(slot: int) -> list[tuple[str, str]]:
    prefix = f"Chart{slot:03d}ConeMS"
    found: list[tuple[int, str, str]] = []
    for path in PAYLOAD_DIR.glob(f"{prefix}*.lean"):
        match = re.fullmatch(rf"{prefix}(\d+)\.lean", path.name)
        if match:
            index = int(match.group(1))
            module = f"Erdos23Delta0.O14.Generated.ChartPayloads.{path.stem}"
            reference = (
                f"Generated.ChartPayloads.Chart{slot:03d}Cone.MS{index:03d}"
            )
            found.append((index, module, reference))
    found.sort()
    require(found, f"no multiplier/slack shards found for slot {slot}")
    require(
        [index for index, _, _ in found] == list(range(len(found))),
        f"non-contiguous multiplier/slack shards for slot {slot}",
    )
    return [(module, reference) for _, module, reference in found]


def replay_slot(
    inventory_row: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[int], int]:
    slot = int(inventory_row["slot"])
    manifest_path = resolve_input(inventory_row["manifest"])
    solution_path = resolve_input(inventory_row["solution_path"])
    check_path = resolve_input(inventory_row["check_summary_path"])

    actual_manifest_sha = sha256_file(manifest_path)
    actual_solution_sha = sha256_file(solution_path)
    actual_check_sha = sha256_file(check_path)
    require(
        actual_manifest_sha == str(inventory_row["manifest_sha256"]).lower(),
        f"slot {slot}: inventory manifest SHA mismatch",
    )
    require(
        actual_solution_sha == str(inventory_row["solution_sha256"]).lower(),
        f"slot {slot}: inventory solution SHA mismatch",
    )
    require(
        actual_check_sha == str(inventory_row["check_summary_sha256"]).lower(),
        f"slot {slot}: inventory check-summary SHA mismatch",
    )

    manifest = read_json(manifest_path)
    accepted = read_json(check_path)
    require(manifest.get("schema") == MANIFEST_SCHEMA, f"slot {slot}: manifest schema")
    require(accepted.get("schema") == CHECK_SCHEMA, f"slot {slot}: check schema")
    require(manifest.get("exact_ok") is True, f"slot {slot}: manifest not exact")
    require(accepted.get("exact_ok") is True, f"slot {slot}: check not exact")
    require(
        str(manifest.get("solution_jsonl_sha256", "")).lower() == actual_solution_sha,
        f"slot {slot}: manifest solution SHA mismatch",
    )
    require(
        str(manifest.get("check_summary_sha256", "")).lower() == actual_check_sha,
        f"slot {slot}: manifest check-summary SHA mismatch",
    )

    chart = int(inventory_row["chart"])
    dominant = int(inventory_row["dominant"])
    band = str(inventory_row["band"])
    support = str(manifest["support"])
    require(int(manifest["chart"]) == chart, f"slot {slot}: chart mismatch")
    require(int(manifest["dominant"]) == dominant, f"slot {slot}: dominant mismatch")
    require(str(manifest["band"]) == band, f"slot {slot}: band mismatch")

    prepared, columns, _matrix, _rhs = probe.build_lp(chart, dominant, band, support)
    target_beta = target_beta_for_manifest(manifest, prepared)
    solution, solution_records = read_solution(solution_path)
    require(solution, f"slot {slot}: empty source solution")
    require(all(value >= 0 for value in solution.values()), f"slot {slot}: negative weight")
    require(
        solution_records == int(manifest["solution_jsonl_records"]),
        f"slot {slot}: solution record count mismatch",
    )
    require(
        len(solution) == int(manifest["nonzero_source_columns"]),
        f"slot {slot}: nonzero source-column count mismatch",
    )
    require(len(columns) == int(manifest["columns_checked"]), f"slot {slot}: columns")
    require(all(0 <= source_col < len(columns) for source_col in solution), "bad column id")

    ordered_solution = sorted(solution.items())
    weight_index = {
        source_col: index for index, (source_col, _value) in enumerate(ordered_solution)
    }
    weight_denom = math.lcm(*(value.denominator for _, value in ordered_solution))
    scaled_weights = [
        int(value * weight_denom) for _, value in ordered_solution
    ]
    require(
        all(Fraction(value, weight_denom) == ordered_solution[index][1]
            for index, value in enumerate(scaled_weights)),
        f"slot {slot}: weight reconstruction failed",
    )

    terms_by_row: dict[int, dict[int, Fraction]] = defaultdict(dict)
    for source_col, _value in ordered_solution:
        weight_id = weight_index[source_col]
        for row_index, coeff in columns[source_col].terms:
            prior = terms_by_row[row_index].get(weight_id, Fraction(0))
            terms_by_row[row_index][weight_id] = prior + coeff
    for row_index in list(terms_by_row):
        terms_by_row[row_index] = {
            weight_id: coeff
            for weight_id, coeff in terms_by_row[row_index].items()
            if coeff
        }
        if not terms_by_row[row_index]:
            del terms_by_row[row_index]

    residual = list(target_beta)
    for source_col, weight in ordered_solution:
        for row_index, coeff in columns[source_col].terms:
            residual[row_index] -= weight * coeff

    negative = [index for index, value in enumerate(residual) if value < 0]
    zero_count = sum(value == 0 for value in residual)
    require(not negative, f"slot {slot}: exact replay has negative residuals")
    require(
        int(accepted["full_negative_residual_count"]) == len(negative),
        f"slot {slot}: accepted negative-residual count mismatch",
    )
    require(
        int(accepted["full_zero_residual_count"]) == zero_count,
        f"slot {slot}: accepted zero-residual count mismatch",
    )
    require(
        int(accepted["solution_negative_count"]) == 0,
        f"slot {slot}: accepted solution-negative count mismatch",
    )
    require(
        int(accepted["nonzero_source_columns"]) == len(solution),
        f"slot {slot}: accepted source-column count mismatch",
    )
    require(int(accepted["columns"]) == len(columns), f"slot {slot}: accepted columns")
    if "target_beta_nonzero_count" in accepted:
        require(
            int(accepted["target_beta_nonzero_count"])
            == sum(value != 0 for value in target_beta),
            f"slot {slot}: target nonzero count mismatch",
        )

    active_rows = sorted(
        set(index for index, value in enumerate(target_beta) if value)
        | set(terms_by_row)
        | set(index for index, value in enumerate(residual) if value)
    )
    active_rows.sort(key=lambda index: (-len(terms_by_row.get(index, {})), index))

    emitted_rows: list[dict[str, Any]] = []
    reconstruction_digest = hashlib.sha256()
    reconstructed_terms = 0
    for certificate_index, row_index in enumerate(active_rows):
        rational_terms = sorted(terms_by_row.get(row_index, {}).items())
        row_scale = target_beta[row_index].denominator
        for _weight_id, coeff in rational_terms:
            row_scale = math.lcm(row_scale, coeff.denominator)
        target_integer_q = target_beta[row_index] * weight_denom * row_scale
        require(target_integer_q.denominator == 1, f"slot {slot}: target scale")
        integer_terms: list[tuple[int, int]] = []
        integer_sum = 0
        for weight_id, coeff in rational_terms:
            coeff_integer_q = coeff * row_scale
            require(coeff_integer_q.denominator == 1, f"slot {slot}: coeff scale")
            coeff_integer = coeff_integer_q.numerator
            integer_terms.append((weight_id, coeff_integer))
            integer_sum += scaled_weights[weight_id] * coeff_integer
            require(
                Fraction(scaled_weights[weight_id], weight_denom)
                * Fraction(coeff_integer, row_scale)
                == ordered_solution[weight_id][1] * coeff,
                f"slot {slot}: term reconstruction failed at row {row_index}",
            )
        target_integer = target_integer_q.numerator
        residual_integer = target_integer - integer_sum
        require(residual_integer >= 0, f"slot {slot}: integer residual negative")
        require(
            Fraction(target_integer, weight_denom * row_scale)
            == target_beta[row_index],
            f"slot {slot}: target reconstruction failed at row {row_index}",
        )
        require(
            Fraction(residual_integer, weight_denom * row_scale)
            == residual[row_index],
            f"slot {slot}: residual reconstruction failed at row {row_index}",
        )
        beta = tuple(int(value) for value in prepared.betas[row_index])
        factor = multinomial(sum(beta), beta)
        emitted_rows.append({
            "certificate_index": certificate_index,
            "source_row": row_index,
            "scale": row_scale,
            "target": target_integer,
            "terms": integer_terms,
            "residual": residual_integer,
            "beta": beta,
            "factor": factor,
        })
        reconstructed_terms += len(integer_terms)
        reconstruction_digest.update(
            (
                f"{row_index}|{row_scale}|{target_integer}|{residual_integer}|"
                f"{factor}|{beta}|{integer_terms}\n"
            ).encode("ascii")
        )

    omitted = set(range(len(target_beta))) - set(active_rows)
    require(
        all(target_beta[index] == 0 and residual[index] == 0
            and index not in terms_by_row for index in omitted),
        f"slot {slot}: omitted row is not identically zero",
    )
    summary = {
        "slot": slot,
        "chart": chart,
        "dominant": dominant,
        "dominant_name": inventory_row.get("dominant_name"),
        "band": band,
        "support": support,
        "manifest": str(manifest_path.relative_to(ROOT)),
        "manifest_sha256": actual_manifest_sha,
        "solution": str(solution_path.relative_to(ROOT)),
        "solution_sha256": actual_solution_sha,
        "check_summary": str(check_path.relative_to(ROOT)),
        "check_summary_sha256": actual_check_sha,
        "solution_records": solution_records,
        "weights": len(scaled_weights),
        "weight_denom_bits": weight_denom.bit_length(),
        "max_scaled_weight_bits": max(value.bit_length() for value in scaled_weights),
        "matrix_rows": len(target_beta),
        "active_rows": len(emitted_rows),
        "omitted_zero_rows": len(omitted),
        "term_occurrences": reconstructed_terms,
        "max_terms_per_row": max(len(row["terms"]) for row in emitted_rows),
        "full_zero_residual_count": zero_count,
        "full_min_residual": fraction_text(min(residual)),
        "full_max_residual": fraction_text(max(residual)),
        "weight_reconstruction_equal": True,
        "target_reconstruction_equal": True,
        "term_reconstruction_equal": True,
        "residual_reconstruction_equal": True,
        "accepted_summary_counts_equal": True,
        "reconstruction_sha256": reconstruction_digest.hexdigest(),
    }
    return summary, emitted_rows, scaled_weights, weight_denom


def namespace_lines(slot: int, leaf: str) -> tuple[list[str], list[str]]:
    opens = [
        "namespace Erdos23Delta0",
        "namespace O14",
        "namespace PackedIntPilot",
        f"namespace Chart{slot:03d}",
        f"namespace {leaf}",
    ]
    closes = [
        f"end {leaf}",
        f"end Chart{slot:03d}",
        "end PackedIntPilot",
        "end O14",
        "end Erdos23Delta0",
    ]
    return opens, closes


def emit_weights(
    path: Path,
    slot_summary: dict[str, Any],
    weight_denom: int,
    scaled_weights: list[int],
) -> dict[str, Any]:
    slot = int(slot_summary["slot"])
    opens, closes = namespace_lines(slot, "Weights")
    values = weight_tree_lean(scaled_weights)
    lines = [
        "/- Generated temporary packed-integer pilot; not a production payload. -/",
        "import Erdos23Delta0.O14.SparseConePackedInt",
        "",
        *opens,
        "",
        "open SparseConePackedInt",
        "",
        "set_option maxHeartbeats 0",
        "set_option maxRecDepth 1000000",
        "",
        f'def manifestSha256 : String := "{slot_summary["manifest_sha256"]}"',
        f'def solutionSha256 : String := "{slot_summary["solution_sha256"]}"',
        f"def weightDenom : Nat := {weight_denom}",
        f"def weightCount : Nat := {len(scaled_weights)}",
        "def weights : WeightTree :=",
        f"  {values}",
        "",
        "theorem weightDenom_pos : 0 < weightDenom := by",
        "  norm_num [weightDenom]",
        "",
        *closes,
        "",
    ]
    return write_text(path, "\n".join(lines))


def emit_rows_shard(
    path: Path,
    slot: int,
    shard_index: int,
    selected: list[dict[str, Any]],
) -> dict[str, Any]:
    leaf = f"Rows{shard_index:03d}"
    opens, closes = namespace_lines(slot, leaf)
    weight_module = (
        f"Erdos23Delta0.O14.PackedIntPilot.Chart{slot:03d}.Weights"
    )
    lines = [
        "/- Generated temporary packed-integer pilot; not a production payload. -/",
        f"import {weight_module}",
        "",
        *opens,
        "",
        "open SparseConePackedInt",
        "open PolyCert",
        f"open Chart{slot:03d}.Weights",
        "",
        "set_option maxHeartbeats 0",
        "set_option maxRecDepth 1000000",
        "",
    ]
    theorem_names: list[str] = []
    row_names: list[str] = []
    for record in selected:
        index = int(record["certificate_index"])
        row_name = f"row{index:05d}"
        theorem_name = f"{row_name}_checked"
        row_names.append(row_name)
        theorem_names.append(theorem_name)
        lines.extend([
            f"def {row_name} : Row :=",
            "  { scalePred := " + str(int(record["scale"]) - 1),
            "    target := " + int_lean(int(record["target"])),
            "    terms := " + tree_lean(record["terms"]) + " }",
            "",
            f"theorem {theorem_name} : checkRow weightCount weights {row_name} = true := by decide",
            "",
        ])
    nf_entries = []
    for record, row_name in zip(selected, row_names):
        nf_entries.append(
            "{ row := " + row_name
            + ", factor := " + str(record["factor"])
            + ", pows := " + pows_lean(record["beta"])
            + " }"
        )
    lines.extend([
        "def nfRows : List NFRow := [",
        "  " + ",\n  ".join(nf_entries),
        "]",
        "",
        "theorem rows_checked : checkRows weightCount weights nfRows = true := by",
        "  simp [checkRows, nfRows, " + ", ".join(theorem_names) + "]",
        "",
        "def baseTerms : NF := base weightDenom weights nfRows",
        "",
        "theorem hbaseTerms : NF.allCoeffNonneg baseTerms = true := by",
        "  exact base_allCoeffNonneg_of_checkRows weightDenom_pos rows_checked",
        "",
        *closes,
        "",
    ])
    result = write_text(path, "\n".join(lines))
    result.update({
        "rows": len(selected),
        "term_occurrences": sum(len(record["terms"]) for record in selected),
        "max_terms": max((len(record["terms"]) for record in selected), default=0),
    })
    return result


def emit_cone(
    path: Path,
    slot: int,
    shard_count: int,
    ms_modules: list[tuple[str, str]],
) -> dict[str, Any]:
    row_modules = [
        f"Erdos23Delta0.O14.PackedIntPilot.Chart{slot:03d}.Rows{index:03d}"
        for index in range(shard_count)
    ]
    row_refs = [
        f"Chart{slot:03d}.Rows{index:03d}" for index in range(shard_count)
    ]
    imports = [f"import {module}" for module in row_modules]
    imports.extend(f"import {module}" for module, _reference in ms_modules)
    opens, closes = namespace_lines(slot, "Cone")
    ms_refs = [reference for _module, reference in ms_modules]
    lines = [
        "/- Generated temporary packed-integer pilot; not a production payload. -/",
        *imports,
        "",
        *opens,
        "",
        "open PolyCert",
        "open ODLFull",
        "open ConeEvalBridge",
        "open SparseConePackedInt",
        f"open Chart{slot:03d}.Weights",
        "",
        "set_option maxHeartbeats 0",
        "set_option maxRecDepth 1000000",
        "",
        "def baseShards : List NF := [",
        "  " + ",\n  ".join(f"{ref}.baseTerms" for ref in row_refs),
        "]",
        "",
        "theorem hbaseShards : baseShards.all NF.allCoeffNonneg = true := by",
        "  simp [baseShards, "
        + ", ".join(f"{ref}.hbaseTerms" for ref in row_refs)
        + "]",
        "",
        "def packedBase : NF := baseShards.flatten",
        "",
        "theorem hbase : NF.allCoeffNonneg packedBase = true := by",
        "  exact allCoeffNonneg_flatten baseShards hbaseShards",
        "",
        "def multShards : List (List NF) := [",
        "  " + ",\n  ".join(f"{ref}.mults" for ref in ms_refs),
        "]",
        "",
        "def slackShards : List (List NF) := [",
        "  " + ",\n  ".join(f"{ref}.slacks" for ref in ms_refs),
        "]",
        "",
        "def mults : List NF := multShards.flatten",
        "def slacks : List NF := slackShards.flatten",
        "",
        "theorem hmultShards :",
        "    multShards.all (fun shard => shard.all NF.allCoeffNonneg) = true := by",
        "  simp [multShards, "
        + ", ".join(f"{ref}.hmults" for ref in ms_refs)
        + "]",
        "",
        "theorem hmults : mults.all NF.allCoeffNonneg = true := by",
        "  exact all_allCoeffNonneg_flatten multShards hmultShards",
        "",
        "theorem coreODLGoal_of_packedInt",
        "    {G : CertGraph.GraphData} {c : CertGraph.CutData}",
        "    {rows : CertGraph.RowDB} {Q : CertGraph.RowCert}",
        "    (core : ODLCoreData G c rows Q)",
        "    (target : NF) (env : Var -> Rat)",
        "    (hvars : forall v, 0 <= env v)",
        "    (hslacks : forall s, s ∈ slacks -> 0 <= NF.eval env s)",
        "    (hidEval :",
        "      NF.eval env target = NF.eval env (comboNF packedBase mults slacks))",
        "    (htarget : NF.eval env target = coreDefect core) :",
        "    CoreODLGoal G c rows Q core := by",
        "  exact coreODLGoal_of_coneEval core target packedBase mults slacks env",
        "    hvars hbase hmults hslacks hidEval htarget",
        "",
        *closes,
        "",
    ]
    result = write_text(path, "\n".join(lines))
    result["ms_shards"] = len(ms_modules)
    return result


def emit_probe(path: Path, slot: int) -> dict[str, Any]:
    module = f"Erdos23Delta0.O14.PackedIntPilot.Chart{slot:03d}.Cone"
    theorem = (
        f"Erdos23Delta0.O14.PackedIntPilot.Chart{slot:03d}.Cone."
        "coreODLGoal_of_packedInt"
    )
    lines = [
        f"import {module}",
        "",
        "#print axioms Erdos23Delta0.O14.SparseConePackedInt.residualRat_nonneg_of_checkRow",
        "#print axioms Erdos23Delta0.O14.SparseConePackedInt.coreODLGoal_of_packedRows",
        f"#print axioms {theorem}",
        "",
    ]
    return write_text(path, "\n".join(lines))


def emit_slot(
    out_dir: Path,
    inventory_row: dict[str, Any],
    chunk_size: int,
) -> dict[str, Any]:
    slot_summary, rows, scaled_weights, weight_denom = replay_slot(inventory_row)
    slot = int(slot_summary["slot"])
    slot_dir = (
        out_dir / "src/Erdos23Delta0/O14/PackedIntPilot" / f"Chart{slot:03d}"
    )
    slot_dir.mkdir(parents=True, exist_ok=True)
    for stale in slot_dir.glob("*.lean"):
        stale.unlink()

    files: list[dict[str, Any]] = []
    files.append(emit_weights(
        slot_dir / "Weights.lean", slot_summary, weight_denom, scaled_weights
    ))
    shard_count = (len(rows) + chunk_size - 1) // chunk_size
    for shard_index, start in enumerate(range(0, len(rows), chunk_size)):
        files.append(emit_rows_shard(
            slot_dir / f"Rows{shard_index:03d}.lean",
            slot,
            shard_index,
            rows[start : start + chunk_size],
        ))
    ms_modules = discover_ms(slot)
    files.append(emit_cone(slot_dir / "Cone.lean", slot, shard_count, ms_modules))
    files.append(emit_probe(slot_dir / "Probe.lean", slot))
    slot_summary.update({
        "chunk_size": chunk_size,
        "row_shards": shard_count,
        "ms_shards": len(ms_modules),
        "emitted_files": len(files),
        "emitted_source_bytes": sum(int(record["bytes"]) for record in files),
        "files": files,
    })
    return slot_summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inventory",
        type=Path,
        default=ROOT / "tmp/codex_o14_v108_ledger_inventory.json",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=ROOT / "tmp/eq_odl1_rung2_chart_batch_ledger_v108_codex.json",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "tmp/o14_packed_int_pilot",
    )
    parser.add_argument("--slots", default=",".join(map(str, DEFAULT_SLOTS)))
    parser.add_argument("--chunk-size", type=int, default=64)
    args = parser.parse_args()

    inventory_path = resolve_input(args.inventory)
    ledger_path = resolve_input(args.ledger)
    out_dir = resolve_input(args.out_dir)
    slots = parse_slots(args.slots)
    require(1 <= args.chunk_size <= 128, "chunk size must be in [1, 128]")

    inventory_sha = sha256_file(inventory_path)
    ledger_sha = sha256_file(ledger_path)
    require(inventory_sha == CANONICAL_INVENTORY_SHA256, "canonical inventory SHA mismatch")
    require(ledger_sha == CANONICAL_LEDGER_SHA256, "canonical v108 ledger SHA mismatch")
    inventory = read_json(inventory_path)
    require(inventory.get("schema") == INVENTORY_SCHEMA, "inventory schema mismatch")
    inventory_rows = inventory.get("rows")
    require(isinstance(inventory_rows, list), "inventory rows missing")
    require(len(inventory_rows) == 108, "accepted inventory must contain 108 rows")
    by_slot = {int(record["slot"]): record for record in inventory_rows}
    require(len(by_slot) == 108, "inventory slots are not unique")

    out_dir.mkdir(parents=True, exist_ok=True)
    emitted = [emit_slot(out_dir, by_slot[slot], args.chunk_size) for slot in slots]
    summary = {
        "schema": "o14_packed_int_pilot_emit_v1",
        "accepted_v108": True,
        "inventory": str(inventory_path.relative_to(ROOT)),
        "inventory_sha256": inventory_sha,
        "ledger": str(ledger_path.relative_to(ROOT)),
        "ledger_sha256": ledger_sha,
        "slots": slots,
        "chunk_size": args.chunk_size,
        "charts": emitted,
        "total_emitted_source_bytes": sum(
            int(record["emitted_source_bytes"]) for record in emitted
        ),
    }
    summary_path = out_dir / "emit_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "summary": str(summary_path.relative_to(ROOT)),
        "inventory_sha256": inventory_sha,
        "ledger_sha256": ledger_sha,
        "slots": slots,
        "source_bytes": summary["total_emitted_source_bytes"],
        "reconstruction_ok": all(
            chart["residual_reconstruction_equal"] for chart in emitted
        ),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
