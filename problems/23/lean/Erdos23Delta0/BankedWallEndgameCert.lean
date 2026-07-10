import Erdos23Delta0.BankedWallHornEscapeBridge
import Erdos23Delta0.BankedWallRestrictedSqueezeCert

/-!
# Endgame wall certificate selector

The Gap#1 wall currently has two accepted consumer routes:

* the closed-shore forced-escape route, packaged as
  `ClosedShore.ForcedEscapeWallCert`;
* the same route in its Horn-closure presentation, packaged as
  `ClosedShore.HornForcedEscapeWallCert`;
* the direct restricted-squeeze route, packaged as `RestrictedSqueezeWallCert`.

This module gives final assembly a single route-agnostic certificate type.  It
does not construct either hard certificate.
-/

namespace Erdos23Delta0
namespace Wall

variable {I : BankedWallLP}

/-- A complete wall certificate may arrive by either currently supported route. -/
inductive EndgameWallCert (I : BankedWallLP) : Type 2 where
  | forcedEscape (C : ClosedShore.ForcedEscapeWallCert I)
  | hornForcedEscape (C : ClosedShore.HornForcedEscapeWallCert I)
  | restrictedSqueeze (C : RestrictedSqueezeWallCert I)

namespace EndgameWallCert

/-- The allowed cut family attached to the selected wall route. -/
def allowed : EndgameWallCert I → I.Cut → Prop
  | forcedEscape C => C.wall.Allowed
  | hornForcedEscape C => C.wall.Allowed
  | restrictedSqueeze C => C.Allowed

@[simp] theorem allowed_forcedEscape (C : ClosedShore.ForcedEscapeWallCert I) :
    allowed (forcedEscape C) = C.wall.Allowed := rfl

@[simp] theorem allowed_hornForcedEscape
    (C : ClosedShore.HornForcedEscapeWallCert I) :
    allowed (hornForcedEscape C) = C.wall.Allowed := rfl

@[simp] theorem allowed_restrictedSqueeze (C : RestrictedSqueezeWallCert I) :
    allowed (restrictedSqueeze C) = C.Allowed := rfl

/-- Route-agnostic restricted-dual consumer. -/
theorem noStrictRestrictedDual
    (C : EndgameWallCert I) {d : Dual I}
    (hd : d.RestrictedChecked C.allowed) :
    ¬ d.StrictGap := by
  cases C with
  | forcedEscape C =>
      exact C.noStrictRestrictedDual (by simpa [allowed] using hd)
  | hornForcedEscape C =>
      exact C.noStrictRestrictedDual (by simpa [allowed] using hd)
  | restrictedSqueeze C =>
      exact C.noStrictRestrictedDual (by simpa [allowed] using hd)

/-- Route-agnostic all-cut consumer for final assembly. -/
theorem noStrictDual
    (C : EndgameWallCert I) {d : Dual I}
    (hd : d.Checked) :
    ¬ d.StrictGap := by
  cases C with
  | forcedEscape C =>
      exact C.noStrictDual hd
  | hornForcedEscape C =>
      exact C.noStrictDual hd
  | restrictedSqueeze C =>
      exact C.noStrictDual hd

end EndgameWallCert

end Wall
end Erdos23Delta0
