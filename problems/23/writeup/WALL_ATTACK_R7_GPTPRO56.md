# WALL ATTACK — R7: fiber falsified; final wall = strict-dual-guided split (GPT-5.6 Pro, 2026-07-10, USER-RELAYED)

**[CLAUDE GATE HEADER — verification queue: the 12-row footprint facts, the 4x5=1 combination, the fractional
solution, the 662-vtx realization, endpoint-half arithmetic (gate script next tick: _claude_r7_fiberless_gate.py).**
- VERDICT 1: **universal fiber existence FALSE** — explicit 12-atom/11-short-edge support tree, all supports
  size 4, no private edge, pair-unions ≥5, connected, EXACT inclusion-minimal defect-one (max r(X) table),
  yet NO exact-one fiber: integer combination A1+A2−2A3−A4−A8+A9+2A10 forces 4·x₅ = 1 (impossible over
  {0,1}); x_i ≡ 1/4 is a feasible FRACTIONAL exact-one solution ⟹ pure integrality obstruction, NO linear
  deficiency ⟹ "fiberless ⟹ door lower bound" is unprovable by any linear/cut-count argument.
- VERDICT 2: "fiberless crossing ⟹ bankable" also NOT derivable (W1 gives sink nonemptiness, not doors/
  capacity/bottleneck-freedom; B-conn gives blue connectivity; minNeg doesn't manufacture tokens).
- **THE FINAL RESEARCH THEOREM (wall of record): `StrictDualRootCrossingPureLensSplit_exists`** ≡
  NoSplitStrictDualImpossible_at_rootCrossing — in a MinNeg cage with a root crossing, a CHECKED STRICT
  full-bank dual forces a checked concrete PureLensCageSplit (+ PureLensBankSingleOwner). The strict dual
  GUIDES the lens selection (static crossing/fiber cannot). Exhaustiveness then: bank primal exists → banked
  branch; else exact Farkas strict dual → split branch. Strictly weaker than both failed proposals.
- Bookkeeping stack (derivable now): checkExactOneFiberExists_iff; **endpointHalf_is_relaxedCutCover**
  (UNIVERSAL half-singleton cover: λ({v})=1/2 on atom endpoints ⟹ coverage = 1 exactly, short congestion ≤ 1
  — atom multiplicity irrelevant!); fullBankBundle_of_endpointHalfDoorComplete;
  rootCrossing_split_or_bank_or_falsifier (trichotomy). Derivable graph inequality:
  **endpointHalf_offSupportLoad_ge_one** (Loff ≥ 1 from Σ½·deltaM_card_le_deltaB_card + defect-one +
  congestion ≤ 1 — genuine, fiberless-independent).
- New checker/API facts: EndpointHalfBoundaryPartition (no contribution lost bridge→LP);
  EndpointHalfDoorComplete (fast path, sufficient not necessary); ConcretePureLensEnumerationComplete;
  FullBankLPBundleEquivalence; checkRootCrossingDichotomyFalsifier.
- **Decisive falsifier target (final form)**: RootCrossingDichotomyFalsifier = MinNeg + crossing +
  noExactOneFiber (census filter) + EXHAUSTIVE noConcretePureLensSplit + checked strict full-bank dual
  (StrictGap). Precursor record: deficient endpoint-half port set (Σ load > Σ legalNbr caps).
- Classifier (decidable, bank-first): (1) endpoint-half λ; (2) exact rational port→bank max-flow — feasible ⟹
  banked; (3) enumerate exact-one fibers → partitions → Restrict/Proper/StrongSplit/singleOwner → split;
  (4) full exact bank LP — primal ⟹ banked, else keep strict Farkas dual; (5) exhaustive PureLens enumeration
  (NOT only fiber-generated); (6) checked falsifier. External solvers may propose; Lean checks everything.

## THE FIBERLESS FOOTPRINT (verbatim data — gate input)
Short edges: f0=0–2 f1=1–3 f2=1–6 f3=2–5 f4=2–10 f5=4–5 f6=4–6 f7=4–8 f8=4–9 f9=5–7 f10=7–11.
Atoms (bad edge : support): A0=3–8:{f1,f2,f6,f7}; A1=6–11:{f6,f5,f9,f10}; A2=9–10:{f8,f5,f3,f4};
A3=3–9:{f1,f2,f6,f8}; A4=6–10:{f6,f5,f3,f4}; A5=1–7:{f2,f6,f5,f9}; A6=8–11:{f7,f5,f9,f10};
A7=1–2:{f2,f6,f5,f3}; A8=0–11:{f0,f3,f9,f10}; A9=0–9:{f0,f3,f5,f8}; A10=3–5:{f1,f2,f6,f5};
A11=8–10:{f7,f5,f3,f4}. Column multiplicities [2,3,5,6,3,9,7,3,3,4,3]. Max r(X) by |X|:
0,0,0,0,1,2,3,5,7,8,10,12 ⟹ every proper subfamily Hall-satisfying; |S|=12 > |Eshort|=11.
Rational solution space: x0=x2=x4=x10=t; x1=x3=x9=1/2−t; x5=x6=x7=x8=1/4.

## THE 662-VTX REALIZATION (verbatim params)
Support tree bipartition: Side0={1,2,4,7}, Side1={0,3,5,6,8,9,10,11}. Locks (10 relations × 13 disjoint
length-6 paths): Side0: (1,4),(2,4),(7,4); Side1: (0,5),(3,5),(6,5),(8,5),(9,5),(10,5),(11,5).
internal(r,k,t) = 12 + 5·(13r+k) + (t−1), r∈[0,9], k∈[0,12], t∈[1,5]. N = 662, E = 11+12+780 = 803.
Violated relation ⟹ ≥13 bad > 12; relations respected ⟹ classes opposite 12 bad / equal 23 ⟹ unique max cut
± complement; Γ-min automatic; tri-free (4 cases); unique length-4 geodesics; blue connected.
Root crossing: V0 = {3,1,6,4,8} (support verts of A0=3–8); atom A3=3–9 unique geodesic 3–1–6–4–9 forces
through 4–9; W = V0 ∪ {9}; thirteen (9,5)-lock ports at 9 with door/VertexSlack(9) sinks disjoint from V0's.
Bank branch explicit: endpoint-half cover; 260 lock endpoint edges, 39 at unselected vertex 4 ⟹ 221 used
door sinks @ load 1/2 (25/2 ≤ 25); total routed 221/2 (5525/2 scaled); DoorCap 6500; balance
25·11 + 6500 − 25·12 = 6475 ⟹ NOT MinNeg — fiberless + crossing, still banked.

## FINAL THEOREM (verbatim shape)
StrictDualRootCrossingPureLensSplit_exists (hGraph hTri hMax hGammaMin hBConn hTenFacts hW1 hCageLegality
hMinNeg) (crossing) (d : fullBankLP.Dual) (hd : checkDual d = true) (hStrict : d.StrictGap) :
∃ S, checkConcretePureLensCageSplit S = true ∧ checkPureLensBankSingleOwner S = true.
Then: bank primal ∨ (Farkas ⟹ strict dual ⟹ split). The 662-vtx example does not challenge it (explicit bank
primal ⟹ no strict dual exists).
