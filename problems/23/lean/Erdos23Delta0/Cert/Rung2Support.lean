/- Shared support for generated Rung-2 exact certificate data. -/
import Mathlib

namespace Erdos23Delta0
namespace Cert

structure Rung2Coeff where
  sourceCol : Nat
  num : Int
  den : Nat
deriving Repr

def Rung2Coeff.check (columnsChecked : Nat) (c : Rung2Coeff) : Bool :=
  decide (c.sourceCol < columnsChecked) && decide (0 <= c.num) && decide (0 < c.den)

def rung2CoeffListCheck (columnsChecked : Nat) : List Rung2Coeff -> Bool
  | [] => true
  | c :: cs => Rung2Coeff.check columnsChecked c && rung2CoeffListCheck columnsChecked cs

def natListSum : List Nat -> Nat
  | [] => 0
  | x :: xs => x + natListSum xs

structure Rung2Meta where
  chart : Nat
  dominant : Nat
  band : String
  support : String
  columnsChecked : Nat
  nonzeroSourceColumns : Nat
  solutionRecords : Nat
  solutionNegativeCount : Nat
  fullNegativeResidualCount : Nat
  fullMinResidual : String
  badRow : Nat
  badBeta : List Nat
  repairSourceCol : Nat
  repairColumnName : String
  repairColumnKind : String
  repairMultiplierExp : List Nat
  solutionSha256 : String
  repairSummarySha256 : String
  checkSummarySha256 : String
deriving Repr

def Rung2Meta.check (m : Rung2Meta) : Bool :=
  (m.chart == 0) &&
  (m.dominant == 7) &&
  (m.band == "near_2s_minus_1") &&
  (m.support == "negative") &&
  (m.columnsChecked == 43128) &&
  (m.nonzeroSourceColumns == m.solutionRecords) &&
  (m.solutionNegativeCount == 0) &&
  (m.fullNegativeResidualCount == 0) &&
  (m.fullMinResidual == "0") &&
  (m.badRow == 71491) &&
  (m.badBeta == [1, 1, 0, 0, 2, 2, 1, 0, 3, 1]) &&
  (m.repairSourceCol == 5251) &&
  (m.repairColumnName == "F5") &&
  (m.repairColumnKind == "gen") &&
  (m.repairMultiplierExp == [1, 0, 0, 0, 2, 2, 1, 0, 3, 0])

end Cert
end Erdos23Delta0
