import Erdos23Delta0.Gamma.MinimumDemandCollisionHall
import Erdos23Delta0.Gamma.TypedFullBankSources

/-!
# Checked micro-reservation ledger

This module implements the R32 exclusivity layer.  A physical free-half key is
the ordered pair of source vertices together with its half bit.  Proofs of
freeness, terminal witnesses, producer tags, and component labels are not part
of that key.  Thus all source patterns meet in one canonical namespace before
any spend is counted.

The checker enforces two independent capacity laws:

* raw free spend plus tokenized spend is at most one at every physical key;
* prior spend plus local reserve plus new spend is at most the official
  `capQ` of every typed bank term.

It also checks source deduplication, typed-term deduplication, and component
coherence for the two half bits of one ordered-pair base key.  Source-family
tags are audit data only: they create neither graph legality nor capacity.
Existence of graph-realized checked data remains an explicit hypothesis at the
end of the file.
-/

namespace Erdos23Delta0
namespace Gamma
namespace CheckedMicroReservationLedger

open scoped BigOperators
open CanonicalCollisionHall
open TypedFullBankSources

/-- The source relations whose union is deduplicated by physical key. -/
inductive SourceFamily where
  | p1
  | p2
  | p3
  | p4
  | p5
  | commonBlue
deriving DecidableEq, Fintype, Repr

/-- Canonical identity of one physical ordered-pair half.

The endpoint order is intentional: the existing `sameFirst` relation treats
`(x,y)` and `(y,x)` differently.  Only proof and producer metadata are erased.
-/
structure PhysicalHalfKey (vertexCount : Nat) where
  sourceX : Fin vertexCount
  sourceY : Fin vertexCount
  half : Fin 2
deriving DecidableEq, Fintype, Repr

/-- The ordered-pair base shared by its two physical half bits. -/
abbrev PhysicalBaseKey (vertexCount : Nat) :=
  Fin vertexCount × Fin vertexCount

namespace PhysicalHalfKey

def baseKey {vertexCount : Nat}
    (key : PhysicalHalfKey vertexCount) : PhysicalBaseKey vertexCount :=
  (key.sourceX, key.sourceY)

/-- Erase proof fields from the production `FreeHalf` source. -/
def ofFreeHalf
    {G : CertGraph.GraphData} {bads : List CertGraph.BadEdgeData}
    {omega : MinimumDemandRowSelection.RowChoice bads}
    (source : FreeHalf G omega) : PhysicalHalfKey G.n where
  sourceX := source.sourceX
  sourceY := source.sourceY
  half := source.half

/-- Canonicalization loses no physical identity; it erases only propositions. -/
theorem ofFreeHalf_injective
    {G : CertGraph.GraphData} {bads : List CertGraph.BadEdgeData}
    {omega : MinimumDemandRowSelection.RowChoice bads} :
    Function.Injective
      (ofFreeHalf (G := G) (bads := bads) (omega := omega)) := by
  intro source target h
  cases source with
  | mk sx sy sh sd sf =>
      cases target with
      | mk tx ty th td tf =>
          simp only [ofFreeHalf, PhysicalHalfKey.mk.injEq] at h
          rcases h with ⟨rfl, rfl, rfl⟩
          rfl

end PhysicalHalfKey

/-- One candidate source after the P1--P5/common-blue union is canonicalized.
The family tag records one checked origin but is not part of source identity. -/
structure SourceEntry (vertexCount componentCount : Nat) where
  family : SourceFamily
  key : PhysicalHalfKey vertexCount
  comp : Fin componentCount
deriving DecidableEq, Fintype, Repr

/-- Exact finite R32 ledger data.  All quantitative fields are rational. -/
structure Data
    (vertexCount componentCount sourceCount termCount : Nat)
    (ExitEdgeKey VertexKey BankBaseKey PruneKey : Type*) where
  source : Fin sourceCount → SourceEntry vertexCount componentCount
  rawFreeSpend : Fin sourceCount → ℚ
  tokenizedSpend : Fin sourceCount → ℚ
  term : Fin termCount →
    TypedLedgerToken componentCount ExitEdgeKey VertexKey BankBaseKey PruneKey
  priorSpend : Fin termCount → ℚ
  localReserve : Fin termCount → ℚ
  newSpend : Fin termCount → ℚ

namespace Data

variable {vertexCount componentCount sourceCount termCount : Nat}
variable {ExitEdgeKey VertexKey BankBaseKey PruneKey : Type*}

variable (D : Data vertexCount componentCount sourceCount termCount
  ExitEdgeKey VertexKey BankBaseKey PruneKey)

def sourceKey (source : Fin sourceCount) : PhysicalHalfKey vertexCount :=
  (D.source source).key

def sourceBaseKey (source : Fin sourceCount) : PhysicalBaseKey vertexCount :=
  (D.sourceKey source).baseKey

def sourceComp (source : Fin sourceCount) : Fin componentCount :=
  (D.source source).comp

/-- Keyed raw spend.  Summing by canonical key makes duplicate producer rows
visible to the exclusivity inequality rather than silently counting twice. -/
def rawFreeSpendAtKey (key : PhysicalHalfKey vertexCount) : ℚ :=
  ∑ source : Fin sourceCount,
    if D.sourceKey source = key then D.rawFreeSpend source else 0

/-- Keyed spend already converted into positive-capacity tokens. -/
def tokenizedSpendAtKey (key : PhysicalHalfKey vertexCount) : ℚ :=
  ∑ source : Fin sourceCount,
    if D.sourceKey source = key then D.tokenizedSpend source else 0

/-- A canonical physical key occurs at most once in the source union. -/
def SourcesDeduplicated : Prop :=
  Function.Injective D.sourceKey

/-- The two halves of one ordered-pair base key cannot be assigned to
different destination components. -/
def BaseKeyComponentCoherent : Prop :=
  ∀ source target,
    D.sourceBaseKey source = D.sourceBaseKey target →
      D.sourceComp source = D.sourceComp target

/-- Raw cancellation and tokenization share one unit of physical capacity. -/
def PhysicalHalfExclusive : Prop :=
  ∀ key : PhysicalHalfKey vertexCount,
    D.rawFreeSpendAtKey key + D.tokenizedSpendAtKey key ≤ 1

/-- Canonical identity of an official typed bank term. -/
def termSourceKey (term : Fin termCount) :=
  ((D.term term).comp, (D.term term).source)

/-- Typed terms are globally deduplicated on `(component, source)`. -/
def TermsDeduplicated : Prop :=
  Function.Injective D.termSourceKey

/-- Residual official capacity before the new spend is installed. -/
def residualCapQ (term : Fin termCount) : ℚ :=
  (D.term term).capQ - D.priorSpend term - D.localReserve term

/-- The proof-facing proposition reflected by `check`. -/
structure Checked : Prop where
  source_dedup : D.SourcesDeduplicated
  base_key_component_coherent : D.BaseKeyComponentCoherent
  term_dedup : D.TermsDeduplicated
  rawFreeSpend_nonneg : ∀ source, 0 ≤ D.rawFreeSpend source
  tokenizedSpend_nonneg : ∀ source, 0 ≤ D.tokenizedSpend source
  physical_half_exclusive : D.PhysicalHalfExclusive
  priorSpend_nonneg : ∀ term, 0 ≤ D.priorSpend term
  localReserve_nonneg : ∀ term, 0 ≤ D.localReserve term
  newSpend_nonneg : ∀ term, 0 ≤ D.newSpend term
  termCap_nonneg : ∀ term, 0 ≤ (D.term term).capQ
  official_term_cap : ∀ term,
    D.priorSpend term + D.localReserve term + D.newSpend term ≤
      (D.term term).capQ

/-- Kernel-decidable finite checker.  It checks only serialized ledger facts;
no graph-existence or matching-existence claim is hidden in this Boolean. -/
noncomputable def check : Bool := by
  classical
  exact decide D.Checked

theorem check_eq_true_iff :
    D.check = true ↔ D.Checked := by
  classical
  simp [check]

/-- Semantic consequences exported to downstream adapters.  This deliberately
contains exactly the checked bookkeeping laws and no graph theorem. -/
structure Sound : Prop where
  source_deduplicated : D.SourcesDeduplicated
  base_key_component_coherent : D.BaseKeyComponentCoherent
  term_deduplicated : D.TermsDeduplicated
  rawFreeSpend_nonneg : ∀ source, 0 ≤ D.rawFreeSpend source
  tokenizedSpend_nonneg : ∀ source, 0 ≤ D.tokenizedSpend source
  no_physical_half_double_spend : D.PhysicalHalfExclusive
  priorSpend_nonneg : ∀ term, 0 ≤ D.priorSpend term
  localReserve_nonneg : ∀ term, 0 ≤ D.localReserve term
  newSpend_nonneg : ∀ term, 0 ≤ D.newSpend term
  termCap_nonneg : ∀ term, 0 ≤ (D.term term).capQ
  no_official_term_overspend : ∀ term,
    D.priorSpend term + D.localReserve term + D.newSpend term ≤
      (D.term term).capQ

/-- Checker soundness is purely reflective: no capacity or source is inferred
from a family tag, maximum cut, or graph predicate. -/
theorem sound_of_check_eq_true (hcheck : D.check = true) : D.Sound := by
  have h := D.check_eq_true_iff.mp hcheck
  exact
    { source_deduplicated := h.source_dedup
      base_key_component_coherent := h.base_key_component_coherent
      term_deduplicated := h.term_dedup
      rawFreeSpend_nonneg := h.rawFreeSpend_nonneg
      tokenizedSpend_nonneg := h.tokenizedSpend_nonneg
      no_physical_half_double_spend := h.physical_half_exclusive
      priorSpend_nonneg := h.priorSpend_nonneg
      localReserve_nonneg := h.localReserve_nonneg
      newSpend_nonneg := h.newSpend_nonneg
      termCap_nonneg := h.termCap_nonneg
      no_official_term_overspend := h.official_term_cap }

theorem source_eq_of_key_eq (h : D.Sound) {source target : Fin sourceCount}
    (hkey : D.sourceKey source = D.sourceKey target) :
    source = target :=
  h.source_deduplicated hkey

theorem source_component_eq_of_same_base
    (h : D.Sound) {source target : Fin sourceCount}
    (hbase : D.sourceBaseKey source = D.sourceBaseKey target) :
    D.sourceComp source = D.sourceComp target :=
  h.base_key_component_coherent source target hbase

theorem term_eq_of_source_eq (h : D.Sound) {first second : Fin termCount}
    (hsource : D.termSourceKey first = D.termSourceKey second) :
    first = second :=
  h.term_deduplicated hsource

/-- The exact residual form of the official bank-term spend law. -/
theorem newSpend_le_residualCapQ (h : D.Sound) (term : Fin termCount) :
    D.newSpend term ≤ D.residualCapQ term := by
  unfold residualCapQ
  linarith [h.no_official_term_overspend term]

theorem residualCapQ_nonneg (h : D.Sound) (term : Fin termCount) :
    0 ≤ D.residualCapQ term := by
  linarith [D.newSpend_le_residualCapQ h term, h.newSpend_nonneg term]

/-- Choose a component label for every ordered-pair base key.  Coherence is
exactly what makes the choice agree with every source entry. -/
noncomputable def baseComponentOf
    (defaultComp : Fin componentCount) (key : PhysicalBaseKey vertexCount) :
    Fin componentCount := by
  classical
  exact if h : ∃ source, D.sourceBaseKey source = key then
    D.sourceComp (Classical.choose h)
  else defaultComp

theorem baseComponentOf_source
    (h : D.Sound) (defaultComp : Fin componentCount)
    (source : Fin sourceCount) :
    D.baseComponentOf defaultComp (D.sourceBaseKey source) =
      D.sourceComp source := by
  classical
  unfold baseComponentOf
  split
  · rename_i hexists
    exact h.base_key_component_coherent (Classical.choose hexists) source
      (Classical.choose_spec hexists)
  · rename_i hnot
    exact (hnot ⟨source, rfl⟩).elim

end Data

/-! ## Explicit graph-existence boundary -/

variable {vertexCount componentCount sourceCount termCount : Nat}
variable {ExitEdgeKey VertexKey BankBaseKey PruneKey : Type*}

/-- A graph layer may define `Realizes D` to mean that every source and term in
`D` is supplied by its checked graph predicates.  Existence is intentionally a
hypothesis: this module neither constructs a row tuple nor proves a matching. -/
def GraphExistenceHypothesis
    (Realizes :
      Data vertexCount componentCount sourceCount termCount
        ExitEdgeKey VertexKey BankBaseKey PruneKey → Prop) : Prop :=
  ∃ D, Realizes D ∧ D.check = true

/-- Reflection transports an explicitly supplied graph-realized checked
ledger to the semantic exclusivity laws.  It does not prove the premise. -/
theorem sound_of_graph_existence
    (Realizes :
      Data vertexCount componentCount sourceCount termCount
        ExitEdgeKey VertexKey BankBaseKey PruneKey → Prop)
    (graph_exists : GraphExistenceHypothesis Realizes) :
    ∃ D, Realizes D ∧ D.Sound := by
  rcases graph_exists with ⟨D, hrealizes, hcheck⟩
  exact ⟨D, hrealizes, D.sound_of_check_eq_true hcheck⟩

#print axioms PhysicalHalfKey.ofFreeHalf_injective
#print axioms Data.check_eq_true_iff
#print axioms Data.sound_of_check_eq_true
#print axioms Data.newSpend_le_residualCapQ
#print axioms Data.baseComponentOf_source
#print axioms sound_of_graph_existence

end CheckedMicroReservationLedger
end Gamma
end Erdos23Delta0
