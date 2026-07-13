# R29 scoped Hall gate (d05)

## Verdict

**Not independently gated from the active scoped state.** The workspace archive contains the aggregate assertion `demand=19953`, `reach=17325+2600`, but no R29 graph edge list, cut, bad-atom list, selected rows, or demand/source incidence payload. Consequently those three inputs cannot be rebuilt from graph data here.

The aggregate arithmetic and owner-flow statement are internally consistent. A fresh integer Edmonds–Karp implementation, importing no production helper, returns max flow and min-cut capacity `19925`; against demand `19953` this gives deficiency `28`.

## Exact aggregate reconstruction

The archived score identity `hubs = 3*6651 = 19953`, together with “including 3 HitNeed”, yields the symmetric decomposition used by the claimed tuple:

- each of `r,cL,cR`: collision demand `6650`, HitNeed `1`, total `6651`;
- sameFirst source pool: `17325` free halves;
- rowCompanion source pool: `2600` free halves.

The reconstructed aggregate network has source-to-owner capacities `6651`; each owner reaches both archived source pools; pool-to-sink capacities are `17325` and `2600`. Owner-to-pool capacity is `19954`, one more than all demand, so it cannot enter a minimum cut.

## Min-cut certificate

- source side: `{SOURCE,r,cL,cR,sameFirst,rowCompanion}`
- sink side: `{SINK}`
- crossing arcs: `sameFirst->SINK` of capacity `17325`; `rowCompanion->SINK` of capacity `2600`
- cut capacity: `17325+2600=19925`
- max flow: `19925`
- unsent demand: `19953-19925=28`

This is a valid certificate for the aggregate network in `min_cut_certificate.json`. It is **conditional on the archived reach-set cardinalities and universal hub-to-pool incidence**; it does not certify that the R29 graph actually induces those data.

## Discrepancy witness

No integer discrepancy occurs in the archived totals. The explicit evidentiary discrepancy is that `WALL_ATTACK_R29_GPTPRO56.md` names claimed generator/result SHA prefix `00186166...`, but no matching payload is present in the workspace: the memo supplies neither the graph-derived active state nor a file having that claimed hash. Thus the requested graph-level owner-flow/min-cut cannot be compared with an independently reconstructed state.

## Reproduction

Run `python independent_owner_flow.py`. It asserts demand `19953`, flow=cut `19925`, and gap `28`, and prints the complete certificate. Only Python integers are used; there are no floats or approximate comparisons.

## SHA256

- `independent_owner_flow.py`: `5BD83E6B910D2CCE90CB8B8CE9FD858B9AA67D14392965169F9A911F261F5AEB`
- `min_cut_certificate.json`: `5547224DB59316DC9E814C90C1B84A2266BA077D0E48C7437013B1F863B1CD01`
- `WALL_ATTACK_R29_GPTPRO56.md`: `FFF06D97F2E574FE2D66B9CEA4F3BC4244037A92EB8ED5BD363ECA73C8591B04`
- `ActiveScopedOwnerHallReduction.lean`: `6A4D47533D10E4B04EB19CDA0D0554658ABD434C94C04566A01916708A90E8F0`

## Proof gaps

1. Reconstruct `Active G c omega`, its 2775-vertex component, and verify the three hubs belong to it.
2. Enumerate `scopedOwnerDemandSet W` from selected rows and verify collision demand `19950` plus exactly three HitNeed units.
3. Enumerate distinct `FreeHalf` sources satisfying `Available`, prove the disjoint/overlap-corrected split `17325+2600`, and verify every aggregate owner-to-pool incidence used above.
4. Hash and retain the missing R29 generator, graph/cut/row fixture, and machine result corresponding to claimed prefix `00186166...`.

Until those payloads exist, the gap-28 claim is arithmetically coherent but not independently certified as a fact about the claimed 2943-vertex tuple.
