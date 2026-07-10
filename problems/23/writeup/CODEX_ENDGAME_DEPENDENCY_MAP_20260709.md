# Codex Endgame Dependency Map - 2026-07-09

This note records the current Lean surface after the v108 chart ledger and the
Chart000/T8/SPEC acceptance messages. It is a coordination artifact, not a new
mathematical claim.

## Current O14 payload state

- The v108 chart ledger is accepted canonical by Claude: 108/108, zero failures.
- `O14/Generated/ChartPayloads` is frozen until Claude posts the console4 wave
  verdict for the regenerated Chart001..107 shard build.
- The accepted route is the value-level chunked cone bridge:
  `O14.ChunkedConeWitness.chartSound_of_chartWitnesses` and per-chart
  `ChartNNNBridge.coreODLGoal_of_chartNNNCone`.

## O14 semantic bridge surface

The generated registry is not the final semantic proof by itself. The current
interface is:

- `O14.Generated.BridgeRegistry.ChartBridgeInputs`
  supplies per-chart `Env`, `hvars`, `hslacks`, `hcombo`, and `htarget`.
- `O14.Generated.BridgeRegistry.chartSound_of_bridgeInputs`
  converts those bindings into `EQODL1ChartSound`.
- `O14.Generated.ListedConcreteCover.coreODLGoal_of_listedCoverage`
  proves `CoreODLGoal` for semantically sound EQODL1 shape instances once:
  - `ListedShapeCoverage` is proved, and
  - `ChartBridgeInputs` is supplied.
- `O14.ListedChartCoverToODLFull.rowODL_of_listed_o14_eq_cover_semantic_tree_of_coverage`
  is the existing higher-level wrapper from listed EQ leaf coverage plus
  route-tree semantic checks to the row-level ODL bound.

Immediate remaining O14 obligations after the console4 payload verdict:

1. Prove or supply `ListedShapeCoverage` for the current semantic extraction.
2. Supply `ChartBridgeInputs` from the real EQODL1 semantic shape data.
3. Use `rowODL_of_listed_o14_eq_cover_semantic_tree_of_coverage` in the final
   component/provider dispatch.

## Row partition / Branch-B dispatch

`Rows.RowPartition` is the provider-facing dispatch surface:

- `ODLFullRowPartitionView.Checked` ties component classification to the shared
  K2 relation.
- `rowGersh_of_partition` dispatches by component, not by individual row length.
- `allRowsGersh_of_partition` gives the value-level all-row GERSH hypothesis.
- `beta_bound_of_partitioned_provider` gives the graph-data beta bound once
  `GoodCutData` and a checked partition provider are available.

Guardrail: EQODL1 owns whole all-L5 components. Branch-B owns mixed components
wholesale, including their length-5 rows.

## Full-bank wall output surface

`Gamma.FullBankToLengthSurplusCharge` and
`Gamma.FullBankChargeCertProvider` provide the compiled output target for the
wall:

- Construct `FullBankGlobalPackage G c rows`.
- Prove `P.Checked`.
- Then `fullBankGlobalPackage_sound` gives
  `lengthSurplusTarget G c rows <= 0`.
- `chargeCertProviderOfFullBankLedger_ok` and
  `gammaUpper_from_fullBankPackage_via_chargeCertV2` route the same result
  through the accepted `LengthSurplusChargeCertV2` checker path.

Remaining wall obligation:

- Produce a checked `FullBankGlobalPackage` from the banked relaxed
  cut-cover / restricted-Farkas / closed-shore route. This is Gap#1.

## Route-agnostic wall consumer

The current Lean tree also has a small final-assembly selector:

```lean
Erdos23Delta0.Wall.EndgameWallCert
```

defined in:

```text
problems/23/lean/Erdos23Delta0/BankedWallEndgameCert.lean
```

It has three constructors:

```lean
EndgameWallCert.forcedEscape :
  ClosedShore.ForcedEscapeWallCert I -> EndgameWallCert I

EndgameWallCert.hornForcedEscape :
  ClosedShore.HornForcedEscapeWallCert I -> EndgameWallCert I

EndgameWallCert.restrictedSqueeze :
  RestrictedSqueezeWallCert I -> EndgameWallCert I
```

and exports:

```lean
EndgameWallCert.noStrictRestrictedDual
EndgameWallCert.noStrictDual
```

This is only a route selector.  It does not construct either route's hard
certificate.  It lets later assembly consume "the wall is closed" without
choosing between the closed-shore and direct restricted-squeeze routes.

Local probe:

```text
tmp/codex_endgame_wall_probe.lean
tmp/codex_endgame_wall_probe.out.txt
```

Targeted check result: `rc=0`; the two exported theorem axiom sets are exactly
`[propext, Classical.choice, Quot.sound]`; source forbidden-token scan has no
hits for `sorry/admit/native_decide/unsafe/axiom/ofReduceBool/trustCompiler`.

## FC / official theorem bridge

`FCBridge.erdos23_fcForm_of_packageProvider` is the current official-form
wrapper. It still requires a generic provider:

```lean
∀ {V : Type*} [Fintype V] [DecidableEq V]
  (Gs : SimpleGraph V) [DecidableRel Gs.Adj],
  Gs.CliqueFree 3 → Nonempty (SimpleGraphCertificatePackage Gs)
```

Only after that provider exists does the official `5 * n` statement follow via
`erdos23_fcForm_of_bipartization`.

The same file now also exposes the all-cardinality rational deletion form:

```lean
theorem erdos23_rationalDeletion_of_packageProvider
    (packageProvider :
      ∀ {V : Type*} [Fintype V] [DecidableEq V]
        (Gs : SimpleGraph V) [DecidableRel Gs.Adj],
        Gs.CliqueFree 3 → Nonempty (SimpleGraphCertificatePackage Gs)) :
    ∀ (V : Type*) [Fintype V] [DecidableEq V],
      ∀ (Gs : SimpleGraph V) [DecidableRel Gs.Adj], Gs.CliqueFree 3 →
        ∃ H : SimpleGraph V,
          H ≤ Gs ∧ H.IsBipartite ∧
            ((Gs.edgeFinset \ H.edgeFinset).card : ℚ) ≤
              (Fintype.card V : ℚ) ^ 2 / 25
```

This is not the official `formal-conjectures` theorem shape, whose current file
`FormalConjectures/ErdosProblems/23.lean` asks the `5 * n` Nat-bound statement.
It is the audit-facing all-`N` rational surface implied by the same package
provider.

The exact compiled wrapper shape is:

```lean
theorem erdos23_fcForm_of_packageProvider
    (packageProvider :
      ∀ {V : Type*} [Fintype V] [DecidableEq V]
        (Gs : SimpleGraph V) [DecidableRel Gs.Adj],
        Gs.CliqueFree 3 → Nonempty (SimpleGraphCertificatePackage Gs)) :
    ∀ (n : ℕ) (V : Type*) [Fintype V] [DecidableEq V],
      Fintype.card V = 5 * n →
        ∀ (Gs : SimpleGraph V) [DecidableRel Gs.Adj], Gs.CliqueFree 3 →
          ∃ H : SimpleGraph V,
            H ≤ Gs ∧ H.IsBipartite ∧
              (Gs.edgeFinset \ H.edgeFinset).card ≤ n^2
```

The package fields in `CertGraph.SimpleGraphCertificatePackage` are:

```lean
enc : SimpleGraphEncodingFacts Gs
cut : CutData
rows : RowDB
hCut : checkCut enc.G cut = true
good : GoodCutData enc.G cut rows
delta : Delta0CertBundles enc.G cut rows
```

The SimpleGraph-to-official-form bridge is not the current mathematical wall:
`SimpleGraphBridge.beta_bipartization` is already used by
`erdos23_fcForm_of_bipartization`.  The remaining FC-level work is exactly to
construct `Nonempty (SimpleGraphCertificatePackage Gs)` for every finite
triangle-free `Gs` by wiring:

1. default/simple encoding facts,
2. a selected checked good cut and rows,
3. row partition / O14 / Branch-B row bounds,
4. the checked full-bank wall package,
5. the resulting `Delta0CertBundles`.

Local scope probe:

```text
tmp/codex_fcbridge_scope_probe.lean
tmp/codex_fcbridge_scope_probe.out.txt
```

Targeted check result: `rc=0`; the rational all-`N` wrappers and the existing
official-form wrapper all have axiom sets exactly
`[propext, Classical.choice, Quot.sound]`.

## Package-provider decomposition

`CertGraph.exists_good_cut_from_providers_default` reduces the generic
good-cut/row side to three pieces:

```lean
ConnectedMaxCutImpliesBConnected G
GammaMinSelectionProvider G
cutFnBridgeFacts_default G
```

The cut-function bridge is already default. The current selection/provider lane
must still supply:

- a graph-connectedness-to-`BConnected` argument in the shape
  `ConnectedMaxCutImpliesBConnected`;
- a gamma-minimal row selector in the shape `GammaMinSelectionProvider`;
- a `RemainingDelta0CertificateData G c rows` provider, whose fields are

```lean
branchA_a1Proper_and_odl :
  ∀ Q : RowCert, RowInDB rows Q → Q.length = 5 →
    BranchAInputs G c rows Q
branchB_bankL_and_UPO :
  ∀ Q : RowCert, RowInDB rows Q → 5 < Q.length →
    BranchBInputs G c rows Q
```

`delta0Bundles_from_remaining` turns this remaining row-level provider into
`Delta0CertBundles`. Thus the final package provider is not another certificate
batch; it is the theorem that the selected good cut and rows always admit those
two row-branch providers. O14 covers the all-L5/EQODL1 side. Branch-B plus the
full-bank wall package covers the mixed-component side.

## Provider seam file

`problems/23/lean/Erdos23Delta0/PackageProviderSkeleton.lean` records the
current intended final adapters:

```lean
GraphDataPackageProviderInputs G
packageProvider_of_graphDataInputs
erdos23_fcForm_of_graphDataInputs
erdos23_rationalDeletion_of_graphDataInputs

GraphDataPartitionProviderInputs G
graphData_beta_bound_of_partitionInputs
erdos23_fcForm_of_partitionInputs
erdos23_rationalDeletion_of_partitionInputs
```

The first path is the older package-provider seam: a proof of
`GraphDataPackageProviderInputs` for every encoded finite triangle-free graph
would immediately provide the package-provider hypothesis consumed by
`FCBridge.erdos23_fcForm_of_packageProvider` and its all-cardinality rational
deletion wrapper.

The second path matches the newer component-level `Rows.RowPartition` route. It
does not force mixed-component length-5 rows through the old length-only
`Delta0CertBundles` split. Instead, a checked
`ODLFullRowPartitionView` gives the graph-data beta bound directly through
`ODLFullRowPartitionView.beta_bound_of_partitioned_provider`, and the seam then
uses the existing `SimpleGraphBridge.beta_bipartization` official-form bridge
or the all-cardinality rational deletion bridge.

Planning preference: the component-level partition seam is the safer final
target unless the older `SimpleGraphCertificatePackage` route is explicitly
needed by the final PR shape.

Status as of this note:

- static forbidden-token scan: clean for `sorry`, `admit`, `native_decide`,
  `axiom`, and `unsafe`;
- source/name audit: fields match `SimpleGraphCertificatePackage`,
  `GoodCutPackage`, `RemainingDelta0CertificateData`, and
  `ODLFullRowPartitionView`;
- Lean build: intentionally deferred while Claude's O14 console4 wave owns the
  Lean worker pool.

This seam file does not prove Gap#1, does not construct
`FullBankGlobalPackage.Checked`, and does not discharge O14 semantic coverage.

## Risk status

The current evidence does not justify treating the remaining work as pure
engineering. The O14/chart side is engineering unless the console4 wave reports
a new payload defect. Gap#1 remains mathematical:

- of-record route: banked relaxed cut-cover / restricted-Farkas /
  closed-shore route;
- required output: a checked `FullBankGlobalPackage`;
- load-bearing unresolved content: root-locality or
  `PositiveRootBlockClosedExtraction`, closed-Hall completeness, exchange
  identity, and the finite rational Farkas bridge.

Fable-5's latest risk read is more conservative than Codex's earlier estimate:
approximately 55% for the mathematics, approximately 80% Lean-completion
conditional on the mathematics, approximately 45% unconditional. Codex should
use that as the current conservative planning estimate until Gap#1 lands or
the O14 wave posts a contradictory defect.

Related source-surface audit:

```text
problems/23/writeup/CODEX_ROOT_LOCALITY_SURFACE_AUDIT_20260709.md
```

It records that `AbstractEscapeQuotient` is still abstract in the current tree,
that no concrete forced-escape quotient instantiation was found by source
search, and that the T8 `Ell5/ConcreteCage` modules are pure-lens split
bookkeeping rather than the root-locality / closed-Hall bridge.

New provider-facing wall contract:

```lean
Erdos23Delta0.Wall.ClosedShore.ForcedEscapeWallInputs
```

defined in:

```text
problems/23/lean/Erdos23Delta0/BankedWallForcedEscapeBridge.lean
```

This packages the W3 inputs (`AbstractEscapeQuotient`, closed-Hall,
positive-root extraction, and closed-root exchange) and consumes the existing
W3 skeleton. It is a naming adapter only; it does not prove any graph-side
root-locality content.

## Current bottlenecks

1. O14 console4 generated-payload wave verdict.
2. O14 semantic bindings and listed-shape coverage.
3. Gap#1: concrete forced-escape/root-locality route producing a checked
   `FullBankGlobalPackage`.
4. Final `SimpleGraphCertificatePackage` provider for every finite
   triangle-free graph.
