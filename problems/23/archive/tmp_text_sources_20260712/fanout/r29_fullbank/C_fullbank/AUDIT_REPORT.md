# R29 all-anchor versus the compiled FullBank wall

## Verdict

The canonical `N=2943` all-anchor tuple exactly falsifies the current active-scoped four-pattern relation:

`D({0,1,2}) = 19953 > 19925 = |Reach4({0,1,2})|`, defect `28`.

It is **not a FullBank falsifier**.  The compiled singleton all-Door constructor gives a zero-defect local wall primal once the own-Door provider hypotheses are supplied.  On this graph the exact conditional Door ledger has capacity `4242`, spend `2750`, and slack `1492` Hall units.  At typed-ledger scale these are `106050`, `68750`, and `37300` capQ.  Thus the `28`-unit (`700` capQ) scoped shortfall is numerically absorbed by the Door class, but this is a different wall routing certificate, not 28 new FreeHalf keys.

The real graph-derived conclusion remains unresolved because own-Door legality, typed sink embedding, component ownership, and the local-to-global package adapter are not constructed by the current compiled APIs.

## Exact gate

For `C = union(selected row vertices)`, `F = selected blue row edges`, and `O = B minus F`:

- `|S|=1383`, `|C|=2127`, `|F|=2797`, `|O|=4242`.
- Singleton weights are `lambda_x=1/2`.
- Every bad atom has coverage `1`; every edge in `F` has congestion `1`.
- Off-support load histogram is `112` at `0`, `2760` at `1/2`, `1370` at `1`.
- Conditional own-Door routing is `q(e,j)=load(e)` when `j=e`, otherwise `0`.
- Distinct edge source keys give token-source uniqueness; each token has `capQ=25`; spends are `0`, `25/2`, or `25`, so no double spend holds exactly.
- Under the still-assumed one-component fields `compN=2943`, `rowCount=1383`, component residual is `8626674`, token cap is `106050`, reserve slack is `8520624`, and superadditivity slack is `0`.

This is the strongest finite rational gate currently supported by the compiled definitions: graph geometry and primal arithmetic are checked; provider fields remain named hypotheses.

## Source classes

- `Door`: conditional absorber. `4242` tokens, spend `2750`, slack `1492`; local wall routing defect `0`.
- `vertexSlack`: no hub capacity. Each hub has `T=3380>N=2943`, hence candidate `max(0,N-T)=0`; each also has internal endpoint load `1/2`.
- `c5Base`: no fresh capacity beyond the deduplicated `19925` FreeHalf source keys (`17325` sameFirst plus `2600` rowCompanion; commonBad/outsideAttachment add `0`). Counting these again would double spend.
- `prune`: `0` instantiated graph-derived tokens. A selector rewrite is not a strict proper descendant and supplies no prune ledger identity.

## Assumed provider fields

1. `ownDoor_inc`: every `e in O` is legally incident to its own Door sink.
2. `ownDoor_capacity`: every such sink has Hall capacity at least `1`, equivalently typed `capQ >= 25`.
3. `DoorWallAdapter`: typed Door tokens embed injectively into real wall sinks and preserve `capQ/25`.
4. Global component/local ownership for every Door token and positive spend.
5. The one-component identification `compN=2943`, `componentRowCountQ=1383`.
6. A semantic adapter from `EndpointHalfDoorFullBankBundle` to `FullBankGlobalPackage`.
7. Any independent c5Base keys disjoint from the existing FreeHalf keys.
8. Any graph-derived prune key, proper descendant, and balance identity.

## Smallest statements

Unconditional falsifier:

`not (ActiveScopedDemand omega {0,1,2} <= card (Reach4 omega {0,1,2}))`, witnessed by `19953 > 19925`.

Conditional wall theorem:

If `forall e in O, inc e e` and `forall e in O, 1 <= kap e`, then `certificate_of_singletonCore_allDoors` instantiated on the R29 all-anchor `S,F,O,C` yields a `FullBankRelaxedCoverCert` with total routed load `2750`, total Door capacity `4242`, and routing defect `0`.

## Replay commands

```powershell
python tmp\fanout\r29_fullbank\C_fullbank\synthesis\r29_fullbank_gate.py
python tmp\fanout\r29_fullbank\C_fullbank\d2_door\replay_door_audit.py
python tmp\fanout\r29_fullbank\C_fullbank\d3_vertex\replay.py
python tmp\fanout\r29_fullbank\C_fullbank\d4_c5base\audit_c5base.py
python tmp\fanout\r29_fullbank\C_fullbank\d5_prune\replay.py
python tmp\fanout\r29_fullbank\C_fullbank\d7_referee\replay.py
```

## SHA-256

- `r29_fullbank_gate.py`: `0efb329f8441124be608c82007b5dd66d9b637307fc0c72def28acdef85cdcdc`
- `result.json`: `131640743597938a38680a4a63bc826ea95e926bd8acb8dea9db12e5a65d23a6`
- canonical R29 builder: `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`
- `Ell5SingletonVertexSlack.lean`: `2c260fdf075f62e308cacfdbbf9a08e4fdc6cb1ec461a0e3890a281ca7121048`
- `EndpointHalfDoorComplete.lean`: `800547bc53068873072306afba3c9e51000b8f13571ed9d1061e1c13ef43e164`
- `FullBankToLengthSurplusCharge.lean`: `f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd`
- `TypedFullBankSources.lean`: `6ab920d11b983848a46d95e9477a4bf4b1b948992a3aef5f158aff4dc1820fbd`
- `TypedOwnDoorHalfLayer.lean`: `793f8b47926dbe93e2b0f476e42ae33a688913faa95e46912205ec69009a4eaa`
- `WIRING_SPECS_GPTPRO.md`: `cc13f03a08750a12a15a5a70620fb31d88e82bde579d3acd72e6218317bb6a0a`
