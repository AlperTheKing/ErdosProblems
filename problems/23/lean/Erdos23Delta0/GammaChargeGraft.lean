/-
Aggregation graft (conjunct-4 gap #1, honest satisfiable route).

The active `CertGraph.gammaBetaProvider_of_rowDB` discharges `GammaBetaFacts.gammaUpper_of_all_rows_gersh`
through `RowDBGammaFacts.totalRowSum_le_N2_of_gersh`, i.e. `Γ ≤ Σ rowSum ≤ N²`. The right conjunct
`Σ rowSum ≤ N²` is UNSATISFIABLE at the extremal (`Σ rowSum` can reach `m(N+η) = N³/25 ≫ N²`), so no real
graph inhabits that field — a latent fake-progress route (grep-confirmed 2026-07-07; the GammaAggregation
header declares the two-field route the design bug).

This module provides the SATISFIABLE replacement: it routes `Γ ≤ N²` through the corrected typed
token-charging cert `GammaAggregation.gammaUpper_from_chargeCertV2` (green). The good-cut provider supplies a
per-instance `ResidualFormulas F` + `LengthSurplusChargeCertV2 cert` with `checkLengthSurplusChargeCertV2 = true`
(a real cert CAN inhabit this, unlike `Σ rowSum ≤ N²`), plus the fundamental `RowDBFactsGeneral` (rows length ≥ 5)
from which the Γ lower bound `25·badCount ≤ Γ` is derived here. Constructing/proving the charge cert exists for
every good cut, with the bank-reserve residual nonneg, remains the aggregation-completeness obligation — but this
replaces the dead route with a live one. Additive: does NOT edit CertGraph.
-/
import Erdos23Delta0.CertGraph
import Erdos23Delta0.GammaAggregation

namespace Erdos23Delta0
namespace GammaChargeGraft

open CertGraph
open GammaAggregation

/-- `Σ ℓ² ≥ 25·(#rows)` when every row has length ≥ 5. (Local reproof; the CertGraph analogue is `private`.) -/
private lemma list_len_sq_ge_25 (l : List RowCert)
    (hLen : ∀ Q : RowCert, Q ∈ l → 5 ≤ Q.length) :
    25 * (l.length : ℚ) ≤ (l.map (fun Q : RowCert => (Q.length : ℚ) ^ 2)).sum := by
  induction l with
  | nil => simp
  | cons Q qs ih =>
      have hQ : 5 ≤ Q.length := hLen Q (by simp)
      have hqs : ∀ R : RowCert, R ∈ qs → 5 ≤ R.length := by
        intro R hR; exact hLen R (by simp [hR])
      have ih' := ih hqs
      have hQsq : (25 : ℚ) ≤ (Q.length : ℚ) ^ 2 := by
        have hQq : (5 : ℚ) ≤ (Q.length : ℚ) := by exact_mod_cast hQ
        nlinarith [sq_nonneg ((Q.length : ℚ) - 5)]
      simp only [List.map_cons, List.sum_cons, List.length_cons]
      have hlen_cast : ((qs.length + 1 : Nat) : ℚ) = (qs.length : ℚ) + 1 := by norm_num
      rw [hlen_cast]
      nlinarith

/-- Γ lower bound `25·badCount ≤ Γ` from the fundamental length-≥5 fact + coverage `#rows = badCount`. -/
theorem gammaLower_of_len5 {G : GraphData} {c : CutData} {rows : RowDB}
    (hRows : RowDBFactsGeneral G c rows)
    (hlen : rows.rowList.length = badCount G c) :
    25 * (badCount G c : ℚ) ≤ gammaOfGD G c rows := by
  unfold gammaOfGD
  have hsum : 25 * (rows.rowList.length : ℚ) ≤
      (rows.rowList.map (fun Q : RowCert => (Q.length : ℚ) ^ 2)).sum :=
    list_len_sq_ge_25 rows.rowList (fun Q hQ => hRows.length_ge_five Q hQ)
  rw [← hlen]
  exact hsum

/-- Satisfiable `GammaBetaFacts` provider via the corrected typed charge certificate. `gammaVal := Γ = Σ ℓ²`,
    and the `Γ ≤ N²` obligation is discharged by `gammaUpper_from_chargeCertV2` (the non-degenerate, compiled
    token-charging route) rather than the unsatisfiable `totalRowSum ≤ N²` field. The Γ lower bound is derived
    from `RowDBFactsGeneral` (rows length ≥ 5) + `hlen`. -/
def gammaBetaProvider_of_chargeCert {G : GraphData} {c : CutData} {rows : RowDB}
    (F : ResidualFormulas G c rows) (cert : LengthSurplusChargeCertV2)
    (hlen : rows.rowList.length = badCount G c)
    (hcheck : checkLengthSurplusChargeCertV2 F cert = true)
    (hRows : RowDBFactsGeneral G c rows) :
    GammaBetaFacts G c rows where
  gammaVal := gammaOfGD G c rows
  betaVal := (badCount G c : ℚ)
  gammaLower := gammaLower_of_len5 hRows hlen
  gammaUpper_of_all_rows_gersh := fun hGersh =>
    gammaUpper_from_chargeCertV2 F hlen cert hcheck hGersh
  beta_eq_badCount := rfl

end GammaChargeGraft
end Erdos23Delta0
