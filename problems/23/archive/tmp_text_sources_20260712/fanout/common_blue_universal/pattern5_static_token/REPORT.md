# Pattern-5 static ownership theorem

## Verdict

The R30 switch interpretation is dead: `sigma >= 0` does not preserve the
selected rows, and the exact 2943 switch invalidates 1,014 rows.  Pattern 5 can
only be used statically.

The weakest assignment-level condition needed by the compiled
`ResidualSourceTokenization.Data` interface is:

```text
BaseKeyComponentCoherent(mu, comp) :=
  for all obligations d,e,
  base(mu(d)) = base(mu(e)) implies comp(d) = comp(e).
```

This condition is necessary and sufficient for a function
`sourceComp : Source -> Comp` satisfying component preservation.  It is not
implied by injectivity on full `(base,half)` keys: the two half bits of one base
key are distinct matching sources.

For a graph-defined Pattern-5 relation, the weakest simple relation-level
theorem sufficient for every chosen matching is:

```text
RelationBaseComponentUnique:
  if one ordered-pair base key is Pattern-5 eligible for owners u and v,
  then u and v lie in the same active destination component.
```

This relation-level theorem is false.  The exact doubled-cage falsifier below
shows that coherence must be imposed on the selected global matching itself;
it cannot be derived from local Pattern-5 eligibility.

No cut flip, row rewrite, or switch-loss capacity is used.  Given this property
and a global injective micro-matching, `StaticOwnership.lean` constructs the
compiled `ResidualSourceTokenization.Data` object at the exact 25-microcopy
scale.  Distinct-source and endpoint-token theorems then come from the existing
tokenization module.

## Exact limitation

This does not construct `FullBankGlobalPackage.Checked`.  Production currently
has no graph-derived constructor or legal port-incidence predicate for an
individual `CapKind.c5Base` ledger token.  A checked FullBank package still
requires the component reserve identity, spend matrix, no cross-component
spend, and legal edge-to-token incidence.  Therefore a theorem claiming

```text
local Pattern-5 witness -> valid checked FullBank token
```

is not expressible from the current production token structure without adding
those global premises.  The exact static endpoint reached here is the residual
tokenization object, not the FullBank package.

## Countermodel to injection alone

`splitHalfAssignment` injects two obligations into `(sameBase,half0)` and
`(sameBase,half1)` while assigning them to two different components.  Lean
proves that no `Source -> Comp` function can satisfy component preservation.
Thus global half-key injectivity alone is insufficient.

## Graph-realizable component counterexample

`doubled_cage_falsifier.py` takes two exact 2943 R29 cages and joins their
quiescent leaf-3 vertices by one blue bridge.  It certifies:

- `n=5886`, `|E|=16845`, triangle-free and blue-connected;
- exact `MaxCut=7039+7039+1=14079`, with an attaining cut;
- all `2766` bad edges have blue distance exactly `4`;
- `Gamma=2766*25=69150`, hence Gamma-minimal by the triangle-free distance
  lower bound;
- the merged quiescent component has size `2758`, boundary
  `{1,55,2944,2998}`, and switch loss `52`;
- the free, unreserved base key `(3,56)` is eligible for owners
  `{0,1,2}` in active root `0` and `{2943,2944,2945}` in root `2943`.

Assigning half 0 to owner `0` and half 1 to owner `2943` is injective on full
half keys but violates base-key component coherence.  This is an exact
graph-realizable falsifier to `RelationBaseComponentUnique` and to every local
ownership rule that permits both independently valid Pattern-5 arcs without a
global same-base component constraint.

## Finite gates

- R29 all-anchor repair: 14 base keys, 28 half keys, all free and unreserved;
  owners `0,1,2` all have active root `0`.  Base-key component coherence holds.
- First N12 P1-P5 failure `K??E@cyjFgWk`, choice `[0,4,5,7]`: 16 eligible
  ordered Pattern-5 base keys, one destination component, coherence holds.
  Matching still fails exactly at demand `78`, flow `69`, defect `9`.

These are finite evidence only.  The exact N12 all-row census remains 89,640
P1-P5 micro failures; no universal matching claim survives.

## Reproduction

```powershell
python tmp/fanout/common_blue_universal/pattern5_static_token/fixture_coherence_gate.py
python tmp/fanout/common_blue_universal/pattern5_static_token/doubled_cage_falsifier.py
```

The Lean build uses the private olean overlay in this directory and reports
only the allowed axioms `propext`, `Classical.choice`, and `Quot.sound`.  There
is no `sorry`, `admit`, `native_decide`, or floating-point theorem evidence.
