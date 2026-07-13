# Static Pattern-5 adapter audit

## Referee correction

Pattern 5 is usable only as a supplied static availability relation. The exact
R29 switch on `K(3)` has `sigma = 26`, but it invalidates 1,014 selected rows,
crosses 1,352 selected support-edge occurrences, and changes 676 listed bad
edges. It therefore does not preserve the row database, active components, or
maximum-cut state, and cannot justify a c5Base token by itself.

Referee report SHA-256:
`E13275A7B805ECA50482823C5642B96CA9E006EBE1681AB37E12881E1F91FC34`.

## Compiled static interface

`StaticPattern5Adapter.lean` contains no state transition. Its `Provider`
requires:

- one global injection from bank-scale `MicroDemand` into source cells and
  half bits;
- an injective map from those cells to literal `FreeHalf` keys;
- a supplied static availability proof for every assigned key;
- explicit `vertexComp`, `debitComp`, `sourceComp`, and
  `component_preserving`;
- an injective typed `c5Base` base-key map;
- an empty new-reservation set;
- a positive residual micro-unit.

The assignment domain is literally
`ActiveCollisionHalf + (ActiveHitNeed x Fin 25)`, so the compiled theorem
`hitNeed_micro_sources_injective` proves 25 distinct source images for each
HitNeed. This conclusion comes from the supplied global injection, not from
the local P5 predicate.

The only availability fact derived from static quiescence is:

```text
not ActiveOwner(sourceX) -> not ScopedReserved(sourceHalf).
```

`assigned_not_scopedReserved` applies it to every supplied assignment. No
triangle-free, max-cut, or switch-loss fact is used.

`Provider.data` constructs `ResidualSourceTokenization.Data`; its
`source_component` field is exactly the supplied component-preservation
hypothesis. `typedC5BaseSource_injective` follows only from the supplied
injective base-key map.

`FullBankSpendHypotheses` states, without deriving, token base-key uniqueness,
nonnegative spend, no double spend, and no cross-component spend. Static P5
availability supplies none of these.

## Reservation comparison

`r29_reservation_recount.py` reconstructs the all-anchor R29 state exactly.
For the posted common-blue family, 28 new halves reserve a 15-edge union and
deduct the old key `(2,2930,1)`, so the honest net is 27. No idempotence is
assumed. Pattern 5 adds 28 static halves, introduces no reservation edges,
and deducts no old key, so its fixture net is 28. This is a fixture accounting
fact, not a token theorem.

The separate full-pool conservative exclusive common-blue gate selects two
base pairs, gains four halves, deducts two old halves, and nets only two.

## Missing graph theorem

The remaining theorem must be selection-sensitive because universal all-row
common-blue MicroHall and universal all-row P5 are both false. A sound provider
theorem must construct, for the selected row tuple:

1. a global literal-half injection for every collision half and all 25 copies
   of every HitNeed;
2. static old/P5 availability and avoidance of the union of all reservation
   deductions;
3. component preservation for every assigned micro-source;
4. globally injective typed c5Base keys;
5. a FullBank spend matrix satisfying no double spend, no cross-component
   spend, and typed source uniqueness.

No inspected static P5 field implies items 1 or 3-5. The R29 switch
countermodel rules out deriving them by changing to the flipped state while
reusing the old rows.

## Build

`lake env lean StaticPattern5Adapter.lean` returned zero. The five axiom probes
use only `propext`, `Classical.choice`, and `Quot.sound`. Forbidden-token grep
is empty.
