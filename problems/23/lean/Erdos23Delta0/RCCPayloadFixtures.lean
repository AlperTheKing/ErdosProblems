import Erdos23Delta0.RelaxedCoverDuality
import Erdos23Delta0.BankedCutDominationCore
import Erdos23Delta0.BankedCutDominationExtras

set_option maxHeartbeats 2000000

/-!
# Concrete relaxed-cover payload fixtures

This module pins a small exact Gap#1 RCC payload against the compiled
weak-duality surface.  The first fixture is the nonzero compressed table of the
24-vertex bare-SSE counterexample: nine rows, eight support edges, nine loaded
off-support exits, three singleton cut columns, and one door-bank sink.

The full graph-level payload, including inert off-support cut edges, lives in
`tmp/codex_rcc_anchor_payloads/bare_sse_24.json`.
-/

namespace Erdos23Delta0
namespace RCCPayloadFixtures
namespace BareSSE24

open Finset
open RelaxedCoverDuality
open BankedCutDominationCore
open BankedCutDominationExtras

abbrev Row := Fin 9
abbrev Edge := Fin 17

inductive CutId where
  | k0 | k1 | k2
  deriving DecidableEq

abbrev Sink := Unit

open CutId

/-- All nine K3,3 bad rows. -/
def S : Finset Row := {(0 : Row), 1, 2, 3, 4, 5, 6, 7, 8}

/-- The eight double-star support edges. -/
def F : Finset Edge := {(0 : Edge), 1, 2, 3, 4, 5, 6, 7}

/-- The nine loaded off-support anchor exits. -/
def O : Finset Edge := {(8 : Edge), 9, 10, 11, 12, 13, 14, 15, 16}

/-- The single door sink. -/
def J : Finset Sink := {()}

/-- The three left-singleton cuts. -/
def K : Finset CutId := {k0, k1, k2}

/-- Cut `k` covers exactly the three rows whose left endpoint is `k`. -/
def sep : CutId → Finset Row
  | k0 => {(0 : Row), 1, 2}
  | k1 => {(3 : Row), 4, 5}
  | k2 => {(6 : Row), 7, 8}

/-- Boundary load of cut `k`: one support spoke plus three left anchor exits. -/
def dB : CutId → Finset Edge
  | k0 => {(0 : Edge), 8, 9, 10}
  | k1 => {(1 : Edge), 11, 12, 13}
  | k2 => {(2 : Edge), 14, 15, 16}

/-- One unit of cover on each singleton cut. -/
def lam (_k : CutId) : ℚ := 1

/-- Every compressed off-support exit routes one unit to the door sink. -/
def q (_e : Edge) (_j : Sink) : ℚ := 1

/-- Door capacity for the compressed nonzero core; 17 is a safe compressed overcapacity. -/
def kap (_j : Sink) : ℚ := 17

/-- In this fixture every off-support edge may spend the door bank. -/
def inc (_e : Edge) (_j : Sink) : Prop := True

example : (0 : Row) ∈ sep k0 := by decide
example : (8 : Edge) ∈ dB k0 := by decide
example : (16 : Edge) ∈ O := by decide

/-- If some entry is selected, the 0/1 sum is at least one. -/
lemma one_le_sum_ite_one_of_exists {α : Type*} [DecidableEq α]
    (s : Finset α) (p : α → Prop) [DecidablePred p]
    (hex : ∃ x, x ∈ s ∧ p x) :
    (1 : ℚ) ≤ ∑ x ∈ s, if p x then (1 : ℚ) else 0 := by
  classical
  rcases hex with ⟨x, hxs, hpx⟩
  have hnon : (s.filter p).Nonempty := ⟨x, by simp [hxs, hpx]⟩
  have hcard : 1 ≤ (s.filter p).card := Nat.succ_le_of_lt (Finset.card_pos.mpr hnon)
  calc
    (1 : ℚ) ≤ ((s.filter p).card : ℚ) := by exact_mod_cast hcard
    _ = ∑ x ∈ s, if p x then (1 : ℚ) else 0 := by simp

/-- If at most one entry is selected, the 0/1 sum is at most one. -/
lemma sum_ite_one_le_one_of_unique {α : Type*} [DecidableEq α]
    (s : Finset α) (p : α → Prop) [DecidablePred p]
    (huniq : ∀ x ∈ s, ∀ y ∈ s, p x → p y → x = y) :
    (∑ x ∈ s, if p x then (1 : ℚ) else 0) ≤ 1 := by
  classical
  have hcard : (s.filter p).card ≤ 1 := by
    rw [Finset.card_le_one]
    intro x hx y hy
    simp only [Finset.mem_filter] at hx hy
    exact huniq x hx.1 y hy.1 hx.2 hy.2
  calc
    (∑ x ∈ s, if p x then (1 : ℚ) else 0) = ((s.filter p).card : ℚ) := by simp
    _ ≤ (1 : ℚ) := by exact_mod_cast hcard
/-- The three singleton cuts cover every row once. -/
lemma hcov : ∀ r ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if r ∈ sep k then lam k else 0 := by
  intro r hr
  fin_cases r
  · exact one_le_sum_ite_one_of_exists K (fun k => (0 : Row) ∈ sep k) ⟨k0, by simp [K], by simp [sep]⟩
  · exact one_le_sum_ite_one_of_exists K (fun k => (1 : Row) ∈ sep k) ⟨k0, by simp [K], by simp [sep]⟩
  · exact one_le_sum_ite_one_of_exists K (fun k => (2 : Row) ∈ sep k) ⟨k0, by simp [K], by simp [sep]⟩
  · exact one_le_sum_ite_one_of_exists K (fun k => (3 : Row) ∈ sep k) ⟨k1, by simp [K], by simp [sep]⟩
  · exact one_le_sum_ite_one_of_exists K (fun k => (4 : Row) ∈ sep k) ⟨k1, by simp [K], by simp [sep]⟩
  · exact one_le_sum_ite_one_of_exists K (fun k => (5 : Row) ∈ sep k) ⟨k1, by simp [K], by simp [sep]⟩
  · exact one_le_sum_ite_one_of_exists K (fun k => (6 : Row) ∈ sep k) ⟨k2, by simp [K], by simp [sep]⟩
  · exact one_le_sum_ite_one_of_exists K (fun k => (7 : Row) ∈ sep k) ⟨k2, by simp [K], by simp [sep]⟩
  · exact one_le_sum_ite_one_of_exists K (fun k => (8 : Row) ∈ sep k) ⟨k2, by simp [K], by simp [sep]⟩

/-- No support edge is loaded by more than one singleton cut. -/
lemma hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ (1 : ℚ) := by
  intro c hc
  apply sum_ite_one_le_one_of_unique
  intro x hx y hy hpx hpy
  cases x <;> cases y <;> fin_cases c <;> simp [K, dB] at hx hy hpx hpy ⊢

/-- Every off-support cut load is routed into the door sink. -/
lemma hroute : ∀ c ∈ O,
    (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ ∑ j ∈ J, q c j := by
  intro c hc
  have hleft : (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ (1 : ℚ) := by
    apply sum_ite_one_le_one_of_unique
    intro x hx y hy hpx hpy
    cases x <;> cases y <;> fin_cases c <;> simp [K, dB] at hx hy hpx hpy ⊢
  have hright : (∑ j ∈ J, q c j) = (1 : ℚ) := by simp [J, q]
  simpa [hright] using hleft

/-- The routed off-support anchor exits fit into the door capacity. -/
lemma hcap : ∀ j ∈ J, (∑ c ∈ O, q c j) ≤ kap j := by
  intro j hj
  cases j
  calc
    (∑ c ∈ O, q c ()) = (O.card : ℚ) := by simp [q]
    _ ≤ (Fintype.card Edge : ℚ) := by exact_mod_cast (Finset.card_le_univ O)
    _ ≤ kap () := by norm_num [kap]

lemma hlam : ∀ k ∈ K, (0 : ℚ) ≤ lam k := by
  intro k hk
  simp [lam]

lemma hq : ∀ c ∈ O, ∀ j ∈ J, (0 : ℚ) ≤ q c j := by
  intro c hc j hj
  simp [q]

/-- The exact abstract no-dual certificate for the 24-vertex bare-SSE counterexample's banked core. -/
theorem bare_sse_24_no_dualCert :
    ¬ ∃ alpha beta gam del, IsDualCert S F O J K sep dB inc kap alpha beta gam del := by
  rintro ⟨alpha, beta, gam, del, hcert⟩
  rcases hcert with ⟨halpha, hbeta, hgam, hdel, hD1, hD2, hD3⟩
  exact relaxed_cover_weak_duality S F O J K sep dB lam q alpha beta gam del kap
    hlam halpha hbeta hgam hdel hq
    hcov hcong hroute hcap
    (fun c hc j hj _hpos => hD2 c hc j hj trivial)
    hD1 hD3

#print axioms bare_sse_24_no_dualCert


lemma hkap_nonneg : ∀ j ∈ J, (0 : ℚ) ≤ kap j := by
  intro j hj
  simp [kap]

/-- The compressed 24-vertex banked core satisfies the δ-eliminated banked cut-domination inequality. -/
theorem bare_sse_24_bankedCutDomination :
    BankedCutDomination S F O J K sep dB inc kap :=
  bankedCutDomination_of_no_dualCert S F O J K sep dB inc kap hkap_nonneg
    bare_sse_24_no_dualCert

#print axioms bare_sse_24_bankedCutDomination

end BareSSE24
end RCCPayloadFixtures
end Erdos23Delta0
