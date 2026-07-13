# R29 all-anchor prune audit

## Verdict

The full graph-derived prune universe justified by the current Lean tree is empty. There is no legal prune token incident to the hub shore, so prune capacity there is exactly `0`. Hence no exact-28 prune absorber exists.

This is an implementation-level certificate, not a claim that every future semantic prune construction is impossible. Lean currently contains only the abstract `CapKind.prune`, `CapSource.prune PruneKey`, arbitrary `capQ`, and global uniqueness/no-double-spend fields. It contains no `CheckedPruneStep`, prune reachability, trace, graph-to-token adapter, or capacity theorem.

## Recovered semantics

- Production Lean: a prune token is only a typed ledger source. Uniqueness is on `(component, source)` in `TypedGlobalLedgerData`, equivalently `(component, kind, payload)`. The global package separately requires `token_source_unique` and `no_double_spend`.
- R19/R20 proposed semantics, not compiled: one same-cut shortest-row rewrite with rows unchanged outside the rewritten atom, zero switch loss, preserved active component, a strictly decreasing local row-rewrite rank, and an injective `move : incoming ↪ outgoing` satisfying `moveSound` on affected half-slot keys.
- Global `Γ` is explicitly invalid as the terminating rank. Individual reachability plus termination is insufficient: two obligations may reach the same FreeHalf source. Source uniqueness therefore comes from the injective slot transport, not from the rank.
- Capacity cannot be inferred from the existence of a rewrite. A justified prune token must retain a unique transported FreeHalf source and its checked capacity; no such constructor is present for R29.

## Canonical rewrite pre-universe

Exact reconstruction gives 676 selector families. Each has 680 shortest rows: 676 anchor rows and 4 local rows. From the chosen canonical anchor row the complete one-row alternative census is:

| necessary geometric candidate | count | justified prune capacity |
|---|---:|---:|
| anchor → different anchor | 456,300 = 676·675 | 0 |
| anchor → local | 2,704 = 676·4 | 0 |
| total | 459,004 | 0 |

These are rewrite candidates only. None is a legal prune move because the repository supplies neither a specified decreasing local rank nor an injective `moveSound` slot map and graph-to-ledger adapter. The 707 rigid atoms have one shortest row and contribute no candidate.

Thus the legal candidate/source enumeration is empty, its capacity sum is `0`, termination is vacuous (empty relation, rank may be constant `0`), and source uniqueness is vacuous. Relabelling any of the already counted 19,925 FreeHalf keys as prune would violate the required graph-derived constructor and risks double spend.

## Exact obstruction

After the certified FreeHalf allocation, owner demands `(6651,6651,6651)` receive `(6651,6651,6623)`, leaving residual `(0,0,28)`. For the prune-only justified universe:

- residual Hall shore: `{owner 2}`;
- neighboring legal prune sources: `∅`;
- neighboring capacity: `0`;
- demand: `28`;
- defect: `28`;
- min-cut capacity / max flow: `0 / 0`;
- Farkas multiplier: `1` on owner 2's residual constraint and `0` elsewhere, giving `28 ≤ 0`, false.

FullBank units require raw `capQ = 25` per Hall unit, so an exact-28 absorber would require total raw `capQ = 700`; the justified prune universe supplies `0`.

## Replay and provenance

```powershell
python tmp\fanout\r29_gate\lead\r29_lead_gate.py
python tmp\fanout\r29_fullbank\E_source_search\flow_dual\check_certificate.py
git grep -n -E "structure CheckedPruneStep|inductive CheckedTransferEdge|def checkedPruneReachability|theorem checkedBaseCorridorPruneMatching" -- problems/23/lean
```

The final grep returns no compiled prune-trace symbol. Exact source hashes:

- `TypedFullBankSources.lean`: `6ab920d11b983848a46d95e9477a4bf4b1b948992a3aef5f158aff4dc1820fbd`
- `FullBankToLengthSurplusCharge.lean`: `f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd`
- `WALL_ATTACK_R19_GPTPRO56.md`: `bfb75636d5e11b7f3d251cb20a64a5227f5b870938f1d1b715f38d400903adfc`
- `WALL_ATTACK_R20_GPTPRO56.md`: `cc4f42d19203a91ca4663a67c51cb1cb01273c442eaee733bf9dce94bb3b29f5`
- owner-Hall certificate: `dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce`

Smallest exact statement: **the current graph-derived prune provider has empty legal source neighborhood at the R29 all-anchor hub residual; therefore prune contributes 0 Hall units and cannot absorb 28.**
