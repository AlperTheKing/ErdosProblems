/-
A1-proper wrapper, stage 1: canonical XMask + symmetry invariance.
XMask on any proper mask A equals the canonical XMask (sum over the canonical mask
of orbit `sd.id` with rotated-back indices). This reduces the a1Proper obligation to
the six canonical masks. Reuses the graph-independent A1MaskSymmetry classifier and
the CertGraph XMask/rowSurplusAt definitions. Honest build.
-/
import Erdos23Delta0.CertGraph
import Erdos23Delta0.A1MaskSymmetry
import Erdos23Delta0.PolyCert

namespace Erdos23Delta0
namespace A1Proper

open A1MaskSymmetry
open CertGraph
open PolyCert

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

/-- The cleared-defect algebra: from `0 ≤ (75+2N)·η − 3N·X` (what a ConeCert for the
    cleared A1 defect delivers) derive `X ≤ (25/N + 2/3)·η`. Pure rational division by
    `3N > 0`; this is the final step of `A1CanonicalCone.sound`. -/
theorem xmask_bound_of_clearedDefect (n η X : ℚ) (hNpos : 0 < n)
    (hdefect : 0 ≤ (75 + 2 * n) * η - 3 * n * X) :
    X ≤ (25 / n + 2 / 3) * η := by
  have hn : n ≠ 0 := ne_of_gt hNpos
  rw [← sub_nonneg]
  have key : (25 / n + 2 / 3) * η - X = ((75 + 2 * n) * η - 3 * n * X) / (3 * n) := by
    field_simp
    ring
  rw [key]
  exact div_nonneg hdefect (by linarith)

/-- Generic A1-cone bridge (cone-independent). Given ANY `ConeCert` together with a
    nonnegative environment, nonnegative slack values, and the env-binding identity
    `eval env target = (75+2N)·η − 3N·XMaskCanonical` (the cleared A1 defect), the
    canonical XMask is bounded by `(25/N + 2/3)·η`. The six specific A1 cones supply
    `cone`, `env`, `hvars`, `hslacks`, and `htarget` at instantiation; this lemma is
    the reusable soundness skeleton (`A1CanonicalCone.sound`). -/
theorem canonicalCone_bound
    (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    {A : Finset (Fin 5)} (sd : MaskSymmetryData A)
    (hNpos : 0 < (G.n : ℚ))
    (cone : ConeCert) (env : Var → ℚ)
    (hvars : ∀ v, 0 ≤ env v)
    (hslacks : ∀ s ∈ cone.slacks, 0 ≤ NF.eval env s)
    (htarget : NF.eval env cone.target
        = (75 + 2 * (G.n : ℚ)) * etaQ G c
          - 3 * (G.n : ℚ) * XMaskCanonical G c rows Q sd) :
    XMaskCanonical G c rows Q sd ≤
      ((25 : ℚ) / (G.n : ℚ) + (2 : ℚ) / 3) * etaQ G c := by
  have h0 : 0 ≤ NF.eval env cone.target := ConeCert.sound cone env hvars hslacks
  rw [htarget] at h0
  exact xmask_bound_of_clearedDefect (G.n : ℚ) (etaQ G c)
    (XMaskCanonical G c rows Q sd) hNpos h0

/-- A1-proper from six A1 cones. If every canonical mask (id, rot) admits a cone with
    a nonnegative environment, nonnegative slacks, and the cleared-defect env-binding,
    then a1Proper holds for all proper masks. This is the exact obligation the six
    A1 ConeCerts must discharge — the `A1ProperCertBundle` interface. -/
theorem a1Proper_of_six_cones
    (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert)
    (hNpos : 0 < (G.n : ℚ))
    (hcone : ∀ (A : Finset (Fin 5)) (sd : MaskSymmetryData A),
      ∃ (cone : ConeCert) (env : Var → ℚ),
        (∀ v, 0 ≤ env v) ∧
        (∀ s ∈ cone.slacks, 0 ≤ NF.eval env s) ∧
        NF.eval env cone.target
          = (75 + 2 * (G.n : ℚ)) * etaQ G c
            - 3 * (G.n : ℚ) * XMaskCanonical G c rows Q sd) :
    ∀ A : Finset (Fin 5), A.Nonempty → A ≠ Finset.univ →
      XMask G c rows Q A ≤
        ((25 : ℚ) / (G.n : ℚ) + (2 : ℚ) / 3) * etaQ G c := by
  apply a1Proper_of_canonical
  intro A sd
  obtain ⟨cone, env, hvars, hslacks, htarget⟩ := hcone A sd
  exact canonicalCone_bound G c rows Q sd hNpos cone env hvars hslacks htarget

end A1Proper
end Erdos23Delta0
