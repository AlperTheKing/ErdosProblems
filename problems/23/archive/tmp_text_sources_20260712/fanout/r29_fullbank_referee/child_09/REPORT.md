# Independent formal referee report: R29 FullBank hub shore

## Verdict

The exact active-scoped quotient is `H={0,1,2}: demand 19953, legacy FreeHalf reach 19925, defect 28`.

For `k` in `door`, `vertexSlack`, `c5Base`, `prune`, let `Delta_k(H)` be the capacity of distinct production source keys of kind `k` which a checked provider proves legal/reachable from `H`, excluding capacity already represented among the 19,925 FreeHalf sources. Exactly:

`H is absorbed iff Delta_door(H)+Delta_vertexSlack(H)+Delta_c5Base(H)+Delta_prune(H) >= 28`.

"Capacity/reach" is the increment in legal capacitated-neighborhood rank (equivalently shore max-flow value), not raw global capacity. Unreachable capacity does not count. I cannot prove or refute R29 absorption from the authoritative inputs: no concrete four-class provider table gives capacities and legal incidence to `H`. The FullBank verdict is **undecided**, not deficient.

## Symbolic quotient and proof

Collapse 19,953 hub obligations to demand node `H`, and 19,925 distinct FreeHalf neighbors to source `F` of capacity 19,925. Add source blocks `D,V,C,P` containing only new legal source capacity. The hub cut is `19925 + Delta_D + Delta_V + Delta_C + Delta_P`; it covers 19,953 iff the added legal rank is at least 28. Integer max-flow/min-cut proves both directions. Aggregate capacity alone does not prove incidence.

## Source-key disjointness and no-double-spend

`CapSource` is a tagged sum, so `door e`, `vertexSlack v`, `c5Base b`, and `prune r` are disjoint even if payload encodings coincide. `TypedGlobalLedgerData.source_injective` gives uniqueness of `(component, source)`, hence `(component, kind, payload)`.

The legacy ledger stores `(comp, kind, sourceId)`. `Checked.token_source_unique` makes that triple unique; `no_double_spend` bounds total token spend by `capQ`; `no_cross_component_spend` confines positive spend to its component. These suffice only if the provider maps every physical source to one canonical key. The 19,925 FreeHalf keys and FullBank keys inhabit different types; no inspected field proves their images disjoint or records overlap, so their capacities cannot simply be added.

## Exact missing provider field

A checked hub-shore incidence exporter is missing:

```text
hubToken : Fin tokenCount -> TypedLedgerToken ...
legalToHub : Fin tokenCount -> Prop
legacyImage : FreeHalf -> Option (Fin tokenCount)
source_injective : Injective (fun t => ((hubToken t).comp, (hubToken t).source))
legal_source : legalToHub t -> productionLegal H (hubToken t).source
cap_nonneg : 0 <= (hubToken t).capQ
legacy_overlap_exact : legacyImage records exactly all FreeHalf/token overlap
spend_le_cap : sum_hub_spend(t) <= (hubToken t).capQ
added_rank_eq : maxFlow(with tokens) - 19925 = nonoverlap legal capacity
```

For unit slots, `added_rank_eq` may be replaced by an injective map of new legal slots to canonical source keys, disjoint from the legacy image, plus a count equality. This is the adapter obligation explicitly left separate in `TypedFullBankSources.lean`. No inspected R29 input supplies it or per-kind totals implying it.

## Replay

`python tmp/fanout/r29_fullbank_referee/child_09/quotient_gate.py`

The gate uses integers and `Fraction`; it checks defect, tag disjointness, legality sensitivity, and both threshold sides.

## SHA256 inputs

- R29 attack: `FFF06D97F2E574FE2D66B9CEA4F3BC4244037A92EB8ED5BD363ECA73C8591B04`
- R29 claimed numbers: `5508CFCBCFE4D5072B52ACECDF0AB8DCCBEC5CBE2A30C8E0997F6B01DD95AD42`
- FullBank ledger: `F4806742BDFF61E0E3A15637C25D796B0ABF0803936AAABC82A77DE2A1DA40CD`
- Typed sources: `6AB920D11B983848A46D95E9477A4BF4B1B948992A3AEF5F158AFF4DC1820FBD`
- ActiveScoped: `6AA3FDD19D15A4A5231494C6B92F3659BFCF13CFA1F2D900B6F3857EC1CF019D`

No other child output was read or imported.
