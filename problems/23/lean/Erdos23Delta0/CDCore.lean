/-
Erdős #23 δ=0 — L4: CD telescope, arithmetic core.
Per LEAN_CDOPS_DESIGN (sibling thread): each completion op carries the σ-drop q and the
residual ρ = 25·max(q,0); the per-op inequality 25·σpre ≤ 25·σpost + ρ telescopes over a
chained trace by list induction. Graph-side legality (footprint counts, terminalPrefix
witness) attaches per-constructor and does not affect this telescope.
-/

import Mathlib

namespace Erdos23Delta0
namespace CDCore

/-- Arithmetic content of one completion op. -/
structure OpArith where
  sigmaPre : ℤ
  sigmaPost : ℤ
  q : ℤ
  rho : ℤ
  hq : sigmaPre - sigmaPost = q
  hrho : rho = 25 * max q 0

/-- Per-op inequality: 25·σpre ≤ 25·σpost + ρ. -/
theorem OpArith.step (o : OpArith) : 25 * o.sigmaPre ≤ 25 * o.sigmaPost + o.rho := by
  have h1 : o.q ≤ max o.q 0 := le_max_left _ _
  have h2 : o.sigmaPre = o.sigmaPost + o.q := by linarith [o.hq]
  rw [h2, o.hrho]
  linarith

/-- ρ ≥ 0. -/
theorem OpArith.rho_nonneg (o : OpArith) : 0 ≤ o.rho := by
  rw [o.hrho]
  have : (0:ℤ) ≤ max o.q 0 := le_max_right _ _
  linarith

/-- Chained trace: σ-states link across the op list. -/
def chainFrom : ℤ → List OpArith → ℤ → Prop
  | s0, [], s1 => s0 = s1
  | s0, o :: ops, s1 => o.sigmaPre = s0 ∧ chainFrom o.sigmaPost ops s1

/-- Total residual of a trace. -/
def rhoSum (l : List OpArith) : ℤ := (l.map OpArith.rho).sum

@[simp] theorem rhoSum_nil : rhoSum [] = 0 := rfl

@[simp] theorem rhoSum_cons (o : OpArith) (l : List OpArith) :
    rhoSum (o :: l) = o.rho + rhoSum l := by
  unfold rhoSum
  simp

/-- THE CD TELESCOPE: over any chained trace, 25·σ_init ≤ 25·σ_final + Σρ. -/
theorem telescope : ∀ (l : List OpArith) (s0 s1 : ℤ),
    chainFrom s0 l s1 → 25 * s0 ≤ 25 * s1 + rhoSum l
  | [], s0, s1, h => by
      unfold chainFrom at h
      simp [h]
  | o :: ops, s0, s1, h => by
      obtain ⟨hpre, hrest⟩ := h
      have hstep := o.step
      have hih := telescope ops o.sigmaPost s1 hrest
      rw [rhoSum_cons]
      rw [← hpre]
      linarith

/-- Residual sums are nonnegative. -/
theorem rhoSum_nonneg (l : List OpArith) : 0 ≤ rhoSum l := by
  induction l with
  | nil => simp
  | cons o ops ih =>
      rw [rhoSum_cons]
      have := o.rho_nonneg
      linarith

/-- CD final form: if the completed switch satisfies ν_K ≥ 25·σ_final (the valid-switch
    inequality) then 25·σ_init ≤ ν_K + Σρ — completion dominance for the trace. -/
theorem completion_dominance (l : List OpArith) (s0 s1 nuK : ℤ)
    (hchain : chainFrom s0 l s1) (hvalid : 25 * s1 ≤ nuK) :
    25 * s0 ≤ nuK + rhoSum l := by
  have := telescope l s0 s1 hchain
  linarith

/-- The exchange quadruple with its defining identities — the Codex v5/v6 emission
    format. SIGN CONVENTION (design risk #1): σpre − σpost = (e_B(X,S) − e_M(X,S))
    − (e_B(X,O) − e_M(X,O)); reversing it flips the telescope. -/
structure ExchangeQuad where
  eB_XS : ℕ
  eM_XS : ℕ
  eB_XO : ℕ
  eM_XO : ℕ
  q : ℤ
  rho : ℤ
  q_eq : q = ((eB_XS : ℤ) - eM_XS) - ((eB_XO : ℤ) - eM_XO)
  rho_eq : rho = 25 * max 0 q

/-- A quad plus the σ-drop identity yields the telescope-ready op content. -/
def ExchangeQuad.toOpArith (Q : ExchangeQuad) (sPre sPost : ℤ)
    (hσ : sPre - sPost = Q.q) : OpArith where
  sigmaPre := sPre
  sigmaPost := sPost
  q := Q.q
  rho := Q.rho
  hq := hσ
  hrho := by rw [Q.rho_eq, max_comm]

theorem ExchangeQuad.rho_nonneg (Q : ExchangeQuad) : 0 ≤ Q.rho := by
  rw [Q.rho_eq]
  have : (0:ℤ) ≤ max 0 Q.q := le_max_left _ _
  linarith

theorem foldl_rho : ∀ (l : List OpArith) (init : ℤ),
    l.foldl (fun acc o => acc + o.rho) init = init + rhoSum l
  | [], init => by simp
  | o :: ops, init => by
      rw [List.foldl_cons, foldl_rho ops (init + o.rho), rhoSum_cons]
      ring

/-- foldl form of rhoSum (generated-trace compatibility). -/
theorem rhoSum_eq_foldl (l : List OpArith) :
    rhoSum l = l.foldl (fun acc o => acc + o.rho) 0 := by
  rw [foldl_rho l 0]
  ring

end CDCore
end Erdos23Delta0
