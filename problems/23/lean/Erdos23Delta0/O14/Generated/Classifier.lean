import Erdos23Delta0.O14.Generated.ChartKeys

/-!
# O14 classifier: pilot scaffold

The production classifier will dispatch over all 108 generated domains.  This
pilot module routes only the accepted numeric-order-0 domain to chart slot `0`;
all other shapes also default to `0`, so this is intentionally not a final
coverage theorem.
-/

namespace Erdos23Delta0
namespace O14
namespace Generated

open EQODL1CoverInterface

/-- Pilot classifier slot.  Final generated code replaces this with a 108-way
partition. -/
def chartOfShapePilot (s : O14Shape) : Nat :=
  if domain000 s then 0 else 0

theorem chartOfShapePilot_lt (s : O14Shape) :
    chartOfShapePilot s < ChartCount := by
  unfold chartOfShapePilot ChartCount
  by_cases h : domain000 s <;> simp [h]

/-- Pilot classifier object for generated-module bring-up only. -/
def pilotClassifier : EQODL1Classifier O14Shape := {
  chartOf := chartOfShapePilot,
  chartOf_lt := chartOfShapePilot_lt
}

#print axioms chartOfShapePilot_lt

end Generated
end O14
end Erdos23Delta0
