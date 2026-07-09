import Erdos23Delta0.O14.EQODL1Shape

/-!
# Generated O14 chart keys: pilot scaffold

This file is the first module-29 generated-shape scaffold.  The bounds are
emitted from the accepted v108 ledger range:

* chart ids: `0..9`;
* dominant ids: `0..14`.

Only the pilot domain for ledger numeric-order `0` is present here.  The full
generator will replace this module with the 108-domain partition.
-/

namespace Erdos23Delta0
namespace O14
namespace Generated

open EQODL1CoverInterface

/-- Bounds emitted from the current v108 ledger for the pilot classifier. -/
def v108PilotBounds : O14Bounds := {
  kMax := 10,
  dMax := 15,
  seedShapeMax := 1,
  maskCodeMax := 1,
  orbitCodeMax := 1,
  routeCodeMax := 1,
  sigCodeMax := 1
}

/-- Pilot chart key: accepted ledger numeric-order 0, chart 5, dominant 13. -/
def domain000 (s : O14Shape) : Bool :=
  natEqB s.kIdx 5 && natEqB s.dIdx 13

theorem domain000_chart {s : O14Shape} (h : domain000 s = true) : s.kIdx = 5 := by
  simp [domain000, natEqB] at h
  exact h.1

theorem domain000_dominant {s : O14Shape} (h : domain000 s = true) :
    s.dIdx = 13 := by
  simp [domain000, natEqB] at h
  exact h.2

#print axioms domain000_chart
#print axioms domain000_dominant

end Generated
end O14
end Erdos23Delta0
