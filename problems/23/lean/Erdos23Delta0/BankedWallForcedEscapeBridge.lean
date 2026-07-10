import Erdos23Delta0.BankedWallW3Skeleton

/-!
# Forced-escape wall bridge

This module packages the current Gap#1 wall obligations into one provider-facing
structure.  It does not prove the graph-side obligations.  Its purpose is to
make the remaining forced-escape route explicit:

* instantiate the concrete `AbstractEscapeQuotient`;
* prove closed weighted-Hall completeness;
* prove positive-root closed extraction;
* prove the closed-root D1 exchange identity for each almost-squeeze.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

variable {I : BankedWallLP}

/-- The concrete forced-escape wall input package needed by the W3 skeleton.
The hard fields are graph-side statements for the real closure. -/
structure ForcedEscapeWallInputs (I : BankedWallLP) where
  Allowed : I.Cut → Prop
  quotient : AbstractEscapeQuotient I
  closedHall : ClosedWeightedHallCompleteness quotient
  positiveRootExtraction : PositiveRootBlockClosedExtraction quotient
  closedRootExchange :
    ∀ {d : Dual I} (Z : DualAlmostSqueeze I Allowed d),
      ClosedRootCutViolatesD1 Allowed quotient d Z.portLoad

namespace ForcedEscapeWallInputs

/-- Restricted-dual consumption form: once the concrete forced-escape wall
inputs and an almost-squeeze are supplied, strict restricted duals are ruled
out by the compiled W3 skeleton. -/
theorem noStrictRestrictedDual
    (W : ForcedEscapeWallInputs I) {d : Dual I}
    (hd : d.RestrictedChecked W.Allowed)
    (Z : DualAlmostSqueeze I W.Allowed d) :
    ¬ d.StrictGap :=
  noStrictRestrictedDual_of_closedHall_and_exchange
    hd Z W.closedHall W.positiveRootExtraction (W.closedRootExchange Z)

/-- All-cut consumption form. -/
theorem noStrictDual
    (W : ForcedEscapeWallInputs I) {d : Dual I}
    (hd : d.Checked)
    (Z : DualAlmostSqueeze I W.Allowed d) :
    ¬ d.StrictGap :=
  noStrictDual_of_closedHall_and_exchange
    hd Z W.closedHall W.positiveRootExtraction (W.closedRootExchange Z)

end ForcedEscapeWallInputs

end ClosedShore
end Wall
end Erdos23Delta0
