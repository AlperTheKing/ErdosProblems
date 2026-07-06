# Poly/ConeCert Checker Design (GPT-Pro compact reply, 2026-07-04, sibling 6a45e152)

N-PARAMETRIC PRINCIPLE: Var.N is an ORDINARY polynomial variable — never specialized
during checking; coefficients like (75+2N) are Poly, not Q.
Var := Nat (N=0; w i = 1+i for Fin 10; aux i = 1000+i). Poly.eval env : Q.
ConeDomain {nAtom, atom : Fin -> Poly (known-nonneg), nSlack, slack : Fin -> Poly
(cone generators), nEq, eqPoly : Fin -> Poly (equality ideal)}.
ConeSem D env : Prop {atom_nonneg, slack_nonneg, eq_zero} — the semantic assumptions
consumers must discharge (e.g. from CutState hypotheses).
ConeCert D {target : Poly; base + baseCert : PosCert (nonneg-cert for base);
slackMult j : Poly each with its own PosCert; eqMult k : Poly FREE (no sign)}.
rhs = base + Sigma slackMult_j * slack_j + Sigma eqMult_k * eqPoly_k.
check = baseCert.check AND all multCerts.check AND Poly.checkEq target rhs.
SOUNDNESS: ConeSem + check = true ==> 0 <= target[env]. (checkEq_sound gives target=rhs
pointwise; base and mults nonneg via PosCert.sound; slacks nonneg via sem; eq terms
vanish.) checkEq canonical-form contract: emitter outputs both sides pre-normalized
(sorted monomial lists) so checkEq is list equality decided by rfl/decide.
FOLLOW-UP PENDING: Bernstein simplex/cube checker nesting + risks (requested).

## FOLLOW-UP (2026-07-04): PosCert + Bernstein checkers (8.6k in-thread)
PosCert: NOT Bernstein — nonneg-coefficient after substituting declared nonneg atoms
(aux-variable representation: repr over Var.aux only, auxSubst maps aux i -> atom;
shifted w=1+x handled by putting x = w-1 in ConeDomain.atom; PosCert agnostic).
Checks: allCoeffNonneg + varsSubsetAux + checkEq target (repr o auxSubst).
BernsteinSimplex: total-degree basis on chart simplex; coefficient list as data; vanish
constraints (seed vertex) as eqPoly data per coefficient cert; nested CoeffCert per
Bernstein coefficient (w-cone conditions); sound (basis nonneg on simplex + coeffs
nonneg) + sound_original (chart substitution version).
BernsteinCube: TENSOR basis over [0,1]^dim; CubeChart {dim, var} (EQV2: mu34/36/54/56 +
rho); CubeSem {lower, upper}; same nested-coefficient structure.
NOTES: cube/simplex checkers prove CLEARED NUMERATOR positivity only — denominator
positivity = separate family lemma; split large expansions per row/chart (one theorem
each); no native_decide.
IMPLEMENTATION ORDER: Poly (eval, normalized ops, subst, checkEq_sound) -> coeff checks
+ soundness -> ConeDomain/ConeSem/PosCert -> ConeCert (+withExtraEqs) -> CoeffCert ->
BernsteinCube (test master cubes first) -> BernsteinSimplex (CERT-2 charts) -> family
wrappers (A1 cones, CERT-2, V2 cubes, SIB/2Door/Seed3 rows).

## AUTHORITATIVE FULL CHECKER TEXT (user-relayed): exact records
PosCert {target, nAux, atomOf : Fin nAux -> Fin D.nAtom, repr (aux-vars ONLY)};
auxSubst maps aux i -> D.atom(atomOf i); check = varsSubsetAux AND allCoeffNonneg AND
checkEq target (subst auxSubst repr); sound via: aux -> nonneg atoms, monomials nonneg,
coeffs nonneg. CoeffCert {vanish : VanishData, coeff, cone : ConeCert
(D.withExtraEqs vanish), target_eq} — SEED-VANISHING = EXTRA EQUALITY POLYS in the
coefficient's cone domain (NOT a Bernstein rule). Nesting: Bernstein coeff -> CoeffCert
-> ConeCert -> PosCert. BernsteinSimplex: EXPLICIT barycentric lambda_0 = 1 - Sigma z
(risk 4: LITERAL polynomial equality, never modulo Sigma lambda = 1); records
SimplexChart{dim, subst, bary}/SimplexSem/SimplexCoeff/BernsteinSimplexCert;
sound + sound_original. BernsteinCube: tensor basis prod binom(d_i, a_i) x^a (1-x)^(d-a);
CubeChart{dim, var} (EQV2 = mu34/36/54/56 + rho); CubeSem{lower, upper}; DegreeVec.
RISKS 1-7: N-coefficients are Poly never Q; repr aux-only (varsSubsetAux in checker);
vanishing as eqs; literal simplex identity; EVERY Bernstein coefficient needs nested
CoeffCert (no bare boolean nonneg for polynomial coefficients); cleared-numerator only
(denominator positivity separate); split per row/chart, no native_decide.
IMPLEMENTATION ORDER 1-8 (Poly eval/ops/checkEq -> coeff checks -> ConeDomain/PosCert ->
ConeCert+withExtraEqs -> CoeffCert -> BernsteinCube first -> BernsteinSimplex ->
family wrappers).

## SEVENCUTCONE/SEED10 DESIGN (GPT-Pro compact, 2026-07-04 — THE LAST DESIGN ITEM)
Seed10: indexed data {name, edge : Finset SeedEdge, side : Fin 10 -> Bool, cls : Fin 10
-> ZMod 5, doors, rows : List SeedRow10} + decidable well-formedness (edge_noloop,
edge_c5 class-consecutivity, door_shape V4xV0, row_valid) — decide-able from literals.
SEVEN-CUT SLACKS ARE WITNESSED, not unexplained literals: SeedCutWitness {X : Finset
(Fin 10)}; slackPoly = Sigma_{cross-side pairs across X} w_i w_j - Sigma_{same-side};
SevenCutSpec {cut : Fin 7 -> witness, slackLit : Fin 7 -> Poly, slack_eq : checkEq
slackLit (slackPoly witness) = true}; ConeDomain built from slackLit.
REALIZABILITY: Seed10Realization carries bag map + blow-up semantics EXPLICIT
(complete_between_bags / no_edges_between_nonedges), rows_lift (templates -> Row S);
**SevenCutSpec.coneSem_of_realization = THE semantic bridge**: graph + gamma-min cut
+ realization ==> ConeSem for the bag-weight env (each witnessed slack >= 0 from
maxCut_sigma_nonneg on the lifted flip set). Door shape = data validation, not cone
soundness. DESIGN PHASE FULLY CLOSED.

# ===== BANK0 LEAN CHECKER BLUEPRINT (main thread, 2026-07-04; full text extracted) =====
DESIGN RULE: two layers. Graph layer = ordinary Lean defs over explicit finite graph +
cut; certificate layer = literal data over Nat vertices replayed by verified checkers.
Checker NEVER proves max-cut/gamma-min/tri-free — those stay theorem hypotheses.

MODULES (implementation order at end):
L0 GraphData: Vtx=Nat; structure GraphData {n, edges: List (Nat x Nat) normalized u<v};
   checkGraph = all-valid + Nodup + Sorted lexOrd; adjb via normEdge lookup; Prop-level
   Adj + Adj_symm/Adj_irrefl given checkGraph=true. NOT SimpleGraph directly (literal
   certs verify by rfl/norm_num); SimpleGraph (Fin n) wrapper buildable later.
L1 CutData {side: List Bool}; sideb getD; blueb/badb; dB/dM: Finset Nat -> Nat over
   UNORDERED edges; sigma = dB - dM : Int. Max-cut hypothesis later gives sigma >= 0.
L2 Rows: Row5 {badId, verts: Vector Nat 5}; checkRow5 = verts<n, nodup, endpoints =
   bad edge, 4 consecutive blue, closing bad. BadEdgeData {u,v,rows}; |cyc| =
   rows.length. Dist4Cert {noBlueLen0..3}: no blue path length<=3 between endpoints +
   displayed length-4 row => dist=4 => l=5 (use existing Row.dist_eq machinery).
L3 RowAtoms: INTEGER arithmetic, global denominator D; AtomData {D, weight, vertex,
   badId, rowId}; weight*rowCount(badId)=D; sNum(U) = sum weights in U;
   pressureNum = 5*sNum - D*n*|U| : Int; nu0Num = D*n*|C| - 5*sNum(C).
CLOSURE-TRACE (Erdos23/Bank0/ClosureTrace.lean): inductive ClosureStep
   C1_rowInterval(rowId,a,b) | C2_rowFamily(badId,orientation,terminal,firstExit,
   rows,prefixes) | C3_blueDetour(rowEdge,path) | C4_terminalShadow(shadow,firstExit,
   cell). ClosureTrace {start,steps,final}; replayTrace = some final. Checks per step
   as specified (C2 type = tuple (badId,orientation,terminal,firstExit) decidable
   equality; C3 path avoids deleted row edge, internal outside U; C4 shared interface
   w/ T=1/T=2 protected-cell checker). checkClosed = closedness RELATIVE TO PROVIDED
   basis (rows/detours/shadows); basis COMPLETENESS = separate theorem input.
   pressureNum sign check on final.
CORRIDOR-PARTITION: Corridor {verts, atomOwners, boundaryRows, terminals};
   CorridorPartition {packet, corridors, owner}. O1 disjoint union = packet;
   O2 containment; O3 terminal metadata; O4 atom ownership (reduces to O1, load
   vertex-based); O5 nu0Num(claimed negative corridor) < 0. ADDITIVITY THEOREM:
   O1 => nu0(U) = sum nu0(C) — pure integer arithmetic.
CROSSCAP: CrossCapCert {corridor, switch, D, blueBoundary, badBoundary, rowDemands,
   blueDemands, vertexSlots, badSlots, flows: List (demandId,slotId,amount),
   residuals}. Blue-boundary demand = D*N each; row atom demand = 5D/|cyc(g)|.
   Switch legality: checker RECOMPUTES boundaries from graph+cut (never trusts);
   no connectedness needed for flip. Demand conservation + capacity (vertex slots
   <= D*N, bad slots <= D*N) => 5D s(C) + DN|dB| <= DN|C| + DN|dM| =>
   D(nu0 - N sigma) >= 0 + residual identity check. CrossCap_sound: check=true +
   nu0Num<0 + (hmax: forall S, 0 <= sigma S) -> False. NO gamma-min needed.
LENS/BH GATES: LensType RR|RB|RD|DD|TTsame|TTopposite|TR; OSC OSC0-4; LensOutcome
   CROSS(CrossCapCert) | LABEL(VoltageCert) | FORBID(ForbidCert: triangle / shorter
   blue path / bad not l5 / invalid shadow config) | OSCRES(residual reduces).
   BH2Cert/BH3Cert {lensType, osc, outcome(, headOn?)}. BH_gate_sound: disjunction.
   Shared with T=1/T=2 engine.
BANKBLOCKS: BankBlock {classes: Fin 5 -> Finset Nat, badIds}; obligations: disjoint,
   <n, bad partition, bad edges in class4--class0, e(B_i,B_{i+1}) >= m_alpha
   (GRAPH-SIDE form preferred; product follows via e <= |B_i||B_{i+1}|). Algebra:
   25 m_alpha <= |B_alpha|^2 (no radicals — use existing bank_amgm route);
   disjoint blocks: sum |B|^2 <= (sum |B|)^2 <= N^2.
ASSEMBLY (Erdos23/Bank0/Assembly.lean): inductive Bank0Cert = globalC5 | bankBlocks |
   cross | peel(PeelCert w/ smallerGraph, smallerCert, n_smaller_lt) | nch.
   GRAPH-SIDE PROPS (theorem hypotheses, NOT checker inputs): TriangleFree, IsMaxCut
   (forall c', badCount c <= badCount c'), GammaMinimal, BConnected, AllBadLengthFive,
   RowsComplete (row database lists EVERY shortest row — either proven via distance
   certificates or theorem hypothesis). CHECKER INPUTS (literal): edges, side, bad
   list, row db, traces, partitions, flows, blocks, lens outcomes.
   MINIMAL-COUNTEREXAMPLE: STRONG INDUCTION ON N (confirmed, improved):
   bank0_all : forall n, (forall n' < n, Bank0Statement n') -> Bank0Statement n;
   bank0 := Nat.strong_induction_on. Bank0Statement n := forall G c cert, G.n = n ->
   checkBank0Cert = true -> Props -> 25*badCount <= n^2. PeelCert carries the smaller
   graph + cert + n' < n; assembly applies IH. Avoids well-founded-recursion trap.
NO native_decide: checkers Bool; proofs by rfl or norm_num on already-normalized
   emitted literals.
RISKS: HIGH = C2 completeness (type tuple precision; missing rows unsound), corridor
   additivity (vertex-disjoint or explicit fractional), CrossCap flow size (sparse
   lists), peel soundness (ONLY blue-pendant; multi-attached needs exchange proof),
   RowsComplete dependency. MEDIUM = Finset normalization (sorted dup-free lists),
   integer scaling via D, boundary recomputation by checker, BH labels structural.
   LOW = bank-block algebra, template cuts, mass identity.
IMPLEMENTATION ORDER: GraphData/CutData/boundaries -> Rows/RowAtoms/pressure ->
   BankBlocks -> CorridorPartition -> CrossCap -> ClosureTrace -> LensGates ->
   Assembly.


# ===== O5: T=1 REC FORMAL ARTIFACT SPEC (main thread, 2026-07-04) =====
PURPOSE: T1HallCert(H,t) => D_t(U) <= |U| for all U in H minus t => NCH-def T=1 input
s_H(t) = D_t(H minus t) <= |H| - 1. Non-circular: row data + switch calculus + REC
capacity + optional C5-label propagation only.
ARTIFACT INVENTORY (per instance):
 - T1Instance {G: GraphData, cut: CutData, H: Finset Nat, root t, badEdges, rows,
   atoms, D} — checker: t in H, H in V(G), rows/atoms inside H or declared terminal.
 - TerminalAssign {atomId, badNeighbor}: atom row contains t as ENDPOINT, bad edge
   (t,a), a in H minus t. Terminal counting: grouped terminalWeightByNeighbor
   (integer numerators), checker verifies terminalWeight(a) <= D per neighbor.
 - RECCert per nonterminal root blue edge e = tu: packets: List RECPacketCert.
 - RECPacketCert {U, switch: SwitchCert, kappaNum (= D*kappa_e(U)), alpha, beta,
   residual: ConeCert}: cleared identity L(D - kappaNum) = A sigma(S_e) +
   B nuK(S_e) + R_e, A,B >= 0, R_e >= 0 (L clears rationals).
 - SwitchCert {S, completion: ClosureTrace, blueBoundary, badBoundary, sigmaVal,
   oldBad, newBlue, oldLenSq, newLenSq, nuVal, KVal, nuKVal}: checker RECOMPUTES
   boundaries + sigma; K = sum l(g)^2 over dM(S) (= 25|dM| in all-l5); new-length
   witnesses lambda(e) >= 5; nu = newLenSq - oldLenSq; nuK = nu + K sigma.
   Soundness: sigma >= 0 (max-cut), nuK >= 0 (Gamma-minimality).
 - Residual ConeCert slack basis: sigma(S_e), nuK(S_e), terminal-closure,
   noncrossing, true-twin, anchor-exclusion, protected-cell residuals, row-atom
   nonneg. Integer arithmetic for finite instances.
 - LabelTrace {label: List (Nat x Fin 5), edgeChecks, rowChecks}: blue/bad edges
   to adjacent labels, rows propagate, overlaps agree; used ONLY in the equality
   escape — global label on assumed-non-C5-hom H = contradiction; proper-subclosure
   label routes to pruning/corridor.
N-PARAMETRIC VS FINITE: soundness theorem fully generic over GraphData (Lean);
artifacts per-instance literal data (no graph search in Lean); optional parametric
quotient form via x_i = w_i - 1 >= 0 ConeCerts for weighted families.
CHECKER OBLIGATIONS IN ORDER: C0 graph/cut/row-database sanity; C1 row
classification (terminal vs unique-root-edge) => D_t(U) = D_t^term(U) +
sum_e kappa_e(U) (3.1); C2 terminal counting <= D per neighbor; C3 packet coverage
(explicit closed-subset list OR zeta-compressed table w/ recurrence check);
C4 switch legality (trace replay, t excluded, boundaries recomputed, sigma/nu/K/nuK
recomputed, length witnesses); C5 REC integer identity + A,B,R >= 0 =>
kappa_e(U) <= 1; C6 counting consistency D_t(U) <= #(bad nbrs in U) + #(blue nbrs
in U) <= |U| (graph simplicity: one edge per vertex pair to t); C7 label escape
(only place C5-labels appear).
ASSEMBLY LEMMA (T1HallCert.sound): check = true + (forall S, sigma(S) >= 0) +
(forall S, nuK(S) >= 0) + tri-free + all-l5 row-db soundness (+ non-C5-hom if label
branch used) => D_t(U) <= |U| forall U => s_H(t) <= |H| - 1.
MICRO-EXAMPLE (EMISSION TEMPLATE — I VERIFIED EVERY FIELD EXACTLY BY HAND):
 C5 graph 0-1-4-2-3-0: edges (2,3),(3,0),(0,1),(1,4),(2,4); sides 0:0,1:1,2:0,3:1,
 4:0; blue 23,30,01,14; bad 24; single row P = (2,3,0,1,4); |cyc| = 1, D = 1;
 root t = 0; U = {1,2,3,4}; root edge e = (0,1); kappaNum = 1.
 Switch S = {1,4}: dB = {01}, dM = {24}, sigma = 0; K = 25; flip makes 01 bad with
 length-5 witness 0-3-2-4-1-0 => newLenSq = 25, nu = 0, nuK = 0.
 REC: 1 - kappa = 0 = 0*sigma + 0*nuK + 0. Fields: alpha = beta = residual = 0.
 Label trace: phi = (0,1,4,2,3) -> (0,1,2,3,4): all five edges adjacent-label. OK.
FINAL CODEX CHECKLIST: header, terminal assignments, root-edge list, per-edge
(packets/zeta, kappaNum, switch, sigma/nu/K/nuK, REC ConeCert), counting
consistency cert, optional label trace, optional shadow-descent chain.


# ===== O16/O18: PASSIVE-AM MASTER-CUBE EMISSION SPEC (main thread, 2026-07-04) =====
TARGET per seed (EQ/SIB), layer l in {V1,V2,V3}, row instance R:
  AM-defect  t + I_seed(Q*) - I_ext^l(R) >= 0   (N_ext = N_seed + t; passive = no new bad door).
LAYERS: passive = positive-flow attachment in ONE interior class, blue edges to adjacent classes
only, no new bad door, nonempty left+right neighbor sets. V0/V4 attachments are bad-door
attachments -> saturation, NOT passive. Exactly 3 master layers per seed.
CUBE VARS: per layer, prev class L_l = {a1,a2}, next R_l = {b1,b2}; pair vars mu_{ab} in [0,1]^4;
valid 9 passive signatures = 0/1 rank-one rectangles (mu_ab = 1_{a in L} 1_{b in R}, L,R nonempty).
Master cert proves the inequality on the WHOLE cube (or row-existence face).
COMPACTIFICATION: rho = t/(1+t), t = rho/(1-rho), Bernstein in rho deg <= 4 (t=1 only is
insufficient — established).
ROW-LOAD GENERATOR: extended denominator D_g^l = sum_seed-rows prod w + sum_attach-rows
eps(P) t prod w (eps(P) = mu_lr existence monomial); loads s_v = W_a W_b N/D form; endpoints
s_a = W_b etc. ROW-EXISTENCE FACE: for attachment rows, certify on face mu_lr = 1 (avoids
mu-degree 4); at signatures where the row is absent no certificate is required.
CLEARED DEFECT: Theta_l,R = t + I_seed(Q*) - I_R^l; D_l = prod D_g^0 * prod D_g^l > 0
(D_g^l >= D_g^0 > 0); P_l,R = D_l Theta_l,R; Phat = (1-rho)^4 P(w, rho/(1-rho), mu).
DEGREES: mu <= 3 (three affine-in-mu denominators; faces avoid the eps factor); rho <= 4;
x-degree emitter-computed, safe caps EQ <= 15, SIB <= 16 (use actual when smaller).
CERT FORM (M): Phat = P0 + sum_j F_j P_j + E* P* — F_j = seed seven-cut inequalities; E* =
denominator-cleared active overfull seed term (overfull branch only); P0/P_j/P* nonnegative in
checker basis = shifted-coeff in x + tensor-Bernstein in mu (deg <= 3) + Bernstein in rho (<= 4).
CHECKER OBJECT PassiveAMCubeCert {seedName, layer, rowId, rowKind SeedRow|AttachmentRow(pair),
fixedMu, degreeMu = 3, degreeRho = 4, targetPoly, slacks, multipliers, identityProof (checkEq),
nonnegProofs}. Checker: row valid; D_l > 0; compactification applied; identity by normalized
checkEq; multipliers nonneg per basis; slacks nonneg under seed cone. Soundness: Phat >= 0 =>
AM-defect >= 0.
EQ DATA: classes V0={1,7} V1={3,5} V2={0,8} V3={4,6} V4={2,9}; doors M={19,27,79}; Q* =
(7,5,8,6,9). Layers: V1 mu {10,18,70,78}; V2 mu {34,36,54,56} (universal vertex = tau0 true-twin
of bag 8); V3 mu {02,09,82,89}. ELEVEN ROW TEMPLATES R0-R10 (fixed indexing):
(1,5,0,6,9),(1,5,8,4,9),(1,5,8,6,9),(7,5,0,6,2),(7,5,8,6,2),(7,3,8,6,2),(7,5,0,6,9),
(7,5,8,4,9),(7,5,8,6,9)=Q*,(7,3,8,4,9),(7,3,8,6,9).
SIB DATA: classes V0={1,2} V1={5,6} V2={0,8} V3={3,4} V4={7,9}; doors M={17,19,29}; Q* =
(1,6,8,4,9). Layers: V1 mu {10,18,20,28}; V2 mu {53,54,63,64} (universal = true twin of 8);
V3 mu {07,09,87,89} — EXPECTED HARDEST (D_17/D_19 split on asymmetric 7/9 attachment).
THIRTEEN ROW TEMPLATES R0-R12: (1,5,8,3,7),(1,5,8,4,7),(1,6,8,3,7),(1,6,8,4,7),(1,6,0,4,7),
(1,5,8,3,9),(1,5,8,4,9),(1,6,8,3,9),(1,6,8,4,9)=Q*,(1,6,0,4,9),(2,6,8,3,9),(2,6,8,4,9),
(2,6,0,4,9).
FALLBACK: (14.1) per-signature specialization: 9 rank-one mu in {0,1} values; 1-D rho-Bernstein
+ shifted-x certs, no mu basis; (14.2) row filtering by mu_lr = 1; (14.3) rho interval split
[0,1/2] u [1/2,1] affine-rescaled Bernstein.
STATUS: VERIFIED — EQ tau0 V2-twin calibration (L={3,5},R={4,6}, twin of bag 8); all 11 EQ row
identities verified with zero multipliers; formulation (3 layers, pair vars, rho map,
vertex-only shortcut refuted). PENDING — EQ 3x11 + generated attachment charts; SIB 3x13 +
attachment charts; SIB V2 twin easiest, SIB V3 one-path hardest.
IMPLEMENTATION ORDER: EQ V2 first (tau0 calibration), then EQ V1, EQ V3, then SIB V2/V1/V3.


# ===== ASSEMBLY THEOREM REVIEW VERDICTS (main thread, 2026-07-04) =====
DECISION A: RowsComplete as Prop hypothesis for the first sorry-free pass. Bundle
RowDBFacts (G c rows) : Prop {rowsSound, rowsComplete, allBadLengthFive, atomDBSound}.
Bank0Statement n := forall G c rows cert, G.n = n -> checkGraph -> checkCut ->
checkBank0Cert -> TriangleFree -> IsMaxCut -> GammaMinimal -> BConnected ->
RowDBFacts -> 25 * badCount <= n^2; bank0_all (strong-induction step) closed by
Nat.strong_induction_on. UPGRADE PATH: rowDBFacts_of_check (checkRowDB = true ->
RowDBFacts) as drop-in; Dist4Cert {witnessRows, noLen1/2/3 certs} lives inside the
row-db checker (checkDist4 -> blueDist = 4), NOT in the first statement. Cost low
iff all modules depend only on RowDBFacts.
DECISION B: IsMaxCut G c := checkCut && forall c' valid, badCount c <= badCount c'
(over ALL side lists, NO connectedness) — CONFIRMED. CORRECTION: GammaMinimal must
be the CONNECTED version: forall c' valid, badCount c' = badCount c -> BConnected c'
-> gammaOf c <= gammaOf c' (all-max-cuts version is STRONGER than the graph setup
guarantees). Consequence: any SwitchCert invoking gamma-minimality on a flip must
prove BConnected (flipCut c S) (completed-switch validity theorem supplies this).
FLIP-COUNTING LEMMA (standalone, Int): badCount(flipCut c S) - badCount(c) =
dB(c,S) - dM(c,S). Proof: partition edges into internal-S / internal-complement /
crossing-blue / crossing-bad; non-crossing edges keep status (both endpoints flip
together or neither); crossing blue <-> bad swap. Lean route: pointwise
isBad_flip_iff (if crosses then IsBlue else IsBad) + INDICATOR SUMS
(badCount = sum over edges of if-indicator) — easier than card_filter chains.
Then sigma_nonneg_of_maxcut: flipCut valid + IsMaxCut.2 applied to flip + the
counting identity => 0 <= dB - dM.
DECISION C: THREE ASSEMBLY LAYERS with provider theorems hiding cert internals:
 (1) BranchAInputs (G c rows Q) : Prop {hLen : Q.length = 5; bank0 : 25m <= N^2;
     a1Proper : forall nonempty proper A, XMask <= (25/N + 2/3) eta;
     odlFull : rowSum <= N + eta}. c5RS_of_branchA_inputs: cases P = positiveMask:
     P = empty -> bank0 gives 0 <= eta; P proper nonempty -> a1Proper + bank0 lift;
     P = univ -> odlFull. Then gersh_L5_of_branchA_inputs via netDW_assembly.
 (2) BranchBInputs {hLen : 5 < L; bankL : 2 rho_L <= eta; bankedUPO : rowSum <=
     N + eta/2 - rho_L}. gersh_Lgt5: eta >= 0 from bankL + rho >= 0 (nlinarith),
     then nlinarith. NOTE: bankL hypothesis REQUIRED (never bankedUPO -> gersh
     bare); align existing bankedUPO_implies_gersh with 2 rho_L <= eta form.
 (3) Delta0Inputs {branchA : forall Q in rows, len = 5 -> BranchAInputs;
     branchB : forall Q, 5 < len -> BranchBInputs}; row_length_ge_five from
     TriangleFree + RowSound; all_rows_gersh by cases on length; then
     delta0_from_gersh (hGersh + GershImpliesDelta0 reduction) =>
     erdos23_delta0 : beta <= N^2/25.
 PROVIDER THEOREMS (later): branchA_inputs_of_certs, branchB_inputs_of_certs,
 odl_full_from_odl_tree, bank0_from_cert — final assembly stays stable while
 Codex emits/repairs certificates. eta := (N^2 - 25 badCount)/25 : Q;
 rho L := (L^2 - 25)/50 : Q; RowGershBound := rowSum <= N + eta.


# ===== O6: T=2 CORRIDOR CERTIFICATE EMISSION FORMAT (main thread, 2026-07-04) =====
PURPOSE: T2HallCert(H, t1, t2) => D_T(U) <= |U| forall U in H minus T =>
s_H(Q cap T) <= |H| - 2 (NCH-def |T| = 2 input). SAME primitive lens/corridor
engine as Bank0 CrossCap; geometry checker shared; certified FUNCTIONAL differs.
DATA: T2Instance {G, cut, H, t1, t2, badEdges, rows, atoms, D}. Demand: a_T(P) =
|V(P) cap {t1,t2}| in {0,1,2}; D_T(U) = sum_g (1/|cyc|) #{P : V(P) minus T in U}
a_T(P); cleared D_T#(U) = D * D_T(U); HallSlack_T(U) = D|U| - D_T#(U) >= 0.
TOP-LEVEL: T2HallCert {instance, closedPackets: List T2PacketCert, coverage}.
Coverage modes: explicit closed-packet list (small instances) OR zeta-compressed
tables (D_T#, |U|, HallSlack per subset/closure class; recurrence checked) —
preferred for model families.
PACKET: T2PacketCert {U, corridors: CorridorPartition, certs}. Owned-core
partition (SAME infra as Bank0 B2, functional swapped to HallSlack):
D_T#(U) = sum_C D_T#(C), D|U| = sum_C D|C| => HallSlack additive => per-corridor
suffices.
CORRIDOR CERTS (inductive): NONNEG {corridor, demandNum, slackNum, residual:
ConeCert} — direct slack identity D|C| - D_T#(C) = R >= 0 (ConeCert form).
CROSS {corridor, lens: PrimitiveLensCert, switch: SwitchCert, A, B, residual} —
L(D|C| - D_T#(C)) = A sigma(S) + B nuK(S) + R, A,B >= 0 ints (L clears);
sigma >= 0 max-cut, nuK >= 0 Gamma-min => slack >= 0. DIFFERENCE FROM BANK0
CROSSCAP: same PrimitiveLensCert/SwitchCert/ClosureTrace/OSC modules; T2
functional = D|C| - D_T#(C) vs Bank0 functional = D(nu0(C) - N sigma(S)) — a
functional plug-in on one engine. LABEL {corridor, labels, edgeChecks, rowChecks,
terminalChecks} — coherent C5-voltage; global label on non-C5-hom support =
contradiction; proper labelled corridor returns to pruning/next decomposition.
OSC {corridor, lens, oscType, residual, next: Option T2CorridorCert} — forbidden /
direct residual / reduce / LABEL; only OSC1 + OSC4-head-on genuine residuals.
PrimitiveLensCert {lensType RR|RB|RD|DD|TTsame|TTopposite|TR, oscType, rows,
terminals, splitData, completionTrace} — SHARED module.
CHECKER ORDER: C0 sanity (shared) | C1 terminal setup (T2) | C2 packet coverage
(shared w/ T1/closure infra) | C3 corridor partition additivity (shared B2,
functional-specific demand) | C4 corridor certs (shared geometry B3/B4) |
C5 switch legality (shared CrossCap) | C6 nonneg from hypotheses (shared) |
C7 packet Hall by summation (T2) | C8 universal conclusion via coverage (T2).
ASSEMBLY (T2HallCert.sound): check = true + (forall S sigma >= 0) + (forall S
nuK >= 0) + row db sound/complete (+ non-C5-hom if global LABEL) =>
D_{t1,t2}(U) <= |U| forall U => s_H(Q cap T) <= |H| - 2.
|T| >= 3 REDUCTION: NO automatic averaging from pairwise T=2. TManySplitCert =
closed-packet cover + corridor partition + per-corridor OWNED TERMINAL subset
T_C <= 2 + row-atom ownership D_T#(U) = sum_C D_{T_C}#(C) + capacity ownership
=> apply T=1 / T=2 / zero certificate per corridor. If no such split exists, the
unresolved packet IS a higher-terminal obstruction (*) -> hunt or new seed
branch. Status CERT-PENDING/HUNT.
MICRO-EXAMPLE (I VERIFIED EVERY FIELD EXACTLY): C5 path 0-1-2-3-4, bad 04, sides
0:0 1:1 2:0 3:1 4:0; row P = (0,1,2,3,4), |cyc| = 1, D = 1; T = {0,4};
U = {1,2,3}: a_T(P) = 2, interior = U => D_T#(U) = 2, capacity 3, slack 1;
one corridor = U, NONNEG cert (demandNum 2, slackNum 1, ConeCert 1 = 1, no
switch); coverage: 8 subsets, only full interior nontrivial; LABEL trace =
identity labelling (all adjacent, 04 = 4-0 door). OK.
=> WITH THIS, EVERY CERT-PENDING NODE IN BOTH LEDGERS HAS AN EMISSION-READY SPEC.


# ===== CROSS-SPEC INTERFACE CANON (12 mismatches resolved; main thread, 2026-07-04) =====
# BINDING for Codex emitters AND my Lean checkers. Full text in thread; O13 spec follows in
# same reply (extraction continuing).
 1 CompletedSwitchCert = ONE shared structure {S, completionTrace: SwitchCompletionTrace,
   blueBoundary, badBoundary, sigmaVal, oldBad, newBlue, oldLenSq, newLenSq, KVal, nuVal,
   nuKVal, flipCutValid: Bool, flipBConnected: Bool}. Used in T1 REC, T2 CROSS, Bank0
   CrossCap, BH/OSC. Checker recomputes sigma, verifies nu = newLenSq - oldLenSq,
   K = oldLenSq, nuK = nu + K sigma. CrossCap-only use may ignore nuK fields.
 2 TWO trace types: BankClosureTrace {start, steps: List BankClosureStep (C1_rowInterval |
   C2_rowFamily | C3_blueDetour | C4_terminalShadow), final} for Bank0 B1 packet closure;
   SwitchCompletionTrace {start, steps: List SwitchCompletionStep (OpSegment | OpTerminal |
   OpNoncross | OpTwin | OpFlat5), final} for every CompletedSwitchCert.
 3 C4 is a PACKET closure step (fields: shadow, firstExit, addedCell, witnessRows); any flip
   it induces is a SEPARATE CompletedSwitchCert.
 4 Numerator canon (all integer, all pre-multiplied by common D): kappaNum (T1 only;
   REC target D - kappaNum); hallDemandNum (T2; slack D|C| - hallDemandNum); sNum, nu0Num
   (Bank0; nu0Num = D N |C| - 5 sNum; CrossCap target nu0Num - D N sigma).
 5 NO rationals in large certs: scale : Nat (pos), aCoeff bCoeff : Int >= 0;
   scale*(target) = aCoeff*sigma + bCoeff*nuK + R.
 6 OSCData {kind : OSC0|1|2|3|4, headOn : Bool} — headOn meaningful only for OSC4;
   OSC4-head-on = {kind := OSC4, headOn := true}.
 7 PrimitiveLensCert = ONE shared structure {lensType RR|RB|RD|DD|TTsame|TTopposite|TR,
   osc : OSCData, rows, terminals, splitData, ownedCore, completionTrace}. Used in T2
   all-modes, Bank0 CrossCap, BH2/BH3.
 8 RESIDUALS: always the implemented ConeCert form target = base + sum mult*slack
   (checkEq identity); constant residuals go in base; slack basis = sigma/nuK/closure
   residual families; NO standalone residual field accepted by checkers.
 9 LabelTrace {labels, edgeAdjChecks, rowOrientationChecks}: BASE condition = C5-adjacency
   for ALL graph edges; row +-1 orientations and 4-0 doors are EXTRA structure.
10 nuK GATING: sigma_nonneg_of_maxcut for ANY S; nuK_nonneg_of_gamma_min REQUIRES
   completed-switch validity + flipBConnected = true (GammaMinimal is the BConnected-
   restricted form per assembly review).
11 Checkers verify row-REFERENCE soundness only; global completeness via RowDBFacts Prop
   (checkRowDB upgrade later).
12 TManySplitCert {terminals, packetCover, corridorOwners, subcerts : List (T1 + T2)} is a
   SEPARATE type; T2HallCert handles exactly two terminals.


# ===== O13: SEED3-PRIME CLASSIFIER SPECIFICATION (main thread, 2026-07-04) =====
PURPOSE: routing certificate for the ODL three-door branch. Input: pruned saturated
C5-hom overfull quotient, exactly 3 effective bad doors. Output: one of seven typed
routes. Classifier does NOT prove ODL/Bank0 — it routes.
INPUT: C5QuotientData {numBags, classOf: Nat -> Fin 5, weightVar, blueEdges,
badDoors, rowTemplates, activeRows, positiveBags, supportBags}; bags = true-twin
classes. Validity: blue edges between consecutive classes; bad doors V4-V0;
|badDoors| = 3; row templates = length-5 class-respecting paths from declared
doors; every effective door has a row template; positive-flow bags on rows (unless
NOT_SATURATED); PrunedSaturatedC5HomOverfullThreeDoor as Prop hypothesis
(overfullness verified from formulas OR hypothesis).
OUTPUT: Seed3Output = EQ(EQIsoCert) | SIB(SIBIsoCert) | NO_OVERFULL | NEG_SWITCH |
PRUNABLE | NOT_SATURATED | FOUR_DOOR; Seed3ClassifierCert {qut, output};
route type Seed3Route.
EQ WITNESS (EQIsoCert): contractMap (bag -> EQ vertex 0-9), fiberOf, weightExpr
(seed weight = sum of fiber weights), edge/row/twin proofs. Checker: totality on
support; fiber partition; class compatibility; true-twin fiber compatibility (same
class, cut side, open neighborhood mod fibers, row-incidence role); blue-edge
image + fullness mod twins (weights aggregate to seed edges); the 3 doors map
bijectively to {19,27,79}; rows map into the 11 EQ templates; template fullness;
weight identification. Concludes: qut true-twin-contracts to EQ. Route: ODL ->
EQ-ODL1 + EQ-AM; Bank0 -> EQ-CERT1.
SIB WITNESS: same shape vs SIB data (doors {17,19,29}, 13 templates). Route:
ODL -> SIB-S7 + SIB-AM; Bank0 -> SIB-CERT1.
NO_OVERFULL: per-active-row RowNoOverfullCert {rowId, denom, target = D_R(N - I_R),
coneCert}; checker: rows exactly once, D_R > 0 on domain, target correctly
generated, ConeCert identity + nonneg. Route: ODL immediate; Bank0 -> BankBlock.
NEG_SWITCH: NegSwitchCert {switch: CompletedSwitchCert, kind CutImprove |
GammaDescent, strictCert}. CutImprove: ConeCert for -sigma(S) - 1 >= 0 (integer
strictness). GammaDescent: sigma identically 0 + flipBConnected = true + ConeCert
for -nu(S) - 1 >= 0 (nu = nuK when sigma = 0). Route: contradiction (branch
impossible under max-cut / Gamma-min).
PRUNABLE: PrunableCert {H, T, rest, noCrossExceptT, loadDenom, loadNum =
D s_H(Q cap T), sizeNum = D(|H|-|T|), defectTarget = sizeNum - loadNum, coneCert}.
Checker: T = H cap rest; no edge H-minus-T to rest-minus-T; load correctly
computed; ConeCert sizeNum - loadNum >= 0. Concludes AmbientPrune applies. Route:
ODL -> reduced core; Bank0 -> reduced-core bank / BankBlock / corridor.
NOT_SATURATED: SaturationFailure = MissingDoor(door,rowWitness) | MissingBag(bag,
rowWitness); checker verifies effectiveness. Not terminal: absorb + rerun; under
saturated-input hypothesis it is contradictory.
FOUR_DOOR: FourDoorCert {fourthDoor, rowWitness}: bad V4-V0 edge distinct from the
3 declared, with valid effective row. Route: ODL -> q>=4 A1-5mask; Bank0 ->
BankBlock; contradicts the 3-door input claim => reroute before Seed3.
COMPLETENESS (Seed3Complete): relies on TrueTwinFiniteSeed3Contraction — under
C5-hom + pruned + saturated + overfull + 3 doors + all-l5 + no NEG_SWITCH +
no PRUNABLE + no NOT_SATURATED + no FOUR_DOOR, the true-twin contraction is one
of the FINITE enumerated 3-door candidates (door-graph types P4, K_{1,3},
P2 u E, 3E); survivors after saturation/pruning/switch/overfull filters = EQ and
SIB exactly; all other candidates emit one of the five other outputs. Status:
finite enumeration certificate.
CHECKER ORDER: syntax -> C5-hom class rule -> three doors -> row validity ->
overfull metadata -> output dispatch (7 branches) -> typed route.
DETERMINISM: output not mathematically unique (e.g. NO_OVERFULL and PRUNABLE can
coexist). EMISSION PRIORITY (convention, not soundness): NOT_SATURATED >
FOUR_DOOR > NEG_SWITCH > PRUNABLE > NO_OVERFULL > EQ > SIB. Checker verifies the
emitted route only. Soundness: Seed3Classifier.sound : check = true -> Seed3Route.
Consumers: ODL (toEQ/toSIB/noOverfull/contradiction/prunable/notSaturated/
fourDoor as routed) and Bank0 (per the archived routing table).
=> O13 DESIGN DONE. All 7 witness families target canon structures
(CompletedSwitchCert, ConeCert).



# ===== BANKCLOSURETRACE C1-C4 REPLAY SEMANTICS (main thread, 2026-07-04) — FULL CONTRACT =====
NAMING: BankClosureTrace (Bank0 packet closure, C1-C4) is DISTINCT from SwitchCompletionTrace
(Op1-Op5). This spec = BankClosureTrace only.
STATE: BankClosureState { U : VSet } ONLY — no deletion set / shadow log / cell ledger mutated;
every step monotone U subset U-prime; all metadata carried by the step and checked locally.
VSet = List Nat with isNormVSet = Sorted lt && Nodup && all < G.n; ops norm/unionVSet/
subsetVSet/memVSet; soundness exposes Finsets, checker stays on lists.
TRACE: BankClosureTrace { start, steps, final, pressureClaim : none | positive | nonpos |
negativeNu0 }; Bank0 positive packets use positive (nu0 < 0 <=> pressure > 0).
BASIS: BankClosureBasis { rowIntervalBasis, rowFamilyBasis, detourBasis, shadowBasis } —
closedness is RELATIVE to the provided basis; basis COMPLETENESS is an external theorem/cert.
Checker never invents basis items.
STEPS (inductive BankClosureStep):
- C1_rowInterval(rowId, a, b): row valid, a,b occur in row verts AND in U; absorb
  interval_R(a,b) = positions min..max. U' = U ∪ interval.
- C2_rowFamily(badId, orientation(fwd|rev), terminal, firstExit, rows : List RowPrefixData
  {rowId, prefixLen 1..4}): terminal-shadow TYPE = the tuple (badId,orientation,terminal,
  firstExit) — canonical "same type" definition. Checks: terminal is an endpoint of badId;
  each row belongs to badId, oriented so r0 = terminal; first-exit edge = r_{l-1} r_l =
  firstExit (normalized); ACTIVATION: some listed prefix has r0 in U and r_{l-1} in U;
  FAMILY COMPLETENESS: supplied rows EXACTLY equal the RowDB family of that type (checker
  recomputes and compares). U' = U ∪ (union of all prefixes {r0..r_{l-1}}).
- C3_blueDetour(rowId, edgePos : Fin 4, path): row edge e = (q_edgePos, q_edgePos+1) blue,
  BOTH endpoints in U; path nonempty simple normalized, endpoints = endpoints of e (either
  order), every consecutive edge blue, no edge equals deleted e; internal-outside-U optional
  (warn, never reject). U' = U ∪ path. This is the theta-witness stabilizer absorber
  (canonical example: path [6,0,5,8] for row edge 6-8).
- C4_terminalShadow(shadow, firstExit, cell, witnessRows, protected : Option
  ProtectedCellCert) + RECOMMENDED explicit field trigger : VSet (ADOPTED — avoids
  ambiguity; default trigger = terminal + inner endpoint of firstExit): shadow ⊆ cell;
  exactly one endpoint of firstExit in shadow (inner), outer outside; witnessRows valid
  (belong to bad edge, oriented from declared terminal, prefix ⊆ shadow, firstExit = first
  exit edge); ACTIVATION trigger ⊆ U; BASIS MEMBERSHIP of the full tuple in shadowBasis;
  if protected = some pc then checkProtectedCell pc = true and pc.cell ⊆ cell. U' = U ∪ cell.
  C4 does NOT spend bank (cell ledger separate); switch soundness separate
  (CompletedSwitchCert).
REPLAY: replayClosureStep : ... -> Option VSet (verify isNormVSet U, preconds, compute,
normalize, U ⊆ U'); replayTrace = steps.foldM replayClosureStep start; trace requires
replayTrace = some final.
CHECKCLOSED (relative closedness of final): C1: for every basis row, every pair a,b in
U∩row => interval ⊆ U (enumerate 10 pairs of 5 positions); C2: family activated => all
prefixes ⊆ U; C3: both edge endpoints in U => path ⊆ U; C4: trigger ⊆ U => cell ⊆ U.
PRESSURE: sNum/pressureNum exactly as CertGraph L3 (D-premultiplied); checkPressureClaim
per claim tag; negativeNu0 = positive pressure (nu0 = -pressure).
FULL CHECKER: checkBankClosureTrace = checkGraph && checkCut && norm(start) && norm(final)
&& replay = some final && checkClosed(final) && pressureClaim. (May omit graph/cut checks if
global, but soundness assumes them.)
SOUNDNESS: replayClosureStep_sound (norm ∧ ⊆ ∧ per-spec addition, by cases);
replayTrace_sound (start ⊆ final ∧ steps valid); checkClosed_sound -> BankClosedRel
{c1..c4_closed}; checkPressureClaim_sound -> PressureClaimProp; MAIN BankClosureTrace.sound:
check = true -> start ⊆ final ∧ BankClosedRel(final) ∧ PressureClaimProp(final, claim).
CONSUMER MAY USE ONLY: containment, relative closedness, pressure sign (+ step metadata by
reference). Trace does NOT prove maximality / gamma-min / all-l5 / RowDB completeness /
corridor additivity / Bank0 — separate modules.
EMISSION CONVENTIONS (Codex): sorted dup-free VSets; normalized edges; global RowDB ids;
C2 families complete vs RowDB; C4 explicit trigger; C3 paths simple+blue; D-premultiplied
integers; ProtectedCellCert emitted separately and referenced; NO dead-tail additions
(C1-C4 only); redundant steps may be omitted (closure checked at end).


# ===== B10 PEEL + BANK0 ASSEMBLY STATEMENT FILE (main thread, 2026-07-04) — FULL CONTRACT =====
CANONICAL CORRECTION: Bank0 `nch` constructor = NCHBankCert (scalar-bank-safe WRAPPER routing
to cross/forbid/label contradiction via corridor engine, bankBlocks, peel, or future non-C5-hom
seed bank). It must NOT consume ODL-only NCH-def (s_H(Q cap T) <= |H|-|T| is row-load pruning
for ODL, not a scalar-bank proof).

PEELCERT (blue-pendant peels ONLY): removes R_rem attached through ONE root t; A = R_rem u {t}.
Fields: removed(VSet), root, keepMap (sorted complement; small i <-> keepMap[i]), smallG,
smallCut, smallRows, smallCert : Bank0Cert, parity : List Bool (side(v) xor side(root)),
nSmallLt, edge/rowCheckData.
CHECKS P0-P7 (all recomputed): P0 sets/ranges/complement/smallG.n = keepMap.length < G.n;
P1 induced edges recomputed + compared to smallG.edges, smallCut = restriction;
P2 PENDANT BOUNDARY: every removed-to-kept edge lands on root (excludes multi-attached);
P3 BLUE-ONLY APPENDAGE: every edge touching removed is blue => badCount(G,c) =
badCount(G_small,c_small) (checker recomputes BOTH);
P4 BLUE-CONNECTED APPENDAGE: every removed vertex blue-connected to root inside
removed u {root} (BFS) — needed to extend B-connectedness back;
P5 PARITY: parity consistent across appendage edges — any small cut EXTENDS to G with all
appendage edges blue: Ext(c*)(v) = c*(root*) xor parity(v);
P6 ROW-INVISIBILITY: NO row in RowDB uses a removed vertex (preserves all-l5 structure);
P7 small RowDB = image of big RowDB under keepMap inverse (bijective row transfer).
PRESERVATION LEMMAS (proofs archived in-reply): P-MaxCut (extend better small cut => beat c);
P-BConnected (P4); P-Distances (blue excursions through appendage repeat root => equal blue
distances between kept vertices); P-AllLengthFive; P-GammaMinimal (Gamma equal on both sides).
PeelCert.sound: check + big Props => PeelPreservesFacts {nSmallLt, badCount_eq, triSmall,
maxSmall, gammaSmall, bconnSmall, rowsSmall}.
BANK TRANSFER: IH 25*badCount_small <= smallN^2, badCount_eq, smallN <= N =>
25*badCount(G,c) <= N^2 (Nat.le_trans + Nat.pow_le_pow_left).

BANK0STATEMENT (exact induction predicate):
Bank0Statement n := forall G c rows cert, G.n = n -> checkGraph -> checkCut ->
checkBank0Cert G c rows cert = true -> TriangleFree G -> IsMaxCut G c ->
GammaMinimalConnected G c rows -> BConnected G c -> RowDBFacts G c rows ->
25 * badCount G c <= n^2.
RowDBFacts (Prop structure): rowsSound, rowsComplete, allBadLengthFive, atomDBSound.

BANK0CERT + DISPATCH: inductive Bank0Cert = globalC5(GlobalC5Cert) |
bankBlocks(BankBlockCoverCert) | cross(Bank0CrossCert) | peel(PeelCert) | nch(NCHBankCert).
checkBank0Cert: structural recursion ON THE CERT (peel case: checkPeelCert && recursive
checkBank0Cert on smallCert) — Lean accepts as ordinary structural recursion; the THEOREM
recursion is on graph size (separate).
CONSTRUCTOR SOUNDNESS: GlobalC5Cert.sound (labelling + template cuts m <= e(Vi,Vi+1) <=
|Vi||Vi+1| + AM-GM => 25m <= N^2; needs hMax); BankBlockCoverCert.sound (disjoint blocks +
bad partition + products + per-block AM-GM + sum|B|^2 <= N^2); Bank0CrossCert.sound (corridor
partition + negative corridor + CrossCap + completed switch => N*sigma <= nu0 < 0 => sigma < 0
vs max-cut => FALSE; then False.elim); PeelConstructor.sound (PeelCert.sound => facts => IH at
smallG.n => transfer); NCHBankCert.sound (route theorem dispatching to the above, takes IH).
STRONG INDUCTION: bank0_all (n) (IH : forall n' < n, Bank0Statement n') : Bank0Statement n :=
intro/subst/cases cert (5 branches as above). bank0_statement_all : forall n, Bank0Statement n
:= Nat.strong_induction_on n bank0_all. bank0_of_cert: the consumer-facing wrapper.
PITFALLS: (6.1) checker recursion structural on cert, proof recursion on N — keep separate;
(6.2) checkPeelCert verifies STRUCTURE only — small Props (maxcut/gamma/bconn/rows) are
DERIVED from big Props via preservation lemmas, never checker-claimed; (6.3) every nu_K use
in Cross/NCH internals requires flipBConnected = true (canonical CompletedSwitchCert field);
(6.4) target in Nat, pressure/sigma in Int — transfer lemmas end in Nat, cast carefully;
(6.5) bad-count equality comes from BLUE-APPENDAGE (P3), never from edge-count equality.
FILE SHAPE: Erdos23Delta0/Bank0/Assembly.lean imports GraphData/CutData/Rows/BankBlocks/
CrossCap/ClosureTrace/Peel/GlobalC5/NCHBank; declares Bank0Statement, bank0_all,
bank0_statement_all, bank0_of_cert. This is the Bank0 scalar theorem consumed by
Branch-A C5-RS.


# ===== TOP-LEVEL ASSEMBLY CONTRACT (main thread, 2026-07-05) — LAST DESIGN ITEM, FULL =====
VERDICTS RE-AFFIRMED: RowDBFacts Prop-first (upgrade later via checkRowDB); IsMaxCut =
checkCut c ∧ forall c* (checkCut => badCount c <= badCount c*); GammaMinimalConnected =
forall c* (checkCut, badCount equal, BConnected c* => gammaOf c <= gammaOf c*); 3 layers.
SHARED Q-QUANTITIES: nQ, mQ, etaQ = (N^2 - 25m)/25, rhoQ L = (L^2-25)/50, tauQ = 5m/N;
RowGershBound Q := rowSum <= N + etaQ.
BRANCH A (L=5): BranchAInputs {hLen, hNpos, bank0 : 25m <= N^2, a1Proper : forall A nonempty
proper mask, XMask A <= (25/N + 2/3) etaQ, odlFull : rowSum <= N + etaQ}.
eta_nonneg_of_bank0 (casts + nlinarith). C5RS := sum_i max(s_i - tau, 0) <= (1 + 25/N) etaQ;
positiveMask; algebra lemmas posPart_sum_eq_XMask + fullMask_X_eq_odl_form (X(univ) form <=>
rowSum form). c5RS_of_branchA_inputs: P=empty (bank0 => eta>=0 => RHS >= 0); P=univ (odlFull
+ fullMask iff); P proper nonempty (a1Proper + 2/3 <= 1 + eta >= 0). gersh_L5_of_branchA_inputs
= c5RS + netDW_assembly (existing net-DW module). CONSUMER EDGE: Bank0 + A1proper + ODLfull
=> GERSH_L5. ODLfull provider consumes: non-overfull, NCH/G1-prime, q<3 2Door-ODL,
Seed3Classifier, EQODL1_of_cover + EQPassiveAM, SIBS7 + SIBPassiveAM, q>=4 A1-5mask.
BRANCH B (L>5): BranchBInputs {hLen 5 < L, bankL : 2 rhoQ L <= etaQ, bankedUPO : rowSum <=
N + etaQ/2 - rhoQ L}. gersh_Lgt5_of_branchB_inputs: 2rho <= eta + L>5 => eta >= 0 =>
eta/2 - rho <= eta. Provider consumes Bank-L six-case, HBD packet, CD op1-5 telescope,
fan/cactus/SH-prime cell ledger, combined peel eta/2 spend.
DELTA0: Delta0Inputs {branchA : forall Q in rowList, len=5 -> BranchAInputs; branchB : ...
5<len -> BranchBInputs}. all_rows_gersh: row soundness gives 5 <= len; by_cases len=5 /
omega. GAMMA: gamma_bound_of_all_rows_gersh (IMPORT from existing Gamma/GERSH reduction —
do NOT reprove in assembly); gamma_lower_bound : 25m <= Gamma (each bad edge length >= 5 =>
l^2 >= 25; RowsSound); beta_eq_badCount_of_isMaxCut (betaGD = min over checked cuts);
beta_bound_of_gamma: 25m <= Gamma <= N^2 => m <= N^2/25 => beta form. d_mono NOT needed
(notation only if legacy text requires).
TOP: GoodCutData {maxCut, gammaMin, bConnected, rowsFacts};
erdos23_delta0_graphData_from_good_cut (SAFE FIRST TARGET) := all_rows_gersh ->
gamma_bound -> beta_bound. exists_good_cut (∃ c rows, GoodCutData) = NONTRIVIAL imported
reduction (B-connectedness) — DO NOT HIDE in the final theorem; two-stage discipline:
certified theorem (cert bundle -> holds) THEN provider theorem (every valid graph has a
bundle) => unconditional.
SIMPLEGRAPH BRIDGE: prove over GraphData first; GraphData.ofSimpleGraph via e : V ≃ Fin card
(edges i<j with Adj through e); lemmas betaGD_ofSimpleGraph_eq_beta, n_ofSimpleGraph,
triangleFree transfer; then erdos23_delta0_simpleGraph.
PITFALLS: cast isolation via the three dedicated lemmas; beta needs IsMaxCut (single-cut
row bound does NOT bound beta); nu_K uses need flip B-connectedness INSIDE providers (top
level must not know); GoodCut existence explicit.
DECLARATION LIST (stable interface): etaQ rhoQ RowGershBound BranchAInputs
eta_nonneg_of_bank0 c5RS_of_branchA_inputs gersh_L5_of_branchA_inputs BranchBInputs
gersh_Lgt5_of_branchB_inputs Delta0Inputs all_rows_gersh gamma_lower_bound
gamma_bound_of_all_rows_gersh beta_eq_badCount_of_isMaxCut beta_bound_of_gamma GoodCutData
erdos23_delta0_graphData_from_good_cut GraphData.ofSimpleGraph betaGD_ofSimpleGraph_eq_beta
erdos23_delta0_simpleGraph.
=> PROGRAM-WIDE DESIGN PHASE CLOSED. Remaining: emissions (Codex), module typing (me),
prose assembly (sibling), exists_good_cut reduction (next main consult).


# ===== EXISTS_GOOD_CUT CONTRACT + PROOF (main thread, 2026-07-05) =====
CORRECTION 1: "every triangle-free graph has a B-connected max cut" is FALSE for disconnected
graphs (two isolated vertices: blue graph empty). Correct API: CONNECTED version +
component reduction (beta additive over components, sizes add, convexity sum Ni^2 <= N^2).
CORRECTION 2: AllBadLengthFive is NOT part of exists_good_cut — a gamma-min B-connected max
cut may have bad edges of length > 5 (Branch B exists for exactly that). At existence level
the theorem is only l(g) >= 5. RowDBFactsGeneral {rowsSound, rowsComplete, length_ge_five,
atomDBSound}; GoodCutData uses it. AllBadLengthFive = branch hypothesis for Bank0/Branch-A
only (or derived by checking each row length = 5); if some l > 5, Bank-L gives eta > 0.
CUT SPACE: use CutFn n := Fin n -> Bool (finite by construction) + CutData.ofFn; avoids
finiteness of arbitrary side lists. maxcut_exists: minimize badCount over finite nonempty
CutFn space (Finset.exists_min_image / argmin); every valid CutData corresponds to a CutFn.
No triangle-freeness needed.
BCONNECTED OF MAXCUT (connected G): blue component S proper nonempty => G connected gives a
crossing graph edge; S = union of blue components => no blue crossing edge => all crossing
edges bad, deltaB(S) = 0 < deltaM(S); flip identity => badCount(flip) < badCount —
contradicts IsMaxCut. (Uses badCount_flip_eq + sigma_nonneg_of_maxcut — ALREADY GREEN in
CertGraph.) No triangle-freeness.
GAMMA-MIN EXISTENCE: C = {valid, maxcut, BConnected} nonempty (above) + finite => minimize
gammaOf over C => GammaMinimalConnected. NOTE 13.5: state GammaMinimalConnected via
gammaOf G c from graph distances, INDEPENDENT of row database (avoid gamma from incomplete
rows) — top-level contract signature (G c, no rows) is the right one; Bank0-side mentions of
GammaMinimalConnected G c rows should be read as the same Prop + rows only for row sums.
ROWDB EXISTENCE: split off — rowDB_exists (hGraph hCut hB hTri) : exists rows,
RowDBFactsGeneral (imported from row module first pass; later computable rowsOf =
enumerate all shortest blue paths per bad edge, denominator = row count, Finset.filter over
bounded lists, NO native_decide). LENGTH >= 5 (badEdge_length_ge_five): bad uv same side =>
blue paths even length; d != 0 (u != v); d != 2 (u-x-v blue + bad uv = triangle); => d >= 4
=> l = d+1 >= 5.
FINAL API: exists_good_cut_core_connected (cut-only); rowDB_exists; exists_good_cut_connected
(hGraph hConn hTri) : exists c rows, checkCut ∧ GoodCutData. Component reduction:
graphData_bound_from_components (beta additivity + convexity). PITFALLS: n=0 handle in
component reduction only (BConnected awkward); n=1 trivial (one-vertex blue graph connected,
Gamma=0); m=0 immediate; final beta step MUST use beta_eq_badCount_of_isMaxCut (never an
arbitrary cut).
=> LAST imported reduction CONTRACTED. Nothing in the program remains design-open.


# ===== CROSS-CONTRACT CONSISTENCY AUDIT — 50 DEFECTS + RESOLUTIONS (main, 2026-07-05) =====
# BINDING for all typing. Full text in-thread; numbered summary with resolutions here.
# MY OVERRIDE (items 11-12): audit proposed Finset Nat signatures for dB/dM/sigma/sNum/
# pressureNum/nu0Num — but the GREEN CertGraph.lean uses List Nat throughout. VERIFIED CODE
# WINS: List signatures are canonical; Finset wrappers only if assembly genuinely needs them.

TYPE-CRITICAL TOP 10 (patch BEFORE typing Peel/Assembly):
 1 GammaMinimalConnected G c (row-INDEPENDENT, gammaOf from distances) — drop the rows arg
   everywhere; nu_K users add CompletedSwitchSound + flip-BConnected hypotheses.
 2 RowDBFactsAll5 extends RowDBFactsGeneral w/ allBadLengthFive — Bank0Statement uses All5;
   GoodCutData/exists_good_cut use General (l >= 5 only).
 3 BranchAInputs.bank0 REPLACED by etaNonneg : 0 <= etaQ (global eta can come from Bank0 OR
   any Branch-B bankL row: eta_nonneg_of_bank0 / eta_nonneg_of_bankL / m=0 trivial).
 4 Delta0Inputs gains global etaNonneg field; provider fills BranchAInputs.etaNonneg from it.
 5 PeelPreservesFacts must ALSO carry hGraphSmall/hCutSmall (checkGraph/checkCut on smallG)
   and rowsSmall : RowDBFactsAll5 (not General) — IH needs all of these.
 6 CompletedSwitchCert single canonical structure (S, completionTrace, boundaries, sigmaVal,
   oldBad, newBlue, oldLenSq, newLenSq, KVal, nuVal, nuKVal, flipCutValid, flipBConnected).
   NOTE: my green version lacks oldBad/newBlue and uses S : List Nat — add the two payload
   fields at next touch, keep List.
 7 BankClosureTrace (C1-C4) vs SwitchCompletionTrace (Op1-Op5) never interchangeable.
 8 Seed3Route consumers split: Seed3Route.toODL vs Seed3Route.toBank0 (NO_OVERFULL means
   I<=N in ODL but routes BankBlock in Bank0); NOT_SATURATED/FOUR_DOOR are REROUTES not
   terminal proofs — ODL provider must be stated over a saturation/route TREE (new design
   item, tasked); PRUNABLE requires ambientPrune then recursion, never direct ODL.
 9 exists_good_cut_connected + component_reduction separate; never call connected version on
   possibly-disconnected data; BConnected n=0 handled outside; existence needs no
   triangle-free (only length bound does).
10 Grouped EQ/SIB generators (UV-T,...,U_A,U_B,B0; SIB G12/G23/GV/GZ) need PROVENANCE before
   use as slacks: EQGroupedSlacks_nonneg / SIBGroupedSlacks_nonneg imported from CERT1
   machinery (Option A); EQCone vs SIBCone separate structures.

OTHER RESOLUTIONS (11-50 condensed): 13 T1/T2/Bank0 numerator field names distinct
(kappaNum/hallDemandNum/sNumCorridor/nu0NumVal); 17 DiffSkipCert replaces RadialSkipCert in
RegionCert (skip constructor takes DiffSkipCert; derivative fields removed pass 1);
18 Gsharp = H_G * Lambda^(2-d) everywhere (never s^(2-d)); 19 all O14 certs over Q (no real
deriv pass 1; density theorem later if needed); 20 sound_height1 needs EQCone hypothesis
(weights >= 1 + F_j >= 0; grouped gens derived); 22 EQODL1_of_cover calls EQCert1_eta_ge_one
internally (CERT1 supplies eta(wbar) >= 1); 23 BranchAInputs.odlFull is AMBIENT eta (pruned
providers go through ambientPrune); 24 supportRowSum + AmbientExcess defs; 25 RowInDB
abstract membership predicate (rep-independent); 26 RowCert {badId, verts, nodup} with
.length = verts.length (Row5 via subtype/coercion); 27 rho_nonneg_of_len_gt5 +
eta_nonneg_of_bankL cast lemmas; 28 delta0_inputs_of_cert_bundles(hGood, hBundles) w/ length
split from rowsFacts.length_ge_five; 29 gamma_bound_of_all_rows_gersh takes NO eta/Bank0
(anti-circularity); 30 gamma_lower_bound needs only l >= 5; 33 final beta step via
beta_eq_badCount_of_isMaxCut always; 34 SimpleGraph bridge via Fintype.equivFin; 35 carry
hGraph/hCut at top level, structures assume-or-check (never both absent); 40 RegionCert.sound
returns 0 <= Phat with empty case via False.elim internally; 41 DiffSkip RIGHT boundary cert
= BoundaryCoverCert covering the boundary IMAGE (s=1/2 point may fall in a DIFFERENT
dominance region — use global near-band cover or reclassified region cert, never a bare
same-(k,a) pointer); 42 LEFT skip carries explicit FaceCert for P(0,u) >= 0; 43 CubeChart
{freeMu, fixedMu, rhoFree} — Bernstein basis after fixedMu substitution; 44 per-cert declared
degrees (degreeX/Mu/Rho), checker verifies <= declared (no hardcoded EQ 15 / SIB 16);
47 IsMaxCut = badCount-minimal structure {valid, min_bad} (8); 49 BConnected def guards n=0;
50 gammaMinConnected_exists needs no triangle-free.


# ===== SIGMACHAIN PROVIDER: P-MAXCUT PRESERVATION (main, 2026-07-05) — LAST BANK0 LINK =====
GOAL: sigmaNonneg_small_of_peel (checkPeel + sigmaNonneg G c => sigmaNonneg smallG smallCut).
Uses ONLY checked peel facts + the green flip calculus (no triangle-free/gamma-min/B-conn).
CONSTRUCTION: idxOf? helper (+ some->lt, some->getD facts); extSide p d v = match idxOf?
keepMap v with some i => sideb d i | none => (match idxOf? removed v with some r =>
xor (sideb d rootSmallIdx) (parity.getD r false) | none => false [unreachable]);
extendCut G p d = { side := (List.range G.n).map (extSide p d) } — length exactly G.n by
construction (NEVER append manually). NOTE: my green PeelData lacks rootSmallIdx — ADD field
+ checker conjunct keepMap.getD rootSmallIdx 0 = root && rootSmallIdx < keepMap.length.
KEY LEMMA 1 badCount_extendCut_eq: badCount G (extendCut p d) = badCount smallG d. Type A
kept-kept edges: sides equal via keepMap restriction => bijective with smallG edges (induced).
Type B removed-touching edges: root-v blue iff parity(v) = true (checker P5 verified from the
ORIGINAL blue appendage); u-v both removed: side xor = parity(u) xor parity(v) — opposite
parity checked => ALL appendage edges blue under EVERY extension (this is WHY P5 exists —
original-cut blueness alone is insufficient, pitfall 7.4). => removed edges contribute 0.
LEMMA 2 extend_smallCut_eq_bigCut_on_sides: Ext(smallCut) sides = c sides (kept: restriction;
removed: c(root) xor parity(v) = c(v) since parity(v) = c(root) xor c(v)); corollary
badCount_smallCut_eq_big: badCount smallG smallCut = badCount G c.
EQUIVALENCE: BadCountMinimal G c := forall valid d, badCount c <= badCount d.
symmDiffSupport G c d = (range n).filter (sideb c != sideb d); flip_symmDiff_eq_on_sides
(Boolean cases); badCount_flip_symmDiff_eq (side extensionality of badCount);
badCount_min_of_sigmaNonneg (flip identity + hSig at S = symmDiff);
sigmaNonneg_of_badCount_min (flip valid + identity); sigmaNonneg_iff_badCount_min.
TRANSFER: small_badCount_min_of_peel (big minimality + badCount_smallCut_eq_big +
badCount_extendCut_eq squeeze); sigmaNonneg_small_of_peel (needs checkGraph/checkCut on
smallG from checkPeel — P0/P1 conjuncts); SigmaChain_of_sigmaNonneg by structural recursion
on cert (peel case: extract hPeel + hSmallCert from the && , apply transfer, recurse).
PITFALLS: 7.1 range-map side list; 7.2 getD guarded by idxOf? bounds, none-branch unreachable
via keepMap ∪ removed = range n; 7.3 removed side uses sideb d rootSmallIdx (the SMALL cut's
current root side, NOT the original); 7.4 P5 = blue-under-every-extension; 7.5 multi-attach
excluded by P2; 7.6 peel cases force n >= 2 (no degenerate handling needed).
=> BANK0 IS FULLY SELF-CONTAINED once typed: bank0Cert_sound + SigmaChain_of_sigmaNonneg +
sigma_nonneg_of_isMaxCut (green) = 25*badCount <= n^2 from IsMaxCut + checkBank0Cert alone.

## ODLFullMaskRouteComplete — keystone route design (GPT-Pro MAIN, 2026-07-07; Claude-gated)

VERDICT: ODLFullMaskRouteComplete is N-uniform + structural, but NOT a single local graph argument — it is a
FINITE route-completeness theorem parameterized by a finite list of structural coverage atoms. Structural
modulo each atom. The ONE census-colored branch is NCHRoute; the keystone is fully structural once NCHRoute
is upgraded census -> certified. So: structurally reducible to finite symbolic coverage; present proof
conditional on the remaining route atoms (especially NCHRoute).

### Total route decision procedure (branch order; absorb/prune are internal, recurse)
Route(O):
 1. row not overfull            -> NO_OVERFULL           (structural: RowDB + closure-basis completeness)
 2. O not saturated             -> ABSORB (missing door/bag witness) -> Route(absorb O)  (internal)
 3. O has a negative switch      -> NEG_SWITCH            (structural: sigma<0 contradicts max-cut; neutral
                                                          switch sigma=0,K(S)<0,flipBConn -> Gamma-min contra)
 4. O prunable                   -> PRUNE (appendage H,T + excess-link) -> Route(prune O)  (internal;
                                    ambient-prune: coreExcess(parent) <= coreExcess(child) => child ODL => parent ODL)
 5. O not C5-hom                 -> NCH                   (*** WEAKEST ATOM — currently census ***)
 6. q = # distinct effective C5 bad doors:
      q<=2 -> TWO_DOOR / q2 leaf
      q=4  -> FOUR_DOOR leaf routed to A1 five-mask / BankBlock
      q=3  -> classify three-door graph (P4/K13/P2uE/3E) via Seed3 classifier: EQ-iso->EQ, SIB-iso->SIB,
              NO_OVERFULL->NO_OVERFULL, NEG_SWITCH->... [uses Claude's compiled Seed3Door.classifyDoor]

### Lean shapes (MAIN)
  inductive ODLRouteLeaf | cone | bank | lens | noOverfull | negSwitch | eq | sib
    | seed3 (door : Seed3DoorType) | qlt2 | fourDoor | nch
  structure FullMaskODLNode (G) (c) (rows) (Q : RowCert) (O : ODLCore) : Prop where
    rowInDB : RowInDB rows Q ; len5 : Q.length = 5 ; fullMask : FullMask G c rows Q
    activeClosure : ActiveClosure G c rows Q O
    saturatedBasisSound : SaturationBasisSound G c rows O
    pruneBasisSound : PruneBasisSound G c rows O ; doorBasisSound : DoorBasisSound G c rows O
  theorem seed3_route_complete (hDoorType : Seed3.DoorTypeOf O ty) (hWidth : Seed3.WidthCertSound ...)
      (hLookup : Seed3.UniverseCertSound ...) : exists leaf, Seed3.RouteLeaf O leaf
  theorem odl_fullmask_route_complete (hTri) (hMax) (hGamma) (hRows) (hNode : FullMaskODLNode ...) :
      exists leaf, ODLRouteLeaf ...   -- via the total procedure + per-branch soundness; NCH = weak atom

### Claude gate + connection
- My compiled Seed3Door module (classifyDoor + hasType_* + k13_star, axiom-clean) IS the q=3 door-type
  branch of this route procedure. Direct plug-in.
- Every route branch is STRUCTURAL except NCH. => the keystone ODLFullMaskRouteComplete, and via it
  SiblingRoute + several others, all reduce to closing NCHRoute (census -> certified/structural) + the
  finite leaf certs. NCHRoute is THE pivotal remaining Branch-A coverage atom.
- Termination: absorb/prune are internal nodes that strictly decrease the ambient-excess / rank measure
  (well-founded), so the recursion terminates.


## Qlt3 PrimeComplete — structural classifier design (GPT-Pro SIBLING, 2026-07-07; Claude-gated)

FALSIFIER-FIRST VERDICT: Qlt3 PrimeComplete is NOT yet a structural theorem. It CAN be made N-uniform +
finite, but ONLY IF (a) the q3-prime (q<=2 door) LEAF TABLE is explicitly emitted, and (b) the
admissible-SIGNATURE EXHAUSTION theorem is proved. SIBLING can design the classifier + Lean statement but
cannot honestly name the certified leaf list unless it exists as an external artifact. Missing either =>
Qlt3 remains a real coverage gap (consistent with the gap ledger).

### Design: finite signature classifier (NOT bounded-N census)
A q3-prime ODL node reduces to a finite SIGNATURE (bounded row/door/side/class/terminal-shadow data), not a
graph-size-dependent object. Row skeleton fixed = (q0,q1,q2,q3,q4) in Z/5Z. The signature records only
bounded door-side / class / terminal-shadow data. Structure Qlt3Sig { rowOrient, ... }.

### Relationship to Seed3 (q=3): DISTINCT domain
q3 = "q<=2" = FEWER than 3 active doors (the route's q<=2 / TWO_DOOR branch); Seed3 = the exactly-3-door
seed-prime condition. Safe classification: q3-prime is a DISTINCT ODL domain with its own finite classifier,
UNLESS the archives contain a formal reduction to Seed3 (then Qlt3PrimeComplete follows from
Seed3ClassifierComplete + an embedding theorem). Overlaps require the route tree to state priority.

### Would-be Lean theorem (two layers)
1. Signature extraction: structure Qlt3Sig where rowOrient : RowOrient ; ... (finite bounded data).
2. Signature-exhaustion + leaf classifier: every admissible Qlt3Sig maps to one of the finite q2 leaves
   (the emitted leaf table), proved by finite enumeration over the signature space.

### Claude gate + unified pattern
Consistent with MAIN's keystone: Qlt3 = the route's q<=2 branch. The UNIFIED PATTERN across the 6 unproven
coverage theorems (Qlt3, NCH, ODLFullMaskRoute-composition, SiblingRoute, ownership): each is a FINITE
SIGNATURE CLASSIFIER needing (i) an emitted finite leaf-table/ownership artifact + (ii) a signature/route
EXHAUSTION proof. NOT census, NOT a hardness wall - a closeable structure (emit artifact + prove exhaustion).
The ONE exception is M6 aggregation existence (lengthSurplusChargeCert_exists = a genuine global Hall/Farkas
theorem, not a finite signature classifier). ACTIONABLE: emit the finite leaf tables (Codex) + prove the
exhaustion theorems (GPT-Pro), per coverage atom. Falsifier watch: a q3/NCH signature outside its finite
leaf table = the gap.


## NCHRoute completeness — structural design (GPT-Pro MAIN, 2026-07-07; Claude-gated)

THE Branch-A coverage bottleneck. Classification:
- NCHRoute SOUNDNESS: finite / checker-complete, N-uniform (NCHRouteCert + payloads, LensGates, T=1/T=2 corridor).
- NCHRoute EXISTENCE/COMPLETENESS: structural theorem STILL OPEN. Missing theorem: every saturated, pruned,
  overfull, full-mask, non-C5-hom core contains a terminal Hall corridor certificate (a Z5 voltage obstruction).

### Structural proof strategy (finite, reducible - NOT a hardness wall)
O saturated+pruned+overfull+full-mask, non-C5-hom => boundary C5 labeling does not extend to a minimal
obstruction H; T = its terminal set. Saturation+pruning => H is a CLOSED terminal obstruction (no missing
door/bag, no prunable appendage, every terminal shadow closed, every corridor owned).
- **T=1**: Terminal Hall theorem. Minimal Hall obstruction rooted at t gives a terminal shadow; the completed
  flip is either sigma<0 (contradicts max-cut), sigma=0 & K<0 (contradicts Gamma-min), or FLAT (C5 labeling
  extends, contradicts minimality of H). => T=1 STRUCTURALLY COVERABLE.
- **T=2**: corridor theorem. A minimal two-terminal label obstruction yields a PRIMITIVE LENS. Finite lens
  types = {RR, RB, RD, DD, TTsame, TTopposite, TR} (7). Each routed by NONNEG (corridor Hall >=0) / CROSS
  (switch contradiction) / LABEL (labeling extends) / FORBID (triangle/shorter-odd-row/invalid-shadow) / OSC
  (residual close).
- **T>=3**: NEEDS THE MULTI-TERMINAL SPLITTING LEMMA (T>=3 -> T<=2). *** THE KEY MISSING PIECE. *** The finite
  7-lens type list does NOT discharge completeness unless the splitting lemma is proven.

### Would-be Lean shapes (MAIN)
  structure FullMaskODLNode (G)(c)(rows)(Q)(O) : Prop where rowInDB; len5; fullMask; overfull; saturated;
    pruned; activeClosure
  structure NCHRouteCert (G)(c)(rows)(Q)(O) : Type where symbol : NCHSymbol; checkSymbol : Bool
    terminalHallPayloads : List TerminalHallCert; corridorPayloads : List T2CorridorCert
    lensPayloads : List LensGates.LensGateData; closePayloads : List LensGates.OSCResidualCloseCert
    leaf : ODLRouteLeaf
  -- Soundness: checkNCHRouteCert = true => NCH leaf bound holds (checker-complete)
  theorem nch_route_complete (hTri)(hMax)(hGamma)(hNode : FullMaskODLNode ...)(hNotC5Hom : not C5HomCore G c O) :
    exists cert, checkNCHRouteCert G c rows Q O cert = true   -- OPEN: needs multi-terminal splitting lemma

### Claude gate + pivot
NCHRoute existence reduces to {T=1 Terminal Hall theorem, 7 primitive-lens routings, MULTI-TERMINAL SPLITTING
LEMMA}. The splitting lemma (T>=3 -> T<=2) is THE pivotal remaining Branch-A sub-lemma; T=1 + 7-lens are finite
structural arguments (max-cut/Gamma-min/tri-free contradictions). Closeable finite structure. Retasked MAIN on
the multi-terminal splitting lemma. Consistent with the unified coverage pattern (finite classifier + exhaustion).


## Multi-terminal splitting lemma — verdict + THE decisive crux (GPT-Pro MAIN, 2026-07-07; Claude-gated)

### Verdict: the NAIVE splitting lemma is FALSE (non-Helly)
As stated it is false at the level of pure C5-label extension: a T>=3 terminal obstruction need NOT contain a
genuine obstruction on a subset T'<=T with |T'|<=2. The obstruction can be NON-HELLY (every 1- and 2-terminal
projection extends, but the whole 3-terminal system does not). MAIN gives a minimal non-Helly obstruction shape.

### NCHRoute status (refined)
- T=1 Terminal Hall: structurally/certifiably CLOSED.
- T=2 primitive lens (7 types): structurally/certifiably CLOSED (modulo lens/OSC close certs).
- T>=3 splitting: GENUINE RESIDUAL STRUCTURAL GAP.

### The separator-split recursion (works EXCEPT the irreducible case)
If a separator S (|S|<=2) splits H into components each meeting terminals: branch over S -> Z5 (<=25 cases).
For each label assignment, at least one component C with terminal set (T cap C) union S must fail to extend
(else all components glue -> extension of H). So the obstruction splits into a finite disjunction of smaller
terminal obstructions; measure |H|+|T| lexicographic; well-founded.
  MultiTerminal(H,T): if |T|<=2 use T=1/T=2 NCH machinery; else if a <=2 separator S exists, for each alpha:S->Z5
  choose a failing component C_alpha, recurse on (C_alpha, (T cap C_alpha) union S); ELSE irreducible high-terminal
  obstruction. THE LAST CASE IS THE PROBLEM.

### Lean shapes (MAIN)
  structure TerminalSeparatorSplitCert { sep : List Nat (card<=2); assignments : List(List Nat) (Fin5);
    children : List ChildObstruction; coverage : Bool (every alpha:sep->Fin5 once); childSound : List ChildNCHCert }
  theorem terminal_separator_split_sound (hcheck = true)(hChildren : forall child, NCHRouteSound child) :
    NCHRouteSound (parent H T)                              -- SOUNDNESS: buildable/checker-complete
  theorem multiterminal_splitting_complete (hTri)(hMax)(hGamma)(hNode)(hMin : MinimalNonC5TerminalBlock ... H T)
    (hT3 : 3 <= T.card) : exists cert : TerminalSeparatorSplitCert, checkTerminalSeparatorSplitCert = true
    -- EXISTENCE: currently MISSING (the irreducible high-terminal case is unproven)

### Two repair paths
1. STRUCTURAL: prove the existence theorem = "every minimal saturated/pruned/full-mask/overfull non-C5-hom
   terminal obstruction HAS a <=2 separator" (rules out irreducible high-terminal cores). => compiled.
2. PER-INSTANCE: extend NCHRouteCert to allow general multi-terminal (T>=3) finite CSP/Hall certificates
   emitted per instance. => sidesteps the theorem but makes these atoms a per-instance certificate SCHEME
   (data, not a compiled structural lemma; anti-fake-progress-insufficient for a compiled M6/coverage).

### THE decisive crux (Claude) — the single shared structural question of the whole remaining program
NCH T>=3 splitting existence == M6 closure-projection (SIBLING): both need EVERY minimal saturated/pruned/
full-mask/overfull non-C5-hom obstruction to have a <=2 SEPARATOR (equiv. project to a CLOSED CORRIDOR /
closed shadow to which the switch-or-C5-label dichotomy applies). ONE structural question:
  Does triangle-freeness + saturation + pruning + full-mask + overfull FORCE a <=2 separator (no irreducible
  high-terminal obstruction)?
  YES => NCHRoute + M6 both close as COMPILED structural theorems => the compiled program can close.
  NO (irreducible obstructions occur in actual cores) => these atoms need per-instance CSP/Hall certs => the
  program is inherently a per-instance certificate scheme for these nodes (not fully compiled-universal).
This is THE decisive question for whether a fully-compiled delta=0 proof is reachable via this program.
Falsifier-watch: if a realizable irreducible high-terminal obstruction (in an actual saturated/pruned/full-mask/
overfull non-C5-hom core) is exhibited, that forces path-2 (per-instance) for these atoms — not a delta=0
falsifier, but a proof that the compiled-universal route needs the general CSP cert.

