import Erdos23Delta0.CollisionTokenAssignment
import Erdos23Delta0.Ell5ActiveComponentBankHall
import Erdos23Delta0.Gamma.FullBankChargeCertProvider
import Erdos23Delta0.Gamma.CommonBlueExtendedMatching
import Erdos23Delta0.Gamma.TypedFullBankSources
import Erdos23Delta0.RootLayerHalfSqueeze

/-!
# Lead E: exact provider-seam probes

This file intentionally lives outside production.  It records only consequences
of the current compiled interfaces; it does not postulate the missing real graph
provider.
-/

namespace Erdos23Delta0
namespace LeadER29FullBank

open CertGraph
open Gamma
open Gamma.FullBankToLengthSurplusCharge
open Wall

/-- The exact proposition that the production aggregate wall still needs from
real graph semantics. -/
def HasCheckedGlobalPackage (G : GraphData) (c : CutData) (rows : RowDB) : Prop :=
  ∃ P : FullBankGlobalPackage G c rows, P.Checked

/-- Smallest honest real-graph provider target expressible by the current
production API.  `GoodCutData` carries max-cut, connected gamma-minimality,
row facts, and gamma/beta aggregation. -/
def RealGraphFullBankProvider : Prop :=
  ∀ (G : GraphData) (c : CutData) (rows : RowDB),
    checkGraph G = true → TriangleFree G → GoodCutData G c rows →
      HasCheckedGlobalPackage G c rows

/-- Once the missing provider exists, the already-compiled downstream theorem
gives the desired gamma bound without any further wall mathematics. -/
theorem gammaUpper_of_hasCheckedGlobalPackage
    {G : GraphData} {c : CutData} {rows : RowDB}
    (h : HasCheckedGlobalPackage G c rows) :
    gammaOfGD G c rows ≤ (G.n : ℚ) ^ 2 := by
  rcases h with ⟨P, hP⟩
  exact FullBankGlobalPackage.gammaUpper_from_fullBankGlobalPackage hP

/-- Exact downstream composition.  Its only non-bookkeeping input is the
real provider above. -/
theorem gammaUpper_of_realGraphFullBankProvider
    (provider : RealGraphFullBankProvider)
    {G : GraphData} {c : CutData} {rows : RowDB}
    (hGraph : checkGraph G = true) (hTri : TriangleFree G)
    (hGood : GoodCutData G c rows) :
    gammaOfGD G c rows ≤ (G.n : ℚ) ^ 2 :=
  gammaUpper_of_hasCheckedGlobalPackage
    (provider G c rows hGraph hTri hGood)

/-- Minimal finite matching-to-Hall adapter needed by any checked R29 source
class: an injective legal source choice with unit capacity proves every subset
Hall inequality.  This lemma is independent of the source's geometric meaning. -/
noncomputable def legalNbr
    {Port Token : Type*} [Fintype Token]
    (legal : Port → Token → Prop) (A : Finset Port) : Finset Token := by
  classical
  exact Finset.univ.filter (fun t => ∃ p ∈ A, legal p t)

theorem unitHall_of_injective_source
    {Port Token : Type*}
    [Fintype Port] [DecidableEq Port] [Fintype Token] [DecidableEq Token]
    (sourceOf : Port → Token) (legal : Port → Token → Prop) (capQ : Token → ℚ)
    (hsource : Function.Injective sourceOf)
    (hlegal : ∀ p, legal p (sourceOf p))
    (hunit : ∀ p, 1 ≤ capQ (sourceOf p))
    (hcap : ∀ t, 0 ≤ capQ t)
    (A : Finset Port) :
    (A.card : ℚ) ≤
      ∑ t ∈ legalNbr legal A, capQ t := by
  classical
  let I : Finset Token := A.image sourceOf
  let R : Finset Token := legalNbr legal A
  have hIR : I ⊆ R := by
    intro t ht
    rcases Finset.mem_image.mp ht with ⟨p, hpA, rfl⟩
    simp only [R, legalNbr, Finset.mem_filter, Finset.mem_univ, true_and]
    exact ⟨p, hpA, hlegal p⟩
  have hcard : I.card = A.card := by
    exact Finset.card_image_iff.mpr fun p _ q _ hpq => hsource hpq
  calc
    (A.card : ℚ) = ∑ t ∈ I, (1 : ℚ) := by simp [hcard]
    _ ≤ ∑ t ∈ I, capQ t := by
      exact Finset.sum_le_sum fun t ht => by
        rcases Finset.mem_image.mp ht with ⟨p, _hpA, rfl⟩
        exact hunit p
    _ ≤ ∑ t ∈ R, capQ t :=
      Finset.sum_le_sum_of_subset_of_nonneg hIR (fun t _ _ => hcap t)
    _ = ∑ t ∈ legalNbr legal A, capQ t := rfl

/-- The currently implemented typed own-Door checker is enough for the unit
Hall interface, provided token nonnegativity comes from the global ledger.
There is no analogous checked adapter yet for vertexSlack/c5Base/prune. -/
theorem ownEdgeDoor_unitHall
    {Port ExitEdgeKey VertexKey BaseKey PruneKey : Type*}
    {componentCount tokenCount : Nat}
    [Fintype Port] [DecidableEq Port] [Fintype (Fin tokenCount)]
    [DecidableEq ExitEdgeKey] [DecidableEq VertexKey]
    [DecidableEq BaseKey] [DecidableEq PruneKey]
    (D : TypedFullBankSources.OwnEdgeDoorSourceData
      Port ExitEdgeKey VertexKey BaseKey PruneKey componentCount tokenCount)
    (hD : D.Checked) (hcap : ∀ t, 0 ≤ D.hallCapQ t)
    (A : Finset Port) :
    (A.card : ℚ) ≤
      ∑ t ∈ legalNbr D.doorLegal A,
        D.hallCapQ t := by
  exact unitHall_of_injective_source D.doorOf D.doorLegal D.hallCapQ
    (D.doorOf_injective hD) (D.doorOf_legal hD)
    (D.one_le_door_hallCapQ hD) hcap A

/-- This is the furthest theorem the current corrected common-blue API can
derive without a bank-incidence adapter: a checked injective matching proves
the finite unit-capacity Hall condition on `FreeHalf` keys. -/
theorem commonBlueMatching_implies_hall
    {G : GraphData} {c : CutData}
    {bads : List BadEdgeData}
    {omega : Gamma.MinimumDemandRowSelection.RowChoice bads}
    (M : Gamma.CommonBlueExtendedMatching.Matching G c omega) :
    Gamma.CommonBlueExtendedMatching.HallCondition G c omega := by
  exact
    (Gamma.CommonBlueExtendedMatching.matching_nonempty_iff_hall
      G c omega).1 <| Nonempty.intro M

/-! A local copy of the production countermodel data is used so this standalone
probe can be compiled without writing an olean into the shared cache. -/

def emptyGraph : GraphData := { n := 0, edges := [] }

def emptyCut : CutData := { side := [] }

def emptyRows : RowDB := { rowList := [] }

def emptyChoice : Gamma.MinimumDemandRowSelection.RowChoice
    ([] : List BadEdgeData) :=
  fun i => Fin.elim0 i

/-- A literal corrected common-blue matching exists on the empty graph.  It
is used only to show that the matching interface and aggregate package fields
still do not determine wall-port incidence. -/
def emptyCommonBlueMatching :
    Gamma.CommonBlueExtendedMatching.Matching
      emptyGraph emptyCut emptyChoice where
  assign := fun d => by
    cases d with
    | inl h => exact Fin.elim0 h.1.owner
    | inr h => exact Fin.elim0 h.1
  injective := by
    intro a b
    cases a with
    | inl h => exact Fin.elim0 h.1.owner
    | inr h => exact Fin.elim0 h.1
  available := by
    intro d
    cases d with
    | inl h => exact Fin.elim0 h.1.owner
    | inr h => exact Fin.elim0 h.1

def emptyPackage : FullBankGlobalPackage emptyGraph emptyCut emptyRows where
  componentCount := 0
  localCount := 0
  tokenCount := 0
  compN := Fin.elim0
  componentRowCountQ := Fin.elim0
  compOfRow := Fin.elim0
  localOfRow := Fin.elim0
  localCover := Fin.elim0
  ledger :=
    { token := Fin.elim0
      spendQ := Fin.elim0
      componentReserveSlackQ := Fin.elim0
      superadditivitySlackQ := 0 }

theorem emptyPackage_checked : emptyPackage.Checked := by
  refine
    { rows_length_eq_badCount := by rfl
      row_length_ge_five := ?_
      row_local_component := ?_
      local_view_checked := ?_
      surplusInLocal_le_demand := ?_
      localCap_eq_kindSpends := ?_
      localCap_eq_spendOfLocal := ?_
      spend_nonneg := ?_
      tokenCap_nonneg := ?_
      no_double_spend := ?_
      no_cross_component_spend := ?_
      token_source_unique := ?_
      lengthSurplus_eq_localSurplus := by rfl
      tokenCapTotal_eq_componentTokenCapTotal := by rfl
      componentReserveSlack_nonneg := ?_
      componentReserveIdentity := ?_
      componentRowCountSum := by rfl
      superadditivitySlack_nonneg := by simp [emptyPackage]
      superadditivityIdentity := by simp [emptyPackage, emptyGraph] }
  all_goals intro i
  all_goals exact Fin.elim0 i

def noIncidenceWall : BankedWallLP where
  Cut := Bool
  Atom := PUnit
  Short := PEmpty
  Port := Bool
  Sink := PUnit
  cutFintype := inferInstance
  atomFintype := inferInstance
  shortFintype := inferInstance
  portFintype := inferInstance
  sinkFintype := inferInstance
  cov := fun _ _ => 1
  useShort := fun _ f => nomatch f
  cutPort := fun X p => if X = p then 1 else 0
  legal := fun _ _ => False
  legalDecidable := fun _ _ => inferInstance
  cap := fun _ => 0

def twoWalls : Fin 2 → noIncidenceWall.Cut := fun i => decide (i = 1)

theorem no_halfLayerRouted :
    ¬ Nonempty (HalfLayerRouted noIncidenceWall twoWalls) := by
  rintro ⟨R⟩
  have hzero : R.rho false PUnit.unit = 0 := by
    by_contra hne
    exact R.rho_legal false PUnit.unit hne
  have hroute := R.port_half_routed false
  simp [twoWalls, noIncidenceWall, hzero] at hroute
  norm_num at hroute

/-- Exact logical guardrail: the fields of `FullBankGlobalPackage.Checked` do
not determine legal wall-port incidence.  The compiled finite countermodel has
a checked aggregate package and no half-layer routing for its wall. -/
theorem checkedAggregatePackage_does_not_supply_portIncidence :
    ∃ (P : FullBankGlobalPackage
        emptyGraph emptyCut emptyRows),
      P.Checked ∧
        ¬ Nonempty
          (HalfLayerRouted
            noIncidenceWall twoWalls) := by
  exact ⟨emptyPackage, emptyPackage_checked, no_halfLayerRouted⟩

/-- No uniform eliminator from a checked aggregate package to this concrete
port-routing obligation can exist.  This is an interface-level statement, not
a graph-level counterexample. -/
theorem no_checkedAggregatePackage_to_portRouting :
    ¬ (∀ (P : FullBankGlobalPackage
          emptyGraph emptyCut emptyRows),
        P.Checked →
          Nonempty
            (HalfLayerRouted
              noIncidenceWall twoWalls)) := by
  intro h
  exact no_halfLayerRouted (h emptyPackage emptyPackage_checked)

/-- Even a corrected common-blue matching together with a checked aggregate
package does not determine legal wall incidence.  A theorem crossing this seam
must accept or construct additional typed source-to-sink data. -/
theorem no_commonBlueMatching_and_checkedPackage_to_portRouting :
    ¬ (Gamma.CommonBlueExtendedMatching.Matching
          emptyGraph emptyCut emptyChoice →
        emptyPackage.Checked →
        Nonempty (HalfLayerRouted noIncidenceWall twoWalls)) := by
  intro h
  exact no_halfLayerRouted (h emptyCommonBlueMatching emptyPackage_checked)

#print axioms gammaUpper_of_hasCheckedGlobalPackage
#print axioms gammaUpper_of_realGraphFullBankProvider
#print axioms unitHall_of_injective_source
#print axioms ownEdgeDoor_unitHall
#print axioms commonBlueMatching_implies_hall
#print axioms emptyPackage_checked
#print axioms emptyCommonBlueMatching
#print axioms no_halfLayerRouted
#print axioms checkedAggregatePackage_does_not_supply_portIncidence
#print axioms no_checkedAggregatePackage_to_portRouting
#print axioms no_commonBlueMatching_and_checkedPackage_to_portRouting

end LeadER29FullBank
end Erdos23Delta0
