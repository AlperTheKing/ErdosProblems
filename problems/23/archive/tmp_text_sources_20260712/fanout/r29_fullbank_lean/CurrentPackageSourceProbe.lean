import Erdos23Delta0.CertGraph
import Erdos23Delta0.Rows.RowPartition

/-
FC-form bridge: from the package-conditional `erdos23_delta0`
(`(betaSimple Gs : ℚ) ≤ (card V)^2 / 25`) to the official
formal-conjectures `erdos_23` statement shape
(`∃ H ≤ G, H.IsBipartite ∧ (G.edgeFinset \ H.edgeFinset).card ≤ n^2`).

Two steps: (1) the rational-to-Nat arithmetic, card V = 5n ⟹ (5n)^2/25 = n^2,
so `betaSimple Gs ≤ n^2` (Nat); (2) the bipartization identity
`betaSimple Gs = min deletion over bipartite subgraphs`, isolated here as the
single hypothesis `beta_bipartization` (a pure Mathlib SimpleGraph fact,
independent of the #23 argument — the minimizing Boolean coloring yields the
bipartite subgraph whose deleted edges are exactly the monochromatic ones).
-/

open SimpleGraph

namespace Erdos23Delta0
namespace CertGraph

universe u

/-- FC-FORM (unconditional). A triangle-free graph with a certificate package on
    `5n` vertices has a bipartite subgraph deleting at most `n^2` edges — the
    official `erdos_23` shape. The bipartization identity is now discharged by the
    proven `SimpleGraphBridge.beta_bipartization`. -/
theorem erdos23_fcForm_of_bipartization
    {V : Type*} [Fintype V] [DecidableEq V]
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj]
    (n : ℕ) (hcard : Fintype.card V = 5 * n)
    (hTri : Gs.CliqueFree 3) (P : SimpleGraphCertificatePackage Gs) :
    ∃ H : SimpleGraph V, H ≤ Gs ∧ H.IsBipartite ∧
      (Gs.edgeFinset \ H.edgeFinset).card ≤ n ^ 2 := by
  have hbound : (betaSimple Gs : ℚ) ≤ (Fintype.card V : ℚ) ^ 2 / 25 :=
    erdos23_delta0 Gs hTri P
  have hcardQ : (Fintype.card V : ℚ) = 5 * (n : ℚ) := by
    rw [hcard]; push_cast; ring
  rw [hcardQ] at hbound
  have hn2 : ((5 : ℚ) * (n : ℚ)) ^ 2 / 25 = (n : ℚ) ^ 2 := by ring
  rw [hn2] at hbound
  have hbeta_le : betaSimple Gs ≤ n ^ 2 := by exact_mod_cast hbound
  exact SimpleGraphBridge.beta_bipartization Gs (n ^ 2) hbeta_le

/-- Rational deletion bridge from a `betaSimple` bound.  This isolates the
`SimpleGraphBridge.beta_bipartization` instance choices for all-cardinality
wrappers. -/
theorem rationalDeletion_of_beta_bound
    {V : Type*} [Fintype V] [DecidableEq V]
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj]
    (hbound : (betaSimple Gs : ℚ) ≤ (Fintype.card V : ℚ) ^ 2 / 25) :
    ∃ H : SimpleGraph V, H ≤ Gs ∧ H.IsBipartite ∧
      ((Gs.edgeFinset \ H.edgeFinset).card : ℚ) ≤
        (Fintype.card V : ℚ) ^ 2 / 25 := by
  obtain ⟨H, hHG, hHbip, hdel⟩ :=
    SimpleGraphBridge.beta_bipartization Gs (betaSimple Gs) (Nat.le_refl _)
  refine ⟨H, hHG, hHbip, ?_⟩
  have hdelQ : ((Gs.edgeFinset \ H.edgeFinset).card : ℚ) ≤
      (betaSimple Gs : ℚ) := by
    exact_mod_cast hdel
  exact le_trans hdelQ hbound

/-- All-cardinality rational deletion form. This is stronger in scope than the
    official `5n` Nat-valued formal-conjectures surface, but keeps the rational
    `N^2/25` target explicit for audits and downstream wrappers. -/
theorem erdos23_rationalDeletion_of_bipartization
    {V : Type*} [Fintype V] [DecidableEq V]
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj]
    (hTri : Gs.CliqueFree 3) (P : SimpleGraphCertificatePackage Gs) :
    ∃ H : SimpleGraph V, H ≤ Gs ∧ H.IsBipartite ∧
      ((Gs.edgeFinset \ H.edgeFinset).card : ℚ) ≤
        (Fintype.card V : ℚ) ^ 2 / 25 := by
  have hbound : (betaSimple Gs : ℚ) ≤ (Fintype.card V : ℚ) ^ 2 / 25 :=
    erdos23_delta0 Gs hTri P
  exact rationalDeletion_of_beta_bound Gs hbound

/-- Official-form wrapper from the remaining generic package provider.

This is the final bookkeeping shape for the `formal-conjectures` theorem: once
the delta=0 assembly constructs a `SimpleGraphCertificatePackage` for every
finite triangle-free graph, the displayed Erdős #23 statement follows. -/
theorem erdos23_fcForm_of_packageProvider
    (packageProvider :
      ∀ {V : Type u} [Fintype V] [DecidableEq V]
        (Gs : SimpleGraph V) [DecidableRel Gs.Adj],
        Gs.CliqueFree 3 → Nonempty (SimpleGraphCertificatePackage Gs)) :
    ∀ (n : ℕ) (V : Type u) [Fintype V] [DecidableEq V],
      Fintype.card V = 5 * n →
        ∀ (Gs : SimpleGraph V) [DecidableRel Gs.Adj], Gs.CliqueFree 3 →
          ∃ H : SimpleGraph V,
            H ≤ Gs ∧ H.IsBipartite ∧
              (Gs.edgeFinset \ H.edgeFinset).card ≤ n^2 := by
  intro n V _ _ hcard Gs _ hTri
  classical
  obtain ⟨P⟩ := packageProvider (V := V) Gs hTri
  exact erdos23_fcForm_of_bipartization Gs n hcard hTri P

/-- All-cardinality rational wrapper from the same remaining generic provider. -/
theorem erdos23_rationalDeletion_of_packageProvider
    (packageProvider :
      ∀ {V : Type u} [Fintype V] [DecidableEq V]
        (Gs : SimpleGraph V) [DecidableRel Gs.Adj],
        Gs.CliqueFree 3 → Nonempty (SimpleGraphCertificatePackage Gs)) :
    ∀ (V : Type u) [Fintype V] [DecidableEq V],
      ∀ (Gs : SimpleGraph V) [DecidableRel Gs.Adj], Gs.CliqueFree 3 →
        ∃ H : SimpleGraph V,
          H ≤ Gs ∧ H.IsBipartite ∧
            ((Gs.edgeFinset \ H.edgeFinset).card : ℚ) ≤
              (Fintype.card V : ℚ) ^ 2 / 25 := by
  intro V _ _ Gs _ hTri
  classical
  obtain ⟨P⟩ := packageProvider (V := V) Gs hTri
  exact erdos23_rationalDeletion_of_bipartization Gs hTri P

end CertGraph
end Erdos23Delta0


/-!
# Final provider skeleton

This file is deliberately small.  It records two final adapter shapes:

* the older package-provider seam, which packages the generic good-cut
  selection surface plus row-level Branch-A/B providers into the
  `SimpleGraphCertificatePackage` demanded by `FCBridge`;
* the newer component-level partition seam, which routes checked
  `Rows.RowPartition.ODLFullRowPartitionView` data directly to the official
  theorem through the existing bipartization bridge.

It does not prove Gap#1.  Instead, it pins the exact provider shape that the
remaining O14/Branch-B/full-bank wall assembly must construct.
-/

namespace Erdos23Delta0
namespace CertGraph

universe u

/-- GraphData-level ingredients still needed after the generic finite
max-cut/row-selection discharges.  The hard content is the `remaining` field:
it supplies the Branch-A and Branch-B row obligations for the selected
gamma-minimal good cut and row database. -/
structure GraphDataPackageProviderInputs (G : GraphData) : Type where
  conn : ConnectedMaxCutImpliesBConnected G
  gammaSel : GammaMinSelectionProvider G
  remaining :
    ∀ {c : CutData} {rows : RowDB},
      checkCut G c = true →
        GoodCutData G c rows →
          RemainingDelta0CertificateData G c rows

/-- Alternative endgame input surface matching the newer component-level row
partition route.  Unlike `RemainingDelta0CertificateData`, this does not force
mixed-component length-5 rows through the old length-only Branch-A/B split.
Instead the supplied partition proves the graph-data beta bound directly via
`Rows.RowPartition.ODLFullRowPartitionView.beta_bound_of_partitioned_provider`.
-/
structure GraphDataPartitionProviderInputs (G : GraphData) : Type where
  conn : ConnectedMaxCutImpliesBConnected G
  gammaSel : GammaMinSelectionProvider G
  partition :
    ∀ {c : CutData} {rows : RowDB},
      checkCut G c = true →
        GoodCutData G c rows →
          ∃ (R : Erdos23Delta0.RowPartitionCore.RowIdx rows →
                 Erdos23Delta0.RowPartitionCore.RowIdx rows → Prop)
            (P : Erdos23Delta0.Rows.RowPartition.ODLFullRowPartitionView G c rows),
              P.Checked R

/-- Assemble a `GoodCutPackage` from the generic good-cut selectors plus the
remaining row-level delta provider. -/
noncomputable def goodCutPackage_of_providerInputs {G : GraphData}
    (H : GraphDataPackageProviderInputs G) : GoodCutPackage G := by
  classical
  let hExists := exists_good_cut_from_providers_default G H.conn H.gammaSel
  let c : CutData := Classical.choose hExists
  let hRowsExists := Classical.choose_spec hExists
  let rows : RowDB := Classical.choose hRowsExists
  have hRowsSpec :
      checkCut G c = true ∧ Nonempty (GoodCutData G c rows) :=
    Classical.choose_spec hRowsExists
  rcases hRowsSpec with ⟨hCut, hGoodNonempty⟩
  let hGood : GoodCutData G c rows := Classical.choice hGoodNonempty
  exact
    { cut := c
      rows := rows
      hCut := hCut
      good := hGood
      delta := delta0Bundles_from_remaining (H.remaining hCut hGood) }

/-- SimpleGraph-level package assembly from GraphData-level provider inputs
for the default encoding of the given graph. -/
noncomputable def simpleGraphCertificatePackage_of_providerInputs
    {V : Type*} [Fintype V] [DecidableEq V]
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj]
    (H : GraphDataPackageProviderInputs
      (simpleGraphEncodingFacts_default (Gs := Gs)).G) :
    SimpleGraphCertificatePackage Gs := by
  classical
  let P : GoodCutPackage (simpleGraphEncodingFacts_default (Gs := Gs)).G :=
    goodCutPackage_of_providerInputs
      (G := (simpleGraphEncodingFacts_default (Gs := Gs)).G) H
  exact
    { enc := simpleGraphEncodingFacts_default (Gs := Gs)
      cut := P.cut
      rows := P.rows
      hCut := P.hCut
      good := P.good
      delta := P.delta }

/-- Nonempty package form, matching the hypothesis consumed by
`FCBridge.erdos23_fcForm_of_packageProvider`. -/
theorem simpleGraphPackage_nonempty_of_providerInputs
    {V : Type*} [Fintype V] [DecidableEq V]
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj]
    (H : GraphDataPackageProviderInputs
      (simpleGraphEncodingFacts_default (Gs := Gs)).G) :
    Nonempty (SimpleGraphCertificatePackage Gs) :=
  ⟨simpleGraphCertificatePackage_of_providerInputs Gs H⟩

/-- Final provider adapter: once the remaining assembly supplies
`GraphDataPackageProviderInputs` for every finite triangle-free graph, the
`SimpleGraphCertificatePackage` provider required by `FCBridge` is available. -/
theorem packageProvider_of_graphDataInputs
    (providerInputs :
      ∀ {V : Type u} [Fintype V] [DecidableEq V]
        (Gs : SimpleGraph V) [DecidableRel Gs.Adj],
          Gs.CliqueFree 3 →
            GraphDataPackageProviderInputs
              (simpleGraphEncodingFacts_default (Gs := Gs)).G) :
    ∀ {V : Type u} [Fintype V] [DecidableEq V]
      (Gs : SimpleGraph V) [DecidableRel Gs.Adj],
        Gs.CliqueFree 3 → Nonempty (SimpleGraphCertificatePackage Gs) := by
  intro V _ _ Gs _ hTri
  exact simpleGraphPackage_nonempty_of_providerInputs Gs
      (providerInputs Gs hTri)

/-- Direct rational beta bound for the older package-provider route.  This is
the beta-bound seam underlying both official-form and all-cardinality deletion
wrappers. -/
theorem simpleGraph_beta_bound_of_graphDataInputs
    {V : Type*} [Fintype V] [DecidableEq V]
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj]
    (hTri : Gs.CliqueFree 3)
    (H : GraphDataPackageProviderInputs
      (simpleGraphEncodingFacts_default (Gs := Gs)).G) :
    (betaSimple Gs : ℚ) ≤ (Fintype.card V : ℚ) ^ 2 / 25 := by
  let P : SimpleGraphCertificatePackage Gs :=
    simpleGraphCertificatePackage_of_providerInputs Gs H
  exact erdos23_delta0 Gs hTri P

/-- Official-form adapter.  Once the endgame supplies graph-data provider inputs
for every finite triangle-free graph, the existing FC bridge yields the final
`5 * n` formal-conjectures statement. -/
theorem erdos23_fcForm_of_graphDataInputs
    (providerInputs :
      ∀ {V : Type u} [Fintype V] [DecidableEq V]
        (Gs : SimpleGraph V) [DecidableRel Gs.Adj],
          Gs.CliqueFree 3 →
            GraphDataPackageProviderInputs
              (simpleGraphEncodingFacts_default (Gs := Gs)).G) :
    ∀ (n : ℕ) (V : Type u) [Fintype V] [DecidableEq V],
      Fintype.card V = 5 * n →
        ∀ (Gs : SimpleGraph V) [DecidableRel Gs.Adj], Gs.CliqueFree 3 →
          ∃ H : SimpleGraph V,
            H ≤ Gs ∧ H.IsBipartite ∧
              (Gs.edgeFinset \ H.edgeFinset).card ≤ n^2 :=
  erdos23_fcForm_of_packageProvider
    (packageProvider_of_graphDataInputs providerInputs)

/-- All-cardinality rational deletion adapter for the older package-provider
route.  This is the direct `N^2/25` form; the `5 * n` theorem above is its
Nat-valued formal-conjectures multiple-of-five specialization. -/
theorem erdos23_rationalDeletion_of_graphDataInputs
    (providerInputs :
      ∀ {V : Type u} [Fintype V] [DecidableEq V]
        (Gs : SimpleGraph V) [DecidableRel Gs.Adj],
          Gs.CliqueFree 3 →
            GraphDataPackageProviderInputs
              (simpleGraphEncodingFacts_default (Gs := Gs)).G) :
    ∀ (V : Type u) [Fintype V] [DecidableEq V],
      ∀ (Gs : SimpleGraph V) [DecidableRel Gs.Adj], Gs.CliqueFree 3 →
        ∃ H : SimpleGraph V,
          H ≤ Gs ∧ H.IsBipartite ∧
            ((Gs.edgeFinset \ H.edgeFinset).card : ℚ) ≤
              (Fintype.card V : ℚ) ^ 2 / 25 :=
  erdos23_rationalDeletion_of_packageProvider
    (packageProvider_of_graphDataInputs providerInputs)

/-- GraphData beta bound obtained through the component-level partition
provider.  This is the seam matching the accepted RowPartition guardrail:
EQODL1 is a component-all-length-5 condition, and mixed components are routed
wholesale to Branch-B. -/
theorem graphData_beta_bound_of_partitionInputs {G : GraphData}
    (H : GraphDataPartitionProviderInputs G) :
    ∃ c rows, ∃ hGood : GoodCutData G c rows,
      checkCut G c = true ∧
        hGood.gammaBeta.betaVal ≤ (G.n : ℚ) ^ 2 / 25 := by
  classical
  rcases exists_good_cut_from_providers_default G H.conn H.gammaSel with
    ⟨c, rows, hCut, hGoodNonempty⟩
  obtain ⟨hGood⟩ := hGoodNonempty
  rcases H.partition hCut hGood with ⟨R, P, hP⟩
  have hBeta :=
    Erdos23Delta0.Rows.RowPartition.ODLFullRowPartitionView.beta_bound_of_partitioned_provider
      (P := P) (R := R) hGood hP
  exact ⟨c, rows, hGood, hCut, hBeta⟩

/-- SimpleGraph rational beta bound via the component-level partition provider
for the default encoded graph. -/
theorem simpleGraph_beta_bound_of_partitionInputs
    {V : Type*} [Fintype V] [DecidableEq V]
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj]
    (H : GraphDataPartitionProviderInputs
      (simpleGraphEncodingFacts_default (Gs := Gs)).G) :
    (betaSimple Gs : ℚ) ≤ (Fintype.card V : ℚ) ^ 2 / 25 := by
  classical
  let E := simpleGraphEncodingFacts_default (Gs := Gs)
  rcases graphData_beta_bound_of_partitionInputs
      (G := E.G) H with ⟨c, _rows, hGood, _hCut, hBeta⟩
  have hβnat : betaSimple Gs = badCount E.G c :=
    betaSimple_eq_badCount_of_isMaxCut Gs E c hGood.maxCut
  have hγβ : hGood.gammaBeta.betaVal = (badCount E.G c : ℚ) :=
    hGood.gammaBeta.beta_eq_badCount
  have hβ : (betaSimple Gs : ℚ) = hGood.gammaBeta.betaVal := by
    rw [hβnat, hγβ]
  rw [hβ, ← E.n_transfer]
  exact hBeta

/-- Official-form adapter for the newer component-level partition route.  This
bypasses `SimpleGraphCertificatePackage` and uses the existing FC
bipartization bridge directly from the rational beta bound. -/
theorem erdos23_fcForm_of_partitionInputs
    (providerInputs :
      ∀ {V : Type u} [Fintype V] [DecidableEq V]
        (Gs : SimpleGraph V) [DecidableRel Gs.Adj],
          Gs.CliqueFree 3 →
            GraphDataPartitionProviderInputs
              (simpleGraphEncodingFacts_default (Gs := Gs)).G) :
    ∀ (n : ℕ) (V : Type u) [Fintype V] [DecidableEq V],
      Fintype.card V = 5 * n →
        ∀ (Gs : SimpleGraph V) [DecidableRel Gs.Adj], Gs.CliqueFree 3 →
          ∃ H : SimpleGraph V,
            H ≤ Gs ∧ H.IsBipartite ∧
              (Gs.edgeFinset \ H.edgeFinset).card ≤ n^2 := by
  intro n V _ _ hcard Gs _ hTri
  classical
  have hbound :
      (betaSimple Gs : ℚ) ≤ (Fintype.card V : ℚ) ^ 2 / 25 :=
    simpleGraph_beta_bound_of_partitionInputs Gs
      (providerInputs Gs hTri)
  have hcardQ : (Fintype.card V : ℚ) = 5 * (n : ℚ) := by
    rw [hcard]; push_cast; ring
  rw [hcardQ] at hbound
  have hn2 : ((5 : ℚ) * (n : ℚ)) ^ 2 / 25 = (n : ℚ) ^ 2 := by
    ring
  rw [hn2] at hbound
  have hbeta_le : betaSimple Gs ≤ n ^ 2 := by
    exact_mod_cast hbound
  exact SimpleGraphBridge.beta_bipartization Gs (n ^ 2) hbeta_le

/-- All-cardinality rational deletion adapter for the newer component-level
partition route.  This exposes the full `N^2/25` theorem shape directly from
the rational beta bound, without requiring `Fintype.card V = 5 * n`. -/
theorem erdos23_rationalDeletion_of_partitionInputs
    (providerInputs :
      ∀ {V : Type u} [Fintype V] [DecidableEq V]
        (Gs : SimpleGraph V) [DecidableRel Gs.Adj],
          Gs.CliqueFree 3 →
            GraphDataPartitionProviderInputs
              (simpleGraphEncodingFacts_default (Gs := Gs)).G) :
    ∀ (V : Type u) [Fintype V] [DecidableEq V],
      ∀ (Gs : SimpleGraph V) [DecidableRel Gs.Adj], Gs.CliqueFree 3 →
        ∃ H : SimpleGraph V,
          H ≤ Gs ∧ H.IsBipartite ∧
            ((Gs.edgeFinset \ H.edgeFinset).card : ℚ) ≤
              (Fintype.card V : ℚ) ^ 2 / 25 := by
  intro V _ _ Gs _ hTri
  classical
  have hbound :
      (betaSimple Gs : ℚ) ≤ (Fintype.card V : ℚ) ^ 2 / 25 :=
    simpleGraph_beta_bound_of_partitionInputs Gs
      (providerInputs Gs hTri)
  exact rationalDeletion_of_beta_bound Gs hbound

end CertGraph
end Erdos23Delta0

#print axioms Erdos23Delta0.CertGraph.erdos23_fcForm_of_graphDataInputs
#print axioms Erdos23Delta0.CertGraph.erdos23_fcForm_of_partitionInputs
#print axioms Erdos23Delta0.CertGraph.erdos23_rationalDeletion_of_partitionInputs
