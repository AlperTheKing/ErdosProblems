/- Generated/shared RawPoly structures for exact certificate data. -/
import Mathlib

namespace Erdos23Delta0
namespace Cert

structure RawTerm where
  coeff : Nat
  exps : List Nat
deriving Repr

abbrev RawPoly := List RawTerm

end Cert
end Erdos23Delta0
