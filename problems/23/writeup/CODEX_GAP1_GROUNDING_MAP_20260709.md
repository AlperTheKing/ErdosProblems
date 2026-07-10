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

## Later Source Audit: W3 Is Now a Three-Hypothesis Shell

A later source pass found the R3 bookkeeping split further along than the
original note assumed.  The following modules are present and source-level
clean under the standard forbidden-token scan:

- `BankedWallRoutingFailure.lean`:
  `strictRestrictedDual_gives_weightedRoutingFailure`.
- `ClosedWeightedHall.lean`:
  `ClosedWeightedHallCompleteness` and
  `uniqueRoot_of_closedWeightedHallCompleteness`.
- `BankedWallW3Skeleton.lean`:
  `ClosedRootCutViolatesD1`,
  `noStrictRestrictedDual_of_closedHall_and_exchange`, and
  `noStrictDual_of_closedHall_and_exchange`.
- `BankedWallLPRestricted.lean`:
  restricted-D1 checker and restricted squeeze soundness.

Thus the current abstract wall is exactly:

```lean
ClosedWeightedHallCompleteness Q
PositiveRootBlockClosedExtraction Q
ClosedRootCutViolatesD1 Allowed Q d Z.portLoad
```

together with an allowed almost-squeeze `Z`.  The first two are graph/closure
grounding statements.  The third is the closed-root cut exchange identity:
given the unique-root closed deficient shore, produce an allowed cut whose D1
inequality is violated.

The downstream `Ell5FullBankInterface` side is also already packaged:

```lean
FullBankRelaxedCoverCert
bankedCutDomination_of_cert
no_dualCert_of_cert
Ell5FullBankHall.hall_bound_of_fullBank_cert
```

So the remaining proof wall should not be described as a generic LP or Hall
problem.  It is the concrete forced-escape/root-locality theorem plus the
closed-root exchange identity needed to feed the already compiled W3 shell, or
an equivalent direct construction of `FullBankRelaxedCoverCert` /
`FullBankGlobalPackage.Checked`.

## Source-Level Status After 2026-07-09 Evening Poll

The live Lean files make the remaining wall especially explicit.

`BankedWallRoutingFailure.lean` proves:

```lean
strictRestrictedDual_gives_weightedRoutingFailure :
  d.RestrictedChecked Allowed ->
  DualAlmostSqueeze I Allowed d ->
  d.StrictGap ->
  WeightedRoutingFailure d Z.portLoad
```

This is pure algebraic bookkeeping: a strict restricted dual plus an allowed
almost-squeeze creates a weighted routing failure.

`ClosedWeightedHall.lean` then **defines**, but does not prove from graph
geometry:

```lean
def ClosedWeightedHallCompleteness (Q : AbstractEscapeQuotient I) : Prop :=
  forall {d : Dual I} {L : I.Port -> Rat},
    WeightedRoutingFailure d L ->
      exists U : Finset Q.QComp,
        Q.fullClosure U = U /\
          MinimalClosedDeficient Q L (Q.exposedPorts U)
```

and proves only the consequence:

```lean
uniqueRoot_of_closedWeightedHallCompleteness :
  ClosedWeightedHallCompleteness Q ->
  PositiveRootBlockClosedExtraction Q ->
  WeightedRoutingFailure d L ->
  exists U, Q.fullClosure U = U /\
    MinimalClosedDeficient Q L (Q.exposedPorts U) /\
    forall D : LegalComponentPartition I (Q.exposedPorts U),
      Fintype.card D.K = 1
```

`ClosedShoreExtraction.lean` likewise defines the second hard graph
obligation:

```lean
def PositiveRootBlockClosedExtraction (Q : AbstractEscapeQuotient I) : Prop :=
  forall (L : I.Port -> Rat) (U : Finset Q.QComp), Q.fullClosure U = U ->
    forall D : LegalComponentPartition I (Q.exposedPorts U),
      HallDeficient I L (Q.exposedPorts U) ->
      2 <= Fintype.card D.K ->
        exists (k : D.K) (Ur : Finset Q.QComp),
          Q.fullClosure Ur = Ur /\
          Q.exposedPorts Ur = D.ports k /\
          D.ports k < Q.exposedPorts U /\
          HallDeficient I L (D.ports k)
```

and proves:

```lean
minimalClosedDeficient_has_unique_root_of_positiveExtraction :
  PositiveRootBlockClosedExtraction Q ->
  MinimalClosedDeficient Q L (Q.exposedPorts U) ->
  forall D : LegalComponentPartition I (Q.exposedPorts U),
    Fintype.card D.K = 1
```

Finally, `BankedWallW3Skeleton.lean` defines the third hard exchange
obligation:

```lean
def ClosedRootCutViolatesD1
    (Allowed : I.Cut -> Prop) (Q : AbstractEscapeQuotient I)
    (d : Dual I) (L : I.Port -> Rat) : Prop :=
  forall U : Finset Q.QComp,
    Q.fullClosure U = U ->
      MinimalClosedDeficient Q L (Q.exposedPorts U) ->
        (forall D : LegalComponentPartition I (Q.exposedPorts U),
          Fintype.card D.K = 1) ->
          exists X : I.Cut,
            Allowed X /\ cutBeta d X + cutGamma d X < cutAlpha d X
```

The compiled W3 theorem is:

```lean
noStrictRestrictedDual_of_closedHall_and_exchange :
  d.RestrictedChecked Allowed ->
  DualAlmostSqueeze I Allowed d ->
  ClosedWeightedHallCompleteness Q ->
  PositiveRootBlockClosedExtraction Q ->
  ClosedRootCutViolatesD1 Allowed Q d Z.portLoad ->
  not d.StrictGap
```

Thus any proposed Gap#1 closure must produce exactly one of the following
verifiable deliverables:

1. instantiate `AbstractEscapeQuotient` for the concrete forced-ell=5 closure
   and prove the three displayed hard obligations; or
2. bypass W3 by directly constructing a checked `FullBankGlobalPackage` /
   `FullBankRelaxedCoverCert`, including the same closed-Hall and no
   double-spend content internally.

The current `Gamma/FullBankChargeCertProvider.lean` is downstream-only.  It
extracts a typed `LengthSurplusChargeCertV2` from an already checked
`FullBankGlobalPackage`; it does not construct that package.  Therefore it
should not be counted as evidence that Gap#1 is closed.

## Additional Source Audit: Restricted-Farkas Iff Is Not Present

The current source tree contains the following Farkas/dual interfaces:

- `BankedWallLP.noStrictDual_of_primal`: a feasible primal `Primal I` refutes
  every strict checked dual.
- `BankedWallLPRestricted.Dual.Checked.restrict` and
  `BankedWallLPRestricted.noStrictRestrictedDual_of_dualSqueeze`: restricted-D1
  variants of the same algebra.
- `BankedWallRoutingFailure.strictRestrictedDual_gives_weightedRoutingFailure`:
  a strict restricted dual plus an allowed almost-squeeze gives a weighted
  routing failure.
- `BankedWallW3Skeleton.noStrictRestrictedDual_of_closedHall_and_exchange`:
  closed-Hall + positive extraction + exchange kill that strict dual.

Source search found no compiled theorem named or shaped like:

```lean
dualSqueeze_exists_iff_no_restrictedStrict
```

or a full finite-rational Farkas equivalence for the restricted allowed-cut
system. Consequently the current wall is not yet a complete no-dual theorem.
It still needs one of the following exact bridges:

1. a finite rational Farkas theorem producing `DualAlmostSqueeze I Allowed d`
   for every relevant checked dual, plus the W3 graph obligations; or
2. a direct primal/package construction (`Primal I`, `FullBankRelaxedCoverCert`,
   or `FullBankGlobalPackage.Checked`) that bypasses restricted duals.

This matters for planning: proving only the three closed-shore obligations does
not by itself construct the wall unless the allowed almost-squeeze source is
also supplied. Conversely, a direct checked full-bank package can close the wall
without exposing the dual obstruction explicitly.

## Current Smallest Complete Gap#1 Deliverable

A complete proof object for Gap#1 must now provide **one** of these two
deliverables.

### Deliverable A: W3 + restricted-Farkas route

For each concrete forced-ell=5 wall instance, provide:

```lean
Q : ClosedShore.AbstractEscapeQuotient I
Allowed : I.Cut -> Prop
```

and prove:

```lean
ClosedShore.ClosedWeightedHallCompleteness Q
ClosedShore.PositiveRootBlockClosedExtraction Q
ClosedShore.ClosedRootCutViolatesD1 Allowed Q d Z.portLoad
```

for every relevant checked dual `d` and almost-squeeze `Z`, together with the
missing finite-rational bridge that supplies such a `Z` for every strict
restricted dual.

### Deliverable B: direct checked package route

Construct directly:

```lean
P : Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage G c rows
hP : P.Checked
```

or equivalently:

```lean
cert : Ell5FullBankInterface.FullBankRelaxedCoverCert S F O J K sep dB inc kap
```

with enough bookkeeping to feed
`FullBankGlobalPackage.gammaUpper_from_fullBankGlobalPackage` or the
`LengthSurplusChargeCertV2` provider. This route must still encode the same
no-double-spend, reserve, and closed-Hall content; it just avoids naming the
dual obstruction explicitly.
