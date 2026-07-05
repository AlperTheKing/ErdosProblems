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

inductive GateBCandidate where
  | none
  | candidateV1
  | candidateV2
deriving Repr, DecidableEq

def GateBCandidate.expectsOps : GateBCandidate -> Bool
  | GateBCandidate.none => false
  | GateBCandidate.candidateV1 => true
  | GateBCandidate.candidateV2 => true

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
  (c.den != 0) && (intListSum c.terms == c.target)

def ScaledGeCert.check (c : ScaledGeCert) : Bool :=
  (c.den != 0) && (c.lhs + Int.ofNat c.margin == c.rhs)

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
  gateBCandidate : GateBCandidate
  pressure : ScaledEqCert
  finiteMargin : ScaledGeCert
  gateBDominance : ScaledGeCert
  opSteps : List OpStepPilot
deriving Repr

def RowPilot.candidateCheck (r : RowPilot) : Bool :=
  GateBCandidate.expectsOps r.gateBCandidate == !r.opSteps.isEmpty

def RowPilot.check (r : RowPilot) : Bool :=
  ScaledEqCert.check r.pressure &&
  ScaledGeCert.check r.finiteMargin &&
  ScaledGeCert.check r.gateBDominance &&
  RowPilot.candidateCheck r &&
  opStepListCheck r.opSteps

def rowPilotListCheck : List RowPilot -> Bool
  | [] => true
  | r :: rs => RowPilot.check r && rowPilotListCheck rs

def rowPilotCaseCount (tag : BranchBCase) : List RowPilot -> Nat
  | [] => 0
  | r :: rs => (if r.caseTag = tag then 1 else 0) + rowPilotCaseCount tag rs

def rowPilotCandidateCount (tag : GateBCandidate) : List RowPilot -> Nat
  | [] => 0
  | r :: rs => (if r.gateBCandidate = tag then 1 else 0) + rowPilotCandidateCount tag rs

def rowPilotGateBRowCount : List RowPilot -> Nat
  | [] => 0
  | r :: rs => (if GateBCandidate.expectsOps r.gateBCandidate then 1 else 0) + rowPilotGateBRowCount rs

def branchBCaseCountVector (rows : List RowPilot) : List Nat := [
  rowPilotCaseCount BranchBCase.tightZero rows,
  rowPilotCaseCount BranchBCase.freePacketExchange rows,
  rowPilotCaseCount BranchBCase.sparseM1BankLBypass rows,
  rowPilotCaseCount BranchBCase.muNuk rows,
  rowPilotCaseCount BranchBCase.muNukRepaired rows,
  rowPilotCaseCount BranchBCase.detourResidual rows
]

def branchBCandidateCountVector (rows : List RowPilot) : List Nat := [
  rowPilotCandidateCount GateBCandidate.none rows,
  rowPilotCandidateCount GateBCandidate.candidateV1 rows,
  rowPilotCandidateCount GateBCandidate.candidateV2 rows
]

end Cert
end Erdos23Delta0
