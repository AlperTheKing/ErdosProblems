import Erdos23Delta0.GammaAggregation

/-!
# Full-bank global ledger to length-surplus charge

This module implements the bookkeeping side of `WIRING_SPECS_GPTPRO.md`
Spec 1.  It does not assert existence of the full-bank wall certificate.
Instead it defines the eta-free global ledger package and proves that a checked
package implies the length-surplus aggregation bound

`lengthSurplusGD rows ≤ 25 * etaQ G c`.

Spendable cap kinds are exactly `door`, `vertexSlack`, `c5Base`, and `prune`.
There is deliberately no eta token constructor.
-/

namespace Erdos23Delta0
namespace Gamma
namespace FullBankToLengthSurplusCharge

open CertGraph
open GammaAggregation
open Finset

/-- Spendable full-bank cap kinds.  There is intentionally no eta kind. -/
inductive CapKind where
  | door
  | vertexSlack
  | c5Base
  | prune
deriving DecidableEq, Repr

/-- Rational view of one checked local full-bank relaxed-cover bundle. -/
structure FullBankRelaxedCoverBundleView where
  demandQ : ℚ
  doorCapQ : ℚ
  vertexSlackCapQ : ℚ
  c5BaseCapQ : ℚ
  pruneCapQ : ℚ
deriving Repr

namespace FullBankRelaxedCoverBundleView

def rhsQ (V : FullBankRelaxedCoverBundleView) : ℚ :=
  V.doorCapQ + V.vertexSlackCapQ + V.c5BaseCapQ + V.pruneCapQ

/-- Local view checker soundness obligations. -/
structure Checked (V : FullBankRelaxedCoverBundleView) : Prop where
  demand_nonneg : 0 ≤ V.demandQ
  door_nonneg : 0 ≤ V.doorCapQ
  vertexSlack_nonneg : 0 ≤ V.vertexSlackCapQ
  c5Base_nonneg : 0 ≤ V.c5BaseCapQ
  prune_nonneg : 0 ≤ V.pruneCapQ
  demand_le_rhs : V.demandQ ≤ V.rhsQ

theorem demand_le_cap {V : FullBankRelaxedCoverBundleView} (h : V.Checked) :
    V.demandQ ≤ V.rhsQ :=
  h.demand_le_rhs

theorem rhs_nonneg {V : FullBankRelaxedCoverBundleView} (h : V.Checked) :
    0 ≤ V.rhsQ := by
  unfold rhsQ
  linarith [h.door_nonneg, h.vertexSlack_nonneg, h.c5Base_nonneg, h.prune_nonneg]

end FullBankRelaxedCoverBundleView

/-- One globally named capacity token.  The `(comp, kind, sourceId)` uniqueness
condition lives in `Checked`. -/
structure LedgerToken (componentCount : Nat) where
  comp : Fin componentCount
  kind : CapKind
  sourceId : Nat
  capQ : ℚ
deriving Repr

/-- Global token ledger and spend matrix.  The two slack families are
non-spendable reserves, as required by the spec. -/
structure GlobalLedgerData (componentCount localCount tokenCount : Nat) where
  token : Fin tokenCount → LedgerToken componentCount
  spendQ : Fin localCount → Fin tokenCount → ℚ
  componentReserveSlackQ : Fin componentCount → ℚ
  superadditivitySlackQ : ℚ

namespace GlobalLedgerData

variable {componentCount localCount tokenCount : Nat}

def spendOfLocal (L : GlobalLedgerData componentCount localCount tokenCount)
    (l : Fin localCount) : ℚ :=
  ∑ t : Fin tokenCount, L.spendQ l t

def spendOfToken (L : GlobalLedgerData componentCount localCount tokenCount)
    (t : Fin tokenCount) : ℚ :=
  ∑ l : Fin localCount, L.spendQ l t

def spendOfKindLocal (L : GlobalLedgerData componentCount localCount tokenCount)
    (l : Fin localCount) (k : CapKind) : ℚ :=
  ∑ t : Fin tokenCount, if (L.token t).kind = k then L.spendQ l t else 0

def tokenCapTotal (L : GlobalLedgerData componentCount localCount tokenCount) : ℚ :=
  ∑ t : Fin tokenCount, (L.token t).capQ

def tokenCapInComponent
    (L : GlobalLedgerData componentCount localCount tokenCount)
    (comp : Fin componentCount) : ℚ :=
  ∑ t : Fin tokenCount, if (L.token t).comp = comp then (L.token t).capQ else 0

def totalSpendByLocal
    (L : GlobalLedgerData componentCount localCount tokenCount) : ℚ :=
  ∑ l : Fin localCount, L.spendOfLocal l

def totalSpendByToken
    (L : GlobalLedgerData componentCount localCount tokenCount) : ℚ :=
  ∑ t : Fin tokenCount, L.spendOfToken t

theorem totalSpendByLocal_eq_totalSpendByToken
    (L : GlobalLedgerData componentCount localCount tokenCount) :
    L.totalSpendByLocal = L.totalSpendByToken := by
  unfold totalSpendByLocal totalSpendByToken spendOfLocal spendOfToken
  exact Finset.sum_comm

end GlobalLedgerData

/-- One local cover with a component owner and the local row surplus it owns. -/
structure FullBankLocalCover (componentCount : Nat) where
  comp : Fin componentCount
  surplusInLocalQ : ℚ
  view : FullBankRelaxedCoverBundleView
deriving Repr

/-- Global full-bank package.  The package carries the component/local row
ownership tables even though this bookkeeping theorem only needs their
aggregate checked consequences. -/
structure FullBankGlobalPackage (G : GraphData) (c : CutData) (rows : RowDB) where
  componentCount : Nat
  localCount : Nat
  tokenCount : Nat
  compN : Fin componentCount → ℚ
  componentRowCountQ : Fin componentCount → ℚ
  compOfRow : Fin rows.rowList.length → Fin componentCount
  localOfRow : Fin rows.rowList.length → Fin localCount
  localCover : Fin localCount → FullBankLocalCover componentCount
  ledger : GlobalLedgerData componentCount localCount tokenCount

namespace FullBankGlobalPackage

variable {G : GraphData} {c : CutData} {rows : RowDB}

def localSurplusTotal (P : FullBankGlobalPackage G c rows) : ℚ :=
  ∑ l : Fin P.localCount, (P.localCover l).surplusInLocalQ

def localDemandTotal (P : FullBankGlobalPackage G c rows) : ℚ :=
  ∑ l : Fin P.localCount, (P.localCover l).view.demandQ

def localCapTotal (P : FullBankGlobalPackage G c rows) : ℚ :=
  ∑ l : Fin P.localCount, (P.localCover l).view.rhsQ

def localSpendTotal (P : FullBankGlobalPackage G c rows) : ℚ :=
  P.ledger.totalSpendByLocal

def tokenCapTotal (P : FullBankGlobalPackage G c rows) : ℚ :=
  P.ledger.tokenCapTotal

def componentTokenCapTotal (P : FullBankGlobalPackage G c rows) : ℚ :=
  ∑ comp : Fin P.componentCount, P.ledger.tokenCapInComponent comp

def componentResidualQ (P : FullBankGlobalPackage G c rows)
    (comp : Fin P.componentCount) : ℚ :=
  P.compN comp ^ 2 - 25 * P.componentRowCountQ comp

def componentResidualTotal (P : FullBankGlobalPackage G c rows) : ℚ :=
  ∑ comp : Fin P.componentCount, P.componentResidualQ comp

/-- Exact checker/soundness obligations for the global package.  The low-level
fields are included for auditability; the final soundness proof uses their
aggregate consequences plus reserve identities. -/
structure Checked (P : FullBankGlobalPackage G c rows) : Prop where
  rows_length_eq_badCount : rows.rowList.length = badCount G c
  row_length_ge_five :
    ∀ i : Fin rows.rowList.length, 5 ≤ (rows.rowList.get i).length
  row_local_component :
    ∀ i : Fin rows.rowList.length, (P.localCover (P.localOfRow i)).comp = P.compOfRow i
  local_view_checked :
    ∀ l : Fin P.localCount, ((P.localCover l).view).Checked
  surplusInLocal_le_demand :
    ∀ l : Fin P.localCount, (P.localCover l).surplusInLocalQ ≤ (P.localCover l).view.demandQ
  localCap_eq_kindSpends :
    ∀ l : Fin P.localCount,
      (P.localCover l).view.doorCapQ = P.ledger.spendOfKindLocal l CapKind.door ∧
      (P.localCover l).view.vertexSlackCapQ = P.ledger.spendOfKindLocal l CapKind.vertexSlack ∧
      (P.localCover l).view.c5BaseCapQ = P.ledger.spendOfKindLocal l CapKind.c5Base ∧
      (P.localCover l).view.pruneCapQ = P.ledger.spendOfKindLocal l CapKind.prune
  localCap_eq_spendOfLocal :
    ∀ l : Fin P.localCount, (P.localCover l).view.rhsQ = P.ledger.spendOfLocal l
  spend_nonneg :
    ∀ l : Fin P.localCount, ∀ t : Fin P.tokenCount, 0 ≤ P.ledger.spendQ l t
  tokenCap_nonneg :
    ∀ t : Fin P.tokenCount, 0 ≤ (P.ledger.token t).capQ
  no_double_spend :
    ∀ t : Fin P.tokenCount, P.ledger.spendOfToken t ≤ (P.ledger.token t).capQ
  no_cross_component_spend :
    ∀ l : Fin P.localCount, ∀ t : Fin P.tokenCount,
      0 < P.ledger.spendQ l t → (P.localCover l).comp = (P.ledger.token t).comp
  token_source_unique :
    ∀ t u : Fin P.tokenCount,
      (P.ledger.token t).comp = (P.ledger.token u).comp →
      (P.ledger.token t).kind = (P.ledger.token u).kind →
      (P.ledger.token t).sourceId = (P.ledger.token u).sourceId →
      t = u
  lengthSurplus_eq_localSurplus :
    lengthSurplusGD rows = P.localSurplusTotal
  tokenCapTotal_eq_componentTokenCapTotal :
    P.tokenCapTotal = P.componentTokenCapTotal
  componentReserveSlack_nonneg :
    ∀ comp : Fin P.componentCount, 0 ≤ P.ledger.componentReserveSlackQ comp
  componentReserveIdentity :
    ∀ comp : Fin P.componentCount,
      P.ledger.tokenCapInComponent comp + P.ledger.componentReserveSlackQ comp =
        P.componentResidualQ comp
  componentRowCountSum :
    (∑ comp : Fin P.componentCount, P.componentRowCountQ comp) =
      (badCount G c : ℚ)
  superadditivitySlack_nonneg :
    0 ≤ P.ledger.superadditivitySlackQ
  superadditivityIdentity :
    (∑ comp : Fin P.componentCount, P.compN comp ^ 2) +
      P.ledger.superadditivitySlackQ = (G.n : ℚ) ^ 2

theorem localSurplus_le_localDemand
    {P : FullBankGlobalPackage G c rows} (h : P.Checked) :
    P.localSurplusTotal ≤ P.localDemandTotal := by
  unfold localSurplusTotal localDemandTotal
  exact Finset.sum_le_sum (fun l _ => h.surplusInLocal_le_demand l)

theorem localDemand_le_localCap
    {P : FullBankGlobalPackage G c rows} (h : P.Checked) :
    P.localDemandTotal ≤ P.localCapTotal := by
  unfold localDemandTotal localCapTotal
  exact Finset.sum_le_sum
    (fun l _ => FullBankRelaxedCoverBundleView.demand_le_cap (h.local_view_checked l))

theorem localCap_eq_localSpend
    {P : FullBankGlobalPackage G c rows} (h : P.Checked) :
    P.localCapTotal = P.localSpendTotal := by
  unfold localCapTotal localSpendTotal
  apply Finset.sum_congr rfl
  intro l _
  exact h.localCap_eq_spendOfLocal l

theorem localSpend_eq_tokenSpend
    (P : FullBankGlobalPackage G c rows) :
    P.localSpendTotal = P.ledger.totalSpendByToken := by
  unfold localSpendTotal
  exact P.ledger.totalSpendByLocal_eq_totalSpendByToken

theorem tokenSpend_le_tokenCap
    {P : FullBankGlobalPackage G c rows} (h : P.Checked) :
    P.ledger.totalSpendByToken ≤ P.tokenCapTotal := by
  unfold GlobalLedgerData.totalSpendByToken tokenCapTotal GlobalLedgerData.tokenCapTotal
  exact Finset.sum_le_sum (fun t _ => h.no_double_spend t)

theorem componentTokenCap_le_componentResidual
    {P : FullBankGlobalPackage G c rows} (h : P.Checked) :
    P.componentTokenCapTotal ≤ P.componentResidualTotal := by
  unfold componentTokenCapTotal componentResidualTotal
  apply Finset.sum_le_sum
  intro comp _
  have hid := h.componentReserveIdentity comp
  have hnn := h.componentReserveSlack_nonneg comp
  linarith

theorem componentResidual_le_globalResidual
    {P : FullBankGlobalPackage G c rows} (h : P.Checked) :
    P.componentResidualTotal ≤ (G.n : ℚ) ^ 2 - 25 * (badCount G c : ℚ) := by
  unfold componentResidualTotal componentResidualQ
  rw [Finset.sum_sub_distrib]
  have hmul :
      (∑ comp : Fin P.componentCount, 25 * P.componentRowCountQ comp) =
        25 * (∑ comp : Fin P.componentCount, P.componentRowCountQ comp) := by
    rw [Finset.mul_sum]
  rw [hmul, h.componentRowCountSum]
  have hsq : (∑ comp : Fin P.componentCount, P.compN comp ^ 2) ≤ (G.n : ℚ) ^ 2 := by
    linarith [h.superadditivityIdentity, h.superadditivitySlack_nonneg]
  linarith

/-- Main Spec1 bookkeeping theorem: a checked global full-bank package pays the
entire length surplus out of legal local caps and component reserves. -/
theorem fullBankGlobalPackage_sound
    {P : FullBankGlobalPackage G c rows} (h : P.Checked) :
    lengthSurplusGD rows ≤ 25 * etaQ G c := by
  have h0 : lengthSurplusGD rows = P.localSurplusTotal :=
    h.lengthSurplus_eq_localSurplus
  have h1 := localSurplus_le_localDemand h
  have h2 := localDemand_le_localCap h
  have h3 := localCap_eq_localSpend h
  have h4 := localSpend_eq_tokenSpend P
  have h5 := tokenSpend_le_tokenCap h
  have h6 : P.tokenCapTotal ≤ P.componentTokenCapTotal := by
    rw [h.tokenCapTotal_eq_componentTokenCapTotal]
  have h7 := componentTokenCap_le_componentResidual h
  have h8 := componentResidual_le_globalResidual h
  have heta :
      (G.n : ℚ) ^ 2 - 25 * (badCount G c : ℚ) = 25 * etaQ G c := by
    unfold etaQ
    ring
  rw [h0]
  rw [← heta]
  linarith

/-- Γ upper bound via the existing corrected aggregation theorem. -/
theorem gammaUpper_from_fullBankGlobalPackage
    {P : FullBankGlobalPackage G c rows} (h : P.Checked) :
    gammaOfGD G c rows ≤ (G.n : ℚ) ^ 2 :=
  gammaUpper_from_lengthSurplus h.rows_length_eq_badCount
    (fullBankGlobalPackage_sound h)

end FullBankGlobalPackage

end FullBankToLengthSurplusCharge
end Gamma
end Erdos23Delta0
