/-
M4: bridge from the transpiler-emitted Branch-B `RowPilot` data (Cert tree,
audit-green) to the abstract `BranchBInputs` obligation (CertGraph).

The emitter's `RowPilot.check` verifies the scaled-integer Banked-UPO and
Bank-L dominance certificates. Given a per-row `RowPilotBinding` (the numeric
identification of the abstract rational quantities with the scaled-integer
data — this identification is the provider obligation, M6/M7), this file
transports the checked integer inequalities to the three rational
`BranchBInputs` fields.

The bridge itself is pure arithmetic and is an M4 compiled lemma. It does NOT
supply the binding (that is per-row provider data).
-/
import Erdos23Delta0.CertGraph
import Erdos23Delta0.Cert.BranchBSupport

namespace Erdos23Delta0
namespace Cert

open Erdos23Delta0.CertGraph

/-- A passing `ScaledGeCert` gives the scaled integer inequality `lhs ≤ rhs`
    (the certificate encodes `lhs + margin = rhs` with `margin : Nat ≥ 0`). -/
theorem ScaledGeCert.le_of_check {s : ScaledGeCert} (h : s.check = true) :
    s.lhs ≤ s.rhs := by
  simp only [ScaledGeCert.check, Bool.and_eq_true, bne_iff_ne, beq_iff_eq] at h
  have heq : s.lhs + Int.ofNat s.margin = s.rhs := h.2
  have hnn : (0 : ℤ) ≤ Int.ofNat s.margin := Int.natCast_nonneg _
  omega

/-- Rational transport: `a ≤ b` over ℤ lifts to `a/d ≤ b/d` over ℚ for any
    `d : Nat` (the Nat cast is nonnegative; division by zero gives `0 ≤ 0`). -/
theorem cast_div_le_of_le {a b : ℤ} {d : Nat} (h : a ≤ b) :
    (a : ℚ) / (d : ℚ) ≤ (b : ℚ) / (d : ℚ) := by
  have hab : (a : ℚ) ≤ (b : ℚ) := by exact_mod_cast h
  have hd : (0 : ℚ) ≤ (d : ℚ) := by positivity
  gcongr

/-- The M4 per-row binding: identifies the abstract rational quantities of the
    Branch-B obligation with the emitted scaled-integer certificate data.
    Supplied per row by the emitter/provider (M6/M7). -/
structure RowPilotBinding (G : GraphData) (c : CutData) (rows : RowDB)
    (Q : RowCert) (r : RowPilot) : Prop where
  len_eq : Q.length = r.L
  bankL_lhs :
    2 * rhoQ Q.length
      = (r.gateBDominance.lhs : ℚ) / (r.gateBDominance.den : ℚ)
  bankL_rhs :
    etaQ G c
      = (r.gateBDominance.rhs : ℚ) / (r.gateBDominance.den : ℚ)
  upo_lhs :
    rowSum G c rows Q
      = (r.finiteMargin.lhs : ℚ) / (r.finiteMargin.den : ℚ)
  upo_rhs :
    (G.n : ℚ) + etaQ G c / 2 - rhoQ Q.length
      = (r.finiteMargin.rhs : ℚ) / (r.finiteMargin.den : ℚ)

/-- M4 BRIDGE. A Branch-B row whose `RowPilot` passes `RowPilot.check`, with a
    `RowPilotBinding` and `5 < r.L`, satisfies the abstract `BranchBInputs`. -/
theorem branchBInputs_of_rowPilot
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert} {r : RowPilot}
    (binding : RowPilotBinding G c rows Q r)
    (hcheck : RowPilot.check r = true)
    (hL : 5 < r.L) :
    BranchBInputs G c rows Q := by
  simp only [RowPilot.check, Bool.and_eq_true] at hcheck
  obtain ⟨⟨⟨⟨_hp, hfm⟩, hgd⟩, _hcand⟩, _hop⟩ := hcheck
  have hgd_le : r.gateBDominance.lhs ≤ r.gateBDominance.rhs :=
    ScaledGeCert.le_of_check hgd
  have hfm_le : r.finiteMargin.lhs ≤ r.finiteMargin.rhs :=
    ScaledGeCert.le_of_check hfm
  refine
    { hLen := ?_, bankL := ?_, bankedUPO := ?_ }
  · rw [binding.len_eq]; exact hL
  · rw [binding.bankL_lhs, binding.bankL_rhs]
    exact cast_div_le_of_le hgd_le
  · rw [binding.upo_lhs, binding.upo_rhs]
    exact cast_div_le_of_le hfm_le

/-- Packaged as the `BranchBCertBundle` extension point consumed by
    `Delta0CertBundles.branchB`. -/
theorem branchBCertBundle_of_rowPilot
    {G : GraphData} {c : CutData} {rows : RowDB} {Q : RowCert} {r : RowPilot}
    (binding : RowPilotBinding G c rows Q r)
    (hcheck : RowPilot.check r = true)
    (hL : 5 < r.L) :
    BranchBCertBundle G c rows Q :=
  { inputs := branchBInputs_of_rowPilot binding hcheck hL }

end Cert
end Erdos23Delta0

