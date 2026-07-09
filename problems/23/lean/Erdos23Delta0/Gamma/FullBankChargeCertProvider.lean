import Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge

/-!
# Full-bank package to typed length-surplus charge certificate

This module is a thin provider bridge from the accepted full-bank global
package interface to the existing `LengthSurplusChargeCertV2` checker route.
It does not construct the wall package; it only shows that once the wall gives
a checked `FullBankGlobalPackage`, the old typed charge-certificate API can be
fed soundly.
-/

namespace Erdos23Delta0
namespace Gamma
namespace FullBankToLengthSurplusCharge

open CertGraph
open GammaAggregation

namespace FullBankGlobalPackage

private theorem ratDot_replicate_zero : ∀ n : Nat, ∀ ys : List ℚ,
    ratDot (List.replicate n (0 : ℚ)) ys = 0 := by
  intro n
  induction n with
  | zero =>
      intro ys
      unfold ratDot
      simp
  | succ n ih =>
      intro ys
      cases ys with
      | nil =>
          unfold ratDot
          simp
      | cons y ys =>
          unfold ratDot
          simp [List.replicate]
          simpa [ratDot] using ih ys

/-- Canonical residual-formula placeholder for the bridge. The produced
certificate uses only the `raw` residual slot, whose nonnegativity is proved
from the checked full-bank package. -/
def residualFormulasOfFullBankPackage
    (G : GraphData) (c : CutData) (rows : RowDB) :
    ResidualFormulas G c rows where
  lrsVal := 0
  cauchyVal := 0
  bankReserveVal := 0

/-- A typed charge certificate extracted from a checked full-bank package.
The coefficients are zero and the single raw residual is exactly the already
proved full-bank length-surplus target. -/
def chargeCertProviderOfFullBankLedger
    {G : GraphData} {c : CutData} {rows : RowDB}
    (_P : FullBankGlobalPackage G c rows) : LengthSurplusChargeCertV2 where
  coeffs := List.replicate rows.rowList.length 0
  residuals := [{
    kind := LengthChargeResidualKind.raw
    value := lengthSurplusTarget G c rows
  }]

/-- The provider bridge passes the existing typed checker. -/
theorem chargeCertProviderOfFullBankLedger_ok
    {G : GraphData} {c : CutData} {rows : RowDB}
    {P : FullBankGlobalPackage G c rows} (h : P.Checked) :
    checkLengthSurplusChargeCertV2
      (residualFormulasOfFullBankPackage G c rows)
      (chargeCertProviderOfFullBankLedger P) = true := by
  have hnn : 0 ≤ lengthSurplusTarget G c rows := by
    unfold lengthSurplusTarget
    have hs := fullBankGlobalPackage_sound h
    exact sub_nonneg.mpr hs
  have hdec : decide (0 ≤ lengthSurplusTarget G c rows) = true := by
    rw [decide_eq_true_eq]
    exact hnn
  unfold checkLengthSurplusChargeCertV2
  simp [chargeCertProviderOfFullBankLedger,
    residualFormulasOfFullBankPackage, checkLengthChargeResidual,
    residualValues, ratDot_replicate_zero, hdec]

/-- The same `Γ ≤ N²` conclusion routed through `LengthSurplusChargeCertV2`. -/
theorem gammaUpper_from_fullBankPackage_via_chargeCertV2
    {G : GraphData} {c : CutData} {rows : RowDB}
    {P : FullBankGlobalPackage G c rows} (h : P.Checked)
    (hGersh : ∀ Q : RowCert, RowInDB rows Q → RowGershBound G c rows Q) :
    gammaOfGD G c rows ≤ (G.n : ℚ) ^ 2 :=
  gammaUpper_from_chargeCertV2
    (residualFormulasOfFullBankPackage G c rows)
    h.rows_length_eq_badCount
    (chargeCertProviderOfFullBankLedger P)
    (chargeCertProviderOfFullBankLedger_ok h)
    hGersh

end FullBankGlobalPackage
end FullBankToLengthSurplusCharge
end Gamma
end Erdos23Delta0
