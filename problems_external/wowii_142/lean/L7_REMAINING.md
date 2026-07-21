# W142 Lean status — 2026-07-18

## Compiled interacting branch

`SplicePath.lean` compiles against the pinned `formal-conjectures-w143` toolchain with

`lake env lean -DwarningAsError=true ..\problems_external\wowii_142\lean\SplicePath.lean`

and exit code 0. It contains no `sorry`, `admit`, or `native_decide`.

The interacting part L7(b) is now formalized end to end for two fixed positive nearest-cycle descents. The principal theorem is:

`Walk.interacting_descents_splice_L7b_largestInducedTreeSize`

Under a girth-realizing cycle of girth at least five and an interaction witness, it proves

`G.girth + G.dist u v ≤ largestInducedTreeSize G`.

The compiled chain includes:

- `Walk.exists_first_interaction_index`: selects the extremal interaction index;
- `Walk.interacting_descents_splice_caseA` and `Walk.interacting_descents_splice_caseB`: close the endpoint and strict-prefix cases, including the depth-one erased-root branch;
- `Walk.interacting_descents_splice_L7b_outside_cycle`: produces `F`, proves `F ∩ K = ∅`, induced-tree structure, exactly one ordered attachment to `K \ {z}`, and `|F| ≥ dist(u,v)+1`;
- `Walk.IsCycle.erase_vertex_path_certificate_splice`: proves `K \ {z}` is an induced path on `girth-1` vertices;
- `IsTree.induce_union_of_disjoint_of_unique_adj_splice`: joins two induced trees across their unique cross-edge;
- `IsTree.card_le_largestInducedTreeSize_splice`: transfers the concrete tree to the supremum invariant.

SHA-256 of `SplicePath.lean` at this checkpoint:

`DAA4D115BE77BAA9ED39B259450E193C68C832FE486DFF764507B55392409598`

## Exact remaining work for Conjecture 142

The following global steps are not yet Lean-formalized:

1. L7(a): for pairwise noninteracting nearest-cycle descents, package their outside trees as an admissible induced forest and prove the componentwise unique-attachment condition and total-cardinality bound.
2. L8: apply L7 to the three selected descents from the paper and derive the stated lower bound for the cycle certificate in both the interacting and noninteracting branches.
3. Formalize the residue and small-girth cases used by `PROOF_142_B.md`, then connect all branches to the exact real-valued statement in `GraphConjecture142.lean`.
4. Run the final theorem with warnings as errors and a source scan.

Therefore the interacting L7(b) and its concrete M(K)-style induced-tree bridge are Lean-complete, but Conjecture 142 as a whole is not yet Lean-complete.
