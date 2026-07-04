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

