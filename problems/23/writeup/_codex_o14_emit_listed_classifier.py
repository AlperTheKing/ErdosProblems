#!/usr/bin/env python3
"""Emit the O14 listed-shape classifier from the accepted v108 ledger.

This is intentionally a supplement to the pilot Generated/Classifier.lean.
It does not claim that every bounded `O14Shape` is covered.  Instead it
defines the 108 certified `(kIdx,dIdx)` pairs and a classifier on the subtype
of EQ-ODL1 instances whose shape is one of those pairs.  The graph/route
semantic extraction layer must still prove that real EQ-ODL1 shapes land in
this listed subtype.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "tmp/eq_odl1_rung2_chart_batch_ledger_v108_codex.json"
OUT = ROOT / "problems/23/lean/Erdos23Delta0/O14/Generated/ListedClassifier.lean"


def fin_slot(slot: int) -> str:
    return f"⟨{slot}, by norm_num [EQODL1CoverInterface.ChartCount]⟩"


def main() -> int:
    with LEDGER.open("r", encoding="utf-8") as f:
        ledger = json.load(f)
    rows = sorted(ledger["certified_rows"], key=lambda r: int(r["numeric_order"]))
    if len(rows) != 108:
        raise SystemExit(f"expected 108 rows, got {len(rows)}")

    pairs: set[tuple[int, int]] = set()
    for slot, row in enumerate(rows):
        if int(row["numeric_order"]) != slot:
            raise SystemExit(f"numeric_order mismatch at slot {slot}: {row['numeric_order']}")
        pair = (int(row["chart"]), int(row["dominant"]))
        if pair in pairs:
            raise SystemExit(f"duplicate chart/dominant pair {pair}")
        pairs.add(pair)

    domain_defs: list[str] = []
    pair_props: list[str] = []
    if_lines: list[str] = []
    for slot, row in enumerate(rows):
        k = int(row["chart"])
        d = int(row["dominant"])
        dom = f"listedDomain{slot:03d}"
        domain_defs.append(
            f"/-- Certified v108 slot {slot}: k={k}, dominant={d}. -/\n"
            f"def {dom} (s : O14Shape) : Bool :=\n"
            f"  natEqB s.kIdx {k} && natEqB s.dIdx {d}\n"
        )
        pair_props.append(f"(s.kIdx = {k} ∧ s.dIdx = {d})")
        if slot == 0:
            if_lines.append(f"  if {dom} s then {fin_slot(slot)}")
        else:
            if_lines.append(f"  else if {dom} s then {fin_slot(slot)}")
    if_lines.append(f"  else {fin_slot(0)}")

    listed_prop = "\n    ∨ ".join(pair_props)

    text = f"""import Erdos23Delta0.O14.Generated.ChartKeys

/-!
# O14 listed-shape classifier

Generated from the accepted v108 ledger.  Unlike the pilot classifier, this
module does not pretend that the bound predicate alone covers exactly the 108
certified charts.  It classifies only the subtype of instances whose
`O14Shape` has one of the certified `(kIdx,dIdx)` pairs.
-/

namespace Erdos23Delta0
namespace O14
namespace Generated

open CertGraph
open ODLFull
open EQODL1CoverInterface

{chr(10).join(domain_defs)}
/-- Propositional listed-shape predicate for the 108 certified ledger slots. -/
def ListedShape (s : O14Shape) : Prop :=
  {listed_prop}

/-- Certified slot lookup.  Unlisted shapes default to slot 0; downstream code
uses this only on `ListedShapeInst`, where the semantic layer supplies the
listed-shape proof. -/
def certifiedPairSlot (s : O14Shape) : Fin ChartCount :=
{chr(10).join(if_lines)}

/-- Numeric chart slot of a listed shape. -/
def chartOfListedShape (s : O14Shape) : Nat :=
  (certifiedPairSlot s).val

theorem chartOfListedShape_lt (s : O14Shape) :
    chartOfListedShape s < ChartCount :=
  (certifiedPairSlot s).isLt

/-- EQ-ODL1 instances whose structural shape is one of the 108 certified
ledger slots.  Proving that real EQ-ODL1 instances inhabit this subtype is the
remaining structural extraction/coverage obligation. -/
structure ListedShapeInst (G : GraphData) (c : CutData) (rows : RowDB)
    (Q : RowCert) where
  inst : EQODL1ShapeInst G c rows Q
  listed : ListedShape inst.shape

/-- Core accessor for the listed-instance subtype. -/
def listedCore {{G : GraphData}} {{c : CutData}} {{rows : RowDB}} {{Q : RowCert}}
    (I : ListedShapeInst G c rows Q) : ODLCoreData G c rows Q :=
  I.inst.core

/-- The total classifier on listed EQ-ODL1 instances. -/
def listedClassifier {{G : GraphData}} {{c : CutData}} {{rows : RowDB}} {{Q : RowCert}} :
    EQODL1Classifier (ListedShapeInst G c rows Q) := {{
  chartOf := fun I => chartOfListedShape I.inst.shape,
  chartOf_lt := fun I => chartOfListedShape_lt I.inst.shape
}}

end Generated
end O14
end Erdos23Delta0
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
