/-
Erdős #23 δ=0 — Cert layer step 1-2: normal-form polynomial arithmetic.
Per LEAN_CHECKER_DESIGN_GPTPRO.md: certificates are emitted as normalized monomial
lists; the PosCert arithmetic heart is: all coefficients nonnegative + all variables
evaluating nonnegatively ⟹ the value is nonnegative. Var := Nat with N = 0 never
specialized (N-parametric certificates carry N as an ordinary variable).
-/

import Mathlib

namespace Erdos23Delta0
namespace PolyCert

/-- Certificate variables (N = 0, w i = 1 + i, aux i = 1000 + i). -/
abbrev Var := Nat

/-- A monomial: rational coefficient and exponent list. -/
structure Mono where
  coeff : ℚ
  pows : List (Var × Nat)
deriving Repr

/-- Normal form: a list of monomials (the emitter's canonical format). -/
abbrev NF := List Mono

/-- Monomial evaluation. -/
def Mono.eval (env : Var → ℚ) (m : Mono) : ℚ :=
  m.coeff * (m.pows.map (fun p => env p.1 ^ p.2)).prod

/-- Normal-form evaluation. -/
def NF.eval (env : Var → ℚ) (f : NF) : ℚ :=
  (f.map (Mono.eval env)).sum

@[simp] theorem NF.eval_nil (env : Var → ℚ) : NF.eval env [] = 0 := rfl

@[simp] theorem NF.eval_cons (env : Var → ℚ) (m : Mono) (f : NF) :
    NF.eval env (m :: f) = m.eval env + NF.eval env f := by
  unfold NF.eval
  simp

/-- Boolean coefficient-nonnegativity check (the PosCert kernel test). -/
def NF.allCoeffNonneg (f : NF) : Bool :=
  f.all (fun m => decide (0 ≤ m.coeff))

/-- Powers of nonnegative values are nonnegative, hence so is each monomial with a
    nonnegative coefficient. -/
theorem Mono.eval_nonneg (env : Var → ℚ) (m : Mono)
    (hvars : ∀ v, 0 ≤ env v) (hc : 0 ≤ m.coeff) :
    0 ≤ m.eval env := by
  unfold Mono.eval
  apply mul_nonneg hc
  induction m.pows with
  | nil => simp
  | cons p ps ih =>
      simp only [List.map_cons, List.prod_cons]
      exact mul_nonneg (pow_nonneg (hvars p.1) p.2) ih

/-- THE POSCERT ARITHMETIC HEART: nonnegative coefficients over nonnegative variables
    give a nonnegative value. -/
theorem NF.eval_nonneg (env : Var → ℚ) (f : NF)
    (hvars : ∀ v, 0 ≤ env v) (hc : f.allCoeffNonneg = true) :
    0 ≤ f.eval env := by
  induction f with
  | nil => simp
  | cons m fs ih =>
      rw [NF.eval_cons]
      unfold NF.allCoeffNonneg at hc
      simp only [List.all_cons, Bool.and_eq_true, decide_eq_true_eq] at hc
      have h1 := Mono.eval_nonneg env m hvars hc.1
      have h2 := ih (by unfold NF.allCoeffNonneg; exact hc.2)
      linarith

/-- Pairwise products of nonnegative lists sum to a nonnegative value. -/
theorem zip_mul_sum_nonneg : ∀ (ms ss : List ℚ),
    (∀ x ∈ ms, 0 ≤ x) → (∀ x ∈ ss, 0 ≤ x) →
    0 ≤ (List.zipWith (· * ·) ms ss).sum
  | [], _, _, _ => by simp
  | _ :: _, [], _, _ => by simp
  | a :: as, b :: bs, hm, hs => by
      simp only [List.zipWith_cons_cons, List.sum_cons]
      have hrest := zip_mul_sum_nonneg as bs
        (fun x hx => hm x (List.mem_cons_of_mem _ hx))
        (fun x hx => hs x (List.mem_cons_of_mem _ hx))
      have ha := hm a (List.mem_cons_self ..)
      have hb := hs b (List.mem_cons_self ..)
      have := mul_nonneg ha hb
      linarith

/-- Linear combination soundness: target = base + Σ multᵢ·slackᵢ (as evaluated values)
    with nonnegative base, multipliers, and slacks gives a nonnegative target —
    the ConeCert value-level core. -/
theorem cone_value_nonneg (target base : ℚ) (mults slacks : List ℚ)
    (hid : target = base + (List.zipWith (· * ·) mults slacks).sum)
    (hbase : 0 ≤ base)
    (hmults : ∀ x ∈ mults, 0 ≤ x)
    (hslacks : ∀ x ∈ slacks, 0 ≤ x) :
    0 ≤ target := by
  rw [hid]
  have := zip_mul_sum_nonneg mults slacks hmults hslacks
  linarith

end PolyCert
end Erdos23Delta0
