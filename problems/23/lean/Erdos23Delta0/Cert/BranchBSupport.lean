/- Generated Branch-B certificate support definitions. -/
import Mathlib

namespace Erdos23Delta0
namespace Cert

inductive BranchBCase where
  | tightZero
  | freePacketExchange
  | sparseM1BankLBypass
  | muNuk
  | muNukRepaired
  | detourResidual
deriving Repr, DecidableEq

inductive DictClass where
  | empty
  | terminalPrefixRawExtraction
  | terminalPrefixLaneAddition
  | noncrossingCoBExtraction
  | noncrossingCoBComponentAddition
deriving Repr, DecidableEq

structure ScaledEqCert where
  terms : List Int
  target : Int
  den : Nat
  proofMode : String
deriving Repr

structure ScaledGeCert where
  lhs : Int
  rhs : Int
  margin : Nat
  den : Nat
  proofMode : String
deriving Repr

def intListSum : List Int -> Int
  | [] => 0
  | x :: xs => x + intListSum xs

def natListSum : List Nat -> Nat
  | [] => 0
  | x :: xs => x + natListSum xs

def ScaledEqCert.check (c : ScaledEqCert) : Bool :=
  intListSum c.terms == c.target

def ScaledGeCert.check (c : ScaledGeCert) : Bool :=
  c.lhs + Int.ofNat c.margin == c.rhs

structure OpStepPilot where
  opClass : DictClass
  stepRole : String
  eB_XS : Int
  eM_XS : Int
  eB_XO : Int
  eM_XO : Int
  q : Int
  rho : Int
  pieceCount : Nat
  pieceContribs : List Nat
  pieceSum : Nat
deriving Repr

def OpStepPilot.expectedQ (s : OpStepPilot) : Int :=
  s.eB_XS - s.eM_XS - s.eB_XO + s.eM_XO

def OpStepPilot.expectedRho (s : OpStepPilot) : Int :=
  if s.q < 0 then 0 else 25 * s.q

def OpStepPilot.check (s : OpStepPilot) : Bool :=
  (s.q == OpStepPilot.expectedQ s) &&
  (s.rho == OpStepPilot.expectedRho s) &&
  (s.pieceContribs.length == s.pieceCount) &&
  (natListSum s.pieceContribs == s.pieceSum) &&
  (s.rho == Int.ofNat s.pieceSum)

def opStepListCheck : List OpStepPilot -> Bool
  | [] => true
  | s :: ss => OpStepPilot.check s && opStepListCheck ss

structure RowPilot where
  name : String
  n : Nat
  m : Nat
  L : Nat
  caseTag : BranchBCase
  pressure : ScaledEqCert
  finiteMargin : ScaledGeCert
  opSteps : List OpStepPilot
deriving Repr

def RowPilot.check (r : RowPilot) : Bool :=
  ScaledEqCert.check r.pressure &&
  ScaledGeCert.check r.finiteMargin &&
  opStepListCheck r.opSteps

def rowPilotListCheck : List RowPilot -> Bool
  | [] => true
  | r :: rs => RowPilot.check r && rowPilotListCheck rs

end Cert
end Erdos23Delta0
