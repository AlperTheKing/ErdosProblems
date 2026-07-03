/-
Erdős #23 δ=0 — L2: vector-indexed Row record and its walk/distance bridges.
Per LEAN_BRANCHB_BLUEPRINT_GPTPRO.md §1.3: a row is a shortest blue path joining the
endpoints of a bad edge, stored with Fin indexing (edge count n = ℓ − 1, so q : Fin (n+1)).
Proves: toWalk (with length n), dist = n (shortestness bridge), and Even n (parity).
Self-contained module; unified at PR assembly.
-/

import Mathlib

namespace Erdos23Delta0
namespace Rows

variable {V : Type*}

/-- A two-sided cut. -/
structure Cut (V : Type*) where
  side : V → Bool

variable (G : SimpleGraph V)

/-- The blue (bichromatic) subgraph of a cut. -/
def blueGraph (c : Cut V) : SimpleGraph V where
  Adj u v := G.Adj u v ∧ c.side u ≠ c.side v
  symm := fun _ _ ⟨ha, hs⟩ => ⟨ha.symm, Ne.symm hs⟩
  loopless := fun _ ⟨_, hs⟩ => hs rfl

/-- A row of blue-edge count `n` (row length ℓ = n+1): a shortest blue path
    joining the endpoints of a bad edge. -/
structure Row (c : Cut V) where
  n : ℕ
  hn : 4 ≤ n
  q : Fin (n + 1) → V
  inj : Function.Injective q
  bad_adj : G.Adj (q 0) (q (Fin.last n))
  bad_same : c.side (q 0) = c.side (q (Fin.last n))
  blue_step : ∀ i : Fin n, (blueGraph G c).Adj (q i.castSucc) (q i.succ)
  shortest : n ≤ (blueGraph G c).dist (q 0) (q (Fin.last n))

namespace Row

variable {G} {c : Cut V} (R : Row G c)

/-- The initial segment walk `q 0 → q m`, built by concatenating blue steps. -/
def walkTo : ∀ (m : ℕ) (hm : m ≤ R.n),
    (blueGraph G c).Walk (R.q 0) (R.q ⟨m, by omega⟩)
  | 0, _ => SimpleGraph.Walk.nil
  | (m + 1), hm =>
      (walkTo m (by omega)).concat
        (by
          have h := R.blue_step ⟨m, by omega⟩
          have h1 : (⟨m, by omega⟩ : Fin R.n).castSucc =
              (⟨m, by omega⟩ : Fin (R.n + 1)) := rfl
          have h2 : (⟨m, by omega⟩ : Fin R.n).succ =
              (⟨m + 1, by omega⟩ : Fin (R.n + 1)) := rfl
          rw [h1, h2] at h
          exact h)

theorem walkTo_length : ∀ (m : ℕ) (hm : m ≤ R.n), (R.walkTo m hm).length = m
  | 0, _ => rfl
  | (m + 1), hm => by
      unfold walkTo
      rw [SimpleGraph.Walk.length_concat, walkTo_length m (by omega)]

/-- The full row walk `q 0 → q (last n)`. -/
def toWalk : (blueGraph G c).Walk (R.q 0) (R.q (Fin.last R.n)) := by
  have h : (Fin.last R.n) = (⟨R.n, by omega⟩ : Fin (R.n + 1)) := rfl
  rw [h]
  exact R.walkTo R.n le_rfl

theorem toWalk_length : R.toWalk.length = R.n := by
  unfold toWalk
  simpa using R.walkTo_length R.n le_rfl

/-- Shortestness bridge: the row realizes the blue distance exactly. -/
theorem dist_eq : (blueGraph G c).dist (R.q 0) (R.q (Fin.last R.n)) = R.n := by
  have hle : (blueGraph G c).dist (R.q 0) (R.q (Fin.last R.n)) ≤ R.n := by
    have := SimpleGraph.dist_le R.toWalk
    rwa [R.toWalk_length] at this
  exact le_antisymm hle R.shortest

/-- Along a blue walk the side flips each step. -/
theorem blue_walk_parity {u v : V} (p : (blueGraph G c).Walk u v) :
    (c.side u = c.side v) ↔ Even p.length := by
  induction p with
  | nil => simp
  | @cons a b w h q ih =>
    have hs : c.side a ≠ c.side b := h.2
    rw [SimpleGraph.Walk.length_cons, Nat.even_add_one]
    constructor
    · intro hav hq
      exact hs (hav.trans (ih.mpr hq).symm)
    · intro hodd
      have hbw : ¬(c.side b = c.side w) := fun h' => hodd (ih.mp h')
      cases ha : c.side a <;> cases hb : c.side b <;> cases hw : c.side w <;>
        simp_all

/-- Rows have even blue-edge count (bad endpoints share a side). -/
theorem even_n : Even R.n := by
  have := (blue_walk_parity R.toWalk).mp R.bad_same
  rwa [R.toWalk_length] at this

/-- Row length ℓ = n + 1 is at least 5. -/
theorem ell_ge_five : 5 ≤ R.n + 1 := by
  have := R.hn
  omega

end Row

end Rows
end Erdos23Delta0
