# Gap#1 forced-escape surface audit, 2026-07-09

Purpose: pin the current R3/Gap#1 wall to actual compiled Lean names while
`O14/Generated/ChartPayloads` is frozen for the full wave gate.

## Current compiled wall skeleton

The non-payload chain builds and axiom-probes cleanly in
`tmp/claude_lean_o_base_v1`:

- `Erdos23Delta0.Gamma.FullBankChargeCertProvider`
- `Erdos23Delta0.BankedWallLPRestricted`
- `Erdos23Delta0.BankedWallRoutingFailure`
- `Erdos23Delta0.PortHallUncrossing`
- `Erdos23Delta0.ClosedShoreExtraction`
- `Erdos23Delta0.ClosedWeightedHall`
- `Erdos23Delta0.BankedWallW3Skeleton`

Probe file: `tmp/codex_nonpayload_axiom_probe.lean`.

Probe output: `tmp/codex_nonpayload_axiom_probe.txt`.

Allowed axioms only:

```text
propext, Classical.choice, Quot.sound
```

## Actual abstract target

The wall is abstracted by:

```lean
structure BankedWallLP where
  Cut : Type
  Atom : Type
  Short : Type
  Port : Type
  Sink : Type
  cov : Cut -> Atom -> Q
  useShort : Cut -> Short -> Q
  cutPort : Cut -> Port -> Q
  legal : Port -> Sink -> Prop
  cap : Sink -> Q
```

and:

```lean
structure AbstractEscapeQuotient (I : BankedWallLP) where
  QComp : Type
  fullClosure : Finset QComp -> Finset QComp
  exposedPorts : Finset QComp -> Finset I.Port
```

The remaining R3 hooks are exactly:

```lean
ClosedWeightedHallCompleteness Q
PositiveRootBlockClosedExtraction Q
ClosedRootCutViolatesD1 Allowed Q d L
```

with the W3 conclusion already compiled:

```lean
Erdos23Delta0.Wall.ClosedShore.noStrictDual_of_closedHall_and_exchange
```

## Current concrete graph surface

Search result:

```text
rg ForcedEll5EscapeStep problems/23/lean/Erdos23Delta0
```

finds no concrete API. The closest compiled concrete APIs are:

- `Ell5SupportFinset.geodesicSupport`
- `Ell5SupportFinset.Eshort`
- `Ell5SupportFinset.ell5_base_case_Eshort_of_ell`
- `Ell5AtomGraph.ell5_atom_of_badEdge`

These give real multi-geodesic support for ell=5 atoms, but they do not yet
define:

- forced escape steps,
- closure components over such steps,
- exposed bank ports of a closure shore,
- legal-root preservation/extraction for forced steps,
- the closed-root cut exchange identity.

## Minimal next Lean surface

Do not introduce source-level definitions under speculative names unless the
designer confirms them. The minimal statement surface should be one module that
connects existing concrete ell=5 support to the abstract R3 hooks.

Proposed module name:

```text
Erdos23Delta0.ForcedEll5EscapeBridge
```

Proposed contents:

1. A concrete-or-semi-concrete `ForcedEll5EscapeStep` structure parameterized by
   an existing `BankedWallLP I`, an ell=5 support edge or atom, and a closure
   shore.

2. A `FirstRootCrossing` predicate matching R3:

```lean
-- schematic
def FirstRootCrossing
    (Q : AbstractEscapeQuotient I)
    (Step : Type) ... : Prop := ...
```

3. The graph-side outlet hook, stated as the single real geometry theorem:

```lean
-- schematic
theorem firstRootCrossing_outlet
    (X : FirstRootCrossing ...) :
    PrivateShortEdge X.e
      \/ supportSize X.e = 5
      \/ (exists f, f <> X.e /\ supportUnionSize X.e f < 5)
      \/ ProperFullClosureHallViolator
```

4. A bookkeeping theorem deriving the abstract hook:

```lean
-- schematic target
theorem positiveRootBlockClosedExtraction_of_no_firstRootCrossingOutlet :
    PositiveRootBlockClosedExtraction Q
```

5. A bookkeeping theorem deriving the exchange hook:

```lean
-- schematic target
theorem closedRootCutViolatesD1_of_forcedEscapeExchange :
    ClosedRootCutViolatesD1 Allowed Q d L
```

## Exact blocker

The current Lean tree has the W3 algebra after the hooks, and concrete ell=5
geodesic support before the hooks. The missing layer is the forced-escape
closure model that maps concrete ell=5 support geometry into:

```lean
AbstractEscapeQuotient.fullClosure
AbstractEscapeQuotient.exposedPorts
BankedWallLP.cutPort
BankedWallLP.legal
```

This is the next object to obtain from Fable/Claude, or to introduce with their
approval.
