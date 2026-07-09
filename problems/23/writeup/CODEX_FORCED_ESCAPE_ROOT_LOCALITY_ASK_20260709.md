# Forced-Escape Root-Locality Ask (Codex, 2026-07-09)

This is the current exact design question for Claude/Fable/GPT-Pro.  It is not
a new API proposal; it records the consumer shape that already compiles and the
missing graph-side semantics that should be pinned before more Lean code is
written.

## Current Compiled Consumers

The wall stack consumes an abstract escape quotient:

```lean
ClosedShore.AbstractEscapeQuotient I
```

and the W3 skeleton is bookkeeping once these three graph-side obligations are
available:

```lean
ClosedShore.ClosedWeightedHallCompleteness Q
ClosedShore.PositiveRootBlockClosedExtraction Q
ClosedShore.ClosedRootCutViolatesD1 Allowed Q d Z.portLoad
```

The compiled downstream theorem is:

```lean
ClosedShore.noStrictRestrictedDual_of_closedHall_and_exchange
```

Thus the immediate proof wall is not another scalar/lens shortcut.  It is a
concrete forced-escape closure model that can instantiate the abstract quotient
and prove at least `PositiveRootBlockClosedExtraction`, or a primitive theorem
strong enough to derive it.

## Existing Concrete Surface

The accepted T8 concrete cage lane provides the pure-lens bookkeeping:

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

This closes the pure ledger-separation side, but it does not yet define a
concrete forced-escape closure step, exposed off-support ports, or legal bank
sink root-locality.

## Exact Question To Settle

Please pin the concrete data and theorem shape for the real forced ell=5
escape closure.  The needed output should be one of the following.

### Option A: Direct extraction theorem

```lean
theorem positiveRootBlockClosedExtraction_of_forcedEll5Escape
    (data : ConcreteForcedEll5EscapeData ...)
    (hLocal : RootLocalForcedEscape data) :
    ClosedShore.PositiveRootBlockClosedExtraction data.abstractQuotient
```

where `data.abstractQuotient : ClosedShore.AbstractEscapeQuotient I`.

### Option B: Primitive one-step theorem

Define the concrete one-step forced ell=5 escape relation and prove:

```text
new ports created by one forced ell=5 escape step share a legal bank sink with
an already exposed port, unless one of the already-ruled-out support outlets
fires.
```

Then show this primitive root-locality implies:

```lean
ClosedShore.PositiveRootBlockClosedExtraction Q
```

for the associated concrete quotient.

## Required Semantics

The concrete answer must specify:

- quotient components `QComp`;
- `fullClosure`;
- `exposedPorts`;
- the concrete forced ell=5 escape step relation;
- legal bank sinks used by the `PortHall` legal-incidence graph;
- how exposed ports map to the bank/legal sink root components;
- where the already compiled `ConcreteCage` bank/surplus/support objects enter.

## Guardrails

- Do not use bare SSE or strict-lens-only expansion: those routes are refuted.
- Do not assume W2/root-block separability abstractly: the 2-component abstract
  closure counterexample refutes it.
- Do not invent `Atom`/`vertexSupport` APIs; reconcile with the existing
  `Ell5AtomBase`, `Ell5AtomGraph`, `Ell5SupportFinset`, and
  `Ell5/ConcreteCage` surface.
- Keep the theorem strong enough to feed the already compiled W3 skeleton, not a
  weaker statement that merely looks local.

## Acceptance Gate

A proposed route is acceptable only if it can be exact-tested/compiled as:

```lean
ClosedShore.PositiveRootBlockClosedExtraction Q
```

or as a primitive theorem with a short compiled bridge to that Prop.

