# Prompt for Fable/GPT-Pro: concrete forced-ell=5 escape bridge for Gap#1

We are proving Erdős Problem #23 in Lean. The finite/chart side is accepted;
the remaining proof wall is Gap#1:

```text
FullBankHall / ShortestSupportExpansion / Ell5FullBankRelaxedCover_exists
```

Bare SSE and old local switch/lens routes are refuted. The active route is the
banked relaxed cut-cover / external slack bank / no-Farkas-dual FullBankHall
route.

## Current compiled Lean surface

The following non-payload wall/provider modules compile and axiom-probe clean:

```lean
Erdos23Delta0.Gamma.FullBankChargeCertProvider
Erdos23Delta0.BankedWallLPRestricted
Erdos23Delta0.BankedWallRoutingFailure
Erdos23Delta0.PortHallUncrossing
Erdos23Delta0.ClosedShoreExtraction
Erdos23Delta0.ClosedWeightedHall
Erdos23Delta0.BankedWallW3Skeleton
```

Allowed axioms only:

```text
propext, Classical.choice, Quot.sound
```

Probe:

```text
tmp/codex_nonpayload_axiom_probe.lean
tmp/codex_nonpayload_axiom_probe.txt
```

The current abstract LP object is:

```lean
structure BankedWallLP where
  Cut : Type
  Atom : Type
  Short : Type
  Port : Type
  Sink : Type
  cutFintype : Fintype Cut
  atomFintype : Fintype Atom
  shortFintype : Fintype Short
  portFintype : Fintype Port
  sinkFintype : Fintype Sink
  cov : Cut -> Atom -> Q
  useShort : Cut -> Short -> Q
  cutPort : Cut -> Port -> Q
  legal : Port -> Sink -> Prop
  legalDecidable : forall p s, Decidable (legal p s)
  cap : Sink -> Q
```

The closed-escape abstraction is:

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

The currently compiled W3 theorem is:

```lean
theorem Erdos23Delta0.Wall.ClosedShore.noStrictDual_of_closedHall_and_exchange
    {Allowed : I.Cut -> Prop} {Q : AbstractEscapeQuotient I} {d : Dual I}
    (hd : d.Checked)
    (Z : DualAlmostSqueeze I Allowed d)
    (hHall : ClosedWeightedHallCompleteness Q)
    (hExtract : PositiveRootBlockClosedExtraction Q)
    (hExchange : ClosedRootCutViolatesD1 Allowed Q d Z.portLoad) :
    not d.StrictGap
```

Thus the remaining graph-side hooks are exactly:

```lean
ClosedWeightedHallCompleteness Q
PositiveRootBlockClosedExtraction Q
ClosedRootCutViolatesD1 Allowed Q d L
```

R3 says the decisive missing concrete geometry is a forced-ell=5 escape /
root-locality theorem. The old `RootBlockClosureSeparable` is false at the
abstract closure level; Claude verified a 2-component abstract counterexample.
So the proof must use the concrete forced-ell=5 escape structure.

## Current concrete ell=5 surface

Search result:

```text
rg ForcedEll5EscapeStep problems/23/lean/Erdos23Delta0
```

finds no API. Existing concrete support facts are:

```lean
Ell5SupportFinset.geodesicSupport
Ell5SupportFinset.Eshort
Ell5SupportFinset.ell5_base_case_Eshort_of_ell
Ell5AtomGraph.ell5_atom_of_badEdge
```

These define and prove facts about the full multi-geodesic support of ell=5
bad edges, but do not yet define forced escape steps, closure components,
exposed bank ports, or root-locality.

## Request

Give the cleanest formalizable concrete bridge from the existing ell=5 support
surface to the abstract W3 hooks above.

Please produce one of these:

1. A precise Lean-style API for a concrete `ForcedEll5EscapeStep` module, using
   existing names where possible, with statements sufficient to prove:

```lean
PositiveRootBlockClosedExtraction Q
ClosedRootCutViolatesD1 Allowed Q d L
```

2. Or a sharper route that avoids introducing `ForcedEll5EscapeStep` entirely
   and directly constructs `ClosedWeightedHallCompleteness`,
   `PositiveRootBlockClosedExtraction`, and `ClosedRootCutViolatesD1` from the
   existing `geodesicSupport` / banked cut-cover objects.

The API must be compatible with the existing abstract targets:

```lean
BankedWallLP.Cut
BankedWallLP.Atom
BankedWallLP.Short
BankedWallLP.Port
BankedWallLP.Sink
BankedWallLP.cov
BankedWallLP.useShort
BankedWallLP.cutPort
BankedWallLP.legal
AbstractEscapeQuotient.fullClosure
AbstractEscapeQuotient.exposedPorts
```

The proof route should isolate exactly one or two genuine graph-theoretic
lemmas. Bookkeeping lemmas can be Lean-written once their types are fixed.

## R3 candidate hook

R3 suggested:

```lean
theorem firstRootCrossing_outlet (X : FirstRootCrossing O Q Step U D r) :
    O.PrivateShortEdge X.e
      or O.supportSize X.e = 5
      or (exists f, f != X.e and O.supportUnionSize X.e f < 5)
      or O.ProperFullClosureHallViolator
```

Then, if the ten checked facts exclude all four outlets, no first root-crossing
escape exists, and positive root-block closed extraction follows.

Need you to make this concrete:

- What is `FirstRootCrossing` over the existing Lean objects?
- What is the minimal concrete definition of `ForcedEll5EscapeStep`?
- How do `supportSize`, `supportUnionSize`, and `ProperFullClosureHallViolator`
  map to existing `geodesicSupport` / `Eshort` definitions?
- Is the closed-root cut exchange identity separate, or does it follow from the
  same forced-escape step theorem?

## Avoid these dead routes

- Do not propose bare ShortestSupportExpansion; it has a verified 24-vertex
  counterexample.
- Do not use abstract closure separability; R3 has an exact abstract
  two-component counterexample.
- Do not use unsupported terminal/lens switch equalities.
- Do not introduce broad, untyped graph APIs that cannot be wired to the
  current `BankedWallLP` / `AbstractEscapeQuotient` surface.

The desired output is a small lemma tree with Lean-ish signatures, exact
hypotheses, and proof sketches for the graph-theoretic nodes only.

## Update after source audit: exact accepted deliverables

The latest Lean source audit makes the acceptable output even narrower.  The
W3 shell is already compiled and only needs concrete graph inputs for the
following three named obligations:

```lean
ClosedWeightedHallCompleteness Q
PositiveRootBlockClosedExtraction Q
ClosedRootCutViolatesD1 Allowed Q d Z.portLoad
```

where:

```lean
def ClosedWeightedHallCompleteness (Q : AbstractEscapeQuotient I) : Prop :=
  forall {d : Dual I} {L : I.Port -> Rat},
    WeightedRoutingFailure d L ->
      exists U : Finset Q.QComp,
        Q.fullClosure U = U /\
          MinimalClosedDeficient Q L (Q.exposedPorts U)
```

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

The compiled consumer is:

```lean
noStrictRestrictedDual_of_closedHall_and_exchange :
  d.RestrictedChecked Allowed ->
  DualAlmostSqueeze I Allowed d ->
  ClosedWeightedHallCompleteness Q ->
  PositiveRootBlockClosedExtraction Q ->
  ClosedRootCutViolatesD1 Allowed Q d Z.portLoad ->
  not d.StrictGap
```

Important correction: source search finds no compiled theorem of the form

```lean
dualSqueeze_exists_iff_no_restrictedStrict
```

or any full finite-rational Farkas equivalence for the restricted allowed-cut
system.  Therefore the three W3 obligations alone do **not** close Gap#1 unless
the route also supplies the `DualAlmostSqueeze I Allowed d` input for every
relevant strict restricted dual.  A complete W3-route answer must include either:

```lean
finiteRestrictedFarkasAlmostSqueeze :
  d.RestrictedChecked Allowed ->
  d.StrictGap ->
  DualAlmostSqueeze I Allowed d
```

with the correct side conditions for the concrete wall instance, or an
equivalent theorem that every relevant strict dual has such an allowed
almost-squeeze.

So please return either:

1. a concrete forced-ell=5 `AbstractEscapeQuotient` construction plus proofs of
   the three obligations above **and** the missing finite-Farkas/almost-squeeze
   source; or
2. a direct construction of `FullBankGlobalPackage.Checked` /
   `FullBankRelaxedCoverCert` that explicitly contains the same closed-Hall,
   positive-root extraction, no-double-spend, and closed-root exchange content.

Do not spend effort on downstream conversions: `Gamma/FullBankChargeCertProvider`
already converts an existing checked full-bank package to the typed
`LengthSurplusChargeCertV2` route.  The missing math is exactly the construction
of that package or the three W3 hypotheses.
