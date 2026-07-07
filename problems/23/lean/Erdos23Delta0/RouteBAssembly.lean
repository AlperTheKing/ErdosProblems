/-
Route-B aggregation assembly (conjunct-4 gap #1) — INCREMENT 1: reserveResidual + β-landing.

GPT-Pro's Route-B reduces the aggregation obligation Γ ≤ N² to a self-contained Γ-minimality pair-door
switch contradiction (no charge cert needed), with `reserveResidual = N² − Γ` and the top theorem
`0 ≤ reserveResidual`. The full switch/cage layer (PairTypeBThetaGate, PairDoorConvex, TerminalCage,
sigma, Balance, Surplus, Bank) + the two residual leaves (NoSideDoorForLongAnnulus,
PositiveSlackAbsorption_Hall) + ReserveLedgerComplete are built in later increments as NAMED hypotheses,
never sorry (spec: problems/23/writeup/GAP1_ROUTEB_FINAL_SKELETON_GPTPRO.md).

This increment lands the chain into the β-bound: `0 ≤ reserveResidual  ⟹  β = badCount ≤ N²/25`, reusing
the fundamental Γ lower bound `25·badCount ≤ Γ` (`GammaChargeGraft.gammaLower_of_len5`, from length ≥ 5 +
coverage). Additive: does NOT edit CertGraph. Honest = no sorry/admit/native_decide.
-/
import Erdos23Delta0.CertGraph
import Erdos23Delta0.GammaChargeGraft

namespace Erdos23Delta0
namespace RouteBAssembly

open CertGraph
open GammaChargeGraft

/-- The reserve residual `= N² − Γ`. Route-B's top theorem `reserveResidual_nonneg_core_routeB` proves this
    `≥ 0` (equivalently `Γ ≤ N²`) via the Γ-minimality pair-door switch contradiction, self-contained. -/
def reserveResidual (G : GraphData) (c : CutData) (rows : RowDB) : ℚ :=
  (G.n : ℚ) ^ 2 - gammaOfGD G c rows

/-- `reserveResidual = N² − Γ`, so `0 ≤ reserveResidual  ↔  Γ ≤ N²`. -/
theorem gamma_le_N2_of_reserveResidual_nonneg {G : GraphData} {c : CutData} {rows : RowDB}
    (h : 0 ≤ reserveResidual G c rows) :
    gammaOfGD G c rows ≤ (G.n : ℚ) ^ 2 := by
  unfold reserveResidual at h; linarith

/-- β-landing: `reserveResidual ≥ 0` (Route-B output) + fundamental length-≥5 + coverage ⟹ `β ≤ N²/25`.
    This is the interface point of the whole Route-B chain into the official bound. -/
theorem betaSimple_le_of_reserveResidual_nonneg {G : GraphData} {c : CutData} {rows : RowDB}
    (hRows : RowDBFactsGeneral G c rows)
    (hlen : rows.rowList.length = badCount G c)
    (h : 0 ≤ reserveResidual G c rows) :
    (badCount G c : ℚ) ≤ (G.n : ℚ) ^ 2 / 25 := by
  have hlower : 25 * (badCount G c : ℚ) ≤ gammaOfGD G c rows := gammaLower_of_len5 hRows hlen
  have hupper : gammaOfGD G c rows ≤ (G.n : ℚ) ^ 2 := gamma_le_N2_of_reserveResidual_nonneg h
  linarith

/-- Core NON-CIRCULAR reserve extraction (GPT-Pro's B4, abstract form). A negative reserve, decomposed as
    `reserve = free + good + Σ_C Balance C` with `free, good ≥ 0`, each cage's slack `sigma C ≥ 0`
    (maximum-cutness) and the slack-absorption `0 < sigma C → 0 ≤ Balance C`, forces a **zero-slack
    negative-balance** terminal cage. NO Γ-minimality and NO switch is used — the hypotheses are exactly the
    ledger facts L1–L5, so this is non-circular by construction (it does not even mention the switch or Γ). -/
theorem zeroSlack_negBalance_cage_of_neg_reserve
    {Cage : Type*} (cages : Finset Cage) (Balance sigma : Cage → ℚ) (free good reserve : ℚ)
    (hLedger : reserve = free + good + ∑ C ∈ cages, Balance C)
    (hFree : 0 ≤ free) (hGood : 0 ≤ good)
    (hSigmaNonneg : ∀ C ∈ cages, 0 ≤ sigma C)
    (hAbsorb : ∀ C ∈ cages, 0 < sigma C → 0 ≤ Balance C)
    (hNeg : reserve < 0) :
    ∃ C ∈ cages, Balance C < 0 ∧ sigma C = 0 := by
  have hsum : (∑ C ∈ cages, Balance C) < 0 := by linarith
  obtain ⟨C, hC, hBneg⟩ : ∃ C ∈ cages, Balance C < 0 := by
    by_contra hcon
    push_neg at hcon
    exact absurd (Finset.sum_nonneg hcon) (not_le.mpr hsum)
  refine ⟨C, hC, hBneg, ?_⟩
  rcases eq_or_lt_of_le (hSigmaNonneg C hC) with hzero | hpos
  · exact hzero.symm
  · exact absurd (hAbsorb C hC hpos) (not_le.mpr hBneg)

/-- CageHallCert soundness core (GPT-Pro R-D step 4, abstract). A per-cage token-matching charge cert `q`
    with **atom-exactness** (`Σ_t q a t = demand a`) and **token-capacity** (`Σ_a q a t ≤ cap t`) forces
    `Surplus = Σ demand ≤ Σ cap = BankCap`. Hence `Balance = BankCap − Surplus ≥ 0` (see corollary). Only
    finite exact-rational sums — NO Γ-minimality, NO switch: this is the non-circular absorption cert, the same
    Hall/charge shape as the Branch-A certificates. The remaining R-D residual is only the *existence* of such a
    `q` for every positive-slack cage (`PositiveSlackHallPrefix`). -/
theorem surplus_le_bankCap_of_hall_charge
    {Atom Token : Type*} (atoms : Finset Atom) (tokens : Finset Token)
    (demand : Atom → ℚ) (cap : Token → ℚ) (q : Atom → Token → ℚ)
    (hAtom : ∀ a ∈ atoms, ∑ t ∈ tokens, q a t = demand a)
    (hCap : ∀ t ∈ tokens, ∑ a ∈ atoms, q a t ≤ cap t) :
    ∑ a ∈ atoms, demand a ≤ ∑ t ∈ tokens, cap t := by
  have h1 : ∑ a ∈ atoms, demand a = ∑ a ∈ atoms, ∑ t ∈ tokens, q a t :=
    Finset.sum_congr rfl (fun a ha => (hAtom a ha).symm)
  rw [h1, Finset.sum_comm]
  exact Finset.sum_le_sum hCap

/-- `Balance ≥ 0` from the Hall charge cert: with `Surplus = Σ demand`, `BankCap = Σ cap`, and
    `Balance = BankCap − Surplus`, the charge cert gives `0 ≤ Balance`. -/
theorem balance_nonneg_of_hall_charge
    {Atom Token : Type*} (atoms : Finset Atom) (tokens : Finset Token)
    (demand : Atom → ℚ) (cap : Token → ℚ) (q : Atom → Token → ℚ)
    (hAtom : ∀ a ∈ atoms, ∑ t ∈ tokens, q a t = demand a)
    (hCap : ∀ t ∈ tokens, ∑ a ∈ atoms, q a t ≤ cap t) :
    0 ≤ (∑ t ∈ tokens, cap t) - (∑ a ∈ atoms, demand a) := by
  have := surplus_le_bankCap_of_hall_charge atoms tokens demand cap q hAtom hCap
  linarith

/-- R-A pruning core (GPT-Pro `SideDoorPruningPreservesPositiveDebt`, algebraic heart). Given the balance-additivity
    identity `Balance(C) = Balance(C') + Balance(D) + PruneRemainder` with `PruneRemainder ≥ 0` and `Balance(D) ≥ 0`
    (from `PositiveSlackAbsorption` on the positive-slack side-door subcage `D`), a positive-debt cage
    (`Balance(C) < 0`) prunes to a proper descendant `C'` that STILL has positive debt (`Balance(C') < 0`) —
    contradicting minimality of `C`. Pure algebra: NO Γ-minimality, NO switch (non-circular). -/
theorem pruned_balance_neg_of_neg
    (balC balC' balD pruneRem : ℚ)
    (hAdd : balC = balC' + balD + pruneRem)
    (hDnn : 0 ≤ balD) (hRemnn : 0 ≤ pruneRem)
    (hCneg : balC < 0) :
    balC' < 0 := by linarith

end RouteBAssembly
end Erdos23Delta0
