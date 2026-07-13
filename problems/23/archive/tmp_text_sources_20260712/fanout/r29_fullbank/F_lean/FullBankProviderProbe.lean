import Erdos23Delta0.Ell5FullBankInterface
import Erdos23Delta0.Gamma.ActiveScopedMinimumExchange
import Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge

/-!
# R29 full-bank provider probe

This file freezes the two provider seams exposed by the R29 audit.  A finite
full-relation gate decides `FullRelationMatching`; the global Erdos bound needs
the strictly stronger `GlobalPackageProviderTarget`.
-/

namespace R29FullBankAudit

open Erdos23Delta0
open Erdos23Delta0.CertGraph
open Erdos23Delta0.Gamma.MinimumDemandRowSelection
open Erdos23Delta0.Gamma.CanonicalCollisionHall
open Erdos23Delta0.Gamma.ActiveScopedMinimumExchange

/-- Exact integer output expected from a Hall-shore checker. -/
structure ExactHallDefect where
  demand : Nat
  neighborhood : Nat
  defect : Nat
deriving Repr, DecidableEq

namespace ExactHallDefect

def Checked (w : ExactHallDefect) : Prop :=
  w.neighborhood < w.demand ∧ w.demand = w.neighborhood + w.defect

instance checkedDecidable (w : ExactHallDefect) : Decidable w.Checked := by
  unfold Checked
  infer_instance

def check (w : ExactHallDefect) : Bool :=
  decide w.Checked

theorem check_eq_true_iff (w : ExactHallDefect) :
    w.check = true ↔ w.Checked := by
  simp [check]

def r29AllAnchor : ExactHallDefect where
  demand := 19953
  neighborhood := 19925
  defect := 28

theorem r29AllAnchor_checked : r29AllAnchor.check = true := by
  norm_num [check, Checked, r29AllAnchor]

theorem r29AllAnchor_smallest_falsifier :
    r29AllAnchor.neighborhood < r29AllAnchor.demand ∧
      r29AllAnchor.demand = r29AllAnchor.neighborhood + r29AllAnchor.defect := by
  exact (check_eq_true_iff r29AllAnchor).mp r29AllAnchor_checked

end ExactHallDefect

/-- Relation-parametric matching surface.  An exact R29 four-pattern gate can
instantiate `rel` once all four source predicates have compiled definitions. -/
def FullRelationMatching
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads)
    (rel : Demand G c omega → FreeHalf G omega → Prop) : Prop :=
  ∃ assign : Demand G c omega → FreeHalf G omega,
    Function.Injective assign ∧ ∀ d, rel d (assign d)

def FullRelationHallCondition
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads)
    (rel : Demand G c omega → FreeHalf G omega → Prop)
    [DecidableRel rel] : Prop :=
  ∀ A : Finset (Demand G c omega),
    A.card ≤
      (Finset.univ.filter fun s : FreeHalf G omega =>
        ∃ d ∈ A, rel d s).card

theorem fullRelationMatching_iff_hall
    (G : GraphData) (c : CutData) {bads : List BadEdgeData}
    (omega : RowChoice bads)
    (rel : Demand G c omega → FreeHalf G omega → Prop)
    [DecidableRel rel] :
    FullRelationMatching G c omega rel ↔
      FullRelationHallCondition G c omega rel := by
  let hHall := Fintype.all_card_le_filter_rel_iff_exists_injective rel
  constructor
  · rintro ⟨assign, hinjective, hrel⟩
    apply hHall.mpr
    exact ⟨assign, hinjective, hrel⟩
  · intro h
    rcases hHall.mp h with ⟨assign, hinjective, hrel⟩
    exact ⟨assign, hinjective, hrel⟩

/-- The exact older LP-provider target.  Graph semantics fix `sep` and `dB`,
but this existential still requires the rational cut and routing data. -/
def RelaxedCoverProviderTarget
    {V JT ι : Type*} [Fintype V] [DecidableEq V]
    (G : SimpleGraph V) [Fintype G.edgeSet] (cut : V → Bool)
    (S F O : Finset (Sym2 V)) (J : Finset JT) (K : Finset ι)
    (Ufam : ι → Finset V) (inc : Sym2 V → JT → Prop) (kap : JT → ℚ) : Prop :=
  Nonempty
    (Ell5FullBankInterface.GraphFullBankRelaxedCoverCert
      G cut S F O J K Ufam inc kap)

/-- The first missing provider target on the accepted global-ledger route. -/
def GlobalPackageProviderTarget (G : GraphData) (c : CutData)
    (rows : RowDB) : Prop :=
  ∃ P : Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage G c rows,
    P.Checked

theorem gammaUpper_of_globalPackageProvider
    {G : GraphData} {c : CutData} {rows : RowDB}
    (h : GlobalPackageProviderTarget G c rows) :
    Erdos23Delta0.CertGraph.gammaOfGD G c rows ≤ (G.n : ℚ) ^ 2 := by
  rcases h with ⟨P, hP⟩
  exact Erdos23Delta0.Gamma.FullBankToLengthSurplusCharge.FullBankGlobalPackage.gammaUpper_from_fullBankGlobalPackage hP

#print axioms ExactHallDefect.check_eq_true_iff
#print axioms ExactHallDefect.r29AllAnchor_checked
#print axioms ExactHallDefect.r29AllAnchor_smallest_falsifier
#print axioms fullRelationMatching_iff_hall
#print axioms gammaUpper_of_globalPackageProvider

end R29FullBankAudit
