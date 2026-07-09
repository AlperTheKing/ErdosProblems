#!/usr/bin/env python3
"""Emit O14 generated BridgeRegistry.lean.

The registry is the data-free module-29 dispatcher layer between:

* the 108 generated `ChartNNNBridge` theorem wrappers, and
* `EQODL1CoverInterface.EQODL1ChartSound`.

It does not construct semantic bindings.  Instead, it names the exact per-chart
env/slack/combo/target obligations that the route/shape layer must supply.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "problems/23/lean/Erdos23Delta0/O14/Generated/BridgeRegistry.lean"


def imports() -> str:
    lines = ["import Erdos23Delta0.O14.Generated.PayloadRegistry"]
    for i in range(108):
        lines.append(f"import Erdos23Delta0.O14.Generated.ChartPayloads.Chart{i:03d}Bridge")
    return "\n".join(lines)


def fields() -> str:
    chunks: list[str] = []
    for i in range(108):
        chart = f"Chart{i:03d}Cone"
        prefix = f"chart{i:03d}"
        chunks.append(
            f"""  {prefix}Env : Inst → Var → ℚ
  {prefix}_hvars :
    ∀ I, C.chartOf I = {i} → ∀ v, 0 ≤ {prefix}Env I v
  {prefix}_hslacks :
    ∀ I, C.chartOf I = {i} →
      ∀ s ∈ ChartPayloads.{chart}.Main.slacks,
        0 ≤ NF.eval ({prefix}Env I) s
  {prefix}_hcombo :
    ∀ I, C.chartOf I = {i} →
      NF.eval ({prefix}Env I)
        ((ChartPayloads.{chart}.Main.pairs.map Prod.snd).flatten) =
      NF.eval ({prefix}Env I)
        (comboNF ChartPayloads.{chart}.Main.base
          ChartPayloads.{chart}.Main.mults
          ChartPayloads.{chart}.Main.slacks)
  {prefix}_htarget :
    ∀ I, C.chartOf I = {i} →
      NF.eval ({prefix}Env I)
        ((ChartPayloads.{chart}.Main.pairs.map Prod.fst).flatten) =
      coreDefect (coreOf I)"""
        )
    return "\n".join(chunks)


def exact_case(i: int, indent: str) -> str:
    prefix = f"chart{i:03d}"
    bridge = f"Chart{i:03d}Bridge"
    return f"""{indent}exact
{indent}  ChartPayloads.{bridge}.coreODLGoal_of_chart{i:03d}Cone
{indent}    (coreOf I) (P.{prefix}Env I)
{indent}    (P.{prefix}_hvars I hchart)
{indent}    (P.{prefix}_hslacks I hchart)
{indent}    (P.{prefix}_hcombo I hchart)
{indent}    (P.{prefix}_htarget I hchart)"""


def cases_tree() -> str:
    lines: list[str] = []
    indent = "    "
    for i in range(108):
        if i == 0:
            lines.append(f"{indent}cases i with")
        else:
            lines.append(f"{indent}| succ i =>")
            indent += "  "
            lines.append(f"{indent}cases i with")
        lines.append(f"{indent}| zero =>")
        lines.append(exact_case(i, indent + "  "))
    lines.append(f"{indent}| succ i =>")
    lines.append(f"{indent}  simp [EQODL1CoverInterface.ChartCount] at hi")
    return "\n".join(lines)


def main() -> int:
    text = f"""{imports()}

/-!
# Generated O14 chart bridge registry

This module packages the 108 generated chart bridge wrappers into the
`EQODL1ChartSound` interface.  It is still data-free: the semantic route/shape
layer must instantiate `ChartBridgeInputs` by providing the exact env,
nonnegativity, combo, and target/core-defect identities for the chart selected
by the classifier.
-/

namespace Erdos23Delta0
namespace O14
namespace Generated

open ODLFull
open PolyCert
open EQODL1CoverInterface

/-- Per-chart semantic bindings needed to use the generated cone witnesses.
The fields are intentionally chart-specific because every chart has its own
generated slack and pair arrays. -/
structure ChartBridgeInputs
    {{G : CertGraph.GraphData}} {{c : CertGraph.CutData}}
    {{rows : CertGraph.RowDB}} {{Q : CertGraph.RowCert}}
    {{Inst : Type*}}
    (coreOf : Inst → ODLCoreData G c rows Q)
    (C : EQODL1Classifier Inst) where
{fields()}

/-- The generated chart bridges give the `EQODL1ChartSound` provider once the
semantic binding layer supplies `ChartBridgeInputs`. -/
theorem chartSound_of_bridgeInputs
    {{G : CertGraph.GraphData}} {{c : CertGraph.CutData}}
    {{rows : CertGraph.RowDB}} {{Q : CertGraph.RowCert}}
    {{Inst : Type*}}
    {{coreOf : Inst → ODLCoreData G c rows Q}}
    {{C : EQODL1Classifier Inst}}
    (P : ChartBridgeInputs coreOf C) :
    EQODL1ChartSound Inst
      (fun I => CoreODLGoal G c rows Q (coreOf I))
      C v108Payload where
  sound := by
    intro i hi _hp I hchart
{cases_tree()}

#print axioms chartSound_of_bridgeInputs

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
