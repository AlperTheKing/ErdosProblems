# LOOP_STATE.md — volatile loop state (UPDATE EVERY TICK; the /loop text never changes)
# Last update: 2026-07-04T14:30Z (P(math)~86, P(Lean)~81)

## MAILBOX
- CODEX_TO_CLAUDE.md read marker (bytes): 1618290
- My outbox: coordination/CLAUDE_TO_CODEX.md (append-only)

## GPT-PRO THREADS (thread URLs stable; tab IDs go stale — find or recreate via tabs_context/tabs_create)
- MAIN    (theorem design):   https://chatgpt.com/c/6a450f06-be68-83eb-b6f4-5b855434e550  [last tab 1267096304]
- SIBLING (writeup + second): https://chatgpt.com/c/6a45e152-8de4-83eb-9aa3-87cb13427526  [last tab 1267096303]

## IN FLIGHT
- MAIN: cross-spec consistency re-audit (T=1/T=2/cubes/Bank0-blueprint interface mismatches) + O13 Seed3 classifier checker format.
- SIBLING: appendices 5.1 (certificate ledger table) + 5.2 (validation annotation).
  AmbientPrune, hunt status + contingency).
- CODEX: rung-2 chart sweep (300 charts, stats pending); then O5-EMIT (T=1 REC artifacts),
  O16/O18-EMIT (master cubes, order EQ V2 -> V1 -> V3 -> SIB V2 -> V1 -> V3), B0-4 lens gates,
  SB-1, A1 six cones.

## RETASK QUEUES
- MAIN queue: T=2 corridor cert emission spec detail (O6) if gaps surface; O11 2Door / O13 Seed3
  emission spec refresh if Codex hits ambiguity; per critical paths A-D.
- SIBLING queue: sections 3.2+ (Branch-B cert details), 5.x appendices (cert ledger, validation),
  definitions-table finalization per assembly plan.

## EXTRACTION QUEUE (landed in threads, not yet saved to files)
- sibling 1.1+1.2 (5618c)            -> problems/23/writeup/PAPER_SECTIONS_GPTPRO.md
- sibling 1.3 (7867c)                -> same
- sibling 2.1 (3914c; head captured) -> same
- sibling 3.1 (4541c)                -> same
- sibling assembly plan (19210c)     -> problems/23/writeup/DOCUMENT_ASSEMBLY_PLAN_GPTPRO.md
- sibling E1-E7 errata (9738c)       -> problems/23/writeup/BRANCH_A_ERRATA_GPTPRO.md

## LEAN (14 files green; build: cd E:\Projects\ErdosProblems\formal-conjectures; lake env lean <abs path>)
- Done: Skeleton, Darts, Distances, Gamma, Row, BankL, BranchAInterface, PacketExchange, CDCore,
  PolyCert (NF+checkEq+PosCert+ConeCert), Bank0Algebra, CertGraph (L0-L3 + B6 BankBlocks checker:
  checkBankBlock + product/disjointness fact-extraction).
- NEXT: CorridorPartition checker (O1-O5 obligations over lists; additivity already proven as
  nu0_append) -> CrossCap -> ClosureTrace -> LensGates -> Seed10/SevenCutCone -> Assembly
  (await main-thread review verdicts on A/B/C before typing Bank0Statement).

## MASTER LEDGER (single source of open obligations)
- WRITEUP_REDTEAM_GPTPRO.md tail: Bank0 B0-B10 + ODL O0-O21 + chain T0-T3 + paths A-D + DoD.
- PROVEN: B0,B7,L7,L8,LemmaA,O1-O3,O8-O10,O12,O15,T0(cond), EQ-ODL1 equality stratum end-to-end.
- DESIGN DONE (specs archived, emission pending): O5 (T=1 REC + verified micro-example),
  O16/O18 (master cubes, 3x11 EQ + 3x13 SIB templates explicit). PROGRAM 100% SPECIFIED.
- CERT-PENDING: B1-B6,B10,O4(O6),O5-EMIT,O11,O13,O14(rung-2 charts),O16-O21-EMIT.  HUNT: O7.
- Certified negative datapoint: EQ-ODL1 restricted F1-F4+B0 Farkas cert exact.
- Full rung-1 cone = 1,755,182 columns (not launched; rung-2 primary).


## TICK NOTES (2026-07-04T10:00Z)
- Assembly plan FINAL (verdicts archived in LEAN_CHECKER_DESIGN_GPTPRO.md tail): RowDBFacts Prop-first; GammaMinimal = BConnected-restricted; flip lemma via indicator sums; 3-layer assembly + providers.
- Lean next: badCount_flip_eq (indicator sums) + sigma_nonneg_of_maxcut derivation in CertGraph.lean; then CorridorPartition checker; Assembly statements per archived plan.
- Extraction queue += sibling 4.1 (~landed). Codex: rung-2 basis-extraction exact replay (B) + 300-chart numeric map (A) in flight; then O5-EMIT, O16/O18-EMIT.
- gersh_Lgt5_of_bankL green (BankL.lean).


## TICK NOTES (2026-07-04T11:15Z)
- O6 T=2 format archived + micro-example hand-verified => EVERY cert-pending node in both ledgers has an emission-ready spec (design queue empty).
- Extraction queue += sibling 4.1 (landed).
- Codex: rung-2 near-band feasible all 3 hard dominants at k=0; inf-band guidance sent (spec par.8 reduced form); basis-extraction replay + 300-chart map in flight.
- Lean next: badCount_flip_eq indicator-sum lemma + sigma_nonneg derivation; then CorridorPartition checker; Assembly statements per archived plan.


## TICK NOTES (2026-07-04T12:25Z)
- Interface canon (12 resolutions) archived + BINDING posted to Codex; O13 Seed3 spec = SAME main reply, offsets ~7900-17359 in window.__au — EXTRACT NEXT TICK (structures C5QuotientData etc.).
- Lean: badCount_flip_eq + sigma_nonneg_of_isMaxCut GREEN (Decision-B core done). Next: CorridorPartition checker; then align existing structures to canon (CompletedSwitchCert, two trace types) as new modules land.
- Codex: modular-rational-reconstruction recipe issued (2686-dim core); inf-band s=0 face INFEASIBLE = spec deviation — RELAY TO MAIN pending (ask corrected leading-homogeneous encoding); numeric map subprocess parallelism approved.
- Main in flight: (this reply done). NEXT RETASK: corrected inf-band encoding question + O13 remainder already in reply. Sibling in flight: appendices 5.1/5.2.
- Commits: fa3a97880.


## TICK NOTES (2026-07-04T13:10Z)
- INF-BAND FIX archived (EQ_HEIGHT_LEMMA tail) + Codex patched: G# = H_G*Lambda^(2-d) lift (bug was s^(2-d) killing linear gens on s=0 face); hard-row priority B0/UA/UB-inf; radial-monotonicity skip criterion. Codex's s=0 infeasibility refuted only the face truncation.
- IN FLIGHT: main = O13 witness/completeness completion; sibling = definitions table (appendices 5.1/5.2 landed 14724c, unextracted).
- EXTRACTION QUEUE grows: appendices 5.1/5.2 (14724c), O13 remainder (window.__au offsets ~7900-17359 — cache may die on tab reload; full text stays in-thread), 4.1, 3.1, 2.1, 1.1-1.3, assembly plan, E1-E7. BATCH SEVERAL NEXT TICK.
- Lean next: CorridorPartition checker + canon alignment (CompletedSwitchCert, two trace types) as new modules.
- Codex: modular replay (2686-dim) TOP + corrected inf-band reruns + numeric map + O5/O6-EMIT queue. Marker 1616087.


## TICK NOTES (2026-07-04T14:30Z)
- O13 classifier spec archived (7 witnesses, completeness enum P4/K13/P2+E/3E, priority order) => LAST fuzzy spec closed. O13-EMIT posted.
- Codex basis-quality ASK ruled: (B) Markowitz/denominator-aware modular pivots + early-exit recon (200-prime cap), (A) one glpsol --exact probe if installed, (C) parallel always.
- IN FLIGHT: main = referee FAQ (defense appendix + gap hunt); sibling = definitions table (appendices 5.1/5.2 landed 14724c unextracted).
- EXTRACTION QUEUE: definitions table (when lands), appendices 5.1/5.2, 4.1, 3.1, 2.1, 1.1-1.3, assembly plan, E1-E7 — BATCH-SAVE next tick to PAPER_SECTIONS_GPTPRO.md etc.
- Lean next: CorridorPartition checker + canon alignment. Marker 1618290.
