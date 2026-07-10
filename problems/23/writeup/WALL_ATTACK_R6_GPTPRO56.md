# WALL ATTACK — R6: pivot-lemma verdict (GPT-5.6 Pro, 2026-07-10, RELAYED VERBATIM BY USER)

**[CLAUDE GATE HEADER:**
- VERDICT: `RootCrossingPureLensSplit_exists` NOT derivable from root crossing + ten facts + W1 + cage
  legality. The direct root-based split FAILS `noDouble` on my verified 359-vtx cage: atom A₁₀ = L₁R₀ is
  `atomSupportedOn` both L₁U (new root side) and VR₀ (old root side) — bank incidence and support incidence
  are INDEPENDENT structures. Real-graph CE to "disjoint legal roots ⟹ atom split".
- BUT: a **left-fiber pure-lens split EXISTS on the cage**: fiber {L₀U,L₁U,L₂U} (every atom uses EXACTLY ONE
  fiber edge = its LᵢU); leftFiber {L₁U} → S₁ = {A₁₀,A₁₁,A₁₂}, X₁={L₁}; rightFiber {L₀U,L₂U} → S₂ = 6 atoms,
  X₂={L₀,L₂}; shared corridor (U,C,V,R₀,R₁,R₂ + UC,CV,VR₀,VR₁,VR₂) stays PARENT-ONLY (the only viable
  ownership rule: child resources may omit, never duplicate).
- **LEDGERS HAND-VERIFIED EXACT (my check)**: raw balances −25 = −50 + (−100) + 125 ✓. Doors: 70 lock paths ×
  2 restriction-exit edges = 140 × 25 = 3500; left 10 (250) + right 20 (500) + parent-only 110 (2750) ✓.
  Balances: left 25+250−75=200; right 50+500−150=400; parent 200+400+2875 = 3475 = 200+3500−225 ✓.
  **⟹ RESIDUAL GATE 2 SETTLED: the 359-vtx cage is NOT MinNeg (balance ≥ +3475 before vertexSlack/C5/prune)
  — a root-crossing exhibit, NOT a wall falsifier. It lies in the BANKED branch (defect 25 ≪ DoorCap 3500).**
- **NEW WALL OF RECORD (corrected lemma)**: research theorem = **every concrete root crossing admits
  `RootCrossingSplitOrBankCert`** (inductive: split = RootCrossingConcretePureLensWitness [fiber-based,
  feeds compiled concretePureLensCageSplit → ledgerSep → no_ledgerSep_in_minNeg] | banked =
  FullBankRelaxedCoverBundle [crossing absorbed by door/vertexSlack/C5Base/prune capacity → feeds
  FullBankGlobalPackage]). Elimination theorem no_rootCrossing_in_minNeg is BOOKKEEPING. Strictly weaker and
  more plausible than the unconditional split; shared corridors stay parent-only or get banked; no η ever.
- NEW CHECKER FACTS: (1) **ForcedEdgePureFiberCert** — fiber transversal (unique fiber edge per nonzero atom
  ⟹ noDouble + cover-or-zero; partitioned leftFiber/rightFiber; proper disjoint restrictions) — genuinely
  new; NOT implied by the ten facts (support ≥6 allows multi-fiber atoms). (2) PureLensBankSingleOwner —
  ownership left|right|parentOnly per Bank-list index, mixed-incidence C5/prune parent-only — mostly
  bookkeeping. (3) parent-neg ⟹ child-neg = compiled bank_add_le_of_disjoint_subcages + PureSplit finite-sum
  (D(parent) ≤ D(left)+D(right)) + rational order algebra (spelled out §d; audit direction of
  ledgerSep_of_concretePureLensCageSplit).
- MY NEXT: (i) extend _claude_r5_candidate_gate.py with the R6 ledger as an exact check (numbers verified by
  hand already); (ii) retask 5.6-Pro on THE research theorem: existence of RootCrossingSplitOrBankCert for
  every concrete root crossing — decisive sub-question: when does the FIBER exist (unique-fiber-edge fails
  for support ≥6 atoms — what replaces the LᵢU-layer in general double-stars? is defect-one + no-private +
  pair-union enough for a transversal fiber?), and when it doesn't, why is the crossing bankable (the
  dichotomy's exhaustiveness IS the wall now); (iii) hand Codex the bookkeeping: elim_minNeg wrapper +
  PureLensBankSingleOwner + SplitOrBank elimination against the compiled T8 surface.**]

---

## KEY VERBATIM PIECES

§(a) The only valid proof chain on the compiled surface: concretePureLensCageSplit (properLeft, properRight,
strongPureLensAtomSplit, vertexDisjoint, …) → ledgerSep_of_concretePureLensCageSplit → no_ledgerSep_in_minNeg.
Root crossing is NOT used after the four graph-heavy hypotheses — so the genuine theorem is
"crossing ⟹ those hypotheses", and the first three do NOT follow from legal-root decomposition.
`RootCrossingConcretePureLensWitness` = the witness package (left/right vertex restrictions disjoint,
children = exactly ConcreteCage.Restrict of them, leftProper/rightProper, strongSplit, bankSourceDisjoint);
`RootCrossingConcretePureLensWitness.elim_minNeg` = bookkeeping elimination.

§(why) On the verified crossing (V₀={L₀,U,C,V,R₀}, atom A₁₀, new comp {L₁}): geodesicSupport(A₁₀) =
{L₁U, UC, CV, VR₀}; A₁₀ supported on BOTH root sides ⟹ root-block children violate noDouble.

§(b) Shared corridor treatments: (1) both children — invalid (double count); (2) one child + complete-support
requirement — the other child can't contain its rows (every row uses UC, CV); (3) parent-only + fiber charge
assignment — the only viable rule. Missing fiber fact = ForcedEdgePureFiberCert (fields: fiber, leftFiber,
rightFiber partition w/ forcingEdge ∈ leftFiber, both nonempty, uniqueFiberSupport [∃! fiber edge per atom OR
AtomPureTerm = 0], disjoint vertex restrictions, fiber_realized filters, proper×2, bankSources_singleOwner).

§(c) WORKED EXAMPLE (all verified): fiber {L₀U,L₁U,L₂U}; left {L₁U}/S₁/X₁={L₁}; right {L₀U,L₂U}/S₂/X₂={L₀,L₂};
parent-only U,C,V,R₀,R₁,R₂ + UC,CV,VR₀,VR₁,VR₂. Ledger: parent 225 demand / 200 support (−25); left 75/25
(−50); right 150/50 (−100); parent-only support 125; identity −25 = −50 −100 +125. Doors: 140 total (2 per
lock path) = 3500; left 250 (10@L₁), right 500 (10@L₀+10@L₂), parent-only 2750 (110). Balances 200 / 400 /
3475 (= 200+3500−225). VertexSlack: left L₁; right L₀,L₂; parent-only U,C,V,R₀,R₁,R₂. C5Base/prune: entirely-
left-local → left; entirely-right-local → right; mixed → parent-only. Bank(left)+Bank(right) ≤ Bank(parent).
The example proves BOTH: root-block split fails noDouble AND the fiber split exists — root crossing alone
neither identifies nor proves the fiber.

§(d) parent-neg ⟹ child-neg: R(left)+R(right) ≤ R(parent) [short no-double + bank_add_le_of_disjoint_subcages]
+ D(parent) ≤ D(left)+D(right) [PureSplit finite-sum from StrongPureLensAtomSplit] ⟹ bal(l)+bal(r) ≤ bal(p);
parent negative ⟹ sum < 0 ⟹ some child < 0 (rational order algebra; ledgerSep_of_concretePureLensCageSplit
should package it — audit its direction).

§(e) `RootCrossingSplitOrBankCert` (split | banked) + `no_rootCrossing_in_minNeg` (cases; banked branch via
bankedCover_not_minNeg). THE RESEARCH THEOREM: every concrete root crossing admits the cert. "The 359-vertex
lock realization lies overwhelmingly in the banked branch: raw defect 25, external DoorCap 3500."
