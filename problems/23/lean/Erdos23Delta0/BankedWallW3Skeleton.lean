import Erdos23Delta0.ClosedWeightedHall

/-!
# W3 abstract skeleton: no strict restricted dual

This module composes the already-isolated R3 pieces.  It does not prove the
graph-side wall facts.  Instead it states the remaining closed-root exchange
identity as a hypothesis and proves that, together with:

* a restricted checked dual,
* an allowed almost-squeeze,
* closed weighted-Hall completeness, and
* positive-root closed extraction,

there can be no strict restricted dual.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

open scoped BigOperators
open PortHall

attribute [local instance] PortHall.portDecEq PortHall.sinkDecEq

variable {I : BankedWallLP}

/-- Closed-root exchange identity in the exact form needed by the W3 skeleton:
from a closed minimal deficient shore with a unique legal root, produce an
allowed cut violating restricted D1 for the given dual.  This is the remaining
graph/quotient cut arithmetic hypothesis, not bookkeeping. -/
def ClosedRootCutViolatesD1
    (Allowed : I.Cut → Prop) (Q : AbstractEscapeQuotient I)
    (d : Dual I) (L : I.Port → ℚ) : Prop :=
  ∀ U : Finset Q.QComp,
    Q.fullClosure U = U →
      MinimalClosedDeficient Q L (Q.exposedPorts U) →
        (∀ D : LegalComponentPartition I (Q.exposedPorts U),
          Fintype.card D.K = 1) →
          ∃ X : I.Cut,
            Allowed X ∧ cutBeta d X + cutGamma d X < cutAlpha d X

/-- W3 abstract skeleton.  The only non-bookkeeping hypotheses are exactly the
named wall bridges: closed weighted Hall, positive-root extraction, and the
closed-root cut exchange identity. -/
theorem noStrictRestrictedDual_of_closedHall_and_exchange
    {Allowed : I.Cut → Prop} {Q : AbstractEscapeQuotient I} {d : Dual I}
    (hd : d.RestrictedChecked Allowed)
    (Z : DualAlmostSqueeze I Allowed d)
    (hHall : ClosedWeightedHallCompleteness Q)
    (hExtract : PositiveRootBlockClosedExtraction Q)
    (hExchange : ClosedRootCutViolatesD1 Allowed Q d Z.portLoad) :
    ¬ d.StrictGap := by
  intro hstrict
  have hFail : WeightedRoutingFailure d Z.portLoad :=
    strictRestrictedDual_gives_weightedRoutingFailure hd Z hstrict
  obtain ⟨U, hUclosed, hMin, hUnique⟩ :=
    uniqueRoot_of_closedWeightedHallCompleteness hHall hExtract hFail
  obtain ⟨X, hAllowed, hbad⟩ := hExchange U hUclosed hMin hUnique
  have hD1 := hd.d1_allowed X hAllowed
  exact not_lt.mpr hD1 hbad

/-- All-cut version of the W3 skeleton.  This is a final-assembly convenience
wrapper: if a dual is checked against every routed cut, it is checked against
the restricted allowed family by `Dual.Checked.restrict`, and the same
closed-Hall/exchange argument rules out strictness. -/
theorem noStrictDual_of_closedHall_and_exchange
    {Allowed : I.Cut → Prop} {Q : AbstractEscapeQuotient I} {d : Dual I}
    (hd : d.Checked)
    (Z : DualAlmostSqueeze I Allowed d)
    (hHall : ClosedWeightedHallCompleteness Q)
    (hExtract : PositiveRootBlockClosedExtraction Q)
    (hExchange : ClosedRootCutViolatesD1 Allowed Q d Z.portLoad) :
    ¬ d.StrictGap :=
  noStrictRestrictedDual_of_closedHall_and_exchange
    (hd.restrict (Allowed := Allowed)) Z hHall hExtract hExchange

end ClosedShore
end Wall
end Erdos23Delta0
