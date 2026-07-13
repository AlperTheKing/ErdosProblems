# Exact deficient-shore vertexSlack audit

Verdict: vertexSlack pays exactly `0` of the `13` unmatched microcopies.

The canonical graph6 decoder and production row-family code reconstruct tuple index `377`, choice `[0,4,5,7]`, as

```
(6,0,9,2,8)
(6,1,10,3,7)
(7,3,10,5,11)
(8,3,10,5,11)
```

The deficient shore is owners `{10,11}`. Production `ActiveScopedMinimumExchange.hitNeedUnits` first subtracts ordinary vertex slack `N-selectedLoad` from active degree. Therefore only slack left after those legal endpoint ports is incremental capacity; adding the pre-subtracted amount again is double spending.

| owner | typed source key | occurrences | selected load | raw graph slack | raw capQ | capQ/25 | legal active-edge ports | active degree | already spent capQ | HitNeed | residual capQ |
|---:|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|
| 10 | `CapSource.vertexSlack(10)` | 3 | 15 | 0 | 0 | 0 | `(0,10)`, `(2,10)` | 2 | 0 | 2 | 0 |
| 11 | `CapSource.vertexSlack(11)` | 2 | 10 | 2 | 50 | 2 | `(0,11)`, `(1,11)` | 2 | 50 | 0 | 0 |

Each listed active-edge endpoint is incident with its owner. In `hitNeedUnits` accounting it consumes one ordinary-slack unit, equivalently `25` microcopies. Separately, the Ell5 local-cover `endpointQ` route charges `1/2` per incident edge; production does not instantiate a global typed vertexSlack token or an adapter equating that local `kap` with ledger `capQ/25`. These two scales are not conflated here. Owner 11's raw capQ `50` is exhausted by its two ports. Owner 10 has no raw slack and leaves two HitNeed slots, hence `50` HitNeed microcopies.

On the deficient shore the collision demand is `22` microcopies and HitNeed demand is `2*25=50`, totaling `72`. Raw vertexSlack is capQ `50`, but all `50` was already subtracted when forming HitNeed. Literal non-double-counted residual is capQ `0`, Hall capacity `0/25=0`; it cannot pay any of defect `13`.

`TypedFullBankSources` supplies the typed constructor but production has no compiled global vertexSlack incidence checker analogous to own-edge Doors. This audit does not infer a FullBank repair from the aggregate `50`; the edge table is the required incidence witness, and the no-double-spend calculation kills the aggregate claim.

Replay:

```
python tmp/fanout/common_blue_universal/pivot_defect13/laneB_vertex_slack/replay_vertex_slack.py
```

