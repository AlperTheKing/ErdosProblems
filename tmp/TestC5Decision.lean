import FormalConjectures.WrittenOnTheWallII.GraphConjecture314
import Mathlib.Combinatorics.SimpleGraph.Circulant

open SimpleGraph

lemma test_cycleGraph_five_minimal_tds_card (S : Finset (Fin 5))
    (hS : IsMinimalTotalDominatingSet (cycleGraph 5) S) : S.card = 3 := by
  revert S
  unfold IsMinimalTotalDominatingSet IsTotalDominatingSet
  decide
