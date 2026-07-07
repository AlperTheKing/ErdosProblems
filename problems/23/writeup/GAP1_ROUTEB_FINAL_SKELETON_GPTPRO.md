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

### CORRECTED PROBE RESULT (2026-07-07T19:52Z, glue core+C5): with sigma>0 <=> boundary_delta>0 fixed:
- 81,670,000 sigma>0 switch sets enumerated; **71,435,000 REACHED witness_structure** (nonempty cross/bdy) -> NO
  detection-machinery bias against sigma>0.
- Yet **ZERO sigma>0 positive-debt DEFICIENT caps**; all 36000 positive-debt deficient caps are sigma=0.
=> STRONG (non-bias) empirical signal: positive-debt deficient cage => sigma=0 (door-balanced). IF this is a
STRUCTURAL fact (not just "deficient" being sigma=0-by-definition), the minimal positive-debt cage is automatically
sigma=0 and **PositiveSlackHallPrefix (the sigma>0 Hall condition) is UNNEEDED -- the hardest residual would be
BYPASSED.** OPEN QUESTIONS for GPT-Pro: (a) does the "deficient terminal cage" definition already force sigma=0
(making this definitional), or is it a real structural theorem "positive-debt deficient => sigma=0"? (b) B4 needs
absorption for positive-debt TERMINAL cages before they are known deficient -- does the sigma=0-forcing apply at that
scope? Testing universality on glue C7 (background). Framed as a QUESTION/signal, NOT a proof (battery != proof, 1 family).

================================================================================
## R-D + R-A FULL PROOF CONTRACTS (GPT-Pro, 2026-07-07, relayed) -- exact bank caps + Ferrers greedy + pruning
================================================================================
### R-D PositiveSlackHallPrefix -- exact per-prefix bank capacities (surplus units):
- C5Cap(i) = 25 * sum_{z in N_C5(P_i)} mass_C(z).
- DoorSlackCap(i) = 25 * sigma_i, sigma_i = delta_B(P_i) - delta_M(P_i) (prefix-local unmatched B-door mass).
- AmbientCap(i) = sum_{h in N_Amb(P_i)} (N-|V_h|) * tau_C(h).
- PruneCap(i) = sum_{D in N_Prune(P_i)} Balance(D)  [WELL-FOUNDED: descendant of smaller cage rank].
- PrefixDeficit(i) = Demand(i) - C5Cap(i) - AmbientCap(i) - PruneCap(i).
THE prefix theorem: for every sigma(C)>0 cage & Ferrers prefix, PrefixDeficit(i) <= 25*sigma_i, i.e.
Demand(i) <= C5Cap(i)+AmbientCap(i)+PruneCap(i)+DoorSlackCap(i).
GREEDY FERRERS FILLING proof: scan atoms a_0..a_{p-1}; fill each atom's demand from earliest available neighbor
tokens in Ferrers order; if it first fails at a_i then N(P_{i+1}) capacity exhausted while Demand(P_{i+1}) exceeds
it -- contradicts prefix-Hall. => charge matrix q exists => (Claude's surplus_le_bankCap => balance_nonneg) Balance>=0.
DECISIVE gate obstruction: sigma(C)>0 & Surplus(C)>BankCap(C), OR a prefix i with Demand(i)>NeighborCap(i) even if total passes.

### R-A SideDoorPruningPreservesPositiveDebt -- debt-additivity route:
1. SideDoorCreatesPositiveSlackSubcage: extra side door d => exists proper subcage D_d with sigma(D_d)>0
   (clean case delta_B(D_d)={d,adjacentDoor}, delta_M(D_d)={one matched}, sigma=1). LOCAL CAP/Ferrers geometry.
2. PositiveSlackAbsorption(D_d): sigma(D_d)>0 => Balance(D_d)>=0.
3. Balance-additivity identity: Balance(C) = Balance(C') + Balance(D_d) + PruneRemainder, PruneRemainder>=0
   (C'=prune(C,D_d)). => Balance(C')=Balance(C)-Balance(D_d)-PruneRemainder <= Balance(C) < 0 => Debt(C')>0
   => proper positive-debt descendant => CONTRADICTS minimality. NO Gamma-min, NO switch.
Lean sigs: PositiveSlackHallPrefix, PositiveSlackAbsorption_Hall, SideDoorCreatesPositiveSlackSubcage,
Balance_prune_sideDoor (the additivity identity), PruneRemainder_nonneg, NoSideDoor_in_minPositiveDebt.

### GPT-Pro RECOMMENDED ORDER: R-D first (DERISK -- a single sigma>0 cage with a failed prefix ineq refutes the
whole absorption route); then R-A pruning (mostly algebra given the additivity identity). gap#1 = PositiveSlackHallPrefix
ALONE iff ReserveLedgerComplete already has the additivity identity + side-door subcage construction; else + SideDoorCreatesAbsorbablePrunableSubcage.

### CLAUDE LEAN (RouteBAssembly.lean, now 6 thms GREEN + axiom-clean): added pruned_balance_neg_of_neg (R-A pruning
algebraic heart: balC=balC'+balD+pruneRem, balD>=0, pruneRem>=0, balC<0 => balC'<0; pure linarith, non-circular).
So the ALGEBRAIC cores of BOTH residuals' assembly + B4 extraction + charge-cert soundness + beta-landing are compiled.
REMAINING (unformalized): the GEOMETRIC/EXISTENCE residuals -- PositiveSlackHallPrefix existence, SideDoorCreatesPositiveSlackSubcage,
the Balance-additivity identity itself, the concrete graph-geodesic ell/switch/cage layer.

### CLAUDE PROBE RECALIBRATION: my "positive-debt deficient => sigma=0" finding (71M sigma>0 sets, 0 deficient) is
battery-SUPPORT for PositiveSlackAbsorption's CONCLUSION (sigma>0 leaf deficient caps don't occur), NOT a proven
bypass -- because the sigma>0 objects R-D/R-A actually handle are the SIDE-DOOR SUBCAGES (sigma(D_d)>0), not leaf
deficient caps. Bypass holds only if "positive-debt deficient => sigma=0" has a DIRECT proof simpler than the Hall
condition (open question for GPT-Pro; may be equivalent-hardness).

================================================================================
## R-D GATE + FINAL RESIDUAL STRUCTURE (GPT-Pro, 2026-07-07, 11669 char)
================================================================================
### CONFIRMED (a) sigma>0 cages = side-door/composite/prunable SUBCAGES, NOT leaf deficient caps => my probe
(positive-debt deficient leaf caps sigma=0 across C5+C7, 632M sets) is CONSISTENT+EXPECTED (support, not bypass).
### CONFIRMED (b) NO bypass: "positive-debt terminal cage => sigma=0" IS EXACTLY PositiveSlackAbsorption + max-cutness;
"the Hall/prefix theorem is the non-circular content." No independent shortcut.

### R-D GATE STATUS -- decisive gate BLOCKED on the concrete rowDB CageBankData:
- Faithful gate must consume emitted rowDB CageBankData(C): prefixes P_i (each with vertex set U_i, sigma_i=
  delta_B(U_i)-delta_M(U_i)), surplus atoms A(C) (demand mu_C(e)*(8j+24)), bank tokens T(C) (C5Cell cap=25*mass,
  DoorSlack cap=25*sigma_i, AmbientSlack cap=(N-|V_h|)*tau, PruneReserve cap=Balance(D)), incidence CanCharge.
- GRAPH-ONLY door-only sufficient test (I CAN compute from adj/side/switch/ell): Demand_graph(i) <= 25*sigma_i
  (ignores C5/Ambient/Prune). **PASS => sufficient (absorption via door slack alone); FAIL => INCONCLUSIVE, NOT a
  refutation.** Since 8j+24 > 25 for j>=1, no one-atom/one-token cover -- mechanism is CUMULATIVE Ferrers Hall.
- So I CANNOT decisively falsify-test PositiveSlackHallPrefix without the rowDB CageBankData emission (concrete layer).

### THE ACTUAL OPEN CONTENT (not yet proven by GPT-Pro):
- GPT-Pro's `PositiveSlackHallPrefix` Lean thm TAKES the prefix inequalities (hPrefix) as a HYPOTHESIS and proves
  Balance>=0 via greedy Ferrers filling + Claude's surplus_le_bankCap_of_hall_charge. **So the greedy-filling
  REDUCTION is provable; the OPEN residual is proving the prefix inequalities THEMSELVES hold for every sigma>0
  cage** (the cumulative Ferrers Hall content, dependent on the concrete C5Cap/AmbientCap/PruneCap cage geometry).
- R-A: SideDoorCreatesPositiveSlackSubcage (extra side door d => proper subcage D_d with sigma(D_d)>0; the side-door
  interval has one more B-door than bad-door). The pruning algebra (Balance additivity + my pruned_balance_neg_of_neg)
  is DONE; the geometric subcage construction + sigma(D_d)>0 is the open R-A residual.

### FINAL RESIDUAL MAP: gap#1 = **PositiveSlackHallPrefix (the prefix inequalities) + SideDoorCreatesPositiveSlackSubcage**,
both GEOMETRIC/structural, both dependent on the concrete rowDB cage/token decomposition (the unbuilt concrete layer).
gap#1 = PositiveSlackHallPrefix ALONE iff SideDoorCreatesPositiveSlackSubcage is already in the CAP boundary blockers.
Everything else PROVEN/formalized (6 RouteBAssembly.lean theorems + GPT-Pro greedy-filling/pruning schemas).
=> The gap#1 "wall risk" now concentrates in these 2 Ferrers/annulus cage-geometry lemmas, which cannot be quickly
gate-de-risked (need the concrete decomposition). Reliant on GPT-Pro proving the geometry OR building the rowDB
CageBankData emission tool.

================================================================================
## FORK RESOLVED -> LIKELY DOOR-ONLY (EASY) CASE (GPT-Pro, 2026-07-07, 11109 char)
================================================================================
GPT-Pro assessment: "You are PROBABLY in the small/door-only case" (evidence: no sigma>0 positive-debt deficient
LEAF caps [my C5+C7 probe], positive-slack objects are side-door subcages, j=0 door-only matches the local picture).

### THE COLLAPSE: if SmallSideDoorSubcage holds, the full Ferrers-Hall (hardest node) is BYPASSED.
SmallSideDoorSubcage: every prunable side-door subcage D has only j=0 assigned atoms (ell=7-level) AND total j=0 mass
<= sigma(D). Then Demand(D) = 24*mass <= 24*sigma(D) <= 25*sigma(D) = DoorSlackCap(D) <= BankCap(D) => Balance(D)>=0
IMMEDIATE by door slack alone. R-D reduces to PositiveSlackAbsorption_DoorOnlyForPrunableSideCage. Extraction then
uses this ONLY for prunable side-door subcages, not every abstract sigma>0 cage.

### CRITICAL nuance: "all bad edges in D have ell=7" is STRONGER than necessary (a subcage may own only the j=0
atom of a LONG ell>=9 edge). The EXACT condition is AssignedAtoms(D) subset {j=0} AND mass <= sigma(D). My probe
"max ell<=7" is a valid SUFFICIENT check (if all edges ell<=7, all atoms j=0), but door-only can ALSO hold with long
edges if only their j=0 atom is assigned. Full-edge-surplus gate: PASS => proven; FAIL => may overcount (not a refutation).

### DECISIVE GRAPH GATE (GPT-Pro sec 6, graph-computable, avoids Ferrers order): for each inclusion-minimal side-door
candidate D (contains extra door d + adjacent door adj(d) as B-doors, sigma(D)>0, connectivity, minimal), check
Demand(D) <= 25*sigma(D). [Exact properties 1-5 truncated in reply -- RE-ASK.] Two gates: Gate A strong graph-only
(Demand_full=sum(ell^2-25) over M_D <= 25*sigma; pass=>proven, fail=>maybe overcount); Gate B exact annular-atom
(needs rowDB atom assignment).

### Lean statements: SmallSideDoorSubcage (D hSide) : Surplus D <= 25*sigma D. doorOnly_absorption (SmallSideDoorSubcage
+ doorSlack_le_bankCap) : Balance>=0. PositiveSlackAbsorption_sideDoorOnly (D hSide) : 0 <= Balance D. Extraction uses
this only for prunable side-door subcages.

### STATUS: if SmallSideDoorSubcage passes/proves => R-D collapses to door-only, gap#1 = SmallSideDoorSubcage +
SideDoorCreatesPositiveSlackSubcage (both LOCAL, gateable) + the pruning algebra (DONE). If not => full PositiveSlackHallPrefix.
CLAUDE C5 PROBE (all bad edges ell<=7, j_max=1) is strong SUFFICIENT support for the door-only case (C7 ell-dist running).
NEXT: RE-ASK exact minimal-side-door-subcage properties 1-5 + build the Demand(D)<=25*sigma(D) gate.

================================================================================
## EXACT SIDE-DOOR SUBCAGE CONSTRUCTION P1-P6 (GPT-Pro, 2026-07-08) -- the decisive door-only gate
================================================================================
For each extra B-door d in delta_B(U)\{born0,born1}, each anchor a in {born0,born1}, each orientation S in {U, W_C\U},
enumerate vertex sets D subset S:
  P1. empty != D proper subset W_C; d in delta_B(D); a in delta_B(D).
  P2. delta_B(D) = {d,a}  (exactly two B-doors = minimal side-door interval).
  P3. B[D] connected AND B[W_C\D] connected (or B[V\D], matching the pruning predicate).
  P4. sigma(D)=|delta_B(D)|-|delta_M(D)| > 0; clean case delta_M(D)={m_D} => sigma=2-1=1.
  P5. no hidden internal surplus: M_internal(D)={bad edges both endpoints in D}=empty (else include in OwnedBad).
  P6. inclusion-minimal among P1-P5 candidates for fixed (d,a,orientation).
Then OwnedBad(D)=delta_M(D) union M_internal(D); Demand(D)=sum_{e in OwnedBad}(ell_B(e)^2-25); CHECK Demand(D)<=25*sigma(D).
CLEAN: delta_B={d,a},delta_M={m_D},ell(m_D)=7 => Demand=24, sigma=1, 24<=25 door-only OK. FAIL: owned ell=9 => Demand=56>25.

### DECISIVE LEMMA: SmallSideDoorSubcage / NoLongSideDoorAnnulus (GPT-Pro: "NOT from S1/S2 alone... a real geometric
lemma; your empirical all-ell<=7 strongly supports it"): an inclusion-minimal side-door subcage cannot own a level
j>=1 atom (every owned bad edge ell<=7, total mass<=sigma(D)). Then Surplus(D)=24*mass<=24*sigma<=25*sigma =>
Balance(D)>=0 by doorOnly_balance_nonneg (GREEN). Clean path: SideDoorCreatesPositiveSlackSubcage + SmallSideDoorSubcage
+ doorOnly_balance_nonneg + pruning algebra. NO full Ferrers Hall if SmallSideDoorSubcage true.

### Lean sigs: IsSideDoorCandidate (P1-P5), IsMinimalSideDoorSubcage (P6), SmallSideDoorSubcage (Surplus<=25*sigma),
SmallSideDoorSubcage_level0 (all j=0 + mass<=sigma), PositiveSlackAbsorption_sideDoorOnly (= doorOnly_balance_nonneg
applied). mass<=sigma: clean minimal case |OwnedBad|=1<=1=sigma; rowDB-fractional sum mu<=sigma.

### CLAUDE GATE TO BUILD: enumerate minimal 2-B-door sigma>0 connected sets D, check Demand(D)<=25*sigma(D) across
census+glue. Pass=door-only CONFIRMED (SmallSideDoorSubcage battery-validated); a genuine minimal side-door D with
Demand>25*sigma = the hard case (full Hall) or obstruction. STATUS: likely small/door-only; not proven from S1/S2
unless NoLongSideDoorAnnulus named+proven. gap#1 clean path = door-only if SmallSideDoorSubcage holds.

================================================================================
## COMPLETE GAP#1 CLOSURE = 2 LOCAL CAP LEMMAS (GPT-Pro, 2026-07-08) -- A + B
================================================================================
gap#1 CLOSES modulo two LOCAL CAP lemmas (everything else proven/compiled: doorOnly_balance_nonneg, pruning algebra,
B4 extraction, switch algebra Route B, reserveResidual=N^2-Gamma, beta-landing -- 9 RouteBAssembly.lean thms green):

### A. NoLongSideDoorAnnulus (HARDER/RISKIER): every inclusion-minimal side-door subcage D (P1-P6) owns only ell<=7
bad edges (all atoms j=0). PROOF STRATEGY: assume D owns ell>=9; CAP first-split gives a split door d' strictly
between d and a, cutting D' proper subset D; 3 cases: (1) D' positive-slack side-door => contradicts minimality;
(2) D' zero-slack type-B core => the long atom belongs to it, not D; (3) split violates Ferrers/S2 => invalid embedding.
IRREDUCIBLE RESIDUAL = LongSideDoorFirstSplit. **Claude gate BATTERY-CONFIRMS A: owned ell in {5,7}, 0 fail, 17757
cases census+glue.** (Proof rests on the S1 Ferrers/S2 annulus CAP theory = prose-level, earlier flagged not-fully-rigorous.)

### B. SideDoorCreatesPositiveSlackSubcage (mostly construction): extra B-door d in delta_B(U)\{born0,born1} =>
exists inclusion-minimal P1-P6 D with sigma(D)>0. CONSTRUCTION: Ferrers door order; a = adjacent door to d; D_d =
interval between a,d endpoints; P1-P3 from Ferrers interval convexity; P4 from AdjacentSideDoorIntervalPositiveSlack
(|delta_M(D_d)|<=1: if =2 it is a nested zero-slack type-B core, not a side-door interval => in minimal-positive-debt
context becomes the active core or a proper zero-slack descendant, contra). IRREDUCIBLE RESIDUAL = AdjacentSideDoorIntervalPositiveSlack.

### COMPLETE NON-CIRCULAR CLOSURE CHAIN (GPT-Pro sec 6):
extra side door -> [B] side-door subcage D, sigma(D)>0 -> [A] Surplus(D)<=25*sigma(D) -> [doorOnly_balance_nonneg]
Balance(D)>=0 -> [pruning algebra] prune D, positive debt preserved in proper descendant -> minimality FORBIDS =>
no extra side door in minimal positive-debt cage -> CAP pair-door gate applies -> pair-door switch Gamma drop>0 ->
Gamma-minimality forbids zero-slack deficient cage -> negative reserve would create one => reserveResidual>=0 =
N^2-Gamma => Gamma<=N^2. QED (modulo A,B).

### GPT-Pro: A is the HARDER node (must rule out all long annular atoms ell>=9 in every minimal side-door interval;
"where hidden long side annuli could exist"). Census strongly supports A but it is the decisive geometric claim.
Recommended gates: Gate A (max ell over OwnedBad(D)<=7 & Demand<=25*sigma -- CLAUDE DONE, 0 fail); Gate B (every
extra side door produces >=1 P1-P6 D -- CLAUDE TO BUILD).

### STATUS: gap#1 = A (LongSideDoorFirstSplit, battery-confirmed) + B (AdjacentSideDoorIntervalPositiveSlack), both
LOCAL CAP geometry lemmas resting on the S1/S2 Ferrers theory. P(gap#1 math)~70. NEXT: build Gate B existence;
GPT-Pro make A rigorous; formalize the closure chain + A,B named hypotheses in Lean.
