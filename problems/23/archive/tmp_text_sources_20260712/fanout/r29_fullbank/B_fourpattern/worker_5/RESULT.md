# Exact four-pattern min-cut audit

## Verdict

The exact R23 `outsideAttachment` relation includes the selected-component
equalities `comp(a)=comp(owner)=comp(b)`.  On the canonical `N=2943` all-anchor
tuple no outside attachment satisfies these equalities.  Thus pattern four
adds zero capacity.  The full owner shore has demand `19953`, neighborhood
capacity `19925`, deficiency `28`, and cut capacity `19925`.  This is an exact
falsifier of the auxiliary four-pattern Hall statement for this tuple.

The looser test which asks only that an attachment co-occur with the owner
would add `912600` half keys, but those keys are not in the stated exact R23
relation: all `676` loose attachment witnesses lie in selected active
components different from the hub component.

## Reservations and multiplicities

A source is a `FreeHalf` triple `(x,y,h)`, with ordered `(x,y)` and
`h in {0,1}`.  Every free ordered cell therefore has capacity two before a
reservation.  Eligibility for several owners changes its outgoing arcs, not
its capacity.  Eligibility through several patterns also does not duplicate a
half key; pattern provenance must be unioned before capacity is counted.

`Reserved` is exactly `h=0` when `normEdge(x,y)` is an active off-support edge.
So a reserved ordered cell retains its `h=1` capacity.  The three affected
cells are `(0,55)`, `(1,2929)`, `(2,2930)`.  Raw same-first capacity is
`3*2888*2=17328`; removing those three half-zero keys yields `17325`.
Row-companion gives `1300*2=2600` shared keys.  Exact outside-attachment gives
zero.  Hence direct expanded-key capacities by owner mask are

`m=1: 5775, m=2: 5775, m=4: 5775, m=7: 2600`,

and total capacity is `19925`.

## Direct cut summation

For owner shore `S`, the independently summed cut is

`19953 - demand(S) + #{unreserved half keys k : mask(k) & S != 0}`.

For shore masks `0,1,...,7`, source-neighborhood capacities are

`0, 8375, 8375, 14150, 8375, 14150, 14150, 19925`,

and network cut capacities are

`19953, 21677, 21677, 20801, 21677, 20801, 20801, 19925`.

Thus the unique minimum among these owner-quotient cuts is the full shore,
with value `19925`; its deficiency is `19953-19925=28`.  All arithmetic is
integer arithmetic.

## Demand-ledger qualification

The `6651` per owner used above equals `6650` collision halves plus one
`HitNeed`, while the source ledger has already removed the reserved hit half.
It is therefore a stronger auxiliary ledger, not literally the Lean
post-reservation `CollisionMatching` ledger.  Literal collision demand is
`6650` per owner; with the same unreserved sources its full-shore deficiency is
`19950-19925=25`.  Hence the exact four-pattern relation fails both ledgers,
by `28` and `25` respectively.

## Smallest justified statement

On the canonical `N=2943` all-anchor tuple, the exact four-pattern
owner-quotient relation with R23's selected-component equalities has no
outside-attachment sources and fails Hall on owner shore `{0,1,2}`: auxiliary
deficiency `28`, and literal post-reservation collision deficiency `25`.

This finite falsifier does not assert a FullBank obstruction; it concerns the
implemented ordered-`FreeHalf` relation only.

Run `python checker.py` to regenerate `certificate.json` by expanding concrete
half keys and directly summing every cut.
