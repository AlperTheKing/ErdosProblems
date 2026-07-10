# Prompt: Concrete Forced-Escape Quotient for Gap#1

We are closing Erdős Problem #23 in Lean. The chart batch is accepted; the
remaining wall is Gap#1:

```text
FullBankHall / ShortestSupportExpansion / Ell5FullBankRelaxedCover_exists.
```

Bare SSE and old local switch/lens routes are refuted except as auxiliary
sublemmas. The active route is the banked relaxed cut-cover / external slack
bank / no-Farkas-dual route.

## Current compiled Lean skeleton

The relevant modules are:

```lean
Erdos23Delta0.BankedWallLP
Erdos23Delta0.BankedWallLPRestricted
Erdos23Delta0.BankedWallRoutingFailure
Erdos23Delta0.ClosedShoreExtraction
Erdos23Delta0.ClosedWeightedHall
Erdos23Delta0.BankedWallW3Skeleton
```

The abstract consumption theorem is:

```lean
theorem noStrictRestrictedDual_of_closedHall_and_exchange
    {Allowed : I.Cut -> Prop} {Q : AbstractEscapeQuotient I} {d : Dual I}
    (hd : d.RestrictedChecked Allowed)
    (Z : DualAlmostSqueeze I Allowed d)
    (hHall : ClosedWeightedHallCompleteness Q)
    (hExtract : PositiveRootBlockClosedExtraction Q)
    (hExchange : ClosedRootCutViolatesD1 Allowed Q d Z.portLoad) :
    ¬ d.StrictGap
```

Thus the remaining graph-side bridge must supply:

```lean
ClosedWeightedHallCompleteness Q
PositiveRootBlockClosedExtraction Q
ClosedRootCutViolatesD1 Allowed Q d Z.portLoad
```

for the concrete forced-ell=5 escape closure, plus the finite rational
Farkas/almost-squeeze source that constructs `DualAlmostSqueeze`.

## Existing abstract quotient interface

```lean
structure AbstractEscapeQuotient (I : BankedWallLP) where
  QComp : Type
  qDecEq : DecidableEq QComp
  qFintype : Fintype QComp
  fullClosure : Finset QComp -> Finset QComp
  exposedPorts : Finset QComp -> Finset I.Port
  closure_extensive : forall U, U <= fullClosure U
  closure_idempotent : forall U, fullClosure (fullClosure U) = fullClosure U
  closure_monotone : forall U V, U <= V -> fullClosure U <= fullClosure V
```

Static search of the current source tree found no concrete
`ForcedEll5EscapeStep` / forced-escape instantiation of this quotient.

## Concrete cage modules are not enough

T8 modules exist and compile:

```lean
Erdos23Delta0.Ell5.ConcreteCage.Basic
Erdos23Delta0.Ell5.ConcreteCage.Bank
Erdos23Delta0.Ell5.ConcreteCage.Proper
Erdos23Delta0.Ell5.ConcreteCage.Restrict
Erdos23Delta0.Ell5.ConcreteCage.PureSplit
Erdos23Delta0.Ell5.ConcreteCage.PureLensSplit
```

They define `AmbientCage`, `atomSupportedOn`, `Bank`, `Balance`,
`StrongPureLensAtomSplit`, and `concretePureLensCageSplit`. They package
pure-lens split bookkeeping once graph-heavy hypotheses are supplied. They do
not instantiate `AbstractEscapeQuotient` and do not prove root-locality or
closed-Hall completeness.

## Requested output

Please give a concrete route, in Lean-facing terms, for the missing forced
escape quotient bridge. Do not propose bare SSE, scalar Hall, or local
strict-lens-only arguments; those have been refuted.

Deliver one of the following:

### Route A: concrete quotient construction

Define, using the existing cage/atom/support surfaces if possible:

1. the concrete quotient component type `QComp`;
2. the exposure map `exposedPorts : Finset QComp -> Finset I.Port`;
3. the forced-escape closure `fullClosure`;
4. proofs or exact finite gates for:
   - extensive,
   - monotone,
   - idempotent;
5. a Lean statement of `PositiveRootBlockClosedExtraction` for this concrete
   quotient, with the exact graph lemma that proves it.

The answer must specify which existing Lean objects represent:

```text
component, legal root, port, exposed port, forced escape, closed shore.
```

### Route B: bypass quotient

Give a theorem that directly implies the W3 skeleton's conclusion

```lean
¬ d.StrictGap
```

from `d.RestrictedChecked Allowed`, `DualAlmostSqueeze`, and concrete cage
facts, without going through `AbstractEscapeQuotient`. It must still explain
how weighted routing failures produce an allowed cut violating D1.

### Route C: falsifier

Produce an exact-testable obstruction showing the current W3 route cannot
prove root-locality as stated. The falsifier must name which input fails:

```text
ClosedWeightedHallCompleteness
PositiveRootBlockClosedExtraction
ClosedRootCutViolatesD1
finite-Farkas/almost-squeeze source
```

and should include a finite model / gate specification that can be checked by
Fraction arithmetic or a small Lean object.

## Acceptance criteria

The answer should be specific enough to become one or more Lean modules. Avoid
new invented APIs unless you define how they map to the current objects. A
usable answer contains:

```text
new definitions,
new theorem statements,
which existing theorem consumes them,
exact finite gates or proof outline,
and known failure modes.
```

The key question: how do we instantiate the abstract closed-shore/root-locality
machinery on the real forced-ell=5 cage closure so that a strict restricted
dual yields an allowed cut D1 violation?
