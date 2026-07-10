# Gap#1 Bridge Definition Of Done, 2026-07-09

This note is a coordination artifact.  It records the exact theorem inputs that
must become real before the Branch-B / delta=0 wall can be counted as closed.
It is deliberately conservative: compiled downstream bookkeeping does not count
as proof of these graph-side facts.

## Accepted downstream state

The following lanes are accepted as bookkeeping or certificate plumbing unless
a later verifier contradicts them.

* v108 chart ledger: `108/108`, `0 failures`, `all_verified=true`.
* O14 sharded payload emitter: Chart000 pilot accepted; scaled ChartPayloads are
  frozen while Claude's wave re-gate runs.
* RowPartition guardrail: EQODL1 dispatch is component-all-length-5, and mixed
  components go wholesale to Branch-B.
* `Gamma/FullBankToLengthSurplusCharge.lean`: compiled wall-output interface;
  the wall must construct a checked `FullBankGlobalPackage`.
* T8 `Ell5/ConcreteCage/*`: pure-lens cage bookkeeping and ledger separation.

## The actual wall

The active consumption skeleton is:

```lean
Erdos23Delta0.Wall.ClosedShore.noStrictRestrictedDual_of_closedHall_and_exchange
Erdos23Delta0.Wall.ClosedShore.noStrictDual_of_closedHall_and_exchange
```

The packaging seam added by Codex is:

```lean
Erdos23Delta0.Wall.ClosedShore.ForcedEscapeWallInputs
Erdos23Delta0.Wall.ClosedShore.ForcedEscapeWallCert
Erdos23Delta0.Wall.RestrictedSqueezeWallCert
Erdos23Delta0.Wall.EndgameWallCert
```

For a concrete forced-escape closure, the wall is closed only when the following
fields are constructed without new axioms or `sorry`.  Equivalently, construct
a value of:

```lean
ForcedEscapeWallCert I
```

for the real banked wall LP instance.

There is also a direct bypass target:

```lean
RestrictedSqueezeWallCert I
```

This skips the closed-shore quotient/Hall/exchange layer, but then its
`squeezeOfStrict` field must directly construct a full `DualSqueeze` from every
strict restricted dual.

For final assembly, either route can now be packaged as:

```lean
EndgameWallCert I
```

and consumed through:

```lean
EndgameWallCert.noStrictDual
```

This selector is bookkeeping only.  It does not weaken the hard obligations
listed below.

## Required theorem inputs

### 1. Concrete quotient

Construct a concrete:

```lean
Q : AbstractEscapeQuotient I
```

for the real forced-ell=5 escape / cage closure.  Its `QComp`, `fullClosure`,
and `exposedPorts` must be the same objects used by the closed-Hall and
exchange proofs.

Done means:

* `closure_extensive`, `closure_idempotent`, and `closure_monotone` compile.
* The quotient is connected to the real `BankedWallLP` ports/cuts, not an
  abstract toy model.

### 2. Closed weighted Hall completeness

Prove:

```lean
ClosedWeightedHallCompleteness Q
```

for the same concrete quotient.

Done means:

* The proof is for closed exposed-port sets of `Q.fullClosure`.
* It does not use a scalar Hall surrogate that has already been falsified.

### 3. Positive root-block extraction

Prove:

```lean
PositiveRootBlockClosedExtraction Q
```

for the same concrete quotient.

Done means:

* Every closed deficient exposed-port set with at least two legal root
  components yields a proper closed subshore on one positive-deficiency root
  block.
* This is the operational root-locality lemma.  It is not supplied by the
  current pure-lens cage split modules.

### 4. Closed-root exchange identity

For the concrete allowed cut family, prove:

```lean
∀ {d : Dual I} (Z : DualAlmostSqueeze I Allowed d),
  ClosedRootCutViolatesD1 Allowed Q d Z.portLoad
```

Done means:

* The produced cut is in `Allowed`.
* It violates restricted D1 in the exact form
  `cutBeta d X + cutGamma d X < cutAlpha d X`.
* The proof uses the same closure/exposure objects as items 1-3.

### 5. Finite rational Farkas / almost-squeeze source

Supply the source that produces the required `DualAlmostSqueeze` object from the
finite wall package:

```lean
∀ {d : Dual I},
  d.RestrictedChecked Allowed →
    d.StrictGap →
      DualAlmostSqueeze I Allowed d
```

Done means:

* The equivalence is exact rational, not floating or empirical.
* The source plugs into `ForcedEscapeWallCert.noStrictDual` or
  `noStrictRestrictedDual` without changing the wall statement.

## Non-closure items

The following facts are useful but are not sufficient by themselves:

* pure-lens ledger separation;
* bare shortest-support expansion;
* scalar Hall / max-flow conditions;
* strict-lens existence without banked relaxed cover data;
* O14 chart payload success alone.

## Route choice

Either of the following is sufficient:

1. Closed-shore route: construct `ForcedEscapeWallCert I`.
2. Direct restricted-Farkas route: construct `RestrictedSqueezeWallCert I`.

The closed-shore route has more graph structure but more bridge lemmas.  The
direct route has a smaller consumer theorem but a stronger finite squeeze
source.  Both must use the real allowed cut family for the banked wall LP.

## Status

As of this note, no current source file instantiates `AbstractEscapeQuotient`
for the real forced-escape closure.  Therefore Gap#1 remains a genuine math
obligation even though the certificate and bookkeeping lanes are substantially
advanced.
