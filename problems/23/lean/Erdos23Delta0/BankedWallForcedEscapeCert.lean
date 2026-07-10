import Erdos23Delta0.BankedWallForcedEscapeBridge

/-!
# Forced-escape wall certificate package

`BankedWallForcedEscapeBridge` packages the closed-shore graph inputs consumed
by the W3 skeleton.  The full wall also needs the finite rational
Farkas/almost-squeeze source.  This module names that combined surface.

It is intentionally only a consumption wrapper.  It does not construct the
forced-escape quotient, closed Hall proof, root-locality proof, exchange cut, or
Farkas source.
-/

namespace Erdos23Delta0
namespace Wall
namespace ClosedShore

variable {I : BankedWallLP}

/-- A complete forced-escape wall certificate for one banked wall LP instance:
closed-shore graph inputs plus the finite source that turns every strict
restricted dual into an allowed almost-squeeze. -/
structure ForcedEscapeWallCert (I : BankedWallLP) where
  wall : ForcedEscapeWallInputs I
  almostSqueezeOfStrict :
    ∀ {d : Dual I},
      d.RestrictedChecked wall.Allowed →
        d.StrictGap →
          DualAlmostSqueeze I wall.Allowed d

namespace ForcedEscapeWallCert

/-- Combined restricted-dual theorem: the closed-shore inputs and the finite
almost-squeeze source rule out every strict restricted dual. -/
theorem noStrictRestrictedDual
    (C : ForcedEscapeWallCert I) {d : Dual I}
    (hd : d.RestrictedChecked C.wall.Allowed) :
    ¬ d.StrictGap := by
  intro hstrict
  exact C.wall.noStrictRestrictedDual hd
    (C.almostSqueezeOfStrict hd hstrict) hstrict

/-- All-cut convenience wrapper. -/
theorem noStrictDual
    (C : ForcedEscapeWallCert I) {d : Dual I}
    (hd : d.Checked) :
    ¬ d.StrictGap := by
  exact C.noStrictRestrictedDual
    (Dual.Checked.restrict (Allowed := C.wall.Allowed) hd)

end ForcedEscapeWallCert

end ClosedShore
end Wall
end Erdos23Delta0
