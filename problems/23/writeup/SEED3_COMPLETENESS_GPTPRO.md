# SEED3-PRIME COMPLETENESS PROOF + CLASSIFIER ARTIFACT — GPT-Pro (main), 2026-07-04

Source: main thread, reply to the Seed3Complete enumeration consult (12,535 chars).
Companion to the O13 classifier spec (archived 2026-07-04). Verbatim-as-rendered summary;
full text in-thread.

## 0. IMPORTANT CORRECTION (honesty upgrade)
A referee-grade Seed3 proof must NOT claim a hand-enumerated list of non-EQ/SIB candidates
unless the literal list is a checked artifact. Seed3Complete = finite-enumeration CERTIFICATE
theorem with TWO artifacts:
 (1) candidate UNIVERSE certificate — every pruned saturated C5-hom overfull three-door
     quotient reduces to a candidate code in the list (or gets an immediate output witness);
 (2) per-candidate OUTPUT certificate — each listed candidate routes to one of
     EQ | SIB | NO_OVERFULL | NEG_SWITCH | PRUNABLE | NOT_SATURATED | FOUR_DOOR.
Only after BOTH check does "survivors = EQ, SIB" follow — as a computed result, not an
assertion.

## 1. Door-graph type completeness — PROVEN
3 effective bad doors form a simple bipartite graph in V4 x V0 with exactly 3 edges
(isolated endpoints removed). Bipartite => no odd cycle. Connected => tree with 3 edges
=> P4 (degrees (2,1)/(2,1)) or K_{1,3} (star). Disconnected => edge partition 2+1 => P2 u E
(2-edge path + disjoint edge), or 1+1+1 => 3E (perfect 3-matching). Exhaustive.

## 2. Candidate encoding
ThreeDoorCandidate { doorType, numBags, classOf : Nat -> Fin 5, blueEdges, badDoors,
rowTemplates, activeRows, positiveBags, supportBags }. Validity: bags in range; edges
loopless+normalized; blue edges join consecutive C5 classes; bad doors V4-V0; EXACTLY 3
declared; door graph has declared type; every row template = length-5 path for a declared
door; every declared door has >= 1 template; every positive bag on >= 1 row;
quotient true-twin-contracted.

## 3. Finiteness via WIDTH CERTIFICATE (no unsafe hand bound)
Seed3WidthCert { maxBags : Fin 5 -> Nat, overflowWitness : forall code, exceeds maxBags code
-> Seed3OutputWitness code }. Any quotient exceeding the width bounds ALREADY has a
non-survivor output (NO_OVERFULL/NEG_SWITCH/PRUNABLE/NOT_SATURATED/FOUR_DOOR). Survivor
candidates have <= maxBags(i) bags in class Vi. Finite code space bound (pre-filter):
prod_i 2^(b_i * b_{i+1}) * C(b4*b0, 3); artifact list is canonical modulo C5 reversal,
within-class relabelling, true-twin contraction, door-type automorphisms.

## 4. Seed3UniverseCert
{ widthCert; candidates : List ThreeDoorCandidate; canonicalTable : CanonicalLookupTable }.
Checker: every candidate valid + canonical; lookup table maps EVERY in-width code to a listed
candidate OR an immediate output witness; over-width codes handled by overflowWitness.
STATUS: CERT-PENDING (Codex artifact).

## 5. Output witnesses (canon structures; consistent with archived O13 spec)
- EQ: EQIsoCert {contractMap, fiberOf, weightExpr, edgeImageProofs, rowImageProofs,
  twinProofs}. EQ classes V0={1,7} V1={3,5} V2={0,8} V3={4,6} V4={2,9}; doors {19,27,79};
  11 row templates: (1,5,0,6,9),(1,5,8,4,9),(1,5,8,6,9),(7,5,0,6,2),(7,5,8,6,2),(7,3,8,6,2),
  (7,5,0,6,9),(7,5,8,4,9),(7,5,8,6,9),(7,3,8,4,9),(7,3,8,6,9). Checker: fibers partition
  bags; fiber -> one EQ vertex; class compat; true-twin compat per fiber; blue edges
  aggregate to EQ blues; doors biject to {19,27,79}; templates map into the 11; weights =
  fiber sums. Consumers: ODL -> EQ-ODL1 + EQ-AM; Bank0 -> EQ-CERT1.
- SIB: same shape; classes V0={1,2} V1={5,6} V2={0,8} V3={3,4} V4={7,9}; doors {17,19,29};
  13 templates: (1,5,8,3,7),(1,5,8,4,7),(1,6,8,3,7),(1,6,8,4,7),(1,6,0,4,7),(1,5,8,3,9),
  (1,5,8,4,9),(1,6,8,3,9),(1,6,8,4,9),(1,6,0,4,9),(2,6,8,3,9),(2,6,8,4,9),(2,6,0,4,9).
  Consumers: ODL -> SIB-S7 + SIB-AM; Bank0 -> SIB-CERT1.
- NO_OVERFULL: per-active-row RowNoOverfullCert {rowId, denom>0, target = D_R(N - I_R),
  coneCert}; every active row exactly once. Consumers: ODL immediate (I_R <= N <= N + eta
  via Bank0 eta >= 0); Bank0 -> BankBlock (not scalar bank).
- NEG_SWITCH: NegSwitchCert {switch : CompletedSwitchCert, kind CutImprove|GammaDescent,
  strictCert}. CutImprove: ConeCert -sigma(S)-1 >= 0. GammaDescent: flipBConnected = true,
  sigma(S) = 0, ConeCert -nu(S)-1 >= 0 (or -nuK-1 with sigma=0). Consumer: contradiction
  (max-cut / gamma-min).
- PRUNABLE: PrunableCert {H, T, rest, noCrossExceptT : BoundarySeparationCert, loadDenom,
  loadNum = D*s_H(Q cap T), sizeNum = D(|H|-|T|), defectTarget, coneCert:
  D(|H|-|T|) - D*s_H(Q cap T) >= 0}. Consumers: ODL -> AmbientPrune; Bank0 -> reduced core /
  BankBlock / NCH machinery.
- NOT_SATURATED: SaturationFailure = MissingDoor(door,rowWitness) | MissingBag(bag,
  rowWitness); checker verifies effectiveness (row intersects active support). Consumer:
  absorb + rerun; contradictory under saturated-input hypothesis.
- FOUR_DOOR: {fourthDoor, rowWitness} — bad V4-V0 edge distinct from the 3 declared with
  valid effective row. Consumers: ODL -> q>=4 A1-5mask; Bank0 -> BankBlock.

## 6. Completeness theorem
TrueTwinFiniteSeed3Contraction: under C5-hom + pruned + saturated + overfull + exactly 3
effective doors + all-l5 + no NEG_SWITCH/PRUNABLE/NOT_SATURATED/FOUR_DOOR witness, the
true-twin contraction lies in the finite universe generated by the 4 door types + width
bounds + row-used interior signature enumeration + saturation/pruning filters.
(Seed3Complete): every admissible three-door quotient has SOME cert with
checkSeed3Classifier = true. Proof skeleton: door type in the 4; over-width -> width cert
output; else finite canonical code -> lookup table -> listed candidate -> checked output.
STATUS: CERT-PENDING as finite enumeration artifact.

## 7. Survivors
After saturation/pruning/negative-switch/overfull/fourth-door filters, the only candidates
with SEED output are EQ and SIB — as the final result of the artifact (all non-EQ/SIB
candidates carry one of the other five outputs).

## 8-9. Checker order + determinism
checkSeed3Classifier: syntax -> C5-hom rule -> 3 doors -> row validity -> output witness
(7 branches) -> typed Seed3Route. Seed3Complete: width cert -> lookup table -> every listed
candidate's witness -> conclude. Output not mathematically unique (NO_OVERFULL and PRUNABLE
can coexist); EMISSION priority NOT_SATURATED > FOUR_DOOR > NEG_SWITCH > PRUNABLE >
NO_OVERFULL > EQ > SIB; checker verifies whichever is emitted; completeness artifact uses
priority so every candidate appears once.

## 10. Final Seed3-prime theorem
Assuming Seed3Complete + classifier soundness: a pruned saturated C5-hom overfull three-door
core routes to EQ, SIB, or a certified non-survivor output; EQ/SIB feed the seed branches
(ODL proven there); the other five reroute or eliminate. The q=3 branch is complete.

## OPEN ITEMS CREATED BY THIS REPLY
- WIDTH BOUNDS: concrete maxBags values + overflow argument = next design consult (main).
- O13-UNIVERSE-EMIT: Codex artifact = width cert + canonical enumeration + lookup table +
  per-candidate output witnesses (directive posted 2026-07-04).


# ===== WIDTH BOUNDS: HONEST FORM (main thread, 2026-07-04) =====

BOTTOM LINE: unconditionally PROVEN only |V0| <= 3 and |V4| <= 3 (3 doors have <= 3 endpoints
per side; in a pruned saturated positive-flow core every positive-flow bag in V0/V4 must be an
effective-door endpoint — else it lies on no length-5 row => suppressed / NOT_SATURATED /
PRUNABLE). Interior classes V1/V2/V3: NO sound hand bound exists from twin-contraction +
saturation + C5-hom + 3-doors alone — the recursive profile inequalities do NOT close
(|V1| <= 7(2^|V2|-1), |V2| <= (2^|V1|-1)(2^|V3|-1), ...). Any handwritten interior bound
(e.g. 49) would be referee-rejected. Interior bounds must be CERTIFICATE-BACKED.

Seed3WidthCert (final contract): { maxBags : Fin 5 -> Nat; endpoint0 : maxBags 0 = 3;
endpoint4 : maxBags 4 = 3; overflowCerts : List OverflowCert; coverage :
OverflowCoverageTable }. Checker: endpoints by door argument; every canonical code exceeding
a declared bound maps via coverage to an OverflowCert; every OverflowCert verifies one
non-survivor output. Sound theorem: checkSeed3WidthCert = true + Seed3CandidateHyp qut +
(exists i, b_i < classSize qut i) -> NonSurvivorRoute qut.

OverflowCert { classId, bound, pattern, reason, witness }; OverflowReason = TwinDuplicate |
NoOverfull | NegSwitch | Prunable | NotSaturated | FourDoor.
- TwinDuplicate (cleanest): two bags same class, identical open neighborhoods, same cut side,
  same row-role + door-endpoint status => true twins => contradicts twin-contraction; reject
  code before routing.
- NotSaturated: missing bag/door forced by the overflow pattern, with effective row witness.
- Prunable: terminal subclosure H via T with s_H(Q cap T) <= |H|-|T| (separation + ConeCert)
  — typical for redundant row-family branches.
- NoOverfull: per-row ConeCerts I_R <= N — expected when many alternative path bags dilute
  row load and increase N.
- NegSwitch: CompletedSwitchCert with sigma < 0, or sigma = 0 and nu < 0 — expected for
  crossing/nonminimal extra bags creating terminal-shadow descent.
- FourDoor: fourth effective door witness.

ATTEMPT LADDER (interior bounds are ARTIFACT choices, not theorems): (3,3,3,3,3) first —
raw size 84 * 2^45 ~ 3e15, canonical expected 1e3-1e5; fallback (3,4,4,4,3) — 84 * 2^65 ~
3e21 raw, needs signature generation, expected 1e5-1e7 (below 1e5 if signature-based);
last resort (3,7,7,7,3) — 84 * 2^149, signature-based ONLY. Raise ONLY the failing class.

EMITTER STRATEGY (mandatory): NEVER raw-enumerate edge bitsets. Row-template generation:
door type (P4/K13/P2uE/3E) -> enumerate length-5 row templates for the 3 doors -> only bags
used by >= 1 row -> blue edges = union of row-adjacent pairs + optional edges ->
immediately true-twin-contract -> saturation test -> overfull test -> emit output witness.

NON-CIRCULARITY (binding): width/overflow proofs may use C5-hom, twin-contracted, saturated,
pruned, overfull, exactly-3-doors, all-l5, max-cut + gamma-min (only through NEG_SWITCH
soundness), NCH-def (only through PRUNABLE). May NOT use ODL, C5-RS, GERSH, or Seed3 itself.
NO_OVERFULL witnesses are non-circular (they contradict the branch hypothesis directly).

FINAL WARNING (verbatim sense): role-profile hand bounds are unsound unless proven equivalent
to true-twin neighborhood data or every overflow profile carries a non-survivor certificate.
The width theorem is certificate-backed — this is the last honest form of Seed3-prime
completeness.


# ===== ODL SEED3 ROUTE-TREE PROVIDER (main thread, 2026-07-05) — FULL CONTRACT =====
PURPOSE: classifier outputs NOT_SATURATED/PRUNABLE are reroutes, FOUR_DOOR exits to q>=4 —
so the ODL provider is a FINITE ROUTE TREE proving ambient rowSum(Q) <= N + eta with eta
ambient through all recursion.
STATE: Seed3CoreState {support : VSet(List Nat), qut : C5QuotientData, activeRow, phase
(saturating|saturated), rank : Nat (audit metadata; checker requires strict decrease but
recursion is STRUCTURAL on the tree — rank prevents invalid cyclic route data)}.
AMBIENT BOOKKEEPING: supportRowSum (support-local, ambient graph); AmbientExcess =
supportRowSum - |S| - etaQ; CoreODLGoal = AmbientExcess <= 0; RootRepresentsRow:
supportRowSum(root) = rowSum(Q); |root.support| <= N => root goal gives ambient ODL.
TREE: inductive Seed3RouteTree = leafEQ(EQIsoCert) | leafSIB(SIBIsoCert) |
leafNoOverfull(NoOverfullCert) | leafNegSwitch(NegSwitchCert) | leafFourDoor(FourDoorCert) |
absorb(NotSaturatedCert, AbsorbLinkCert, child, subtree) |
prune(PrunableCert, PruneLinkCert, child, saturationSubtree).
ABSORB NODE: AbsorbLinkCert {parentSupport, childSupport, absorbedKind (missingDoor|
missingBag), absorbedDoor/Bag, rowWitness, recomputeProof : QuotientRecomputeCert,
supportProof, excessLink : ConeCert}. excessLink proves D*(AmbientExcess(child) -
AmbientExcess(parent)) >= 0 — EXPLICIT, no informal harmlessness. Checker: witness valid +
child = EXACT recomputed absorbed quotient + parent.phase = saturating + rank decrease +
excessLink. Sound: child goal + link => parent goal.
PRUNE NODE: PruneLinkCert {parentSupport, H, T, childSupport, separation, loadDefect
ConeCert D(|H|-|T|) - D s_H(Q cap T) >= 0, recomputeProof, saturationProof :
BankClosureTrace}. TWO CHILD VERSIONS: A pure prune (child = parent \ (H\T); simpler for
Lean) | B prune-and-close (saturationProof verifies closure; easier for emitters) — both
allowed with the excess-link chain AmbientExcess(parent) <= AmbientExcess(pureChild) <=
AmbientExcess(child).
LEAVES: EQ (checkEQIsoCert + EQBranchODLInputs => goal); SIB (SIB-S7 + SIB-AM);
NO_OVERFULL (I_R <= |support| all active rows + etaNonneg => goal); NEG_SWITCH (sigma < 0
OR sigma = 0 + nuK < 0 + flipBConnected; contradiction w/ maxcut/gamma-min => False.elim);
FOUR_DOOR (leaf carries FourDoorCert only; FourMaskInputs lives in the GLOBAL provider
package, not the leaf — q>=4 A1-5mask absorption applied by fourDoor_to_ODL).
TERMINATION: checker structurally recursive on the tree (Lean-sufficient); rank checked
strictly decreasing per internal node; recommended emitter rank = M*satDebt + supportSize
(M > Nmax) but ANY strictly-decreasing Nat accepted (rank = audit metadata, not soundness).
CHECKER: checkSeed3RouteTree dispatch per constructor (leaf checkers; internal: witness +
link + rank + recurse).
PROVIDER PACKAGE: ODLRouteInputs {etaNonneg, eqBranch, sibBranch, fourMask, maxCut,
gammaMin (G c form), ambientRepresent}. SOUNDNESS: Seed3RouteTree.sound by tree recursion
(7 cases). ROOT: Seed3RouteTree.odl_full: check + inputs + RootRepresentsRow + support in
universe => rowSum <= N + etaQ.
BANK0 MAP (distinct consumers): EQ -> EQ-CERT1; SIB -> SIB-CERT1; NO_OVERFULL -> BankBlock;
NEG_SWITCH -> contradiction; PRUNABLE -> reduced core/BankBlock/NCHBank; NOT_SATURATED ->
absorb+rerun; FOUR_DOOR -> BankBlock. Never reuse ODL conclusions for Bank0.
EMISSION RULES: NOT_SATURATED => absorb node (never leaf); PRUNABLE => prune node;
FOUR_DOOR => leaf; every internal node = witness + child quotient + recompute cert +
excess-link ConeCert + smaller rank; root = first candidate entering the route (need not be
saturated — tree supports saturation repair internally, serving both the formal
saturated-core theorem and the practical emitter pipeline).
=> ODL PROVIDER ARCHITECTURE COMPLETE. Next validation step: hand-verified micro example.
