import FormalConjectures.WrittenOnTheWallII.GraphConjecture314
import Mathlib.Combinatorics.SimpleGraph.ConcreteColorings
import Mathlib.Combinatorics.SimpleGraph.Metric

/-!
# Lean candidates for the structural route of WOWII 314

This file does not modify the target theorem.  It records the finite lemma
tree for `L1`--`L3` and compiles the first load-bearing pieces.

## Mathlib audit

`Mathlib.Combinatorics.SimpleGraph.Bipartite` explicitly leaves
"bipartite iff no odd cycle" as a TODO.  However,
`SimpleGraph.two_colorable_iff_forall_loop_even` is available from
`ConcreteColorings`; its contrapositive gives an odd closed walk immediately.

## Finite lemma tree

* `L1a` (compiled below): nonbipartite implies an odd closed walk.
* `L1b` (compiled below): choose one of minimum length.
* `L1c`: a minimum odd closed walk is a cycle.  If its tail support repeats a
  vertex, split at two occurrences; the two closed subwalk lengths add to the
  original odd length, so one is odd and strictly shorter.
* `L1d`: a shortest odd cycle is induced.  A chord splits it into two cycles;
  exactly one has odd length and is shorter.
* `L1e`: triangle-freeness gives length at least five.  Length at least seven
  exposes five consecutive vertices as an induced `P5`; `L0` excludes this.
  Hence the induced odd cycle has length five.
* `L2a`: relative to an induced `C5`, triangle-freeness bounds a vertex's
  cycle-neighborhood by two nonconsecutive vertices.
* `L2b`: one cycle-neighbor gives an explicit induced `P5`; hence every
  distance-one vertex has the signature `{c_(i-1), c_(i+1)}`.
* `L2c`: a distance-two vertex, its predecessor, and three consecutive cycle
  vertices give an induced `P5`; connectedness therefore puts every vertex at
  distance at most one from the cycle.
* `L2d`: equal or nonconsecutive signatures cannot be adjacent by
  triangle-freeness.  A missing edge between consecutive signatures gives
  `u-c_(i-1)-c_(i-2)-c_(i-3)-v`, an induced `P5`.  Thus consecutive bags are
  complete and the graph is an exact nonempty `C5` blow-up.
* `L3a` (compiled below): incomparable neighborhoods in one side of a
  bipartition give an induced `2K2` certificate.
* `L3b`: among the four endpoint pairs of that `2K2`, choose a pair of minimum
  graph distance and a shortest path.  Append the unused endpoint edge at
  each end.  Minimality eliminates every chord (the length-one end cases use
  bipartiteness), producing an induced path with at least five vertices.
* `L3c`: `L0` excludes five consecutive vertices of that path, so no induced
  `2K2` exists.  `L3a` then makes neighborhoods linearly ordered on each side.

No unbounded auxiliary hierarchy occurs: the only unfinished generic step is
the single minimum-odd-walk splitting lemma `L1c`; every later obstruction is
a fixed five-vertex certificate.
-/

open Classical

namespace WOWII314.StructureCandidates

open SimpleGraph

variable {V : Type*} [Fintype V] [DecidableEq V]
variable {G : SimpleGraph V} [DecidableRel G.Adj]

/-- The existing parity theorem supplies the missing first half of the
nonbipartite-to-odd-cycle route: a nonbipartite graph has an odd closed walk. -/
lemma not_bipartite_exists_odd_closed_walk (hG : ¬ G.IsBipartite) :
    ∃ v : V, ∃ w : G.Walk v v, Odd w.length := by
  change ¬ G.Colorable 2 at hG
  rw [two_colorable_iff_forall_loop_even] at hG
  push_neg at hG
  obtain ⟨v, w, hw⟩ := hG
  exact ⟨v, w, Nat.not_even_iff_odd.mp hw⟩

/-- An odd closed walk is nonempty. -/
lemma odd_closed_walk_ne_nil {v : V} {w : G.Walk v v} (hw : Odd w.length) :
    w ≠ .nil := by
  intro h
  subst w
  simp at hw

/-- In a simple graph an odd closed walk has at least three edges. -/
lemma odd_closed_walk_three_le_length {v : V} (w : G.Walk v v)
    (hw : Odd w.length) : 3 ≤ w.length := by
  match w with
  | .nil => simp at hw
  | .cons h .nil => simp at h
  | .cons _ (.cons _ .nil) => norm_num [Walk.length_cons] at hw
  | .cons _ (.cons _ (.cons _ _)) =>
      simp only [Walk.length_cons]
      omega

/-- A shortest odd closed walk, packaged with exactly the minimality property
needed to prove that it is a cycle. -/
structure ShortestOddClosedWalk (G : SimpleGraph V) where
  vertex : V
  walk : G.Walk vertex vertex
  odd_length : Odd walk.length
  minimal : ∀ {u : V} (q : G.Walk u u), Odd q.length → walk.length ≤ q.length

/-- Nonbipartiteness supplies a shortest odd closed walk by well-ordering of
natural-number lengths. -/
lemma exists_shortest_odd_closed_walk (hG : ¬ G.IsBipartite) :
    ∃ v : V, ∃ w : G.Walk v v, Odd w.length ∧
      ∀ {u : V} (q : G.Walk u u), Odd q.length → w.length ≤ q.length := by
  have hex : ∃ n : ℕ, ∃ v : V, ∃ w : G.Walk v v,
      w.length = n ∧ Odd n := by
    obtain ⟨v, w, hw⟩ := not_bipartite_exists_odd_closed_walk hG
    exact ⟨w.length, v, w, rfl, hw⟩
  obtain ⟨v, w, hlen, hodd⟩ := Nat.find_spec hex
  refine ⟨v, w, hlen ▸ hodd, ?_⟩
  intro u q hq
  rw [hlen]
  exact Nat.find_min' hex ⟨u, q, rfl, hq⟩

/-- The six adjacency/nonadjacency facts constituting an induced `2K2` with
edges `xy` and `x'y'`. -/
structure IsInducedTwoKTwoAt (G : SimpleGraph V) (x y x' y' : V) : Prop where
  adj_left : G.Adj x y
  adj_right : G.Adj x' y'
  not_adj_cross_left : ¬ G.Adj x y'
  not_adj_cross_right : ¬ G.Adj x' y
  not_adj_same_left : ¬ G.Adj x x'
  not_adj_same_right : ¬ G.Adj y y'

lemma not_adj_of_mem_left_of_isBipartiteWith
    {X Y : Set V} (hXY : G.IsBipartiteWith X Y)
    {x x' : V} (hx : x ∈ X) (hx' : x' ∈ X) : ¬ G.Adj x x' := by
  intro hxx'
  exact Set.disjoint_left.mp
    (isBipartiteWith_neighborSet_disjoint hXY hx)
    (by simpa using hxx') hx'

lemma not_adj_of_mem_right_of_isBipartiteWith
    {X Y : Set V} (hXY : G.IsBipartiteWith X Y)
    {y y' : V} (hy : y ∈ Y) (hy' : y' ∈ Y) : ¬ G.Adj y y' := by
  intro hyy'
  exact Set.disjoint_left.mp
    (isBipartiteWith_neighborSet_disjoint' hXY hy)
    (by simpa using hyy') hy'

/-- Incomparable neighborhoods on one side of a bipartition give a fully
explicit induced `2K2`.  This is the algebraic core of the chain-graph branch. -/
lemma incomparable_neighborSets_induce_twoKTwo
    {X Y : Set V} (hXY : G.IsBipartiteWith X Y)
    {x x' : V} (hx : x ∈ X) (hx' : x' ∈ X)
    (hnotle : ¬ G.neighborSet x ⊆ G.neighborSet x')
    (hnotge : ¬ G.neighborSet x' ⊆ G.neighborSet x) :
    ∃ y y' : V, IsInducedTwoKTwoAt G x y x' y' := by
  obtain ⟨y, hyx, hyx'⟩ := Set.not_subset.mp hnotle
  obtain ⟨y', hy'x', hy'x⟩ := Set.not_subset.mp hnotge
  have hxy : G.Adj x y := by simpa using hyx
  have hx'y' : G.Adj x' y' := by simpa using hy'x'
  have hnyx' : ¬ G.Adj x' y := by simpa using hyx'
  have hny'x : ¬ G.Adj x y' := by simpa using hy'x
  have hyY : y ∈ Y := hXY.mem_of_mem_adj hx hxy
  have hy'Y : y' ∈ Y := hXY.mem_of_mem_adj hx' hx'y'
  exact ⟨y, y', ⟨hxy, hx'y', hny'x, hnyx',
    not_adj_of_mem_left_of_isBipartiteWith hXY hx hx',
    not_adj_of_mem_right_of_isBipartiteWith hXY hyY hy'Y⟩⟩

/-- Once induced `2K2`s are forbidden, neighborhoods on either fixed side of
a bipartition are comparable. -/
lemma neighborSets_comparable_of_no_induced_twoKTwo
    {X Y : Set V} (hXY : G.IsBipartiteWith X Y)
    (hfree : ∀ x y x' y' : V, ¬ IsInducedTwoKTwoAt G x y x' y')
    {x x' : V} (hx : x ∈ X) (hx' : x' ∈ X) :
    G.neighborSet x ⊆ G.neighborSet x' ∨
      G.neighborSet x' ⊆ G.neighborSet x := by
  by_contra h
  rw [not_or] at h
  obtain ⟨y, y', h2k2⟩ :=
    incomparable_neighborSets_induce_twoKTwo hXY hx hx' h.1 h.2
  exact hfree x y x' y' h2k2
/-- In a triangle-free graph, two vertices with a common neighbor are not
adjacent.  This closes all same-bag and nonconsecutive-bag nonedge cases. -/
lemma not_adj_of_common_neighbor
    (hTriFree : ∀ a b c : V, G.Adj a b → G.Adj b c → G.Adj c a → False)
    {a b c : V} (hac : G.Adj a c) (hbc : G.Adj b c) : ¬ G.Adj a b := by
  intro hab
  exact hTriFree a b c hab hbc hac.symm

/-- The target's pointwise triangle-free hypothesis implies mathlib's
`CliqueFree 3` predicate. -/
lemma cliqueFree_three_of_triangle_free
    (hTriFree : ∀ a b c : V, G.Adj a b → G.Adj b c → G.Adj c a → False) :
    G.CliqueFree 3 := by
  intro s hs
  rw [is3Clique_iff] at hs
  obtain ⟨a, b, c, hab, hac, hbc, rfl⟩ := hs
  exact hTriFree a b c hab hbc hac.symm

/-- A triangle-free graph has no three-edge cycle. -/
lemma cycle_length_ne_three_of_triangle_free
    (hTriFree : ∀ a b c : V, G.Adj a b → G.Adj b c → G.Adj c a → False)
    {v : V} {c : G.Walk v v} (hc : c.IsCycle) : c.length ≠ 3 := by
  intro hlen
  have hcliques : ∃ s : Finset V, G.IsNClique 3 s :=
    is3Clique_iff_exists_cycle_length_three.mpr ⟨v, c, hc, hlen⟩
  obtain ⟨s, hs⟩ := hcliques
  exact (cliqueFree_three_of_triangle_free hTriFree) s hs

/-- Every odd cycle in a triangle-free graph has at least five edges. -/
lemma five_le_length_of_odd_cycle_triangle_free
    (hTriFree : ∀ a b c : V, G.Adj a b → G.Adj b c → G.Adj c a → False)
    {v : V} {c : G.Walk v v} (hc : c.IsCycle)
    (hodd : Odd c.length) : 5 ≤ c.length := by
  have hthree : 3 ≤ c.length := hc.three_le_length
  have hnthree : c.length ≠ 3 :=
    cycle_length_ne_three_of_triangle_free hTriFree hc
  have hnfour : c.length ≠ 4 := by
    intro h
    rw [h] at hodd
    norm_num at hodd
  omega

end WOWII314.StructureCandidates
