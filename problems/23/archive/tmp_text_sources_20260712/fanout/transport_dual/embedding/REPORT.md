# Component-aware embedding report

## Exact graph statement

Let `R` be the union of the old and replacement row vertex sets. Let `H` be
the old active graph and `Hq` the active graph after alternative `q`. Assume

`H.Adj x y XOR Hq.Adj x y -> x in R and y in R`.

For every `Hq` connected component `K` disjoint from `R`, containment gives a
unique old component `F(K)`. Then `F` is injective on the `Hq` components
disjoint from `R`.

This is stronger than the existing pointwise theorem
`newComponent_reachable_old_of_not_touchesChangedRows`: distinct persistent
new components cannot merely land in the same old component.

## Proof attempt

Take persistent components `K,L` and owners `u in K`, `v in L`, with `u,v`
old-reachable. Traverse an old walk from `u` to `v`. Inductively, suppose its
current vertex `x` is new-reachable from `u`. Persistence says `x notin R`.
For the next old edge `x--y`, row locality implies that an edge absent in the
new graph would have both endpoints in `R`, impossible because `x notin R`.
Thus `x--y` is also new, so `y` is new-reachable. The whole walk copies to the
new graph; hence `u,v` are new-reachable and `K=L`.

Lean proof gap: the production file proves equality only for edges whose four
row nonmembership hypotheses are supplied. A short bridge lemma is still
needed: symmetric-difference locality for active edges, namely that a changed
active edge has both endpoints in the old/new row union. With it, the walk
induction above is direct. No production file was edited and no `sorry`,
`native_decide`, or floating-point acceptance was used.

## Exact capacitated statement behind the structure

Fix one alternative `q`. Let `Dq` be its new demands, let `O` be the number of
old demands whose owners lie outside `A`, and for `X subseteq Dq` let `N(X)` be
the old shore sources eligible for at least one member of `X` under
`ComponentTransportSourceEligible`. A legal injection for this `q` exists iff

`|X| <= O + |N(X)|` for every `X subseteq Dq`.

Because both sides of `CoordinateTransportTarget` carry the alternative tag,
the alternatives are disjoint: `ComponentAwareCoordinateReplacementInjection`
exists iff this inequality holds separately for every `q`.

The persistent-component injection makes the inherited old component unique,
but does not bound the number of demand copies owned by that component. The
missing real graph lemma is therefore the displayed capacitated Hall inequality
(or a stronger per-component inequality implying it), not component
containment itself.

## Exact tests and falsifiers

`exact_embedding_gate.py` enumerated every ordered pair of simple graphs on
`n <= 5`, defining `R` exactly as the endpoints of changed edges. It checked
1,052,741 pairs and 22,555 persistent new components. There were 0 failures of
injectivity of the component map.

It also enumerated 369,339 eligibility systems with at most 4 demands and 4
shore sources, all common outside capacities `0..d`, and 5,465,593 Hall subset
checks. Brute-force matching and `|X| <= O+|N(X)|` disagreed 0 times.

No graph falsifier was found in the tested range. The smallest abstract
counterexample to deriving transport from component injection alone has one
persistent component carrying two new demands, no outside target, and one
eligible shore source: component mapping is injective but demand capacity is
`2 > 1`.

## Proof gap

Prove active-edge symmetric-difference locality in Lean, then formalize the
persistent-component injection. After that, the unresolved graph content is
to show `|X| <= O+|N(X)|` for every demand subset and every alternative from
triangle-freeness, max-cut, B-connectivity, complete shortest rows, and the
deficient owner shore. Persistence alone cannot supply the demand multiplicity
capacity.

## SHA256

Hashes are listed in `SHA256SUMS.txt`.
