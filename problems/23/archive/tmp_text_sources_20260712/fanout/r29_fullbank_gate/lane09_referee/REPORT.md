# R29 FullBank exact audit — lane09 independent referee

## Verdict

**UNDEFINED** for the decisive production question.

The deterministic R29 all-anchor tuple is fully reconstructed and the literal
`Gamma/ActiveScoped*` owner-Hall failure is independently reproduced.  However,
the production tree contains no fully instantiated relation connecting those
cardinality objects to FullBank off-support ports, typed tokens, legal incidence,
and rational capacities.  Therefore neither “production absorbs 28” nor “28
survives every production source class” is a defined, replayable proposition in
the current implementation.

Two narrower verdicts are exact:

1. **FAIL — literal implemented ActiveScoped relation.**  Demand is `19,953`,
   reachable `FreeHalf` source identities are `19,925`, and shore `{0,1,2}` has
   defect `28`.
2. **PASS — conditional auxiliary composition only.**  If the compiled
   `CheckedC5BaseTransfer.TerminalData.Valid` predicate is composed with the
   R29 `FreeHalf` universe and treated as an owner-uniform global matching class,
   it adds `216` new source identities after overlap removal.  Reach becomes
   `20,141`; all seven nonempty owner shores pass, with minimum slack `188` at
   `{0,1,2}`.  That composition is not implemented production semantics.

The R23 `outsideAttachment` prose relation contributes exactly `0` source
identities on R29 when its stated selected-component equality is enforced: the
`816` outside vertices form `704` blue components (`676` of size 1, `28` of size
5), and every component has owner eligibility mask 0.  This is a result about a
prose-only relation, not a production source class.

## Exact reconstruction and incremental accounting

The gate imports only `r29_lead_gate.py:build()` and independently rebuilds the
all-anchor rows, ordered pair counts, support, selected set, active graph and
components, collision demand, HitNeed demand, reservations, and all eight owner
shores.

| Stage | Candidates | Prior overlap | New identities | Union | Full-shore gap |
|---|---:|---:|---:|---:|---:|
| `sameFirst` | 17,325 | 0 | 17,325 | 17,325 | — |
| `rowCompanion` | 2,600 | 0 | 2,600 | 19,925 | +28 |
| checked common-blue terminal, conditional composition | 2,824 | 2,608 | 216 | 20,141 | -188 |
| R23 prose `outsideAttachment` | 0 | 0 | 0 | 20,141 | -188 |

All rows have length 5.  Reconstructed graph counts are `N=2,943`, `|B|=7,039`,
`|M|=1,383`; the all-anchor scope has 2,127 selected vertices, 1,370 active
edges, 19 active vertices, and 18 demanded active edges.  Each hub has collision
6,650 and HitNeed 1, hence demand 6,651.

No capacities were arithmetically summed across classes.  Sources are unioned by
the exact `(sourceX, sourceY, half)` identity; owner masks are unioned on overlap.
`ScopedReserved` half-zero active-edge sources are removed before counting.

## Why the production question is undefined

- ActiveScoped demand is the cardinality of `ActiveCollisionHalf ⊕ ActiveHitNeed`,
  and matching is an injection into ordered `FreeHalf` triples
  (`Gamma/ActiveScopedMinimumExchange.lean:80-158`).
- The FullBank relaxed-cover interface instead routes rational load on
  off-support edges `O` through an abstract `inc : E → JT → Prop` and
  `kap : JT → ℚ`; existence remains open
  (`Ell5FullBankInterface.lean:7-10,23-40`).
- `FullBankGlobalPackage` is a supplied rational ledger.  It checks local
  `demandQ`, four cap kinds, spends, and no-double-spend, but does not construct
  the package (`Gamma/FullBankToLengthSurplusCharge.lean:6-14,34-54,134-227`).
- Production explicitly states that legal edge-to-token incidence is absent and
  its finite sinks do not assert Hall
  (`Gamma/FullBankPortSinks.lean:80-81`).
- Typed sources likewise state that connection to the wall `Sink` is a separate
  adapter obligation (`Gamma/TypedFullBankSources.lean:6-14`).
- `ActiveComponentBankHall` takes `incBase`, `kapBase`, and the entire weighted
  Hall condition as parameters; it does not instantiate them for R29
  (`Ell5ActiveComponentBankHall.lean:27-64`).
- The checked common-blue module says permanent-Free ownership and global
  matching are separate layers (`Gamma/CheckedC5BaseTransfer.lean:13-15`).
  The row-companion module says the source-slot and global matching layers remain
  separate (`Gamma/CheckedRowCompanionBaseTransfer.lean:8-13`).
- The repository contains an exact countermodel proving an aggregate checked
  ledger alone cannot create port incidence
  (`AggregateLedgerNoIncidenceCounterexample.lean:6-16,152-157`).
- No `outsideAttachment`, `CheckedOutsideAttachmentBaseTerminal`,
  `CheckedTransferMatching`, `checkedTransferMatching_to_activeFullBank`, or
  `ActiveComponentFullBankCert` definition occurs in the audited Gamma/FullBank
  production surface.  R23 supplies only prose/“Lean shapes given”
  (`WALL_ATTACK_R23_GPTPRO56.md:7-15,29-34`).

There is also a unit mismatch with no compiled bridge: ActiveScoped counts whole
obligation/source identities; FullBank uses rational port load, ledger sinks use
`capQ/25`, and typed Doors require raw `capQ ≥ 25` to obtain Hall capacity at
least 1 (`Gamma/FullBankPortSinks.lean:41-49` and
`Gamma/TypedFullBankSources.lean:151-159`).  No theorem identifies one
ActiveScoped unit with a FullBank load or token fraction.

## Minimal missing semantics

1. The concrete R29 FullBank port set `O` and exact rational load per port.
2. Concrete typed door/vertexSlack/c5Base/prune tokens with exact `capQ`,
   component, and unique source identity.
3. Computed legal port-to-token incidence, including implemented
   outside-attachment/prune definitions if those are intended source classes.
4. A bridge from ActiveScoped obligations to FullBank loads, including factor 25
   and any half/`K` scaling.
5. One overlap-safe global flow/spend certificate enforcing reservations,
   no-double-spend, and component locality.
6. An instantiated checked `FullBankGlobalPackage` or
   `FullBankRelaxedCoverCert` for this R29 tuple.

## Replay

From `E:\Projects\ErdosProblems`:

```powershell
python tmp\fanout\r29_fullbank_gate\lane09_referee\audit_r29_fullbank.py
python tmp\fanout\r29_fullbank_gate\lane09_referee\make_hashes.py
```

The first command exits 0 only after asserting the R29 counts, canonical payload
hash, scope counts, demand 19,953, implemented reach 19,925, defect 28, reference
certificate agreement, and absence of the named unimplemented symbols.  Exact
details, all eight cuts at every stage, source overlaps, source-line contract,
and input hashes are in `audit_result.json`.

## SHA256

- `audit_r29_fullbank.py`:
  `386532d17f94b01863c080abf2e70878701677741c4d8119a2868d15e223f2dc`
- `audit_result.json`:
  `58cdf9a7855e2b9a6832cbd624aa982cfc8797ced0dfd9fd8a018682cf365ba7`
- authoritative lead script:
  `5d29b1d6e35957405c53176fab1fb21660d727cb334a1e20462eb5ebe36678f6`
- reconstructed canonical lead payload:
  `fc4f3ab94bed810669976b1fdb21743fdd4ebe57eea15ef52afcfc2165e2fb1f`
- reference cut certificate:
  `dd1f1a2cff0886e6eaf8ed6487d7a5f308e51446b2ffbc284d6caac3f797e1ce`
- `ActiveScopedMinimumExchange.lean`:
  `6aa3fdd19d15a4a5231494c6b92f3659bfcf13cfa1f2d900b6f3857ec1cf019d`
- `CheckedC5BaseTransfer.lean`:
  `12451978d18a455b312ef292aa249f7f6d5a1c950e3112ec03a0d4ed86d17ee0`
- `FullBankToLengthSurplusCharge.lean`:
  `f4806742bdff61e0e3a15637c25d796b0abf0803936aaabc82a77de2a1da40cd`
- `FullBankPortSinks.lean`:
  `ec03183e2dd9c1ee5578d589558e5400d9d4c8260a056fbbc5da483b8614a4f6`
- `TypedFullBankSources.lean`:
  `6ab920d11b983848a46d95e9477a4bf4b1b948992a3aef5f158aff4dc1820fbd`

`HASHES.json` records all lane artifact hashes, including this report.
