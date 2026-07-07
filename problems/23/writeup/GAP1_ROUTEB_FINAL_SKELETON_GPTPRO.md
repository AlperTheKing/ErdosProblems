# GAP-#1 ROUTE-B FINAL NON-CIRCULAR CLOSURE SKELETON (GPT-Pro MAIN R-A+R-D reply, 2026-07-07, 14535 char)

This is the DEFINITIVE Lean-ready reduction of gap #1 (aggregation Γ≤N² = reserveResidual_nonneg). The entire chain
is specified; exactly TWO residual leaves remain unproven. GPT-Pro's risk ranking: **R-D PositiveSlackAbsorption_Hall
= hardest** (global-to-local token-bank extraction, cannot be validated by stretched tests); R-A NoSideDoorForLongAnnulus
= local CAP geometry, lower risk.

## reserveResidual = N^2 - Gamma  (Claude-verified EXACT). S = Γ-25m, Reserve = 25η - S = N^2 - Γ.

## THE TWO RESIDUAL LEAVES (everything else proven):
### LEAF 1 -- NoSideDoorForLongAnnulus / CAP_PairDoorBoundary_LUniform  [local CAP, lower risk]
For a nested type-B L/(L+2) CAP core inside a min-positive-debt sigma-0 deficient terminal cage with canonical
terminal-shadow U: **every B-edge crossing U is one of the two Ferrers first-split doors, i.e. deltaB(U)={born0,born1}.**
What S1/S2 must prove: (1) U is a Ferrers interval/terminal shadow in the first-split order; (2) the only cover
relations leaving that interval are born0,born1; (3) any additional B-edge crossing U creates a boundary-compat
blocker (extra four-door theta violating Ferrers, side annulus wrong increment, or a proper smaller deficient cage).
GPT-Pro A2: "the real ambient obstruction is NOT convexity once the door endpoints and local paths are fixed; the
real obstruction is deltaB(U) might have extra ambient side doors -- that is exactly NoSideDoorForLongAnnulus." Once
deltaB(U)={born0,born1}, pair-door convexity is L-uniform (Ferrers gives internal/external door distances 1->2).
**Claude ambient gate CONVERGES: _claude_ambient_pairdoor_convexity_gate.py found convexity of the RAW sigma=0 switch
set fails 1000/4000 (extra side doors) BUT metric stability + strict drop hold on ALL 4000 -- confirming the
obstruction is the extra ambient doors (NoSideDoor), not convexity, and the gap#1 CONCLUSION is robust.**

### LEAF 2 -- PositiveSlackAbsorption_Hall  [global-to-local token-bank, HARDEST, non-circular required]
**PositiveSlackAbsorption: sigma(C) > 0  =>  Balance(C) = 25*Bank(C) - Surplus(C) >= 0.** (equivalently
debt(C)>0 => sigma(C)=0). GPT-Pro B0 CIRCULARITY CONSTRAINT: this MUST be proved WITHOUT Gamma-minimality, the
pair-door switch contradiction, Γ(B^U)<Γ(B), Γ≤N², or reserveResidual_nonneg_core. Its signature must NOT take
hGammaMin. It MAY use: max-cut local inequalities, terminal-cage structure, RowDBFactsGeneral, exact token-bank/
Hall/CSP charge certs, ODL row residual nonnegativity. RISK (GPT-Pro): "if this lemma fails, the reserve can be
negative because of positive-slack positive-debt cages that the switch contradiction never reaches."
B3 checkable form = **SlackAbsorptionLocal via a per-cage Hall/CSP charge cert**: surplus atoms A_C (weight(a)),
bank tokens T_C (capacity(t)), charge matrix q(a,t)>=0; checker verifies exact rationals:
  for each surplus atom a: sum_t q(a,t) = weight(a);  for each bank token t: sum_a q(a,t) <= capacity(t);
  sum_a weight(a) = Surplus(C);  sum_t capacity(t) <= 25*Bank(C).
Then Surplus(C) <= 25*Bank(C) => Balance(C) >= 0. Residual = existence of this matching for EVERY positive-slack cage.

## PROVEN (general) -- the switch algebra + extraction + assembly:
- pairDoor_deltaM_exact_of_maxcut: |deltaM(U)| <= |deltaB(U)| = 2, oldLo/oldHi distinct => deltaM(U)={oldLo,oldHi}.
- pairDoor_metric_stability: given deltaB/deltaBU doors + PairDoorConvex(B) & (B^U), for bad e not crossing U,
  ell_{B^U}(e)=ell_B(e). Proof: same-side path uses 0 or 2 doors; convexity bounds the 2-door detour by the inside
  path; B[U]=B^U[U], B[V\U]=B^U[V\U] (switch changes only crossing edges) => same-side distances equal.
- pairTypeBTheta_gammaDrop_pos: Γ(B)-Γ(B^U) >= L^2+(L+2)^2-L^2-L^2 = 4L+4 > 0.
- pairTypeBTheta_switch_connected.
- B4 negative_reserve_yields_minPositive_sigma0_deficient_cage (NON-CIRCULAR): from L1 Reserve=FreeBank+GoodBalance+
  sum_C Balance(C), L2 FreeBank>=0, L3 GoodBalance>=0, L4 sigma(C)>=0 (max-cut), L5 PositiveSlackAbsorption, L6
  Balance(C)<0=>Deficient, L7 terminalization. Proof: Reserve<0 => some Balance(C)<0 => Debt(C)>0 => choose minimal
  => sigma(C)>=0; if sigma>0 then L5 gives Balance>=0 contra; so sigma=0; deficient. (No Γ-min, no switch.)

## FINAL LEAN THEOREM SIGNATURES (GPT-Pro):
- CAP_PairDoorTheta_LUniform (G B C gate hTri hMax hNested:NestedTypeBCore) : PairTypeBThetaFacts G B gate.
  [PairTypeBThetaFacts = Odd L /\ 5<=L /\ born0!=born1 /\ oldLo!=oldHi /\ deltaB=pairSet born0 born1 /\ oldLo,oldHi
   in badEdges /\ in edgeBoundary U /\ ell_B oldLo=L /\ ell_B oldHi=L+2 /\ ell_{B^U} born0<=L /\ born1<=L /\
   PairDoorConvex B U born0 born1 /\ PairDoorConvex (switchCut B U) U oldLo oldHi /\ PairDoorSidesConnected B U ...]
  RESIDUAL: NoSideDoorForLongAnnulus / CAP_PairDoorBoundary_LUniform.
- pairDoor_metric_stability (...hDoorB hDoorBU hConvB hConvBU e hBad hStable) : ell (switchCut B U) e = ell B e.
- pairDoor_deltaM_exact_of_maxcut (...hMax hBorn hBornNe hOld*Bad hOld*Cross hOldNe) : deltaM B U = pairSet oldLo oldHi.
- pairTypeBTheta_gammaDrop_pos (...hFacts:PairTypeBThetaFacts) : GammaOfCut (switchCut B U) < GammaOfCut B.
- PositiveSlackAbsorption (G B C hRows:RowDBFactsGeneral hSigmaPos:0<sigma) : 0 <= Balance G B rowDB C.
  [NO hGammaMin -- non-circular by signature.] RESIDUAL: PositiveSlackAbsorption_Hall.
- negative_reserve_yields_minPositive_sigma0_deficient_cage (G B rowDB hMax hRows hLedger:ReserveLedgerComplete
  hAbsorb:(forall C, 0<sigma C -> 0<=Balance C) hNeg:reserveResidual<0) : exists C, MinimalPositiveDebtCage /\
  sigma C=0 /\ DeficientTerminalCage.
- reserveResidual_nonneg_core_routeB (G B rowDB hTri hMax hConn hGammaMin hRows hLedger hAbsorb hCAP:(forall C,
  Deficient C -> exists gate, PairTypeBThetaFacts /\ gateInsideCage)) : 0 <= reserveResidual G B rowDB.
  Proof: assume <0; theorem-8 gives C; hCAP gives gate; gammaDrop_pos + switch_connected; sigma(gate.U)=0 from
  no-cross => switch preserves max cut; contradict Γ-minimality. THE FINAL NON-CIRCULAR ROUTE-B CLOSURE.

## GAP#1 STATUS: fully reduced. 2 residual leaves = NoSideDoorForLongAnnulus (local CAP) + PositiveSlackAbsorption_Hall
(per-cage Hall charge cert, hardest, non-circular). ReserveLedgerComplete = per-cage bank decomposition (top-level
Reserve=N^2-Γ verified). NEXT: (Claude) formalize this skeleton in Lean as a NEW module (reserveResidual:=N^2-Γ;
the 2 leaves + ReserveLedgerComplete as NAMED hypotheses, never sorry; prove the switch algebra + extraction + top);
(GPT-Pro) prove NoSideDoorForLongAnnulus from S1/S2 boundary-compat blockers + construct PositiveSlackAbsorption_Hall
charge cert. Gap#1 NOT closed until both leaves proven.
