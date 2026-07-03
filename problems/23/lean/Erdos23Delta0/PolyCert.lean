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

/-! ### NF arithmetic (append / negate / multiply) with evaluation soundness.

Products concatenate power lists and re-canonicalize them by variable-sorted
insertion with exponent addition; evaluation is preserved (`pow_add`), so
soundness never depends on the emitter's ordering. -/

/-- Power-list product (the monomial body). -/
def prodPows (env : Var → ℚ) (l : List (Var × Nat)) : ℚ :=
  (l.map (fun p => env p.1 ^ p.2)).prod

@[simp] theorem prodPows_nil (env : Var → ℚ) : prodPows env [] = 1 := rfl

@[simp] theorem prodPows_cons (env : Var → ℚ) (p : Var × Nat) (l : List (Var × Nat)) :
    prodPows env (p :: l) = env p.1 ^ p.2 * prodPows env l := by
  unfold prodPows
  simp

theorem prodPows_append (env : Var → ℚ) (l₁ l₂ : List (Var × Nat)) :
    prodPows env (l₁ ++ l₂) = prodPows env l₁ * prodPows env l₂ := by
  unfold prodPows
  simp

theorem Mono.eval_eq_prodPows (env : Var → ℚ) (m : Mono) :
    m.eval env = m.coeff * prodPows env m.pows := rfl

/-- Insert one power into a variable-sorted power list, adding exponents on match. -/
def insertPow (p : Var × Nat) : List (Var × Nat) → List (Var × Nat)
  | [] => [p]
  | q :: qs =>
      if p.1 < q.1 then p :: q :: qs
      else if p.1 = q.1 then (q.1, p.2 + q.2) :: qs
      else q :: insertPow p qs

theorem insertPow_prod (env : Var → ℚ) (p : Var × Nat) : ∀ l : List (Var × Nat),
    prodPows env (insertPow p l) = env p.1 ^ p.2 * prodPows env l
  | [] => by simp [insertPow]
  | q :: qs => by
      unfold insertPow
      by_cases h1 : p.1 < q.1
      · simp [h1]
      · by_cases h2 : p.1 = q.1
        · rw [if_neg h1, if_pos h2]
          simp only [prodPows_cons]
          rw [h2, pow_add]
          ring
        · rw [if_neg h1, if_neg h2]
          simp only [prodPows_cons]
          rw [insertPow_prod env p qs]
          ring

/-- Canonicalize a power list (variable-sorted, merged exponents). -/
def canonPows : List (Var × Nat) → List (Var × Nat)
  | [] => []
  | p :: ps => insertPow p (canonPows ps)

theorem canonPows_prod (env : Var → ℚ) : ∀ l : List (Var × Nat),
    prodPows env (canonPows l) = prodPows env l
  | [] => rfl
  | p :: ps => by
      unfold canonPows
      rw [insertPow_prod, canonPows_prod env ps, prodPows_cons]

/-- Monomial product (canonicalized powers). -/
def Mono.mul (m₁ m₂ : Mono) : Mono :=
  ⟨m₁.coeff * m₂.coeff, canonPows (m₁.pows ++ m₂.pows)⟩

theorem Mono.mul_eval (env : Var → ℚ) (m₁ m₂ : Mono) :
    (m₁.mul m₂).eval env = m₁.eval env * m₂.eval env := by
  simp only [Mono.mul, Mono.eval_eq_prodPows, canonPows_prod, prodPows_append]
  ring

theorem NF.eval_append (env : Var → ℚ) (f g : NF) :
    NF.eval env (f ++ g) = NF.eval env f + NF.eval env g := by
  unfold NF.eval
  simp

/-- Monomial × NF. -/
def NF.mulMono (m : Mono) (g : NF) : NF := g.map (Mono.mul m)

theorem NF.mulMono_eval (env : Var → ℚ) (m : Mono) : ∀ g : NF,
    NF.eval env (NF.mulMono m g) = m.eval env * NF.eval env g
  | [] => by simp [NF.mulMono]
  | n :: g => by
      unfold NF.mulMono at *
      simp only [List.map_cons, NF.eval_cons, Mono.mul_eval,
        NF.mulMono_eval env m g]
      ring

/-- NF product. -/
def NF.mul : NF → NF → NF
  | [], _ => []
  | m :: f, g => NF.mulMono m g ++ NF.mul f g

theorem NF.mul_eval (env : Var → ℚ) : ∀ f g : NF,
    NF.eval env (NF.mul f g) = NF.eval env f * NF.eval env g
  | [], g => by simp [NF.mul]
  | m :: f, g => by
      unfold NF.mul
      rw [NF.eval_append, NF.mulMono_eval, NF.eval_cons, NF.mul_eval env f g]
      ring

/-- NF negation. -/
def NF.neg (f : NF) : NF := f.map (fun m => ⟨-m.coeff, m.pows⟩)

theorem NF.neg_eval (env : Var → ℚ) : ∀ f : NF,
    NF.eval env (NF.neg f) = -NF.eval env f
  | [] => by simp [NF.neg]
  | m :: f => by
      unfold NF.neg at *
      simp only [List.map_cons, NF.eval_cons, NF.neg_eval env f]
      unfold Mono.eval
      simp
      ring

/-- NF subtraction. -/
def NF.sub (f g : NF) : NF := f ++ NF.neg g

theorem NF.sub_eval (env : Var → ℚ) (f g : NF) :
    NF.eval env (NF.sub f g) = NF.eval env f - NF.eval env g := by
  unfold NF.sub
  rw [NF.eval_append, NF.neg_eval]
  ring

/-! ### checkEq: grouping-based zero test.

`collect` groups monomials by syntactically equal power lists (adding
coefficients); `isZeroNF` then demands every collected coefficient be zero.
Soundness needs no ordering; completeness is the emitter's canonicalization
obligation (variable-sorted powers, no zero exponents). -/

/-- Add a monomial into a collected NF: merge with the first syntactically equal
    power list, else append at the end. -/
def insertAdd (m : Mono) : NF → NF
  | [] => [m]
  | n :: g =>
      if m.pows = n.pows then ⟨m.coeff + n.coeff, n.pows⟩ :: g
      else n :: insertAdd m g

theorem insertAdd_eval (env : Var → ℚ) (m : Mono) : ∀ g : NF,
    NF.eval env (insertAdd m g) = m.eval env + NF.eval env g
  | [] => by simp [insertAdd]
  | n :: g => by
      unfold insertAdd
      by_cases h : m.pows = n.pows
      · simp only [h, if_true, NF.eval_cons]
        unfold Mono.eval
        rw [h]
        ring
      · simp only [h, if_false, NF.eval_cons, insertAdd_eval env m g]
        ring

/-- Group all monomials by equal power lists. -/
def collect : NF → NF
  | [] => []
  | m :: f => insertAdd m (collect f)

theorem collect_eval (env : Var → ℚ) : ∀ f : NF,
    NF.eval env (collect f) = NF.eval env f
  | [] => rfl
  | m :: f => by
      unfold collect
      rw [insertAdd_eval, NF.eval_cons, collect_eval env f]

/-- All-zero coefficient test. -/
def isZeroNF (f : NF) : Bool := f.all (fun m => decide (m.coeff = 0))

theorem isZeroNF_eval (env : Var → ℚ) : ∀ f : NF,
    isZeroNF f = true → NF.eval env f = 0
  | [], _ => rfl
  | m :: f, h => by
      unfold isZeroNF at h
      simp only [List.all_cons, Bool.and_eq_true, decide_eq_true_eq] at h
      rw [NF.eval_cons, isZeroNF_eval env f (by unfold isZeroNF; exact h.2)]
      unfold Mono.eval
      rw [h.1]
      ring

/-- THE IDENTITY CHECKER: polynomial equality via collected difference. -/
def checkEq (f g : NF) : Bool := isZeroNF (collect (NF.sub f g))

/-- checkEq soundness: a passing check gives equal evaluations in every
    environment — the ConeCert identity bridge. -/
theorem checkEq_sound (f g : NF) (h : checkEq f g = true) (env : Var → ℚ) :
    NF.eval env f = NF.eval env g := by
  unfold checkEq at h
  have h0 := isZeroNF_eval env _ h
  rw [collect_eval, NF.sub_eval] at h0
  linarith

/-! ### PosCert: positivity via aux-substitution.

Aux variables stand for shifted quantities (e.g. aux₀ = N − 5) defined by
coefficient-nonnegative NFs over base/earlier variables; a polynomial that is
coefficient-nonnegative over the extended variables is nonnegative whenever the
base environment is. -/

/-- Extend an environment by evaluating aux definitions in order (later
    definitions may refer to earlier aux variables). -/
def extendEnv (env : Var → ℚ) : List (Var × NF) → (Var → ℚ)
  | [] => env
  | (v, d) :: rest =>
      extendEnv (fun w => if w = v then d.eval env else env w) rest

theorem extendEnv_nonneg : ∀ (defs : List (Var × NF)) (env : Var → ℚ),
    (∀ w, 0 ≤ env w) →
    defs.all (fun p => p.2.allCoeffNonneg) = true →
    ∀ w, 0 ≤ extendEnv env defs w
  | [], env, henv, _, w => henv w
  | (v, d) :: rest, env, henv, hdefs, w => by
      simp only [List.all_cons, Bool.and_eq_true] at hdefs
      have hd : 0 ≤ d.eval env := NF.eval_nonneg env d henv hdefs.1
      have henv' : ∀ u, 0 ≤ (fun u => if u = v then d.eval env else env u) u := by
        intro u
        by_cases h : u = v <;> simp [h, hd, henv u]
      exact extendEnv_nonneg rest _ henv' hdefs.2 w

/-- Positivity certificate: an NF over extended variables, all coefficients
    nonnegative, with coefficient-nonnegative aux definitions. -/
structure PosCert where
  nf : NF
  auxDefs : List (Var × NF)
  hcoeff : nf.allCoeffNonneg = true
  hauxCoeff : auxDefs.all (fun p => p.2.allCoeffNonneg) = true

/-- PosCert soundness: nonnegative base environment gives nonnegative value. -/
theorem PosCert.sound (c : PosCert) (env : Var → ℚ) (henv : ∀ w, 0 ≤ env w) :
    0 ≤ c.nf.eval (extendEnv env c.auxDefs) :=
  NF.eval_nonneg _ c.nf (extendEnv_nonneg c.auxDefs env henv c.hauxCoeff) c.hcoeff

/-! ### ConeCert: target = base + Σ multᵢ·slackᵢ as a checked polynomial
identity, with coefficient-nonnegative base and multipliers; slack
nonnegativity enters as graph-side hypotheses. -/

/-- The combination polynomial base + Σ multᵢ·slackᵢ. -/
def comboNF (base : NF) (mults slacks : List NF) : NF :=
  base ++ (List.zipWith NF.mul mults slacks).flatten

theorem zip_nfmul_flatten_eval (env : Var → ℚ) : ∀ ms ss : List NF,
    NF.eval env (List.zipWith NF.mul ms ss).flatten
      = (List.zipWith (fun f g => NF.eval env f * NF.eval env g) ms ss).sum
  | [], _ => by simp [NF.eval]
  | _ :: _, [] => by simp [NF.eval]
  | f :: fs, g :: gs => by
      simp only [List.zipWith_cons_cons, List.flatten_cons, List.sum_cons]
      rw [NF.eval_append, NF.mul_eval, zip_nfmul_flatten_eval env fs gs]

theorem zip_nfmul_sum_nonneg (env : Var → ℚ) (henv : ∀ v, 0 ≤ env v) :
    ∀ ms ss : List NF,
    ms.all NF.allCoeffNonneg = true →
    (∀ s ∈ ss, 0 ≤ NF.eval env s) →
    0 ≤ (List.zipWith (fun f g => NF.eval env f * NF.eval env g) ms ss).sum
  | [], _, _, _ => by simp
  | _ :: _, [], _, _ => by simp
  | f :: fs, g :: gs, hm, hs => by
      simp only [List.all_cons, Bool.and_eq_true] at hm
      have hf : 0 ≤ NF.eval env f := NF.eval_nonneg env f henv hm.1
      have hg : 0 ≤ NF.eval env g := hs g (List.mem_cons_self ..)
      have hrest := zip_nfmul_sum_nonneg env henv fs gs hm.2
        (fun s hsm => hs s (List.mem_cons_of_mem _ hsm))
      simp only [List.zipWith_cons_cons, List.sum_cons]
      have := mul_nonneg hf hg
      linarith

/-- Cone certificate: a checked identity target = base + Σ multᵢ·slackᵢ with
    coefficient-nonnegative base and multipliers. -/
structure ConeCert where
  target : NF
  base : NF
  mults : List NF
  slacks : List NF
  hid : checkEq target (comboNF base mults slacks) = true
  hbase : base.allCoeffNonneg = true
  hmults : mults.all NF.allCoeffNonneg = true

/-- CONECERT SOUNDNESS: nonnegative variables and nonnegative slack values give
    a nonnegative target — the machine-certificate bridge for the A1 cones,
    seed banks, and CrossCap capacity identities. -/
theorem ConeCert.sound (c : ConeCert) (env : Var → ℚ)
    (hvars : ∀ v, 0 ≤ env v)
    (hslacks : ∀ s ∈ c.slacks, 0 ≤ NF.eval env s) :
    0 ≤ NF.eval env c.target := by
  rw [checkEq_sound _ _ c.hid env]
  unfold comboNF
  rw [NF.eval_append, zip_nfmul_flatten_eval]
  have hbase := NF.eval_nonneg env c.base hvars c.hbase
  have hzip := zip_nfmul_sum_nonneg env hvars c.mults c.slacks c.hmults hslacks
  linarith

end PolyCert
end Erdos23Delta0
