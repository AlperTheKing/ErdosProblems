/-
A1-proper wrapper, stage 1: canonical XMask + symmetry invariance.
XMask on any proper mask A equals the canonical XMask (sum over the canonical mask
of orbit `sd.id` with rotated-back indices). This reduces the a1Proper obligation to
the six canonical masks. Reuses the graph-independent A1MaskSymmetry classifier and
the CertGraph XMask/rowSurplusAt definitions. Honest build.
-/
import Erdos23Delta0.CertGraph
import Erdos23Delta0.A1MaskSymmetry

namespace Erdos23Delta0
namespace A1Proper

open A1MaskSymmetry
open CertGraph

/-- Canonical XMask: sum over the canonical mask of orbit `sd.id`, reading the row
    surplus at the rotated-back index. -/
def XMaskCanonical (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    {A : Finset (Fin 5)} (sd : MaskSymmetryData A) : ℚ :=
  ∑ i ∈ canonicalMask sd.id, rowSurplusAt G c rows Q (rotBack sd.rot i)

/-- Symmetry invariance: XMask on a proper mask equals the canonical XMask. -/
theorem mask_symmetry_sound (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    {A : Finset (Fin 5)} (sd : MaskSymmetryData A) :
    XMask G c rows Q A = XMaskCanonical G c rows Q sd := by
  classical
  unfold XMask XMaskCanonical
  conv_lhs => rw [sd.mask_eq]
  rw [Finset.sum_image (fun a _ b _ h => rotBack_injective sd.rot h)]

/-- Consequence: to bound XMask on every proper mask it suffices to bound the six
    canonical XMasks. -/
theorem a1Proper_of_canonical
    (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    (hcanon : ∀ (A : Finset (Fin 5)) (sd : MaskSymmetryData A),
      XMaskCanonical G c rows Q sd ≤
        ((25 : ℚ) / (G.n : ℚ) + (2 : ℚ) / 3) * etaQ G c) :
    ∀ A : Finset (Fin 5), A.Nonempty → A ≠ Finset.univ →
      XMask G c rows Q A ≤
        ((25 : ℚ) / (G.n : ℚ) + (2 : ℚ) / 3) * etaQ G c := by
  intro A hAne hAproper
  have sd := maskSymmetryData_of_proper A hAne hAproper
  rw [mask_symmetry_sound G c rows Q sd]
  exact hcanon A sd

end A1Proper
end Erdos23Delta0
