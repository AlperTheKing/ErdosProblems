import Erdos23Delta0.Ell5CSReduction

/-!
# T7 finite-lift interface

The exhaustive exact artifact

`tmp/codex_rcc_f5_lift_parallel_nF6_full.json`

checks all `6435` minimal four-uniform Hall-deficient abstract cores with
`|F| = 6`: `6345` have no P4 lift, and the remaining `90` path-consistent
lifts force an odd cycle in the cut graph. This file does not attempt to
kernel-check that enumeration. Instead it records the small Lean-facing
interface that the enumeration is meant to discharge.

The remaining mathematical reduction is now explicit:

* a size-seven ell=5 minimal support violator must reduce to a
  `FourUniformF5Core`;
* the concrete graph geometry must make that core satisfy the caller's
  `Realizable` predicate;
* the finite artifact supplies `NoRealizableF5Core Realizable`.

The theorem below is just the glue: once those two facts are available, the
size-seven obstruction is impossible.
-/

namespace Erdos23Delta0
namespace Ell5F5LiftInterface

open Finset

/-- Abstract four-uniform Hall-deficient core with six support edges and seven
rows. This is the exact combinatorial shape enumerated by the T7 lift gate. -/
structure FourUniformF5Core (Row Edge : Type*) [DecidableEq Row] [DecidableEq Edge] where
  rows : Finset Row
  edges : Finset Edge
  supp : Row → Finset Edge
  rows_card : rows.card = 7
  edges_card : edges.card = 6
  supp_subset : ∀ r ∈ rows, supp r ⊆ edges
  supp_card : ∀ r ∈ rows, (supp r).card = 4
  deficient : (rows.biUnion supp).card < rows.card
  minimal : ∀ T, T ⊂ rows → T.card ≤ (T.biUnion supp).card
  no_private : ∀ r ∈ rows, supp r ⊆ (rows.erase r).biUnion supp
  row_inj : Set.InjOn supp rows

/-- The exact finite-artifact hypothesis: no enumerated `|F|=6` four-uniform
minimal Hall-deficient core has a valid P4 realization for the supplied graph
realizability predicate. -/
def NoRealizableF5Core {Row Edge : Type*} [DecidableEq Row] [DecidableEq Edge]
    (Realizable : FourUniformF5Core Row Edge → Prop) : Prop :=
  ∀ C, ¬ Realizable C

/-- Pure finite-set extraction: a size-seven minimal Hall obstruction whose
rows are injectively labelled four-subsets of a six-set is exactly a
`FourUniformF5Core`. This theorem is useful when the graph reduction has
already proved that all full geodesic supports have cardinality four. -/
theorem fourUniformF5Core_of_minimal_obstruction
    {Row Edge : Type*} [DecidableEq Row] [DecidableEq Edge]
    (Erow : Row → Finset Edge) (S : Finset Row)
    (hS : S.card = 7)
    (hlt : (S.biUnion Erow).card < S.card)
    (hmin : ∀ T, T ⊂ S → T.card ≤ (T.biUnion Erow).card)
    (hrow4 : ∀ r ∈ S, (Erow r).card = 4)
    (hinj : Set.InjOn Erow S) :
    ∃ U : Finset Edge, ∃ C : FourUniformF5Core Row Edge,
      U = S.biUnion Erow ∧ C.rows = S ∧ C.edges = U ∧ C.supp = Erow := by
  obtain ⟨hcard, hnoPrivate⟩ :=
    Ell5CSReduction.minimal_hall_obstruction_no_private_edge Erow S hlt hmin
  let U : Finset Edge := S.biUnion Erow
  have hU : U.card = 6 := by
    dsimp [U]
    omega
  let C : FourUniformF5Core Row Edge :=
    { rows := S
      edges := U
      supp := Erow
      rows_card := hS
      edges_card := hU
      supp_subset := by
        intro r hr
        exact Finset.subset_biUnion_of_mem Erow hr
      supp_card := hrow4
      deficient := hlt
      minimal := hmin
      no_private := hnoPrivate
      row_inj := hinj }
  exact ⟨U, C, rfl, rfl, rfl, rfl⟩

/-- T7 glue theorem. To eliminate a size-seven minimal ell=5 support violator,
it suffices to reduce it to a four-uniform F5 core, prove that the graph
geometry realizes the corresponding P4 lift, and invoke the finite no-realized
core certificate. -/
theorem no_card_seven_violator_of_no_realizable_f5_core
    {Row Edge : Type*} [DecidableEq Row] [DecidableEq Edge]
    (Realizable : FourUniformF5Core Row Edge → Prop)
    (hNo : NoRealizableF5Core Realizable)
    (Erow : Row → Finset Edge) (S : Finset Row)
    (hS : S.card = 7)
    (hlt : (S.biUnion Erow).card < S.card)
    (hmin : ∀ T, T ⊂ S → T.card ≤ (T.biUnion Erow).card)
    (hrow4 : ∀ r ∈ S, (Erow r).card = 4)
    (hinj : Set.InjOn Erow S)
    (hrealize :
      ∀ U C, U = S.biUnion Erow → C.rows = S → C.edges = U → C.supp = Erow →
        Realizable C) :
    False := by
  obtain ⟨U, C, hU, hCrows, hCedges, hCsupp⟩ :=
    fourUniformF5Core_of_minimal_obstruction Erow S hS hlt hmin hrow4 hinj
  exact hNo C (hrealize U C hU hCrows hCedges hCsupp)

/-- Convenience extraction form for the true geodesic-support application.  In a
size-seven minimal obstruction the total support has cardinality six, so every
row support is contained in a six-set.  If the graph facts rule out support
sizes five and six, the row supports are automatically four-uniform. -/
theorem fourUniformF5Core_of_minimal_obstruction_no_large_rows
    {Row Edge : Type*} [DecidableEq Row] [DecidableEq Edge]
    (Erow : Row → Finset Edge) (S : Finset Row)
    (hS : S.card = 7)
    (hlt : (S.biUnion Erow).card < S.card)
    (hmin : ∀ T, T ⊂ S → T.card ≤ (T.biUnion Erow).card)
    (h4 : ∀ r ∈ S, 4 ≤ (Erow r).card)
    (hnot5 : ∀ r ∈ S, (Erow r).card ≠ 5)
    (hnot6 : ∀ r ∈ S, (Erow r).card ≠ 6)
    (hinj : Set.InjOn Erow S) :
    ∃ U : Finset Edge, ∃ C : FourUniformF5Core Row Edge,
      U = S.biUnion Erow ∧ C.rows = S ∧ C.edges = U ∧ C.supp = Erow := by
  obtain ⟨hcard, hnoPrivate⟩ :=
    Ell5CSReduction.minimal_hall_obstruction_no_private_edge Erow S hlt hmin
  let U : Finset Edge := S.biUnion Erow
  have hU : U.card = 6 := by
    dsimp [U]
    omega
  have hsub : ∀ r ∈ S, Erow r ⊆ U := by
    intro r hr
    dsimp [U]
    exact Finset.subset_biUnion_of_mem Erow hr
  have hrow4 : ∀ r ∈ S, (Erow r).card = 4 := by
    intro r hr
    have hle : (Erow r).card ≤ U.card := Finset.card_le_card (hsub r hr)
    have hge : 4 ≤ (Erow r).card := h4 r hr
    have hn5 : (Erow r).card ≠ 5 := hnot5 r hr
    have hn6 : (Erow r).card ≠ 6 := hnot6 r hr
    omega
  exact fourUniformF5Core_of_minimal_obstruction Erow S hS hlt hmin hrow4 hinj

/-- T7 glue theorem with the row-size facts separated.  The only graph-specific
row-size input not already compiled is the no-six-support clause. -/
theorem no_card_seven_violator_of_no_realizable_f5_core_no_large_rows
    {Row Edge : Type*} [DecidableEq Row] [DecidableEq Edge]
    (Realizable : FourUniformF5Core Row Edge → Prop)
    (hNo : NoRealizableF5Core Realizable)
    (Erow : Row → Finset Edge) (S : Finset Row)
    (hS : S.card = 7)
    (hlt : (S.biUnion Erow).card < S.card)
    (hmin : ∀ T, T ⊂ S → T.card ≤ (T.biUnion Erow).card)
    (h4 : ∀ r ∈ S, 4 ≤ (Erow r).card)
    (hnot5 : ∀ r ∈ S, (Erow r).card ≠ 5)
    (hnot6 : ∀ r ∈ S, (Erow r).card ≠ 6)
    (hinj : Set.InjOn Erow S)
    (hrealize :
      ∀ U C, U = S.biUnion Erow → C.rows = S → C.edges = U → C.supp = Erow →
        Realizable C) :
    False := by
  obtain ⟨U, C, hU, hCrows, hCedges, hCsupp⟩ :=
    fourUniformF5Core_of_minimal_obstruction_no_large_rows Erow S hS hlt hmin h4 hnot5 hnot6 hinj
  exact hNo C (hrealize U C hU hCrows hCedges hCsupp)
/-- Shape-artifact predicate for the six-support gate: a distinct four-edge row
support cannot be contained in a six-edge row support.  The exact shape script
`_codex_ell5_six_support_shapes.py` checks this for all two-geodesic six-edge
support shapes. -/
def NoFourSupportInsideSixSupport {Row Edge : Type*} [DecidableEq Row] [DecidableEq Edge]
    (Erow : Row → Finset Edge) (S : Finset Row) : Prop :=
  ∀ a ∈ S, ∀ b ∈ S, a ≠ b → (Erow a).card = 6 → (Erow b).card = 4 →
    Erow b ⊆ Erow a → False

/-- In a size-seven minimal obstruction, the six-support shape artifact rules
out six-edge row supports.  If one row filled the whole six-edge total support,
injectivity makes every other row non-full; with support size five already
ruled out, any other row is a four-edge row contained in the six-edge row,
contradicting `NoFourSupportInsideSixSupport`. -/
theorem no_six_row_in_minimal_obstruction_of_shape_gate
    {Row Edge : Type*} [DecidableEq Row] [DecidableEq Edge]
    (Erow : Row → Finset Edge) (S : Finset Row)
    (hS : S.card = 7)
    (hlt : (S.biUnion Erow).card < S.card)
    (hmin : ∀ T, T ⊂ S → T.card ≤ (T.biUnion Erow).card)
    (h4 : ∀ r ∈ S, 4 ≤ (Erow r).card)
    (hnot5 : ∀ r ∈ S, (Erow r).card ≠ 5)
    (hinj : Set.InjOn Erow S)
    (hshape : NoFourSupportInsideSixSupport Erow S) :
    ∀ r ∈ S, (Erow r).card ≠ 6 := by
  intro a ha h6
  obtain ⟨hcard, hnoPrivate⟩ :=
    Ell5CSReduction.minimal_hall_obstruction_no_private_edge Erow S hlt hmin
  let U : Finset Edge := S.biUnion Erow
  have hU : U.card = 6 := by
    dsimp [U]
    omega
  have hsub : ∀ r ∈ S, Erow r ⊆ U := by
    intro r hr
    dsimp [U]
    exact Finset.subset_biUnion_of_mem Erow hr
  have haU : Erow a = U := by
    exact Finset.eq_of_subset_of_card_le (hsub a ha) (by rw [h6, hU])
  have heraseCard : (S.erase a).card = 6 := by
    rw [Finset.card_erase_of_mem ha]
    omega
  have heraseNonempty : (S.erase a).Nonempty := by
    exact Finset.card_pos.mp (by omega)
  obtain ⟨b, hbErase⟩ := heraseNonempty
  have hba : b ≠ a := (Finset.mem_erase.mp hbErase).1
  have hb : b ∈ S := (Finset.mem_erase.mp hbErase).2
  have hbLe : (Erow b).card ≤ 6 := by
    calc
      (Erow b).card ≤ U.card := Finset.card_le_card (hsub b hb)
      _ = 6 := hU
  have hbNot6 : (Erow b).card ≠ 6 := by
    intro hb6
    have hbU : Erow b = U :=
      Finset.eq_of_subset_of_card_le (hsub b hb) (by rw [hb6, hU])
    have hEq : Erow b = Erow a := hbU.trans haU.symm
    exact hba (hinj hb ha hEq)
  have hb4 : (Erow b).card = 4 := by
    have hbGe : 4 ≤ (Erow b).card := h4 b hb
    have hbNot5 : (Erow b).card ≠ 5 := hnot5 b hb
    omega
  exact hshape a ha b hb hba.symm h6 hb4 (by rw [haU]; exact hsub b hb)

/-- T7 glue theorem using the six-support shape gate instead of taking `hnot6`
as a primitive hypothesis. -/
theorem no_card_seven_violator_of_no_realizable_f5_core_shape_gate
    {Row Edge : Type*} [DecidableEq Row] [DecidableEq Edge]
    (Realizable : FourUniformF5Core Row Edge → Prop)
    (hNo : NoRealizableF5Core Realizable)
    (Erow : Row → Finset Edge) (S : Finset Row)
    (hS : S.card = 7)
    (hlt : (S.biUnion Erow).card < S.card)
    (hmin : ∀ T, T ⊂ S → T.card ≤ (T.biUnion Erow).card)
    (h4 : ∀ r ∈ S, 4 ≤ (Erow r).card)
    (hnot5 : ∀ r ∈ S, (Erow r).card ≠ 5)
    (hinj : Set.InjOn Erow S)
    (hshape : NoFourSupportInsideSixSupport Erow S)
    (hrealize :
      ∀ U C, U = S.biUnion Erow → C.rows = S → C.edges = U → C.supp = Erow →
        Realizable C) :
    False := by
  exact no_card_seven_violator_of_no_realizable_f5_core_no_large_rows Realizable hNo Erow S
    hS hlt hmin h4 hnot5
    (no_six_row_in_minimal_obstruction_of_shape_gate Erow S hS hlt hmin h4 hnot5 hinj hshape)
    hinj hrealize
#print axioms fourUniformF5Core_of_minimal_obstruction
#print axioms no_six_row_in_minimal_obstruction_of_shape_gate
#print axioms no_card_seven_violator_of_no_realizable_f5_core_shape_gate
#print axioms fourUniformF5Core_of_minimal_obstruction_no_large_rows
#print axioms no_card_seven_violator_of_no_realizable_f5_core
#print axioms no_card_seven_violator_of_no_realizable_f5_core_no_large_rows

end Ell5F5LiftInterface
end Erdos23Delta0







