/- Shared support for generated Rung-2 source-certificate data. -/
import Mathlib

namespace Erdos23Delta0
namespace Cert

structure Rung2SourceCoeff where
  sourceCol : Nat
  num : Int
  den : Nat
deriving Repr

def Rung2SourceCoeff.check (columnsChecked : Nat) (c : Rung2SourceCoeff) : Bool :=
  decide (c.sourceCol < columnsChecked) && decide (0 <= c.num) && decide (0 < c.den)

def rung2SourceCoeffListCheck (columnsChecked : Nat) : List Rung2SourceCoeff -> Bool
  | [] => true
  | c :: cs => Rung2SourceCoeff.check columnsChecked c && rung2SourceCoeffListCheck columnsChecked cs

def natListSum : List Nat -> Nat
  | [] => 0
  | x :: xs => x + natListSum xs

structure Rung2SourceMeta where
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
  fullZeroResidualCount : Nat
  solutionSha256 : String
  checkSummarySha256 : String
  modularSummarySha256 : String
deriving Repr

def Rung2SourceMeta.check (m : Rung2SourceMeta) : Bool :=
  (m.nonzeroSourceColumns == m.solutionRecords) &&
  (m.solutionNegativeCount == 0) &&
  (m.fullNegativeResidualCount == 0) &&
  (m.fullMinResidual == "0") &&
  decide (0 < m.columnsChecked)

end Cert
end Erdos23Delta0
