/-
Erdős #23 δ=0 — L1: blue distances and the ℓ ≥ 5 lemma.
Per LEAN_BRANCHB_BLUEPRINT_GPTPRO.md §2: this replaces the general odd-closed-walk
theorem in the CD op2 witness argument. Key content:
  blue_walk_parity : sides agree across a blue walk iff its length is even;
  badEdge_ell_ge_five : triangle-free ⟹ every connected bad edge has row length ≥ 5
    (ℓ = blue-dist + 1; ℓ ≠ 1 loopless, ℓ ≠ 3 triangle, parity kills even ℓ).
Self-contained module (Cut duplicated); unified at PR assembly.
-/

import Mathlib

namespace Erdos23Delta0
namespace Distances

variable {V : Type*}

/-- A two-sided cut (independent of the graph). -/
structure Cut (V : Type*) where
  side : V → Bool

variable (G : SimpleGraph V)

/-- The blue (bichromatic) subgraph of a cut. -/
def blueGraph (c : Cut V) : SimpleGraph V where
  Adj u v := G.Adj u v ∧ c.side u ≠ c.side v
  symm := fun _ _ ⟨ha, hs⟩ => ⟨ha.symm, Ne.symm hs⟩
  loopless := fun _ ⟨_, hs⟩ => hs rfl

/-- Along a blue walk the side flips each step: endpoints agree iff length is even. -/
theorem blue_walk_parity (c : Cut V) {u v : V} (p : (blueGraph G c).Walk u v) :
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

/-- Row length of a bad edge: blue distance + 1. -/
noncomputable def ell (c : Cut V) (u v : V) : ℕ :=
  (blueGraph G c).dist u v + 1

/-- Triangle-free ⟹ every blue-connected bad edge has row length at least 5. -/
theorem badEdge_ell_ge_five [DecidableEq V] (c : Cut V) {u v : V}
    (htf : G.CliqueFree 3) (hadj : G.Adj u v) (hbad : c.side u = c.side v)
    (hconn : (blueGraph G c).Reachable u v) :
    5 ≤ ell G c u v := by
  have hne : u ≠ v := G.ne_of_adj hadj
  obtain ⟨p, hp⟩ := hconn.exists_walk_length_eq_dist
  -- parity: the shortest walk has even length
  have hpar : Even ((blueGraph G c).dist u v) := by
    rw [← hp]
    exact (blue_walk_parity G c p).mp hbad
  -- dist ≠ 0 (endpoints differ)
  have hd0 : (blueGraph G c).dist u v ≠ 0 := by
    intro h0
    exact hne ((SimpleGraph.Reachable.dist_eq_zero_iff hconn).mp h0)
  -- dist ≠ 2 (would give a triangle)
  have hd2 : (blueGraph G c).dist u v ≠ 2 := by
    intro h2
    rw [h2] at hp
    -- extract the middle vertex of the length-2 walk
    cases p with
    | nil => simp at hp
    | cons h₁ q =>
      cases q with
      | nil => simp at hp
      | cons h₂ r =>
        cases r with
        | nil =>
          -- u —(h₁)— b —(h₂)— v plus the bad edge u—v: a triangle
          exact htf _ (SimpleGraph.is3Clique_triple_iff.mpr
            ⟨h₁.1, hadj, h₂.1⟩)
        | cons h₃ s => simp at hp
  -- even, ≠ 0, ≠ 2 ⟹ ≥ 4
  obtain ⟨k, hk⟩ := hpar
  unfold ell
  omega

end Distances
end Erdos23Delta0
