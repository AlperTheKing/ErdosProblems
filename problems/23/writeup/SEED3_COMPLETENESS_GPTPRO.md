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
