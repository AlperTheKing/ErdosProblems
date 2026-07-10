import Erdos23Delta0.BankedWallEndgameCert
import Erdos23Delta0.BankedWallLPFiniteFarkas

/-!
# Finite-Farkas endgame bridge for the banked wall

The constructive rational alternative produces a routed squeeze exactly when
there is no strict alpha-fixed restricted dual.  Every accepted endgame wall
certificate already rules out such a restricted dual after it is viewed on
the existing `Dual.RestrictedChecked` surface.  This module composes those two
facts and leaves construction of `EndgameWallCert` as the only wall input.
-/

namespace Erdos23Delta0
namespace Wall

variable {I : BankedWallLP}

namespace EndgameWallCert

/-- A complete endgame wall certificate, together with the elementary alpha
and capacity signs, constructs the full routed squeeze supplied by the exact
rational finite-Farkas alternative. -/
theorem dualSqueeze_exists
    (C : EndgameWallCert I) (d : Dual I)
    (halpha : forall a, 0 <= d.alpha a)
    (hcap : forall s, 0 <= I.cap s) :
    Nonempty (DualSqueeze I C.allowed d) := by
  apply (dualSqueeze_exists_iff_no_restrictedStrict C.allowed d hcap).2
  rintro ⟨R, hstrict⟩
  have hd : R.toDual.RestrictedChecked C.allowed :=
    R.toRestrictedChecked halpha hcap
  exact C.noStrictRestrictedDual hd hstrict

end EndgameWallCert

end Wall
end Erdos23Delta0
