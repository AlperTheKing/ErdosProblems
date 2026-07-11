import Erdos23Delta0.BankedWallRoutingFailure
import Erdos23Delta0.ClosedShoreExtraction

/-!
# Exact dual-weighted Hall reduction

`WeightedRoutingFailure d L` is an ordinary rational Hall obstruction after
scaling port loads by `d.gamma` and sink capacities by `d.delta`.  The legal
relation is unchanged.  The full port shore has more load than the capacity
of all sinks, hence also more load than its legal-neighborhood capacity once
the scaled capacities are nonnegative.

The final theorem deliberately states the extra closure input exactly: some
closed quotient shore must expose every port.  This is precisely the seed
needed for finite descent to a minimal closed deficient shore.  Requiring the
quotient universe itself to expose every port is a convenient sufficient
condition; its closedness follows from extensivity.
-/

namespace Erdos23Delta0
namespace Wall
namespace DualWeightedHallReduction

open scoped BigOperators
open PortHall ClosedShore

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP}

/-- Copy a banked wall LP and replace each sink capacity `cap s` by
`cap s * d.delta s`.  All finite types and the legal relation are unchanged. -/
def dualScaledLP (I : BankedWallLP) (d : Dual I) : BankedWallLP where
  Cut := I.Cut
  Atom := I.Atom
  Short := I.Short
  Port := I.Port
  Sink := I.Sink
  cutFintype := I.cutFintype
  atomFintype := I.atomFintype
  shortFintype := I.shortFintype
  portFintype := I.portFintype
  sinkFintype := I.sinkFintype
  cov := I.cov
  useShort := I.useShort
  cutPort := I.cutPort
  legal := I.legal
  legalDecidable := I.legalDecidable
  cap := fun s => I.cap s * d.delta s

/-- The Hall load corresponding to the dual-weighted port objective. -/
def dualScaledLoad (d : Dual I) (L : I.Port -> ℚ) :
    (dualScaledLP I d).Port -> ℚ :=
  fun p => L p * d.gamma p

@[simp] theorem dualScaledLP_cap (d : Dual I) (s : I.Sink) :
    (dualScaledLP I d).cap s = I.cap s * d.delta s := rfl

@[simp] theorem dualScaledLoad_apply (d : Dual I) (L : I.Port -> ℚ) (p : I.Port) :
    dualScaledLoad d L p = L p * d.gamma p := rfl

/-- Restricted checking gives nonnegative capacities in the scaled LP. -/
theorem dualScaledLP_cap_nonneg {Allowed : I.Cut -> Prop} {d : Dual I}
    (hd : d.RestrictedChecked Allowed) :
    forall s : (dualScaledLP I d).Sink, 0 <= (dualScaledLP I d).cap s := by
  intro s
  exact mul_nonneg (hd.cap_nonneg s) (hd.delta_nonneg s)

/-- The scaled full-port load is exactly the weighted routing objective. -/
theorem dualScaled_loadQ_univ (d : Dual I) (L : I.Port -> ℚ) :
    loadQ (dualScaledLP I d) (dualScaledLoad d L)
        (Finset.univ : Finset (dualScaledLP I d).Port) =
      ∑ p : I.Port, L p * d.gamma p := by
  simp [loadQ, dualScaledLoad, dualScaledLP]

/-- The scaled capacity of all sinks is exactly `totalDeltaCap`. -/
theorem dualScaled_capQ_univ (d : Dual I) :
    capQ (dualScaledLP I d)
        (Finset.univ : Finset (dualScaledLP I d).Sink) =
      totalDeltaCap d := by
  simp [capQ, dualScaledLP, totalDeltaCap]

/-- Exact rational identity before restricting to the legal neighborhood. -/
theorem dualScaled_totalGap_eq (d : Dual I) (L : I.Port -> ℚ) :
    loadQ (dualScaledLP I d) (dualScaledLoad d L)
          (Finset.univ : Finset (dualScaledLP I d).Port) -
        capQ (dualScaledLP I d)
          (Finset.univ : Finset (dualScaledLP I d).Sink) =
      (∑ p : I.Port, L p * d.gamma p) - totalDeltaCap d := by
  rw [dualScaled_loadQ_univ, dualScaled_capQ_univ]

/-- Weighted routing failure is exactly positivity of the scaled total gap. -/
theorem weightedRoutingFailure_iff_dualScaled_totalGap_pos
    (d : Dual I) (L : I.Port -> ℚ) :
    WeightedRoutingFailure d L <->
      0 < loadQ (dualScaledLP I d) (dualScaledLoad d L)
            (Finset.univ : Finset (dualScaledLP I d).Port) -
          capQ (dualScaledLP I d)
            (Finset.univ : Finset (dualScaledLP I d).Sink) := by
  unfold WeightedRoutingFailure
  rw [dualScaled_totalGap_eq, sub_pos]

/-- The exact total gap is at most the Hall deficiency of the full port shore.
Unexposed sinks cause no problem: they only remove nonnegative capacity from
the legal-neighborhood term. -/
theorem dualScaled_totalGap_le_deficiency_univ
    {Allowed : I.Cut -> Prop} {d : Dual I}
    (hd : d.RestrictedChecked Allowed) (L : I.Port -> ℚ) :
    loadQ (dualScaledLP I d) (dualScaledLoad d L)
          (Finset.univ : Finset (dualScaledLP I d).Port) -
        capQ (dualScaledLP I d)
          (Finset.univ : Finset (dualScaledLP I d).Sink) <=
      deficiencyQ (dualScaledLP I d) (dualScaledLoad d L)
        (Finset.univ : Finset (dualScaledLP I d).Port) := by
  have hcap :
      capQ (dualScaledLP I d)
          (legalNbr (dualScaledLP I d)
            (Finset.univ : Finset (dualScaledLP I d).Port)) <=
        capQ (dualScaledLP I d)
          (Finset.univ : Finset (dualScaledLP I d).Sink) :=
    capQ_mono (dualScaledLP_cap_nonneg hd) (Finset.subset_univ _)
  unfold deficiencyQ
  linarith

/-- Exact rational reduction from weighted routing failure to Hall deficiency. -/
theorem weightedRoutingFailure_gives_dualScaled_hallDeficient_univ
    {Allowed : I.Cut -> Prop} {d : Dual I} {L : I.Port -> ℚ}
    (hd : d.RestrictedChecked Allowed) (hFail : WeightedRoutingFailure d L) :
    HallDeficient (dualScaledLP I d) (dualScaledLoad d L)
      (Finset.univ : Finset (dualScaledLP I d).Port) := by
  have hgap :=
    (weightedRoutingFailure_iff_dualScaled_totalGap_pos d L).mp hFail
  have hle := dualScaled_totalGap_le_deficiency_univ hd L
  exact lt_of_lt_of_le hgap hle

/-- Copy an escape quotient to the dual-scaled LP.  This is data-preserving:
the component type, closure, and exposed port sets are definitionally the
same. -/
def dualScaledQuotient (Q : AbstractEscapeQuotient I) (d : Dual I) :
    AbstractEscapeQuotient (dualScaledLP I d) where
  QComp := Q.QComp
  qDecEq := Q.qDecEq
  qFintype := Q.qFintype
  fullClosure := Q.fullClosure
  exposedPorts := Q.exposedPorts
  closure_extensive := Q.closure_extensive
  closure_idempotent := Q.closure_idempotent
  closure_monotone := Q.closure_monotone

/-- The exact closure seed needed below: some closed shore exposes all ports. -/
def ClosedExposesUniv (Q : AbstractEscapeQuotient I) : Prop :=
  exists U : Finset Q.QComp,
    Q.fullClosure U = U /\
      Q.exposedPorts U = (Finset.univ : Finset I.Port)

theorem closedExposesUniv_iff_closedPortSet_univ
    (Q : AbstractEscapeQuotient I) :
    ClosedExposesUniv Q <->
      ClosedPortSet Q (Finset.univ : Finset I.Port) := by
  rfl

/-- Every extensive finite closure fixes the quotient universe. -/
theorem fullClosure_univ (Q : AbstractEscapeQuotient I) :
    Q.fullClosure (Finset.univ : Finset Q.QComp) = Finset.univ := by
  apply Finset.Subset.antisymm
  · exact Finset.subset_univ _
  · exact Q.closure_extensive _

/-- Thus `exposedPorts univ = univ` is a convenient sufficient form of the
exact `ClosedExposesUniv` hypothesis. -/
theorem closedExposesUniv_of_exposedPorts_univ
    (Q : AbstractEscapeQuotient I)
    (hExpose : Q.exposedPorts (Finset.univ : Finset Q.QComp) =
      (Finset.univ : Finset I.Port)) :
    ClosedExposesUniv Q :=
  ⟨Finset.univ, fullClosure_univ Q, hExpose⟩

/-- Copying the quotient preserves the exact closed-exposure seed. -/
theorem dualScaledQuotient_closedExposesUniv_iff
    (Q : AbstractEscapeQuotient I) (d : Dual I) :
    ClosedExposesUniv (dualScaledQuotient Q d) <-> ClosedExposesUniv Q := by
  rfl

/-- Finite descent: every closed deficient port set contains a deficient port
set minimal among the closed ones.  No monotonicity of exposure is needed. -/
theorem exists_minimalClosedDeficient_of_closed_hallDeficient
    {J : BankedWallLP} {Q : AbstractEscapeQuotient J}
    {W : J.Port -> ℚ} {P : Finset J.Port}
    (hClosed : ClosedPortSet Q P) (hDef : HallDeficient J W P) :
    exists U : Finset Q.QComp,
      Q.fullClosure U = U /\
        MinimalClosedDeficient Q W (Q.exposedPorts U) := by
  classical
  let candidates : Set (Finset J.Port) :=
    {R | ClosedPortSet Q R /\ HallDeficient J W R}
  have hcandidates : candidates.Nonempty := by
    refine ⟨P, ?_⟩
    change ClosedPortSet Q P /\ HallDeficient J W P
    exact ⟨hClosed, hDef⟩
  obtain ⟨M, hM⟩ := (Set.toFinite candidates).exists_minimal hcandidates
  have hMmem : ClosedPortSet Q M /\ HallDeficient J W M := by
    have hMmem' : M ∈ candidates := hM.1
    change ClosedPortSet Q M /\ HallDeficient J W M at hMmem'
    exact hMmem'
  obtain ⟨⟨U, hUclosed, hUexposed⟩, hMdef⟩ := hMmem
  refine ⟨U, hUclosed, ?_⟩
  refine ⟨⟨U, hUclosed, rfl⟩, ?_, ?_⟩
  · simpa [hUexposed] using hMdef
  · intro P' hP'closed hP'proper
    apply le_of_not_gt
    intro hP'def
    have hP'mem : P' ∈ candidates := by
      change ClosedPortSet Q P' /\ HallDeficient J W P'
      exact ⟨hP'closed, hP'def⟩
    have hP'properM : P' ⊂ M := by
      simpa [hUexposed] using hP'proper
    have hMsub : M ⊆ P' := hM.2 hP'mem hP'properM.1
    exact hP'properM.2 hMsub

/-- Full reduction to a minimal closed deficient shore.  `ClosedExposesUniv`
is the exact additional exposed-universe/closure hypothesis: it says exactly
that the full deficient port set supplied by the Hall reduction is closed. -/
theorem weightedRoutingFailure_gives_minimalClosedDeficient
    {Allowed : I.Cut -> Prop} {d : Dual I} {L : I.Port -> ℚ}
    (Q : AbstractEscapeQuotient I)
    (hd : d.RestrictedChecked Allowed)
    (hClosedUniv : ClosedExposesUniv Q)
    (hFail : WeightedRoutingFailure d L) :
    exists U : Finset (dualScaledQuotient Q d).QComp,
      (dualScaledQuotient Q d).fullClosure U = U /\
        MinimalClosedDeficient (dualScaledQuotient Q d)
          (dualScaledLoad d L) ((dualScaledQuotient Q d).exposedPorts U) := by
  have hDef :=
    weightedRoutingFailure_gives_dualScaled_hallDeficient_univ hd hFail
  have hClosed :
      ClosedPortSet (dualScaledQuotient Q d)
        (Finset.univ : Finset (dualScaledLP I d).Port) := by
    rw [← closedExposesUniv_iff_closedPortSet_univ]
    exact (dualScaledQuotient_closedExposesUniv_iff Q d).mpr hClosedUniv
  exact exists_minimalClosedDeficient_of_closed_hallDeficient hClosed hDef

end DualWeightedHallReduction
end Wall
end Erdos23Delta0
