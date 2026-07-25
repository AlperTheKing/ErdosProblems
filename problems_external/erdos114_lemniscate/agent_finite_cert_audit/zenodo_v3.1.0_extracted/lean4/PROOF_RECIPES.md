# Proof Recipes

## 2026-04-20 - Erdos30_BFR support lemmas

Compiled source: `erdos-experiments/Erdos30/lean/Erdos30_BFR.lean`

### Recipe: range bound via injective image plus `Finset.card_le_card`

Use this when a Sidon map is already known to be injective and the remaining job is only to count how many target values are possible.

Pattern:

1. Build the image finset explicitly.
2. Prove it sits inside `Finset.range bound`.
3. Finish with `Finset.card_le_card` on the subset proof.

In the current BFR batch this appears as `distinctSums_subset_range` and `erdos_turan_counting_bound`. The useful split is to keep the subset lemma separate from the final cardinality inequality so the same subset proof can feed more than one counting argument.

### Recipe: shifted-family intersection at most one

For additive-combinatorics arguments, define a translated copy
`shifted A t := A.image (fun a => a + t)` and count collisions between two translates through a Sidon difference lemma.

Pattern:

1. Prove `card_shifted` by `Finset.card_image_of_injective`.
2. Prove each shift stays inside a concrete range (`shifted_subset_range`).
3. For `card (shifted A t ∩ shifted A s) <= 1`, convert membership in the intersection into
   `a1 + t = a2 + s`, rearrange to `a1 - a2 = s - t`, and invoke the imported Sidon distinct-differences lemma.

In the current BFR batch this appears as `shifted`, `card_shifted`, `shifted_subset_range`, and `shifted_inter_card_le_one`.

### Mathlib / repo pitfall

Do not import `Erdos30_Complete` just to reach a Sidon difference lemma. In this repo that import drags a stale dependency chain. Import `Erdos30_Lindstrom` directly and reuse `sidon_distinct_differences`.

## 2026-04-20 - Dense finite rigidity scratch targets

Compiled source: `erdos-experiments/Erdos30/scratch/Erdos30_IntervalOccupancyTarget.lean`

### Recipe: convert an initial-segment counting statement into a sorted-prefix identity

Use this when the mathematical claim is "the elements of `A` below the `i`-th order statistic are exactly the first `i+1` sorted elements," and Lean needs that turned into a cardinality theorem on a filtered finset.

Pattern:

1. Set `l := A.sort (· ≤ ·)` and `a := orderedElement A i`.
2. Express the initial segment as a boolean filter on the list: `p x := decide (x ≤ a)`.
3. Prove `(l.filter p).toFinset = intervalSlice A 0 a` by extensional `simp`.
4. Compute the filter length by splitting `l` as `take (i+1) ++ drop (i+1)`.
5. Show the prefix contributes all its length using sortedness and `rel_get_of_le`.
6. Show the suffix contributes zero using strict sortedness plus `rel_of_mem_take_of_mem_drop`.
7. Convert `toFinset.card` back to list length via nodup.

In the current scratch target this is the proof of `ordered_prefix_card_target`. The reusable lesson is that `List.countP`, `take_append_drop`, and `sort_toFinset` are the clean bridge between order-statistic statements and finset cardinality statements.

### Recipe: isolate an honest algebraic obstruction with a correction-term split

Use this when a heuristic target is "almost" obtained from a proved counting theorem, but one residual term still needs separate control.

Pattern:

1. Package the proved error term as `q`.
2. Package the residual correction term as `r`.
3. Rewrite the target expression as `-q + r`.
4. Apply `Int.natAbs_add_le`.
5. Keep the correction term explicit instead of hiding it in an over-optimistic target.
6. Add a promotion lemma saying that any standalone bound on `r` upgrades the corrected statement to the desired final shape.

In the current scratch target this appears as `dense_sidon_ordered_element_with_correction` and `dense_sidon_ordered_element_of_correction_bound`. This is the right pattern whenever the proof architecture is sound but one geometric estimate is still missing.

### Recipe: transport an external ordered-element theorem to a prefix-count statement at cutpoints

Use this when the literature gives an asymptotic theorem for the `i`-th ordered element, while the local formalization wants a statement about prefix counts evaluated at `t = a_i`.

Pattern:

1. Keep the external theorem as an explicit axiom/interface with citation and honest scale.
2. Prove the exact local identity `|(A ∩ [0, a_i])| = i+1`.
3. Rewrite the literature theorem by replacing `i+1` with that exact prefix count.
4. Treat the result as a cutpoint consequence, not as a uniform discrepancy theorem on all prefixes.

In the current scratch target this appears as `dense_sidon_ordered_element_external` together with `ordered_prefix_card_target`, yielding `dense_sidon_prefix_cutpoint_external`. The lesson is that exact local combinatorics can still extract useful structure from an imported asymptotic theorem even when the stronger local discrepancy theorem is out of reach.
