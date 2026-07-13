# Failed LEAD-T adapter audit

## Verdict

A supplied `CommonBlueExtendedMatching.Matching` does **not** construct
`ResidualSourceTokenization.Data`. It does construct the following exact
partial adapter:

```text
(Debit ⊕ Slot) ↪ Source
        gives
((Debit × Fin 2) ⊕ (Slot × Fin 2)) ↪ (Source × Fin 2).
```

Here `Debit = ActiveCollisionHalf`, `Slot = ActiveHitNeed`, and
`Source = FreeHalf`. Thus the collision side is fully paid (two microcopies),
but each hit slot receives only 2 of the required 25 microcopies. The missing
scale is exactly 23 microcopies per hit slot, disjoint from every debit image
and from the two already used hit images.

Production now exposes `MicroMatching` with domain
`ActiveCollisionHalf ⊕ (ActiveHitNeed × Fin 25)`. That stronger object can
supply a raw residual embedding (use both target half copies for each matched
collision source, and one target half copy for each of the 25 separately
matched hit sources). The originally supplied `Matching` cannot be promoted
to it.

## Exact cardinal boundary

The supplied matching proves only

```text
card Debit + card Slot <= card Source.
```

`ResidualSourceTokenization.Data` implies, and its raw embedding is constructible
from, exactly

```text
2 * card Debit + 25 * card Slot <= 2 * card Source.
```

At tight matching scale `card Source = card Debit + card Slot`, this inequality
holds iff `card Slot = 0`. Hence any positive hit population defeats the
one-copy-to-residual implication.

The smallest **global cardinal** addition is precisely the residual inequality
above. The smallest hypothesis sufficient for the full `Data` constructor is
stronger and componentwise: a component-preserving embedding

```text
((Debit × Fin 2) ⊕ (Slot × Fin 25)) ↪ (Source × Fin 2)
```

whose source component equals the debit component on the left summand and the
slot owner's vertex component on the right summand, plus `unit > 0`. Equivalently,
one may assume the residual inequality separately in every component and use
finite embeddings within each component. A global inequality alone cannot
prove `Data.source_component`.

Relative to the supplied matching, the minimal explicit capacity provider is
a disjoint component-preserving provider for the remaining
`Slot × Fin 23` copies. It must avoid the images of all `Debit × Fin 2` and the
first `Slot × Fin 2`; this is the no-double-counting formulation.

## R29 gate

The reconciled 28-key common-blue absorber is assigned exclusively to 28
owner-2 collision obligations. Those matches cancel debits and create no
FullBank token spend. Exact arithmetic confirms that reusing those same keys
for even one slot would require

```text
2*28 + 25*1 <= 2*28,
```

which is false (`81 <= 56`). The 216 new eligible keys and 28-key minimum flow
repair therefore certify only collision cancellation, not residual hit-token
capacity. This agrees with the reconciliation statement that HitNeed scaling
is not invoked by the repair.

## Tiny exact gate

The smallest mixed model has one debit, one slot, and two sources. A perfect
one-copy matching `(Fin 1 ⊕ Fin 1) ↪ Fin 2` exists. The residual domain has
`2 + 25 = 27` elements while the target has `2*2 = 4`, so no residual embedding
exists. This is proved kernel-side in `tiny_matching_but_no_residual_embedding`.

## Assignment and FullBank boundary

Once `ResidualSourceTokenization.Data` is supplied, its production
`Data.assignment` constructs a sorry-free `CollisionTokenAssignment.Assignment`.
No further obstruction occurs at that arrow.

The next arrow cannot be built from the matching or assignment APIs:

* `TypedFullBankSources` gives typed Door-source checking, but no conversion
  from `FreeHalf`, corrected common-blue terminals, or residual slots to
  `CapSource` tokens.
* `FullBankPortSinks` partitions an already supplied ledger and rescales its
  capacities, but explicitly has no legal edge-to-token incidence.
* `Matching.available` proves owner eligibility/unreservedness; it says
  nothing about ledger token identity, `CapKind`, component-local token
  ownership, `capQ`, or sink legality.

The smallest additional FullBank hypothesis is therefore a typed incidence
provider: for every residual slot, a ledger token of the correct component and
non-door source kind, with capacity at least the slot's 25 micro-units, global
no-double-spend, and legality for every incident demanded edge. Door ports
separately require `OwnEdgeDoorSourceData.Checked` (own-edge source equality,
capacity at least 25, and injectivity). These facts are independent of the
common-blue terminal checker.

## Checked artifacts

`AdapterAudit.lean` compiles with rc=0. Its six `#print axioms` results are all
subsets of `{propext, Classical.choice, Quot.sound}`; in particular there is no
`sorryAx`. The file proves the two-scale lift, tight-budget characterization,
tiny countermodel, R29 non-reuse arithmetic, and sufficiency of the raw
cardinal budget.
