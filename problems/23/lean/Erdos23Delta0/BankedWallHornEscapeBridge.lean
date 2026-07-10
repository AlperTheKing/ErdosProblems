import Erdos23Delta0.BankedWallHornQuotient
import Erdos23Delta0.BankedWallForcedEscapeCert

/-!
# Horn forced-escape wall bridge

This is a thin packaging layer for the current Gap#1 route.  The graph-side
adapter is expected to construct a `HornEscapeSurface`.  Once closed weighted
Hall, positive-root extraction, and closed-root exchange are proved for the
quotient `surface.toQ`, this file converts those fields into the already
compiled `ForcedEscapeWallInputs` consumer.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

variable {I : BankedWallLP}

/-- Forced-escape wall inputs stated with a Horn closure surface instead of an
arbitrary abstract quotient.  This keeps the final assembly honest about the
specific GPT-Pro/Fable route while reusing the W3 consumer. -/
structure HornForcedEscapeWallInputs (I : BankedWallLP) where
  Allowed : I.Cut → Prop
  surface : HornEscapeSurface I
  closedHall : ClosedWeightedHallCompleteness surface.toQ
  positiveRootExtraction : PositiveRootBlockClosedExtraction surface.toQ
  closedRootExchange :
    ∀ {d : Dual I} (Z : DualAlmostSqueeze I Allowed d),
      ClosedRootCutViolatesD1 Allowed surface.toQ d Z.portLoad

namespace HornForcedEscapeWallInputs

/-- Forget the Horn presentation and expose the W3 input package. -/
noncomputable def toForcedEscapeWallInputs (W : HornForcedEscapeWallInputs I) :
    ForcedEscapeWallInputs I where
  Allowed := W.Allowed
  quotient := W.surface.toQ
  closedHall := W.closedHall
  positiveRootExtraction := W.positiveRootExtraction
  closedRootExchange := W.closedRootExchange

/-- Restricted-dual consumption form for Horn-presented wall inputs. -/
theorem noStrictRestrictedDual
    (W : HornForcedEscapeWallInputs I) {d : Dual I}
    (hd : d.RestrictedChecked W.Allowed)
    (Z : DualAlmostSqueeze I W.Allowed d) :
    ¬ d.StrictGap :=
  (toForcedEscapeWallInputs W).noStrictRestrictedDual hd Z

/-- All-cut consumption form for Horn-presented wall inputs. -/
theorem noStrictDual
    (W : HornForcedEscapeWallInputs I) {d : Dual I}
    (hd : d.Checked)
    (Z : DualAlmostSqueeze I W.Allowed d) :
    ¬ d.StrictGap :=
  (toForcedEscapeWallInputs W).noStrictDual hd Z

end HornForcedEscapeWallInputs

/-- Complete Horn-presented wall certificate: Horn closure graph inputs plus
the finite rational source that turns strict restricted duals into allowed
almost-squeezes. -/
structure HornForcedEscapeWallCert (I : BankedWallLP) where
  wall : HornForcedEscapeWallInputs I
  almostSqueezeOfStrict :
    ∀ {d : Dual I},
      d.RestrictedChecked wall.Allowed →
        d.StrictGap →
          DualAlmostSqueeze I wall.Allowed d

namespace HornForcedEscapeWallCert

/-- Convert the Horn-presented certificate into the existing forced-escape
certificate package. -/
noncomputable def toForcedEscapeWallCert (C : HornForcedEscapeWallCert I) :
    ForcedEscapeWallCert I where
  wall := C.wall.toForcedEscapeWallInputs
  almostSqueezeOfStrict := C.almostSqueezeOfStrict

/-- Restricted-dual theorem for the complete Horn-presented certificate. -/
theorem noStrictRestrictedDual
    (C : HornForcedEscapeWallCert I) {d : Dual I}
    (hd : d.RestrictedChecked C.wall.Allowed) :
    ¬ d.StrictGap :=
  (toForcedEscapeWallCert C).noStrictRestrictedDual hd

/-- All-cut theorem for the complete Horn-presented certificate. -/
theorem noStrictDual
    (C : HornForcedEscapeWallCert I) {d : Dual I}
    (hd : d.Checked) :
    ¬ d.StrictGap :=
  (toForcedEscapeWallCert C).noStrictDual hd

end HornForcedEscapeWallCert

end ClosedShore
end Wall
end Erdos23Delta0
