import Erdos23Delta0.RelaxedCoverDuality
import Erdos23Delta0.BankedCutDominationCore

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

abbrev Row := Fin 9
abbrev Edge := Fin 17
abbrev CutId := Fin 3
abbrev Sink := Fin 1

/-- All nine K3,3 bad rows. -/
def S : Finset Row := {(0 : Row), 1, 2, 3, 4, 5, 6, 7, 8}

/-- The eight double-star support edges. -/
def F : Finset Edge := {(0 : Edge), 1, 2, 3, 4, 5, 6, 7}

/-- The nine loaded off-support anchor exits. -/
def O : Finset Edge := {(8 : Edge), 9, 10, 11, 12, 13, 14, 15, 16}

/-- The single door sink. -/
def J : Finset Sink := {(0 : Sink)}

/-- The three left-singleton cuts. -/
def K : Finset CutId := {(0 : CutId), 1, 2}

/-- Cut `k` covers exactly the three rows whose left endpoint is `k`. -/
def sep (k : CutId) : Finset Row :=
  if (k : Nat) = 0 then {(0 : Row), 1, 2}
  else if (k : Nat) = 1 then {(3 : Row), 4, 5}
  else {(6 : Row), 7, 8}

/-- Boundary load of cut `k`: one support spoke plus three left anchor exits. -/
def dB (k : CutId) : Finset Edge :=
  if (k : Nat) = 0 then {(0 : Edge), 8, 9, 10}
  else if (k : Nat) = 1 then {(1 : Edge), 11, 12, 13}
  else {(2 : Edge), 14, 15, 16}

/-- One unit of cover on each singleton cut. -/
def lam (_k : CutId) : ℚ := 1

/-- Every compressed off-support exit routes one unit to the door sink. -/
def q (_e : Edge) (_j : Sink) : ℚ := 1

/-- Door capacity for the compressed nonzero core; 17 is a safe compressed overcapacity. -/
def kap (_j : Sink) : ℚ := 17

/-- In this fixture every off-support edge may spend the door bank. -/
def inc (_e : Edge) (_j : Sink) : Prop := True

example : (0 : Row) ∈ sep 0 := by decide
example : (8 : Edge) ∈ dB 0 := by decide
example : (16 : Edge) ∈ O := by decide

/-- The three singleton cuts cover every row once. -/
lemma hcov : ∀ r ∈ S, (1 : ℚ) ≤ ∑ k ∈ K, if r ∈ sep k then lam k else 0 := by
  intro r hr
  fin_cases r <;> decide

/-- No support edge is loaded by more than one singleton cut. -/
lemma hcong : ∀ c ∈ F, (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ (1 : ℚ) := by
  intro c hc
  fin_cases c <;> decide

/-- Every off-support cut load is routed into the door sink. -/
lemma hroute : ∀ c ∈ O,
    (∑ k ∈ K, if c ∈ dB k then lam k else 0) ≤ ∑ j ∈ J, q c j := by
  intro c hc
  fin_cases c <;> decide

/-- The routed off-support anchor exits fit into the door capacity. -/
lemma hcap : ∀ j ∈ J, (∑ c ∈ O, q c j) ≤ kap j := by
  intro j hj
  fin_cases j
  calc
    (∑ c ∈ O, q c (0 : Sink)) = (O.card : ℚ) := by simp [q]
    _ ≤ (Fintype.card Edge : ℚ) := by exact_mod_cast (Finset.card_le_univ O)
    _ ≤ kap (0 : Sink) := by norm_num [kap]

lemma hlam : ∀ k ∈ K, (0 : ℚ) ≤ lam k := by
  intro k hk
  norm_num [lam]

lemma hq : ∀ c ∈ O, ∀ j ∈ J, (0 : ℚ) ≤ q c j := by
  intro c hc j hj
  norm_num [q]

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

end BareSSE24
end RCCPayloadFixtures
end Erdos23Delta0
