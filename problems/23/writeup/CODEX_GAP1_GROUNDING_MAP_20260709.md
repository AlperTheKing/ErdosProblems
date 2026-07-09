# Gap#1 Grounding Map (Codex, 2026-07-09)

This note records the current source-level boundary between the compiled wall
bookkeeping and the still-missing graph-side grounding.  It is intentionally a
map, not a new Lean API: the concrete escape surface should be defined only
after Claude/Fable agree on the exact forced-escape semantics.

## Compiled Wall Consumers

The R3 wall stack currently consumes three graph-side obligations through the
abstract `ClosedShore.AbstractEscapeQuotient` interface.

- `ClosedShore.PositiveRootBlockClosedExtraction Q`
  in `Erdos23Delta0/ClosedShoreExtraction.lean`.
  This is the accepted replacement for the false W2 separability statement:
  a closed deficient exposed-port set with at least two legal components must
  contain a proper closed positive-deficiency root block.

- `ClosedShore.ClosedWeightedHallCompleteness Q`
  in `Erdos23Delta0/ClosedWeightedHall.lean`.
  This packages the weighted Hall failure as a minimal full-escape-closed
  deficient shore.

- `ClosedShore.ClosedRootCutViolatesD1 Allowed Q d Z.portLoad`
  in `Erdos23Delta0/BankedWallW3Skeleton.lean`.
  This is the closed-cut exchange identity: the unique-root closed shore
  produces an allowed cut violating D1.

The compiled skeleton theorem is:

```lean
ClosedShore.noStrictRestrictedDual_of_closedHall_and_exchange
```

It is bookkeeping once the three obligations above are supplied.

## Accepted Wall Output Interface

The downstream global ledger interface is now compiled in
`Gamma/FullBankToLengthSurplusCharge.lean`.  A successful wall construction
should ultimately provide:

```lean
P : Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage G c rows
hP : P.Checked
```

The compiled consequences are:

```lean
FullBankGlobalPackage.fullBankGlobalPackage_sound hP
FullBankGlobalPackage.gammaUpper_from_fullBankGlobalPackage hP
Gamma.FullBankChargeCertProvider.chargeCertProviderOfFullBankLedger_ok hP
```

Thus the concrete forced-escape closure should either instantiate the three
`ClosedShore` obligations that W3 consumes, or directly populate the checked
full-bank package fields: local demand/cap views, token no-double-spend,
component reserve identities, and the final superadditivity reserve.

## Concrete Cage Surface Already Present

The accepted T8 concrete cage lane currently provides the pure-lens side:

- `ConcreteCage.AmbientCage`
- `ConcreteCage.BankFrame`
- `ConcreteCage.ProperRelative`
- `ConcreteCage.restrict` / `ConcreteCage.restrictCompl`
- `ConcreteCage.StrongPureLensAtomSplit`
- `ConcreteCage.concretePureLensCageSplit`
- `ConcreteCage.ledgerSep_of_concretePureLensCageSplit`

After cleanup, the six `Ell5/ConcreteCage/*.lean` modules have no remaining
forbidden proof-token hits under the standard scanner.

Narrow verification after cleanup:

- `PureLensSplit.lean` elaboration: `rc=0`
  (`tmp/codex_t8_purelenssplit_cleanup_build2.txt`).
- Axiom probe for `concretePureLensCageSplit` and
  `ledgerSep_of_concretePureLensCageSplit`: only
  `[propext, Classical.choice, Quot.sound]`
  (`tmp/codex_t8_cleanup_axiom_probe2.txt`).

## Missing Concrete Grounding Surface

Source search found no Lean definition of a concrete
`ForcedEll5EscapeStep`.  The name appears only in R3 comments/writeups as the
intended graph-side closure step.

Therefore the current missing interface is not another pure-cage bookkeeping
lemma.  It is the concrete forced-escape closure model that can instantiate
`AbstractEscapeQuotient` and prove, at minimum:

```lean
ClosedShore.PositiveRootBlockClosedExtraction Q
```

or an equivalent root-locality theorem strong enough to derive it.

The concrete surface should connect forced ell=5 escape steps to:

- exposed off-support ports,
- bank/legal sinks,
- root components in the `PortHall` legal-incidence graph,
- the already compiled `ConcreteCage` support/surplus/bank objects,
- and the `FullBankGlobalPackage.Checked` ledger fields above.

## Next Exact Target

The next useful theorem statement should be one of:

1. A direct concrete extraction theorem:

```lean
theorem positiveRootBlockClosedExtraction_of_forcedEll5Escape
    (data : ConcreteForcedEll5EscapeData ...)
    (hLocal : RootLocalForcedEscape data) :
    ClosedShore.PositiveRootBlockClosedExtraction data.abstractQuotient
```

2. Or the more primitive root-local forced-step theorem that R3 describes:
new ports created by one forced ell=5 escape step share a legal bank sink with
an already exposed port unless one of the already-ruled-out support outlets
fires.

The source audit says this is the current wall hook.  It should be sent to
Claude/Fable as the next grounding question rather than re-attacking bare SSE
or strict-lens statements.
