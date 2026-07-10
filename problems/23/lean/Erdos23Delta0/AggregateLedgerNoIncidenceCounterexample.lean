import Erdos23Delta0.RootLayerHalfSqueeze
import Erdos23Delta0.Gamma.FullBankPortSinks
import Erdos23Delta0.MaxCutVertexIneq

/-!
# Aggregate ledger data does not determine port incidence

`FullBankGlobalPackage.Checked` contains aggregate token/spend bookkeeping but
no relation between wall ports and ledger tokens.  This file gives an exact
finite countermodel: a checked empty aggregate package coexists with a wall
whose two rows cover its positive atom twice, yet whose port has no legal sink
and whose checked dual has a strict gap.

The example does not model a real extractor.  Its purpose is narrower: no
theorem can derive `HalfLayerRouted` from the present aggregate package fields
alone.  A typed, checked port-to-token incidence adapter is logically needed.
-/

namespace Erdos23Delta0
namespace AggregateLedgerNoIncidenceCounterexample

open scoped BigOperators
open CertGraph
open Gamma.FullBankToLengthSurplusCharge
open Wall
open MaxCutVertexIneq

def emptyGraph : GraphData := { n := 0, edges := [] }

def emptyCut : CutData := { side := [] }

def emptyRows : RowDB := { rowList := [] }

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

def strictDual : Dual noIncidenceWall where
  alpha := fun _ => 1 / 3
  beta := fun f => nomatch f
  gamma := fun _ => 1 / 3
  delta := fun _ => 0

theorem strictDual_checked : strictDual.Checked := by
  refine
    { alpha_nonneg := by intro a; cases a; norm_num [strictDual]
      beta_nonneg := by intro f; exact PEmpty.elim f
      gamma_nonneg := by intro p; cases p <;> norm_num [strictDual]
      delta_nonneg := by intro s; cases s; norm_num [strictDual]
      cap_nonneg := by intro s; cases s; change (0 : ℚ) ≤ 0; norm_num
      d1 := ?_
      d2 := ?_ }
  · intro X
    cases X <;>
      simp [cutAlpha, cutBeta, cutGamma, noIncidenceWall, strictDual]
  · intro _ _ hlegal
    exact False.elim hlegal

theorem strictDual_strictGap : strictDual.StrictGap := by
  simp [Dual.StrictGap, totalAlpha, totalBeta, totalDeltaCap,
    noIncidenceWall, strictDual]

def twoWalls : Fin 2 → noIncidenceWall.Cut := fun i => decide (i = 1)

def petalShore (i : Fin 2) : Finset (Fin 4) :=
  if i = 0 then {0} else {1}

def portEdge : noIncidenceWall.Port → Sym2 (Fin 4)
  | false => s(0, 2)
  | true => s(1, 3)

theorem petalShore_pairwise_disjoint :
    ∀ i j, i ≠ j → Disjoint (petalShore i) (petalShore j) := by
  intro i j hij
  fin_cases i <;> fin_cases j <;>
    simp_all [petalShore]

theorem port_is_actual_boundary :
    ∀ i p,
      noIncidenceWall.cutPort (twoWalls i) p =
        if edgeBoundary (petalShore i) (portEdge p) = true then 1 else 0 := by
  decide

theorem positiveAlpha_twoCover :
    ∀ a : noIncidenceWall.Atom, 0 < strictDual.alpha a →
      ∑ i : Fin 2, noIncidenceWall.cov (twoWalls i) a = 2 := by
  intro a _
  cases a
  change (∑ _i : Fin 2, (1 : ℚ)) = 2
  norm_num

theorem no_halfLayerRouted :
    ¬ Nonempty (HalfLayerRouted noIncidenceWall twoWalls) := by
  rintro ⟨routed⟩
  exact
    (noStrictDual_of_halfLayerTwoCover strictDual strictDual_checked twoWalls
      positiveAlpha_twoCover routed) strictDual_strictGap

/-- Exact logical separation: aggregate package checking alone cannot create
the missing wall-port routing. -/
theorem checkedAggregatePackage_and_noHalfLayerRouting :
    emptyPackage.Checked ∧
      ¬ Nonempty (HalfLayerRouted noIncidenceWall twoWalls) :=
  ⟨emptyPackage_checked, no_halfLayerRouted⟩

#print axioms emptyPackage_checked
#print axioms strictDual_checked
#print axioms strictDual_strictGap
#print axioms petalShore_pairwise_disjoint
#print axioms port_is_actual_boundary
#print axioms no_halfLayerRouted
#print axioms checkedAggregatePackage_and_noHalfLayerRouting

end AggregateLedgerNoIncidenceCounterexample
end Erdos23Delta0
