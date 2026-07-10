import Erdos23Delta0.BankedWallLPRestricted

/-!
# Restricted squeeze certificate package

This module names the direct route from a finite restricted-Farkas/squeeze
source to `¬ d.StrictGap`.  It is parallel to the closed-shore
`ForcedEscapeWallCert` wrapper, but bypasses the quotient/Hall/exchange layer:
if every strict restricted dual yields a full `DualSqueeze`, the compiled
restricted squeeze theorem closes the wall immediately.

It is only a consumption wrapper.  The hard theorem remains construction of the
`squeezeOfStrict` field for the real allowed cut family.
-/

namespace Erdos23Delta0
namespace Wall

variable {I : BankedWallLP}

/-- Direct restricted-squeeze wall certificate for one allowed cut family. -/
structure RestrictedSqueezeWallCert (I : BankedWallLP) where
  Allowed : I.Cut → Prop
  squeezeOfStrict :
    ∀ {d : Dual I},
      d.RestrictedChecked Allowed →
        d.StrictGap →
          DualSqueeze I Allowed d

namespace RestrictedSqueezeWallCert

/-- A direct restricted squeeze source rules out every strict restricted dual. -/
theorem noStrictRestrictedDual
    (C : RestrictedSqueezeWallCert I) {d : Dual I}
    (hd : d.RestrictedChecked C.Allowed) :
    ¬ d.StrictGap := by
  intro hstrict
  exact noStrictDual_of_restrictedDualSqueeze hd
    (C.squeezeOfStrict hd hstrict) hstrict

/-- All-cut convenience wrapper. -/
theorem noStrictDual
    (C : RestrictedSqueezeWallCert I) {d : Dual I}
    (hd : d.Checked) :
    ¬ d.StrictGap := by
  exact C.noStrictRestrictedDual
    (Dual.Checked.restrict (Allowed := C.Allowed) hd)

end RestrictedSqueezeWallCert

end Wall
end Erdos23Delta0
