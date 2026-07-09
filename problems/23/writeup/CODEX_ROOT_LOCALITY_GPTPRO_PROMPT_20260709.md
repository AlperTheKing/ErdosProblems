# GPT-Pro / Fable prompt: root-local forced ell=5 escape

We are finishing the full Erdos Problem #23 Lean proof.  Do not re-propose
bare SSE, strict-lens-only arguments, scalar Hall, or old terminal-switch
routes: those have been exact-refuted or reduced to auxiliary bookkeeping.

The current wall is the graph-side grounding of the banked relaxed cut-cover
route.  The bookkeeping is already compiled.  The remaining target is a
concrete forced ell=5 escape / root-locality theorem strong enough to feed the
compiled W3 skeleton.

## Existing compiled consumer surface

The Lean wall stack consumes an abstract escape quotient:

```lean
ClosedShore.AbstractEscapeQuotient I
```

and needs these three graph-side obligations:

```lean
ClosedShore.ClosedWeightedHallCompleteness Q
ClosedShore.PositiveRootBlockClosedExtraction Q
ClosedShore.ClosedRootCutViolatesD1 Allowed Q d Z.portLoad
```

The downstream theorem already compiles:

```lean
ClosedShore.noStrictRestrictedDual_of_closedHall_and_exchange
```

So the proof goal is not another scalar inequality.  It is to construct or
derive one of the missing graph-side obligations, especially
`PositiveRootBlockClosedExtraction`.

## Current accepted wall output interface

Spec-1 is now the compiled output interface for the wall.  The wall should
produce:

```lean
P : Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage G c rows
hP : P.Checked
```

The existing compiled route then gives:

```lean
Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage.fullBankGlobalPackage_sound hP
Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage.gammaUpper_from_fullBankGlobalPackage hP
Gamma.FullBankChargeCertProvider.chargeCertProviderOfFullBankLedger_ok hP
```

So the forced-escape/root-locality theorem should either feed the three
`ClosedShore` obligations consumed by W3, or directly supply the checked
full-bank package fields.  There is no eta-cap token in the accepted package:
the spendable kinds are door, vertexSlack, c5Base, and prune, plus reserve
identities.

## Exact Lean definitions already present

From `ClosedShoreExtraction.lean`:

```lean
structure AbstractEscapeQuotient (I : BankedWallLP) where
  QComp : Type
  qDecEq : DecidableEq QComp
  qFintype : Fintype QComp
  fullClosure : Finset QComp -> Finset QComp
  exposedPorts : Finset QComp -> Finset I.Port
  closure_extensive : forall U, U subset fullClosure U
  closure_idempotent : forall U, fullClosure (fullClosure U) = fullClosure U
  closure_monotone : forall U V, U subset V -> fullClosure U subset fullClosure V
```

```lean
def ClosedPortSet (Q : AbstractEscapeQuotient I) (P : Finset I.Port) : Prop :=
  exists U : Finset Q.QComp, Q.fullClosure U = U and Q.exposedPorts U = P
```

```lean
def MinimalClosedDeficient (Q : AbstractEscapeQuotient I) (L : I.Port -> Rat)
    (P : Finset I.Port) : Prop :=
  ClosedPortSet Q P and HallDeficient I L P and
    forall P' : Finset I.Port, ClosedPortSet Q P' -> P' properSubset P ->
      deficiencyQ I L P' <= 0
```

```lean
def PositiveRootBlockClosedExtraction (Q : AbstractEscapeQuotient I) : Prop :=
  forall (L : I.Port -> Rat) (U : Finset Q.QComp), Q.fullClosure U = U ->
    forall D : LegalComponentPartition I (Q.exposedPorts U),
      HallDeficient I L (Q.exposedPorts U) -> 2 <= Fintype.card D.K ->
        exists (k : D.K) (Ur : Finset Q.QComp),
          Q.fullClosure Ur = Ur and Q.exposedPorts Ur = D.ports k and
            D.ports k properSubset Q.exposedPorts U and HallDeficient I L (D.ports k)
```

This is the accepted replacement for false W2/root-block separability.

## Why old W2 is false

The abstraction-level counterexample has two quotient components A,B, ports
pA,pB, sinks sA,sB, disjoint legal arcs pA--sA and pB--sB, and closure
`cl(U) = {A,B}` if `A in U` else `U`.  The full closed shore `{A,B}` is
minimal deficient with two legal roots, but no closed shore exposes `{pA}`.
Thus a closure step can cross legal roots unless the real forced ell=5 escape
geometry proves root-locality.

Therefore the theorem must use the concrete forced ell=5 escape relation, not
only abstract closure laws.

## Concrete surface already available

The T8 concrete cage bookkeeping exists and compiles:

```lean
ConcreteCage.AmbientCage
ConcreteCage.BankFrame
ConcreteCage.ProperRelative
ConcreteCage.restrict
ConcreteCage.restrictCompl
ConcreteCage.StrongPureLensAtomSplit
ConcreteCage.concretePureLensCageSplit
ConcreteCage.ledgerSep_of_concretePureLensCageSplit
```

This closes the pure-lens ledger split but does not yet define the real
forced-escape closure, exposed off-support ports, or legal bank-sink roots.

## Request

Produce the cleanest theorem shape and proof route for the concrete forced
ell=5 escape closure.  Prefer a statement that can be compiled with the
existing surfaces above.

Option A, direct:

```lean
theorem positiveRootBlockClosedExtraction_of_forcedEll5Escape
    (data : ConcreteForcedEll5EscapeData ...)
    (hLocal : RootLocalForcedEscape data) :
    ClosedShore.PositiveRootBlockClosedExtraction data.abstractQuotient
```

Option B, primitive:

Define the one-step forced ell=5 escape relation and prove:

```text
If one forced ell=5 escape step adds a new exposed off-support port, then the
new port shares a legal bank sink with an already exposed port, unless one of
the already-ruled-out support outlets fires:

1. private short edge;
2. support size = 5;
3. pair-union support size < 5;
4. proper full-closure Hall violator / proper cage descendant.
```

Then give the short bridge from that primitive theorem to:

```lean
ClosedShore.PositiveRootBlockClosedExtraction Q
```

## Required output

Be concrete.  State:

1. What is `QComp` for the real quotient?
2. What is `fullClosure`?
3. What is `exposedPorts`?
4. What exactly is one forced ell=5 escape step?
5. What are the legal bank sinks used by the PortHall legal-incidence graph?
6. How do newly exposed ports inherit/share a legal root?
7. Which existing ConcreteCage / Ell5 support objects are used?
8. Which theorem should Codex formalize first?
9. How does it feed `FullBankGlobalPackage.Checked`, especially no-double-spend,
   component reserve identities, and the final component residual bank?

The answer should be exact-testable: either a Lean theorem skeleton matching
existing names, or a finite checker condition that can be run on the current
census/falsifier suite before formalization.
