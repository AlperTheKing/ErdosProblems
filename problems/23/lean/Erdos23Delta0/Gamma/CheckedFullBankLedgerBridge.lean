import Erdos23Delta0.Gamma.CheckedMicroReservationLedger
import Erdos23Delta0.Gamma.CheckedFullBankMicroFlow

/-!
# Bridge from the serialized R32 ledger to the full-bank microflow ledger

`CheckedMicroReservationLedger.Data` is the certificate-facing ledger.  The
microflow module uses an arbitrary finite source and term type.  This file
proves that one compatible serialized ledger supplies the latter view; the
two exclusivity checks are therefore not independent hypotheses downstream.

Graph legality and existence of the collision/hit assignments remain in
`CheckedFullBankMicroFlow.CheckedFullBankMicroFlow` and are not constructed
here.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CheckedFullBankLedgerBridge

open TypedFullBankSources

namespace Serialized

open CheckedMicroReservationLedger

/-- The structural physical-key representation used by the microflow file. -/
def physicalKeyEmbedding (vertexCount : Nat) :
    PhysicalHalfKey vertexCount ↪
      CheckedFullBankMicroFlow.FreeHalfKey (PhysicalBaseKey vertexCount) where
  toFun key := (key.baseKey, key.half)
  inj' := by
    intro first second h
    cases first
    cases second
    simp_all [PhysicalHalfKey.baseKey]

end Serialized

open CheckedFullBankMicroFlow

section

variable {vertexCount componentCount sourceCount termCount : Nat}
variable {Debit Hit DoorKey VertexKey PruneKey : Type*}
  [Fintype Debit] [Fintype Hit]

abbrev SerializedLedger
    (vertexCount componentCount sourceCount termCount : Nat)
    (DoorKey VertexKey PruneKey : Type*) :=
  CheckedMicroReservationLedger.Data
    vertexCount componentCount sourceCount termCount
    DoorKey VertexKey Empty PruneKey

abbrev MicroFlow
    (vertexCount componentCount sourceCount termCount : Nat)
    (Debit Hit DoorKey VertexKey PruneKey : Type*) :=
  FullBankMicroFlowData
    (Fin vertexCount) (Fin sourceCount)
    (CheckedMicroReservationLedger.PhysicalBaseKey vertexCount)
    Debit Hit (Fin componentCount) DoorKey VertexKey PruneKey (Fin termCount)

abbrev MicroLedger (sourceCount termCount : Nat) :=
  MicroReservationLedgerData (Fin sourceCount) (Fin termCount)

/-- Literal agreement between the serialized certificate and the microflow
view.  Every equality is checkable finite data; no graph theorem is hidden in
the bridge. -/
structure Compatible
    (D : SerializedLedger vertexCount componentCount sourceCount termCount
      DoorKey VertexKey PruneKey)
    (F : MicroFlow vertexCount componentCount sourceCount termCount Debit Hit
      DoorKey VertexKey PruneKey)
    (L : MicroLedger sourceCount termCount) : Prop where
  source_key : ∀ source,
    F.freeKey source =
      Serialized.physicalKeyEmbedding vertexCount (D.sourceKey source)
  raw_free_spend : ∀ source,
    L.rawFreeSpendQ source = D.rawFreeSpend source
  tokenized_spend : ∀ source,
    FullBankMicroFlowData.tokenizedSpendQ F source = D.tokenizedSpend source
  term_component : ∀ term,
    F.bankComp term = (D.term term).comp
  term_source : ∀ term,
    (F.bankSource term).toCapSource = (D.term term).source
  term_capacity : ∀ term,
    FullBankMicroFlowData.officialCapQ F term = (D.term term).capQ
  prior_spend : ∀ term,
    L.priorSpendQ term = D.priorSpend term
  local_reserve : ∀ term,
    L.localReserveQ term = D.localReserve term
  new_spend : ∀ term,
    FullBankMicroFlowData.newSpendQ F term = D.newSpend term
  reservation_recorded : ∀ source,
    F.reservedB source = true → 1 ≤ L.rawFreeSpendQ source

namespace Compatible

variable
  {D : SerializedLedger vertexCount componentCount sourceCount termCount
    DoorKey VertexKey PruneKey}
  {F : MicroFlow vertexCount componentCount sourceCount termCount Debit Hit
    DoorKey VertexKey PruneKey}
  {L : MicroLedger sourceCount termCount}

private theorem rawFreeSpendAt_source
    (hD : D.Sound) (source : Fin sourceCount) :
    D.rawFreeSpendAtKey (D.sourceKey source) = D.rawFreeSpend source := by
  classical
  unfold CheckedMicroReservationLedger.Data.rawFreeSpendAtKey
  have hiff : ∀ other : Fin sourceCount,
      D.sourceKey other = D.sourceKey source ↔ other = source := by
    intro other
    constructor
    · exact D.source_eq_of_key_eq hD
    · intro heq
      exact congrArg D.sourceKey heq
  simp [hiff]

private theorem tokenizedSpendAt_source
    (hD : D.Sound) (source : Fin sourceCount) :
    D.tokenizedSpendAtKey (D.sourceKey source) = D.tokenizedSpend source := by
  classical
  unfold CheckedMicroReservationLedger.Data.tokenizedSpendAtKey
  have hiff : ∀ other : Fin sourceCount,
      D.sourceKey other = D.sourceKey source ↔ other = source := by
    intro other
    constructor
    · exact D.source_eq_of_key_eq hD
    · intro heq
      exact congrArg D.sourceKey heq
  simp [hiff]

/-- A compatible serialized R32 ledger supplies exactly the reservation view
required by the microflow soundness theorems. -/
theorem toMicroReservationLedger
    (hD : D.Sound) (h : Compatible D F L) :
    CheckedFullBankMicroFlow.CheckedMicroReservationLedger F L := by
  refine
    { rawFreeSpendQ_nonneg := ?_
      priorSpendQ_nonneg := ?_
      localReserveQ_nonneg := ?_
      reservation_recorded := h.reservation_recorded
      free_exclusive := ?_
      bank_exclusive := ?_ }
  · intro source
    rw [h.raw_free_spend source]
    exact hD.rawFreeSpend_nonneg source
  · intro term
    rw [h.prior_spend term]
    exact hD.priorSpend_nonneg term
  · intro term
    rw [h.local_reserve term]
    exact hD.localReserve_nonneg term
  · intro source
    have hexclusive :=
      hD.no_physical_half_double_spend (D.sourceKey source)
    rw [rawFreeSpendAt_source hD source,
      tokenizedSpendAt_source hD source] at hexclusive
    rw [h.raw_free_spend source, h.tokenized_spend source]
    exact hexclusive
  · intro term
    calc
      L.priorSpendQ term + L.localReserveQ term +
          FullBankMicroFlowData.newSpendQ F term =
          D.priorSpend term + D.localReserve term + D.newSpend term := by
            rw [h.prior_spend term, h.local_reserve term, h.new_spend term]
      _ ≤ (D.term term).capQ := hD.no_official_term_overspend term
      _ = FullBankMicroFlowData.officialCapQ F term :=
        (h.term_capacity term).symm

/-- The connected accounting chain: a checked serialized ledger plus a
checked graph-facing microflow yields both collision tokenization and the
typed full-bank local inequality. -/
theorem connectedSoundness
    (hD : D.Sound) (hcompat : Compatible D F L)
    (hF : CheckedFullBankMicroFlow F) :
    (∃ _residual : ResidualSourceTokenization.Data
        (V := Fin vertexCount)
        (Source := CheckedMicroReservationLedger.PhysicalBaseKey vertexCount)
        (Debit := Debit) (Slot := Empty) (Comp := Fin componentCount),
      2 * Fintype.card Debit ≤
        2 * Fintype.card
          (CheckedMicroReservationLedger.PhysicalBaseKey vertexCount)) ∧
      (L.fullBankView F).Checked := by
  let hL := toMicroReservationLedger hD hcompat
  refine ⟨?_, Soundness.fullBankView_checked hF hL⟩
  exact ⟨Soundness.toResidualSourceTokenization hF,
    Soundness.collision_card_budget hF⟩

end Compatible
end

#print axioms Compatible.toMicroReservationLedger
#print axioms Compatible.connectedSoundness

end CheckedFullBankLedgerBridge
end Gamma
end Erdos23Delta0
