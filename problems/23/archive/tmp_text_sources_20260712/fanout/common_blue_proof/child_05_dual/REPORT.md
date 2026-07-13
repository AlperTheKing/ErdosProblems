# Hall-deficiency dual report

## Exact reduction

The common-blue extended matching LP has the fractional vertex-cover dual in `CERTIFICATE_SCHEMA.md`. Since `MicroAvailable d s` depends on `d` only via `microDemandOwner d`, every obstruction saturates to whole owner fibers with the same neighborhood. Universal micro-Hall is equivalent to, for every owner set U,

`sum_(v in U) (collisionHalfCount(v)+25*hitNeedCount(v)) <= |{s: not ScopedReserved(s) and exists v in U, EligibleOwner(v,s) or CommonBlueOwner(v,s)}|`.

A violating U gives an exact integral Farkas witness: demand weights 0 on its saturated shore and 1 outside; source weights 1 on its neighborhood and 0 outside. The objective is `|D|-defect(U)`. An inclusion-minimal witness is obtained by deleting owners while defect stays positive.

## Max-cut/surplus limit

Each new arc satisfies `dM({x,y})+2 <= dB({x,y})`, so adjusted surplus `dB-dM-2` is nonnegative. This proves arc legality after reserving two owner edges. It gives no distinct-source cardinality bound: summing before an injection exists may reuse one source.

`abstract_countermodel.json` is minimal abstractly: two demands of one owner, one common source, adjusted surplus 0 on both arcs. Every arc-local inequality holds, but Hall defect is 1. It is not claimed graph-realizable under every GraphData predicate.

## Minimal open lemma

**OwnerShoreCapacity:** for every valid triangle-free G, Gamma-minimal max cut c, row choice omega, and owner finset U, the micro-demand count above is at most the number of unreserved FreeHalf keys old-eligible or corrected-common-blue eligible for some v in U.

No inspected max-cut inequality implies this distinct-key count. A proof needs source-disjoint counting or a capacity-bearing certificate. R29 satisfies its tested instance and is not a countermodel.

Run `python check_dual.py abstract_countermodel.json`; the checker uses integer cardinalities and `fractions.Fraction`, with no float or solver.