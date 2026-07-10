# GPT-Pro Forced-Escape Quotient Distillation, 2026-07-09

Source answer:

```text
problems/23/writeup/CODEX_GPTPRO_FORCED_ESCAPE_ANSWER_20260709.md
```

This note extracts the usable gates from the GPT-Pro answer and compares them
to the current Lean source surface. It is not a proof claim.

## Key Proposal

Instantiate the W3 `AbstractEscapeQuotient` with an atom-level quotient, not a
root-block quotient and not a bank-component quotient.

The proposed abstract shape is:

```lean
structure HornRule (α : Type*) [DecidableEq α] where
  pre  : Finset α
  post : α

def HornClosed (R : Finset (HornRule α)) (U : Finset α) : Prop :=
  ∀ r, r ∈ R -> r.pre ⊆ U -> r.post ∈ U
```

The forced escape closure is the least Horn-closed superset of a shore.  The
closure object should be converted into:

```lean
Q : AbstractEscapeQuotient I
```

with:

- `QComp` = real forced-ell=5 cage/atom components;
- `fullClosure` = Horn closure under forced-escape rules;
- `exposedPorts U` = base atom/shore port exposure plus bank exposure, but not
  bank components as quotient vertices.

GPT-Pro's explicit warning:

- do not use `QComp := RootBlock`;
- do not put bank components into `QComp`;
- do not use unary-only closure unless the real forced-escape rules are unary;
- prove Hall only for `fullClosure`-closed shores;
- do not omit bank exposure from `exposedPorts`.

## Real API Mismatch

The current concrete cage surface is graph-side:

```lean
AmbientCage (G : SimpleGraph V) (c : Distances.Cut V)
Atom H := Ell5AtomBase.Ell5Atom H
atomSupportedOn : Atom H -> Finset V -> Prop
BankFrame
```

The W3 skeleton is wall-LP-side:

```lean
AbstractEscapeQuotient (I : BankedWallLP)
ClosedWeightedHallCompleteness Q
PositiveRootBlockClosedExtraction Q
ClosedRootCutViolatesD1 Allowed Q d Z.portLoad
```

Therefore the first missing adapter is not merely a closure definition.  We
need a graph/cage-to-`BankedWallLP` surface that identifies:

```text
QComp
I.Port
I.Cut
legal root
supportedOn c r
bankExposes c p
Allowed cut
```

The current `Ell5/ConcreteCage/*` modules do not expose these objects.  They
prove pure-lens bank/surplus bookkeeping only after graph-heavy hypotheses are
supplied.

## Exact Gates Suggested By GPT-Pro

### Gate 1: root-fiber closure

For each root block, the fiber of atoms supported by that block must be closed
under the Horn rules:

```lean
∀ b : RootBlock, HornClosed rules (rootFiber b)
```

Failure diagnostic:

```lean
badRootFiberRules :
  Finset (RootBlock × HornRule QComp)
```

Nonempty `badRootFiberRules` means the failing input is
`PositiveRootBlockClosedExtraction`: the closure imports a different legal
root block.

### Gate 2: atom-root purity

No quotient atom may be supported by two legal roots from different root blocks:

```lean
∀ c r s (hr : legalRoot r) (hs : legalRoot s),
  supportedOn c r ->
  supportedOn c s ->
  rootBlockOf r hr = rootBlockOf s hs
```

Failure diagnostic:

```lean
∃ c r s, supportedOn c r ∧ supportedOn c s ∧
  rootBlockOf r ≠ rootBlockOf s
```

If this fails, raw cage atoms are too coarse or the W3 route cannot prove
root-locality as currently stated.

### Gate 3: closed weighted Hall

For every closure-fixed shore:

```lean
U ∈ closedRows
```

construct a banked relaxed cover:

```lean
Ell5FullBankRelaxedCover K
  (roots supported by U)
  (exposedPorts U)
```

and prove its rational validity. This is where `FullBankHall` and surviving
SSE-like facts belong. Scalar Hall is not enough.

Failure diagnostic:

```lean
badClosedHallRows : Finset (Finset QComp)
```

Nonempty means `ClosedWeightedHallCompleteness` fails for the proposed
quotient/closure.

### Gate 4: closed-shore cut extraction / D1 exchange

For every closure-fixed `U`, construct an allowed cut:

```lean
cutOf U : I.Cut
Allowed (cutOf U)
CutPorts (cutOf U) = exposedPorts U
CutRoots (cutOf U) = roots supported by U
D1CutExpr d portLoad (cutOf U) = ClosedRowExpr Q d portLoad U
```

This is the concrete content needed to instantiate:

```lean
ClosedRootCutViolatesD1 Allowed Q d portLoad
```

Failure diagnostic:

```lean
badClosedShoreCutRow :
  ∃ U, fullClosure U = U ∧
    ¬ ∃ C : I.Cut,
      Allowed C ∧ CutPorts C = exposedPorts U ∧ CutRoots C = roots U
```

### Gate 5: finite rational almost-squeeze source

Keep the finite rational Farkas source separate:

```lean
∀ {d : Dual I},
  d.RestrictedChecked Allowed ->
  d.StrictGap ->
  DualAlmostSqueeze I Allowed d
```

Failure modes:

- negative multiplier;
- non-allowed support cut;
- root coefficient mismatch;
- port coefficient mismatch;
- objective squeeze mismatch.

## Consumer Theorem Shape

If the above gates are supplied, the current W3 skeleton consumes them as:

```lean
noStrictRestrictedDual_of_closedHall_and_exchange
  hd Z
  (forcedEll5_closedWeightedHallCompleteness S hHall)
  (forcedEll5_positiveRootBlockClosedExtraction S hFiber hAtomPure)
  (forcedEll5_closedRootCutViolatesD1 S hCut)
```

This matches the Codex wrapper:

```lean
ForcedEscapeWallInputs
ForcedEscapeWallCert
```

## Next Exact-Test Request

Before writing more Lean, test whether the current real cage/support data can
even supply the proposal's four primitives:

```text
QComp, supportedOn c r, bankExposes c p, rootBlockOf r
```

If yes, build the three finite diagnostics:

```text
badRootFiberRules
badMixedRootAtoms
badClosedHallRows
```

on the current census/witness battery.  If any is nonempty, report the exact
row/model and which W3 input fails.

If no, the immediate task is not proving root-locality; it is defining the
graph/cage-to-BankedWallLP adapter surface.
