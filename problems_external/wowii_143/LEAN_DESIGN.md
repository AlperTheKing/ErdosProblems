# W143 Lean 4 design

Date: 2026-07-17

Scope: decompose the proof in `PROOF.md` into small proof obligations for
`FormalConjectures/WrittenOnTheWallII/GraphConjecture143.lean`.  No Lean build was
run while preparing this design, as requested.  All declarations below are
proposed statements, not compilation claims.

## Direct route and arithmetic normal form

The exact final goal is

```lean
(G.girth : ℝ) + 1 ≤
  (largestInducedTreeSize G : ℝ) * (secondSmallestDegree G : ℝ)
```

Prove the corresponding natural-number inequality first and cast only once:

```lean
have hnat :
    G.girth + 1 ≤ largestInducedTreeSize G * secondSmallestDegree G := by
  ...
exact_mod_cast hnat
```

The load-bearing geometric certificate remains the one in the approach
registry: a maximum induced tree containing two specified leaves has an outside
vertex with two neighbours in the tree.  The unique tree path between those
neighbours, together with the outside vertex, gives a cycle.  The two leaves
are absent from that cycle, yielding two extra vertices in the tree.

For the `2 ≤ secondSmallestDegree G` branch, it is cheaper in Lean to reuse the
same maximum-tree obstruction and prove

```lean
G.girth ≤ largestInducedTreeSize G + 1
```

than to formalize from scratch that a shortest cycle is chordless.  This is the
same numerical bridge `largestInducedTreeSize G ≥ G.girth - 1` used in
`PROOF.md`, but it shares all difficult infrastructure with the two-leaf lemma.
The literal shortest-cycle formulation is recorded below as an optional lemma.

## Existing API audit

The target currently has only the conjecture and two sanity checks.  The two
custom invariants have definitions but no usable theorem API.

```lean
noncomputable def largestInducedTreeSize (G : SimpleGraph α) : ℕ :=
  sSup {n | ∃ s : Finset α,
    s.card = n ∧ (G.induce (s : Set α)).IsTree}

noncomputable def secondSmallestDegree
    (G : SimpleGraph α) [DecidableRel G.Adj] : ℕ :=
  (degreeSequence G).getD 1 0
```

The following existing Mathlib declarations are directly useful (names and
argument shapes were checked in the vendored Mathlib source):

```lean
SimpleGraph.IsTree.isConnected
SimpleGraph.IsTree.IsAcyclic
SimpleGraph.IsTree.existsUnique_path
SimpleGraph.Connected.exists_path_of_dist
SimpleGraph.Walk.isPath_of_length_eq_dist
SimpleGraph.Walk.connected_induce_support
SimpleGraph.Walk.exists_boundary_dart
SimpleGraph.Walk.IsTrail.not_mem_support_of_subsingleton_neighborSet
SimpleGraph.Path.mapEmbedding
SimpleGraph.Path.cons_isCycle
SimpleGraph.Embedding.induce
SimpleGraph.induceUnivIso
SimpleGraph.girth_le_length
SimpleGraph.three_le_girth
SimpleGraph.girth_eq_zero
SimpleGraph.exists_girth_eq_length
SimpleGraph.degree_eq_one_iff_existsUnique_adj
SimpleGraph.Preconnected.degree_pos_of_nontrivial
```

In particular, the exact cycle-closing API is

```lean
theorem Path.cons_isCycle {u v : V} (p : G.Path v u) (h : G.Adj u v)
    (he : s(u, v) ∉ (p : G.Walk v u).edges) :
    (Walk.cons h ↑p).IsCycle
```

and the girth API needed after constructing a cycle is simply

```lean
lemma girth_le_length {a} {w : G.Walk a a}
    (h : w.IsCycle) : G.girth ≤ w.length
```

There is no current lemma extracting the two least-degree vertices from
`degreeSequence`, no witness theorem for `largestInducedTreeSize`, and no
one-vertex extension lemma for induced trees.

## Proposed reusable invariant API

These declarations belong in
`FormalConjecturesForMathlib/Combinatorics/SimpleGraph/LargestInducedTree.lean`.
They must be fully proved there; `sorry` is forbidden in that directory.

```lean
namespace SimpleGraph

open Classical

variable {α : Type*} [Fintype α] [DecidableEq α]
variable {G : SimpleGraph α}

/-- Every induced tree is bounded by `largestInducedTreeSize`. -/
lemma card_le_largestInducedTreeSize {s : Finset α}
    (hs : (G.induce (s : Set α)).IsTree) :
    s.card ≤ largestInducedTreeSize G := by
  ...

/-- On a nonempty finite vertex type, the supremum is attained. -/
lemma exists_largestInducedTree [Nonempty α] (G : SimpleGraph α) :
    ∃ s : Finset α,
      (G.induce (s : Set α)).IsTree ∧
      s.card = largestInducedTreeSize G := by
  ...

/-- The whole vertex set witnesses the invariant when `G` is a tree. -/
lemma IsTree.card_le_largestInducedTreeSize (hG : G.IsTree) :
    Fintype.card α ≤ largestInducedTreeSize G := by
  ...

/-- Attach one new vertex along its unique neighbour in the old induced tree. -/
lemma IsTree.induce_insert_of_unique_adj
    {s : Finset α} {z a : α}
    (hT : (G.induce (s : Set α)).IsTree)
    (hz : z ∉ s) (ha : a ∈ s) (hza : G.Adj z a)
    (huniq : ∀ ⦃b : α⦄, b ∈ s → G.Adj z b → b = a) :
    (G.induce ((insert z s : Finset α) : Set α)).IsTree := by
  ...

end SimpleGraph
```

Implementation notes:

* `card_le_largestInducedTreeSize` is an `sSup` membership/boundedness proof;
  every witness card is at most `Fintype.card α`.
* `exists_largestInducedTree` first uses an induced singleton as a nonempty
  witness, then finite bounded `sSup` attainment.
* `IsTree.card_le_largestInducedTreeSize` uses `s = Finset.univ` and
  `(induceUnivIso G).isTree_iff`.
* `IsTree.induce_insert_of_unique_adj` is the first build target.  Prove
  connectedness by joining the old connected induced graph to `z` through
  `a`; prove acyclicity by showing a cycle through `z` would give two distinct
  neighbours of `z`, while a cycle avoiding `z` maps into the old tree.

The degree-order extraction belongs in
`FormalConjecturesForMathlib/Combinatorics/SimpleGraph/Degrees.lean`:

```lean
namespace SimpleGraph

open Classical

variable {α : Type*} [Fintype α] [DecidableEq α] [Nontrivial α]

/-- Two distinct vertices occur at or below the second entry of the degree sequence. -/
lemma exists_distinct_degree_le_secondSmallestDegree
    (G : SimpleGraph α) [DecidableRel G.Adj] :
    ∃ x y : α, x ≠ y ∧
      G.degree x ≤ secondSmallestDegree G ∧
      G.degree y ≤ secondSmallestDegree G := by
  ...

/-- In a connected graph, second-smallest degree one supplies two leaves. -/
lemma Connected.exists_two_degree_one_of_secondSmallestDegree_eq_one
    {G : SimpleGraph α} [DecidableRel G.Adj]
    (hG : G.Connected) (hσ : secondSmallestDegree G = 1) :
    ∃ x y : α, x ≠ y ∧ G.degree x = 1 ∧ G.degree y = 1 := by
  ...

end SimpleGraph
```

For the first lemma, expose only as much sorted-list API as the proof actually
needs: `degreeSequence` has length `Fintype.card α`, is sorted by `≤`, and its
entries come from `Finset.univ.val.map (fun v => G.degree v)`.  The second lemma
uses `hG.preconnected.degree_pos_of_nontrivial` to turn both `≤ 1` conclusions
into equality.

## Small geometric lemmas

The statements below may initially be private helpers in
`GraphConjecture143.lean`.  If kept in the problem file, every non-private
declaration needs `@[category API, AMS 5]`.  Once stable, the genuinely general
ones can move to `FormalConjecturesForMathlib`.

### 1. A geodesic induces a tree

```lean
lemma Walk.induce_support_isTree_of_length_eq_dist
    {u v : α} (p : G.Walk u v)
    (hp : p.length = G.dist u v) :
    (G.induce (p.support.toFinset : Set α)).IsTree := by
  ...
```

`p.isPath_of_length_eq_dist hp` supplies the path property and
`p.connected_induce_support` supplies connectedness.  For acyclicity, any
induced chord between two nonconsecutive support vertices shortens the
corresponding subwalk; use `length_eq_dist_of_subwalk` on subpaths.  This lemma
is exactly the formal version of “a shortest `x`–`y` path is induced”.

The pair-containing seed is then a very small wrapper:

```lean
lemma Connected.exists_induced_tree_containing_pair
    (hG : G.Connected) (x y : α) :
    ∃ s : Finset α,
      x ∈ s ∧ y ∈ s ∧ (G.induce (s : Set α)).IsTree := by
  ...
```

Use `hG.exists_path_of_dist x y`, take `s = p.support.toFinset`, and apply the
preceding lemma.

### 2. Finite maximum with prescribed vertices

```lean
lemma exists_max_card_induced_tree_superset
    (G : SimpleGraph α) (r : Finset α)
    (hr : ∃ s : Finset α,
      r ⊆ s ∧ (G.induce (s : Set α)).IsTree) :
    ∃ s : Finset α,
      r ⊆ s ∧
      (G.induce (s : Set α)).IsTree ∧
      ∀ t : Finset α, r ⊆ t →
        (G.induce (t : Set α)).IsTree → t.card ≤ s.card := by
  ...
```

Select a maximum from `Finset.univ.powerset`; no choice over an infinite family
is needed.  For the two-leaf branch use `r = {x, y}` and the geodesic seed.

### 3. Boundary and maximality obstruction

```lean
lemma Connected.exists_adj_finset_compl
    (hG : G.Connected) {s : Finset α}
    (hs : s.Nonempty) (hsu : s ≠ Finset.univ) :
    ∃ a ∈ s, ∃ z ∉ s, G.Adj a z := by
  ...
```

Choose an inside and outside vertex, choose a connecting walk, and apply
`Walk.exists_boundary_dart` to the set `(s : Set α)`.

```lean
lemma exists_two_adj_of_max_card_induced_tree_superset
    {r s : Finset α}
    (hG : G.Connected)
    (hrs : r ⊆ s)
    (hT : (G.induce (s : Set α)).IsTree)
    (hmax : ∀ t : Finset α, r ⊆ t →
      (G.induce (t : Set α)).IsTree → t.card ≤ s.card)
    (hsu : s ≠ Finset.univ) :
    ∃ z ∉ s, ∃ a ∈ s, ∃ b ∈ s,
      a ≠ b ∧ G.Adj z a ∧ G.Adj z b := by
  ...
```

The boundary lemma gives one neighbour `a`.  Negating the conclusion makes
`a` the unique neighbour of `z` in `s`; then
`hT.induce_insert_of_unique_adj` produces a larger admissible tree, contradicting
`hmax` and `Finset.card_insert_of_notMem`.

### 4. The finite cycle certificate

Two list/cardinality facts keep the cycle count separate from the graph proof:

```lean
lemma Walk.IsCycle.card_support_toFinset
    {v : α} {c : G.Walk v v} (hc : c.IsCycle) :
    c.support.toFinset.card = c.length := by
  ...

lemma Walk.IsCycle.not_mem_support_of_subsingleton_neighborSet
    {v x : α} {c : G.Walk v v} (hc : c.IsCycle)
    (hx : (G.neighborSet x).Subsingleton) :
    x ∉ c.support := by
  ...
```

For the first, the only repeated support entry of a simple cycle is its base
vertex; use `hc.support_nodup`, `hc.count_support`, and `Walk.length_support`.
For the second, rotate the cycle to `x`; `snd` and `penultimate` are distinct
neighbours of `x`, contradicting subsingletonness.

The unique path in the induced tree can now be closed explicitly:

```lean
lemma IsTree.exists_isCycle_support_subset_insert_of_two_adj
    {s : Finset α}
    (hT : (G.induce (s : Set α)).IsTree)
    {z a b : α}
    (hz : z ∉ s) (ha : a ∈ s) (hb : b ∈ s)
    (hab : a ≠ b) (hza : G.Adj z a) (hzb : G.Adj z b) :
    ∃ v (c : G.Walk v v),
      c.IsCycle ∧
      z ∈ c.support ∧
      c.support.toFinset ⊆ insert z s := by
  ...
```

Obtain the unique `a`–`b` path from `hT.existsUnique_path`, map it into `G`
with `Path.mapEmbedding (SimpleGraph.Embedding.induce (s : Set α))`, prepend
the edge `z-a`, and close with `b-z` using `Path.cons_isCycle`.  The hypotheses
`hz` and `hab` discharge the path and fresh-edge side conditions.  Extra edges
from `z` to the path do not matter.

The two numerical corollaries are the exact geometric interfaces used later:

```lean
lemma IsTree.girth_le_card_add_one_of_two_adj
    {s : Finset α}
    (hT : (G.induce (s : Set α)).IsTree)
    {z a b : α}
    (hz : z ∉ s) (ha : a ∈ s) (hb : b ∈ s)
    (hab : a ≠ b) (hza : G.Adj z a) (hzb : G.Adj z b) :
    G.girth ≤ s.card + 1 := by
  ...

lemma IsTree.girth_add_one_le_card_of_two_leaves_of_two_adj
    [DecidableRel G.Adj]
    {s : Finset α}
    (hT : (G.induce (s : Set α)).IsTree)
    {x y z a b : α}
    (hxs : x ∈ s) (hys : y ∈ s) (hxy : x ≠ y)
    (hx : G.degree x = 1) (hy : G.degree y = 1)
    (hz : z ∉ s) (ha : a ∈ s) (hb : b ∈ s)
    (hab : a ≠ b) (hza : G.Adj z a) (hzb : G.Adj z b) :
    G.girth + 1 ≤ s.card := by
  ...
```

For the first corollary, cycle support has `c.length` vertices and lies in the
`s.card + 1` vertices of `insert z s`; finish with `G.girth_le_length`.
For the second, `degree_eq_one_iff_existsUnique_adj` makes both leaf neighbour
sets subsingletons.  Therefore the cycle support omits `x` and `y`, while it
contains `z`; finite-set counting gives `c.length + 1 ≤ s.card`, hence the
claimed girth inequality.

## Two direct numerical lemmas

These isolate all graph geometry from the final degree arithmetic.

```lean
lemma girth_le_largestInducedTreeSize_add_one
    (G : SimpleGraph α) (hG : G.Connected)
    (hcyc : ¬ G.IsAcyclic) :
    G.girth ≤ largestInducedTreeSize G + 1 := by
  ...
```

Choose `s` with `exists_largestInducedTree`.  It is proper, since a spanning
induced tree would make `G` a tree via `induceUnivIso`, contradicting `hcyc`.
Apply `exists_two_adj_of_max_card_induced_tree_superset` with `r = ∅`, then
`hT.girth_le_card_add_one_of_two_adj`, and rewrite `s.card` using the witness
equality.

```lean
lemma girth_add_one_le_largestInducedTreeSize_of_two_leaves
    (G : SimpleGraph α) [DecidableRel G.Adj]
    (hG : G.Connected) (hcyc : ¬ G.IsAcyclic)
    {x y : α} (hxy : x ≠ y)
    (hx : G.degree x = 1) (hy : G.degree y = 1) :
    G.girth + 1 ≤ largestInducedTreeSize G := by
  ...
```

Use `Connected.exists_induced_tree_containing_pair`, choose a maximum among
trees containing `{x, y}`, show it is proper using `hcyc`, obtain `z,a,b` from
the maximality obstruction, apply the two-leaf cardinal lemma, and finish with
`card_le_largestInducedTreeSize`.

For a literal formalization of the shortest-cycle sentence in `PROOF.md`, the
desired standalone interface is:

```lean
lemma exists_induced_tree_card_add_one_eq_girth
    (G : SimpleGraph α) (hcyc : ¬ G.IsAcyclic) :
    ∃ s : Finset α,
      (G.induce (s : Set α)).IsTree ∧ s.card + 1 = G.girth := by
  ...
```

It follows from `exists_girth_eq_length` plus a new proof that a minimum-length
cycle has no chord, followed by deleting one cycle vertex.  Do not make this
the first target: the maximum-tree lemma above proves the only needed numerical
consequence and avoids a second, independent chord formalization.

## Main theorem skeleton

After the preceding interfaces compile, `conjecture143` should reduce to this
case split and elementary natural-number arithmetic:

```lean
theorem conjecture143 (G : SimpleGraph α) [DecidableRel G.Adj]
    (hG : G.Connected) (hσ : 0 < secondSmallestDegree G) :
    (G.girth : ℝ) + 1 ≤
      (largestInducedTreeSize G : ℝ) *
        (secondSmallestDegree G : ℝ) := by
  have hnat :
      G.girth + 1 ≤
        largestInducedTreeSize G * secondSmallestDegree G := by
    by_cases hcyc : ¬ G.IsAcyclic
    · have hg3 : 3 ≤ G.girth := G.three_le_girth hcyc
      by_cases hσ1 : secondSmallestDegree G = 1
      · obtain ⟨x, y, hxy, hx, hy⟩ :=
          hG.exists_two_degree_one_of_secondSmallestDegree_eq_one hσ1
        have ht := girth_add_one_le_largestInducedTreeSize_of_two_leaves
          G hG hcyc hxy hx hy
        simpa [hσ1] using ht
      · have hσ2 : 2 ≤ secondSmallestDegree G := by omega
        have ht : G.girth ≤ largestInducedTreeSize G + 1 :=
          girth_le_largestInducedTreeSize_add_one G hG hcyc
        have htwo :
            G.girth + 1 ≤ 2 * largestInducedTreeSize G := by
          omega
        exact htwo.trans (by
          simpa [Nat.mul_comm] using
            Nat.mul_le_mul_left (largestInducedTreeSize G) hσ2)
    · have hacyc : G.IsAcyclic := not_not.mp hcyc
      have hg0 : G.girth = 0 := hacyc.girth_eq_zero
      have htree : G.IsTree := ⟨hG, hacyc⟩
      have ht : 1 ≤ largestInducedTreeSize G :=
        (Fintype.card_pos).trans htree.card_le_largestInducedTreeSize
      calc
        G.girth + 1 = 1 := by simp [hg0]
        _ ≤ largestInducedTreeSize G := ht
        _ = largestInducedTreeSize G * 1 := by simp
        _ ≤ largestInducedTreeSize G * secondSmallestDegree G :=
          Nat.mul_le_mul_left _ hσ
  exact_mod_cast hnat
```

The polarity `by_cases hcyc : ¬ G.IsAcyclic` is intentional: in the false
branch, `not_not.mp hcyc` gives acyclicity immediately.  If elaboration of
`Fintype.card_pos` needs an explicit instance, obtain `Nonempty α` from the
existing `[Nontrivial α]` instance.

## Dependency order and first build target

Recommended build order (each line should compile before starting the next):

1. `IsTree.induce_insert_of_unique_adj`.
2. `card_le_largestInducedTreeSize` and `exists_largestInducedTree`.
3. `Connected.exists_adj_finset_compl` and
   `exists_two_adj_of_max_card_induced_tree_superset`.
4. Cycle support/card lemmas and
   `IsTree.exists_isCycle_support_subset_insert_of_two_adj`.
5. The two girth/card corollaries.
6. Geodesic-induced-tree and prescribed-pair maximum lemmas.
7. Degree-sequence extraction lemmas.
8. The two direct numerical lemmas, then `conjecture143`.

The highest-leverage first build target is exactly:

```lean
lemma IsTree.induce_insert_of_unique_adj
    {α : Type*} [Fintype α] [DecidableEq α]
    {G : SimpleGraph α} {s : Finset α} {z a : α}
    (hT : (G.induce (s : Set α)).IsTree)
    (hz : z ∉ s) (ha : a ∈ s) (hza : G.Adj z a)
    (huniq : ∀ ⦃b : α⦄, b ∈ s → G.Adj z b → b = a) :
    (G.induce ((insert z s : Finset α) : Set α)).IsTree := by
  ...
```

It is falsifiable in isolation, has no dependence on either custom numerical
invariant, and is the sole logical bridge from maximality to “the boundary
vertex has at least two tree neighbours” in both cyclic branches.
