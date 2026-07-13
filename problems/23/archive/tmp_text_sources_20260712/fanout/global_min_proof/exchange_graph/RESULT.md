# RESULT — compressed exchange graph

## Verdict

The literal target “Hall failure forces a negative multi-row cycle” is false for
the natural exchange graph whose vertices are row tuples and whose edge weight is
the exact scoped-score change.  Such weights are potential differences, hence
every closed walk has total weight exactly zero.  A negative **open path** (a
simultaneous trade), or a negative cycle of separately defined dual/reduced costs,
is the viable formulation.

## Exact definitions used

Let `X = Π_i R_i` be the finite set of row choices and let
`F : X -> Nat` be Lean `scopedObligationScore`, i.e. the cardinality of active
collision halves plus active HitNeed units.  The compressed Hamming exchange graph
has an arc `x -> y` when one row coordinate changes and exact weight
`w(x,y) = (F(y):Int) - F(x)`.  A multi-row trade is an arbitrary pair `x,y`, with
weight `F(y)-F(x)`; a coordinate path realizes it by changing the differing rows.

## Exact falsifier

On two binary row coordinates set

`F(00)=0, F(10)=2, F(01)=2, F(11)=-1`.

Then `00` is a strict Hamming-one local minimum (both outgoing changes cost `+2`),
but the simultaneous two-row trade `00 -> 11` costs `-1`.  Nevertheless every
directed cycle has weight zero by telescoping.  The attached checker enumerates all
six simple directed cycles of the Hamming square and verifies this using integers.
This is the smallest dimension in which local ascent and simultaneous descent can
coexist; one coordinate has no distinct multi-row trade.

Command and exact output:

```text
python tmp/fanout/global_min_proof/exchange_graph/check_falsifier.py
states=4 local_deltas=2,2 simultaneous_delta=-1
simple_directed_cycles_checked=6 all_cycle_sums=0
```

## Proved theorem chain and named gaps

1. For exact score-difference weights, every closed walk sums to zero (telescoping).
2. A global minimizer has no negative open path to any other tuple, by definition.
3. Therefore the desired global-minimum result would follow from the corrected
   structural statement: Hall failure at `omega` implies an `eta` with
   `scopedObligationScore eta < scopedObligationScore omega`.
4. The existing Lean files prove a stronger conditional bridge for one-coordinate
   aggregate variation: component-aware coordinate injections imply negative summed
   variation, and negative summed variation contradicts global minimality.
5. **GAP EG-1:** no uniform graph-theoretic construction of those injections (or of
   an unbounded simultaneous trade) is proved.
6. **GAP EG-2:** persistent-component monotonicity of `activeDegree` and HitNeed only
   controls components avoiding changed rows.  A simultaneous trade may merge,
   split, create, or destroy touched active components; no conservation/transport
   law for those touched components is present.
7. **GAP EG-3:** to use a negative-cycle theorem, one must define non-potential
   reduced costs from a Hall dual and prove that cycle augmentation corresponds to
   a legal simultaneous row tuple with strictly lower actual score.  Neither
   implication currently exists.

Thus the supplied 4,801,067-tuple N12 evidence supports the already formalized
aggregate-variation route, but it cannot establish a negative score-cycle theorem.
No executable 2943 constructor/data or claimed `00186166...` artifact exists in the
workspace; only the prose specification was found, so no 2943 gate is claimed.

## SHA-256

Created artifact:

- `check_falsifier.py`: `f207df2a3429d6fe3143aa98a61aa7ef40ebc441ddc95538005e3ff91e3d7364`

Relied inputs:

- `COMMON.md`: `533cd8772b6f0cd8f667e3388b7baba9a0734f862e41cb01cd6958ac2c296003`
- `GOAL_CODEX_SHORT.txt`: `e032a3a8877ad80cdd0e628ea3352208330520f5b8d79a5b55da7b7637518b09`
- `CODEX_ONBOARDING.md`: `e3012793accde4e8f8fa3ed3e514a794a7d006a07e4bdc23e4239d14c9d61ad0`
- `CLAUDE_TO_CODEX.md`: `b533191baf54a2e3d53ce05e1f46269b78e6eedba90f08cb9b80b7feab6e9126`
- `WALL_ATTACK_R29_GPTPRO56.md`: `fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04`
- `ActiveScopedMinimumExchange.lean`: `b916318f53d69b4d9adff2c4a79b23c139513640f16550daea092ce3a9e77982`
- `ActiveScopedVariationReduction.lean`: `f3ffd8b22edd2de55d53664f20b77651df4b35033ba3e1ecb5d029aa11f8a921`
- `ActiveScopedCoordinateTransport.lean`: `6b10458bedd26b4d460fdd4ad034d55cb6b1dee16a2691f22460e562941dc272`
