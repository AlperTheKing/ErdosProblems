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

