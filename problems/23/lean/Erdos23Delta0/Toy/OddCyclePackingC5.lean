/-
Toy instantiation (M6.5 validation): the OddCyclePacking TRUE-max-cut checker
certifies the maximum cut of the 5-cycle C5, evaluated WITHOUT kernel-bypassing automation
(honest `decide` on concrete n=5 data). Confirms the checker is usable in the
general max-cut provider (M6) path.

C5:  vertices 0..4, edges (0,1)(1,2)(2,3)(3,4)(0,4).
Cut: side = [F,T,F,T,F] -> the only monochromatic edge is (0,4), so badCount = 1.
Pack: the single odd 5-cycle [0,1,2,3,4,0] packs that one bad edge, so the cut is
      TRUE-max (IsMaxCut) by `checkOddCyclePacking_sound`.
-/
import Erdos23Delta0.CertGraph

namespace Erdos23Delta0
namespace CertGraph

open OddCyclePacking

def c5Graph : GraphData := ⟨5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]⟩

def c5Cut : CutData := ⟨[false, true, false, true, false]⟩

def c5Cert : OddCyclePackingCert := ⟨1, [[0, 1, 2, 3, 4, 0]]⟩

/-- The odd-cycle-packing checker accepts the C5 maximum cut (concrete Boolean
    evaluation, no kernel-bypassing automation). -/
theorem c5_checkOddCyclePacking :
    checkOddCyclePacking c5Graph c5Cut c5Cert = true := by decide

/-- Toy validation of the M6.5 provider path: the C5 cut is TRUE-max. -/
theorem c5_isMaxCut : IsMaxCut c5Graph c5Cut :=
  checkOddCyclePacking_sound c5_checkOddCyclePacking

end CertGraph
end Erdos23Delta0
