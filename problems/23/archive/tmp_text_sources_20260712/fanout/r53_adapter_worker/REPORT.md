# R53 production-independent typed adapter

## Verdict

`SoftEdgeCapGraphAdapter.lean` compiles under Lean 4.27.0. The adapter uses
the global `MinimumDemandCollisionHall.CollisionHalf` domain and realizes the
entire abstract edge-capped key shore as actual proof-carrying
`MinimumDemandCollisionHall.FreeHalf` values. It asserts no flow/provider
existence.

There is no missing graph lemma at this layer. The needed fact is proved as
`activeEdge_pairCount_eq_zero`: if an active blue edge co-occurred on a
selected checked row, `checkedRow_blue_cooccur_implies_pathEdge` would put its
normalized edge in `selectedSupport`, contradicting `activeEdges`.

## Compiled declarations

- `collisionHalf_card_eq_two_mul_collisionUnits`
- `collisionMass_pairCount_eq_collisionUnits`
- `collisionHalf_card_eq_two_mul_collisionMass`
- `activeEdge_card_eq_activeEdges_length`
- `activeEdge_pairCount_eq_zero`
- `activeEdge_reverse_pairCount_eq_zero`
- `activeEdgeFreeHalfKeys_card`
- `activeEdgeFreeHalfBlocks_disjoint`
- `freeBasePartitionEquiv`
- `edgeCappedKeyEquivFreeHalf`
- `edgeCappedKeyEquivFreeHalf_active`
- `edgeCappedKeyEquivFreeHalf_direct`
- `freeBase_card_eq_active_add_direct`
- `active_direct_card_le_freeMass`
- `transportEligible`
- `collision_add_active_le_free_of_globalFlow`

`freeBasePartitionEquiv` is the exact partition

```text
(ActiveEdge x Fin 2) + DirectBase  ~=  FreeBase.
```

The extra `Fin 2` is the orientation of an active undirected edge. Lifting
through the half bit gives `edgeCappedKeyEquivFreeHalf`; its active branch is
definitionally `activeFreeHalf e orientation half`. Thus each aggregate cap
is imposed on exactly the four actual keys in `activeEdgeFreeHalfBlock e`.

`transportEligible` pulls back any concrete eligibility relation, including
a union of six production relations, along this exact equivalence. It does
not construct or assume a feasible flow.

## Verification

- Toolchain: Lean 4.27.0, commit `db93fe1608548721853390a10cd40580fe7d22ae`.
- Final build: exit code 0.
- Printed axioms for eight load-bearing declarations: exactly `propext`,
  `Classical.choice`, and `Quot.sound`.
- Forbidden source tokens (`sorry`, `admit`, `native_decide`, `sorryAx`,
  declared `axiom`): 0.
- Source SHA256:
  `4F790F524D1765E713F4A44FA34ED31A4C38795F529F214FC4B1666F25A9E1AE`.
- Olean SHA256:
  `AEC968B8CB69C19723775F60AD128558F717AEBD790648AB2AF8295133CEBD82`.

Source:
`problems/23/lean/Erdos23Delta0/Gamma/SoftEdgeCapGraphAdapter.lean`.

Olean:
`tmp/fanout/r53_adapter_worker/olean/Erdos23Delta0/Gamma/SoftEdgeCapGraphAdapter.olean`.
