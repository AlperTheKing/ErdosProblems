import Erdos23Delta0.DualWeightedHallReduction

/-!
# W3 skeleton over the exact dual-scaled Hall instance

The original W3 skeleton assumes `ClosedWeightedHallCompleteness` for the
unscaled port Hall problem.  A strict dual already supplies a simpler exact
Hall obstruction after multiplying port loads by `gamma` and sink capacities
by `delta`.  This module consumes that obstruction directly.

The result removes closed-Hall completeness from the hypothesis list.  The
remaining graph content is a positive-root extraction and a closed-root D1
exchange for the copied, dual-scaled quotient.
-/

namespace Erdos23Delta0
namespace Wall
namespace DualWeightedW3

open ClosedShore PortHall DualWeightedHallReduction

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP}

/-- Closed-root exchange stated on the dual-scaled minimal Hall shore while
concluding a violation of D1 in the original wall LP. -/
def ScaledClosedRootCutViolatesD1
    (Allowed : I.Cut → Prop) (Q : AbstractEscapeQuotient I)
    (d : Dual I) (L : I.Port → ℚ) : Prop :=
  ∀ U : Finset (dualScaledQuotient Q d).QComp,
    (dualScaledQuotient Q d).fullClosure U = U →
      MinimalClosedDeficient (dualScaledQuotient Q d)
        (dualScaledLoad d L) ((dualScaledQuotient Q d).exposedPorts U) →
        (∀ D : LegalComponentPartition (dualScaledLP I d)
            ((dualScaledQuotient Q d).exposedPorts U),
          Fintype.card D.K = 1) →
          ∃ X : I.Cut,
            Allowed X ∧ cutBeta d X + cutGamma d X < cutAlpha d X

/-- Restricted-D1 W3 theorem with exact dual-scaled Hall descent. -/
theorem noStrictRestrictedDual_of_scaledHall_and_exchange
    {Allowed : I.Cut → Prop} {Q : AbstractEscapeQuotient I} {d : Dual I}
    (hd : d.RestrictedChecked Allowed)
    (Z : DualAlmostSqueeze I Allowed d)
    (hClosedUniv : ClosedExposesUniv Q)
    (hExtract : PositiveRootBlockClosedExtraction (dualScaledQuotient Q d))
    (hExchange : ScaledClosedRootCutViolatesD1 Allowed Q d Z.portLoad) :
    ¬d.StrictGap := by
  intro hstrict
  have hFail : WeightedRoutingFailure d Z.portLoad :=
    strictRestrictedDual_gives_weightedRoutingFailure hd Z hstrict
  obtain ⟨U, hUclosed, hMin⟩ :=
    weightedRoutingFailure_gives_minimalClosedDeficient
      Q hd hClosedUniv hFail
  have hUnique :
      ∀ D : LegalComponentPartition (dualScaledLP I d)
          ((dualScaledQuotient Q d).exposedPorts U),
        Fintype.card D.K = 1 := by
    intro D
    exact minimalClosedDeficient_has_unique_root_of_positiveExtraction
      hExtract (dualScaledLoad d Z.portLoad) U hUclosed hMin D
  obtain ⟨X, hAllowed, hbad⟩ :=
    hExchange U hUclosed hMin hUnique
  exact (not_lt_of_ge (hd.d1_allowed X hAllowed)) hbad

/-- All-cut convenience wrapper. -/
theorem noStrictDual_of_scaledHall_and_exchange
    {Allowed : I.Cut → Prop} {Q : AbstractEscapeQuotient I} {d : Dual I}
    (hd : d.Checked)
    (Z : DualAlmostSqueeze I Allowed d)
    (hClosedUniv : ClosedExposesUniv Q)
    (hExtract : PositiveRootBlockClosedExtraction (dualScaledQuotient Q d))
    (hExchange : ScaledClosedRootCutViolatesD1 Allowed Q d Z.portLoad) :
    ¬d.StrictGap :=
  noStrictRestrictedDual_of_scaledHall_and_exchange
    hd.restrict Z hClosedUniv hExtract hExchange

#print axioms noStrictRestrictedDual_of_scaledHall_and_exchange
#print axioms noStrictDual_of_scaledHall_and_exchange

end DualWeightedW3
end Wall
end Erdos23Delta0
