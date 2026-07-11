# R29 transfer reconciliation

## Scope

The 2,943-vertex R29 cage is an exact falsifier to both of the following
claims for the auxiliary active-scoped relation in
`Gamma/ActiveScopedMinimumExchange.lean`:

1. every scoped-score global minimizer has an active-scoped matching;
2. the PHT averaged descent inequality.

At the all-anchor global minimum, the hub shore `{0,1,2}` has demand `19953`
and active-scoped reach `19925`, hence defect `28`.

It is not a falsifier to the corrected common-blue transfer relation.

## R23 outside-attachment discrepancy

The executable R23 fixture gate admits an outside component for owner `v`
when its attachment boundary contains a selected-row companion of `v`.  On
R29 this loose predicate yields `912600` new half-slots and trivially closes
the defect.

The written R23 predicate additionally requires the attachment witnesses and
the owner to lie in the same selected component.  That condition is absent
from the executable gate.  With the component equalities enforced, R29 has no
eligible outside-attachment source and the defect remains `28`.

Therefore the loose outside-attachment count is not an accepted repair.

## Corrected common-blue repair

`Gamma/CheckedC5BaseTransfer.lean` already compiles the corrected R19 terminal
predicate for a source pair `(x,y)` and owner `v`:

```text
x != y,
xv and yv are blue,
dM({x,y}) + 2 <= dB({x,y}).
```

Exact enumeration on the R29 all-anchor tuple finds `2824` valid
owner-terminal half instances, of which `216` are new global FreeHalf keys.
Adding them to the old relation makes every one of the eight hub-owner shores
Hall-feasible and gives exact maximum flow `19953/19953`.

A minimum repair uses owner `2`, vertex `2930`, leaves `29..42`, and both
half bits:

```text
{(x,2930,h) : 29 <= x <= 42, h in {0,1}}.
```

For every one of these 28 keys,

```text
dB({x,2930}) = 30,
dM({x,2930}) = 27,
dB - dM - 2 = 1.
```

The keys are pairwise distinct, Free, unreserved, and absent from the old
`19925`-key certificate.  Assigning them to 28 owner-2 collision obligations
finishes the injection.  Collision matches cancel and create no FullBank
token spend; the token-capacity scaling used for HitNeed is therefore not
invoked by this repair.

The repaired shore margins for masks `0..7` are:

```text
0, 1724, 1724, 848, 1752, 876, 876, 0.
```

The repair is minimum in source-key cardinality because the old full shore
has exact defect `28`.

## Production microcopy scale

The preceding `19953` demand is the exploratory one-copy HitNeed model.
`ResidualSourceTokenization` instead requires 25 source microcopies for every
endpoint-need slot.  R29 has one HitNeed at each hub, so the corrected demand
is

```text
6650 + 25 = 6675 per hub,
20025 in total.
```

The same common-blue source relation has `20141` distinct keys.  Exact Hall
margins for masks `0..7` are

```text
0, 1708, 1808, 912, 1808, 912, 1016, 116.
```

Thus R29 also passes at the production microcopy scale, with full-shore margin
`116`.  An explicit injective allocation of all `20025` micro-demands is
stored in `r29_common_blue_micro_allocation.json`.

## Compiled-interface status

This fixture repair is not the full theorem.

- `CheckedC5BaseTransfer` checks one terminal but has no compiled consumer
  mapping terminals to a global transfer matching or typed bank incidence.
- No production declaration named `CheckedTransferMatching` exists.
- `Gamma/FullBankPortSinks.lean` explicitly records that legal edge-to-token
  incidence is absent from `FullBankGlobalPackage`.
- `Gamma/TypedFullBankSources.lean` leaves the sink adapter as a separate
  obligation.
- `Ell5FullBankInterface.lean` states existence of the graph-derived full-bank
  relaxed cover as the remaining open theorem.

Thus the exact conclusion is:

> R29 kills the narrow selector-descent/PHT route.  The existing corrected
> common-blue transfer predicate absorbs its 28-unit obstruction.  The
> surviving wall is construction and formalization of the universal real
> transfer matching and typed FullBank incidence/provider.

## Reproduction

```powershell
python tmp/fanout/r29_fullbank/E_source_search/lead/r29_c5base_absorber.py
python tmp/fanout/r29_fullbank/E_source_search/lead/verify_c5base_absorber_independent.py
python tmp/fanout/r29_fullbank_local/r29_common_blue_micro_gate.py
```

Pinned exact outputs:

```text
minimum absorber keys: 28
new common-blue keys: 216
assignment SHA-256: 43e50aee99b019df6804aa173ba5456f4de2e5ec08b540e13f08349f1398012a
certificate SHA-256: 7572576bcdbc94390faac23b3b4cba0848b0799858a28ccfaa326293fa9497e9
independent verification SHA-256: ccab5e0f50eece849acb5d17d584990196409418c5af3db27b33a546a5fae860
micro gate SHA-256: DF6560388F0EEB54A16B77F3857CC0E82DA392E670C6A52FFF8C188E86FF14C5
micro result SHA-256: 343F90405B932B4A66C98DD180D9EEECC6BAFFDE8785C112F81DF7EC9CD10351
micro allocation SHA-256: CF3F3A985BA748089407521BAE5DD4B19E795DA7A43634A5CD6E174D4E5C313B
```
