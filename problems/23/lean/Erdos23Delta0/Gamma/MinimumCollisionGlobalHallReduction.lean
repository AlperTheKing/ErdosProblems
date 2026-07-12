import Erdos23Delta0.Gamma.CheckedSoftCollisionTwoCover

/-!
# Global grouped-cap Hall reduction at a minimum-defect row tuple

This file is the graph-free finite layer for the R53 adaptive-reservation
model.  Two dummy demands are attached to every active edge.  They can use
the four physical keys over that edge, so an injective assignment of all real
and dummy demands leaves at most two of those keys for real collision demand.
The grouped-cap flow problem is therefore an ordinary finite Hall problem on
the augmented demand shore.

The second part selects no graph object.  It records the abstract consequence
of minimizing the resulting Hall defect over a finite family of row tuples:
if the minimum is positive, every allowed replacement has a deficient shore.
The shore shortage is tied to the replacement by an exact integer delta
identity, with no floating-point or oracle computation.
-/

namespace Erdos23Delta0
namespace Gamma
namespace MinimumCollisionGlobalHallReduction

open scoped BigOperators
open CheckedSoftCollisionTwoCover

universe uState uObligation uEdge uBase

/-! ## Grouped caps as an ordinary Hall system -/

/-- The two dummy demands which consume two of the four physical keys over an
active edge. -/
abbrev ActiveCapDummy (ActiveEdge : Type uEdge) := ActiveEdge × Fin 2

/-- Real collision obligations together with the active-edge cap dummies. -/
abbrev AugmentedDemand
    (Obligation : Type uObligation) (ActiveEdge : Type uEdge) :=
  Obligation ⊕ ActiveCapDummy ActiveEdge

/-- A physical key belongs to the four-key block over an active edge. -/
def KeyOnActiveEdge
    {ActiveEdge : Type uEdge} {DirectBase : Type uBase}
    (edge : ActiveEdge) :
    EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop
  | (Sum.inl (edge', _), _) => edge = edge'
  | (Sum.inr _, _) => False

/-- The literal four physical keys over one active edge. -/
noncomputable def activeKeySet
    {ActiveEdge : Type uEdge} {DirectBase : Type uBase}
    (edge : ActiveEdge) :
    Finset (EdgeCappedPhysicalKey ActiveEdge DirectBase) := by
  classical
  exact Finset.univ.image fun slot : Fin 2 × Fin 2 =>
    ((Sum.inl (edge, slot.1)), slot.2)

@[simp] theorem mem_activeKeySet_iff
    {ActiveEdge : Type uEdge} {DirectBase : Type uBase}
    (edge : ActiveEdge)
    (key : EdgeCappedPhysicalKey ActiveEdge DirectBase) :
    key ∈ activeKeySet edge ↔ KeyOnActiveEdge edge key := by
  classical
  rcases key with ⟨base, half⟩
  rcases base with ⟨⟨edge', orientation⟩⟩ | direct
  · simp [activeKeySet, KeyOnActiveEdge]
  · simp [activeKeySet, KeyOnActiveEdge]

@[simp] theorem card_activeKeySet
    {ActiveEdge : Type uEdge} {DirectBase : Type uBase}
    (edge : ActiveEdge) :
    (activeKeySet (DirectBase := DirectBase) edge).card = 4 := by
  classical
  rw [activeKeySet, Finset.card_image_of_injective]
  · simp
  · intro left right heq
    apply Prod.ext
    · exact congrArg Prod.snd (Sum.inl_injective (congrArg Prod.fst heq))
    · exact congrArg
        (fun key : EdgeCappedPhysicalKey ActiveEdge DirectBase => key.2) heq

/-- Ordinary Hall incidence for the augmented system.  A real demand keeps
the caller's eligibility relation.  Either dummy over an active edge sees all
four physical keys over that edge and no other key. -/
def AugmentedEligible
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop) :
    AugmentedDemand Obligation ActiveEdge →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop
  | Sum.inl obligation, key => Eligible obligation key
  | Sum.inr (edge, _), key => KeyOnActiveEdge edge key

/-- An integral grouped-cap flow is an ordinary transversal after adding two
cap dummies per active edge.  The assignment is deliberately graph-free;
all graph legality remains in `Eligible`. -/
structure IntegralGroupedCapFlow
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop) where
  assign : AugmentedDemand Obligation ActiveEdge →
    EdgeCappedPhysicalKey ActiveEdge DirectBase
  injective : Function.Injective assign
  supported : ∀ demand, AugmentedEligible Eligible demand (assign demand)

namespace IntegralGroupedCapFlow

variable {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
variable {DirectBase : Type uBase}
variable {Eligible : Obligation →
  EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop}

/-- Restriction of an augmented transversal to the real obligations. -/
def realAssign (flow : IntegralGroupedCapFlow Eligible) (obligation : Obligation) :
    EdgeCappedPhysicalKey ActiveEdge DirectBase :=
  flow.assign (Sum.inl obligation)

theorem realAssign_injective (flow : IntegralGroupedCapFlow Eligible) :
    Function.Injective flow.realAssign := by
  intro left right heq
  exact Sum.inl.inj (flow.injective heq)

theorem realAssign_supported (flow : IntegralGroupedCapFlow Eligible)
    (obligation : Obligation) :
    Eligible obligation (flow.realAssign obligation) :=
  flow.supported (Sum.inl obligation)

/-- Number of real obligations assigned to the four physical keys over one
active edge. -/
noncomputable def realActiveLoad
    [Fintype Obligation] [Fintype ActiveEdge] [Fintype DirectBase]
    (flow : IntegralGroupedCapFlow Eligible) (edge : ActiveEdge) : Nat := by
  classical
  exact (Finset.univ.filter fun obligation =>
    KeyOnActiveEdge edge (flow.realAssign obligation)).card

/-- The two cap dummies consume two distinct keys in every active four-key
block.  Injectivity therefore leaves at most two keys in that block for real
obligations. -/
theorem realActiveLoad_le_two
    [Fintype Obligation] [Fintype ActiveEdge] [Fintype DirectBase]
    (flow : IntegralGroupedCapFlow Eligible) (edge : ActiveEdge) :
    flow.realActiveLoad edge ≤ 2 := by
  classical
  let realDemands : Finset (AugmentedDemand Obligation ActiveEdge) :=
    (Finset.univ.filter fun obligation =>
      KeyOnActiveEdge edge (flow.realAssign obligation)).image Sum.inl
  let capDummies : Finset (AugmentedDemand Obligation ActiveEdge) :=
    Finset.univ.image fun half : Fin 2 => Sum.inr (edge, half)
  let assignedAtEdge := realDemands ∪ capDummies
  let activeKeys : Finset
      (EdgeCappedPhysicalKey ActiveEdge DirectBase) :=
    activeKeySet edge
  have hrealCard : realDemands.card = flow.realActiveLoad edge := by
    simp only [realDemands]
    rw [Finset.card_image_of_injective]
    · rfl
    · exact Sum.inl_injective
  have hdummyCard : capDummies.card = 2 := by
    simp only [capDummies]
    rw [Finset.card_image_of_injective]
    · simp
    · intro left right heq
      exact congrArg Prod.snd (Sum.inr_injective heq)
  have hdisjoint : Disjoint realDemands capDummies := by
    refine Finset.disjoint_left.mpr ?_
    intro demand hreal hdummy
    rcases Finset.mem_image.mp hreal with ⟨obligation, _, rfl⟩
    rcases Finset.mem_image.mp hdummy with ⟨half, _, hfalse⟩
    exact Sum.inr_ne_inl hfalse
  have himageSubset : assignedAtEdge.image flow.assign ⊆ activeKeys := by
    intro key hkey
    rcases Finset.mem_image.mp hkey with ⟨demand, hdemand, rfl⟩
    rcases Finset.mem_union.mp hdemand with hreal | hdummy
    · rcases Finset.mem_image.mp hreal with ⟨obligation, hobligation, rfl⟩
      exact (mem_activeKeySet_iff edge _).mpr
        (Finset.mem_filter.mp hobligation).2
    · rcases Finset.mem_image.mp hdummy with ⟨half, _, rfl⟩
      exact (mem_activeKeySet_iff edge _).mpr
        (flow.supported (Sum.inr (edge, half)))
  have hactiveKeysCard : activeKeys.card = 4 := by
    simp [activeKeys]
  have hcard := Finset.card_le_card himageSubset
  rw [Finset.card_image_of_injective _ flow.injective,
    Finset.card_union_of_disjoint hdisjoint, hrealCard, hdummyCard,
    hactiveKeysCard] at hcard
  omega

end IntegralGroupedCapFlow

/-- Physical sources reached by an augmented Hall shore. -/
noncomputable def shoreSources
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop)
    (shore : Finset (AugmentedDemand Obligation ActiveEdge)) :
    Finset (EdgeCappedPhysicalKey ActiveEdge DirectBase) := by
  classical
  exact Finset.univ.filter fun key =>
    ∃ demand ∈ shore, AugmentedEligible Eligible demand key

/-- Hall's inequalities on all augmented demand shores.  The dummy demands
are the exact finite encoding of the aggregate cap two on each active edge. -/
def GroupedCapHallCondition
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop) : Prop :=
  ∀ shore : Finset (AugmentedDemand Obligation ActiveEdge),
    shore.card ≤ (shoreSources Eligible shore).card

/-- The grouped-cap integral flow problem is exactly the ordinary Hall shore
condition on real demands plus the two cap dummies per active edge. -/
theorem integralGroupedCapFlow_nonempty_iff_hall
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop) :
    Nonempty (IntegralGroupedCapFlow Eligible) ↔
      GroupedCapHallCondition Eligible := by
  classical
  let relation := AugmentedEligible Eligible
  have hHall :=
    Fintype.all_card_le_filter_rel_iff_exists_injective relation
  constructor
  · rintro ⟨flow⟩
    unfold GroupedCapHallCondition
    intro shore
    have hallForRelation := hHall.mpr
      ⟨flow.assign, flow.injective, flow.supported⟩
    simpa only [shoreSources, relation] using hallForRelation shore
  · intro hall
    have hallForRelation :
        ∀ shore : Finset (AugmentedDemand Obligation ActiveEdge),
          shore.card ≤
            (Finset.univ.filter fun key =>
              ∃ demand ∈ shore, relation demand key).card := by
      simpa only [GroupedCapHallCondition, shoreSources, relation] using hall
    rcases hHall.mp hallForRelation with ⟨assign, hinjective, hsupported⟩
    exact ⟨{
      assign := assign
      injective := hinjective
      supported := hsupported
    }⟩

/-! ## Exact Hall defect -/

/-- Cardinal shortage of one augmented Hall shore. -/
noncomputable def shoreDefect
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop)
    (shore : Finset (AugmentedDemand Obligation ActiveEdge)) : Nat :=
  shore.card - (shoreSources Eligible shore).card

/-- Maximum augmented-shore shortage.  This is the exact integer defect used
by the finite row selector. -/
noncomputable def hallDefect
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype Obligation] [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop) : Nat := by
  classical
  exact (Finset.univ :
    Finset (Finset (AugmentedDemand Obligation ActiveEdge))).sup
      (shoreDefect Eligible)

theorem shoreDefect_le_hallDefect
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype Obligation] [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop)
    (shore : Finset (AugmentedDemand Obligation ActiveEdge)) :
    shoreDefect Eligible shore ≤ hallDefect Eligible := by
  classical
  exact Finset.le_sup (Finset.mem_univ shore)

/-- Some shore realizes the exact maximum shortage. -/
theorem exists_shoreDefect_eq_hallDefect
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype Obligation] [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop) :
    ∃ shore : Finset (AugmentedDemand Obligation ActiveEdge),
      shoreDefect Eligible shore = hallDefect Eligible := by
  classical
  have huniv :
      (Finset.univ :
        Finset (Finset (AugmentedDemand Obligation ActiveEdge))).Nonempty :=
    ⟨∅, Finset.mem_univ ∅⟩
  rcases Finset.exists_mem_eq_sup
      (Finset.univ :
        Finset (Finset (AugmentedDemand Obligation ActiveEdge)))
      huniv (shoreDefect Eligible) with ⟨shore, _, heq⟩
  exact ⟨shore, heq.symm⟩

/-- Zero exact defect is equivalent to every grouped-cap Hall inequality. -/
theorem hallDefect_eq_zero_iff_hall
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype Obligation] [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop) :
    hallDefect Eligible = 0 ↔ GroupedCapHallCondition Eligible := by
  classical
  constructor
  · intro hzero shore
    have hle := shoreDefect_le_hallDefect Eligible shore
    rw [hzero] at hle
    exact Nat.sub_eq_zero_iff_le.mp (Nat.eq_zero_of_le_zero hle)
  · intro hall
    apply Nat.eq_zero_of_le_zero
    apply Finset.sup_le
    intro shore _
    exact (Nat.sub_eq_zero_iff_le.mpr (hall shore)).le

/-- Zero exact defect is equivalent to existence of a total integral
grouped-cap flow. -/
theorem hallDefect_eq_zero_iff_flow
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype Obligation] [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop) :
    hallDefect Eligible = 0 ↔
      Nonempty (IntegralGroupedCapFlow Eligible) := by
  rw [hallDefect_eq_zero_iff_hall,
    ← integralGroupedCapFlow_nonempty_iff_hall]

/-- A deficient shore has the literal strict cardinal inequality. -/
def DeficientShore
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop)
    (shore : Finset (AugmentedDemand Obligation ActiveEdge)) : Prop :=
  (shoreSources Eligible shore).card < shore.card

/-- Positive exact defect has a shore realizing that whole defect. -/
theorem exists_deficientShore_realizing_hallDefect
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype Obligation] [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop)
    (hpositive : 0 < hallDefect Eligible) :
    ∃ shore : Finset (AugmentedDemand Obligation ActiveEdge),
      DeficientShore Eligible shore ∧
        shoreDefect Eligible shore = hallDefect Eligible := by
  obtain ⟨shore, heq⟩ := exists_shoreDefect_eq_hallDefect Eligible
  refine ⟨shore, ?_, heq⟩
  apply Nat.sub_pos_iff_lt.mp
  change 0 < shoreDefect Eligible shore
  rw [heq]
  exact hpositive

/-- On a deficient shore, natural subtraction is the literal integer
cardinality difference. -/
theorem shoreDefect_int_eq_card_sub
    {Obligation : Type uObligation} {ActiveEdge : Type uEdge}
    {DirectBase : Type uBase}
    [Fintype ActiveEdge] [Fintype DirectBase]
    (Eligible : Obligation →
      EdgeCappedPhysicalKey ActiveEdge DirectBase → Prop)
    (shore : Finset (AugmentedDemand Obligation ActiveEdge))
    (hdeficient : DeficientShore Eligible shore) :
    (shoreDefect Eligible shore : Int) =
      (shore.card : Int) - ((shoreSources Eligible shore).card : Int) := by
  unfold shoreDefect DeficientShore at *
  omega

/-! ## Minimum-defect row tuples and replacement shores -/

section RowSelection

variable {State : Type uState}
variable (Obligation : State → Type uObligation)
variable (ActiveEdge : State → Type uEdge)
variable (DirectBase : State → Type uBase)
variable [∀ state, Fintype (Obligation state)]
variable [∀ state, Fintype (ActiveEdge state)]
variable [∀ state, Fintype (DirectBase state)]
variable (Eligible : ∀ state,
  Obligation state →
    EdgeCappedPhysicalKey (ActiveEdge state) (DirectBase state) → Prop)

/-- Exact grouped-cap Hall defect of one row tuple. -/
noncomputable def rowDefect (state : State) : Nat :=
  hallDefect (Eligible state)

/-- A row tuple globally minimizes the exact grouped-cap defect. -/
def IsMinimumDefectTuple (omega : State) : Prop :=
  ∀ eta : State,
    rowDefect Obligation ActiveEdge DirectBase Eligible omega ≤
      rowDefect Obligation ActiveEdge DirectBase Eligible eta

/-- Canonical finite row tuple minimizing the exact grouped-cap defect. -/
noncomputable def minimumDefectTuple [Fintype State] [Nonempty State] : State :=
  (CertGraph.chooseFiniteMinimizer
    (rowDefect Obligation ActiveEdge DirectBase Eligible)).1

/-- The canonical finite tuple satisfies the global minimum contract. -/
theorem minimumDefectTuple_isMinimum [Fintype State] [Nonempty State] :
    IsMinimumDefectTuple Obligation ActiveEdge DirectBase Eligible
      (minimumDefectTuple Obligation ActiveEdge DirectBase Eligible) :=
  (CertGraph.chooseFiniteMinimizer
    (rowDefect Obligation ActiveEdge DirectBase Eligible)).2

/-- Signed exact change in defect under a row replacement. -/
noncomputable def defectDelta (omega eta : State) : Int :=
  (rowDefect Obligation ActiveEdge DirectBase Eligible eta : Int) -
    (rowDefect Obligation ActiveEdge DirectBase Eligible omega : Int)

/-- A replacement shore compensates the old positive defect when it realizes
the new tuple's full defect and its literal cardinal shortage is the old
defect plus the signed replacement delta. -/
def CompensatingDeficientShore (omega eta : State) : Prop :=
  ∃ shore : Finset
      (AugmentedDemand (Obligation eta) (ActiveEdge eta)),
    DeficientShore (Eligible eta) shore ∧
    shoreDefect (Eligible eta) shore =
      rowDefect Obligation ActiveEdge DirectBase Eligible eta ∧
    (shore.card : Int) -
        ((shoreSources (Eligible eta) shore).card : Int) =
      (rowDefect Obligation ActiveEdge DirectBase Eligible omega : Int) +
        defectDelta Obligation ActiveEdge DirectBase Eligible omega eta

/-- Exact finite minimum principle.  If a minimum-defect row tuple still has
positive defect, every caller-designated allowed replacement has a new
deficient Hall shore.  The final conjunct is the exact delta identity; the
delta is nonnegative by global minimality. -/
theorem positive_minimum_every_replacement_has_compensating_shore
    (AllowedReplacement : State → State → Prop)
    (omega : State)
    (hminimum :
      IsMinimumDefectTuple Obligation ActiveEdge DirectBase Eligible omega)
    (hpositive :
      0 < rowDefect Obligation ActiveEdge DirectBase Eligible omega) :
    ∀ eta : State, AllowedReplacement omega eta →
      0 ≤ defectDelta Obligation ActiveEdge DirectBase Eligible omega eta ∧
      CompensatingDeficientShore
        Obligation ActiveEdge DirectBase Eligible omega eta := by
  intro eta _hreplacement
  have hminimumEta := hminimum eta
  have hpositiveEta :
      0 < rowDefect Obligation ActiveEdge DirectBase Eligible eta :=
    lt_of_lt_of_le hpositive hminimumEta
  have hdeltaNonneg :
      0 ≤ defectDelta Obligation ActiveEdge DirectBase Eligible omega eta := by
    unfold defectDelta
    apply sub_nonneg.mpr
    exact_mod_cast hminimumEta
  refine ⟨hdeltaNonneg, ?_⟩
  obtain ⟨shore, hdeficient, hrealizes⟩ :=
    exists_deficientShore_realizing_hallDefect
      (Eligible eta) hpositiveEta
  refine ⟨shore, hdeficient, hrealizes, ?_⟩
  have hcard := shoreDefect_int_eq_card_sub
    (Eligible eta) shore hdeficient
  calc
    (shore.card : Int) -
          ((shoreSources (Eligible eta) shore).card : Int) =
        (shoreDefect (Eligible eta) shore : Int) := hcard.symm
    _ = (rowDefect Obligation ActiveEdge DirectBase Eligible eta : Int) := by
      exact_mod_cast hrealizes
    _ = (rowDefect Obligation ActiveEdge DirectBase Eligible omega : Int) +
          defectDelta Obligation ActiveEdge DirectBase Eligible omega eta := by
      rw [defectDelta]
      omega

/-- Canonical finite-row specialization of the minimum principle. -/
theorem positive_canonical_every_replacement_has_compensating_shore
    [Fintype State] [Nonempty State]
    (AllowedReplacement : State → State → Prop)
    (hpositive :
      0 < rowDefect Obligation ActiveEdge DirectBase Eligible
        (minimumDefectTuple Obligation ActiveEdge DirectBase Eligible)) :
    ∀ eta : State,
      AllowedReplacement
          (minimumDefectTuple Obligation ActiveEdge DirectBase Eligible) eta →
        0 ≤ defectDelta Obligation ActiveEdge DirectBase Eligible
          (minimumDefectTuple Obligation ActiveEdge DirectBase Eligible) eta ∧
        CompensatingDeficientShore Obligation ActiveEdge DirectBase Eligible
          (minimumDefectTuple Obligation ActiveEdge DirectBase Eligible) eta := by
  exact positive_minimum_every_replacement_has_compensating_shore
    Obligation ActiveEdge DirectBase Eligible AllowedReplacement
    (minimumDefectTuple Obligation ActiveEdge DirectBase Eligible)
    (minimumDefectTuple_isMinimum Obligation ActiveEdge DirectBase Eligible)
    hpositive

/-- Provider-free zero-defect endpoint for one row tuple. -/
theorem rowDefect_eq_zero_iff_flow (state : State) :
    rowDefect Obligation ActiveEdge DirectBase Eligible state = 0 ↔
      Nonempty (IntegralGroupedCapFlow (Eligible state)) := by
  exact hallDefect_eq_zero_iff_flow (Eligible state)

end RowSelection

#print axioms integralGroupedCapFlow_nonempty_iff_hall
#print axioms IntegralGroupedCapFlow.realActiveLoad_le_two
#print axioms hallDefect_eq_zero_iff_flow
#print axioms exists_deficientShore_realizing_hallDefect
#print axioms shoreDefect_int_eq_card_sub
#print axioms minimumDefectTuple_isMinimum
#print axioms positive_minimum_every_replacement_has_compensating_shore
#print axioms positive_canonical_every_replacement_has_compensating_shore

end MinimumCollisionGlobalHallReduction
end Gamma
end Erdos23Delta0
