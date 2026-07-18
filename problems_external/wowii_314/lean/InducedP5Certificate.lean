import FormalConjectures.WrittenOnTheWallII.GraphConjecture314
import Mathlib.Combinatorics.SimpleGraph.Hasse
import Mathlib.Combinatorics.SimpleGraph.Metric

/-!
# A reusable induced-P5 certificate

The first five vertices of a chordless walk with at least four edges induce
`pathGraph 5`.  This is the fixed certificate used by structural lemmas
`L1e`, `L2`, and `L3` for WOWII Conjecture 314.
-/

open Classical

namespace WOWII314.InducedP5Certificate

open SimpleGraph

variable {V : Type*} {G : SimpleGraph V}

/-- A walk has no chords when adjacency among its indexed vertices occurs
exactly at consecutive indices. -/
def Walk.IsChordless {u v : V} (p : G.Walk u v) : Prop :=
  ∀ i j : ℕ, i ≤ p.length → j ≤ p.length →
    (G.Adj (p.getVert i) (p.getVert j) ↔ i + 1 = j ∨ j + 1 = i)

noncomputable def inducedPathGraphFiveEmbedding {u v : V} (p : G.Walk u v)
    (hp : p.IsPath) (hlen : 4 ≤ p.length) (hchord : p.IsChordless) :
    pathGraph 5 ↪g G where
  toFun i := p.getVert i.val
  inj' := by
    intro i j hij
    apply Fin.ext
    exact hp.getVert_injOn (by simp; omega) (by simp; omega) hij
  map_rel_iff' := by
    intro i j
    rw [pathGraph_adj]
    exact (hchord i.val j.val (by omega) (by omega)).symm

lemma inducedPathGraphFive_of_chordless_walk {u v : V} (p : G.Walk u v)
    (hp : p.IsPath) (hlen : 4 ≤ p.length) (hchord : p.IsChordless) :
    SimpleGraph.IsIndContained (pathGraph 5) G :=
  ⟨inducedPathGraphFiveEmbedding p hp hlen hchord⟩

end WOWII314.InducedP5Certificate
