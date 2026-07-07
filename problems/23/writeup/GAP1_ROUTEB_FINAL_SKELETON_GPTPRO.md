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

================================================================================
## R-D + R-A LEAF REPLY (GPT-Pro, 2026-07-07, 12120 char) -- gap#1 -> ONE irreducible residual
================================================================================
GPT-Pro attacked R-D first and gave the EXACT ledger definitions + a KEY R-A<->R-D bridge.

### R-D exact definitions:
- ell(e)^2 - 25 = sum_{j=0}^{r_e-1} [(5+2(j+1))^2-(5+2j)^2], increment d_j = (7+2j)^2-(5+2j)^2 = 8j+24. (r_e=(ell(e)-5)/2)
- Surplus atoms A(C) = {(e,j): e in M, mu_C(e)>0, 0<=j<r_e}; demand_C(e,j) = mu_C(e)*(8j+24).
- Surplus(C) = sum_a demand = sum_e mu_C(e)*(ell(e)^2-25). [mu_C(e) integral 0/1.]
- Bank tokens T(C) (kinds C5Cell/DoorSlack/AmbientSlack/PruneReserve), cap_C(t)>=0; BankCap(C)=sum cap = 25*Bank(C).
- CageHallCert = charge matrix q_C(a,t)>=0 (0 if not CanCharge = Ferrers domination) + unused. Checker (exact rational):
  atom-exactness sum_t q(a,t)=demand(a); token-capacity sum_a q(a,t)+unused(t)=cap(t), unused>=0.

### PROVABLE NOW (GPT-Pro "Final answer" -- 3 parts, 2 now Lean-formalized by Claude):
1. CageHallCert soundness: exact charge matrix => Balance(C)>=0. [CLAUDE LEAN: surplus_le_bankCap_of_hall_charge +
   balance_nonneg_of_hall_charge in RouteBAssembly.lean, GREEN + axiom-clean -- Surplus=sum demand <= sum cap=BankCap
   by atom-exactness+token-capacity+sum_comm; non-circular.]
2. PositiveSlackAbsorptionProvider soundness: checked Hall certs for ALL sigma>0 cages => absorption.
3. Negative reserve extraction: Reserve<0 + absorption => min-positive-debt sigma=0 deficient cage. [CLAUDE LEAN:
   zeroSlack_negBalance_cage_of_neg_reserve in RouteBAssembly.lean, GREEN + axiom-clean, NON-CIRCULAR (no hGammaMin/switch).]

### THE SINGLE IRREDUCIBLE RESIDUAL (R-D leaf):
**PositiveSlackHallPrefix**: for every terminal cage C with sigma(C)>0, order atoms/tokens by the Ferrers door/annulus
order; for every Ferrers prefix P of surplus atoms, demand(P) <= capacity(N(P)). Then greedy Ferrers filling
constructs q_C => the Hall matching exists => Balance(C)>=0. "A single sigma>0 / Balance<0 cage would break the
extraction, and switch Gamma-minimality cannot repair it without circularity." = THE hardest node, global-to-local.

### R-A resolved into 3 options; Option C = the R-A<->R-D BRIDGE:
- Option A CAP_PairDoorBoundary_LUniform (deltaB(U)={born0,born1} for canonical U). If Claude's gate sees extra side
  doors for the SAME canonical U, Option A is FALSE. [my ambient gate found side-doors on RAW switch sets -- need to
  test the CANONICAL U specifically to decide A.]
- Option B CAP_PairDoorBoundary_AfterDoorClosure (replace raw U by canonical door-closed U^cl).
- **Option C SideDoorCreatesPositiveSlackAbsorbableCage: any extra side door creates a POSITIVE-SLACK subcage whose
  balance is nonneg by PositiveSlackAbsorption, so it cannot occur in the minimal-positive-debt ZERO-SLACK
  extraction. "Option C may be the natural bridge between R-A and R-D."** My ambient finding (side-doors = positive-
  slack leakages) SUPPORTS Option C -> R-A largely SUBSUMED into R-D.

## GAP#1 NOW = ESSENTIALLY ONE IRREDUCIBLE RESIDUAL: PositiveSlackHallPrefix (universal Ferrers prefix-Hall for
positive-slack cages). Everything else (extraction, charge-cert soundness, R-A via Option C) is provable/proven;
Claude has 5 RouteBAssembly.lean theorems GREEN + axiom-clean covering the extraction + charge-cert soundness.
Retask to MAIN: prove PositiveSlackHallPrefix (Ferrers prefix inequalities) + confirm R-A Option C. Gap#1 NOT closed.

================================================================================
## PositiveSlackHallPrefix REPLY (GPT-Pro, 2026-07-07, 10316 char) -- EXACT sigma/bank defs + FINAL residual map
================================================================================
### EXACT sigma(C) def (CONFIRMS Claude probe): sigma(C) = delta_B(C) - delta_M(C) = #unmatched B-doors after
matching each crossing bad-door to a crossing B-door. >=0 by max-cutness. [= -boundary_delta: boundary_delta =
delta_M - delta_B = -sigma. So Claude's _claude_sigma_positive_debt_probe.py (classifying by boundary_delta) IS
measuring -sigma correctly.]

### Bank token capacities (exact):
- C5Cell: ordinary C5-bank units.
- DoorSlack d (the positive-slack source): cap = 25*mass_C(d); TOTAL door-slack cap = 25*sigma(C). So sigma>0 feeds
  the Hall bank through DoorSlack.
- AmbientSlack h: cap = (N-|V(X_h)|)*tau_C(h) [from sign-atom R_full = R_local + (N-|Vcomp|)*T], surplus units.
- PruneReserve.
- BankCap(C) = sum_t cap_C(t); Balance(C) = BankCap(C) - Surplus(C); Debt(C) = -Balance(C).

### Surplus atoms: ell(e)=5+2*r_e; ell(e)^2-25 = sum_{j=0}^{r_e-1}(8j+24); atom demand weight_C(e,j)=mu_C(e)*(8j+24).

### The R-D residual PositiveSlackHallPrefix (necessary+sufficient for the nonneg charge matrix):
For sigma(C)>0, every Ferrers prefix P_i: Demand(i) <= NeighborCap(i), where NeighborCap(i)=C5Cap(i)+AmbientCap(i)+
PruneCap(i)+DoorSlackCap(i), DoorSlackCap(i)=25*sigma_i (prefix-local unmatched B-door mass sigma_i=delta_B(P_i)-delta_M(P_i)).
Core checkable inequality: PrefixDeficit(i) := Demand(i)-C5Cap(i)-AmbientCap(i)-PruneCap(i) <= 25*sigma_i.

### R-A Option C needs MORE than absorption (a PRUNING lemma):
A side-door d creates a positive-slack subcage D_d (sigma(D_d)>0, cleanest =1). PositiveSlackAbsorption => Balance(D_d)>=0
(not a source of positive debt). BUT to rule out side doors in the min-positive-debt ZERO-slack extraction you ALSO
need SideDoorPruningPreservesPositiveDebt: C min-positive-debt + D_d proper side-door subcage with Balance(D_d)>=0 =>
pruning D_d leaves a proper descendant C' with positive debt => contradicts minimality. Chain: extra side door ->
positive-slack subcage -> absorption gives nonneg balance -> pruning leaves smaller positive-debt cage -> contra minimality.

### FINAL RESIDUAL MAP (GPT-Pro):
- ALREADY FORMALIZED (Claude Lean): reserveResidual=N^2-Gamma; Hall charge-cert soundness (checked q => Surplus<=BankCap
  => Balance>=0); B4 non-circular extraction.
- REMAINING: gap#1 = PositiveSlackHallPrefix ALONE **iff** ReserveLedgerComplete/terminalization already proves side-
  door pruning; ELSE gap#1 = PositiveSlackHallPrefix + SideDoorCreatesAbsorbablePrunableSubcage. "Ambient side doors
  exist for raw switches, so the safe formal statement is the PRUNING version." R-D is the riskier/more important node.

### CLAUDE PROBE (_claude_sigma_positive_debt_probe.py, glue core+C5, sigma-def now CONFIRMED): ALL 36000 positive-debt
deficient caps have sigma=0 (boundary_delta=0); ZERO at sigma>0. SUGGESTS a POSSIBLE BYPASS: if "positive-debt
deficient cage => sigma=0" holds directly, the minimal positive-debt cage is automatically sigma=0 and
PositiveSlackHallPrefix (about sigma>0 cages) is not needed. CAVEAT: one family + possible detection bias; needs
GPT-Pro to (a) confirm the detection can find sigma>0 caps, (b) say if "positive-debt=>sigma=0" is directly provable.

### !!! CORRECTION (2026-07-07T19:20Z) to the CLAUDE PROBE note above !!!
boundary_delta(n,adj,side,mask) = dB - dM = |delta_B| - |delta_M| = **+sigma(C)** (NOT -sigma). Verified from the
def (_codex_k2t_switch_probe.py:47). So sigma=0 <=> bd=0, sigma>0 <=> bd>0. The first probe run had `if bd>0: continue`
which SKIPPED all sigma>0 caps -> its "all 36000 caps sigma=0, zero sigma>0" was a BUG ARTIFACT (bias diagnostic
sigmapos_masks=0 CAUGHT it). Probe FIXED (sigma>0 <=> bd>0) and re-running. The "possible bypass" claim is RETRACTED
pending the corrected run. (The sigma=0-filtered gates -- _claude_ambient_pairdoor_convexity_gate.py,
_claude_multiatom_gammadrop_gate.py -- were CORRECT; only this new probe had the sign confusion in its relaxation.)
