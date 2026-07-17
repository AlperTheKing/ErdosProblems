import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.LargestInducedTree
import FormalConjecturesForMathlib.Combinatorics.SimpleGraph.Degrees
import Mathlib.Data.Set.Finite.Lemmas

open SimpleGraph
example {α : Type*} [Fintype α] [DecidableEq α] {G : SimpleGraph α} {s : Finset α}
    (hs : (G.induce (s : Set α)).IsTree) : s.card ≤ largestInducedTreeSize G :=
  card_le_largestInducedTreeSize hs
#check @SimpleGraph.Walk.exists_boundary_dart
#check @Set.exists_max_image
#check @SimpleGraph.Path.cons_isCycle
#check @SimpleGraph.girth_le_length
#check @SimpleGraph.Walk.induce_support_isTree_of_length_eq_dist
#check @SimpleGraph.girth_sub_one_le_largestInducedTreeSize
#check @SimpleGraph.secondSmallestDegree
