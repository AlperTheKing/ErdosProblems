# R20/R23 source-kind audit

Scope: production sources only: `WALL_ATTACK_R20_GPTPRO56.md`, `WALL_ATTACK_R23_GPTPRO56.md`, and compiled files under `problems/23/lean/Erdos23Delta0/Gamma`.

## Decision

| transfer relation | compiled production meaning | FullBank field it may feed | fields it may not feed | present bridge |
|---|---|---|---|---|
| `sameFirst` | Lean name `SameOwner`: `s.sourceX = d.owner`; also the first disjunct of `ActiveScopedMinimumExchange.EligibleOwner` | `c5Base`, when the matched `FreeHalf` pays an endpoint/base obligation | `door`, `vertexSlack`, `prune` | absent |
| `commonBad` | R20's older common-neighbour base terminal; compiled checker is `CheckedC5BaseTransfer.TerminalData.Valid`, requiring two blue source-to-owner edges and `dM switch + 2 ≤ dB switch` | `c5Base` | `door`, `vertexSlack`, `prune` | absent |
| `rowCompanion` | `RowCompanion` / second disjunct of `EligibleOwner`: both source coordinates co-occur with owner and the two-vertex switch has nonnegative `sigma`; the stronger literal checker is `CheckedRowCompanionBaseTerminal` | `c5Base` | `door`, `vertexSlack`, `prune` | absent |
| `outsideAttachment` | R23 non-local outside-component attachment transfer, intended to spend the matched permanent `FreeHalf`; no production Lean declaration or checker exists | `c5Base` only, after formalization | `door`, `vertexSlack`, `prune` | absent at both terminal and token layers |

Thus none of the four relations can semantically populate `doorCapQ`, `vertexSlackCapQ`, or `pruneCapQ`. They are all C5-base transfer patterns. A collision-demand match is cancellation and creates no FullBank spend; only a matched endpoint/base obligation becomes a `c5Base` token/spend. This demand distinction must be retained by the adapter.

## Why the other kinds are incompatible

- `door` has exact own-exit-edge provenance. `CapSource.door` carries an `ExitEdgeKey`, and `OwnEdgeDoorSourceData.Checked` requires source equality with `door (portEdge p)`. A free ordered pair plus any of the four transfer relations does not supply that equality.
- `vertexSlack` is keyed by a vertex. None of the four relations proves that its free-pair unit is vertex residual slack; an owner appearing in the relation is a destination/support vertex, not a `vertexSlack` provenance proof.
- `prune` is keyed by a prune witness and R20 requires an actual checked row rewrite with injective slot transport and decreasing local rank. A base relation alone supplies no such witness.
- `c5Base` is keyed by `BaseKey`, exactly the missing place to encode the permanent `FreeHalf` source used by these base transfers.

## Compiled-semantics caveats

`FullBankGlobalPackage.Checked` checks only numeric kind totals, nonnegative spend, token capacity, component agreement, and uniqueness of legacy `(comp, kind, sourceId)`. It contains no relation between a graph terminal and a token. Consequently, the aggregate package can presently be filled with a token labelled `c5Base` without proving `sameFirst`, `commonBad`, `rowCompanion`, or `outsideAttachment`.

`TypedFullBankSources.CapSource` repairs kind/payload typing, but only the `door` constructor has a production legality checker. The file explicitly leaves the adapter to wall sinks separate. There is no `c5BaseLegal`, no conversion from a matched `FreeHalf` to `BaseKey`, no typed-ledger-to-`FullBankGlobalPackage.ledger` adapter, and no theorem connecting a transfer matching to `localCap_eq_kindSpends`.

There is also a relation mismatch inside compiled production: `MinimumDemandCollisionHall.Eligible` and `ActiveScopedMinimumExchange.EligibleOwner` contain only same-owner and row-companion. `commonBad` exists as a standalone checked terminal but is not a named disjunct there (it is geometrically subsumed only if one separately proves the row-companion hypotheses). `outsideAttachment` is absent entirely. Therefore R23's claimed “compiled consumer unchanged” is not realized by the current production relation.

## Smallest candidate bridge theorem

The first useful bridge should be relation-agnostic after a four-pattern legality predicate is defined, and should expose exactly the typed source equality required downstream:

```lean
theorem matchedBase_source
    {G : GraphData} {c : CutData} {bads : List BadEdgeData}
    {omega : RowChoice bads}
    (baseKey : FreeHalf G omega → BaseKey)
    (token : Fin tokenCount →
      TypedLedgerToken componentCount ExitEdgeKey VertexKey BaseKey PruneKey)
    (baseOf : FreeHalf G omega → Fin tokenCount)
    (legal : ∀ d s, FourPatternEligible G c omega d s →
      (token (baseOf s)).source = CapSource.c5Base (baseKey s))
    {d : Demand G c omega} {s : FreeHalf G omega}
    (h : FourPatternEligible G c omega d s) :
    (token (baseOf s)).source = CapSource.c5Base (baseKey s) :=
  legal d s h
```

This is deliberately the smallest signature: it bridges eligibility to typed `c5Base` provenance without falsely deriving capacity, injectivity, component ownership, or spend accounting. Those require separate hypotheses/theorems. Before this can compile, production needs `FourPatternEligible` (including a checked `outsideAttachment`) and a `BaseKey` encoding of `FreeHalf`; after it, a second adapter must connect typed tokens and matched endpoint/base demands to the legacy FullBank ledger and `c5BaseCapQ` equality.
