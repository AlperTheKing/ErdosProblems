# Root-Locality Surface Audit, 2026-07-09

This note records the current Lean source surface for Gap#1's root-locality /
closed-shore route. It is a coordination artifact, not a new theorem.

## Current abstract wall skeleton

The compiled W3 skeleton lives in:

```lean
Erdos23Delta0.BankedWallW3Skeleton
Erdos23Delta0.ClosedWeightedHall
Erdos23Delta0.ClosedShoreExtraction
```

The skeleton proves:

```lean
noStrictRestrictedDual_of_closedHall_and_exchange
noStrictDual_of_closedHall_and_exchange
uniqueRoot_of_closedWeightedHallCompleteness
minimalClosedDeficient_has_unique_root_of_positiveExtraction
```

but it consumes the following graph-side inputs as Props:

```lean
ClosedWeightedHallCompleteness Q
PositiveRootBlockClosedExtraction Q
ClosedRootCutViolatesD1 Allowed Q d Z.portLoad
```

The finite-Farkas / almost-squeeze source that supplies the `DualAlmostSqueeze`
object remains a separate required bridge.

## Abstract quotient status

`AbstractEscapeQuotient` is currently an abstract interface:

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

Static search of `problems/23/lean/Erdos23Delta0` found no concrete
`ForcedEll5EscapeStep` / forced-escape instantiation of this quotient. The
comments say the concrete cage model should instantiate `QComp`,
`fullClosure`, and `exposedPorts`, but that instantiation is not present in the
current source tree.

## ConcreteCage status

The T8 modules under:

```lean
Erdos23Delta0.Ell5.ConcreteCage.Basic
Erdos23Delta0.Ell5.ConcreteCage.Bank
Erdos23Delta0.Ell5.ConcreteCage.Proper
Erdos23Delta0.Ell5.ConcreteCage.Restrict
Erdos23Delta0.Ell5.ConcreteCage.PureSplit
Erdos23Delta0.Ell5.ConcreteCage.PureLensSplit
```

are pure-lens split bookkeeping. They define:

```lean
AmbientCage
atomSupportedOn
Bank
Balance
StrongPureLensAtomSplit
concretePureLensCageSplit
ledgerSep_of_concretePureLensCageSplit
```

They do not instantiate `AbstractEscapeQuotient`, do not prove
`PositiveRootBlockClosedExtraction`, and do not prove
`ClosedWeightedHallCompleteness`. The graph-heavy pure-lens facts enter as
explicit hypotheses:

```lean
ProperRelative C (restrict C U)
ProperRelative C (restrictCompl C U)
StrongPureLensAtomSplit C U
Disjoint (restrict C U).verts (restrictCompl C U).verts
```

Thus T8 is useful downstream of a pure-lens graph split, but it should not be
counted as closing root-locality.

## Immediate consequence

The current Gap#1 bridge is:

1. Construct the concrete forced-escape quotient used by the real cage model.
2. Prove `PositiveRootBlockClosedExtraction` for that quotient, or an equivalent
   root-locality theorem strong enough for the W3 skeleton.
3. Prove `ClosedWeightedHallCompleteness` for the same closure, not for a
   different scalar Hall surrogate.
4. Prove the closed-root exchange identity
   `ClosedRootCutViolatesD1` in the exact `Allowed` cut family.
5. Supply the finite rational Farkas / almost-squeeze source that feeds
   `DualAlmostSqueeze`.

Until these are supplied, the wall remains a genuine math obligation even
though the downstream bookkeeping modules are compiled.
