/-
GERSH aggregation — CORRECTED reduction (GPT-Pro MAIN + Claude gate).
The compiled deductive skeleton previously reduced Γ ≤ N² via two RowDBGammaFacts fields
`gamma_le_totalRowSum` (Γ ≤ Σ rowSum) and `totalRowSum_le_N2_of_gersh` (Σ rowSum ≤ N²). The
adversarial audit + Claude's exact verification found this is a DESIGN BUG: with
`totalRowSum = Σ_Q rowSum(Q)` over one row per bad edge and each `rowSum(Q) ≤ N+η`, one only gets
`Σ rowSum ≤ m(N+η) = N³/25 > N²` at the extremal — so `totalRowSum ≤ N²` is NOT derivable and the
field pair is unsatisfiable/wrong.

The CORRECT aggregation is the length-surplus token-charging:
  Σ_Q (ℓ(Q)² − 25) ≤ 25·η   ⟺   Γ = 25m + Σ(ℓ²−25) ≤ 25m + 25η = N².
This module compiles the REDUCTION (the trivial algebra + the `Γ = 25m + surplus` identity). The
token-charging inequality `lengthSurplus ≤ 25η` itself is the substantive LRS certificate (task #16,
proven); it remains the one genuine assumed obligation, to be discharged as a compiled provider.
Honest build. NOTE: CertGraph's `RowDBGammaFacts` still carries the buggy fields; grafting this
corrected form into CertGraph (replacing the pair with `lengthSurplus_le_25eta_of_gersh`) is the
assembly-time fix — done carefully to avoid downstream breakage.
-/
import Erdos23Delta0.CertGraph

namespace Erdos23Delta0
namespace GammaAggregation

open CertGraph

/-- Total length-surplus over the row database: `Σ_Q (ℓ(Q)² − 25)`. -/
def lengthSurplusGD (rows : RowDB) : ℚ :=
  (rows.rowList.map (fun Q : RowCert => (Q.length : ℚ) ^ 2 - 25)).sum

/-- List identity: `Σ ℓ² = 25·(#rows) + Σ(ℓ²−25)`. -/
theorem sum_sq_eq_25_len_plus_surplus (l : List RowCert) :
    (l.map (fun Q : RowCert => (Q.length : ℚ) ^ 2)).sum =
      25 * (l.length : ℚ) + (l.map (fun Q : RowCert => (Q.length : ℚ) ^ 2 - 25)).sum := by
  induction l with
  | nil => simp
  | cons R rs ih =>
      simp only [List.map_cons, List.sum_cons, List.length_cons, ih, Nat.cast_add, Nat.cast_one]
      ring

/-- Γ decomposition: with coverage (`#rows = badCount`), `Γ = 25m + lengthSurplus`. -/
theorem gamma_eq_25m_plus_surplus {G : GraphData} {c : CutData} {rows : RowDB}
    (hlen : rows.rowList.length = badCount G c) :
    gammaOfGD G c rows = 25 * (badCount G c : ℚ) + lengthSurplusGD rows := by
  unfold gammaOfGD lengthSurplusGD
  rw [sum_sq_eq_25_len_plus_surplus rows.rowList, hlen]

/-- CORRECTED GERSH aggregation reduction: coverage + the length-surplus token-charging bound
    `lengthSurplus ≤ 25η` give `Γ ≤ N²`. This is the compiled replacement for the buggy
    `gammaUpper_from_all_rows_gersh` two-field route. Pure exact rational algebra. -/
theorem gammaUpper_from_lengthSurplus {G : GraphData} {c : CutData} {rows : RowDB}
    (hlen : rows.rowList.length = badCount G c)
    (hsurp : lengthSurplusGD rows ≤ 25 * etaQ G c) :
    gammaOfGD G c rows ≤ (G.n : ℚ) ^ 2 := by
  have hgamma := gamma_eq_25m_plus_surplus (G := G) (c := c) (rows := rows) hlen
  have h25eta : 25 * etaQ G c = (G.n : ℚ) ^ 2 - 25 * (badCount G c : ℚ) := by
    unfold etaQ; ring
  rw [h25eta] at hsurp
  rw [hgamma]
  linarith

end GammaAggregation
end Erdos23Delta0
