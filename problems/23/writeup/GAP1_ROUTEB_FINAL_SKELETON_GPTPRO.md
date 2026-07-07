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

================================================================================
## gap#1 = MINIMAL CAP PRIMITIVE INTERFACE; A,B DERIVED; ONE key primitive (GPT-Pro, 2026-07-08)
================================================================================
GPT-Pro: formalize A,B as DERIVED theorems from a minimal CAP primitive interface, then the closure chain. The single
most important primitive = **AnnularAtom_has_firstSplit** ("if not in the S1 Ferrers archive, it is the true residual wall").

### PROOF that a long owned atom forces an interior split (GPT-Pro sec 3, L-UNIFORM, no L=5 forcing):
level-j atom x=(e,j), j>=1 => shortest B-geodesic closing e crosses j+1 nested annular layers I_0<I_1<...<I_j<D
(Ferrers nested intervals). Transition I_{j-1}->I_j is a first-split with an INTERIOR split door d' (Ferrers first-
split primitive). j>=1 => d' strictly inside D (not the outer doors a,d) => proper subinterval D'<D. Level-0 atoms
charge at the outer two-door interval; level>=1 necessarily crosses an inner annular transition = the interior first split.

### A (NoLongSideDoorAnnulus) DERIVED from: AnnularAtom_has_firstSplit + FirstSplit_classification (=> D' is PS
positive-slack side-door | ZT zero-slack type-B core | BAD S2/boundary violation) + ValidCAPFrame_no_violation +
OwnedAtom_terminality/NoHiddenSurplus. 3 cases: PS contra P6 minimality; ZT contra ownership (atom belongs to D' not
D); BAD contra ValidCAPFrame. => all owned atoms level 0 => owned ell<=7. NON-CIRCULAR (no Gamma-min/switch/reserve).
Then SmallSideDoorSubcage: Surplus(D)=24*mass<=24*sigma<=25*sigma (mass<=sigma via OwnedMass_le_sigma_of_minSideDoor:
clean minimal case |OwnedBad|<=1<=1=sigma).

### B (SideDoorCreatesPositiveSlackSubcage) DERIVED from: FerrersInterval_twoDoorBoundary + FerrersInterval_connected
(+complement) + AdjacentExtraDoorInterval_sigma_pos (the only nontrivial B primitive: adjacent extra-door interval
has |delta_M|<=1 => sigma>0; if |delta_M|=2 it is a nested zero-slack type-B core not a side-door interval).

### MINIMAL CAP PRIMITIVE INTERFACE (Lean-ready sigs, GPT-Pro sec 7) -- the NAMED HYPOTHESES to formalize:
 7.1 structure FerrersFrame {G,B,parent,doorRank,interval}; IsFerrersDoor/Interval, DoorBetween, AdjacentDoors.
 7.2 FerrersInterval_twoDoorBoundary (AdjacentDoors a d => deltaB D = pairSet a d).
 7.3 FerrersInterval_connected + FerrersInterval_complement_connected.
 7.4 **AnnularAtom_has_firstSplit** (OwnedAtom + level>=1 => exists proper D' + interior split door). = THE key primitive.
 7.5 FirstSplit_classification (=> PS | ZT | BAD) + ValidCAPFrame_no_violation (Valid => not BAD).
 7.6 OwnedAtom_terminality (proper zero-slack core D'<D owns x => not OwnedAtom D x) / NoHiddenSurplus_of_minSideDoor.
 7.7 AdjacentExtraDoorInterval_sigma_pos (= THE key B primitive).

### HONEST FINAL STATUS: gap#1 = these CAP primitives; A,B + closure chain are DERIVED (proofs given). THE RESIDUAL
= AnnularAtom_has_firstSplit (is it in the S1 Ferrers archive, or new/the wall?). Battery confirms A's CONCLUSION very
strongly (17757 cases, 0 fail, no ell>=9). NEXT: (1) CHECK the S1/S2 archive for the first-split theorem; (2) formalize
the CAP primitive interface + derive A,B + closure chain in Lean (named-hypothesis form, AnnularAtom_has_firstSplit
the key primitive); (3) if S1 doesn't prove it, AnnularAtom_has_firstSplit = the true residual wall -- surface.

================================================================================
## gap#1 = ONE SUB-THEOREM: S1S2_annularLayer_cover (GPT-Pro, 2026-07-08) -- the decisive audit
================================================================================
GPT-Pro HONEST: AnnularAtom_has_firstSplit is NOT a consequence of Ferrers order alone. It reduces to ONE sub-theorem:
  S1S2_annularLayer_cover: a STRICT annular-layer transition I_{k-1}->I_k (in a two-door Ferrers interval, owned atom
  level j>=1) has an INTERIOR first-split / cover-relation door d' strictly between the two outer doors {a,d}.
PROOF of AnnularAtom_has_firstSplit GIVEN S1S2_annularLayer_cover (GPT-Pro sec 4): x=(e,j), j>=1 => annular layers
I_0<...<I_j; first transition I_0->I_1 strict; S1 first-split gives interior door d' (NOT a: I_0 inside D; NOT d:
else x level 0) => D'=firstSplitInterval(D,d') proper subset D. QED. Then A (3-case), B (adjacent-door), closure chain.
Where tri-free/max-cut enter (sec 5): INSIDE S1/S2 -- tri-free rules out shortcut chords collapsing the transition;
max-cut enforces door/bad-door balance; S2 annulus-increment=2 => each proper transition = one +2 layer so j>=1 => >=1 strict transition.

### THE DECISIVE AUDIT QUESTION: does the archived S1 first-split/last-rejoin theta theorem assert
  "annular layer transition => interior first-split/cover-relation door"  [=> gap#1 math CLOSES]
or only
  "the four-door theta is Ferrers-ordered"  [=> S1S2_annularLayer_cover is the TRUE RESIDUAL WALL].
GPT-Pro: keep AnnularAtom_has_firstSplit as the named primitive obligation until the archive is re-audited vs this exact statement.

### FULL CAP PRIMITIVE INTERFACE (GPT-Pro sec 8, Lean-ready): FerrersFrame{G,B,parent,doorRank,interval}; ValidCAPFrame
(packages tri-free + max-cut + S1 + S2 + boundary-blockers + no-violation); IsTwoDoorFerrersInterval,
IsInclusionMinimalSideDoorSubcage, IsFirstSplitInterval, IsInteriorSplitDoor; SurplusAtom{edge,level,mass}, OwnedAtom.
PRIMITIVES: (1) AnnularAtom_has_firstSplit [=S1S2_annularLayer_cover]; (2) FirstSplit_classification (PS|ZT|BAD);
(3) ValidCAPFrame_no_violation; (4) positiveSideDoor_contradicts_minimal; (5) OwnedAtom terminality/NoHiddenSurplus;
(6) SideDoorCreatesPositiveSlackSubcage [from Ferrers_adjacentDoorInterval_exists + twoDoorBoundary + connected +
AdjacentExtraDoorInterval_sigma_pos + finite descent]. A,B + closure = DERIVED theorems.

### STATUS: gap#1 math = S1S2_annularLayer_cover (ONE geometric sub-theorem) + the CAP interface derivations. Battery
confirms the conclusion (17757, 0 fail). NEXT: (1) RE-AUDIT archived S1 first-split for the layer-cover conclusion
(K2T_INTERVAL_HALL_PROOF_TARGET / BANK0_SECTION / BRANCH_A_ASSEMBLY_AUDIT); (2) formalize the CAP interface + derive
A,B + closure in Lean (named-hyp form, S1S2_annularLayer_cover the isolated obligation). P(gap#1 math)~70.

================================================================================
## RECONCILED RESIDUAL = ApplicationGeometry (GPT-Pro + Claude S2 full-read, 2026-07-08)
================================================================================
Reconciles the WALL verdict with GPT-Pro's refinement by reading S2_FROZEN_STATEMENT.md IN FULL:
- ell(h) IS the true cut-geodesic: D_h = ell(h)-1 = dist_B(a,b) (S2 :24). "blue"="cut" (B-walk = cut walk, :12-13).
- S2-Core 1 (:32-76) PROVEN (pure walk-concat arithmetic): a NewArm saving>=2 => shorter B-walk P' of len<=ell(h)-3
  => dist_B<=ell(h)-3 CONTRADICTS D_h=ell(h)-1. This IS GPT-Pro's ShorterBlueRow_impossible, ALREADY ARCHIVED.
- S2-Core 2 (:78-108) PROVEN (trivial): triangle degeneration => REAL triangle u-x-v. This IS TriangleDegeneration_sound.
- BUT S2-Core 3 (:110-146) = ONLY A WRAPPER around Core1+Core2 + an APPLICATION-SUPPLIED disjunction (:225 "S2-Core 3
  is only a wrapper around 1 and 2 plus an application-supplied geometry disjunction"; :154-159 "take the disjunction-
  producing hypothesis FROM THE APPLICATION: ApplicationGeometry -> IntermediateDoor OR TriangleDegeneration OR
  ValidReplacementArmSavingAtLeastTwo"). So S2 does NOT prove the disjunction -- WALL verdict CONFIRMED.
=> THE TRUE RESIDUAL = **ApplicationGeometry** for a level-j>=1 owned atom of a GENERAL inclusion-minimal side-door
subcage: prove the long annular transition yields a strict-reduced-theta with a replacement arm saving>=2 (the
"annulus excess>=2" of the Cap-L5-Forcing application row, S2 :203-216, which currently proves ApplicationGeometry
only for a GIVEN nested core L>=7 with reducedness + no-intermediate-door; general minimal side-door subcage + the
boundary-attach leg are open). GIVEN ApplicationGeometry: S2-Core 1 kills ValidReplacementArm (=>ShorterBlueRow=>dist
contradiction), tri-free kills Triangle => IntermediateDoor FORCED => AnnularAtom_has_firstSplit => NoLongSideDoorAnnulus.

### CLAUDE LEAN (RouteBCAP.lean, 3 thms GREEN + axiom-clean): noLongSideDoor_of_primitives (no axioms, the 3-case A
derivation), **intermediateDoor_forced_of_S2disjunction** (NEW: given the S2 disjunction hS2 + tri-free + dist-min,
door FORCED via omega/rcases -- machine-checks the S2 CLOSING step, isolating ApplicationGeometry=hS2 as the residual),
surplus_le_25sigma_of_level0. So the whole S2-disjunct-forcing DERIVATION is compiled; the single open obligation is
ApplicationGeometry (the local geometric forcing: level>=1 atom => saving>=2 replacement arm), battery-only (17757, 0 fail).

### GPT-Pro RECOMMENDS: formalize AnnularAtom_has_firstSplit / S2_forces_intermediateDoor_of_owned_long_atom as THE
named hypothesis (not pair-door metric-stability); do NOT spend budget on the L5_FORCING boundary-attach leg (Route B
avoids L5 forcing, only needs strict drop 4L+4). P(gap#1 math) ~55-60 (residual now LOCAL + closing machinery archived,
but the geometric forcing ApplicationGeometry still open + battery-only).

================================================================================
## ⚠ DECISIVE: NoLongSideDoorAnnulus FALSE from weak hyps -- C_18 single-row escape (GPT-Pro + Claude verified 2026-07-08)
================================================================================
GPT-Pro answered the decisive question with a CONCRETE COUNTEREXAMPLE, which Claude EXACT-VERIFIED
(_claude_c18_singlerow_escape.py): AnnularAtom_has_firstSplit / NoLongSideDoorAnnulus is FALSE from
{triangle-free, max-cut, Ferrers order, inclusion-minimal side-door interval, ell>=9} ALONE.
  C_18 (even cycle, parity cut) + ONE bad edge h=(v0,v8): triangle-free; parity=max cut; ell(h)=9; D={v0} is a
  two-door (deltaB={v0v1,v0v17}) one-bad (deltaM={v0v8}) sigma=1 inclusion-minimal side-door subcage, both sides
  connected, owning the ell=9 edge with NO companion row / theta / interior door / triangle / shorter blue row.
  Demand(D)=81-25=56 > 25=25*sigma => DOOR-ONLY ABSORPTION FAILS. (beta=1<=12.96 => CONJECTURE still holds; C_18 is
  NOT a tight/deficient cage -- this refutes the LEMMA, not the theorem.)
CONSEQUENCE: Claude's _claude_sidedoor_dooronly_gate.py "0 fail / no ell>=9 in 17757 cases" was a SEARCH-SPACE
ARTIFACT (census N<=9 + specific glue cannot host an ell>=9 single-row escape, needs N>=18). The battery does NOT
support NoLongSideDoorAnnulus. This corrects the session's reliance on it.

### THE RESIDUAL is now LongOwnedAtom_has_companionTheta (GPT-Pro sec 4-5): exists a companion atom y != x, owned/
adjacent, with FormsStrictReducedTerminalTheta(x,y) => S2ApplicationGeometry => S2 disjunction => (tri-free + dist-min)
=> interior door. The C_18 escape is excluded ONLY IF the actual negative-reserve / deficient-cage / rowDB-ownership
extraction FORBIDS single-row long annuli (a TIGHT-BANK argument, NOT battery). "If that stronger condition exists in
the rowDB decomposition, make it explicit in ValidCAPFrame or the hypothesis." This is genuinely OPEN and NOT battery-
supported. GPT-Pro: name S2/application-geometry as the Lean hypothesis (not pair-door metric-stability); do NOT close
L5_FORCING (Route B needs only strict drop 4L+4).

### RECALIBRATE: P(gap#1 math) ~55-60 -> ~45-50. The door-only path (the "easy" branch) is BROKEN by a verified escape;
the real residual (companion-theta) needs the deficient-cage/tight-bank structure to exclude single-row annuli and is
NOT battery-supported. NOT a conjecture falsifier (C_18: beta=1<=N^2/25). P(full Lean) ~12-20.

================================================================================
## RESOLUTION: residual = PositiveSlackAbsorption_FullBank (the ORIGINAL hard node) (GPT-Pro, 2026-07-08)
================================================================================
The C_18 escape resolves the fork to (B): the residual is NOT companion-theta (false under weak hyps) and NOT
door-only (special case). It is the FULL-BANK absorption = the original PositiveSlackHallPrefix hard node:
  PositiveSlackAbsorption_FullBank: sigma(D)>0 => Surplus(D) <= 25*sigma(D) + C5Cap(D) + AmbientCap(D) + PruneCap(D).
  (Ferrers-prefix form: PrefixDemand(i) <= 25*PrefixSigma(i) + PrefixC5Cap(i) + PrefixAmbientCap(i) + PrefixPruneCap(i).)
DOOR-ONLY = the special case DoorSlackCap only (handles ell<=7 / j=0 atoms). My RouteBCAP door-only theorems are CORRECT
but PARTIAL -- they prove the ell<=7 subcase; the general (long) case needs the full bank.

### C_18 ACCOUNTING (GPT-Pro): N=18,m=1,ell=9,Gamma=81,Reserve=N^2-Gamma=243>0 (globally far from deficient). D={v0}:
sigma=1, Surplus=56, DoorSlackCap=25, door-only deficit=31. Balance(D)>=0 IFF C5Cap+AmbientCap+PruneCap>=31. With
AmbientCap=(18-|V_h|)*tau: V_h={v8} tau=2 => 34>=31 absorbed; |V_h|=9 needs tau>=31/9. => depends on the ACTUAL rowDB
tau/V_h; NOT graph-computable. So C_18 does NOT refute the theorem if the full bank absorbs it (and beta=1<=12.96
anyway). C18_sideDoor_balance_condition (Balance>=0 <-> C5+Ambient+Prune>=31) = a sanity check, not needed in the proof.

### GPT-Pro SALVAGE of companion-theta (add the missing bank hypothesis): NegativeBalanceLongAtom_has_companionTheta:
a sigma-positive side-door cage owning a level-j>=1 atom WITH Balance(D)<0 cannot be a single-row annulus (a single
row would have Balance>=0 via the full bank = LongSingleRowAmbientAbsorption), so it has a companion theta. Route:
sigma>0 + Balance<0 => not single-row => companion theta => application geometry => S2 disjunction => door forced.
So the extraction (which produces Balance<0 positive-debt cages) may exclude single rows IF LongSingleRowAmbientAbsorption holds.

### NET: gap#1's absorption residual = the FULL PositiveSlackHallPrefix (the hard node from the very start). The
door-only detour proved the ell<=7 special case + found the C_18 escape (shortcut fails for long atoms) + confirmed
the residual is the full-bank Hall. NOT graph-gateable (needs rowDB C5/Ambient/Prune model = deep infra). Lean:
formalize PositiveSlackAbsorption_FullBank (or the prefix Hall form) as THE named hypothesis; door-only theorems are
the proven special case. P(gap#1 math) ~45-50 (back at the hard node, no shortcut; C_18 reconciled not refuting).

================================================================================
## gap#1 TRUE WALL = PositiveSlackHallPrefix_FullBank + candidate discharging proof (GPT-Pro, 2026-07-08)
================================================================================
GPT-Pro HONEST READ: "PositiveSlackHallPrefix_FullBank is the true wall now. The pair-door switch and S2 disjunction
issues have been downgraded; the proof now lives or dies on the full ambient/C5/prune bank." NOT equivalent to the
whole conjecture (easier 3 ways: only sigma>0 cages; local/prefixwise; checkable by an exact capacitated Hall/charge
certificate). But NOT a minor lemma -- a counterexample = a sigma>0 Balance<0 cage surviving absorption (the exact
obstruction). Idea (1) FAILS: global Reserve<0 gives only sum-of-balances<0, NOT a per-cage ambient lower bound.

### THE SHARP RESIDUAL (Lean-ready):
  PositiveSlackHallPrefix_FullBank (rowDB C) (hSigma:0<sigma) : forall i, IsFerrersPrefix i ->
    PrefixDemand(i) <= 25*PrefixSigma(i) + PrefixC5Cap(i) + PrefixAmbientCap(i) + PrefixPruneCap(i).
  Atomic form AmbientShadowPrefixBound: PrefixLongDeficit(i) := PrefixDemand(i)-25*PrefixSigma(i)-PrefixC5Cap(i)-
    PrefixPruneCap(i) <= PrefixAmbientCap(i). Door-only was the special case PrefixLongDeficit(i)<=0 (C_18 breaks it).

### CANDIDATE DISCHARGING PROOF (GPT-Pro sec 3-5): fractional charge q(a,v)=rem(a)/(N-|V_a|) for v in Amb(a) (ambient
vertices OFF atom a's geodesic support V_a), 0 for v in V_a. Atom-exactness automatic (sum_v q = rem(a)). Reduces to
the PER-VERTEX AmbientShadowPrefixBound: for every ambient vertex v, sum_{a: v notin V_a} rem(a)/(N-|V_a|) <= cap_i(v)
(sum_v cap(v)=PrefixAmbientCap(i)). Hypotheses used: Ferrers nesting (laminar V_a), max-cut slack (25sigma), TRIANGLE-
FREE (prevents shortcut overlaps overcharging a vertex), rowDB ambient ownership (cap_i(v)). Reframing: "long single-
row atoms are ALLOWED, but their long annular residual is SPREAD over the ambient vertices outside their support, and
the rowDB ambient capacities are large enough" = the C_18 reconciliation.

### TO GATE (GPT-Pro sec 8): needs rowDB bank data (graph-only insufficient). For every sigma-positive cage/prefix emit
PrefixDemand, PrefixSigma, PrefixC5Cap, PrefixAmbientCap, PrefixPruneCap + check the inequality = exact Ferrers charge
certificate. rem(a),V_a (geodesic support) ARE graph-computable; cap_i(v) needs the rowDB ambient capacity model.

### STATUS: gap#1 = PositiveSlackHallPrefix_FullBank (THE true wall = GERSH crux), precisely named + Lean-ready + a
candidate discharging proof (per-vertex AmbientShadowPrefixBound). Needs the rowDB bank emitter to gate + a real proof
of the per-vertex bound. P(gap#1 math) ~45-50 (well-characterized wall with a candidate approach, not lower).
### BROWSER: old MAIN tab 1267096933 STUCK rendering; FRESH tab (recreate from URL) renders correctly -- use a fresh tab.

================================================================================
## cap(v) MODEL + graph-computable diagnostic N-T(v) (GPT-Pro, 2026-07-08)
================================================================================
cap_i(v) is NOT graph-determined: rowDB ambient-token allocation cap_i(v) = sum_{h: v notin V_h, h avail to prefix i}
tau_h (exact rational bank weights, not recoverable from adj/side/ell alone). THE RESIDUAL = AmbientShadowLoadBound /
PositiveSlackHallPrefix_FullBank: for every prefix i and vertex v, sum_{a: v notin V_a} rem(a)/(N-|V_a|) <= cap_i(v).
Gate forms: UNIFORM q(a,v)=rem(a)/(N-|V_a|); or STRONGER max-flow/LP feasibility (q>=0, sum_v q=rem(a), sum_a q<=cap(v),
q=0 if v in V_a). GRAPH-COMPUTABLE DIAGNOSTIC cap (GPT-Pro sec 2): cap_global(v) = N - T(v), T(v)=sum_e ell(e)*p_e(v)
the load; sum_v (N-T(v)) = N^2-Gamma = reserveResidual. "Use cap=N-T(v) as a STRONG DIAGNOSTIC; not the official cap_i(v)
unless a theorem shows rowDB AmbientCap dominates this vertex slack model." C_18: cap=18 on the 9 outside vertices >= 31/9
=> passes. Lean: structure AmbientToken{support,tau}; PositiveSlackHallPrefix_FullBank; AmbientShadowLoadBound. Proof
provable "only after tau_h and the ambient token ownership rules are fixed" (tri-free+Ferrers-laminar+max-cut MAY prove it
for the intended tau_h, but the theorem is not determined until tau_h defined).

### CLAUDE GATE (_claude_ambient_shadow_gate.py, cap=N-T(v), door-precharge 25 + max-flow LP): even-cycle+chord
N=18,22,26,30 (the C_18 single-row-long-annulus ESCAPE regime) 0 fail => cap=N-T(v) door+ambient ABSORBS the escapes
(C_18 reconciliation CONFIRMED, N>=18 coverage). Census N<=11: 185/192032 fail, all near-extremal ell=9-in-N=9
(Gamma=N^2, cycle fills graph, no ambient room, 1 door token insufficient) => the crude proxy limit; the extremal
boundary needs the full rowDB bank (actual 25sigma sigma>=2 + C5 + prune), NOT a refutation. Fixed my own ell off-by-one.
STATUS: escape regime empirically absorbed by the natural cap; the wall's PROOF still needs the rowDB tau_h + the
discharging argument. P(gap#1 math) ~48-52.

================================================================================
## HONEST CONSOLIDATION: wall = rowDB Hall theorem; triangle-free discharging FAILS (GPT-Pro, 2026-07-08)
================================================================================
GPT-Pro HONEST verdict (sec 4,9): AmbientShadowLoadBound / the per-vertex load_i(v)<=N-T(v) bound CANNOT be proved
from triangle-free + Ferrers-laminar + max-cut alone. "Overcharging a vertex v does not necessarily create a local
triangle/shortcut; if many long supports all avoid v, v can be in many ambient shadows without a forbidden triangle.
Triangle-free controls edges and short chords; ambient shadow charging is a GLOBAL property." The per-vertex capacity
inequality "is not a direct corollary of triangle-free. It is a rowDB bank theorem -- a Hall-prefix theorem in disguise."
=> the DISCHARGING SHORTCUT does NOT close the wall. cap=N-T(v) is "the ambient part only, too weak as the full bank."

### THE WALL, FINAL FORM = FULL-BANK HALL/MAX-FLOW CERTIFICATE. FullCap_i = DoorCap_i + AmbientCap_i + C5Cap_i +
PruneCap_i. Single flow network per prefix: atom nodes (demand) -> door sink (cap 25*sigma_i) + ambient vertex sinks
(cap_i^amb(v)=sum_{h: v notin V_h} tau_h, atom a->v iff v notin V_a) + C5/Prune sinks (PrefixC5Cap, PrefixPruneCap).
Feasibility proves full absorption. Split (GPT-Pro sec 8):
  PositiveSlackAbsorption_FullBank: AmbientResidualDemand(i) <= PrefixAmbientCap(i).
  FullSupportResidual_C5PruneBound: FullSupportResidualDemand(i) <= PrefixC5Cap(i)+PrefixPruneCap(i)  [the ell=9-fill-
    graph / N=9 Gamma=N^2 tight regime where ambient is empty]. These two cover C_18 + the N=9 extremal failures.
Proof must be EITHER (A) a checked per-cage max-flow/Hall certificate over the rowDB door/ambient/C5/prune tokens, OR
(B) a structural rowDB Hall-prefix theorem (tau_h laminar along the same chain as the supports V_a).

### CLAUDE STATUS: gap#1 = the rowDB Hall absorption theorem, FULLY CHARACTERIZED. My cap=N-T(v) ambient gate
CONFIRMS the ambient diagnostic (escape regime absorbed, Gamma-min scope, N>=18; extremal ell=9 need sigma>=3 door /
C5/prune). But the FULL proof needs the rowDB bank construction (tau_h + C5Cap + PruneCap) + a Hall/max-flow certificate
-- NOT a triangle-free discharging shortcut (that route is now closed). This is the original GERSH crux, no shortcut.
P(gap#1 math) ~45-50 (discharging shortcut eliminated; the wall is the full rowDB Hall theorem, needs deep bank construction).
