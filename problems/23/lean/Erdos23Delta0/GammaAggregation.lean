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

/-! ### Token-charging as a length-surplus charge certificate (GPT-Pro MAIN).
The substantive obligation `lengthSurplus ≤ 25η` is a Positivstellensatz certificate:
`25η − lengthSurplus = R + Σ_Q a_Q·((N+η) − rowSum(Q))` with `R ≥ 0`, `a_Q ≥ 0`. Under the per-row
GERSH bounds each slack is nonnegative, so the target is nonnegative. This makes the deep GERSH
aggregation an EXACT-VERIFIABLE certificate (like the A1 cones): the LRS reduction (task #16) provides
the coefficients `a_Q` and residual `R`; the checker verifies the exact rational identity + nonneg. -/

/-- The per-row GERSH slack `(N+η) − rowSum(Q)` (≥0 under RowGershBound). -/
def rowGershSlack (G : GraphData) (c : CutData) (rows : RowDB) (Q : RowCert) : ℚ :=
  (G.n : ℚ) + etaQ G c - rowSum G c rows Q

def rowGershSlackList (G : GraphData) (c : CutData) (rows : RowDB) : List ℚ :=
  rows.rowList.map (fun Q => rowGershSlack G c rows Q)

def ratDot (xs ys : List ℚ) : ℚ :=
  (List.zipWith (fun x y => x * y) xs ys).sum

def lengthSurplusTarget (G : GraphData) (c : CutData) (rows : RowDB) : ℚ :=
  25 * etaQ G c - lengthSurplusGD rows

structure LengthSurplusChargeCert where
  coeffs : List ℚ
  residual : ℚ
deriving Repr

/-- Checker: nonneg residual, nonneg coefficients, matching length, and the exact charge identity. -/
def checkLengthSurplusChargeCert (G : GraphData) (c : CutData) (rows : RowDB)
    (cert : LengthSurplusChargeCert) : Bool :=
  decide (0 ≤ cert.residual) &&
    (cert.coeffs.all (fun a => decide (0 ≤ a)) &&
      (decide (cert.coeffs.length = rows.rowList.length) &&
        decide (lengthSurplusTarget G c rows =
          cert.residual + ratDot cert.coeffs (rowGershSlackList G c rows))))

theorem ratDot_nonneg : ∀ (xs ys : List ℚ),
    (∀ x ∈ xs, 0 ≤ x) → (∀ y ∈ ys, 0 ≤ y) → 0 ≤ ratDot xs ys := by
  intro xs
  induction xs with
  | nil => intro ys _ _; unfold ratDot; simp
  | cons x xs ih =>
      intro ys hxs hys
      cases ys with
      | nil => unfold ratDot; simp
      | cons y ys =>
          unfold ratDot
          simp only [List.zipWith_cons_cons, List.sum_cons]
          have hx : 0 ≤ x := hxs x (by simp)
          have hy : 0 ≤ y := hys y (by simp)
          have hxs' : ∀ z ∈ xs, 0 ≤ z := fun z hz => hxs z (by simp [hz])
          have hys' : ∀ z ∈ ys, 0 ≤ z := fun z hz => hys z (by simp [hz])
          have hrest : 0 ≤ ratDot xs ys := ih ys hxs' hys'
          unfold ratDot at hrest
          nlinarith [mul_nonneg hx hy]

/-- SOUNDNESS: a passing length-surplus charge certificate + the per-row GERSH bounds give the
    token-charging inequality `lengthSurplus ≤ 25η` (hence, with `gammaUpper_from_lengthSurplus`,
    `Γ ≤ N²`). This is the corrected, satisfiable, COMPILED GERSH-aggregation provider. -/
theorem lengthSurplus_le_25eta_of_charge {G : GraphData} {c : CutData} {rows : RowDB}
    (cert : LengthSurplusChargeCert)
    (hcheck : checkLengthSurplusChargeCert G c rows cert = true)
    (hGersh : ∀ Q : RowCert, RowInDB rows Q → RowGershBound G c rows Q) :
    lengthSurplusGD rows ≤ 25 * etaQ G c := by
  unfold checkLengthSurplusChargeCert at hcheck
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at hcheck
  obtain ⟨hres, hcoeffs, _hlen, hid⟩ := hcheck
  have hcoeffs' : ∀ a ∈ cert.coeffs, 0 ≤ a := by
    intro a ha
    have := hcoeffs a ha
    simpa using this
  have hslacks : ∀ y ∈ rowGershSlackList G c rows, 0 ≤ y := by
    intro y hy
    unfold rowGershSlackList at hy
    rw [List.mem_map] at hy
    obtain ⟨Q, hQ, rfl⟩ := hy
    have hgersh := hGersh Q hQ
    unfold RowGershBound at hgersh
    unfold rowGershSlack
    linarith
  have hdot := ratDot_nonneg cert.coeffs (rowGershSlackList G c rows) hcoeffs' hslacks
  unfold lengthSurplusTarget at hid
  linarith

/-- The full corrected aggregation from a charge certificate: coverage + a passing charge cert +
    per-row GERSH give `Γ ≤ N²`. This is the compiled, satisfiable replacement for the design-bug
    `gammaUpper_from_all_rows_gersh` route. -/
theorem gammaUpper_from_chargeCert {G : GraphData} {c : CutData} {rows : RowDB}
    (hlen : rows.rowList.length = badCount G c)
    (cert : LengthSurplusChargeCert)
    (hcheck : checkLengthSurplusChargeCert G c rows cert = true)
    (hGersh : ∀ Q : RowCert, RowInDB rows Q → RowGershBound G c rows Q) :
    gammaOfGD G c rows ≤ (G.n : ℚ) ^ 2 :=
  gammaUpper_from_lengthSurplus hlen (lengthSurplus_le_25eta_of_charge cert hcheck hGersh)

end GammaAggregation
end Erdos23Delta0
